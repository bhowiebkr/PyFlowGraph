"""Run each test file with pytest in its own process.

Some tests replace PySide6 with mocks, so one process for all the files gives false failures.
Each file must finish in 10 seconds. The Qt windows stay hidden.

Usage, from any folder:
    python tools/run_tests.py                     all the files in tests/
    python tools/run_tests.py tests/test_x.py     only these files
    python tools/run_tests.py --log-dir DIR       also write the full output of each file to DIR

The exit code is 0 when every file passes.
"""

import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile
import time

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_LIMIT_SECONDS = 10
TAIL_LINES = 40
COUNTS = ("passed", "failed", "errors", "skipped", "xfailed", "xpassed")
COUNT_PATTERNS = {
    "passed": r"\b(\d+) passed",
    "failed": r"\b(\d+) failed",
    "errors": r"\b(\d+) errors?\b",
    "skipped": r"\b(\d+) skipped",
    "xfailed": r"\b(\d+) xfailed",
    "xpassed": r"\b(\d+) xpassed",
}


def as_text(data):
    if isinstance(data, bytes):
        return data.decode("utf-8", "replace")
    return data or ""


def run_file(path, env):
    """Run one test file. Return (status, counts, seconds, output)."""
    command = [sys.executable, "-m", "pytest", path, "-q", "-p", "no:cacheprovider",
               f"--timeout={FILE_LIMIT_SECONDS}"]
    start = time.monotonic()
    # Each file gets its own temporary folder, removed afterwards also when the file crashes.
    with tempfile.TemporaryDirectory(prefix="pyflowgraph_tests_", ignore_cleanup_errors=True) as tmp:
        env = dict(env, TMP=tmp, TEMP=tmp, TMPDIR=tmp)
        try:
            done = subprocess.run(command, cwd=REPO_DIR, env=env, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=FILE_LIMIT_SECONDS)
        except subprocess.TimeoutExpired as e:
            output = as_text(e.stdout) + as_text(e.stderr)
            return "TIMEOUT", dict.fromkeys(COUNTS, 0), time.monotonic() - start, output
    seconds = time.monotonic() - start
    output = done.stdout + done.stderr
    summary_lines = [line for line in output.splitlines()
                     if re.search(r"\d+ (passed|failed|errors?|skipped|xfailed|xpassed)\b", line)]
    summary = summary_lines[-1] if summary_lines else ""
    counts = {}
    for key in COUNTS:
        match = re.search(COUNT_PATTERNS[key], summary)
        counts[key] = int(match.group(1)) if match else 0
    if done.returncode == 0:
        status = "PASS"
    elif done.returncode == 1:
        status = "FAIL"
    elif done.returncode == 2:
        status = "ERROR"  # pytest stopped, for example on an import error.
    elif done.returncode == 5:
        status = "NO TESTS"
    else:
        status = "CRASH"
    return status, counts, seconds, output


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*", help="test files; all of tests/test_*.py if none")
    parser.add_argument("--log-dir", help="write the full output of each file to this folder")
    args = parser.parse_args()

    files = [os.path.abspath(f) for f in args.files]
    if not files:
        files = sorted(glob.glob(os.path.join(REPO_DIR, "tests", "test_*.py")))
    if args.log_dir:
        os.makedirs(args.log_dir, exist_ok=True)

    env = dict(os.environ)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env["PYTHONFAULTHANDLER"] = "1"  # A crash prints the Python stack.

    totals = dict.fromkeys(COUNTS, 0)
    not_passed = []
    for path in files:
        name = os.path.relpath(path, REPO_DIR)
        status, counts, seconds, output = run_file(path, env)
        for key in COUNTS:
            totals[key] += counts[key]
        shown = ", ".join(f"{counts[key]} {key}" for key in COUNTS if counts[key])
        print(f"{status:<8} {seconds:5.1f}s  {name}  {shown}", flush=True)
        if args.log_dir:
            log_name = os.path.basename(path) + ".log"
            with open(os.path.join(args.log_dir, log_name), "w", encoding="utf-8") as f:
                f.write(output)
        if status != "PASS":
            not_passed.append(name)
            for line in output.splitlines()[-TAIL_LINES:]:
                print("    " + line)

    print()
    print(f"{len(files) - len(not_passed)} of {len(files)} files pass. "
          + ", ".join(f"{totals[key]} {key}" for key in COUNTS if totals[key]) + ".")
    for name in not_passed:
        print(f"Not passed: {name}")
    return 1 if not_passed else 0


if __name__ == "__main__":
    sys.exit(main())

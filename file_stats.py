import os
from pathlib import Path
import pathspec

def load_gitignore(path=".gitignore"):
    if not os.path.exists(path):
        return pathspec.PathSpec.from_lines('gitwildmatch', [])
    with open(path, "r", encoding="utf-8") as f:
        return pathspec.PathSpec.from_lines('gitwildmatch', f)

def get_file_stats(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    lines = content.splitlines()
    words = content.split()
    chars = len(content)
    chars_no_ws = len(content.replace(' ', '').replace('\n', '').replace('\t', ''))
    return {
        'lines': len(lines),
        'words': len(words),
        'chars': chars,
        'chars_no_ws': chars_no_ws
    }

def scan_files(root_dir, extensions, ignore_spec):
    file_stats = []
    for subdir, dirs, files in os.walk(root_dir):
        # Normalize path relative to root
        rel_dir = os.path.relpath(subdir, root_dir)
        if ignore_spec.match_file(rel_dir) and rel_dir != ".":
            dirs[:] = []  # Skip descending into ignored directory
            continue

        for file in files:
            rel_path = os.path.normpath(os.path.join(rel_dir, file))
            if ignore_spec.match_file(rel_path):
                continue
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(subdir, file)
                try:
                    stats = get_file_stats(full_path)
                    file_stats.append((full_path, stats))
                except Exception as e:
                    print(f"Failed to process {full_path}: {e}")
    return file_stats

def summarize_stats(file_stats):
    summary = {
        'files': len(file_stats),
        'lines': 0,
        'words': 0,
        'chars': 0,
        'chars_no_ws': 0
    }
    for _, stats in file_stats:
        for key in summary:
            if key != 'files':
                summary[key] += stats[key]
    return summary

def print_summary(title, file_stats):
    print(f"\n--- {title} ---")
    summary = summarize_stats(file_stats)
    for key, value in summary.items():
        print(f"{key.capitalize()}: {value}")

def main():
    root_dir = '.'
    ignore_spec = load_gitignore()

    py_stats = scan_files(root_dir, ['.py'], ignore_spec)
    json_stats = scan_files(root_dir, ['.json'], ignore_spec)

    print_summary("Python Files", py_stats)
    print_summary("JSON Files", json_stats)

if __name__ == "__main__":
    main()

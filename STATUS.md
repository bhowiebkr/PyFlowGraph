# Status

The current state of PyFlowGraph. Read the known problems and the known limits before you
report a problem: a request to remove a limit is a feature request, not a bug.

## What works

The tests for these parts pass:

- Nodes with input and output pins that come from the Python function signature.
- Connections, reroute nodes and groups. Data passes through chains of reroute nodes, and graphs
  with reroute nodes open from a file.
- Undo and redo for node, connection, group and code changes. The undo of a code change makes
  again the connections that the change removed. A change to the **GUI Definition** or
  **GUI State Handler** code is one undo step and keeps the widget values.
- A connection dragged from an input pin starts at the output pin. A drag onto an input that
  has a connection replaces it in one undo step.
- Graph files in Markdown: open and save. Save writes the `## Dependencies` section with all
  its fields. The 4 example graphs in `examples/` open.
- When no recent file is known, the editor opens `examples/password_generator_tool_group.md`.
  When it opens no file, the title is `PyFlowGraph - Untitled`.
- Batch execution in one process. Nodes pass Python objects to each other by reference. The
  inputs of a node go only to its function, not to the shared namespace.
- Live mode keeps one executor, so the node namespace stays between button clicks. Each
  activation connects the buttons of nodes added since the last one.
- Trust checks: the editor asks before it opens or pastes a graph whose nodes have GUI code,
  unless the graph is trusted. Graph dependencies that pip would read as options stop the
  environment setup.
- Startup speed: the default environment check reads files and starts no process, and the
  executor imports NumPy, pandas, PyTorch and TensorFlow only when node code uses them. The
  default environment is made with venv and pip in a worker thread, while a progress dialog
  shows and the window keeps painting.
- Log messages go to the console. `PYFLOWGRAPH_LOG_LEVEL` sets the level; the default is
  `WARNING`.

## What was checked

On 2026-11-14, on Windows 11 with Python 3.13.14 and PySide6 6.12.0, with the Qt windows hidden
(`QT_QPA_PLATFORM=offscreen`):

- `pip install -e .[test]` installs the editor and the test packages, and `pip check` finds no
  problems.
- `src/main.py` starts the editor, loads the stylesheet, shows the window and exits with code 0.
  With no settings, it asks which environment the example uses, then opens
  `password_generator_tool_group` with 4 nodes. The check used throwaway settings, started in a
  temporary folder and answered the question with **Cancel**.
- Startup, with throwaway settings, from a temporary folder: the editor reopens a bundled
  example and a trusted copy of it. It does not reopen an untrusted copy, asks no question and
  writes the reason in the output log.
- `tools/run_tests.py` ran each test file with pytest in its own process, with a limit of 10
  seconds for each file. 60 of 60 files pass. 508 tests pass, and none is marked `xfail`. 20
  tests are skipped because NumPy, pandas, PyTorch and TensorFlow are not installed. The slowest
  file takes 4.3 seconds.
- A timing script, with throwaway settings and this repository's `venv` as the default
  environment: the creation of the window with the default example went from 287 ms to 24 ms.
  `tests/test_speed_fixes.py` checks that the environment setup runs off the GUI thread and
  that Qt timers run during it.
- `tests/test_undo_and_execution_fixes.py` covers the fixes of the problems that were in this
  list: issues 50 to 53, the drag direction and replacement, the code change undo, the widget
  values, the Dependencies section, the input namespace and live mode. The script that found
  these problems showed each one before its fix.
- The same result with Python 3.11.0, in a new environment made with `pip install -e .[test]`,
  as the test workflow does.
- The tests use throwaway settings. The registry key `HKCU\Software\PyFlowGraph` was the same
  before and after the test runs.
- Not checked: the trust questions by hand on the desktop, live mode by hand (only in tests),
  running the example graphs by hand, the progress dialog of the environment setup on the
  desktop with a real pip install, the tests with NumPy, pandas, PyTorch or TensorFlow, the
  Windows build with Nuitka, Linux and macOS.

GitHub Actions builds the Windows app with Nuitka. The **Tests** workflow
(`.github/workflows/tests.yml`) runs `tools/run_tests.py` on Windows with Python 3.11 for each
push and pull request to `main`. Its first run, on commit `1d55e72`, passed 58 of 60 files: two
timing asserts were slower on the GitHub runner than their limits. The timing tests now take the
best of several runs, the median or the 95th percentile, so one slow run does not fail them. The
limits did not change. The result of each run shows on the **Actions** page of the repository.

## Known problems

From the test runs above, and from the source:

- Live mode connects the buttons when it is turned on. A node whose widgets are made again
  after that, by a change to its GUI code or by the undo of its delete, has buttons that do not
  run the graph until you turn live mode off and on (source-derived, not run).
- Code that the editor does not use: `load_file` in `src/pyflowgraph/data/file_operations.py`
  (it calls `window.file_operations_manager`, which does not exist; two tests call it with an
  example that was removed), and the group interface
  classes `GroupInterfacePin`, `GroupConnectionRouter`, `GroupPinGenerator`,
  `ConnectionAnalyzer` and `group_type_inference`. Only tests use them.

## Known limits

- Node code runs with `exec()` in the editor process, not in a separate process. A node that
  hangs or crashes stops the editor.
- The **GUI Definition** and **GUI State Handler** code of each node runs when a graph opens or
  is pasted. The editor asks first, unless the graph is a bundled example, a file that you
  saved, or a version of the file that you trusted before. After you trust a graph, its code
  runs with no question until the file changes. The other node code runs when you run the
  graph, with no question. A graph file is a program: trust only graphs whose source you trust.
- Paste does not ask when the text is what this editor copied last. Text copied in another
  window of the editor counts as foreign text, so paste asks.
- Each graph dependency must be one package name. Entries with pip options, such as
  `--index-url`, are refused.
- The packages of a graph's virtual environment are added to the editor's Python path. They
  stay there when you change to another environment, until you start the editor again.
- The release build is for Windows only. On Linux and macOS, run from the source code.

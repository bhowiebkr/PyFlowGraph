# CLAUDE.md

## Project Overview

PyFlowGraph: Universal node-based visual scripting editor built with Python and PySide6. "Code as Nodes" philosophy with automatic pin generation from Python function signatures.

## Commands

**Running**: `run.bat` (Windows) or `./run.sh` (Linux/macOS)
**Testing**: `run_test_gui.bat` - Professional GUI test runner
**Dependencies**: `pip install PySide6`

## Architecture

**Core**: `src/` contains 25+ Python modules

- `main.py` - Entry point with Font Awesome fonts/QSS
- `node_editor_window.py` - Main QMainWindow
- `node_editor_view.py` - QGraphicsView (pan/zoom/copy/paste)
- `node_graph.py` - QGraphicsScene (nodes/connections/clipboard)
- `graph_executor.py` - Execution engine with subprocess isolation
- `commands/` - Command pattern for undo/redo system

**Node System**: `node.py`, `pin.py`, `connection.py`, `reroute_node.py`
**Code Editing**: `code_editor_dialog.py`, `python_code_editor.py`, `python_syntax_highlighter.py`
**Event System**: `event_system.py` - Live mode execution support

## Key Concepts

**Node Function Parsing**: Automatic pin generation from Python function signatures with type hints
**Data Flow Execution**: Data-driven (not control-flow), subprocess isolation, JSON serialization
**Graph Persistence**: Clean JSON format, saved to `examples/` directory

## File Organization

```
PyFlowGraph/
├── src/                    # 25+ Python modules + commands/
├── tests/                  # 18+ test files with GUI test runner
├── docs/                   # Organized documentation
│   ├── architecture/       # Technical architecture docs
│   ├── specifications/     # Feature specs (flow_spec.md, ui-ux, etc.)
│   └── development/        # Testing guides, implementation notes
├── examples/               # Sample .md graph files
├── venv/ + venvs/         # Virtual environments
└── run.bat, run_test_gui.bat # Launchers
```

## Testing

**Current Suite**: 18+ test files covering node system, pins, connections, execution, file formats
**GUI Runner**: `run_test_gui.bat` - Professional PySide6 interface with real-time status
**Coverage**: Core components, command system, integration scenarios

## Development Notes

- **WINDOWS-ONLY CODEBASE**: This project runs exclusively on Windows
- PySide6 Qt-based GUI with Font Awesome icons
- Isolated subprocess execution for security
- No Claude attribution in commits or code comments
- **NEVER use emojis in any code, tests, or temporary files - causes encoding issues**
- Clean, professional, technical documentation only

## Windows Platform Requirements

**CRITICAL**: This is a Windows-only codebase. Claude Code MUST use Windows-compatible commands:

- **Shell Commands**: Use `cmd`, `powershell`, or Windows batch commands only
- **File Operations**: Use Windows paths with backslashes `\` or forward slashes `/`
- **Batch Files**: Execute `.bat` files directly (e.g., `run.bat`, `run_test_gui.bat`)
- **Python Execution**: Use `python` command (not `python3`)
- **Path Separators**: Use Windows-style paths `E:\HOME\PyFlowGraph\`

**FORBIDDEN Linux Commands**:
- Do NOT use: `ls`, `grep`, `find`, `chmod`, `./script.sh`, `/usr/bin/bash`
- Use instead: `dir`, `findstr`, `where`, `attrib`, `script.bat`, `cmd.exe`

## Code Standards

**NO EMOJIS RULE**: Absolutely no emoji characters in:

- Source code (`.py` files)
- Test files (all tests in `tests/` directory)
- Temporary test files or scripts
- Comments, docstrings, or print statements
- Variable names, function names, or any identifiers
- Console output or logging messages

**Reason**: Emojis cause Unicode encoding errors on Windows console (cp1252 codec) and create test failures. Use ASCII text alternatives like "PASS"/"FAIL", "OK"/"ERROR", etc.

# important-instruction-reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
NEVER use emojis in any code, tests, or temporary files - causes Windows encoding errors.

**WINDOWS-ONLY PLATFORM REQUIREMENTS**:
- NEVER use Linux commands: `ls`, `grep`, `find`, `chmod`, `/usr/bin/bash`, `./script.sh`
- ALWAYS use Windows commands: `dir`, `findstr`, `where`, `attrib`, `cmd.exe`, `script.bat`
- Execute batch files directly: `run.bat`, `run_test_gui.bat` (not `./run.bat`)
- Use Windows paths: `E:\HOME\PyFlowGraph\` or forward slashes for compatibility
- Use `python` command (not `python3`)

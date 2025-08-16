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

- Experimental AI-generated codebase for learning
- PySide6 Qt-based GUI with Font Awesome icons
- Isolated subprocess execution for security
- No Claude attribution in commits or code comments
- No emojis in code - causes issues
- Clean, professional, technical documentation only

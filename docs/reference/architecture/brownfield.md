# PyFlowGraph Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the PyFlowGraph codebase, including its architecture, patterns, and design decisions. It serves as a reference for AI agents working on enhancements or maintenance tasks.

### Document Scope

Comprehensive documentation of the entire PyFlowGraph system - a universal node-based visual scripting editor built with Python and PySide6.

### Change Log

| Date       | Version | Description                 | Author    |
| ---------- | ------- | --------------------------- | --------- |
| 2025-08-15 | 1.0     | Initial brownfield analysis | AI Agent  |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

- **Main Entry**: `src/main.py` - Application bootstrap, Font Awesome loading, QSS stylesheet
- **Main Window**: `src/node_editor_window.py` - QMainWindow with menus, toolbars, dock widgets
- **Graph Scene**: `src/node_graph.py` - QGraphicsScene managing nodes and connections
- **Node System**: `src/node.py` - Core Node class with automatic pin generation
- **Execution Engine**: `src/execution/graph_executor.py` - Shared process execution coordination
- **Process Manager**: `src/execution/shared_process_manager.py` - Persistent worker process pool management
- **Event System**: `src/event_system.py` - Live mode event-driven execution
- **File Format**: `src/flow_format.py` - Markdown-based persistence
- **Configuration**: `dark_theme.qss` - Application styling

### Launch Scripts

- **Windows**: `run.bat` - Activates venv and runs main.py
- **Linux/macOS**: `run.sh` - Shell equivalent
- **Test GUI**: `run_test_gui.bat` - Launches professional test runner

## High Level Architecture

### Technical Summary

PyFlowGraph implements a "Code as Nodes" philosophy where Python functions are represented as visual nodes with automatically generated pins based on type hints. The system supports both batch execution (sequential data flow) and live mode (event-driven interactive execution).

### Actual Tech Stack (from requirements.txt)

| Category     | Technology       | Version | Notes                                    |
| ------------ | ---------------- | ------- | ---------------------------------------- |
| GUI Framework| PySide6          | Latest  | Qt6 bindings for Python                 |
| Compiler     | Nuitka           | Latest  | Optional - for creating executables     |
| Markdown     | markdown-it-py   | Latest  | For parsing .md flow format files       |
| Python       | Python           | 3.8+    | Core runtime requirement                 |
| Icons        | Font Awesome     | Embedded| In src/resources/ directory             |

### Repository Structure Reality Check

- Type: Monolithic application
- Package Manager: pip with requirements.txt
- Virtual Environments: Project-specific venvs in `venvs/` directory
- Notable: Clean separation between core engine and UI components

## Source Tree and Module Organization

### Project Structure (Actual)

```text
PyFlowGraph/
├── src/                           # All Python source code
│   ├── resources/                 # Font Awesome fonts (fa-regular-400.ttf, fa-solid-900.ttf)
│   ├── main.py                   # Entry point, font and stylesheet loading
│   ├── node_editor_window.py     # Main QMainWindow application
│   ├── node_editor_view.py       # QGraphicsView with mouse/keyboard handling
│   ├── node_graph.py             # QGraphicsScene managing nodes/connections
│   ├── node.py                   # Core Node class with pin generation
│   ├── pin.py                    # Input/output connection points
│   ├── connection.py             # Bezier curve connections
│   ├── reroute_node.py           # Simple routing nodes
│   ├── graph_executor.py         # Batch mode execution engine
│   ├── event_system.py           # Live mode event-driven execution
│   ├── execution_controller.py   # Central execution coordination
│   ├── flow_format.py            # Markdown format parser/serializer
│   ├── file_operations.py        # File I/O and import/export
│   ├── code_editor_dialog.py     # Modal code editing dialog
│   ├── python_code_editor.py     # Core editor widget
│   ├── python_syntax_highlighter.py # Syntax highlighting
│   ├── environment_manager.py    # Virtual environment management
│   ├── default_environment_manager.py # Default venv handling
│   ├── environment_selection_dialog.py # Environment picker
│   ├── settings_dialog.py        # Application settings
│   ├── graph_properties_dialog.py # Graph-level settings
│   ├── node_properties_dialog.py # Node property editing
│   ├── color_utils.py            # Color manipulation utilities
│   ├── ui_utils.py               # Common UI helpers
│   ├── view_state_manager.py     # View state persistence
│   └── test_runner_gui.py        # Professional test runner UI
├── tests/                         # Comprehensive test suite
│   ├── test_node_system.py       # Node functionality tests
│   ├── test_pin_system.py        # Pin creation and connections
│   ├── test_connection_system.py # Connection/bezier curves
│   ├── test_graph_management.py  # Graph operations
│   ├── test_execution_engine.py  # Code execution testing
│   ├── test_file_formats.py      # Format parsing/conversion
│   ├── test_integration.py       # End-to-end workflows
│   └── test_view_state_persistence.py # View state tests
├── examples/                      # 10 sample .md graph files
├── docs/                          # Documentation
├── test_reports/                  # Generated test outputs
├── images/                        # Screenshots and visuals
├── venv/                          # Main application virtual environment
├── venvs/                         # Project-specific environments
├── dark_theme.qss                 # Application stylesheet
├── requirements.txt               # Python dependencies
├── CLAUDE.md                      # AI agent instructions
└── README.md                      # Project documentation
```

### Key Modules and Their Purpose

#### Core Node System
- **Node Management**: `src/node.py` - Node class with automatic pin generation from Python function signatures
- **Pin System**: `src/pin.py` - Type-based colored pins for data/execution flow
- **Connections**: `src/connection.py` - Bezier curve connections with validation
- **Reroute Nodes**: `src/reroute_node.py` - Simple pass-through nodes for organization

#### Execution Engine
- **Batch Executor**: `src/graph_executor.py` - Sequential execution in subprocess isolation
- **Live Executor**: `src/event_system.py` - Event-driven interactive execution with EventManager
- **Controller**: `src/execution_controller.py` - Coordinates between batch/live modes
- **Environment Management**: `src/environment_manager.py` - Per-project virtual environments

#### User Interface
- **Main Window**: `src/node_editor_window.py` - Application shell with menus/toolbars
- **Graph View**: `src/node_editor_view.py` - Pan/zoom/selection handling
- **Graph Scene**: `src/node_graph.py` - Node/connection management, clipboard operations
- **Code Editor**: `src/python_code_editor.py` - Python editor with line numbers

#### File Operations
- **Flow Format**: `src/flow_format.py` - Markdown-based graph persistence
- **File Operations**: `src/file_operations.py` - Save/load/import/export handling
- **View State**: `src/view_state_manager.py` - Camera position persistence

## Data Models and APIs

### Core Data Structures

Instead of duplicating, reference actual implementation files:

- **Node Model**: See `src/node.py:Node` class
- **Pin Model**: See `src/pin.py:Pin` class  
- **Connection Model**: See `src/connection.py:Connection` class
- **Graph Event**: See `src/event_system.py:GraphEvent` class

### Internal APIs

#### Node Pin Generation
Nodes automatically parse Python function signatures to create pins:
- Input pins from function parameters with type hints
- Output pins from return type annotations
- Supports `Tuple[...]` for multiple outputs
- Type determines pin color (int=blue, str=green, float=orange, bool=red)

#### Execution Protocol (Shared Process Architecture)
Each node executes in shared worker process:
1. Acquire worker from persistent process pool
2. Pass object references for large data (tensors, DataFrames), JSON for primitives
3. Execute node code in shared process with direct memory access
4. Return results via object references or direct values
5. Pass to connected nodes with zero-copy for large objects

#### Event System (Live Mode)
- `EventType`: Defines event categories (TIMER, USER_INPUT, etc.)
- `EventManager`: Manages event subscriptions and dispatching
- `LiveGraphExecutor`: Executes nodes in response to events

## Technical Debt and Known Issues

### Minimal Technical Debt

1. **Copy/Paste Bug Fix**: In `src/node_editor_view.py:39` - Comment notes copy_selected method signature changed
2. **JSON Backward Compatibility**: `src/node_graph.py:78` - Fallback JSON parsing for old format files
3. **UUID Regeneration**: `src/node_graph.py:132-134` - Node UUIDs regenerated when pasting with offset

### Design Decisions and Constraints

- **Subprocess Isolation**: Each node runs in separate process for security - adds overhead but prevents crashes
- **JSON Serialization**: All data between nodes must be JSON-serializable - limits complex object passing
- **Type Hint Parsing**: Relies on AST parsing of function signatures - complex types may not parse correctly
- **Virtual Environment Per Project**: Each graph can have isolated dependencies - disk space overhead

### Areas for Potential Enhancement

- No built-in version control integration
- Limited debugging capabilities for node execution
- No node grouping/subgraph functionality
- No undo/redo system implemented
- Test coverage focused on core functionality only

## Integration Points and External Dependencies

### External Services

PyFlowGraph is self-contained with no external service dependencies.

### Python Package Dependencies

| Package        | Purpose              | Integration Type | Key Files                          |
| -------------- | -------------------- | ---------------- | ---------------------------------- |
| PySide6        | GUI Framework        | Direct Import    | All UI files                       |
| markdown-it-py | Markdown Parsing     | Library          | `src/flow_format.py`               |
| Nuitka         | Compilation          | Build Tool       | Used in build process only         |

### Virtual Environment Integration

- Creates project-specific venvs in `venvs/` directory
- Uses subprocess to run pip in isolated environments
- Stores requirements in graph metadata

## Development and Deployment

### Local Development Setup

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate environment:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run application: `python src/main.py` or use `run.bat`/`run.sh`

### Known Setup Issues

- Font Awesome fonts must be present in `src/resources/`
- QSS stylesheet (`dark_theme.qss`) must be in root directory
- Windows may require administrator privileges for some venv operations

### Build and Deployment Process

- **Development**: Run directly with Python interpreter
- **Testing**: Use `run_test_gui.bat` or `python src/test_runner_gui.py`
- **Compilation**: Nuitka can create standalone executables (optional)
- **Distribution**: Package with all resources and dependencies

## Testing Reality

### Current Test Coverage

- **Unit Tests**: Comprehensive coverage of core functionality
- **Test Files**: 8 test modules covering all major components
- **Test Runner**: Professional GUI test runner with visual feedback
- **Execution Time**: All tests complete within 5 seconds

### Test Organization

```bash
tests/
├── test_node_system.py        # Node creation, properties, serialization
├── test_pin_system.py         # Pin types, connections, compatibility
├── test_connection_system.py  # Connection creation, reroute nodes
├── test_graph_management.py   # Graph operations, clipboard
├── test_execution_engine.py   # Code execution, error handling
├── test_file_formats.py       # Markdown/JSON parsing
├── test_integration.py        # End-to-end workflows
└── test_view_state_persistence.py # View state saving/loading
```

### Running Tests

```bash
# GUI Test Runner (Recommended)
run_test_gui.bat              # Windows
python src/test_runner_gui.py # Direct

# Manual Testing
python tests/test_name.py     # Individual test file
```

## Architecture Patterns and Conventions

### Code Organization Patterns

1. **Single Responsibility**: Each module has clear, focused purpose
2. **Qt Model-View**: Separation between data (nodes/graph) and presentation (view/scene)
3. **Factory Pattern**: Node creation through graph methods
4. **Observer Pattern**: Signal/slot connections for UI updates

### Naming Conventions

- **Files**: Snake_case for all Python files
- **Classes**: PascalCase (e.g., `NodeEditorWindow`, `GraphExecutor`)
- **Methods**: Snake_case with underscore prefix for private
- **Qt Overrides**: Maintain Qt naming (e.g., `mousePressEvent`)

### UI/UX Patterns

- Blueprint-style visual design with dark theme
- Right-click for context menus and navigation
- Modal dialogs for complex operations
- Dock widgets for output and properties

## Common Development Tasks

### Adding New Node Types

1. Modify node's code with proper function signature
2. Include type hints for automatic pin generation
3. Return single value or Tuple for multiple outputs

### Extending Execution Modes

- Batch Mode: Modify `GraphExecutor` class
- Live Mode: Extend `LiveGraphExecutor` and `EventManager`
- Add new `EventType` enum values as needed

### Customizing UI Theme

- Edit `dark_theme.qss` for application-wide styling
- Node colors defined in `src/node.py` color constants
- Pin colors in `src/pin.py` based on data types

## Appendix - Useful Commands and Scripts

### Frequently Used Commands

```bash
# Running the Application
run.bat                    # Windows launcher
./run.sh                   # Linux/macOS launcher
python src/main.py         # Direct Python execution

# Testing
run_test_gui.bat           # Launch test runner GUI
python src/test_runner_gui.py  # Direct test GUI

# Environment Management
python -m venv venv        # Create main venv
pip install -r requirements.txt  # Install dependencies
```

### File Locations

- **Example Graphs**: `examples/` directory contains 10 sample .md files
- **Test Reports**: `test_reports/` for test output
- **Project Environments**: `venvs/` for isolated environments
- **Documentation**: `docs/` for additional documentation

### Important Implementation Notes

1. **No Git Config Modification**: Never update git configuration
2. **No Emojis in Code**: Avoid emoji usage that can cause encoding issues
3. **No Marketing Language**: Keep documentation technical and factual
4. **CLAUDE.md Override**: Project instructions in CLAUDE.md take precedence

## System Constraints and Gotchas

### Must Respect

- **Font Loading**: Font Awesome fonts must load before UI creation
- **Subprocess Timeout**: Default 10-second timeout for node execution
- **JSON Serialization**: All node data must be JSON-compatible
- **Virtual Environment Paths**: Stored as absolute paths in graph files

### Known Workarounds

- **Copy/Paste**: UUID regeneration ensures unique nodes when pasting
- **File Format**: Markdown format with JSON fallback for compatibility
- **View State**: Saved separately per file to maintain camera position

### Performance Considerations

- **Execution Performance**: Shared process pool eliminates subprocess overhead (10-100x faster)
- **Large Graphs**: No optimization for graphs with 100+ nodes
- **Virtual Environments**: Creating new environments can be slow

## Summary

PyFlowGraph is a well-architected visual scripting system with clean separation of concerns, minimal technical debt, and thoughtful design decisions. The codebase follows consistent patterns and provides a solid foundation for enhancement or extension. Key strengths include the automatic pin generation system, dual execution modes, and human-readable file format. Areas for potential improvement include adding undo/redo, node grouping, and enhanced debugging capabilities.
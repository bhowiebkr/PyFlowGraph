# PyFlowGraph Source Tree

## Project Root Structure

```
PyFlowGraph/
├── src/                     # All Python source code (24 modules)
├── tests/                   # Test suite (7 test files)
├── docs/                    # Documentation
│   └── architecture/        # Architecture documentation
├── examples/                # Sample graph files (10 examples)
├── images/                  # Screenshots and documentation images
├── test_reports/            # Generated test outputs
├── pre-release/             # Pre-built binaries
├── venv/                    # Main application virtual environment
├── venvs/                   # Project-specific virtual environments
├── .github/                 # GitHub configuration
│   └── workflows/           # CI/CD pipelines
├── run.bat                  # Windows launcher
├── run.sh                   # Unix launcher
├── run_test_gui.bat         # Test runner launcher
├── dark_theme.qss           # Application stylesheet
├── requirements.txt         # Python dependencies
├── LICENSE.txt              # MIT License
├── README.md                # Project documentation
└── CLAUDE.md                # AI assistant guidelines
```

## Source Code Directory (src/)

### Core Application Files
```
src/
├── main.py                  # Application entry point
├── node_editor_window.py    # Main application window
├── node_editor_view.py      # Graphics view for node editor
└── node_graph.py            # Scene management for nodes
```

### Node System
```
src/
├── node.py                  # Base node class with pin generation
├── pin.py                   # Input/output connection points
├── connection.py            # Bezier curve connections
└── reroute_node.py          # Connection routing nodes
```

### Code Editing
```
src/
├── code_editor_dialog.py    # Modal code editor dialog
├── python_code_editor.py    # Core editor widget
└── python_syntax_highlighter.py  # Syntax highlighting
```

### Execution System
```
src/
├── graph_executor.py        # Graph execution engine
├── execution_controller.py  # Execution coordination
└── event_system.py          # Event-driven execution
```

### User Interface
```
src/
├── node_properties_dialog.py  # Node configuration dialog
├── environment_manager.py     # Virtual environment management
├── settings_dialog.py          # Application settings
├── test_runner_gui.py          # GUI test runner
└── ui_utils.py                 # Common UI utilities
```

### File Operations
```
src/
├── file_operations.py       # Load/save operations
└── flow_format.py           # Markdown flow format handling
```

### Utilities
```
src/
├── color_utils.py           # Color manipulation utilities
└── view_state_manager.py    # View state persistence
```

### Resources
```
src/resources/               # Embedded Font Awesome fonts
├── Font Awesome 6 Free-Regular-400.otf
└── Font Awesome 6 Free-Solid-900.otf
```

## Test Directory (tests/)

```
tests/
├── test_node_system.py      # Node functionality tests
├── test_pin_system.py       # Pin creation and connections
├── test_connection_system.py # Connection and bezier curves
├── test_graph_management.py  # Graph operations
├── test_execution_engine.py  # Code execution tests
├── test_file_formats.py      # File I/O and formats
└── test_integration.py       # End-to-end workflows
```

## Documentation Directory (docs/)

```
docs/
├── architecture/            # Architecture documentation
│   ├── coding-standards.md # Coding conventions
│   ├── tech-stack.md        # Technology stack
│   └── source-tree.md       # This file
├── flow_spec.md             # Flow format specification
├── TEST_RUNNER_README.md    # Test runner documentation
├── TODO.md                  # Project task list
├── brownfield-architecture.md # Legacy architecture notes
├── undo-redo-implementation.md # Feature documentation
└── priority-1-features-project-brief.md # Feature planning
```

## Examples Directory

```
examples/
├── simple_math.md           # Basic arithmetic operations
├── data_processing.md       # Data manipulation example
├── visualization.md         # Plotting and graphics
├── control_flow.md          # Conditionals and loops
├── file_operations.md       # File I/O examples
├── api_integration.md       # External API usage
├── machine_learning.md      # ML pipeline example
├── web_scraping.md          # Web data extraction
├── image_processing.md      # Image manipulation
└── database_query.md        # Database operations
```

## Module Responsibilities

### Application Layer
- **main.py**: Entry point, font loading, QSS styling
- **node_editor_window.py**: Menu bar, toolbars, dock widgets, file operations
- **node_editor_view.py**: Mouse/keyboard handling, pan/zoom, selection

### Graph Management
- **node_graph.py**: Scene container, node/connection management, clipboard
- **file_operations.py**: JSON/Markdown serialization, import/export
- **flow_format.py**: Markdown flow format parsing

### Node System
- **node.py**: Function parsing, pin generation, code management
- **pin.py**: Type detection, color coding, connection validation
- **connection.py**: Bezier paths, hit detection, serialization
- **reroute_node.py**: Visual organization, connection routing

### Code Execution
- **graph_executor.py**: Subprocess isolation, dependency resolution
- **execution_controller.py**: Execution coordination, error handling
- **event_system.py**: Live mode, event dispatching

### User Interface
- **code_editor_dialog.py**: Modal editing, save/cancel operations
- **python_code_editor.py**: Line numbers, indentation, text operations
- **python_syntax_highlighter.py**: Keyword highlighting, string detection
- **node_properties_dialog.py**: Node metadata, descriptions
- **environment_manager.py**: Pip packages, virtual environments
- **settings_dialog.py**: User preferences, configuration
- **test_runner_gui.py**: Test discovery, execution, reporting
- **ui_utils.py**: Common dialogs, helpers

### Utilities
- **color_utils.py**: HSL/RGB conversion, color manipulation
- **view_state_manager.py**: Zoom level, pan position persistence

## File Naming Conventions

### Python Files
- **Snake_case**: All Python modules use snake_case
- **Descriptive names**: Clear indication of purpose
- **Suffix patterns**:
  - `*_dialog.py`: Modal dialog windows
  - `*_utils.py`: Utility functions
  - `*_system.py`: Core subsystems
  - `*_manager.py`: State management

### Test Files
- **Prefix**: All test files start with `test_`
- **Module mapping**: Tests mirror source module names
- **Organization**: Grouped by functional area

### Documentation Files
- **Markdown**: All docs use .md extension
- **Descriptive**: Clear titles indicating content
- **Hierarchical**: Organized in subdirectories

## Import Hierarchy

### Level 0 (No Dependencies)
- color_utils.py
- ui_utils.py

### Level 1 (Basic Dependencies)
- pin.py (uses color_utils)
- python_syntax_highlighter.py
- view_state_manager.py

### Level 2 (Component Dependencies)
- node.py (uses pin)
- connection.py (uses pin)
- python_code_editor.py (uses syntax_highlighter)
- reroute_node.py (uses node)

### Level 3 (System Dependencies)
- node_graph.py (uses node, connection, reroute_node)
- code_editor_dialog.py (uses python_code_editor)
- graph_executor.py (uses node, connection)
- event_system.py

### Level 4 (Integration)
- node_editor_view.py (uses node_graph)
- execution_controller.py (uses graph_executor, event_system)
- file_operations.py (uses node_graph, flow_format)

### Level 5 (Application)
- node_editor_window.py (uses all major components)
- main.py (uses node_editor_window)

## Key Design Patterns

### Model-View Architecture
- **Model**: node.py, pin.py, connection.py
- **View**: QGraphicsItem implementations
- **Controller**: node_graph.py, node_editor_view.py

### Observer Pattern
- Qt signals/slots for event handling
- Event system for execution notifications

### Factory Pattern
- Node creation from function signatures
- Pin generation from type hints

### Command Pattern
- Clipboard operations
- Future: Undo/redo system

### Singleton Pattern
- Settings management
- Font loading

## Module Metrics

### Lines of Code (Approximate)
- **Largest**: node_editor_window.py (~1200 lines)
- **Medium**: node.py, node_graph.py (~500 lines)
- **Smallest**: color_utils.py, ui_utils.py (~100 lines)

### Complexity
- **High**: graph_executor.py (subprocess management)
- **Medium**: node.py (parsing, pin generation)
- **Low**: reroute_node.py (simple forwarding)

### Test Coverage Focus
- **Critical**: Node system, execution engine
- **Important**: File operations, connections
- **Standard**: UI components, utilities
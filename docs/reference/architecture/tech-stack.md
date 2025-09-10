# PyFlowGraph Technology Stack

## Core Technologies

### Programming Language
- **Python 3.8+**
  - Primary development language
  - Required for type hints and modern Python features
  - Cross-platform compatibility (Windows, Linux, macOS)

### GUI Framework
- **PySide6 (Qt6)**
  - Qt-based Python bindings for cross-platform GUI
  - Modern Qt6 features and performance
  - QGraphicsView framework for node editor
  - Signal/slot mechanism for event handling

## Dependencies

### Required Packages
```txt
PySide6==6.5.0+    # GUI framework
Nuitka             # Optional: For building executables
```

### Development Dependencies
- **pytest**: Unit testing framework
- **black**: Code formatting (optional)
- **pylint**: Code linting (optional)

## Architecture Components

### Core Systems

#### Node System
- **Purpose**: Visual representation and code execution
- **Technology**: QGraphicsItem-based custom widgets
- **Key Classes**: Node, Pin, Connection, RerouteNode

#### Code Editor
- **Purpose**: Python code editing with syntax highlighting
- **Technology**: QPlainTextEdit with custom QSyntaxHighlighter
- **Features**: Line numbers, smart indentation, Python syntax highlighting

#### Execution Engine
- **Purpose**: Safe execution of node graphs
- **Technology**: Python subprocess isolation
- **Communication**: JSON serialization between processes
- **Security**: Sandboxed execution environment

#### Event System
- **Purpose**: Interactive and event-driven execution
- **Technology**: Custom event dispatcher with Qt signals
- **Modes**: Batch (sequential) and Live (event-driven)

### User Interface

#### Main Window
- **Framework**: QMainWindow
- **Components**: Menus, toolbars, dock widgets
- **Styling**: Custom QSS dark theme

#### Graphics View
- **Framework**: QGraphicsView/QGraphicsScene
- **Features**: Pan, zoom, selection, copy/paste
- **Rendering**: Hardware-accelerated Qt rendering

#### Dialogs
- **Framework**: QDialog derivatives
- **Examples**: Settings, node properties, environment manager
- **Style**: Consistent dark theme

### File Formats

#### Graph Files (.md)
- **Format**: Markdown with embedded JSON
- **Purpose**: Human-readable graph storage
- **Structure**: Flow format specification

#### JSON Format
- **Purpose**: Machine-readable graph data
- **Contents**: Nodes, connections, metadata
- **Versioning**: Format version tracking

### Font Resources
- **Font Awesome 6**
  - Embedded in src/resources/
  - Professional iconography
  - Solid and regular variants

## Development Tools

### Build System
- **Virtual Environments**: Python venv
  - Main app environment: `venv/`
  - Graph-specific environments: `venvs/`
- **Package Management**: pip with requirements.txt

### Testing Framework
- **Unit Tests**: Python unittest
- **Test Runner**: Custom PySide6 GUI test runner
- **Coverage**: Core functionality testing
- **Execution**: < 5 seconds per test file

### Version Control
- **Git**: Source control
- **GitHub**: Repository hosting
- **GitHub Actions**: CI/CD pipeline

## Deployment

### Distribution Methods
- **Source**: Direct Python execution
- **Compiled**: Nuitka-built executables
- **Releases**: Pre-built binaries in pre-release/

### Platform Support
- **Windows**: Primary platform (run.bat)
- **Linux**: Supported (run.sh)
- **macOS**: Supported (run.sh)

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 4GB RAM
- 100MB disk space
- OpenGL 2.0 support (for Qt rendering)

### Recommended
- Python 3.10+
- 8GB RAM
- SSD storage
- Modern GPU for smooth graphics

## Security Considerations

### Code Execution
- Subprocess isolation for node execution
- No direct eval/exec on user code
- JSON-only inter-process communication

### File System
- Restricted file access patterns
- Virtual environment isolation
- No system-level modifications

## Future Considerations

### Potential Additions
- WebSocket support for remote execution
- Additional language support beyond Python
- Plugin system for custom nodes
- Cloud storage integration

### Performance Optimizations
- Lazy loading for large graphs
- Cached execution results
- Parallel node execution
- GPU acceleration for graphics

## Integration Points

### External Tools
- Python packages via pip
- System commands via subprocess
- File system for import/export

### Extensibility
- Custom node types via Python code
- Theme customization via QSS
- Virtual environment per graph
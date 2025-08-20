# PyFlowGraph Source Code

This directory contains all Python source code for PyFlowGraph, a universal node-based visual scripting editor. The architecture follows a modular design with clear separation of concerns across functional areas.

## Purpose

The `src/` directory implements PyFlowGraph's "Code as Nodes" philosophy, providing a complete visual programming environment where Python functions become visual nodes with automatically generated pins based on function signatures and type hints.

## Key Files

### `main.py`
- **Application Entry Point**: Main application startup and initialization
- Font Awesome font loading and registration with Qt font system
- QSS stylesheet loading for professional application styling
- Application instance creation and main window launch
- Resource management and application-wide configuration

### `__init__.py`
Standard Python package initialization file for the src module.

## Module Organization

### Core System Modules

#### `commands/` - Command Pattern Implementation
- Undo/redo system using Command pattern
- All user actions encapsulated as reversible commands
- Command history management and batch operations
- Integration with UI for comprehensive undo/redo support

#### `core/` - Fundamental Components
- Node system with automatic pin generation from Python functions
- Pin and connection management with type-based validation
- Node graph scene management and serialization
- Group system for hierarchical node organization
- Event system for live execution and real-time updates

#### `execution/` - Graph Execution Engine
- Data-driven execution with subprocess isolation
- Environment management and virtual environment support
- Execution controller for batch and interactive modes
- Security features including sandboxing and resource limits

#### `data/` - Persistence and File Operations
- File I/O operations with comprehensive error handling
- Markdown-based flow format for human-readable graph storage
- JSON serialization for complete graph state preservation
- Import/export functionality and format conversion utilities

### User Interface Modules

#### `ui/` - Complete User Interface System
- **`editor/`**: Main editor window, graphics view, and view state management
- **`dialogs/`**: Modal dialogs for specialized operations and configuration
- **`code_editing/`**: Python code editor with syntax highlighting and smart features
- **`utils/`**: Common UI utilities and styling helpers

Professional PySide6-based interface with modern desktop application features.

### Support Modules

#### `resources/` - Embedded Application Resources
- Font Awesome 6 and 7 font files for scalable vector icons
- Professional icon system integrated throughout the application
- Embedded resources for reliable cross-platform distribution

#### `utils/` - Utility Functions and Helpers
- Color management and theme utilities
- Debug configuration and development tools
- Common operations shared across application modules

## Architecture Principles

### Modular Design
- **Clear Separation**: Each module has a specific, well-defined responsibility
- **Loose Coupling**: Modules interact through clean interfaces with minimal dependencies
- **High Cohesion**: Related functionality is grouped together within modules
- **Extensibility**: Architecture supports easy addition of new features and capabilities

### Professional Standards
- **Qt Integration**: Built on PySide6 for professional desktop application capabilities
- **Security First**: Subprocess isolation and sandboxing for safe code execution
- **Performance Optimized**: Efficient rendering and execution for large graphs
- **Cross-Platform**: Windows-focused with consideration for platform-specific requirements

### Visual Programming Focus
- **Code as Nodes**: Python functions automatically become visual nodes
- **Type Safety**: Pin connections validated based on Python type hints
- **Live Execution**: Real-time execution and feedback for interactive development
- **Professional Tools**: Complete development environment with debugging and analysis

## Dependencies

### External Libraries
- **PySide6**: Qt framework for professional desktop GUI applications
- **Python Standard Library**: Core Python functionality for execution and data handling

### Internal Dependencies
- **Core-Centric**: Most modules depend on core components for fundamental operations
- **UI Independence**: Core functionality operates independently of UI components
- **Command Integration**: All user actions flow through the command system
- **Event Coordination**: Event system enables loose coupling between components

## Development Workflow

### Entry Point Flow
1. **main.py**: Application startup and resource loading
2. **UI Initialization**: Main window and interface components created
3. **Core Systems**: Node graph, execution engine, and command system initialized
4. **User Interaction**: Complete visual programming environment ready for use

### Module Interaction
- **Commands**: All user actions generate commands for undo/redo support
- **Core**: Provides fundamental objects (nodes, pins, connections) used throughout
- **Execution**: Transforms visual graphs into executable programs
- **UI**: Provides visual representation and interaction for all core concepts

## Architecture Integration

The source code architecture reflects PyFlowGraph's goal of making programming more accessible through visual representation while maintaining the full power and flexibility of Python. Each module contributes to a cohesive system that bridges visual design and code execution in a professional, reliable environment.
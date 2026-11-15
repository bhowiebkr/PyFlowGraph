# Dialogs Module

This module contains modal dialog windows that provide specialized interfaces for various PyFlowGraph operations. Each dialog focuses on a specific aspect of the application, offering detailed configuration and editing capabilities in focused, task-oriented interfaces.

## Purpose

The dialogs module implements PyFlowGraph's modal interface components, providing focused workflows for complex operations that require detailed user input or configuration. These dialogs maintain consistency with the main interface while offering specialized functionality.

## Key Files

### `__init__.py`
Standard Python package initialization file.

### `code_editor_dialog.py`
- **CodeEditorDialog**: Full-featured modal code editing environment
- Embedded Python code editor with syntax highlighting
- Function signature parsing and validation
- Integration with node pin generation system
- Code formatting and validation tools
- Modal workflow for focused code editing sessions

### `environment_selection_dialog.py`
- **EnvironmentSelectionDialog**: Python environment and virtual environment management
- Detection and listing of available Python environments
- Virtual environment creation and configuration
- Package installation and dependency management
- Environment validation and compatibility checking
- Integration with execution engine for environment switching

### `graph_properties_dialog.py`
- **GraphPropertiesDialog**: Graph metadata and configuration management
- Graph title, description, and documentation editing
- Metadata management for graph files
- Author information and version tracking
- Graph-level settings and preferences
- Export and sharing configuration options

### `group_creation_dialog.py`
- **GroupCreationDialog**: Node group creation and configuration interface
- Group naming and description setup
- Node selection and grouping validation
- Interface pin configuration for groups
- Group boundary and layout options
- Integration with group management system

### `node_properties_dialog.py`
- **NodePropertiesDialog**: Individual node property editing and configuration
- Node naming and description management
- Function signature editing and validation
- Pin configuration and type management
- Node-specific settings and behavior options
- Integration with code editor for function editing

### `settings_dialog.py`
- **SettingsDialog**: Application-wide settings and preferences management
- User interface theme and appearance settings
- Editor configuration and code formatting preferences
- Execution engine settings and timeout configuration
- File handling and auto-save preferences
- Keyboard shortcut customization and management

### `undo_history_dialog.py`
- **UndoHistoryDialog**: Visual undo/redo history and command management
- Graphical representation of command history
- Visual browsing of undo/redo stack
- Command details and impact visualization
- Selective undo/redo operations
- History branching and merge conflict resolution

## Features

### Modal Workflow Design
- **Focused Interfaces**: Each dialog provides a specialized, distraction-free environment
- **Validation Systems**: Real-time input validation and error feedback
- **Help Integration**: Context-sensitive help and documentation
- **Consistent Styling**: Unified appearance matching the main application

### Professional Functionality
- **Advanced Editors**: Rich text editing with syntax highlighting where appropriate
- **Smart Defaults**: Intelligent default values and auto-completion
- **Error Prevention**: Input validation and constraint checking
- **Batch Operations**: Support for bulk editing and configuration

### Integration Features
- **Command System**: Full integration with undo/redo functionality
- **Real-time Updates**: Live preview of changes where applicable
- **Cross-Dialog Communication**: Coordinated workflows between related dialogs
- **State Persistence**: Remembers user preferences and dialog states

## Dependencies

- **PySide6**: Qt dialog widgets and modal interface components
- **Core Module**: Integration with nodes, graphs, and system components
- **Commands Module**: Undo/redo support for dialog operations
- **Code Editing Module**: Embedded code editors in relevant dialogs

## Usage Notes

- All dialogs support standard keyboard shortcuts and accessibility features
- Modal design ensures focused user attention and prevents incomplete operations
- Validation systems provide immediate feedback on input errors
- Integration with main application ensures consistent data handling
- Professional styling maintains visual consistency across the application

## Dialog Categories

### Editing Dialogs
- **Code Editor**: Advanced Python code editing with full IDE features
- **Node Properties**: Comprehensive node configuration and customization
- **Graph Properties**: High-level graph metadata and settings management

### Configuration Dialogs
- **Settings**: Application-wide preferences and behavior configuration
- **Environment Selection**: Python environment management and setup
- **Group Creation**: Node grouping and organization tools

### Management Dialogs
- **Undo History**: Visual command history and selective undo/redo
- **Advanced Workflows**: Support for complex multi-step operations

## Architecture Integration

The dialogs module provides essential focused interfaces that complement PyFlowGraph's main editor. By offering specialized modal workflows, it enables complex operations while maintaining the simplicity and clarity of the primary visual interface.
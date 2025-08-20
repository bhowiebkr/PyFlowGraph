# UI Module

This module contains all user interface components for PyFlowGraph's visual node editor. It provides a comprehensive PySide6-based interface including code editing, dialog systems, and the main editor environment with professional desktop application features.

## Purpose

The UI module delivers PyFlowGraph's complete graphical user interface, implementing a modern, intuitive node editor with advanced code editing capabilities. It provides the visual layer that makes node-based programming accessible and efficient for users of all skill levels.

## Subfolders

### `code_editing/`
Python code editor with syntax highlighting and smart editing features:
- **python_code_editor.py**: Main code editor widget with line numbers and smart indentation
- **python_syntax_highlighter.py**: Real-time Python syntax highlighting implementation

### `dialogs/`
Modal dialog windows for various application functions:
- **code_editor_dialog.py**: Full-featured code editing dialog for node functions
- **environment_selection_dialog.py**: Python environment and virtual environment selection
- **graph_properties_dialog.py**: Graph metadata and properties configuration
- **group_creation_dialog.py**: Node group creation and configuration
- **node_properties_dialog.py**: Individual node property editing and configuration
- **settings_dialog.py**: Application-wide settings and preferences
- **undo_history_dialog.py**: Visual undo/redo history and command management

### `editor/`
Main editor interface and view management:
- **node_editor_window.py**: Primary application window with menus, toolbars, and docking
- **node_editor_view.py**: Graphics view handling mouse/keyboard interactions and viewport management
- **view_state_manager.py**: View state management for zoom, pan, and navigation

### `utils/`
User interface utility functions and helpers:
- **ui_utils.py**: Common UI operations, styling helpers, and widget utilities

## Key Files

### `__init__.py`
Standard Python package initialization file.

## Features

### Professional Interface
- **Modern Design**: Clean, professional interface following modern UI conventions
- **Docking System**: Flexible layout with dockable panels and toolbars
- **Menu System**: Comprehensive menu structure with keyboard shortcuts
- **Toolbar Access**: Quick access to common operations via customizable toolbars

### Advanced Editing
- **Code Editor**: Full-featured Python code editor with syntax highlighting
- **Smart Indentation**: Automatic indentation and code formatting
- **Line Numbers**: Professional code editing with line number display
- **Find/Replace**: Advanced text search and replacement capabilities

### Interactive Dialogs
- **Modal Workflows**: Professional dialog system for complex operations
- **Property Editing**: Detailed property sheets for nodes and graphs
- **Configuration**: Comprehensive settings management
- **Visual History**: Graphical undo/redo history browser

### Responsive Design
- **Scalable Interface**: Adapts to different screen sizes and DPI settings
- **Zoom Controls**: Smooth zooming and panning in the node editor
- **Navigation**: Intuitive navigation with keyboard and mouse support
- **State Persistence**: Remembers window layouts and user preferences

## Dependencies

- **PySide6**: Qt framework for cross-platform GUI development
- **Core Module**: Integrates with node system for visual representation
- **Commands Module**: Provides undo/redo functionality for UI operations
- **Resources Module**: Uses Font Awesome icons for professional appearance

## Usage Notes

- All UI components follow Qt's signal/slot architecture for clean event handling
- Interface supports both mouse and keyboard-driven workflows
- Dialogs provide validation and error handling for user input
- View management enables smooth navigation of large node graphs
- Professional styling with custom CSS and Font Awesome icons

## Architecture Integration

The UI module serves as PyFlowGraph's complete user interface layer, providing an intuitive and powerful visual environment for node-based programming. It bridges the gap between complex functionality and user accessibility, ensuring that advanced features remain approachable through thoughtful interface design.
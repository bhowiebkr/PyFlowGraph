# Editor Module

This module contains the core editor interface components that form PyFlowGraph's main visual editing environment. It implements the primary application window, graphics view system, and view state management for professional node-based visual programming.

## Purpose

The editor module provides PyFlowGraph's central editing interface, implementing a professional desktop application environment with advanced graphics capabilities, intuitive navigation, and comprehensive view management for complex node graphs.

## Key Files

### `__init__.py`
Standard Python package initialization file.

### `node_editor_window.py`
- **NodeEditorWindow**: Primary application window and main interface
- Complete menu system with file, edit, view, and tools menus
- Professional toolbar with quick access to common operations
- Dockable panels for tools, properties, and information display
- Status bar with real-time information and progress indicators
- Window management including save/restore of layout preferences
- Integration point for all major application subsystems

### `node_editor_view.py`
- **NodeEditorView**: Advanced QGraphicsView for node graph visualization
- Smooth pan and zoom with configurable zoom limits and behavior
- Professional mouse and keyboard interaction handling
- Selection management with rubber-band selection and multi-select
- Copy, paste, and duplicate operations with intelligent positioning
- Context menu system for right-click operations
- Drag-and-drop support for nodes and external content
- View transformation and coordinate system management

### `view_state_manager.py`
- **ViewStateManager**: Comprehensive view state management and persistence
- Zoom level tracking and restoration across sessions
- Pan position memory and intelligent view centering
- Selection state preservation during view changes
- View mode management (fit to window, actual size, custom zoom)
- Animation support for smooth view transitions
- Performance optimization for large graph rendering

## Features

### Professional Interface
- **Modern Window Design**: Clean, professional application window with standard desktop conventions
- **Flexible Layout**: Dockable panels and customizable interface layout
- **Menu Integration**: Comprehensive menu system with keyboard shortcuts
- **Toolbar Access**: Quick access toolbar with customizable button sets

### Advanced Graphics
- **Smooth Navigation**: Fluid pan and zoom with optimized performance
- **High-Quality Rendering**: Anti-aliased graphics with scalable vector elements
- **Interactive Selection**: Professional selection tools with visual feedback
- **Context Awareness**: Right-click context menus appropriate to selected objects

### View Management
- **State Persistence**: Automatic saving and restoration of view preferences
- **Intelligent Centering**: Smart view positioning for optimal graph visibility
- **Zoom Controls**: Professional zoom management with fit-to-view options
- **Performance Optimization**: Efficient rendering for large and complex graphs

### User Experience
- **Responsive Interface**: Immediate feedback for all user interactions
- **Keyboard Navigation**: Complete keyboard support for power users
- **Mouse Integration**: Intuitive mouse controls with standard conventions
- **Accessibility**: Support for accessibility features and high-DPI displays

## Dependencies

- **PySide6**: Qt framework for professional desktop application interface
- **Core Module**: Integration with node graph system for visual representation
- **Commands Module**: Undo/redo support for all editor operations
- **UI Utils**: Common interface utilities and styling helpers

## Usage Notes

- Graphics view uses scene/view architecture for efficient large graph handling
- All user interactions generate appropriate commands for undo/redo support
- View state is automatically preserved and restored between application sessions
- Interface supports both mouse-driven and keyboard-driven workflows
- Professional styling with consistent visual design throughout

## Navigation Features

### Mouse Controls
- **Pan**: Middle mouse drag or Shift+left drag for smooth panning
- **Zoom**: Mouse wheel for precise zoom control with focus point awareness
- **Selection**: Left click and drag for rubber-band selection
- **Context Menus**: Right-click for context-appropriate operation menus

### Keyboard Controls
- **Arrow Keys**: Precise node positioning and selection navigation
- **Zoom Shortcuts**: Keyboard shortcuts for common zoom operations
- **Selection**: Keyboard selection management with Shift and Ctrl modifiers
- **Operations**: Full keyboard access to editing operations

### View Modes
- **Fit to View**: Automatically adjusts zoom to show entire graph
- **Actual Size**: 1:1 zoom ratio for precise editing
- **Custom Zoom**: User-defined zoom levels with percentage display
- **Smart Centering**: Intelligent view positioning based on content

## Architecture Integration

The editor module serves as PyFlowGraph's primary user interface, providing the visual environment where all node-based programming activities take place. It integrates all application subsystems into a cohesive, professional editing experience that supports both simple and complex visual programming workflows.
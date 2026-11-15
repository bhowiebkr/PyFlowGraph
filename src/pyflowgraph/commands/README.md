# Commands Module

This module implements the Command pattern for undo/redo functionality in PyFlowGraph. All user actions that modify the node graph are encapsulated as commands that can be executed, undone, and redone.

## Purpose

The commands module provides a robust undo/redo system by implementing the Command design pattern. Each user action (creating nodes, making connections, moving objects) is wrapped in a command object that knows how to execute itself and how to reverse its effects.

## Key Files

### `__init__.py`
Standard Python package initialization file.

### `command_base.py`
- **CommandBase**: Abstract base class defining the command interface
- **CompositeCommand**: Container for grouping multiple commands into a single undoable action
- Provides the foundation for all command implementations

### `command_history.py`
- Manages the undo/redo stack
- Tracks command execution history
- Handles command grouping and batch operations
- Provides undo/redo state management

### `connection_commands.py`
Commands related to connection operations:
- Creating connections between pins
- Deleting connections
- Rerouting connections through reroute nodes
- Connection validation and error handling

### `create_group_command.py`
Commands for group management:
- Creating node groups from selected nodes
- Managing group boundaries and interfaces
- Group creation validation and setup

### `node_commands.py`
Commands for node operations:
- Creating new nodes
- Deleting nodes
- Moving nodes
- Modifying node properties
- Node position and state management

### `resize_group_command.py`
Commands specific to group resizing:
- Resizing group boundaries
- Maintaining group interface consistency
- Validating group size constraints

## Dependencies

- **Core Module**: Commands operate on core objects (nodes, pins, connections, groups)
- **Event System**: Commands may trigger events for UI updates
- **Node Graph**: Commands modify the main graph scene

## Usage Notes

- All commands inherit from `CommandBase` and implement `execute()` and `undo()` methods
- Commands are automatically added to the command history when executed
- Composite commands allow grouping related operations for single undo/redo
- Commands handle their own validation and error states
- The command system supports both immediate execution and deferred execution patterns

## Architecture Integration

The command system is central to PyFlowGraph's user interaction model, ensuring that all graph modifications can be undone and redone reliably. This provides a professional editing experience and prevents data loss from user mistakes.
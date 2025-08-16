# PyFlowGraph Technical Architecture
## Command Pattern Implementation & Node Grouping System

### Document Information
- **Version**: 1.0
- **Date**: 2025-08-16
- **Author**: Winston, System Architect
- **Status**: Design Phase
- **Related Documents**: PyFlowGraph PRD v1.0

---

## Executive Summary

This document defines the technical architecture for implementing Command Pattern-based undo/redo functionality and Node Grouping system in PyFlowGraph. The design maintains backward compatibility with existing PySide6 architecture while delivering 40-60% reduction in error recovery time and 5-10x larger graph management capabilities.

**Key Architecture Decisions:**
- Command Pattern implementation integrated into existing NodeGraph operations
- Hierarchical grouping system using Qt's QGraphicsItemGroup with custom extensions
- Memory-efficient command history with configurable depth (default 50, max 200)
- Backward-compatible file format extensions preserving existing .md workflow

---

## Current Architecture Analysis

### Core Application Structure

PyFlowGraph follows a layered desktop application architecture built on PySide6:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
├─────────────────────────────────────────────────────────────┤
│ NodeEditorWindow (QMainWindow)                              │
│ ├── NodeEditorView (QGraphicsView)                          │
│ ├── CodeEditorDialog (Modal)                               │
│ ├── NodePropertiesDialog                                   │
│ └── Various Dock Widgets                                   │
├─────────────────────────────────────────────────────────────┤
│                     Business Logic Layer                    │
├─────────────────────────────────────────────────────────────┤
│ NodeGraph (QGraphicsScene)                                 │
│ ├── Node Management (create_node, remove_node)             │
│ ├── Connection Management (create_connection, remove_connection) │
│ ├── Serialization (serialize, deserialize)                 │
│ └── Clipboard Operations (copy_selected, paste)            │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                          │
├─────────────────────────────────────────────────────────────┤
│ Node (QGraphicsItem) - Pin generation from Python parsing  │
│ Connection (QGraphicsItem) - Bezier curve connections      │
│ Pin (QGraphicsItem) - Type-safe connection points          │
│ RerouteNode (QGraphicsItem) - Connection organization      │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                     │
├─────────────────────────────────────────────────────────────┤
│ GraphExecutor - Subprocess isolation & execution           │
│ FlowFormat - Markdown serialization                        │
│ EventSystem - Event-driven execution                       │
│ FileOperations - File I/O management                       │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points for New Features

**Primary Integration Point: NodeGraph (src/node_graph.py)**
- Central hub for all graph operations
- Current methods provide natural command implementation points:
  - `create_node()` → CreateNodeCommand
  - `remove_node()` → DeleteNodeCommand  
  - `create_connection()` → CreateConnectionCommand
  - `remove_connection()` → DeleteConnectionCommand

**Secondary Integration Points:**
- **NodeEditorWindow**: Menu integration, keyboard shortcuts, UI controls
- **FlowFormat**: File format extensions for group metadata
- **Node/Connection classes**: Enhanced serialization for state preservation

---

## Command Pattern Infrastructure

### Architecture Overview

The Command Pattern implementation provides a robust, extensible foundation for undo/redo functionality while integrating seamlessly with existing NodeGraph operations.

```
┌─────────────────────────────────────────────────────────────┐
│                    Command Pattern Architecture             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   CommandBase   │    │ CommandHistory  │                │
│  │   (Abstract)    │    │   (Manager)     │                │
│  │                 │    │                 │                │
│  │ + execute()     │    │ - commands[]    │                │
│  │ + undo()        │    │ - current_index │                │
│  │ + get_desc()    │    │ - max_depth     │                │
│  └─────────────────┘    │                 │                │
│           ▲              │ + execute_cmd() │                │
│           │              │ + undo()        │                │
│           │              │ + redo()        │                │
│  ┌─────────────────┐    │ + clear()       │                │
│  │ Concrete Commands│    └─────────────────┘                │
│  │                 │                                        │
│  │ CreateNodeCmd   │    ┌─────────────────┐                │
│  │ DeleteNodeCmd   │    │   NodeGraph     │                │
│  │ MoveNodeCmd     │    │   (Modified)    │                │
│  │ CreateConnCmd   │    │                 │                │
│  │ DeleteConnCmd   │    │ + command_hist  │                │
│  │ PropertyCmd     │    │ + execute_cmd() │                │
│  │ CodeChangeCmd   │    │                 │                │
│  │ CompositeCmd    │    │ [integrate all  │                │
│  │ GroupCmd        │    │  operations]    │                │
│  │ UngroupCmd      │    └─────────────────┘                │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

### Core Command Pattern Classes

#### CommandBase (Abstract Base Class)
```python
# src/commands/command_base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class CommandBase(ABC):
    """Abstract base class for all undoable commands."""
    
    def __init__(self, description: str):
        self.description = description
        self.timestamp = time.time()
        self._executed = False
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command. Returns True if successful."""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command. Returns True if successful."""
        pass
    
    def get_description(self) -> str:
        """Get human-readable description for UI display."""
        return self.description
    
    def can_merge_with(self, other: 'CommandBase') -> bool:
        """Check if this command can be merged with another."""
        return False
    
    def merge_with(self, other: 'CommandBase') -> Optional['CommandBase']:
        """Merge with another command if possible."""
        return None
```

#### CommandHistory (Command Manager)
```python
# src/commands/command_history.py
from typing import List, Optional
from .command_base import CommandBase

class CommandHistory:
    """Manages command execution history and undo/redo operations."""
    
    def __init__(self, max_depth: int = 50):
        self.commands: List[CommandBase] = []
        self.current_index: int = -1
        self.max_depth = max_depth
        self._memory_usage = 0
        self._memory_limit = 50 * 1024 * 1024  # 50MB as per NFR3
    
    def execute_command(self, command: CommandBase) -> bool:
        """Execute a command and add to history."""
        if not command.execute():
            return False
        
        # Remove any commands ahead of current position
        if self.current_index < len(self.commands) - 1:
            self.commands = self.commands[:self.current_index + 1]
        
        # Add command to history
        self.commands.append(command)
        self.current_index += 1
        
        # Maintain depth limit and memory constraints
        self._enforce_limits()
        return True
    
    def undo(self) -> Optional[str]:
        """Undo the last command. Returns description if successful."""
        if not self.can_undo():
            return None
        
        command = self.commands[self.current_index]
        if command.undo():
            self.current_index -= 1
            return command.get_description()
        return None
    
    def redo(self) -> Optional[str]:
        """Redo the next command. Returns description if successful."""
        if not self.can_redo():
            return None
        
        command = self.commands[self.current_index + 1]
        if command.execute():
            self.current_index += 1
            return command.get_description()
        return None
    
    def can_undo(self) -> bool:
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        return self.current_index < len(self.commands) - 1
    
    def _enforce_limits(self):
        """Enforce depth and memory limits."""
        # Remove oldest commands if over depth limit
        while len(self.commands) > self.max_depth:
            removed = self.commands.pop(0)
            self.current_index -= 1
            self._memory_usage -= self._estimate_command_size(removed)
        
        # Enforce memory limit (NFR3)
        while (self._memory_usage > self._memory_limit and 
               len(self.commands) > 0):
            removed = self.commands.pop(0)
            self.current_index -= 1
            self._memory_usage -= self._estimate_command_size(removed)
```

### Specific Command Implementations

#### Node Operations
```python
# src/commands/node_commands.py
class CreateNodeCommand(CommandBase):
    """Command for creating nodes with full state preservation."""
    
    def __init__(self, node_graph, node_type: str, position: QPointF, 
                 node_id: str = None):
        super().__init__(f"Create {node_type} node")
        self.node_graph = node_graph
        self.node_type = node_type
        self.position = position
        self.node_id = node_id or self._generate_id()
        self.created_node = None
    
    def execute(self) -> bool:
        """Create the node and add to graph."""
        self.created_node = self.node_graph._create_node_internal(
            self.node_type, self.position, self.node_id)
        return self.created_node is not None
    
    def undo(self) -> bool:
        """Remove the created node."""
        if self.created_node and self.created_node in self.node_graph.nodes:
            self.node_graph._remove_node_internal(self.created_node)
            return True
        return False

class DeleteNodeCommand(CommandBase):
    """Command for deleting nodes with complete state preservation."""
    
    def __init__(self, node_graph, node):
        super().__init__(f"Delete {node.title}")
        self.node_graph = node_graph
        self.node = node
        self.node_state = None
        self.affected_connections = []
    
    def execute(self) -> bool:
        """Delete node after preserving complete state."""
        # Preserve full node state
        self.node_state = {
            'id': self.node.id,
            'position': self.node.pos(),
            'title': self.node.title,
            'code': self.node.code,
            'properties': self.node.get_properties(),
            'pin_data': self.node.serialize_pins()
        }
        
        # Preserve affected connections
        self.affected_connections = []
        for conn in list(self.node_graph.connections):
            if (conn.output_pin.node == self.node or 
                conn.input_pin.node == self.node):
                self.affected_connections.append({
                    'connection': conn,
                    'output_node_id': conn.output_pin.node.id,
                    'output_pin_index': conn.output_pin.index,
                    'input_node_id': conn.input_pin.node.id,
                    'input_pin_index': conn.input_pin.index
                })
        
        # Perform deletion
        self.node_graph._remove_node_internal(self.node)
        return True
    
    def undo(self) -> bool:
        """Restore node with complete state and reconnections."""
        # Recreate node with preserved state
        restored_node = self.node_graph._create_node_internal(
            self.node_state['title'], 
            self.node_state['position'],
            self.node_state['id']
        )
        
        if not restored_node:
            return False
        
        # Restore node properties
        restored_node.code = self.node_state['code']
        restored_node.set_properties(self.node_state['properties'])
        restored_node.deserialize_pins(self.node_state['pin_data'])
        
        # Restore connections
        for conn_data in self.affected_connections:
            output_node = self.node_graph.get_node_by_id(
                conn_data['output_node_id'])
            input_node = self.node_graph.get_node_by_id(
                conn_data['input_node_id'])
            
            if output_node and input_node:
                self.node_graph._create_connection_internal(
                    output_node.output_pins[conn_data['output_pin_index']],
                    input_node.input_pins[conn_data['input_pin_index']]
                )
        
        return True
```

#### Composite Commands for Complex Operations
```python
# src/commands/composite_command.py
class CompositeCommand(CommandBase):
    """Command that groups multiple operations as single undo unit."""
    
    def __init__(self, description: str, commands: List[CommandBase]):
        super().__init__(description)
        self.commands = commands
        self.executed_commands = []
    
    def execute(self) -> bool:
        """Execute all commands, rolling back on failure."""
        self.executed_commands = []
        
        for command in self.commands:
            if command.execute():
                self.executed_commands.append(command)
            else:
                # Rollback executed commands
                for executed in reversed(self.executed_commands):
                    executed.undo()
                return False
        
        return True
    
    def undo(self) -> bool:
        """Undo all executed commands in reverse order."""
        success = True
        for command in reversed(self.executed_commands):
            if not command.undo():
                success = False
        return success
```

---

## Node Grouping System Architecture

### Hierarchical Group Structure

The Node Grouping system creates a hierarchical abstraction layer enabling management of complex graphs through collapsible containers while maintaining full compatibility with existing execution and serialization systems.

```
┌─────────────────────────────────────────────────────────────┐
│                 Node Grouping Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   NodeGroup     │    │  GroupManager   │                │
│  │ (QGraphicsItem) │    │   (Controller)  │                │
│  │                 │    │                 │                │
│  │ + child_nodes[] │    │ + groups[]      │                │
│  │ + interface_pins│    │ + depth_limit   │                │
│  │ + is_collapsed  │    │                 │                │
│  │ + group_bounds  │    │ + create_group()│                │
│  │                 │    │ + expand_group()│                │
│  │ + collapse()    │    │ + validate_sel()│                │
│  │ + expand()      │    │ + check_cycles()│                │
│  │ + generate_pins()│   │ + save_template()│               │
│  └─────────────────┘    └─────────────────┘                │
│           ▲                                                 │
│           │                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   GroupPin      │    │ GroupTemplate   │                │
│  │   (Special)     │    │   (Serialized)  │                │
│  │                 │    │                 │                │
│  │ + internal_conn │    │ + metadata      │                │
│  │ + external_conn │    │ + node_data[]   │                │
│  │ + pin_type      │    │ + interface_def │                │
│  └─────────────────┘    │ + version       │                │
│                         └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Core Group Classes

#### NodeGroup (Primary Container)
```python
# src/grouping/node_group.py
from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsItem
from PySide6.QtCore import QRectF, QPointF
from typing import List, Dict, Any, Optional

class NodeGroup(QGraphicsItemGroup):
    """Hierarchical container for organizing nodes into manageable groups."""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__()
        self.group_id = self._generate_id()
        self.name = name
        self.description = description
        self.is_collapsed = False
        self.depth_level = 0
        self.max_depth = 10  # NFR7 requirement
        
        # Child management
        self.child_nodes: List[QGraphicsItem] = []
        self.child_groups: List['NodeGroup'] = []
        self.parent_group: Optional['NodeGroup'] = None
        
        # Interface pins for external connectivity
        self.interface_pins: List['GroupPin'] = []
        self.external_connections: List[Dict] = []
        
        # Visual properties
        self.group_bounds = QRectF()
        self.collapsed_size = QSizeF(200, 100)
        self.expanded_bounds = QRectF()
        
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
    
    def add_child_node(self, node) -> bool:
        """Add node to group with validation."""
        if self._would_create_cycle(node):
            return False
        
        self.child_nodes.append(node)
        self.addToGroup(node)
        node.parent_group = self
        self._update_bounds()
        return True
    
    def add_child_group(self, group: 'NodeGroup') -> bool:
        """Add nested group with depth validation."""
        if self.depth_level + 1 >= self.max_depth:
            return False
        
        if self._would_create_cycle(group):
            return False
        
        self.child_groups.append(group)
        group.parent_group = self
        group.depth_level = self.depth_level + 1
        self.addToGroup(group)
        self._update_bounds()
        return True
    
    def collapse(self) -> bool:
        """Collapse group to single node representation."""
        if self.is_collapsed:
            return True
        
        # Store expanded positions
        self.expanded_bounds = self.group_bounds
        for node in self.child_nodes:
            node.expanded_position = node.pos()
        
        # Generate interface pins
        self._generate_interface_pins()
        
        # Hide internal nodes
        for node in self.child_nodes:
            node.setVisible(False)
        for group in self.child_groups:
            group.setVisible(False)
        
        # Set collapsed visual state
        self.is_collapsed = True
        self._update_collapsed_appearance()
        return True
    
    def expand(self) -> bool:
        """Expand group to show internal nodes."""
        if not self.is_collapsed:
            return True
        
        # Restore node positions
        for node in self.child_nodes:
            if hasattr(node, 'expanded_position'):
                node.setPos(node.expanded_position)
            node.setVisible(True)
        
        for group in self.child_groups:
            group.setVisible(True)
        
        # Restore interface connections
        self._restore_internal_connections()
        
        self.is_collapsed = False
        self._update_expanded_appearance()
        return True
    
    def _generate_interface_pins(self):
        """Analyze external connections and generate interface pins."""
        self.interface_pins.clear()
        self.external_connections.clear()
        
        input_types = {}
        output_types = {}
        
        # Analyze all connections crossing group boundary
        for node in self.child_nodes:
            for pin in node.input_pins:
                for conn in pin.connections:
                    if conn.output_pin.node not in self.child_nodes:
                        # External input connection
                        pin_type = pin.pin_type
                        if pin_type not in input_types:
                            input_types[pin_type] = []
                        input_types[pin_type].append({
                            'connection': conn,
                            'internal_pin': pin,
                            'external_pin': conn.output_pin
                        })
            
            for pin in node.output_pins:
                for conn in pin.connections:
                    if conn.input_pin.node not in self.child_nodes:
                        # External output connection
                        pin_type = pin.pin_type
                        if pin_type not in output_types:
                            output_types[pin_type] = []
                        output_types[pin_type].append({
                            'connection': conn,
                            'internal_pin': pin,
                            'external_pin': conn.input_pin
                        })
        
        # Create interface pins
        for pin_type, connections in input_types.items():
            interface_pin = GroupPin(self, 'input', pin_type, connections)
            self.interface_pins.append(interface_pin)
        
        for pin_type, connections in output_types.items():
            interface_pin = GroupPin(self, 'output', pin_type, connections)
            self.interface_pins.append(interface_pin)
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize group for file persistence."""
        return {
            'group_id': self.group_id,
            'name': self.name,
            'description': self.description,
            'is_collapsed': self.is_collapsed,
            'depth_level': self.depth_level,
            'group_bounds': {
                'x': self.group_bounds.x(),
                'y': self.group_bounds.y(),
                'width': self.group_bounds.width(),
                'height': self.group_bounds.height()
            },
            'child_node_ids': [node.id for node in self.child_nodes],
            'child_group_ids': [group.group_id for group in self.child_groups],
            'interface_pins': [pin.serialize() for pin in self.interface_pins],
            'external_connections': self.external_connections
        }
```

#### GroupPin (Interface Connectivity)
```python
# src/grouping/group_pin.py
class GroupPin:
    """Special pin type for group external interface."""
    
    def __init__(self, parent_group: NodeGroup, direction: str, 
                 pin_type: str, connections: List[Dict]):
        self.parent_group = parent_group
        self.direction = direction  # 'input' or 'output'
        self.pin_type = pin_type
        self.internal_connections = connections
        self.position = QPointF()
        self.external_connection = None
    
    def connect_external(self, external_pin) -> bool:
        """Connect this interface pin to external node."""
        if not self._validate_connection(external_pin):
            return False
        
        self.external_connection = external_pin
        
        # Route through to internal connections
        for conn_data in self.internal_connections:
            internal_pin = conn_data['internal_pin']
            original_conn = conn_data['connection']
            
            # Create new connection from external pin to internal pin
            if self.direction == 'input':
                new_conn = Connection(external_pin, internal_pin)
            else:
                new_conn = Connection(internal_pin, external_pin)
            
            # Update node graph
            self.parent_group.scene().create_connection(new_conn)
        
        return True
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize interface pin data."""
        return {
            'direction': self.direction,
            'pin_type': self.pin_type,
            'position': {'x': self.position.x(), 'y': self.position.y()},
            'internal_connections': [
                {
                    'node_id': conn['internal_pin'].node.id,
                    'pin_index': conn['internal_pin'].index,
                    'external_node_id': conn['external_pin'].node.id,
                    'external_pin_index': conn['external_pin'].index
                }
                for conn in self.internal_connections
            ]
        }
```

#### GroupManager (Central Controller)
```python
# src/grouping/group_manager.py
class GroupManager:
    """Central controller for all group operations and validation."""
    
    def __init__(self, node_graph):
        self.node_graph = node_graph
        self.groups: List[NodeGroup] = []
        self.max_depth = 10
        self.group_templates: Dict[str, 'GroupTemplate'] = {}
    
    def create_group(self, selected_nodes: List, name: str, 
                    description: str = "") -> Optional[NodeGroup]:
        """Create new group from selected nodes with validation."""
        # Validation (FR5)
        if not self._validate_group_creation(selected_nodes):
            return None
        
        # Create group
        group = NodeGroup(name, description)
        
        # Add nodes to group
        for node in selected_nodes:
            if not group.add_child_node(node):
                return None
        
        # Generate interface pins (FR6)
        group._generate_interface_pins()
        
        # Add to management
        self.groups.append(group)
        self.node_graph.addItem(group)
        
        return group
    
    def expand_group(self, group: NodeGroup) -> bool:
        """Expand group with position restoration (FR8)."""
        if not group.is_collapsed:
            return True
        
        return group.expand()
    
    def save_group_template(self, group: NodeGroup, 
                          metadata: Dict[str, Any]) -> bool:
        """Save group as reusable template (FR9)."""
        template = GroupTemplate(group, metadata)
        
        if not template.validate():
            return False
        
        template_id = f"{metadata['name']}_{metadata['version']}"
        self.group_templates[template_id] = template
        
        # Persist to file system
        return template.save_to_file()
    
    def _validate_group_creation(self, nodes: List) -> bool:
        """Validate group creation preventing circular dependencies."""
        if len(nodes) < 2:
            return False
        
        # Check for existing group membership conflicts
        for node in nodes:
            if hasattr(node, 'parent_group') and node.parent_group:
                return False
        
        # Check for circular dependencies
        return not self._would_create_circular_dependency(nodes)
    
    def _would_create_circular_dependency(self, nodes: List) -> bool:
        """Check if grouping would create circular dependency."""
        # Implement cycle detection algorithm
        # This is simplified - real implementation would use DFS
        visited = set()
        for node in nodes:
            if self._has_cycle_from_node(node, visited, nodes):
                return True
        return False
```

---

## PySide6 Integration Strategy

### UI Component Integration

The architecture leverages existing PySide6 patterns while adding new UI components for undo/redo and grouping functionality.

#### Menu Integration
```python
# src/node_editor_window.py - Enhanced menu system
class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.command_history = CommandHistory()
        self.group_manager = GroupManager(self.node_graph)
        self._setup_enhanced_menus()
    
    def _setup_enhanced_menus(self):
        """Setup menus with undo/redo and grouping support."""
        edit_menu = self.menuBar().addMenu("Edit")
        
        # Undo/Redo actions
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self.undo_operation)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.triggered.connect(self.redo_operation)
        
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        
        # Grouping actions
        self.group_action = QAction("Group Selected", self)
        self.group_action.setShortcut(QKeySequence("Ctrl+G"))
        self.group_action.triggered.connect(self.create_group)
        
        self.ungroup_action = QAction("Ungroup", self)
        self.ungroup_action.setShortcut(QKeySequence("Ctrl+Shift+G"))
        self.ungroup_action.triggered.connect(self.ungroup_selected)
        
        edit_menu.addAction(self.group_action)
        edit_menu.addAction(self.ungroup_action)
    
    def undo_operation(self):
        """Execute undo with UI feedback."""
        description = self.command_history.undo()
        if description:
            self.statusBar().showMessage(f"Undid: {description}", 2000)
        self._update_menu_states()
    
    def redo_operation(self):
        """Execute redo with UI feedback."""
        description = self.command_history.redo()
        if description:
            self.statusBar().showMessage(f"Redid: {description}", 2000)
        self._update_menu_states()
    
    def _update_menu_states(self):
        """Update menu item enabled states."""
        self.undo_action.setEnabled(self.command_history.can_undo())
        self.redo_action.setEnabled(self.command_history.can_redo())
        
        # Update descriptions with next operation
        if self.command_history.can_undo():
            next_undo = self.command_history.get_undo_description()
            self.undo_action.setText(f"Undo {next_undo}")
        else:
            self.undo_action.setText("Undo")
```

#### Specialized UI Dialogs
```python
# src/ui/undo_history_dialog.py
class UndoHistoryDialog(QDialog):
    """Visual undo history timeline (FR4)."""
    
    def __init__(self, command_history: CommandHistory, parent=None):
        super().__init__(parent)
        self.command_history = command_history
        self.setWindowTitle("Undo History")
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # History list
        self.history_list = QListWidget()
        self._populate_history()
        layout.addWidget(self.history_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.undo_to_button = QPushButton("Undo To Selected")
        self.undo_to_button.clicked.connect(self._undo_to_selected)
        button_layout.addWidget(self.undo_to_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)

# src/ui/group_creation_dialog.py
class GroupCreationDialog(QDialog):
    """Dialog for group creation with metadata input."""
    
    def __init__(self, selected_nodes: List, parent=None):
        super().__init__(parent)
        self.selected_nodes = selected_nodes
        self.setWindowTitle("Create Node Group")
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QFormLayout(self)
        
        # Group name
        self.name_edit = QLineEdit()
        self.name_edit.setText(f"Group_{len(self.selected_nodes)}_nodes")
        layout.addRow("Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        layout.addRow("Description:", self.description_edit)
        
        # Preview selected nodes
        preview_label = QLabel(f"Selected Nodes ({len(self.selected_nodes)}):")
        layout.addRow(preview_label)
        
        node_list = QListWidget()
        node_list.setMaximumHeight(100)
        for node in self.selected_nodes:
            node_list.addItem(f"{node.title} (ID: {node.id})")
        layout.addRow(node_list)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
```

### Enhanced NodeGraph Integration
```python
# src/node_graph.py - Modified for command integration
class NodeGraph(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.command_history = CommandHistory()
        self.group_manager = GroupManager(self)
        # ... existing initialization
    
    def execute_command(self, command: CommandBase) -> bool:
        """Central command execution with history tracking."""
        success = self.command_history.execute_command(command)
        if success:
            self.commandExecuted.emit(command.get_description())
        return success
    
    def create_node(self, node_type: str, position: QPointF) -> bool:
        """Create node via command pattern."""
        command = CreateNodeCommand(self, node_type, position)
        return self.execute_command(command)
    
    def remove_node(self, node) -> bool:
        """Remove node via command pattern."""
        command = DeleteNodeCommand(self, node)
        return self.execute_command(command)
    
    def create_group_from_selection(self) -> Optional[NodeGroup]:
        """Create group from currently selected nodes."""
        selected_nodes = [item for item in self.selectedItems() 
                         if isinstance(item, Node)]
        
        if len(selected_nodes) < 2:
            return None
        
        # Show group creation dialog
        dialog = GroupCreationDialog(selected_nodes)
        if dialog.exec() == QDialog.Accepted:
            command = CreateGroupCommand(
                self.group_manager, 
                selected_nodes,
                dialog.name_edit.text(),
                dialog.description_edit.toPlainText()
            )
            
            if self.execute_command(command):
                return command.created_group
        
        return None
```

---

## Performance Requirements & Optimization

### Performance Architecture Strategy

The architecture addresses specific performance requirements (NFR1-NFR3) through targeted optimization strategies across all system layers.

#### Command History Optimization (NFR1, NFR3)
```python
# src/commands/performance_optimizations.py
class OptimizedCommandHistory(CommandHistory):
    """Performance-optimized command history implementation."""
    
    def __init__(self, max_depth: int = 50):
        super().__init__(max_depth)
        self._memory_monitor = MemoryMonitor(50 * 1024 * 1024)  # 50MB limit
        self._execution_timer = ExecutionTimer()
    
    def execute_command(self, command: CommandBase) -> bool:
        """Execute with performance monitoring."""
        with self._execution_timer.measure() as timer:
            success = super().execute_command(command)
            
            # Verify NFR1: Individual operations < 100ms
            if timer.elapsed_ms() > 100:
                logger.warning(
                    f"Command {command.get_description()} exceeded 100ms: "
                    f"{timer.elapsed_ms():.1f}ms"
                )
            
            return success
    
    def _estimate_command_size(self, command: CommandBase) -> int:
        """Accurate memory estimation for commands."""
        if isinstance(command, DeleteNodeCommand):
            # Estimate based on node complexity
            node_state = command.node_state
            base_size = 1024  # Base overhead
            code_size = len(node_state.get('code', '')) * 2  # Unicode
            props_size = len(str(node_state.get('properties', {}))) * 2
            connections_size = len(command.affected_connections) * 200
            return base_size + code_size + props_size + connections_size
        
        elif isinstance(command, CompositeCommand):
            return sum(self._estimate_command_size(cmd) 
                      for cmd in command.commands)
        
        else:
            return 512  # Conservative estimate for simple commands

class MemoryMonitor:
    """Real-time memory usage monitoring."""
    
    def __init__(self, limit_bytes: int):
        self.limit_bytes = limit_bytes
        self.current_usage = 0
    
    def check_limit(self) -> bool:
        """Check if current usage exceeds limit."""
        return self.current_usage > self.limit_bytes
    
    def add_usage(self, bytes_used: int):
        """Track additional memory usage."""
        self.current_usage += bytes_used
    
    def remove_usage(self, bytes_freed: int):
        """Track freed memory."""
        self.current_usage = max(0, self.current_usage - bytes_freed)
```

#### Group Operations Scaling (NFR2)
```python
# src/grouping/performance_optimized_group.py
class PerformanceOptimizedNodeGroup(NodeGroup):
    """Group implementation optimized for large node counts."""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self._cached_bounds = None
        self._bounds_dirty = True
        self._pin_generation_cache = {}
    
    def add_child_node(self, node) -> bool:
        """Optimized node addition with deferred updates."""
        start_time = time.perf_counter()
        
        success = super().add_child_node(node)
        
        if success:
            # Mark caches as dirty instead of immediate recalculation
            self._bounds_dirty = True
            self._invalidate_pin_cache()
            
            # Verify NFR2: 10ms per node for creation
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            if elapsed_ms > 10:
                logger.warning(
                    f"Node addition exceeded 10ms target: {elapsed_ms:.1f}ms"
                )
        
        return success
    
    def _generate_interface_pins(self):
        """Cached pin generation for performance."""
        cache_key = self._get_pin_cache_key()
        
        if cache_key in self._pin_generation_cache:
            self.interface_pins = self._pin_generation_cache[cache_key]
            return
        
        # Generate pins with optimized algorithm
        start_time = time.perf_counter()
        
        # Use sets for O(1) lookup instead of lists
        internal_node_set = set(self.child_nodes)
        input_connections = {}
        output_connections = {}
        
        # Single pass through all connections
        for node in self.child_nodes:
            for pin in node.input_pins:
                for conn in pin.connections:
                    if conn.output_pin.node not in internal_node_set:
                        pin_type = pin.pin_type
                        if pin_type not in input_connections:
                            input_connections[pin_type] = []
                        input_connections[pin_type].append(conn)
            
            for pin in node.output_pins:
                for conn in pin.connections:
                    if conn.input_pin.node not in internal_node_set:
                        pin_type = pin.pin_type
                        if pin_type not in output_connections:
                            output_connections[pin_type] = []
                        output_connections[pin_type].append(conn)
        
        # Create interface pins
        self.interface_pins = []
        for pin_type, conns in input_connections.items():
            self.interface_pins.append(GroupPin(self, 'input', pin_type, conns))
        for pin_type, conns in output_connections.items():
            self.interface_pins.append(GroupPin(self, 'output', pin_type, conns))
        
        # Cache results
        self._pin_generation_cache[cache_key] = self.interface_pins
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Pin generation took {elapsed_ms:.1f}ms for "
                    f"{len(self.child_nodes)} nodes")
    
    def expand(self) -> bool:
        """Optimized expansion with batch operations."""
        start_time = time.perf_counter()
        
        if not self.is_collapsed:
            return True
        
        # Batch visibility updates to reduce redraws
        self.scene().blockSignals(True)
        
        try:
            # Restore positions in batch
            for node in self.child_nodes:
                if hasattr(node, 'expanded_position'):
                    node.setPos(node.expanded_position)
                node.setVisible(True)
            
            for group in self.child_groups:
                group.setVisible(True)
            
            self.is_collapsed = False
            self._update_expanded_appearance()
            
        finally:
            self.scene().blockSignals(False)
            self.scene().update()  # Single update instead of per-item
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Verify NFR2: 5ms per node for expansion
        target_ms = len(self.child_nodes) * 5
        if elapsed_ms > target_ms:
            logger.warning(
                f"Group expansion exceeded target ({target_ms}ms): "
                f"{elapsed_ms:.1f}ms for {len(self.child_nodes)} nodes"
            )
        
        return True
```

#### Large Graph Optimization (NFR6)
```python
# src/performance/large_graph_optimizations.py
class LargeGraphOptimizer:
    """Optimization strategies for graphs with 1000+ nodes."""
    
    def __init__(self, node_graph):
        self.node_graph = node_graph
        self.viewport_culling = ViewportCulling(node_graph)
        self.level_of_detail = LevelOfDetail(node_graph)
    
    def optimize_for_size(self, node_count: int):
        """Apply size-appropriate optimizations."""
        if node_count > 1000:
            # Activate aggressive optimizations
            self.viewport_culling.enable()
            self.level_of_detail.enable()
            self._enable_render_caching()
            
        elif node_count > 500:
            # Moderate optimizations
            self.viewport_culling.enable()
            self.level_of_detail.set_mode('moderate')
            
        else:
            # Minimal optimizations for small graphs
            self.viewport_culling.disable()
            self.level_of_detail.disable()

class ViewportCulling:
    """Cull items outside visible viewport."""
    
    def __init__(self, node_graph):
        self.node_graph = node_graph
        self.enabled = False
    
    def enable(self):
        """Enable viewport culling."""
        self.enabled = True
        self.node_graph.view.viewportChanged.connect(self._update_visibility)
    
    def _update_visibility(self):
        """Update item visibility based on viewport."""
        if not self.enabled:
            return
        
        visible_rect = self.node_graph.view.mapToScene(
            self.node_graph.view.viewport().rect()).boundingRect()
        
        # Expand visible area for smooth scrolling
        margin = 100
        visible_rect.adjust(-margin, -margin, margin, margin)
        
        for item in self.node_graph.items():
            if isinstance(item, (Node, NodeGroup)):
                item.setVisible(visible_rect.intersects(item.boundingRect()))
```

---

## Backward Compatibility & File Format

### File Format Evolution Strategy

The architecture maintains 100% backward compatibility with existing .md files while extending the format to support new group metadata.

#### Enhanced Flow Format
```python
# src/flow_format.py - Enhanced for grouping support
class EnhancedFlowFormat(FlowFormat):
    """Extended flow format supporting groups while maintaining compatibility."""
    
    FORMAT_VERSION = "1.1"  # Incremental version for new features
    
    def serialize_graph(self, node_graph) -> str:
        """Serialize graph with optional group data."""
        # Generate base markdown (compatible with v1.0)
        base_markdown = super().serialize_graph(node_graph)
        
        # Add group metadata if groups exist
        if node_graph.group_manager.groups:
            group_metadata = self._serialize_groups(node_graph.group_manager.groups)
            base_markdown += "\n\n<!-- GROUP_METADATA_V1.1\n"
            base_markdown += json.dumps(group_metadata, indent=2)
            base_markdown += "\n-->\n"
        
        return base_markdown
    
    def deserialize_graph(self, markdown_content: str, node_graph):
        """Deserialize with group support and version detection."""
        # Extract group metadata if present
        group_metadata = self._extract_group_metadata(markdown_content)
        
        # Remove group metadata for base parsing
        clean_content = self._remove_group_metadata(markdown_content)
        
        # Parse base graph (maintains v1.0 compatibility)
        super().deserialize_graph(clean_content, node_graph)
        
        # Apply group data if available
        if group_metadata:
            self._apply_group_metadata(group_metadata, node_graph)
    
    def _serialize_groups(self, groups: List[NodeGroup]) -> Dict[str, Any]:
        """Serialize group data to metadata format."""
        return {
            'format_version': self.FORMAT_VERSION,
            'groups': [group.serialize() for group in groups],
            'group_hierarchy': self._build_hierarchy_map(groups),
            'compatibility_notes': [
                'This file contains node grouping data',
                'Groups will be ignored when opened in PyFlowGraph < v0.8.0',
                'All node and connection data remains fully compatible'
            ]
        }
    
    def _extract_group_metadata(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract group metadata from markdown comments."""
        import re
        
        pattern = r'<!-- GROUP_METADATA_V[\d\.]+\n(.*?)\n-->'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                logger.warning("Invalid group metadata found, ignoring")
                return None
        
        return None
    
    def _apply_group_metadata(self, metadata: Dict[str, Any], node_graph):
        """Apply group metadata to recreate group structure."""
        if metadata.get('format_version', '1.0') < '1.1':
            logger.info("Unsupported group metadata version, skipping")
            return
        
        # Create groups in dependency order
        created_groups = {}
        
        for group_data in metadata['groups']:
            group = NodeGroup(
                group_data['name'], 
                group_data['description']
            )
            
            # Restore group properties
            group.group_id = group_data['group_id']
            group.is_collapsed = group_data['is_collapsed']
            group.depth_level = group_data['depth_level']
            
            # Set bounds
            bounds_data = group_data['group_bounds']
            group.group_bounds = QRectF(
                bounds_data['x'], bounds_data['y'],
                bounds_data['width'], bounds_data['height']
            )
            
            created_groups[group.group_id] = group
            node_graph.group_manager.groups.append(group)
            node_graph.addItem(group)
        
        # Restore group relationships and node assignments
        for group_data in metadata['groups']:
            group = created_groups[group_data['group_id']]
            
            # Add child nodes
            for node_id in group_data['child_node_ids']:
                node = node_graph.get_node_by_id(node_id)
                if node:
                    group.add_child_node(node)
            
            # Add child groups
            for child_group_id in group_data['child_group_ids']:
                child_group = created_groups.get(child_group_id)
                if child_group:
                    group.add_child_group(child_group)
```

#### Version Detection and Migration
```python
# src/compatibility/version_handler.py
class FileVersionHandler:
    """Handle file format versions and migrations."""
    
    SUPPORTED_VERSIONS = ['1.0', '1.1']
    CURRENT_VERSION = '1.1'
    
    def detect_version(self, file_content: str) -> str:
        """Detect file format version."""
        # Check for group metadata
        if 'GROUP_METADATA_V1.1' in file_content:
            return '1.1'
        
        # Default to v1.0 for compatibility
        return '1.0'
    
    def ensure_compatibility(self, file_content: str, 
                           target_version: str = None) -> str:
        """Ensure file content is compatible with target version."""
        current_version = self.detect_version(file_content)
        target_version = target_version or self.CURRENT_VERSION
        
        if current_version == target_version:
            return file_content
        
        # Migration logic
        if current_version == '1.0' and target_version == '1.1':
            # No migration needed - v1.1 is backward compatible
            return file_content
        
        elif current_version == '1.1' and target_version == '1.0':
            # Downgrade by removing group metadata
            return self._remove_group_metadata(file_content)
        
        else:
            raise ValueError(f"Unsupported version migration: "
                           f"{current_version} -> {target_version}")
    
    def _remove_group_metadata(self, content: str) -> str:
        """Remove group metadata for v1.0 compatibility."""
        import re
        pattern = r'\n\n<!-- GROUP_METADATA_V[\d\.]+\n.*?\n-->\n'
        return re.sub(pattern, '', content, flags=re.DOTALL)
```

---

## Implementation Roadmap

### Development Phases

Based on the PRD epic structure, implementation follows a carefully planned sequence ensuring continuous integration and testing.

#### Phase 1: Command Pattern Foundation (Epic 1)
**Duration: 2-3 weeks**
**Deliverables:**
- CommandBase abstract class with execution framework
- CommandHistory manager with memory constraints
- Basic node operation commands (Create, Delete)
- Connection operation commands (Create, Delete)
- Integration into NodeGraph operations
- Keyboard shortcut implementation (Ctrl+Z, Ctrl+Y)

**Technical Milestones:**
- [ ] All node/connection operations execute via commands
- [ ] Undo/redo functionality working for basic operations
- [ ] Memory usage stays under 50MB limit (NFR3)
- [ ] Individual operations complete under 100ms (NFR1)

#### Phase 2: Advanced Undo/Redo (Epic 2)
**Duration: 2 weeks**
**Deliverables:**
- Node movement and property change commands
- Code modification undo support
- Composite commands for multi-operation transactions
- Copy/paste operation undo
- Undo History UI dialog
- Menu integration with dynamic descriptions

**Technical Milestones:**
- [ ] All graph operations are undoable
- [ ] Composite operations group correctly
- [ ] UI shows appropriate undo/redo states
- [ ] Bulk operations complete under 500ms (NFR1)

#### Phase 3: Core Grouping System (Epic 3)
**Duration: 3-4 weeks**
**Deliverables:**
- NodeGroup class with hierarchy support
- GroupPin interface system
- Group creation from selection
- Collapse/expand functionality
- Basic group visual representation
- Group validation logic

**Technical Milestones:**
- [ ] Groups collapse to single node representation
- [ ] Interface pins route connections correctly
- [ ] Group operations scale linearly (NFR2)
- [ ] Nested groups work up to 10 levels (NFR7)

#### Phase 4: Advanced Grouping & Integration (Epic 4)
**Duration: 2-3 weeks**
**Deliverables:**
- Group/ungroup commands for undo system
- Nested group support with navigation
- Group template system
- Template management UI
- Complete file format integration
- Performance optimizations

**Technical Milestones:**
- [ ] All grouping operations are undoable
- [ ] Template save/load functionality works
- [ ] File format maintains backward compatibility
- [ ] Large graphs (1000+ nodes) perform acceptably (NFR6)

#### Phase 5: Testing & Polish (Ongoing)
**Duration: Throughout development**
**Deliverables:**
- Comprehensive test suite additions
- Performance benchmarking
- UI polish and user experience refinement
- Documentation updates
- Bug fixes and stability improvements

**Technical Milestones:**
- [ ] Test coverage > 90% for new functionality
- [ ] All performance requirements met (NFR1-NFR7)
- [ ] Zero regression in existing functionality
- [ ] Professional UI consistency maintained

---

## Risk Assessment & Mitigation

### Technical Risks

#### High-Risk Areas

**1. Command History Memory Management (NFR3)**
- **Risk**: Command history exceeding 50MB limit with complex operations
- **Mitigation**: 
  - Implement aggressive memory monitoring
  - Use lazy serialization for large command data
  - Provide manual history clearing options
  - Add memory usage indicators in UI

**2. Large Group Performance (NFR2, NFR6)**
- **Risk**: Group operations becoming unusably slow with 200+ nodes
- **Mitigation**:
  - Implement viewport culling for large groups
  - Use cached bounds calculation
  - Provide performance warnings and degradation modes
  - Add progress indicators for long operations

**3. Backward Compatibility Maintenance**
- **Risk**: File format changes breaking existing workflows
- **Mitigation**:
  - Extensive compatibility testing with existing files
  - Version detection and migration tools
  - Fallback modes for unsupported features
  - Clear communication about format evolution

#### Medium-Risk Areas

**4. Qt Graphics Performance with Deep Nesting**
- **Risk**: QGraphicsItemGroup performance degradation with deep hierarchy
- **Mitigation**:
  - Benchmark Qt performance with deep nesting
  - Implement custom rendering for collapsed groups
  - Provide flattening options for performance

**5. Undo/Redo State Consistency**
- **Risk**: Complex operations leaving system in inconsistent state
- **Mitigation**:
  - Implement ACID properties for all commands (NFR5)
  - Add state validation after each operation
  - Provide recovery mechanisms for corruption

### Quality Assurance Strategy

#### Testing Approach
```python
# tests/test_command_system.py - Example test structure
class TestCommandSystem:
    """Comprehensive command system testing."""
    
    def test_memory_limits_enforcement(self):
        """Verify NFR3: Memory usage under 50MB."""
        command_history = CommandHistory(max_depth=200)
        
        # Create memory-intensive commands
        for i in range(100):
            large_node_command = self._create_large_node_command()
            command_history.execute_command(large_node_command)
        
        # Verify memory constraint
        memory_usage = command_history._memory_monitor.current_usage
        assert memory_usage < 50 * 1024 * 1024, \
            f"Memory usage {memory_usage} exceeds 50MB limit"
    
    def test_performance_requirements(self):
        """Verify NFR1: Operation timing requirements."""
        node_graph = self._create_test_graph()
        
        # Test individual operation timing
        start_time = time.perf_counter()
        command = CreateNodeCommand(node_graph, "TestNode", QPointF(0, 0))
        success = node_graph.execute_command(command)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        assert success, "Command execution failed"
        assert elapsed_ms < 100, \
            f"Individual operation took {elapsed_ms:.1f}ms, exceeds 100ms limit"
    
    def test_group_scaling_performance(self):
        """Verify NFR2: Group operation scaling."""
        node_graph = self._create_test_graph_with_nodes(100)
        nodes = list(node_graph.nodes)
        
        start_time = time.perf_counter()
        group = node_graph.group_manager.create_group(nodes, "TestGroup")
        creation_time = time.perf_counter() - start_time
        
        # Should be ~10ms per node
        expected_max_ms = len(nodes) * 10
        actual_ms = creation_time * 1000
        
        assert actual_ms < expected_max_ms, \
            f"Group creation took {actual_ms:.1f}ms for {len(nodes)} nodes, "
            f"exceeds {expected_max_ms}ms target"
```

---

## Conclusion

This technical architecture provides a comprehensive foundation for implementing Command Pattern-based undo/redo functionality and Node Grouping system in PyFlowGraph. The design carefully balances performance requirements, backward compatibility, and extensibility while maintaining the application's existing architectural patterns.

**Key Success Factors:**
- **Incremental Implementation**: Phased approach ensures continuous integration
- **Performance-First Design**: Architecture optimized for specified performance requirements  
- **Backward Compatibility**: File format evolution maintains existing workflow compatibility
- **Extensible Foundation**: Command Pattern enables future feature expansion
- **Qt Integration**: Leverages existing PySide6 patterns and optimizations

The architecture enables PyFlowGraph to transition from "interesting prototype" to "professional tool" by addressing the two most critical competitive gaps while establishing a foundation for continued professional feature development.

---

**Document Status**: Ready for Development Phase Implementation  
**Next Phase**: Begin Epic 1 - Command Pattern Foundation Development
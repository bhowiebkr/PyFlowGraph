# PyFlowGraph Undo/Redo Implementation Guide

## Architecture: Hybrid with Commit Pattern

This implementation provides separate undo/redo contexts for the graph and code editor, with code changes committed as atomic operations to the graph history.

## Core Implementation Code

### 1. Base Command System (`src/commands/base_command.py`)

```python
from abc import ABC, abstractmethod
from typing import Optional, Any
import uuid

class Command(ABC):
    """Base class for all undoable commands"""
    
    def __init__(self, description: str = ""):
        self.id = str(uuid.uuid4())
        self.description = description
        self.timestamp = None
        self.can_merge = False
        
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command. Returns True if successful."""
        pass
        
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command. Returns True if successful."""
        pass
        
    def redo(self) -> bool:
        """Redo the command. Default implementation calls execute."""
        return self.execute()
        
    def merge_with(self, other: 'Command') -> bool:
        """Attempt to merge with another command. Used for coalescing."""
        return False
        
    def __str__(self) -> str:
        return self.description or self.__class__.__name__
```

### 2. Command History Manager (`src/commands/command_history.py`)

```python
from typing import List, Optional
from PySide6.QtCore import QObject, Signal
import time

class CommandHistory(QObject):
    """Manages undo/redo history with signals for UI updates"""
    
    # Signals for UI updates
    history_changed = Signal()
    undo_available_changed = Signal(bool)
    redo_available_changed = Signal(bool)
    
    def __init__(self, max_size: int = 50):
        super().__init__()
        self.max_size = max_size
        self.history: List[Command] = []
        self.current_index = -1
        self.is_executing = False
        self.last_save_index = -1  # Track saved state
        
    def push(self, command: Command) -> bool:
        """Add a new command to history and execute it"""
        if self.is_executing:
            return False
            
        # Clear redo history when new command is added
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
            
        # Try to merge with last command if possible
        if (self.history and 
            self.current_index >= 0 and 
            command.can_merge and 
            self.history[self.current_index].merge_with(command)):
            self.history_changed.emit()
            return True
            
        # Execute the command
        self.is_executing = True
        try:
            command.timestamp = time.time()
            success = command.execute()
            if success:
                self.history.append(command)
                self.current_index += 1
                
                # Maintain max history size
                if len(self.history) > self.max_size:
                    removed = self.history.pop(0)
                    self.current_index -= 1
                    if self.last_save_index > 0:
                        self.last_save_index -= 1
                        
                self._emit_state_changes()
                return True
        finally:
            self.is_executing = False
            
        return False
        
    def undo(self) -> bool:
        """Undo the last command"""
        if not self.can_undo():
            return False
            
        self.is_executing = True
        try:
            command = self.history[self.current_index]
            success = command.undo()
            if success:
                self.current_index -= 1
                self._emit_state_changes()
                return True
        finally:
            self.is_executing = False
            
        return False
        
    def redo(self) -> bool:
        """Redo the next command"""
        if not self.can_redo():
            return False
            
        self.is_executing = True
        try:
            self.current_index += 1
            command = self.history[self.current_index]
            success = command.redo()
            if success:
                self._emit_state_changes()
                return True
            else:
                self.current_index -= 1
        finally:
            self.is_executing = False
            
        return False
        
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.current_index >= 0
        
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.current_index < len(self.history) - 1
        
    def get_undo_text(self) -> str:
        """Get description of command to be undone"""
        if self.can_undo():
            return str(self.history[self.current_index])
        return ""
        
    def get_redo_text(self) -> str:
        """Get description of command to be redone"""
        if self.can_redo():
            return str(self.history[self.current_index + 1])
        return ""
        
    def clear(self):
        """Clear all history"""
        self.history.clear()
        self.current_index = -1
        self.last_save_index = -1
        self._emit_state_changes()
        
    def mark_saved(self):
        """Mark current state as saved"""
        self.last_save_index = self.current_index
        
    def is_modified(self) -> bool:
        """Check if document has unsaved changes"""
        return self.current_index != self.last_save_index
        
    def _emit_state_changes(self):
        """Emit signals for UI updates"""
        self.history_changed.emit()
        self.undo_available_changed.emit(self.can_undo())
        self.redo_available_changed.emit(self.can_redo())
        
    def get_history_list(self) -> List[str]:
        """Get list of command descriptions for UI"""
        return [str(cmd) for cmd in self.history]
```

### 3. Graph Commands (`src/commands/graph_commands.py`)

```python
from typing import Optional, Dict, Any, List, Tuple
from PySide6.QtCore import QPointF
from .base_command import Command

class CreateNodeCommand(Command):
    """Command to create a new node"""
    
    def __init__(self, graph, node_type: str, position: QPointF, 
                 properties: Optional[Dict[str, Any]] = None):
        super().__init__(f"Create {node_type} Node")
        self.graph = graph
        self.node_type = node_type
        self.position = position
        self.properties = properties or {}
        self.node = None
        self.node_id = None
        
    def execute(self) -> bool:
        from ..node import Node
        self.node = Node(self.node_type)
        self.node.setPos(self.position)
        
        for key, value in self.properties.items():
            setattr(self.node, key, value)
            
        self.graph.addItem(self.node)
        self.node_id = self.node.uuid
        return True
        
    def undo(self) -> bool:
        if self.node_id:
            node = self.graph.get_node_by_id(self.node_id)
            if node:
                # Remove all connections first
                for pin in node.pins:
                    for connection in list(pin.connections):
                        self.graph.removeItem(connection)
                self.graph.removeItem(node)
                return True
        return False
        
    def redo(self) -> bool:
        # Re-create with same ID
        from ..node import Node
        self.node = Node(self.node_type)
        self.node.uuid = self.node_id
        self.node.setPos(self.position)
        
        for key, value in self.properties.items():
            setattr(self.node, key, value)
            
        self.graph.addItem(self.node)
        return True


class DeleteNodeCommand(Command):
    """Command to delete a node and its connections"""
    
    def __init__(self, graph, node):
        super().__init__(f"Delete {node.title}")
        self.graph = graph
        self.node = node
        self.node_data = None
        self.connection_data = []
        
    def execute(self) -> bool:
        # Store node data for undo
        self.node_data = self.node.serialize()
        
        # Store connection data
        for pin in self.node.pins:
            for conn in pin.connections:
                self.connection_data.append({
                    'source_node': conn.source_pin.node.uuid,
                    'source_pin': conn.source_pin.name,
                    'target_node': conn.target_pin.node.uuid,
                    'target_pin': conn.target_pin.name
                })
                
        # Delete connections
        for pin in self.node.pins:
            for conn in list(pin.connections):
                self.graph.removeItem(conn)
                
        # Delete node
        self.graph.removeItem(self.node)
        return True
        
    def undo(self) -> bool:
        if self.node_data:
            # Recreate node
            from ..node import Node
            node = Node.deserialize(self.node_data, self.graph)
            self.graph.addItem(node)
            
            # Recreate connections
            for conn_data in self.connection_data:
                source_node = self.graph.get_node_by_id(conn_data['source_node'])
                target_node = self.graph.get_node_by_id(conn_data['target_node'])
                if source_node and target_node:
                    source_pin = source_node.get_pin_by_name(conn_data['source_pin'])
                    target_pin = target_node.get_pin_by_name(conn_data['target_pin'])
                    if source_pin and target_pin:
                        self.graph.create_connection(source_pin, target_pin)
            return True
        return False


class MoveNodeCommand(Command):
    """Command to move a node or multiple nodes"""
    
    def __init__(self, nodes: List, delta: QPointF):
        node_names = ", ".join([n.title for n in nodes[:3]])
        if len(nodes) > 3:
            node_names += f" and {len(nodes)-3} more"
        super().__init__(f"Move {node_names}")
        
        self.nodes = nodes
        self.delta = delta
        self.can_merge = True  # Allow merging consecutive moves
        
    def execute(self) -> bool:
        for node in self.nodes:
            node.setPos(node.pos() + self.delta)
        return True
        
    def undo(self) -> bool:
        for node in self.nodes:
            node.setPos(node.pos() - self.delta)
        return True
        
    def merge_with(self, other: Command) -> bool:
        if isinstance(other, MoveNodeCommand):
            # Check if same nodes
            if set(self.nodes) == set(other.nodes):
                self.delta += other.delta
                return True
        return False


class CreateConnectionCommand(Command):
    """Command to create a connection between pins"""
    
    def __init__(self, graph, source_pin, target_pin):
        super().__init__(f"Connect {source_pin.name} to {target_pin.name}")
        self.graph = graph
        self.source_pin = source_pin
        self.target_pin = target_pin
        self.connection = None
        
    def execute(self) -> bool:
        if self.source_pin.can_connect_to(self.target_pin):
            self.connection = self.graph.create_connection(
                self.source_pin, self.target_pin
            )
            return self.connection is not None
        return False
        
    def undo(self) -> bool:
        if self.connection:
            self.graph.removeItem(self.connection)
            self.source_pin.connections.remove(self.connection)
            self.target_pin.connections.remove(self.connection)
            self.connection = None
            return True
        return False
        
    def redo(self) -> bool:
        return self.execute()


class DeleteConnectionCommand(Command):
    """Command to delete a connection"""
    
    def __init__(self, graph, connection):
        super().__init__("Delete Connection")
        self.graph = graph
        self.connection = connection
        self.source_pin = connection.source_pin
        self.target_pin = connection.target_pin
        
    def execute(self) -> bool:
        self.graph.removeItem(self.connection)
        self.source_pin.connections.remove(self.connection)
        self.target_pin.connections.remove(self.connection)
        return True
        
    def undo(self) -> bool:
        self.connection = self.graph.create_connection(
            self.source_pin, self.target_pin
        )
        return self.connection is not None


class ChangeNodeCodeCommand(Command):
    """Command for code changes from editor dialog"""
    
    def __init__(self, node, old_code: str, new_code: str):
        super().__init__(f"Edit Code: {node.title}")
        self.node = node
        self.old_code = old_code
        self.new_code = new_code
        self.old_pins = None
        
    def execute(self) -> bool:
        # Store old pin configuration
        self.old_pins = [(p.name, p.pin_type) for p in self.node.pins]
        
        # Update code
        self.node.set_code(self.new_code)
        
        # Rebuild pins from new code
        self.node.update_pins_from_code()
        return True
        
    def undo(self) -> bool:
        # Restore old code
        self.node.set_code(self.old_code)
        
        # Rebuild pins from old code
        self.node.update_pins_from_code()
        return True


class CompositeCommand(Command):
    """Command that groups multiple commands as one operation"""
    
    def __init__(self, description: str, commands: List[Command]):
        super().__init__(description)
        self.commands = commands
        
    def execute(self) -> bool:
        for command in self.commands:
            if not command.execute():
                # Rollback on failure
                for cmd in reversed(self.commands[:self.commands.index(command)]):
                    cmd.undo()
                return False
        return True
        
    def undo(self) -> bool:
        for command in reversed(self.commands):
            if not command.undo():
                return False
        return True
        
    def redo(self) -> bool:
        return self.execute()
```

### 4. Integration with NodeGraph (`src/node_graph.py` modifications)

```python
# Add to existing NodeGraph class

from commands.command_history import CommandHistory
from commands.graph_commands import *

class NodeGraph(QGraphicsScene):
    def __init__(self):
        super().__init__()
        # ... existing init code ...
        
        # Add command history
        self.command_history = CommandHistory(max_size=50)
        
        # Connect signals for UI updates
        self.command_history.undo_available_changed.connect(
            self.on_undo_available_changed
        )
        self.command_history.redo_available_changed.connect(
            self.on_redo_available_changed
        )
        
    def create_node(self, node_type: str, position: QPointF, 
                   execute_command: bool = True) -> Optional[Node]:
        """Create a node with undo support"""
        if execute_command:
            command = CreateNodeCommand(self, node_type, position)
            if self.command_history.push(command):
                return command.node
            return None
        else:
            # Direct creation without undo (for loading files)
            node = Node(node_type)
            node.setPos(position)
            self.addItem(node)
            return node
            
    def delete_selected(self):
        """Delete selected items with undo support"""
        selected = self.selectedItems()
        if not selected:
            return
            
        commands = []
        for item in selected:
            if isinstance(item, Node):
                commands.append(DeleteNodeCommand(self, item))
            elif isinstance(item, Connection):
                commands.append(DeleteConnectionCommand(self, item))
                
        if len(commands) == 1:
            self.command_history.push(commands[0])
        elif commands:
            composite = CompositeCommand("Delete Selection", commands)
            self.command_history.push(composite)
            
    def undo(self):
        """Perform undo operation"""
        return self.command_history.undo()
        
    def redo(self):
        """Perform redo operation"""
        return self.command_history.redo()
        
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.command_history.can_undo()
        
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.command_history.can_redo()
        
    def clear_history(self):
        """Clear undo/redo history"""
        self.command_history.clear()
        
    def on_undo_available_changed(self, available: bool):
        """Signal handler for undo availability changes"""
        # This will be connected to menu/toolbar updates
        pass
        
    def on_redo_available_changed(self, available: bool):
        """Signal handler for redo availability changes"""
        # This will be connected to menu/toolbar updates
        pass
```

### 5. Code Editor Integration (`src/code_editor_dialog.py` modifications)

```python
# Modify existing CodeEditorDialog class

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QDialogButtonBox
from PySide6.QtCore import Qt
from commands.graph_commands import ChangeNodeCodeCommand

class CodeEditorDialog(QDialog):
    def __init__(self, node, graph, parent=None):
        super().__init__(parent)
        self.node = node
        self.graph = graph  # Need reference to graph for command history
        self.original_code = node.code
        
        self.setWindowTitle(f"Edit Code - {node.title}")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create code editor with its own undo/redo
        self.editor = PythonCodeEditor()
        self.editor.setPlainText(self.original_code)
        
        # Editor has its own undo/redo during editing
        # These shortcuts only work while editor has focus
        self.editor.setup_editor_undo()  # Uses QTextEdit built-in
        
        layout.addWidget(self.editor)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.resize(800, 600)
        
    def accept(self):
        """On accept, commit code changes as single undo command"""
        new_code = self.editor.toPlainText()
        
        if new_code != self.original_code:
            # Create and execute command through graph's history
            command = ChangeNodeCodeCommand(
                self.node,
                self.original_code,
                new_code
            )
            self.graph.command_history.push(command)
            
        super().accept()
        
    def reject(self):
        """On cancel, discard all changes"""
        # No changes to graph history
        super().reject()
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        # Let Ctrl+Z/Y work in editor only
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            self.editor.undo()
        elif event.key() == Qt.Key_Y and event.modifiers() == Qt.ControlModifier:
            self.editor.redo()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
```

### 6. UI Integration (`src/node_editor_window.py` modifications)

```python
# Add to existing NodeEditorWindow class

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu

class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... existing init code ...
        self._create_undo_actions()
        
    def _create_undo_actions(self):
        """Create undo/redo actions"""
        # Undo action
        self.action_undo = QAction("Undo", self)
        self.action_undo.setShortcut(QKeySequence.Undo)
        self.action_undo.setEnabled(False)
        self.action_undo.triggered.connect(self.on_undo)
        
        # Redo action
        self.action_redo = QAction("Redo", self)
        self.action_redo.setShortcut(QKeySequence.Redo)
        self.action_redo.setEnabled(False)
        self.action_redo.triggered.connect(self.on_redo)
        
        # Connect to history signals
        self.graph.command_history.undo_available_changed.connect(
            self.action_undo.setEnabled
        )
        self.graph.command_history.redo_available_changed.connect(
            self.action_redo.setEnabled
        )
        self.graph.command_history.history_changed.connect(
            self.update_undo_actions
        )
        
    def _create_menus(self):
        """Add undo/redo to Edit menu"""
        # ... existing menu code ...
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("Edit")
        edit_menu.addAction(self.action_undo)
        edit_menu.addAction(self.action_redo)
        edit_menu.addSeparator()
        
        # History submenu
        history_menu = edit_menu.addMenu("History")
        self.action_clear_history = QAction("Clear History", self)
        self.action_clear_history.triggered.connect(self.on_clear_history)
        history_menu.addAction(self.action_clear_history)
        
    def _create_toolbar(self):
        """Add undo/redo to toolbar"""
        # ... existing toolbar code ...
        
        toolbar.addSeparator()
        toolbar.addAction(self.action_undo)
        toolbar.addAction(self.action_redo)
        
    def on_undo(self):
        """Handle undo action"""
        self.graph.undo()
        self.view.viewport().update()
        
    def on_redo(self):
        """Handle redo action"""
        self.graph.redo()
        self.view.viewport().update()
        
    def on_clear_history(self):
        """Clear undo history with confirmation"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Clear all undo/redo history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.graph.clear_history()
            
    def update_undo_actions(self):
        """Update undo/redo action text with command descriptions"""
        history = self.graph.command_history
        
        if history.can_undo():
            self.action_undo.setText(f"Undo {history.get_undo_text()}")
        else:
            self.action_undo.setText("Undo")
            
        if history.can_redo():
            self.action_redo.setText(f"Redo {history.get_redo_text()}")
        else:
            self.action_redo.setText("Redo")
            
    def on_save(self):
        """Mark saved state in history"""
        # ... existing save code ...
        self.graph.command_history.mark_saved()
        
    def closeEvent(self, event):
        """Check for unsaved changes"""
        if self.graph.command_history.is_modified():
            from PySide6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.on_save()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
```

### 7. Mouse Interaction Updates (`src/node_editor_view.py` modifications)

```python
# Modify mouse handling to use commands

from commands.graph_commands import MoveNodeCommand

class NodeEditorView(QGraphicsView):
    def __init__(self):
        super().__init__()
        # ... existing init code ...
        self.drag_start_positions = {}  # Track initial positions for move
        
    def mousePressEvent(self, event):
        # ... existing mouse press code ...
        
        # Store initial positions for potential move
        if event.button() == Qt.LeftButton:
            for item in self.scene().selectedItems():
                if isinstance(item, Node):
                    self.drag_start_positions[item] = item.pos()
                    
    def mouseReleaseEvent(self, event):
        # ... existing mouse release code ...
        
        if event.button() == Qt.LeftButton and self.drag_start_positions:
            # Check if any nodes were moved
            moved_nodes = []
            delta = None
            
            for node, start_pos in self.drag_start_positions.items():
                if node.pos() != start_pos:
                    if delta is None:
                        delta = node.pos() - start_pos
                    moved_nodes.append(node)
                    # Reset position for command to handle
                    node.setPos(start_pos)
                    
            if moved_nodes and delta:
                # Create move command
                command = MoveNodeCommand(moved_nodes, delta)
                self.scene().command_history.push(command)
                
            self.drag_start_positions.clear()
```

## Testing the Implementation

### Unit Test Example (`tests/test_undo_redo.py`)

```python
import unittest
from PySide6.QtCore import QPointF
from src.node_graph import NodeGraph
from src.commands.graph_commands import *

class TestUndoRedo(unittest.TestCase):
    def setUp(self):
        self.graph = NodeGraph()
        
    def test_create_undo_redo(self):
        # Create node
        pos = QPointF(100, 100)
        node = self.graph.create_node("TestNode", pos)
        self.assertIsNotNone(node)
        self.assertEqual(len(self.graph.items()), 1)
        
        # Undo creation
        self.assertTrue(self.graph.undo())
        self.assertEqual(len(self.graph.items()), 0)
        
        # Redo creation
        self.assertTrue(self.graph.redo())
        self.assertEqual(len(self.graph.items()), 1)
        
    def test_move_coalescing(self):
        # Create node
        node = self.graph.create_node("TestNode", QPointF(0, 0))
        
        # Multiple small moves should coalesce
        for i in range(5):
            command = MoveNodeCommand([node], QPointF(10, 0))
            self.graph.command_history.push(command)
            
        # Should only need one undo for all moves
        self.graph.undo()
        self.assertEqual(node.pos(), QPointF(0, 0))
        
    def test_code_change_atomic(self):
        # Create node with code
        node = self.graph.create_node("TestNode", QPointF(0, 0))
        original_code = "def test(): pass"
        node.set_code(original_code)
        
        # Change code
        new_code = "def test():\n    return 42"
        command = ChangeNodeCodeCommand(node, original_code, new_code)
        self.graph.command_history.push(command)
        self.assertEqual(node.code, new_code)
        
        # Undo should restore original
        self.graph.undo()
        self.assertEqual(node.code, original_code)
```

## Summary

This implementation provides:

1. **Separate Contexts**: Graph operations and code editing have independent undo/redo
2. **Clean History**: Code changes appear as single atomic operations in graph history
3. **Natural UX**: Modal dialog behavior matches user expectations
4. **Performance**: Leverages Qt's built-in text undo for efficiency
5. **Extensibility**: Easy to add new command types
6. **State Management**: Tracks saved state and modifications

The hybrid approach gives users the best experience: granular editing while coding, clean history for graph operations, and predictable behavior throughout.
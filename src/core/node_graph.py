# node_graph.py
# The QGraphicsScene that manages nodes, connections, and their interactions.
# Now with a definitive fix for node resizing on initial graph load.

import uuid
import json
import os
import sys
from PySide6.QtWidgets import QGraphicsScene, QApplication
from PySide6.QtCore import Qt, QPointF, QTimer, Signal
from PySide6.QtGui import QKeyEvent, QColor
from .node import Node
from .reroute_node import RerouteNode
from .connection import Connection
from .pin import Pin

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from commands import (
    CommandHistory, CreateNodeCommand, DeleteNodeCommand, MoveNodeCommand,
    CreateConnectionCommand, DeleteConnectionCommand, CreateRerouteNodeCommand,
    CompositeCommand
)


class NodeGraph(QGraphicsScene):
    # Signals for UI updates
    commandExecuted = Signal(str)  # Emitted when command is executed
    commandUndone = Signal(str)    # Emitted when command is undone
    commandRedone = Signal(str)    # Emitted when command is redone
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(Qt.darkGray)
        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.nodes, self.connections = [], []
        self._drag_connection, self._drag_start_pin = None, None
        self.graph_title = "Untitled Graph"
        self.graph_description = ""
        
        # Command system integration
        self.command_history = CommandHistory()
        self._tracking_moves = {}  # Track node movements for command batching
    
    def get_node_by_id(self, node_id):
        """Find node by UUID - helper for command restoration."""
        for node in self.nodes:
            if hasattr(node, 'uuid') and node.uuid == node_id:
                return node
        return None

    def execute_command(self, command):
        """Execute a command and add it to history."""
        success = self.command_history.execute_command(command)
        if success:
            self.commandExecuted.emit(command.get_description())
        return success
    
    def undo_last_command(self):
        """Undo the last command."""
        description = self.command_history.undo()
        if description:
            self.commandUndone.emit(description)
            return True
        return False
    
    def redo_last_command(self):
        """Redo the last undone command."""
        description = self.command_history.redo()
        if description:
            self.commandRedone.emit(description)
            return True
        return False
    
    def can_undo(self):
        """Check if undo is available."""
        return self.command_history.can_undo()
    
    def can_redo(self):
        """Check if redo is available."""
        return self.command_history.can_redo()
    
    def get_undo_description(self):
        """Get description of next undo operation."""
        return self.command_history.get_undo_description()
    
    def get_redo_description(self):
        """Get description of next redo operation."""
        return self.command_history.get_redo_description()

    def clear_graph(self):
        """Removes all nodes and connections from the scene."""
        # Remove all connections first
        for connection in list(self.connections):
            self.remove_connection(connection, use_command=False)
        
        # Remove all nodes directly (bypass command pattern for clearing)
        for node in list(self.nodes):
            self.remove_node(node, use_command=False)
        
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        # Handle undo/redo shortcuts
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Z:
                if event.modifiers() & Qt.ShiftModifier:
                    print(f"\n=== KEYBOARD REDO TRIGGERED ===")
                    self.redo_last_command()
                else:
                    print(f"\n=== KEYBOARD UNDO TRIGGERED ===")
                    self.undo_last_command()
                return
            elif event.key() == Qt.Key_Y:
                print(f"\n=== KEYBOARD REDO (Y) TRIGGERED ===")
                self.redo_last_command()
                return
        
        # Handle delete operations
        if event.key() == Qt.Key_Delete:
            print(f"\n=== KEYBOARD DELETE TRIGGERED ===")
            selected_items = list(self.selectedItems())
            print(f"DEBUG: Found {len(selected_items)} selected items")
            
            for i, item in enumerate(selected_items):
                print(f"DEBUG: Selected item {i}: {type(item).__name__} - {getattr(item, 'title', 'No title')} (ID: {id(item)})")
            
            if selected_items:
                commands = []
                
                # Create delete commands for selected items
                for item in selected_items:
                    if isinstance(item, (Node, RerouteNode)):
                        print(f"DEBUG: Creating DeleteNodeCommand for {getattr(item, 'title', 'Unknown')} (ID: {id(item)})")
                        commands.append(DeleteNodeCommand(self, item))
                    elif isinstance(item, Connection):
                        print(f"DEBUG: Creating DeleteConnectionCommand for connection {id(item)}")
                        commands.append(DeleteConnectionCommand(self, item))
                
                print(f"DEBUG: Created {len(commands)} delete commands")
                
                # Execute as composite command if multiple items
                if len(commands) > 1:
                    print(f"DEBUG: Executing composite command with {len(commands)} commands")
                    composite = CompositeCommand(f"Delete {len(commands)} items", commands)
                    result = self.execute_command(composite)
                    print(f"DEBUG: Composite command returned: {result}")
                elif len(commands) == 1:
                    print(f"DEBUG: Executing single command")
                    result = self.execute_command(commands[0])
                    print(f"DEBUG: Single command returned: {result}")
                else:
                    print(f"DEBUG: No commands to execute")
            else:
                print(f"DEBUG: No items selected for deletion")
        else:
            super().keyPressEvent(event)

    def copy_selected(self):
        """Copies selected nodes, their connections, and the graph's requirements to the clipboard."""
        selected_nodes = [item for item in self.selectedItems() if isinstance(item, (Node, RerouteNode))]
        if not selected_nodes:
            return {"requirements": [], "nodes": [], "connections": []}

        nodes_data = [node.serialize() for node in selected_nodes]
        connections_data = []
        selected_node_uuids = {node.uuid for node in selected_nodes}
        for conn in self.connections:
            if hasattr(conn.start_pin.node, "uuid") and hasattr(conn.end_pin.node, "uuid") and conn.start_pin.node.uuid in selected_node_uuids and conn.end_pin.node.uuid in selected_node_uuids:
                connections_data.append(conn.serialize())

        # Get requirements from main window if available
        requirements = []
        views = self.views()
        if views:
            main_window = views[0].window()
            requirements = main_window.current_requirements if hasattr(main_window, "current_requirements") else []

        clipboard_data = {"requirements": requirements, "nodes": nodes_data, "connections": connections_data}

        # Convert to markdown format for clipboard
        try:
            from data.flow_format import FlowFormatHandler
            handler = FlowFormatHandler()
            clipboard_markdown = handler.data_to_markdown(clipboard_data, "Clipboard Content", "Copied nodes from PyFlowGraph")
            QApplication.clipboard().setText(clipboard_markdown)
        except ImportError:
            # Fallback to JSON format if FlowFormatHandler is not available (e.g., during testing)
            import json
            QApplication.clipboard().setText(json.dumps(clipboard_data, indent=2))
        print(f"Copied {len(nodes_data)} nodes to clipboard as markdown.")
        
        return clipboard_data

    def paste(self):
        """Pastes nodes and connections from the clipboard using command pattern."""
        clipboard_text = QApplication.clipboard().text()
        
        # Determine paste position
        paste_pos = QPointF(0, 0)  # Default position
        views = self.views()
        if views:
            paste_pos = views[0].mapToScene(views[0].viewport().rect().center())
        
        try:
            # Try to parse as markdown first
            from data.flow_format import FlowFormatHandler
            handler = FlowFormatHandler()
            data = handler.markdown_to_data(clipboard_text)
            self._paste_with_command(data, paste_pos)
        except ImportError:
            # FlowFormatHandler not available, try JSON
            try:
                import json
                data = json.loads(clipboard_text)
                self._paste_with_command(data, paste_pos)
            except (json.JSONDecodeError, TypeError):
                print("Clipboard does not contain valid graph data.")
        except Exception:
            # Fallback: try to parse as JSON for backward compatibility
            try:
                import json
                data = json.loads(clipboard_text)
                self._paste_with_command(data, paste_pos)
            except (json.JSONDecodeError, TypeError):
                print("Clipboard does not contain valid graph data.")
    
    def _paste_with_command(self, data, paste_pos):
        """Helper method to paste using PasteNodesCommand."""
        if not data or not data.get('nodes'):
            print("No nodes to paste.")
            return
        
        # Convert data format to match PasteNodesCommand expectations
        clipboard_data = self._convert_data_format(data)
        
        # Create and execute paste command
        from commands.node_commands import PasteNodesCommand
        paste_cmd = PasteNodesCommand(self, clipboard_data, paste_pos)
        result = self.execute_command(paste_cmd)
        
        if not result:
            print("Failed to paste nodes.")
    
    def _convert_data_format(self, data):
        """Convert deserialize format to PasteNodesCommand format."""
        clipboard_data = {
            'nodes': [],
            'connections': []
        }
        
        # Convert nodes
        for node_data in data.get('nodes', []):
            converted_node = {
                'id': node_data.get('uuid', ''),
                'title': node_data.get('title', 'Unknown'),
                'description': node_data.get('description', ''),
                'code': node_data.get('code', ''),
                'pos': node_data.get('pos', [0, 0])
            }
            clipboard_data['nodes'].append(converted_node)
        
        # Convert connections
        for conn_data in data.get('connections', []):
            converted_conn = {
                'output_node_id': conn_data.get('start_node_uuid', ''),
                'input_node_id': conn_data.get('end_node_uuid', ''),
                'output_pin_name': conn_data.get('start_pin_name', ''),
                'input_pin_name': conn_data.get('end_pin_name', '')
            }
            clipboard_data['connections'].append(converted_conn)
        
        return clipboard_data

    def serialize(self):
        """Serializes all nodes and their connections."""
        nodes_data = [node.serialize() for node in self.nodes]
        connections_data = [conn.serialize() for conn in self.connections if conn.serialize()]
        return {
            "graph_title": self.graph_title,
            "graph_description": self.graph_description,
            "nodes": nodes_data, 
            "connections": connections_data
        }

    def deserialize(self, data, offset=QPointF(0, 0)):
        """Deserializes graph data, creating all nodes and applying custom properties."""
        if not data:
            return
        if offset == QPointF(0, 0):
            self.clear_graph()
            # Load graph metadata only when loading a complete graph (not copying/pasting)
            self.graph_title = data.get("graph_title", "Untitled Graph")
            self.graph_description = data.get("graph_description", "")

        uuid_to_node_map = {}
        nodes_to_update = []

        for node_data in data.get("nodes", []):
            original_pos = QPointF(node_data["pos"][0], node_data["pos"][1])
            new_pos = original_pos + offset
            is_reroute = node_data.get("is_reroute", False)
            
            # Determine UUID first
            old_uuid = node_data["uuid"]
            new_uuid = str(uuid.uuid4()) if offset != QPointF(0, 0) else old_uuid
            
            if is_reroute:
                node = self.create_node("", pos=(new_pos.x(), new_pos.y()), is_reroute=True, use_command=False)
            else:
                node = self.create_node(node_data["title"], pos=(new_pos.x(), new_pos.y()), use_command=False)
                
                # Set UUID BEFORE doing any operations that might reference the node
                node.uuid = new_uuid
                
                node.description = node_data.get("description", "")
                node.set_code(node_data.get("code", ""))
                node.set_gui_code(node_data.get("gui_code", ""))
                node.set_gui_get_values_code(node_data.get("gui_get_values_code", ""))
                if "size" in node_data:
                    # Apply size validation during loading
                    loaded_width, loaded_height = node_data["size"]
                    
                    # Calculate minimum size requirements
                    min_width, min_height = node.calculate_absolute_minimum_size()
                    
                    # Ensure loaded size meets minimum requirements
                    corrected_width = max(loaded_width, min_width)
                    corrected_height = max(loaded_height, min_height)
                    
                    # Debug logging for size corrections
                    from utils.debug_config import should_debug, DEBUG_FILE_LOADING
                    if should_debug(DEBUG_FILE_LOADING) and (corrected_width != loaded_width or corrected_height != loaded_height):
                        print(f"DEBUG: Node '{node_data['title']}' size corrected from "
                              f"{loaded_width}x{loaded_height} to {corrected_width}x{corrected_height}")
                    
                    node.width, node.height = corrected_width, corrected_height
                colors = node_data.get("colors", {})
                if "title" in colors:
                    node.color_title_bar = QColor(colors["title"])
                if "body" in colors:
                    node.color_body = QColor(colors["body"])
                node.update()
                node.apply_gui_state(node_data.get("gui_state", {}))
                nodes_to_update.append(node)

            # UUID is already set for regular nodes, set it for reroute nodes
            if is_reroute:
                node.uuid = new_uuid
                
            uuid_to_node_map[old_uuid] = node

        for conn_data in data.get("connections", []):
            start_node = uuid_to_node_map.get(conn_data["start_node_uuid"])
            end_node = uuid_to_node_map.get(conn_data["end_node_uuid"])
            if start_node and end_node:
                start_pin = start_node.get_pin_by_name(conn_data["start_pin_name"])
                end_pin = end_node.get_pin_by_name(conn_data["end_pin_name"])
                if start_pin and end_pin:
                    self.create_connection(start_pin, end_pin, use_command=False)

        # --- Definitive Resizing Fix ---
        # Defer the final layout calculation. This allows the Qt event loop to
        # process all pending widget creation and resizing events first, ensuring
        # that the size hints are accurate when fit_size_to_content is called.
        QTimer.singleShot(0, lambda: self.final_load_update(nodes_to_update))

    def final_load_update(self, nodes_to_update):
        """A helper method called by a timer to run the final layout pass."""
        from utils.debug_config import should_debug, DEBUG_FILE_LOADING
        
        for node in nodes_to_update:
            # Check if node is still valid (not deleted)
            try:
                if node.scene() is None:
                    continue  # Node has been removed from scene
                
                # Re-validate minimum size now that GUI is fully constructed
                min_width, min_height = node.calculate_absolute_minimum_size()
                current_width, current_height = node.width, node.height
                
                # Check if current size is still too small after GUI construction
                required_width = max(current_width, min_width)
                required_height = max(current_height, min_height)
                
                if required_width != current_width or required_height != current_height:
                    if should_debug(DEBUG_FILE_LOADING):
                        print(f"DEBUG: Final size validation - Node '{node.title}' needs resize from "
                              f"{current_width}x{current_height} to {required_width}x{required_height}")
                    
                    node.width = required_width
                    node.height = required_height
                
                # Force a complete layout rebuild like manual resize does
                node._update_layout()
                # Update all pin connections like manual resize does
                for pin in node.pins:
                    pin.update_connections()
                # Force node visual update
                node.update()
            except RuntimeError:
                # Node has been deleted, skip
                continue
        self.update()

    # --- Other methods remain the same ---
    def create_node(self, title, pos=(0, 0), is_reroute=False, use_command=True):
        """Create a node, optionally using command pattern for undo/redo."""
        if use_command and not is_reroute:
            # Use command pattern for regular nodes
            position = QPointF(pos[0], pos[1])
            command = CreateNodeCommand(self, title, position)
            if self.execute_command(command):
                return command.created_node
            return None
        else:
            # Direct creation for reroute nodes or when commands disabled
            node = RerouteNode() if is_reroute else Node(title)
            node.setPos(pos[0], pos[1])
            self.addItem(node)
            self.nodes.append(node)
            return node

    def remove_node(self, node, use_command=True):
        """Remove a node, optionally using command pattern for undo/redo."""
        print(f"\n=== NODE GRAPH REMOVE_NODE START ===")
        print(f"DEBUG: remove_node called with use_command={use_command}")
        print(f"DEBUG: Node to remove: '{getattr(node, 'title', 'Unknown')}' (ID: {id(node)})")
        print(f"DEBUG: Graph has {len(self.nodes)} nodes before removal")
        print(f"DEBUG: Scene has {len(self.items())} items before removal")
        
        if use_command:
            print(f"DEBUG: Using command pattern for removal")
            # Use command pattern
            command = DeleteNodeCommand(self, node)
            result = self.execute_command(command)
            print(f"DEBUG: Command execution returned: {result}")
            print(f"=== NODE GRAPH REMOVE_NODE END (COMMAND) ===\n")
            return result
        else:
            print(f"DEBUG: Direct removal (bypassing command pattern)")
            # Direct removal (for internal use by commands)
            # First, remove all connections to/from this node
            connections_to_remove = []
            for connection in list(self.connections):
                if (hasattr(connection, 'start_pin') and connection.start_pin.node == node or 
                    hasattr(connection, 'end_pin') and connection.end_pin.node == node):
                    connections_to_remove.append(connection)
                    print(f"DEBUG: Found connection to remove: {connection}")
            
            print(f"DEBUG: Removing {len(connections_to_remove)} connections first")
            
            # Remove connections first
            for connection in connections_to_remove:
                print(f"DEBUG: Removing connection: {connection}")
                result = self.remove_connection(connection, use_command=False)
                print(f"DEBUG: Connection removal returned: {result}")
            
            # Then remove and destroy all pins
            if hasattr(node, "pins"):
                print(f"DEBUG: Node has {len(node.pins)} pins to clean up")
                for pin in list(node.pins):
                    # Clean up pin without trying to remove connections (already done)
                    print(f"DEBUG: Cleaning up pin: {pin}")
                    pin.connections.clear()  # Clear the connections list
                    pin.destroy()  # This will safely handle scene removal
                    print(f"DEBUG: Pin cleaned up")
                    
                # Clear all pin lists
                if hasattr(node, 'pins'):
                    node.pins.clear()
                    print(f"DEBUG: Cleared pins list")
                if hasattr(node, 'input_pins'):
                    node.input_pins.clear()
                    print(f"DEBUG: Cleared input_pins list")
                if hasattr(node, 'output_pins'):
                    node.output_pins.clear()
                    print(f"DEBUG: Cleared output_pins list")
                if hasattr(node, 'execution_pins'):
                    node.execution_pins.clear()
                    print(f"DEBUG: Cleared execution_pins list")
                if hasattr(node, 'data_pins'):
                    node.data_pins.clear()
                    print(f"DEBUG: Cleared data_pins list")
            
            # Finally remove the node itself
            print(f"DEBUG: Removing node from nodes list...")
            if node in self.nodes:
                self.nodes.remove(node)
                print(f"DEBUG: Node removed from nodes list (count now: {len(self.nodes)})")
            else:
                print(f"DEBUG: WARNING - Node not in nodes list!")
                
            print(f"DEBUG: Removing node from scene...")
            if node.scene() == self:
                self.removeItem(node)
                print(f"DEBUG: Node removed from scene (items now: {len(self.items())})")
            else:
                print(f"DEBUG: WARNING - Node not in scene or scene mismatch!")
                print(f"DEBUG: Node scene: {node.scene()}")
                print(f"DEBUG: This scene: {self}")
            
            print(f"=== NODE GRAPH REMOVE_NODE END (DIRECT) ===\n")
            return True

    def create_connection(self, start_pin, end_pin, use_command=True):
        """Create a connection, optionally using command pattern for undo/redo."""
        if not start_pin.can_connect_to(end_pin):
            return None
            
        if use_command:
            # Use command pattern
            command = CreateConnectionCommand(self, start_pin, end_pin)
            if self.execute_command(command):
                return command.created_connection
            return None
        else:
            # Direct creation (for internal use by commands)
            conn = Connection(start_pin, end_pin)
            self.addItem(conn)
            self.connections.append(conn)
            if isinstance(end_pin.node, RerouteNode):
                end_pin.node.update_color()
            return conn

    def remove_connection(self, connection, use_command=True):
        """Remove a connection, optionally using command pattern for undo/redo."""
        if use_command:
            # Use command pattern
            command = DeleteConnectionCommand(self, connection)
            return self.execute_command(command)
        else:
            # Direct removal (for internal use by commands)
            end_pin = connection.end_pin
            connection.remove()
            if connection in self.connections:
                self.connections.remove(connection)
            self.removeItem(connection)
            if end_pin and isinstance(end_pin.node, RerouteNode):
                end_pin.node.update_color()
            return True

    def create_reroute_node_on_connection(self, connection, position, use_command=True):
        """Create a reroute node on a connection, optionally using command pattern."""
        if use_command:
            # Use command pattern
            command = CreateRerouteNodeCommand(self, connection, position)
            success = self.execute_command(command)
            if success:
                return command.reroute_node  # Return the created node
            else:
                return None
        else:
            # Direct creation (for internal use)
            start_pin, end_pin = connection.start_pin, connection.end_pin
            self.remove_connection(connection, use_command=False)
            reroute_node = self.create_node("", pos=(position.x(), position.y()), is_reroute=True, use_command=False)
            self.create_connection(start_pin, reroute_node.input_pin, use_command=False)
            self.create_connection(reroute_node.output_pin, end_pin, use_command=False)
            return reroute_node

    def start_drag_connection(self, start_pin):
        self._drag_start_pin = start_pin
        self._drag_connection = Connection(start_pin, None)
        self.addItem(self._drag_connection)

    def update_drag_connection(self, end_pos):
        if self._drag_connection:
            self._drag_connection.set_end_pos(end_pos)
            self.update()

    def end_drag_connection(self, end_pos):
        if self._drag_connection is None or self._drag_start_pin is None:
            return
        target_item = self.itemAt(end_pos, self.views()[0].transform())
        self.removeItem(self._drag_connection)
        self._drag_connection = None
        if isinstance(target_item, Pin):
            end_pin = target_item
            if end_pin.direction == "input" and end_pin.connections:
                self.remove_connection(end_pin.connections[0])
            self.create_connection(self._drag_start_pin, end_pin)
        self._drag_start_pin = None

    def mouseMoveEvent(self, event):
        if self._drag_connection:
            self.update_drag_connection(event.scenePos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_connection:
            self.end_drag_connection(event.scenePos())
        super().mouseReleaseEvent(event)

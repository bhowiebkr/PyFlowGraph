# node_graph.py
# The QGraphicsScene that manages nodes, connections, and their interactions.
# Now with a definitive fix for node resizing on initial graph load.

import uuid
import json
from PySide6.QtWidgets import QGraphicsScene, QApplication
from PySide6.QtCore import Qt, QPointF, QTimer, Signal
from PySide6.QtGui import QKeyEvent, QColor
from .node import Node
from .reroute_node import RerouteNode
from .connection import Connection
from .pin import Pin


from pyflowgraph.commands import (
    CommandHistory, CreateNodeCommand, DeleteNodeCommand, MoveNodeCommand,
    CreateConnectionCommand, DeleteConnectionCommand, CreateRerouteNodeCommand,
    CompositeCommand
)
import logging

logger = logging.getLogger(__name__)


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
        self.groups = []  # Initialize groups list
        self._drag_connection, self._drag_start_pin = None, None
        self.graph_title = "Untitled Graph"
        self.graph_description = ""
        self._is_pasting = False  # Flag to prevent Group.itemChange during paste operations
        # The text this editor last put on the clipboard. Pasting it back needs no question.
        self._last_copied_text = None
        # Asks the user before pasted nodes run their GUI code. Tests can replace it.
        self.confirm_pasted_code = self._ask_to_run_pasted_code
        
        # Command system integration
        self.command_history = CommandHistory()
        self._tracking_moves = {}  # Track node movements for command batching  # Track node movements for command batching  # Track node movements for command batching
    
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
        """Removes all nodes, connections, and groups from the scene."""
        # Remove all connections first
        for connection in list(self.connections):
            self.remove_connection(connection, use_command=False)
        
        # Remove all nodes directly (bypass command pattern for clearing)
        for node in list(self.nodes):
            self.remove_node(node, use_command=False)
        
        # Remove all groups
        if hasattr(self, 'groups'):
            for group in list(self.groups):
                self.removeItem(group)
            self.groups.clear()
        
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        # Handle undo/redo shortcuts
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Z:
                if event.modifiers() & Qt.ShiftModifier:
                    logger.debug(f"=== KEYBOARD REDO TRIGGERED ===")
                    self.redo_last_command()
                else:
                    logger.debug(f"=== KEYBOARD UNDO TRIGGERED ===")
                    self.undo_last_command()
                return
            elif event.key() == Qt.Key_Y:
                logger.debug(f"=== KEYBOARD REDO (Y) TRIGGERED ===")
                self.redo_last_command()
                return
            elif event.key() == Qt.Key_G:
                selected_nodes = [item for item in self.selectedItems() if isinstance(item, Node)]
                if len(selected_nodes) >= 2:
                    self._create_group_from_selection(selected_nodes)
                # If insufficient nodes, the validation in _create_group_from_selection will show an error
                return
        
        # Handle delete operations
        if event.key() == Qt.Key_Delete:
            logger.debug(f"=== KEYBOARD DELETE TRIGGERED ===")
            selected_items = list(self.selectedItems())
            logger.debug(f"Found {len(selected_items)} selected items")
            
            for i, item in enumerate(selected_items):
                logger.debug(f"Selected item {i}: {type(item).__name__} - {getattr(item, 'title', 'No title')} (ID: {id(item)})")
            
            if selected_items:
                commands = []
                
                # Use the improved DeleteMultipleCommand that handles all item types including Groups
                from pyflowgraph.commands.node.batch_operations import DeleteMultipleCommand
                delete_cmd = DeleteMultipleCommand(self, selected_items)
                logger.debug(f"Using DeleteMultipleCommand: {delete_cmd.get_description()}")
                result = self.execute_command(delete_cmd)
                logger.debug(f"DeleteMultipleCommand returned: {result}")
                return
                
                logger.debug(f"Created {len(commands)} delete commands")
                
                # Execute as composite command if multiple items
                if len(commands) > 1:
                    logger.debug(f"Executing composite command with {len(commands)} commands")
                    composite = CompositeCommand(f"Delete {len(commands)} items", commands)
                    result = self.execute_command(composite)
                    logger.debug(f"Composite command returned: {result}")
                elif len(commands) == 1:
                    logger.debug(f"Executing single command")
                    result = self.execute_command(commands[0])
                    logger.debug(f"Single command returned: {result}")
                else:
                    logger.debug(f"No commands to execute")
            else:
                logger.debug(f"No items selected for deletion")
        else:
            super().keyPressEvent(event)
    
    def _create_group_from_selection(self, selected_nodes):
        """Create a group from selected nodes using the group creation dialog"""
        # Validate selection
        try:
            from pyflowgraph.core.group import validate_group_creation
        except ImportError:
            from pyflowgraph.core.group import validate_group_creation
        
        is_valid, error_message = validate_group_creation(selected_nodes)
        
        if not is_valid:
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Invalid Selection")
            msg.setText(f"Cannot create group: {error_message}")
            msg.setIcon(QMessageBox.Warning)
            msg.exec()
            return
        
        # Show group creation dialog
        try:
            from pyflowgraph.ui.dialogs.group_creation_dialog import show_group_creation_dialog
        except ImportError:
            from pyflowgraph.ui.dialogs.group_creation_dialog import show_group_creation_dialog
        
        # Get the main window as parent for the dialog
        main_window = None
        views = self.views()
        if views:
            main_window = views[0].window()
        
        group_properties = show_group_creation_dialog(selected_nodes, main_window)
        
        if group_properties:
            # Create and execute the group creation command
            try:
                from pyflowgraph.commands.create_group_command import CreateGroupCommand
            except ImportError:
                from pyflowgraph.commands.create_group_command import CreateGroupCommand
            command = CreateGroupCommand(self, group_properties)
            self.execute_command(command)

    def copy_selected(self):
        """Copies selected nodes, their connections, and groups to the clipboard."""
        selected_nodes = [item for item in self.selectedItems() if isinstance(item, (Node, RerouteNode))]
        selected_groups = [item for item in self.selectedItems() if type(item).__name__ == 'Group']
        
        if not selected_nodes and not selected_groups:
            return {"requirements": [], "nodes": [], "groups": [], "connections": []}

        nodes_data = [node.serialize() for node in selected_nodes]
        groups_data = [group.serialize() for group in selected_groups]
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

        clipboard_data = {
            "requirements": requirements, 
            "nodes": nodes_data, 
            "groups": groups_data,
            "connections": connections_data
        }

        # Convert to markdown format for clipboard
        try:
            from pyflowgraph.data.flow_format import FlowFormatHandler
            handler = FlowFormatHandler()
            clipboard_markdown = handler.data_to_markdown(clipboard_data, "Clipboard Content", "Copied nodes and groups from PyFlowGraph")
            self._last_copied_text = clipboard_markdown
            QApplication.clipboard().setText(clipboard_markdown)
        except ImportError:
            # Fallback to JSON format if FlowFormatHandler is not available (e.g., during testing)
            import json
            self._last_copied_text = json.dumps(clipboard_data, indent=2)
            QApplication.clipboard().setText(self._last_copied_text)
        
        total_items = len(nodes_data) + len(groups_data)
        logger.info(f"Copied {len(nodes_data)} nodes and {len(groups_data)} groups ({total_items} items total) to clipboard as markdown.")
        
        return clipboard_data

    def paste(self, mouse_position=None):
        """Pastes nodes and connections from clipboard at mouse position or viewport center."""
        clipboard_text = QApplication.clipboard().text()
        
        # Use mouse position if provided, otherwise fall back to viewport center
        if mouse_position is not None:
            paste_pos = mouse_position
        else:
            # Existing fallback logic
            paste_pos = QPointF(0, 0)  # Default position
            views = self.views()
            if views:
                paste_pos = views[0].mapToScene(views[0].viewport().rect().center())
        
        data = self._parse_clipboard_text(clipboard_text)
        if data is None:
            logger.info("Clipboard does not contain valid graph data.")
            return

        if not self._may_run_pasted_code(clipboard_text, data):
            logger.info("Paste cancelled. The code of the pasted nodes did not run.")
            return

        try:
            self._paste_with_command(data, paste_pos)
        except Exception as e:
            logger.error(f"Paste failed: {e}")

    @staticmethod
    def _parse_clipboard_text(clipboard_text):
        """Return graph data from clipboard text in the .md format or in JSON, or None."""
        markdown_data = None
        try:
            from pyflowgraph.data.flow_format import FlowFormatHandler
            markdown_data = FlowFormatHandler().markdown_to_data(clipboard_text)
        except Exception:
            markdown_data = None
        if isinstance(markdown_data, dict) and markdown_data.get("nodes"):
            return markdown_data

        try:
            json_data = json.loads(clipboard_text)
        except (ValueError, TypeError):
            json_data = None
        if isinstance(json_data, dict):
            return json_data
        return markdown_data if isinstance(markdown_data, dict) else None

    @staticmethod
    def _normalize_clipboard_text(text):
        return (text or "").replace("\r\n", "\n").strip()

    def _may_run_pasted_code(self, clipboard_text, data):
        """Return True when the pasted nodes may be built, which runs their GUI code."""
        from pyflowgraph.data.graph_trust import nodes_with_open_code

        titles = nodes_with_open_code(data)
        if not titles:
            return True
        if self._last_copied_text is not None and (
            self._normalize_clipboard_text(clipboard_text) == self._normalize_clipboard_text(self._last_copied_text)
        ):
            return True
        return bool(self.confirm_pasted_code(titles))

    def _ask_to_run_pasted_code(self, titles):
        from PySide6.QtWidgets import QMessageBox
        from pyflowgraph.data.graph_trust import describe_nodes

        views = self.views()
        box = QMessageBox(views[0] if views else None)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Run Code from the Clipboard?")
        box.setText("Pasting these nodes runs code from the clipboard on this computer.")
        box.setInformativeText(
            "These nodes have GUI code that runs when they are added:\n"
            + describe_nodes(titles)
            + "\n\nPaste them only if you trust where the text came from."
        )
        paste_button = box.addButton("Paste and Run", QMessageBox.AcceptRole)
        cancel_button = box.addButton(QMessageBox.Cancel)
        box.setDefaultButton(cancel_button)
        box.exec()
        return box.clickedButton() is paste_button

    def _paste_with_command(self, data, paste_pos):
        """Helper method to paste using PasteNodesCommand."""
        if not data or not data.get('nodes'):
            logger.info("No nodes to paste.")
            return
        
        # Convert data format to match PasteNodesCommand expectations
        clipboard_data = self._convert_data_format(data)
        
        # Set paste operation flag to prevent Group.itemChange from moving nodes automatically
        self._is_pasting = True
        
        try:
            # Create and execute paste command
            from pyflowgraph.commands.node_commands import PasteNodesCommand
            paste_cmd = PasteNodesCommand(self, clipboard_data, paste_pos)
            result = self.execute_command(paste_cmd)
            
            if not result:
                logger.error("Failed to paste nodes.")
        finally:
            # Always clear the paste flag
            self._is_pasting = False
    
    def _convert_data_format(self, data):
        """Convert deserialize format to PasteNodesCommand format."""
        clipboard_data = {
            'nodes': [],
            'groups': [],
            'connections': []
        }
        
        # Convert nodes - preserve ALL properties
        for node_data in data.get('nodes', []):
            converted_node = {
                'id': node_data.get('uuid', node_data.get('id', '')),  # Try 'uuid' first, then 'id'
                'title': node_data.get('title', 'Unknown'),
                'description': node_data.get('description', ''),
                'code': node_data.get('code', ''),
                'pos': node_data.get('pos', [0, 0]),
                'size': node_data.get('size', [200, 150]),
                'colors': node_data.get('colors', {}),
                'gui_state': node_data.get('gui_state', {}),
                'gui_code': node_data.get('gui_code', ''),
                'gui_get_values_code': node_data.get('gui_get_values_code', ''),
                'is_reroute': node_data.get('is_reroute', False)
            }
            clipboard_data['nodes'].append(converted_node)
        
        # Convert groups
        for group_data in data.get('groups', []):
            # Groups use their full serialized data for pasting
            clipboard_data['groups'].append(group_data)
        
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
        """Serializes all nodes, connections, and groups."""
        nodes_data = [node.serialize() for node in self.nodes]
        connections_data = [conn.serialize() for conn in self.connections if conn.serialize()]
        groups_data = [group.serialize() for group in self.groups] if hasattr(self, 'groups') else []
        return {
            "graph_title": self.graph_title,
            "graph_description": self.graph_description,
            "nodes": nodes_data, 
            "connections": connections_data,
            "groups": groups_data
        }

    def deserialize(self, data, offset=QPointF(0, 0)):
        """Deserializes graph data, creating all nodes, connections, and groups."""
        if not data:
            return
        if offset == QPointF(0, 0):
            self.clear_graph()
            # Load graph metadata only when loading a complete graph (not copying/pasting)
            self.graph_title = data.get("graph_title", "Untitled Graph")
            self.graph_description = data.get("graph_description", "")

        uuid_to_node_map = {}
        nodes_to_update = []

        # First, deserialize nodes
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
                    if logger.isEnabledFor(logging.DEBUG) and (corrected_width != loaded_width or corrected_height != loaded_height):
                        logger.debug(f"Node '{node_data['title']}' size corrected from "
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

        # Then, deserialize connections
        for conn_data in data.get("connections", []):
            start_node = uuid_to_node_map.get(conn_data["start_node_uuid"])
            end_node = uuid_to_node_map.get(conn_data["end_node_uuid"])
            if start_node and end_node:
                # For connections, start_pin should be output and end_pin should be input
                start_pin = start_node.get_pin_by_name_and_direction(conn_data["start_pin_name"], "output")
                end_pin = end_node.get_pin_by_name_and_direction(conn_data["end_pin_name"], "input")
                if start_pin and end_pin:
                    self.create_connection(start_pin, end_pin, use_command=False)

        # Finally, deserialize groups (only for complete graph loading, not copy/paste)
        if offset == QPointF(0, 0) and "groups" in data:
            try:
                # Import Group class for deserialization
                from pyflowgraph.core.group import Group
                
                for group_data in data.get("groups", []):
                    # Deserialize the group
                    group = Group.deserialize(group_data)
                    
                    # Add to scene and groups list
                    self.addItem(group)
                    if not hasattr(self, 'groups'):
                        self.groups = []
                    self.groups.append(group)
                    
                    logger.info(f"Restored group '{group.name}' with {len(group.member_node_uuids)} members")
                    
            except ImportError as e:
                logger.warning(f"Could not import Group class for deserialization: {e}")
            except Exception as e:
                logger.warning(f"Failed to deserialize groups: {e}")

        # --- Definitive Resizing Fix ---
        # Defer the final layout calculation. This allows the Qt event loop to
        # process all pending widget creation and resizing events first, ensuring
        # that the size hints are accurate when fit_size_to_content is called.
        QTimer.singleShot(0, lambda: self.final_load_update(nodes_to_update))

    def final_load_update(self, nodes_to_update):
        """A helper method called by a timer to run the final layout pass."""
        
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
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Final size validation - Node '{node.title}' needs resize from "
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
        logger.debug(f"=== NODE GRAPH REMOVE_NODE START ===")
        logger.debug(f"remove_node called with use_command={use_command}")
        logger.debug(f"Node to remove: '{getattr(node, 'title', 'Unknown')}' (ID: {id(node)})")
        logger.debug(f"Graph has {len(self.nodes)} nodes before removal")
        logger.debug(f"Scene has {len(self.items())} items before removal")
        
        if use_command:
            logger.debug(f"Using command pattern for removal")
            # Use command pattern
            command = DeleteNodeCommand(self, node)
            result = self.execute_command(command)
            logger.debug(f"Command execution returned: {result}")
            logger.debug(f"=== NODE GRAPH REMOVE_NODE END (COMMAND) ===")
            return result
        else:
            logger.debug(f"Direct removal (bypassing command pattern)")
            # Direct removal (for internal use by commands)
            # First, remove all connections to/from this node
            connections_to_remove = []
            for connection in list(self.connections):
                if (hasattr(connection, 'start_pin') and connection.start_pin.node == node or 
                    hasattr(connection, 'end_pin') and connection.end_pin.node == node):
                    connections_to_remove.append(connection)
                    logger.debug(f"Found connection to remove: {connection}")
            
            logger.debug(f"Removing {len(connections_to_remove)} connections first")
            
            # Remove connections first
            for connection in connections_to_remove:
                logger.debug(f"Removing connection: {connection}")
                result = self.remove_connection(connection, use_command=False)
                logger.debug(f"Connection removal returned: {result}")
            
            # Then remove and destroy all pins
            if hasattr(node, "pins"):
                logger.debug(f"Node has {len(node.pins)} pins to clean up")
                for pin in list(node.pins):
                    # Clean up pin without trying to remove connections (already done)
                    logger.debug(f"Cleaning up pin: {pin}")
                    pin.connections.clear()  # Clear the connections list
                    pin.destroy()  # This will safely handle scene removal
                    logger.debug(f"Pin cleaned up")
                    
                # Clear all pin lists
                if hasattr(node, 'pins'):
                    node.pins.clear()
                    logger.debug(f"Cleared pins list")
                if hasattr(node, 'input_pins'):
                    node.input_pins.clear()
                    logger.debug(f"Cleared input_pins list")
                if hasattr(node, 'output_pins'):
                    node.output_pins.clear()
                    logger.debug(f"Cleared output_pins list")
                if hasattr(node, 'execution_pins'):
                    node.execution_pins.clear()
                    logger.debug(f"Cleared execution_pins list")
                if hasattr(node, 'data_pins'):
                    node.data_pins.clear()
                    logger.debug(f"Cleared data_pins list")
            
            # Finally remove the node itself
            logger.debug(f"Removing node from nodes list...")
            if node in self.nodes:
                self.nodes.remove(node)
                logger.debug(f"Node removed from nodes list (count now: {len(self.nodes)})")
            else:
                logger.warning(f"Node not in nodes list!")
                
            logger.debug(f"Removing node from scene...")
            if node.scene() == self:
                self.removeItem(node)
                logger.debug(f"Node removed from scene (items now: {len(self.items())})")
            else:
                logger.warning(f"Node not in scene or scene mismatch!")
                logger.debug(f"Node scene: {node.scene()}")
                logger.debug(f"This scene: {self}")
            
            logger.debug(f"=== NODE GRAPH REMOVE_NODE END (DIRECT) ===")
            return True

    def create_connection(self, start_pin, end_pin, use_command=True):
        """Create a connection, optionally using command pattern for undo/redo."""
        if start_pin.direction == "input":
            # A connection always starts at the output pin.
            start_pin, end_pin = end_pin, start_pin
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
            if connection.scene() is self:
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
            self.connect_dragged_pins(self._drag_start_pin, target_item)
        self._drag_start_pin = None

    def connect_dragged_pins(self, pin_a, pin_b):
        """Connect two pins that the user joined by a drag, in either direction.

        The output pin becomes the start of the connection. A connection already on the input
        pin is replaced in the same undo step, and only when the new connection is valid.
        """
        if pin_a.direction == "input":
            pin_a, pin_b = pin_b, pin_a
        if not pin_a.can_connect_to(pin_b, replace=True):
            return None
        if any(conn.start_pin is pin_a for conn in pin_b.connections):
            return None
        command = CreateConnectionCommand(self, pin_a, pin_b)
        if self.execute_command(command):
            return command.created_connection
        return None

    def mouseMoveEvent(self, event):
        if self._drag_connection:
            self.update_drag_connection(event.scenePos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_connection:
            self.end_drag_connection(event.scenePos())
        super().mouseReleaseEvent(event)

    def selectionChanged(self):
        """Override QGraphicsScene.selectionChanged to handle group resize handle updates"""
        super().selectionChanged()
        
        # Force update of all groups when scene selection changes
        # This ensures resize handles are properly shown/hidden
        for item in self.items():
            if type(item).__name__ == 'Group':
                # Prepare for potential bounding rect changes
                item.prepareGeometryChange()
                # Force visual update
                item.update()
                # Update scene area where handles might be drawn/cleared
                expanded_rect = item.boundingRect()
                scene_rect = item.mapRectToScene(expanded_rect)
                self.update(scene_rect)

    def handle_node_position_changed(self, node):
        """Handle node position changes and update group memberships accordingly"""
        if not hasattr(node, 'uuid'):
            return
        
        # Check all groups in the scene to see if this node should be added or removed
        for item in self.items():
            if type(item).__name__ == 'Group':
                is_node_inside = item._is_node_within_group_bounds(node)
                is_currently_member = item.is_member(node.uuid)
                
                if is_node_inside and not is_currently_member:
                    # Node moved into group - add it as a member
                    item.add_member_node(node.uuid)
                    # Update group title to reflect new member count
                    item.update()
                    
                elif not is_node_inside and is_currently_member:
                    # Node moved out of group - remove it as a member
                    item.remove_member_node(node.uuid)
                    # Update group title to reflect new member count
                    item.update()

"""
Batch node operations: paste, move multiple, delete multiple commands.

Handles operations that affect multiple nodes or complex multi-step operations.
"""

import uuid
import sys
import os
from typing import Dict, Any, List
from PySide6.QtCore import QPointF

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from commands.command_base import CompositeCommand
from .basic_operations import CreateNodeCommand, DeleteNodeCommand, MoveNodeCommand


class PasteNodesCommand(CompositeCommand):
    """Command for pasting nodes and connections as a single undo unit."""
    
    def __init__(self, node_graph, clipboard_data: Dict[str, Any], paste_position: QPointF):
        """
        Initialize paste nodes command.
        
        Args:
            node_graph: The NodeGraph instance
            clipboard_data: Data from clipboard containing nodes, groups, and connections
            paste_position: Position to paste nodes at
        """
        # Parse clipboard data to determine operation description
        node_count = len(clipboard_data.get('nodes', []))
        group_count = len(clipboard_data.get('groups', []))
        connection_count = len(clipboard_data.get('connections', []))
        
        if node_count == 1 and group_count == 0 and connection_count == 0:
            description = f"Paste '{clipboard_data['nodes'][0].get('title', 'node')}'"
        elif node_count > 1 and group_count == 0 and connection_count == 0:
            description = f"Paste {node_count} nodes"
        elif node_count == 0 and group_count == 1 and connection_count == 0:
            description = f"Paste group '{clipboard_data['groups'][0].get('name', 'Group')}'"
        elif node_count > 0 and group_count > 0:
            description = f"Paste {node_count} nodes and {group_count} groups"
        elif group_count > 1:
            description = f"Paste {group_count} groups"
        else:
            total_items = node_count + group_count
            description = f"Paste {total_items} items with {connection_count} connections"
        
        # Store data for execute method to handle connection and group creation
        self.node_graph = node_graph
        self.clipboard_data = clipboard_data
        self.paste_position = paste_position
        self.uuid_mapping = {}  # Map old UUIDs to new UUIDs
        self.created_nodes = []
        self.created_groups = []
        
        # Create only node creation commands initially
        commands = []
        nodes_data = clipboard_data.get('nodes', [])
        groups_data = clipboard_data.get('groups', [])
        
        # Check if we're pasting groups with nodes - use different positioning logic
        has_groups = len(groups_data) > 0
        
        for i, node_data in enumerate(nodes_data):
            # Generate new UUID for this node
            old_uuid = node_data.get('id', str(uuid.uuid4()))
            new_uuid = str(uuid.uuid4())
            self.uuid_mapping[old_uuid] = new_uuid
            
            if has_groups:
                # When pasting groups, preserve original absolute positions
                # The group will handle positioning itself and its members
                original_pos = node_data.get('pos', [0, 0])
                node_position = QPointF(original_pos[0], original_pos[1])
            else:
                # When pasting nodes only, arrange in grid pattern
                offset_x = (i % 3) * 200  # Arrange in grid pattern
                offset_y = (i // 3) * 150
                node_position = QPointF(
                    paste_position.x() + offset_x,
                    paste_position.y() + offset_y
                )
            
            # Create node command with all properties
            create_cmd = CreateNodeCommand(
                node_graph=node_graph,
                title=node_data.get('title', 'Pasted Node'),
                position=node_position,
                node_id=new_uuid,
                code=node_data.get('code', ''),
                description=node_data.get('description', ''),
                size=node_data.get('size', [200, 150]),
                colors=node_data.get('colors', {}),
                gui_state=node_data.get('gui_state', {}),
                gui_code=node_data.get('gui_code', ''),
                gui_get_values_code=node_data.get('gui_get_values_code', ''),
                is_reroute=node_data.get('is_reroute', False)
            )
            commands.append(create_cmd)
            self.created_nodes.append((create_cmd, node_data))
        
        super().__init__(description, commands)
    
    def execute(self) -> bool:
        """Execute node creation first, then create connections and groups."""
        # First execute node creation commands
        if not super().execute():
            return False
        
        # Now create connections using actual pin objects
        connections_data = self.clipboard_data.get('connections', [])
        connection_commands = []
        
        for conn_data in connections_data:
            # Map old UUIDs to new UUIDs
            old_output_node_id = conn_data.get('output_node_id', '')
            old_input_node_id = conn_data.get('input_node_id', '')
            
            new_output_node_id = self.uuid_mapping.get(old_output_node_id)
            new_input_node_id = self.uuid_mapping.get(old_input_node_id)
            
            # Only create connection if both nodes are being pasted
            if new_output_node_id and new_input_node_id:
                # Find the actual created nodes
                output_node = self._find_node_by_id(new_output_node_id)
                input_node = self._find_node_by_id(new_input_node_id)
                
                if output_node and input_node:
                    # Find pins by name
                    output_pin_name = conn_data.get('output_pin_name', '')
                    input_pin_name = conn_data.get('input_pin_name', '')
                    
                    output_pin = output_node.get_pin_by_name(output_pin_name)
                    input_pin = input_node.get_pin_by_name(input_pin_name)
                    
                    if output_pin and input_pin:
                        # Import here to avoid circular imports
                        from commands.connection_commands import CreateConnectionCommand
                        
                        conn_cmd = CreateConnectionCommand(
                            node_graph=self.node_graph,
                            output_pin=output_pin,
                            input_pin=input_pin
                        )
                        connection_commands.append(conn_cmd)
        
        # Execute connection commands
        for conn_cmd in connection_commands:
            result = conn_cmd.execute()
            if result:
                conn_cmd._mark_executed()
                self.commands.append(conn_cmd)
                self.executed_commands.append(conn_cmd)
            else:
                print(f"Failed to create connection: {conn_cmd.get_description()}")
        
        # DEBUG: Check node positions before group processing
        print("DEBUG: Node positions after creation, before group processing:")
        for cmd, node_data in self.created_nodes:
            if cmd.created_node:
                pos = cmd.created_node.pos()
                print(f"  {cmd.created_node.title}: ({pos.x()}, {pos.y()})")
        
        # Create groups after nodes and connections are established
        groups_data = self.clipboard_data.get('groups', [])
        group_commands = []
        
        for group_data in groups_data:
            # Generate new UUID for the group
            old_group_uuid = group_data.get('uuid', str(uuid.uuid4()))
            new_group_uuid = str(uuid.uuid4())
            
            # Update member node UUIDs to use new UUIDs
            old_member_uuids = group_data.get('member_node_uuids', [])
            new_member_uuids = []
            for old_member_uuid in old_member_uuids:
                new_member_uuid = self.uuid_mapping.get(old_member_uuid)
                if new_member_uuid:  # Only include nodes that were pasted
                    new_member_uuids.append(new_member_uuid)
            
            # Only create group if it has member nodes that were pasted
            if new_member_uuids:
                # Calculate transformation needed to move group to paste position
                group_position = group_data.get('position', {'x': 0, 'y': 0})
                original_group_pos = QPointF(group_position['x'], group_position['y'])
                transform_offset = self.paste_position - original_group_pos
                
                # Position group at paste position
                offset_position = self.paste_position
                
                # Transform all member nodes by the same offset to maintain relative positions
                print(f"DEBUG: Applying transform offset ({transform_offset.x()}, {transform_offset.y()}) to nodes")
                for node_uuid in new_member_uuids:
                    found_node = None
                    for cmd, _ in self.created_nodes:
                        if hasattr(cmd, 'created_node') and cmd.created_node and cmd.created_node.uuid == node_uuid:
                            found_node = cmd.created_node
                            break
                    if found_node:
                        current_pos = found_node.pos()
                        new_pos = current_pos + transform_offset
                        print(f"  {found_node.title}: ({current_pos.x()}, {current_pos.y()}) -> ({new_pos.x()}, {new_pos.y()})")
                        found_node.setPos(new_pos)
                
                # Create modified group properties for the command
                group_properties = {
                    'name': group_data.get('name', 'Pasted Group'),
                    'description': group_data.get('description', ''),
                    'member_node_uuids': new_member_uuids,
                    'auto_size': False,  # Keep original size
                    'padding': group_data.get('padding', 20)
                }
                
                # Import here to avoid circular imports  
                from commands.create_group_command import CreateGroupCommand
                
                group_cmd = CreateGroupCommand(self.node_graph, group_properties)
                # Override the UUID to use our new one
                group_cmd.group_uuid = new_group_uuid
                
                result = group_cmd.execute()
                if result:
                    group_cmd._mark_executed()
                    self.commands.append(group_cmd)
                    self.executed_commands.append(group_cmd)
                    
                    # Apply additional properties (position, size, colors)
                    created_group = group_cmd.created_group
                    if created_group:
                        created_group.setPos(offset_position)
                        
                        # Use original group size since we preserved relative layout
                        size = group_data.get('size', {'width': 200, 'height': 150})
                        created_group.width = size['width']
                        created_group.height = size['height']
                        
                        created_group.setRect(0, 0, created_group.width, created_group.height)
                        
                        # Restore colors if present
                        colors = group_data.get('colors', {})
                        if colors:
                            from PySide6.QtGui import QColor, QPen, QBrush
                            
                            if 'background' in colors:
                                bg = colors['background']
                                created_group.color_background = QColor(bg['r'], bg['g'], bg['b'], bg['a'])
                                created_group.brush_background = QBrush(created_group.color_background)
                            
                            if 'border' in colors:
                                border = colors['border']
                                created_group.color_border = QColor(border['r'], border['g'], border['b'], border['a'])
                                created_group.pen_border = QPen(created_group.color_border, 2.0)
                            
                            if 'title_bg' in colors:
                                title_bg = colors['title_bg']
                                created_group.color_title_bg = QColor(title_bg['r'], title_bg['g'], title_bg['b'], title_bg['a'])
                                created_group.brush_title = QBrush(created_group.color_title_bg)
                            
                            if 'title_text' in colors:
                                title_text = colors['title_text']
                                created_group.color_title_text = QColor(title_text['r'], title_text['g'], title_text['b'], title_text['a'])
                            
                            if 'selection' in colors:
                                selection = colors['selection']
                                created_group.color_selection = QColor(selection['r'], selection['g'], selection['b'], selection['a'])
                                created_group.pen_selected = QPen(created_group.color_selection, 3.0)
                        
                        created_group.update()
                    
                    self.created_groups.append(group_cmd)
                    print(f"Pasted group '{group_properties['name']}' with {len(new_member_uuids)} members")
                else:
                    print(f"Failed to create group: {group_properties['name']}")
        
        # Schedule deferred GUI update for pasted nodes - similar to file loading
        # This ensures GUI widgets refresh properly for nodes with GUI code
        nodes_to_update = []
        for cmd, _ in self.created_nodes:
            if cmd.created_node:
                # Check if it's a reroute node by checking for is_reroute attribute
                is_reroute = hasattr(cmd.created_node, 'is_reroute') and cmd.created_node.is_reroute
                if not is_reroute:
                    # Only update regular nodes that might have GUI widgets
                    nodes_to_update.append(cmd.created_node)
        
        if nodes_to_update:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._final_paste_update(nodes_to_update))
        
        return True
    
    def _find_node_by_id(self, node_id: str):
        """Find node in graph by UUID."""
        for node in self.node_graph.nodes:
            if hasattr(node, 'uuid') and node.uuid == node_id:
                return node
        return None
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage for paste operation."""
        base_size = 1024
        data_size = len(str(self.clipboard_data)) * 2
        mapping_size = len(self.uuid_mapping) * 100
        return base_size + data_size + mapping_size

    def _final_paste_update(self, nodes_to_update):
        """Final update pass for pasted nodes - ensures GUI widgets refresh properly."""
        for node in nodes_to_update:
            try:
                if node.scene() is None:
                    continue  # Node has been removed from scene
                
                # Force complete layout rebuild like file loading does
                node._update_layout()
                
                # Update all pin connections
                for pin in node.pins:
                    pin.update_connections()
                
                # Force node visual update
                node.update()
            except RuntimeError:
                # Node has been deleted, skip
                continue
        
        # Force scene update
        self.node_graph.update()


class MoveMultipleCommand(CompositeCommand):
    """Command for moving multiple nodes as a single undo unit."""
    
    def __init__(self, node_graph, nodes_and_positions: List[tuple]):
        """
        Initialize move multiple command.
        
        Args:
            node_graph: The NodeGraph instance
            nodes_and_positions: List of (node, old_pos, new_pos) tuples
        """
        # Create individual move commands
        commands = []
        node_count = len(nodes_and_positions)
        
        if node_count == 1:
            node = nodes_and_positions[0][0]
            description = f"Move '{node.title}'"
        else:
            description = f"Move {node_count} nodes"
        
        for node, old_pos, new_pos in nodes_and_positions:
            move_cmd = MoveNodeCommand(node_graph, node, old_pos, new_pos)
            commands.append(move_cmd)
        
        super().__init__(description, commands)
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage for move operation."""
        base_size = 256
        return base_size + super().get_memory_usage()


class DeleteMultipleCommand(CompositeCommand):
    """Command for deleting multiple items as a single undo unit."""
    
    def __init__(self, node_graph, selected_items: List):
        """
        Initialize delete multiple command.
        
        Args:
            node_graph: The NodeGraph instance
            selected_items: List of items (nodes and connections) to delete
        """
        # Import here to avoid circular imports
        from core.node import Node
        from core.reroute_node import RerouteNode
        from core.connection import Connection
        
        # Create individual delete commands
        commands = []
        node_count = 0
        connection_count = 0
        
        for item in selected_items:
            if isinstance(item, (Node, RerouteNode)):
                commands.append(DeleteNodeCommand(node_graph, item))
                node_count += 1
            elif isinstance(item, Connection):
                from commands.connection_commands import DeleteConnectionCommand
                commands.append(DeleteConnectionCommand(node_graph, item))
                connection_count += 1
        
        # Generate description
        if node_count > 0 and connection_count > 0:
            description = f"Delete {node_count} nodes and {connection_count} connections"
        elif node_count > 1:
            description = f"Delete {node_count} nodes"
        elif node_count == 1:
            node_title = getattr(selected_items[0], 'title', 'node')
            description = f"Delete '{node_title}'"
        elif connection_count > 1:
            description = f"Delete {connection_count} connections"
        else:
            description = f"Delete {len(selected_items)} items"
        
        super().__init__(description, commands)
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage for delete operation."""
        base_size = 512
        return base_size + super().get_memory_usage()
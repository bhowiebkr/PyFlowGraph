"""
Command implementations for node operations in PyFlowGraph.

Provides undoable commands for all node-related operations including
creation, deletion, movement, and property changes.
"""

import uuid
from typing import Dict, Any, List, Optional
from PySide6.QtCore import QPointF
from .command_base import CommandBase, CompositeCommand


class CreateNodeCommand(CommandBase):
    """Command for creating nodes with full state preservation."""
    
    def __init__(self, node_graph, title: str, position: QPointF, 
                 node_id: str = None, code: str = "", description: str = ""):
        """
        Initialize create node command.
        
        Args:
            node_graph: The NodeGraph instance
            title: Node title/type
            position: Position to create node at
            node_id: Optional specific node ID (for undo consistency)
            code: Initial code for the node
            description: Node description
        """
        super().__init__(f"Create '{title}' node")
        self.node_graph = node_graph
        self.title = title
        self.position = position
        self.node_id = node_id or str(uuid.uuid4())
        self.code = code
        self.node_description = description
        self.created_node = None
    
    def execute(self) -> bool:
        """Create the node and add to graph."""
        try:
            # Import here to avoid circular imports
            from node import Node
            
            # Create the node
            self.created_node = Node(self.title)
            self.created_node.uuid = self.node_id
            self.created_node.description = self.node_description
            self.created_node.setPos(self.position)
            
            if self.code:
                self.created_node.code = self.code
                self.created_node.update_pins_from_code()
            
            # Add to graph
            self.node_graph.addItem(self.created_node)
            self.node_graph.nodes.append(self.created_node)
            
            self._mark_executed()
            return True
            
        except Exception as e:
            print(f"Failed to create node: {e}")
            return False
    
    def undo(self) -> bool:
        """Remove the created node."""
        if not self.created_node or self.created_node not in self.node_graph.nodes:
            return False
        
        try:
            # Remove all connections to this node first
            connections_to_remove = []
            for connection in list(self.node_graph.connections):
                if (hasattr(connection, 'start_pin') and connection.start_pin.node == self.created_node or 
                    hasattr(connection, 'end_pin') and connection.end_pin.node == self.created_node):
                    connections_to_remove.append(connection)
            
            for connection in connections_to_remove:
                # Remove from connections list first
                if connection in self.node_graph.connections:
                    self.node_graph.connections.remove(connection)
                # Remove from scene if it's still there
                if connection.scene() == self.node_graph:
                    self.node_graph.removeItem(connection)
            
            # Remove node from graph
            if self.created_node in self.node_graph.nodes:
                self.node_graph.nodes.remove(self.created_node)
            if self.created_node.scene() == self.node_graph:
                self.node_graph.removeItem(self.created_node)
            
            self._mark_undone()
            return True
            
        except Exception as e:
            print(f"Failed to undo node creation: {e}")
            return False
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage of this command."""
        base_size = 512
        title_size = len(self.title) * 2
        code_size = len(self.code) * 2
        description_size = len(self.node_description) * 2
        return base_size + title_size + code_size + description_size


class DeleteNodeCommand(CommandBase):
    """Command for deleting nodes with complete state preservation."""
    
    def __init__(self, node_graph, node):
        """
        Initialize delete node command.
        
        Args:
            node_graph: The NodeGraph instance
            node: Node to delete
        """
        super().__init__(f"Delete '{node.title}' node")
        self.node_graph = node_graph
        self.node = node
        self.node_state = None
        self.affected_connections = []
        self.node_index = None
    
    def execute(self) -> bool:
        """Delete node after preserving complete state."""
        try:
            # Check if this node object is actually in the nodes list
            found_in_list = False
            node_in_list = None
            for i, node in enumerate(self.node_graph.nodes):
                if node is self.node:  # Same object reference
                    found_in_list = True
                    node_in_list = node
                    self.node_index = i
                    break
                elif hasattr(node, 'uuid') and hasattr(self.node, 'uuid') and node.uuid == self.node.uuid:
                    # Use the node that's actually in the list (UUID synchronization fix)
                    self.node = node
                    found_in_list = True
                    node_in_list = node
                    self.node_index = i
                    break
            
            if not found_in_list:
                print(f"Error: Node '{getattr(self.node, 'title', 'Unknown')}' not found in graph")
                return False
            
            # Preserve complete node state including colors and size
            self.node_state = {
                'id': self.node.uuid,
                'title': self.node.title,
                'description': getattr(self.node, 'description', ''),
                'position': self.node.pos(),
                'code': getattr(self.node, 'code', ''),
                'gui_code': getattr(self.node, 'gui_code', ''),
                'gui_get_values_code': getattr(self.node, 'gui_get_values_code', ''),
                'function_name': getattr(self.node, 'function_name', None),
                'width': getattr(self.node, 'width', 150),
                'height': getattr(self.node, 'height', 150),
                'base_width': getattr(self.node, 'base_width', 150),
                'is_reroute': getattr(self.node, 'is_reroute', False),
                # Preserve colors
                'color_title_bar': getattr(self.node, 'color_title_bar', None),
                'color_body': getattr(self.node, 'color_body', None),
                'color_title_text': getattr(self.node, 'color_title_text', None),
                # Preserve GUI state
                'gui_state': {}
            }
            
            # Try to capture GUI state if possible
            try:
                if hasattr(self.node, 'gui_widgets') and self.node.gui_widgets and self.node.gui_get_values_code:
                    scope = {"widgets": self.node.gui_widgets}
                    exec(self.node.gui_get_values_code, scope)
                    get_values_func = scope.get("get_values")
                    if callable(get_values_func):
                        self.node_state['gui_state'] = get_values_func(self.node.gui_widgets)
                        print(f"DEBUG: Captured GUI state: {self.node_state['gui_state']}")
            except Exception as e:
                print(f"DEBUG: Could not capture GUI state: {e}")
            
            # Check connections before removal
            connections_to_node = []
            for connection in list(self.node_graph.connections):
                if (hasattr(connection, 'start_pin') and connection.start_pin.node == self.node or 
                    hasattr(connection, 'end_pin') and connection.end_pin.node == self.node):
                    connections_to_node.append(connection)
            
            # Preserve affected connections
            self.affected_connections = []
            for connection in connections_to_node:
                
                # Handle different pin structures for regular nodes vs RerouteNodes
                start_node = connection.start_pin.node
                end_node = connection.end_pin.node
                
                # Get pin indices based on node type
                if hasattr(start_node, 'is_reroute') and start_node.is_reroute:
                    # RerouteNode - use single pins
                    output_pin_index = 0 if connection.start_pin == start_node.output_pin else -1
                else:
                    # Regular Node - use pin lists
                    output_pin_index = self._get_pin_index(start_node.output_pins, connection.start_pin)
                
                if hasattr(end_node, 'is_reroute') and end_node.is_reroute:
                    # RerouteNode - use single pins
                    input_pin_index = 0 if connection.end_pin == end_node.input_pin else -1
                else:
                    # Regular Node - use pin lists
                    input_pin_index = self._get_pin_index(end_node.input_pins, connection.end_pin)
                
                conn_data = {
                    'connection': connection,
                    'output_node_id': start_node.uuid,
                    'output_pin_index': output_pin_index,
                    'input_node_id': end_node.uuid,
                    'input_pin_index': input_pin_index
                }
                self.affected_connections.append(conn_data)
                
                # Remove connection safely
                if connection in self.node_graph.connections:
                    self.node_graph.connections.remove(connection)
                    
                if connection.scene() == self.node_graph:
                    self.node_graph.removeItem(connection)
            
            # Remove node from graph safely
            if self.node in self.node_graph.nodes:
                self.node_graph.nodes.remove(self.node)
            else:
                print(f"Error: Node not in nodes list during removal")
                return False
                
            if self.node.scene() == self.node_graph:
                self.node_graph.removeItem(self.node)
            else:
                print(f"Error: Node not in scene or scene mismatch")
                return False
            
            self._mark_executed()
            return True
            
        except Exception as e:
            print(f"Error: Failed to delete node: {e}")
            return False
    
    def undo(self) -> bool:
        """Restore node with complete state and reconnections."""
        if not self.node_state:
            print(f"Error: No node state to restore")
            return False
        
        try:
            
            # Import here to avoid circular imports
            from node import Node
            from PySide6.QtGui import QColor
            
            # Recreate node with preserved state - check if it was a RerouteNode
            if self.node_state.get('is_reroute', False):
                # Recreate as RerouteNode
                from reroute_node import RerouteNode
                restored_node = RerouteNode()
                restored_node.uuid = self.node_state['id']
                restored_node.setPos(self.node_state['position'])
                # RerouteNodes don't have most of the properties that regular nodes have
            else:
                # Recreate as regular Node
                restored_node = Node(self.node_state['title'])
                restored_node.uuid = self.node_state['id']
                restored_node.description = self.node_state['description']
                restored_node.setPos(self.node_state['position'])
                restored_node.code = self.node_state['code']
                restored_node.gui_code = self.node_state['gui_code']
                restored_node.gui_get_values_code = self.node_state['gui_get_values_code']
                restored_node.function_name = self.node_state['function_name']
            
            # Only apply regular node properties if it's not a RerouteNode
            if not self.node_state.get('is_reroute', False):
                from debug_config import should_debug, DEBUG_UNDO_REDO
                if should_debug(DEBUG_UNDO_REDO):
                    print(f"DEBUG: Restoring regular node properties for '{self.node_state['title']}'")
                    print(f"DEBUG: Original size: {self.node_state['width']}x{self.node_state['height']}")
                # Restore size BEFORE updating pins (important for layout)
                restored_node.width = self.node_state['width']
                restored_node.height = self.node_state['height']
                restored_node.base_width = self.node_state['base_width']
                
                # Restore colors
                if self.node_state['color_title_bar']:
                    if isinstance(self.node_state['color_title_bar'], str):
                        restored_node.color_title_bar = QColor(self.node_state['color_title_bar'])
                    else:
                        restored_node.color_title_bar = self.node_state['color_title_bar']
                
                if self.node_state['color_body']:
                    if isinstance(self.node_state['color_body'], str):
                        restored_node.color_body = QColor(self.node_state['color_body'])
                    else:
                        restored_node.color_body = self.node_state['color_body']
                
                if self.node_state['color_title_text']:
                    if isinstance(self.node_state['color_title_text'], str):
                        restored_node.color_title_text = QColor(self.node_state['color_title_text'])
                    else:
                        restored_node.color_title_text = self.node_state['color_title_text']
                
                # Update pins to match saved state BEFORE setting size
                if should_debug(DEBUG_UNDO_REDO):
                    print(f"DEBUG: Updating pins from code")
                restored_node.update_pins_from_code()
                
                # Calculate minimum size requirements for validation
                min_width, min_height = restored_node.calculate_absolute_minimum_size()
                
                # Validate restored size against minimum requirements
                original_width = self.node_state['width']
                original_height = self.node_state['height']
                corrected_width = max(original_width, min_width)
                corrected_height = max(original_height, min_height)
                
                if should_debug(DEBUG_UNDO_REDO) and (corrected_width != original_width or corrected_height != original_height):
                    print(f"DEBUG: Node restoration size corrected from "
                          f"{original_width}x{original_height} to {corrected_width}x{corrected_height}")
                
                # Apply validated size
                restored_node.width = corrected_width
                restored_node.height = corrected_height
                restored_node.base_width = self.node_state['base_width']
                
                if should_debug(DEBUG_UNDO_REDO):
                    print(f"DEBUG: Node size set to {restored_node.width}x{restored_node.height}")
            
            # Force visual update with correct colors and size
            restored_node.update()
            
            # Add back to graph at original position
            if self.node_index is not None and self.node_index <= len(self.node_graph.nodes):
                self.node_graph.nodes.insert(self.node_index, restored_node)
            else:
                self.node_graph.nodes.append(restored_node)
            
            self.node_graph.addItem(restored_node)
            
            # Apply GUI state BEFORE final layout
            if self.node_state.get('gui_state'):
                try:
                    if should_debug(DEBUG_UNDO_REDO):
                        print(f"DEBUG: Applying GUI state")
                    restored_node.apply_gui_state(self.node_state['gui_state'])
                except Exception as e:
                    if should_debug(DEBUG_UNDO_REDO):
                        print(f"DEBUG: GUI state restoration failed: {e}")
            
            # Restore connections
            restored_connections = 0
            for conn_data in self.affected_connections:
                # Find nodes by ID
                output_node = self._find_node_by_id(conn_data['output_node_id'])
                input_node = self._find_node_by_id(conn_data['input_node_id'])
                
                if output_node and input_node:
                    # Get pins by index based on node type
                    try:
                        # Handle output pin
                        if hasattr(output_node, 'is_reroute') and output_node.is_reroute:
                            # RerouteNode - use single output pin
                            output_pin = output_node.output_pin
                        else:
                            # Regular Node - use pin list
                            output_pin = output_node.output_pins[conn_data['output_pin_index']]
                        
                        # Handle input pin
                        if hasattr(input_node, 'is_reroute') and input_node.is_reroute:
                            # RerouteNode - use single input pin
                            input_pin = input_node.input_pin
                        else:
                            # Regular Node - use pin list
                            input_pin = input_node.input_pins[conn_data['input_pin_index']]
                        
                        # Recreate connection
                        from connection import Connection
                        new_connection = Connection(output_pin, input_pin)
                        self.node_graph.addItem(new_connection)
                        self.node_graph.connections.append(new_connection)
                        restored_connections += 1
                        
                    except (IndexError, AttributeError):
                        pass  # Connection restoration failed, but continue with other connections
            
            # Final layout update sequence (only for regular nodes)
            if not self.node_state.get('is_reroute', False):
                if should_debug(DEBUG_UNDO_REDO):
                    print(f"DEBUG: Final layout update sequence")
                
                # Force layout update to ensure pins are positioned correctly
                restored_node._update_layout()
                
                # Ensure size still meets minimum requirements after GUI state
                restored_node.fit_size_to_content()
                
                if should_debug(DEBUG_UNDO_REDO):
                    print(f"DEBUG: Final node size: {restored_node.width}x{restored_node.height}")
                
            # Final visual refresh
            restored_node.update()
            
            # Update node reference
            self.node = restored_node
            
            if should_debug(DEBUG_UNDO_REDO):
                print(f"DEBUG: Node restoration completed successfully")
            self._mark_undone()
            return True
            
        except Exception as e:
            print(f"Error: Failed to undo node deletion: {e}")
            return False
    
    def _find_node_by_id(self, node_id: str):
        """Find node in graph by UUID."""
        for node in self.node_graph.nodes:
            if node.uuid == node_id:
                return node
        return None
    
    def _get_pin_index(self, pin_list, pin):
        """Safely get pin index."""
        try:
            return pin_list.index(pin)
        except (ValueError, AttributeError):
            return 0
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage of this command."""
        if not self.node_state:
            return 512
        
        base_size = 1024
        code_size = len(self.node_state.get('code', '')) * 2
        gui_code_size = len(self.node_state.get('gui_code', '')) * 2
        title_size = len(self.node_state.get('title', '')) * 2
        connections_size = len(self.affected_connections) * 200
        
        return base_size + code_size + gui_code_size + title_size + connections_size


class MoveNodeCommand(CommandBase):
    """Command for moving nodes with position tracking."""
    
    def __init__(self, node_graph, node, old_position: QPointF, new_position: QPointF):
        """
        Initialize move node command.
        
        Args:
            node_graph: The NodeGraph instance
            node: Node to move
            old_position: Original position
            new_position: New position
        """
        super().__init__(f"Move '{node.title}' node")
        self.node_graph = node_graph
        self.node = node
        self.old_position = old_position
        self.new_position = new_position
    
    def execute(self) -> bool:
        """Move node to new position."""
        try:
            self.node.setPos(self.new_position)
            self._mark_executed()
            return True
        except Exception as e:
            print(f"Failed to move node: {e}")
            return False
    
    def undo(self) -> bool:
        """Move node back to original position."""
        try:
            self.node.setPos(self.old_position)
            self._mark_undone()
            return True
        except Exception as e:
            print(f"Failed to undo node move: {e}")
            return False
    
    def can_merge_with(self, other: CommandBase) -> bool:
        """Check if this move can be merged with another move."""
        return (isinstance(other, MoveNodeCommand) and 
                other.node == self.node and
                abs(other.timestamp - self.timestamp) < 1.0)  # Within 1 second
    
    def merge_with(self, other: CommandBase) -> Optional[CommandBase]:
        """Merge with another move command."""
        if not self.can_merge_with(other):
            return None
        
        # Create merged command using original start position and latest end position
        return MoveNodeCommand(
            self.node_graph,
            self.node,
            self.old_position,
            other.new_position
        )


class PropertyChangeCommand(CommandBase):
    """Command for node property changes."""
    
    def __init__(self, node_graph, node, property_name: str, old_value: Any, new_value: Any):
        """
        Initialize property change command.
        
        Args:
            node_graph: The NodeGraph instance
            node: Node whose property is changing
            property_name: Name of the property
            old_value: Original value
            new_value: New value
        """
        super().__init__(f"Change '{property_name}' of '{node.title}'")
        self.node_graph = node_graph
        self.node = node
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
    
    def execute(self) -> bool:
        """Apply the property change."""
        try:
            setattr(self.node, self.property_name, self.new_value)
            
            # Special handling for certain properties
            if self.property_name in ['code', 'gui_code']:
                self.node.update_pins_from_code()
            elif self.property_name in ['width', 'height']:
                self.node.fit_size_to_content()
            
            self._mark_executed()
            return True
        except Exception as e:
            print(f"Failed to change property: {e}")
            return False
    
    def undo(self) -> bool:
        """Revert the property change."""
        try:
            setattr(self.node, self.property_name, self.old_value)
            
            # Special handling for certain properties
            if self.property_name in ['code', 'gui_code']:
                self.node.update_pins_from_code()
            elif self.property_name in ['width', 'height']:
                self.node.fit_size_to_content()
            
            self._mark_undone()
            return True
        except Exception as e:
            print(f"Failed to undo property change: {e}")
            return False
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage of this command."""
        base_size = 256
        old_size = len(str(self.old_value)) * 2 if self.old_value else 0
        new_size = len(str(self.new_value)) * 2 if self.new_value else 0
        return base_size + old_size + new_size


class CodeChangeCommand(CommandBase):
    """Command for tracking code changes in nodes."""
    
    def __init__(self, node_graph, node, old_code: str, new_code: str):
        """
        Initialize code change command.
        
        Args:
            node_graph: The NodeGraph instance
            node: Node whose code is changing
            old_code: Original code
            new_code: New code
        """
        super().__init__(f"Change code in '{node.title}'")
        self.node_graph = node_graph
        self.node = node
        self.old_code = old_code
        self.new_code = new_code
    
    def execute(self) -> bool:
        """Apply the code change."""
        try:
            self.node.code = self.new_code
            self.node.update_pins_from_code()
            self._mark_executed()
            return True
        except Exception as e:
            print(f"Failed to change code: {e}")
            return False
    
    def undo(self) -> bool:
        """Revert the code change."""
        try:
            self.node.code = self.old_code
            self.node.update_pins_from_code()
            self._mark_undone()
            return True
        except Exception as e:
            print(f"Failed to undo code change: {e}")
            return False
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage for code changes."""
        base_size = 512
        old_code_size = len(self.old_code) * 2
        new_code_size = len(self.new_code) * 2
        return base_size + old_code_size + new_code_size
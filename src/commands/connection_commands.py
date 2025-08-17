"""
Command implementations for connection operations in PyFlowGraph.

Provides undoable commands for all connection-related operations including
creation, deletion, and reroute node operations.
"""

import sys
import os
from typing import Dict, Any, Optional

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .command_base import CommandBase


class CreateConnectionCommand(CommandBase):
    """Command for creating connections between pins."""
    
    def __init__(self, node_graph, output_pin, input_pin):
        """
        Initialize create connection command.
        
        Args:
            node_graph: The NodeGraph instance
            output_pin: Source pin for the connection
            input_pin: Target pin for the connection
        """
        # Note: output_pin is the source (start), input_pin is the target (end)
        output_name = getattr(output_pin, 'name', 'output')
        input_name = getattr(input_pin, 'name', 'input')
        super().__init__(f"Connect {output_pin.node.title}.{output_name} to {input_pin.node.title}.{input_name}")
        
        self.node_graph = node_graph
        self.output_pin = output_pin  # This becomes start_pin in Connection
        self.input_pin = input_pin    # This becomes end_pin in Connection
        self.created_connection = None
        
        # Store connection data for restoration (handle different node types)
        output_node = output_pin.node
        input_node = input_pin.node
        
        # Get pin indices based on node type
        if hasattr(output_node, 'is_reroute') and output_node.is_reroute:
            # RerouteNode - use single pins
            output_pin_index = 0 if output_pin == output_node.output_pin else -1
        else:
            # Regular Node - use pin lists
            output_pin_index = self._get_pin_index(output_node.output_pins, output_pin)
        
        if hasattr(input_node, 'is_reroute') and input_node.is_reroute:
            # RerouteNode - use single pins
            input_pin_index = 0 if input_pin == input_node.input_pin else -1
        else:
            # Regular Node - use pin lists
            input_pin_index = self._get_pin_index(input_node.input_pins, input_pin)
        
        self.connection_data = {
            'output_node_id': output_node.uuid,
            'output_pin_index': output_pin_index,
            'input_node_id': input_node.uuid,
            'input_pin_index': input_pin_index
        }
    
    def execute(self) -> bool:
        """Create the connection and add to graph."""
        try:
            # Import here to avoid circular imports
            from core.connection import Connection
            
            # Validate connection is still possible
            if not self._validate_connection():
                return False
            
            # Remove any existing connection to the input pin (end_pin)
            existing_connection = None
            for conn in self.node_graph.connections:
                if hasattr(conn, 'end_pin') and conn.end_pin == self.input_pin:
                    existing_connection = conn
                    break
            
            if existing_connection:
                self.node_graph.removeItem(existing_connection)
                self.node_graph.connections.remove(existing_connection)
            
            # Create new connection
            self.created_connection = Connection(self.output_pin, self.input_pin)
            
            # Add to graph
            self.node_graph.addItem(self.created_connection)
            self.node_graph.connections.append(self.created_connection)
            
            # Note: Pin connections are already added in Connection constructor
            
            self._mark_executed()
            return True
            
        except Exception as e:
            print(f"Failed to create connection: {e}")
            return False
    
    def undo(self) -> bool:
        """Remove the created connection."""
        if not self.created_connection or self.created_connection not in self.node_graph.connections:
            return False
        
        try:
            # Remove connection references from pins using proper methods
            if hasattr(self.output_pin, 'remove_connection'):
                self.output_pin.remove_connection(self.created_connection)
            if hasattr(self.input_pin, 'remove_connection'):
                self.input_pin.remove_connection(self.created_connection)
            
            # Remove from graph
            self.node_graph.removeItem(self.created_connection)
            self.node_graph.connections.remove(self.created_connection)
            
            self._mark_undone()
            return True
            
        except Exception as e:
            print(f"Failed to undo connection creation: {e}")
            return False
    
    def _validate_connection(self) -> bool:
        """Validate that the connection can still be made."""
        # Check that pins still exist and are valid
        if not hasattr(self.output_pin, 'node') or not hasattr(self.input_pin, 'node'):
            return False
        
        # Check that nodes still exist in graph
        if (self.output_pin.node not in self.node_graph.nodes or 
            self.input_pin.node not in self.node_graph.nodes):
            return False
        
        # Check pin compatibility (basic type checking)
        if hasattr(self.output_pin, 'pin_type') and hasattr(self.input_pin, 'pin_type'):
            # Allow 'any' or 'Any' type to connect to anything
            output_type = self.output_pin.pin_type.lower()
            input_type = self.input_pin.pin_type.lower()
            if (output_type != input_type and 
                output_type != 'any' and 
                input_type != 'any'):
                return False
        
        return True
    
    def _get_pin_index(self, pin_list, pin):
        """Safely get pin index."""
        try:
            return pin_list.index(pin)
        except (ValueError, AttributeError):
            return 0
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage of this command."""
        return 512  # Base connection memory usage


class DeleteConnectionCommand(CommandBase):
    """Command for deleting connections with complete state preservation."""
    
    def __init__(self, node_graph, connection):
        """
        Initialize delete connection command.
        
        Args:
            node_graph: The NodeGraph instance
            connection: Connection to delete
        """
        # Use start_pin and end_pin (correct attributes for Connection class)
        start_name = getattr(connection.start_pin, 'name', 'output')
        end_name = getattr(connection.end_pin, 'name', 'input')
        super().__init__(f"Disconnect {connection.start_pin.node.title}.{start_name} from {connection.end_pin.node.title}.{end_name}")
        
        self.node_graph = node_graph
        self.connection = connection
        
        # Preserve connection data for restoration (handle different node types)
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
        
        self.connection_data = {
            'output_node_id': start_node.uuid,
            'output_pin_index': output_pin_index,
            'input_node_id': end_node.uuid,
            'input_pin_index': input_pin_index,
            'color': connection.color if hasattr(connection, 'color') else None
        }
    
    def execute(self) -> bool:
        """Delete the connection."""
        try:
            # Check if connection is still in the scene and connections list
            if self.connection not in self.node_graph.connections:
                # Connection was already removed (likely by node deletion)
                # This is not an error - just mark as executed and continue
                self._mark_executed()
                return True
            
            # Remove connection references from pins using proper methods
            if hasattr(self.connection.start_pin, 'remove_connection'):
                self.connection.start_pin.remove_connection(self.connection)
            if hasattr(self.connection.end_pin, 'remove_connection'):
                self.connection.end_pin.remove_connection(self.connection)
            
            # Remove from connections list first
            self.node_graph.connections.remove(self.connection)
            
            # Remove from scene if it's still there
            if self.connection.scene() == self.node_graph:
                self.node_graph.removeItem(self.connection)
            
            self._mark_executed()
            return True
            
        except Exception as e:
            print(f"Error: Failed to delete connection: {e}")
            return False
    
    def undo(self) -> bool:
        """Restore the deleted connection."""
        try:
            # Find nodes by ID
            output_node = self._find_node_by_id(self.connection_data['output_node_id'])
            input_node = self._find_node_by_id(self.connection_data['input_node_id'])
            
            if not output_node or not input_node:
                return False
            
            # Get pins by index based on node type
            try:
                # Handle output pin
                if hasattr(output_node, 'is_reroute') and output_node.is_reroute:
                    # RerouteNode - use single output pin
                    output_pin = output_node.output_pin
                else:
                    # Regular Node - use pin list
                    output_pin = output_node.output_pins[self.connection_data['output_pin_index']]
                
                # Handle input pin
                if hasattr(input_node, 'is_reroute') and input_node.is_reroute:
                    # RerouteNode - use single input pin
                    input_pin = input_node.input_pin
                else:
                    # Regular Node - use pin list
                    input_pin = input_node.input_pins[self.connection_data['input_pin_index']]
                    
            except (IndexError, AttributeError) as e:
                print(f"Warning: Could not restore connection due to pin access error: {e}")
                return False
            
            # Recreate connection
            from core.connection import Connection
            restored_connection = Connection(output_pin, input_pin)
            
            # Restore color if available
            if self.connection_data['color']:
                restored_connection.color = self.connection_data['color']
            
            # Add back to graph
            self.node_graph.addItem(restored_connection)
            self.node_graph.connections.append(restored_connection)
            
            # Update pin connection references using proper methods
            if hasattr(output_pin, 'add_connection'):
                output_pin.add_connection(restored_connection)
            if hasattr(input_pin, 'add_connection'):
                input_pin.add_connection(restored_connection)
            
            # Update connection reference
            self.connection = restored_connection
            
            self._mark_undone()
            return True
            
        except Exception as e:
            print(f"Failed to undo connection deletion: {e}")
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
        return 512  # Base connection memory usage


class CreateRerouteNodeCommand(CommandBase):
    """Command for creating reroute nodes on connections."""
    
    def __init__(self, node_graph, connection, position):
        """
        Initialize create reroute node command.
        
        Args:
            node_graph: The NodeGraph instance
            connection: Connection to split with reroute node
            position: Position to place reroute node
        """
        super().__init__("Create reroute node")
        self.node_graph = node_graph
        self.original_connection = connection
        self.position = position
        self.reroute_node = None
        self.first_connection = None
        self.second_connection = None
        
        # Store original connection data (handle different node types)
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
        
        self.original_connection_data = {
            'output_node_id': start_node.uuid,
            'output_pin_index': output_pin_index,
            'input_node_id': end_node.uuid,
            'input_pin_index': input_pin_index
        }
    
    def execute(self) -> bool:
        """Create reroute node and split connection."""
        try:
            # Import here to avoid circular imports
            from core.reroute_node import RerouteNode
            from core.connection import Connection
            
            # Create reroute node
            self.reroute_node = RerouteNode()
            self.reroute_node.setPos(self.position)
            
            # Find the original pins (they should still exist)
            output_node = self._find_node_by_id(self.original_connection_data['output_node_id'])
            input_node = self._find_node_by_id(self.original_connection_data['input_node_id'])
            
            if not output_node or not input_node:
                return False
            
            # Get pins by index based on node type
            if hasattr(output_node, 'is_reroute') and output_node.is_reroute:
                # RerouteNode - use single output pin
                original_output_pin = output_node.output_pin
            else:
                # Regular Node - use pin list
                original_output_pin = output_node.output_pins[self.original_connection_data['output_pin_index']]
            
            if hasattr(input_node, 'is_reroute') and input_node.is_reroute:
                # RerouteNode - use single input pin
                original_input_pin = input_node.input_pin
            else:
                # Regular Node - use pin list
                original_input_pin = input_node.input_pins[self.original_connection_data['input_pin_index']]
            
            # Find and remove the current connection between these pins (it may not be the original object)
            connection_to_remove = None
            for connection in list(self.node_graph.connections):
                if (connection.start_pin == original_output_pin and 
                    connection.end_pin == original_input_pin):
                    connection_to_remove = connection
                    break
            
            if connection_to_remove:
                # Remove the current connection using proper methods
                if hasattr(original_output_pin, 'remove_connection'):
                    original_output_pin.remove_connection(connection_to_remove)
                if hasattr(original_input_pin, 'remove_connection'):
                    original_input_pin.remove_connection(connection_to_remove)
                
                # Remove from scene and connections list safely
                if connection_to_remove.scene() == self.node_graph:
                    self.node_graph.removeItem(connection_to_remove)
                if connection_to_remove in self.node_graph.connections:
                    self.node_graph.connections.remove(connection_to_remove)
            
            # Add reroute node to graph
            self.node_graph.addItem(self.reroute_node)
            self.node_graph.nodes.append(self.reroute_node)
            
            # Create first connection (original output to reroute input)
            self.first_connection = Connection(original_output_pin, self.reroute_node.input_pin)
            self.node_graph.addItem(self.first_connection)
            self.node_graph.connections.append(self.first_connection)
            if hasattr(original_output_pin, 'add_connection'):
                original_output_pin.add_connection(self.first_connection)
            if hasattr(self.reroute_node.input_pin, 'add_connection'):
                self.reroute_node.input_pin.add_connection(self.first_connection)
            
            # Create second connection (reroute output to original input)
            self.second_connection = Connection(self.reroute_node.output_pin, original_input_pin)
            self.node_graph.addItem(self.second_connection)
            self.node_graph.connections.append(self.second_connection)
            if hasattr(self.reroute_node.output_pin, 'add_connection'):
                self.reroute_node.output_pin.add_connection(self.second_connection)
            if hasattr(original_input_pin, 'add_connection'):
                original_input_pin.add_connection(self.second_connection)
            
            self._mark_executed()
            return True
            
        except Exception as e:
            print(f"Failed to create reroute node: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
    
    def undo(self) -> bool:
        """Remove reroute node and restore original connection."""
        try:
            # Find original pins
            output_node = self._find_node_by_id(self.original_connection_data['output_node_id'])
            input_node = self._find_node_by_id(self.original_connection_data['input_node_id'])
            
            if not output_node or not input_node:
                return False
            
            # Get pins by index based on node type
            if hasattr(output_node, 'is_reroute') and output_node.is_reroute:
                # RerouteNode - use single output pin
                output_pin = output_node.output_pin
            else:
                # Regular Node - use pin list
                output_pin = output_node.output_pins[self.original_connection_data['output_pin_index']]
            
            if hasattr(input_node, 'is_reroute') and input_node.is_reroute:
                # RerouteNode - use single input pin
                input_pin = input_node.input_pin
            else:
                # Regular Node - use pin list
                input_pin = input_node.input_pins[self.original_connection_data['input_pin_index']]
            
            # Find the CURRENT reroute node by UUID (it may have been recreated by DeleteNodeCommand.undo)
            current_reroute_node = None
            if self.reroute_node and hasattr(self.reroute_node, 'uuid'):
                current_reroute_node = self._find_node_by_id(self.reroute_node.uuid)
            
            if not current_reroute_node:
                # Fallback: find any RerouteNode
                for node in self.node_graph.nodes:
                    if hasattr(node, 'is_reroute') and node.is_reroute:
                        current_reroute_node = node
                        break
            
            # Remove connections to/from the reroute node
            if current_reroute_node:
                connections_to_remove = []
                for connection in list(self.node_graph.connections):
                    if (hasattr(connection, 'start_pin') and connection.start_pin.node == current_reroute_node or 
                        hasattr(connection, 'end_pin') and connection.end_pin.node == current_reroute_node):
                        connections_to_remove.append(connection)
                
                for connection in connections_to_remove:
                    self._remove_connection_safely(connection)
                
                # Remove the current reroute node
                if current_reroute_node.scene() == self.node_graph:
                    self.node_graph.removeItem(current_reroute_node)
                
                if current_reroute_node in self.node_graph.nodes:
                    self.node_graph.nodes.remove(current_reroute_node)
            
            # Recreate original connection
            from core.connection import Connection
            restored_connection = Connection(output_pin, input_pin)
            self.node_graph.addItem(restored_connection)
            self.node_graph.connections.append(restored_connection)
            if hasattr(output_pin, 'add_connection'):
                output_pin.add_connection(restored_connection)
            if hasattr(input_pin, 'add_connection'):
                input_pin.add_connection(restored_connection)
            
            self._mark_undone()
            return True
            
        except Exception as e:
            print(f"Failed to undo reroute node creation: {e}")
            return False
    
    def _remove_connection_safely(self, connection):
        """Safely remove a connection and its pin references."""
        try:
            # Remove pin references using proper methods
            if hasattr(connection, 'start_pin') and hasattr(connection.start_pin, 'remove_connection'):
                connection.start_pin.remove_connection(connection)
            if hasattr(connection, 'end_pin') and hasattr(connection.end_pin, 'remove_connection'):
                connection.end_pin.remove_connection(connection)
            
            # Remove from connections list first
            if connection in self.node_graph.connections:
                self.node_graph.connections.remove(connection)
            
            # Remove from scene if it's still there
            if connection.scene() == self.node_graph:
                self.node_graph.removeItem(connection)
        except Exception:
            pass  # Ignore errors during cleanup
    
    def _find_node_by_id(self, node_id: str):
        """Find node in graph by UUID."""
        for node in self.node_graph.nodes:
            if hasattr(node, 'uuid') and node.uuid == node_id:
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
        return 1024  # Reroute node + two connections
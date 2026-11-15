"""
Node property change commands: property and code modifications.

Handles undo/redo for changes to node properties like code, size, colors, etc.
"""

from typing import Any


from pyflowgraph.commands.command_base import CommandBase
import logging

logger = logging.getLogger(__name__)


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
            logger.error(f"Failed to change property: {e}")
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
            logger.error(f"Failed to undo property change: {e}")
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
            # A code change that removes a pin also removes its connections; undo makes
            # them again from this list.
            self.old_connections = self._connections_by_name()
            self.node.set_code(self.new_code)
            self._mark_executed()
            return True
        except Exception as e:
            logger.error(f"Failed to change code: {e}")
            return False
    
    def undo(self) -> bool:
        """Revert the code change."""
        try:
            self.node.set_code(self.old_code)
            self._restore_connections()
            self._mark_undone()
            return True
        except Exception as e:
            logger.error(f"Failed to undo code change: {e}")
            return False

    def _connections_by_name(self):
        """The connections of the node, as (start node, pin name, end node, pin name)."""
        connections = getattr(self.node_graph, "connections", None)
        if not isinstance(connections, list):
            return []
        return [(c.start_pin.node, c.start_pin.name, c.end_pin.node, c.end_pin.name)
                for c in connections
                if self.node in (c.start_pin.node, c.end_pin.node)]

    def _restore_connections(self):
        nodes = getattr(self.node_graph, "nodes", [])
        for start_node, start_name, end_node, end_name in getattr(self, "old_connections", []):
            if start_node not in nodes or end_node not in nodes:
                continue
            start_pin = start_node.get_pin_by_name_and_direction(start_name, "output")
            end_pin = end_node.get_pin_by_name_and_direction(end_name, "input")
            if start_pin is None or end_pin is None:
                continue
            if any(c.start_pin is start_pin for c in end_pin.connections):
                continue
            if not start_pin.can_connect_to(end_pin):
                continue
            self.node_graph.create_connection(start_pin, end_pin, use_command=False)
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage for code changes."""
        base_size = 512
        old_code_size = len(self.old_code) * 2
        new_code_size = len(self.new_code) * 2
        return base_size + old_code_size + new_code_size


class GuiCodeChangeCommand(CommandBase):
    """Command for changes to the GUI Definition and GUI State Handler code of a node.

    The widget values are kept across the change and across undo.
    """

    def __init__(self, node_graph, node, old_gui_code: str, new_gui_code: str,
                 old_logic_code: str, new_logic_code: str):
        super().__init__(f"Change GUI code in '{node.title}'")
        self.node_graph = node_graph
        self.node = node
        self.old_gui_code = old_gui_code
        self.new_gui_code = new_gui_code
        self.old_logic_code = old_logic_code
        self.new_logic_code = new_logic_code

    def _apply(self, gui_code, logic_code):
        state = self.node.get_gui_values()
        self.node.gui_get_values_code = logic_code
        self.node.gui_code = gui_code
        self.node.rebuild_gui(state)

    def execute(self) -> bool:
        try:
            self._apply(self.new_gui_code, self.new_logic_code)
            self._mark_executed()
            return True
        except Exception as e:
            logger.error(f"Failed to change GUI code: {e}")
            return False

    def undo(self) -> bool:
        try:
            self._apply(self.old_gui_code, self.old_logic_code)
            self._mark_undone()
            return True
        except Exception as e:
            logger.error(f"Failed to undo GUI code change: {e}")
            return False

    def get_memory_usage(self) -> int:
        texts = (self.old_gui_code, self.new_gui_code, self.old_logic_code, self.new_logic_code)
        return 512 + sum(len(t or "") * 2 for t in texts)

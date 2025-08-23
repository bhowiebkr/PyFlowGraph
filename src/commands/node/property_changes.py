"""
Node property change commands: property and code modifications.

Handles undo/redo for changes to node properties like code, size, colors, etc.
"""

import sys
import os
from typing import Any

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from commands.command_base import CommandBase


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
            self.node.set_code(self.new_code)
            self._mark_executed()
            return True
        except Exception as e:
            print(f"Failed to change code: {e}")
            return False
    
    def undo(self) -> bool:
        """Revert the code change."""
        try:
            self.node.set_code(self.old_code)
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
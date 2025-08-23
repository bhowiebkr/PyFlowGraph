"""
Command for deleting groups with full state preservation and undo support.

Handles the deletion and restoration of group objects including their visual state,
member relationships, and scene integration.
"""

import sys
import os
from typing import Dict, Any, List

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .command_base import CommandBase


class DeleteGroupCommand(CommandBase):
    """Command for deleting groups with complete state preservation."""
    
    def __init__(self, node_graph, group):
        """
        Initialize delete group command.
        
        Args:
            node_graph: The NodeGraph instance
            group: Group to delete
        """
        super().__init__(f"Delete group '{group.name}'")
        self.node_graph = node_graph
        self.group = group
        self.group_state = None
        self.group_index = None
    
    def execute(self) -> bool:
        """Delete group after preserving complete state."""
        try:
            # Find group in the graph's groups list
            found_in_list = False
            for i, group in enumerate(getattr(self.node_graph, 'groups', [])):
                if group is self.group:  # Same object reference
                    found_in_list = True
                    self.group_index = i
                    break
                elif hasattr(group, 'uuid') and hasattr(self.group, 'uuid') and group.uuid == self.group.uuid:
                    # Use the group that's actually in the list (UUID synchronization fix)
                    self.group = group
                    found_in_list = True
                    self.group_index = i
                    break
            
            if not found_in_list:
                print(f"Warning: Group '{getattr(self.group, 'name', 'Unknown')}' not found in graph groups list")
                # Still try to remove from scene if it exists there
            
            # Preserve complete group state for restoration
            self.group_state = {
                'uuid': self.group.uuid,
                'name': self.group.name,
                'description': getattr(self.group, 'description', ''),
                'member_node_uuids': self.group.member_node_uuids.copy(),
                'position': self.group.pos(),
                'width': self.group.width,
                'height': self.group.height,
                'padding': getattr(self.group, 'padding', 20.0),
                'creation_timestamp': getattr(self.group, 'creation_timestamp', ''),
                'is_expanded': getattr(self.group, 'is_expanded', True),
                # Preserve colors
                'color_background': getattr(self.group, 'color_background', None),
                'color_border': getattr(self.group, 'color_border', None),
                'color_title_bg': getattr(self.group, 'color_title_bg', None),
                'color_title_text': getattr(self.group, 'color_title_text', None),
                'color_selection': getattr(self.group, 'color_selection', None)
            }
            
            # Remove from groups list if it exists
            if hasattr(self.node_graph, 'groups') and self.group in self.node_graph.groups:
                self.node_graph.groups.remove(self.group)
            
            # Remove from scene if it's still there
            if self.group.scene() == self.node_graph:
                self.node_graph.removeItem(self.group)
            
            self._mark_executed()
            return True
            
        except Exception as e:
            print(f"Error: Failed to delete group: {e}")
            return False
    
    def undo(self) -> bool:
        """Restore group with complete state."""
        if not self.group_state:
            print(f"Error: No group state to restore")
            return False
        
        try:
            # Restore all properties directly to the existing group object
            self.group.uuid = self.group_state['uuid']
            self.group.name = self.group_state['name']
            self.group.description = self.group_state['description']
            self.group.member_node_uuids = self.group_state['member_node_uuids'].copy()
            self.group.setPos(self.group_state['position'])
            self.group.width = self.group_state['width']
            self.group.height = self.group_state['height']
            self.group.padding = self.group_state['padding']
            self.group.creation_timestamp = self.group_state['creation_timestamp']
            self.group.is_expanded = self.group_state['is_expanded']
            
            # Set the rect geometry
            self.group.setRect(0, 0, self.group.width, self.group.height)
            
            # Restore colors
            if self.group_state['color_background']:
                self.group.color_background = self.group_state['color_background']
                from PySide6.QtGui import QBrush
                self.group.brush_background = QBrush(self.group.color_background)
            
            if self.group_state['color_border']:
                self.group.color_border = self.group_state['color_border']
                from PySide6.QtGui import QPen
                self.group.pen_border = QPen(self.group.color_border, 2.0)
            
            if self.group_state['color_title_bg']:
                self.group.color_title_bg = self.group_state['color_title_bg']
                from PySide6.QtGui import QBrush
                self.group.brush_title = QBrush(self.group.color_title_bg)
            
            if self.group_state['color_title_text']:
                self.group.color_title_text = self.group_state['color_title_text']
            
            if self.group_state['color_selection']:
                self.group.color_selection = self.group_state['color_selection']
                from PySide6.QtGui import QPen
                self.group.pen_selected = QPen(self.group.color_selection, 3.0)
            
            # Add back to scene
            self.node_graph.addItem(self.group)
            
            # Add back to groups list at original position
            if not hasattr(self.node_graph, 'groups'):
                self.node_graph.groups = []
            
            if self.group_index is not None and self.group_index <= len(self.node_graph.groups):
                self.node_graph.groups.insert(self.group_index, self.group)
            else:
                self.node_graph.groups.append(self.group)
            
            # Update group visual representation
            self.group.update()
            
            self._mark_undone()
            return True
            
        except Exception as e:
            print(f"Error: Failed to undo group deletion: {e}")
            return False
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage of this command."""
        if not self.group_state:
            return 512
        
        base_size = 1024
        name_size = len(self.group_state.get('name', '')) * 2
        description_size = len(self.group_state.get('description', '')) * 2
        members_size = len(self.group_state.get('member_node_uuids', [])) * 40  # UUID strings
        
        return base_size + name_size + description_size + members_size
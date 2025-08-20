# resize_group_command.py
# Command for resizing groups with full undo/redo support and membership tracking.

import sys
import os
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QRectF, QPointF

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from commands.command_base import CommandBase


class ResizeGroupCommand(CommandBase):
    """Command for resizing groups with full state preservation and undo/redo support."""
    
    def __init__(self, node_graph, group, old_bounds: QRectF, new_bounds: QRectF, 
                 old_members: List[str], new_members: List[str]):
        """
        Initialize resize group command.
        
        Args:
            node_graph: The NodeGraph instance
            group: The Group instance being resized
            old_bounds: Original group bounds (x, y, width, height)
            new_bounds: New group bounds after resize
            old_members: List of member node UUIDs before resize
            new_members: List of member node UUIDs after resize
        """
        super().__init__(f"Resize group '{group.name}'")
        self.node_graph = node_graph
        self.group_uuid = group.uuid
        self.group = group
        
        # Store bounds information
        self.old_bounds = QRectF(old_bounds)
        self.new_bounds = QRectF(new_bounds)
        
        # Store membership changes
        self.old_members = old_members.copy()
        self.new_members = new_members.copy()
        
        # Track which members were added/removed
        self.added_members = [uuid for uuid in new_members if uuid not in old_members]
        self.removed_members = [uuid for uuid in old_members if uuid not in new_members]
    
    def execute(self) -> bool:
        """Apply the resize operation."""
        try:
            if not self.group:
                return False
            
            # Apply new bounds
            self.group.setPos(self.new_bounds.x(), self.new_bounds.y())
            self.group.width = self.new_bounds.width()
            self.group.height = self.new_bounds.height()
            self.group.setRect(0, 0, self.group.width, self.group.height)
            
            # Apply new membership
            self.group.member_node_uuids = self.new_members.copy()
            
            # Update the scene
            if hasattr(self.node_graph, 'update'):
                self.node_graph.update()
            
            return True
            
        except Exception as e:
            print(f"Failed to execute resize group command: {e}")
            return False
    
    def undo(self) -> bool:
        """Undo the resize operation."""
        try:
            if not self.group:
                return False
            
            # Restore original bounds
            self.group.setPos(self.old_bounds.x(), self.old_bounds.y())
            self.group.width = self.old_bounds.width()
            self.group.height = self.old_bounds.height()
            self.group.setRect(0, 0, self.group.width, self.group.height)
            
            # Restore original membership
            self.group.member_node_uuids = self.old_members.copy()
            
            # Update the scene
            if hasattr(self.node_graph, 'update'):
                self.node_graph.update()
            
            return True
            
        except Exception as e:
            print(f"Failed to undo resize group command: {e}")
            return False
    
    def is_valid(self) -> bool:
        """Check if command is valid for execution."""
        return (self.group is not None and 
                self.old_bounds.isValid() and 
                self.new_bounds.isValid())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the resize operation for debugging."""
        return {
            "group_name": self.group.name if self.group else "Unknown",
            "group_uuid": self.group_uuid,
            "old_bounds": {
                "x": self.old_bounds.x(), "y": self.old_bounds.y(),
                "width": self.old_bounds.width(), "height": self.old_bounds.height()
            },
            "new_bounds": {
                "x": self.new_bounds.x(), "y": self.new_bounds.y(),
                "width": self.new_bounds.width(), "height": self.new_bounds.height()
            },
            "members_added": len(self.added_members),
            "members_removed": len(self.removed_members),
            "added_member_uuids": self.added_members,
            "removed_member_uuids": self.removed_members
        }
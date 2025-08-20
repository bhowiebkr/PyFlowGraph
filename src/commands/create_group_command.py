# create_group_command.py
# Command for creating groups with full undo/redo support and state preservation.

import sys
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from PySide6.QtCore import QPointF

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from commands.command_base import CommandBase


class CreateGroupCommand(CommandBase):
    """Command for creating groups with full state preservation and undo/redo support."""
    
    def __init__(self, node_graph, group_properties: Dict[str, Any]):
        """
        Initialize create group command.
        
        Args:
            node_graph: The NodeGraph instance
            group_properties: Dictionary containing group configuration:
                - name: Group name
                - description: Group description
                - member_node_uuids: List of member node UUIDs
                - auto_size: Whether to auto-size the group
                - padding: Padding around member nodes
        """
        super().__init__(f"Create group '{group_properties.get('name', 'Group')}'")
        self.node_graph = node_graph
        self.group_properties = group_properties.copy()
        self.created_group = None
        self.group_uuid = str(uuid.uuid4())
        
        # Store creation timestamp
        self.group_properties["creation_timestamp"] = datetime.now().isoformat()
    
    def execute(self) -> bool:
        """Create the group and add to graph."""
        try:
            # Import here to avoid circular imports
            from core.group import Group
            
            # Validate that all member nodes exist
            member_nodes = self._get_member_nodes()
            if len(member_nodes) != len(self.group_properties["member_node_uuids"]):
                print(f"Warning: Some member nodes not found. Expected {len(self.group_properties['member_node_uuids'])}, found {len(member_nodes)}")
                return False
            
            # Create the group
            self.created_group = Group(
                name=self.group_properties["name"],
                member_node_uuids=self.group_properties["member_node_uuids"]
            )
            
            # Set properties
            self.created_group.uuid = self.group_uuid
            self.created_group.description = self.group_properties.get("description", "")
            self.created_group.creation_timestamp = self.group_properties["creation_timestamp"]
            self.created_group.padding = self.group_properties.get("padding", 20.0)
            
            # Auto-size if requested
            if self.group_properties.get("auto_size", True):
                self.created_group.calculate_bounds_from_members(self.node_graph)
            
            # Add to graph
            self.node_graph.addItem(self.created_group)
            
            # Store reference in node graph (groups list will be added to NodeGraph)
            if not hasattr(self.node_graph, 'groups'):
                self.node_graph.groups = []
            self.node_graph.groups.append(self.created_group)
            
            print(f"Created group '{self.created_group.name}' with {len(self.created_group.member_node_uuids)} members")
            self._mark_executed()
            return True
            
        except Exception as e:
            print(f"Failed to create group: {e}")
            return False
    
    def undo(self) -> bool:
        """Remove the created group."""
        if not self.created_group:
            return False
        
        try:
            # Remove from groups list if it exists
            if hasattr(self.node_graph, 'groups') and self.created_group in self.node_graph.groups:
                self.node_graph.groups.remove(self.created_group)
            
            # Remove from scene if it's still there
            if self.created_group.scene() == self.node_graph:
                self.node_graph.removeItem(self.created_group)
            
            print(f"Undid creation of group '{self.created_group.name}'")
            self._mark_undone()
            return True
            
        except Exception as e:
            print(f"Failed to undo group creation: {e}")
            return False
    
    def redo(self) -> bool:
        """Re-execute the group creation."""
        # For redo, we can re-execute if the group still exists
        if self.created_group:
            try:
                # Add back to graph
                self.node_graph.addItem(self.created_group)
                
                # Add back to groups list
                if not hasattr(self.node_graph, 'groups'):
                    self.node_graph.groups = []
                if self.created_group not in self.node_graph.groups:
                    self.node_graph.groups.append(self.created_group)
                
                print(f"Redid creation of group '{self.created_group.name}'")
                self._mark_executed()
                return True
                
            except Exception as e:
                print(f"Failed to redo group creation: {e}")
                return False
        else:
            # If group was destroyed, re-execute from scratch
            return self.execute()
    
    def _get_member_nodes(self) -> List:
        """Get the actual node objects for the member UUIDs."""
        member_nodes = []
        member_uuids = set(self.group_properties["member_node_uuids"])
        
        for node in self.node_graph.nodes:
            if hasattr(node, 'uuid') and node.uuid in member_uuids:
                member_nodes.append(node)
        
        return member_nodes
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage of this command."""
        base_size = 1024  # Base command overhead
        name_size = len(self.group_properties.get("name", "")) * 2
        description_size = len(self.group_properties.get("description", "")) * 2
        members_size = len(self.group_properties.get("member_node_uuids", [])) * 40  # UUID strings
        return base_size + name_size + description_size + members_size
    
    def can_merge_with(self, other_command) -> bool:
        """Groups creation commands cannot be merged."""
        return False
    
    def get_affected_items(self) -> List:
        """Return list of items affected by this command."""
        affected = []
        
        # Include the created group
        if self.created_group:
            affected.append(self.created_group)
        
        # Include member nodes
        member_nodes = self._get_member_nodes()
        affected.extend(member_nodes)
        
        return affected
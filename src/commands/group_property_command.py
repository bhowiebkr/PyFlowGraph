"""
Group Property Change Command

Provides undoable commands for changing group properties including name, 
description, colors, and size. Supports batch property changes in a single command.
"""

import sys
import os
from typing import Dict, Any, Optional
from PySide6.QtGui import QColor

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .command_base import CommandBase


class GroupPropertyChangeCommand(CommandBase):
    """Command for changing group properties with full undo/redo support."""
    
    def __init__(self, node_graph, group, property_changes: Dict[str, Any]):
        """
        Initialize group property change command.
        
        Args:
            node_graph: The NodeGraph instance
            group: Group whose properties are changing
            property_changes: Dictionary of property names to new values
        """
        # Create description based on what's being changed
        if len(property_changes) == 1:
            prop_name = list(property_changes.keys())[0]
            super().__init__(f"Change {prop_name} of group '{group.name}'")
        else:
            super().__init__(f"Change properties of group '{group.name}'")
        
        self.node_graph = node_graph
        self.group = group
        self.property_changes = property_changes.copy()
        self.old_values = {}
        
        # Store original values for undo
        for prop_name in property_changes.keys():
            if hasattr(group, prop_name):
                old_value = getattr(group, prop_name)
                # Handle QColor objects specially
                if isinstance(old_value, QColor):
                    self.old_values[prop_name] = QColor(old_value)  # Create copy
                else:
                    self.old_values[prop_name] = old_value
    
    def execute(self) -> bool:
        """Apply the property changes."""
        try:
            for prop_name, new_value in self.property_changes.items():
                if hasattr(self.group, prop_name):
                    # Handle QColor objects
                    if isinstance(new_value, QColor):
                        setattr(self.group, prop_name, QColor(new_value))
                    else:
                        setattr(self.group, prop_name, new_value)
                    
                    # Special handling for certain properties
                    self._handle_property_side_effects(prop_name, new_value)
            
            # Update visual representation
            self._update_group_visuals()
            
            self._mark_executed()
            return True
        except Exception as e:
            print(f"Failed to change group properties: {e}")
            return False
    
    def undo(self) -> bool:
        """Revert the property changes."""
        try:
            for prop_name, old_value in self.old_values.items():
                if hasattr(self.group, prop_name):
                    # Handle QColor objects
                    if isinstance(old_value, QColor):
                        setattr(self.group, prop_name, QColor(old_value))
                    else:
                        setattr(self.group, prop_name, old_value)
                    
                    # Special handling for certain properties
                    self._handle_property_side_effects(prop_name, old_value)
            
            # Update visual representation
            self._update_group_visuals()
            
            self._mark_undone()
            return True
        except Exception as e:
            print(f"Failed to undo group property changes: {e}")
            return False

    
    def redo(self) -> bool:
        """Re-apply the property changes (same as execute)."""
        return self.execute()
    
    def _handle_property_side_effects(self, prop_name: str, value: Any):
        """Handle side effects of changing specific properties."""
        if prop_name in ['color_background', 'color_border', 'color_title_bg', 
                        'color_title_text', 'color_selection']:
            # Update related brushes and pens when colors change
            self._update_color_related_objects(prop_name, value)
        elif prop_name in ['width', 'height']:
            # Ensure size doesn't go below minimums
            if prop_name == 'width':
                self.group.width = max(value, self.group.min_width)
            elif prop_name == 'height':
                self.group.height = max(value, self.group.min_height)
            
            # Update group rectangle
            self.group.setRect(0, 0, self.group.width, self.group.height)
        elif prop_name == 'padding':
            # Padding changes might affect auto-sizing
            if hasattr(self.group, 'calculate_bounds_from_members'):
                self.group.calculate_bounds_from_members(self.node_graph)
    
    def _update_color_related_objects(self, prop_name: str, color: QColor):
        """Update brushes and pens when colors change."""
        from PySide6.QtGui import QPen, QBrush
        
        if prop_name == 'color_background':
            self.group.brush_background = QBrush(color)
        elif prop_name == 'color_border':
            self.group.pen_border = QPen(color, 2.0)
        elif prop_name == 'color_title_bg':
            self.group.brush_title = QBrush(color)
        elif prop_name == 'color_selection':
            self.group.pen_selected = QPen(color, 3.0)
    
    def _update_group_visuals(self):
        """Update group visual representation after property changes."""
        # Prepare for geometry changes if size changed
        if any(prop in self.property_changes for prop in ['width', 'height', 'padding']):
            self.group.prepareGeometryChange()
        
        # Force visual update
        self.group.update()
        
        # Update scene area if size changed
        if any(prop in self.property_changes for prop in ['width', 'height']):
            if self.group.scene():
                # Update the scene area where the group might have changed size
                expanded_rect = self.group.boundingRect()
                scene_rect = self.group.mapRectToScene(expanded_rect)
                self.group.scene().update(scene_rect)
    
    def can_merge_with(self, other_command) -> bool:
        """
        Check if this command can be merged with another group property change.
        
        Allow merging if:
        - Same group
        - Same command type
        - Recent enough (within 2 seconds)
        """
        return (isinstance(other_command, GroupPropertyChangeCommand) and
                other_command.group == self.group and
                abs(other_command.timestamp - self.timestamp) < 2.0)
    
    def merge_with(self, other_command) -> Optional['CommandBase']:
        """Merge with another group property change command."""
        if not self.can_merge_with(other_command):
            return None
        
        # Create merged property changes
        merged_changes = self.property_changes.copy()
        merged_changes.update(other_command.property_changes)
        
        # Create new command with merged changes
        merged_command = GroupPropertyChangeCommand(
            self.node_graph,
            self.group,
            merged_changes
        )
        
        # Use the original old values from the first command
        merged_command.old_values = self.old_values.copy()
        
        # For properties that weren't in the original command, 
        # use old values from the other command
        for prop_name, new_value in other_command.property_changes.items():
            if prop_name not in self.property_changes:
                merged_command.old_values[prop_name] = other_command.old_values.get(prop_name)
        
        return merged_command
    
    def get_memory_usage(self) -> int:
        """Estimate memory usage of this command."""
        base_size = 512
        
        # Estimate size based on number of properties and their types
        for prop_name, value in self.property_changes.items():
            if isinstance(value, str):
                base_size += len(value) * 2  # Unicode characters
            elif isinstance(value, QColor):
                base_size += 16  # RGBA values
            else:
                base_size += 8  # Basic numeric types
        
        # Same estimation for old values
        for prop_name, value in self.old_values.items():
            if isinstance(value, str):
                base_size += len(value) * 2
            elif isinstance(value, QColor):
                base_size += 16
            else:
                base_size += 8
        
        return base_size
    
    def get_affected_items(self):
        """Return list of items affected by this command."""
        return [self.group]
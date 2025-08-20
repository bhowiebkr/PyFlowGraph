# group.py
# Group class for managing collections of nodes with visual representation and persistence.

import sys
import os
import uuid
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class Group(QGraphicsRectItem):
    """
    Represents a visual grouping of nodes that can be organized, collapsed, and persisted.
    Inherits from QGraphicsRectItem for visual representation in the scene.
    """

    def __init__(self, name: str = "Group", member_node_uuids: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        
        # Unique identification
        self.uuid = str(uuid.uuid4())
        
        # Group metadata
        self.name = name
        self.description = ""
        self.creation_timestamp = ""
        
        # Member tracking - store UUIDs instead of direct references to avoid circular dependencies
        self.member_node_uuids = member_node_uuids or []
        
        # Visual state
        self.is_expanded = True
        self.is_selected = False
        
        # Dimensions and positioning
        self.width = 200.0
        self.height = 150.0
        self.padding = 20.0
        
        # Visual styling
        self.color_background = QColor(45, 45, 55, 120)  # Semi-transparent background
        self.color_border = QColor(100, 150, 200, 180)   # Blue border
        self.color_title_bg = QColor(60, 60, 70, 200)    # Title bar background
        self.color_title_text = QColor(220, 220, 220)    # Title text
        self.color_selection = QColor(255, 165, 0, 100)  # Orange selection highlight
        
        # Pens and brushes
        self.pen_border = QPen(self.color_border, 2.0)
        self.pen_selected = QPen(self.color_selection, 3.0)
        self.brush_background = QBrush(self.color_background)
        self.brush_title = QBrush(self.color_title_bg)
        
        # Setup graphics item properties
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setZValue(-1)  # Groups should be behind nodes
        
    def add_member_node(self, node_uuid: str):
        """Add a node UUID to the group membership"""
        if node_uuid not in self.member_node_uuids:
            self.member_node_uuids.append(node_uuid)
    
    def remove_member_node(self, node_uuid: str):
        """Remove a node UUID from the group membership"""
        if node_uuid in self.member_node_uuids:
            self.member_node_uuids.remove(node_uuid)
    
    def get_member_count(self) -> int:
        """Get the number of member nodes"""
        return len(self.member_node_uuids)
    
    def is_member(self, node_uuid: str) -> bool:
        """Check if a node UUID is a member of this group"""
        return node_uuid in self.member_node_uuids
    
    def calculate_bounds_from_members(self, scene):
        """Calculate and update group bounds based on member node positions"""
        if not self.member_node_uuids:
            return
        
        # Find all member nodes in the scene
        member_nodes = []
        for item in scene.items():
            if hasattr(item, 'uuid') and item.uuid in self.member_node_uuids:
                member_nodes.append(item)
        
        if not member_nodes:
            return
        
        # Calculate bounding rectangle of all member nodes
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for node in member_nodes:
            node_rect = node.boundingRect()
            node_pos = node.pos()
            
            node_min_x = node_pos.x() + node_rect.left()
            node_min_y = node_pos.y() + node_rect.top()
            node_max_x = node_pos.x() + node_rect.right()
            node_max_y = node_pos.y() + node_rect.bottom()
            
            min_x = min(min_x, node_min_x)
            min_y = min(min_y, node_min_y)
            max_x = max(max_x, node_max_x)
            max_y = max(max_y, node_max_y)
        
        # Add padding around the group
        self.width = max_x - min_x + (2 * self.padding)
        self.height = max_y - min_y + (2 * self.padding)
        
        # Position the group to encompass all nodes
        self.setPos(min_x - self.padding, min_y - self.padding)
        self.setRect(0, 0, self.width, self.height)
    
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle for this group"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter: QPainter, option, widget=None):
        """Custom paint method for group visualization"""
        # Set up painter
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.setBrush(self.brush_background)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.boundingRect(), 8, 8)
        
        # Draw title bar
        title_height = 30
        title_rect = QRectF(0, 0, self.width, title_height)
        painter.setBrush(self.brush_title)
        painter.drawRoundedRect(title_rect, 8, 8)
        
        # Draw border
        border_pen = self.pen_selected if self.isSelected() else self.pen_border
        painter.setBrush(Qt.NoBrush)
        painter.setPen(border_pen)
        painter.drawRoundedRect(self.boundingRect(), 8, 8)
        
        # Draw title text
        painter.setPen(self.color_title_text)
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        
        title_text = f"{self.name} ({len(self.member_node_uuids)} nodes)"
        painter.drawText(title_rect, Qt.AlignCenter, title_text)
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize group data for persistence"""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            "creation_timestamp": self.creation_timestamp,
            "member_node_uuids": self.member_node_uuids,
            "is_expanded": self.is_expanded,
            "position": {"x": self.pos().x(), "y": self.pos().y()},
            "size": {"width": self.width, "height": self.height},
            "padding": self.padding
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Group':
        """Create a Group instance from serialized data"""
        group = cls(
            name=data.get("name", "Group"),
            member_node_uuids=data.get("member_node_uuids", [])
        )
        
        # Restore properties
        group.uuid = data.get("uuid", str(uuid.uuid4()))
        group.description = data.get("description", "")
        group.creation_timestamp = data.get("creation_timestamp", "")
        group.is_expanded = data.get("is_expanded", True)
        
        # Restore position and size
        position = data.get("position", {"x": 0, "y": 0})
        group.setPos(position["x"], position["y"])
        
        size = data.get("size", {"width": 200, "height": 150})
        group.width = size["width"]
        group.height = size["height"]
        group.setRect(0, 0, group.width, group.height)
        
        group.padding = data.get("padding", 20.0)
        
        return group


def validate_group_creation(selected_nodes) -> tuple[bool, str]:
    """
    Validate whether the selected nodes can form a valid group.
    Returns (is_valid, error_message)
    """
    # Must have at least 2 nodes
    if len(selected_nodes) < 2:
        return False, "Groups require at least 2 nodes"
    
    # Check for valid node types - try different import paths
    try:
        from core.node import Node
    except ImportError:
        try:
            from src.core.node import Node
        except ImportError:
            # Fallback - check for Node-like objects
            for node in selected_nodes:
                if not hasattr(node, 'uuid') or not hasattr(node, 'title'):
                    return False, f"Invalid item type: {type(node).__name__}. Only nodes can be grouped."
            # Skip type check if we can't import Node class
            Node = None
    
    if Node is not None:
        for node in selected_nodes:
            if not isinstance(node, Node):
                return False, f"Invalid item type: {type(node).__name__}. Only nodes can be grouped."
    
    # Check for duplicate UUIDs (should not happen, but safety check)
    uuids = [node.uuid for node in selected_nodes]
    if len(uuids) != len(set(uuids)):
        return False, "Duplicate nodes detected in selection"
    
    # Additional validation rules can be added here
    # For example: prevent grouping nodes that are already in other groups
    
    return True, ""


def generate_group_name(selected_nodes) -> str:
    """
    Generate a default group name based on selected nodes.
    """
    if not selected_nodes:
        return "Empty Group"
    
    # Use the first few node titles
    node_titles = [getattr(node, 'title', 'Node') for node in selected_nodes[:3]]
    
    if len(selected_nodes) <= 3:
        return f"Group ({', '.join(node_titles)})"
    else:
        return f"Group ({', '.join(node_titles)}, +{len(selected_nodes) - 3} more)"
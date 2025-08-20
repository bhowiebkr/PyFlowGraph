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
        
        # Groups no longer have interface pins - they keep original connections
        
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
        
        # Resize handle properties
        self.handle_size = 16.0  # Large, simple handles
        self.is_resizing = False
        self.resize_handle = None
        self.resize_start_pos = QPointF()
        self.resize_start_rect = QRectF()
        
        # Handle types enumeration
        self.HANDLE_NONE = 0
        self.HANDLE_NW = 1    # Northwest corner
        self.HANDLE_N = 2     # North edge  
        self.HANDLE_NE = 3    # Northeast corner
        self.HANDLE_E = 4     # East edge
        self.HANDLE_SE = 5    # Southeast corner
        self.HANDLE_S = 6     # South edge
        self.HANDLE_SW = 7    # Southwest corner
        self.HANDLE_W = 8     # West edge
        
        # Minimum size constraints
        self.min_width = 100.0
        self.min_height = 80.0
        
        # Setup graphics item properties
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
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
    
    def get_handle_at_pos(self, pos: QPointF) -> int:
        """Determine which resize handle (if any) is at the given position"""
        if not self.isSelected():
            return self.HANDLE_NONE
            
        rect = QRectF(0, 0, self.width, self.height)
        handle_size = self.handle_size
        
        # Handle rectangles OUTSIDE the group box - matching drawing positions
        handles = {
            self.HANDLE_NW: QRectF(rect.left() - handle_size - handle_size/2, rect.top() - handle_size - handle_size/2, handle_size, handle_size),
            self.HANDLE_N: QRectF(rect.center().x() - handle_size/2, rect.top() - handle_size - handle_size/2, handle_size, handle_size),
            self.HANDLE_NE: QRectF(rect.right() + handle_size - handle_size/2, rect.top() - handle_size - handle_size/2, handle_size, handle_size),
            self.HANDLE_E: QRectF(rect.right() + handle_size - handle_size/2, rect.center().y() - handle_size/2, handle_size, handle_size),
            self.HANDLE_SE: QRectF(rect.right() + handle_size - handle_size/2, rect.bottom() + handle_size - handle_size/2, handle_size, handle_size),
            self.HANDLE_S: QRectF(rect.center().x() - handle_size/2, rect.bottom() + handle_size - handle_size/2, handle_size, handle_size),
            self.HANDLE_SW: QRectF(rect.left() - handle_size - handle_size/2, rect.bottom() + handle_size - handle_size/2, handle_size, handle_size),
            self.HANDLE_W: QRectF(rect.left() - handle_size - handle_size/2, rect.center().y() - handle_size/2, handle_size, handle_size)
        }
        
        # Check which handle contains the position
        for handle_type, handle_rect in handles.items():
            if handle_rect.contains(pos):
                return handle_type
                
        return self.HANDLE_NONE
    
    def get_cursor_for_handle(self, handle_type: int) -> Qt.CursorShape:
        """Get the appropriate cursor shape for the given handle type"""
        cursor_map = {
            self.HANDLE_NW: Qt.SizeFDiagCursor,
            self.HANDLE_N: Qt.SizeVerCursor,
            self.HANDLE_NE: Qt.SizeBDiagCursor,
            self.HANDLE_E: Qt.SizeHorCursor,
            self.HANDLE_SE: Qt.SizeFDiagCursor,
            self.HANDLE_S: Qt.SizeVerCursor,
            self.HANDLE_SW: Qt.SizeBDiagCursor,
            self.HANDLE_W: Qt.SizeHorCursor
        }
        return cursor_map.get(handle_type, Qt.ArrowCursor)
    
    def start_resize(self, handle_type: int, start_pos: QPointF):
        """Start a resize operation"""
        self.is_resizing = True
        self.resize_handle = handle_type
        self.resize_start_pos = start_pos
        self.resize_start_rect = QRectF(self.pos().x(), self.pos().y(), self.width, self.height)
    
    def update_resize(self, current_pos: QPointF):
        """Update group size during resize operation"""
        if not self.is_resizing or self.resize_handle == self.HANDLE_NONE:
            return
            
        delta = current_pos - self.resize_start_pos
        start_rect = self.resize_start_rect
        
        # Calculate new dimensions based on handle type
        new_x = start_rect.x()
        new_y = start_rect.y() 
        new_width = start_rect.width()
        new_height = start_rect.height()
        
        if self.resize_handle in [self.HANDLE_NW, self.HANDLE_N, self.HANDLE_NE]:
            # Top handles: adjust y and height
            new_y = start_rect.y() + delta.y()
            new_height = start_rect.height() - delta.y()
            
        if self.resize_handle in [self.HANDLE_SW, self.HANDLE_S, self.HANDLE_SE]:
            # Bottom handles: adjust height only
            new_height = start_rect.height() + delta.y()
            
        if self.resize_handle in [self.HANDLE_NW, self.HANDLE_W, self.HANDLE_SW]:
            # Left handles: adjust x and width
            new_x = start_rect.x() + delta.x()
            new_width = start_rect.width() - delta.x()
            
        if self.resize_handle in [self.HANDLE_NE, self.HANDLE_E, self.HANDLE_SE]:
            # Right handles: adjust width only
            new_width = start_rect.width() + delta.x()
        
        # Apply minimum size constraints
        if new_width < self.min_width:
            if self.resize_handle in [self.HANDLE_NW, self.HANDLE_W, self.HANDLE_SW]:
                new_x = start_rect.right() - self.min_width
            new_width = self.min_width
            
        if new_height < self.min_height:
            if self.resize_handle in [self.HANDLE_NW, self.HANDLE_N, self.HANDLE_NE]:
                new_y = start_rect.bottom() - self.min_height
            new_height = self.min_height
        
        # Update group position and size
        self.setPos(new_x, new_y)
        self.width = new_width
        self.height = new_height
        self.setRect(0, 0, self.width, self.height)
        
    def finish_resize(self):
        """Complete a resize operation and update membership"""
        if not self.is_resizing:
            return
        
        # Store current state for command
        old_bounds = self.resize_start_rect
        new_bounds = QRectF(self.pos().x(), self.pos().y(), self.width, self.height)
        old_members = self.member_node_uuids.copy()
        
        # Update group membership based on new boundaries
        self._update_membership_after_resize()
        
        # Create and execute resize command if scene has command support
        if self.scene() and hasattr(self.scene(), 'execute_command'):
            try:
                # Import here to avoid circular imports
                from commands.resize_group_command import ResizeGroupCommand
                
                new_members = self.member_node_uuids.copy()
                command = ResizeGroupCommand(
                    self.scene(), self, old_bounds, new_bounds, old_members, new_members
                )
                self.scene().execute_command(command)
            except ImportError:
                # If command import fails, just continue without undo support
                pass
        
        self.is_resizing = False
        self.resize_handle = self.HANDLE_NONE
        
    def _update_membership_after_resize(self):
        """Update group membership after resize - add nodes inside, keep existing members"""
        if not self.scene():
            return
            
        # Get all nodes in the scene
        for item in self.scene().items():
            if (hasattr(item, 'uuid') and 
                type(item).__name__ in ['Node', 'RerouteNode'] and
                item.uuid not in self.member_node_uuids):
                
                # Check if this non-member node is now inside the group
                if self._is_node_within_group_bounds(item):
                    self.add_member_node(item.uuid)
    

    
    def itemChange(self, change, value):
        """Handle item changes, particularly position changes to move member nodes."""
        if change == QGraphicsItem.ItemPositionChange and self.scene() and not self.is_resizing:
            # Only move member nodes during group movement, not during resize
            # Calculate the delta movement
            old_pos = self.pos()
            new_pos = value
            delta = new_pos - old_pos
            
            # Move all member nodes by the same delta
            self._move_member_nodes(delta)
            
        elif change == QGraphicsItem.ItemSelectedChange:
            # Force visual update when selection changes
            self.update()
            
        return super().itemChange(change, value)
    
    def setSelected(self, selected):
        """Override setSelected to trigger visual updates when selection changes"""
        was_selected = self.isSelected()
        super().setSelected(selected)
        
        # Force visual update when selection state changes
        if was_selected != selected:
            # Force geometry change notification since boundingRect changes with selection
            self.prepareGeometryChange()
            
            # Trigger immediate visual update to show/hide handles
            self.update()
            
            # Force scene update in the affected area to clear any drawing artifacts
            if self.scene():
                # Update the expanded bounding rect area to ensure handle artifacts are cleared
                expanded_rect = self.boundingRect()
                scene_rect = self.mapRectToScene(expanded_rect)
                self.scene().update(scene_rect)
            
            # When deselecting, ensure all other groups in scene are also properly updated
            if not selected and self.scene():
                for item in self.scene().items():
                    if type(item).__name__ == 'Group' and item != self:
                        item.update()  # This will trigger a repaint to show/hide handles
    
    def _move_member_nodes(self, delta):
        """Move all member nodes by the given delta, but remove nodes that end up fully outside group boundaries."""
        if not self.scene():
            return
            
        # Find all member nodes and move them
        nodes_to_remove = []
        for item in self.scene().items():
            if (hasattr(item, 'uuid') and 
                item.uuid in self.member_node_uuids and
                type(item).__name__ in ['Node', 'RerouteNode']):
                
                # Move the node
                current_pos = item.pos()
                new_pos = current_pos + delta
                item.setPos(new_pos)
                
                # Check if node is still within group boundaries after movement
                if not self._is_node_within_group_bounds(item):
                    nodes_to_remove.append(item.uuid)
                
                # Update any connections attached to this node
                if hasattr(item, 'pins'):
                    for pin in item.pins:
                        if hasattr(pin, 'update_connections'):
                            pin.update_connections()
        
        # Remove nodes that are fully outside group boundaries
        for node_uuid in nodes_to_remove:
            self.remove_member_node(node_uuid)
    
    def _is_node_within_group_bounds(self, node) -> bool:
        """Check if a node is significantly within the group's content boundaries."""
        if not hasattr(node, 'boundingRect') or not hasattr(node, 'pos'):
            return True  # Default to keeping node if we can't determine bounds
        
        # Use content rectangle for membership detection (not the expanded bounding rect with handles)
        content_rect = self.get_content_rect()
        group_pos = self.pos()
        group_scene_rect = QRectF(
            group_pos.x() + content_rect.left(),
            group_pos.y() + content_rect.top(),
            content_rect.width(),
            content_rect.height()
        )
        
        # Get node center point rather than full bounding rect for more precise detection
        node_pos = node.pos()
        node_rect = node.boundingRect()
        
        # Use the node's center point for membership detection
        # This is more intuitive than using the full bounding rectangle
        node_center = QPointF(
            node_pos.x() + node_rect.width() / 2,
            node_pos.y() + node_rect.height() / 2
        )
        
        # Check if the node's center is within the group's content area
        return group_scene_rect.contains(node_center)

    def check_and_update_node_membership(self, node):
        """Check if a node should be added to or removed from this group based on its position"""
        if not hasattr(node, 'uuid'):
            return
        
        is_node_inside = self._is_node_within_group_bounds(node)
        is_currently_member = self.is_member(node.uuid)
        
        if is_node_inside and not is_currently_member:
            # Node is inside group but not a member - add it
            self.add_member_node(node.uuid)
            print(f"Node '{getattr(node, 'title', 'Unknown')}' added to group '{self.name}'")
            return True
            
        elif not is_node_inside and is_currently_member:
            # Node is outside group but still a member - remove it
            self.remove_member_node(node.uuid)
            print(f"Node '{getattr(node, 'title', 'Unknown')}' removed from group '{self.name}'")
            return True
            
        return False
    
    def _get_member_nodes(self):
        """Get the actual node objects for member UUIDs."""
        member_nodes = []
        if not self.scene():
            return member_nodes
            
        for item in self.scene().items():
            if (hasattr(item, 'uuid') and 
                item.uuid in self.member_node_uuids and
                type(item).__name__ in ['Node', 'RerouteNode']):
                member_nodes.append(item)
                
        return member_nodes

    
    
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
        """Return the bounding rectangle for this group including resize handles"""
        if self.isSelected():
            # Include space for handles positioned outside the group
            margin = self.handle_size + self.handle_size / 2  # Full handle size plus half for centering
            return QRectF(-margin, -margin, self.width + margin * 2, self.height + margin * 2)
        else:
            return QRectF(0, 0, self.width, self.height)
    
    def get_content_rect(self) -> QRectF:
        """Return the content rectangle (excluding handles) for internal calculations"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter: QPainter, option, widget=None):
        """Custom paint method for group visualization"""
        # Set up painter
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw group content in the standard area
        content_rect = QRectF(0, 0, self.width, self.height)
        
        # Draw background
        painter.setBrush(self.brush_background)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(content_rect, 8, 8)
        
        # Draw title bar
        title_height = 30
        title_rect = QRectF(0, 0, self.width, title_height)
        painter.setBrush(self.brush_title)
        painter.drawRoundedRect(title_rect, 8, 8)
        
        # Draw border
        border_pen = self.pen_selected if self.isSelected() else self.pen_border
        painter.setBrush(Qt.NoBrush)
        painter.setPen(border_pen)
        painter.drawRoundedRect(content_rect, 8, 8)
        
        # Draw title text
        painter.setPen(self.color_title_text)
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        
        title_text = f"{self.name} ({len(self.member_node_uuids)} nodes)"
        painter.drawText(title_rect, Qt.AlignCenter, title_text)
        
        # Draw resize handles when selected
        if self.isSelected():
            self._draw_resize_handles(painter)
    
    def _draw_resize_handles(self, painter: QPainter):
        """Draw simple, large resize handles OUTSIDE the group box"""
        rect = QRectF(0, 0, self.width, self.height)
        handle_size = self.handle_size
        
        # Handle positions OUTSIDE the group box
        handles = [
            (rect.left() - handle_size, rect.top() - handle_size),        # NW
            (rect.center().x(), rect.top() - handle_size),                # N
            (rect.right() + handle_size, rect.top() - handle_size),       # NE
            (rect.right() + handle_size, rect.center().y()),              # E
            (rect.right() + handle_size, rect.bottom() + handle_size),    # SE
            (rect.center().x(), rect.bottom() + handle_size),             # S
            (rect.left() - handle_size, rect.bottom() + handle_size),     # SW
            (rect.left() - handle_size, rect.center().y())                # W
        ]
        
        # Draw large, simple white handles with dark border
        painter.setPen(QPen(QColor(0, 0, 0), 2.0))
        painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
        
        for x, y in handles:
            handle_rect = QRectF(x - handle_size/2, y - handle_size/2, handle_size, handle_size)
            painter.drawRect(handle_rect)
    
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
    
    # Use duck typing instead of isinstance checks to avoid import path issues
    # A valid node should have these essential attributes and the right class name
    for i, node in enumerate(selected_nodes):
        node_type_name = type(node).__name__
        
        # Check if it's a Node-like object by class name
        if node_type_name not in ['Node', 'RerouteNode']:
            error_msg = f"Invalid item type: {node_type_name}. Only nodes can be grouped."
            return False, error_msg
        
        # Check for essential Node attributes
        if not hasattr(node, 'uuid'):
            error_msg = f"Invalid item type: {node_type_name}. Only nodes can be grouped."
            return False, error_msg
            
        if not hasattr(node, 'title'):
            error_msg = f"Invalid item type: {node_type_name}. Only nodes can be grouped."
            return False, error_msg
        
        # Additional duck typing checks for Node-like behavior
        if not hasattr(node, 'pins'):
            error_msg = f"Invalid item type: {node_type_name}. Only nodes can be grouped."
            return False, error_msg
    
    # Check for duplicate UUIDs (should not happen, but safety check)
    uuids = [node.uuid for node in selected_nodes]
    if len(uuids) != len(set(uuids)):
        error_msg = "Duplicate nodes detected in selection"
        return False, error_msg
    
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
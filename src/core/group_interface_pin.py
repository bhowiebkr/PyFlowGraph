# group_interface_pin.py
# Specialized pin class for group interface pins with routing and type inference.

import sys
import os
import uuid
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.pin import Pin
from utils.color_utils import generate_color_from_string


class GroupInterfacePin(Pin):
    """
    Specialized pin class for group interface pins.
    Extends the base Pin class with group-specific behavior including
    routing to internal nodes and specialized visual representation.
    """

    def __init__(self, group, name, direction, pin_type_str, pin_category="data", 
                 internal_pin_mappings=None, parent=None):
        """
        Initialize a group interface pin.
        
        Args:
            group: The Group instance this pin belongs to
            name: Pin name
            direction: "input" or "output"
            pin_type_str: Data type string
            pin_category: "data" or "execution"
            internal_pin_mappings: List of internal pin UUIDs this interface connects to
            parent: Qt parent item
        """
        # Initialize with group as the node (interface pins belong to groups)
        super().__init__(group, name, direction, pin_type_str, pin_category, parent)
        
        self.group = group
        self.internal_pin_mappings = internal_pin_mappings or []
        self.is_interface_pin = True
        
        # Interface pin specific properties
        self.auto_generated = True
        self.original_connection_data = {}  # Store original connection info for restoration
        
        # Enhanced visual styling for interface pins
        self.interface_color_modifier = 1.2  # Make interface pins slightly brighter
        self._update_interface_visual_style()
        
    def _update_interface_visual_style(self):
        """Update visual styling to distinguish interface pins from regular pins."""
        # Make interface pins slightly larger and more prominent
        self.radius = 8  # Larger than regular pins (6)
        
        # Enhance color for interface pins
        if self.pin_category == "execution":
            # Execution interface pins are brighter
            self.color = QColor("#F5F5F5") if self.direction == "output" else QColor("#C0C0C0")
        else:
            # Data interface pins use enhanced type-based colors
            base_color = generate_color_from_string(self.pin_type)
            self.color = QColor(
                min(255, int(base_color.red() * self.interface_color_modifier)),
                min(255, int(base_color.green() * self.interface_color_modifier)),
                min(255, int(base_color.blue() * self.interface_color_modifier))
            )
        
        self.brush = QBrush(self.color)
        
        # Enhanced border for interface pins
        self.pen = QPen(QColor("#FFFFFF"))
        self.pen.setWidth(3)  # Thicker border than regular pins
        
        # Update label styling for interface pins
        if hasattr(self, 'label') and self.label:
            self.label.setDefaultTextColor(QColor("#FFFFFF"))
            font = QFont("Arial", 11, QFont.Bold)  # Slightly larger and bold
            self.label.setFont(font)

    def add_internal_pin_mapping(self, internal_pin_uuid: str):
        """
        Add a mapping to an internal node pin.
        
        Args:
            internal_pin_uuid: UUID of the internal pin this interface pin routes to
        """
        if internal_pin_uuid not in self.internal_pin_mappings:
            self.internal_pin_mappings.append(internal_pin_uuid)

    def remove_internal_pin_mapping(self, internal_pin_uuid: str):
        """
        Remove a mapping to an internal node pin.
        
        Args:
            internal_pin_uuid: UUID of the internal pin to remove from routing
        """
        if internal_pin_uuid in self.internal_pin_mappings:
            self.internal_pin_mappings.remove(internal_pin_uuid)

    def get_internal_pins(self, node_graph) -> List[Pin]:
        """
        Get the actual internal pin objects this interface pin routes to.
        
        Args:
            node_graph: The NodeGraph instance to search for pins
            
        Returns:
            List of internal Pin objects
        """
        internal_pins = []
        
        # Search through all nodes for pins matching our mappings
        for node in node_graph.nodes:
            if hasattr(node, 'pins'):
                for pin in node.pins:
                    if hasattr(pin, 'uuid') and pin.uuid in self.internal_pin_mappings:
                        internal_pins.append(pin)
        
        return internal_pins

    def route_data_to_internal_pins(self, data, node_graph):
        """
        Route data from this interface pin to all mapped internal pins.
        
        Args:
            data: The data to route
            node_graph: The NodeGraph instance
        """
        internal_pins = self.get_internal_pins(node_graph)
        
        for internal_pin in internal_pins:
            if hasattr(internal_pin, 'value'):
                internal_pin.value = data

    def route_data_from_internal_pins(self, node_graph):
        """
        Collect data from mapped internal pins for output interface pins.
        
        Args:
            node_graph: The NodeGraph instance
            
        Returns:
            The collected data value
        """
        internal_pins = self.get_internal_pins(node_graph)
        
        if not internal_pins:
            return None
        
        # For output pins, typically get data from the first mapped internal pin
        # More complex routing logic can be added here if needed
        if internal_pins[0].value is not None:
            return internal_pins[0].value
        
        return None

    def update_interface_position(self, group_bounds):
        """
        Update the position of this interface pin on the group boundary.
        
        Args:
            group_bounds: QRectF representing the group's bounding rectangle
        """
        # Position input pins on the left side, output pins on the right side
        if self.direction == "input":
            # Left side of group
            x_pos = group_bounds.left()
            y_pos = group_bounds.top() + (group_bounds.height() * 0.3)  # TODO: Better positioning logic
        else:
            # Right side of group
            x_pos = group_bounds.right()
            y_pos = group_bounds.top() + (group_bounds.height() * 0.3)  # TODO: Better positioning logic
        
        self.setPos(x_pos, y_pos)

    def paint(self, painter: QPainter, option, widget=None):
        """Custom paint method for interface pin visualization."""
        # Call parent paint method for base rendering
        super().paint(painter, option, widget)
        
        # Add interface pin indicator (small diamond overlay)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw small diamond indicator
        diamond_size = 3
        center_x, center_y = 0, 0
        
        # Diamond points
        points = [
            (center_x, center_y - diamond_size),  # Top
            (center_x + diamond_size, center_y),  # Right
            (center_x, center_y + diamond_size),  # Bottom
            (center_x - diamond_size, center_y)   # Left
        ]
        
        # Draw diamond
        painter.setBrush(QBrush(QColor("#FFFF00")))  # Yellow indicator
        painter.setPen(QPen(QColor("#000000"), 1))
        from PySide6.QtGui import QPolygonF
        from PySide6.QtCore import QPointF
        diamond = QPolygonF([QPointF(x, y) for x, y in points])
        painter.drawPolygon(diamond)

    def can_connect_to(self, other_pin):
        """
        Enhanced connection compatibility checking for interface pins.
        Interface pins have additional routing considerations.
        """
        # First check base compatibility
        if not super().can_connect_to(other_pin):
            return False
        
        # Interface pins cannot connect to pins within the same group
        if hasattr(other_pin, 'node') and other_pin.node == self.group:
            return False
        
        # Additional interface-specific connection rules can be added here
        
        return True

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize interface pin data including routing information.
        
        Returns:
            Dict containing serialized interface pin data
        """
        base_data = super().serialize()
        
        # Add interface-specific data
        interface_data = {
            **base_data,
            "is_interface_pin": True,
            "auto_generated": self.auto_generated,
            "internal_pin_mappings": self.internal_pin_mappings.copy(),
            "original_connection_data": self.original_connection_data.copy(),
            "group_uuid": self.group.uuid if hasattr(self.group, 'uuid') else None
        }
        
        return interface_data

    @classmethod
    def deserialize(cls, data: Dict[str, Any], group, parent=None):
        """
        Create a GroupInterfacePin instance from serialized data.
        
        Args:
            data: Serialized pin data
            group: The Group instance this pin belongs to
            parent: Qt parent item
            
        Returns:
            GroupInterfacePin instance
        """
        interface_pin = cls(
            group=group,
            name=data.get("name", "Interface"),
            direction=data.get("direction", "input"),
            pin_type_str=data.get("type", "any"),
            pin_category=data.get("category", "data"),
            internal_pin_mappings=data.get("internal_pin_mappings", []),
            parent=parent
        )
        
        # Restore properties
        interface_pin.uuid = data.get("uuid", str(uuid.uuid4()))
        interface_pin.auto_generated = data.get("auto_generated", True)
        interface_pin.original_connection_data = data.get("original_connection_data", {})
        
        return interface_pin

    def get_routing_info(self) -> Dict[str, Any]:
        """
        Get routing information for this interface pin.
        
        Returns:
            Dict containing routing details
        """
        return {
            "interface_pin_uuid": self.uuid,
            "direction": self.direction,
            "pin_type": self.pin_type,
            "pin_category": self.pin_category,
            "internal_pin_mappings": self.internal_pin_mappings.copy(),
            "mapping_count": len(self.internal_pin_mappings),
            "group_uuid": self.group.uuid if hasattr(self.group, 'uuid') else None
        }

    def update_type_from_mappings(self, node_graph):
        """
        Update the interface pin type based on mapped internal pins.
        Implements type inference from connected internal pins.
        
        Args:
            node_graph: The NodeGraph instance
        """
        internal_pins = self.get_internal_pins(node_graph)
        
        if not internal_pins:
            return
        
        # Collect types from internal pins
        internal_types = {pin.pin_type for pin in internal_pins if hasattr(pin, 'pin_type')}
        
        if len(internal_types) == 1:
            # Single type - use it directly
            new_type = list(internal_types)[0]
        elif len(internal_types) > 1:
            # Multiple types - use 'any' if types are incompatible
            if 'any' in internal_types:
                new_type = 'any'
            else:
                # Check for compatible types - for now, fall back to 'any'
                new_type = 'any'
        else:
            # No types found - keep current type
            return
        
        # Update type if it has changed
        if new_type != self.pin_type:
            self.pin_type = new_type
            self._update_interface_visual_style()
            if hasattr(self, 'label') and self.label:
                self.update_label_pos()
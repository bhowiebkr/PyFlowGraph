# pin.py
# Represents an input or output socket on a node.
# Now uses a dynamic string for its type and generates its color procedurally.

import uuid
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import QRectF, Qt, QSettings
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.color_utils import generate_color_from_string


class Pin(QGraphicsItem):
    """
    A pin represents an input or output on a Node.
    Supports both execution flow control and data transfer.
    """

    def __init__(self, node, name, direction, pin_type_str, pin_category="data", parent=None):
        super().__init__(node)

        self.node = node
        self.name = name
        self.direction = direction  # "input" or "output"
        self.pin_type = pin_type_str  # Data type for data pins, "exec" for execution pins
        self.pin_category = pin_category  # "data" or "execution"
        self.uuid = str(uuid.uuid4())

        self.radius = 6
        self.connections = []
        self.value = None
        self.label_margin = 8
        self.hover_state = False  # Track hover state for visual feedback

        # --- Dynamic Color Generation ---
        if self.pin_category == "execution":
            # Execution pins are white/gray
            self.color = QColor("#E0E0E0") if direction == "output" else QColor("#A0A0A0")
        else:
            # Data pins use type-based colors
            self.color = generate_color_from_string(self.pin_type)
        
        self.brush = QBrush(self.color)
        self.pen = QPen(QColor("#F0F0F0"))
        self.pen.setWidth(2)

        # --- Label ---
        self.label = QGraphicsTextItem(self._get_display_name(), self)
        self.label.setDefaultTextColor(QColor("#FFDDDDDD"))
        self.label.setFont(QFont("Arial", 10))
        self.update_label_pos()

        self.setAcceptHoverEvents(True)

    def _get_display_name(self):
        """Get the display name for the pin label, optionally including type."""
        base_name = self.name.replace("_", " ").title()
        
        # Check settings for type visibility
        settings = QSettings("PyFlowGraph", "NodeEditor")
        show_types = settings.value("show_pin_types", True, type=bool)
        
        if show_types and self.pin_category == "data":
            return f"{base_name} ({self.pin_type})"
        else:
            return base_name

    def update_label_text(self):
        """Update the label text based on current settings."""
        if hasattr(self, 'label') and self.label:
            self.label.setPlainText(self._get_display_name())
            self.update_label_pos()

    def destroy(self):
        """Cleanly remove the pin and its label from the scene."""
        self.label.setParentItem(None)
        if self.node and self.node.scene():
            self.node.scene().removeItem(self.label)
        self.setParentItem(None)
        if self.node and self.node.scene():
            self.node.scene().removeItem(self)

    def update_label_pos(self):
        """Update the position of the pin's text label relative to the pin."""
        from utils.debug_config import should_debug, DEBUG_PINS
        
        if should_debug(DEBUG_PINS):
            print(f"DEBUG: update_label_pos() called for pin '{self.name}' (direction: {self.direction})")
        
        if self.direction == "output":
            label_x = -self.label.boundingRect().width() - self.label_margin
            self.label.setPos(label_x, -self.label.boundingRect().height() / 2)
        else:
            label_x = self.label_margin
            self.label.setPos(label_x, -self.label.boundingRect().height() / 2)
        
        # Enhanced visual update - trigger repaint for label
        self.label.update()
        
        if should_debug(DEBUG_PINS):
            print(f"DEBUG: Pin '{self.name}' label positioned at ({label_x}, {-self.label.boundingRect().height() / 2})")

    def update_visual_state(self):
        """Force complete visual refresh of pin and its components."""
        from utils.debug_config import should_debug, DEBUG_PINS
        
        if should_debug(DEBUG_PINS):
            print(f"DEBUG: update_visual_state() called for pin '{self.name}'")
        
        # Update pin position and label
        self.update_label_pos()
        
        # Trigger Qt repaint for pin itself
        self.update()
        
        # Update all connections
        self.update_connections()

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget=None):
        # Use lighter color when hovering for visual feedback
        if self.hover_state:
            hover_color = self.color.lighter(130)
            hover_brush = QBrush(hover_color)
            painter.setBrush(hover_brush)
        else:
            painter.setBrush(self.brush)
        
        painter.setPen(self.pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def get_scene_pos(self):
        return self.scenePos()

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def update_connections(self):
        for conn in self.connections:
            conn.update_path()
        if self.scene():
            self.scene().update()

    def can_connect_to(self, other_pin):
        """Checks for compatibility based on pin category and type."""
        if not other_pin or self == other_pin:
            return False
        if self.node == other_pin.node:
            return False
        if self.direction == other_pin.direction:
            return False
        if other_pin.direction == "input" and len(other_pin.connections) > 0:
            return False
        if self.direction == "input" and len(self.connections) > 0:
            return False

        # Pins must be the same category (execution to execution, data to data)
        if self.pin_category != other_pin.pin_category:
            return False

        # Execution pins can always connect to each other
        if self.pin_category == "execution":
            return True

        # For data pins, check type compatibility
        # Allow 'any' to connect to anything
        if self.pin_type == "any" or other_pin.pin_type == "any":
            return True

        # Otherwise, require an exact type match
        return self.pin_type == other_pin.pin_type

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.scene().start_drag_connection(self)
            event.accept()
        else:
            event.ignore()

    def serialize(self):
        return {
            "uuid": self.uuid, 
            "name": self.name, 
            "direction": self.direction, 
            "type": self.pin_type,
            "category": self.pin_category
        }

    def hoverEnterEvent(self, event):
        """Handle mouse hover enter - activate hover visual effect"""
        self.hover_state = True
        self.setCursor(Qt.CrossCursor)  # Set cursor directly on the pin
        self.update()  # Trigger repaint with hover state
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave - deactivate hover visual effect"""
        self.hover_state = False
        self.setCursor(Qt.ArrowCursor)  # Reset cursor to default
        self.update()  # Trigger repaint without hover state
        super().hoverLeaveEvent(event)

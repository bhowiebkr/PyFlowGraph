# reroute_node.py
# A simple, draggable node for organizing connections.

import uuid
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from pin import Pin
from socket_type import SocketType

class RerouteNode(QGraphicsItem):
    """
    A small, circular node that simply passes a connection through.
    Created by double-clicking on a Connection.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.uuid = str(uuid.uuid4())
        self.title = "Reroute"
        self.radius = 8
        self.pins = []
        
        # --- Visuals ---
        self.color_background = QColor("#A0A0A0")
        self.pen_default = QPen(QColor("#202020"))
        self.pen_selected = QPen(QColor("#FFFFA500"), 2)

        # A reroute node has one input and one output of a generic type
        self.input_pin = self.add_pin("input", "input", SocketType.ANY)
        self.output_pin = self.add_pin("output", "output", SocketType.ANY)
        
        # Manually set pin positions to the center
        self.input_pin.setPos(0, 0)
        self.output_pin.setPos(0, 0)

    def add_pin(self, name, direction, pin_type_enum):
        """Adds a pin to the reroute node."""
        pin = Pin(self, name, direction, pin_type_enum)
        # Hide the pin's visuals since the node itself acts as the pin
        pin.hide()
        self.pins.append(pin)
        return pin

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius).normalized()

    def itemChange(self, change, value):
        """Update connections when the node moves."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            for pin in self.pins:
                pin.update_connections()
        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option, widget=None):
        """Paint the reroute node as a simple circle."""
        painter.setBrush(self.color_background)
        painter.setPen(self.pen_selected if self.isSelected() else self.pen_default)
        painter.drawEllipse(self.boundingRect())

    def keyPressEvent(self, event):
        """Handle key presses, e.g., delete the node."""
        if event.key() == Qt.Key_Delete:
            self.scene().remove_node(self) # Assuming a generic remove_node method exists
        else:
            super().keyPressEvent(event)

# reroute_node.py
# A simple, draggable node for organizing connections.
# Now with an expanded hitbox for easier interaction.

import uuid
from PySide6.QtWidgets import QGraphicsItem, QStyle
from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QRadialGradient, 
                           QKeyEvent, QPainterPath)
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
        self.color_base = QColor("#606060")
        self.color_highlight = QColor("#8A8A8A")
        self.color_shadow = QColor("#2D2D2D")
        self.pen_default = QPen(self.color_shadow, 1.5)
        self.pen_selected = QPen(QColor("#00AEEF"), 2.5)

        self.input_pin = self.add_pin("input", "input", SocketType.ANY)
        self.output_pin = self.add_pin("output", "output", SocketType.ANY)
        
        self.input_pin.setPos(0, 0)
        self.output_pin.setPos(0, 0)

    def add_pin(self, name, direction, pin_type_enum):
        pin = Pin(self, name, direction, pin_type_enum)
        pin.hide()
        self.pins.append(pin)
        return pin

    def boundingRect(self):
        # The bounding rect should be slightly larger than the hitbox to prevent clipping
        hitbox_margin = 5
        return QRectF(-self.radius - hitbox_margin, -self.radius - hitbox_margin, 
                      (self.radius + hitbox_margin) * 2, (self.radius + hitbox_margin) * 2)

    def shape(self):
        """Define a larger, invisible shape for easier interaction (hitbox)."""
        path = QPainterPath()
        # Make the hitbox a bit bigger than the visual radius
        hitbox_radius = self.radius + 4 
        path.addEllipse(QPointF(0, 0), hitbox_radius, hitbox_radius)
        return path

    def itemChange(self, change, value):
        """Update connections when the node moves."""
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for pin in self.pins:
                pin.update_connections()
        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option, widget=None):
        """Paint the reroute node, using the visual radius, not the hitbox."""
        
        # Suppress the default dotted-line selection box
        if option.state & QStyle.State_Selected:
            option.state &= ~QStyle.State_LMBDown
        
        # The rect to draw in
        draw_rect = QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

        gradient = QRadialGradient(QPointF(0, 0), self.radius)
        if self.isSelected():
            gradient.setColorAt(0, QColor("#00AEEF"))
            gradient.setColorAt(0.7, QColor("#008ECC"))
            gradient.setColorAt(1, QColor("#006EAC"))
            painter.setPen(self.pen_selected)
        else:
            gradient.setColorAt(0, self.color_highlight)
            gradient.setColorAt(1, self.color_base)
            painter.setPen(self.pen_default)

        painter.setBrush(gradient)
        painter.drawEllipse(draw_rect)

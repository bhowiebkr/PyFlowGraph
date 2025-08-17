# reroute_node.py
# A simple, draggable node for organizing connections.
# Now uses the dynamic color generation system.

import uuid
import sys
import os

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QGraphicsItem, QStyle
from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QKeyEvent, QPainterPath
from .pin import Pin
from utils.color_utils import generate_color_from_string


class RerouteNode(QGraphicsItem):
    """
    A small, circular node that passes a connection through and
    adopts the color of the data type.
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
        self.is_reroute = True  # Mark this as a reroute node for special handling

        self.input_pin = self.add_pin("input", "input", "any")
        self.output_pin = self.add_pin("output", "output", "any")

        self.input_pin.setPos(0, 0)
        self.output_pin.setPos(0, 0)

        self.update_color()

    def update_color(self):
        """Updates the node's color based on its input connection."""
        if self.input_pin.connections:
            source_pin = self.input_pin.connections[0].start_pin
            new_type = source_pin.pin_type
            new_color = source_pin.color
        else:
            new_type = "any"
            new_color = generate_color_from_string("any")

        self.color_base = new_color.darker(110)
        self.color_highlight = new_color.lighter(110)
        self.color_shadow = new_color.darker(140)
        self.pen_default = QPen(self.color_shadow, 1.5)
        self.pen_selected = QPen(new_color.lighter(150), 2.5)

        self.output_pin.pin_type = new_type
        self.output_pin.color = new_color

        if self.scene():
            self.output_pin.update_connections()
            self.update()

    def add_pin(self, name, direction, pin_type_str, pin_category="data"):
        pin = Pin(self, name, direction, pin_type_str, pin_category)
        pin.hide()
        self.pins.append(pin)
        return pin

    def get_pin_by_name(self, name):
        if name == "input":
            return self.input_pin
        elif name == "output":
            return self.output_pin
        return None

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius).adjusted(-5, -5, 5, 5)

    def shape(self):
        path = QPainterPath()
        hitbox_radius = self.radius + 4
        path.addEllipse(QPointF(0, 0), hitbox_radius, hitbox_radius)
        return path

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for pin in self.pins:
                pin.update_connections()
        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option, widget=None):
        if option.state & QStyle.State_Selected:
            option.state &= ~QStyle.State_Selected

        draw_rect = QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)
        gradient = QRadialGradient(QPointF(0, 0), self.radius)

        if self.isSelected():
            painter.setPen(self.pen_selected)
            gradient.setColorAt(0, self.color_base.lighter(130))
            gradient.setColorAt(1, self.color_base)
        else:
            painter.setPen(self.pen_default)
            gradient.setColorAt(0, self.color_highlight)
            gradient.setColorAt(1, self.color_base)

        painter.setBrush(gradient)
        painter.drawEllipse(draw_rect)

    def serialize(self):
        return {"uuid": self.uuid, "pos": (self.pos().x(), self.pos().y()), "is_reroute": True}

# pin.py
# Represents an input or output socket on a node.
# Now manages its own text label.

import uuid
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from socket_type import SocketType

class Pin(QGraphicsItem):
    """
    A pin represents an input or output on a Node.
    It handles drawing itself, its label, and its connections.
    """
    def __init__(self, node, name, direction, pin_type_enum, parent=None):
        super().__init__(node)
        
        self.node = node
        self.name = name
        self.direction = direction
        self.pin_type = pin_type_enum
        self.uuid = str(uuid.uuid4())
        
        self.radius = 6
        self.connections = []
        self.value = None
        self.label_margin = 8

        # --- Visuals ---
        self.color = self.pin_type.value
        self.brush = QBrush(self.color)
        self.pen = QPen(QColor("#F0F0F0"))
        self.pen.setWidth(2)
        
        # --- Label ---
        self.label = QGraphicsTextItem(self.name.replace("_", " ").title(), self)
        self.label.setDefaultTextColor(QColor("#FFDDDDDD"))
        self.label.setFont(QFont("Arial", 10))
        self.update_label_pos()

        self.setAcceptHoverEvents(True)

    def destroy(self):
        """Cleanly remove the pin and its label from the scene."""
        self.label.setParentItem(None)
        self.node.scene().removeItem(self.label)
        self.setParentItem(None)
        self.node.scene().removeItem(self)

    def update_label_pos(self):
        """Update the position of the pin's text label relative to the pin."""
        if self.direction == "output":
            # Align text to the left of the pin
            label_x = -self.label.boundingRect().width() - self.label_margin
            self.label.setPos(label_x, -self.label.boundingRect().height() / 2)
        else:
            # Align text to the right of the pin
            label_x = self.label_margin
            self.label.setPos(label_x, -self.label.boundingRect().height() / 2)

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget=None):
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
        self.scene().update()

    def can_connect_to(self, other_pin):
        if not other_pin or self == other_pin: return False
        if self.node == other_pin.node: return False
        if self.direction == other_pin.direction: return False
        if other_pin.direction == "input" and len(other_pin.connections) > 0: return False
        if self.direction == "input" and len(self.connections) > 0: return False
        
        if self.pin_type == other_pin.pin_type: return True
        if self.pin_type == SocketType.ANY or other_pin.pin_type == SocketType.ANY: return True
        
        return False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.scene().start_drag_connection(self)
            event.accept()
        else:
            event.ignore()

    def serialize(self):
        return {"uuid": self.uuid, "name": self.name, "direction": self.direction, "type": self.pin_type.name.lower()}

# connection.py
# Represents the visual (Bezier curve) and logical link between two pins.
# Now correctly serializes connections involving reroute nodes.

from PySide6.QtWidgets import QGraphicsPathItem, QStyle, QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QPainterPath, QColor, QMouseEvent

class Connection(QGraphicsPathItem):
    """
    A Bezier curve connecting two pins in the node graph.
    """
    def __init__(self, start_pin, end_pin, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

        self.start_pin = start_pin
        self.end_pin = end_pin
        
        self.color = QColor("lightgray")
        self._pen = QPen(self.color)
        self._pen.setWidth(3)
        self._pen_selected = QPen(self.color)
        self._pen_selected.setWidth(4)
        
        self.setPen(self._pen)

        if self.start_pin and self.end_pin:
            self.start_pin.add_connection(self)
            self.end_pin.add_connection(self)
            self.update_path()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.scene().create_reroute_node_on_connection(self, event.scenePos())
        event.accept()

    def set_end_pos(self, pos):
        self.update_path(end_pos=pos)

    def update_path(self, end_pos=None):
        path = QPainterPath()
        if not self.start_pin: return
        
        self.color = self.start_pin.color
        self._pen.setColor(self.color)
        self._pen_selected.setColor(self.color.lighter(150))

        p1 = self.start_pin.get_scene_pos()
        p2 = end_pos if (self.end_pin is None and end_pos) else self.end_pin.get_scene_pos()
        path.moveTo(p1)
        dx = p2.x() - p1.x()
        ctrl1 = p1 + QPointF(dx * 0.5, 0)
        ctrl2 = p2 - QPointF(dx * 0.5, 0)
        path.cubicTo(ctrl1, ctrl2, p2)
        self.setPath(path)

    def paint(self, painter, option, widget=None):
        self.setPen(self._pen_selected if self.isSelected() else self._pen)
        if option.state & QStyle.State_Selected:
            option.state &= ~QStyle.State_Selected
        super().paint(painter, option, widget)

    def remove(self):
        if self.start_pin: self.start_pin.remove_connection(self)
        if self.end_pin: self.end_pin.remove_connection(self)

    def destroy(self):
        """Destroy the connection by removing it from connected pins."""
        self.remove()

    def serialize(self):
        """Serializes the connection, including pin UUIDs as expected by tests."""
        if not self.start_pin or not self.end_pin: 
            return None
        
        # Check if both connected nodes have a UUID attribute. Both Node and RerouteNode do.
        if not hasattr(self.start_pin.node, 'uuid') or not hasattr(self.end_pin.node, 'uuid'):
            return None

        return {
            "start_node_uuid": self.start_pin.node.uuid,
            "start_pin_uuid": self.start_pin.uuid,
            "start_pin_name": self.start_pin.name,
            "end_node_uuid": self.end_pin.node.uuid,
            "end_pin_uuid": self.end_pin.uuid,
            "end_pin_name": self.end_pin.name,
        }

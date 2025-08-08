# connection.py
# Represents the visual (Bezier curve) and logical link between two pins.
# Now handles double-clicks to create reroute nodes.

from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QPainterPath, QColor, QMouseEvent

class Connection(QGraphicsPathItem):
    """
    A Bezier curve connecting two pins in the node graph.
    """
    def __init__(self, start_pin, end_pin, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsPathItem.ItemIsSelectable)
        self.setZValue(-1)

        self.start_pin = start_pin
        self.end_pin = end_pin
        
        self.color = start_pin.color if start_pin else QColor("lightgray")
        self._pen = QPen(self.color)
        self._pen.setWidth(3)
        self._pen_selected = QPen(QColor("#FFFFA500"))
        self._pen_selected.setWidth(5)
        
        self.setPen(self._pen)

        if self.start_pin and self.end_pin:
            self.start_pin.add_connection(self)
            self.end_pin.add_connection(self)
            self.update_path()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """On double-click, create a reroute node."""
        self.scene().create_reroute_node_on_connection(self, event.scenePos())
        event.accept()

    def set_end_pos(self, pos):
        self.update_path(end_pos=pos)

    def update_path(self, end_pos=None):
        path = QPainterPath()
        if not self.start_pin: return
        
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
        super().paint(painter, option, widget)

    def remove(self):
        if self.start_pin: self.start_pin.remove_connection(self)
        if self.end_pin: self.end_pin.remove_connection(self)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.scene().remove_connection(self)
        else:
            super().keyPressEvent(event)

    def serialize(self):
        if not self.start_pin or not self.end_pin: return None
        # Do not serialize connections to/from reroute nodes directly in this format
        # as they are rebuilt dynamically. A more robust system would be needed.
        # For now, we just save direct node-to-node connections.
        from node import Node
        if not isinstance(self.start_pin.node, Node) or not isinstance(self.end_pin.node, Node):
            return None

        return {
            "start_node_uuid": self.start_pin.node.uuid,
            "start_pin_uuid": self.start_pin.name,
            "end_node_uuid": self.end_pin.node.uuid,
            "end_pin_uuid": self.end_pin.name,
        }

# node_interaction_handler.py
# Handles all mouse and context menu interactions for a Node.
# This version contains the definitive fix for the resizing logic.

from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor
from node_properties_dialog import NodePropertiesDialog

class NodeInteractionHandler:
    """A mixin class for Node that handles all user interaction events."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_resizing = False
        self._resize_handle_size = 15

    def itemChange(self, change, value):
        """
        Handles selection and position changes to update visuals and connections.
        """
        if change == QGraphicsItem.ItemSelectedChange:
            self.highlight_connections(value)
        
        if change == QGraphicsItem.ItemPositionHasChanged:
            for pin in self.pins:
                pin.update_connections()

        return super().itemChange(change, value)

    def highlight_connections(self, selected):
        """Sets the selection state of all connected wires."""
        for pin in self.pins:
            for conn in pin.connections:
                conn.setSelected(selected)

    def contextMenuEvent(self, event):
        parent_widget = self.scene().views()[0] if self.scene().views() else None
        dialog = NodePropertiesDialog(self.title, self.color_title_bar, self.color_body, parent_widget)
        if dialog.exec():
            props = dialog.get_properties()
            self.title = props["title"]
            self._title_item.setPlainText(self.title)
            self.color_title_bar = QColor(props["title_color"])
            self.color_body = QColor(props["body_color"])
            self.update()

    def get_resize_handle_rect(self):
        return QRectF(self.width - self._resize_handle_size, self.height - self._resize_handle_size,
                      self._resize_handle_size, self._resize_handle_size)

    def hoverMoveEvent(self, event):
        if self.get_resize_handle_rect().contains(event.pos()):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if self.get_resize_handle_rect().contains(event.pos()):
            self._is_resizing = True
        else:
            self._is_resizing = False
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_resizing:
            # --- Definitive Resizing Fix ---
            # 1. Prepare the item for a geometry change.
            self.prepareGeometryChange()
            
            # 2. The drag event is the source of truth for the new size.
            self.width = max(250, event.pos().x())
            self.height = max(150, event.pos().y())
            
            # 3. Trigger a layout update to make internal components conform to the new size.
            self._update_layout()
            
            # 4. Update connections in real-time.
            for pin in self.pins:
                pin.update_connections()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._is_resizing:
            self._is_resizing = False
            self._update_layout()
            self.update()
        else:
            super().mouseReleaseEvent(event)

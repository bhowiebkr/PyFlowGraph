# node_editor_view.py
# The QGraphicsView responsible for rendering the scene and handling user interactions.
# Now with a fix for the copy/paste key event crash.

from PySide6.QtWidgets import QGraphicsView, QMenu
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent, QContextMenuEvent, QKeyEvent, QCursor

class NodeEditorView(QGraphicsView):
    """
    Custom QGraphicsView for the node editor. Handles zooming, panning, and key events.
    """
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        self._is_panning = False
        self._pan_start_pos = QPoint()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for copy and paste."""
        # BUG FIX: QKeyEvent does not have globalPos(). Use QCursor.pos() instead
        # to get the current global mouse position.
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            cursor_pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            self.scene().copy_selected(cursor_pos)
            event.accept()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            cursor_pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            self.scene().paste(cursor_pos)
            event.accept()
        else:
            # Pass other key events (like Delete) to the scene
            super().keyPressEvent(event)

    def show_context_menu(self, event: QContextMenuEvent):
        menu = QMenu(self)
        add_node_action = menu.addAction("Add Node")
        action = menu.exec(event.globalPos())
        if action == add_node_action:
            main_window = self.window()
            if hasattr(main_window, 'on_add_node'):
                scene_pos = self.mapToScene(event.pos())
                main_window.on_add_node(scene_pos=scene_pos)

    def mousePressEvent(self, event: QMouseEvent):
        is_pan_button = event.button() in (Qt.RightButton, Qt.MiddleButton)
        if is_pan_button:
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.setDragMode(QGraphicsView.NoDrag)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            delta = event.pos() - self._pan_start_pos
            self._pan_start_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        is_pan_button = event.button() in (Qt.RightButton, Qt.MiddleButton)
        if self._is_panning and is_pan_button:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.RubberBandDrag)
            if event.button() == Qt.RightButton and (event.pos() - self._pan_start_pos).manhattanLength() < 3:
                pos = event.pos()
                global_pos = event.globalPos()
                modifiers = event.modifiers()
                QTimer.singleShot(0, lambda: self.show_context_menu(QContextMenuEvent(
                    QContextMenuEvent.Mouse, pos, global_pos, modifiers
                )))
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        background_color = QColor("#393939")
        light_pen_color = QColor("#2F2F2F")
        dark_pen_color = QColor("#202020")
        painter.fillRect(rect, background_color)
        grid_size_small, grid_size_large = 20, 100
        pen_light, pen_dark = QPen(light_pen_color), QPen(dark_pen_color)
        pen_light.setWidth(1); pen_dark.setWidth(2)
        left, right = int(rect.left()), int(rect.right())
        top, bottom = int(rect.top()), int(rect.bottom())
        first_left_s, first_top_s = left - (left % grid_size_small), top - (top % grid_size_small)
        first_left_l, first_top_l = left - (left % grid_size_large), top - (top % grid_size_large)
        painter.setPen(pen_light)
        for x in range(first_left_s, right, grid_size_small): painter.drawLine(x, top, x, bottom)
        for y in range(first_top_s, bottom, grid_size_small): painter.drawLine(left, y, right, y)
        painter.setPen(pen_dark)
        for x in range(first_left_l, right, grid_size_large): painter.drawLine(x, top, x, bottom)
        for y in range(first_top_l, bottom, grid_size_large): painter.drawLine(left, y, right, y)

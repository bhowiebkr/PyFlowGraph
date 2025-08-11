# node_editor_view.py
# The QGraphicsView responsible for rendering the scene and handling user interactions.
# Now with an improved, more refined background grid and panning logic.

from PySide6.QtWidgets import QGraphicsView, QMenu
from PySide6.QtCore import Qt, QPoint, QTimer, QLineF
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent, QContextMenuEvent, QKeyEvent, QCursor


class NodeEditorView(QGraphicsView):
    """
    Custom QGraphicsView for the node editor. Handles zooming and Blueprint-style panning.
    """

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        # --- UI Enhancements ---
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # --- Background Grid Properties ---
        self._background_color = QColor(38, 38, 38)
        self._grid_size_fine = 15
        self._grid_size_course = 150
        self._grid_pen_s = QPen(QColor(52, 52, 52, 255), 0.5)
        self._grid_pen_l = QPen(QColor(22, 22, 22, 255), 1.0)

        self._is_panning = False
        self._pan_start_pos = QPoint()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for copy and paste."""
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            cursor_pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            self.scene().copy_selected(cursor_pos)
            event.accept()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            cursor_pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            self.scene().paste(cursor_pos)
            event.accept()
        else:
            super().keyPressEvent(event)

    def show_context_menu(self, event: QContextMenuEvent):
        menu = QMenu(self)
        add_node_action = menu.addAction("Add Node")
        action = menu.exec(event.globalPos())
        if action == add_node_action:
            main_window = self.window()
            if hasattr(main_window, "on_add_node"):
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
            # --- New Panning Logic ---
            # This method simulates dragging the scrollbars for a more robust pan.
            delta = event.pos() - self._pan_start_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            # Update the start position for the next move event.
            self._pan_start_pos = event.pos()
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
                pos, global_pos, modifiers = event.pos(), event.globalPos(), event.modifiers()
                QTimer.singleShot(0, lambda: self.show_context_menu(QContextMenuEvent(QContextMenuEvent.Mouse, pos, global_pos, modifiers)))
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
        """
        Draws the background for the node editor view.
        """
        painter.fillRect(rect, self._background_color)

        left = int(rect.left()) - (int(rect.left()) % self._grid_size_fine)
        top = int(rect.top()) - (int(rect.top()) % self._grid_size_fine)

        # Draw horizontal fine lines
        gridLines = []
        painter.setPen(self._grid_pen_s)
        y = float(top)
        while y < float(rect.bottom()):
            gridLines.append(QLineF(rect.left(), y, rect.right(), y))
            y += self._grid_size_fine
        painter.drawLines(gridLines)

        # Draw vertical fine lines
        gridLines = []
        x = float(left)
        while x < float(rect.right()):
            gridLines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += self._grid_size_fine
        painter.drawLines(gridLines)

        # Draw thick grid
        left = int(rect.left()) - (int(rect.left()) % self._grid_size_course)
        top = int(rect.top()) - (int(rect.top()) % self._grid_size_course)

        # Draw vertical thick lines
        gridLines = []
        painter.setPen(self._grid_pen_l)
        x = left
        while x < rect.right():
            gridLines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += self._grid_size_course
        painter.drawLines(gridLines)

        # Draw horizontal thick lines
        gridLines = []
        y = top
        while y < rect.bottom():
            gridLines.append(QLineF(rect.left(), y, rect.right(), y))
            y += self._grid_size_course
        painter.drawLines(gridLines)

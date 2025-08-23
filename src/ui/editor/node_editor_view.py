# node_editor_view.py
# The QGraphicsView responsible for rendering the scene and handling user interactions.
# Now with an improved, more refined background grid and panning logic.

import sys
import os
from PySide6.QtWidgets import QGraphicsView, QMenu
from PySide6.QtCore import Qt, QPoint, QTimer, QLineF
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent, QContextMenuEvent, QKeyEvent, QCursor

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


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
        
        # Group resize state
        self._is_resizing_group = False
        self._resize_group = None
        self._resize_handle = None

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for copy and paste."""
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            # BUG FIX: The copy_selected method no longer takes the cursor position as an argument.
            self.scene().copy_selected()
            event.accept()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # Get current mouse cursor position in scene coordinates
            global_mouse_pos = QCursor.pos()
            local_mouse_pos = self.mapFromGlobal(global_mouse_pos)  
            scene_mouse_pos = self.mapToScene(local_mouse_pos)
            self.scene().paste(scene_mouse_pos)  # Pass actual mouse position
            event.accept()
        else:
            super().keyPressEvent(event)

    def show_context_menu(self, event: QContextMenuEvent):
        scene_pos = self.mapToScene(event.pos())
        item_at_pos = self.scene().itemAt(scene_pos, self.transform())
        
        # Find the top-level item if we clicked on a child item (using duck typing)
        node = None
        group = None
        if item_at_pos:
            current_item = item_at_pos
            while current_item:
                if type(current_item).__name__ in ['Node', 'RerouteNode']:
                    node = current_item
                    break
                elif type(current_item).__name__ == 'Group':
                    group = current_item
                    break
                current_item = current_item.parentItem()
        
        menu = QMenu(self)
        
        # Get selected items for group operations (using duck typing)
        selected_items = [item for item in self.scene().selectedItems() if type(item).__name__ in ['Node', 'RerouteNode']]
        
        if group:
            # Context menu for a group
            properties_action = menu.addAction("Group Properties")
            
            action = menu.exec(event.globalPos())
            if action == properties_action:
                group.show_properties_dialog()
                
        elif node:
            # Context menu for a node
            properties_action = menu.addAction("Properties")
            
            # Add group option if multiple nodes are selected
            group_action = None
            if len(selected_items) >= 2:
                group_action = menu.addAction("Group Selected")
                # Basic validation - ensure we have valid nodes
                if not self._can_group_nodes(selected_items):
                    group_action.setEnabled(False)
            
            action = menu.exec(event.globalPos())
            if action == properties_action:
                node.show_properties_dialog()
            elif action == group_action and group_action:
                self._create_group_from_selection(selected_items)
        else:
            # Context menu for empty space
            add_node_action = menu.addAction("Add Node")
            
            # Add group option if multiple nodes are selected
            group_action = None
            if len(selected_items) >= 2:
                group_action = menu.addAction("Group Selected")
                # Basic validation - ensure we have valid nodes
                if not self._can_group_nodes(selected_items):
                    group_action.setEnabled(False)
            
            # Add group properties option if a group is selected (but not clicked directly)
            selected_groups = [item for item in self.scene().selectedItems() if type(item).__name__ == 'Group']
            group_properties_action = None
            if len(selected_groups) == 1:
                group_properties_action = menu.addAction("Group Properties")
            
            action = menu.exec(event.globalPos())
            if action == add_node_action:
                main_window = self.window()
                if hasattr(main_window, "on_add_node"):
                    main_window.on_add_node(scene_pos=scene_pos)
            elif action == group_action and group_action:
                self._create_group_from_selection(selected_items)
            elif action == group_properties_action and group_properties_action:
                selected_groups[0].show_properties_dialog()
    
    def _can_group_nodes(self, nodes):
        """Basic validation for group creation"""
        # Must have at least 2 nodes
        if len(nodes) < 2:
            return False
        
        # Use duck typing to validate node-like objects
        for node in nodes:
            node_type_name = type(node).__name__
            
            # Check if it's a Node-like object by class name
            if node_type_name not in ['Node', 'RerouteNode']:
                return False
            
            # Check for essential Node attributes
            if not hasattr(node, 'uuid'):
                return False
            if not hasattr(node, 'title'):
                return False
            if not hasattr(node, 'pins'):
                return False
                
        return True
    
    def _create_group_from_selection(self, selected_nodes):
        """Create a group from selected nodes"""
        # Delegate to the node graph for actual group creation
        self.scene()._create_group_from_selection(selected_nodes)
    
    def _get_group_resize_handle_at_pos(self, scene_pos):
        """Find if a group resize handle is at the given scene position"""
        # Check ALL groups in the scene, regardless of Z-order
        # This fixes the issue where groups with Z=-1 are behind other items
        for item in self.scene().items():
            if type(item).__name__ == 'Group' and item.isSelected():
                # Check if the scene position is within the group's bounding rect
                group_rect = item.sceneBoundingRect()
                if group_rect.contains(scene_pos):
                    # Convert scene position to item-local coordinates
                    local_pos = item.mapFromScene(scene_pos)
                    handle = item.get_handle_at_pos(local_pos)
                    if handle != item.HANDLE_NONE:
                        return item, handle
        return None, None

    def mousePressEvent(self, event: QMouseEvent):
        is_pan_button = event.button() in (Qt.RightButton, Qt.MiddleButton)
        
        # Check for group resize handle interaction first
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            group, handle = self._get_group_resize_handle_at_pos(scene_pos)
            
            if group and handle != group.HANDLE_NONE:
                # Start group resize operation
                self._is_resizing_group = True
                self._resize_group = group
                self._resize_handle = handle
                self.setCursor(group.get_cursor_for_handle(handle))
                self.setDragMode(QGraphicsView.NoDrag)
                group.start_resize(handle, scene_pos)
                event.accept()
                return
        
        if is_pan_button:
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.setDragMode(QGraphicsView.NoDrag)
            event.accept()
        else:
            # Before letting base class handle selection, prepare all groups for potential state changes
            if event.button() == Qt.LeftButton:
                # Force all groups to prepare for geometry changes (in case selection changes)
                for item in self.scene().items():
                    if type(item).__name__ == 'Group':
                        item.prepareGeometryChange()
            
            # Let the base class handle selection, which should properly clear other selections
            super().mousePressEvent(event)
            
            # After selection is handled, force comprehensive update of all groups
            if event.button() == Qt.LeftButton:
                # Get the area that needs updating (all group bounding rects)
                update_regions = []
                for item in self.scene().items():
                    if type(item).__name__ == 'Group':
                        # Update the group itself
                        item.update()
                        # Also update the scene area where handles might have been drawn
                        expanded_rect = item.boundingRect()
                        scene_rect = item.mapRectToScene(expanded_rect)
                        update_regions.append(scene_rect)
                
                # Force scene updates for all affected regions to clear drawing artifacts
                for region in update_regions:
                    self.scene().update(region)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_resizing_group and self._resize_group:
            # Handle group resizing
            scene_pos = self.mapToScene(event.pos())
            self._resize_group.update_resize(scene_pos)
            event.accept()
        elif self._is_panning:
            # This method simulates dragging the scrollbars for a more robust pan.
            delta = event.pos() - self._pan_start_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            # Update the start position for the next move event.
            self._pan_start_pos = event.pos()
            event.accept()
        else:
            # Update cursor when hovering over resize handles
            scene_pos = self.mapToScene(event.pos())
            group, handle = self._get_group_resize_handle_at_pos(scene_pos)
            if group and handle != group.HANDLE_NONE:
                self.setCursor(group.get_cursor_for_handle(handle))
            else:
                self.setCursor(Qt.ArrowCursor)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        is_pan_button = event.button() in (Qt.RightButton, Qt.MiddleButton)
        
        if self._is_resizing_group and event.button() == Qt.LeftButton:
            # Finish group resize operation
            if self._resize_group:
                self._resize_group.finish_resize()
            self._is_resizing_group = False
            self._resize_group = None
            self._resize_handle = None
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.RubberBandDrag)
            event.accept()
        elif self._is_panning and is_pan_button:
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

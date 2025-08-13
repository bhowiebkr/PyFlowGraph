# view_state_manager.py
# View state management for saving and restoring view transforms and positions

from PySide6.QtCore import QSettings, QPointF
from PySide6.QtGui import QTransform


class ViewStateManager:
    """Manages saving and loading of view state (zoom, pan) for different files."""
    
    def __init__(self, view, file_operations_manager):
        self.view = view
        self.file_ops = file_operations_manager
        self.settings = QSettings("PyFlowGraph", "NodeEditor")
    
    def save_view_state(self):
        """Saves the current view's transform (zoom) and center point (pan) to QSettings."""
        if self.file_ops.current_file_path:
            self.settings.beginGroup(f"view_state/{self.file_ops.current_file_path}")
            self.settings.setValue("transform", self.view.transform())
            # Save the scene coordinates of the center of the view
            center_point = self.view.mapToScene(self.view.viewport().rect().center())
            self.settings.setValue("center_point", center_point)
            self.settings.endGroup()

    def load_view_state(self):
        """Loads and applies the view's transform and center point from QSettings."""
        if self.file_ops.current_file_path:
            self.settings.beginGroup(f"view_state/{self.file_ops.current_file_path}")
            transform_data = self.settings.value("transform")
            center_point = self.settings.value("center_point")
            self.settings.endGroup()

            if isinstance(transform_data, QTransform):
                self.view.setTransform(transform_data)

            if isinstance(center_point, QPointF):
                # Use centerOn to robustly set the pan position
                self.view.centerOn(center_point)
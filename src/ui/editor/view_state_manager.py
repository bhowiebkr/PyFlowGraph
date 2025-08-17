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
    
    def save_view_state(self, file_path=None):
        """Saves the current view's transform (zoom) and center point (pan) to QSettings."""
        # Use provided file_path or fall back to current file path
        target_file_path = file_path or self.file_ops.current_file_path
        
        if target_file_path:
            transform = self.view.transform()
            center_point = self.view.mapToScene(self.view.viewport().rect().center())
            
            self.settings.beginGroup(f"view_state/{target_file_path}")
            self.settings.setValue("transform", transform)
            self.settings.setValue("center_point", center_point)
            self.settings.endGroup()
            

    def load_view_state(self):
        """Loads and applies the view's transform and center point from QSettings."""
        if self.file_ops.current_file_path:
            self.settings.beginGroup(f"view_state/{self.file_ops.current_file_path}")
            transform = self.settings.value("transform")
            center_point = self.settings.value("center_point")
            self.settings.endGroup()

            if transform:
                self.view.setTransform(transform)
            if center_point:
                self.view.centerOn(center_point)
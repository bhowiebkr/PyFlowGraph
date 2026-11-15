# environment_selection_dialog.py
# Dialog for selecting virtual environment when loading example graphs

import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QRadioButton, QButtonGroup, QTextEdit,
                              QDialogButtonBox, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class EnvironmentSelectionDialog(QDialog):
    """Dialog for selecting virtual environment type when loading example graphs."""
    
    def __init__(self, graph_name, parent=None):
        super().__init__(parent)
        self.graph_name = graph_name
        self.selected_option = "default"  # default, graph_specific, existing
        
        self.setWindowTitle("Environment Selection")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        
        # Set window flags to ensure it appears on top and gets focus
        self.setWindowFlags(
            Qt.Dialog | 
            Qt.WindowTitleHint | 
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint
        )
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel(f"Select Environment for '{self.graph_name}'")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "Choose how to handle the Python environment for this graph. "
            "If you're new to PyFlowGraph, the default environment is recommended."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888; margin: 10px 0;")
        layout.addWidget(desc_label)
        
        # Radio button group
        self.button_group = QButtonGroup(self)
        
        # Option 1: Use Default Environment (Recommended)
        self._add_option_section(layout, 
                               "default",
                               "Use Default Environment (Recommended)",
                               "Uses venvs/default with basic packages like PySide6. Perfect for beginners "
                               "and trying out examples. Created automatically if needed.",
                               True)  # Selected by default
        
        # Option 2: Create Graph-Specific Environment  
        self._add_option_section(layout,
                               "graph_specific", 
                               "Create Graph-Specific Environment",
                               "Creates a dedicated environment just for this graph. Allows custom "
                               "packages but requires setup time.",
                               False)
        
        # Option 3: Use Existing Environment (if available)
        existing_path = self._get_existing_venv_path()
        if existing_path and os.path.exists(existing_path):
            self._add_option_section(layout,
                                   "existing",
                                   "Use Existing Graph Environment", 
                                   f"Uses the existing environment for this graph: {existing_path}",
                                   False)
        
        layout.addStretch()
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _add_option_section(self, layout, option_id, title, description, selected=False):
        """Add an option section with radio button and description."""
        # Create frame for this option
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #444; border-radius: 5px; padding: 10px; margin: 5px 0; }")
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(15, 10, 15, 10)
        
        # Radio button with title
        radio = QRadioButton(title)
        radio.setChecked(selected)
        if selected:
            self.selected_option = option_id
        
        radio_font = QFont()
        radio_font.setPointSize(11)
        radio_font.setBold(True)
        radio.setFont(radio_font)
        
        self.button_group.addButton(radio)
        radio.toggled.connect(lambda checked, opt=option_id: self._on_option_selected(checked, opt))
        
        frame_layout.addWidget(radio)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #bbb; margin-left: 20px; margin-top: 5px;")
        frame_layout.addWidget(desc_label)
        
        layout.addWidget(frame)
    
    def _on_option_selected(self, checked, option_id):
        """Handle option selection."""
        if checked:
            self.selected_option = option_id
    
    def _get_existing_venv_path(self):
        """Get the path to existing graph-specific venv if it exists."""
        # This would be passed from the parent or calculated
        # For now, return a placeholder path
        return os.path.join("venvs", self.graph_name)
    
    def get_selected_option(self):
        """Get the selected environment option."""
        return self.selected_option
    
    def get_explanation_text(self):
        """Get explanation text for the selected option."""
        explanations = {
            "default": "Will use venvs/default environment. Ready to execute immediately.",
            "graph_specific": f"Will create environment: venvs/{self.graph_name}. You can customize packages in the Environment Manager.",
            "existing": f"Will use existing environment: venvs/{self.graph_name}."
        }
        return explanations.get(self.selected_option, "")
    
    def exec(self):
        """Override exec to ensure the dialog appears on top and gets focus."""
        # Center on parent if available
        if self.parent():
            parent_rect = self.parent().geometry()
            dialog_rect = self.geometry()
            x = parent_rect.x() + (parent_rect.width() - dialog_rect.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - dialog_rect.height()) // 2
            self.move(x, y)
        
        # Ensure the dialog appears on top and gets focus
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Call the parent exec method
        return super().exec()
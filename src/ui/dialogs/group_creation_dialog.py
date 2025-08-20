# group_creation_dialog.py
# Dialog for configuring group creation parameters with automatic name generation and validation.

import sys
import os
from typing import List, Optional

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QTextEdit, QPushButton, QDialogButtonBox,
                               QFormLayout, QSpinBox, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class GroupCreationDialog(QDialog):
    """
    Dialog for creating a new group with automatic name generation and validation.
    Allows users to customize group properties before creation.
    """

    def __init__(self, selected_nodes, parent=None):
        super().__init__(parent)
        self.selected_nodes = selected_nodes
        self.setWindowTitle("Create Group")
        self.setModal(True)
        self.resize(400, 300)
        
        # Initialize dialog properties
        self._setup_ui()
        self._generate_default_name()
        self._validate_inputs()
    
    def _setup_ui(self):
        """Setup the dialog user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Create New Group")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Group information section
        form_layout = QFormLayout()
        
        # Group name input
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter group name...")
        self.name_edit.textChanged.connect(self._validate_inputs)
        form_layout.addRow("Group Name:", self.name_edit)
        
        # Group description input
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional description...")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        # Member count display (read-only)
        self.member_count_label = QLabel(str(len(self.selected_nodes)))
        form_layout.addRow("Member Nodes:", self.member_count_label)
        
        layout.addLayout(form_layout)
        
        # Group options section
        options_label = QLabel("Options")
        options_font = QFont()
        options_font.setBold(True)
        options_label.setFont(options_font)
        layout.addWidget(options_label)
        
        options_layout = QVBoxLayout()
        
        # Auto-size checkbox
        self.auto_size_checkbox = QCheckBox("Auto-size group to fit members")
        self.auto_size_checkbox.setChecked(True)
        options_layout.addWidget(self.auto_size_checkbox)
        
        # Padding spinbox
        padding_layout = QHBoxLayout()
        padding_layout.addWidget(QLabel("Padding:"))
        self.padding_spinbox = QSpinBox()
        self.padding_spinbox.setRange(10, 100)
        self.padding_spinbox.setValue(20)
        self.padding_spinbox.setSuffix(" px")
        padding_layout.addWidget(self.padding_spinbox)
        padding_layout.addStretch()
        options_layout.addLayout(padding_layout)
        
        layout.addLayout(options_layout)
        
        # Member nodes preview
        preview_label = QLabel("Selected Nodes:")
        preview_font = QFont()
        preview_font.setBold(True)
        preview_label.setFont(preview_font)
        layout.addWidget(preview_label)
        
        self.nodes_preview = QTextEdit()
        self.nodes_preview.setMaximumHeight(100)
        self.nodes_preview.setReadOnly(True)
        self._update_nodes_preview()
        layout.addWidget(self.nodes_preview)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setText("Create Group")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Store reference for validation
        self.button_box = button_box
    
    def _generate_default_name(self):
        """Generate a default group name based on selected nodes"""
        from core.group import generate_group_name
        default_name = generate_group_name(self.selected_nodes)
        self.name_edit.setText(default_name)
    
    def _update_nodes_preview(self):
        """Update the preview of selected nodes"""
        if not self.selected_nodes:
            self.nodes_preview.setPlainText("No nodes selected")
            return
        
        node_info = []
        for i, node in enumerate(self.selected_nodes, 1):
            title = getattr(node, 'title', f'Node {i}')
            node_type = type(node).__name__
            node_info.append(f"{i}. {title} ({node_type})")
        
        self.nodes_preview.setPlainText("\n".join(node_info))
    
    def _validate_inputs(self):
        """Validate user inputs and enable/disable OK button"""
        is_valid = True
        error_messages = []
        
        # Validate group name
        name = self.name_edit.text().strip()
        if not name:
            is_valid = False
            error_messages.append("Group name is required")
        elif len(name) > 100:
            is_valid = False
            error_messages.append("Group name too long (max 100 characters)")
        
        # Validate member count
        if len(self.selected_nodes) < 2:
            is_valid = False
            error_messages.append("Groups require at least 2 nodes")
        
        # Additional validation using group validation function
        from core.group import validate_group_creation
        group_valid, group_error = validate_group_creation(self.selected_nodes)
        if not group_valid:
            is_valid = False
            error_messages.append(group_error)
        
        # Update UI based on validation
        self.ok_button.setEnabled(is_valid)
        
        # Show tooltip with error messages if invalid
        if error_messages:
            self.ok_button.setToolTip("Cannot create group:\n" + "\n".join(error_messages))
        else:
            self.ok_button.setToolTip("Create group with selected nodes")
    
    def get_group_properties(self) -> dict:
        """Get the configured group properties from the dialog"""
        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "member_node_uuids": [node.uuid for node in self.selected_nodes],
            "auto_size": self.auto_size_checkbox.isChecked(),
            "padding": self.padding_spinbox.value()
        }
    
    def accept(self):
        """Override accept to perform final validation"""
        # Final validation before accepting
        properties = self.get_group_properties()
        
        if not properties["name"]:
            QMessageBox.warning(self, "Invalid Input", "Group name is required.")
            return
        
        from core.group import validate_group_creation
        is_valid, error_message = validate_group_creation(self.selected_nodes)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Selection", error_message)
            return
        
        super().accept()


def show_group_creation_dialog(selected_nodes, parent=None) -> Optional[dict]:
    """
    Convenience function to show the group creation dialog and return properties.
    Returns None if user cancels, otherwise returns group properties dict.
    """
    dialog = GroupCreationDialog(selected_nodes, parent)
    
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_group_properties()
    else:
        return None
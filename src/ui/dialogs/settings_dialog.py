# settings_dialog.py
# A dialog for managing application-wide settings, like the default
# path for virtual environments.

import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QDialogButtonBox, QCheckBox
from PySide6.QtCore import QSettings


class SettingsDialog(QDialog):
    """
    A dialog for editing application-wide preferences.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)

        # Use QSettings to store persistent application settings
        self.settings = QSettings("PyFlowGraph", "NodeEditor")

        layout = QVBoxLayout(self)

        # --- Venv Parent Directory Setting ---
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Default Venv Parent Directory:"))

        # Determine project root directory for default path
        if os.path.basename(os.getcwd()) == "src":
            # Development mode - go up one level from src/
            project_root = os.path.dirname(os.getcwd())
        else:
            # Compiled mode - use current directory
            project_root = os.getcwd()
        
        default_path = os.path.join(project_root, "venvs")
        current_path = self.settings.value("venv_parent_dir", default_path)
        self.path_edit = QLineEdit(current_path)

        path_layout.addWidget(self.path_edit)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_button)
        layout.addLayout(path_layout)

        # --- Pin Type Visibility Setting ---
        self.show_pin_types_checkbox = QCheckBox("Show pin types in labels (e.g., 'name (int)')")
        self.show_pin_types_checkbox.setChecked(self.settings.value("show_pin_types", True, type=bool))
        layout.addWidget(self.show_pin_types_checkbox)

        # --- OK and Cancel Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def browse_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Default Parent Directory for Virtual Environments")
        if directory:
            self.path_edit.setText(directory)

    def accept(self):
        """Saves the settings when the user clicks OK."""
        self.settings.setValue("venv_parent_dir", self.path_edit.text())
        self.settings.setValue("show_pin_types", self.show_pin_types_checkbox.isChecked())
        super().accept()

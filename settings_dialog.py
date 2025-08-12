# settings_dialog.py
# A dialog for managing application-wide settings, like the default
# path for virtual environments.

import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QDialogButtonBox
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

        default_path = os.path.join(os.getcwd(), "venvs")
        current_path = self.settings.value("venv_parent_dir", default_path)
        self.path_edit = QLineEdit(current_path)

        path_layout.addWidget(self.path_edit)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_button)
        layout.addLayout(path_layout)

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
        super().accept()

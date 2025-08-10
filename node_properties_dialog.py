# node_properties_dialog.py
# A dialog for editing the visual properties of a node, like its title and colors.

from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QColorDialog, QDialogButtonBox
from PySide6.QtGui import QColor, QPalette, QBrush


class NodePropertiesDialog(QDialog):
    """
    A dialog for editing a node's properties, including title and colors.
    """

    def __init__(self, node_title, title_color, body_color, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Node Properties")

        self.node_title = node_title
        self.title_color = QColor(title_color)
        self.body_color = QColor(body_color)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Title Editor ---
        self.title_edit = QLineEdit(self.node_title)
        form_layout.addRow("Title:", self.title_edit)

        # --- Title Color Picker ---
        self.title_color_button = QPushButton()
        self.title_color_button.clicked.connect(self.pick_title_color)
        self.update_button_color(self.title_color_button, self.title_color)
        form_layout.addRow("Title Bar Color:", self.title_color_button)

        # --- Body Color Picker ---
        self.body_color_button = QPushButton()
        self.body_color_button.clicked.connect(self.pick_body_color)
        self.update_button_color(self.body_color_button, self.body_color)
        form_layout.addRow("Body Color:", self.body_color_button)

        layout.addLayout(form_layout)

        # --- OK and Cancel Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def pick_title_color(self):
        color = QColorDialog.getColor(self.title_color, self, "Choose Title Bar Color")
        if color.isValid():
            self.title_color = color
            self.update_button_color(self.title_color_button, self.title_color)

    def pick_body_color(self):
        color = QColorDialog.getColor(self.body_color, self, "Choose Node Body Color")
        if color.isValid():
            self.body_color = color
            self.update_button_color(self.body_color_button, self.body_color)

    def update_button_color(self, button, color):
        """Sets the background color of a button to visualize the selected color."""
        button.setStyleSheet(f"background-color: {color.name()};")

    def get_properties(self):
        """Returns the edited properties."""
        return {"title": self.title_edit.text(), "title_color": self.title_color.name(), "body_color": self.body_color.name()}

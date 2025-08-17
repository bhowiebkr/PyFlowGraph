# graph_properties_dialog.py
# A dialog for editing the graph's title and description

from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox, QLabel
from PySide6.QtGui import QFont


class GraphPropertiesDialog(QDialog):
    """
    A dialog for editing a graph's properties, including title and description.
    """

    def __init__(self, graph_title, graph_description, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Graph Properties")
        self.setMinimumSize(600, 450)

        self.graph_title = graph_title
        self.graph_description = graph_description

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Title Editor ---
        self.title_edit = QLineEdit(self.graph_title)
        self.title_edit.setPlaceholderText("Enter graph title...")
        form_layout.addRow("Title:", self.title_edit)

        # --- Description Editor ---
        desc_label = QLabel("Description:")
        form_layout.addRow(desc_label)
        
        self.description_edit = QTextEdit(self.graph_description)
        self.description_edit.setMinimumHeight(250)
        self.description_edit.setPlaceholderText("Enter a description for this graph (markdown supported)...")
        
        # Set monospace font for description editor
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.description_edit.setFont(font)
        
        form_layout.addRow(self.description_edit)

        layout.addLayout(form_layout)

        # --- OK and Cancel Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_properties(self):
        """Returns the edited properties."""
        return {
            "title": self.title_edit.text().strip() or "Untitled Graph",
            "description": self.description_edit.toPlainText()
        }
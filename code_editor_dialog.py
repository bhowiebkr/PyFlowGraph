# code_editor_dialog.py
# A dedicated dialog window for editing a node's Python code.

from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
from PySide6.QtGui import QFont

class CodeEditorDialog(QDialog):
    """
    A dialog that contains a QTextEdit for editing a node's code.
    """
    def __init__(self, code, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Node Code Editor")
        self.setMinimumSize(600, 400)

        # --- Layout ---
        layout = QVBoxLayout(self)

        # --- Code Editor Widget ---
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText(code)
        self.code_edit.setFont(QFont("Monospace", 11))
        self.code_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2E2E2E;
                color: #F0F0F0;
                border: 1px solid #555;
            }
        """)
        layout.addWidget(self.code_edit)

        # --- OK and Cancel Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_code(self):
        """Returns the code currently in the editor."""
        return self.code_edit.toPlainText()

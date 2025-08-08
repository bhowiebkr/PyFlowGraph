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

        layout = QVBoxLayout(self)

        self.code_edit = QTextEdit()
        # Set placeholder text if the initial code is empty
        if not code:
            code = ("from typing import Tuple\n\n"
                    "def process_data(input_1: str) -> Tuple[str, int]:\n"
                    "    # Your code here\n"
                    "    # Use parameters for inputs and return for outputs.\n"
                    "    # Type hints define the pins.\n"
                    "    return 'processed', len(input_1)")
        
        self.code_edit.setPlainText(code)
        self.code_edit.setFont(QFont("Monospace", 11))
        
        layout.addWidget(self.code_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_code(self):
        """Returns the code currently in the editor."""
        return self.code_edit.toPlainText()

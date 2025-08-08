# code_editor_dialog.py
# A dedicated dialog window that now uses the advanced PythonCodeEditor widget.

from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtGui import QFont
from python_code_editor import PythonCodeEditor

class CodeEditorDialog(QDialog):
    """
    A dialog that hosts the advanced PythonCodeEditor widget.
    """
    def __init__(self, code, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Node Code Editor")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        # --- Use the new advanced code editor ---
        self.code_editor = PythonCodeEditor()
        self.code_editor.setFont(QFont("Monospace", 11))
        
        # Set placeholder text if the initial code is empty
        if not code:
            code = ("from typing import Tuple\n\n"
                    "def process_data(input_1: str) -> Tuple[str, int]:\n"
                    "    # Your code here\n"
                    "    # Use parameters for inputs and return for outputs.\n"
                    "    # Type hints define the pins.\n"
                    "    return 'processed', len(input_1)")
        
        self.code_editor.setPlainText(code)
        
        layout.addWidget(self.code_editor)

        # --- OK and Cancel Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_code(self):
        """Returns the code currently in the editor."""
        return self.code_editor.toPlainText()

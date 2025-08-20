# code_editor_dialog.py
# A dedicated dialog window that now uses a QTabWidget to host
# separate editors for execution code, GUI layout, and GUI logic.

import sys
import os

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QTabWidget
from PySide6.QtGui import QFont
from ui.code_editing.python_code_editor import PythonCodeEditor


class CodeEditorDialog(QDialog):
    """
    A dialog that hosts a tabbed interface for editing all of a node's code.
    """

    def __init__(self, node, node_graph, code, gui_code, gui_logic_code, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unified Code Editor")
        self.setMinimumSize(750, 600)
        
        # Store references for command creation
        self.node = node
        self.node_graph = node_graph
        self.original_code = code
        self.original_gui_code = gui_code
        self.original_gui_logic_code = gui_logic_code

        layout = QVBoxLayout(self)
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # --- Execution Code Editor ---
        self.code_editor = PythonCodeEditor()
        self.code_editor.setFont(QFont("Monospace", 11))
        exec_placeholder = "from typing import Tuple\n\n" "@node_entry\n" "def node_function(input_1: str) -> Tuple[str, int]:\n" "    return 'hello', len(input_1)"
        # Only add placeholder if the code is None (new node)
        self.code_editor.setPlainText(code if code is not None else exec_placeholder)
        tab_widget.addTab(self.code_editor, "Execution Code")

        # --- GUI Layout Code Editor ---
        self.gui_editor = PythonCodeEditor()
        self.gui_editor.setFont(QFont("Monospace", 11))
        gui_placeholder = (
            "# This script builds the node's custom GUI.\n"
            "# Use 'parent', 'layout', 'widgets', and 'QtWidgets' variables.\n\n"
            "label = QtWidgets.QLabel('Multiplier:', parent)\n"
            "spinbox = QtWidgets.QSpinBox(parent)\n"
            "spinbox.setValue(2)\n"
            "layout.addWidget(label)\n"
            "layout.addWidget(spinbox)\n"
            "widgets['multiplier'] = spinbox\n"
        )
        self.gui_editor.setPlainText(gui_code if gui_code is not None else gui_placeholder)
        tab_widget.addTab(self.gui_editor, "GUI Layout")

        # --- GUI Logic Code Editor ---
        self.gui_logic_editor = PythonCodeEditor()
        self.gui_logic_editor.setFont(QFont("Monospace", 11))
        gui_logic_placeholder = (
            "# This script defines how the GUI interacts with the execution code.\n\n"
            "def get_values(widgets):\n"
            "    return {'multiplier': widgets['multiplier'].value()}\n\n"
            "def set_values(widgets, outputs):\n"
            "    # result = outputs.get('output_1', 'N/A')\n"
            "    # widgets['result_label'].setText(f'Result: {result}')\n\n"
            "def set_initial_state(widgets, state):\n"
            "    if 'multiplier' in state:\n"
            "        widgets['multiplier'].setValue(state['multiplier'])\n"
        )
        self.gui_logic_editor.setPlainText(gui_logic_code if gui_logic_code is not None else gui_logic_placeholder)
        tab_widget.addTab(self.gui_logic_editor, "GUI Logic")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._handle_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_results(self):
        """Returns the code from all three editors in a dictionary."""
        return {"code": self.code_editor.toPlainText(), "gui_code": self.gui_editor.toPlainText(), "gui_logic_code": self.gui_logic_editor.toPlainText()}
    
    def _handle_accept(self):
        """Handle accept button by creating command and pushing to history."""
        try:
            # Get current editor content
            new_code = self.code_editor.toPlainText()
            new_gui_code = self.gui_editor.toPlainText()
            new_gui_logic_code = self.gui_logic_editor.toPlainText()
            
            # Create command for execution code changes
            if new_code != self.original_code:
                from commands.node_commands import CodeChangeCommand
                code_command = CodeChangeCommand(
                    self.node_graph, self.node, self.original_code, new_code
                )
                # Push command to graph's history if it exists
                if hasattr(self.node_graph, 'command_history'):
                    self.node_graph.command_history.push(code_command)
                else:
                    # Fallback: execute directly
                    code_command.execute()
            
            # Handle GUI code changes with direct method calls (not part of story scope)
            if new_gui_code != self.original_gui_code:
                self.node.set_gui_code(new_gui_code)
            
            if new_gui_logic_code != self.original_gui_logic_code:
                self.node.set_gui_get_values_code(new_gui_logic_code)
            
            # Accept the dialog
            self.accept()
            
        except Exception as e:
            print(f"Error handling code editor accept: {e}")
            # Still accept the dialog to avoid blocking user
            self.accept()

"""Run the password generator example after a delete and an undo.

The person deletes the two middle nodes, undoes both deletes and runs the graph. The output
node must show the password that the generator made in this run.
"""

import os
import re
import unittest

import pytest
from PySide6.QtWidgets import QApplication, QTextEdit

from pyflowgraph.commands.node_commands import DeleteNodeCommand
from pyflowgraph.execution.graph_executor import GraphExecutor
from pyflowgraph.ui.editor.node_editor_window import NodeEditorWindow

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "examples", "password_generator_tool_group.md")


class TestActualExecutionAfterUndo(unittest.TestCase):

    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.window = NodeEditorWindow()
        self.graph = self.window.graph
        self.assertTrue(self.window.file_ops.load(EXAMPLE), "The example should open")
        # Nodes run in this process, with the environment of the window.
        self.log_widget = QTextEdit()
        self.executor = GraphExecutor(self.graph, self.log_widget, self.window._get_current_venv_path)

    def tearDown(self):
        self.window.close()

    def node(self, title):
        for node in self.graph.nodes:
            if node.title == title:
                return node
        self.fail(f"Node with title '{title}' not found")

    def assert_output_shows_new_password(self):
        """Run the graph. The output node shows the one password that the generator made."""
        self.log_widget.clear()
        self.executor.execute()
        generated = re.findall(r"^Generated password: (.*)$", self.log_widget.toPlainText(), re.M)
        self.assertEqual(len(generated), 1, "The generator should run once")
        widgets = self.node("Password Output & Copy").gui_widgets
        self.assertEqual(widgets["password_field"].text(), generated[0])
        self.assertIn(f"Generated Password: {generated[0]}", widgets["strength_display"].toPlainText())

    def test_execution_updates_output(self):
        self.assert_output_shows_new_password()

    def test_actual_execution_after_delete_undo(self):
        self.assert_output_shows_new_password()
        commands = [DeleteNodeCommand(self.graph, self.node(title))
                    for title in ("Password Generator Engine", "Password Strength Analyzer")]
        for command in commands:
            self.assertTrue(command.execute(), "Delete should succeed")
        for command in reversed(commands):
            self.assertTrue(command.undo(), "Undo should succeed")
        self.assert_output_shows_new_password()


if __name__ == "__main__":
    unittest.main()

"""
Integration tests for CodeEditorDialog workflow with command system.

Tests the real dialog, with hidden Qt windows: a change of the execution code goes through a
CodeChangeCommand, so that undo works. GUI code changes use direct method calls.
"""

import unittest
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication, QDialog

from pyflowgraph.commands.command_base import CompositeCommand
from pyflowgraph.commands.node_commands import CodeChangeCommand, GuiCodeChangeCommand
from pyflowgraph.ui.dialogs.code_editor_dialog import CodeEditorDialog

app = QApplication.instance() or QApplication([])


class TestCodeEditorDialogIntegration(unittest.TestCase):
    """Test CodeEditorDialog integration with command system."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock node
        self.mock_node = Mock()
        self.mock_node.title = "Test Node"

        # Create mock node graph with command history
        self.mock_node_graph = Mock()
        self.command_history = Mock()
        self.mock_node_graph.command_history = self.command_history

        # Test codes
        self.original_code = "def original(): return 'original'"
        self.original_gui_code = "# Original GUI"
        self.original_gui_logic = "# Original logic"
        self.new_code = "def modified(): return 'modified'"
        self.new_gui_code = "# Modified GUI"
        self.new_gui_logic = "# Modified logic"

    def make_dialog(self, node_graph=None):
        dialog = CodeEditorDialog(
            self.mock_node, node_graph or self.mock_node_graph,
            self.original_code, self.original_gui_code, self.original_gui_logic
        )
        self.addCleanup(dialog.deleteLater)
        return dialog

    def test_dialog_initialization_with_graph_reference(self):
        """Test dialog initializes with proper node and graph references."""
        dialog = self.make_dialog()

        self.assertIs(dialog.node, self.mock_node)
        self.assertIs(dialog.node_graph, self.mock_node_graph)
        self.assertEqual(dialog.original_code, self.original_code)
        self.assertEqual(dialog.code_editor.toPlainText(), self.original_code)
        self.assertEqual(dialog.gui_editor.toPlainText(), self.original_gui_code)
        self.assertEqual(dialog.gui_logic_editor.toPlainText(), self.original_gui_logic)

    def test_accept_creates_command_for_code_changes(self):
        """Test accept button creates CodeChangeCommand for execution code changes."""
        dialog = self.make_dialog()
        dialog.code_editor.setPlainText(self.new_code)

        dialog._handle_accept()

        # Verify command was pushed to history
        self.command_history.execute_command.assert_called_once()
        pushed_command = self.command_history.execute_command.call_args[0][0]
        self.assertIsInstance(pushed_command, CodeChangeCommand)
        self.assertEqual(pushed_command.old_code, self.original_code)
        self.assertEqual(pushed_command.new_code, self.new_code)
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)

    def test_cancel_does_not_affect_command_history(self):
        """Test cancel button does not create commands or affect history."""
        dialog = self.make_dialog()
        dialog.code_editor.setPlainText(self.new_code)

        dialog.reject()

        # Verify no commands were pushed
        self.command_history.execute_command.assert_not_called()
        self.assertEqual(dialog.result(), QDialog.DialogCode.Rejected)

    def test_no_changes_does_not_create_command(self):
        """Test that no command is created when code is unchanged."""
        dialog = self.make_dialog()

        dialog._handle_accept()

        # Verify no commands were pushed and nothing was set
        self.command_history.execute_command.assert_not_called()
        self.mock_node.set_gui_code.assert_not_called()
        self.mock_node.set_gui_get_values_code.assert_not_called()

    def test_fallback_when_no_command_history(self):
        """Test fallback behavior when node_graph has no command_history."""
        # Create node graph without command_history
        mock_node_graph_no_history = Mock()
        del mock_node_graph_no_history.command_history
        dialog = self.make_dialog(mock_node_graph_no_history)
        dialog.code_editor.setPlainText(self.new_code)

        # The dialog imports the command class when it needs it, so patch it where it lives
        with patch('pyflowgraph.commands.node_commands.CodeChangeCommand') as MockCommand:
            dialog._handle_accept()

        # Verify command was executed directly
        MockCommand.assert_called_once_with(
            mock_node_graph_no_history, self.mock_node, self.original_code, self.new_code)
        MockCommand.return_value.execute.assert_called_once()

    def test_sequential_code_changes(self):
        """Test multiple sequential code changes create separate commands."""
        # First change
        command1 = CodeChangeCommand(
            self.mock_node_graph, self.mock_node,
            self.original_code, self.new_code
        )

        # Second change
        command2 = CodeChangeCommand(
            self.mock_node_graph, self.mock_node,
            self.new_code, "def final(): return 'final'"
        )

        # Both commands should be independent
        self.assertNotEqual(command1.old_code, command2.old_code)
        self.assertEqual(command1.new_code, command2.old_code)

    def test_gui_code_changes_are_one_undo_command(self):
        """GUI code changes go to the undo history as one command."""
        dialog = self.make_dialog()
        dialog.gui_editor.setPlainText(self.new_gui_code)
        dialog.gui_logic_editor.setPlainText(self.new_gui_logic)

        dialog._handle_accept()

        self.command_history.execute_command.assert_called_once()
        command = self.command_history.execute_command.call_args[0][0]
        self.assertIsInstance(command, GuiCodeChangeCommand)
        self.assertEqual(command.new_gui_code, self.new_gui_code)
        self.assertEqual(command.new_logic_code, self.new_gui_logic)
        self.assertEqual(command.old_gui_code, self.original_gui_code)
        self.assertEqual(command.old_logic_code, self.original_gui_logic)

    def test_code_and_gui_changes_are_one_undo_step(self):
        """A dialog that changes the code and the GUI code makes one undo step."""
        dialog = self.make_dialog()
        dialog.code_editor.setPlainText(self.new_code)
        dialog.gui_editor.setPlainText(self.new_gui_code)

        dialog._handle_accept()

        self.command_history.execute_command.assert_called_once()
        command = self.command_history.execute_command.call_args[0][0]
        self.assertIsInstance(command, CompositeCommand)
        self.assertEqual([type(c) for c in command.commands],
                         [CodeChangeCommand, GuiCodeChangeCommand])


if __name__ == '__main__':
    unittest.main()

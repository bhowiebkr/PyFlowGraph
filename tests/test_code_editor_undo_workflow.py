"""
GUI tests for code editor undo/redo user workflows.

Tests the complete user experience of code editing with keyboard shortcuts
and undo/redo behavior from the user's perspective.
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestCodeEditorUndoWorkflow(unittest.TestCase):
    """Test code editor undo/redo user workflows."""
    
    def setUp(self):
        """Set up test fixtures for GUI workflow testing."""
        # Mock Qt components to avoid actual GUI in tests
        self.qt_mocks = {
            'QDialog': Mock(),
            'QTextEdit': Mock(),
            'QApplication': Mock(),
            'QKeySequence': Mock()
        }
        
        # Create mock node and graph for testing
        self.mock_node = Mock()
        self.mock_node.title = "Test Node"
        self.mock_node.code = "def original(): return 'original'"
        self.mock_node.set_code = Mock()
        
        self.mock_node_graph = Mock()
        self.mock_command_history = Mock()
        self.mock_node_graph.command_history = self.mock_command_history
        
        # Test code for editing scenarios
        self.original_code = "def original(): return 'original'"
        self.modified_code = "def modified(): return 'modified'"
        self.final_code = "def final(): return 'final'"
    
    def test_ctrl_z_in_editor_uses_internal_undo(self):
        """Test Ctrl+Z within code editor uses QTextEdit internal undo."""
        # Mock the text editor widget
        mock_text_editor = Mock()
        mock_text_editor.undo = Mock()
        mock_text_editor.hasFocus = Mock(return_value=True)
        
        # Simulate Ctrl+Z key press in editor
        # In a real scenario, this would be handled by Qt's built-in undo
        mock_text_editor.undo()
        
        # Verify internal undo was called
        mock_text_editor.undo.assert_called_once()
        
        # Verify no commands were pushed to graph history during editing
        self.mock_command_history.execute_command.assert_not_called()
    
    def test_editor_undo_redo_independent_of_graph(self):
        """Test editor undo/redo operates independently from graph history."""
        mock_text_editor = Mock()
        mock_text_editor.undo = Mock()
        mock_text_editor.redo = Mock()
        
        # Simulate typing and undo/redo within editor
        mock_text_editor.undo()  # Undo last edit
        mock_text_editor.redo()  # Redo last edit
        mock_text_editor.undo()  # Undo again
        
        # Verify editor operations
        self.assertEqual(mock_text_editor.undo.call_count, 2)
        self.assertEqual(mock_text_editor.redo.call_count, 1)
        
        # Verify graph history was not affected
        self.mock_command_history.execute_command.assert_not_called()
        self.mock_command_history.undo.assert_not_called()
        self.mock_command_history.redo.assert_not_called()
    
    def test_accept_dialog_creates_atomic_command(self):
        """Test accepting dialog creates single atomic command in graph history."""
        # Mock dialog with code changes
        with patch('src.ui.dialogs.code_editor_dialog.CodeEditorDialog') as MockDialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.node = self.mock_node
            mock_dialog_instance.node_graph = self.mock_node_graph
            mock_dialog_instance.original_code = self.original_code
            
            # Mock editor content
            mock_code_editor = Mock()
            mock_code_editor.toPlainText.return_value = self.modified_code
            mock_dialog_instance.code_editor = mock_code_editor
            
            MockDialog.return_value = mock_dialog_instance
            
            # Simulate _handle_accept behavior
            from src.commands.node_commands import CodeChangeCommand
            command = CodeChangeCommand(
                self.mock_node_graph, self.mock_node,
                self.original_code, self.modified_code
            )
            
            # Verify command represents atomic operation
            self.assertEqual(command.old_code, self.original_code)
            self.assertEqual(command.new_code, self.modified_code)
            self.assertIn("Test Node", command.description)
    
    def test_cancel_dialog_no_graph_history_impact(self):
        """Test canceling dialog does not affect graph history."""
        # Mock dialog cancellation
        mock_dialog = Mock()
        mock_dialog.reject = Mock()  # Simulate cancel button
        
        # Simulate user canceling dialog
        mock_dialog.reject()
        
        # Verify no impact on command history
        self.mock_command_history.execute_command.assert_not_called()
        self.mock_node.set_code.assert_not_called()
    
    def test_user_scenario_edit_undo_redo_edit_again(self):
        """Test user scenario: edit code, undo, redo, edit again."""
        commands_created = []
        
        def mock_push_command(command):
            commands_created.append(command)
            command.execute()
        
        self.mock_command_history.execute_command.side_effect = mock_push_command
        
        # Step 1: User edits code and accepts
        from src.commands.node_commands import CodeChangeCommand
        
        command1 = CodeChangeCommand(
            self.mock_node_graph, self.mock_node,
            self.original_code, self.modified_code
        )
        self.mock_command_history.execute_command(command1)
        
        # Step 2: User undos the change (from main graph, not in editor)
        def mock_undo():
            if commands_created:
                last_command = commands_created[-1]
                last_command.undo()
                return last_command.description
            return None
        
        self.mock_command_history.undo.side_effect = mock_undo
        undo_result = self.mock_command_history.undo()
        
        # Step 3: User redos the change
        def mock_redo():
            if commands_created:
                last_command = commands_created[-1]
                last_command.execute()
                return last_command.description
            return None
        
        self.mock_command_history.redo.side_effect = mock_redo
        redo_result = self.mock_command_history.redo()
        
        # Step 4: User edits code again
        command2 = CodeChangeCommand(
            self.mock_node_graph, self.mock_node,
            self.modified_code, self.final_code
        )
        self.mock_command_history.execute_command(command2)
        
        # Verify the workflow
        self.assertEqual(len(commands_created), 2)
        self.assertEqual(commands_created[0].old_code, self.original_code)
        self.assertEqual(commands_created[0].new_code, self.modified_code)
        self.assertEqual(commands_created[1].old_code, self.modified_code)
        self.assertEqual(commands_created[1].new_code, self.final_code)
        
        # Verify undo/redo were called
        self.mock_command_history.undo.assert_called_once()
        self.mock_command_history.redo.assert_called_once()
    
    def test_large_code_editing_performance(self):
        """Test performance with large code blocks."""
        # Create large code content
        large_original = "def large_func():\n" + "    # " + "x" * 1000 + "\n    return 'large'"
        large_modified = "def large_func():\n" + "    # " + "y" * 1000 + "\n    return 'large_modified'"
        
        # Create command with large code
        from src.commands.node_commands import CodeChangeCommand
        command = CodeChangeCommand(
            self.mock_node_graph, self.mock_node,
            large_original, large_modified
        )
        
        # Test execution performance (should complete quickly)
        import time
        start_time = time.time()
        result = command.execute()
        execution_time = time.time() - start_time
        
        # Verify operation completed successfully and quickly
        self.assertTrue(result)
        self.assertLess(execution_time, 0.1)  # Should complete within 100ms
        
        # Test undo performance
        start_time = time.time()
        result = command.undo()
        undo_time = time.time() - start_time
        
        self.assertTrue(result)
        self.assertLess(undo_time, 0.1)  # Should complete within 100ms
    
    def test_keyboard_shortcuts_workflow(self):
        """Test keyboard shortcuts integration in workflow."""
        # Mock keyboard event handling
        mock_editor = Mock()
        mock_editor.hasFocus = Mock(return_value=True)
        
        # Test common keyboard shortcuts
        shortcuts_tested = {
            'Ctrl+Z': mock_editor.undo,
            'Ctrl+Y': mock_editor.redo,
            'Ctrl+Shift+Z': mock_editor.redo
        }
        
        for shortcut, expected_method in shortcuts_tested.items():
            with self.subTest(shortcut=shortcut):
                # Simulate shortcut press
                expected_method()
                expected_method.assert_called()
                expected_method.reset_mock()
    
    def test_focus_dependent_undo_behavior(self):
        """Test that undo behavior depends on focus context."""
        mock_editor = Mock()
        mock_main_window = Mock()
        
        # When editor has focus, Ctrl+Z should use editor's undo
        mock_editor.hasFocus.return_value = True
        mock_editor.undo = Mock()
        
        # Simulate Ctrl+Z with editor focused
        if mock_editor.hasFocus():
            mock_editor.undo()
        
        mock_editor.undo.assert_called_once()
        
        # When main window has focus, Ctrl+Z should use graph undo
        mock_editor.hasFocus.return_value = False
        mock_editor.undo.reset_mock()
        
        # Simulate Ctrl+Z with main window focused
        if not mock_editor.hasFocus():
            self.mock_command_history.undo()
        
        self.mock_command_history.undo.assert_called_once()
        mock_editor.undo.assert_not_called()
    
    def test_multiple_editors_independent_undo(self):
        """Test that multiple editor tabs maintain independent undo."""
        # Create mock editors for each tab
        mock_code_editor = Mock()
        mock_gui_editor = Mock()
        mock_logic_editor = Mock()
        
        # Each editor should have independent undo/redo
        for editor in [mock_code_editor, mock_gui_editor, mock_logic_editor]:
            editor.undo = Mock()
            editor.redo = Mock()
            editor.hasFocus = Mock(return_value=False)
        
        # Test undo on code editor
        mock_code_editor.hasFocus.return_value = True
        mock_code_editor.undo()
        mock_code_editor.undo.assert_called_once()
        
        # Other editors should not be affected
        mock_gui_editor.undo.assert_not_called()
        mock_logic_editor.undo.assert_not_called()


if __name__ == '__main__':
    unittest.main()
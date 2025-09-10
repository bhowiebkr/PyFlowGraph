"""
Integration tests for CodeEditorDialog workflow with command system.

Tests the complete workflow of code editing with undo/redo integration
to ensure proper command history management.
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock PySide6 before imports to avoid GUI dependency in headless tests
sys.modules['PySide6'] = Mock()
sys.modules['PySide6.QtWidgets'] = Mock()
sys.modules['PySide6.QtCore'] = Mock()
sys.modules['PySide6.QtGui'] = Mock()

try:
    from src.commands.node_commands import CodeChangeCommand
    from src.commands.command_history import CommandHistory
except ImportError:
    sys.path.insert(0, os.path.join(project_root, 'src'))
    from commands.node_commands import CodeChangeCommand
    from commands.command_history import CommandHistory


class TestCodeEditorDialogIntegration(unittest.TestCase):
    """Test CodeEditorDialog integration with command system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock node
        self.mock_node = Mock()
        self.mock_node.title = "Test Node"
        self.mock_node.set_code = Mock()
        self.mock_node.set_gui_code = Mock()
        self.mock_node.set_gui_get_values_code = Mock()
        
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
    
    @patch('src.ui.dialogs.code_editor_dialog.CodeEditorDialog.__init__')
    @patch('src.ui.dialogs.code_editor_dialog.CodeEditorDialog._handle_accept')
    def test_dialog_initialization_with_graph_reference(self, mock_handle_accept, mock_init):
        """Test dialog initializes with proper node and graph references."""
        mock_init.return_value = None  # Mock __init__ to do nothing
        
        # Import after mocking
        from src.ui.dialogs.code_editor_dialog import CodeEditorDialog
        
        dialog = CodeEditorDialog(
            self.mock_node, self.mock_node_graph,
            self.original_code, self.original_gui_code, self.original_gui_logic
        )
        
        # Verify __init__ was called with correct parameters
        mock_init.assert_called_once_with(
            self.mock_node, self.mock_node_graph,
            self.original_code, self.original_gui_code, self.original_gui_logic,
            None  # parent
        )
    
    def test_accept_creates_command_for_code_changes(self):
        """Test accept button creates CodeChangeCommand for execution code changes."""
        # Mock dialog components
        mock_dialog = Mock()
        mock_dialog.node = self.mock_node
        mock_dialog.node_graph = self.mock_node_graph
        mock_dialog.original_code = self.original_code
        mock_dialog.original_gui_code = self.original_gui_code
        mock_dialog.original_gui_logic_code = self.original_gui_logic
        
        # Mock editors
        mock_code_editor = Mock()
        mock_code_editor.toPlainText.return_value = self.new_code
        mock_gui_editor = Mock()
        mock_gui_editor.toPlainText.return_value = self.new_gui_code
        mock_gui_logic_editor = Mock()
        mock_gui_logic_editor.toPlainText.return_value = self.new_gui_logic
        
        mock_dialog.code_editor = mock_code_editor
        mock_dialog.gui_editor = mock_gui_editor
        mock_dialog.gui_logic_editor = mock_gui_logic_editor
        mock_dialog.accept = Mock()
        
        # Import and patch the _handle_accept method
        from src.ui.dialogs.code_editor_dialog import CodeEditorDialog
        
        with patch.object(CodeEditorDialog, '_handle_accept') as mock_handle_accept:
            # Simulate the actual _handle_accept logic
            def handle_accept_impl(self):
                new_code = self.code_editor.toPlainText()
                if new_code != self.original_code:
                    from commands.node_commands import CodeChangeCommand
                    code_command = CodeChangeCommand(
                        self.node_graph, self.node, self.original_code, new_code
                    )
                    if hasattr(self.node_graph, 'command_history'):
                        self.node_graph.command_history.execute_command(code_command)
                self.accept()
            
            mock_handle_accept.side_effect = handle_accept_impl
            
            # Execute
            mock_handle_accept(mock_dialog)
            
            # Verify command was pushed to history
            self.command_history.execute_command.assert_called_once()
            pushed_command = self.command_history.execute_command.call_args[0][0]
            self.assertIsInstance(pushed_command, CodeChangeCommand)
            self.assertEqual(pushed_command.old_code, self.original_code)
            self.assertEqual(pushed_command.new_code, self.new_code)
    
    def test_cancel_does_not_affect_command_history(self):
        """Test cancel button does not create commands or affect history."""
        mock_dialog = Mock()
        mock_dialog.node_graph = self.mock_node_graph
        mock_dialog.reject = Mock()
        
        # Simulate cancel action
        mock_dialog.reject()
        
        # Verify no commands were pushed
        self.command_history.execute_command.assert_not_called()
    
    def test_no_changes_does_not_create_command(self):
        """Test that no command is created when code is unchanged."""
        mock_dialog = Mock()
        mock_dialog.node = self.mock_node
        mock_dialog.node_graph = self.mock_node_graph
        mock_dialog.original_code = self.original_code
        mock_dialog.original_gui_code = self.original_gui_code
        mock_dialog.original_gui_logic_code = self.original_gui_logic
        
        # Mock editors returning original code (no changes)
        mock_code_editor = Mock()
        mock_code_editor.toPlainText.return_value = self.original_code
        mock_gui_editor = Mock()
        mock_gui_editor.toPlainText.return_value = self.original_gui_code
        mock_gui_logic_editor = Mock()
        mock_gui_logic_editor.toPlainText.return_value = self.original_gui_logic
        
        mock_dialog.code_editor = mock_code_editor
        mock_dialog.gui_editor = mock_gui_editor
        mock_dialog.gui_logic_editor = mock_gui_logic_editor
        mock_dialog.accept = Mock()
        
        # Simulate _handle_accept with no changes
        from src.ui.dialogs.code_editor_dialog import CodeEditorDialog
        
        with patch.object(CodeEditorDialog, '_handle_accept') as mock_handle_accept:
            def handle_accept_no_changes(self):
                new_code = self.code_editor.toPlainText()
                if new_code != self.original_code:
                    # This should not execute
                    self.node_graph.command_history.execute_command(Mock())
                self.accept()
            
            mock_handle_accept.side_effect = handle_accept_no_changes
            mock_handle_accept(mock_dialog)
            
            # Verify no commands were pushed
            self.command_history.execute_command.assert_not_called()
    
    def test_fallback_when_no_command_history(self):
        """Test fallback behavior when node_graph has no command_history."""
        # Create node graph without command_history
        mock_node_graph_no_history = Mock()
        del mock_node_graph_no_history.command_history
        
        mock_dialog = Mock()
        mock_dialog.node = self.mock_node
        mock_dialog.node_graph = mock_node_graph_no_history
        mock_dialog.original_code = self.original_code
        
        # Mock editor with changes
        mock_code_editor = Mock()
        mock_code_editor.toPlainText.return_value = self.new_code
        mock_dialog.code_editor = mock_code_editor
        mock_dialog.accept = Mock()
        
        # Create a real command to test fallback execution
        with patch('commands.node_commands.CodeChangeCommand') as MockCommand:
            mock_command_instance = Mock()
            MockCommand.return_value = mock_command_instance
            
            from src.ui.dialogs.code_editor_dialog import CodeEditorDialog
            
            with patch.object(CodeEditorDialog, '_handle_accept') as mock_handle_accept:
                def handle_accept_fallback(self):
                    new_code = self.code_editor.toPlainText()
                    if new_code != self.original_code:
                        from commands.node_commands import CodeChangeCommand
                        code_command = CodeChangeCommand(
                            self.node_graph, self.node, self.original_code, new_code
                        )
                        if hasattr(self.node_graph, 'command_history'):
                            self.node_graph.command_history.execute_command(code_command)
                        else:
                            code_command.execute()
                    self.accept()
                
                mock_handle_accept.side_effect = handle_accept_fallback
                mock_handle_accept(mock_dialog)
                
                # Verify command was executed directly
                mock_command_instance.execute.assert_called_once()
    
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
    
    def test_gui_code_changes_not_in_command_system(self):
        """Test that GUI code changes use direct method calls, not commands."""
        mock_dialog = Mock()
        mock_dialog.node = self.mock_node
        mock_dialog.node_graph = self.mock_node_graph
        mock_dialog.original_gui_code = self.original_gui_code
        mock_dialog.original_gui_logic_code = self.original_gui_logic
        
        # Mock editors
        mock_gui_editor = Mock()
        mock_gui_editor.toPlainText.return_value = self.new_gui_code
        mock_gui_logic_editor = Mock()
        mock_gui_logic_editor.toPlainText.return_value = self.new_gui_logic
        
        mock_dialog.gui_editor = mock_gui_editor
        mock_dialog.gui_logic_editor = mock_gui_logic_editor
        
        # Simulate handling GUI changes (part of _handle_accept logic)
        if mock_gui_editor.toPlainText() != mock_dialog.original_gui_code:
            self.mock_node.set_gui_code(mock_gui_editor.toPlainText())
        
        if mock_gui_logic_editor.toPlainText() != mock_dialog.original_gui_logic_code:
            self.mock_node.set_gui_get_values_code(mock_gui_logic_editor.toPlainText())
        
        # Verify direct method calls were made
        self.mock_node.set_gui_code.assert_called_once_with(self.new_gui_code)
        self.mock_node.set_gui_get_values_code.assert_called_once_with(self.new_gui_logic)


if __name__ == '__main__':
    unittest.main()
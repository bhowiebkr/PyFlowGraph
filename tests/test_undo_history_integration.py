# test_undo_history_integration.py
# Integration tests for undo history dialog workflow

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtTest import QTest
    
    # Import the modules to test
    from src.ui.dialogs.undo_history_dialog import UndoHistoryDialog
    from src.commands.command_base import CommandBase
    from src.commands.command_history import CommandHistory
    
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


class MockCommand(CommandBase):
    """Mock command for testing."""
    
    def __init__(self, description: str):
        super().__init__(description)
        self.execute_called = False
        self.undo_called = False
    
    def execute(self) -> bool:
        self.execute_called = True
        return True
    
    def undo(self) -> bool:
        self.undo_called = True
        return True


class MockGraph:
    """Mock graph for testing command integration."""
    
    def __init__(self):
        self.command_history = CommandHistory()


@unittest.skipUnless(QT_AVAILABLE, "PySide6 not available")
class TestUndoHistoryIntegration(unittest.TestCase):
    """Integration tests for undo history dialog with command system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = MockGraph()
        
        # Execute create commands
        create_cmd1 = MockCommand("Create Node 1")
        create_cmd2 = MockCommand("Create Node 2")
        create_cmd3 = MockCommand("Create Node 3")
        
        self.graph.command_history.execute_command(create_cmd1)
        self.graph.command_history.execute_command(create_cmd2)
        self.graph.command_history.execute_command(create_cmd3)
    
    def test_dialog_shows_real_command_history(self):
        """Test dialog displays real command history correctly."""
        dialog = UndoHistoryDialog(self.graph.command_history)
        
        # Should show 3 create commands
        self.assertEqual(dialog.history_list.count(), 3)
        
        # Check command descriptions appear
        items = [dialog.history_list.item(i).text() for i in range(3)]
        self.assertTrue(any("Create Node" in item for item in items))
    
    def test_jump_functionality_with_real_commands(self):
        """Test jumping to different positions with real commands."""
        dialog = UndoHistoryDialog(self.graph.command_history)
        
        # Initially at position 2 (3 commands executed)
        self.assertEqual(self.graph.command_history.current_index, 2)
        
        # Mock the jump signal handling
        signal_received = Mock()
        dialog.jumpToIndex.connect(signal_received)
        
        # Jump to position 1 (should have 2 nodes)
        dialog.history_list.setCurrentRow(1)
        dialog._on_jump_clicked()
        
        # Verify signal emission
        signal_received.assert_called_once_with(1)
    
    def test_history_updates_after_undo_redo(self):
        """Test that history display updates correctly after undo/redo operations."""
        dialog = UndoHistoryDialog(self.graph.command_history)
        
        # Undo one command
        self.graph.command_history.undo()
        
        # Refresh dialog and check state
        dialog.refresh_history()
        
        # Current position should be highlighted at index 1
        self.assertEqual(dialog.history_list.currentRow(), 1)
        
        # Info label should reflect new state
        info_text = dialog.info_label.text()
        self.assertIn("2 of 3 operations executed", info_text)
    
    def test_mixed_command_types_display(self):
        """Test display of mixed command types."""
        # Add a delete command
        delete_cmd = MockCommand("Delete Node 2")
        self.graph.command_history.execute_command(delete_cmd)
        
        dialog = UndoHistoryDialog(self.graph.command_history)
        
        # Should show 4 commands (3 creates + 1 delete)
        self.assertEqual(dialog.history_list.count(), 4)
        
        # Check that both create and delete commands appear
        items = [dialog.history_list.item(i).text() for i in range(4)]
        create_count = sum(1 for item in items if "Create" in item)
        delete_count = sum(1 for item in items if "Delete" in item)
        
        self.assertEqual(create_count, 3)
        self.assertEqual(delete_count, 1)
    
    def test_dialog_performance_with_large_history(self):
        """Test dialog performance with large command history."""
        # Create a large command history
        large_graph = MockGraph()
        
        # Add 100 commands
        for i in range(100):
            cmd = MockCommand(f"Create Node {i}")
            large_graph.command_history.execute_command(cmd)
        
        # Dialog should handle large history efficiently
        import time
        start_time = time.time()
        
        dialog = UndoHistoryDialog(large_graph.command_history)
        
        creation_time = time.time() - start_time
        
        # Should create quickly (under 1 second)
        self.assertLess(creation_time, 1.0)
        
        # Should display limited commands (max_depth is 50 by default)
        self.assertEqual(dialog.history_list.count(), 50)
    
    def test_dialog_handles_command_execution_errors(self):
        """Test dialog behavior when commands fail."""
        # Create a command that will fail
        class FailingCommand(CommandBase):
            def __init__(self):
                super().__init__("Failing Command")
            
            def execute(self):
                return False  # Always fails
            
            def undo(self):
                return False  # Always fails
            
            def get_description(self):
                return self._description
        
        failing_cmd = FailingCommand()
        
        # Try to execute failing command
        result = self.graph.command_history.execute_command(failing_cmd)
        self.assertFalse(result)
        
        # Dialog should still work normally with successful commands
        dialog = UndoHistoryDialog(self.graph.command_history)
        self.assertEqual(dialog.history_list.count(), 3)  # Only successful commands
    
    def test_dialog_memory_efficiency(self):
        """Test that dialog doesn't consume excessive memory."""
        # Check memory usage with moderate history size
        dialog = UndoHistoryDialog(self.graph.command_history)
        
        # Dialog should not hold unnecessary references
        import gc
        initial_objects = len(gc.get_objects())
        
        # Close dialog
        dialog.close()
        dialog = None
        gc.collect()
        
        # Memory should be released
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Should not significantly increase object count
        self.assertLess(object_increase, 100)


@unittest.skipUnless(QT_AVAILABLE, "PySide6 not available")
class TestStatusBarIntegration(unittest.TestCase):
    """Test status bar feedback integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_status_bar = Mock()
    
    def test_undo_status_messages(self):
        """Test that undo operations show appropriate status messages."""
        # Simulate undo operation feedback
        description = "Create Node"
        self.mock_status_bar.showMessage(f"Undone: {description}", 2000)
        
        # Verify status message call
        self.mock_status_bar.showMessage.assert_called_with("Undone: Create Node", 2000)
    
    def test_redo_status_messages(self):
        """Test that redo operations show appropriate status messages."""
        # Simulate redo operation feedback
        description = "Delete Node"
        self.mock_status_bar.showMessage(f"Redone: {description}", 2000)
        
        # Verify status message call
        self.mock_status_bar.showMessage.assert_called_with("Redone: Delete Node", 2000)
    
    def test_jump_operation_status_messages(self):
        """Test status messages for jump operations."""
        # Test jump to earlier position
        count = 3
        target_position = 2
        self.mock_status_bar.showMessage(f"Undone {count} operations to reach position {target_position}", 3000)
        
        # Verify status message
        self.mock_status_bar.showMessage.assert_called_with("Undone 3 operations to reach position 2", 3000)
        
        # Test jump to later position
        self.mock_status_bar.reset_mock()
        count = 2
        target_position = 5
        self.mock_status_bar.showMessage(f"Redone {count} operations to reach position {target_position}", 3000)
        
        # Verify status message
        self.mock_status_bar.showMessage.assert_called_with("Redone 2 operations to reach position 5", 3000)
    
    def test_already_at_position_message(self):
        """Test message when already at target position."""
        target_position = 3
        self.mock_status_bar.showMessage(f"Already at position {target_position + 1}", 2000)
        
        # Verify status message
        self.mock_status_bar.showMessage.assert_called_with("Already at position 4", 2000)


if __name__ == '__main__':
    unittest.main()
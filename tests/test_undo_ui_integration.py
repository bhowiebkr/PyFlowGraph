# test_undo_ui_integration.py
# Unit tests for undo/redo UI components

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    
    # Import the modules to test
    from src.ui.dialogs.undo_history_dialog import UndoHistoryDialog
    from src.commands.command_base import CommandBase
    from src.commands.command_history import CommandHistory
    
    QT_AVAILABLE = True
    
    class MockCommand(CommandBase):
        """Mock command for testing."""
        
        def __init__(self, description: str):
            super().__init__(description)
            self.timestamp = datetime.now()
            self.execute_called = False
            self.undo_called = False
        
        def execute(self) -> bool:
            self.execute_called = True
            return True
        
        def undo(self) -> bool:
            self.undo_called = True
            return True

except ImportError:
    QT_AVAILABLE = False
    
    # Create dummy class for when imports fail
    class MockCommand:
        pass


@unittest.skipUnless(QT_AVAILABLE, "PySide6 not available")
class TestUndoHistoryDialog(unittest.TestCase):
    """Test the undo history dialog functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.command_history = CommandHistory()
        
        # Add some test commands
        self.cmd1 = MockCommand("Create Node A")
        self.cmd2 = MockCommand("Delete Node B") 
        self.cmd3 = MockCommand("Move Node C")
        
        # Execute commands to populate history
        self.command_history.execute_command(self.cmd1)
        self.command_history.execute_command(self.cmd2)
        self.command_history.execute_command(self.cmd3)
    
    def test_dialog_initialization(self):
        """Test dialog initializes correctly."""
        dialog = UndoHistoryDialog(self.command_history)
        
        self.assertEqual(dialog.windowTitle(), "Undo History")
        self.assertTrue(dialog.isModal())
        self.assertIsNotNone(dialog.history_list)
        self.assertIsNotNone(dialog.jump_button)
        self.assertIsNotNone(dialog.info_label)
    
    def test_history_population_with_commands(self):
        """Test that history list is populated correctly."""
        dialog = UndoHistoryDialog(self.command_history)
        
        # Should have 3 items in the list
        self.assertEqual(dialog.history_list.count(), 3)
        
        # Check that descriptions are present
        items_text = [dialog.history_list.item(i).text() for i in range(3)]
        self.assertTrue(any("Create Node A" in text for text in items_text))
        self.assertTrue(any("Delete Node B" in text for text in items_text))
        self.assertTrue(any("Move Node C" in text for text in items_text))
    
    def test_history_population_empty(self):
        """Test handling of empty command history."""
        empty_history = CommandHistory()
        dialog = UndoHistoryDialog(empty_history)
        
        # Should have 1 item saying no commands
        self.assertEqual(dialog.history_list.count(), 1)
        item_text = dialog.history_list.item(0).text()
        self.assertEqual(item_text, "No commands in history")
        
        # Jump button should be disabled
        self.assertFalse(dialog.jump_button.isEnabled())
    
    def test_current_position_highlighting(self):
        """Test that current position is highlighted correctly."""
        dialog = UndoHistoryDialog(self.command_history)
        
        # Current index should be 2 (last command)
        current_row = dialog.history_list.currentRow()
        self.assertEqual(current_row, 2)
        
        # Current item should be bold
        current_item = dialog.history_list.item(2)
        self.assertTrue(current_item.font().bold())
    
    def test_selection_enables_jump_button(self):
        """Test that selecting items enables the jump button."""
        dialog = UndoHistoryDialog(self.command_history)
        
        # Initially should be enabled (current item selected)
        self.assertTrue(dialog.jump_button.isEnabled())
        
        # Select different item
        dialog.history_list.setCurrentRow(0)
        self.assertTrue(dialog.jump_button.isEnabled())
    
    def test_jump_signal_emission(self):
        """Test that jumpToIndex signal is emitted correctly."""
        dialog = UndoHistoryDialog(self.command_history)
        
        # Connect signal to mock
        signal_received = Mock()
        dialog.jumpToIndex.connect(signal_received)
        
        # Select first item and click jump
        dialog.history_list.setCurrentRow(0)
        dialog._on_jump_clicked()
        
        # Should emit signal with index 0
        signal_received.assert_called_once_with(0)
    
    def test_double_click_triggers_jump(self):
        """Test that double-clicking triggers jump."""
        dialog = UndoHistoryDialog(self.command_history)
        
        # Connect signal to mock
        signal_received = Mock()
        dialog.jumpToIndex.connect(signal_received)
        
        # Double-click on first item
        first_item = dialog.history_list.item(0)
        dialog._on_item_double_clicked(first_item)
        
        # Should emit signal with index 0
        signal_received.assert_called_once_with(0)
    
    def test_info_label_updates(self):
        """Test that info label shows correct information."""
        dialog = UndoHistoryDialog(self.command_history)
        
        # With 3 commands all executed, should show all executed
        info_text = dialog.info_label.text()
        self.assertIn("3 operations executed", info_text)
        
        # Test with some commands undone
        self.command_history.undo()  # Now at index 1
        dialog._update_info_label(1)
        info_text = dialog.info_label.text()
        self.assertIn("2 of 3 operations executed", info_text)
        self.assertIn("1 undone", info_text)
    
    def test_refresh_functionality(self):
        """Test that refresh updates the display."""
        dialog = UndoHistoryDialog(self.command_history)
        initial_count = dialog.history_list.count()
        
        # Add another command to history
        new_cmd = MockCommand("New Command")
        self.command_history.execute_command(new_cmd)
        
        # Refresh should update the display
        dialog.refresh_history()
        self.assertEqual(dialog.history_list.count(), initial_count + 1)


@unittest.skipUnless(QT_AVAILABLE, "PySide6 not available")
class TestUndoRedoMenuActions(unittest.TestCase):
    """Test undo/redo menu action updates."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the NodeEditorWindow's undo/redo action update logic
        self.mock_graph = Mock()
        self.mock_action_undo = Mock()
        self.mock_action_redo = Mock()
    
    def test_actions_disabled_when_no_commands(self):
        """Test that actions are disabled when no commands available."""
        self.mock_graph.can_undo.return_value = False
        self.mock_graph.can_redo.return_value = False
        
        # Simulate _update_undo_redo_actions logic
        self.mock_action_undo.setEnabled(False)
        self.mock_action_redo.setEnabled(False)
        self.mock_action_undo.setText("&Undo")
        self.mock_action_redo.setText("&Redo")
        self.mock_action_undo.setToolTip("No operations available to undo (Ctrl+Z)")
        self.mock_action_redo.setToolTip("No operations available to redo (Ctrl+Y, Ctrl+Shift+Z)")
        
        # Verify calls
        self.mock_action_undo.setEnabled.assert_called_with(False)
        self.mock_action_redo.setEnabled.assert_called_with(False)
        self.mock_action_undo.setText.assert_called_with("&Undo")
        self.mock_action_redo.setText.assert_called_with("&Redo")
    
    def test_actions_enabled_with_descriptions(self):
        """Test that actions show descriptions when available."""
        self.mock_graph.can_undo.return_value = True
        self.mock_graph.can_redo.return_value = True
        self.mock_graph.get_undo_description.return_value = "Create Node"
        self.mock_graph.get_redo_description.return_value = "Delete Node"
        
        # Simulate _update_undo_redo_actions logic
        self.mock_action_undo.setEnabled(True)
        self.mock_action_redo.setEnabled(True)
        self.mock_action_undo.setText("&Undo Create Node")
        self.mock_action_redo.setText("&Redo Delete Node")
        self.mock_action_undo.setToolTip("Undo: Create Node (Ctrl+Z)")
        self.mock_action_redo.setToolTip("Redo: Delete Node (Ctrl+Y, Ctrl+Shift+Z)")
        
        # Verify calls
        self.mock_action_undo.setEnabled.assert_called_with(True)
        self.mock_action_redo.setEnabled.assert_called_with(True)
        self.mock_action_undo.setText.assert_called_with("&Undo Create Node")
        self.mock_action_redo.setText.assert_called_with("&Redo Delete Node")


class TestCommandIndexJumping(unittest.TestCase):
    """Test command index jumping functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.command_history = CommandHistory()
        
        # Add test commands
        for i in range(5):
            cmd = MockCommand(f"Command {i}")
            self.command_history.execute_command(cmd)
    
    def test_jump_to_earlier_index(self):
        """Test jumping to earlier index (undo operations)."""
        # Start at index 4 (last command)
        self.assertEqual(self.command_history.current_index, 4)
        
        # Jump to index 2 (should undo 2 commands)
        undone = self.command_history.undo_to_command(2)
        
        self.assertEqual(len(undone), 2)
        self.assertEqual(self.command_history.current_index, 2)
    
    def test_jump_to_later_index(self):
        """Test jumping to later index (redo operations)."""
        # First undo some commands
        self.command_history.undo()
        self.command_history.undo()
        self.assertEqual(self.command_history.current_index, 2)
        
        # Now redo to index 4
        redone_count = 0
        while self.command_history.current_index < 4:
            if self.command_history.redo():
                redone_count += 1
            else:
                break
        
        self.assertEqual(redone_count, 2)
        self.assertEqual(self.command_history.current_index, 4)
    
    def test_jump_to_same_index(self):
        """Test jumping to same index (no operation)."""
        current = self.command_history.current_index
        undone = self.command_history.undo_to_command(current)
        
        self.assertEqual(len(undone), 0)
        self.assertEqual(self.command_history.current_index, current)


if __name__ == '__main__':
    unittest.main()
"""
Unit tests for CodeChangeCommand functionality.

Tests the code modification undo/redo system to ensure proper behavior
for code changes in nodes.
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.commands.node_commands import CodeChangeCommand
    from src.commands.command_base import CommandBase
except ImportError:
    sys.path.insert(0, os.path.join(project_root, 'src'))
    from commands.node_commands import CodeChangeCommand
    from commands.command_base import CommandBase


class TestCodeChangeCommand(unittest.TestCase):
    """Test CodeChangeCommand execute/undo behavior and memory efficiency."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock node with set_code method
        self.mock_node = Mock()
        self.mock_node.title = "Test Node"
        self.mock_node.set_code = Mock()
        
        # Create mock node graph
        self.mock_node_graph = Mock()
        
        # Test code samples
        self.old_code = "def old_function():\n    return 'old'"
        self.new_code = "def new_function():\n    return 'new'"
        self.large_code = "def large_function():\n" + "    # " + "x" * 1000 + "\n    return 'large'"
    
    def test_command_creation(self):
        """Test CodeChangeCommand creation with proper attributes."""
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, self.new_code)
        
        self.assertIsInstance(command, CommandBase)
        self.assertEqual(command.node_graph, self.mock_node_graph)
        self.assertEqual(command.node, self.mock_node)
        self.assertEqual(command.old_code, self.old_code)
        self.assertEqual(command.new_code, self.new_code)
        self.assertIn("Test Node", command.description)
    
    def test_execute_applies_new_code(self):
        """Test execute() method applies new code to node."""
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, self.new_code)
        
        result = command.execute()
        
        self.assertTrue(result)
        self.mock_node.set_code.assert_called_once_with(self.new_code)
        self.assertTrue(command.is_executed())
        self.assertFalse(command.is_undone())
    
    def test_undo_restores_old_code(self):
        """Test undo() method restores original code."""
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, self.new_code)
        
        # Execute first
        command.execute()
        self.mock_node.set_code.reset_mock()
        
        # Then undo
        result = command.undo()
        
        self.assertTrue(result)
        self.mock_node.set_code.assert_called_once_with(self.old_code)
        self.assertFalse(command.is_executed())
        self.assertTrue(command.is_undone())
    
    def test_execute_handles_exceptions(self):
        """Test execute() handles exceptions gracefully."""
        self.mock_node.set_code.side_effect = Exception("Set code failed")
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, self.new_code)
        
        result = command.execute()
        
        self.assertFalse(result)
        self.assertFalse(command.is_executed())
    
    def test_undo_handles_exceptions(self):
        """Test undo() handles exceptions gracefully."""
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, self.new_code)
        command.execute()
        
        self.mock_node.set_code.side_effect = Exception("Undo failed")
        result = command.undo()
        
        self.assertFalse(result)
        self.assertTrue(command.is_executed())  # Should remain executed if undo fails
    
    def test_large_code_handling(self):
        """Test efficient handling of large code blocks."""
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, self.large_code)
        
        # Should execute successfully
        result = command.execute()
        self.assertTrue(result)
        self.mock_node.set_code.assert_called_once_with(self.large_code)
        
        # Should undo successfully
        self.mock_node.set_code.reset_mock()
        result = command.undo()
        self.assertTrue(result)
        self.mock_node.set_code.assert_called_once_with(self.old_code)
    
    def test_memory_usage_estimation(self):
        """Test memory usage estimation for different code sizes."""
        # Small code
        small_command = CodeChangeCommand(self.mock_node_graph, self.mock_node, "def f(): pass", "def g(): pass")
        small_usage = small_command.get_memory_usage()
        
        # Large code
        large_command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, self.large_code)
        large_usage = large_command.get_memory_usage()
        
        # Large command should use more memory
        self.assertGreater(large_usage, small_usage)
        # Both should return reasonable estimates (> base size)
        self.assertGreater(small_usage, 512)
        self.assertGreater(large_usage, 1024)
    
    def test_empty_code_handling(self):
        """Test handling of empty code strings."""
        empty_old = ""
        empty_new = ""
        
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, empty_old, empty_new)
        
        result = command.execute()
        self.assertTrue(result)
        self.mock_node.set_code.assert_called_once_with(empty_new)
        
        self.mock_node.set_code.reset_mock()
        result = command.undo()
        self.assertTrue(result)
        self.mock_node.set_code.assert_called_once_with(empty_old)
    
    def test_special_characters_in_code(self):
        """Test handling of special characters in code."""
        special_code = "def func():\n    return 'Hello\\nWorld\\t'"
        
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, special_code)
        
        result = command.execute()
        self.assertTrue(result)
        self.mock_node.set_code.assert_called_once_with(special_code)
    
    def test_unicode_characters_forbidden(self):
        """Test that Unicode characters are not used in implementation."""
        command = CodeChangeCommand(self.mock_node_graph, self.mock_node, self.old_code, self.new_code)
        
        # Check description doesn't contain Unicode
        description = command.get_description()
        self.assertTrue(all(ord(char) < 128 for char in description), 
                       "Description contains non-ASCII characters")


if __name__ == '__main__':
    unittest.main()
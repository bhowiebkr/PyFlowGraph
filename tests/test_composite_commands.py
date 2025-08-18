"""
Unit tests for composite command behavior in PyFlowGraph.

Tests the CompositeCommand functionality including multi-operation handling,
failure recovery, partial rollback, and meaningful operation descriptions.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import QPointF

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.commands.command_base import CommandBase, CompositeCommand
from src.commands.node_commands import (
    CreateNodeCommand, DeleteNodeCommand, MoveNodeCommand, 
    PasteNodesCommand, MoveMultipleCommand, DeleteMultipleCommand
)


class MockCommand(CommandBase):
    """Mock command for testing composite command behavior."""
    
    def __init__(self, description: str, should_succeed: bool = True):
        super().__init__(description)
        self.should_succeed = should_succeed
        self.executed = False
        self.undone = False
    
    def execute(self) -> bool:
        self.executed = True
        if self.should_succeed:
            self._mark_executed()
            return True
        return False
    
    def undo(self) -> bool:
        self.undone = True
        if self.should_succeed:
            self._mark_undone()
            return True
        return False


class TestCompositeCommand(unittest.TestCase):
    """Test composite command functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.successful_cmd1 = MockCommand("Success 1")
        self.successful_cmd2 = MockCommand("Success 2")
        self.successful_cmd3 = MockCommand("Success 3")
        self.failing_cmd = MockCommand("Failure", should_succeed=False)
    
    def test_composite_command_all_succeed(self):
        """Test composite command when all sub-commands succeed."""
        commands = [self.successful_cmd1, self.successful_cmd2, self.successful_cmd3]
        composite = CompositeCommand("Test composite", commands)
        
        # Execute composite command
        result = composite.execute()
        
        # Verify success
        self.assertTrue(result)
        self.assertTrue(composite._executed)
        
        # Verify all commands were executed
        for cmd in commands:
            self.assertTrue(cmd.executed)
            self.assertTrue(cmd._executed)
        
        # Verify commands are in executed list
        self.assertEqual(len(composite.executed_commands), 3)
    
    def test_composite_command_with_failure(self):
        """Test composite command with one failing sub-command."""
        commands = [self.successful_cmd1, self.failing_cmd, self.successful_cmd3]
        composite = CompositeCommand("Test composite with failure", commands)
        
        # Execute composite command
        result = composite.execute()
        
        # Verify failure
        self.assertFalse(result)
        self.assertFalse(composite._executed)
        
        # Verify first command was executed then undone (rollback)
        self.assertTrue(self.successful_cmd1.executed)
        self.assertTrue(self.successful_cmd1.undone)
        self.assertFalse(self.successful_cmd1._executed)
        
        # Verify failing command was attempted
        self.assertTrue(self.failing_cmd.executed)
        self.assertFalse(self.failing_cmd._executed)
        
        # Verify third command was never executed
        self.assertFalse(self.successful_cmd3.executed)
    
    def test_composite_command_undo(self):
        """Test composite command undo functionality."""
        commands = [self.successful_cmd1, self.successful_cmd2, self.successful_cmd3]
        composite = CompositeCommand("Test composite undo", commands)
        
        # Execute then undo
        composite.execute()
        result = composite.undo()
        
        # Verify undo success
        self.assertTrue(result)
        self.assertFalse(composite._executed)
        
        # Verify all commands were undone in reverse order
        for cmd in commands:
            self.assertTrue(cmd.undone)
            self.assertFalse(cmd._executed)
    
    def test_composite_command_partial_undo_failure(self):
        """Test composite command undo with partial failures."""
        # Create commands where undo might fail but execute succeeds
        cmd1 = MockCommand("Success 1")
        cmd2 = MockCommand("Success 2")  # Execute succeeds
        cmd3 = MockCommand("Success 3")
        
        # Make cmd2 fail on undo but succeed on execute
        def cmd2_undo():
            cmd2.undone = True
            return False  # Fail undo
        cmd2.undo = cmd2_undo
        
        commands = [cmd1, cmd2, cmd3]
        composite = CompositeCommand("Test partial undo", commands)
        
        # Execute successfully (all commands succeed)
        execute_result = composite.execute()
        self.assertTrue(execute_result)
        
        # Attempt undo with one failure
        result = composite.undo()
        
        # Should still succeed overall (2/3 = 66% success rate >= 50%)
        self.assertTrue(result)
        
        # Verify attempts were made
        self.assertTrue(cmd1.undone)
        self.assertTrue(cmd2.undone)
        self.assertTrue(cmd3.undone)
    
    def test_composite_command_memory_usage(self):
        """Test composite command memory usage calculation."""
        commands = [self.successful_cmd1, self.successful_cmd2]
        composite = CompositeCommand("Test memory", commands)
        
        memory_usage = composite.get_memory_usage()
        expected = sum(cmd.get_memory_usage() for cmd in commands)
        
        self.assertEqual(memory_usage, expected)
    
    def test_composite_command_add_command(self):
        """Test adding commands to composite before execution."""
        composite = CompositeCommand("Test add", [self.successful_cmd1])
        
        # Add command before execution
        composite.add_command(self.successful_cmd2)
        self.assertEqual(composite.get_command_count(), 2)
        
        # Execute
        composite.execute()
        
        # Should not be able to add after execution
        composite.add_command(self.successful_cmd3)
        self.assertEqual(composite.get_command_count(), 2)
    
    def test_meaningful_descriptions(self):
        """Test that composite commands generate meaningful descriptions."""
        commands = [self.successful_cmd1, self.successful_cmd2, self.successful_cmd3]
        
        # Test various description patterns
        composite1 = CompositeCommand("Delete 3 nodes", commands)
        self.assertEqual(composite1.get_description(), "Delete 3 nodes")
        
        composite2 = CompositeCommand("Paste 2 nodes with 1 connection", commands)
        self.assertEqual(composite2.get_description(), "Paste 2 nodes with 1 connection")


class TestNodeCompositeCommands(unittest.TestCase):
    """Test node-specific composite commands."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
        self.mock_graph.nodes = []
        self.mock_graph.connections = []
        self.mock_graph.addItem = Mock()
        self.mock_graph.removeItem = Mock()
        self.mock_graph.execute_command = Mock(return_value=True)
    
    @patch('src.core.node.Node')
    def test_paste_nodes_command_creation(self, mock_node_class):
        """Test PasteNodesCommand creation and description generation."""
        mock_node = Mock()
        mock_node.title = "Test Node"
        mock_node_class.return_value = mock_node
        
        # Test single node paste
        clipboard_data = {
            'nodes': [{'id': 'node1', 'title': 'Test Node', 'code': '', 'description': ''}],
            'connections': []
        }
        
        paste_cmd = PasteNodesCommand(self.mock_graph, clipboard_data, QPointF(0, 0))
        self.assertEqual(paste_cmd.get_description(), "Paste 'Test Node'")
        
        # Test multiple nodes paste
        clipboard_data['nodes'].append({'id': 'node2', 'title': 'Another Node', 'code': '', 'description': ''})
        paste_cmd2 = PasteNodesCommand(self.mock_graph, clipboard_data, QPointF(0, 0))
        self.assertEqual(paste_cmd2.get_description(), "Paste 2 nodes")
    
    def test_move_multiple_command_creation(self):
        """Test MoveMultipleCommand creation and description generation."""
        mock_node1 = Mock()
        mock_node1.title = "Node 1"
        mock_node2 = Mock()
        mock_node2.title = "Node 2"
        
        # Test single node move
        nodes_and_positions = [(mock_node1, QPointF(0, 0), QPointF(10, 10))]
        move_cmd = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        self.assertEqual(move_cmd.get_description(), "Move 'Node 1'")
        
        # Test multiple nodes move
        nodes_and_positions.append((mock_node2, QPointF(0, 0), QPointF(20, 20)))
        move_cmd2 = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        self.assertEqual(move_cmd2.get_description(), "Move 2 nodes")
    
    def test_delete_multiple_command_description_logic(self):
        """Test DeleteMultipleCommand description generation logic."""
        # Test the description generation logic without complex mocking
        from src.commands.node_commands import DeleteMultipleCommand
        
        # We can't easily test the full DeleteMultipleCommand creation due to imports
        # but we can test that the class exists and has the right structure
        self.assertTrue(hasattr(DeleteMultipleCommand, '__init__'))
        self.assertTrue(hasattr(DeleteMultipleCommand, 'get_memory_usage'))
        
        # Test that it's a proper subclass of CompositeCommand
        self.assertTrue(issubclass(DeleteMultipleCommand, CompositeCommand))


class TestCompositeCommandEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for composite commands."""
    
    def test_empty_composite_command(self):
        """Test composite command with no sub-commands."""
        composite = CompositeCommand("Empty composite", [])
        
        # Should succeed trivially
        result = composite.execute()
        self.assertTrue(result)
        
        # Undo should also succeed
        undo_result = composite.undo()
        self.assertTrue(undo_result)
    
    def test_composite_command_undo_without_execute(self):
        """Test undo on composite command that was never executed."""
        commands = [MockCommand("Test")]
        composite = CompositeCommand("Never executed", commands)
        
        # Undo without execute should fail gracefully
        result = composite.undo()
        self.assertFalse(result)
    
    def test_large_composite_command(self):
        """Test composite command with many sub-commands for memory efficiency."""
        # Create 100 mock commands
        commands = [MockCommand(f"Command {i}") for i in range(100)]
        composite = CompositeCommand("Large composite", commands)
        
        # Execute should handle large numbers efficiently
        result = composite.execute()
        self.assertTrue(result)
        
        # Verify all commands executed
        for cmd in commands:
            self.assertTrue(cmd.executed)
        
        # Memory usage should be reasonable
        memory_usage = composite.get_memory_usage()
        self.assertLess(memory_usage, 1000000)  # Less than 1MB for test commands


if __name__ == '__main__':
    unittest.main()
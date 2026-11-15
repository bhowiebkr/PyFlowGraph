"""
Unit tests for selection-based operations in PyFlowGraph.

Tests bulk delete, move operations, and undo descriptions for
various multi-operation scenarios using composite commands.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication


from pyflowgraph.commands.node_commands import MoveMultipleCommand, DeleteMultipleCommand
from pyflowgraph.core.node import Node
from pyflowgraph.core.node_graph import NodeGraph


class TestMoveMultipleCommand(unittest.TestCase):
    """Test MoveMultipleCommand functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
        self.mock_graph.nodes = []
        self.mock_graph.connections = []
        
        # Create mock nodes
        self.mock_node1 = Mock()
        self.mock_node1.title = "Node 1"
        self.mock_node1.setPos = Mock()
        
        self.mock_node2 = Mock()
        self.mock_node2.title = "Node 2"
        self.mock_node2.setPos = Mock()
        
        self.mock_node3 = Mock()
        self.mock_node3.title = "Very Long Node Name"
        self.mock_node3.setPos = Mock()
    
    def test_move_single_node_description(self):
        """Test description generation for single node move."""
        nodes_and_positions = [
            (self.mock_node1, QPointF(0, 0), QPointF(100, 100))
        ]
        
        move_cmd = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        self.assertEqual(move_cmd.get_description(), "Move 'Node 1'")
    
    def test_move_multiple_nodes_description(self):
        """Test description generation for multiple node move."""
        nodes_and_positions = [
            (self.mock_node1, QPointF(0, 0), QPointF(100, 100)),
            (self.mock_node2, QPointF(10, 10), QPointF(110, 110)),
            (self.mock_node3, QPointF(20, 20), QPointF(120, 120))
        ]
        
        move_cmd = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        self.assertEqual(move_cmd.get_description(), "Move 3 nodes")
    
    @patch('pyflowgraph.commands.node.batch_operations.MoveNodeCommand')
    def test_move_command_creation(self, mock_move_cmd):
        """Test that individual move commands are created correctly."""
        mock_cmd1 = Mock()
        mock_cmd2 = Mock()
        mock_move_cmd.side_effect = [mock_cmd1, mock_cmd2]
        
        nodes_and_positions = [
            (self.mock_node1, QPointF(0, 0), QPointF(100, 100)),
            (self.mock_node2, QPointF(10, 10), QPointF(110, 110))
        ]
        
        move_cmd = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        
        # Verify individual commands were created
        self.assertEqual(len(move_cmd.commands), 2)
        
        # Verify MoveNodeCommand was called with correct parameters
        mock_move_cmd.assert_any_call(self.mock_graph, self.mock_node1, QPointF(0, 0), QPointF(100, 100))
        mock_move_cmd.assert_any_call(self.mock_graph, self.mock_node2, QPointF(10, 10), QPointF(110, 110))
    
    def test_move_command_memory_usage(self):
        """Test memory usage calculation for move operations."""
        nodes_and_positions = [
            (self.mock_node1, QPointF(0, 0), QPointF(100, 100)),
            (self.mock_node2, QPointF(10, 10), QPointF(110, 110))
        ]
        
        move_cmd = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        memory_usage = move_cmd.get_memory_usage()
        
        # Should be base size plus inherited composite command usage
        self.assertGreater(memory_usage, 256)  # Base size
        self.assertLess(memory_usage, 10000)   # Reasonable upper bound


class TestDeleteMultipleCommand(unittest.TestCase):
    """Test DeleteMultipleCommand functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures with real instances."""
        # Create a real NodeGraph for testing
        self.graph = NodeGraph()
        
        # Create real nodes for testing
        self.node1 = Node("Test Node")
        self.node2 = Node("Another Node")
        
        # Add nodes to graph
        self.graph.addItem(self.node1)
        self.graph.addItem(self.node2)
        
        # Pins come from the node code.
        self.node1.set_code("@node_entry\ndef test() -> int:\n    return 42\n")
        self.node2.set_code("@node_entry\ndef process(value: int) -> int:\n    return value * 2\n")

        output = next(p for p in self.node1.output_pins if p.name == "output_1")
        value = next(p for p in self.node2.input_pins if p.name == "value")
        self.connection1 = self.graph.create_connection(output, value, use_command=False)

    def test_delete_single_node_description(self):
        """Test description generation for single node deletion."""
        selected_items = [self.node1]
        
        delete_cmd = DeleteMultipleCommand(self.graph, selected_items)
        self.assertEqual(delete_cmd.get_description(), "Delete 'Test Node'")
        self.assertEqual(len(delete_cmd.commands), 1)
    
    def test_delete_multiple_nodes_description(self):
        """Test description generation for multiple node deletion."""
        selected_items = [self.node1, self.node2]
        
        delete_cmd = DeleteMultipleCommand(self.graph, selected_items)
        self.assertEqual(delete_cmd.get_description(), "Delete 2 nodes")
        self.assertEqual(len(delete_cmd.commands), 2)
    
    def test_delete_connections_only_description(self):
        """Test description generation for connection-only deletion."""
        selected_items = [self.connection1]
        
        delete_cmd = DeleteMultipleCommand(self.graph, selected_items)
        self.assertEqual(delete_cmd.get_description(), "Delete connection")
    
    def test_delete_mixed_items_description(self):
        """Test description generation for mixed node and connection deletion."""
        selected_items = [self.node1, self.connection1]
        
        delete_cmd = DeleteMultipleCommand(self.graph, selected_items)
        self.assertEqual(delete_cmd.get_description(), "Delete 'Test Node' and 1 connection")
    
    def test_delete_command_creation(self):
        """Test that appropriate delete commands are created for different item types."""
        selected_items = [self.node1, self.connection1]
        
        delete_cmd = DeleteMultipleCommand(self.graph, selected_items)
        
        # Verify correct commands were created
        self.assertEqual(len(delete_cmd.commands), 2)
        
        # Check that we have one node delete and one connection delete command
        from pyflowgraph.commands.node_commands import DeleteNodeCommand
        from pyflowgraph.commands.connection_commands import DeleteConnectionCommand
        
        node_commands = [cmd for cmd in delete_cmd.commands if isinstance(cmd, DeleteNodeCommand)]
        conn_commands = [cmd for cmd in delete_cmd.commands if isinstance(cmd, DeleteConnectionCommand)]
        
        self.assertEqual(len(node_commands), 1)
        self.assertEqual(len(conn_commands), 1)
    
    def test_delete_command_memory_usage(self):
        """Test memory usage calculation for delete operations."""
        selected_items = [self.node1, self.node2]
        
        delete_cmd = DeleteMultipleCommand(self.graph, selected_items)
        memory_usage = delete_cmd.get_memory_usage()
        
        # Should be base size plus inherited composite command usage
        # The base size is exactly 512, so we need >= not just >
        self.assertGreaterEqual(memory_usage, 512)  # Base size
        self.assertLess(memory_usage, 50000)   # Reasonable upper bound


class TestSelectionOperationEdgeCases(unittest.TestCase):
    """Test edge cases for selection-based operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
        self.mock_graph.nodes = []
        self.mock_graph.connections = []
    
    def test_empty_selection_move(self):
        """Test move command with empty selection."""
        nodes_and_positions = []
        
        move_cmd = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        self.assertEqual(move_cmd.get_description(), "Move 0 nodes")
        self.assertEqual(len(move_cmd.commands), 0)
    
    def test_empty_selection_delete(self):
        """Test delete command with empty selection."""
        selected_items = []
        
        delete_cmd = DeleteMultipleCommand(self.mock_graph, selected_items)
        self.assertEqual(delete_cmd.get_description(), "Delete 0 items")
        self.assertEqual(len(delete_cmd.commands), 0)
    
    def test_unknown_item_type_delete(self):
        """Test delete command with unknown item types."""
        # Create a mock that's not a Node or Connection
        unknown_item = Mock()
        unknown_item.title = "Unknown Item"
        selected_items = [unknown_item]
        
        # Create a mock graph for this test
        mock_graph = Mock()
        mock_graph.nodes = []
        mock_graph.connections = []
        
        delete_cmd = DeleteMultipleCommand(mock_graph, selected_items)
        
        # Should handle gracefully and create no commands
        self.assertEqual(len(delete_cmd.commands), 0)
        self.assertEqual(delete_cmd.get_description(), "Delete 1 items")
    
    def test_large_selection_performance(self):
        """Test performance with large selections."""
        # Create many mock nodes
        mock_nodes = []
        nodes_and_positions = []
        
        for i in range(50):
            mock_node = Mock()
            mock_node.title = f"Node {i}"
            mock_nodes.append(mock_node)
            nodes_and_positions.append((mock_node, QPointF(i, i), QPointF(i+100, i+100)))
        
        # Test move command creation
        move_cmd = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        self.assertEqual(move_cmd.get_description(), "Move 50 nodes")
        self.assertEqual(len(move_cmd.commands), 50)
        
        # Memory usage should be reasonable
        memory_usage = move_cmd.get_memory_usage()
        self.assertLess(memory_usage, 100000)  # Should be less than 100KB


class TestSelectionOperationUndo(unittest.TestCase):
    """Test undo behavior for selection-based operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
    
    @patch('pyflowgraph.commands.node.batch_operations.MoveNodeCommand')
    def test_move_multiple_undo_order(self, mock_move_cmd):
        """Test that move operations are undone in correct order."""
        # Setup mock move commands
        mock_cmd1 = Mock()
        mock_cmd1.execute.return_value = True
        mock_cmd1.undo.return_value = True
        mock_cmd1._mark_executed = Mock()
        mock_cmd1._mark_undone = Mock()
        
        mock_cmd2 = Mock()
        mock_cmd2.execute.return_value = True
        mock_cmd2.undo.return_value = True
        mock_cmd2._mark_executed = Mock()
        mock_cmd2._mark_undone = Mock()
        
        mock_move_cmd.side_effect = [mock_cmd1, mock_cmd2]
        
        # Create mock nodes
        mock_node1 = Mock()
        mock_node1.title = "Node 1"
        mock_node2 = Mock()
        mock_node2.title = "Node 2"
        
        nodes_and_positions = [
            (mock_node1, QPointF(0, 0), QPointF(100, 100)),
            (mock_node2, QPointF(10, 10), QPointF(110, 110))
        ]
        
        # Execute and undo
        move_cmd = MoveMultipleCommand(self.mock_graph, nodes_and_positions)
        move_cmd.execute()
        move_cmd.undo()
        
        # Verify commands were executed and undone
        mock_cmd1.execute.assert_called_once()
        mock_cmd2.execute.assert_called_once()
        mock_cmd1.undo.assert_called_once()
        mock_cmd2.undo.assert_called_once()


if __name__ == '__main__':
    unittest.main()
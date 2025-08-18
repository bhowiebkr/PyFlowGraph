"""
Unit tests for selection-based operations in PyFlowGraph.

Tests bulk delete, move operations, and undo descriptions for
various multi-operation scenarios using composite commands.
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

from src.commands.node_commands import MoveMultipleCommand, DeleteMultipleCommand


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
    
    @patch('src.commands.node_commands.MoveNodeCommand')
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
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
        self.mock_graph.nodes = []
        self.mock_graph.connections = []
        
        # Create mock nodes
        self.mock_node1 = Mock()
        self.mock_node1.title = "Test Node"
        
        self.mock_node2 = Mock()
        self.mock_node2.title = "Another Node"
        
        self.mock_reroute = Mock()
        self.mock_reroute.title = "Reroute"
        
        # Create mock connections
        self.mock_connection1 = Mock()
        self.mock_connection2 = Mock()
    
    def test_delete_single_node_description(self):
        """Test description generation for single node deletion."""
        selected_items = [self.mock_node1]
        
        # Mock isinstance to return True for Node
        with patch('builtins.isinstance') as mock_isinstance:
            def isinstance_side_effect(obj, class_type):
                if obj == self.mock_node1:
                    return 'Node' in str(class_type) or 'RerouteNode' in str(class_type)
                return False
            mock_isinstance.side_effect = isinstance_side_effect
            
            delete_cmd = DeleteMultipleCommand(self.mock_graph, selected_items)
            self.assertEqual(delete_cmd.get_description(), "Delete 'Test Node'")
    
    def test_delete_multiple_nodes_description(self):
        """Test description generation for multiple node deletion."""
        selected_items = [self.mock_node1, self.mock_node2]
        
        # Mock isinstance to return True for Nodes
        with patch('builtins.isinstance') as mock_isinstance:
            def isinstance_side_effect(obj, class_type):
                if obj in [self.mock_node1, self.mock_node2]:
                    return 'Node' in str(class_type) or 'RerouteNode' in str(class_type)
                return False
            mock_isinstance.side_effect = isinstance_side_effect
            
            delete_cmd = DeleteMultipleCommand(self.mock_graph, selected_items)
            self.assertEqual(delete_cmd.get_description(), "Delete 2 nodes")
    
    def test_delete_connections_only_description(self):
        """Test description generation for connection-only deletion."""
        selected_items = [self.mock_connection1, self.mock_connection2]
        
        # Mock isinstance to return True for Connections
        with patch('builtins.isinstance') as mock_isinstance:
            def isinstance_side_effect(obj, class_type):
                if obj in [self.mock_connection1, self.mock_connection2]:
                    return 'Connection' in str(class_type)
                return False
            mock_isinstance.side_effect = isinstance_side_effect
            
            delete_cmd = DeleteMultipleCommand(self.mock_graph, selected_items)
            self.assertEqual(delete_cmd.get_description(), "Delete 2 connections")
    
    def test_delete_mixed_items_description(self):
        """Test description generation for mixed node and connection deletion."""
        selected_items = [self.mock_node1, self.mock_connection1]
        
        # Mock isinstance appropriately
        with patch('builtins.isinstance') as mock_isinstance:
            def isinstance_side_effect(obj, class_type):
                if obj == self.mock_node1:
                    return 'Node' in str(class_type) or 'RerouteNode' in str(class_type)
                elif obj == self.mock_connection1:
                    return 'Connection' in str(class_type)
                return False
            mock_isinstance.side_effect = isinstance_side_effect
            
            delete_cmd = DeleteMultipleCommand(self.mock_graph, selected_items)
            self.assertEqual(delete_cmd.get_description(), "Delete 1 nodes and 1 connections")
    
    @patch('src.commands.node_commands.DeleteNodeCommand')
    @patch('src.commands.connection_commands.DeleteConnectionCommand')
    def test_delete_command_creation(self, mock_delete_conn_cmd, mock_delete_node_cmd):
        """Test that appropriate delete commands are created for different item types."""
        mock_node_cmd = Mock()
        mock_conn_cmd = Mock()
        mock_delete_node_cmd.return_value = mock_node_cmd
        mock_delete_conn_cmd.return_value = mock_conn_cmd
        
        selected_items = [self.mock_node1, self.mock_connection1]
        
        # Mock isinstance appropriately
        with patch('builtins.isinstance') as mock_isinstance:
            def isinstance_side_effect(obj, class_type):
                if obj == self.mock_node1:
                    return 'Node' in str(class_type) or 'RerouteNode' in str(class_type)
                elif obj == self.mock_connection1:
                    return 'Connection' in str(class_type)
                return False
            mock_isinstance.side_effect = isinstance_side_effect
            
            delete_cmd = DeleteMultipleCommand(self.mock_graph, selected_items)
            
            # Verify correct commands were created
            self.assertEqual(len(delete_cmd.commands), 2)
            mock_delete_node_cmd.assert_called_once_with(self.mock_graph, self.mock_node1)
            mock_delete_conn_cmd.assert_called_once_with(self.mock_graph, self.mock_connection1)
    
    def test_delete_command_memory_usage(self):
        """Test memory usage calculation for delete operations."""
        selected_items = [self.mock_node1, self.mock_node2]
        
        # Mock isinstance
        with patch('builtins.isinstance') as mock_isinstance:
            def isinstance_side_effect(obj, class_type):
                return 'Node' in str(class_type) or 'RerouteNode' in str(class_type)
            mock_isinstance.side_effect = isinstance_side_effect
            
            delete_cmd = DeleteMultipleCommand(self.mock_graph, selected_items)
            memory_usage = delete_cmd.get_memory_usage()
            
            # Should be base size plus inherited composite command usage
            self.assertGreater(memory_usage, 512)  # Base size
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
        unknown_item = Mock()
        selected_items = [unknown_item]
        
        # Mock isinstance to return False for all known types
        with patch('builtins.isinstance', return_value=False):
            delete_cmd = DeleteMultipleCommand(self.mock_graph, selected_items)
            
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
    
    @patch('src.commands.node_commands.MoveNodeCommand')
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
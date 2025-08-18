"""
Integration tests for copy/paste workflow in PyFlowGraph.

Tests the complete copy/paste functionality including clipboard operations,
command integration, and undo/redo behavior for pasted content.
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.commands.node_commands import PasteNodesCommand


class TestCopyPasteIntegration(unittest.TestCase):
    """Test copy/paste integration workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
        self.mock_graph.nodes = []
        self.mock_graph.connections = []
        self.mock_graph.addItem = Mock()
        self.mock_graph.removeItem = Mock()
        self.mock_graph.execute_command = Mock(return_value=True)
        
        # Mock command history
        self.mock_graph.command_history = Mock()
        self.mock_graph.command_history.execute_command = Mock(return_value=True)
    
    @patch('src.commands.node_commands.Node')
    def test_paste_single_node_workflow(self, mock_node_class):
        """Test pasting a single node creates proper commands."""
        # Setup mock node
        mock_node = Mock()
        mock_node.title = "Test Node"
        mock_node.uuid = "test-uuid"
        mock_node.get_pin_by_name = Mock(return_value=None)
        mock_node_class.return_value = mock_node
        
        # Test data for single node
        clipboard_data = {
            'nodes': [{
                'id': 'original-uuid',
                'title': 'Test Node',
                'description': 'A test node',
                'code': 'def test(): pass'
            }],
            'connections': []
        }
        
        # Create paste command
        paste_cmd = PasteNodesCommand(self.mock_graph, clipboard_data, QPointF(100, 200))
        
        # Verify command description
        self.assertEqual(paste_cmd.get_description(), "Paste 'Test Node'")
        
        # Verify UUID mapping was created
        self.assertEqual(len(paste_cmd.uuid_mapping), 1)
        self.assertIn('original-uuid', paste_cmd.uuid_mapping)
        self.assertNotEqual(paste_cmd.uuid_mapping['original-uuid'], 'original-uuid')
    
    @patch('src.commands.node_commands.Node')
    def test_paste_multiple_nodes_with_connections(self, mock_node_class):
        """Test pasting multiple nodes with connections preserves relationships."""
        # Setup mock nodes
        mock_node1 = Mock()
        mock_node1.title = "Input Node"
        mock_node1.uuid = "new-uuid-1"
        mock_node1.get_pin_by_name = Mock(return_value=Mock())
        
        mock_node2 = Mock()
        mock_node2.title = "Output Node"
        mock_node2.uuid = "new-uuid-2"
        mock_node2.get_pin_by_name = Mock(return_value=Mock())
        
        mock_node_class.side_effect = [mock_node1, mock_node2]
        
        # Test data with connections
        clipboard_data = {
            'nodes': [
                {
                    'id': 'input-uuid',
                    'title': 'Input Node',
                    'description': '',
                    'code': 'def input(): return 42'
                },
                {
                    'id': 'output-uuid',
                    'title': 'Output Node',
                    'description': '',
                    'code': 'def output(x): print(x)'
                }
            ],
            'connections': [
                {
                    'output_node_id': 'input-uuid',
                    'input_node_id': 'output-uuid',
                    'output_pin_name': 'result',
                    'input_pin_name': 'x'
                }
            ]
        }
        
        # Create paste command
        paste_cmd = PasteNodesCommand(self.mock_graph, clipboard_data, QPointF(100, 200))
        
        # Verify command description
        self.assertEqual(paste_cmd.get_description(), "Paste 2 nodes with 1 connections")
        
        # Verify UUID mapping
        self.assertEqual(len(paste_cmd.uuid_mapping), 2)
        self.assertIn('input-uuid', paste_cmd.uuid_mapping)
        self.assertIn('output-uuid', paste_cmd.uuid_mapping)
    
    @patch('src.commands.node_commands.Node')
    def test_paste_nodes_positioning(self, mock_node_class):
        """Test that pasted nodes are positioned correctly with offsets."""
        mock_node_class.return_value = Mock()
        
        # Test data with multiple nodes
        clipboard_data = {
            'nodes': [
                {'id': 'node1', 'title': 'Node 1', 'description': '', 'code': ''},
                {'id': 'node2', 'title': 'Node 2', 'description': '', 'code': ''},
                {'id': 'node3', 'title': 'Node 3', 'description': '', 'code': ''},
                {'id': 'node4', 'title': 'Node 4', 'description': '', 'code': ''}
            ],
            'connections': []
        }
        
        paste_position = QPointF(100, 200)
        paste_cmd = PasteNodesCommand(self.mock_graph, clipboard_data, paste_position)
        
        # Verify that node commands were created with proper positioning
        self.assertEqual(len(paste_cmd.commands), 4)
        
        # Check positioning logic (grid arrangement)
        positions = []
        for cmd in paste_cmd.commands:
            positions.append(cmd.position)
        
        # Should be arranged in grid: (100,200), (300,200), (500,200), (100,350)
        expected_positions = [
            QPointF(100, 200),  # (0%3)*200 + 100, (0//3)*150 + 200
            QPointF(300, 200),  # (1%3)*200 + 100, (1//3)*150 + 200
            QPointF(500, 200),  # (2%3)*200 + 100, (2//3)*150 + 200
            QPointF(100, 350)   # (3%3)*200 + 100, (3//3)*150 + 200
        ]
        
        for i, expected_pos in enumerate(expected_positions):
            self.assertEqual(positions[i], expected_pos)
    
    def test_paste_command_memory_usage(self):
        """Test memory usage calculation for paste operations."""
        clipboard_data = {
            'nodes': [
                {'id': 'node1', 'title': 'Small Node', 'description': '', 'code': ''},
                {'id': 'node2', 'title': 'Large Node', 'description': 'A' * 1000, 'code': 'B' * 2000}
            ],
            'connections': []
        }
        
        paste_cmd = PasteNodesCommand(self.mock_graph, clipboard_data, QPointF(0, 0))
        memory_usage = paste_cmd.get_memory_usage()
        
        # Should account for clipboard data size
        self.assertGreater(memory_usage, 1024)  # Base size
        self.assertLess(memory_usage, 10000)    # Reasonable upper bound


class TestCopyPasteCommandUndo(unittest.TestCase):
    """Test undo/redo behavior for copy/paste operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
        self.mock_graph.nodes = []
        self.mock_graph.connections = []
        self.mock_graph.addItem = Mock()
        self.mock_graph.removeItem = Mock()
    
    @patch('src.commands.node_commands.CreateNodeCommand')
    def test_paste_command_undo_behavior(self, mock_create_cmd):
        """Test that paste command undo properly removes all created nodes."""
        # Setup mock create commands
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
        
        mock_create_cmd.side_effect = [mock_cmd1, mock_cmd2]
        
        clipboard_data = {
            'nodes': [
                {'id': 'node1', 'title': 'Node 1', 'description': '', 'code': ''},
                {'id': 'node2', 'title': 'Node 2', 'description': '', 'code': ''}
            ],
            'connections': []
        }
        
        # Create and execute paste command
        paste_cmd = PasteNodesCommand(self.mock_graph, clipboard_data, QPointF(0, 0))
        execute_result = paste_cmd.execute()
        self.assertTrue(execute_result)
        
        # Undo paste command
        undo_result = paste_cmd.undo()
        self.assertTrue(undo_result)
        
        # Verify all create commands were undone
        mock_cmd1.undo.assert_called_once()
        mock_cmd2.undo.assert_called_once()
    
    @patch('src.commands.node_commands.CreateNodeCommand')
    def test_paste_command_partial_failure_rollback(self, mock_create_cmd):
        """Test paste command rollback when one node creation fails."""
        # Setup mock commands - first succeeds, second fails
        mock_cmd1 = Mock()
        mock_cmd1.execute.return_value = True
        mock_cmd1.undo.return_value = True
        mock_cmd1._mark_executed = Mock()
        mock_cmd1._mark_undone = Mock()
        
        mock_cmd2 = Mock()
        mock_cmd2.execute.return_value = False  # This one fails
        
        mock_create_cmd.side_effect = [mock_cmd1, mock_cmd2]
        
        clipboard_data = {
            'nodes': [
                {'id': 'node1', 'title': 'Node 1', 'description': '', 'code': ''},
                {'id': 'node2', 'title': 'Node 2', 'description': '', 'code': ''}
            ],
            'connections': []
        }
        
        # Create and execute paste command
        paste_cmd = PasteNodesCommand(self.mock_graph, clipboard_data, QPointF(0, 0))
        execute_result = paste_cmd.execute()
        
        # Should fail overall
        self.assertFalse(execute_result)
        
        # First command should have been rolled back
        mock_cmd1.undo.assert_called_once()


class TestDataFormatConversion(unittest.TestCase):
    """Test data format conversion for copy/paste operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
        self.mock_graph._convert_data_format = Mock()
    
    def test_deserialize_to_paste_format_conversion(self):
        """Test conversion from deserialize format to paste command format."""
        # Mock the actual conversion method from node_graph
        from src.core.node_graph import NodeGraph
        
        # Create a minimal mock instance to test the conversion method
        graph = Mock(spec=NodeGraph)
        graph._convert_data_format = NodeGraph._convert_data_format.__get__(graph, NodeGraph)
        
        # Test data in deserialize format
        deserialize_data = {
            'nodes': [
                {
                    'uuid': 'test-uuid-1',
                    'title': 'Test Node',
                    'description': 'A test node',
                    'code': 'def test(): pass',
                    'pos': [100, 200]
                }
            ],
            'connections': [
                {
                    'start_node_uuid': 'test-uuid-1',
                    'end_node_uuid': 'test-uuid-2',
                    'start_pin_name': 'output',
                    'end_pin_name': 'input'
                }
            ]
        }
        
        # Convert to paste format
        paste_data = graph._convert_data_format(deserialize_data)
        
        # Verify conversion
        self.assertEqual(len(paste_data['nodes']), 1)
        self.assertEqual(paste_data['nodes'][0]['id'], 'test-uuid-1')
        self.assertEqual(paste_data['nodes'][0]['title'], 'Test Node')
        
        self.assertEqual(len(paste_data['connections']), 1)
        self.assertEqual(paste_data['connections'][0]['output_node_id'], 'test-uuid-1')
        self.assertEqual(paste_data['connections'][0]['input_node_id'], 'test-uuid-2')


if __name__ == '__main__':
    unittest.main()
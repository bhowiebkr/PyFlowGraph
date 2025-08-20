"""
Real-world integration tests using actual example files.

Tests the command system with real workflows to find bugs in practice.
Uses the password generator example to test complex operations.
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

# Mock PySide6 for headless testing
if not QApplication.instance():
    app = QApplication([])

from src.commands.node_commands import (
    CodeChangeCommand, PasteNodesCommand, DeleteMultipleCommand,
    CreateNodeCommand, MoveMultipleCommand
)
from src.commands.command_base import CompositeCommand
from src.data.flow_format import FlowFormatHandler


class TestRealWorkflowIntegration(unittest.TestCase):
    """Test command system with real password generator workflow."""
    
    def setUp(self):
        """Set up test fixtures with real example data."""
        self.example_file = os.path.join(project_root, 'examples', 'password_generator_tool.md')
        
        # Create mock graph components
        self.mock_graph = Mock()
        self.mock_graph.nodes = []
        self.mock_graph.connections = []
        self.mock_graph.addItem = Mock()
        self.mock_graph.removeItem = Mock()
        self.mock_graph.command_history = Mock()
        
        # Load real example data
        self.example_data = self._load_example_data()
        
    def _load_example_data(self):
        """Load and parse the password generator example file."""
        try:
            with open(self.example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            handler = FlowFormatHandler()
            data = handler.markdown_to_data(content)
            return data
        except Exception as e:
            self.skipTest(f"Could not load example file: {e}")
    
    @patch('src.core.node.Node')
    def test_paste_real_password_generator_workflow(self, mock_node_class):
        """Test pasting the complete password generator workflow."""
        # Setup mock nodes for each node in the workflow
        mock_nodes = {}
        expected_nodes = ['config-input', 'password-generator', 'strength-analyzer', 'output-display']
        
        for i, node_id in enumerate(expected_nodes):
            mock_node = Mock()
            mock_node.title = f"Test Node {i}"
            mock_node.uuid = f"new-{node_id}"
            mock_node.get_pin_by_name = Mock(return_value=Mock())
            mock_nodes[node_id] = mock_node
        
        mock_node_class.side_effect = list(mock_nodes.values())
        
        # Convert example data to paste format
        paste_data = self._convert_to_paste_format(self.example_data)
        
        # Create paste command
        paste_cmd = PasteNodesCommand(self.mock_graph, paste_data, QPointF(100, 100))
        
        # Verify command creation
        self.assertIsInstance(paste_cmd, CompositeCommand)
        self.assertEqual(len(paste_cmd.commands), len(expected_nodes))
        
        # Verify UUID mapping was created for all nodes
        self.assertEqual(len(paste_cmd.uuid_mapping), len(expected_nodes))
        for node_id in expected_nodes:
            self.assertIn(node_id, paste_cmd.uuid_mapping)
            self.assertNotEqual(paste_cmd.uuid_mapping[node_id], node_id)
    
    def _convert_to_paste_format(self, data):
        """Convert example data to format expected by PasteNodesCommand."""
        paste_data = {
            'nodes': [],
            'connections': []
        }
        
        # Convert nodes
        for node_data in data.get('nodes', []):
            converted_node = {
                'id': node_data.get('uuid', ''),
                'title': node_data.get('title', 'Unknown'),
                'description': node_data.get('description', ''),
                'code': node_data.get('code', ''),
                'pos': node_data.get('pos', [0, 0])
            }
            paste_data['nodes'].append(converted_node)
        
        # Convert connections
        for conn_data in data.get('connections', []):
            converted_conn = {
                'output_node_id': conn_data.get('start_node_uuid', ''),
                'input_node_id': conn_data.get('end_node_uuid', ''),
                'output_pin_name': conn_data.get('start_pin_name', ''),
                'input_pin_name': conn_data.get('end_pin_name', '')
            }
            paste_data['connections'].append(converted_conn)
        
        return paste_data
    
    def test_code_modification_with_real_node_data(self):
        """Test code modification using real node code from example."""
        # Get real code from password generator node
        password_gen_node = None
        for node in self.example_data.get('nodes', []):
            if node.get('uuid') == 'password-generator':
                password_gen_node = node
                break
        
        self.assertIsNotNone(password_gen_node, "Password generator node not found in example")
        
        # Create mock node with real code
        mock_node = Mock()
        mock_node.title = password_gen_node['title']
        mock_node.set_code = Mock()
        
        original_code = password_gen_node['code']
        modified_code = original_code.replace('random.choice(charset)', 'random.SystemRandom().choice(charset)')
        
        # Create code change command
        code_cmd = CodeChangeCommand(self.mock_graph, mock_node, original_code, modified_code)
        
        # Execute command
        result = code_cmd.execute()
        self.assertTrue(result)
        mock_node.set_code.assert_called_once_with(modified_code)
        
        # Test undo
        mock_node.set_code.reset_mock()
        undo_result = code_cmd.undo()
        self.assertTrue(undo_result)
        mock_node.set_code.assert_called_once_with(original_code)
    
    def test_complex_multi_node_operations(self):
        """Test complex operations with multiple nodes from real workflow."""
        # Import the actual classes to create instances that pass isinstance checks
        from src.core.node import Node
        from unittest.mock import create_autospec
        
        # Create mock nodes that will pass isinstance checks
        mock_nodes = []
        for node_data in self.example_data.get('nodes', []):
            # Create an autospec that will pass isinstance checks
            mock_node = create_autospec(Node, instance=True)
            mock_node.title = node_data['title']
            mock_node.uuid = node_data['uuid']
            mock_nodes.append(mock_node)
        
        # Test delete multiple command with real nodes
        delete_cmd = DeleteMultipleCommand(self.mock_graph, mock_nodes)
        
        # Verify command structure
        self.assertIsInstance(delete_cmd, CompositeCommand)
        self.assertEqual(len(delete_cmd.commands), len(mock_nodes))
        
        # Verify description generation
        expected_description = f"Delete {len(mock_nodes)} nodes"
        self.assertEqual(delete_cmd.get_description(), expected_description)
    
    def test_workflow_connection_integrity(self):
        """Test that connections in the workflow are properly handled."""
        connections = self.example_data.get('connections', [])
        
        # Verify we have the expected number of connections
        self.assertGreater(len(connections), 0, "Example should have connections")
        
        # Verify connection structure
        for conn in connections:
            self.assertIn('start_node_uuid', conn)
            self.assertIn('end_node_uuid', conn)
            self.assertIn('start_pin_name', conn)
            self.assertIn('end_pin_name', conn)
            
            # Verify UUIDs are not empty
            self.assertTrue(conn['start_node_uuid'])
            self.assertTrue(conn['end_node_uuid'])
    
    def test_node_positioning_in_paste_operation(self):
        """Test that nodes are positioned correctly when pasted."""
        paste_data = self._convert_to_paste_format(self.example_data)
        
        paste_position = QPointF(200, 300)
        paste_cmd = PasteNodesCommand(self.mock_graph, paste_data, paste_position)
        
        # Verify positioning logic
        for i, cmd in enumerate(paste_cmd.commands):
            expected_x = paste_position.x() + (i % 3) * 200
            expected_y = paste_position.y() + (i // 3) * 150
            expected_pos = QPointF(expected_x, expected_y)
            
            self.assertEqual(cmd.position, expected_pos)
    
    def test_memory_usage_with_real_data(self):
        """Test memory usage calculation with real workflow data."""
        paste_data = self._convert_to_paste_format(self.example_data)
        paste_cmd = PasteNodesCommand(self.mock_graph, paste_data, QPointF(0, 0))
        
        memory_usage = paste_cmd.get_memory_usage()
        
        # Should account for all the real code content
        self.assertGreater(memory_usage, 2000)  # Real code is substantial
        self.assertLess(memory_usage, 50000)    # But not excessive
    
    def test_error_handling_with_malformed_data(self):
        """Test error handling when example data is malformed."""
        # Test with missing required fields
        bad_data = {
            'nodes': [
                {'title': 'Bad Node'}  # Missing UUID and other required fields
            ],
            'connections': [
                {'start_node_uuid': 'missing-end'}  # Missing end_node_uuid
            ]
        }
        
        # Should not crash, but may produce warnings
        paste_cmd = PasteNodesCommand(self.mock_graph, bad_data, QPointF(0, 0))
        
        # Verify it handles the malformed data gracefully
        self.assertIsInstance(paste_cmd, CompositeCommand)
        self.assertEqual(len(paste_cmd.commands), 1)  # Should create command for the node
    
    def test_gui_state_preservation_in_paste(self):
        """Test that GUI state from real nodes is preserved during paste."""
        # Get config node with GUI state
        config_node = None
        for node in self.example_data.get('nodes', []):
            if node.get('uuid') == 'config-input':
                config_node = node
                break
        
        self.assertIsNotNone(config_node, "Config node not found")
        
        # Verify GUI state exists
        gui_state = config_node.get('gui_state', {})
        self.assertGreater(len(gui_state), 0, "Config node should have GUI state")
        
        # Expected state from example
        expected_keys = ['length', 'include_uppercase', 'include_lowercase', 'include_numbers', 'include_symbols']
        for key in expected_keys:
            self.assertIn(key, gui_state, f"Missing GUI state key: {key}")


class TestWorkflowEdgeCases(unittest.TestCase):
    """Test edge cases found through real workflow testing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph = Mock()
        self.mock_graph.nodes = []
        self.mock_graph.connections = []
        self.mock_graph.addItem = Mock()
        self.mock_graph.removeItem = Mock()
    
    def test_empty_charset_error_handling(self):
        """Test password generator error case when no character types selected."""
        # This tests the actual logic from the password generator node
        def generate_password_logic(length, include_uppercase, include_lowercase, include_numbers, include_symbols):
            charset = ''
            
            if include_uppercase:
                charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            if include_lowercase:
                charset += 'abcdefghijklmnopqrstuvwxyz'
            if include_numbers:
                charset += '0123456789'
            if include_symbols:
                charset += '!@#$%^&*()_+-=[]{}|;:,.<>?'
            
            if not charset:
                return "Error: No character types selected!"
            
            return "password_would_be_generated"
        
        # Test the error case
        result = generate_password_logic(12, False, False, False, False)
        self.assertEqual(result, "Error: No character types selected!")
        
        # Test normal case
        result = generate_password_logic(12, True, True, True, False)
        self.assertNotEqual(result, "Error: No character types selected!")
    
    def test_strength_analyzer_edge_cases(self):
        """Test password strength analyzer with edge cases."""
        # Simulate the strength analysis logic from the example
        def analyze_strength_logic(password):
            import re
            score = 0
            feedback = []
            
            # Length check
            if len(password) >= 12:
                score += 25
            elif len(password) >= 8:
                score += 15
                feedback.append("Consider using 12+ characters")
            else:
                feedback.append("Password too short (8+ recommended)")
            
            # Character variety
            if re.search(r'[A-Z]', password):
                score += 20
            else:
                feedback.append("Add uppercase letters")
                
            if re.search(r'[a-z]', password):
                score += 20
            else:
                feedback.append("Add lowercase letters")
                
            if re.search(r'[0-9]', password):
                score += 20
            else:
                feedback.append("Add numbers")
                
            if re.search(r'[!@#$%^&*()_+=\[\]{}|;:,.<>?-]', password):
                score += 15
            else:
                feedback.append("Add symbols for extra security")
            
            return score, feedback
        
        # Test edge cases
        score, feedback = analyze_strength_logic("")
        self.assertEqual(score, 0)
        self.assertIn("Password too short", str(feedback))
        
        score, feedback = analyze_strength_logic("a")
        self.assertEqual(score, 20)  # Only lowercase
        
        score, feedback = analyze_strength_logic("Aa1!")
        self.assertEqual(score, 75)  # Short but all types (0+20+20+20+15) - <8 chars gets 0 for length
        
        score, feedback = analyze_strength_logic("AAAAAAAAAAAA")
        self.assertEqual(score, 45)  # Long but only uppercase (25+20)


class TestCommandSystemBugs(unittest.TestCase):
    """Test for bugs discovered through integration testing."""
    
    def test_uuid_mapping_collision_bug(self):
        """Test for UUID collision bug in PasteNodesCommand."""
        mock_graph = Mock()
        
        # Create paste data with missing node IDs (triggers the bug)
        clipboard_data = {
            'nodes': [
                {'title': 'Node 1'},  # Missing 'id' field
                {'title': 'Node 2'}   # Missing 'id' field
            ],
            'connections': []
        }
        
        paste_cmd = PasteNodesCommand(mock_graph, clipboard_data, QPointF(0, 0))
        
        # Both nodes should get unique UUIDs even when original ID is missing
        mapped_uuids = list(paste_cmd.uuid_mapping.values())
        self.assertEqual(len(set(mapped_uuids)), len(mapped_uuids), "UUID collision detected!")
    
    def test_connection_creation_with_missing_pins(self):
        """Test connection creation when pins are missing."""
        mock_graph = Mock()
        mock_graph.nodes = []  # Make it an empty list so it's iterable
        mock_graph.connections = []
        mock_graph.addItem = Mock()
        
        # Create paste data with connections but nodes that might not have the pins
        clipboard_data = {
            'nodes': [
                {'id': 'node1', 'title': 'Node 1', 'code': '', 'description': ''},
                {'id': 'node2', 'title': 'Node 2', 'code': '', 'description': ''}
            ],
            'connections': [
                {
                    'output_node_id': 'node1',
                    'input_node_id': 'node2',
                    'output_pin_name': 'nonexistent_output',
                    'input_pin_name': 'nonexistent_input'
                }
            ]
        }
        
        with patch('src.core.node.Node') as mock_node_class:
            mock_node1 = Mock()
            mock_node1.uuid = 'new-uuid-1'
            mock_node1.get_pin_by_name = Mock(return_value=None)  # Pin not found
            
            mock_node2 = Mock()
            mock_node2.uuid = 'new-uuid-2'
            mock_node2.get_pin_by_name = Mock(return_value=None)  # Pin not found
            
            mock_node_class.side_effect = [mock_node1, mock_node2]
            
            paste_cmd = PasteNodesCommand(mock_graph, clipboard_data, QPointF(0, 0))
            
            # Simulate nodes being added to graph during execute
            def mock_addItem(item):
                if hasattr(item, 'uuid'):
                    mock_graph.nodes.append(item)
            mock_graph.addItem.side_effect = mock_addItem
            
            # Should not crash when executing with missing pins
            try:
                result = paste_cmd.execute()
                # Should succeed for node creation even if connection fails
                self.assertTrue(result)
            except Exception as e:
                self.fail(f"Paste command should handle missing pins gracefully: {e}")


if __name__ == '__main__':
    unittest.main()
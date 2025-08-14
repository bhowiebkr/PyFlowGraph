#!/usr/bin/env python3

"""
Graph Management Tests

Tests the NodeGraph class and graph-level operations including:
- Graph initialization and setup
- Node addition and removal
- Connection management
- Graph serialization and deserialization
- Clipboard operations (copy/paste)
- Graph clearing and cleanup
- Scene management and bounds
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QKeyEvent

from node_graph import NodeGraph
from node import Node
from reroute_node import RerouteNode
from connection import Connection
from pin import Pin


class TestGraphManagement(unittest.TestCase):
    """Test suite for NodeGraph functionality and management."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for the entire test suite."""
        if QApplication.instance() is None:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures before each test."""
        self.graph = NodeGraph()
    
    def tearDown(self):
        """Clean up after each test."""
        self.graph.clear()
    
    def test_graph_initialization(self):
        """Test graph initialization and default properties."""
        graph = NodeGraph()
        
        # Test initial state
        self.assertEqual(len(graph.nodes), 0)
        self.assertEqual(len(graph.connections), 0)
        self.assertIsNone(graph._drag_connection)
        self.assertIsNone(graph._drag_start_pin)
        
        # Test scene properties
        scene_rect = graph.sceneRect()
        self.assertEqual(scene_rect.x(), -10000)
        self.assertEqual(scene_rect.y(), -10000)
        self.assertEqual(scene_rect.width(), 20000)
        self.assertEqual(scene_rect.height(), 20000)
    
    def test_node_creation_and_addition(self):
        """Test creating and adding nodes to the graph."""
        # Test basic node creation
        node = self.graph.create_node("Test Node", pos=(100, 200))
        
        self.assertEqual(node.title, "Test Node")
        self.assertEqual(node.pos().x(), 100)
        self.assertEqual(node.pos().y(), 200)
        self.assertIn(node, self.graph.nodes)
        self.assertIn(node, self.graph.items())
        
        # Test reroute node creation
        reroute = self.graph.create_node("", pos=(50, 50), is_reroute=True)
        
        self.assertIsInstance(reroute, RerouteNode)
        self.assertIn(reroute, self.graph.nodes)
        
        # Test multiple node creation
        node2 = self.graph.create_node("Second Node", pos=(300, 100))
        self.assertEqual(len(self.graph.nodes), 3)  # Including reroute
    
    def test_node_removal(self):
        """Test removing nodes from the graph."""
        # Create test nodes
        node1 = self.graph.create_node("Node 1", pos=(0, 0))
        node2 = self.graph.create_node("Node 2", pos=(200, 0))
        
        # Add some code to create pins
        node1.set_code('''
@node_entry
def test1() -> str:
    return "test"
''')
        
        node2.set_code('''
@node_entry
def test2(input_val: str) -> str:
    return input_val.upper()
''')
        
        # Create connection between nodes
        output_pin = next(p for p in node1.output_pins if p.pin_category == "data")
        input_pin = next(p for p in node2.input_pins if p.pin_category == "data")
        connection = self.graph.create_connection(output_pin, input_pin)
        
        self.assertEqual(len(self.graph.nodes), 2)
        self.assertEqual(len(self.graph.connections), 1)
        
        # Remove node1 - should also remove connection
        self.graph.remove_node(node1)
        
        self.assertEqual(len(self.graph.nodes), 1)
        self.assertEqual(len(self.graph.connections), 0)
        self.assertNotIn(node1, self.graph.items())
        self.assertNotIn(connection, self.graph.items())
    
    def test_connection_creation_and_management(self):
        """Test creating and managing connections between pins."""
        # Create nodes with pins
        node1 = self.graph.create_node("Output Node", pos=(0, 0))
        node2 = self.graph.create_node("Input Node", pos=(300, 0))
        
        node1.set_code('''
@node_entry
def output_func() -> str:
    return "hello"
''')
        
        node2.set_code('''
@node_entry
def input_func(text: str) -> str:
    return text.upper()
''')
        
        # Get pins
        output_pin = next(p for p in node1.output_pins if p.pin_category == "data")
        input_pin = next(p for p in node2.input_pins if p.pin_category == "data")
        
        # Create connection
        connection = self.graph.create_connection(output_pin, input_pin)
        
        self.assertIsInstance(connection, Connection)
        self.assertEqual(connection.start_pin, output_pin)
        self.assertEqual(connection.end_pin, input_pin)
        self.assertIn(connection, self.graph.connections)
        self.assertIn(connection, self.graph.items())
        
        # Test connection removal
        self.graph.remove_connection(connection)
        self.assertNotIn(connection, self.graph.connections)
        self.assertNotIn(connection, self.graph.items())
    
    def test_graph_serialization(self):
        """Test complete graph serialization."""
        # Create a test graph
        node1 = self.graph.create_node("First Node", pos=(100, 100))
        node2 = self.graph.create_node("Second Node", pos=(400, 200))
        
        # Add code to nodes
        node1.set_code('''
@node_entry
def first_func(x: int) -> str:
    return str(x * 2)
''')
        
        node2.set_code('''
@node_entry
def second_func(text: str) -> str:
    return text.upper()
''')
        
        # Create connection
        output_pin = next(p for p in node1.output_pins if p.pin_category == "data")
        input_pin = next(p for p in node2.input_pins if p.pin_category == "data")
        connection = self.graph.create_connection(output_pin, input_pin)
        
        # Serialize graph
        serialized = self.graph.serialize()
        
        # Test serialized structure
        self.assertIn("nodes", serialized)
        self.assertIn("connections", serialized)
        self.assertEqual(len(serialized["nodes"]), 2)
        self.assertEqual(len(serialized["connections"]), 1)
        
        # Test node data
        node_data = serialized["nodes"][0]
        self.assertIn("title", node_data)
        self.assertIn("uuid", node_data)
        self.assertIn("pos", node_data)
        self.assertIn("code", node_data)
        
        # Test connection data
        conn_data = serialized["connections"][0]
        self.assertIn("start_pin_uuid", conn_data)
        self.assertIn("end_pin_uuid", conn_data)
    
    def test_graph_deserialization(self):
        """Test graph reconstruction from serialized data."""
        # Create test data
        test_data = {
            "nodes": [
                {
                    "uuid": "node-1-uuid",
                    "title": "Test Node 1",
                    "pos": [150, 150],
                    "size": [250, 150],
                    "code": '''
@node_entry
def test1() -> int:
    return 42
''',
                    "gui_code": "",
                    "gui_get_values_code": "",
                    "colors": {},
                    "gui_state": {}
                },
                {
                    "uuid": "node-2-uuid",
                    "title": "Test Node 2",
                    "pos": [450, 150],
                    "size": [250, 150],
                    "code": '''
@node_entry
def test2(value: int) -> str:
    return str(value)
''',
                    "gui_code": "",
                    "gui_get_values_code": "",
                    "colors": {},
                    "gui_state": {}
                }
            ],
            "connections": []
        }
        
        # Deserialize
        self.graph.deserialize(test_data)
        
        # Verify nodes were created
        self.assertEqual(len(self.graph.nodes), 2)
        
        # Verify node properties
        node1 = self.graph.nodes[0]
        self.assertEqual(node1.title, "Test Node 1")
        self.assertEqual(node1.uuid, "node-1-uuid")
        self.assertEqual(node1.pos().x(), 150)
        self.assertEqual(node1.pos().y(), 150)
        
        # Verify pins were created from code
        self.assertGreater(len(node1.output_pins), 0)
        
        node2 = self.graph.nodes[1]
        self.assertGreater(len(node2.input_pins), 0)
    
    def test_graph_clear(self):
        """Test clearing the entire graph."""
        # Create test content
        node1 = self.graph.create_node("Node 1", pos=(0, 0))
        node2 = self.graph.create_node("Node 2", pos=(200, 0))
        reroute = self.graph.create_node("", pos=(100, 100), is_reroute=True)
        
        # Add code and connections
        node1.set_code('''
@node_entry
def test() -> str:
    return "test"
''')
        
        node2.set_code('''
@node_entry
def receive(text: str):
    print(text)
''')
        
        # Create connections
        output_pin = next(p for p in node1.output_pins if p.pin_category == "data")
        input_pin = next(p for p in node2.input_pins if p.pin_category == "data")
        conn = self.graph.create_connection(output_pin, input_pin)
        
        # Verify content exists
        self.assertEqual(len(self.graph.nodes), 3)
        self.assertEqual(len(self.graph.connections), 1)
        self.assertGreater(len(self.graph.items()), 0)
        
        # Clear graph
        self.graph.clear_graph()
        
        # Verify everything is cleared
        self.assertEqual(len(self.graph.nodes), 0)
        self.assertEqual(len(self.graph.connections), 0)
        # Scene items should only contain background items
        remaining_items = [item for item in self.graph.items() 
                          if not isinstance(item, (Node, RerouteNode, Connection))]
        self.assertEqual(len(self.graph.items()), len(remaining_items))
    
    def test_clipboard_operations(self):
        """Test copy and paste functionality."""
        # Create test nodes
        node1 = self.graph.create_node("Copy Node 1", pos=(100, 100))
        node2 = self.graph.create_node("Copy Node 2", pos=(300, 100))
        
        node1.set_code('''
@node_entry
def copy_test() -> str:
    return "copied"
''')
        
        node2.set_code('''
@node_entry
def paste_test(text: str) -> str:
    return text + " pasted"
''')
        
        # Create connection
        output_pin = next(p for p in node1.output_pins if p.pin_category == "data")
        input_pin = next(p for p in node2.input_pins if p.pin_category == "data")
        self.graph.create_connection(output_pin, input_pin)
        
        # Select nodes
        node1.setSelected(True)
        node2.setSelected(True)
        
        # Test copy
        with patch('PySide6.QtWidgets.QApplication.clipboard') as mock_clipboard:
            mock_clipboard_instance = Mock()
            mock_clipboard.return_value = mock_clipboard_instance
            
            self.graph.copy_selected()
            
            # Should have called setText with JSON data
            mock_clipboard_instance.setText.assert_called_once()
            args = mock_clipboard_instance.setText.call_args[0]
            clipboard_data = json.loads(args[0])
            
            self.assertIn("nodes", clipboard_data)
            self.assertIn("connections", clipboard_data)
            self.assertEqual(len(clipboard_data["nodes"]), 2)
            self.assertEqual(len(clipboard_data["connections"]), 1)
    
    def test_keyboard_deletion(self):
        """Test keyboard deletion of selected items."""
        # Create test content
        node1 = self.graph.create_node("Delete Node", pos=(0, 0))
        node2 = self.graph.create_node("Keep Node", pos=(200, 0))
        
        node1.set_code('''
@node_entry
def delete_me() -> str:
    return "delete"
''')
        
        node2.set_code('''
@node_entry
def keep_me(text: str):
    print(text)
''')
        
        # Create connection
        output_pin = next(p for p in node1.output_pins if p.pin_category == "data")
        input_pin = next(p for p in node2.input_pins if p.pin_category == "data")
        connection = self.graph.create_connection(output_pin, input_pin)
        
        # Select node1 and connection
        node1.setSelected(True)
        connection.setSelected(True)
        
        # Simulate delete key press
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        self.graph.keyPressEvent(delete_event)
        
        # Should remove selected node and connection
        self.assertNotIn(node1, self.graph.nodes)
        self.assertNotIn(connection, self.graph.connections)
        self.assertIn(node2, self.graph.nodes)  # Should keep unselected node
    
    def test_reroute_node_creation_on_connection(self):
        """Test creating reroute nodes by double-clicking connections."""
        # Create nodes and connection
        node1 = self.graph.create_node("Start", pos=(0, 0))
        node2 = self.graph.create_node("End", pos=(400, 0))
        
        node1.set_code('''
@node_entry
def start() -> str:
    return "start"
''')
        
        node2.set_code('''
@node_entry
def end(text: str):
    print(text)
''')
        
        output_pin = next(p for p in node1.output_pins if p.pin_category == "data")
        input_pin = next(p for p in node2.input_pins if p.pin_category == "data")
        original_connection = self.graph.create_connection(output_pin, input_pin)
        
        # Test reroute creation
        reroute_pos = QPointF(200, 0)
        self.graph.create_reroute_node_on_connection(original_connection, reroute_pos)
        
        # Should have created a reroute node
        reroute_nodes = [n for n in self.graph.nodes if isinstance(n, RerouteNode)]
        self.assertEqual(len(reroute_nodes), 1)
        
        reroute = reroute_nodes[0]
        self.assertEqual(reroute.pos(), reroute_pos)
        
        # Original connection should be removed, new connections created
        self.assertNotIn(original_connection, self.graph.connections)
        self.assertEqual(len(self.graph.connections), 2)  # Two new connections through reroute
    
    def test_graph_bounds_and_scene_management(self):
        """Test graph scene bounds and management."""
        # Create nodes at various positions
        node1 = self.graph.create_node("Center", pos=(0, 0))
        node2 = self.graph.create_node("Far Right", pos=(5000, 0))
        node3 = self.graph.create_node("Far Down", pos=(0, 5000))
        
        # All nodes should be within scene bounds
        scene_rect = self.graph.sceneRect()
        
        for node in [node1, node2, node3]:
            node_pos = node.pos()
            self.assertTrue(scene_rect.contains(node_pos))
    
    def test_graph_selection_management(self):
        """Test selection and multi-selection functionality."""
        # Create multiple nodes
        nodes = []
        for i in range(3):
            node = self.graph.create_node(f"Node {i}", pos=(i * 200, 0))
            nodes.append(node)
        
        # Test individual selection
        nodes[0].setSelected(True)
        selected_items = self.graph.selectedItems()
        self.assertEqual(len(selected_items), 1)
        self.assertIn(nodes[0], selected_items)
        
        # Test multi-selection
        nodes[1].setSelected(True)
        nodes[2].setSelected(True)
        selected_items = self.graph.selectedItems()
        self.assertEqual(len(selected_items), 3)
        
        # Test deselection
        for node in nodes:
            node.setSelected(False)
        selected_items = self.graph.selectedItems()
        self.assertEqual(len(selected_items), 0)


def run_graph_management_tests():
    """Run all graph management tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGraphManagement)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_graph_management_tests()
    
    # Clean up QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
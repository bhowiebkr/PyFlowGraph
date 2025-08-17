#!/usr/bin/env python3

"""
Connection System Tests

Tests the Connection class and connection management functionality including:
- Connection creation between pins
- Bezier curve path generation and updates
- Connection serialization and deserialization
- Reroute node integration
- Connection validation and constraints
- Visual connection properties
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainterPath

from core.connection import Connection
from core.pin import Pin
from core.node import Node
from core.reroute_node import RerouteNode
from core.node_graph import NodeGraph


class TestConnectionSystem(unittest.TestCase):
    """Test suite for Connection functionality and management."""
    
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
        
        # Create test nodes
        self.node1 = Node("Output Node")
        self.node2 = Node("Input Node")
        self.graph.addItem(self.node1)
        self.graph.addItem(self.node2)
        
        # Position nodes for testing
        self.node1.setPos(0, 0)
        self.node2.setPos(300, 0)
        
        # Create test pins
        self.output_pin = Pin(
            node=self.node1,
            name="output",
            direction="output",
            pin_type_str="str",
            pin_category="data"
        )
        
        self.input_pin = Pin(
            node=self.node2,
            name="input",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
    
    def tearDown(self):
        """Clean up after each test."""
        self.graph.clear()
    
    def test_connection_creation(self):
        """Test basic connection creation between two pins."""
        connection = Connection(self.output_pin, self.input_pin)
        
        # Test basic properties
        self.assertEqual(connection.start_pin, self.output_pin)
        self.assertEqual(connection.end_pin, self.input_pin)
        
        # Test that connection was added to pins
        self.assertIn(connection, self.output_pin.connections)
        self.assertIn(connection, self.input_pin.connections)
        
        # Test visual properties
        self.assertIsInstance(connection.color, QColor)
        self.assertEqual(connection.color, self.output_pin.color)
        
        # Test Z-value for proper layering
        self.assertEqual(connection.zValue(), -1)
    
    def test_connection_path_generation(self):
        """Test bezier curve path generation."""
        connection = Connection(self.output_pin, self.input_pin)
        
        # Connection should have a valid path
        path = connection.path()
        self.assertIsInstance(path, QPainterPath)
        self.assertFalse(path.isEmpty())
        
        # Path should start and end at pin positions
        start_pos = self.output_pin.get_scene_pos()
        end_pos = self.input_pin.get_scene_pos()
        
        # Verify path starts near output pin
        path_start = path.pointAtPercent(0)
        self.assertLess(abs(path_start.x() - start_pos.x()), 10)
        self.assertLess(abs(path_start.y() - start_pos.y()), 10)
        
        # Verify path ends near input pin
        path_end = path.pointAtPercent(1)
        self.assertLess(abs(path_end.x() - end_pos.x()), 10)
        self.assertLess(abs(path_end.y() - end_pos.y()), 10)
    
    def test_connection_color_inheritance(self):
        """Test that connections inherit color from source pin."""
        # Test with different pin types and colors
        int_output = Pin(
            node=self.node1,
            name="int_output",
            direction="output",
            pin_type_str="int",
            pin_category="data"
        )
        
        int_input = Pin(
            node=self.node2,
            name="int_input",
            direction="input",
            pin_type_str="int",
            pin_category="data"
        )
        
        connection = Connection(int_output, int_input)
        
        # Connection should inherit color from output pin
        self.assertEqual(connection.color, int_output.color)
        
        # Test with execution pins
        exec_output = Pin(
            node=self.node1,
            name="exec_out",
            direction="output",
            pin_type_str="exec",
            pin_category="execution"
        )
        
        exec_input = Pin(
            node=self.node2,
            name="exec_in",
            direction="input",
            pin_type_str="exec",
            pin_category="execution"
        )
        
        exec_connection = Connection(exec_output, exec_input)
        self.assertEqual(exec_connection.color, exec_output.color)
    
    def test_connection_update_path(self):
        """Test connection path updates when pins move."""
        connection = Connection(self.output_pin, self.input_pin)
        original_path = connection.path()
        
        # Move the output node
        self.node1.setPos(100, 100)
        
        # Update connection path
        connection.update_path()
        updated_path = connection.path()
        
        # Path should be different after node movement
        self.assertNotEqual(original_path.pointAtPercent(0), updated_path.pointAtPercent(0))
    
    def test_connection_serialization(self):
        """Test connection serialization to dictionary format."""
        connection = Connection(self.output_pin, self.input_pin)
        
        serialized = connection.serialize()
        
        # Test required fields
        self.assertIn("start_pin_uuid", serialized)
        self.assertIn("end_pin_uuid", serialized)
        self.assertIn("start_node_uuid", serialized)
        self.assertIn("end_node_uuid", serialized)
        
        # Test UUIDs match pins and nodes
        self.assertEqual(serialized["start_pin_uuid"], self.output_pin.uuid)
        self.assertEqual(serialized["end_pin_uuid"], self.input_pin.uuid)
        self.assertEqual(serialized["start_node_uuid"], self.node1.uuid)
        self.assertEqual(serialized["end_node_uuid"], self.node2.uuid)
    
    def test_connection_destruction(self):
        """Test proper connection cleanup and removal."""
        connection = Connection(self.output_pin, self.input_pin)
        
        # Verify connection is in pin lists
        self.assertIn(connection, self.output_pin.connections)
        self.assertIn(connection, self.input_pin.connections)
        
        # Test destruction
        connection.destroy()
        
        # Connection should be removed from pins
        self.assertNotIn(connection, self.output_pin.connections)
        self.assertNotIn(connection, self.input_pin.connections)
    
    def test_connection_with_reroute_node(self):
        """Test connections involving reroute nodes."""
        # Create a reroute node
        reroute = RerouteNode()
        reroute.setPos(150, 0)
        self.graph.addItem(reroute)
        
        # Connect output to reroute
        conn1 = Connection(self.output_pin, reroute.input_pin)
        
        # Connect reroute to input
        conn2 = Connection(reroute.output_pin, self.input_pin)
        
        # Test that connections are valid
        self.assertEqual(conn1.start_pin, self.output_pin)
        self.assertEqual(conn1.end_pin, reroute.input_pin)
        self.assertEqual(conn2.start_pin, reroute.output_pin)
        self.assertEqual(conn2.end_pin, self.input_pin)
        
        # Test serialization with reroute nodes
        serialized1 = conn1.serialize()
        serialized2 = conn2.serialize()
        
        self.assertIsNotNone(serialized1)
        self.assertIsNotNone(serialized2)
    
    def test_connection_validation(self):
        """Test connection validation and constraints."""
        # Test valid connection (compatible types)
        valid_connection = Connection(self.output_pin, self.input_pin)
        self.assertIsNotNone(valid_connection)
        
        # Test invalid connection (incompatible types)
        int_input = Pin(
            node=self.node2,
            name="int_input",
            direction="input",
            pin_type_str="int",
            pin_category="data"
        )
        
        # This should still create a connection (validation might be handled elsewhere)
        # but we can test the type mismatch
        invalid_connection = Connection(self.output_pin, int_input)
        self.assertNotEqual(self.output_pin.pin_type, int_input.pin_type)
        
        # Test connection between same direction pins (should be invalid)
        output2 = Pin(
            node=self.node2,
            name="output2",
            direction="output",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Same direction connection
        same_direction_conn = Connection(self.output_pin, output2)
        # Should still create but be logically invalid
        self.assertEqual(self.output_pin.direction, output2.direction)
    
    def test_connection_selection_visual_feedback(self):
        """Test connection selection and visual feedback."""
        connection = Connection(self.output_pin, self.input_pin)
        
        # Test selection
        connection.setSelected(True)
        self.assertTrue(connection.isSelected())
        
        # Selection should affect pen width
        selected_pen = connection.pen()
        connection.setSelected(False)
        normal_pen = connection.pen()
        
        # Different pen properties for selection
        self.assertNotEqual(selected_pen.width(), normal_pen.width())
    
    def test_connection_temporary_mode(self):
        """Test temporary connection creation during dragging."""
        # Create a temporary connection with no end pin
        temp_connection = Connection(self.output_pin, None)
        
        self.assertEqual(temp_connection.start_pin, self.output_pin)
        self.assertIsNone(temp_connection.end_pin)
        
        # Set temporary end position
        temp_pos = QPointF(200, 100)
        temp_connection.set_end_pos(temp_pos)
        
        # Path should update to use temporary position
        path = temp_connection.path()
        self.assertFalse(path.isEmpty())
    
    def test_connection_double_click_reroute(self):
        """Test double-click creation of reroute nodes."""
        connection = Connection(self.output_pin, self.input_pin)
        self.graph.addItem(connection)
        
        # Mock the scene method for creating reroute nodes
        with patch.object(self.graph, 'create_reroute_node_on_connection') as mock_create:
            # Simulate double-click event
            from PySide6.QtGui import QMouseEvent
            from PySide6.QtCore import Qt
            
            click_pos = QPointF(150, 0)
            event = Mock()
            event.scenePos.return_value = click_pos
            
            connection.mouseDoubleClickEvent(event)
            
            # Should call reroute creation
            mock_create.assert_called_once_with(connection, click_pos)
    
    def test_multiple_connections_on_pin(self):
        """Test multiple connections on a single pin."""
        # Create additional nodes and pins
        node3 = Node("Third Node")
        self.graph.addItem(node3)
        
        input2 = Pin(
            node=node3,
            name="input2",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Create multiple connections from same output
        conn1 = Connection(self.output_pin, self.input_pin)
        conn2 = Connection(self.output_pin, input2)
        
        # Output pin should have multiple connections
        self.assertEqual(len(self.output_pin.connections), 2)
        self.assertIn(conn1, self.output_pin.connections)
        self.assertIn(conn2, self.output_pin.connections)
        
        # Each input should have one connection
        self.assertEqual(len(self.input_pin.connections), 1)
        self.assertEqual(len(input2.connections), 1)
    
    def test_connection_path_curve_properties(self):
        """Test bezier curve mathematical properties."""
        connection = Connection(self.output_pin, self.input_pin)
        
        # Test that path has proper bezier curve characteristics
        path = connection.path()
        
        # Should have control points for smooth curves
        # Path should be smooth between start and end
        start_point = path.pointAtPercent(0)
        mid_point = path.pointAtPercent(0.5)
        end_point = path.pointAtPercent(1)
        
        # Middle point should be between start and end (roughly)
        self.assertGreater(mid_point.x(), start_point.x())
        self.assertLess(mid_point.x(), end_point.x())
    
    def test_connection_graph_integration(self):
        """Test connection integration with graph management."""
        connection = Connection(self.output_pin, self.input_pin)
        
        # Add connection to graph
        self.graph.connections.append(connection)
        self.graph.addItem(connection)
        
        # Test that connection is tracked by graph
        self.assertIn(connection, self.graph.connections)
        self.assertIn(connection, self.graph.items())
        
        # Test removal through graph
        self.graph.remove_connection(connection)
        self.assertNotIn(connection, self.graph.connections)


def run_connection_system_tests():
    """Run all connection system tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestConnectionSystem)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_connection_system_tests()
    
    # Clean up QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
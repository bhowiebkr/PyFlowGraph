#!/usr/bin/env python3

"""
Pin System Tests

Tests the Pin class and pin management functionality including:
- Pin creation and initialization
- Pin type detection and color assignment
- Pin positioning and label management
- Data vs execution pin handling
- Pin connection compatibility
- Pin serialization
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
from PySide6.QtGui import QColor

from core.pin import Pin
from core.node import Node
from core.node_graph import NodeGraph
from utils.color_utils import generate_color_from_string


class TestPinSystem(unittest.TestCase):
    """Test suite for Pin functionality and management."""
    
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
        self.node = Node("Test Node")
        self.graph.addItem(self.node)
    
    def tearDown(self):
        """Clean up after each test."""
        self.graph.clear()
    
    def test_pin_creation(self):
        """Test basic pin creation and initialization."""
        pin = Pin(
            node=self.node,
            name="test_pin",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Test basic properties
        self.assertEqual(pin.node, self.node)
        self.assertEqual(pin.name, "test_pin")
        self.assertEqual(pin.direction, "input")
        self.assertEqual(pin.pin_type, "str")
        self.assertEqual(pin.pin_category, "data")
        
        # Test UUID generation
        self.assertIsNotNone(pin.uuid)
        self.assertEqual(len(pin.uuid.split('-')), 5)  # Valid UUID format
        
        # Test initial state
        self.assertEqual(len(pin.connections), 0)
        self.assertIsNone(pin.value)
        self.assertEqual(pin.radius, 6)
    
    def test_execution_pin_creation(self):
        """Test creation of execution pins with proper styling."""
        exec_pin = Pin(
            node=self.node,
            name="exec_in",
            direction="input",
            pin_type_str="exec",
            pin_category="execution"
        )
        
        self.assertEqual(exec_pin.pin_category, "execution")
        self.assertEqual(exec_pin.pin_type, "exec")
        
        # Execution pins should have specific colors
        self.assertIsInstance(exec_pin.color, QColor)
        # Input execution pins should be gray-ish
        self.assertEqual(exec_pin.color, QColor("#A0A0A0"))
        
        # Test output execution pin
        exec_out = Pin(
            node=self.node,
            name="exec_out", 
            direction="output",
            pin_type_str="exec",
            pin_category="execution"
        )
        
        # Output execution pins should be lighter
        self.assertEqual(exec_out.color, QColor("#E0E0E0"))
    
    def test_data_pin_type_colors(self):
        """Test that data pins get colors based on their types."""
        # Test common data types
        test_types = ["int", "str", "float", "bool", "list", "dict"]
        
        for pin_type in test_types:
            pin = Pin(
                node=self.node,
                name=f"test_{pin_type}",
                direction="input",
                pin_type_str=pin_type,
                pin_category="data"
            )
            
            # Should have a color generated from the type string
            expected_color = generate_color_from_string(pin_type)
            self.assertEqual(pin.color, expected_color)
            self.assertIsInstance(pin.color, QColor)
    
    def test_pin_label_formatting(self):
        """Test pin label text formatting and positioning."""
        # Test underscore replacement and title case
        pin = Pin(
            node=self.node,
            name="input_value_test",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Label should replace underscores and use title case
        expected_label = "Input Value Test"
        self.assertEqual(pin.label.toPlainText(), expected_label)
        
        # Test label positioning for input pin
        pin.update_label_pos()
        label_pos = pin.label.pos()
        self.assertGreater(label_pos.x(), 0)  # Input labels should be to the right
        
        # Test output pin label positioning
        output_pin = Pin(
            node=self.node,
            name="output_result",
            direction="output",
            pin_type_str="str",
            pin_category="data"
        )
        
        output_pin.update_label_pos()
        output_label_pos = output_pin.label.pos()
        self.assertLess(output_label_pos.x(), 0)  # Output labels should be to the left
    
    def test_pin_scene_position(self):
        """Test pin scene position calculation."""
        pin = Pin(
            node=self.node,
            name="position_test",
            direction="input",
            pin_type_str="int",
            pin_category="data"
        )
        
        # Set node position
        self.node.setPos(100, 200)
        
        # Pin should report scene position relative to node
        scene_pos = pin.get_scene_pos()
        self.assertIsInstance(scene_pos, QPointF)
        
        # Scene position should be offset from node position
        self.assertGreaterEqual(scene_pos.x(), 100)
        self.assertGreaterEqual(scene_pos.y(), 200)
    
    def test_pin_connection_management(self):
        """Test pin connection tracking."""
        pin1 = Pin(
            node=self.node,
            name="output_pin",
            direction="output",
            pin_type_str="str",
            pin_category="data"
        )
        
        pin2 = Pin(
            node=self.node,
            name="input_pin",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Mock connection object
        mock_connection = Mock()
        
        # Test adding connections
        pin1.add_connection(mock_connection)
        pin2.add_connection(mock_connection)
        
        self.assertIn(mock_connection, pin1.connections)
        self.assertIn(mock_connection, pin2.connections)
        self.assertEqual(len(pin1.connections), 1)
        self.assertEqual(len(pin2.connections), 1)
        
        # Test removing connections
        pin1.remove_connection(mock_connection)
        self.assertNotIn(mock_connection, pin1.connections)
        self.assertEqual(len(pin1.connections), 0)
    
    def test_pin_type_compatibility(self):
        """Test pin type compatibility for connections."""
        # Same type should be compatible
        str_pin1 = Pin(
            node=self.node,
            name="str1",
            direction="output",
            pin_type_str="str",
            pin_category="data"
        )
        
        str_pin2 = Pin(
            node=self.node,
            name="str2",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Should be able to connect same types
        self.assertTrue(str_pin1.can_connect_to(str_pin2))
        
        # Different types should not be compatible
        int_pin = Pin(
            node=self.node,
            name="int_pin",
            direction="input",
            pin_type_str="int",
            pin_category="data"
        )
        
        self.assertFalse(str_pin1.can_connect_to(int_pin))
        
        # Execution pins should only connect to execution pins
        exec_pin = Pin(
            node=self.node,
            name="exec_pin",
            direction="input",
            pin_type_str="exec",
            pin_category="execution"
        )
        
        self.assertFalse(str_pin1.can_connect_to(exec_pin))
        self.assertFalse(exec_pin.can_connect_to(str_pin1))
    
    def test_pin_direction_constraints(self):
        """Test that pins enforce direction constraints."""
        output_pin = Pin(
            node=self.node,
            name="output",
            direction="output",
            pin_type_str="str",
            pin_category="data"
        )
        
        input_pin = Pin(
            node=self.node,
            name="input",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Output to input should be valid
        self.assertTrue(output_pin.can_connect_to(input_pin))
        
        # Input to output should be invalid
        self.assertFalse(input_pin.can_connect_to(output_pin))
        
        # Same direction should be invalid
        output_pin2 = Pin(
            node=self.node,
            name="output2",
            direction="output",
            pin_type_str="str",
            pin_category="data"
        )
        
        self.assertFalse(output_pin.can_connect_to(output_pin2))
    
    def test_pin_value_storage(self):
        """Test pin value storage and retrieval."""
        pin = Pin(
            node=self.node,
            name="value_test",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Initial value should be None
        self.assertIsNone(pin.value)
        
        # Test setting and getting values
        test_value = "Hello World"
        pin.value = test_value
        self.assertEqual(pin.value, test_value)
        
        # Test different value types
        pin.value = 42
        self.assertEqual(pin.value, 42)
        
        pin.value = [1, 2, 3]
        self.assertEqual(pin.value, [1, 2, 3])
    
    def test_pin_destruction(self):
        """Test proper pin cleanup and destruction."""
        pin = Pin(
            node=self.node,
            name="destroy_test",
            direction="input",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Add pin to scene
        self.graph.addItem(pin)
        self.assertIn(pin, self.graph.items())
        
        # Test destruction
        pin.destroy()
        
        # Pin should be removed from scene
        self.assertNotIn(pin, self.graph.items())
    
    def test_complex_pin_types(self):
        """Test pins with complex type annotations."""
        from typing import List, Dict, Optional, Union, Tuple
        
        # Test generic types
        complex_types = [
            "List[str]",
            "Dict[str, int]", 
            "Optional[str]",
            "Union[int, str]",
            "Tuple[int, str, bool]"
        ]
        
        for pin_type in complex_types:
            pin = Pin(
                node=self.node,
                name=f"complex_{pin_type.lower().replace('[', '_').replace(']', '').replace(',', '_').replace(' ', '')}",
                direction="input",
                pin_type_str=pin_type,
                pin_category="data"
            )
            
            # Should still generate a color for complex types
            self.assertIsInstance(pin.color, QColor)
            self.assertEqual(pin.pin_type, pin_type)
    
    def test_pin_with_node_integration(self):
        """Test pin integration with node pin generation."""
        # Test that pins are properly added to node when created through node.set_code
        code = '''
from typing import Tuple

@node_entry
def test_function(input_a: int, input_b: str) -> Tuple[str, int]:
    return input_b.upper(), input_a * 2
'''
        
        self.node.set_code(code)
        
        # Check that pins were created and added to node
        self.assertGreater(len(self.node.pins), 0)
        self.assertGreater(len(self.node.input_pins), 0)
        self.assertGreater(len(self.node.output_pins), 0)
        
        # Check that specific pins exist
        input_names = [pin.name for pin in self.node.input_pins]
        output_names = [pin.name for pin in self.node.output_pins]
        
        self.assertIn("input_a", input_names)
        self.assertIn("input_b", input_names)
        self.assertIn("output_1", output_names)
        self.assertIn("output_2", output_names)
        
        # Check pin types are correct
        input_a_pin = next(p for p in self.node.input_pins if p.name == "input_a")
        input_b_pin = next(p for p in self.node.input_pins if p.name == "input_b")
        
        self.assertEqual(input_a_pin.pin_type, "int")
        self.assertEqual(input_b_pin.pin_type, "str")
    
    def test_pin_update_connections(self):
        """Test pin connection update mechanism."""
        pin = Pin(
            node=self.node,
            name="update_test",
            direction="output",
            pin_type_str="str",
            pin_category="data"
        )
        
        # Mock connections
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        
        pin.add_connection(mock_conn1)
        pin.add_connection(mock_conn2)
        
        # Test connection updates
        pin.update_connections()
        
        # Should call update on all connections
        mock_conn1.update_path.assert_called()
        mock_conn2.update_path.assert_called()


def run_pin_system_tests():
    """Run all pin system tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPinSystem)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_pin_system_tests()
    
    # Clean up QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
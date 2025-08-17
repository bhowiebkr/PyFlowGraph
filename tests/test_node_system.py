#!/usr/bin/env python3

"""
Core Node System Tests

Tests the fundamental Node class functionality including:
- Node creation and initialization
- Property management (title, colors, dimensions)
- Code management and storage
- Serialization and deserialization
- Pin generation from function signatures
- Node resizing and visual properties
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor

from core.node import Node
from core.node_graph import NodeGraph


class TestNodeSystem(unittest.TestCase):
    """Test suite for core Node functionality."""
    
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
        self.test_title = "Test Node"
        self.node = Node(self.test_title)
        self.graph.addItem(self.node)
    
    def tearDown(self):
        """Clean up after each test."""
        self.graph.clear()
    
    def test_node_creation(self):
        """Test basic node creation and initialization."""
        node = Node("Test Node")
        
        # Test basic properties
        self.assertEqual(node.title, "Test Node")
        self.assertIsNotNone(node.uuid)
        self.assertEqual(len(node.uuid.split('-')), 5)  # Valid UUID format
        
        # Test default dimensions
        self.assertEqual(node.base_width, 250)
        self.assertEqual(node.width, 250)
        self.assertEqual(node.height, 150)
        
        # Test initial pin lists
        self.assertEqual(len(node.pins), 0)
        self.assertEqual(len(node.input_pins), 0)
        self.assertEqual(len(node.output_pins), 0)
        
        # Test initial code storage
        self.assertEqual(node.code, "")
        self.assertEqual(node.gui_code, "")
        self.assertEqual(node.gui_get_values_code, "")
        self.assertIsNone(node.function_name)
    
    def test_node_properties_modification(self):
        """Test modification of node properties."""
        node = Node("Original Title")
        
        # Test title modification
        node.title = "Modified Title"
        self.assertEqual(node.title, "Modified Title")
        
        # Test dimension modification
        node.width = 300
        node.height = 200
        self.assertEqual(node.width, 300)
        self.assertEqual(node.height, 200)
        
        # Test color modification
        new_color = QColor(255, 0, 0)
        node.color_body = new_color
        self.assertEqual(node.color_body, new_color)
    
    def test_code_management(self):
        """Test node code setting and management."""
        node = Node("Code Node")
        
        # Test setting basic code
        test_code = '''
def test_function(x: int) -> str:
    return str(x * 2)
'''
        node.set_code(test_code)
        self.assertEqual(node.code, test_code)
        
        # Test function name extraction
        self.assertEqual(node.function_name, "test_function")
    
    def test_pin_generation_from_code(self):
        """Test automatic pin generation from function signatures."""
        node = Node("Pin Generation Test")
        
        # Test simple function with one input and one output
        simple_code = '''
@node_entry
def simple_func(value: int) -> str:
    return str(value)
'''
        node.set_code(simple_code)
        
        # Should have input pins: exec_in, value
        # Should have output pins: exec_out, output_1
        input_pin_names = [pin.name for pin in node.input_pins]
        output_pin_names = [pin.name for pin in node.output_pins]
        
        self.assertIn("value", input_pin_names)
        self.assertIn("output_1", output_pin_names)
        
        # Test multiple inputs and outputs (tuple return)
        complex_code = '''
from typing import Tuple

@node_entry
def complex_func(a: int, b: str, c: float) -> Tuple[int, str, bool]:
    return a * 2, b.upper(), a > 5
'''
        node.set_code(complex_code)
        
        input_pin_names = [pin.name for pin in node.input_pins]
        output_pin_names = [pin.name for pin in node.output_pins]
        
        # Check input pins
        self.assertIn("a", input_pin_names)
        self.assertIn("b", input_pin_names)
        self.assertIn("c", input_pin_names)
        
        # Check output pins (tuple creates multiple outputs)
        self.assertIn("output_1", output_pin_names)
        self.assertIn("output_2", output_pin_names)
        self.assertIn("output_3", output_pin_names)
    
    def test_execution_pins(self):
        """Test that execution pins are properly created."""
        node = Node("Execution Test")
        
        code_with_entry = '''
@node_entry
def test_func(x: int) -> int:
    return x + 1
'''
        node.set_code(code_with_entry)
        
        # Check for execution pins
        exec_input_pins = [p for p in node.input_pins if p.pin_category == "execution"]
        exec_output_pins = [p for p in node.output_pins if p.pin_category == "execution"]
        
        self.assertEqual(len(exec_input_pins), 1)
        self.assertEqual(len(exec_output_pins), 1)
        self.assertEqual(exec_input_pins[0].name, "exec_in")
        self.assertEqual(exec_output_pins[0].name, "exec_out")
    
    def test_node_serialization(self):
        """Test node serialization to dictionary format."""
        node = Node("Serialize Test")
        node.setPos(100, 200)
        node.width = 300
        node.height = 180
        
        # Set some code
        test_code = '''
@node_entry
def serialize_test(input_val: str) -> str:
    return input_val.upper()
'''
        node.set_code(test_code)
        
        # Serialize the node
        serialized = node.serialize()
        
        # Verify serialized data
        self.assertEqual(serialized["title"], "Serialize Test")
        self.assertEqual(serialized["uuid"], node.uuid)
        self.assertEqual(serialized["pos"], [100, 200])
        self.assertEqual(serialized["size"], [300, 180])
        self.assertEqual(serialized["code"], test_code)
        self.assertIn("colors", serialized)
    
    def test_node_deserialization(self):
        """Test node reconstruction from serialized data."""
        # Create test data
        test_data = {
            "uuid": "test-uuid-12345",
            "title": "Deserialized Node",
            "pos": [150, 250],
            "size": [400, 220],
            "code": '''
@node_entry
def deserialize_test(x: int) -> int:
    return x * 3
''',
            "gui_code": "",
            "gui_get_values_code": "",
            "colors": {
                "title": "#FF0000",
                "body": "#00FF00"
            },
            "gui_state": {}
        }
        
        # Create node from graph (simulates deserialization)
        node = self.graph.create_node(test_data["title"], pos=test_data["pos"])
        node.uuid = test_data["uuid"]
        node.set_code(test_data["code"])
        node.width, node.height = test_data["size"]
        
        # Verify properties were restored
        self.assertEqual(node.title, "Deserialized Node")
        self.assertEqual(node.uuid, "test-uuid-12345")
        self.assertEqual(node.width, 400)
        self.assertEqual(node.height, 220)
        self.assertIn("deserialize_test", node.code)
    
    def test_pin_type_detection(self):
        """Test that pin types are correctly detected from function signatures."""
        node = Node("Type Detection Test")
        
        # Test various Python types
        typed_code = '''
from typing import List, Dict, Optional

@node_entry
def type_test(
    int_val: int,
    str_val: str,
    float_val: float,
    bool_val: bool,
    list_val: List[str],
    dict_val: Dict[str, int],
    optional_val: Optional[str]
) -> Tuple[int, str, bool]:
    return 42, "test", True
'''
        node.set_code(typed_code)
        
        # Check that pins were created for each parameter
        input_names = [pin.name for pin in node.input_pins if pin.pin_category == "data"]
        expected_inputs = ["int_val", "str_val", "float_val", "bool_val", 
                          "list_val", "dict_val", "optional_val"]
        
        for expected in expected_inputs:
            self.assertIn(expected, input_names)
        
        # Check pin types are correctly assigned
        pin_types = {pin.name: pin.pin_type for pin in node.input_pins if pin.pin_category == "data"}
        self.assertEqual(pin_types["int_val"], "int")
        self.assertEqual(pin_types["str_val"], "str")
        self.assertEqual(pin_types["float_val"], "float")
        self.assertEqual(pin_types["bool_val"], "bool")
    
    def test_node_gui_code_management(self):
        """Test GUI code setting and management."""
        node = Node("GUI Test Node")
        
        # Test setting GUI code
        gui_code = '''
from PySide6.QtWidgets import QLabel, QLineEdit

widgets['label'] = QLabel('Input:', parent)
layout.addWidget(widgets['label'])

widgets['input'] = QLineEdit(parent)
layout.addWidget(widgets['input'])
'''
        node.set_gui_code(gui_code)
        self.assertEqual(node.gui_code, gui_code)
        
        # Test setting GUI get values code
        get_values_code = '''
def get_values(widgets):
    return {'input_value': widgets['input'].text()}
'''
        node.set_gui_get_values_code(get_values_code)
        self.assertEqual(node.gui_get_values_code, get_values_code)
    
    def test_node_visual_properties(self):
        """Test node visual property management."""
        node = Node("Visual Test")
        
        # Test default colors are set
        self.assertIsInstance(node.color_body, QColor)
        self.assertIsInstance(node.color_title_bar, QColor)
        self.assertIsInstance(node.color_title_text, QColor)
        self.assertIsInstance(node.color_border, QColor)
        
        # Test color modification
        new_body_color = QColor(100, 150, 200)
        node.color_body = new_body_color
        self.assertEqual(node.color_body, new_body_color)
    
    def test_node_position_management(self):
        """Test node positioning and movement."""
        node = Node("Position Test")
        
        # Test initial position (should be 0,0)
        initial_pos = node.pos()
        self.assertEqual(initial_pos.x(), 0)
        self.assertEqual(initial_pos.y(), 0)
        
        # Test position setting
        new_pos = QPointF(100, 200)
        node.setPos(new_pos)
        self.assertEqual(node.pos(), new_pos)
    
    def test_invalid_code_handling(self):
        """Test node behavior with invalid Python code."""
        node = Node("Invalid Code Test")
        
        # Test syntactically invalid code
        invalid_code = '''
def broken_function(x: int) -> str
    # Missing colon and invalid syntax
    return str(x)
'''
        # Should not crash, but might not generate pins
        node.set_code(invalid_code)
        self.assertEqual(node.code, invalid_code)
        
        # Function name should not be extracted from invalid code
        self.assertIsNone(node.function_name)


def run_node_system_tests():
    """Run all node system tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNodeSystem)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_node_system_tests()
    
    # Clean up QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
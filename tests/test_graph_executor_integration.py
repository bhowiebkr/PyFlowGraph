"""
Integration tests for GraphExecutor with SingleProcessExecutor.
Tests the complete execution flow with direct object references.
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.execution.graph_executor import GraphExecutor
from src.core.node import Node
from src.core.pin import Pin
from src.core.connection import Connection
from src.core.reroute_node import RerouteNode


class MockGraph:
    """Mock graph for testing."""
    def __init__(self):
        self.nodes = []


class MockPin:
    """Mock pin for testing."""
    def __init__(self, name, pin_category="data", node=None):
        self.name = name
        self.pin_category = pin_category
        self.connections = []
        self.node = node


class MockConnection:
    """Mock connection for testing."""
    def __init__(self, start_pin, end_pin):
        self.start_pin = start_pin
        self.end_pin = end_pin


class MockNode:
    """Mock node for testing."""
    def __init__(self, title, function_name="", code=""):
        self.title = title
        self.function_name = function_name
        self.code = code
        self.input_pins = []
        self.output_pins = []
        self.gui_values = {}
    
    def get_gui_values(self):
        return self.gui_values
    
    def set_gui_values(self, values):
        self.gui_values.update(values)


class TestGraphExecutorIntegration(unittest.TestCase):
    """Test complete GraphExecutor integration with single process execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.graph = MockGraph()
        self.venv_callback = lambda: None
        self.executor = GraphExecutor(self.graph, self.log, self.venv_callback)
    
    def test_single_node_execution(self):
        """Test AC1: Single Python interpreter shared across all node executions."""
        # Create a simple node
        node = MockNode("Add Node", "add_func")
        node.code = '''
def add_func(a, b):
    return a + b
'''
        
        # Add input pins
        input_pin_a = MockPin("a", "data", node)
        input_pin_b = MockPin("b", "data", node)
        node.input_pins = [input_pin_a, input_pin_b]
        
        # Add output pin
        output_pin = MockPin("result", "data", node)
        node.output_pins = [output_pin]
        
        # Set GUI values (simulating user input)
        node.gui_values = {"a": 5, "b": 3}
        
        # Add to graph
        self.graph.nodes = [node]
        
        # Execute
        self.executor.execute()
        
        # Verify execution happened
        self.assertIn("--- Executing Node: Add Node ---", self.log)
        
        # Verify result was computed and stored in GUI
        self.assertEqual(node.gui_values.get("result"), 8)
    
    def test_connected_nodes_execution(self):
        """Test AC4: Shared memory space for all Python objects."""
        # Create first node (generator)
        node1 = MockNode("Generator", "generate_data")
        node1.code = '''
def generate_data():
    return [1, 2, 3, 4, 5]
'''
        output_pin1 = MockPin("data", "data", node1)
        node1.output_pins = [output_pin1]
        
        # Create second node (processor)
        node2 = MockNode("Processor", "process_data")
        node2.code = '''
def process_data(data):
    return sum(data)
'''
        input_pin2 = MockPin("data", "data", node2)
        output_pin2 = MockPin("result", "data", node2)
        node2.input_pins = [input_pin2]
        node2.output_pins = [output_pin2]
        
        # Connect nodes
        connection = MockConnection(output_pin1, input_pin2)
        output_pin1.connections = [connection]
        input_pin2.connections = [connection]
        
        # Add to graph
        self.graph.nodes = [node1, node2]
        
        # Execute
        self.executor.execute()
        
        # Verify both nodes executed
        self.assertIn("--- Executing Node: Generator ---", self.log)
        self.assertIn("--- Executing Node: Processor ---", self.log)
        
        # Verify result
        self.assertEqual(node2.gui_values.get("result"), 15)
    
    def test_persistent_imports_across_nodes(self):
        """Test AC2: Persistent namespace allowing imports to remain loaded."""
        # First node imports datetime
        node1 = MockNode("Importer", "import_datetime")
        node1.code = '''
import datetime
current_year = datetime.datetime.now().year

def import_datetime():
    return current_year
'''
        output_pin1 = MockPin("year", "data", node1)
        node1.output_pins = [output_pin1]
        
        # Second node uses the import
        node2 = MockNode("User", "use_datetime")
        node2.code = '''
def use_datetime():
    # Should be able to use datetime without re-importing
    return datetime.datetime.now().month
'''
        output_pin2 = MockPin("month", "data", node2)
        node2.output_pins = [output_pin2]
        
        # Add to graph
        self.graph.nodes = [node1, node2]
        
        # Execute
        self.executor.execute()
        
        # Verify both executed successfully
        self.assertIn("--- Executing Node: Importer ---", self.log)
        self.assertIn("--- Executing Node: User ---", self.log)
        
        # Verify results are reasonable
        year_result = node1.gui_values.get("year")
        month_result = node2.gui_values.get("month")
        
        self.assertIsInstance(year_result, int)
        self.assertGreaterEqual(year_result, 2024)
        self.assertIsInstance(month_result, int)
        self.assertGreaterEqual(month_result, 1)
        self.assertLessEqual(month_result, 12)
    
    def test_execution_performance(self):
        """Test AC5: Zero startup overhead between node executions."""
        # Create multiple simple nodes
        nodes = []
        for i in range(5):
            node = MockNode(f"Node_{i}", "simple_func")
            node.code = '''
def simple_func(x):
    return x * 2
'''
            node.gui_values = {"x": i}
            output_pin = MockPin("result", "data", node)
            node.output_pins = [output_pin]
            nodes.append(node)
        
        self.graph.nodes = nodes
        
        # Time execution
        start_time = time.perf_counter()
        self.executor.execute()
        execution_time = time.perf_counter() - start_time
        
        # Verify all nodes executed
        for i in range(5):
            self.assertIn(f"--- Executing Node: Node_{i} ---", self.log)
            self.assertEqual(nodes[i].gui_values.get("result"), i * 2)
        
        # Verify execution was fast (should be under 100ms for 5 simple nodes)
        self.assertLess(execution_time, 0.1, 
                       f"Execution took {execution_time:.3f}s, should be under 0.1s")
    
    def test_error_handling_maintains_execution(self):
        """Test that errors in one node don't prevent others from executing."""
        # Good node
        node1 = MockNode("Good Node", "good_func")
        node1.code = '''
def good_func():
    return "success"
'''
        output_pin1 = MockPin("result", "data", node1)
        node1.output_pins = [output_pin1]
        
        # Bad node
        node2 = MockNode("Bad Node", "bad_func")
        node2.code = '''
def bad_func():
    raise ValueError("Intentional error")
'''
        output_pin2 = MockPin("result", "data", node2)
        node2.output_pins = [output_pin2]
        
        # Another good node
        node3 = MockNode("Another Good Node", "another_good_func")
        node3.code = '''
def another_good_func():
    return "also success"
'''
        output_pin3 = MockPin("result", "data", node3)
        node3.output_pins = [output_pin3]
        
        self.graph.nodes = [node1, node2, node3]
        
        # Execute
        self.executor.execute()
        
        # Verify good nodes executed
        self.assertIn("--- Executing Node: Good Node ---", self.log)
        self.assertIn("--- Executing Node: Another Good Node ---", self.log)
        
        # Verify error was logged
        self.assertTrue(any("ERROR in node 'Bad Node'" in msg for msg in self.log))
        
        # Verify good nodes have results
        self.assertEqual(node1.gui_values.get("result"), "success")
        self.assertEqual(node3.gui_values.get("result"), "also success")
        
        # Bad node should not have result
        self.assertNotIn("result", node2.gui_values)
    
    def test_reroute_node_handling(self):
        """Test that RerouteNodes work correctly with direct object references."""
        # Create source node
        source_node = MockNode("Source", "source_func")
        source_node.code = '''
def source_func():
    return [10, 20, 30]
'''
        source_output = MockPin("data", "data", source_node)
        source_node.output_pins = [source_output]
        
        # Create reroute node
        reroute_node = RerouteNode()
        reroute_node.input_pin = MockPin("input", "data", reroute_node)
        reroute_node.output_pin = MockPin("output", "data", reroute_node)
        
        # Create destination node
        dest_node = MockNode("Destination", "dest_func")
        dest_node.code = '''
def dest_func(data):
    return len(data)
'''
        dest_input = MockPin("data", "data", dest_node)
        dest_output = MockPin("count", "data", dest_node)
        dest_node.input_pins = [dest_input]
        dest_node.output_pins = [dest_output]
        
        # Connect: Source -> Reroute -> Destination
        conn1 = MockConnection(source_output, reroute_node.input_pin)
        conn2 = MockConnection(reroute_node.output_pin, dest_input)
        
        source_output.connections = [conn1]
        reroute_node.input_pin.connections = [conn1]
        reroute_node.output_pin.connections = [conn2]
        dest_input.connections = [conn2]
        
        self.graph.nodes = [source_node, reroute_node, dest_node]
        
        # Execute
        self.executor.execute()
        
        # Verify execution
        self.assertIn("--- Executing Node: Source ---", self.log)
        self.assertIn("--- Executing Node: Destination ---", self.log)
        
        # Verify result (length of [10, 20, 30] is 3)
        self.assertEqual(dest_node.gui_values.get("count"), 3)
    
    def test_complex_object_preservation(self):
        """Test that complex Python objects maintain their identity across nodes."""
        # Node that creates a custom object
        node1 = MockNode("Object Creator", "create_object")
        node1.code = '''
class CustomObject:
    def __init__(self, value):
        self.value = value
        self.id = id(self)
    
    def get_info(self):
        return f"Object {self.id} with value {self.value}"

def create_object():
    return CustomObject(42)
'''
        output_pin1 = MockPin("obj", "data", node1)
        node1.output_pins = [output_pin1]
        
        # Node that uses the object
        node2 = MockNode("Object User", "use_object")
        node2.code = '''
def use_object(obj):
    return obj.get_info()
'''
        input_pin2 = MockPin("obj", "data", node2)
        output_pin2 = MockPin("info", "data", node2)
        node2.input_pins = [input_pin2]
        node2.output_pins = [output_pin2]
        
        # Connect nodes
        connection = MockConnection(output_pin1, input_pin2)
        output_pin1.connections = [connection]
        input_pin2.connections = [connection]
        
        self.graph.nodes = [node1, node2]
        
        # Execute
        self.executor.execute()
        
        # Verify execution
        self.assertIn("--- Executing Node: Object Creator ---", self.log)
        self.assertIn("--- Executing Node: Object User ---", self.log)
        
        # Verify the object was passed correctly
        info = node2.gui_values.get("info")
        self.assertIsInstance(info, str)
        self.assertIn("Object", info)
        self.assertIn("with value 42", info)


if __name__ == '__main__':
    unittest.main()
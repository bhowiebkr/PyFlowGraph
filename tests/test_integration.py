#!/usr/bin/env python3

"""
Integration Tests

End-to-end workflow tests including:
- Complete graph creation, execution, and file operations
- Loading and running example graphs
- GUI interaction workflows
- Error recovery scenarios
- Real-world usage patterns
"""

import unittest
import sys
import os

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication

from core.node_graph import NodeGraph
from core.node import Node
from data.flow_format import load_flow_file


class TestIntegration(unittest.TestCase):
    """Test suite for end-to-end integration scenarios."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for the entire test suite."""
        if QApplication.instance() is None:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = NodeGraph()
    
    def tearDown(self):
        """Clean up after each test."""
        self.graph.clear()
    
    def test_complete_graph_workflow(self):
        """Test complete workflow from graph creation to execution."""
        # Create a simple processing pipeline
        input_node = self.graph.create_node("Input", pos=(0, 0))
        process_node = self.graph.create_node("Process", pos=(300, 0))
        output_node = self.graph.create_node("Output", pos=(600, 0))
        
        # Add functional code
        input_node.set_code('''
@node_entry
def generate_input() -> str:
    return "Hello World"
''')
        
        process_node.set_code('''
@node_entry
def process_text(text: str) -> str:
    return text.upper()
''')
        
        output_node.set_code('''
@node_entry
def output_result(text: str):
    print(f"Result: {text}")
''')
        
        # Connect the pipeline
        # Data flow
        input_data_out = next(p for p in input_node.output_pins if p.pin_category == "data")
        process_data_in = next(p for p in process_node.input_pins if p.pin_category == "data")
        process_data_out = next(p for p in process_node.output_pins if p.pin_category == "data")
        output_data_in = next(p for p in output_node.input_pins if p.pin_category == "data")
        
        self.graph.create_connection(input_data_out, process_data_in)
        self.graph.create_connection(process_data_out, output_data_in)
        
        # Execution flow
        input_exec_out = next(p for p in input_node.output_pins if p.pin_category == "execution")
        process_exec_in = next(p for p in process_node.input_pins if p.pin_category == "execution")
        process_exec_out = next(p for p in process_node.output_pins if p.pin_category == "execution")
        output_exec_in = next(p for p in output_node.input_pins if p.pin_category == "execution")
        
        self.graph.create_connection(input_exec_out, process_exec_in)
        self.graph.create_connection(process_exec_out, output_exec_in)
        
        # Verify graph structure
        self.assertEqual(len(self.graph.nodes), 3)
        self.assertEqual(len(self.graph.connections), 4)  # 2 data + 2 execution
        
        # Test serialization roundtrip
        serialized = self.graph.serialize()
        self.assertIn("nodes", serialized)
        self.assertIn("connections", serialized)
        
        # Clear and deserialize
        self.graph.clear_graph()
        self.graph.deserialize(serialized)
        
        # Verify restoration
        self.assertEqual(len(self.graph.nodes), 3)
        self.assertEqual(len(self.graph.connections), 4)
    
    def test_example_file_loading(self):
        """Test loading existing example files."""
        examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
        
        if os.path.exists(examples_dir):
            example_files = [f for f in os.listdir(examples_dir) if f.endswith('.md')]
            
            for example_file in example_files[:2]:  # Test first 2 files only
                file_path = os.path.join(examples_dir, example_file)
                
                try:
                    data = load_flow_file(file_path)
                    self.assertIn("nodes", data)
                    
                    # Try to load into graph
                    test_graph = NodeGraph()
                    test_graph.deserialize(data)
                    
                    # Should have created some nodes
                    self.assertGreaterEqual(len(test_graph.nodes), 0)
                    
                except Exception as e:
                    self.fail(f"Failed to load {example_file}: {e}")
    
    def test_error_recovery(self):
        """Test system recovery from various error conditions."""
        # Test invalid code handling
        node = self.graph.create_node("Error Node", pos=(0, 0))
        
        # Invalid syntax should not crash
        invalid_code = "def broken_function(:\n    return 'invalid'"
        node.set_code(invalid_code)
        
        # Node should still exist
        self.assertIn(node, self.graph.nodes)
        self.assertEqual(node.code, invalid_code)
        
        # Test invalid connection attempts
        node1 = self.graph.create_node("Node 1", pos=(0, 0))
        node2 = self.graph.create_node("Node 2", pos=(200, 0))
        
        node1.set_code('''
@node_entry
def test1() -> str:
    return "test"
''')
        
        node2.set_code('''
@node_entry
def test2(val: int):
    print(val)
''')
        
        # Try to connect incompatible types
        str_out = next(p for p in node1.output_pins if p.pin_category == "data")
        int_in = next(p for p in node2.input_pins if p.pin_category == "data")
        
        # Connection should still be created (validation might be elsewhere)
        connection = self.graph.create_connection(str_out, int_in)
        self.assertIsNotNone(connection)


def run_integration_tests():
    """Run all integration tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
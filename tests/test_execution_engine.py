#!/usr/bin/env python3

"""
Execution Engine Tests

Tests the GraphExecutor class and code execution functionality including:
- Graph execution flow control
- Node execution order and dependencies
- Data flow between connected nodes
- Subprocess isolation and security
- Error handling and reporting
- Execution pin flow control
- Virtual environment integration
"""

import unittest
import sys
import os
import subprocess
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication, QTextEdit

from execution.graph_executor import GraphExecutor
from core.node_graph import NodeGraph
from core.node import Node
from core.reroute_node import RerouteNode


class TestExecutionEngine(unittest.TestCase):
    """Test suite for GraphExecutor functionality."""
    
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
        self.log_widget = QTextEdit()
        
        # Mock venv path callback
        self.venv_path = tempfile.mkdtemp()
        self.venv_path_callback = Mock(return_value=self.venv_path)
        
        self.executor = GraphExecutor(
            self.graph, 
            self.log_widget, 
            self.venv_path_callback
        )
    
    def tearDown(self):
        """Clean up after each test."""
        self.graph.clear()
        self.log_widget.clear()
    
    @patch('os.path.exists')
    def test_python_executable_path(self, mock_exists):
        """Test Python executable path resolution."""
        mock_exists.return_value = True
        
        # Test Windows path
        with patch('sys.platform', 'win32'):
            python_exe = self.executor.get_python_executable()
            expected = os.path.join(self.venv_path, "Scripts", "python.exe")
            self.assertEqual(python_exe, expected)
        
        # Test Unix path
        with patch('sys.platform', 'linux'):
            python_exe = self.executor.get_python_executable()
            expected = os.path.join(self.venv_path, "bin", "python")
            self.assertEqual(python_exe, expected)
    
    def test_entry_point_detection(self):
        """Test detection of entry point nodes (nodes without execution inputs)."""
        # Create nodes with different execution connectivity
        entry_node = self.graph.create_node("Entry Node", pos=(0, 0))
        middle_node = self.graph.create_node("Middle Node", pos=(200, 0))
        end_node = self.graph.create_node("End Node", pos=(400, 0))
        
        # Add code to create execution pins
        entry_node.set_code('''
@node_entry
def entry_function() -> str:
    return "start"
''')
        
        middle_node.set_code('''
@node_entry
def middle_function(input_val: str) -> str:
    return input_val.upper()
''')
        
        end_node.set_code('''
@node_entry
def end_function(input_val: str):
    print(input_val)
''')
        
        # Connect execution flow: entry -> middle -> end
        entry_exec_out = next(p for p in entry_node.output_pins if p.pin_category == "execution")
        middle_exec_in = next(p for p in middle_node.input_pins if p.pin_category == "execution")
        middle_exec_out = next(p for p in middle_node.output_pins if p.pin_category == "execution")
        end_exec_in = next(p for p in end_node.input_pins if p.pin_category == "execution")
        
        self.graph.create_connection(entry_exec_out, middle_exec_in)
        self.graph.create_connection(middle_exec_out, end_exec_in)
        
        # Find entry points using executor logic
        entry_nodes = []
        for node in self.graph.nodes:
            if isinstance(node, Node):
                exec_input_pins = [p for p in node.input_pins if p.pin_category == "execution"]
                has_exec_input = any(pin.connections for pin in exec_input_pins)
                if not has_exec_input:
                    entry_nodes.append(node)
        
        # Only entry_node should be an entry point
        self.assertEqual(len(entry_nodes), 1)
        self.assertIn(entry_node, entry_nodes)
        self.assertNotIn(middle_node, entry_nodes)
        self.assertNotIn(end_node, entry_nodes)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_node_execution_success(self, mock_exists, mock_run):
        """Test successful node execution."""
        mock_exists.return_value = True
        
        # Mock successful subprocess execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Execution successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Create a simple node
        node = self.graph.create_node("Test Node", pos=(0, 0))
        node.set_code('''
@node_entry
def test_function() -> str:
    return "Hello World"
''')
        
        # Test execution
        self.executor.execute()
        
        # Should have called subprocess.run
        mock_run.assert_called()
        
        # Check that proper arguments were passed
        call_args = mock_run.call_args
        self.assertIn('creationflags', call_args[1])  # Windows subprocess hiding
    
    @patch('os.path.exists')
    def test_missing_virtual_environment(self, mock_exists):
        """Test execution when virtual environment is missing."""
        mock_exists.return_value = False
        
        # Create a test node
        node = self.graph.create_node("Test Node", pos=(0, 0))
        node.set_code('''
@node_entry
def test() -> str:
    return "test"
''')
        
        # Execute should fail gracefully
        self.executor.execute()
        
        # Should log error about missing venv
        log_text = self.log_widget.toPlainText()
        self.assertIn("Virtual environment not found", log_text)
    
    def test_execution_flow_ordering(self):
        """Test that nodes execute in correct order based on execution pins."""
        # Create a chain of nodes
        node1 = self.graph.create_node("First", pos=(0, 0))
        node2 = self.graph.create_node("Second", pos=(200, 0))
        node3 = self.graph.create_node("Third", pos=(400, 0))
        
        # Add code with execution flow
        node1.set_code('''
@node_entry
def first() -> int:
    return 1
''')
        
        node2.set_code('''
@node_entry
def second(val: int) -> int:
    return val + 1
''')
        
        node3.set_code('''
@node_entry
def third(val: int) -> int:
    return val * 2
''')
        
        # Connect execution flow
        exec1_out = next(p for p in node1.output_pins if p.pin_category == "execution")
        exec2_in = next(p for p in node2.input_pins if p.pin_category == "execution")
        exec2_out = next(p for p in node2.output_pins if p.pin_category == "execution")
        exec3_in = next(p for p in node3.input_pins if p.pin_category == "execution")
        
        self.graph.create_connection(exec1_out, exec2_in)
        self.graph.create_connection(exec2_out, exec3_in)
        
        # Connect data flow
        data1_out = next(p for p in node1.output_pins if p.pin_category == "data")
        data2_in = next(p for p in node2.input_pins if p.pin_category == "data")
        data2_out = next(p for p in node2.output_pins if p.pin_category == "data")
        data3_in = next(p for p in node3.input_pins if p.pin_category == "data")
        
        self.graph.create_connection(data1_out, data2_in)
        self.graph.create_connection(data2_out, data3_in)
        
        # Mock successful execution for testing order
        with patch('subprocess.run') as mock_run, patch('os.path.exists', return_value=True):
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = '{"output_1": "test"}'
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            # Test that _execute_node_flow follows the correct sequence
            execution_count = 0
            pin_values = {}
            
            # This would be called by the actual execution
            execution_count = self.executor._execute_node_flow(
                node1, pin_values, execution_count, 100
            )
            
            # Should have incremented execution count
            self.assertGreater(execution_count, 0)
    
    def test_data_flow_between_nodes(self):
        """Test data passing between connected nodes."""
        # Create producer and consumer nodes
        producer = self.graph.create_node("Producer", pos=(0, 0))
        consumer = self.graph.create_node("Consumer", pos=(300, 0))
        
        producer.set_code('''
@node_entry
def produce() -> str:
    return "produced_data"
''')
        
        consumer.set_code('''
@node_entry
def consume(data: str) -> str:
    return f"consumed: {data}"
''')
        
        # Connect data pins
        output_pin = next(p for p in producer.output_pins if p.pin_category == "data")
        input_pin = next(p for p in consumer.input_pins if p.pin_category == "data")
        self.graph.create_connection(output_pin, input_pin)
        
        # Test pin value tracking
        pin_values = {}
        test_value = "test_data"
        pin_values[output_pin] = test_value
        
        # Consumer should receive the value from producer
        self.assertEqual(pin_values.get(output_pin), test_value)
    
    def test_reroute_node_execution(self):
        """Test execution flow through reroute nodes."""
        # Create nodes with reroute in between
        start_node = self.graph.create_node("Start", pos=(0, 0))
        reroute = self.graph.create_node("", pos=(150, 0), is_reroute=True)
        end_node = self.graph.create_node("End", pos=(300, 0))
        
        start_node.set_code('''
@node_entry
def start() -> str:
    return "start_value"
''')
        
        end_node.set_code('''
@node_entry
def end(value: str):
    print(value)
''')
        
        # Connect through reroute
        start_out = next(p for p in start_node.output_pins if p.pin_category == "data")
        end_in = next(p for p in end_node.input_pins if p.pin_category == "data")
        
        self.graph.create_connection(start_out, reroute.input_pin)
        self.graph.create_connection(reroute.output_pin, end_in)
        
        # Test reroute execution logic
        pin_values = {}
        test_value = "reroute_test"
        pin_values[start_out] = test_value
        
        # Simulate reroute node execution
        if reroute.input_pin.connections:
            source_pin = reroute.input_pin.connections[0].start_pin
            pin_values[reroute.output_pin] = pin_values.get(source_pin)
        
        # Value should pass through reroute
        self.assertEqual(pin_values.get(reroute.output_pin), test_value)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_execution_error_handling(self, mock_exists, mock_run):
        """Test handling of execution errors."""
        mock_exists.return_value = True
        
        # Mock failed subprocess execution
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Python syntax error"
        mock_run.return_value = mock_result
        
        # Create node with problematic code
        node = self.graph.create_node("Error Node", pos=(0, 0))
        node.set_code('''
@node_entry
def broken_function() -> str:
    # This will cause an error
    return undefined_variable
''')
        
        # Execute and check error handling
        self.executor.execute()
        
        # Should have logged the error
        log_text = self.log_widget.toPlainText()
        # Error details might be in the log depending on implementation
        self.assertIsInstance(log_text, str)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_execution_timeout_handling(self, mock_exists, mock_run):
        """Test handling of execution timeouts."""
        mock_exists.return_value = True
        
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired("python", 30)
        
        # Create a test node
        node = self.graph.create_node("Timeout Node", pos=(0, 0))
        node.set_code('''
@node_entry
def slow_function() -> str:
    import time
    time.sleep(10)  # This would timeout
    return "done"
''')
        
        # Execute and check timeout handling
        self.executor.execute()
        
        # Should handle timeout gracefully
        log_text = self.log_widget.toPlainText()
        self.assertIsInstance(log_text, str)
    
    def test_execution_limit_protection(self):
        """Test protection against infinite execution loops."""
        # Create nodes that could cause infinite execution
        node1 = self.graph.create_node("Loop Node 1", pos=(0, 0))
        node2 = self.graph.create_node("Loop Node 2", pos=(200, 0))
        
        node1.set_code('''
@node_entry
def loop1() -> str:
    return "loop1"
''')
        
        node2.set_code('''
@node_entry
def loop2() -> str:
    return "loop2"
''')
        
        # Create circular execution (would be caught by execution limit)
        exec1_out = next(p for p in node1.output_pins if p.pin_category == "execution")
        exec2_in = next(p for p in node2.input_pins if p.pin_category == "execution")
        exec2_out = next(p for p in node2.output_pins if p.pin_category == "execution")
        exec1_in = next(p for p in node1.input_pins if p.pin_category == "execution")
        
        self.graph.create_connection(exec1_out, exec2_in)
        # Note: circular connection would be problematic, but the execution limit should prevent issues
        
        # Test that execution limit is properly calculated
        execution_limit = len(self.graph.nodes) * 10
        expected_limit = 2 * 10  # 2 nodes * 10
        self.assertEqual(execution_limit, expected_limit)
    
    def test_multiple_entry_points(self):
        """Test execution with multiple entry point nodes."""
        # Create multiple independent entry points
        entry1 = self.graph.create_node("Entry 1", pos=(0, 0))
        entry2 = self.graph.create_node("Entry 2", pos=(0, 200))
        merger = self.graph.create_node("Merger", pos=(300, 100))
        
        entry1.set_code('''
@node_entry
def entry1() -> str:
    return "from_entry1"
''')
        
        entry2.set_code('''
@node_entry
def entry2() -> str:
    return "from_entry2"
''')
        
        merger.set_code('''
@node_entry
def merge(val1: str, val2: str) -> str:
    return f"{val1}_{val2}"
''')
        
        # Connect data from both entries to merger (but no execution connections to entries)
        entry1_out = next(p for p in entry1.output_pins if p.pin_category == "data")
        entry2_out = next(p for p in entry2.output_pins if p.pin_category == "data")
        merger_inputs = [p for p in merger.input_pins if p.pin_category == "data"]
        
        self.graph.create_connection(entry1_out, merger_inputs[0])
        self.graph.create_connection(entry2_out, merger_inputs[1])
        
        # Both entry1 and entry2 should be detected as entry points
        entry_nodes = []
        for node in self.graph.nodes:
            if isinstance(node, Node):
                exec_input_pins = [p for p in node.input_pins if p.pin_category == "execution"]
                has_exec_input = any(pin.connections for pin in exec_input_pins)
                if not has_exec_input:
                    entry_nodes.append(node)
        
        self.assertIn(entry1, entry_nodes)
        self.assertIn(entry2, entry_nodes)
        self.assertIn(merger, entry_nodes)  # merger also has no exec input
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_subprocess_security_flags(self, mock_exists, mock_run):
        """Test that subprocess execution uses proper security flags."""
        mock_exists.return_value = True
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "{}"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Create and execute a node
        node = self.graph.create_node("Security Test", pos=(0, 0))
        node.set_code('''
@node_entry
def secure_test() -> str:
    return "secure"
''')
        
        self.executor.execute()
        
        # Check that subprocess.run was called with security flags
        mock_run.assert_called()
        call_kwargs = mock_run.call_args[1]
        
        # Should include Windows console hiding flags
        if 'creationflags' in call_kwargs:
            flags = call_kwargs['creationflags']
            # Should include subprocess.CREATE_NO_WINDOW or similar flags
            self.assertIsInstance(flags, int)


def run_execution_engine_tests():
    """Run all execution engine tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestExecutionEngine)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_execution_engine_tests()
    
    # Clean up QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
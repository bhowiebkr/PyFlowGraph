"""
Unit tests for SingleProcessExecutor - testing direct Python execution
replacing subprocess isolation for maximum performance.
"""

import unittest
import sys
import os
import time
import gc
from unittest.mock import Mock, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.execution.single_process_executor import SingleProcessExecutor
from src.core.node import Node
from src.core.pin import Pin


class TestSingleProcessExecutor(unittest.TestCase):
    """Test single process execution functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
        
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def test_initialization(self):
        """Test SingleProcessExecutor initializes correctly."""
        self.assertIsNotNone(self.executor.namespace)
        self.assertIsNotNone(self.executor.object_store)
        self.assertIsNotNone(self.executor.execution_times)
        
        # Check essential modules are loaded
        self.assertIn('json', self.executor.namespace)
        self.assertIn('sys', self.executor.namespace)
        self.assertIn('node_entry', self.executor.namespace)
    
    def test_direct_function_execution(self):
        """Test AC3: Direct function calls replacing subprocess communication."""
        # Create a mock node with simple function
        node = Mock(spec=Node)
        node.title = "Test Node"
        node.function_name = "add_numbers"
        node.code = '''
def add_numbers(a, b):
    return a + b
'''
        
        inputs = {'a': 5, 'b': 3}
        result, output = self.executor.execute_node(node, inputs)
        
        self.assertEqual(result, 8)
        self.assertEqual(output, "")
        
    def test_persistent_namespace(self):
        """Test AC2: Persistent namespace allowing imports and variables to remain loaded."""
        # First execution - define a variable
        node1 = Mock(spec=Node)
        node1.title = "Define Variable"
        node1.function_name = "define_var"
        node1.code = '''
global persistent_var
persistent_var = 42

def define_var():
    return persistent_var
'''
        
        result1, _ = self.executor.execute_node(node1, {})
        self.assertEqual(result1, 42)
        
        # Second execution - use the variable
        node2 = Mock(spec=Node)
        node2.title = "Use Variable" 
        node2.function_name = "use_var"
        node2.code = '''
def use_var():
    return persistent_var * 2
'''
        
        result2, _ = self.executor.execute_node(node2, {})
        self.assertEqual(result2, 84)
        
        # Verify variable persists in namespace
        self.assertIn('persistent_var', self.executor.namespace)
        self.assertEqual(self.executor.namespace['persistent_var'], 42)
    
    def test_import_persistence(self):
        """Test that imports persist between node executions."""
        # First node imports datetime
        node1 = Mock(spec=Node)
        node1.title = "Import Module"
        node1.function_name = "import_datetime"
        node1.code = '''
import datetime

def import_datetime():
    return datetime.datetime.now().year
'''
        
        result1, _ = self.executor.execute_node(node1, {})
        self.assertIsInstance(result1, int)
        self.assertGreaterEqual(result1, 2024)
        
        # Second node uses the imported module
        node2 = Mock(spec=Node)
        node2.title = "Use Import"
        node2.function_name = "use_datetime"
        node2.code = '''
def use_datetime():
    return datetime.datetime.now().month
'''
        
        result2, _ = self.executor.execute_node(node2, {})
        self.assertIsInstance(result2, int)
        self.assertGreaterEqual(result2, 1)
        self.assertLessEqual(result2, 12)
        
        # Verify datetime is in namespace
        self.assertIn('datetime', self.executor.namespace)
    
    def test_direct_object_passing(self):
        """Test AC4: Shared memory space for all Python objects."""
        # Create a complex object (list)
        test_list = [1, 2, 3, 4, 5]
        
        # Store object directly
        self.executor.store_object('test_list', test_list)
        
        # Retrieve object
        retrieved_list = self.executor.get_object('test_list')
        
        # Verify it's the same object (same memory reference)
        self.assertIs(retrieved_list, test_list)
        
        # Modify original and verify change in retrieved
        test_list.append(6)
        self.assertEqual(len(retrieved_list), 6)
        self.assertEqual(retrieved_list[-1], 6)
    
    def test_zero_startup_overhead(self):
        """Test AC5: Zero startup overhead between node executions."""
        # Create simple node
        node = Mock(spec=Node)
        node.title = "Fast Node"
        node.function_name = "fast_func"
        node.code = '''
def fast_func(x):
    return x * 2
'''
        
        # Execute multiple times and measure
        execution_times = []
        for i in range(10):
            start_time = time.perf_counter()
            result, _ = self.executor.execute_node(node, {'x': i})
            execution_time = time.perf_counter() - start_time
            execution_times.append(execution_time)
            self.assertEqual(result, i * 2)
        
        # Verify all executions are fast (under 10ms each)
        for exec_time in execution_times:
            self.assertLess(exec_time, 0.01, "Execution should be under 10ms")
        
        # Verify no significant startup overhead after first execution
        if len(execution_times) > 1:
            first_time = execution_times[0]
            subsequent_times = execution_times[1:]
            avg_subsequent = sum(subsequent_times) / len(subsequent_times)
            
            # Subsequent executions should not be significantly slower
            self.assertLess(avg_subsequent, first_time * 2, 
                          "Subsequent executions should not have significant overhead")
    
    def test_error_handling(self):
        """Test that errors are properly caught and reported."""
        node = Mock(spec=Node)
        node.title = "Error Node"
        node.function_name = "error_func"
        node.code = '''
def error_func():
    raise ValueError("Test error")
'''
        
        with self.assertRaises(RuntimeError) as cm:
            self.executor.execute_node(node, {})
        
        self.assertIn("ERROR in node 'Error Node'", str(cm.exception))
        self.assertIn("Test error", str(cm.exception))
    
    def test_stdout_capture(self):
        """Test that stdout is properly captured from direct execution."""
        node = Mock(spec=Node)
        node.title = "Print Node"
        node.function_name = "print_func"
        node.code = '''
def print_func(message):
    print(f"Output: {message}")
    return message.upper()
'''
        
        result, output = self.executor.execute_node(node, {'message': 'hello'})
        
        self.assertEqual(result, 'HELLO')
        self.assertIn('Output: hello', output)
    
    def test_multiple_outputs(self):
        """Test handling of multiple output values."""
        node = Mock(spec=Node)
        node.title = "Multi Output Node"
        node.function_name = "multi_output"
        node.code = '''
def multi_output(x):
    return x, x * 2, x * 3
'''
        
        result, _ = self.executor.execute_node(node, {'x': 5})
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(result, (5, 10, 15))
    
    def test_performance_tracking(self):
        """Test that performance statistics are tracked."""
        node = Mock(spec=Node)
        node.title = "Timed Node"
        node.function_name = "timed_func"
        node.code = '''
import time
def timed_func():
    time.sleep(0.001)  # Sleep 1ms
    return "done"
'''
        
        self.executor.execute_node(node, {})
        
        stats = self.executor.get_performance_stats()
        self.assertEqual(stats['total_executions'], 1)
        self.assertGreater(stats['total_time'], 0.0)
        self.assertIn('Timed Node', self.executor.execution_times)
    
    def test_memory_cleanup(self):
        """Test memory cleanup functionality."""
        # Create some objects
        for i in range(10):
            self.executor.store_object(f'obj_{i}', list(range(i * 100)))
        
        initial_objects = len(self.executor.object_store)
        self.assertEqual(initial_objects, 10)
        
        # Perform cleanup
        collected = self.executor.cleanup_memory()
        
        # Verify cleanup happened (collected should be >= 0)
        self.assertGreaterEqual(collected, 0)
    
    def test_namespace_reset(self):
        """Test namespace reset functionality."""
        # Add some data
        self.executor.namespace['test_var'] = 123
        self.executor.store_object('test_obj', [1, 2, 3])
        
        # Reset
        self.executor.reset_namespace()
        
        # Verify clean state
        self.assertNotIn('test_var', self.executor.namespace)
        self.assertEqual(len(self.executor.object_store), 0)
        self.assertEqual(len(self.executor.execution_times), 0)
        
        # Verify essentials are back
        self.assertIn('node_entry', self.executor.namespace)


class TestComplexObjectPassing(unittest.TestCase):
    """Test complex object passing scenarios."""
    
    def setUp(self):
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
    
    def tearDown(self):
        self.executor.reset_namespace()
        gc.collect()
    
    def test_numpy_array_passing(self):
        """Test passing NumPy arrays if NumPy is available."""
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy not available")
        
        # Create array and store
        arr = np.array([1, 2, 3, 4, 5])
        self.executor.store_object('numpy_array', arr)
        
        # Retrieve and verify same object
        retrieved_arr = self.executor.get_object('numpy_array')
        self.assertIs(retrieved_arr, arr)
        
        # Test with node execution
        node = Mock(spec=Node)
        node.title = "NumPy Node"
        node.function_name = "numpy_func"
        node.code = '''
import numpy as np
def numpy_func(arr):
    return np.sum(arr)
'''
        
        result, _ = self.executor.execute_node(node, {'arr': arr})
        self.assertEqual(result, 15)
    
    def test_pandas_dataframe_passing(self):
        """Test passing Pandas DataFrames if Pandas is available."""
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("Pandas not available")
        
        # Create DataFrame
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        self.executor.store_object('dataframe', df)
        
        # Retrieve and verify same object
        retrieved_df = self.executor.get_object('dataframe')
        self.assertIs(retrieved_df, df)
        
        # Test with node execution
        node = Mock(spec=Node)
        node.title = "Pandas Node"
        node.function_name = "pandas_func"
        node.code = '''
def pandas_func(df):
    return df['A'].sum()
'''
        
        result, _ = self.executor.execute_node(node, {'df': df})
        self.assertEqual(result, 6)


if __name__ == '__main__':
    unittest.main()
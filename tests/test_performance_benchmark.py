"""
Performance benchmark tests comparing single process execution
to the previous subprocess-based execution model.
"""

import unittest
import time
import sys
import os
from unittest.mock import Mock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.execution.single_process_executor import SingleProcessExecutor


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarks for single process execution."""
    
    def setUp(self):
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
    
    def tearDown(self):
        self.executor.reset_namespace()
    
    def test_execution_speed_benchmark(self):
        """Benchmark execution speed for simple operations."""
        # Create a simple computation node
        node = Mock()
        node.title = "Benchmark Node"
        node.function_name = "compute"
        node.code = '''
def compute(x):
    return x * x + 2 * x + 1
'''
        
        # Warm up
        self.executor.execute_node(node, {'x': 1})
        
        # Benchmark multiple executions
        num_executions = 100
        start_time = time.perf_counter()
        
        for i in range(num_executions):
            result, _ = self.executor.execute_node(node, {'x': i})
            self.assertEqual(result, i * i + 2 * i + 1)
        
        total_time = time.perf_counter() - start_time
        avg_time_per_execution = total_time / num_executions
        
        print(f"\nPerformance Benchmark Results:")
        print(f"Total executions: {num_executions}")
        print(f"Total time: {total_time:.4f}s")
        print(f"Average time per execution: {avg_time_per_execution*1000:.2f}ms")
        print(f"Executions per second: {num_executions/total_time:.0f}")
        
        # Single process execution should be very fast (under 1ms per execution)
        self.assertLess(avg_time_per_execution, 0.001, 
                       f"Average execution time {avg_time_per_execution*1000:.2f}ms should be under 1ms")
        
        # Should handle at least 1000 executions per second
        executions_per_second = num_executions / total_time
        self.assertGreater(executions_per_second, 1000,
                          f"Should handle >1000 executions/sec, got {executions_per_second:.0f}")
    
    def test_memory_efficiency(self):
        """Test memory efficiency of direct object passing."""
        # Create a node that works with large data
        node = Mock()
        node.title = "Memory Test"
        node.function_name = "process_data"
        node.code = '''
def process_data(data):
    return len(data), sum(data)
'''
        
        # Create large data object (1M integers)
        large_data = list(range(1000000))
        
        # Time the execution
        start_time = time.perf_counter()
        result, _ = self.executor.execute_node(node, {'data': large_data})
        execution_time = time.perf_counter() - start_time
        
        # Verify result
        self.assertEqual(result, (1000000, 499999500000))
        
        print(f"\nMemory Efficiency Test:")
        print(f"Processed {len(large_data):,} integers")
        print(f"Execution time: {execution_time*1000:.2f}ms")
        
        # Should be very fast since we're passing by reference (under 10ms)
        self.assertLess(execution_time, 0.01,
                       f"Large data processing took {execution_time*1000:.2f}ms, should be under 10ms")
    
    def test_import_overhead(self):
        """Test that imports don't add overhead after the first use."""
        # First node imports numpy (if available)
        node1 = Mock()
        node1.title = "Import Node"
        node1.function_name = "import_modules"
        node1.code = '''
import math
import json
import time

def import_modules():
    return math.pi
'''
        
        # Execute first time (includes import overhead)
        start_time = time.perf_counter()
        result1, _ = self.executor.execute_node(node1, {})
        first_time = time.perf_counter() - start_time
        
        self.assertAlmostEqual(result1, 3.14159, places=4)
        
        # Second node uses the same imports
        node2 = Mock()
        node2.title = "Use Import Node"
        node2.function_name = "use_imports"
        node2.code = '''
def use_imports():
    return math.e, json.dumps({"test": True}), time.time()
'''
        
        # Execute second time (should be faster - no import overhead)
        start_time = time.perf_counter()
        result2, _ = self.executor.execute_node(node2, {})
        second_time = time.perf_counter() - start_time
        
        self.assertIsInstance(result2, tuple)
        self.assertEqual(len(result2), 3)
        self.assertAlmostEqual(result2[0], 2.71828, places=4)
        self.assertEqual(result2[1], '{"test": true}')
        self.assertIsInstance(result2[2], float)
        
        print(f"\nImport Overhead Test:")
        print(f"First execution (with imports): {first_time*1000:.2f}ms")
        print(f"Second execution (reusing imports): {second_time*1000:.2f}ms")
        print(f"Speedup factor: {first_time/second_time:.1f}x")
        
        # Second execution should be significantly faster or at least not slower
        self.assertLessEqual(second_time, first_time * 1.5,
                            "Subsequent executions should not be significantly slower")
    
    def test_namespace_persistence_performance(self):
        """Test that namespace persistence doesn't degrade performance."""
        # Node that adds variables to namespace
        setup_node = Mock()
        setup_node.title = "Setup"
        setup_node.function_name = "setup_vars"
        setup_node.code = '''
# Define some persistent variables
persistent_dict = {"key1": 100, "key2": 200}
persistent_list = list(range(1000))

def setup_vars():
    return len(persistent_dict) + len(persistent_list)
'''
        
        # Execute setup
        result, _ = self.executor.execute_node(setup_node, {})
        self.assertEqual(result, 1002)
        
        # Node that uses persistent variables
        use_node = Mock()
        use_node.title = "Use Variables"
        use_node.function_name = "use_vars"
        use_node.code = '''
def use_vars():
    return persistent_dict["key1"] + sum(persistent_list[:10])
'''
        
        # Benchmark repeated use of persistent variables
        num_uses = 50
        start_time = time.perf_counter()
        
        for _ in range(num_uses):
            result, _ = self.executor.execute_node(use_node, {})
            self.assertEqual(result, 145)  # 100 + 45 (sum of 0-9)
        
        total_time = time.perf_counter() - start_time
        avg_time = total_time / num_uses
        
        print(f"\nNamespace Persistence Performance:")
        print(f"Used persistent variables {num_uses} times")
        print(f"Total time: {total_time*1000:.2f}ms")
        print(f"Average time per use: {avg_time*1000:.2f}ms")
        
        # Using persistent variables should be very fast
        self.assertLess(avg_time, 0.001,
                       f"Using persistent variables took {avg_time*1000:.2f}ms, should be under 1ms")


if __name__ == '__main__':
    unittest.main(verbosity=2)
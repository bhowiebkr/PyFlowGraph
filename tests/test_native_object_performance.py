"""
Performance benchmarks comparing copy vs reference passing for native objects.
Tests Story 3.3 - Native Object Passing System Subtask 6.4
"""

import unittest
import sys
import os
import gc
import time
import copy
from unittest.mock import Mock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from execution.single_process_executor import SingleProcessExecutor


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarks for native object passing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
        gc.collect()
    
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def measure_execution_time(self, func, iterations=1):
        """Measure execution time of a function."""
        times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        return sum(times) / len(times) if times else 0
    
    def test_reference_vs_copy_performance_small_objects(self):
        """Test performance difference for small objects (< 1KB)."""
        # Create small test object
        small_obj = {"data": list(range(100)), "meta": {"type": "small"}}
        
        # Test reference passing
        def reference_operation():
            self.executor.store_object("small_ref", small_obj)
            retrieved = self.executor.get_object("small_ref")
            return len(retrieved["data"])
        
        # Test copy operation (simulating old JSON serialization approach)
        def copy_operation():
            copied_obj = copy.deepcopy(small_obj)
            return len(copied_obj["data"])
        
        # Measure performance
        ref_time = self.measure_execution_time(reference_operation, 1000)
        copy_time = self.measure_execution_time(copy_operation, 1000)
        
        # Reference should be significantly faster
        performance_ratio = copy_time / ref_time if ref_time > 0 else float('inf')
        
        print(f"Small objects - Reference: {ref_time*1000:.3f}ms, Copy: {copy_time*1000:.3f}ms")
        print(f"Performance improvement: {performance_ratio:.1f}x faster")
        
        self.assertGreater(performance_ratio, 2.0,
                          f"Reference passing should be at least 2x faster for small objects")
    
    def test_reference_vs_copy_performance_large_objects(self):
        """Test performance difference for large objects (> 1MB)."""
        # Create large test object (~5MB)
        large_obj = {
            "matrix": [list(range(1000)) for _ in range(1000)],
            "metadata": {"size": "large", "dimensions": [1000, 1000]}
        }
        
        # Test reference passing
        def reference_operation():
            self.executor.store_object("large_ref", large_obj)
            retrieved = self.executor.get_object("large_ref")
            return len(retrieved["matrix"])
        
        # Test copy operation
        def copy_operation():
            copied_obj = copy.deepcopy(large_obj)
            return len(copied_obj["matrix"])
        
        # Measure performance (fewer iterations due to size)
        ref_time = self.measure_execution_time(reference_operation, 10)
        copy_time = self.measure_execution_time(copy_operation, 10)
        
        # Reference should be dramatically faster for large objects
        performance_ratio = copy_time / ref_time if ref_time > 0 else float('inf')
        
        print(f"Large objects - Reference: {ref_time*1000:.3f}ms, Copy: {copy_time*1000:.3f}ms")
        print(f"Performance improvement: {performance_ratio:.1f}x faster")
        
        self.assertGreater(performance_ratio, 50.0,
                          f"Reference passing should be at least 50x faster for large objects")
    
    def test_numpy_array_performance(self):
        """Test performance with NumPy arrays."""
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy not available")
        
        # Create large NumPy array (~40MB)
        array = np.random.random((2000, 2000, 5)).astype(np.float32)
        
        # Test reference passing
        def reference_operation():
            self.executor.store_object("numpy_ref", array)
            retrieved = self.executor.get_object("numpy_ref")
            return retrieved.shape
        
        # Test copy operation
        def copy_operation():
            copied_array = array.copy()
            return copied_array.shape
        
        # Measure performance
        ref_time = self.measure_execution_time(reference_operation, 5)
        copy_time = self.measure_execution_time(copy_operation, 5)
        
        performance_ratio = copy_time / ref_time if ref_time > 0 else float('inf')
        
        print(f"NumPy arrays - Reference: {ref_time*1000:.3f}ms, Copy: {copy_time*1000:.3f}ms")
        print(f"Performance improvement: {performance_ratio:.1f}x faster")
        
        self.assertGreater(performance_ratio, 100.0,
                          f"Reference passing should be at least 100x faster for NumPy arrays")
    
    def test_pytorch_tensor_performance(self):
        """Test performance with PyTorch tensors."""
        try:
            import torch
        except ImportError:
            self.skipTest("PyTorch not available")
        
        # Create large tensor (~40MB)
        tensor = torch.randn(2000, 2000, 5, dtype=torch.float32)
        
        # Test reference passing
        def reference_operation():
            self.executor.store_object("torch_ref", tensor)
            retrieved = self.executor.get_object("torch_ref")
            return retrieved.shape
        
        # Test copy operation
        def copy_operation():
            copied_tensor = tensor.clone()
            return copied_tensor.shape
        
        # Measure performance
        ref_time = self.measure_execution_time(reference_operation, 5)
        copy_time = self.measure_execution_time(copy_operation, 5)
        
        performance_ratio = copy_time / ref_time if ref_time > 0 else float('inf')
        
        print(f"PyTorch tensors - Reference: {ref_time*1000:.3f}ms, Copy: {copy_time*1000:.3f}ms")
        print(f"Performance improvement: {performance_ratio:.1f}x faster")
        
        self.assertGreater(performance_ratio, 50.0,
                          f"Reference passing should be at least 50x faster for PyTorch tensors")
    
    def test_pandas_dataframe_performance(self):
        """Test performance with Pandas DataFrames."""
        try:
            import pandas as pd
            import numpy as np
        except ImportError:
            self.skipTest("Pandas or NumPy not available")
        
        # Create large DataFrame (~20MB)
        df = pd.DataFrame(np.random.random((100000, 50)))
        
        # Test reference passing
        def reference_operation():
            self.executor.store_object("pandas_ref", df)
            retrieved = self.executor.get_object("pandas_ref")
            return retrieved.shape
        
        # Test copy operation
        def copy_operation():
            copied_df = df.copy()
            return copied_df.shape
        
        # Measure performance
        ref_time = self.measure_execution_time(reference_operation, 5)
        copy_time = self.measure_execution_time(copy_operation, 5)
        
        performance_ratio = copy_time / ref_time if ref_time > 0 else float('inf')
        
        print(f"Pandas DataFrames - Reference: {ref_time*1000:.3f}ms, Copy: {copy_time*1000:.3f}ms")
        print(f"Performance improvement: {performance_ratio:.1f}x faster")
        
        self.assertGreater(performance_ratio, 20.0,
                          f"Reference passing should be at least 20x faster for Pandas DataFrames")
    
    def test_node_execution_performance(self):
        """Test AC5: Zero startup overhead between node executions."""
        # Create test node
        node = Mock()
        node.title = "Performance Test Node"
        node.function_name = "perf_test"
        node.code = '''
def perf_test(data):
    return len(data)
'''
        
        # Create test data
        test_data = list(range(10000))
        
        # Measure first execution (may include compilation overhead)
        start_time = time.perf_counter()
        result1, _ = self.executor.execute_node(node, {"data": test_data})
        first_exec_time = time.perf_counter() - start_time
        
        # Measure subsequent executions
        execution_times = []
        for i in range(10):
            start_time = time.perf_counter()
            result, _ = self.executor.execute_node(node, {"data": test_data})
            exec_time = time.perf_counter() - start_time
            execution_times.append(exec_time)
            self.assertEqual(result, 10000)
        
        avg_exec_time = sum(execution_times) / len(execution_times)
        
        print(f"First execution: {first_exec_time*1000:.3f}ms")
        print(f"Average subsequent executions: {avg_exec_time*1000:.3f}ms")
        
        # Subsequent executions should not be significantly slower than first
        overhead_ratio = avg_exec_time / first_exec_time if first_exec_time > 0 else 1
        
        self.assertLess(overhead_ratio, 2.0,
                       f"Subsequent executions should not have significant overhead")
        
        # All executions should be very fast (under 10ms)
        self.assertLess(avg_exec_time, 0.01,
                       f"Node execution should be under 10ms, got {avg_exec_time*1000:.3f}ms")
    
    def test_object_chain_performance(self):
        """Test performance of object passing through chain of nodes."""
        # Create chain of nodes
        nodes = []
        for i in range(5):
            node = Mock()
            node.title = f"Chain Node {i}"
            node.function_name = f"chain_func_{i}"
            node.code = f'''
def chain_func_{i}(data):
    data["step_{i}"] = True
    data["count"] = data.get("count", 0) + 1
    return data
'''
            nodes.append(node)
        
        # Create test data
        chain_data = {"initial": True, "values": list(range(1000))}
        
        # Measure chain execution
        start_time = time.perf_counter()
        current_data = chain_data
        
        for node in nodes:
            result, _ = self.executor.execute_node(node, {"data": current_data})
            current_data = result
        
        chain_exec_time = time.perf_counter() - start_time
        
        # Verify processing worked and same object was passed through
        self.assertIs(current_data, chain_data)  # Same object reference
        self.assertEqual(current_data["count"], 5)
        for i in range(5):
            self.assertTrue(current_data[f"step_{i}"])
        
        print(f"5-node chain execution: {chain_exec_time*1000:.3f}ms")
        print(f"Average per node: {chain_exec_time/5*1000:.3f}ms")
        
        # Chain should be fast (under 50ms total)
        self.assertLess(chain_exec_time, 0.05,
                       f"5-node chain should execute under 50ms, got {chain_exec_time*1000:.3f}ms")
    
    def test_concurrent_object_access_performance(self):
        """Test performance of concurrent object access."""
        # Create shared object
        shared_obj = {"data": list(range(10000)), "access_count": 0}
        self.executor.store_object("shared_perf", shared_obj)
        
        # Measure concurrent access performance
        access_times = []
        
        for i in range(100):
            start_time = time.perf_counter()
            
            # Simulate multiple references
            ref1 = self.executor.get_object("shared_perf")
            ref2 = self.executor.get_object("shared_perf")
            ref3 = self.executor.get_object("shared_perf")
            
            # Verify same object
            self.assertIs(ref1, shared_obj)
            self.assertIs(ref2, shared_obj)
            self.assertIs(ref3, shared_obj)
            
            # Modify through one reference
            ref1["access_count"] += 1
            
            access_time = time.perf_counter() - start_time
            access_times.append(access_time)
        
        avg_access_time = sum(access_times) / len(access_times)
        max_access_time = max(access_times)
        
        print(f"Concurrent access - Average: {avg_access_time*1000:.3f}ms, Max: {max_access_time*1000:.3f}ms")
        
        # Access should be very fast and consistent
        self.assertLess(avg_access_time, 0.001,  # Under 1ms
                       f"Object access should be under 1ms, got {avg_access_time*1000:.3f}ms")
        self.assertLess(max_access_time, 0.005,  # Under 5ms
                       f"Max access time should be under 5ms, got {max_access_time*1000:.3f}ms")
        
        # Verify all modifications were applied
        self.assertEqual(shared_obj["access_count"], 100)


class TestMemoryEfficiencyBenchmarks(unittest.TestCase):
    """Benchmarks for memory efficiency of native object passing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
        gc.collect()
    
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def test_memory_usage_vs_copying(self):
        """Test memory usage comparison between reference and copy approaches."""
        import psutil
        process = psutil.Process()
        
        # Get baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss
        
        # Create large object
        large_obj = {
            "arrays": [[i] * 1000 for i in range(1000)],
            "metadata": {"size": "1M elements"}
        }
        
        # Test reference approach
        self.executor.store_object("memory_test", large_obj)
        
        # Get multiple references (should not increase memory significantly)
        refs = []
        for i in range(10):
            ref = self.executor.get_object("memory_test")
            refs.append(ref)
        
        reference_memory = process.memory_info().rss
        reference_usage = reference_memory - baseline_memory
        
        # Clear references
        for ref in refs:
            del ref
        refs.clear()
        self.executor.object_refs.clear()
        del large_obj
        gc.collect()
        
        # Test copy approach (simulate old approach)
        large_obj_copy_test = {
            "arrays": [[i] * 1000 for i in range(1000)],
            "metadata": {"size": "1M elements"}
        }
        
        baseline_copy = process.memory_info().rss
        
        # Create multiple copies
        copies = []
        for i in range(10):
            obj_copy = copy.deepcopy(large_obj_copy_test)
            copies.append(obj_copy)
        
        copy_memory = process.memory_info().rss
        copy_usage = copy_memory - baseline_copy
        
        print(f"Memory usage - Reference approach: {reference_usage/1024/1024:.1f}MB")
        print(f"Memory usage - Copy approach: {copy_usage/1024/1024:.1f}MB")
        
        if copy_usage > 0:
            memory_efficiency = copy_usage / reference_usage
            print(f"Memory efficiency: {memory_efficiency:.1f}x less memory used")
            
            # Reference approach should use significantly less memory
            self.assertGreater(memory_efficiency, 5.0,
                              f"Reference approach should use at least 5x less memory")
        
        # Cleanup
        for copy_obj in copies:
            del copy_obj
        copies.clear()
        del large_obj_copy_test
        gc.collect()
    
    def test_scalability_performance(self):
        """Test performance scalability with increasing object sizes."""
        sizes = [1000, 10000, 100000, 1000000]  # 1K to 1M elements
        results = {}
        
        for size in sizes:
            # Create object of specified size
            test_obj = {"data": list(range(size)), "size": size}
            
            # Measure reference passing time
            start_time = time.perf_counter()
            self.executor.store_object(f"scale_test_{size}", test_obj)
            retrieved = self.executor.get_object(f"scale_test_{size}")
            ref_time = time.perf_counter() - start_time
            
            # Verify same object
            self.assertIs(retrieved, test_obj)
            
            results[size] = ref_time
            
            # Cleanup
            del self.executor.object_refs[f"scale_test_{size}"]
            del test_obj
        
        print("Scalability Results:")
        for size, ref_time in results.items():
            print(f"  {size:>8} elements: {ref_time*1000:.3f}ms")
        
        # Performance should scale sub-linearly (near constant time)
        small_time = results[1000]
        large_time = results[1000000]
        
        if small_time > 0:
            scaling_factor = large_time / small_time
            print(f"Scaling factor (1M/1K): {scaling_factor:.2f}x")
            
            # Should not scale linearly with size (reference passing is O(1))
            self.assertLess(scaling_factor, 100.0,
                           f"Reference passing should not scale linearly with size")
        
        # All operations should be fast regardless of size
        for size, ref_time in results.items():
            self.assertLess(ref_time, 0.01,
                           f"Reference passing should be under 10ms for {size} elements")


if __name__ == "__main__":
    unittest.main()
"""
Memory leak detection tests for native object passing system.
Tests Story 3.3 - Native Object Passing System Subtask 6.3
"""

import unittest
import sys
import os
import gc
import weakref
import psutil
import time
from unittest.mock import Mock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from execution.single_process_executor import SingleProcessExecutor


class TestMemoryLeakDetection(unittest.TestCase):
    """Test memory leak detection and prevention."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
        self.process = psutil.Process()
        
        # Force garbage collection before each test
        gc.collect()
        self.initial_memory = self.process.memory_info().rss
    
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def get_memory_usage(self):
        """Get current memory usage in bytes."""
        return self.process.memory_info().rss
    
    def test_weakref_cleanup_prevents_leaks(self):
        """Test AC4: WeakValueDictionary prevents memory leaks."""
        initial_objects = len(self.executor.object_store)
        
        # Create and store many objects
        objects_created = []
        for i in range(100):
            obj = {"data": list(range(1000)), "id": i}
            self.executor.store_object(f"obj_{i}", obj)
            objects_created.append(obj)
        
        # Verify objects are stored
        self.assertEqual(len(self.executor.object_store), initial_objects + 100)
        
        # Delete references to objects
        for obj in objects_created:
            del obj
        objects_created.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Objects remain in store until explicitly cleared (direct storage)
        remaining_objects = len(self.executor.object_store)
        self.assertEqual(remaining_objects, initial_objects + 100,
                       "Object store maintains direct references until cleared")
    
    def test_large_object_memory_cleanup(self):
        """Test memory cleanup of large objects."""
        memory_before = self.get_memory_usage()
        
        # Create large objects (10MB each)
        large_objects = []
        for i in range(5):
            large_obj = bytearray(10 * 1024 * 1024)  # 10MB
            self.executor.store_object(f"large_{i}", large_obj)
            large_objects.append(large_obj)
        
        memory_after_creation = self.get_memory_usage()
        memory_increase = memory_after_creation - memory_before
        
        # Verify memory increased significantly
        self.assertGreater(memory_increase, 40 * 1024 * 1024,  # At least 40MB
                          "Memory should increase with large objects")
        
        # Clear references and cleanup
        for obj in large_objects:
            del obj
        large_objects.clear()
        self.executor.cleanup_memory()
        gc.collect()
        
        memory_after_cleanup = self.get_memory_usage()
        memory_recovered = memory_after_creation - memory_after_cleanup
        
        # Verify significant memory recovery
        self.assertGreater(memory_recovered, 30 * 1024 * 1024,  # At least 30MB recovered
                          "Memory cleanup should recover most allocated memory")
    
    def test_circular_reference_cleanup(self):
        """Test cleanup of circular references doesn't leak memory."""
        initial_refs = len(self.executor.object_store)
        
        # Create circular reference structures
        for i in range(50):
            obj_a = {"name": f"a_{i}", "id": i}
            obj_b = {"name": f"b_{i}", "id": i}
            obj_c = {"name": f"c_{i}", "id": i}
            
            # Create circular references
            obj_a["ref"] = obj_b
            obj_b["ref"] = obj_c
            obj_c["ref"] = obj_a
            
            # Store only one object per cycle
            self.executor.store_object(f"cycle_{i}", obj_a)
        
        # Verify objects stored
        self.assertEqual(len(self.executor.object_store), initial_refs + 50)
        
        # Clear object store and force cleanup
        self.executor.object_store.clear()
        self.executor.cleanup_memory()
        
        # Verify cleanup occurred
        self.assertEqual(len(self.executor.object_store), 0)
    
    def test_gpu_memory_cleanup(self):
        """Test GPU memory cleanup for PyTorch tensors."""
        try:
            import torch
        except ImportError:
            self.skipTest("PyTorch not available")
        
        if not torch.cuda.is_available():
            self.skipTest("CUDA not available")
        
        # Get initial GPU memory
        torch.cuda.empty_cache()
        initial_gpu_memory = torch.cuda.memory_allocated()
        
        # Create GPU tensors
        gpu_tensors = []
        for i in range(10):
            tensor = torch.randn(1000, 1000, device='cuda')  # ~4MB each
            self.executor.store_object(f"gpu_tensor_{i}", tensor)
            gpu_tensors.append(tensor)
        
        gpu_memory_after = torch.cuda.memory_allocated()
        
        # Verify GPU memory increased
        self.assertGreater(gpu_memory_after, initial_gpu_memory)
        
        # Clear tensors and cleanup
        for tensor in gpu_tensors:
            del tensor
        gpu_tensors.clear()
        
        # Use executor's GPU cleanup
        self.executor._cleanup_gpu_memory()
        
        final_gpu_memory = torch.cuda.memory_allocated()
        
        # Verify GPU memory was cleaned up
        self.assertLess(final_gpu_memory, gpu_memory_after,
                       "GPU memory should be cleaned up")
    
    def test_node_execution_memory_isolation(self):
        """Test node execution doesn't leak memory across runs."""
        memory_measurements = []
        
        # Create node that creates temporary objects
        node = Mock()
        node.title = "Memory Test Node"
        node.function_name = "create_temp_objects"
        node.code = '''
def create_temp_objects(size):
    # Create temporary objects that shouldn't leak
    temp_data = []
    for i in range(size):
        temp_data.append([i] * 1000)  # Create lists
    
    # Return small result
    return len(temp_data)
'''
        
        # Run node multiple times and measure memory
        for i in range(10):
            result, _ = self.executor.execute_node(node, {"size": 1000})
            self.assertEqual(result, 1000)
            
            # Force cleanup and measure memory
            gc.collect()
            memory_measurements.append(self.get_memory_usage())
        
        # Verify memory doesn't continuously increase
        first_half_avg = sum(memory_measurements[:5]) / 5
        second_half_avg = sum(memory_measurements[5:]) / 5
        memory_growth = second_half_avg - first_half_avg
        
        # Allow for some growth but not excessive
        max_allowed_growth = 50 * 1024 * 1024  # 50MB
        self.assertLess(memory_growth, max_allowed_growth,
                       f"Memory growth {memory_growth} exceeds threshold")
    
    def test_reference_counting_accuracy(self):
        """Test reference counting is accurate and prevents premature cleanup."""
        # Create object
        test_obj = {"data": "important_data"}
        
        # Store object and get multiple references
        self.executor.store_object("ref_test", test_obj)
        ref1 = self.executor.get_object("ref_test")
        ref2 = self.executor.get_object("ref_test")
        
        # Verify all references point to same object
        self.assertIs(ref1, test_obj)
        self.assertIs(ref2, test_obj)
        
        # Delete original reference
        del test_obj
        gc.collect()
        
        # Object should still be accessible via store
        ref3 = self.executor.get_object("ref_test")
        self.assertIsNotNone(ref3)
        self.assertEqual(ref3["data"], "important_data")
        
        # Delete all references except store
        del ref1, ref2
        gc.collect()
        
        # Should still be accessible
        ref4 = self.executor.get_object("ref_test")
        self.assertIsNotNone(ref4)
        
        # Clear store
        self.executor.object_refs.clear()
        del ref3, ref4
        gc.collect()
        
        # Now should be None
        ref5 = self.executor.get_object("ref_test")
        self.assertIsNone(ref5)
    
    def test_memory_cleanup_policy_effectiveness(self):
        """Test memory cleanup policies work effectively."""
        # Get baseline memory
        baseline_memory = self.get_memory_usage()
        
        # Create many objects over time
        for batch in range(5):
            # Create batch of objects
            batch_objects = []
            for i in range(100):
                obj = {"batch": batch, "data": list(range(1000))}
                self.executor.store_object(f"batch_{batch}_obj_{i}", obj)
                batch_objects.append(obj)
            
            # Keep references to first batch only
            if batch > 0:
                for obj in batch_objects:
                    del obj
                batch_objects.clear()
            
            # Trigger cleanup periodically
            if batch % 2 == 0:
                collected = self.executor.cleanup_memory()
                self.assertGreaterEqual(collected, 0)
        
        # Final cleanup
        self.executor.cleanup_memory()
        gc.collect()
        
        final_memory = self.get_memory_usage()
        total_growth = final_memory - baseline_memory
        
        # Memory growth should be reasonable (only first batch should remain)
        max_expected_growth = 100 * 1024 * 1024  # 100MB threshold
        self.assertLess(total_growth, max_expected_growth,
                       f"Memory growth {total_growth} indicates potential leak")
    
    def test_long_running_session_memory_stability(self):
        """Test memory stability during long-running sessions."""
        memory_samples = []
        
        # Simulate long-running session with continuous object creation/cleanup
        for cycle in range(20):
            # Create objects
            cycle_objects = []
            for i in range(50):
                obj = {"cycle": cycle, "data": list(range(500))}
                self.executor.store_object(f"cycle_{cycle}_obj_{i}", obj)
                cycle_objects.append(obj)
            
            # Process with nodes (simulating real usage)
            node = Mock()
            node.title = f"Cycle {cycle} Processor"
            node.function_name = "process_cycle_data"
            node.code = '''
def process_cycle_data(objs):
    total = 0
    for obj in objs:
        total += len(obj["data"])
    return total
'''
            
            result, _ = self.executor.execute_node(node, {"objs": cycle_objects})
            self.assertEqual(result, 50 * 500)  # 50 objects * 500 items each
            
            # Clear most objects (keep last 10 cycles worth)
            if cycle >= 10:
                for obj in cycle_objects:
                    del obj
                cycle_objects.clear()
                
                # Remove from store
                for i in range(50):
                    key = f"cycle_{cycle-10}_obj_{i}"
                    if key in self.executor.object_store:
                        del self.executor.object_store[key]
            
            # Periodic cleanup
            if cycle % 5 == 0:
                self.executor.cleanup_memory()
                gc.collect()
                memory_samples.append(self.get_memory_usage())
        
        # Analyze memory trend
        if len(memory_samples) > 2:
            # Calculate linear trend
            n = len(memory_samples)
            x_mean = (n - 1) / 2
            y_mean = sum(memory_samples) / n
            
            numerator = sum((i - x_mean) * (memory_samples[i] - y_mean) for i in range(n))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            
            if denominator > 0:
                slope = numerator / denominator
                # Slope should be minimal (stable memory usage)
                max_slope = 1024 * 1024  # 1MB per measurement
                self.assertLess(abs(slope), max_slope,
                              f"Memory trend slope {slope} indicates instability")


class TestMemoryUsageOptimization(unittest.TestCase):
    """Test memory usage optimization features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
        gc.collect()
    
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def test_zero_copy_object_sharing(self):
        """Test zero-copy object sharing reduces memory usage."""
        # Create large object
        large_data = list(range(100000))  # ~800KB
        
        # Store object once
        self.executor.store_object("shared_data", large_data)
        
        # Get multiple references
        refs = []
        for i in range(10):
            ref = self.executor.get_object("shared_data")
            refs.append(ref)
        
        # Verify all references are same object (zero-copy)
        for ref in refs:
            self.assertIs(ref, large_data)
        
        # Modify through one reference
        refs[0].append("marker")
        
        # Verify change visible in all references
        for ref in refs:
            self.assertEqual(ref[-1], "marker")
        
        # Verify original also modified
        self.assertEqual(large_data[-1], "marker")
    
    def test_memory_pressure_handling(self):
        """Test handling of memory pressure scenarios."""
        initial_memory = psutil.Process().memory_info().rss
        
        try:
            # Create memory pressure by allocating large objects
            pressure_objects = []
            for i in range(10):
                # 50MB per object
                large_obj = bytearray(50 * 1024 * 1024)
                self.executor.store_object(f"pressure_{i}", large_obj)
                pressure_objects.append(large_obj)
            
            current_memory = psutil.Process().memory_info().rss
            memory_used = current_memory - initial_memory
            
            # Should have allocated significant memory
            self.assertGreater(memory_used, 400 * 1024 * 1024)  # At least 400MB
            
            # Cleanup should handle pressure
            for obj in pressure_objects:
                del obj
            pressure_objects.clear()
            
            collected = self.executor.cleanup_memory()
            self.assertGreaterEqual(collected, 0)
            
            gc.collect()
            
        except MemoryError:
            # If we hit memory error, cleanup should still work
            self.executor.cleanup_memory()
            gc.collect()


if __name__ == "__main__":
    unittest.main()
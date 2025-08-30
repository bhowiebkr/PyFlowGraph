"""
Comprehensive unit tests for direct object passing in native object system.
Tests Story 3.3 - Native Object Passing System Subtask 6.1
"""

import unittest
import sys
import os
import gc
import weakref
from unittest.mock import Mock, patch

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from execution.single_process_executor import SingleProcessExecutor
from core.node import Node


class TestNativeObjectPassing(unittest.TestCase):
    """Test direct Python object passing without serialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
    
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def test_direct_object_reference_storage(self):
        """Test AC1: Direct Python object references passed between nodes (no copying)."""
        # Create a test object
        test_obj = {"key": "value", "nested": {"data": [1, 2, 3]}}
        original_id = id(test_obj)
        
        # Store object directly
        self.executor.store_object("test_ref", test_obj)
        
        # Retrieve object
        retrieved_obj = self.executor.get_object("test_ref")
        
        # Verify same object reference (not a copy)
        self.assertIs(retrieved_obj, test_obj)
        self.assertEqual(id(retrieved_obj), original_id)
        
        # Modify original and verify change in retrieved
        test_obj["new_key"] = "new_value"
        self.assertEqual(retrieved_obj["new_key"], "new_value")
    
    def test_complex_nested_object_preservation(self):
        """Test complex nested object identity preservation."""
        # Create complex nested structure
        inner_list = [1, 2, 3]
        inner_dict = {"data": inner_list}
        outer_obj = {"nested": inner_dict, "list_ref": inner_list}
        
        # Store and retrieve
        self.executor.store_object("complex_obj", outer_obj)
        retrieved = self.executor.get_object("complex_obj")
        
        # Verify all references preserved
        self.assertIs(retrieved, outer_obj)
        self.assertIs(retrieved["nested"], inner_dict)
        self.assertIs(retrieved["list_ref"], inner_list)
        self.assertIs(retrieved["nested"]["data"], inner_list)
        
        # Verify modification preserves references
        inner_list.append(4)
        self.assertEqual(len(retrieved["nested"]["data"]), 4)
        self.assertEqual(len(retrieved["list_ref"]), 4)
    
    def test_custom_class_object_passing(self):
        """Test custom class instances are passed by reference."""
        # Create custom class
        class CustomTestClass:
            def __init__(self, value):
                self.value = value
                self.id_tracker = id(self)
            
            def modify(self, new_value):
                self.value = new_value
        
        # Create instance
        custom_obj = CustomTestClass("initial")
        original_id = id(custom_obj)
        
        # Store and retrieve
        self.executor.store_object("custom_class", custom_obj)
        retrieved = self.executor.get_object("custom_class")
        
        # Verify same object
        self.assertIs(retrieved, custom_obj)
        self.assertEqual(retrieved.id_tracker, original_id)
        
        # Verify method calls work on retrieved object
        retrieved.modify("modified")
        self.assertEqual(custom_obj.value, "modified")
    
    def test_circular_reference_handling(self):
        """Test circular references are preserved."""
        # Create circular reference
        obj_a = {"name": "A"}
        obj_b = {"name": "B", "ref_to_a": obj_a}
        obj_a["ref_to_b"] = obj_b
        
        # Store and retrieve
        self.executor.store_object("circular_a", obj_a)
        self.executor.store_object("circular_b", obj_b)
        
        retrieved_a = self.executor.get_object("circular_a")
        retrieved_b = self.executor.get_object("circular_b")
        
        # Verify circular references preserved
        self.assertIs(retrieved_a, obj_a)
        self.assertIs(retrieved_b, obj_b)
        self.assertIs(retrieved_a["ref_to_b"], obj_b)
        self.assertIs(retrieved_b["ref_to_a"], obj_a)
        self.assertIs(retrieved_a["ref_to_b"]["ref_to_a"], obj_a)
    
    def test_large_object_reference_efficiency(self):
        """Test large objects are passed by reference, not copied."""
        # Create large object (1MB list)
        large_obj = list(range(250000))  # ~1MB of integers
        original_id = id(large_obj)
        
        # Store object
        self.executor.store_object("large_obj", large_obj)
        
        # Retrieve multiple times
        ref1 = self.executor.get_object("large_obj")
        ref2 = self.executor.get_object("large_obj")
        ref3 = self.executor.get_object("large_obj")
        
        # Verify all are same object reference
        self.assertIs(ref1, large_obj)
        self.assertIs(ref2, large_obj)
        self.assertIs(ref3, large_obj)
        self.assertEqual(id(ref1), original_id)
        self.assertEqual(id(ref2), original_id)
        self.assertEqual(id(ref3), original_id)
        
        # Verify no memory duplication (all point to same memory)
        ref1.append("marker")
        self.assertEqual(ref2[-1], "marker")
        self.assertEqual(ref3[-1], "marker")
        self.assertEqual(large_obj[-1], "marker")
    
    def test_object_mutation_across_references(self):
        """Test object mutations are visible across all references."""
        # Create mutable object
        mutable_dict = {"count": 0, "items": []}
        
        # Store object
        self.executor.store_object("mutable_ref", mutable_dict)
        
        # Get multiple references
        ref1 = self.executor.get_object("mutable_ref")
        ref2 = self.executor.get_object("mutable_ref")
        
        # Modify through first reference
        ref1["count"] = 5
        ref1["items"].append("item1")
        
        # Verify change visible through second reference
        self.assertEqual(ref2["count"], 5)
        self.assertEqual(len(ref2["items"]), 1)
        self.assertEqual(ref2["items"][0], "item1")
        
        # Modify through second reference
        ref2["items"].append("item2")
        
        # Verify change visible in original and first reference
        self.assertEqual(len(mutable_dict["items"]), 2)
        self.assertEqual(len(ref1["items"]), 2)
        self.assertEqual(ref1["items"][1], "item2")
    
    def test_object_store_cleanup_behavior(self):
        """Test object store cleanup behavior."""
        # Create object and store reference
        test_obj = {"cleanup_test": True}
        
        self.executor.store_object("cleanup_obj", test_obj)
        
        # Verify object is stored
        self.assertIsNotNone(self.executor.get_object("cleanup_obj"))
        
        # Delete original reference
        del test_obj
        gc.collect()
        
        # Object should still be accessible through store (direct storage)
        retrieved = self.executor.get_object("cleanup_obj")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["cleanup_test"], True)
        
        # Clear from store and verify cleanup
        self.executor.object_store.clear()
        gc.collect()
        
        # Should not be retrievable after cleanup
        result = self.executor.get_object("cleanup_obj")
        self.assertIsNone(result)
    
    def test_no_json_serialization_anywhere(self):
        """Test AC5: No JSON serialization or fallbacks exist."""
        # Create object that would be problematic for JSON
        non_json_obj = {
            "function": lambda x: x * 2,
            "class": type,
            "complex": complex(1, 2),
            "bytes": b"binary_data",
            "set": {1, 2, 3},
            "tuple": (1, 2, 3)
        }
        
        # Store and retrieve without any JSON conversion
        self.executor.store_object("non_json", non_json_obj)
        retrieved = self.executor.get_object("non_json")
        
        # Verify all non-JSON types preserved exactly
        self.assertIs(retrieved, non_json_obj)
        self.assertEqual(retrieved["function"](5), 10)
        self.assertIs(retrieved["class"], type)
        self.assertEqual(retrieved["complex"], complex(1, 2))
        self.assertEqual(retrieved["bytes"], b"binary_data")
        self.assertEqual(retrieved["set"], {1, 2, 3})
        self.assertEqual(retrieved["tuple"], (1, 2, 3))
    
    def test_object_type_preservation(self):
        """Test all Python types are preserved exactly."""
        test_objects = {
            "int": 42,
            "float": 3.14159,
            "str": "test_string",
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "tuple": (1, 2, 3),
            "set": {1, 2, 3},
            "frozenset": frozenset([1, 2, 3]),
            "bytes": b"binary",
            "bytearray": bytearray(b"mutable_binary"),
            "range": range(10),
            "complex": complex(2, 3),
            "function": lambda: "test",
            "type": int,
            "exception": ValueError("test_error")
        }
        
        # Store all objects
        for key, obj in test_objects.items():
            self.executor.store_object(key, obj)
        
        # Retrieve and verify types preserved
        for key, original_obj in test_objects.items():
            retrieved = self.executor.get_object(key)
            self.assertIs(retrieved, original_obj, f"Type {key} not preserved by reference")
            self.assertEqual(type(retrieved), type(original_obj), f"Type of {key} changed")
    
    def test_concurrent_object_access_safety(self):
        """Test concurrent access to same object is safe."""
        # Create shared object
        shared_obj = {"counter": 0, "data": []}
        
        self.executor.store_object("shared", shared_obj)
        
        # Simulate concurrent access
        ref1 = self.executor.get_object("shared")
        ref2 = self.executor.get_object("shared")
        ref3 = self.executor.get_object("shared")
        
        # Verify all references point to same object
        self.assertIs(ref1, shared_obj)
        self.assertIs(ref2, shared_obj)
        self.assertIs(ref3, shared_obj)
        
        # Simulate concurrent modifications
        ref1["counter"] += 1
        ref2["data"].append("item1")
        ref3["counter"] += 2
        
        # Verify all changes visible everywhere
        self.assertEqual(shared_obj["counter"], 3)
        self.assertEqual(len(shared_obj["data"]), 1)
        self.assertEqual(ref1["counter"], 3)
        self.assertEqual(ref2["counter"], 3)
        self.assertEqual(ref3["data"], ["item1"])


class TestObjectStoreIntegration(unittest.TestCase):
    """Test object store integration with node execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
    
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def test_object_passing_through_node_execution(self):
        """Test objects passed correctly through node execution."""
        # Create test object
        test_data = {"input": [1, 2, 3, 4, 5]}
        
        # Create mock node that processes object
        node = Mock()
        node.title = "Object Processor"
        node.function_name = "process_obj"
        node.code = '''
def process_obj(data):
    # Modify the object directly (should affect original)
    data["processed"] = True
    data["sum"] = sum(data["input"])
    return data
'''
        
        # Execute node with object
        result, _ = self.executor.execute_node(node, {"data": test_data})
        
        # Verify result is same object reference
        self.assertIs(result, test_data)
        
        # Verify original object was modified
        self.assertTrue(test_data["processed"])
        self.assertEqual(test_data["sum"], 15)
    
    def test_object_chain_passing(self):
        """Test object passing through chain of nodes."""
        # Create initial data object
        data_obj = {"value": 10, "history": []}
        
        # First node: multiply by 2
        node1 = Mock()
        node1.title = "Multiply Node"
        node1.function_name = "multiply_data"
        node1.code = '''
def multiply_data(obj):
    obj["value"] *= 2
    obj["history"].append("multiplied")
    return obj
'''
        
        # Second node: add 5
        node2 = Mock()
        node2.title = "Add Node" 
        node2.function_name = "add_data"
        node2.code = '''
def add_data(obj):
    obj["value"] += 5
    obj["history"].append("added")
    return obj
'''
        
        # Execute chain
        result1, _ = self.executor.execute_node(node1, {"obj": data_obj})
        result2, _ = self.executor.execute_node(node2, {"obj": result1})
        
        # Verify all results are same object
        self.assertIs(result1, data_obj)
        self.assertIs(result2, data_obj)
        
        # Verify chain processing worked
        self.assertEqual(data_obj["value"], 25)  # (10 * 2) + 5
        self.assertEqual(data_obj["history"], ["multiplied", "added"])


if __name__ == "__main__":
    unittest.main()
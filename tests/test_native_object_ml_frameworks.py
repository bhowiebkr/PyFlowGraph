"""
Integration tests for ML framework objects in native object passing system.
Tests Story 3.3 - Native Object Passing System Subtask 6.2
"""

import unittest
import sys
import os
import gc
from unittest.mock import Mock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from execution.single_process_executor import SingleProcessExecutor


class TestMLFrameworkObjectPassing(unittest.TestCase):
    """Test ML framework object passing without serialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
    
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def test_numpy_array_direct_passing(self):
        """Test AC2: NumPy array support with dtype preservation."""
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy not available")
        
        # Create NumPy array with specific dtype
        arr = np.array([1.5, 2.7, 3.14, 4.9], dtype=np.float32)
        original_id = id(arr)
        original_dtype = arr.dtype
        original_shape = arr.shape
        
        # Store and retrieve
        self.executor.store_object("numpy_array", arr)
        retrieved = self.executor.get_object("numpy_array")
        
        # Verify same object reference (not copy)
        self.assertIs(retrieved, arr)
        self.assertEqual(id(retrieved), original_id)
        
        # Verify dtype and shape preserved
        self.assertEqual(retrieved.dtype, original_dtype)
        self.assertEqual(retrieved.shape, original_shape)
        
        # Verify modifications affect original
        retrieved[0] = 9.9
        self.assertEqual(arr[0], 9.9)
    
    def test_numpy_array_node_execution(self):
        """Test NumPy arrays passed through node execution."""
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy not available")
        
        # Create test array
        input_array = np.array([[1, 2], [3, 4]], dtype=np.int32)
        
        # Create node that processes NumPy array
        node = Mock()
        node.title = "NumPy Processor"
        node.function_name = "process_array"
        node.code = '''
import numpy as np
def process_array(arr):
    # Modify array in-place and return
    arr *= 2
    return arr.sum(), arr
'''
        
        # Execute node
        result, _ = self.executor.execute_node(node, {"arr": input_array})
        
        # Verify result contains sum and modified array
        sum_result, array_result = result
        self.assertEqual(sum_result, 20)  # (1+2+3+4) * 2 = 20
        self.assertIs(array_result, input_array)  # Same object reference
        
        # Verify original array was modified
        expected = np.array([[2, 4], [6, 8]], dtype=np.int32)
        np.testing.assert_array_equal(input_array, expected)
    
    def test_pytorch_tensor_direct_passing(self):
        """Test AC2: PyTorch tensor support with device management."""
        try:
            import torch
        except ImportError:
            self.skipTest("PyTorch not available")
        
        # Create PyTorch tensor
        tensor = torch.tensor([1.0, 2.0, 3.0, 4.0], dtype=torch.float32)
        original_id = id(tensor)
        original_device = tensor.device
        original_dtype = tensor.dtype
        
        # Store and retrieve
        self.executor.store_object("torch_tensor", tensor)
        retrieved = self.executor.get_object("torch_tensor")
        
        # Verify same object reference
        self.assertIs(retrieved, tensor)
        self.assertEqual(id(retrieved), original_id)
        
        # Verify device and dtype preserved
        self.assertEqual(retrieved.device, original_device)
        self.assertEqual(retrieved.dtype, original_dtype)
        
        # Verify modifications affect original
        retrieved[0] = 9.0
        self.assertEqual(tensor[0].item(), 9.0)
    
    def test_pytorch_tensor_node_execution(self):
        """Test PyTorch tensors passed through node execution."""
        try:
            import torch
        except ImportError:
            self.skipTest("PyTorch not available")
        
        # Create test tensor
        input_tensor = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        
        # Create node that processes PyTorch tensor
        node = Mock()
        node.title = "PyTorch Processor"
        node.function_name = "process_tensor"
        node.code = '''
import torch
def process_tensor(tensor):
    # Modify tensor in-place and return processed result
    tensor *= 2.0
    return tensor.sum().item(), tensor
'''
        
        # Execute node
        result, _ = self.executor.execute_node(node, {"tensor": input_tensor})
        
        # Verify result
        sum_result, tensor_result = result
        self.assertEqual(sum_result, 20.0)  # (1+2+3+4) * 2 = 20
        self.assertIs(tensor_result, input_tensor)  # Same object reference
        
        # Verify original tensor was modified
        expected = torch.tensor([[2.0, 4.0], [6.0, 8.0]])
        torch.testing.assert_allclose(input_tensor, expected)
    
    def test_pytorch_gpu_tensor_device_preservation(self):
        """Test GPU tensor device preservation if CUDA available."""
        try:
            import torch
        except ImportError:
            self.skipTest("PyTorch not available")
        
        if not torch.cuda.is_available():
            self.skipTest("CUDA not available")
        
        # Create GPU tensor
        gpu_tensor = torch.tensor([1.0, 2.0, 3.0]).cuda()
        original_device = gpu_tensor.device
        
        # Store and retrieve
        self.executor.store_object("gpu_tensor", gpu_tensor)
        retrieved = self.executor.get_object("gpu_tensor")
        
        # Verify same object and device preserved
        self.assertIs(retrieved, gpu_tensor)
        self.assertEqual(retrieved.device, original_device)
        self.assertTrue(retrieved.is_cuda)
    
    def test_pandas_dataframe_direct_passing(self):
        """Test AC2: Pandas DataFrame support with index/column preservation."""
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("Pandas not available")
        
        # Create DataFrame with specific index and columns
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4.0, 5.0, 6.0],
            'C': ['x', 'y', 'z']
        }, index=['row1', 'row2', 'row3'])
        
        original_id = id(df)
        original_index = df.index.copy()
        original_columns = df.columns.copy()
        
        # Store and retrieve
        self.executor.store_object("pandas_df", df)
        retrieved = self.executor.get_object("pandas_df")
        
        # Verify same object reference
        self.assertIs(retrieved, df)
        self.assertEqual(id(retrieved), original_id)
        
        # Verify index and columns preserved
        pd.testing.assert_index_equal(retrieved.index, original_index)
        pd.testing.assert_index_equal(retrieved.columns, original_columns)
        
        # Verify modifications affect original
        retrieved.loc['row1', 'A'] = 99
        self.assertEqual(df.loc['row1', 'A'], 99)
    
    def test_pandas_dataframe_node_execution(self):
        """Test Pandas DataFrames passed through node execution."""
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("Pandas not available")
        
        # Create test DataFrame
        df = pd.DataFrame({
            'values': [1, 2, 3, 4],
            'categories': ['A', 'B', 'A', 'B']
        })
        
        # Create node that processes DataFrame
        node = Mock()
        node.title = "Pandas Processor"
        node.function_name = "process_dataframe"
        node.code = '''
import pandas as pd
def process_dataframe(df):
    # Add new column and return stats
    df["doubled"] = df["values"] * 2
    return df["values"].sum(), df
'''
        
        # Execute node
        result, _ = self.executor.execute_node(node, {"df": df})
        
        # Verify result
        sum_result, df_result = result
        self.assertEqual(sum_result, 10)  # 1+2+3+4 = 10
        self.assertIs(df_result, df)  # Same object reference
        
        # Verify original DataFrame was modified
        self.assertTrue("doubled" in df.columns)
        expected_doubled = [2, 4, 6, 8]
        self.assertEqual(df["doubled"].tolist(), expected_doubled)
    
    def test_tensorflow_tensor_direct_passing(self):
        """Test TensorFlow tensor passing if available."""
        try:
            import tensorflow as tf
        except ImportError:
            self.skipTest("TensorFlow not available")
        
        # Create TensorFlow tensor
        tensor = tf.constant([1.0, 2.0, 3.0, 4.0], dtype=tf.float32)
        original_id = id(tensor)
        
        # Store and retrieve
        self.executor.store_object("tf_tensor", tensor)
        retrieved = self.executor.get_object("tf_tensor")
        
        # Verify same object reference
        self.assertIs(retrieved, tensor)
        self.assertEqual(id(retrieved), original_id)
        
        # Verify tensor properties preserved
        self.assertEqual(retrieved.dtype, tf.float32)
        self.assertEqual(retrieved.shape, tensor.shape)
        tf.debugging.assert_equal(retrieved, tensor)
    
    def test_complex_ml_object_composition(self):
        """Test complex objects containing multiple ML framework objects."""
        frameworks_available = []
        ml_objects = {}
        
        # Build object with available frameworks
        try:
            import numpy as np
            ml_objects["numpy_array"] = np.array([1, 2, 3])
            frameworks_available.append("numpy")
        except ImportError:
            pass
        
        try:
            import torch
            ml_objects["torch_tensor"] = torch.tensor([4.0, 5.0, 6.0])
            frameworks_available.append("torch")
        except ImportError:
            pass
        
        try:
            import pandas as pd
            ml_objects["pandas_df"] = pd.DataFrame({"col": [7, 8, 9]})
            frameworks_available.append("pandas")
        except ImportError:
            pass
        
        if not frameworks_available:
            self.skipTest("No ML frameworks available")
        
        # Create complex object containing ML objects
        complex_obj = {
            "ml_data": ml_objects,
            "metadata": {"frameworks": frameworks_available},
            "processing_chain": []
        }
        
        # Store and retrieve
        self.executor.store_object("complex_ml", complex_obj)
        retrieved = self.executor.get_object("complex_ml")
        
        # Verify same object reference at all levels
        self.assertIs(retrieved, complex_obj)
        self.assertIs(retrieved["ml_data"], ml_objects)
        
        for framework in frameworks_available:
            if framework == "numpy":
                self.assertIs(retrieved["ml_data"]["numpy_array"], ml_objects["numpy_array"])
            elif framework == "torch":
                self.assertIs(retrieved["ml_data"]["torch_tensor"], ml_objects["torch_tensor"])
            elif framework == "pandas":
                self.assertIs(retrieved["ml_data"]["pandas_df"], ml_objects["pandas_df"])
    
    def test_framework_object_chain_processing(self):
        """Test ML objects passed through chain of processing nodes."""
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy not available")
        
        # Create initial array
        data = np.array([1.0, 2.0, 3.0, 4.0])
        
        # First node: normalize
        node1 = Mock()
        node1.title = "Normalize"
        node1.function_name = "normalize_array"
        node1.code = '''
import numpy as np
def normalize_array(arr):
    mean = arr.mean()
    std = arr.std()
    arr -= mean  # In-place modification
    arr /= std
    return arr
'''
        
        # Second node: scale
        node2 = Mock()
        node2.title = "Scale"
        node2.function_name = "scale_array"
        node2.code = '''
import numpy as np
def scale_array(arr):
    arr *= 100.0  # In-place scaling
    return arr
'''
        
        # Execute processing chain
        result1, _ = self.executor.execute_node(node1, {"arr": data})
        result2, _ = self.executor.execute_node(node2, {"arr": result1})
        
        # Verify all results are same object
        self.assertIs(result1, data)
        self.assertIs(result2, data)
        
        # Verify processing was applied to original array
        # After normalization and scaling, values should be scaled z-scores
        self.assertTrue(abs(data.mean()) < 1e-10)  # Mean should be ~0 after normalization
        self.assertTrue(abs(abs(data).max() - abs(data).min()) > 50)  # Should be scaled


class TestFrameworkAutoImport(unittest.TestCase):
    """Test automatic framework imports in persistent namespace."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.log = []
        self.executor = SingleProcessExecutor(self.log)
    
    def tearDown(self):
        """Clean up after tests."""
        self.executor.reset_namespace()
        gc.collect()
    
    def test_numpy_auto_import_availability(self):
        """Test numpy automatically available in namespace."""
        try:
            import numpy
        except ImportError:
            self.skipTest("NumPy not available on system")
        
        # Check if numpy is in namespace after initialization
        self.assertIn('numpy', self.executor.namespace)
        self.assertIn('np', self.executor.namespace)
        
        # Verify it's the actual numpy module
        self.assertIs(self.executor.namespace['numpy'], numpy)
    
    def test_pandas_auto_import_availability(self):
        """Test pandas automatically available in namespace."""
        try:
            import pandas
        except ImportError:
            self.skipTest("Pandas not available on system")
        
        # Check if pandas is in namespace after initialization  
        self.assertIn('pandas', self.executor.namespace)
        self.assertIn('pd', self.executor.namespace)
        
        # Verify it's the actual pandas module
        self.assertIs(self.executor.namespace['pandas'], pandas)
    
    def test_torch_auto_import_availability(self):
        """Test torch automatically available in namespace."""
        try:
            import torch
        except ImportError:
            self.skipTest("PyTorch not available on system")
        
        # Check if torch is in namespace after initialization
        self.assertIn('torch', self.executor.namespace)
        
        # Verify it's the actual torch module  
        self.assertIs(self.executor.namespace['torch'], torch)
    
    def test_tensorflow_auto_import_availability(self):
        """Test tensorflow automatically available in namespace."""
        try:
            import tensorflow
        except ImportError:
            self.skipTest("TensorFlow not available on system")
        
        # Check if tensorflow is in namespace after initialization
        self.assertIn('tensorflow', self.executor.namespace)
        self.assertIn('tf', self.executor.namespace)
        
        # Verify it's the actual tensorflow module
        self.assertIs(self.executor.namespace['tensorflow'], tensorflow)


if __name__ == "__main__":
    unittest.main()
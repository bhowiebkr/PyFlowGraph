# single_process_executor.py
# Executes nodes directly in the current Python interpreter for maximum performance.
# Replaces subprocess isolation with direct function calls and object references.

import os
import sys
import io
import gc
import time
import weakref
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional, Callable, List, Tuple

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.node import Node
from src.core.reroute_node import RerouteNode


class SingleProcessExecutor:
    """Executes nodes directly in a single persistent Python interpreter."""
    
    def __init__(self, log_widget=None):
        """Initialize the single process executor.
        
        Args:
            log_widget: Optional logging widget for output messages
        """
        self.log = log_widget if log_widget is not None else []
        
        # Persistent namespace for all node executions
        self.namespace: Dict[str, Any] = {}
        
        # Direct object storage for pin values (no serialization)
        self.object_store: Dict[Any, Any] = {}
        
        # Performance tracking
        self.execution_times: Dict[str, float] = {}
        
        # Reference counting for memory management
        self.object_refs: Dict[Any, int] = weakref.WeakValueDictionary()
        
        # Initialize with essential imports
        self._initialize_namespace()
    
    def _initialize_namespace(self):
        """Initialize persistent namespace with common imports and utilities."""
        # Add the node_entry decorator that nodes expect
        self.namespace['node_entry'] = lambda func: func
        
        # Add common imports that nodes might use
        essential_modules = {
            'json': __import__('json'),
            'sys': __import__('sys'),
            'os': __import__('os'),
            'time': __import__('time'),
            'math': __import__('math'),
            're': __import__('re'),
        }
        
        self.namespace.update(essential_modules)
        
        # Try to import common data science libraries (optional)
        optional_modules = ['numpy', 'pandas', 'torch', 'tensorflow']
        for module_name in optional_modules:
            try:
                module = __import__(module_name)
                self.namespace[module_name] = module
            except ImportError:
                # Module not available, skip
                pass
    
    def execute_node(self, node: Node, inputs: Dict[str, Any]) -> Tuple[Any, str]:
        """Execute a single node directly in the current interpreter.
        
        Args:
            node: The node to execute
            inputs: Dictionary of input values for the node
            
        Returns:
            Tuple of (result, captured_output)
        """
        if not node.function_name:
            return None, f"SKIP: Node '{node.title}' has no valid function defined."
        
        start_time = time.perf_counter()
        
        # Capture stdout for logging
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Execute the node's code directly in the persistent namespace
            # This ensures all definitions (functions, variables, imports) persist
            temp_namespace = {**self.namespace, **inputs}
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute code directly in persistent namespace to ensure persistence
                exec(node.code, temp_namespace)
                
                # Update persistent namespace with all new definitions
                self.namespace.update(temp_namespace)
                
                # Call the node's function with inputs
                if node.function_name in temp_namespace:
                    function = temp_namespace[node.function_name]
                    result = function(**inputs)
                else:
                    raise RuntimeError(f"Function '{node.function_name}' not found after code execution")
            
            # Record performance
            execution_time = time.perf_counter() - start_time
            self.execution_times[node.title] = execution_time
            
            # Get captured output
            captured_output = stdout_capture.getvalue()
            captured_errors = stderr_capture.getvalue()
            
            output_message = ""
            if captured_output:
                output_message += captured_output.strip()
            if captured_errors:
                output_message += f"\nSTDERR: {captured_errors.strip()}"
            
            return result, output_message
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            self.execution_times[node.title] = execution_time
            
            error_message = f"ERROR in node '{node.title}': {e}"
            
            # Include any captured stderr
            captured_errors = stderr_capture.getvalue()
            if captured_errors:
                error_message += f"\nSTDERR: {captured_errors.strip()}"
                
            raise RuntimeError(error_message) from e
    
    def _update_persistent_namespace(self, exec_globals: Dict[str, Any]):
        """Update persistent namespace with new imports and variables.
        
        Args:
            exec_globals: The globals dict after node execution
        """
        # Update with new imports and module-level definitions
        for key, value in exec_globals.items():
            if key.startswith('__') and key.endswith('__'):
                continue  # Skip built-in attributes
                
            # Add new modules and functions to persistent namespace
            if (hasattr(value, '__module__') or 
                callable(value) or 
                key in ['np', 'pd', 'torch', 'tf', 'plt']):  # Common aliases
                self.namespace[key] = value
    
    def store_object(self, key: Any, value: Any):
        """Store an object directly without serialization.
        
        Args:
            key: Key to store the object under
            value: The object to store (direct reference)
        """
        self.object_store[key] = value
    
    def get_object(self, key: Any) -> Any:
        """Retrieve a stored object by direct reference.
        
        Args:
            key: Key to retrieve the object
            
        Returns:
            The stored object (direct reference)
        """
        return self.object_store.get(key)
    
    def cleanup_memory(self):
        """Perform memory cleanup and garbage collection."""
        # Clear execution times older than last 100 executions
        if len(self.execution_times) > 100:
            items = list(self.execution_times.items())
            self.execution_times = dict(items[-100:])
        
        # Force garbage collection
        collected = gc.collect()
        
        # GPU memory cleanup if available
        self._cleanup_gpu_memory()
        
        return collected
    
    def _cleanup_gpu_memory(self):
        """Clean up GPU memory if PyTorch is available."""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except ImportError:
            pass  # PyTorch not available
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for executed nodes.
        
        Returns:
            Dictionary of performance statistics
        """
        if not self.execution_times:
            return {}
            
        times = list(self.execution_times.values())
        return {
            'total_executions': len(times),
            'total_time': sum(times),
            'average_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'recent_executions': dict(list(self.execution_times.items())[-10:])
        }
    
    def reset_namespace(self):
        """Reset the persistent namespace (useful for testing)."""
        self.namespace.clear()
        self.object_store.clear()
        self.execution_times.clear()
        self._initialize_namespace()
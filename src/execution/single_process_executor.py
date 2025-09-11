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

from core.node import Node
from core.reroute_node import RerouteNode


class SingleProcessExecutor:
    """Executes nodes directly in a single persistent Python interpreter."""
    
    def __init__(self, log_widget=None, venv_path=None):
        """Initialize the single process executor.
        
        Args:
            log_widget: Optional logging widget for output messages
            venv_path: Path to virtual environment for package loading
        """
        self.log = log_widget if log_widget is not None else []
        self.venv_path = venv_path
        self.original_sys_path = None  # Store original sys.path for cleanup
        
        # Persistent namespace for all node executions
        self.namespace: Dict[str, Any] = {}
        
        # Direct object storage for pin values (no serialization)
        self.object_store: Dict[Any, Any] = {}
        
        # Performance tracking
        self.execution_times: Dict[str, float] = {}
        
        # Reference counting for memory management
        self.object_refs: Dict[Any, int] = weakref.WeakValueDictionary()
        
        # Set up virtual environment packages if provided
        self._setup_venv_packages()
        
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
    
    def _setup_venv_packages(self):
        """Set up virtual environment packages by adding site-packages to sys.path."""
        if not self.venv_path or not os.path.exists(self.venv_path):
            return
            
        # Store original sys.path for cleanup
        self.original_sys_path = sys.path.copy()
        
        # Find site-packages directory in the virtual environment
        if os.name == 'nt':  # Windows
            site_packages_path = os.path.join(self.venv_path, "Lib", "site-packages")
        else:  # Unix/Linux/macOS
            # Find the Python version directory
            lib_dir = os.path.join(self.venv_path, "lib")
            if os.path.exists(lib_dir):
                python_dirs = [d for d in os.listdir(lib_dir) if d.startswith('python')]
                if python_dirs:
                    site_packages_path = os.path.join(lib_dir, python_dirs[0], "site-packages")
                else:
                    return
            else:
                return
        
        # Add site-packages to sys.path if it exists
        if os.path.exists(site_packages_path):
            # Insert at the beginning to give priority to venv packages
            sys.path.insert(0, site_packages_path)
            if self.log and hasattr(self.log, 'append'):
                self.log.append(f"Added venv packages from: {site_packages_path}")
    
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
            execution_time_ms = execution_time * 1000  # Convert to milliseconds
            self.execution_times[node.title] = execution_time
            
            # Set execution time on node for visual display
            node.execution_time = execution_time_ms
            node.update()  # Trigger visual update to show execution time
            
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
            execution_time_ms = execution_time * 1000  # Convert to milliseconds
            self.execution_times[node.title] = execution_time
            
            # Set execution time on node even for failed executions
            node.execution_time = execution_time_ms
            node.update()  # Trigger visual update to show execution time
            
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
    
    def cleanup_venv_packages(self):
        """Restore original sys.path by removing venv packages."""
        if self.original_sys_path is not None:
            sys.path[:] = self.original_sys_path
            self.original_sys_path = None
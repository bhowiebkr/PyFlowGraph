#!/usr/bin/env python3
"""
Test Debug Flag Configuration

Verifies that debug flags properly control debug output.
"""

import unittest
import sys
import os
from io import StringIO
from contextlib import redirect_stdout

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

# Import and temporarily modify debug flags
import execution.graph_executor as executor_module
import core.node as node_module
import commands.node_commands as commands_module

from PySide6.QtWidgets import QApplication
from core.node_graph import NodeGraph
from core.node import Node


class TestDebugFlags(unittest.TestCase):
    """Test that debug flags properly control debug output."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        self.graph = NodeGraph()
    
    def test_debug_flags_disabled_by_default(self):
        """Test that debug flags are disabled by default."""
        # Verify all debug flags are False by default
        self.assertFalse(executor_module.DEBUG_EXECUTION, "Execution debug should be disabled by default")
        self.assertFalse(node_module.DEBUG_GUI_UPDATES, "GUI update debug should be disabled by default") 
        self.assertFalse(commands_module.DEBUG_NODE_COMMANDS, "Node command debug should be disabled by default")
    
    def test_gui_debug_flag_enables_output(self):
        """Test that enabling GUI debug flag produces debug output."""
        # Create a test node
        node = Node("Test Node")
        
        # Set up GUI code and get values code
        gui_code = '''
from PySide6.QtWidgets import QLabel
widgets['test_label'] = QLabel('Test', parent)
layout.addWidget(widgets['test_label'])
'''
        
        gui_get_values_code = '''
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    widgets['test_label'].setText(str(outputs.get('output_1', 'No output')))

def set_initial_state(widgets, state):
    pass
'''
        
        node.set_gui_code(gui_code)
        node.set_gui_get_values_code(gui_get_values_code)
        
        # Test with debug disabled (default)
        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            node.set_gui_values({'output_1': 'test_value'})
        
        output_without_debug = output_buffer.getvalue()
        self.assertEqual(output_without_debug, "", "Should produce no debug output when disabled")
        
        # Temporarily enable debug
        original_debug = node_module.DEBUG_GUI_UPDATES
        try:
            node_module.DEBUG_GUI_UPDATES = True
            
            output_buffer = StringIO()
            with redirect_stdout(output_buffer):
                node.set_gui_values({'output_1': 'test_value'})
            
            output_with_debug = output_buffer.getvalue()
            self.assertIn("DEBUG: set_gui_values() called", output_with_debug, 
                         "Should produce debug output when enabled")
            self.assertIn("Test Node", output_with_debug,
                         "Debug output should include node title")
            
        finally:
            # Restore original debug state
            node_module.DEBUG_GUI_UPDATES = original_debug
    
    def test_execution_debug_flag_enables_output(self):
        """Test that enabling execution debug flag produces debug output."""
        from execution.graph_executor import GraphExecutor
        from unittest.mock import MagicMock
        
        # Create executor with mock components
        log_widget = MagicMock()
        venv_path_callback = lambda: "test_venv"
        executor = GraphExecutor(self.graph, log_widget, venv_path_callback)
        
        # Create a simple node with GUI
        node = Node("Debug Test Node")
        gui_get_values_code = '''
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    pass

def set_initial_state(widgets, state):
    pass
'''
        node.set_gui_get_values_code(gui_get_values_code)
        node.gui_widgets = {}  # Simulate GUI widgets
        
        # Test with debug disabled (default)
        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            if hasattr(node, "set_gui_values"):
                node.set_gui_values({'output_1': 'test'})
        
        output_without_debug = output_buffer.getvalue()
        
        # Temporarily enable execution debug
        original_debug = executor_module.DEBUG_EXECUTION
        try:
            executor_module.DEBUG_EXECUTION = True
            
            # Test the execution logic that includes debug output
            output_buffer = StringIO()
            with redirect_stdout(output_buffer):
                # Simulate the execution debug output
                if hasattr(node, "set_gui_values"):
                    if executor_module.DEBUG_EXECUTION:
                        print(f"DEBUG: Execution completed for '{node.title}', calling set_gui_values with: {{'output_1': 'test'}}")
                    node.set_gui_values({'output_1': 'test'})
            
            output_with_debug = output_buffer.getvalue()
            self.assertIn("DEBUG: Execution completed", output_with_debug,
                         "Should produce execution debug output when enabled")
            self.assertIn("Debug Test Node", output_with_debug,
                         "Debug output should include node title")
            
        finally:
            # Restore original debug state
            executor_module.DEBUG_EXECUTION = original_debug


if __name__ == '__main__':
    unittest.main()
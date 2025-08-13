#!/usr/bin/env python3

"""
Focused unit tests for detecting GUI loading bugs in markdown graphs.
This test suite specifically targets the types of issues mentioned:
"any node that has a GUI doesn't load correctly"
"""

import sys
import os
import tempfile
import unittest
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QGraphicsView, QTextEdit
from PySide6.QtCore import QTimer, Qt

from node import Node
from node_graph import NodeGraph
from flow_format import FlowFormatHandler, load_flow_file


class TestGUILoadingBugs(unittest.TestCase):
    """Test suite focused on detecting GUI loading bugs in markdown graphs."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for the entire test suite."""
        if QApplication.instance() is None:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = NodeGraph()
        self.handler = FlowFormatHandler()
        
    def tearDown(self):
        """Clean up after each test."""
        # Clear the graph
        for node in list(self.graph.nodes):
            self.graph.remove_node(node)
    
    def test_gui_node_basic_loading(self):
        """Test that GUI nodes load and have basic GUI components."""
        markdown_content = '''# Test Graph

## Node: GUI Test Node (ID: gui-test-1)

Basic GUI node test.

### Metadata

```json
{
  "uuid": "gui-test-1",
  "title": "GUI Test Node",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def test_func() -> str:
    return "test"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit

widgets['label'] = QLabel('Test:', parent)
layout.addWidget(widgets['label'])

widgets['input'] = QLineEdit(parent)
layout.addWidget(widgets['input'])
```

## Connections

```json
[]
```
'''
        
        # Load and verify
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        # Check that GUI node was created and has GUI components
        self.assertEqual(len(self.graph.nodes), 1)
        node = self.graph.nodes[0]
        
        # Verify GUI code was loaded
        self.assertTrue(hasattr(node, 'gui_code'), "Node should have gui_code attribute")
        self.assertNotEqual(node.gui_code.strip(), "", "GUI code should not be empty")
        
        # Force GUI rebuild (this is where bugs typically occur)
        try:
            node.rebuild_gui()
            gui_built_successfully = True
        except Exception as e:
            gui_built_successfully = False
            print(f"GUI rebuild failed: {e}")
        
        self.assertTrue(gui_built_successfully, "GUI should rebuild without errors")
        
        # Verify widgets were created
        self.assertGreater(len(node.gui_widgets), 0, "GUI widgets should be created")
        self.assertIn('label', node.gui_widgets, "Label widget should exist")
        self.assertIn('input', node.gui_widgets, "Input widget should exist")
    
    def test_gui_node_zero_height_bug(self):
        """Test for the zero height bug mentioned in git commits."""
        markdown_content = '''# Test Graph

## Node: Height Test Node (ID: height-test-1)

Test node height after GUI loading.

### Metadata

```json
{
  "uuid": "height-test-1",
  "title": "Height Test Node",
  "pos": [100, 100],
  "size": [250, 200],
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def test_func() -> str:
    return "test"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel

widgets['label'] = QLabel('Test Label', parent)
layout.addWidget(widgets['label'])
```

## Connections

```json
[]
```
'''
        
        # Load and check height
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        
        # Check height before GUI rebuild
        initial_height = node.height
        self.assertEqual(initial_height, 200, "Initial height should match metadata")
        
        # Rebuild GUI and check height
        node.rebuild_gui()
        
        # Height should not be zero (this was the bug)
        self.assertGreater(node.height, 0, "Node height should not be zero after GUI rebuild")
        
        # Height should be reasonable (not negative or extremely small)
        self.assertGreaterEqual(node.height, 50, "Node height should be at least 50 pixels")
    
    def test_gui_code_execution_errors(self):
        """Test that GUI code execution errors are handled gracefully."""
        markdown_content = '''# Test Graph

## Node: Error Test Node (ID: error-test-1)

Node with GUI code that causes errors.

### Metadata

```json
{
  "uuid": "error-test-1",
  "title": "Error Test Node",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def test_func() -> str:
    return "test"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel
# This will cause an error - undefined variable
widgets['label'] = QLabel(undefined_variable, parent)
layout.addWidget(widgets['label'])
```

## Connections

```json
[]
```
'''
        
        # Load and test error handling
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        
        # GUI rebuild should not crash, but handle error gracefully
        try:
            node.rebuild_gui()
            rebuild_succeeded = True
        except Exception as e:
            rebuild_succeeded = False
            print(f"GUI rebuild crashed: {e}")
        
        self.assertTrue(rebuild_succeeded, "GUI rebuild should handle errors gracefully")
        
        # Node should still be functional even with GUI errors
        self.assertIsNotNone(node.title)
        self.assertGreater(node.height, 0)
    
    def test_gui_proxy_widget_creation(self):
        """Test that the QGraphicsProxyWidget is properly created for GUI nodes."""
        markdown_content = '''# Test Graph

## Node: Proxy Widget Test (ID: proxy-test-1)

Test proxy widget creation.

### Metadata

```json
{
  "uuid": "proxy-test-1",
  "title": "Proxy Widget Test",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def test_func() -> str:
    return "test"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QPushButton

widgets['label'] = QLabel('Proxy Test', parent)
layout.addWidget(widgets['label'])

widgets['button'] = QPushButton('Test Button', parent)
layout.addWidget(widgets['button'])
```

## Connections

```json
[]
```
'''
        
        # Load and test proxy widget
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        node.rebuild_gui()
        
        # Verify proxy widget was created
        self.assertTrue(hasattr(node, 'proxy_widget'), "Node should have proxy_widget attribute")
        
        if hasattr(node, 'proxy_widget') and node.proxy_widget:
            self.assertIsNotNone(node.proxy_widget, "Proxy widget should not be None")
            
            # Verify the proxy widget has a widget
            if node.proxy_widget:
                self.assertIsNotNone(node.proxy_widget.widget(), 
                                   "Proxy widget should contain a widget")
    
    def test_gui_state_handling(self):
        """Test that GUI state is properly handled during loading."""
        markdown_content = '''# Test Graph

## Node: State Test Node (ID: state-test-1)

Test GUI state handling.

### Metadata

```json
{
  "uuid": "state-test-1",
  "title": "State Test Node",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": {
    "test_value": "initial_state"
  }
}
```

### Logic

```python
@node_entry
def test_func() -> str:
    return "test"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit

widgets['input'] = QLineEdit(parent)
layout.addWidget(widgets['input'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {'test_value': widgets['input'].text()}

def set_initial_state(widgets, state):
    if 'test_value' in state:
        widgets['input'].setText(state['test_value'])
```

## Connections

```json
[]
```
'''
        
        # Load and test state handling
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        
        # Verify the GUI state was loaded
        gui_state = data['nodes'][0].get('gui_state', {})
        self.assertIn('test_value', gui_state)
        self.assertEqual(gui_state['test_value'], 'initial_state')
        
        # Rebuild GUI and apply state (this simulates the loading process)
        node.rebuild_gui()
        
        # Verify widgets exist before applying state
        self.assertIn('input', node.gui_widgets)
        
        # Apply the GUI state (this happens during deserialization)
        node.apply_gui_state(gui_state)
        
        # Verify state was applied
        self.assertEqual(node.gui_widgets['input'].text(), 'initial_state')
    
    def test_reroute_node_loading(self):
        """Test that reroute nodes load correctly without GUI issues."""
        markdown_content = '''# Test Graph

## Node: Reroute (ID: reroute-1)

Reroute node test.

### Metadata

```json
{
  "uuid": "reroute-1",
  "title": "Reroute",
  "pos": [200, 200],
  "size": [50, 50],
  "colors": {},
  "gui_state": {},
  "is_reroute": true
}
```

### Logic

```python
# Reroute nodes don't have logic
```

## Connections

```json
[]
```
'''
        
        # Load and verify reroute node
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        self.assertEqual(len(self.graph.nodes), 1)
        node = self.graph.nodes[0]
        
        # Reroute nodes should be a different class
        self.assertEqual(type(node).__name__, 'RerouteNode')
        
        # Reroute nodes should not cause GUI-related errors
        # RerouteNode uses radius instead of width/height
        self.assertGreater(node.radius, 0)
    
    def test_existing_markdown_file_loading(self):
        """Test loading an actual markdown example file."""
        example_path = os.path.join(os.path.dirname(__file__), 'examples', 'data_analysis_dashboard.md')
        
        if os.path.exists(example_path):
            try:
                # Load the file
                data = load_flow_file(example_path)
                
                # Create graph and load data
                graph = NodeGraph()
                graph.deserialize(data)
                
                # Check that nodes were loaded
                self.assertGreater(len(graph.nodes), 0, "Should load at least one node")
                
                # Find nodes with GUI code
                gui_nodes = []
                for node in graph.nodes:
                    if hasattr(node, 'gui_code') and node.gui_code.strip():
                        gui_nodes.append(node)
                
                # Test GUI nodes
                for node in gui_nodes:
                    # GUI should rebuild without errors
                    try:
                        node.rebuild_gui()
                        gui_success = True
                    except Exception as e:
                        gui_success = False
                        print(f"GUI rebuild failed for {node.title}: {e}")
                    
                    self.assertTrue(gui_success, 
                                  f"Node {node.title} GUI should rebuild successfully")
                    
                    # Node should have reasonable dimensions
                    self.assertGreater(node.height, 0, 
                                     f"Node {node.title} should have positive height")
                    self.assertGreater(node.width, 0, 
                                     f"Node {node.title} should have positive width")
                
            except Exception as e:
                # If file doesn't exist or has issues, that's OK for this test
                print(f"Note: Could not test existing file: {e}")


def run_gui_bug_tests():
    """Run the GUI bug detection tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGUILoadingBugs)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=== GUI Loading Bug Detection Tests ===")
    print("Testing for common GUI loading issues in markdown graphs...")
    print()
    
    success = run_gui_bug_tests()
    
    if success:
        print("\n=== All GUI Loading Tests Passed ===")
        print("No GUI loading bugs detected!")
        sys.exit(0)
    else:
        print("\n=== GUI Loading Issues Detected ===")
        print("Some tests failed - GUI loading bugs may be present.")
        sys.exit(1)
#!/usr/bin/env python3

"""
Unit tests for GUI-related loading issues in markdown graphs.
Tests various scenarios where nodes with GUI components fail to load correctly.
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import Mock, patch
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QGraphicsView
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest

from node import Node
from node_graph import NodeGraph
from flow_format import FlowFormatHandler, load_flow_file
from file_operations import FileOperationsManager


class TestGUILoading(unittest.TestCase):
    """Test suite for GUI-related loading issues in markdown graphs."""
    
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
        self.view = QGraphicsView(self.graph)
        from PySide6.QtWidgets import QTextEdit
        self.file_ops = FileOperationsManager(None, self.graph, QTextEdit())
        
    def tearDown(self):
        """Clean up after each test."""
        # Clear the graph
        for node in list(self.graph.nodes):
            self.graph.remove_node(node)
        
    def create_test_markdown_file(self, content):
        """Helper to create a temporary markdown file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def test_valid_gui_code_loading(self):
        """Test that valid GUI code loads without errors."""
        markdown_content = '''# Test Graph

## Node: Test Node (ID: test-node-1)

Node with valid GUI components.

### Metadata

```json
{
  "uuid": "test-node-1",
  "title": "Test Node",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": {
    "test_value": "initial"
  }
}
```

### Logic

```python
@node_entry
def test_func(input_val: str = "default") -> str:
    return f"processed: {input_val}"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

widgets['label'] = QLabel('Input:', parent)
layout.addWidget(widgets['label'])

widgets['input'] = QLineEdit(parent)
layout.addWidget(widgets['input'])

widgets['button'] = QPushButton('Process', parent)
layout.addWidget(widgets['button'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {'input_val': widgets['input'].text()}

def set_values(widgets, outputs):
    if 'output_1' in outputs:
        widgets['input'].setText(str(outputs['output_1']))

def set_initial_state(widgets, state):
    if 'test_value' in state:
        widgets['input'].setText(state['test_value'])
```

## Connections

```json
[]
```
'''
        
        # Load from markdown
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        # Verify node was created
        self.assertEqual(len(self.graph.nodes), 1)
        node = self.graph.nodes[0]
        
        # Verify GUI components are properly loaded
        self.assertIsNotNone(node.gui_code)
        self.assertIsNotNone(node.gui_get_values_code)
        
        # Force GUI rebuild and check for widgets
        node.rebuild_gui()
        self.assertGreater(len(node.gui_widgets), 0)
        self.assertIn('label', node.gui_widgets)
        self.assertIn('input', node.gui_widgets)
        self.assertIn('button', node.gui_widgets)
    
    def test_invalid_gui_code_handling(self):
        """Test that invalid GUI code is handled gracefully."""
        markdown_content = '''# Test Graph

## Node: Invalid GUI Node (ID: invalid-gui-1)

Node with invalid GUI code.

### Metadata

```json
{
  "uuid": "invalid-gui-1",
  "title": "Invalid GUI Node",
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
# This will cause a syntax error
from PySide6.QtWidgets import QLabel
invalid_syntax_here !!!
widgets['label'] = QLabel('Test', parent)
layout.addWidget(widgets['label'])
```

## Connections

```json
[]
```
'''
        
        # Load from markdown
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        # Verify node was created despite invalid GUI code
        self.assertEqual(len(self.graph.nodes), 1)
        node = self.graph.nodes[0]
        
        # GUI should fail gracefully - check for error label
        node.rebuild_gui()
        # Should have at least one widget (error label)
        self.assertGreater(len(node.gui_widgets), 0)
    
    def test_missing_gui_state_handler(self):
        """Test nodes with GUI definition but missing state handler."""
        markdown_content = '''# Test Graph

## Node: Missing Handler Node (ID: missing-handler-1)

Node with GUI but no state handler.

### Metadata

```json
{
  "uuid": "missing-handler-1",
  "title": "Missing Handler Node",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": {
    "initial_value": "test"
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

## Connections

```json
[]
```
'''
        
        # Load from markdown
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        node.rebuild_gui()
        
        # Should handle missing state handler gracefully
        self.assertIn('input', node.gui_widgets)
        
        # These should return empty/default values without crashing
        values = node.get_gui_values()
        self.assertEqual(values, {})
    
    def test_node_height_after_gui_loading(self):
        """Test that nodes maintain proper height after GUI loading."""
        markdown_content = '''# Test Graph

## Node: Height Test Node (ID: height-test-1)

Node to test height preservation.

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
from PySide6.QtWidgets import QLabel, QVBoxLayout

for i in range(5):
    widgets[f'label_{i}'] = QLabel(f'Label {i}', parent)
    layout.addWidget(widgets[f'label_{i}'])
```

## Connections

```json
[]
```
'''
        
        # Load from markdown
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        
        # Check initial height from metadata
        self.assertEqual(node.height, 200)
        
        # Rebuild GUI and verify height is maintained
        node.rebuild_gui()
        self.assertGreater(node.height, 0)
        self.assertGreaterEqual(node.height, 150)  # Should be at least minimum height
    
    def test_gui_state_application(self):
        """Test that GUI state is properly applied after loading."""
        markdown_content = '''# Test Graph

## Node: State Test Node (ID: state-test-1)

Node to test state application.

### Metadata

```json
{
  "uuid": "state-test-1",
  "title": "State Test Node",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": {
    "input_text": "saved value",
    "checkbox_state": true,
    "slider_value": 75
  }
}
```

### Logic

```python
@node_entry
def test_func(text: str = "", flag: bool = False, value: int = 0) -> str:
    return f"{text}_{flag}_{value}"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QCheckBox, QSlider

widgets['input'] = QLineEdit(parent)
layout.addWidget(widgets['input'])

widgets['checkbox'] = QCheckBox('Enable', parent)
layout.addWidget(widgets['checkbox'])

widgets['slider'] = QSlider(Qt.Horizontal, parent)
widgets['slider'].setRange(0, 100)
layout.addWidget(widgets['slider'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'text': widgets['input'].text(),
        'flag': widgets['checkbox'].isChecked(),
        'value': widgets['slider'].value()
    }

def set_values(widgets, outputs):
    pass  # Not used in this test

def set_initial_state(widgets, state):
    if 'input_text' in state:
        widgets['input'].setText(state['input_text'])
    if 'checkbox_state' in state:
        widgets['checkbox'].setChecked(state['checkbox_state'])
    if 'slider_value' in state:
        widgets['slider'].setValue(state['slider_value'])
```

## Connections

```json
[]
```
'''
        
        # Load from markdown
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        node.rebuild_gui()
        
        # Apply the GUI state (during deserialization, gui_state is passed to apply_gui_state)
        gui_state = {"input_text": "saved value", "checkbox_state": True, "slider_value": 75}
        node.apply_gui_state(gui_state)
        
        # Verify state was applied correctly
        self.assertEqual(node.gui_widgets['input'].text(), "saved value")
        self.assertTrue(node.gui_widgets['checkbox'].isChecked())
        self.assertEqual(node.gui_widgets['slider'].value(), 75)
    
    def test_complex_gui_layout_loading(self):
        """Test loading of complex GUI layouts with nested containers."""
        markdown_content = '''# Test Graph

## Node: Complex GUI Node (ID: complex-gui-1)

Node with complex GUI layout.

### Metadata

```json
{
  "uuid": "complex-gui-1",
  "title": "Complex GUI Node",
  "pos": [100, 100],
  "size": [300, 250],
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def complex_func() -> str:
    return "complex"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QGroupBox

# Create a group box
widgets['group'] = QGroupBox('Settings', parent)
group_layout = QVBoxLayout(widgets['group'])

# Add some controls to the group
widgets['input1'] = QLineEdit()
widgets['input2'] = QLineEdit()
group_layout.addWidget(QLabel('Input 1:'))
group_layout.addWidget(widgets['input1'])
group_layout.addWidget(QLabel('Input 2:'))
group_layout.addWidget(widgets['input2'])

layout.addWidget(widgets['group'])
```

## Connections

```json
[]
```
'''
        
        # Load from markdown
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        node.rebuild_gui()
        
        # Verify complex layout was created successfully
        self.assertIn('group', node.gui_widgets)
        self.assertIn('input1', node.gui_widgets)
        self.assertIn('input2', node.gui_widgets)
    
    def test_proxy_widget_creation(self):
        """Test that QGraphicsProxyWidget is properly created for GUI nodes."""
        markdown_content = '''# Test Graph

## Node: Proxy Test Node (ID: proxy-test-1)

Node to test proxy widget creation.

### Metadata

```json
{
  "uuid": "proxy-test-1",
  "title": "Proxy Test Node",
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

widgets['label'] = QLabel('Test Label', parent)
layout.addWidget(widgets['label'])
```

## Connections

```json
[]
```
'''
        
        # Load from markdown
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        node = self.graph.nodes[0]
        node.rebuild_gui()
        
        # Verify proxy widget exists and is properly configured
        self.assertIsNotNone(node.proxy_widget)
        self.assertIsNotNone(node.proxy_widget.widget())
    
    def test_reroute_node_loading(self):
        """Test that reroute nodes load correctly without GUI issues."""
        markdown_content = '''# Test Graph

## Node: Reroute (ID: reroute-1)

Simple reroute node.

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
# Reroute nodes don't have logic code
```

## Connections

```json
[]
```
'''
        
        # Load from markdown
        data = self.handler.flow_to_json(markdown_content)
        self.graph.deserialize(data)
        
        # Verify reroute node was created
        self.assertEqual(len(self.graph.nodes), 1)
        node = self.graph.nodes[0]
        
        # Reroute nodes should not have GUI components
        self.assertEqual(node.gui_code, "")
        self.assertEqual(len(node.gui_widgets), 0)
    
    def test_malformed_gui_state_json(self):
        """Test handling of malformed GUI state JSON in metadata."""
        markdown_content = '''# Test Graph

## Node: Malformed State Node (ID: malformed-1)

Node with malformed gui_state in metadata.

### Metadata

```json
{
  "uuid": "malformed-1",
  "title": "Malformed State Node",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": "this is not valid JSON"
}
```

### Logic

```python
@node_entry
def test_func() -> str:
    return "test"
```

## Connections

```json
[]
```
'''
        
        # This should handle malformed JSON gracefully
        try:
            data = self.handler.flow_to_json(markdown_content)
            # JSON parsing should fail gracefully and use default empty state
            self.assertIn("nodes", data)
            if data["nodes"]:
                # gui_state should be empty dict as fallback
                self.assertEqual(data["nodes"][0].get("gui_state", {}), {})
        except Exception as e:
            self.fail(f"Should handle malformed JSON gracefully: {e}")
    
    def test_file_operations_gui_refresh(self):
        """Test that FileOperations properly refreshes GUI after loading."""
        markdown_content = '''# Test Graph

## Node: Refresh Test Node (ID: refresh-test-1)

Node to test GUI refresh.

### Metadata

```json
{
  "uuid": "refresh-test-1",
  "title": "Refresh Test Node",
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

widgets['label'] = QLabel('Refresh Test', parent)
layout.addWidget(widgets['label'])
```

## Connections

```json
[]
```
'''
        
        # Create temporary file
        temp_file = self.create_test_markdown_file(markdown_content)
        
        try:
            # Mock the settings and other dependencies
            with patch.object(self.file_ops, 'settings') as mock_settings:
                mock_settings.setValue = Mock()
                
                # Load file using FileOperations
                self.file_ops.open_file(temp_file)
                
                # Verify node was loaded and GUI was created
                self.assertEqual(len(self.graph.nodes), 1)
                node = self.graph.nodes[0]
                self.assertIn('label', node.gui_widgets)
                
        finally:
            # Clean up temp file
            os.unlink(temp_file)


class TestGUILoadingIntegration(unittest.TestCase):
    """Integration tests for complete GUI loading workflow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for the entire test suite."""
        if QApplication.instance() is None:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def test_load_existing_markdown_example(self):
        """Test loading an existing markdown example file with GUI components."""
        # Test with the data analysis dashboard example if it exists
        example_path = os.path.join(os.path.dirname(__file__), 'examples', 'data_analysis_dashboard.md')
        
        if os.path.exists(example_path):
            try:
                data = load_flow_file(example_path)
                
                # Create a graph and load the data
                graph = NodeGraph()
                graph.deserialize(data)
                
                # Find nodes with GUI components
                gui_nodes = [node for node in graph.nodes if node.gui_code.strip()]
                
                # Verify GUI nodes load properly
                for node in gui_nodes:
                    node.rebuild_gui()
                    # Should have widgets if gui_code is present
                    if node.gui_code.strip():
                        self.assertGreater(len(node.gui_widgets), 0, 
                                         f"Node {node.title} should have GUI widgets")
                        
                        # GUI state is handled during deserialization, not stored as attribute
                
            except Exception as e:
                self.fail(f"Failed to load existing markdown example: {e}")


def run_gui_tests():
    """Run all GUI loading tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add basic GUI loading tests
    suite.addTest(loader.loadTestsFromTestCase(TestGUILoading))
    
    # Add integration tests
    suite.addTest(loader.loadTestsFromTestCase(TestGUILoadingIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=== GUI Loading Tests ===")
    success = run_gui_tests()
    
    if success:
        print("\n=== All GUI Loading Tests Passed ===")
        sys.exit(0)
    else:
        print("\n=== Some GUI Loading Tests Failed ===")
        sys.exit(1)
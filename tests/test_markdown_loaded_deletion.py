#!/usr/bin/env python3
"""
Test for node deletion issues specifically with markdown-loaded nodes.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent

from ui.editor.node_editor_window import NodeEditorWindow
from core.node import Node
from core.reroute_node import RerouteNode
from data.flow_format import FlowFormatHandler

def test_markdown_loaded_node_deletion():
    """Test deletion of nodes loaded from markdown."""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = NodeEditorWindow()
    graph = window.graph
    
    # Clear any existing content
    graph.clear_graph()
    
    # Create a simple markdown content with nodes
    markdown_content = '''# Test Graph

A simple test graph for testing node deletion.

## Node: Test Node A (ID: node-a)

Simple test node A.

### Metadata

```json
{
  "uuid": "node-a",
  "title": "Test Node A",
  "pos": [100, 100],
  "size": [200, 150],
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def test_function_a() -> str:
    return "test_a"
```

## Node: Test Node B (ID: node-b)

Simple test node B.

### Metadata

```json
{
  "uuid": "node-b",
  "title": "Test Node B",
  "pos": [400, 100],
  "size": [200, 150],
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def test_function_b(input_val: str):
    print(input_val)
```

## Connections

```json
[
  {
    "start_node_uuid": "node-a",
    "start_pin_name": "output_1",
    "end_node_uuid": "node-b",
    "end_pin_name": "input_val"
  }
]
```
'''
    
    # Load the markdown content
    handler = FlowFormatHandler()
    data = handler.markdown_to_data(markdown_content)
    
    print("Loading markdown data...")
    graph.deserialize(data)
    
    print(f"Loaded nodes: {len(graph.nodes)}")
    print(f"Loaded connections: {len(graph.connections)}")
    
    for i, node in enumerate(graph.nodes):
        print(f"  Node {i}: {node.title} (ID: {id(node)}) - Scene: {node.scene() is not None}")
    
    # Now try to delete the first node
    if len(graph.nodes) > 0:
        node_to_delete = graph.nodes[0]
        print(f"\nAttempting to delete loaded node: {node_to_delete.title}")
        
        # Select and delete the node
        node_to_delete.setSelected(True)
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        graph.keyPressEvent(delete_event)
        
        # Process events
        app.processEvents()
        
        print(f"After deletion attempt:")
        print(f"  Nodes count: {len(graph.nodes)}")
        print(f"  Scene items count: {len(graph.items())}")
        
        for i, node in enumerate(graph.nodes):
            print(f"  Remaining node {i}: {node.title} (ID: {id(node)})")
        
        # Check if the node we tried to delete is still there
        node_still_exists = node_to_delete in graph.nodes
        print(f"  Node we tried to delete still in nodes list: {node_still_exists}")
        print(f"  Node we tried to delete still in scene: {node_to_delete.scene() is not None}")
        
        # Check if node is still in scene
        orphaned_nodes = [item for item in graph.items() 
                         if isinstance(item, (Node, RerouteNode)) and item not in graph.nodes]
        
        if orphaned_nodes or node_still_exists:
            if orphaned_nodes:
                print(f"Found {len(orphaned_nodes)} orphaned nodes!")
                for node in orphaned_nodes:
                    print(f"  Orphaned: {getattr(node, 'title', 'Unknown')} (ID: {id(node)})")
            if node_still_exists:
                print(f"Node deletion failed - node still exists!")
            assert False, "Node deletion issues found"
        else:
            print("No orphaned nodes found - deletion successful")
            # Test passed - no return needed
    else:
        assert False, "No nodes to test deletion"

if __name__ == "__main__":
    try:
        test_markdown_loaded_node_deletion()
        print("\nTest passed - Markdown-loaded node deletion works correctly")
        sys.exit(0)
    except AssertionError:
        print("\nTest failed - Markdown-loaded nodes have deletion issues")
        sys.exit(1)
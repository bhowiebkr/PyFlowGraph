#!/usr/bin/env python3
"""
Test for RerouteNode deletion and undo/redo.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent

from node_editor_window import NodeEditorWindow
from node import Node
from reroute_node import RerouteNode

def test_reroute_undo_redo():
    """Test deletion and undo/redo of RerouteNode objects."""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = NodeEditorWindow()
    graph = window.graph
    view = window.view
    
    # Clear any existing content
    graph.clear_graph()
    
    print("Creating test setup with RerouteNode...")
    
    # Create a regular node
    node1 = graph.create_node("Test Node", pos=(100, 100))
    node1.set_code('''
@node_entry
def test_function() -> str:
    return "test_output"
''')
    
    # Create a RerouteNode manually
    reroute = RerouteNode()
    reroute.setPos(300, 100)
    graph.addItem(reroute)
    graph.nodes.append(reroute)
    
    # Create another regular node
    node2 = graph.create_node("Test Node 2", pos=(500, 100))
    node2.set_code('''
@node_entry
def test_function_2(input_val: str):
    print(input_val)
''')
    
    print(f"Initial state:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Scene items: {len(graph.items())}")
    
    # Verify we have the right node types
    print(f"\nNode types:")
    for i, node in enumerate(graph.nodes):
        node_type = "RerouteNode" if isinstance(node, RerouteNode) else "Node"
        print(f"  Node {i}: {node.title} - {node_type}")
    
    # Select and delete the RerouteNode
    print(f"\nStep 1: Deleting RerouteNode...")
    reroute.setSelected(True)
    delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
    graph.keyPressEvent(delete_event)
    app.processEvents()
    
    print(f"After deletion:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Scene items: {len(graph.items())}")
    
    # Check if RerouteNode is gone
    reroute_still_exists = reroute in graph.nodes
    reroute_still_in_scene = reroute in graph.items()
    print(f"  RerouteNode still in nodes list: {reroute_still_exists}")
    print(f"  RerouteNode still in scene: {reroute_still_in_scene}")
    
    if reroute_still_exists or reroute_still_in_scene:
        print("FAIL: RerouteNode deletion failed!")
        return False
    
    # Step 2: Undo the deletion
    print(f"\nStep 2: Undoing deletion (Ctrl+Z)...")
    undo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
    view.keyPressEvent(undo_event)
    app.processEvents()
    
    print(f"After undo:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Scene items: {len(graph.items())}")
    
    # Check node types after undo
    print(f"\nNode types after undo:")
    reroute_restored = False
    for i, node in enumerate(graph.nodes):
        node_type = "RerouteNode" if isinstance(node, RerouteNode) else "Node"
        print(f"  Node {i}: {node.title} - {node_type}")
        if isinstance(node, RerouteNode) and node.title == "Reroute":
            reroute_restored = True
            restored_reroute = node
    
    if not reroute_restored:
        print("FAIL: RerouteNode was not restored as RerouteNode!")
        return False
    
    # Step 3: Redo the deletion
    print(f"\nStep 3: Redoing deletion (Ctrl+Y)...")
    redo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Y, Qt.ControlModifier)
    view.keyPressEvent(redo_event)
    app.processEvents()
    
    print(f"After redo:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Scene items: {len(graph.items())}")
    
    # Check if RerouteNode is gone again
    reroute_still_exists = restored_reroute in graph.nodes
    reroute_still_in_scene = restored_reroute in graph.items()
    print(f"  RerouteNode still in nodes list: {reroute_still_exists}")
    print(f"  RerouteNode still in scene: {reroute_still_in_scene}")
    
    if reroute_still_exists or reroute_still_in_scene:
        print("FAIL: RerouteNode redo deletion failed!")
        return False
    
    # Step 4: Undo again to test multiple cycles
    print(f"\nStep 4: Undoing again...")
    undo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
    view.keyPressEvent(undo_event)
    app.processEvents()
    
    print(f"After second undo:")
    print(f"  Nodes: {len(graph.nodes)}")
    
    # Final verification
    reroute_restored_again = False
    for node in graph.nodes:
        if isinstance(node, RerouteNode) and node.title == "Reroute":
            reroute_restored_again = True
            break
    
    if not reroute_restored_again:
        print("FAIL: RerouteNode was not restored correctly on second undo!")
        return False
    
    print("SUCCESS: RerouteNode deletion and undo/redo works correctly!")
    return True

if __name__ == "__main__":
    success = test_reroute_undo_redo()
    if success:
        print("\nTest passed - RerouteNode undo/redo works correctly")
    else:
        print("\nTest failed - RerouteNode undo/redo has issues")
    
    sys.exit(0 if success else 1)
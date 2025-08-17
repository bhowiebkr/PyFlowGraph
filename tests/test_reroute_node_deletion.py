#!/usr/bin/env python3
"""
Test for RerouteNode deletion specifically.
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

def test_reroute_node_deletion():
    """Test deletion of RerouteNode objects."""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = NodeEditorWindow()
    graph = window.graph
    
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
    
    # Create a RerouteNode
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
    
    # Create connections: node1 -> reroute -> node2
    print("Creating connections...")
    if node1.output_pins and node2.input_pins:
        # Connect node1 to reroute
        conn1 = graph.create_connection(node1.output_pins[0], reroute.input_pin)
        print(f"Created connection: node1 -> reroute")
        
        # Connect reroute to node2
        conn2 = graph.create_connection(reroute.output_pin, node2.input_pins[0])
        print(f"Created connection: reroute -> node2")
    
    print(f"After connections:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Connections: {len(graph.connections)}")
    print(f"  Scene items: {len(graph.items())}")
    
    # Verify RerouteNode structure
    print(f"\nRerouteNode details:")
    print(f"  Title: {reroute.title}")
    print(f"  UUID: {reroute.uuid}")
    print(f"  is_reroute: {getattr(reroute, 'is_reroute', 'MISSING')}")
    print(f"  Has input_pin: {hasattr(reroute, 'input_pin')}")
    print(f"  Has output_pin: {hasattr(reroute, 'output_pin')}")
    print(f"  Has input_pins: {hasattr(reroute, 'input_pins')}")
    print(f"  Has output_pins: {hasattr(reroute, 'output_pins')}")
    
    # Now try to delete the RerouteNode
    print(f"\nAttempting to delete RerouteNode...")
    reroute.setSelected(True)
    delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
    graph.keyPressEvent(delete_event)
    
    # Process events
    app.processEvents()
    
    print(f"After deletion attempt:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Connections: {len(graph.connections)}")
    print(f"  Scene items: {len(graph.items())}")
    
    # Check if RerouteNode is still there
    reroute_still_exists = reroute in graph.nodes
    reroute_still_in_scene = reroute in graph.items()
    
    print(f"  RerouteNode still in nodes list: {reroute_still_exists}")
    print(f"  RerouteNode still in scene: {reroute_still_in_scene}")
    
    # Check for orphaned items
    orphaned_items = [item for item in graph.items() 
                     if isinstance(item, (Node, RerouteNode)) and item not in graph.nodes]
    
    if orphaned_items:
        print(f"Found {len(orphaned_items)} orphaned items!")
        for item in orphaned_items:
            print(f"  Orphaned: {getattr(item, 'title', 'Unknown')} - {type(item).__name__}")
        return False
    
    if reroute_still_exists or reroute_still_in_scene:
        print("RerouteNode deletion failed!")
        return False
    
    print("RerouteNode deletion successful!")
    return True

if __name__ == "__main__":
    success = test_reroute_node_deletion()
    if success:
        print("\nTest passed - RerouteNode deletion works correctly")
    else:
        print("\nTest failed - RerouteNode deletion has issues")
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test for RerouteNode creation, deletion, and undo sequence.
This reproduces the user's reported issue with undo/redo of RerouteNode operations.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QKeyEvent

from src.ui.editor.node_editor_window import NodeEditorWindow
from src.core.node import Node
from src.core.reroute_node import RerouteNode

def test_reroute_creation_undo_sequence():
    """Test the user's reported issue: create reroute -> delete -> undo delete -> undo create."""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = NodeEditorWindow()
    graph = window.graph
    view = window.view
    
    # Clear any existing content
    graph.clear_graph()
    
    print("=== Testing RerouteNode Creation/Deletion/Undo Sequence ===")
    print("This reproduces the user's reported issue\n")
    
    # Step 1: Create two nodes and connect them
    print("Step 1: Creating two connected nodes...")
    node1 = graph.create_node("Source", pos=(100, 100))
    node1.set_code('''
@node_entry
def source() -> str:
    return "data"
''')
    
    node2 = graph.create_node("Target", pos=(400, 100))
    node2.set_code('''
@node_entry
def target(input_val: str):
    print(input_val)
''')
    
    # Create connection between them
    if node1.output_pins and node2.input_pins:
        connection = graph.create_connection(node1.output_pins[0], node2.input_pins[0])
        print(f"  Created connection between {node1.title} and {node2.title}")
    
    print(f"  Initial state: {len(graph.nodes)} nodes, {len(graph.connections)} connections")
    print(f"  Command history size: {len(graph.command_history.commands)}")
    
    # Step 2: Create a RerouteNode on the connection (using proper method)
    print("\nStep 2: Creating RerouteNode on connection...")
    if graph.connections:
        connection = graph.connections[0]
        middle_point = QPointF(250, 100)  # Middle point of the connection
        
        # Use the proper creation method that should use commands
        reroute = graph.create_reroute_node_on_connection(connection, middle_point, use_command=True)
        app.processEvents()
        
        print(f"  Created RerouteNode using command system")
        print(f"  State: {len(graph.nodes)} nodes, {len(graph.connections)} connections")
        print(f"  Command history size: {len(graph.command_history.commands)}")
        
        # List the types of nodes
        for i, node in enumerate(graph.nodes):
            node_type = "RerouteNode" if isinstance(node, RerouteNode) else "Node"
            print(f"    Node {i}: {node.title} ({node_type})")
    
    # Step 3: Delete the RerouteNode
    print("\nStep 3: Deleting RerouteNode...")
    reroute_nodes = [node for node in graph.nodes if isinstance(node, RerouteNode)]
    if reroute_nodes:
        reroute = reroute_nodes[0]
        reroute.setSelected(True)
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        graph.keyPressEvent(delete_event)
        app.processEvents()
        
        print(f"  Deleted RerouteNode")
        print(f"  State: {len(graph.nodes)} nodes, {len(graph.connections)} connections")
        print(f"  Command history size: {len(graph.command_history.commands)}")
    
    # Step 4: Undo the deletion (should restore RerouteNode)
    print("\nStep 4: Undoing RerouteNode deletion...")
    undo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
    view.keyPressEvent(undo_event)
    app.processEvents()
    
    print(f"  Undone deletion")
    print(f"  State: {len(graph.nodes)} nodes, {len(graph.connections)} connections")
    print(f"  Command history size: {len(graph.command_history.commands)}")
    
    # Check if RerouteNode was restored properly
    reroute_nodes_after_undo = [node for node in graph.nodes if isinstance(node, RerouteNode)]
    if reroute_nodes_after_undo:
        restored_reroute = reroute_nodes_after_undo[0]
        print(f"  SUCCESS: RerouteNode restored as: {type(restored_reroute).__name__}")
    else:
        print(f"  FAIL: RerouteNode not restored!")
        return False
    
    # Step 5: Undo the creation (this is where the user reports issues)
    print("\nStep 5: Undoing RerouteNode creation (user reported issue here)...")
    undo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
    view.keyPressEvent(undo_event)
    app.processEvents()
    
    print(f"  Attempted to undo creation")
    print(f"  State: {len(graph.nodes)} nodes, {len(graph.connections)} connections")
    print(f"  Command history size: {len(graph.command_history.commands)}")
    
    # Check final state
    reroute_nodes_final = [node for node in graph.nodes if isinstance(node, RerouteNode)]
    direct_connection_exists = False
    
    # Check if we have a direct connection between the original nodes
    for conn in graph.connections:
        if ((conn.start_pin.node == node1 and conn.end_pin.node == node2) or
            (conn.start_pin.node == node2 and conn.end_pin.node == node1)):
            direct_connection_exists = True
            break
    
    print(f"\nFinal Analysis:")
    print(f"  RerouteNodes still exist: {len(reroute_nodes_final)}")
    print(f"  Direct connection exists: {direct_connection_exists}")
    
    if len(reroute_nodes_final) == 0 and direct_connection_exists:
        print(f"  COMPLETE SUCCESS: RerouteNode creation was properly undone!")
        return True
    elif len(reroute_nodes_final) > 0 and direct_connection_exists:
        print(f"  PARTIAL: RerouteNode still exists but connection was restored (user's reported issue)")
        return False
    else:
        print(f"  FAIL: Unexpected state")
        return False

def test_reroute_redo():
    """Test redo operations with RerouteNodes."""
    print("\n=== Testing RerouteNode Redo Operations ===")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = NodeEditorWindow()
    graph = window.graph
    view = window.view
    
    # Clear any existing content
    graph.clear_graph()
    
    # Setup: Create connected nodes and a RerouteNode
    node1 = graph.create_node("Source", pos=(100, 100))
    node1.set_code('@node_entry\ndef source() -> str:\n    return "data"')
    
    node2 = graph.create_node("Target", pos=(400, 100))
    node2.set_code('@node_entry\ndef target(input_val: str):\n    print(input_val)')
    
    connection = graph.create_connection(node1.output_pins[0], node2.input_pins[0])
    reroute = graph.create_reroute_node_on_connection(connection, QPointF(250, 100), use_command=True)
    
    print("Setup complete: 2 nodes + 1 RerouteNode + 2 connections")
    
    # Delete RerouteNode, then undo, then redo
    reroute_nodes = [node for node in graph.nodes if isinstance(node, RerouteNode)]
    if reroute_nodes:
        reroute = reroute_nodes[0]
        reroute.setSelected(True)
        
        # Delete
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        graph.keyPressEvent(delete_event)
        app.processEvents()
        print(f"After delete: {len(graph.nodes)} nodes, {len(graph.connections)} connections")
        
        # Undo
        undo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
        view.keyPressEvent(undo_event)
        app.processEvents()
        print(f"After undo: {len(graph.nodes)} nodes, {len(graph.connections)} connections")
        
        # Redo
        redo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Y, Qt.ControlModifier)
        view.keyPressEvent(redo_event)
        app.processEvents()
        print(f"After redo: {len(graph.nodes)} nodes, {len(graph.connections)} connections")
        
        # Check final state
        final_reroute_nodes = [node for node in graph.nodes if isinstance(node, RerouteNode)]
        if len(final_reroute_nodes) == 0:
            print("SUCCESS: Redo worked correctly - RerouteNode is deleted")
            return True
        else:
            print("FAIL: Redo failed - RerouteNode still exists")
            return False
    
    return False

if __name__ == "__main__":
    print("Testing RerouteNode creation/deletion/undo sequence...\n")
    
    success1 = test_reroute_creation_undo_sequence()
    success2 = test_reroute_redo()
    
    if success1 and success2:
        print("\nSUCCESS: All tests passed")
    else:
        print(f"\nFAIL: Tests failed - creation/undo: {success1}, redo: {success2}")
    
    sys.exit(0 if (success1 and success2) else 1)
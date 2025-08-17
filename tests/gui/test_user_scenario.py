#!/usr/bin/env python3
"""
Test for the specific user scenario: RerouteNode deletion and undo.
"""

import sys
import os

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent

from ui.editor.node_editor_window import NodeEditorWindow
from core.node import Node
from core.reroute_node import RerouteNode

def test_user_scenario():
    """Test the exact user scenario: delete reroute, undo it."""
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = NodeEditorWindow()
    graph = window.graph
    view = window.view
    
    # Clear any existing content
    graph.clear_graph()
    
    print("Creating RerouteNode...")
    
    # Create a RerouteNode manually (like user would do)
    reroute = RerouteNode()
    reroute.setPos(300, 100)
    graph.addItem(reroute)
    graph.nodes.append(reroute)
    
    print(f"Initial state:")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  RerouteNode type: {type(reroute).__name__}")
    print(f"  RerouteNode title: {reroute.title}")
    print(f"  RerouteNode has input_pin: {hasattr(reroute, 'input_pin')}")
    print(f"  RerouteNode has output_pin: {hasattr(reroute, 'output_pin')}")
    
    # Step 1: Delete the RerouteNode
    print(f"\nStep 1: Deleting RerouteNode...")
    reroute.setSelected(True)
    delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
    graph.keyPressEvent(delete_event)
    app.processEvents()
    
    print(f"After deletion:")
    print(f"  Nodes: {len(graph.nodes)}")
    
    # Step 2: Undo the deletion (this is where the user saw the issue)
    print(f"\nStep 2: Undoing deletion (this is where the user reported the issue)...")
    undo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
    view.keyPressEvent(undo_event)
    app.processEvents()
    
    print(f"After undo:")
    print(f"  Nodes: {len(graph.nodes)}")
    
    # Check what type of node was restored
    if len(graph.nodes) > 0:
        restored_node = None
        for node in graph.nodes:
            if hasattr(node, 'title') and node.title == "Reroute":
                restored_node = node
                break
        
        if restored_node:
            print(f"\nRestored node details:")
            print(f"  Type: {type(restored_node).__name__}")
            print(f"  Title: {restored_node.title}")
            print(f"  Is RerouteNode: {isinstance(restored_node, RerouteNode)}")
            print(f"  Has input_pin: {hasattr(restored_node, 'input_pin')}")
            print(f"  Has output_pin: {hasattr(restored_node, 'output_pin')}")
            print(f"  Has input_pins: {hasattr(restored_node, 'input_pins')}")
            print(f"  Has output_pins: {hasattr(restored_node, 'output_pins')}")
            
            if isinstance(restored_node, RerouteNode):
                print(f"  [PASS] SUCCESS: RerouteNode correctly restored as RerouteNode!")
                return True
            else:
                print(f"  [FAIL] FAIL: RerouteNode was restored as regular Node!")
                return False
        else:
            print(f"  [FAIL] FAIL: No node with title 'Reroute' found!")
            return False
    else:
        print(f"  [FAIL] FAIL: No nodes restored!")
        return False

if __name__ == "__main__":
    success = test_user_scenario()
    if success:
        print("\n[PASS] Test passed - User issue has been FIXED!")
        print("RerouteNodes now correctly restore as RerouteNodes, not regular Nodes")
    else:
        print("\n[FAIL] Test failed - User issue still exists")
    
    sys.exit(0 if success else 1)
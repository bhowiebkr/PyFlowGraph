#!/usr/bin/env python3
"""
GUI-based test for node deletion issues.
This test runs with actual Qt widgets and scene interactions.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent

from src.ui.editor.node_editor_window import NodeEditorWindow
from src.core.node import Node
from src.core.reroute_node import RerouteNode
from src.core.connection import Connection

class TestGUINodeDeletion:
    """Test node deletion with actual GUI interactions."""
    
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.window = NodeEditorWindow()
        self.graph = self.window.graph
        self.view = self.window.view
        
        # Load the problematic file to reproduce the issue
        try:
            from data.file_operations import load_file
            load_file(self.window, "examples/file_organizer_automation.md")
            print("Loaded file_organizer_automation.md for testing")
        except Exception as e:
            print(f"Could not load file: {e}")
            # Clear any existing content
            self.graph.clear_graph()
        
        # Show window for visual debugging
        self.window.show()
        self.window.resize(1200, 800)
        
    def create_test_graph(self):
        """Create a test graph with connected nodes."""
        print("Creating test graph with connected nodes...")
        
        # Create nodes
        node1 = self.graph.create_node("Test Node 1", pos=(100, 100))
        node2 = self.graph.create_node("Test Node 2", pos=(400, 100))
        node3 = self.graph.create_node("Test Node 3", pos=(700, 100))
        
        # Add code to generate pins
        node1.set_code('''
@node_entry
def produce_data() -> str:
    return "test_data"
''')
        
        node2.set_code('''
@node_entry
def process_data(input_text: str) -> str:
    return f"processed_{input_text}"
''')
        
        node3.set_code('''
@node_entry
def consume_data(final_text: str):
    print(final_text)
''')
        
        # Create connections
        # Node1 -> Node2
        output_pin1 = None
        input_pin2 = None
        
        for pin in node1.output_pins:
            if pin.pin_category == "data":
                output_pin1 = pin
                break
        
        for pin in node2.input_pins:
            if pin.pin_category == "data":
                input_pin2 = pin
                break
        
        if output_pin1 and input_pin2:
            conn1 = self.graph.create_connection(output_pin1, input_pin2)
            print(f"Created connection 1: {node1.title} -> {node2.title}")
        
        # Node2 -> Node3
        output_pin2 = None
        input_pin3 = None
        
        for pin in node2.output_pins:
            if pin.pin_category == "data":
                output_pin2 = pin
                break
        
        for pin in node3.input_pins:
            if pin.pin_category == "data":
                input_pin3 = pin
                break
        
        if output_pin2 and input_pin3:
            conn2 = self.graph.create_connection(output_pin2, input_pin3)
            print(f"Created connection 2: {node2.title} -> {node3.title}")
        
        print(f"Graph state:")
        print(f"  Nodes: {len(self.graph.nodes)}")
        print(f"  Connections: {len(self.graph.connections)}")
        print(f"  Scene items: {len(self.graph.items())}")
        
        return node1, node2, node3
    
    def analyze_graph_state(self, description=""):
        """Analyze and report current graph state."""
        print(f"\n=== Graph Analysis: {description} ===")
        print(f"Nodes in graph.nodes: {len(self.graph.nodes)}")
        print(f"Connections in graph.connections: {len(self.graph.connections)}")
        print(f"Total scene items: {len(self.graph.items())}")
        
        # Count different types of items in scene
        node_items = 0
        connection_items = 0
        pin_items = 0
        other_items = 0
        
        for item in self.graph.items():
            if isinstance(item, (Node, RerouteNode)):
                node_items += 1
                print(f"  Node: {getattr(item, 'title', 'Unknown')} - Scene: {item.scene() is not None}")
            elif isinstance(item, Connection):
                connection_items += 1
                print(f"  Connection: {item} - Scene: {item.scene() is not None}")
            elif hasattr(item, 'pin_type'):  # Likely a pin
                pin_items += 1
            else:
                other_items += 1
        
        print(f"Scene item breakdown:")
        print(f"  Node items: {node_items}")
        print(f"  Connection items: {connection_items}")
        print(f"  Pin items: {pin_items}")
        print(f"  Other items: {other_items}")
        
        # Check for orphaned items
        orphaned_nodes = [item for item in self.graph.items() 
                         if isinstance(item, (Node, RerouteNode)) and item not in self.graph.nodes]
        if orphaned_nodes:
            print(f"WARNING: Found {len(orphaned_nodes)} orphaned nodes in scene!")
            for node in orphaned_nodes:
                print(f"  Orphaned: {getattr(node, 'title', 'Unknown')} - {type(node).__name__}")
        
        return orphaned_nodes
    
    def test_node_deletion_sequence(self):
        """Test deleting nodes in sequence and check for issues."""
        print("\n" + "="*60)
        print("STARTING NODE DELETION TEST")
        print("="*60)
        
        # Test deleting nodes from the loaded file
        if len(self.graph.nodes) > 0:
            print("Testing deletion of nodes from loaded file...")
            
            # Initial state
            self.analyze_graph_state("Initial state")
            
            # Wait for GUI to update
            self.app.processEvents()
            
            # Test deleting the first few nodes
            for i in range(min(3, len(self.graph.nodes))):
                node_to_delete = self.graph.nodes[0]  # Always delete the first node
                print(f"\n--- TEST {i+1}: Deleting node ({node_to_delete.title}) ---")
                node_to_delete.setSelected(True)
                delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
                self.graph.keyPressEvent(delete_event)
                
                self.app.processEvents()
                
                orphaned = self.analyze_graph_state(f"After deleting node {i+1}")
                
                if orphaned:
                    print("ISSUE FOUND: Orphaned nodes detected!")
                    return False
        
        # Also create test graph
        node1, node2, node3 = self.create_test_graph()
        
        # Test 1: Delete middle node (most complex case)
        print(f"\n--- TEST: Deleting middle node ({node2.title}) ---")
        node2.setSelected(True)
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        self.graph.keyPressEvent(delete_event)
        
        self.app.processEvents()
        
        # Force a scene update
        self.app.processEvents()
        
        orphaned = self.analyze_graph_state("After deleting middle node")
        
        if orphaned:
            print("ISSUE FOUND: Orphaned nodes detected!")
            return False
        
        # Test 2: Delete another node
        print(f"\n--- TEST 2: Deleting node ({node1.title}) ---")
        node1.setSelected(True)
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        self.graph.keyPressEvent(delete_event)
        
        self.app.processEvents()
        
        orphaned = self.analyze_graph_state("After deleting first node")
        
        if orphaned:
            print("ISSUE FOUND: Orphaned nodes detected!")
            return False
        
        # Test 3: Delete final node
        print(f"\n--- TEST 3: Deleting final node ({node3.title}) ---")
        node3.setSelected(True)
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        self.graph.keyPressEvent(delete_event)
        
        self.app.processEvents()
        
        orphaned = self.analyze_graph_state("After deleting final node")
        
        if orphaned:
            print("ISSUE FOUND: Orphaned nodes detected!")
            return False
        
        print("\n--- TEST COMPLETED SUCCESSFULLY ---")
        return True
    
    def run_tests(self):
        """Run all GUI deletion tests."""
        try:
            success = self.test_node_deletion_sequence()
            
            if success:
                print("\nALL TESTS PASSED - No orphaned nodes detected")
            else:
                print("\nTESTS FAILED - Orphaned nodes found (this is the 'black node' bug)")
            
            return success
            
        except Exception as e:
            print(f"\nTEST CRASHED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Keep window open for manual inspection
            print("\nWindow will stay open for 5 seconds for visual inspection...")
            QTimer.singleShot(5000, self.app.quit)
            self.app.exec()

def main():
    """Run the GUI-based node deletion test."""
    print("Starting GUI Node Deletion Test...")
    print("This test will open a PyFlowGraph window and test node deletion.")
    
    tester = TestGUINodeDeletion()
    success = tester.run_tests()
    
    if success:
        print("Test completed successfully!")
        sys.exit(0)
    else:
        print("Test failed - node deletion issues detected!")
        sys.exit(1)

if __name__ == "__main__":
    main()
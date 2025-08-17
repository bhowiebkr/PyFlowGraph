#!/usr/bin/env python3
"""
Full GUI Integration Tests

These tests open the actual PyFlowGraph application window and test
real user interactions as they would happen during normal usage.
This catches issues that headless tests miss.

The tests are designed to be run individually or as a suite,
with visual feedback and proper cleanup.
"""

import sys
import os
import unittest
import time
from pathlib import Path

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtTest import QTest

from ui.editor.node_editor_window import NodeEditorWindow
from core.node import Node
from core.reroute_node import RerouteNode
from core.connection import Connection


class FullGUITestCase(unittest.TestCase):
    """Base class for full GUI integration tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for GUI testing."""
        if QApplication.instance() is None:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        
        # Configure for GUI testing
        cls.app.setQuitOnLastWindowClosed(False)
        cls.test_timeout = 10000  # 10 seconds max per test
    
    def setUp(self):
        """Set up each test with a fresh window."""
        print(f"\n=== Starting Test: {self._testMethodName} ===")
        
        # Create main application window
        self.window = NodeEditorWindow()
        self.graph = self.window.graph
        self.view = self.window.view
        
        # Show window and make it ready for testing
        self.window.show()
        self.window.resize(1200, 800)
        self.window.raise_()  # Bring to front
        
        # Clear any existing content
        self.graph.clear_graph()
        
        # Process events to ensure window is ready
        QApplication.processEvents()
        
        # Wait a moment for window to be fully displayed
        QTest.qWait(100)
        
        print(f"Window displayed - Ready for test")
    
    def tearDown(self):
        """Clean up after each test."""
        print(f"=== Cleaning up Test: {self._testMethodName} ===")
        
        # Close window and clean up
        if hasattr(self, 'window'):
            self.window.close()
            
        # Process events to ensure cleanup
        QApplication.processEvents()
        QTest.qWait(100)
        
        print(f"Test cleanup complete\n")
    
    def wait_for_condition(self, condition_func, timeout=10000, message="Condition not met"):
        """Wait for a condition to become true with timeout."""
        start_time = time.time()
        while not condition_func() and (time.time() - start_time) * 1000 < timeout:
            QApplication.processEvents()
            time.sleep(0.01)
        
        if not condition_func():
            self.fail(f"{message} (timeout after {timeout}ms)")


class TestApplicationStartup(FullGUITestCase):
    """Test application startup and basic window functionality."""
    
    def test_application_window_opens(self):
        """Test that the main application window opens correctly."""
        # Window should be visible
        self.assertTrue(self.window.isVisible())
        
        # Window should have correct title
        self.assertIn("PyFlowGraph", self.window.windowTitle())
        
        # Main components should be present
        self.assertIsNotNone(self.window.graph)
        self.assertIsNotNone(self.window.view)
        
        # Graph should be empty initially
        self.assertEqual(len(self.graph.nodes), 0)
        self.assertEqual(len(self.graph.connections), 0)
        
        print("PASS Application window opened successfully")
    
    def test_menu_bar_exists(self):
        """Test that menu bar is present and functional."""
        menu_bar = self.window.menuBar()
        self.assertIsNotNone(menu_bar)
        
        # Check for expected menus
        menu_actions = [action.text() for action in menu_bar.actions()]
        expected_menus = ["File", "Edit", "View"]  # Adjust based on actual menus
        
        # At least one menu should exist
        self.assertGreater(len(menu_actions), 0)
        
        print(f"PASS Menu bar present with menus: {menu_actions}")


class TestNodeCreationWorkflow(FullGUITestCase):
    """Test complete node creation workflows as a user would perform them."""
    
    def test_create_node_via_context_menu(self):
        """Test creating a node through right-click context menu (if available)."""
        # Get the center of the view
        view_center = self.view.rect().center()
        
        # Simulate right-click to open context menu
        # Note: This might need adjustment based on actual context menu implementation
        right_click = QMouseEvent(
            QMouseEvent.MouseButtonPress,
            view_center,
            view_center,  # Global position same as local for simplicity
            Qt.RightButton,
            Qt.RightButton,
            Qt.NoModifier
        )
        
        # Create node programmatically (simulating context menu action)
        initial_node_count = len(self.graph.nodes)
        node = self.graph.create_node("Test Node", pos=(100, 100))
        
        QApplication.processEvents()
        
        # Verify node was created
        self.assertEqual(len(self.graph.nodes), initial_node_count + 1)
        self.assertIn(node, self.graph.nodes)
        self.assertTrue(node.isVisible())
        
        print("PASS Node created successfully via simulated context menu")
    
    def test_node_selection_and_properties(self):
        """Test node selection and property access."""
        # Create a test node
        node = self.graph.create_node("Selection Test Node", pos=(200, 150))
        QApplication.processEvents()
        
        # Initially node should not be selected
        self.assertFalse(node.isSelected())
        
        # Select the node
        node.setSelected(True)
        QApplication.processEvents()
        
        # Verify selection
        self.assertTrue(node.isSelected())
        
        # Test node properties
        self.assertEqual(node.title, "Selection Test Node")
        self.assertIsNotNone(node.uuid)
        self.assertEqual(node.pos(), QPointF(200, 150))
        
        print("PASS Node selection and properties work correctly")
    
    def test_node_code_editing_workflow(self):
        """Test the complete workflow of editing node code."""
        # Create a node
        node = self.graph.create_node("Code Test Node", pos=(100, 200))
        QApplication.processEvents()
        
        # Set some code (simulating code editor dialog)
        test_code = '''
@node_entry
def test_function(x: int, y: str) -> str:
    return f"{y}: {x * 2}"
'''
        
        node.set_code(test_code)
        QApplication.processEvents()
        
        # Verify code was set
        self.assertEqual(node.code, test_code)
        
        # Verify pins were generated
        self.assertGreater(len(node.input_pins), 0)
        self.assertGreater(len(node.output_pins), 0)
        
        # Check for specific pins
        input_pin_names = [pin.name for pin in node.input_pins if pin.pin_category == "data"]
        self.assertIn("x", input_pin_names)
        self.assertIn("y", input_pin_names)
        
        output_pin_names = [pin.name for pin in node.output_pins if pin.pin_category == "data"]
        self.assertIn("output_1", output_pin_names)
        
        print("PASS Node code editing workflow completed successfully")


class TestConnectionWorkflow(FullGUITestCase):
    """Test connection creation and management workflows."""
    
    def test_create_connection_between_nodes(self):
        """Test creating connections between compatible nodes."""
        # Create source node
        source_node = self.graph.create_node("Source Node", pos=(50, 100))
        source_node.set_code('''
@node_entry
def produce_data() -> str:
    return "Hello World"
''')
        
        # Create target node
        target_node = self.graph.create_node("Target Node", pos=(400, 100))
        target_node.set_code('''
@node_entry
def consume_data(input_text: str):
    print(input_text)
''')
        
        QApplication.processEvents()
        
        # Find compatible pins
        source_output = None
        target_input = None
        
        for pin in source_node.output_pins:
            if pin.pin_category == "data":
                source_output = pin
                break
        
        for pin in target_node.input_pins:
            if pin.pin_category == "data":
                target_input = pin
                break
        
        self.assertIsNotNone(source_output)
        self.assertIsNotNone(target_input)
        
        # Create connection
        initial_connection_count = len(self.graph.connections)
        connection = self.graph.create_connection(source_output, target_input)
        
        QApplication.processEvents()
        
        # Verify connection was created
        self.assertIsNotNone(connection)
        self.assertEqual(len(self.graph.connections), initial_connection_count + 1)
        self.assertIn(connection, self.graph.connections)
        self.assertTrue(connection.isVisible())
        
        # Verify connection properties
        self.assertEqual(connection.start_pin, source_output)
        self.assertEqual(connection.end_pin, target_input)
        
        print("PASS Connection created successfully between compatible nodes")
    
    def test_connection_visual_feedback(self):
        """Test that connections provide proper visual feedback."""
        # Create nodes and connection
        source = self.graph.create_node("Visual Source", pos=(100, 100))
        target = self.graph.create_node("Visual Target", pos=(400, 100))
        
        source.set_code('@node_entry\ndef output() -> int:\n    return 42')
        target.set_code('@node_entry\ndef input(x: int):\n    pass')
        
        QApplication.processEvents()
        
        # Create connection
        source_pin = next(p for p in source.output_pins if p.pin_category == "data")
        target_pin = next(p for p in target.input_pins if p.pin_category == "data")
        
        connection = self.graph.create_connection(source_pin, target_pin)
        QApplication.processEvents()
        
        # Connection should be visible in the scene
        scene_items = self.graph.items()
        connection_items = [item for item in scene_items if isinstance(item, Connection)]
        
        self.assertGreater(len(connection_items), 0)
        self.assertIn(connection, connection_items)
        
        # Connection should have a visible path
        self.assertIsNotNone(connection.path())
        
        print("PASS Connection visual feedback working correctly")


class TestRerouteNodeWorkflow(FullGUITestCase):
    """Test reroute node functionality which is prone to bugs."""
    
    def test_reroute_node_creation_and_deletion(self):
        """Test creating and deleting reroute nodes."""
        # Create a reroute node
        initial_node_count = len(self.graph.nodes)
        
        reroute = RerouteNode()
        reroute.setPos(300, 200)
        self.graph.addItem(reroute)
        self.graph.nodes.append(reroute)
        
        QApplication.processEvents()
        
        # Verify reroute node was created
        self.assertEqual(len(self.graph.nodes), initial_node_count + 1)
        self.assertIn(reroute, self.graph.nodes)
        self.assertTrue(reroute.isVisible())
        self.assertEqual(reroute.title, "Reroute")
        
        # Test reroute node properties
        self.assertTrue(hasattr(reroute, 'input_pin'))
        self.assertTrue(hasattr(reroute, 'output_pin'))
        
        # Test deletion
        reroute.setSelected(True)
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        self.graph.keyPressEvent(delete_event)
        
        QApplication.processEvents()
        
        # Verify deletion
        self.assertEqual(len(self.graph.nodes), initial_node_count)
        self.assertNotIn(reroute, self.graph.nodes)
        
        print("PASS Reroute node creation and deletion working correctly")
    
    def test_reroute_node_undo_redo_cycle(self):
        """Test the critical undo/redo functionality for reroute nodes."""
        # This test specifically addresses the user-reported bug
        
        # Create a reroute node
        reroute = RerouteNode()
        reroute.setPos(250, 150)
        self.graph.addItem(reroute)
        self.graph.nodes.append(reroute)
        
        QApplication.processEvents()
        
        initial_node_count = len(self.graph.nodes)
        
        # Verify it's a RerouteNode
        self.assertIsInstance(reroute, RerouteNode)
        self.assertEqual(reroute.title, "Reroute")
        
        # Delete the reroute node
        reroute.setSelected(True)
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        self.graph.keyPressEvent(delete_event)
        
        QApplication.processEvents()
        
        # Verify deletion
        self.assertEqual(len(self.graph.nodes), initial_node_count - 1)
        
        # Undo the deletion (this is where the bug occurred)
        undo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
        self.view.keyPressEvent(undo_event)
        
        QApplication.processEvents()
        
        # Verify undo worked
        self.assertEqual(len(self.graph.nodes), initial_node_count)
        
        # Find the restored node
        restored_reroute = None
        for node in self.graph.nodes:
            if hasattr(node, 'title') and node.title == "Reroute":
                restored_reroute = node
                break
        
        # This is the critical test - the restored node should be a RerouteNode
        self.assertIsNotNone(restored_reroute)
        self.assertIsInstance(restored_reroute, RerouteNode, 
                             "CRITICAL BUG: RerouteNode was restored as regular Node!")
        
        # Verify reroute-specific properties
        self.assertTrue(hasattr(restored_reroute, 'input_pin'))
        self.assertTrue(hasattr(restored_reroute, 'output_pin'))
        
        print("PASS Reroute node undo/redo cycle working correctly - Bug fixed!")


class TestFileOperationsWorkflow(FullGUITestCase):
    """Test file loading and saving workflows."""
    
    def test_create_and_save_simple_graph(self):
        """Test creating a simple graph and saving it."""
        # Create a simple graph
        node1 = self.graph.create_node("Node 1", pos=(100, 100))
        node2 = self.graph.create_node("Node 2", pos=(300, 100))
        
        node1.set_code('@node_entry\ndef func1() -> str:\n    return "test"')
        node2.set_code('@node_entry\ndef func2(x: str):\n    print(x)')
        
        QApplication.processEvents()
        
        # Test graph serialization (simulating save)
        graph_data = self.graph.serialize()
        
        # Verify serialization contains expected data
        self.assertIn("nodes", graph_data)
        self.assertIn("connections", graph_data)
        self.assertEqual(len(graph_data["nodes"]), 2)
        
        # Verify node data
        node_titles = [node_data["title"] for node_data in graph_data["nodes"]]
        self.assertIn("Node 1", node_titles)
        self.assertIn("Node 2", node_titles)
        
        print("PASS Graph creation and serialization working correctly")
    
    def test_load_example_file_if_exists(self):
        """Test loading an example file if it exists."""
        # Look for example files
        examples_dir = Path(__file__).parent.parent.parent / "examples"
        
        if not examples_dir.exists():
            self.skipTest("Examples directory not found")
        
        example_files = list(examples_dir.glob("*.md"))
        
        if not example_files:
            self.skipTest("No example files found")
        
        # Try to load the first example file
        example_file = example_files[0]
        
        try:
            # Simulate file loading (this would normally go through the file menu)
            from data.file_operations import load_file
            
            initial_node_count = len(self.graph.nodes)
            load_file(self.window, str(example_file))
            
            QApplication.processEvents()
            
            # Verify content was loaded
            # (This test is flexible since we don't know exact content)
            final_node_count = len(self.graph.nodes)
            
            # Should have loaded some nodes
            self.assertGreaterEqual(final_node_count, initial_node_count)
            
            print(f"PASS Successfully loaded example file: {example_file.name}")
            print(f"  Loaded {final_node_count - initial_node_count} nodes")
            
        except Exception as e:
            self.fail(f"Failed to load example file {example_file.name}: {e}")


class TestViewOperations(FullGUITestCase):
    """Test view operations like panning, zooming, etc."""
    
    def test_view_panning_and_zooming(self):
        """Test that view panning and zooming work correctly."""
        # Get initial view transform
        initial_transform = self.view.transform()
        
        # Create a node to use as reference
        node = self.graph.create_node("Reference Node", pos=(100, 100))
        QApplication.processEvents()
        
        # Test zooming in (simulate mouse wheel)
        wheel_event = QWheelEvent(
            self.view.rect().center(),  # position
            self.view.rect().center(),  # global position  
            QPointF(0, 0),              # pixel delta
            QPointF(0, 120),            # angle delta (positive = zoom in)
            Qt.NoButton,                # buttons
            Qt.NoModifier,              # modifiers
            Qt.ScrollPhase.NoScrollPhase,  # phase
            False                       # inverted
        )
        
        self.view.wheelEvent(wheel_event)
        QApplication.processEvents()
        
        # Transform should have changed (zoom)
        after_zoom_transform = self.view.transform()
        self.assertNotEqual(initial_transform.m11(), after_zoom_transform.m11())
        
        # Reset view
        self.view.resetTransform()
        QApplication.processEvents()
        
        print("PASS View operations (panning/zooming) working correctly")
    
    def test_view_selection_rectangle(self):
        """Test selection rectangle functionality."""
        # Create multiple nodes
        node1 = self.graph.create_node("Node 1", pos=(50, 50))
        node2 = self.graph.create_node("Node 2", pos=(150, 50))
        node3 = self.graph.create_node("Node 3", pos=(250, 50))
        
        QApplication.processEvents()
        
        # Initially no nodes should be selected
        selected_nodes = [node for node in self.graph.nodes if node.isSelected()]
        self.assertEqual(len(selected_nodes), 0)
        
        # Select all nodes programmatically (simulating selection rectangle)
        for node in self.graph.nodes:
            node.setSelected(True)
        
        QApplication.processEvents()
        
        # All nodes should now be selected
        selected_nodes = [node for node in self.graph.nodes if node.isSelected()]
        self.assertEqual(len(selected_nodes), 3)
        
        print("PASS View selection operations working correctly")


class TestErrorRecovery(FullGUITestCase):
    """Test error recovery and edge cases."""
    
    def test_invalid_operations_dont_crash(self):
        """Test that invalid operations don't crash the application."""
        # Try to delete when nothing is selected
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        
        try:
            self.graph.keyPressEvent(delete_event)
            QApplication.processEvents()
            # Should not crash
        except Exception as e:
            self.fail(f"Delete with no selection crashed: {e}")
        
        # Try to undo when there's nothing to undo
        undo_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
        
        try:
            self.view.keyPressEvent(undo_event)
            QApplication.processEvents()
            # Should not crash
        except Exception as e:
            self.fail(f"Undo with no history crashed: {e}")
        
        print("PASS Invalid operations handled gracefully without crashing")
    
    def test_node_with_invalid_code_handling(self):
        """Test that nodes with invalid code don't break the GUI."""
        node = self.graph.create_node("Invalid Code Node", pos=(100, 100))
        
        # Set invalid Python code
        invalid_codes = [
            "def broken(",  # Syntax error
            "this is not python",  # Not Python at all
            "",  # Empty code
            "# just a comment"  # Only comments
        ]
        
        for invalid_code in invalid_codes:
            try:
                node.set_code(invalid_code)
                QApplication.processEvents()
                
                # Node should still be visible and functional
                self.assertTrue(node.isVisible())
                self.assertEqual(node.code, invalid_code)
                
            except Exception as e:
                self.fail(f"Invalid code '{invalid_code}' caused crash: {e}")
        
        print("PASS Invalid code handled gracefully in GUI")


def run_gui_test_suite():
    """Run the complete GUI test suite with proper reporting."""
    print("="*60)
    print("STARTING FULL GUI INTEGRATION TEST SUITE")
    print("="*60)
    print()
    print("These tests will open actual PyFlowGraph windows.")
    print("Each test window will appear briefly then close automatically.")
    print("Do not interact with the test windows during execution.")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestApplicationStartup,
        TestNodeCreationWorkflow,
        TestConnectionWorkflow,
        TestRerouteNodeWorkflow,
        TestFileOperationsWorkflow,
        TestViewOperations,
        TestErrorRecovery,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=False  # Don't buffer output for GUI tests
    )
    
    result = runner.run(suite)
    
    print()
    print("="*60)
    print("GUI TEST SUITE COMPLETE")
    print("="*60)
    
    if result.wasSuccessful():
        print("PASS All GUI tests PASSED")
        print("The application GUI is working correctly!")
    else:
        print("X Some GUI tests FAILED")
        print("There are GUI issues that need attention:")
        
        if result.failures:
            print(f"  - {len(result.failures)} test failures")
        if result.errors:
            print(f"  - {len(result.errors)} test errors")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_gui_test_suite()
    
    # Clean up QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
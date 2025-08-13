#!/usr/bin/env python3

"""
GUI Rendering Tests for PyFlowGraph

This test suite specifically tests that GUI components are actually rendered and visible
after loading markdown files, not just that widgets exist in memory.

Addresses the issue: "nodes that have a GUI don't actually have the GUI shown"
"""

import sys
import os
import unittest
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QGraphicsView, QWidget, QMainWindow
from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtTest import QTest

from src.node import Node
from src.node_graph import NodeGraph
from src.flow_format import load_flow_file
from src.node_editor_view import NodeEditorView
from src.node_editor_window import NodeEditorWindow


class TestGUIRendering(unittest.TestCase):
    """Test suite for verifying actual GUI rendering after markdown loading."""
    
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
        self.view = NodeEditorView(self.graph)
        self.view.show()  # Important: GUI must be shown to render properly
        
        # Process events to ensure GUI is initialized
        QApplication.processEvents()
        
    def tearDown(self):
        """Clean up after each test."""
        # Clean up the view
        self.view.hide()
        self.view.close()
        
        # Clear the graph
        for node in list(self.graph.nodes):
            self.graph.remove_node(node)
        
        # Process events to clean up
        QApplication.processEvents()
    
    def wait_for_rendering(self, timeout_ms=1000):
        """Wait for GUI rendering to complete."""
        start_time = time.time() * 1000
        while (time.time() * 1000 - start_time) < timeout_ms:
            QApplication.processEvents()
            QTest.qWait(10)
    
    def test_text_processing_pipeline_gui_rendering(self):
        """Test that the text_processing_pipeline.md file loads with visible GUIs."""
        pipeline_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples', 'text_processing_pipeline.md')
        
        if not os.path.exists(pipeline_path):
            self.skipTest(f"Test file not found: {pipeline_path}")
        
        # Load the markdown file
        try:
            data = load_flow_file(pipeline_path)
            self.graph.deserialize(data)
        except Exception as e:
            self.fail(f"Failed to load text processing pipeline: {e}")
        
        # Verify nodes were loaded
        self.assertGreater(len(self.graph.nodes), 0, "Should load nodes from the file")
        
        # Find nodes with GUI components
        gui_nodes = []
        for node in self.graph.nodes:
            if hasattr(node, 'gui_code') and node.gui_code.strip():
                gui_nodes.append(node)
        
        self.assertGreater(len(gui_nodes), 0, "Should have nodes with GUI code")
        
        # Force GUI rebuild and rendering
        for node in gui_nodes:
            node.rebuild_gui()
        
        # Wait for rendering to complete
        self.wait_for_rendering(2000)
        
        # Test each GUI node
        for node in gui_nodes:
            with self.subTest(node=node.title):
                self.verify_node_gui_rendering(node)
    
    def verify_node_gui_rendering(self, node):
        """Verify that a node's GUI is actually rendered and visible."""
        
        # 1. Check that GUI widgets were created
        self.assertGreater(len(node.gui_widgets), 0, 
                          f"Node {node.title} should have GUI widgets")
        
        # 2. Check that proxy widget exists and is visible
        self.assertTrue(hasattr(node, 'proxy_widget'), 
                       f"Node {node.title} should have proxy_widget attribute")
        
        if node.proxy_widget:
            self.assertIsNotNone(node.proxy_widget.widget(), 
                               f"Node {node.title} proxy widget should contain a widget")
            
            # Check if proxy widget is visible
            self.assertTrue(node.proxy_widget.isVisible(), 
                          f"Node {node.title} proxy widget should be visible")
        
        # 3. Check node dimensions (should not be zero height)
        self.assertGreater(node.height, 0, 
                          f"Node {node.title} height should be > 0, got {node.height}")
        self.assertGreater(node.width, 0, 
                          f"Node {node.title} width should be > 0, got {node.width}")
        
        # 4. Check that node height is reasonable (not tiny)
        self.assertGreaterEqual(node.height, 100, 
                               f"Node {node.title} should have reasonable height (≥100px), got {node.height}")
        
        # 5. Check that the node has proper bounding rect
        bounding_rect = node.boundingRect()
        self.assertGreater(bounding_rect.width(), 0, 
                          f"Node {node.title} bounding rect width should be > 0")
        self.assertGreater(bounding_rect.height(), 0, 
                          f"Node {node.title} bounding rect height should be > 0")
        
        # 6. For nodes with custom widgets, verify the container is properly sized
        if hasattr(node, 'content_container') and node.content_container:
            container_size = node.content_container.size()
            self.assertGreater(container_size.width(), 0, 
                             f"Node {node.title} content container width should be > 0")
            self.assertGreater(container_size.height(), 0, 
                             f"Node {node.title} content container height should be > 0")
    
    def test_gui_node_zero_height_regression(self):
        """Test for the specific zero height bug mentioned."""
        # Create a test node with GUI
        node = self.graph.create_node("Zero Height Test", pos=(100, 100))
        
        # Set GUI code that should create visible components
        gui_code = '''
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QCheckBox

widgets['label1'] = QLabel('Test Label 1', parent)
layout.addWidget(widgets['label1'])

widgets['input1'] = QLineEdit(parent)
widgets['input1'].setMinimumHeight(30)
layout.addWidget(widgets['input1'])

widgets['checkbox1'] = QCheckBox('Test Checkbox', parent)
layout.addWidget(widgets['checkbox1'])

widgets['button1'] = QPushButton('Test Button', parent)
layout.addWidget(widgets['button1'])
'''
        node.set_gui_code(gui_code)
        
        # Simulate the loading process
        node.rebuild_gui()
        self.wait_for_rendering()
        
        # Verify the node doesn't have zero height
        self.assertGreater(node.height, 0, "Node height should not be zero after GUI rebuild")
        self.assertGreaterEqual(node.height, 150, "Node should have reasonable height for its content")
        
        # Verify widgets exist and are properly sized
        self.assertEqual(len(node.gui_widgets), 4, "Should have 4 GUI widgets")
        
        # Check that proxy widget is properly configured
        if node.proxy_widget:
            proxy_size = node.proxy_widget.size()
            self.assertGreater(proxy_size.width(), 0, "Proxy widget should have positive width")
            self.assertGreater(proxy_size.height(), 0, "Proxy widget should have positive height")
    
    def test_pin_positions_after_gui_loading(self):
        """Test that pins are not stuck in top-left corner after GUI loading."""
        # Create a node with GUI that should affect layout
        node = self.graph.create_node("Pin Position Test", pos=(200, 200))
        
        # Set code that will create input and output pins
        logic_code = '''
@node_entry
def test_function(input1: str, input2: int, flag: bool) -> str:
    return f"result: {input1}_{input2}_{flag}"
'''
        node.set_code(logic_code)
        
        # Set GUI code that adds substantial height
        gui_code = '''
from PySide6.QtWidgets import QLabel, QTextEdit, QSpinBox, QCheckBox

for i in range(3):
    widgets[f'label_{i}'] = QLabel(f'Label {i}', parent)
    layout.addWidget(widgets[f'label_{i}'])

widgets['text_area'] = QTextEdit(parent)
widgets['text_area'].setMinimumHeight(100)
layout.addWidget(widgets['text_area'])

widgets['spinner'] = QSpinBox(parent)
layout.addWidget(widgets['spinner'])

widgets['check'] = QCheckBox('Enable feature', parent)
layout.addWidget(widgets['check'])
'''
        node.set_gui_code(gui_code)
        
        # Rebuild everything
        node.update_pins_from_code()  # This creates pins
        node.rebuild_gui()    # This should update layout
        self.wait_for_rendering()
        
        # Check that node has reasonable height
        self.assertGreaterEqual(node.height, 200, "Node with substantial GUI should be tall enough")
        
        # Check that pins are positioned correctly (not all at 0,0)
        input_pins = [pin for pin in node.pins if pin.pin_direction == "input"]
        output_pins = [pin for pin in node.pins if pin.pin_direction == "output"]
        
        self.assertGreater(len(input_pins), 0, "Should have input pins")
        self.assertGreater(len(output_pins), 0, "Should have output pins")
        
        # Verify input pins are positioned down the left side
        for i, pin in enumerate(input_pins):
            pin_pos = pin.pos()
            expected_y = 30 + i * 25  # Approximate expected position
            
            # Pin should not be at (0, 0) or stuck at the top
            self.assertNotEqual(pin_pos.x(), 0, f"Input pin {pin.name} should not be at x=0")
            self.assertGreaterEqual(pin_pos.y(), 20, f"Input pin {pin.name} should be positioned below title bar")
            
            # Pin should be positioned progressively down
            if i > 0:
                prev_pin_y = input_pins[i-1].pos().y()
                self.assertGreater(pin_pos.y(), prev_pin_y, 
                                 f"Input pin {pin.name} should be below previous pin")
        
        # Verify output pins are positioned down the right side
        for i, pin in enumerate(output_pins):
            pin_pos = pin.pos()
            
            # Pin should be on the right side of the node
            self.assertGreater(pin_pos.x(), node.width - 50, 
                             f"Output pin {pin.name} should be on right side")
            self.assertGreaterEqual(pin_pos.y(), 20, 
                                  f"Output pin {pin.name} should be positioned below title bar")
    
    def test_gui_refresh_after_markdown_load(self):
        """Test that GUI properly refreshes after markdown loading (simulating the bug)."""
        # This test simulates the sequence that happens when loading a .md file
        
        # Create a node manually first (simulating JSON loading)
        node = self.graph.create_node("Refresh Test", pos=(300, 300))
        
        # Set the properties as they would be loaded from markdown
        node.width = 250
        node.height = 180  # Set a specific height
        
        node.set_code('''
@node_entry
def test_func(text: str) -> str:
    return text.upper()
''')
        
        node.set_gui_code('''
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

widgets['label'] = QLabel('Enter text:', parent)
layout.addWidget(widgets['label'])

widgets['input'] = QLineEdit(parent)
widgets['input'].setPlaceholderText('Type here...')
layout.addWidget(widgets['input'])

widgets['button'] = QPushButton('Process', parent)
layout.addWidget(widgets['button'])
''')
        
        # Update pins from code (this happens during deserialization)
        node.update_pins_from_code()
        
        # Now simulate the refresh that should happen after markdown loading
        # This is what might be failing
        node.rebuild_gui()
        
        # Force scene update (this is what the file_operations.py does)
        self.graph.update()
        
        # Wait for rendering
        self.wait_for_rendering(1000)
        
        # Verify the refresh worked properly
        self.verify_node_gui_rendering(node)
        
        # Additional check: verify the GUI state can be applied
        if hasattr(node, 'apply_gui_state'):
            test_state = {'text': 'test input'}
            try:
                node.apply_gui_state(test_state)
                gui_state_works = True
            except Exception as e:
                gui_state_works = False
                print(f"GUI state application failed: {e}")
            
            self.assertTrue(gui_state_works, "GUI state application should work after refresh")


class TestGUIRenderingIntegration(unittest.TestCase):
    """Integration test with full NodeEditorWindow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for the entire test suite."""
        if QApplication.instance() is None:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def test_full_application_gui_loading(self):
        """Test GUI loading in the context of the full application."""
        # This test is more realistic but also more complex
        try:
            # Create a minimal NodeEditorWindow
            window = NodeEditorWindow()
            window.show()
            
            # Process events to initialize
            QApplication.processEvents()
            QTest.qWait(100)
            
            # Try to load the text processing pipeline
            pipeline_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples', 'text_processing_pipeline.md')
            
            if os.path.exists(pipeline_path):
                # Use the window's file operations to load
                try:
                    window.file_ops.load(pipeline_path)
                    
                    # Wait for loading to complete
                    QTest.qWait(500)
                    QApplication.processEvents()
                    
                    # Check that nodes with GUI were loaded properly
                    gui_nodes = []
                    for node in window.graph.nodes:
                        if hasattr(node, 'gui_code') and node.gui_code.strip():
                            gui_nodes.append(node)
                    
                    self.assertGreater(len(gui_nodes), 0, "Should load GUI nodes")
                    
                    # Verify each GUI node is properly rendered
                    for node in gui_nodes:
                        self.assertGreater(len(node.gui_widgets), 0, 
                                         f"Node {node.title} should have widgets")
                        self.assertGreater(node.height, 50, 
                                         f"Node {node.title} should have reasonable height")
                    
                except Exception as e:
                    self.fail(f"Failed to load file through NodeEditorWindow: {e}")
            
            # Clean up
            window.close()
            
        except Exception as e:
            # If we can't create the full window, skip this test
            self.skipTest(f"Could not create NodeEditorWindow: {e}")


def run_gui_rendering_tests():
    """Run all GUI rendering tests."""
    # Run with GUI event processing
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add the main rendering tests
    suite.addTest(loader.loadTestsFromTestCase(TestGUIRendering))
    
    # Add integration tests
    suite.addTest(loader.loadTestsFromTestCase(TestGUIRenderingIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=== GUI Rendering Tests ===")
    print("Testing actual GUI visibility and rendering after markdown loading...")
    print("This test verifies that GUI components are visually rendered, not just created in memory.")
    print()
    
    success = run_gui_rendering_tests()
    
    if success:
        print("\n=== All GUI Rendering Tests Passed ===")
        print("GUI components are rendering correctly after markdown loading!")
        sys.exit(0)
    else:
        print("\n=== GUI Rendering Issues Detected ===")
        print("Some GUI components are not rendering properly after markdown loading.")
        sys.exit(1)
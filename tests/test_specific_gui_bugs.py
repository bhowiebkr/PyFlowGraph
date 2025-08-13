#!/usr/bin/env python3

"""
Specific GUI Bug Tests for PyFlowGraph

This test file specifically targets the reported issues:
1. "nodes that have a GUI don't actually have the GUI shown" 
2. "nodes that don't have gui's will load with zero height which messes up the pin locations"
3. Issues with text_processing_pipeline.md specifically

Designed to reproduce and detect the exact bugs mentioned.
"""

import sys
import os
import unittest
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QGraphicsView
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest

from src.node import Node
from src.node_graph import NodeGraph
from src.flow_format import load_flow_file


class TestSpecificGUIBugs(unittest.TestCase):
    """Test suite for the specific GUI bugs reported."""
    
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
        self.view = QGraphicsView(self.graph)
        self.view.show()
        QApplication.processEvents()
        
    def tearDown(self):
        """Clean up after each test."""
        self.view.hide()
        self.view.close()
        for node in list(self.graph.nodes):
            self.graph.remove_node(node)
        QApplication.processEvents()
    
    def wait_for_gui_update(self, timeout_ms=1000):
        """Wait for GUI updates to complete."""
        start_time = time.time() * 1000
        while (time.time() * 1000 - start_time) < timeout_ms:
            QApplication.processEvents()
            QTest.qWait(10)
    
    def test_text_processing_pipeline_specific_bugs(self):
        """Test the specific text_processing_pipeline.md for GUI rendering issues."""
        pipeline_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples', 'text_processing_pipeline.md')
        
        if not os.path.exists(pipeline_path):
            self.skipTest(f"Test file not found: {pipeline_path}")
        
        print(f"\\nTesting {pipeline_path}...")
        
        # Load the file
        data = load_flow_file(pipeline_path)
        self.graph.deserialize(data)
        
        self.wait_for_gui_update(2000)
        
        # Analyze each node individually
        nodes_with_gui = []
        nodes_without_gui = []
        
        for node in self.graph.nodes:
            print(f"\\nAnalyzing node: {node.title}")
            print(f"  UUID: {getattr(node, 'uuid', 'N/A')}")
            print(f"  Type: {type(node).__name__}")
            print(f"  Position: ({node.pos().x():.1f}, {node.pos().y():.1f})")
            if hasattr(node, 'width') and hasattr(node, 'height'):
                print(f"  Size: {node.width}x{node.height}")
            elif hasattr(node, 'radius'):
                print(f"  Size: radius {node.radius}")
            
            # Check if it's a reroute node
            if type(node).__name__ == 'RerouteNode':
                print(f"  -> Reroute node (expected to be small)")
                continue
            
            # Check for GUI code
            has_gui = hasattr(node, 'gui_code') and node.gui_code.strip()
            print(f"  Has GUI code: {has_gui}")
            
            if has_gui:
                nodes_with_gui.append(node)
                print(f"  GUI widgets count: {len(getattr(node, 'gui_widgets', {}))}")
                
                # Check if proxy widget exists and is visible
                if hasattr(node, 'proxy_widget') and node.proxy_widget:
                    print(f"  Proxy widget exists: True")
                    print(f"  Proxy widget visible: {node.proxy_widget.isVisible()}")
                    proxy_size = node.proxy_widget.size()
                    print(f"  Proxy widget size: {proxy_size.width()}x{proxy_size.height()}")
                else:
                    print(f"  Proxy widget exists: False")
                
                # This is the key bug check: GUI nodes should show their GUI
                self.assertGreater(len(node.gui_widgets), 0, 
                                 f"Node '{node.title}' has GUI code but no widgets were created")
                
                if hasattr(node, 'proxy_widget') and node.proxy_widget:
                    self.assertTrue(node.proxy_widget.isVisible(),
                                  f"Node '{node.title}' proxy widget should be visible")
                
            else:
                nodes_without_gui.append(node)
                
                # Check for zero height bug in non-GUI nodes
                print(f"  Height check: {node.height} (should be > 0)")
                self.assertGreater(node.height, 0, 
                                 f"Node '{node.title}' without GUI has zero height")
                
                # Check pin positions for non-GUI nodes
                input_pins = [p for p in getattr(node, 'pins', []) if hasattr(p, 'pin_direction') and p.pin_direction == 'input']
                output_pins = [p for p in getattr(node, 'pins', []) if hasattr(p, 'pin_direction') and p.pin_direction == 'output']
                
                print(f"  Input pins: {len(input_pins)}, Output pins: {len(output_pins)}")
                
                # Check that pins are not stuck at (0,0) or top-left corner
                for pin in input_pins + output_pins:
                    pin_pos = pin.pos()
                    print(f"    Pin '{pin.name}' at ({pin_pos.x():.1f}, {pin_pos.y():.1f})")
                    
                    # Pins should not all be at the same position (stuck)
                    self.assertNotEqual((pin_pos.x(), pin_pos.y()), (0, 0),
                                      f"Pin '{pin.name}' in node '{node.title}' is stuck at origin")
        
        print(f"\\nSummary:")
        print(f"  Nodes with GUI: {len(nodes_with_gui)}")
        print(f"  Nodes without GUI: {len(nodes_without_gui)}")
        
        # Verify we found the expected nodes
        self.assertGreater(len(nodes_with_gui), 0, "Should have found nodes with GUI")
        
        # All GUI nodes should have visible widgets
        for node in nodes_with_gui:
            with self.subTest(node=node.title):
                self.verify_gui_node_rendering(node)
    
    def verify_gui_node_rendering(self, node):
        """Detailed verification of a GUI node's rendering."""
        print(f"\\nDetailed GUI check for: {node.title}")
        
        # 1. Widgets should exist
        widgets = getattr(node, 'gui_widgets', {})
        print(f"  GUI widgets: {list(widgets.keys())}")
        self.assertGreater(len(widgets), 0, f"Node should have GUI widgets")
        
        # 2. Proxy widget should exist and be configured
        if hasattr(node, 'proxy_widget'):
            proxy = node.proxy_widget
            if proxy:
                print(f"  Proxy widget size: {proxy.size().width()}x{proxy.size().height()}")
                print(f"  Proxy widget visible: {proxy.isVisible()}")
                print(f"  Proxy widget pos: ({proxy.pos().x():.1f}, {proxy.pos().y():.1f})")
                
                self.assertTrue(proxy.isVisible(), "Proxy widget should be visible")
                self.assertGreater(proxy.size().width(), 0, "Proxy widget should have width")
                self.assertGreater(proxy.size().height(), 0, "Proxy widget should have height")
            else:
                self.fail("Node has gui_code but no proxy widget")
        
        # 3. Node should have reasonable dimensions
        print(f"  Node dimensions: {node.width}x{node.height}")
        self.assertGreater(node.height, 50, f"GUI node should have reasonable height")
        self.assertGreater(node.width, 100, f"GUI node should have reasonable width")
        
        # 4. Content container should exist and be sized
        if hasattr(node, 'content_container'):
            container = node.content_container
            if container:
                container_size = container.size()
                print(f"  Content container: {container_size.width()}x{container_size.height()}")
                self.assertGreater(container_size.height(), 0, "Content container should have height")
    
    def test_gui_vs_non_gui_node_comparison(self):
        """Compare GUI and non-GUI nodes to verify different behaviors."""
        
        # Create a non-GUI node
        non_gui_node = self.graph.create_node("Non-GUI Node", pos=(100, 100))
        non_gui_node.set_code('''
@node_entry  
def simple_function(input_text: str) -> str:
    return input_text.upper()
''')
        non_gui_node.update_pins_from_code()
        
        # Create a GUI node
        gui_node = self.graph.create_node("GUI Node", pos=(300, 100))
        gui_node.set_code('''
@node_entry
def gui_function(input_text: str, flag: bool) -> str:
    return input_text if flag else ""
''')
        gui_node.set_gui_code('''
from PySide6.QtWidgets import QLabel, QLineEdit, QCheckBox

widgets['label'] = QLabel('Enter text:', parent)
layout.addWidget(widgets['label'])

widgets['input'] = QLineEdit(parent)
layout.addWidget(widgets['input'])

widgets['flag'] = QCheckBox('Enable processing', parent)
layout.addWidget(widgets['flag'])
''')
        gui_node.update_pins_from_code()
        
        self.wait_for_gui_update(500)
        
        print(f"\\nNode comparison:")
        print(f"  Non-GUI node: {non_gui_node.width}x{non_gui_node.height}")
        print(f"  GUI node: {gui_node.width}x{gui_node.height}")
        
        # Non-GUI node checks
        self.assertGreater(non_gui_node.height, 0, "Non-GUI node should not have zero height")
        self.assertEqual(len(getattr(non_gui_node, 'gui_widgets', {})), 0, 
                        "Non-GUI node should not have GUI widgets")
        
        # GUI node checks
        self.assertGreater(len(gui_node.gui_widgets), 0, "GUI node should have widgets")
        self.assertGreater(gui_node.height, non_gui_node.height, 
                          "GUI node should be taller than non-GUI node")
        
        # Pin position checks for both
        for node, name in [(non_gui_node, "Non-GUI"), (gui_node, "GUI")]:
            pins = getattr(node, 'pins', [])
            print(f"  {name} node pins:")
            for pin in pins:
                pos = pin.pos()
                print(f"    {pin.name}: ({pos.x():.1f}, {pos.y():.1f})")
                self.assertNotEqual((pos.x(), pos.y()), (0, 0), 
                                  f"{name} node pin should not be at origin")
    
    def test_markdown_vs_json_gui_rendering(self):
        """Test if there's a difference between loading from markdown vs JSON."""
        
        # Create test data that simulates what would be in a markdown file
        test_data = {
            "nodes": [{
                "uuid": "test-gui-node",
                "title": "Test GUI Node",
                "pos": [200, 200],
                "size": [250, 180],
                "code": '''
@node_entry
def test_function(text: str) -> str:
    return text.upper()
''',
                "gui_code": '''
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

widgets['label'] = QLabel('Input:', parent)
layout.addWidget(widgets['label'])

widgets['input'] = QLineEdit(parent)
widgets['input'].setPlaceholderText('Enter text...')
layout.addWidget(widgets['input'])

widgets['button'] = QPushButton('Convert', parent)
layout.addWidget(widgets['button'])
''',
                "gui_get_values_code": '''
def get_values(widgets):
    return {'text': widgets['input'].text()}

def set_initial_state(widgets, state):
    widgets['input'].setText(state.get('text', ''))
''',
                "gui_state": {"text": "test input"},
                "colors": {"title": "#007bff", "body": "#0056b3"}
            }],
            "connections": []
        }
        
        # Load using the same method as markdown loading
        self.graph.deserialize(test_data)
        self.wait_for_gui_update(1000)
        
        # Verify the node loaded correctly
        self.assertEqual(len(self.graph.nodes), 1)
        node = self.graph.nodes[0]
        
        print(f"\\nMarkdown-style loading test:")
        print(f"  Node: {node.title}")
        print(f"  Size: {node.width}x{node.height}")
        print(f"  GUI widgets: {len(node.gui_widgets)}")
        
        # Verify GUI is working
        self.verify_gui_node_rendering(node)
        
        # Check that GUI state was applied
        if 'input' in node.gui_widgets:
            current_text = node.gui_widgets['input'].text()
            print(f"  Input text: '{current_text}'")
            # Note: GUI state might not be applied automatically in this test


def run_specific_bug_tests():
    """Run the specific GUI bug tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSpecificGUIBugs)
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=False)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=== Specific GUI Bug Detection Tests ===")
    print("Testing for the reported issues:")
    print("1. Nodes with GUI don't show their GUI components")
    print("2. Nodes without GUI have zero height and broken pin positions")
    print("3. Issues with text_processing_pipeline.md specifically")
    print()
    
    success = run_specific_bug_tests()
    
    if success:
        print("\\n=== All Specific Bug Tests Passed ===")
        print("Could not reproduce the reported GUI bugs.")
        sys.exit(0)
    else:
        print("\\n=== GUI Bugs Detected ===")
        print("Found issues matching the reported problems!")
        sys.exit(1)
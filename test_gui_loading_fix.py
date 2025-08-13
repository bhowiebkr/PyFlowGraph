#!/usr/bin/env python3
"""
Test to verify that GUI widgets load correctly from .md files without requiring manual resize.

This test checks for the zero height bug and GUI loading issues that were present
when loading .md files compared to JSON files.
"""

import sys
import os
import tempfile
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QEventLoop
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from node_graph import NodeGraph
from flow_format import FlowFormatHandler


class TestGUILoadingFix:
    """Test class to verify GUI loading works correctly from .md files."""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.graph = NodeGraph()
        
    def create_test_node_data(self):
        """Create test data for a node with GUI components."""
        return {
            "nodes": [
                {
                    "uuid": "test-node-with-gui",
                    "title": "Test GUI Node", 
                    "pos": [100, 100],
                    "size": [300, 200],
                    "code": """from typing import Tuple

@node_entry
def test_function(input_value: str) -> Tuple[str, int]:
    return f"Processed: {input_value}", len(input_value)""",
                    "gui_code": """from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

layout.addWidget(QLabel('Test Input:', parent))
widgets['input_field'] = QLineEdit(parent)
widgets['input_field'].setText('Default text')
layout.addWidget(widgets['input_field'])

widgets['button'] = QPushButton('Test Button', parent)
layout.addWidget(widgets['button'])""",
                    "gui_get_values_code": """def get_values(widgets):
    return {'input_value': widgets['input_field'].text()}

def set_initial_state(widgets, state):
    if 'input_value' in state:
        widgets['input_field'].setText(state['input_value'])""",
                    "gui_state": {"input_value": "Test value"},
                    "colors": {"title": "#007bff", "body": "#004494"},
                    "is_reroute": False
                },
                {
                    "uuid": "test-node-no-gui", 
                    "title": "Test No GUI Node",
                    "pos": [400, 100],
                    "size": [200, 150],
                    "code": """@node_entry
def simple_function(x: int) -> int:
    return x * 2""",
                    "gui_code": "",
                    "gui_get_values_code": "",
                    "gui_state": {},
                    "colors": {"title": "#28a745", "body": "#1e7e34"},
                    "is_reroute": False
                }
            ],
            "connections": [],
            "requirements": []
        }
    
    def create_test_md_file(self, data):
        """Create a temporary .md file with test data."""
        handler = FlowFormatHandler()
        md_content = handler.json_to_flow(data, "Test Graph", "Test graph for GUI loading verification")
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
        temp_file.write(md_content)
        temp_file.close()
        return temp_file.name
    
    def wait_for_deferred_updates(self):
        """Wait for Qt's deferred updates to complete."""
        # Process all pending events
        self.app.processEvents()
        
        # Wait a bit more for the QTimer.singleShot(0, ...) to execute
        loop = QEventLoop()
        QTimer.singleShot(50, loop.quit)  # 50ms should be enough for deferred updates
        loop.exec()
        
        # Process events again after the timer
        self.app.processEvents()
    
    def test_md_file_loading(self):
        """Test that .md file loading works correctly."""
        print("Testing .md file loading...")
        
        # Create test data and temporary .md file
        test_data = self.create_test_node_data()
        md_file_path = self.create_test_md_file(test_data)
        
        try:
            # Load the .md file
            handler = FlowFormatHandler()
            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            loaded_data = handler.flow_to_json(md_content)
            
            # Clear the graph and load the data
            self.graph.clear_graph()
            self.graph.deserialize(loaded_data)
            
            # Wait for deferred updates to complete
            self.wait_for_deferred_updates()
            
            # Verify nodes were created
            assert len(self.graph.nodes) == 2, f"Expected 2 nodes, got {len(self.graph.nodes)}"
            
            # Find the GUI node and no-GUI node
            gui_node = None
            no_gui_node = None
            
            for node in self.graph.nodes:
                if node.title == "Test GUI Node":
                    gui_node = node
                elif node.title == "Test No GUI Node":
                    no_gui_node = node
            
            assert gui_node is not None, "GUI node not found"
            assert no_gui_node is not None, "No-GUI node not found"
            
            # Test 1: Check that nodes have proper non-zero dimensions
            print(f"GUI node dimensions: {gui_node.width}x{gui_node.height}")
            print(f"No-GUI node dimensions: {no_gui_node.width}x{no_gui_node.height}")
            
            assert gui_node.height > 0, f"GUI node has zero height: {gui_node.height}"
            assert gui_node.width > 0, f"GUI node has zero width: {gui_node.width}"
            assert no_gui_node.height > 0, f"No-GUI node has zero height: {no_gui_node.height}"
            assert no_gui_node.width > 0, f"No-GUI node has zero width: {no_gui_node.width}"
            
            # Test 2: Check that GUI widgets were created
            assert len(gui_node.gui_widgets) > 0, "GUI widgets were not created"
            assert 'input_field' in gui_node.gui_widgets, "Input field widget not found"
            assert 'button' in gui_node.gui_widgets, "Button widget not found"
            
            # Test 3: Check that GUI widgets are properly sized and visible
            content_size_hint = gui_node.content_container.sizeHint()
            print(f"Content container size hint: {content_size_hint.width()}x{content_size_hint.height()}")
            assert content_size_hint.height() > 0, "Content container has zero height size hint"
            
            # Test 4: Check that pins were created correctly
            assert len(gui_node.pins) > 0, "GUI node has no pins"
            assert len(no_gui_node.pins) > 0, "No-GUI node has no pins"
            
            # Test 5: Check that GUI state was applied
            input_field = gui_node.gui_widgets.get('input_field')
            if input_field and hasattr(input_field, 'text'):
                current_text = input_field.text()
                print(f"Input field text: '{current_text}'")
                assert current_text == "Test value", f"GUI state not applied correctly. Expected 'Test value', got '{current_text}'"
            
            print("✓ All tests passed! GUI loading works correctly.")
            return True
            
        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(md_file_path)
            except:
                pass
    
    def test_json_loading_comparison(self):
        """Test that JSON loading still works for comparison."""
        print("Testing JSON file loading for comparison...")
        
        test_data = self.create_test_node_data()
        
        # Create temporary JSON file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(test_data, temp_file, indent=2)
        temp_file.close()
        
        try:
            # Load JSON data directly
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            # Clear the graph and load the data
            self.graph.clear_graph()
            self.graph.deserialize(loaded_data)
            
            # Wait for deferred updates
            self.wait_for_deferred_updates()
            
            # Verify it works the same way
            assert len(self.graph.nodes) == 2, f"JSON loading: Expected 2 nodes, got {len(self.graph.nodes)}"
            
            for node in self.graph.nodes:
                assert node.height > 0, f"JSON loading: Node {node.title} has zero height"
                assert node.width > 0, f"JSON loading: Node {node.title} has zero width"
            
            print("✓ JSON loading comparison test passed!")
            return True
            
        except Exception as e:
            print(f"✗ JSON comparison test failed: {str(e)}")
            return False
            
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass


def main():
    """Run the GUI loading tests."""
    print("Running GUI Loading Fix Tests")
    print("=" * 40)
    
    tester = TestGUILoadingFix()
    
    # Run tests
    md_test_passed = tester.test_md_file_loading()
    json_test_passed = tester.test_json_loading_comparison()
    
    print("\n" + "=" * 40)
    if md_test_passed and json_test_passed:
        print("🎉 All tests PASSED! The GUI loading fix is working correctly.")
        return 0
    else:
        print("❌ Some tests FAILED. There may still be issues with GUI loading.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
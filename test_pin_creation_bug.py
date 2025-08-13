#!/usr/bin/env python3

"""
Pin Creation Bug Tests

This test specifically targets the issue where nodes loaded from markdown
don't get their pins created properly, which causes:
1. Pins to be missing or stuck at (0,0)
2. Nodes to appear broken/unusable
3. Connection issues

This is the REAL bug being experienced.
"""

import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication

from node import Node
from node_graph import NodeGraph
from flow_format import load_flow_file


class TestPinCreationBug(unittest.TestCase):
    """Test suite for pin creation issues during markdown loading."""
    
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
        
    def tearDown(self):
        """Clean up after each test."""
        for node in list(self.graph.nodes):
            self.graph.remove_node(node)
    
    def test_text_analyzer_pin_creation(self):
        """Test the specific Text Statistics Analyzer node that has no pins."""
        pipeline_path = os.path.join(os.path.dirname(__file__), 'examples', 'text_processing_pipeline.md')
        
        if not os.path.exists(pipeline_path):
            self.skipTest(f"Test file not found: {pipeline_path}")
        
        # Load the markdown file
        data = load_flow_file(pipeline_path)
        self.graph.deserialize(data)
        
        # Find the Text Statistics Analyzer node
        analyzer_node = None
        for node in self.graph.nodes:
            if hasattr(node, 'title') and 'Text Statistics Analyzer' in node.title:
                analyzer_node = node
                break
        
        self.assertIsNotNone(analyzer_node, "Should find Text Statistics Analyzer node")
        
        print(f"\\nAnalyzing Text Statistics Analyzer node:")
        print(f"  Title: {analyzer_node.title}")
        print(f"  Code length: {len(analyzer_node.code)} characters")
        print(f"  Code preview: {analyzer_node.code[:100]}...")
        print(f"  Total pins: {len(getattr(analyzer_node, 'pins', []))}")
        
        # Check the pins in detail
        pins = getattr(analyzer_node, 'pins', [])
        input_pins = [p for p in pins if hasattr(p, 'pin_direction') and p.pin_direction == 'input']
        output_pins = [p for p in pins if hasattr(p, 'pin_direction') and p.pin_direction == 'output']
        
        print(f"  Input pins: {len(input_pins)}")
        for pin in input_pins:
            print(f"    - {pin.name} ({getattr(pin, 'pin_type', 'unknown')})")
        
        print(f"  Output pins: {len(output_pins)}")
        for pin in output_pins:
            print(f"    - {pin.name} ({getattr(pin, 'pin_type', 'unknown')})")
        
        # This is the bug: the node should have pins based on its function signature
        # Function: def analyze_text(text: str) -> Tuple[int, int, int, int, float, str]
        # Should have: 1 input pin (text), 6 output pins, plus exec pins
        
        # Check for expected pins
        expected_input_pins = ['text']  # plus exec_in
        expected_output_pins = ['output_1', 'output_2', 'output_3', 'output_4', 'output_5', 'output_6']  # plus exec_out
        
        input_pin_names = [pin.name for pin in input_pins]
        output_pin_names = [pin.name for pin in output_pins]
        
        print(f"  Expected input pins: {expected_input_pins}")
        print(f"  Actual input pin names: {input_pin_names}")
        print(f"  Expected output pins: {expected_output_pins}")
        print(f"  Actual output pin names: {output_pin_names}")
        
        # The bug test: pins should exist
        self.assertGreater(len(pins), 0, "Node should have pins")
        self.assertGreater(len(input_pins), 0, "Node should have input pins")
        self.assertGreater(len(output_pins), 0, "Node should have output pins")
        
        # Check for the text input pin specifically
        has_text_input = any(pin.name == 'text' for pin in input_pins)
        self.assertTrue(has_text_input, "Node should have 'text' input pin")
        
        # Check for multiple output pins (Tuple return creates multiple outputs)
        self.assertGreaterEqual(len(output_pins), 6, "Node should have 6+ output pins for Tuple return")
    
    def test_manual_pin_creation_vs_markdown_loading(self):
        """Compare manually created node vs markdown loaded node."""
        
        # 1. Create a node manually and set the same code
        manual_node = self.graph.create_node("Manual Test Node", pos=(100, 100))
        manual_node.set_code('''
import re
from typing import Tuple
from collections import Counter

@node_entry
def analyze_text(text: str) -> Tuple[int, int, int, int, float, str]:
    # Basic counts
    char_count = len(text)
    word_count = len(text.split())
    sentence_count = len(re.findall(r'[.!?]+', text))
    paragraph_count = len([p for p in text.split('\\n\\n') if p.strip()])
    
    # Average word length
    words = text.split()
    avg_word_length = sum(len(word.strip('.,!?;:')) for word in words) / len(words) if words else 0
    
    # Most common words (top 5)
    word_freq = Counter(word.lower().strip('.,!?;:') for word in words if len(word) > 2)
    top_words = ', '.join([f"{word}({count})" for word, count in word_freq.most_common(5)])
    
    return char_count, word_count, sentence_count, paragraph_count, round(avg_word_length, 1), top_words
''')
        
        # 2. Load the same node from markdown
        pipeline_path = os.path.join(os.path.dirname(__file__), 'examples', 'text_processing_pipeline.md')
        if os.path.exists(pipeline_path):
            data = load_flow_file(pipeline_path)
            
            # Create a second graph for the markdown node
            markdown_graph = NodeGraph()
            markdown_graph.deserialize(data)
            
            # Find the analyzer node
            markdown_node = None
            for node in markdown_graph.nodes:
                if hasattr(node, 'title') and 'Text Statistics Analyzer' in node.title:
                    markdown_node = node
                    break
            
            if markdown_node:
                # Compare the two nodes
                manual_pins = len(getattr(manual_node, 'pins', []))
                markdown_pins = len(getattr(markdown_node, 'pins', []))
                
                print(f"\\nPin comparison:")
                print(f"  Manual node pins: {manual_pins}")
                print(f"  Markdown node pins: {markdown_pins}")
                
                manual_inputs = [p for p in getattr(manual_node, 'pins', []) if hasattr(p, 'pin_direction') and p.pin_direction == 'input']
                markdown_inputs = [p for p in getattr(markdown_node, 'pins', []) if hasattr(p, 'pin_direction') and p.pin_direction == 'input']
                
                print(f"  Manual input pins: {[p.name for p in manual_inputs]}")
                print(f"  Markdown input pins: {[p.name for p in markdown_inputs]}")
                
                # This is the bug: markdown loaded node should have same pins as manual node
                self.assertEqual(manual_pins, markdown_pins, 
                               "Markdown loaded node should have same number of pins as manually created node")
                
                self.assertEqual(len(manual_inputs), len(markdown_inputs),
                               "Markdown loaded node should have same number of input pins")
    
    def test_pin_creation_during_deserialization(self):
        """Test the pin creation process during deserialization."""
        
        # Simulate the data that would come from markdown
        test_data = {
            "nodes": [{
                "uuid": "test-analyzer",
                "title": "Test Analyzer",
                "pos": [100, 100],
                "size": [250, 150],
                "code": '''
import re
from typing import Tuple

@node_entry
def analyze_text(text: str) -> Tuple[int, int, int]:
    char_count = len(text)
    word_count = len(text.split())
    sentence_count = len(re.findall(r'[.!?]+', text))
    return char_count, word_count, sentence_count
''',
                "gui_code": "",
                "gui_get_values_code": "",
                "gui_state": {},
                "colors": {}
            }],
            "connections": []
        }
        
        # Load using deserialize (same as markdown loading)
        self.graph.deserialize(test_data)
        
        # Check the node
        self.assertEqual(len(self.graph.nodes), 1)
        node = self.graph.nodes[0]
        
        print(f"\\nDeserialization test:")
        print(f"  Node title: {node.title}")
        print(f"  Total pins: {len(getattr(node, 'pins', []))}")
        
        pins = getattr(node, 'pins', [])
        input_pins = [p for p in pins if hasattr(p, 'pin_direction') and p.pin_direction == 'input']
        output_pins = [p for p in pins if hasattr(p, 'pin_direction') and p.pin_direction == 'output']
        
        print(f"  Input pins: {[p.name for p in input_pins]}")
        print(f"  Output pins: {[p.name for p in output_pins]}")
        
        # Should have text input and 3 outputs for Tuple[int, int, int]
        self.assertGreater(len(pins), 0, "Deserialized node should have pins")
        
        # Check for specific expected pins
        input_names = [p.name for p in input_pins]
        self.assertIn('text', input_names, "Should have 'text' input pin")
        
        # Should have 3 output pins for the Tuple return
        output_names = [p.name for p in output_pins]
        expected_outputs = ['output_1', 'output_2', 'output_3']
        for expected in expected_outputs:
            self.assertIn(expected, output_names, f"Should have '{expected}' output pin")


def run_pin_creation_tests():
    """Run the pin creation bug tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPinCreationBug)
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=False)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=== Pin Creation Bug Tests ===")
    print("Testing for the pin creation issues in markdown-loaded nodes...")
    print("This is likely the root cause of the GUI rendering problems.")
    print()
    
    success = run_pin_creation_tests()
    
    if success:
        print("\\n=== No Pin Creation Issues Found ===")
    else:
        print("\\n=== Pin Creation Bug Detected ===")
        print("Found the root cause of the GUI rendering issues!")
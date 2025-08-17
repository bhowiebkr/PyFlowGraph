#!/usr/bin/env python3

"""
File Format Tests

Tests file format parsing and conversion functionality including:
- Markdown (.md) format parsing and generation
- JSON format compatibility  
- Format conversion between .md and JSON
- File metadata preservation
- Requirements management
"""

import unittest
import sys
import os
import json
import tempfile

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

# Import directly to avoid circular dependency through data.__init__
sys.path.insert(0, os.path.join(src_path, 'data'))
import flow_format
FlowFormatHandler = flow_format.FlowFormatHandler
load_flow_file = flow_format.load_flow_file
# Skip FileOperationsManager import to avoid circular dependency
# from data.file_operations import FileOperationsManager


class TestFileFormats(unittest.TestCase):
    """Test suite for file format handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = FlowFormatHandler()
    
    def test_json_to_markdown_conversion(self):
        """Test converting JSON graph data to markdown format."""
        test_data = {
            "nodes": [{
                "uuid": "test-node-1",
                "title": "Test Node",
                "pos": [100, 100],
                "size": [250, 150],
                "code": '@node_entry\ndef test() -> str:\n    return "test"',
                "gui_code": "",
                "colors": {},
                "gui_state": {}
            }],
            "connections": []
        }
        
        markdown = self.handler.data_to_markdown(test_data, "Test Graph")
        
        self.assertIn("# Test Graph", markdown)
        self.assertIn("## Node: Test Node", markdown)
        self.assertIn("test-node-1", markdown)
        self.assertIn("@node_entry", markdown)
    
    def test_markdown_to_json_conversion(self):
        """Test parsing markdown format back to JSON."""
        markdown_content = '''# Test Graph

## Node: Test Node (ID: test-node-1)

Test node description.

### Metadata

```json
{
  "uuid": "test-node-1",
  "title": "Test Node",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def test() -> str:
    return "test"
```

## Connections

```json
[]
```
'''
        
        data = self.handler.markdown_to_data(markdown_content)
        
        self.assertIn("nodes", data)
        self.assertEqual(len(data["nodes"]), 1)
        self.assertEqual(data["nodes"][0]["title"], "Test Node")
        self.assertEqual(data["nodes"][0]["uuid"], "test-node-1")


def run_file_format_tests():
    """Run all file format tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFileFormats)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_file_format_tests()
    sys.exit(0 if success else 1)
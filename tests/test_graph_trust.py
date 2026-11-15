"""
Graph trust and dependency checks.

Opening or pasting a graph runs the GUI code of its nodes, so the editor asks first unless
the file is trusted. Graph dependencies go to pip, so entries that are pip options are refused.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication

from pyflowgraph.data.graph_trust import (
    GraphTrustStore,
    bundled_example_dirs,
    describe_nodes,
    is_bundled_example,
    nodes_with_open_code,
)
from pyflowgraph.data.file_operations import FileOperationsManager
from pyflowgraph.execution.environment_manager import find_unsafe_requirements


GRAPH_WITH_GUI_CODE = '''# Trust Test

A graph whose node builds a widget.

## Node: Widget Node (ID: node-1)

```json
{
  "uuid": "node-1",
  "title": "Widget Node",
  "pos": [0, 0],
  "size": [250, 150]
}
```

### Logic

```python
@node_entry
def make_value() -> int:
    return 1
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel
layout.addWidget(QLabel("hello"))
```
'''


class MemorySettings:
    """Stands in for QSettings so that tests never write the user's settings."""

    def __init__(self):
        self.values = {}

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value


class TestNodesWithOpenCode(unittest.TestCase):
    def test_finds_gui_code_and_state_handler(self):
        data = {
            "nodes": [
                {"title": "Plain", "code": "def f(): pass", "gui_code": "", "gui_get_values_code": "   "},
                {"title": "Widget", "gui_code": "layout.addWidget(None)"},
                {"title": "Values", "gui_get_values_code": "def get_values(w): return {}"},
            ]
        }
        self.assertEqual(nodes_with_open_code(data), ["Widget", "Values"])

    def test_ignores_bad_data(self):
        self.assertEqual(nodes_with_open_code({}), [])
        self.assertEqual(nodes_with_open_code({"nodes": None}), [])
        self.assertEqual(nodes_with_open_code({"nodes": ["text", 3]}), [])
        self.assertEqual(nodes_with_open_code(None), [])

    def test_describe_nodes_shortens_long_lists(self):
        text = describe_nodes([f"Node {i}" for i in range(15)])
        self.assertIn("- Node 9", text)
        self.assertNotIn("- Node 10", text)
        self.assertIn("and 5 more", text)


class TestGraphTrustStore(unittest.TestCase):
    def setUp(self):
        self.store = GraphTrustStore(MemorySettings(), example_dirs=[])
        self.data = {"nodes": [{"title": "Widget", "gui_code": "x = 1"}]}

    def test_untrusted_file_needs_confirmation(self):
        self.assertEqual(self.store.needs_confirmation("graph.md", "text", self.data), ["Widget"])

    def test_trusted_content_needs_no_confirmation(self):
        self.store.trust("graph.md", "text")
        self.assertEqual(self.store.needs_confirmation("graph.md", "text", self.data), [])

    def test_changed_content_needs_confirmation_again(self):
        self.store.trust("graph.md", "text")
        self.assertEqual(self.store.needs_confirmation("graph.md", "changed text", self.data), ["Widget"])

    def test_trust_is_per_file(self):
        self.store.trust("graph.md", "text")
        self.assertEqual(self.store.needs_confirmation("other.md", "text", self.data), ["Widget"])

    def test_graph_without_gui_code_needs_no_confirmation(self):
        data = {"nodes": [{"title": "Plain", "code": "def f(): pass"}]}
        self.assertEqual(self.store.needs_confirmation("graph.md", "text", data), [])


class TestBundledExamples(unittest.TestCase):
    def test_file_inside_examples_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            examples = os.path.join(folder, "examples")
            os.makedirs(examples)
            inside = os.path.join(examples, "demo.md")
            outside = os.path.join(folder, "demo.md")
            self.assertTrue(is_bundled_example(inside, [examples]))
            self.assertFalse(is_bundled_example(outside, [examples]))
            # A sibling folder whose name starts with "examples" is not the examples folder.
            self.assertFalse(is_bundled_example(os.path.join(folder, "examples2", "demo.md"), [examples]))

    def test_repository_examples_are_found(self):
        repo_examples = os.path.join(REPO_ROOT, "examples")
        normalized = [os.path.normcase(os.path.abspath(d)) for d in bundled_example_dirs()]
        self.assertIn(os.path.normcase(os.path.abspath(repo_examples)), normalized)


class TestUnsafeRequirements(unittest.TestCase):
    def test_package_names_are_accepted(self):
        safe = ["numpy", "pandas>=2.0", "requests[socks]==2.31.0", 'torch; python_version >= "3.9"', "opencv-python"]
        self.assertEqual(find_unsafe_requirements(safe), [])

    def test_pip_options_are_refused(self):
        unsafe = [
            "--index-url=http://example.invalid/simple",
            "-r other.txt",
            "numpy --extra-index-url http://example.invalid/simple",
            "numpy\n--pre",
            "",
            "   ",
            5,
        ]
        self.assertEqual(find_unsafe_requirements(unsafe), unsafe)

    def test_empty_list(self):
        self.assertEqual(find_unsafe_requirements([]), [])
        self.assertEqual(find_unsafe_requirements(None), [])


class TestFileOperationsTrust(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "trust_test.md")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(GRAPH_WITH_GUI_CODE)

        self.graph = MagicMock()
        self.log = MagicMock()
        self.manager = FileOperationsManager(MagicMock(), self.graph, self.log)
        self.manager.settings = MemorySettings()
        self.manager.trust_store = GraphTrustStore(self.manager.settings, example_dirs=[])
        self.asked = []

    def tearDown(self):
        self.folder.cleanup()

    def _answer(self, answer):
        def confirm(file_path, titles):
            self.asked.append((file_path, titles))
            return answer
        self.manager.confirm_untrusted_code = confirm

    def test_declined_graph_does_not_open(self):
        self._answer(False)
        self.assertFalse(self.manager.load(self.path))
        self.assertEqual(self.asked, [(self.path, ["Widget Node"])])
        self.graph.deserialize.assert_not_called()
        self.assertIsNone(self.manager.current_file_path)

    def test_accepted_graph_opens_and_is_remembered(self):
        self._answer(True)
        self.assertTrue(self.manager.load(self.path))
        self.graph.deserialize.assert_called_once()

        self.asked.clear()
        self.assertTrue(self.manager.load(self.path))
        self.assertEqual(self.asked, [])

    def test_startup_skips_untrusted_graph_without_asking(self):
        self._answer(True)
        self.assertFalse(self.manager.load(self.path, startup=True))
        self.assertEqual(self.asked, [])
        self.graph.deserialize.assert_not_called()

    def test_changed_file_asks_again(self):
        self._answer(True)
        self.assertTrue(self.manager.load(self.path))
        with open(self.path, "a", encoding="utf-8") as f:
            f.write("\n")
        self.asked.clear()
        self.assertTrue(self.manager.load(self.path))
        self.assertEqual(len(self.asked), 1)


class TestPasteTrust(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from pyflowgraph.core.node_graph import NodeGraph

        self.graph = NodeGraph()
        self.asked = []

        def confirm(titles):
            self.asked.append(titles)
            return False

        self.graph.confirm_pasted_code = confirm
        self.data = {"nodes": [{"title": "Widget", "gui_code": "x = 1"}]}

    def test_foreign_text_with_gui_code_asks(self):
        self.assertFalse(self.graph._may_run_pasted_code("text from elsewhere", self.data))
        self.assertEqual(self.asked, [["Widget"]])

    def test_text_this_editor_copied_does_not_ask(self):
        self.graph._last_copied_text = "line one\nline two"
        self.assertTrue(self.graph._may_run_pasted_code("line one\r\nline two", self.data))
        self.assertEqual(self.asked, [])

    def test_nodes_without_gui_code_do_not_ask(self):
        data = {"nodes": [{"title": "Plain", "code": "def f(): pass"}]}
        self.assertTrue(self.graph._may_run_pasted_code("text from elsewhere", data))
        self.assertEqual(self.asked, [])


if __name__ == "__main__":
    unittest.main()

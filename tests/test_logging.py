"""Check that the editor reports through the logging module.

Debug messages appear only when the log level allows them, and failures that used to print a
traceback still reach the log at the error level.
"""

import contextlib
import io
import logging
import os
import unittest
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from pyflowgraph.commands.command_base import CommandBase
from pyflowgraph.commands.command_history import CommandHistory
from pyflowgraph.core.node import Node
from pyflowgraph.core.node_graph import NodeGraph

GUI_CODE = """
from PySide6.QtWidgets import QLabel
widgets['label'] = QLabel('Test', parent)
layout.addWidget(widgets['label'])
"""

GUI_VALUES_CODE = """
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    widgets['label'].setText(str(outputs.get('output_1', '')))
"""

FAILING_GUI_VALUES_CODE = """
def set_values(widgets, outputs):
    raise RuntimeError('set_values failed on purpose')
"""


class FailingCommand(CommandBase):
    def __init__(self):
        super().__init__("Failing command")

    def execute(self):
        raise RuntimeError("execute failed on purpose")

    def undo(self):
        return True


class TestLogging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.graph = NodeGraph()
        self.node = Node("Test Node")
        self.graph.addItem(self.node)
        self.node.set_gui_code(GUI_CODE)
        self.node.set_gui_get_values_code(GUI_VALUES_CODE)

    def test_old_debug_flags_are_gone(self):
        import pyflowgraph.commands.node.basic_operations as basic_operations
        import pyflowgraph.core.node as node_module
        import pyflowgraph.execution.graph_executor as graph_executor

        self.assertFalse(hasattr(graph_executor, "DEBUG_EXECUTION"))
        self.assertFalse(hasattr(node_module, "DEBUG_GUI_UPDATES"))
        self.assertFalse(hasattr(basic_operations, "DEBUG_NODE_COMMANDS"))

    def test_silent_at_the_default_level(self):
        self.assertFalse(logging.getLogger("pyflowgraph.core.node").isEnabledFor(logging.DEBUG))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.node.set_gui_values({"output_1": "value"})
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(self.node.gui_widgets["label"].text(), "value")

    def test_debug_level_shows_gui_updates(self):
        with self.assertLogs("pyflowgraph.core.node", level="DEBUG") as logs:
            self.node.set_gui_values({"output_1": "value"})
        text = "\n".join(logs.output)
        self.assertIn("set_gui_values() called for 'Test Node'", text)
        self.assertNotIn("DEBUG:", "\n".join(r.getMessage() for r in logs.records))

    def test_gui_update_failure_has_traceback_at_debug_level(self):
        self.node.set_gui_get_values_code(FAILING_GUI_VALUES_CODE)
        with self.assertLogs("pyflowgraph.core.node", level="DEBUG") as logs:
            self.node.set_gui_values({"output_1": "value"})
        failures = [r for r in logs.records if "failed" in r.getMessage()]
        self.assertEqual(len(failures), 1)
        self.assertIsNotNone(failures[0].exc_info)

    def test_command_failure_is_an_error_with_traceback(self):
        history = CommandHistory()
        with self.assertLogs("pyflowgraph.commands.command_history", level="ERROR") as logs:
            self.assertFalse(history.execute_command(FailingCommand()))
        self.assertEqual(len(logs.records), 1)
        record = logs.records[0]
        self.assertEqual(record.levelno, logging.ERROR)
        self.assertIn("execute failed on purpose", record.getMessage())
        self.assertIsNotNone(record.exc_info)
        self.assertEqual(history.get_command_count(), 0)


class TestSetupLogging(unittest.TestCase):
    def setUp(self):
        import main

        self.main = main

    def level_for(self, value):
        env = {} if value is None else {"PYFLOWGRAPH_LOG_LEVEL": value}
        with mock.patch.dict(os.environ, env, clear=False), mock.patch("logging.basicConfig") as config:
            if value is None:
                os.environ.pop("PYFLOWGRAPH_LOG_LEVEL", None)
            self.main.setup_logging()
        return config.call_args.kwargs["level"]

    def test_default_level_is_warning(self):
        self.assertEqual(self.level_for(None), logging.WARNING)

    def test_level_from_environment(self):
        self.assertEqual(self.level_for("debug"), logging.DEBUG)
        self.assertEqual(self.level_for("INFO"), logging.INFO)

    def test_unknown_level_falls_back_to_warning(self):
        self.assertEqual(self.level_for("loud"), logging.WARNING)
        self.assertEqual(self.level_for("basic_format"), logging.WARNING)


if __name__ == "__main__":
    unittest.main()

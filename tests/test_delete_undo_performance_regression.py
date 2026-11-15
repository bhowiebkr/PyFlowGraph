"""Delete and undo on the password generator example.

After a delete and its undo, the graph must be the same as before: the same connections, no
connection left on a pin that the graph does not have, and each node runs once per execution.
A connection left on a pin makes the graph slower after each undo, because the nodes after it
run again. These checks find that cause exactly, so they do not compare times.
"""

import os
import random
import time
import unittest

import pytest
from PySide6.QtWidgets import QApplication, QTextEdit

from pyflowgraph.commands.node_commands import DeleteNodeCommand
from pyflowgraph.execution.graph_executor import GraphExecutor
from pyflowgraph.ui.editor.node_editor_window import NodeEditorWindow

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "examples", "password_generator_tool_group.md")
RUN_PREFIX = "--- Executing Node: "


class TestDeleteUndoPerformanceRegression(unittest.TestCase):

    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.window = NodeEditorWindow()
        self.graph = self.window.graph
        self.assertTrue(self.window.file_ops.load(EXAMPLE), "The example should open")
        self.assertGreaterEqual(len(self.graph.nodes), 4)
        self.assertGreaterEqual(len(self.graph.connections), 10)

        # Nodes run in this process, with the environment of the window.
        self.log_widget = QTextEdit()
        self.executor = GraphExecutor(self.graph, self.log_widget, self.window._get_current_venv_path)

        self.original_connections = self.connection_keys()
        self.assert_each_node_runs_once()

    def tearDown(self):
        self.window.close()

    def connection_keys(self):
        """The connections of the graph by node title and pin name."""
        return sorted((c.start_pin.node.title, c.start_pin.name, c.end_pin.node.title, c.end_pin.name)
                      for c in self.graph.connections)

    def stale_connections(self):
        """Connections on a pin of a graph node that are not in the graph."""
        live = {id(c) for c in self.graph.connections}
        return [(node.title, pin.name)
                for node in self.graph.nodes
                for pin in node.input_pins + node.output_pins
                for connection in pin.connections if id(connection) not in live]

    def assert_connections_intact(self, expected=None):
        """Each connection is in the graph once, on both of its pins, and no pin holds others."""
        keys = self.connection_keys()
        self.assertEqual(len(keys), len(set(keys)), "A connection is in the graph twice")
        if expected is not None:
            self.assertEqual(keys, expected)
        for connection in self.graph.connections:
            self.assertEqual(connection.start_pin.connections.count(connection), 1)
            self.assertEqual(connection.end_pin.connections.count(connection), 1)
        self.assertEqual(self.stale_connections(), [], "Pins hold connections that the graph does not have")

    def executed_titles(self):
        """Run the graph once. Return the titles of the nodes that ran, in order."""
        self.log_widget.clear()
        self.executor.execute()
        return [line[len(RUN_PREFIX):].removesuffix(" ---")
                for line in self.log_widget.toPlainText().splitlines() if line.startswith(RUN_PREFIX)]

    def assert_each_node_runs_once(self):
        self.assertEqual(sorted(self.executed_titles()), sorted(n.title for n in self.graph.nodes))

    def node(self, title):
        for node in self.graph.nodes:
            if node.title == title:
                return node
        self.fail(f"Node with title '{title}' not found")

    def delete(self, title):
        command = DeleteNodeCommand(self.graph, self.node(title))
        self.assertTrue(command.execute(), f"Delete of '{title}' should succeed")
        return command

    def timed_undo(self, command):
        start = time.perf_counter()
        self.assertTrue(command.undo(), "Undo should succeed")
        return (time.perf_counter() - start) * 1000

    def test_single_node_delete_undo_performance(self):
        command = self.delete("Password Generator Engine")
        self.assertLess(self.timed_undo(command), 50, "Undo should take less than 50 ms")
        self.assert_connections_intact(self.original_connections)
        self.assert_each_node_runs_once()

    def test_multiple_node_delete_undo_performance(self):
        commands = [self.delete("Password Strength Analyzer"), self.delete("Password Output & Copy")]
        for command in reversed(commands):
            self.timed_undo(command)
            self.assert_connections_intact()
        self.assert_connections_intact(self.original_connections)
        self.assert_each_node_runs_once()

    def test_connection_heavy_node_performance(self):
        # The configuration node has the most connections.
        command = self.delete("Password Configuration")
        self.assertLess(self.timed_undo(command), 100, "Undo should take less than 100 ms")
        self.assert_connections_intact(self.original_connections)
        self.assert_each_node_runs_once()

    def test_chaos_delete_undo_performance(self):
        rng = random.Random(1)
        titles = [n.title for n in self.graph.nodes if n.title != "Password Configuration"]
        for cycle in range(5):
            # Find the node by title: an undo restores a new node object.
            command = self.delete(rng.choice(titles))
            self.assertLess(self.timed_undo(command), 75, f"Undo {cycle + 1} should be fast")
            self.assert_connections_intact(self.original_connections)
            self.assert_each_node_runs_once()

    def test_performance_thresholds_compliance(self):
        start = time.perf_counter()
        for _ in range(5):
            self.executor.execute()
        self.assertLess((time.perf_counter() - start) * 1000 / 5, 500, "Execution should take less than 500 ms")

        start = time.perf_counter()
        command = self.delete("Password Strength Analyzer")
        self.assertLess((time.perf_counter() - start) * 1000, 25, "Delete should take less than 25 ms")
        self.assertLess(self.timed_undo(command), 50, "Undo should take less than 50 ms")


if __name__ == "__main__":
    unittest.main()

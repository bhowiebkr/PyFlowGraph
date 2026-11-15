"""Delete and undo on small graphs: the connections and the executions stay as they were.

The pins come from the node code, as in the editor, so that the undo can make them again.
"""

import time
import unittest

import pytest
from PySide6.QtWidgets import QApplication, QTextEdit

from pyflowgraph.commands.node_commands import DeleteNodeCommand
from pyflowgraph.core.node_graph import NodeGraph
from pyflowgraph.execution.graph_executor import GraphExecutor

RUN_PREFIX = "--- Executing Node: "


def pin(node, name):
    for p in node.input_pins + node.output_pins:
        if p.name == name:
            return p
    raise KeyError(f"{node.title} has no pin {name!r}")


class TestPerformanceRegressionValidation(unittest.TestCase):

    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.graph = NodeGraph()
        self.log_widget = QTextEdit()
        # No environment: the node code uses only the standard library.
        self.executor = GraphExecutor(self.graph, self.log_widget, lambda: None)

    def create_chain(self, count, data=True, execution=True):
        """Node0 -> Node1 -> ... Node0 has no inputs; each other node passes its input on."""
        nodes = []
        for i in range(count):
            node = self.graph.create_node(f"Node{i}", pos=(200 * i, 0), use_command=False)
            if i == 0:
                node.set_code("@node_entry\ndef node0() -> str:\n    return 'value'\n")
            else:
                node.set_code(f"@node_entry\ndef node{i}(v: str) -> str:\n    return v\n")
                previous = nodes[-1]
                if data:
                    self.graph.create_connection(pin(previous, "output_1"), pin(node, "v"), use_command=False)
                if execution:
                    self.graph.create_connection(pin(previous, "exec_out"), pin(node, "exec_in"), use_command=False)
            nodes.append(node)
        return nodes

    def node(self, title):
        for node in self.graph.nodes:
            if node.title == title:
                return node
        self.fail(f"Node with title '{title}' not found")

    def pin_connection_count(self):
        """Connections on the pins of the graph nodes. Each graph connection is on two pins."""
        return sum(len(p.connections) for n in self.graph.nodes for p in n.input_pins + n.output_pins)

    def executed_titles(self):
        self.log_widget.clear()
        self.executor.execute()
        return [line[len(RUN_PREFIX):].removesuffix(" ---")
                for line in self.log_widget.toPlainText().splitlines() if line.startswith(RUN_PREFIX)]

    def delete(self, title):
        command = DeleteNodeCommand(self.graph, self.node(title))
        self.assertTrue(command.execute(), f"Delete of {title} should succeed")
        return command

    def test_duplicate_connection_prevention(self):
        self.create_chain(3, execution=False)
        self.assertEqual(self.pin_connection_count(), 4)

        command = self.delete("Node1")
        self.assertEqual(len(self.graph.connections), 0, "Connections should be removed with the node")
        self.assertEqual(self.pin_connection_count(), 0, "No pin should keep a removed connection")

        self.assertTrue(command.undo(), "Undo should succeed")
        self.assertEqual(len(self.graph.connections), 2)
        self.assertEqual(self.pin_connection_count(), 4)
        for node in self.graph.nodes:
            for p in node.input_pins + node.output_pins:
                self.assertEqual(len(p.connections), len(set(map(id, p.connections))),
                                 f"Pin {node.title}.{p.name} holds a connection twice")

    def test_execution_performance_stability(self):
        self.create_chain(4)
        expected = ["Node0", "Node1", "Node2", "Node3"]
        self.assertEqual(self.executed_titles(), expected)

        self.assertTrue(self.delete("Node1").undo())
        self.assertEqual(len(self.graph.connections), 6, "All connections should be restored")
        self.assertEqual(self.executed_titles(), expected, "Each node should run once after the undo")

    def test_multiple_delete_undo_cycles(self):
        self.create_chain(3)
        for cycle in range(3):
            # Find the node by title: an undo restores a new node object.
            self.assertTrue(self.delete("Node1").undo())
            self.assertEqual(self.pin_connection_count(), 8, f"Cycle {cycle + 1} should not add connections")
        self.assertEqual(self.executed_titles(), ["Node0", "Node1", "Node2"])

    def test_performance_regression_thresholds(self):
        self.create_chain(1)
        # The best of several cycles: one timing on a shared CI runner can be slow for reasons
        # outside the test. A slower delete or undo still shows in the best run.
        deletes, undos = [], []
        for _ in range(5):
            start = time.perf_counter()
            command = self.delete("Node0")
            deletes.append((time.perf_counter() - start) * 1000)

            start = time.perf_counter()
            self.assertTrue(command.undo(), "Undo should succeed")
            undos.append((time.perf_counter() - start) * 1000)

        self.assertLess(min(deletes), 50, "Delete should take less than 50 ms")
        self.assertLess(min(undos), 100, "Undo should take less than 100 ms")


if __name__ == "__main__":
    unittest.main()

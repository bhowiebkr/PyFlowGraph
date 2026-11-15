"""Delete and undo keep the connections of the other nodes as they were.

A connection that a delete leaves on a pin makes each execution after the undo run the nodes
after it again, so the graph gets slower after each delete and undo. The pins come from the
node code, as in the editor, so that the undo can make them again.
"""

import unittest

import pytest
from PySide6.QtWidgets import QApplication

from pyflowgraph.commands.node_commands import DeleteNodeCommand
from pyflowgraph.core.node_graph import NodeGraph

SOURCE_CODE = "@node_entry\ndef source() -> str:\n    return 'x'\n"
STEP_CODE = "@node_entry\ndef step(v: str) -> str:\n    return v\n"


def pin(node, name):
    for p in node.input_pins + node.output_pins:
        if p.name == name:
            return p
    raise KeyError(f"{node.title} has no pin {name!r}")


class TestPerformanceFixDemonstration(unittest.TestCase):

    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.graph = NodeGraph()

    def add_node(self, title, code, x):
        node = self.graph.create_node(title, pos=(x, 0), use_command=False)
        node.set_code(code)
        return node

    def connect(self, start, start_pin, end, end_pin):
        self.graph.create_connection(pin(start, start_pin), pin(end, end_pin), use_command=False)

    def node(self, title):
        for node in self.graph.nodes:
            if node.title == title:
                return node
        self.fail(f"Node with title '{title}' not found")

    def pin_connection_count(self):
        """Connections on the pins of the graph nodes. Each graph connection is on two pins."""
        return sum(len(p.connections) for n in self.graph.nodes for p in n.input_pins + n.output_pins)

    def test_performance_fix_demonstration(self):
        # Config -> Generator -> Analyzer -> Output, and Config gives its value to each of them.
        config = self.add_node("Config", SOURCE_CODE, 0)
        previous = config
        for i, title in enumerate(("Generator", "Analyzer", "Output"), 1):
            node = self.add_node(title, STEP_CODE, 200 * i)
            self.connect(previous, "exec_out", node, "exec_in")
            self.connect(config, "output_1", node, "v")
            previous = node
        self.assertEqual(len(self.graph.connections), 6)
        self.assertEqual(self.pin_connection_count(), 12)

        for title in ("Generator", "Analyzer", "Output"):
            command = DeleteNodeCommand(self.graph, self.node(title))
            self.assertTrue(command.execute(), f"Delete of {title} should succeed")
            self.assertTrue(command.undo(), f"Undo of {title} should succeed")
            self.assertEqual(len(self.graph.connections), 6, f"Undo of {title} should restore all connections")
            self.assertEqual(self.pin_connection_count(), 12,
                             f"After the undo of {title}, the pins should hold only the graph connections")

    def test_connection_integrity_validation(self):
        first = self.add_node("Node1", SOURCE_CODE, 0)
        second = self.add_node("Node2", STEP_CODE, 200)
        self.connect(first, "output_1", second, "v")

        command = DeleteNodeCommand(self.graph, first)
        self.assertTrue(command.execute())
        self.assertEqual(pin(second, "v").connections, [], "Delete should remove the connection from the other pin")

        self.assertTrue(command.undo())
        restored = self.node("Node1")
        self.assertEqual(len(pin(restored, "output_1").connections), 1)
        self.assertEqual(len(pin(second, "v").connections), 1)


if __name__ == "__main__":
    unittest.main()

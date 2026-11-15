"""A reroute node on a data connection, with real nodes: run the graph, save it and open it again.

Node A gives 'hello' to node B. A runs before B by an execution connection. The data goes
through a reroute node.
"""

import pytest
from PySide6.QtWidgets import QApplication, QTextEdit

from pyflowgraph.core.node_graph import NodeGraph
from pyflowgraph.data.flow_format import FlowFormatHandler
from pyflowgraph.execution.graph_executor import GraphExecutor


def pin(node, name):
    return next(p for p in node.input_pins + node.output_pins if p.name == name)


def build_graph(reroute):
    graph = NodeGraph()
    a = graph.create_node("A", pos=(0, 0), use_command=False)
    a.set_code("@node_entry\ndef a() -> str:\n    return 'hello'\n")
    b = graph.create_node("B", pos=(400, 0), use_command=False)
    b.set_code("@node_entry\ndef b(v: str) -> str:\n    print('B got', repr(v))\n    return v\n")
    graph.create_connection(pin(a, "exec_out"), pin(b, "exec_in"), use_command=False)
    if reroute:
        r = graph.create_node("", pos=(200, 100), is_reroute=True, use_command=False)
        graph.create_connection(pin(a, "output_1"), r.input_pin, use_command=False)
        graph.create_connection(r.output_pin, pin(b, "v"), use_command=False)
    else:
        graph.create_connection(pin(a, "output_1"), pin(b, "v"), use_command=False)
    return graph


def value_that_b_got(graph):
    log = QTextEdit()
    GraphExecutor(graph, log, lambda: None).execute()
    return [line for line in log.toPlainText().splitlines() if line.startswith("B got")]


@pytest.fixture(autouse=True)
def app():
    return QApplication.instance() or QApplication([])


def test_direct_connection_passes_data():
    assert value_that_b_got(build_graph(reroute=False)) == ["B got 'hello'"]


def test_reroute_passes_data():
    assert value_that_b_got(build_graph(reroute=True)) == ["B got 'hello'"]


def test_reroute_graph_opens_again():
    handler = FlowFormatHandler()
    text = handler.data_to_markdown(build_graph(reroute=True).serialize(), "Reroute data")
    loaded = NodeGraph()
    loaded.deserialize(handler.markdown_to_data(text))
    assert len(loaded.nodes) == 3
    assert len(loaded.connections) == 3

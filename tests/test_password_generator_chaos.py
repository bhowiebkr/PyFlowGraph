"""Deletes, undos and redos on the password generator example, then the run button.

The steps go through the undo history of the graph, as the editor menus do. After each step,
each connection of the graph is on its two pins and no pin holds a connection that the graph
does not have. After all the steps are undone, the graph is as before, and a run shows the
new password in the output node.
"""

import os
import random
import re

import pytest
from PySide6.QtWidgets import QApplication

from pyflowgraph.ui.editor.node_editor_window import NodeEditorWindow

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "examples", "password_generator_tool_group.md")


@pytest.fixture
def window():
    QApplication.instance() or QApplication([])
    window = NodeEditorWindow()
    assert window.file_ops.load(EXAMPLE), "The example should open"
    assert not window.graph.can_undo(), "Opening a file should leave nothing to undo"
    yield window
    window.close()


def node(graph, title):
    for n in graph.nodes:
        if n.title == title:
            return n
    raise AssertionError(f"Node with title '{title}' not found")


def connection_keys(graph):
    return sorted((c.start_pin.node.title, c.start_pin.name, c.end_pin.node.title, c.end_pin.name)
                  for c in graph.connections)


def assert_connections_intact(graph):
    keys = connection_keys(graph)
    assert len(keys) == len(set(keys)), "A connection is in the graph twice"
    for c in graph.connections:
        assert c.start_pin.connections.count(c) == 1
        assert c.end_pin.connections.count(c) == 1
    live = {id(c) for c in graph.connections}
    stale = [(n.title, p.name) for n in graph.nodes for p in n.input_pins + n.output_pins
             for c in p.connections if id(c) not in live]
    assert stale == [], "Pins hold connections that the graph does not have"


def undo_all(graph):
    while graph.can_undo():
        assert graph.undo_last_command()
        assert_connections_intact(graph)


def run_and_check_output(window):
    """Click the run button. The output node shows the one password that the generator made."""
    window.execution_ctrl.main_exec_button.click()
    generated = re.findall(r"^Generated password: (.*)$", window.output_log.toPlainText(), re.M)
    assert len(generated) == 1, "The generator should run once"
    widgets = node(window.graph, "Password Output & Copy").gui_widgets
    assert widgets["password_field"].text() == generated[0]
    assert f"Generated Password: {generated[0]}" in widgets["strength_display"].toPlainText()


def delete_node(graph, title):
    assert graph.remove_node(node(graph, title)) is not False
    assert_connections_intact(graph)


def delete_connection(graph, index):
    assert graph.remove_connection(graph.connections[index]) is not False
    assert_connections_intact(graph)


def test_chaos_deletion_undo_redo_execution(window):
    graph = window.graph
    original = connection_keys(graph)
    run_and_check_output(window)
    rng = random.Random(7)
    for _ in range(3):
        deletes = rng.randint(1, 3)
        for _ in range(deletes):
            if rng.random() < 0.5 and len(graph.nodes) > 1:
                delete_node(graph, rng.choice(graph.nodes).title)
            elif graph.connections:
                delete_connection(graph, rng.randrange(len(graph.connections)))
        undos = rng.randint(1, deletes)
        for _ in range(undos):
            assert graph.undo_last_command()
            assert_connections_intact(graph)
        for _ in range(rng.randint(0, undos)):
            assert graph.redo_last_command()
            assert_connections_intact(graph)
    undo_all(graph)
    assert connection_keys(graph) == original
    run_and_check_output(window)


@pytest.mark.parametrize("pattern", [
    "delete middle node, undo",
    "delete output node, undo",
    "delete connection, undo, redo",
    "delete two connections, undo all",
])
def test_specific_deletion_patterns(window, pattern):
    graph = window.graph
    original = connection_keys(graph)
    if pattern == "delete middle node, undo":
        delete_node(graph, "Password Generator Engine")
    elif pattern == "delete output node, undo":
        delete_node(graph, "Password Output & Copy")
    elif pattern == "delete connection, undo, redo":
        removed = connection_keys(graph)
        delete_connection(graph, 0)
        removed = [k for k in removed if k not in connection_keys(graph)]
        assert graph.undo_last_command()
        assert connection_keys(graph) == original
        assert graph.redo_last_command()
        assert_connections_intact(graph)
        assert connection_keys(graph) == sorted(set(original) - set(removed))
        return
    else:
        delete_connection(graph, 0)
        delete_connection(graph, 0)
    undo_all(graph)
    assert connection_keys(graph) == original
    run_and_check_output(window)


def test_rapid_operations(window):
    graph = window.graph
    original = connection_keys(graph)
    rng = random.Random(3)
    for i in range(10):
        if i % 2 == 0:
            delete_node(graph, rng.choice(graph.nodes).title)
        else:
            delete_connection(graph, rng.randrange(len(graph.connections)))
        assert graph.undo_last_command()
        assert_connections_intact(graph)
    assert connection_keys(graph) == original
    run_and_check_output(window)

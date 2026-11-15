"""Regression tests for the fixes of the 2026-11 bug pass.

Each test fails on the code before the fix: connection drags, code change undo, widget values
across GUI code changes, the Dependencies section, the execution namespace, live mode, reroute
chains and the startup graph.
"""

import os
import sys

import pytest
import shiboken6
from PySide6.QtWidgets import QApplication, QGraphicsView, QTextEdit

from pyflowgraph.commands.node_commands import CodeChangeCommand, GuiCodeChangeCommand
from pyflowgraph.core.event_system import LiveGraphExecutor
from pyflowgraph.core.node_graph import NodeGraph
from pyflowgraph.data.flow_format import FlowFormatHandler
from pyflowgraph.execution.graph_executor import GraphExecutor

GUI_CODE = (
    "from PySide6.QtWidgets import QLineEdit, QPushButton\n"
    "widgets['text'] = QLineEdit('default')\n"
    "layout.addWidget(widgets['text'])\n"
    "widgets['run'] = QPushButton('Run')\n"
    "layout.addWidget(widgets['run'])\n"
)
GUI_LOGIC = (
    "def get_values(widgets):\n"
    "    return {'text': widgets['text'].text()}\n"
    "def set_values(widgets, outputs):\n"
    "    pass\n"
    "def set_initial_state(widgets, state):\n"
    "    widgets['text'].setText(state.get('text', 'default'))\n"
)


@pytest.fixture(scope="module", autouse=True)
def app():
    return QApplication.instance() or QApplication([])


def pin(node, name):
    return next(p for p in node.input_pins + node.output_pins if p.name == name)


def code_node(graph, title, code, x=0):
    node = graph.create_node(title, pos=(x, 0), use_command=False)
    node.set_code(code)
    return node


def gui_node(graph, title="G"):
    node = code_node(graph, title, "@node_entry\ndef g(text: str) -> str:\n    return text\n")
    node.set_gui_get_values_code(GUI_LOGIC)
    node.set_gui_code(GUI_CODE)
    return node


def links(graph):
    return sorted((c.start_pin.node.title, c.end_pin.node.title) for c in graph.connections)


def drag(graph, start_pin, target_pin):
    """Drag a new connection from start_pin and drop it on target_pin."""
    view = QGraphicsView(graph)
    graph.itemAt = lambda *args: target_pin
    graph.start_drag_connection(start_pin)
    graph.end_drag_connection(target_pin.scenePos())
    # Delete the view now: no event loop runs to process deleteLater.
    shiboken6.delete(view)


def source_and_sink(graph):
    a = code_node(graph, "A", "@node_entry\ndef a() -> str:\n    return 'x'\n")
    b = code_node(graph, "B", "@node_entry\ndef b(v: str) -> str:\n    return v\n", 300)
    return a, b


def test_drag_from_input_pin_starts_the_connection_at_the_output():
    graph = NodeGraph()
    a, b = source_and_sink(graph)
    drag(graph, pin(b, "v"), pin(a, "output_1"))
    assert len(graph.connections) == 1
    assert graph.connections[0].start_pin is pin(a, "output_1")
    assert graph.connections[0].end_pin is pin(b, "v")


def test_drag_onto_connected_input_replaces_in_one_undo_step():
    graph = NodeGraph()
    a, b = source_and_sink(graph)
    c = code_node(graph, "C", "@node_entry\ndef c() -> str:\n    return 'y'\n")
    graph.create_connection(pin(a, "output_1"), pin(b, "v"), use_command=False)
    drag(graph, pin(c, "output_1"), pin(b, "v"))
    assert links(graph) == [("C", "B")]
    assert len(pin(b, "v").connections) == 1
    graph.undo_last_command()
    assert links(graph) == [("A", "B")]
    assert [x.start_pin.node.title for x in pin(b, "v").connections] == ["A"]


def test_drag_of_wrong_type_keeps_the_old_connection():
    graph = NodeGraph()
    a, b = source_and_sink(graph)
    c = code_node(graph, "C", "@node_entry\ndef c() -> int:\n    return 1\n")
    graph.create_connection(pin(a, "output_1"), pin(b, "v"), use_command=False)
    drag(graph, pin(c, "output_1"), pin(b, "v"))
    assert links(graph) == [("A", "B")]
    assert graph.command_history.commands == []


def test_code_change_undo_restores_removed_connections():
    graph = NodeGraph()
    a, b = source_and_sink(graph)
    old = b.code
    graph.create_connection(pin(a, "output_1"), pin(b, "v"), use_command=False)
    graph.execute_command(CodeChangeCommand(graph, b, old, "@node_entry\ndef b() -> str:\n    return 'y'\n"))
    assert graph.connections == []
    graph.undo_last_command()
    assert links(graph) == [("A", "B")]
    assert len(pin(b, "v").connections) == 1


def test_gui_code_edit_keeps_widget_values():
    graph = NodeGraph()
    node = gui_node(graph)
    node.gui_widgets["text"].setText("changed")
    node.set_gui_code(GUI_CODE + "\n# edited\n")
    assert node.gui_widgets["text"].text() == "changed"


def test_gui_code_change_command_undo():
    graph = NodeGraph()
    node = gui_node(graph)
    node.gui_widgets["text"].setText("changed")
    new_gui = GUI_CODE + "widgets['extra'] = QLineEdit('more')\nlayout.addWidget(widgets['extra'])\n"
    graph.execute_command(GuiCodeChangeCommand(graph, node, GUI_CODE, new_gui, GUI_LOGIC, GUI_LOGIC))
    assert "extra" in node.gui_widgets
    assert node.gui_widgets["text"].text() == "changed"
    graph.undo_last_command()
    assert node.gui_code == GUI_CODE
    assert "extra" not in node.gui_widgets
    assert node.gui_widgets["text"].text() == "changed"


def test_dependencies_survive_save_and_open():
    handler = FlowFormatHandler()
    data = NodeGraph().serialize()
    data["dependencies"] = {"requirements": ["old"], "python": ">=3.11", "notes": "n"}
    data["requirements"] = ["requests"]
    text = handler.data_to_markdown(data, "T", "Description.")
    assert text.index("## Dependencies") < text.index("## Connections")
    back = handler.markdown_to_data(text)
    assert back["requirements"] == ["requests"]
    assert back["dependencies"] == {"requirements": ["requests"], "python": ">=3.11", "notes": "n"}


def test_no_dependencies_section_without_dependencies():
    data = NodeGraph().serialize()
    data["requirements"] = []
    assert "## Dependencies" not in FlowFormatHandler().data_to_markdown(data, "T")


def test_node_inputs_do_not_stay_in_the_namespace():
    graph = NodeGraph()
    a = code_node(graph, "A", "@node_entry\ndef a() -> str:\n    return 'secret'\n")
    b = code_node(graph, "B", "@node_entry\ndef b(v: str) -> str:\n    return v\n", 300)
    c = code_node(graph, "C",
                  "@node_entry\ndef c(w: str) -> str:\n    print('C sees', globals().get('v'))\n    return w\n", 600)
    graph.create_connection(pin(a, "exec_out"), pin(b, "exec_in"), use_command=False)
    graph.create_connection(pin(b, "exec_out"), pin(c, "exec_in"), use_command=False)
    graph.create_connection(pin(a, "output_1"), pin(b, "v"), use_command=False)
    graph.create_connection(pin(b, "output_1"), pin(c, "w"), use_command=False)
    log = QTextEdit()
    GraphExecutor(graph, log, lambda: None).execute()
    assert [x for x in log.toPlainText().splitlines() if x.startswith("C sees")] == ["C sees None"]


def test_data_passes_through_a_chain_of_reroute_nodes():
    graph = NodeGraph()
    a = code_node(graph, "A", "@node_entry\ndef a() -> str:\n    return 'through'\n")
    b = code_node(graph, "B", "@node_entry\ndef b(v: str) -> str:\n    print('B got', v)\n    return v\n", 600)
    r1 = graph.create_node("R1", pos=(200, 0), is_reroute=True, use_command=False)
    r2 = graph.create_node("R2", pos=(400, 0), is_reroute=True, use_command=False)
    graph.create_connection(pin(a, "exec_out"), pin(b, "exec_in"), use_command=False)
    graph.create_connection(pin(a, "output_1"), r1.input_pin, use_command=False)
    graph.create_connection(r1.output_pin, r2.input_pin, use_command=False)
    graph.create_connection(r2.output_pin, pin(b, "v"), use_command=False)
    log = QTextEdit()
    GraphExecutor(graph, log, lambda: None).execute()
    assert [x for x in log.toPlainText().splitlines() if x.startswith("B got")] == ["B got through"]


def test_live_mode_keeps_the_namespace_and_adds_the_venv_once(tmp_path):
    site = os.path.join(str(tmp_path), "Lib" if os.name == "nt" else "lib", "site-packages")
    if os.name != "nt":
        site = os.path.join(str(tmp_path), "lib", "python3", "site-packages")
    os.makedirs(site)
    graph = NodeGraph()
    node = code_node(graph, "Counter",
                     "count = globals().get('count', 0) + 1\n"
                     "@node_entry\ndef counter() -> int:\n    print('count', count)\n    return count\n")
    log = QTextEdit()
    live = LiveGraphExecutor(graph, log, lambda: str(tmp_path))
    live.set_live_mode(True)
    before = sys.path.count(site)
    try:
        live.trigger_node_execution(node)
        live.trigger_node_execution(node)
        assert sys.path.count(site) - before == 1
    finally:
        while site in sys.path:
            sys.path.remove(site)
    counts = [x for x in log.toPlainText().splitlines() if x.startswith("count")]
    assert counts == ["count 1", "count 2"]


def test_live_mode_connects_buttons_added_later_once():
    graph = NodeGraph()
    log = QTextEdit()
    live = LiveGraphExecutor(graph, log, lambda: None)
    live.set_live_mode(True)
    live.set_live_mode(False)
    node = gui_node(graph, "Late")
    live.set_live_mode(True)
    live.set_live_mode(False)
    live.set_live_mode(True)
    node.gui_widgets["run"].click()
    assert log.toPlainText().count("Button clicked in 'Late'") == 1


def test_startup_opens_the_default_example():
    from pyflowgraph.data.file_operations import DEFAULT_GRAPH
    from pyflowgraph.settings import app_settings
    from pyflowgraph.ui.editor.node_editor_window import NodeEditorWindow

    settings = app_settings()
    settings.setValue("default_graph", DEFAULT_GRAPH)
    try:
        window = NodeEditorWindow()
        try:
            assert window.windowTitle() == "PyFlowGraph - " + os.path.splitext(DEFAULT_GRAPH)[0]
            assert window.graph.nodes
        finally:
            window.close()
            shiboken6.delete(window)
    finally:
        settings.setValue("default_graph", "")
        settings.remove("last_file_path")
        settings.remove("last_directory")

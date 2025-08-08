# node_editor_window.py
# Contains the main application window (QMainWindow).
# Now connects the default nodes on startup.

import json
from PySide6.QtWidgets import QMainWindow, QMenuBar, QFileDialog, QTextEdit, QDockWidget, QInputDialog
from PySide6.QtGui import QAction, QFont
from PySide6.QtCore import Qt, QPointF
from node_graph import NodeGraph
from node_editor_view import NodeEditorView
from graph_executor import GraphExecutor

class NodeEditorWindow(QMainWindow):
    """
    The main window of the application, hosting the node graph editor.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("PySide6 Node Editor")
        self.setGeometry(200, 200, 1400, 900)

        self.graph = NodeGraph(self)
        self.view = NodeEditorView(self.graph, self)
        self.setCentralWidget(self.view)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        dock = QDockWidget("Output Log")
        dock.setWidget(self.output_log)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.executor = GraphExecutor(self.graph, self.output_log)

        self._create_actions()
        self._create_menus()
        self.create_default_nodes()

    def _create_actions(self):
        self.action_save = QAction("&Save Graph...", self)
        self.action_save.triggered.connect(self.on_save)
        self.action_load = QAction("&Load Graph...", self)
        self.action_load.triggered.connect(self.on_load)
        self.action_execute = QAction("&Execute Graph", self)
        self.action_execute.setShortcut("F5")
        self.action_execute.triggered.connect(self.on_execute)
        self.action_add_node = QAction("Add &Node...", self)
        self.action_add_node.triggered.connect(self.on_add_node)
        self.action_exit = QAction("E&xit", self)
        self.action_exit.triggered.connect(self.close)

    def _create_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_load)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.action_add_node)
        run_menu = menu_bar.addMenu("&Run")
        run_menu.addAction(self.action_execute)

    def create_default_nodes(self):
        """Create and connect a few example nodes to demonstrate functionality."""
        # --- Create Nodes ---
        node1 = self.graph.create_node("Number Generator", pos=(100, 300))
        node1.set_code("output_value: float = 42.5")

        node2 = self.graph.create_node("String Formatter", pos=(450, 300))
        node2.set_code(
            "input_number: float\n"
            "input_prefix: str = 'Result:'\n"
            "output_text: str = f'{input_prefix} {input_number * 2}'"
        )
        
        node3 = self.graph.create_node("Printer", pos=(800, 300))
        node3.set_code("input_message: str\nprint(input_message)")
        
        # --- Connect Nodes ---
        # Find the pins by their variable names
        start_pin1 = node1.get_pin_by_name("output_value")
        end_pin1 = node2.get_pin_by_name("input_number")
        
        start_pin2 = node2.get_pin_by_name("output_text")
        end_pin2 = node3.get_pin_by_name("input_message")

        # Create the connections
        if start_pin1 and end_pin1:
            self.graph.create_connection(start_pin1, end_pin1)
        
        if start_pin2 and end_pin2:
            self.graph.create_connection(start_pin2, end_pin2)

        self.graph.update()

    def on_add_node(self, scene_pos=None):
        title, ok = QInputDialog.getText(self, "Add Node", "Enter Node Title:")
        if ok and title:
            if not isinstance(scene_pos, QPointF):
                scene_pos = self.view.mapToScene(self.view.viewport().rect().center())
            node = self.graph.create_node(title, pos=(scene_pos.x(), scene_pos.y()))
            node.set_code("# Add your Python code here\n# e.g., input_x: int\n# output_y: int = input_x * 2")

    def on_save(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "JSON Files (*.json)")
        if file_path:
            data = self.graph.serialize()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            self.output_log.append(f"Graph saved to {file_path}")

    def on_load(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Graph", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.graph.deserialize(data)
            self.output_log.append(f"Graph loaded from {file_path}")
    
    def on_execute(self):
        self.output_log.clear()
        self.output_log.append("--- Execution Started ---")
        self.executor.execute()
        self.output_log.append("--- Execution Finished ---")

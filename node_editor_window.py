# node_editor_window.py
# The main application window.
# Now features a toolbar with a dedicated Run button for better UX.

import json
import os
from PySide6.QtWidgets import (QMainWindow, QMenuBar, QFileDialog, QTextEdit, 
                               QDockWidget, QInputDialog, QToolBar, QStyle)
from PySide6.QtGui import QAction, QFont
from PySide6.QtCore import Qt, QPointF
from node_graph import NodeGraph
from node_editor_view import NodeEditorView
from graph_executor import GraphExecutor
from environment_manager import EnvironmentManagerDialog

class NodeEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyFlowCanvas")
        self.setGeometry(100, 100, 1800, 1000)

        # --- Environment Configuration ---
        self.venv_path = os.path.abspath(os.path.join(os.getcwd(), ".venv_graph"))
        self.current_requirements = []

        self.graph = NodeGraph(self)
        self.view = NodeEditorView(self.graph, self)
        self.setCentralWidget(self.view)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        dock = QDockWidget("Output Log")
        dock.setWidget(self.output_log)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.executor = GraphExecutor(self.graph, self.output_log, self.get_venv_path)

        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        
        self.load_initial_graph("examples/text_adventure_graph.json")

    def get_venv_path(self):
        """Provides the current venv path to the executor."""
        return self.venv_path

    def _create_actions(self):
        self.action_save = QAction("&Save Graph...", self)
        self.action_save.triggered.connect(self.on_save)
        self.action_load = QAction("&Load Graph...", self)
        self.action_load.triggered.connect(self.on_load)
        self.action_manage_env = QAction("&Manage Environment...", self)
        self.action_manage_env.triggered.connect(self.on_manage_env)
        
        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.action_execute = QAction(icon, "&Execute Graph", self)
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
        run_menu.addAction(self.action_manage_env)
        run_menu.addAction(self.action_execute)
        
    def _create_toolbar(self):
        """Creates the main toolbar with the run button."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addAction(self.action_execute)

    def load_initial_graph(self, file_path):
        """Loads a specific graph from a JSON file on startup."""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.graph.deserialize(data)
                self.current_requirements = data.get('requirements', [])
                self.venv_path = data.get('venv_path', self.venv_path)
                self.output_log.append(f"Loaded default graph: {file_path}")
            except Exception as e:
                self.output_log.append(f"Error loading default graph '{file_path}': {e}")
        else:
            self.output_log.append(f"Default graph file not found: '{file_path}'. Starting with an empty canvas.")

    def on_manage_env(self):
        dialog = EnvironmentManagerDialog(self.venv_path, self.current_requirements, self)
        if dialog.exec():
            self.venv_path, self.current_requirements = dialog.get_results()
            self.output_log.append("Environment configuration updated.")

    def on_save(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "JSON Files (*.json)")
        if file_path:
            data = self.graph.serialize()
            data['requirements'] = self.current_requirements
            data['venv_path'] = self.venv_path
            with open(file_path, 'w') as f: json.dump(data, f, indent=4)
            self.output_log.append(f"Graph saved to {file_path}")

    def on_load(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Graph", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'r') as f: data = json.load(f)
            self.graph.deserialize(data)
            self.current_requirements = data.get('requirements', [])
            self.venv_path = data.get('venv_path', self.venv_path)
            self.output_log.append(f"Graph loaded from {file_path}")
            self.output_log.append("Dependencies loaded. Please verify the environment via the 'Run' menu.")
    
    def on_execute(self):
        self.output_log.clear()
        self.output_log.append("--- Execution Started ---")
        self.executor.execute()
        self.output_log.append("--- Execution Finished ---")

    def on_add_node(self, scene_pos=None):
        title, ok = QInputDialog.getText(self, "Add Node", "Enter Node Title:")
        if ok and title:
            if not isinstance(scene_pos, QPointF):
                scene_pos = self.view.mapToScene(self.view.viewport().rect().center())
            node = self.graph.create_node(title, pos=(scene_pos.x(), scene_pos.y()))
            node.set_code("from typing import Tuple\n\n"
                          "@node_entry\n"
                          "def node_function(input_1: str) -> Tuple[str, int]:\n"
                          "    return 'hello', len(input_1)")

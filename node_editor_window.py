# node_editor_window.py
# The main application window.
# Now correctly saves and restores the view's center point for robust panning.

import json
import os
from PySide6.QtWidgets import QMainWindow, QMenuBar, QFileDialog, QTextEdit, QDockWidget, QInputDialog, QToolBar, QStyle
from PySide6.QtGui import QAction, QFont, QTransform, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, QPointF, QSettings
from node_graph import NodeGraph
from node_editor_view import NodeEditorView
from graph_executor import GraphExecutor
from environment_manager import EnvironmentManagerDialog
from settings_dialog import SettingsDialog


def create_fa_icon(char_code, color="white"):
    """Creates a QIcon from a Font Awesome character code."""
    from PySide6.QtGui import QPixmap

    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    font = QFont("Font Awesome 6 Free Solid")
    font.setPixelSize(24)
    painter.setFont(font)
    painter.setPen(QColor(color))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, char_code)
    painter.end()
    return QIcon(pixmap)


class NodeEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyFlowCanvas")
        self.setGeometry(100, 100, 1800, 1000)

        # --- Settings and Environment Configuration ---
        self.settings = QSettings("PyFlowCanvas", "NodeEditor")
        self.venv_parent_dir = self.settings.value("venv_parent_dir", os.path.join(os.getcwd(), "venvs"))
        self.current_graph_name = "untitled"
        self.current_requirements = []
        self.current_file_path = None

        self.graph = NodeGraph(self)
        self.view = NodeEditorView(self.graph, self)
        self.setCentralWidget(self.view)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        dock = QDockWidget("Output Log")
        dock.setWidget(self.output_log)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.executor = GraphExecutor(self.graph, self.output_log, self.get_current_venv_path)

        self._create_actions()
        self._create_menus()
        self._create_toolbar()

        self.load_last_file()

    def get_current_venv_path(self):
        """Provides the full path to the venv for the current graph."""
        return os.path.join(self.venv_parent_dir, self.current_graph_name)

    def _create_actions(self):
        self.action_new = QAction(create_fa_icon("\uf15b"), "&New Scene", self)  # fa-file
        self.action_new.triggered.connect(self.on_new_scene)

        self.action_save = QAction(create_fa_icon("\uf0c7"), "&Save Graph...", self)  # fa-save
        self.action_save.triggered.connect(self.on_save)

        self.action_load = QAction(create_fa_icon("\uf07c"), "&Load Graph...", self)  # fa-folder-open
        self.action_load.triggered.connect(self.on_load)

        self.action_settings = QAction("Settings...", self)
        self.action_settings.triggered.connect(self.on_settings)

        self.action_manage_env = QAction("&Manage Environment...", self)
        self.action_manage_env.triggered.connect(self.on_manage_env)

        self.action_execute = QAction(create_fa_icon("\uf04b"), "&Execute Graph", self)  # fa-play
        self.action_execute.setShortcut("F5")
        self.action_execute.triggered.connect(self.on_execute)

        self.action_add_node = QAction("Add &Node...", self)
        self.action_add_node.triggered.connect(self.on_add_node)
        self.action_exit = QAction("E&xit", self)
        self.action_exit.triggered.connect(self.close)

    def _create_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.action_new)
        file_menu.addAction(self.action_load)
        file_menu.addAction(self.action_save)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.action_add_node)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_settings)
        run_menu = menu_bar.addMenu("&Run")
        run_menu.addAction(self.action_manage_env)
        run_menu.addAction(self.action_execute)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_load)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()
        toolbar.addAction(self.action_execute)

    def save_view_state(self):
        """Saves the current view's transform (zoom) and center point (pan) to QSettings."""
        if self.current_file_path:
            self.settings.beginGroup(f"view_state/{self.current_file_path}")
            self.settings.setValue("transform", self.view.transform())
            # Save the scene coordinates of the center of the view
            center_point = self.view.mapToScene(self.view.viewport().rect().center())
            self.settings.setValue("center_point", center_point)
            self.settings.endGroup()

    def load_view_state(self):
        """Loads and applies the view's transform and center point from QSettings."""
        if self.current_file_path:
            self.settings.beginGroup(f"view_state/{self.current_file_path}")
            transform_data = self.settings.value("transform")
            center_point = self.settings.value("center_point")
            self.settings.endGroup()

            if isinstance(transform_data, QTransform):
                self.view.setTransform(transform_data)

            if isinstance(center_point, QPointF):
                # Use centerOn to robustly set the pan position
                self.view.centerOn(center_point)

    def closeEvent(self, event):
        """Save the view state of the current file before closing."""
        self.save_view_state()
        event.accept()

    def load_last_file(self):
        last_file = self.settings.value("last_file_path", None)
        if last_file and os.path.exists(last_file):
            self.on_load(file_path=last_file)
        else:
            self.load_initial_graph("examples/text_adventure_graph_rerouted.json")

    def on_new_scene(self):
        self.save_view_state()
        self.graph.clear_graph()
        self.current_graph_name = "untitled"
        self.current_requirements = []
        self.current_file_path = None
        self.view.resetTransform()
        self.output_log.append("New scene created.")

    def load_initial_graph(self, file_path):
        if os.path.exists(file_path):
            self.on_load(file_path=file_path)
        else:
            self.output_log.append(f"Default graph file not found: '{file_path}'. Starting with an empty canvas.")

    def on_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.venv_parent_dir = self.settings.value("venv_parent_dir")
            self.output_log.append(f"Default venv directory updated to: {self.venv_parent_dir}")

    def on_manage_env(self):
        venv_path = self.get_current_venv_path()
        dialog = EnvironmentManagerDialog(venv_path, self.current_requirements, self)
        if dialog.exec():
            _, self.current_requirements = dialog.get_results()
            self.output_log.append("Environment requirements updated.")

    def on_save(self):
        if not self.current_file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph As...", "", "JSON Files (*.json)")
            if not file_path:
                return
            self.current_file_path = file_path

        self.current_graph_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        data = self.graph.serialize()
        data["requirements"] = self.current_requirements
        with open(self.current_file_path, "w") as f:
            json.dump(data, f, indent=4)
        self.settings.setValue("last_file_path", self.current_file_path)
        self.output_log.append(f"Graph saved to {self.current_file_path}")

    def on_load(self, file_path=None):
        if not file_path:
            self.save_view_state()
            file_path, _ = QFileDialog.getOpenFileName(self, "Load Graph", "", "JSON Files (*.json)")

        if file_path and os.path.exists(file_path):
            self.current_file_path = file_path
            self.current_graph_name = os.path.splitext(os.path.basename(file_path))[0]
            with open(file_path, "r") as f:
                data = json.load(f)
            self.graph.deserialize(data)
            self.current_requirements = data.get("requirements", [])
            self.settings.setValue("last_file_path", file_path)
            self.load_view_state()
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
            node.set_code("from typing import Tuple\n\n" "@node_entry\n" "def node_function(input_1: str) -> Tuple[str, int]:\n" "    return 'hello', len(input_1)")

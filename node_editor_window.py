# node_editor_window.py
# The main application window - refactored for better maintainability

import os
from PySide6.QtWidgets import (QMainWindow, QTextEdit, QDockWidget, QInputDialog, 
                              QToolBar, QWidget, QHBoxLayout)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPointF, QSettings

from node_graph import NodeGraph
from node_editor_view import NodeEditorView
from environment_manager import EnvironmentManagerDialog
from settings_dialog import SettingsDialog

# Import our new modular components
from ui_utils import create_fa_icon, create_execution_control_widget
from file_operations import FileOperationsManager
from execution_controller import ExecutionController
from view_state_manager import ViewStateManager


class NodeEditorWindow(QMainWindow):
    """Main application window for PyFlowGraph node editor."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(100, 100, 1800, 1000)

        # Initialize core components
        self._setup_core_components()
        self._setup_ui()
        self._setup_managers()
        
        # Load initial state
        self.file_ops.load_last_file()

    def _setup_core_components(self):
        """Initialize the core graph and view components."""
        self.settings = QSettings("PyFlowGraph", "NodeEditor")
        self.venv_parent_dir = self.settings.value("venv_parent_dir", os.path.join(os.getcwd(), "venvs"))
        
        # Core graph components
        self.graph = NodeGraph(self)
        self.view = NodeEditorView(self.graph, self)
        self.setCentralWidget(self.view)

        # Output log
        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        dock = QDockWidget("Output Log")
        dock.setWidget(self.output_log)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def _setup_ui(self):
        """Setup the user interface elements."""
        self._create_actions()
        self._create_menus()
        self._create_toolbar()

    def _setup_managers(self):
        """Initialize the manager components."""
        # File operations manager
        self.file_ops = FileOperationsManager(self, self.graph, self.output_log)
        
        # View state manager
        self.view_state = ViewStateManager(self.view, self.file_ops)
        
        # Execution controller (initialized after toolbar creation)
        self.execution_ctrl = ExecutionController(
            self.graph, 
            self.output_log, 
            self._get_current_venv_path,
            self.exec_widget.main_exec_button,
            self.exec_widget.status_label
        )

    def _get_current_venv_path(self):
        """Provides the full path to the venv for the current graph."""
        return self.file_ops.get_current_venv_path(self.venv_parent_dir)

    def _create_actions(self):
        """Create all the action objects for menus and toolbars."""
        self.action_new = QAction(create_fa_icon("\uf15b", "lightblue"), "&New Scene", self)
        self.action_new.triggered.connect(self.on_new_scene)

        self.action_save = QAction(create_fa_icon("\uf0c7", "orange"), "&Save Graph...", self)
        self.action_save.triggered.connect(self.on_save)

        self.action_save_as = QAction(create_fa_icon("\uf0c5", "orange"), "Save &As...", self)
        self.action_save_as.triggered.connect(self.on_save_as)

        self.action_load = QAction(create_fa_icon("\uf07c", "yellow"), "&Load Graph...", self)
        self.action_load.triggered.connect(self.on_load)

        self.action_settings = QAction("Settings...", self)
        self.action_settings.triggered.connect(self.on_settings)

        self.action_manage_env = QAction("&Manage Environment...", self)
        self.action_manage_env.triggered.connect(self.on_manage_env)

        self.action_add_node = QAction("Add &Node...", self)
        self.action_add_node.triggered.connect(self.on_add_node)
        
        self.action_exit = QAction("E&xit", self)
        self.action_exit.triggered.connect(self.close)

    def _create_menus(self):
        """Create the menu bar and menus."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.action_new)
        file_menu.addAction(self.action_load)
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.action_add_node)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_settings)
        
        # Run menu
        run_menu = menu_bar.addMenu("&Run")
        run_menu.addAction(self.action_manage_env)

    def _create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # File operations
        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_load)
        toolbar.addAction(self.action_save)
        toolbar.addAction(self.action_save_as)
        toolbar.addSeparator()

        # Create execution control widget
        self.exec_widget = create_execution_control_widget(
            self._on_mode_changed,
            self._on_main_button_clicked
        )
        toolbar.addWidget(self.exec_widget)

    def _on_mode_changed(self, mode_id):
        """Handle execution mode changes."""
        self.execution_ctrl.on_mode_changed(mode_id)

    def _on_main_button_clicked(self):
        """Handle main execution button clicks."""
        self.execution_ctrl.on_main_button_clicked()

    # File operation handlers
    def on_new_scene(self):
        """Create a new scene."""
        self.view_state.save_view_state()
        self.file_ops.new_scene()
        self.view.resetTransform()

    def on_save(self):
        """Save the current graph."""
        self.file_ops.save()

    def on_save_as(self):
        """Save the current graph with a new filename."""
        self.file_ops.save_as()

    def on_load(self, file_path=None):
        """Load a graph from file."""
        if not file_path:
            self.view_state.save_view_state()
        
        if self.file_ops.load(file_path):
            self.view_state.load_view_state()

    # Settings and environment handlers
    def on_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.venv_parent_dir = self.settings.value("venv_parent_dir")
            self.output_log.append(f"Default venv directory updated to: {self.venv_parent_dir}")

    def on_manage_env(self):
        """Open the environment manager dialog."""
        venv_path = self._get_current_venv_path()
        dialog = EnvironmentManagerDialog(venv_path, self.file_ops.current_requirements, self)
        if dialog.exec():
            _, self.file_ops.current_requirements = dialog.get_results()
            self.output_log.append("Environment requirements updated.")

    def on_add_node(self, scene_pos=None):
        """Add a new node to the graph."""
        title, ok = QInputDialog.getText(self, "Add Node", "Enter Node Title:")
        if ok and title:
            if not isinstance(scene_pos, QPointF):
                scene_pos = self.view.mapToScene(self.view.viewport().rect().center())
            node = self.graph.create_node(title, pos=(scene_pos.x(), scene_pos.y()))
            node.set_code("from typing import Tuple\n\n" "@node_entry\n" 
                         "def node_function(input_1: str) -> Tuple[str, int]:\n" 
                         "    return 'hello', len(input_1)")

    def closeEvent(self, event):
        """Handle application close event."""
        self.view_state.save_view_state()
        event.accept()
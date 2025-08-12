# node_editor_window.py
# The main application window.
# Now correctly saves and restores the view's center point for robust panning.

import json
import os
from PySide6.QtWidgets import QMainWindow, QMenuBar, QFileDialog, QTextEdit, QDockWidget, QInputDialog, QToolBar, QStyle, QWidget, QHBoxLayout, QRadioButton, QPushButton, QButtonGroup, QLabel
from PySide6.QtGui import QAction, QFont, QTransform, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, QPointF, QSettings
from node_graph import NodeGraph
from node_editor_view import NodeEditorView
from graph_executor import GraphExecutor
from event_system import LiveGraphExecutor
from environment_manager import EnvironmentManagerDialog
from settings_dialog import SettingsDialog


def create_fa_icon(char_code, color="white", font_style="regular"):
    """Creates a QIcon from a Font Awesome character code."""
    from PySide6.QtGui import QPixmap

    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    
    if font_style == "solid":
        font = QFont("Font Awesome 6 Free Solid")
    else:
        font = QFont("Font Awesome 7 Free Regular")
    
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

        # Dual execution system: batch (traditional) and live (interactive)
        self.executor = GraphExecutor(self.graph, self.output_log, self.get_current_venv_path)
        self.live_executor = LiveGraphExecutor(self.graph, self.output_log, self.get_current_venv_path)
        self.live_mode = False
        self.live_active = False  # Whether live mode is currently active

        self._create_actions()
        self._create_menus()
        self._create_toolbar()

        self.load_last_file()

    def get_current_venv_path(self):
        """Provides the full path to the venv for the current graph."""
        return os.path.join(self.venv_parent_dir, self.current_graph_name)

    def _create_actions(self):
        self.action_new = QAction(create_fa_icon("\uf15b", "lightblue"), "&New Scene", self)  # fa-file
        self.action_new.triggered.connect(self.on_new_scene)

        self.action_save = QAction(create_fa_icon("\uf0c7", "orange"), "&Save Graph...", self)  # fa-save
        self.action_save.triggered.connect(self.on_save)

        self.action_save_as = QAction(create_fa_icon("\uf0c5", "orange"), "Save &As...", self)  # fa-copy
        self.action_save_as.triggered.connect(self.on_save_as)

        self.action_load = QAction(create_fa_icon("\uf07c", "yellow"), "&Load Graph...", self)  # fa-folder-open
        self.action_load.triggered.connect(self.on_load)

        self.action_settings = QAction("Settings...", self)
        self.action_settings.triggered.connect(self.on_settings)

        self.action_manage_env = QAction("&Manage Environment...", self)
        self.action_manage_env.triggered.connect(self.on_manage_env)

        # Remove old execution actions - we'll use custom widgets instead

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
        file_menu.addAction(self.action_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.action_add_node)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_settings)
        run_menu = menu_bar.addMenu("&Run")
        run_menu.addAction(self.action_manage_env)
        run_menu.addSeparator()
        # Execution controls are now in toolbar only for better UX

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # File operations
        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_load)
        toolbar.addAction(self.action_save)
        toolbar.addAction(self.action_save_as)
        toolbar.addSeparator()
        
        # Create execution control widget
        self._create_execution_controls(toolbar)

    def _create_execution_controls(self, toolbar):
        """Create the execution mode and control widget."""
        # Container widget
        exec_widget = QWidget()
        layout = QHBoxLayout(exec_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Mode selection label
        mode_label = QLabel("Execution Mode:")
        mode_label.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        layout.addWidget(mode_label)
        
        # Radio buttons for mode selection
        self.mode_button_group = QButtonGroup()
        
        self.batch_radio = QRadioButton("Batch")
        self.batch_radio.setToolTip("Traditional one-shot execution of entire graph")
        self.batch_radio.setChecked(True)  # Default mode
        self.batch_radio.setStyleSheet("""
            QRadioButton { color: #E0E0E0; font-weight: bold; }
            QRadioButton::indicator::checked { background-color: #4CAF50; }
        """)
        
        self.live_radio = QRadioButton("Live")
        self.live_radio.setToolTip("Interactive mode with event-driven execution")
        self.live_radio.setStyleSheet("""
            QRadioButton { color: #E0E0E0; font-weight: bold; }
            QRadioButton::indicator::checked { background-color: #FF9800; }
        """)
        
        self.mode_button_group.addButton(self.batch_radio, 0)
        self.mode_button_group.addButton(self.live_radio, 1)
        self.mode_button_group.idClicked.connect(self.on_mode_changed)
        
        layout.addWidget(self.batch_radio)
        layout.addWidget(self.live_radio)
        
        # Separator
        separator = QLabel("|")
        separator.setStyleSheet("color: #666; font-size: 16px;")
        layout.addWidget(separator)
        
        # Main execution button - changes based on mode
        self.main_exec_button = QPushButton("▶️ Execute Graph")
        self.main_exec_button.setMinimumSize(140, 35)
        self.main_exec_button.setStyleSheet(self._get_button_style("batch"))
        self.main_exec_button.clicked.connect(self.on_main_button_clicked)
        self.main_exec_button.setShortcut("F5")
        layout.addWidget(self.main_exec_button)
        
        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Add to toolbar
        toolbar.addWidget(exec_widget)
    
    def _get_button_style(self, mode, state="ready"):
        """Get stylesheet for the main button based on mode and state."""
        if mode == "batch":
            if state == "ready":
                return """
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                    QPushButton:pressed {
                        background-color: #3d8b40;
                    }
                """
            else:  # executing
                return """
                    QPushButton {
                        background-color: #607D8B;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                """
        else:  # live mode
            if state == "ready":
                return """
                    QPushButton {
                        background-color: #FF9800;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #F57C00;
                    }
                    QPushButton:pressed {
                        background-color: #E65100;
                    }
                """
            elif state == "active":
                return """
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """
            else:  # paused
                return """
                    QPushButton {
                        background-color: #F44336;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #da190b;
                    }
                """

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

    def on_save_as(self):
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

    def on_mode_changed(self, mode_id):
        """Handle radio button change between Batch (0) and Live (1) modes."""
        self.live_mode = (mode_id == 1)
        self.output_log.clear()
        
        if self.live_mode:
            # Switch to live mode
            self.live_executor.set_live_mode(True)
            self.live_active = False
            self.main_exec_button.setText("🔥 Start Live Mode")
            self.main_exec_button.setStyleSheet(self._get_button_style("live", "ready"))
            self.status_label.setText("Live Ready")
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
            
            self.output_log.append("🎯 === LIVE MODE SELECTED ===")
            self.output_log.append("📋 Click 'Start Live Mode' to activate interactive execution")
            self.output_log.append("💡 Then use buttons inside nodes to control flow!")
        else:
            # Switch to batch mode
            self.live_executor.set_live_mode(False)
            self.live_active = False
            self.main_exec_button.setText("▶️ Execute Graph")
            self.main_exec_button.setStyleSheet(self._get_button_style("batch", "ready"))
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            self.output_log.append("📦 === BATCH MODE SELECTED ===")
            self.output_log.append("Click 'Execute Graph' to run entire graph at once")

    def on_main_button_clicked(self):
        """Handle the main execution button based on current mode and state."""
        if not self.live_mode:
            # Batch mode execution
            self._execute_batch_mode()
        else:
            # Live mode - toggle between start/pause
            if not self.live_active:
                self._start_live_mode()
            else:
                self._pause_live_mode()
    
    def _execute_batch_mode(self):
        """Execute graph in batch mode."""
        self.output_log.clear()
        self.output_log.append("▶️ === BATCH EXECUTION STARTED ===")
        
        # Update button state during execution
        self.main_exec_button.setText("⏳ Executing...")
        self.main_exec_button.setStyleSheet(self._get_button_style("batch", "executing"))
        self.status_label.setText("Executing")
        self.status_label.setStyleSheet("color: #607D8B; font-weight: bold;")
        
        try:
            self.executor.execute()
            self.output_log.append("✅ === BATCH EXECUTION FINISHED ===")
        except Exception as e:
            self.output_log.append(f"❌ === EXECUTION FAILED: {e} ===")
        finally:
            # Restore button state
            self.main_exec_button.setText("▶️ Execute Graph")
            self.main_exec_button.setStyleSheet(self._get_button_style("batch", "ready"))
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
    
    def _start_live_mode(self):
        """Start live interactive mode."""
        self.output_log.clear()
        self.output_log.append("🔥 === LIVE MODE ACTIVATED ===")
        self.output_log.append("✨ Interactive execution enabled!")
        self.output_log.append("🎮 Click buttons inside nodes to trigger execution")
        self.output_log.append("📋 Graph state has been reset and is ready for interaction")
        
        self.live_active = True
        self.live_executor.restart_graph()
        
        # Update button to pause state
        self.main_exec_button.setText("⏸️ Pause Live Mode") 
        self.main_exec_button.setStyleSheet(self._get_button_style("live", "active"))
        self.status_label.setText("Live Active")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
    
    def _pause_live_mode(self):
        """Pause live mode."""
        self.live_active = False
        self.live_executor.set_live_mode(False)
        
        self.main_exec_button.setText("🔥 Resume Live Mode")
        self.main_exec_button.setStyleSheet(self._get_button_style("live", "paused"))
        self.status_label.setText("Live Paused")
        self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")
        
        self.output_log.append("⏸️ Live mode paused - node buttons are now inactive")
        self.output_log.append("Click 'Resume Live Mode' to reactivate")

    def on_add_node(self, scene_pos=None):
        title, ok = QInputDialog.getText(self, "Add Node", "Enter Node Title:")
        if ok and title:
            if not isinstance(scene_pos, QPointF):
                scene_pos = self.view.mapToScene(self.view.viewport().rect().center())
            node = self.graph.create_node(title, pos=(scene_pos.x(), scene_pos.y()))
            node.set_code("from typing import Tuple\n\n" "@node_entry\n" "def node_function(input_1: str) -> Tuple[str, int]:\n" "    return 'hello', len(input_1)")

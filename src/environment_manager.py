# environment_manager.py
# A comprehensive system for managing a dedicated virtual environment for graph execution.
# This version contains the definitive fix for venv creation in a compiled application.

import os
import sys
import subprocess
import venv
from PySide6.QtCore import QObject, Signal, QThread, Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                              QDialogButtonBox, QLineEdit, QFileDialog, QListWidget, QListWidgetItem, 
                              QMenu, QTabWidget, QWidget, QTreeWidget, QTreeWidgetItem, QSplitter, 
                              QGroupBox, QMessageBox)
from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction, QGuiApplication


class ClickableLabel(QLineEdit):
    """A read-only QLineEdit styled as a label that supports right-click to copy."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(lambda: QGuiApplication.clipboard().setText(self.text()))
        menu.addAction(copy_action)
        menu.exec(self.mapToGlobal(pos))


class EnvironmentWorker(QObject):
    """
    Worker to run environment tasks (creation, installation, verification) in a thread.
    """

    finished = Signal(bool, str)
    progress = Signal(str)

    def __init__(self, venv_path, requirements, task="setup"):
        super().__init__()
        self.venv_path = venv_path
        self.requirements = requirements
        self.task = task

    def get_venv_python_executable(self):
        """Gets the path to the python executable inside the created venv."""
        if sys.platform == "win32":
            return os.path.join(self.venv_path, "Scripts", "python.exe")
        else:
            return os.path.join(self.venv_path, "bin", "python")

    def run(self):
        try:
            if self.task == "setup":
                self.run_setup()
            elif self.task == "verify":
                self.run_verify()
        except Exception as e:
            self.finished.emit(False, f"An unexpected error occurred: {e}")

    def run_setup(self):
        self.progress.emit("--- STARTING SETUP PROCESS ---")

        if not os.path.exists(self.venv_path):
            self.progress.emit(f"Target venv path does not exist: {self.venv_path}")
            self.progress.emit("Attempting to create new virtual environment...")

            # --- Definitive Fix ---
            # Instead of relying on a potentially faulty is_frozen() check, we will
            # determine the execution mode by looking for the bundled python_runtime.
            base_path = os.path.dirname(sys.executable)
            runtime_python_home = os.path.join(base_path, "python_runtime")
            runtime_python_exe = os.path.join(runtime_python_home, "python.exe")

            self.progress.emit(f"DEBUG: sys.executable is: {sys.executable}")
            self.progress.emit(f"DEBUG: Base path determined as: {base_path}")
            self.progress.emit(f"DEBUG: Checking for runtime at: {runtime_python_home}")

            if os.path.exists(runtime_python_home):
                # If the runtime folder exists, we are in a compiled environment.
                self.progress.emit("INFO: 'python_runtime' folder found. Running in COMPILED mode.")

                if not os.path.exists(runtime_python_exe):
                    self.progress.emit(f"CRITICAL FAILURE: Bundled Python not found at '{runtime_python_exe}'.")
                    self.finished.emit(False, f"Bundled Python runtime not found at '{runtime_python_exe}'.")
                    return
                self.progress.emit("DEBUG: Bundled python.exe found.")

                cmd = [runtime_python_exe, "-m", "venv", self.venv_path]
                self.progress.emit(f"DEBUG: Subprocess command to run: {cmd}")

                # No need to set cwd, as we use an absolute path to the executable.
                result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)

                if result.returncode != 0:
                    self.progress.emit(f"ERROR: Subprocess failed with return code {result.returncode}.")
                    self.progress.emit(f"ERROR STDOUT: {result.stdout}")
                    self.progress.emit(f"ERROR STDERR: {result.stderr}")
                    self.finished.emit(False, f"Failed to create venv. See log for details.")
                    return
                self.progress.emit("INFO: Subprocess to create venv completed successfully.")
            else:
                # If the runtime folder does not exist, we are in a development environment.
                self.progress.emit("INFO: 'python_runtime' folder not found. Running in SCRIPT mode.")
                venv.create(self.venv_path, with_pip=True)

        venv_python_exe = self.get_venv_python_executable()
        self.progress.emit(f"DEBUG: Using venv python executable for pip: {venv_python_exe}")
        if not self.requirements:
            self.finished.emit(True, "Environment exists. No packages to install.")
            return

        self.progress.emit(f"Installing {len(self.requirements)} dependencies...")
        cmd = [venv_python_exe, "-m", "pip", "install"] + self.requirements
        self.progress.emit(f"DEBUG: Pip install command: {cmd}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
        for line in iter(process.stdout.readline, ""):
            self.progress.emit(line.strip())
        process.wait()

        if process.returncode == 0:
            self.finished.emit(True, "Environment setup complete.")
        else:
            self.finished.emit(False, "Failed to install one or more packages.")

    def run_verify(self):
        self.progress.emit("Starting verification...")
        venv_python_exe = self.get_venv_python_executable()
        if not os.path.exists(venv_python_exe):
            self.finished.emit(False, "Verification Failed: Virtual environment not found.")
            return

        self.progress.emit("Virtual environment found.")
        if not self.requirements:
            self.finished.emit(True, "Verification Succeeded: No packages required.")
            return

        self.progress.emit("Checking installed packages...")
        cmd = [venv_python_exe, "-m", "pip", "freeze"]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode != 0:
            self.finished.emit(False, "Verification Failed: Could not list installed packages.")
            return

        installed_packages = {line.split("==")[0].lower() for line in result.stdout.splitlines()}
        missing_packages = [req for req in self.requirements if req.split("==")[0].lower() not in installed_packages]

        if not missing_packages:
            self.finished.emit(True, f"Verification Succeeded: All {len(self.requirements)} packages are installed.")
        else:
            self.finished.emit(False, f"Verification Failed: Missing packages: {', '.join(missing_packages)}")


class EnvironmentManagerDialog(QDialog):
    def __init__(self, venv_path, requirements, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Execution Environment Manager")
        self.setMinimumSize(750, 600)

        self.initial_venv_path = venv_path
        self.requirements = requirements.copy()
        self.settings = QSettings("PyFlowGraph", "NodeEditor")

        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_current_environment_tab()
        self._create_saved_environments_tab()
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _create_current_environment_tab(self):
        """Create the tab for managing the current graph's environment."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Environment Path:"))
        self.path_edit = QLineEdit(self.initial_venv_path)
        path_layout.addWidget(self.path_edit)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_button)
        
        # Add "Use Default" button
        default_button = QPushButton("Use Default")
        default_button.clicked.connect(self.use_default_environment)
        path_layout.addWidget(default_button)
        
        layout.addLayout(path_layout)

        layout.addWidget(QLabel("Graph Python Dependencies:"))
        self.reqs_list = QListWidget()
        self.reqs_list.addItems(self.requirements)
        layout.addWidget(self.reqs_list)

        req_edit_layout = QHBoxLayout()
        self.req_input = QLineEdit()
        self.req_input.setPlaceholderText("e.g., requests==2.28.1 or numpy")
        req_edit_layout.addWidget(self.req_input)
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_requirement)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_requirement)
        req_edit_layout.addWidget(add_button)
        req_edit_layout.addWidget(remove_button)
        layout.addLayout(req_edit_layout)

        action_layout = QHBoxLayout()
        self.setup_button = QPushButton("Create / Update Environment")
        self.setup_button.clicked.connect(self.run_task_setup)
        self.verify_button = QPushButton("Verify Environment")
        self.verify_button.clicked.connect(self.run_task_verify)
        action_layout.addWidget(self.setup_button)
        action_layout.addWidget(self.verify_button)
        layout.addLayout(action_layout)

        self.status_display = ClickableLabel("Status: Ready")
        layout.addWidget(self.status_display)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        layout.addWidget(self.output_log)

        self.tab_widget.addTab(tab, "Current Environment")
        self.update_status_color(None)

    def _create_saved_environments_tab(self):
        """Create the tab for managing saved environment configurations."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header_label = QLabel("Saved Environment Configurations")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 2px; padding: 4px;")
        header_label.setMaximumHeight(30)
        layout.addWidget(header_label)
        
        # Create splitter for list and details
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side: Environment list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        list_layout.addWidget(QLabel("Saved Graphs:"))
        self.saved_envs_list = QListWidget()
        self.saved_envs_list.itemSelectionChanged.connect(self._on_saved_env_selected)
        list_layout.addWidget(self.saved_envs_list)
        
        # Buttons for list management
        list_buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_saved_environments)
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self._delete_saved_environment)
        self.delete_button.setEnabled(False)
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self._clear_all_saved_environments)
        
        list_buttons_layout.addWidget(self.refresh_button)
        list_buttons_layout.addWidget(self.delete_button)
        list_buttons_layout.addWidget(self.clear_all_button)
        list_layout.addLayout(list_buttons_layout)
        
        splitter.addWidget(list_widget)
        
        # Right side: Details panel
        details_group = QGroupBox("Environment Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_graph_name = QLabel("Graph: (none selected)")
        self.details_env_type = QLabel("Type: -")
        self.details_env_path = QLabel("Path: -")
        self.details_env_status = QLabel("Status: -")
        
        details_layout.addWidget(self.details_graph_name)
        details_layout.addWidget(self.details_env_type)
        details_layout.addWidget(self.details_env_path)
        details_layout.addWidget(self.details_env_status)
        
        # Edit button
        self.edit_button = QPushButton("Edit Environment Choice")
        self.edit_button.clicked.connect(self._edit_saved_environment)
        self.edit_button.setEnabled(False)
        details_layout.addWidget(self.edit_button)
        
        details_layout.addStretch()
        splitter.addWidget(details_group)
        
        # Set splitter proportions
        splitter.setSizes([300, 400])
        
        self.tab_widget.addTab(tab, "Saved Environments")
        
        # Load saved environments
        self._refresh_saved_environments()

    def update_status_color(self, status):
        """Updates the status display's background color."""
        style = "color: white; padding: 4px; border-radius: 4px; border: 1px solid #2E2E2E;"
        if status is None:
            self.status_display.setStyleSheet(f"background-color: #5A5A5A; {style}")
        elif status == "running":
            self.status_display.setStyleSheet(f"background-color: #3A5A8A; {style}")
        elif status is True:
            self.status_display.setStyleSheet(f"background-color: #3A6A3A; {style}")
        elif status is False:
            self.status_display.setStyleSheet(f"background-color: #8A3A3A; {style}")

    def browse_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Environment Parent Directory")
        if directory:
            self.path_edit.setText(os.path.join(directory, ".venv_graph"))
    
    def use_default_environment(self):
        """Set the path to use the default environment."""
        # Get the parent directory and set to default
        parent_dir = os.path.dirname(self.initial_venv_path)
        default_path = os.path.join(parent_dir, "default")
        self.path_edit.setText(default_path)
        self.status_display.setText("Status: Switched to default environment (venvs/default)")
        self.update_status_color(None)

    def add_requirement(self):
        req = self.req_input.text().strip()
        if req and req not in self.requirements:
            self.requirements.append(req)
            self.reqs_list.addItem(req)
            self.req_input.clear()

    def remove_requirement(self):
        selected_items = self.reqs_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.requirements.remove(item.text())
            self.reqs_list.takeItem(self.reqs_list.row(item))

    def run_task_setup(self):
        self.run_task("setup")

    def run_task_verify(self):
        self.run_task("verify")

    def run_task(self, task_name):
        self.setup_button.setEnabled(False)
        self.verify_button.setEnabled(False)
        self.output_log.clear()
        self.status_display.setText(f"Status: Running {task_name}...")
        self.update_status_color("running")

        self.worker = EnvironmentWorker(self.path_edit.text(), self.requirements, task_name)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.output_log.append)
        self.worker.finished.connect(self.on_finished)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_finished(self, success, message):
        self.status_display.setText(f"Status: {message}")
        self.update_status_color(success)
        self.setup_button.setEnabled(True)
        self.verify_button.setEnabled(True)
        self.thread.quit()
        self.thread.wait()

    def get_results(self):
        return self.path_edit.text(), self.requirements
    
    def _refresh_saved_environments(self):
        """Load and display all saved environment configurations from QSettings."""
        self.saved_envs_list.clear()
        
        # Get all keys that start with "graph_env_choice/"
        all_keys = self.settings.allKeys()
        env_keys = [key for key in all_keys if key.startswith("graph_env_choice/")]
        
        if not env_keys:
            item = QListWidgetItem("No saved environments found")
            item.setData(Qt.UserRole, None)
            self.saved_envs_list.addItem(item)
            return
        
        for key in sorted(env_keys):
            graph_name = key.replace("graph_env_choice/", "")
            env_choice = self.settings.value(key)
            
            # Create display text
            display_text = f"{graph_name} → {self._get_env_type_display(env_choice)}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, {"graph_name": graph_name, "env_choice": env_choice, "key": key})
            self.saved_envs_list.addItem(item)
    
    def _get_env_type_display(self, env_choice):
        """Convert environment choice to display text."""
        if env_choice == "default":
            return "Default (venvs/default)"
        elif env_choice == "graph_specific":
            return "Graph-specific"
        elif env_choice == "existing":
            return "Existing"
        else:
            return f"Unknown ({env_choice})"
    
    def _get_env_path(self, graph_name, env_choice):
        """Get the full path for an environment choice."""
        # Determine project root directory (same logic as node_editor_window.py)
        if os.path.basename(os.getcwd()) == "src":
            # Development mode - go up one level from src/
            project_root = os.path.dirname(os.getcwd())
        else:
            # Compiled mode - use current directory
            project_root = os.getcwd()
        
        default_venv_dir = os.path.join(project_root, "venvs")
        venv_parent = self.settings.value("venv_parent_dir", default_venv_dir)
        
        if env_choice == "default":
            return os.path.join(venv_parent, "default")
        else:
            return os.path.join(venv_parent, graph_name)
    
    def _check_env_exists(self, env_path):
        """Check if the environment path exists and is valid."""
        if not os.path.exists(env_path):
            return False, "Path does not exist"
        
        # Check for Python executable
        if os.name == 'nt':  # Windows
            python_exe = os.path.join(env_path, "Scripts", "python.exe")
        else:  # Unix/Linux/Mac
            python_exe = os.path.join(env_path, "bin", "python")
        
        if not os.path.exists(python_exe):
            return False, "Invalid environment (missing Python)"
        
        return True, "Valid environment"
    
    def _on_saved_env_selected(self):
        """Handle selection change in saved environments list."""
        selected_items = self.saved_envs_list.selectedItems()
        if not selected_items:
            self._clear_details()
            return
        
        item = selected_items[0]
        data = item.data(Qt.UserRole)
        
        if not data:
            self._clear_details()
            return
        
        graph_name = data["graph_name"]
        env_choice = data["env_choice"]
        env_path = self._get_env_path(graph_name, env_choice)
        exists, status = self._check_env_exists(env_path)
        
        # Update details panel
        self.details_graph_name.setText(f"Graph: {graph_name}")
        self.details_env_type.setText(f"Type: {self._get_env_type_display(env_choice)}")
        self.details_env_path.setText(f"Path: {env_path}")
        
        if exists:
            self.details_env_status.setText(f"Status: ✅ {status}")
            self.details_env_status.setStyleSheet("color: green;")
        else:
            self.details_env_status.setText(f"Status: ❌ {status}")
            self.details_env_status.setStyleSheet("color: red;")
        
        # Enable buttons
        self.delete_button.setEnabled(True)
        self.edit_button.setEnabled(True)
    
    def _clear_details(self):
        """Clear the details panel."""
        self.details_graph_name.setText("Graph: (none selected)")
        self.details_env_type.setText("Type: -")
        self.details_env_path.setText("Path: -")
        self.details_env_status.setText("Status: -")
        self.details_env_status.setStyleSheet("")
        
        self.delete_button.setEnabled(False)
        self.edit_button.setEnabled(False)
    
    def _delete_saved_environment(self):
        """Delete the selected saved environment configuration."""
        selected_items = self.saved_envs_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        data = item.data(Qt.UserRole)
        
        if not data:
            return
        
        graph_name = data["graph_name"]
        key = data["key"]
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Delete Environment Configuration",
            f"Are you sure you want to delete the saved environment configuration for '{graph_name}'?\n\n"
            f"This will not delete the actual environment, but the graph will prompt for environment selection on next load.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings.remove(key)
            self._refresh_saved_environments()
            self._clear_details()
    
    def _clear_all_saved_environments(self):
        """Clear all saved environment configurations."""
        # Get count for confirmation
        all_keys = self.settings.allKeys()
        env_keys = [key for key in all_keys if key.startswith("graph_env_choice/")]
        
        if not env_keys:
            QMessageBox.information(self, "No Configurations", "No saved environment configurations to clear.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Clear All Environment Configurations", 
            f"Are you sure you want to clear all {len(env_keys)} saved environment configurations?\n\n"
            f"This will not delete actual environments, but all graphs will prompt for environment selection on next load.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for key in env_keys:
                self.settings.remove(key)
            self._refresh_saved_environments()
            self._clear_details()
    
    def _edit_saved_environment(self):
        """Edit the selected saved environment configuration."""
        selected_items = self.saved_envs_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        data = item.data(Qt.UserRole)
        
        if not data:
            return
        
        graph_name = data["graph_name"]
        current_choice = data["env_choice"]
        key = data["key"]
        
        # Simple dialog to change environment choice
        from environment_selection_dialog import EnvironmentSelectionDialog
        
        dialog = EnvironmentSelectionDialog(graph_name, self)
        
        # Set current selection based on saved choice
        if current_choice == "default":
            dialog.selected_option = "default"
        elif current_choice == "graph_specific":
            dialog.selected_option = "graph_specific"
        elif current_choice == "existing":
            dialog.selected_option = "existing"
        
        if dialog.exec():
            new_choice = dialog.get_selected_option()
            self.settings.setValue(key, new_choice)
            self._refresh_saved_environments()
            
            # Try to reselect the same item
            for i in range(self.saved_envs_list.count()):
                item = self.saved_envs_list.item(i)
                item_data = item.data(Qt.UserRole)
                if item_data and item_data["graph_name"] == graph_name:
                    self.saved_envs_list.setCurrentItem(item)
                    break

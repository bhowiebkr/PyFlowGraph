# environment_manager.py
# A comprehensive system for managing a dedicated virtual environment for graph execution.
# This version contains the definitive fix for venv creation in a compiled application.

import os
import sys
import subprocess
import venv
from PySide6.QtCore import QObject, Signal, QThread, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QDialogButtonBox, QLineEdit, QFileDialog, QListWidget, QListWidgetItem, QMenu
from PySide6.QtGui import QAction, QGuiApplication


def is_frozen():
    """Checks if the application is running as a frozen (e.g., Nuitka) executable."""
    return getattr(sys, "frozen", False)


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
        """Creates the venv and installs packages."""
        if not os.path.exists(self.venv_path):
            self.progress.emit(f"Creating virtual environment at: {self.venv_path}")

            if is_frozen():
                # --- Definitive Fix for Frozen Apps ---
                # The standard 'venv' module fails when run from a compiled exe.
                # We must create the venv structure manually.
                base_path = os.path.dirname(sys.executable)
                runtime_python_home = os.path.join(base_path, "python_runtime")

                if not os.path.exists(os.path.join(runtime_python_home, "python.exe")):
                    self.finished.emit(False, f"Bundled Python runtime not found at '{runtime_python_home}'.")
                    return

                # 1. Create the builder without pip to avoid the failing 'ensurepip' call.
                builder = venv.EnvBuilder(with_pip=False)
                builder.create(self.venv_path)

                # 2. Overwrite the incorrect pyvenv.cfg file.
                # This is the most critical step. It tells the new venv where to find
                # the full Python installation (our bundled runtime).
                cfg_path = os.path.join(self.venv_path, "pyvenv.cfg")
                with open(cfg_path, "w") as f:
                    f.write(f"home = {runtime_python_home}\n")
                    f.write("include-system-site-packages = false\n")
                    f.write(f"version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n")

                # 3. Manually install pip into the newly created environment.
                venv_python_exe = self.get_venv_python_executable()
                self.progress.emit("Bootstrapping pip...")
                pip_bootstrap_cmd = [venv_python_exe, "-m", "ensurepip"]
                result = subprocess.run(pip_bootstrap_cmd, capture_output=True, text=True, encoding="utf-8")
                if result.returncode != 0:
                    self.finished.emit(False, f"Failed to bootstrap pip: {result.stderr}")
                    return
            else:
                # For development, the standard venv creation works fine.
                venv.create(self.venv_path, with_pip=True)

        venv_python_exe = self.get_venv_python_executable()
        if not self.requirements:
            self.finished.emit(True, "Environment exists. No packages to install.")
            return

        self.progress.emit(f"Installing {len(self.requirements)} dependencies...")
        cmd = [venv_python_exe, "-m", "pip", "install"] + self.requirements
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
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
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
        self.setMinimumSize(650, 500)

        self.initial_venv_path = venv_path
        self.requirements = requirements.copy()

        layout = QVBoxLayout(self)

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Environment Path:"))
        self.path_edit = QLineEdit(self.initial_venv_path)
        path_layout.addWidget(self.path_edit)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_button)
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

        # UI FIX: Use the custom ClickableLabel for the status display.
        self.status_display = ClickableLabel("Status: Ready")
        layout.addWidget(self.status_display)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        layout.addWidget(self.output_log)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.update_status_color(None)

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

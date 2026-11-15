# default_environment_manager.py
# Manages the default virtual environment for PyFlowGraph

import glob
import os
import queue
import shutil
import subprocess
import sys
import threading

from PySide6.QtCore import QCoreApplication, QEventLoop, QThread, QTimer


class DefaultEnvironmentManager:
    """Manages the default virtual environment for PyFlowGraph."""

    def __init__(self, venv_parent_dir):
        self.venv_parent_dir = venv_parent_dir
        self.default_venv_path = os.path.join(venv_parent_dir, "default")
        self.default_requirements = ["PySide6"]

    def ensure_default_venv_exists(self, log_widget=None):
        """Ensure the default virtual environment exists and is properly configured."""
        if self.is_default_venv_ready():
            if log_widget:
                log_widget.append("Default virtual environment is ready.")
            return True

        if log_widget:
            log_widget.append("Default virtual environment not found. Creating...")

        return self.create_default_venv_sync(log_widget)

    def is_default_venv_ready(self):
        """Check if the default virtual environment exists and has PySide6.

        This looks for the files only. Starting the environment's Python to import PySide6
        took about 130 ms each time, and the editor checks at startup and for each graph.
        """
        if sys.platform == "win32":
            python_path = os.path.join(self.default_venv_path, "Scripts", "python.exe")
            site_dirs = [os.path.join(self.default_venv_path, "Lib", "site-packages")]
        else:
            python_path = os.path.join(self.default_venv_path, "bin", "python")
            site_dirs = glob.glob(os.path.join(self.default_venv_path, "lib", "python*", "site-packages"))
        if not os.path.exists(python_path):
            return False
        return any(os.path.isfile(os.path.join(d, "PySide6", "__init__.py")) for d in site_dirs)

    def create_default_venv_sync(self, log_widget=None):
        """Create the default virtual environment and return True when it is ready.

        On the GUI thread, venv and pip run in a worker thread. The window shows a progress
        dialog and keeps painting until they finish, which can take minutes.
        """
        app = QCoreApplication.instance()
        if app is None or QThread.currentThread() is not app.thread():
            return self._create_default_venv(log_widget.append if log_widget else None)
        return self._create_with_progress(log_widget)

    def _create_with_progress(self, log_widget):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QProgressDialog, QWidget

        messages = queue.SimpleQueue()
        result = {}

        def work():
            result["ok"] = self._create_default_venv(messages.put)

        parent = log_widget.window() if isinstance(log_widget, QWidget) else None
        progress = QProgressDialog("Setting up the default Python environment...", None, 0, 0, parent)
        progress.setWindowTitle("PyFlowGraph")
        progress.setWindowModality(Qt.ApplicationModal)
        progress.setMinimumDuration(0)
        loop = QEventLoop()
        timer = QTimer()
        timer.setInterval(100)
        worker = threading.Thread(target=work, name="default-venv", daemon=True)

        def poll():
            while True:
                try:
                    message = messages.get_nowait()
                except queue.Empty:
                    break
                if log_widget:
                    log_widget.append(message)
                progress.setLabelText(message)
            if not worker.is_alive():
                timer.stop()
                loop.quit()

        timer.timeout.connect(poll)
        worker.start()
        timer.start()
        progress.show()
        loop.exec()
        poll()  # the last messages
        progress.close()
        progress.deleteLater()
        return result.get("ok", False)

    def _create_default_venv(self, report=None):
        """Run venv and pip. report(message) gets each step. Safe to run in any thread."""
        say = report or (lambda message: None)
        try:
            say(f"Creating default venv at: {self.default_venv_path}")
            os.makedirs(os.path.dirname(self.default_venv_path), exist_ok=True)

            result = subprocess.run([
                sys.executable, "-m", "venv", self.default_venv_path
            ], capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                say(f"Failed to create venv: {result.stderr}")
                return False

            if sys.platform == "win32":
                pip_path = os.path.join(self.default_venv_path, "Scripts", "pip.exe")
            else:
                pip_path = os.path.join(self.default_venv_path, "bin", "pip")

            for requirement in self.default_requirements:
                say(f"Installing {requirement} in default environment...")
                result = subprocess.run([
                    pip_path, "install", requirement
                ], capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    say(f"Failed to install {requirement}: {result.stderr}")
                    return False

            say("Default virtual environment created successfully!")
            return True

        except subprocess.TimeoutExpired:
            say("Timeout creating default environment")
            return False
        except Exception as e:
            say(f"Error creating default environment: {str(e)}")
            return False

    def get_default_venv_path(self):
        """Get the path to the default virtual environment."""
        return self.default_venv_path

    def reset_default_venv(self, log_widget=None):
        """Remove and recreate the default virtual environment."""
        try:
            if os.path.exists(self.default_venv_path):
                if log_widget:
                    log_widget.append("Removing existing default environment...")
                shutil.rmtree(self.default_venv_path)

            return self.create_default_venv_sync(log_widget)

        except Exception as e:
            if log_widget:
                log_widget.append(f"Error resetting default environment: {str(e)}")
            return False

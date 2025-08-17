# default_environment_manager.py
# Manages the default virtual environment for PyFlowGraph

import os
import sys
import subprocess
import json
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal


class DefaultEnvironmentWorker(QObject):
    """Worker thread for creating/updating the default environment."""
    
    progress = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, venv_path, requirements=None):
        super().__init__()
        self.venv_path = venv_path
        self.requirements = requirements or ["PySide6"]
    
    def run(self):
        """Create or update the default virtual environment."""
        try:
            self.progress.emit("Creating default virtual environment...")
            
            # Create the venv
            if not self._create_venv():
                self.finished.emit(False, "Failed to create virtual environment")
                return
            
            # Install basic requirements
            if not self._install_requirements():
                self.finished.emit(False, "Failed to install requirements")
                return
            
            self.progress.emit("Default environment ready!")
            self.finished.emit(True, "Default environment created successfully")
            
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")
    
    def _create_venv(self):
        """Create the virtual environment."""
        try:
            self.progress.emit(f"Creating venv at: {self.venv_path}")
            
            # Create parent directory if needed
            os.makedirs(os.path.dirname(self.venv_path), exist_ok=True)
            
            # Create the venv
            result = subprocess.run([
                sys.executable, "-m", "venv", self.venv_path
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                self.progress.emit(f"Error creating venv: {result.stderr}")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            self.progress.emit("Timeout creating virtual environment")
            return False
        except Exception as e:
            self.progress.emit(f"Exception creating venv: {str(e)}")
            return False
    
    def _install_requirements(self):
        """Install requirements in the virtual environment."""
        try:
            # Get pip path
            if sys.platform == "win32":
                pip_path = os.path.join(self.venv_path, "Scripts", "pip.exe")
            else:
                pip_path = os.path.join(self.venv_path, "bin", "pip")
            
            if not os.path.exists(pip_path):
                self.progress.emit("pip not found in virtual environment")
                return False
            
            # Upgrade pip first
            self.progress.emit("Upgrading pip...")
            result = subprocess.run([
                pip_path, "install", "--upgrade", "pip"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                self.progress.emit(f"Warning: pip upgrade failed: {result.stderr}")
            
            # Install requirements
            for req in self.requirements:
                self.progress.emit(f"Installing {req}...")
                result = subprocess.run([
                    pip_path, "install", req
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    self.progress.emit(f"Failed to install {req}: {result.stderr}")
                    return False
            
            return True
            
        except subprocess.TimeoutExpired:
            self.progress.emit("Timeout installing requirements")
            return False
        except Exception as e:
            self.progress.emit(f"Exception installing requirements: {str(e)}")
            return False


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
        """Check if the default virtual environment exists and has required packages."""
        if not os.path.exists(self.default_venv_path):
            return False
        
        # Check if Python executable exists
        if sys.platform == "win32":
            python_path = os.path.join(self.default_venv_path, "Scripts", "python.exe")
        else:
            python_path = os.path.join(self.default_venv_path, "bin", "python")
        
        if not os.path.exists(python_path):
            return False
        
        # Check if PySide6 is installed
        try:
            result = subprocess.run([
                python_path, "-c", "import PySide6; print('OK')"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0 and "OK" in result.stdout
            
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def create_default_venv_sync(self, log_widget=None):
        """Create the default virtual environment synchronously."""
        try:
            if log_widget:
                log_widget.append(f"Creating default venv at: {self.default_venv_path}")
            
            # Ensure parent directory exists
            if not os.path.exists(self.venv_parent_dir):
                if log_widget:
                    log_widget.append(f"Creating venvs parent directory: {self.venv_parent_dir}")
                os.makedirs(self.venv_parent_dir, exist_ok=True)
            
            # Ensure default venv directory can be created
            default_venv_parent = os.path.dirname(self.default_venv_path)
            if not os.path.exists(default_venv_parent):
                os.makedirs(default_venv_parent, exist_ok=True)
            
            # Create venv
            result = subprocess.run([
                sys.executable, "-m", "venv", self.default_venv_path
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                if log_widget:
                    log_widget.append(f"Failed to create venv: {result.stderr}")
                return False
            
            # Install PySide6
            if sys.platform == "win32":
                pip_path = os.path.join(self.default_venv_path, "Scripts", "pip.exe")
            else:
                pip_path = os.path.join(self.default_venv_path, "bin", "pip")
            
            if log_widget:
                log_widget.append("Installing PySide6 in default environment...")
            
            result = subprocess.run([
                pip_path, "install", "PySide6"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                if log_widget:
                    log_widget.append(f"Failed to install PySide6: {result.stderr}")
                return False
            
            if log_widget:
                log_widget.append("Default virtual environment created successfully!")
            
            return True
            
        except subprocess.TimeoutExpired:
            if log_widget:
                log_widget.append("Timeout creating default environment")
            return False
        except Exception as e:
            if log_widget:
                log_widget.append(f"Error creating default environment: {str(e)}")
            return False
    
    def get_default_venv_path(self):
        """Get the path to the default virtual environment."""
        return self.default_venv_path
    
    def create_default_venv_async(self, progress_callback=None, finished_callback=None):
        """Create the default virtual environment asynchronously."""
        self.worker = DefaultEnvironmentWorker(self.default_venv_path, self.default_requirements)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        if progress_callback:
            self.worker.progress.connect(progress_callback)
        if finished_callback:
            self.worker.finished.connect(finished_callback)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.started.connect(self.worker.run)
        self.thread.start()
    
    def reset_default_venv(self, log_widget=None):
        """Remove and recreate the default virtual environment."""
        import shutil
        
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
# execution_controller.py
# Execution controller for managing batch and live mode execution

import sys
import os

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QPushButton, QLabel
from .graph_executor import GraphExecutor
from core.event_system import LiveGraphExecutor
class ExecutionController:
    """Manages execution modes and controls for the node graph."""
    
    def __init__(self, graph, output_log, get_venv_path_callback, 
                 main_exec_button: QPushButton, status_label: QLabel, 
                 button_style_callback=None, file_ops=None):
        self.graph = graph
        self.output_log = output_log
        self.get_venv_path_callback = get_venv_path_callback
        self.main_exec_button = main_exec_button
        self.status_label = status_label
        self.file_ops = file_ops
        self.button_style_callback = button_style_callback
        
        # Execution systems
        self.executor = GraphExecutor(graph, output_log, get_venv_path_callback)
        self.live_executor = LiveGraphExecutor(graph, output_log, get_venv_path_callback)
        
        # Execution state
        self.live_mode = False
        self.live_active = False
        
        # Environment state tracking
        self.venv_is_valid = False
        self.last_venv_path = None  # Cache for environment validation
        
        # UI update throttling
        self._ui_update_in_progress = False
        
        # Initialize UI
        self._update_ui_for_batch_mode()
        self._check_environment_validity()
    
    def on_mode_changed(self, mode_id):
        """Handle radio button change between Batch (0) and Live (1) modes."""
        self.live_mode = mode_id == 1
        self.output_log.clear()

        if self.live_mode:
            self._update_ui_for_live_mode()
        else:
            self._update_ui_for_batch_mode()
    
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
    
    def _update_ui_for_batch_mode(self):
        """Update UI elements for batch mode."""
        self.live_executor.set_live_mode(False)
        self.live_active = False
        self.main_exec_button.setText("Execute Graph")
        if self.button_style_callback:
            self.main_exec_button.setStyleSheet(self.button_style_callback("batch", "ready"))
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

        self.output_log.append("[BATCH] === BATCH MODE SELECTED ===")
        self.output_log.append("Click 'Execute Graph' to run entire graph at once")
    
    def _update_ui_for_live_mode(self):
        """Update UI elements for live mode."""
        if self._ui_update_in_progress:
            return  # Prevent redundant updates
        
        self._ui_update_in_progress = True
        try:
            self.live_executor.set_live_mode(True)
            self.live_active = False
            self.main_exec_button.setText("Start Live Mode")
            if self.button_style_callback:
                self.main_exec_button.setStyleSheet(self.button_style_callback("live", "ready"))
            self.status_label.setText("Live Ready")
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")

            self.output_log.append("[LIVE] === LIVE MODE SELECTED ===")
            self.output_log.append("=> Click 'Start Live Mode' to activate interactive execution")
            self.output_log.append("=> Then use buttons inside nodes to control flow!")
        finally:
            self._ui_update_in_progress = False
    
    def _execute_batch_mode(self):
        """Execute graph in batch mode."""
        # Ensure environment is selected before executing
        if self.file_ops:
            self.file_ops.ensure_environment_selected()
            
        self.output_log.clear()
        self.output_log.append("=> === BATCH EXECUTION STARTED ===")

        # Update button state during execution
        self.main_exec_button.setText("Executing...")
        if self.button_style_callback:
            self.main_exec_button.setStyleSheet(self.button_style_callback("batch", "executing"))
        self.status_label.setText("Executing")
        self.status_label.setStyleSheet("color: #607D8B; font-weight: bold;")

        try:
            self.executor.execute()
            self.output_log.append("[OK] === BATCH EXECUTION FINISHED ===")
        except Exception as e:
            self.output_log.append(f"[ERROR] === EXECUTION FAILED: {e} ===")
        finally:
            # Restore button state
            self.main_exec_button.setText("Execute Graph")
            if self.button_style_callback:
                self.main_exec_button.setStyleSheet(self.button_style_callback("batch", "ready"))
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def _start_live_mode(self):
        """Start live interactive mode."""
        # Ensure environment is selected before starting live mode
        if self.file_ops:
            self.file_ops.ensure_environment_selected()
            
        self.output_log.clear()
        self.output_log.append("[LIVE] === LIVE MODE ACTIVATED ===")
        self.output_log.append("=> Interactive execution enabled!")
        self.output_log.append("=> Click buttons inside nodes to trigger execution")
        self.output_log.append("=> Graph state has been reset and is ready for interaction")

        self.live_active = True
        # CRITICAL FIX: Ensure live mode is enabled in the executor
        self.live_executor.set_live_mode(True)
        self.live_executor.restart_graph()

        # Update button to pause state
        self.main_exec_button.setText("Pause Live Mode")
        if self.button_style_callback:
            self.main_exec_button.setStyleSheet(self.button_style_callback("live", "active"))
        self.status_label.setText("Live Active")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def _pause_live_mode(self):
        """Pause live mode."""
        self.live_active = False
        self.live_executor.set_live_mode(False)

        self.main_exec_button.setText("Resume Live Mode")
        if self.button_style_callback:
            self.main_exec_button.setStyleSheet(self.button_style_callback("live", "paused"))
        self.status_label.setText("Live Paused")
        self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")

        self.output_log.append("[PAUSE] Live mode paused - node buttons are now inactive")
        self.output_log.append("Click 'Resume Live Mode' to reactivate")
    
    def _check_environment_validity(self):
        """Check if current virtual environment is valid and update button state."""
        import os
        
        try:
            venv_path = self.get_venv_path_callback()
            
            # Use cached result if path hasn't changed
            if venv_path == self.last_venv_path and hasattr(self, '_last_validity_result'):
                if self._last_validity_result:
                    self._set_environment_valid()
                else:
                    self._set_environment_invalid(self._last_invalid_reason)
                return
            
            self.last_venv_path = venv_path
            
            # Check if venv exists and has Python executable
            if not venv_path or not os.path.exists(venv_path):
                self._last_validity_result = False
                self._last_invalid_reason = "No virtual environment configured"
                self._set_environment_invalid(self._last_invalid_reason)
                return
            
            # Check for Python executable
            if os.name == 'nt':  # Windows
                python_exe = os.path.join(venv_path, "Scripts", "python.exe")
            else:  # Unix/Linux/Mac
                python_exe = os.path.join(venv_path, "bin", "python")
            
            if not os.path.exists(python_exe):
                self._last_validity_result = False
                self._last_invalid_reason = "Virtual environment is invalid (missing Python)"
                self._set_environment_invalid(self._last_invalid_reason)
                return
            
            # Environment is valid
            self._last_validity_result = True
            self._set_environment_valid()
            
        except Exception as e:
            self._last_validity_result = False
            self._last_invalid_reason = f"Environment check failed: {str(e)}"
            self._set_environment_invalid(self._last_invalid_reason)
    
    def _set_environment_valid(self):
        """Enable execution when environment is valid."""
        self.venv_is_valid = True
        self.main_exec_button.setEnabled(True)
        
        # Restore appropriate button state
        if self.live_mode:
            self._update_ui_for_live_mode()
        else:
            self._update_ui_for_batch_mode()
    
    def _set_environment_invalid(self, reason):
        """Disable execution when environment is invalid."""
        self.venv_is_valid = False
        self.main_exec_button.setEnabled(False)
        self.main_exec_button.setText("No Environment")
        self.main_exec_button.setStyleSheet("background-color: #888; color: #ccc; border: 1px solid #555;")
        self.status_label.setText(f"Environment Issue: {reason}")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
    
    def refresh_environment_state(self):
        """Public method to refresh environment state (called after environment selection)."""
        self._check_environment_validity()
        
        # Refresh the GraphExecutor's SingleProcessExecutor with new venv path
        if self.executor:
            self.executor.refresh_executor_environment()
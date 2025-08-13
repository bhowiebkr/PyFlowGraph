# execution_controller.py
# Execution controller for managing batch and live mode execution

from PySide6.QtWidgets import QPushButton, QLabel
from .graph_executor import GraphExecutor
from .event_system import LiveGraphExecutor
from .ui_utils import ButtonStyleManager


class ExecutionController:
    """Manages execution modes and controls for the node graph."""
    
    def __init__(self, graph, output_log, get_venv_path_callback, 
                 main_exec_button: QPushButton, status_label: QLabel):
        self.graph = graph
        self.output_log = output_log
        self.get_venv_path_callback = get_venv_path_callback
        self.main_exec_button = main_exec_button
        self.status_label = status_label
        
        # Execution systems
        self.executor = GraphExecutor(graph, output_log, get_venv_path_callback)
        self.live_executor = LiveGraphExecutor(graph, output_log, get_venv_path_callback)
        
        # Execution state
        self.live_mode = False
        self.live_active = False
        
        # Initialize UI
        self._update_ui_for_batch_mode()
    
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
        self.main_exec_button.setText("▶️ Execute Graph")
        self.main_exec_button.setStyleSheet(ButtonStyleManager.get_button_style("batch", "ready"))
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

        self.output_log.append("📦 === BATCH MODE SELECTED ===")
        self.output_log.append("Click 'Execute Graph' to run entire graph at once")
    
    def _update_ui_for_live_mode(self):
        """Update UI elements for live mode."""
        self.live_executor.set_live_mode(True)
        self.live_active = False
        self.main_exec_button.setText("🔥 Start Live Mode")
        self.main_exec_button.setStyleSheet(ButtonStyleManager.get_button_style("live", "ready"))
        self.status_label.setText("Live Ready")
        self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")

        self.output_log.append("🎯 === LIVE MODE SELECTED ===")
        self.output_log.append("📋 Click 'Start Live Mode' to activate interactive execution")
        self.output_log.append("💡 Then use buttons inside nodes to control flow!")
    
    def _execute_batch_mode(self):
        """Execute graph in batch mode."""
        self.output_log.clear()
        self.output_log.append("▶️ === BATCH EXECUTION STARTED ===")

        # Update button state during execution
        self.main_exec_button.setText("⏳ Executing...")
        self.main_exec_button.setStyleSheet(ButtonStyleManager.get_button_style("batch", "executing"))
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
            self.main_exec_button.setStyleSheet(ButtonStyleManager.get_button_style("batch", "ready"))
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
        self.main_exec_button.setStyleSheet(ButtonStyleManager.get_button_style("live", "active"))
        self.status_label.setText("Live Active")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def _pause_live_mode(self):
        """Pause live mode."""
        self.live_active = False
        self.live_executor.set_live_mode(False)

        self.main_exec_button.setText("🔥 Resume Live Mode")
        self.main_exec_button.setStyleSheet(ButtonStyleManager.get_button_style("live", "paused"))
        self.status_label.setText("Live Paused")
        self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")

        self.output_log.append("⏸️ Live mode paused - node buttons are now inactive")
        self.output_log.append("Click 'Resume Live Mode' to reactivate")
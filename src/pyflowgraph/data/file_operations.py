# file_operations.py
# File operations manager for PyFlowGraph supporting both .md and .json formats

import json
import os


from PySide6.QtWidgets import QFileDialog, QMessageBox
from pyflowgraph.paths import examples_dir
from pyflowgraph.settings import app_settings
from .flow_format import FlowFormatHandler, extract_title_from_filename
from .graph_trust import GraphTrustStore, describe_nodes


# The example that opens when no recent file is known. The setting default_graph changes it;
# an empty value starts with an empty canvas.
DEFAULT_GRAPH = "password_generator_tool_group.md"


class FileOperationsManager:
    """Manages file operations for loading and saving graphs in multiple formats."""
    
    def __init__(self, parent_window, graph, output_log, default_env_manager=None):
        self.parent_window = parent_window
        self.graph = graph
        self.output_log = output_log
        self.settings = app_settings()
        
        # Current file state
        self.current_file_path = None
        self.current_graph_name = "untitled"
        self.current_requirements = []
        # The Dependencies section of the open file; save writes its other fields back.
        self.current_dependencies = {}

        # Environment management (lazy import to avoid circular dependencies)
        self.default_env_manager = default_env_manager

        # Opening a graph runs its GUI code, so untrusted files need the user's consent.
        # Tests can replace confirm_untrusted_code.
        self.trust_store = GraphTrustStore(self.settings)
        self.confirm_untrusted_code = self._ask_to_trust_graph

    def set_execution_controller(self, execution_controller):
        """Set reference to execution controller for updating button state."""
        self.execution_controller = execution_controller
    
    
    def update_window_title(self):
        """Updates the window title to show the current graph name."""
        if self.current_graph_name == "untitled":
            self.parent_window.setWindowTitle("PyFlowGraph - Untitled")
        else:
            self.parent_window.setWindowTitle(f"PyFlowGraph - {self.current_graph_name}")
    
    def new_scene(self):
        """Create a new empty scene."""
        self.graph.clear_graph()
        self.current_graph_name = "untitled"
        self.current_requirements = []
        self.current_dependencies = {}
        self.current_file_path = None
        self.update_window_title()
        self.output_log.append("New scene created.")
    
    def save(self):
        """Save the current graph."""
        if not self.current_file_path:
            # Get last used directory
            last_dir = self.settings.value("last_directory", "")
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent_window, 
                "Save Graph As...", 
                last_dir, 
                "Flow Files (*.md)"
            )
            if not file_path:
                return False
            self.current_file_path = file_path
            # Save directory for next time
            self.settings.setValue("last_directory", os.path.dirname(file_path))

        self.current_graph_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        self.update_window_title()
        return self._save_file(self.current_file_path)
    
    def save_as(self):
        """Save the current graph with a new filename."""
        # Get last used directory
        last_dir = self.settings.value("last_directory", "")
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent_window, 
            "Save Graph As...", 
            last_dir, 
            "Flow Files (*.md)"
        )
        if not file_path:
            return False

        self.current_file_path = file_path
        # Save directory for next time
        self.settings.setValue("last_directory", os.path.dirname(file_path))
        self.current_graph_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        self.update_window_title()
        return self._save_file(self.current_file_path)
    
    def load(self, file_path=None, startup=False):
        """Load a graph from file.

        A graph whose nodes have GUI code opens only when the file is trusted or the user
        agrees. At startup an untrusted file is not reopened and no question is asked.
        """
        if not file_path:
            # Get last used directory
            last_dir = self.settings.value("last_directory", "")
            file_path, _ = QFileDialog.getOpenFileName(
                self.parent_window, 
                "Load Graph", 
                last_dir, 
                "Flow Files (*.md);;All Files (*.*)"
            )

        if file_path and os.path.exists(file_path):
            content, data = self._load_file(file_path)
            if not data:
                return False

            if not self._may_run_graph_code(file_path, content, data, startup):
                return False

            self.current_file_path = file_path
            self.current_graph_name = os.path.splitext(os.path.basename(file_path))[0]

            self.update_window_title()

            self.graph.deserialize(data)
            self.current_requirements = data.get("requirements", [])
            self.current_dependencies = data.get("dependencies", {})
            self.settings.setValue("last_file_path", file_path)
            # Save directory for next time
            self.settings.setValue("last_directory", os.path.dirname(file_path))

            # Handle environment selection for the loaded graph
            self._handle_environment_selection(file_path)

            self.output_log.append(f"Graph loaded from {file_path}")
            self._show_environment_status()
            return True

        return False
    
    def load_last_file(self):
        """Load the last opened file or default graph."""
        last_file = self.settings.value("last_file_path", None)
        if last_file and os.path.exists(last_file):
            loaded = self.load(file_path=last_file, startup=True)
        else:
            default_graph = self.settings.value("default_graph", DEFAULT_GRAPH)
            loaded = bool(default_graph) and self.load_initial_graph(
                os.path.join(examples_dir(), default_graph))
        if not loaded:
            # The canvas stays empty: show the same title as File > New.
            self.update_window_title()
        return loaded

    def load_initial_graph(self, file_path):
        """Load the initial default graph."""
        if os.path.exists(file_path):
            return self.load(file_path=file_path, startup=True)
        else:
            self.output_log.append(f"Default graph file not found: '{file_path}'. Starting with an empty canvas.")
            return False
    
    def _save_file(self, file_path: str):
        """Save the graph to .md format."""
        try:
            data = self.graph.serialize()
            data["requirements"] = self.current_requirements
            data["dependencies"] = self.current_dependencies

            # Save as .md format
            handler = FlowFormatHandler()
            title = data.get("graph_title", extract_title_from_filename(file_path))
            description = data.get("graph_description", f"Graph created with PyFlowGraph containing {len(data.get('nodes', []))} nodes.")
            content = handler.data_to_markdown(data, title, description)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            # The user wrote this content from the editor, so its code is theirs.
            self.trust_store.trust(file_path, content)

            self.settings.setValue("last_file_path", file_path)
            # Save directory for next time
            self.settings.setValue("last_directory", os.path.dirname(file_path))
            self.output_log.append(f"Graph saved to {file_path}")
            return True
            
        except Exception as e:
            self.output_log.append(f"Error saving file {file_path}: {str(e)}")
            return False
    
    def _load_file(self, file_path: str):
        """Read a graph in the .md format. Return (text, data), or (None, None) on error."""
        try:
            handler = FlowFormatHandler()
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            data = handler.markdown_to_data(content)

            return content, data
        except Exception as e:
            self.output_log.append(f"Error loading file {file_path}: {str(e)}")
            return None, None

    def _may_run_graph_code(self, file_path, content, data, startup):
        """Return True when the graph may be built, which runs the GUI code of its nodes."""
        titles = self.trust_store.needs_confirmation(file_path, content, data)
        if not titles:
            return True
        if startup:
            self.output_log.append(
                f"Did not reopen {file_path}. It has GUI code that runs when it opens, and "
                "you have not trusted this version of the file. Use File > Load Graph to open it."
            )
            return False
        if not self.confirm_untrusted_code(file_path, titles):
            self.output_log.append(f"Did not open {file_path}. Its code did not run.")
            return False
        self.trust_store.trust(file_path, content)
        return True

    def _ask_to_trust_graph(self, file_path, titles):
        box = QMessageBox(self.parent_window)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Run Code from This Graph?")
        box.setText(f"Opening {os.path.basename(file_path)} runs code from it on this computer.")
        box.setInformativeText(
            "These nodes have GUI code that runs when the graph opens:\n"
            + describe_nodes(titles)
            + "\n\nOpen the graph only if you trust where it came from. "
            "The editor remembers your choice until the file changes."
        )
        open_button = box.addButton("Open and Trust", QMessageBox.AcceptRole)
        cancel_button = box.addButton(QMessageBox.Cancel)
        box.setDefaultButton(cancel_button)
        box.exec()
        return box.clickedButton() is open_button
    
    def _handle_environment_selection(self, file_path=None):
        """Handle environment selection for graphs."""
        # For new/untitled graphs or example graphs, prompt for environment selection
        should_prompt = False
        
        if file_path:
            # Check if this is from the examples directory
            normalized_path = os.path.normpath(file_path)
            if "examples" in normalized_path.split(os.sep):
                should_prompt = True
        else:
            # No file path means new/untitled graph
            should_prompt = True
            
        if should_prompt:
            # Check if user has already made an environment choice for this graph
            settings_key = f"graph_env_choice/{self.current_graph_name}"
            saved_choice = self.settings.value(settings_key, None)
            
            if saved_choice:
                # Use saved environment choice
                self.output_log.append(f"Using saved environment preference: {saved_choice}")
                self._apply_environment_selection(saved_choice)
            else:
                # Show dialog for first-time loading (lazy import to avoid circular dependency)
                from pyflowgraph.ui.dialogs.environment_selection_dialog import EnvironmentSelectionDialog
                dialog = EnvironmentSelectionDialog(self.current_graph_name, self.parent_window)
                if dialog.exec():
                    selected_option = dialog.get_selected_option()
                    # Save the choice for future loads
                    self.settings.setValue(settings_key, selected_option)
                    self._apply_environment_selection(selected_option)
                else:
                    # User cancelled - default to default environment and save choice
                    self.settings.setValue(settings_key, "default")
                    self._apply_environment_selection("default")
    
    def _apply_environment_selection(self, option):
        """Apply the selected environment option."""
        if option == "default":
            # Set current graph to use default environment
            self.use_default_environment = True
            self.output_log.append("Using default environment (venvs/default) for this graph.")
            
            # Ensure the default environment actually exists
            if self.default_env_manager:
                self.output_log.append("Ensuring default environment exists...")
                success = self.default_env_manager.ensure_default_venv_exists(self.output_log)
                if success:
                    self.output_log.append("Default environment is ready!")
                else:
                    self.output_log.append("Warning: Could not create default environment")
            else:
                self.output_log.append("Warning: Default environment manager not available")
                
        elif option == "graph_specific":
            # Use graph-specific environment (existing behavior)
            self.use_default_environment = False
            self.output_log.append(f"Will create/use graph-specific environment: venvs/{self.current_graph_name}")
        elif option == "existing":
            # Use existing graph-specific environment
            self.use_default_environment = False
            self.output_log.append(f"Using existing environment: venvs/{self.current_graph_name}")
        
        # Refresh execution controller state after environment selection
        if self.execution_controller:
            self.execution_controller.refresh_environment_state()
    
    def _show_environment_status(self):
        """Show appropriate environment status message."""
        if hasattr(self, 'use_default_environment') and self.use_default_environment:
            self.output_log.append("Environment: venvs/default (ready to execute)")
        else:
            self.output_log.append("Dependencies loaded. Please verify the environment via the 'Run' menu.")
    
    def ensure_environment_selected(self):
        """Ensure environment is selected before execution. Called from execution controller."""
        # Check if this is an untitled/new graph that hasn't had environment selected
        if self.current_graph_name == "untitled" and not self.current_file_path:
            settings_key = f"graph_env_choice/{self.current_graph_name}"
            saved_choice = self.settings.value(settings_key, None)
            
            if not saved_choice:
                # Prompt for environment selection
                self._handle_environment_selection()
    
    def get_current_venv_path(self, venv_parent_dir):
        """Provides the full path to the venv for the current graph."""
        if hasattr(self, 'use_default_environment') and self.use_default_environment:
            return os.path.join(venv_parent_dir, "default")
        return os.path.join(venv_parent_dir, self.current_graph_name)


def load_file(window, file_path):
    """Convenience function to load a file using the window's file operations manager.
    
    Args:
        window: The main window object with file_operations_manager
        file_path: Path to the file to load
        
    Returns:
        bool: True if successful, False otherwise
    """
    if hasattr(window, 'file_operations_manager'):
        return window.file_operations_manager.load(file_path)
    return False
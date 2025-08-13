# file_operations.py
# File operations manager for PyFlowGraph supporting both .md and .json formats

import json
import os
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QSettings
from flow_format import FlowFormatHandler, extract_title_from_filename


class FileOperationsManager:
    """Manages file operations for loading and saving graphs in multiple formats."""
    
    def __init__(self, parent_window, graph, output_log):
        self.parent_window = parent_window
        self.graph = graph
        self.output_log = output_log
        self.settings = QSettings("PyFlowGraph", "NodeEditor")
        
        # Current file state
        self.current_file_path = None
        self.current_graph_name = "untitled"
        self.current_requirements = []
    
    def get_current_venv_path(self, venv_parent_dir):
        """Provides the full path to the venv for the current graph."""
        return os.path.join(venv_parent_dir, self.current_graph_name)
    
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
        self.current_file_path = None
        self.update_window_title()
        self.output_log.append("New scene created.")
    
    def save(self):
        """Save the current graph."""
        if not self.current_file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent_window, 
                "Save Graph As...", 
                "", 
                "Flow Files (*.md);;JSON Files (*.json)"
            )
            if not file_path:
                return False
            self.current_file_path = file_path

        self.current_graph_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        self.update_window_title()
        return self._save_file(self.current_file_path)
    
    def save_as(self):
        """Save the current graph with a new filename."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent_window, 
            "Save Graph As...", 
            "", 
            "Flow Files (*.md);;JSON Files (*.json)"
        )
        if not file_path:
            return False

        self.current_file_path = file_path
        self.current_graph_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        self.update_window_title()
        return self._save_file(self.current_file_path)
    
    def load(self, file_path=None):
        """Load a graph from file."""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self.parent_window, 
                "Load Graph", 
                "", 
                "Flow Files (*.md);;JSON Files (*.json);;All Files (*.*)"
            )

        if file_path and os.path.exists(file_path):
            self.current_file_path = file_path
            self.current_graph_name = os.path.splitext(os.path.basename(file_path))[0]
            self.update_window_title()
            
            data = self._load_file(file_path)
            if data:
                self.graph.deserialize(data)
                self.current_requirements = data.get("requirements", [])
                self.settings.setValue("last_file_path", file_path)
                
                # Force a complete view refresh to ensure proper rendering
                # This addresses GUI refresh issues particularly with .md file loading
                from PySide6.QtCore import QTimer
                
                def force_complete_refresh():
                    # Update the scene
                    self.graph.update()
                    self.graph.invalidate()  # Force scene to recalculate everything
                    
                    # Update all views  
                    for view in self.graph.views():
                        view.invalidateScene()  # Invalidate cached scene data
                        view.update()
                        view.viewport().update()
                        view.repaint()  # Force immediate repaint
                
                # Execute refresh immediately and also defer one for after Qt event processing
                force_complete_refresh()
                QTimer.singleShot(10, force_complete_refresh)
                
                self.output_log.append(f"Graph loaded from {file_path}")
                self.output_log.append("Dependencies loaded. Please verify the environment via the 'Run' menu.")
                return True
        
        return False
    
    def load_last_file(self):
        """Load the last opened file or default graph."""
        last_file = self.settings.value("last_file_path", None)
        if last_file and os.path.exists(last_file):
            return self.load(file_path=last_file)
        else:
            return self.load_initial_graph("examples/password_generator_tool.md")
    
    def load_initial_graph(self, file_path):
        """Load the initial default graph."""
        if os.path.exists(file_path):
            return self.load(file_path=file_path)
        else:
            self.output_log.append(f"Default graph file not found: '{file_path}'. Starting with an empty canvas.")
            return False
    
    def _save_file(self, file_path: str):
        """Save the graph to either .md or .json format based on file extension."""
        try:
            data = self.graph.serialize()
            data["requirements"] = self.current_requirements
            
            if file_path.lower().endswith('.md'):
                # Save as .md format
                handler = FlowFormatHandler()
                title = extract_title_from_filename(file_path)
                description = f"Graph created with PyFlowGraph containing {len(data.get('nodes', []))} nodes."
                content = handler.json_to_flow(data, title, description)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                # Save as JSON format
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            
            self.settings.setValue("last_file_path", file_path)
            self.output_log.append(f"Graph saved to {file_path}")
            return True
            
        except Exception as e:
            self.output_log.append(f"Error saving file {file_path}: {str(e)}")
            return False
    
    def _load_file(self, file_path: str):
        """Load a graph from either .md or .json format based on file extension."""
        try:
            if file_path.lower().endswith('.md'):
                # Load .md format
                handler = FlowFormatHandler()
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                data = handler.flow_to_json(content)
            else:
                # Load JSON format
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            return data
        except Exception as e:
            self.output_log.append(f"Error loading file {file_path}: {str(e)}")
            return None
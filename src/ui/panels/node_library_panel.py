# node_library_panel.py
# Node library panel with dependency status indicators and drag & drop support

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QTreeWidget, QTreeWidgetItem, QLineEdit, QPushButton,
    QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QMessageBox, QComboBox, QSplitter, QTextEdit, QToolTip, QFileDialog
)
from PySide6.QtCore import Qt, QMimeData, QTimer, QPoint, QSize
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QBrush, QPen, QFont

# Add project root to path for cross-package imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.node_scanner import NodeScanner
from src.core.dependency_checker import DependencyStatus


class NodePreviewWidget(QGraphicsView):
    """Full-width preview widget that renders REAL nodes like the main editor."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(150)  # Full width, taller for better node view
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        
        # Create scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Simple dark background like main editor
        self.setStyleSheet("QGraphicsView { border: 1px solid #555; background: #2a2a2a; }")
        
        self.current_node = None
    
    def set_node_data(self, node_data: Dict[str, Any]):
        """Set node data to display REAL node preview.
        
        Args:
            node_data: Node data with dependency information
        """
        self.scene.clear()
        
        try:
            # Import Node dynamically to avoid circular imports
            from src.core.node import Node
            
            # Create a REAL node for preview
            title = node_data.get("title", "Preview Node")
            preview_node = Node(title)
            
            # Set node properties
            if node_data.get("size"):
                size = node_data["size"]
                preview_node.width = size[0]
                preview_node.height = size[1]
            
            # Set colors from node data
            colors = node_data.get("colors", {})
            if "title" in colors:
                preview_node.color_title_bar = QColor(colors["title"])
            if "body" in colors:
                preview_node.color_body = QColor(colors["body"])
            
            # Set code to trigger pin generation
            if node_data.get("code"):
                preview_node.set_code(node_data["code"])
            
            # Set GUI code if present
            if node_data.get("gui_code"):
                preview_node.set_gui_code(node_data["gui_code"])
            
            if node_data.get("gui_get_values_code"):
                preview_node.gui_get_values_code = node_data["gui_get_values_code"]
            
            # Store original colors for dependency status indicator
            original_title_color = preview_node.color_title_bar
            original_body_color = preview_node.color_body
            
            # Add subtle dependency status indication without completely overriding colors
            status = node_data.get("dependency_status", DependencyStatus.UNKNOWN)
            if status == DependencyStatus.SATISFIED:
                # Keep original colors for satisfied dependencies
                pass
            elif status == DependencyStatus.OPTIONAL_MISSING:
                # Slightly darken for optional missing
                if original_body_color:
                    r, g, b, a = original_body_color.getRgb()
                    preview_node.color_body = QColor(max(0, r-30), max(0, g-20), max(0, b-30), a)
            elif status == DependencyStatus.REQUIRED_MISSING:
                # Add red tint for required missing
                if original_body_color:
                    r, g, b, a = original_body_color.getRgb()
                    preview_node.color_body = QColor(min(255, r+30), max(0, g-20), max(0, b-20), a)
            
            # Position the node and add to scene
            preview_node.setPos(10, 10)
            self.scene.addItem(preview_node)
            self.current_node = preview_node
            
            # Apply the same resize trick used for drag/drop nodes and loading
            # This ensures pins are positioned correctly for all node types
            QTimer.singleShot(0, lambda: self._final_preview_update(preview_node))
            
        except Exception as e:
            # If node creation fails, show the error
            self._draw_error_message(f"Preview Error: {e}")
    
    def _draw_error_message(self, error_text: str):
        """Draw error message if node creation fails."""
        # Simple text item for errors
        text_item = self.scene.addText(error_text, QFont("Arial", 9))
        text_item.setDefaultTextColor(QColor(255, 100, 100))
        text_item.setPos(10, 10)
    
    def _final_preview_update(self, preview_node):
        """Apply final layout update to preview node (same as drag/drop and loading).
        
        This ensures pins are positioned correctly by deferring layout calculations
        until after the Qt event loop processes all pending widget creation events.
        """
        try:
            if preview_node.scene() is None:
                return  # Node has been removed from scene
            
            # Force a complete layout rebuild
            preview_node._update_layout()
            # Update all pin connections
            for pin in preview_node.pins:
                pin.update_connections()
            # Force node visual update
            preview_node.update()
            
            # Now set scene rect and fit view with correct node bounds
            node_rect = preview_node.boundingRect()
            scene_rect = node_rect.adjusted(0, 0, 20, 20)  # Add padding
            self.scene.setSceneRect(scene_rect)
            
            # Fit the node in view with some margin
            self.fitInView(scene_rect, Qt.KeepAspectRatio)
            
        except RuntimeError:
            # Node has been deleted, skip
            pass


class NodeLibraryItem(QTreeWidgetItem):
    """Custom tree widget item for nodes with dependency data."""
    
    def __init__(self, parent=None, node_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.node_data = node_data
        
        if node_data:
            self._setup_node_item()
    
    def _setup_node_item(self):
        """Setup the tree item for a node."""
        # Set title
        title = self.node_data.get("title", "Unknown Node")
        self.setText(0, title)
        
        # Set dependency status icon and color
        status = self.node_data.get("dependency_status", DependencyStatus.UNKNOWN)
        
        if status == DependencyStatus.SATISFIED:
            self.setText(1, "OK")
            self.setForeground(1, QColor(100, 200, 100))
        elif status == DependencyStatus.OPTIONAL_MISSING:
            self.setText(1, "WARN")
            self.setForeground(1, QColor(200, 150, 50))
        elif status == DependencyStatus.REQUIRED_MISSING:
            self.setText(1, "ERROR")
            self.setForeground(1, QColor(200, 100, 100))
        else:
            self.setText(1, "UNKNOWN")
            self.setForeground(1, QColor(150, 150, 150))
        
        # Create tooltip with dependency information
        self._create_tooltip()
    
    def _create_tooltip(self):
        """Create detailed tooltip with dependency information."""
        if not self.node_data:
            return
        
        lines = []
        
        # Basic info
        title = self.node_data.get("title", "Unknown")
        description = self.node_data.get("description", "")
        source_file = self.node_data.get("source_filename", "")
        
        lines.append(f"Node: {title}")
        if source_file:
            lines.append(f"Source: {source_file}")
        if description:
            lines.append(f"Description: {description[:100]}...")
        
        # Dependency info
        dep_info = self.node_data.get("dependency_info", {})
        if dep_info:
            lines.append("")
            lines.append("Dependencies:")
            
            required = dep_info.get("required_dependencies", [])
            if required:
                lines.append(f"  Required: {', '.join(required)}")
            
            optional = dep_info.get("optional_dependencies", [])
            if optional:
                lines.append(f"  Optional: {', '.join(optional)}")
            
            missing_req = dep_info.get("missing_required", [])
            if missing_req:
                lines.append(f"  Missing Required: {', '.join(missing_req)}")
            
            missing_opt = dep_info.get("missing_optional", [])
            if missing_opt:
                lines.append(f"  Missing Optional: {', '.join(missing_opt)}")
        
        tooltip_text = "\n".join(lines)
        self.setToolTip(0, tooltip_text)
        self.setToolTip(1, tooltip_text)


class NodeLibraryPanel(QDockWidget):
    """Node library panel with search, filtering, and dependency indicators."""
    
    def __init__(self, parent=None, examples_dir: str = "examples", venv_path: Optional[str] = None):
        super().__init__("Node Library", parent)
        
        # Initialize scanner
        self.scanner = NodeScanner(examples_dir, venv_path)
        self.current_nodes = {}
        
        # Setup UI
        self._setup_ui()
        
        # Initial population
        self._populate_tree()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._check_for_updates)
        self.refresh_timer.start(2000)  # Check every 2 seconds
    
    def _setup_ui(self):
        """Setup the user interface."""
        main_widget = QWidget()
        self.setWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        
        # Search section
        search_layout = QVBoxLayout()
        
        # First row: search box and status filter
        search_row1 = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search nodes...")
        self.search_box.textChanged.connect(self._filter_tree)
        self.search_box.setStyleSheet("QLineEdit { border: 1px solid #555; padding: 4px; background: #3a3a3a; color: white; }")
        search_row1.addWidget(self.search_box)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Nodes", None)
        self.status_filter.addItem("Available", DependencyStatus.SATISFIED)
        self.status_filter.addItem("Missing Optional", DependencyStatus.OPTIONAL_MISSING)
        self.status_filter.addItem("Missing Required", DependencyStatus.REQUIRED_MISSING)
        self.status_filter.currentTextChanged.connect(self._filter_tree)
        self.status_filter.setStyleSheet("QComboBox { border: 1px solid #555; padding: 4px; background: #3a3a3a; color: white; }")
        self.status_filter.setMaximumWidth(120)
        search_row1.addWidget(self.status_filter)
        
        search_layout.addLayout(search_row1)
        
        # Second row: buttons
        button_row = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_cache)
        refresh_btn.setStyleSheet("QPushButton { border: 1px solid #555; padding: 6px 12px; background: #4a4a4a; color: white; } QPushButton:hover { background: #5a5a5a; }")
        button_row.addWidget(refresh_btn)
        
        # Directory button
        dir_btn = QPushButton("Change Directory")
        dir_btn.clicked.connect(self._change_directory)
        dir_btn.setStyleSheet("QPushButton { border: 1px solid #555; padding: 6px 12px; background: #4a6a9e; color: white; } QPushButton:hover { background: #5a7aae; }")
        button_row.addWidget(dir_btn)
        
        search_layout.addLayout(button_row)
        
        layout.addLayout(search_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Node", "Status"])
        self.tree_widget.setColumnWidth(0, 200)
        self.tree_widget.setColumnWidth(1, 80)
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setDefaultDropAction(Qt.CopyAction)
        
        # Styling for tree widget
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #555;
                background: #2a2a2a;
                color: white;
                selection-background-color: #4a6a9e;
            }
            QTreeWidget::item {
                padding: 3px;
                border-bottom: 1px solid #333;
            }
            QTreeWidget::item:hover {
                background: #3a3a3a;
            }
            QTreeWidget::item:selected {
                background: #4a6a9e;
            }
            QHeaderView::section {
                background: #3a3a3a;
                color: white;
                padding: 5px;
                border: 1px solid #555;
                font-weight: bold;
            }
        """)
        
        # Enable drag from tree
        self.tree_widget.setDragDropMode(QTreeWidget.DragOnly)
        self.tree_widget.startDrag = self._start_drag
        
        # Item selection and preview
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        
        splitter.addWidget(self.tree_widget)
        
        # Info panel
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # Preview section - full width
        preview_label = QLabel("Preview")
        preview_label.setStyleSheet("QLabel { font-weight: bold; color: #4a9eff; margin-bottom: 5px; }")
        info_layout.addWidget(preview_label)
        
        self.preview_widget = NodePreviewWidget()
        info_layout.addWidget(self.preview_widget)
        
        # Details text
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #555;
                background: #2a2a2a;
                color: white;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
            }
        """)
        info_layout.addWidget(self.details_text)
        
        splitter.addWidget(info_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 150])
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def _populate_tree(self):
        """Populate the tree with nodes from examples."""
        self.tree_widget.clear()
        
        try:
            # Update status
            self.status_label.setText("Scanning nodes...")
            
            # Get all nodes
            self.current_nodes = self.scanner.scan_nodes()
            
            # Group by source file
            for file_path, nodes in self.current_nodes.items():
                if not nodes:
                    continue
                
                # Create file group
                file_name = os.path.basename(file_path)
                file_item = QTreeWidgetItem(self.tree_widget)
                file_item.setText(0, file_name)
                file_item.setText(1, f"({len(nodes)} nodes)")
                file_item.setExpanded(True)
                
                # Add nodes
                for node_data in nodes:
                    node_item = NodeLibraryItem(file_item, node_data)
            
            # Update status with summary
            summary = self.scanner.get_dependency_summary()
            total = summary.get("total_nodes", 0)
            satisfied = summary.get("status_counts", {}).get(DependencyStatus.SATISFIED, 0)
            self.status_label.setText(f"Loaded {total} nodes ({satisfied} available)")
            
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
            QMessageBox.warning(self, "Scan Error", f"Failed to scan nodes: {e}")
    
    def _filter_tree(self):
        """Filter the tree based on search text and status filter."""
        search_text = self.search_box.text().lower()
        status_filter = self.status_filter.currentData()
        
        # Iterate through all items
        for i in range(self.tree_widget.topLevelItemCount()):
            file_item = self.tree_widget.topLevelItem(i)
            file_visible = False
            
            # Check child nodes
            for j in range(file_item.childCount()):
                node_item = file_item.child(j)
                
                # Apply filters
                visible = True
                
                # Text filter
                if search_text:
                    node_title = node_item.text(0).lower()
                    node_data = getattr(node_item, 'node_data', {})
                    node_desc = node_data.get("description", "").lower()
                    
                    if search_text not in node_title and search_text not in node_desc:
                        visible = False
                
                # Status filter
                if status_filter is not None:
                    node_data = getattr(node_item, 'node_data', {})
                    if node_data.get("dependency_status") != status_filter:
                        visible = False
                
                node_item.setHidden(not visible)
                if visible:
                    file_visible = True
            
            file_item.setHidden(not file_visible)
    
    def _on_selection_changed(self):
        """Handle tree selection changes to update preview and details."""
        selected_items = self.tree_widget.selectedItems()
        
        if not selected_items:
            self.details_text.clear()
            return
        
        item = selected_items[0]
        
        # Only show details for node items (not file groups)
        if isinstance(item, NodeLibraryItem) and item.node_data:
            node_data = item.node_data
            
            # Update preview
            self.preview_widget.set_node_data(node_data)
            
            # Update details text
            details = []
            details.append(f"Title: {node_data.get('title', 'Unknown')}")
            details.append(f"Source: {node_data.get('source_filename', 'Unknown')}")
            
            description = node_data.get('description', '')
            if description:
                details.append(f"Description: {description}")
            
            # Dependency information
            dep_info = node_data.get('dependency_info', {})
            if dep_info:
                details.append("")
                details.append("Dependencies:")
                
                req_deps = dep_info.get('required_dependencies', [])
                if req_deps:
                    details.append(f"  Required: {', '.join(req_deps)}")
                
                opt_deps = dep_info.get('optional_dependencies', [])
                if opt_deps:
                    details.append(f"  Optional: {', '.join(opt_deps)}")
                
                missing_req = dep_info.get('missing_required', [])
                if missing_req:
                    details.append(f"  Missing Required: {', '.join(missing_req)}")
                
                missing_opt = dep_info.get('missing_optional', [])
                if missing_opt:
                    details.append(f"  Missing Optional: {', '.join(missing_opt)}")
            
            self.details_text.setText("\n".join(details))
        else:
            self.details_text.clear()
    
    def _start_drag(self, supported_actions):
        """Start drag operation for selected node."""
        selected_items = self.tree_widget.selectedItems()
        
        if not selected_items:
            return
        
        item = selected_items[0]
        
        # Only allow dragging node items (not file groups)
        if not isinstance(item, NodeLibraryItem) or not item.node_data:
            return
        
        # Create drag operation
        drag = QDrag(self.tree_widget)
        mime_data = QMimeData()
        
        # Set node data as JSON (filter out non-serializable data)
        clean_node_data = {}
        for key, value in item.node_data.items():
            # Skip non-serializable items added by scanner
            if key in ["dependency_info", "dependency_status", "has_missing_required", 
                      "has_missing_optional", "all_dependencies_satisfied", "source_file", "source_filename"]:
                continue
            clean_node_data[key] = value
        
        node_json = json.dumps(clean_node_data, indent=2)
        mime_data.setData("application/x-pyflowgraph-node", node_json.encode('utf-8'))
        
        # Set text representation
        title = item.node_data.get('title', 'Unknown Node')
        mime_data.setText(f"Node: {title}")
        
        drag.setMimeData(mime_data)
        
        # Create drag pixmap (simple representation)
        pixmap = QPixmap(100, 60)
        pixmap.fill(QColor(80, 80, 80, 180))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(5, 30, title[:12])
        painter.end()
        
        drag.setPixmap(pixmap)
        
        # Execute drag
        drag.exec(Qt.CopyAction)
    
    def _check_for_updates(self):
        """Check for updated files and refresh if needed."""
        try:
            updated_files = self.scanner.check_for_updates()
            if updated_files:
                self._populate_tree()
        except Exception:
            # Silently handle errors in background update
            pass
    
    def _refresh_cache(self):
        """Manually refresh the entire cache."""
        try:
            self.status_label.setText("Refreshing...")
            files_count = self.scanner.refresh_cache()
            self._populate_tree()
            self.status_label.setText(f"Refreshed {files_count} files")
        except Exception as e:
            self.status_label.setText(f"Refresh error: {e}")
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh: {e}")
    
    def _change_directory(self):
        """Allow user to change the library directory."""
        current_dir = self.scanner.examples_dir
        new_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Node Library Directory",
            current_dir
        )
        
        if new_dir and new_dir != current_dir:
            # Update scanner
            self.scanner.examples_dir = new_dir
            
            # Save to settings if we have access to main window
            main_window = self.parent()
            if hasattr(main_window, 'settings'):
                main_window.settings.setValue("library_directory", new_dir)
            
            # Refresh the tree
            self._refresh_cache()
            self.status_label.setText(f"Changed library to: {new_dir}")
    
    def get_scanner(self) -> NodeScanner:
        """Get the node scanner instance.
        
        Returns:
            The NodeScanner instance used by this panel
        """
        return self.scanner
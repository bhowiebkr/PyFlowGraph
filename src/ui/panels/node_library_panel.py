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
    QMessageBox, QComboBox, QSplitter, QTextEdit, QToolTip, QFileDialog,
    QSizePolicy
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
        self.setMinimumHeight(100)  # Set minimum height instead of fixed height
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        
        # Disable interaction - make it read-only for preview
        self.setDragMode(QGraphicsView.NoDrag)
        self.setInteractive(False)
        
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
            # Show missing optional packages
            dep_info = self.node_data.get("dependency_info", {})
            missing_optional = dep_info.get("missing_optional", [])
            if missing_optional:
                # Show first few missing packages
                display_packages = missing_optional[:2]
                status_text = f"Missing: {', '.join(display_packages)}"
                if len(missing_optional) > 2:
                    status_text += f" (+{len(missing_optional) - 2} more)"
                self.setText(1, status_text)
            else:
                self.setText(1, "WARN")
            self.setForeground(1, QColor(200, 150, 50))
        elif status == DependencyStatus.REQUIRED_MISSING:
            # Show missing required packages instead of just "ERROR"
            dep_info = self.node_data.get("dependency_info", {})
            missing_required = dep_info.get("missing_required", [])
            if missing_required:
                # Show first few missing packages
                display_packages = missing_required[:2]
                status_text = f"Missing: {', '.join(display_packages)}"
                if len(missing_required) > 2:
                    status_text += f" (+{len(missing_required) - 2} more)"
                self.setText(1, status_text)
            else:
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
        
        # Top row: Refresh and Change Directory buttons at the very top
        top_button_row = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_cache)
        refresh_btn.setStyleSheet("QPushButton { border: 1px solid #555; padding: 6px 12px; background: #4a4a4a; color: white; } QPushButton:hover { background: #5a5a5a; }")
        top_button_row.addWidget(refresh_btn)
        
        # Directory button
        dir_btn = QPushButton("Change Directory")
        dir_btn.clicked.connect(self._change_directory)
        dir_btn.setStyleSheet("QPushButton { border: 1px solid #555; padding: 6px 12px; background: #4a6a9e; color: white; } QPushButton:hover { background: #5a7aae; }")
        top_button_row.addWidget(dir_btn)
        
        # Add stretch to push buttons to the left
        top_button_row.addStretch()
        
        layout.addLayout(top_button_row)
        
        # Search section
        search_layout = QVBoxLayout()
        
        # Search row: search box and status filter
        search_row = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search nodes...")
        self.search_box.textChanged.connect(self._filter_tree)
        self.search_box.setStyleSheet("QLineEdit { border: 1px solid #555; padding: 4px; background: #3a3a3a; color: white; }")
        search_row.addWidget(self.search_box)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Nodes", None)
        self.status_filter.addItem("Available", DependencyStatus.SATISFIED)
        self.status_filter.addItem("Missing Optional", DependencyStatus.OPTIONAL_MISSING)
        self.status_filter.addItem("Missing Required", DependencyStatus.REQUIRED_MISSING)
        self.status_filter.currentTextChanged.connect(self._filter_tree)
        self.status_filter.setStyleSheet("QComboBox { border: 1px solid #555; padding: 4px; background: #3a3a3a; color: white; }")
        self.status_filter.setMaximumWidth(120)
        search_row.addWidget(self.status_filter)
        
        search_layout.addLayout(search_row)
        
        layout.addLayout(search_layout)
        
        # Main content splitter
        self.splitter = QSplitter(Qt.Vertical)
        
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
        
        self.splitter.addWidget(self.tree_widget)
        
        # Info panel
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(2, 2, 2, 2)  # Reduce side margins
        
        # Details text first (description)
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(150)
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #555;
                background: #2a2a2a;
                color: white;
                padding: 3px 2px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
        """)
        info_layout.addWidget(self.details_text)
        
        # Preview widget below description (no label needed)
        self.preview_widget = NodePreviewWidget()
        self.preview_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        info_layout.addWidget(self.preview_widget, 1)  # Give it stretch factor of 1
        
        self.splitter.addWidget(info_widget)
        
        # Load saved splitter state or set default proportions
        self._load_splitter_state()
        
        # Connect splitter moved signal to save state
        self.splitter.splitterMoved.connect(self._save_splitter_state)
        
        layout.addWidget(self.splitter)
        
    
    def _populate_tree(self):
        """Populate the tree with nodes from examples."""
        self.tree_widget.clear()
        
        try:
            # Update status
            
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
            
        except Exception as e:
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
            
            # Update details text with HTML formatting and colors
            details = []
            
            # Title with blue color for labels, white for values
            title = node_data.get('title', 'Unknown')
            details.append(f"<span style='color: #6ab7ff;'><b>Title:</b></span> <span style='color: #ffffff;'>{title}</span>")
            
            # Source file with green color
            source = node_data.get('source_filename', 'Unknown')
            details.append(f"<span style='color: #6ab7ff;'><b>Source:</b></span> <span style='color: #90ee90;'>{source}</span>")
            
            # Description with lighter text
            description = node_data.get('description', '')
            if description:
                details.append(f"<span style='color: #6ab7ff;'><b>Description:</b></span><br><span style='color: #d0d0d0;'>{description}</span>")
            
            # Dependency information
            dep_info = node_data.get('dependency_info', {})
            if dep_info:
                details.append("")
                details.append("<span style='color: #ffa500;'><b>Dependencies:</b></span>")
                
                req_deps = dep_info.get('required_dependencies', [])
                if req_deps:
                    deps_text = ', '.join(req_deps)
                    details.append(f"  <span style='color: #6ab7ff;'>Required:</span> <span style='color: #ffffff;'>{deps_text}</span>")
                
                opt_deps = dep_info.get('optional_dependencies', [])
                if opt_deps:
                    deps_text = ', '.join(opt_deps)
                    details.append(f"  <span style='color: #6ab7ff;'>Optional:</span> <span style='color: #cccccc;'>{deps_text}</span>")
                
                missing_req = dep_info.get('missing_required', [])
                if missing_req:
                    deps_text = ', '.join(missing_req)
                    details.append(f"  <span style='color: #ff6b6b;'>Missing Required:</span> <span style='color: #ff9999;'>{deps_text}</span>")
                
                missing_opt = dep_info.get('missing_optional', [])
                if missing_opt:
                    deps_text = ', '.join(missing_opt)
                    details.append(f"  <span style='color: #ffaa55;'>Missing Optional:</span> <span style='color: #ffcc88;'>{deps_text}</span>")
            
            # Set HTML content
            html_content = "<br>".join(details)
            self.details_text.setHtml(html_content)
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
            files_count = self.scanner.refresh_cache()
            self._populate_tree()
        except Exception as e:
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
    
    def get_scanner(self) -> NodeScanner:
        """Get the node scanner instance.
        
        Returns:
            The NodeScanner instance used by this panel
        """
        return self.scanner

    
    def _load_splitter_state(self):
        """Load saved splitter state from settings."""
        # Try to get settings from main window
        main_window = self.parent()
        if hasattr(main_window, 'settings'):
            saved_state = main_window.settings.value("library_splitter_state")
            if saved_state:
                try:
                    # Convert saved state to list of integers
                    sizes = [int(x) for x in saved_state.split(',')]
                    if len(sizes) == 2 and all(s > 0 for s in sizes):
                        self.splitter.setSizes(sizes)
                        return
                except (ValueError, AttributeError):
                    pass
        
        # Fall back to default sizes if no valid saved state
        self.splitter.setSizes([300, 150])
    
    def _save_splitter_state(self):
        """Save current splitter state to settings."""
        # Try to get settings from main window
        main_window = self.parent()
        if hasattr(main_window, 'settings'):
            sizes = self.splitter.sizes()
            state_string = ','.join(str(size) for size in sizes)
            main_window.settings.setValue("library_splitter_state", state_string)

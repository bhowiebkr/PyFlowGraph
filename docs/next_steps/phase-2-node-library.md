# Phase 2: Node Library System

## Task Overview

This phase introduces a comprehensive node library system that fundamentally changes how users discover and add nodes to their graphs. The primary goal is to create an intuitive, searchable library panel that automatically scans and organizes available nodes from the examples directory, making node discovery effortless and efficient.

The system transforms PyFlowGraph from requiring manual node creation to providing a rich library of pre-built nodes that users can browse, search, and drag directly into their workspace. This addresses one of the key usability challenges in node-based editors - discovering what functionality is available and how to access it quickly.

## Implementation Goals

**Node Scanning System**: Create an automated scanning system that discovers and parses node definitions from markdown files in the examples directory. This system will maintain a cached registry of available nodes, automatically detecting when files change and updating the library accordingly.

**Library Panel Widget**: Implement a dockable panel featuring a hierarchical tree view that organizes nodes by source file and category. The panel will include node previews, descriptions, and visual thumbnails to help users quickly identify the functionality they need.

**Drag & Drop Implementation**: Enable seamless node creation through drag and drop from the library to the editor canvas. Users can simply drag a node from the library and drop it onto their graph at the desired location, with the system handling all the complexity of node instantiation and positioning.

**Search Functionality**: Provide real-time search capabilities across all available nodes, allowing users to quickly filter by name, description, or functionality. This makes large node libraries manageable and helps users discover relevant nodes without browsing through extensive hierarchies.

The overall objective is to transform node creation from a manual, code-centric process to an intuitive, visual workflow that encourages exploration and rapid prototyping. This system serves as the foundation for a user-friendly node editing experience that scales from simple graphs to complex workflows.

## Node Scanner System with Dependency Detection

### Implementation Target: `src/core/node_scanner.py` (NEW)

**Core functionality:**
```python
class NodeScanner:
    def __init__(self, examples_dir="examples"):
        self.examples_dir = examples_dir
        self.cache = {}
        self.file_timestamps = {}
        self.dependency_checker = DependencyChecker()
    
    def scan_nodes(self):
        # Scan .md files in examples/
        # Parse using existing flow format
        # Extract dependencies from metadata and code
        # Return dict: {filepath: [nodes_with_dependencies]}
    
    def parse_node_from_md(self, content):
        # Extract nodes from markdown
        # Use existing parser from flow loading
        # Parse node-level dependencies from metadata
        # Fall back to import scanning if no explicit dependencies
        # Return node metadata + code + dependencies
```

**Dependency resolution priority:**
1. Node-specific dependencies from metadata (highest priority)
2. Graph-level dependencies (fallback)
3. Import scanning from node code (automatic detection)

**Integration with existing flow parser:**
- Reuse parsing logic from file operations
- Extract node definitions without creating instances
- Store metadata: title, description, pins, code, **dependencies**

## Library Panel Widget

### Implementation Target: `src/ui/panels/node_library_panel.py` (NEW)

**Base structure:**
```python
class NodeLibraryPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Node Library", parent)
        self.scanner = NodeScanner()
        self.tree_widget = QTreeWidget()
        self.search_box = QLineEdit()
        self._setup_ui()
        self._populate_tree()
```

**Tree structure:**
- Top level: source files (basic_math.md, image_processing.md)
- Children: individual nodes with previews and dependency status
- Use QTreeWidgetItem with custom data including dependency info

**Dependency Status Visual Indicators:**
- ✓ Green icon: All dependencies satisfied
- ⚠ Yellow icon: Optional dependencies missing  
- ✗ Red icon: Required dependencies missing
- Tooltip showing exact requirements and what's missing

**Preview generation:**
- Create mini QGraphicsView (100x60px)
- Render node without full instantiation
- Overlay dependency status icon on preview
- Cache previews by node signature + dependency state

## Drag & Drop Implementation

### Source: `src/ui/panels/node_library_panel.py`
### Target: `src/ui/editor/node_editor_view.py`

**Drag start (Library Panel):**
```python
def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
        item = self.tree_widget.itemAt(event.pos())
        if item and item.node_data:
            self._start_drag(item.node_data)

def _start_drag(self, node_data):
    drag = QDrag(self)
    mime_data = QMimeData()
    mime_data.setData("application/x-pyflowgraph-node", 
                     json.dumps(node_data).encode())
    drag.setMimeData(mime_data)
    drag.exec_(Qt.CopyAction)
```

**Pre-drop Dependency Validation:**
- Check dependency status before allowing drop
- Show warning dialog if required dependencies missing
- Offer options: "Install Dependencies", "Cancel", "Create Anyway"

**Drop handling (NodeEditorView):**
- Add to existing mousePressEvent() and dropEvent()
- Check for "application/x-pyflowgraph-node" MIME type  
- Validate dependencies before node creation
- Create node at drop position using existing node creation logic
- Use NodeEditorWindow.on_add_node() pattern

**Node creation integration:**
- Extract code and dependencies from MIME data
- Validate environment compatibility
- Create Node instance at drop coordinates
- Add to scene using existing graph.add_node() method

## Search Functionality

### Implementation Target: `src/ui/panels/node_library_panel.py`

**Search widget:**
```python
def _setup_search(self):
    self.search_box.textChanged.connect(self._filter_tree)
    self.search_box.setPlaceholderText("Search nodes...")

def _filter_tree(self, text):
    iterator = QTreeWidgetItemIterator(self.tree_widget)
    while iterator.value():
        item = iterator.value()
        self._update_item_visibility(item, text.lower())
        iterator += 1
```

**Filtering logic:**
- Hide/show items based on name and description match
- Filter by dependency status (compatible only, all, etc.)
- Expand parent items when children match
- Use existing Qt item flags for visibility

## Dependency Checker System

### Implementation Target: `src/core/dependency_checker.py` (NEW)

**Core functionality:**
```python
class DependencyChecker:
    def __init__(self, venv_path=None):
        self.venv_path = venv_path
        self.import_to_package_map = {
            "cv2": "opencv-python", 
            "PIL": "pillow",
            "torch": "torch",
            # ... more mappings
        }
    
    def check_node_dependencies(self, node_data):
        # Check explicit dependencies from metadata
        # Fall back to import scanning if none specified
        # Return dependency status with details
    
    def scan_imports_from_code(self, code):
        # Use AST to extract import statements
        # Map imports to package names
        # Return list of required packages
    
    def validate_package_availability(self, packages):
        # Check if packages exist in current venv
        # Validate version requirements
        # Return status for each package
```

**Per-Node Dependencies in Metadata:**
```json
{
  "uuid": "image-processor",
  "title": "Image Processor", 
  "dependencies": ["pillow>=8.0.0", "numpy"],
  "optional_dependencies": ["opencv-python"],
  "pos": [0, 0],
  "size": [250, 150],
  ...
}
```

## Integration with Main Window

### Implementation Target: `src/ui/editor/node_editor_window.py`

**Add to _setup_ui() method:**
```python
# Around line 85, after existing setup
self.library_panel = NodeLibraryPanel(self)
self.addDockWidget(Qt.RightDockWidgetArea, self.library_panel)
```

**Window menu integration:**
- Add to _create_menus() method
- Toggle visibility action
- Save state in QSettings

## File Monitoring

### Implementation Target: `src/core/node_scanner.py`

**Hot reload support:**
```python
def check_for_updates(self):
    for filepath in self.file_timestamps:
        current_time = os.path.getmtime(filepath)
        if current_time > self.file_timestamps[filepath]:
            self._reload_file(filepath)
            self.file_timestamps[filepath] = current_time
```

**Integration:**
- Use QTimer for periodic checks (every 2 seconds)
- Signal library panel to refresh tree
- Maintain selection state during refresh

## Performance Optimizations

**Lazy loading:**
- Load node previews only when tree items are expanded
- Cache parsed results until file changes
- Limit preview generation to visible items

**Memory management:**
- Clear unused previews after time limit
- Reuse QGraphicsView instances
- Batch tree updates to prevent UI lag

## Dependencies

**Existing systems to leverage:**
- Flow format parser (file operations)
- Node creation (NodeGraph.add_node)
- QSettings (window state persistence)
- Command system (for undo/redo of node creation)
# Phase 3: GUI Layout Improvements

## Task Overview

This phase focuses on modernizing PyFlowGraph's user interface layout to create a more professional and efficient workspace. The primary goal is to replace traditional menu-driven interfaces with contemporary floating elements and collapsible panels that maximize screen real estate while maintaining accessibility to essential functions.

The phase transforms the application from a conventional desktop application layout to a modern, streamlined interface that prioritizes the node editing canvas while keeping tools and information readily accessible. This includes introducing floating toolbars, reorganizing output displays, and adding smooth animations that enhance the overall user experience.

## Implementation Goals

**Floating Toolbar**: Replace the traditional toolbar with a semi-transparent floating overlay positioned in the top-left corner. This approach frees up valuable screen space while keeping essential tools (New, Save, Load, Undo, Redo, Clear) easily accessible with improved visual styling and hover effects.

**Collapsible Output Panel**: Redesign the output system by moving it from a bottom dock to a collapsible right-side panel with colored text support for different message types (errors, warnings, success, info). This provides better organization and allows users to hide output when not needed.

**Animation System**: Implement smooth transitions and animations throughout the interface using QPropertyAnimation. This includes expand/collapse animations for panels, fade effects for UI elements, and smooth resizing operations that create a polished, professional feel.

**Window Management Menu**: Add comprehensive window management capabilities through a new View menu that allows users to toggle panel visibility, reset layouts, and customize their workspace. This includes keyboard shortcuts and persistent state saving for user preferences.

The overall objective is to create a modern, efficient workspace that adapts to different workflow needs while maintaining the powerful functionality that makes PyFlowGraph effective. The new layout emphasizes the node editor canvas while providing sophisticated tools for managing complex projects.

## Floating Toolbar

### Implementation Target: `src/ui/editor/node_editor_window.py`

**Replace existing toolbar system:**
- Current `_create_toolbar()` method (line 189-216) creates QToolBar
- Replace with floating overlay widget

**Floating toolbar widget:**
```python
class FloatingToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        # Add icon buttons: New, Save, Load, Undo, Redo, Clear
        self.setLayout(layout)
```

**Integration:**
- Create in `_setup_ui()` method
- Position in top-left corner: `setGeometry(10, 10, 250, 50)`
- Connect to existing actions (action_new, action_save, etc.)
- Maintain existing keyboard shortcuts

**Button styling:**
- Use existing QSS styles
- Add hover effects and tooltips
- Semi-transparent background

## Collapsible Output Panel

### Implementation Target: `src/ui/panels/output_panel.py` (NEW)

**Panel structure:**
```python
class OutputPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Output", parent)
        self.text_widget = QTextEdit()
        self.is_collapsed = False
        self._setup_ui()
    
    def _setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout()
        
        # Header with collapse button
        header = self._create_header()
        layout.addWidget(header)
        layout.addWidget(self.text_widget)
        
        container.setLayout(layout)
        self.setWidget(container)
```

**Colored text support:**
```python
def log_message(self, message, level="info"):
    colors = {
        "error": "red",
        "warning": "yellow", 
        "success": "green",
        "info": "gray"
    }
    self.text_widget.setTextColor(QColor(colors[level]))
    self.text_widget.append(message)
```

**Integration with existing output_log:**
- Current: QTextEdit in bottom dock (node_editor_window.py line 73)
- Replace with OutputPanel in right dock area
- Maintain existing logging interface

## Animation System

### Implementation Target: `src/core/group.py` and UI files

**Base animation class:**
```python
class AnimationManager:
    @staticmethod
    def animate_expand(widget, start_size, end_size, duration=250):
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_size)
        animation.setEndValue(end_size)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        return animation
    
    @staticmethod
    def animate_fade(widget, start_opacity, end_opacity, duration=200):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        return animation
```

**Group expand/collapse:**
- Add to Group class methods for smooth size changes
- Animate width/height properties
- Use QPropertyAnimation with OutCubic easing

**Panel animations:**
- Fade-in/fade-out for dock widgets
- Smooth resize for collapsible panels
- 200-300ms duration for responsive feel

## Window Management Menu

### Implementation Target: `src/ui/editor/node_editor_window.py`

**Add to _create_menus() method:**
```python
# Around line 160, add new menu
view_menu = self.menuBar().addMenu("&View")
view_menu.addAction("&Output Panel", self._toggle_output_panel)
view_menu.addAction("&Node Library", self._toggle_library_panel)
view_menu.addAction("&Status Bar", self.statusBar().setVisible)
view_menu.addSeparator()
view_menu.addAction("&Reset Layout", self._reset_layout)
```

**Toggle methods:**
```python
def _toggle_output_panel(self):
    panel = self.output_panel
    panel.setVisible(not panel.isVisible())

def _toggle_library_panel(self):
    panel = self.library_panel  
    panel.setVisible(not panel.isVisible())

def _reset_layout(self):
    self.restoreState(self._get_default_layout_state())
```

**State persistence:**
- Use existing QSettings (line 51)
- Save panel visibility and positions
- Restore on startup

**Keyboard shortcuts:**
```python
# Add to _create_actions() method
QShortcut(QKeySequence("Ctrl+1"), self, self._toggle_output_panel)
QShortcut(QKeySequence("Ctrl+2"), self, self._toggle_library_panel)
```

## Layout Reorganization

### Implementation Target: `src/ui/editor/node_editor_window.py`

**Current layout (_setup_ui method line 82-86):**
- Central widget: view (QGraphicsView)
- Bottom dock: output_log

**New layout:**
- Central widget: view (unchanged)
- Right dock: library_panel (from Phase 2)
- Right dock: output_panel (collapsible)
- Floating: toolbar overlay

**Dock arrangement:**
```python
def _setup_dock_layout(self):
    # Library panel on top-right
    self.addDockWidget(Qt.RightDockWidgetArea, self.library_panel)
    
    # Output panel below library
    self.addDockWidget(Qt.RightDockWidgetArea, self.output_panel)
    
    # Split right area vertically
    self.splitDockWidget(self.library_panel, self.output_panel, 
                        Qt.Vertical)
```

## Theme Integration

**Use existing QSS styling:**
- Match current color scheme
- Semi-transparent elements for floating toolbar
- Consistent fonts and spacing
- Hover states and transitions

**Animation compatibility:**
- Ensure animations work with QSS styles
- Test with different themes
- Fallback for performance issues

## Performance Considerations

**Animation optimization:**
- Use QPropertyAnimation for GPU acceleration
- Limit concurrent animations
- Provide disable option in settings

**Memory management:**
- Reuse animation objects
- Clean up completed animations
- Limit panel content during animations

## Integration Points

**Existing systems:**
- QSettings for state persistence (line 51)
- Action system for menu integration (line 114-158)
- Current toolbar actions (line 189-216)
- Output logging system (line 73)

**Dependencies:**
- Node Library Panel (Phase 2)
- Font Awesome icons (existing)
- QSS styling system (existing)
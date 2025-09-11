# Phase 1: Visual Feedback & Interaction

## Task Overview

This phase focuses on improving the visual feedback and interaction system within PyFlowGraph's node editor. The primary goal is to enhance user experience by providing immediate visual responses to user actions, making the interface feel more responsive and intuitive. These improvements establish the foundation for a professional-grade node editing experience.

The phase encompasses four main areas: pin hover effects, cursor state management, connection hover effects, and temporary connection visualization. Additionally, it includes implementing node performance metrics display to give users insight into execution timing. These features work together to create a more polished and informative user interface that responds dynamically to user interactions.

## Implementation Goals

**Pin Hover Effects**: Implement visual highlighting when users hover over pins, providing clear feedback about interactive elements. This involves adding hover event handlers to the Pin class and modifying the paint method to show brightness increases or glow effects when pins are under the cursor.

**Cursor Management**: Create an intelligent cursor system that changes based on context - showing crosshair cursors when hovering over pins while maintaining existing cursors for dragging and resizing operations. This requires updating the NodeEditorView to track cursor states and respond appropriately to different UI elements.

**Connection Hover Effects**: Add visual feedback for connections when users hover over them, including highlighting effects and potential tooltips showing data type information. This makes it easier for users to understand the data flow and interact with connections in complex graphs.

**Temporary Connection Visualization**: Implement a dynamic preview system that shows dashed lines during connection creation, giving users real-time feedback about where their connections will land. This improves the connection creation process by making it more predictable and user-friendly.

**Performance Metrics**: Display execution timing information directly on nodes, showing users how long each node takes to execute. This provides valuable feedback for optimization and helps users understand the performance characteristics of their graphs.

## Pin Hover Effects

### Implementation Target: `src/core/pin.py`

Pin class (line 14-186) has existing methods:
- `paint()` (line 122-125) - visual rendering
- `update_visual_state()` (line 103-117) - state updates
- `boundingRect()` (line 119-120) - collision detection

**Add hover methods:**
```python
def hoverEnterEvent(self, event):
    self.hover_state = True
    self._apply_hover_effect()
    self.update()

def hoverLeaveEvent(self, event):
    self.hover_state = False
    self._remove_hover_effect()
    self.update()

def _apply_hover_effect(self):
    # Option 1: Glow effect using QGraphicsDropShadowEffect
    glow_effect = QGraphicsDropShadowEffect()
    glow_effect.setColor(self.color.lighter(150))
    glow_effect.setBlurRadius(10)
    glow_effect.setOffset(0, 0)  # Center the glow
    self.setGraphicsEffect(glow_effect)

def _remove_hover_effect(self):
    self.setGraphicsEffect(None)
```

**Alternative approach (brightness only):**
```python
def _apply_hover_effect(self):
    # Option 2: Simple brightness increase in paint()
    self.update()  # Triggers repaint with hover state

# In paint() method:
if hasattr(self, 'hover_state') and self.hover_state:
    color = self.color.lighter(130)
    brush = QBrush(color)
    painter.setBrush(brush)
```

## Cursor Management

### Implementation Target: `src/ui/editor/node_editor_view.py`

NodeEditorView class has existing mouse handlers:
- `mousePressEvent()` (line 184-235)
- `mouseMoveEvent()` (line 237-259)
- `mouseReleaseEvent()` (line 261-283)

**Add cursor tracking:**
```python
def _update_cursor_for_item(self, item):
    if isinstance(item, Pin):
        self.setCursor(Qt.CrossCursor)
    else:
        self.setCursor(Qt.ArrowCursor)
```

**Integrate in mouseMoveEvent()** - call after line 240

## Connection Hover Effects

### Implementation Target: `src/core/connection.py`

Connection class (line 8-94) has:
- `paint()` method (line 63-68)
- `_pen` and `_pen_selected` properties (lines 21, 23)

**Add hover detection:**
```python
def hoverEnterEvent(self, event):
    self.hover_state = True
    self.setZValue(1)  # Bring to front
    self._apply_hover_effect()

def hoverLeaveEvent(self, event):
    self.hover_state = False
    self.setZValue(0)
    self._remove_hover_effect()

def _apply_hover_effect(self):
    # Option 1: Glow effect for connections
    glow_effect = QGraphicsDropShadowEffect()
    glow_effect.setColor(self.color.lighter(200))
    glow_effect.setBlurRadius(8)
    glow_effect.setOffset(0, 0)
    self.setGraphicsEffect(glow_effect)

def _remove_hover_effect(self):
    self.setGraphicsEffect(None)
```

**Alternative approach (thicker line):**
```python
def _apply_hover_effect(self):
    # Option 2: Thicker line in paint()
    self.update()

# In paint() method:
if hasattr(self, 'hover_state') and self.hover_state:
    hover_pen = QPen(self.color, 3)
    painter.setPen(hover_pen)
else:
    painter.setPen(self._pen)
```

## Temporary Connection Visualization

### Implementation Target: `src/core/node_graph.py`

Add TempConnection class:
```python
class TempConnection(QGraphicsPathItem):
    def __init__(self, start_pos):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = start_pos
        pen = QPen(QColor(100, 100, 100), 2, Qt.DashLine)
        self.setPen(pen)
    
    def update_end_pos(self, pos):
        self.end_pos = pos
        # Update path using existing Connection.update_path() logic
```

**Integration points:**
- Start in Pin.mousePressEvent()
- Update in NodeEditorView.mouseMoveEvent()
- Convert to Connection on successful drop

## Node Performance Metrics

### Implementation Target: `src/core/node.py`

Node class has:
- `paint()` method (line 420-447)
- Existing properties for visual state

**Add execution time property:**
```python
self.execution_time = None  # Add to __init__ around line 60
```

**Modify paint() method:**
- Add time display at bottom of node
- Format: "Execution: X.XXms"
- Use small gray font (QFont size 8)
- Position below existing content

**Update from executor:**
- SingleProcessExecutor should set node.execution_time
- Update after each node execution
- Handle None case (not executed yet)

## Implementation Notes

**QGraphicsItem Requirements:**
- All hover events require `setAcceptHoverEvents(True)` in constructors
- Call in Pin.__init__(), Connection.__init__()
- Import QGraphicsDropShadowEffect from PySide6.QtWidgets

**Performance Considerations:**
- QGraphicsDropShadowEffect can impact performance with many items
- Consider using simple brightness/thickness changes for better performance
- Each item needs its own QGraphicsDropShadowEffect instance
- Use update() only on changed items, avoid full scene repaints

**Effect Limitations:**
- Only one QGraphicsEffect can be applied per item at a time
- Effects may increase bounding rectangle size (requires updateBoundingRect())
- setGraphicsEffect(None) removes any existing effect

**Integration Points:**
- Pin hover enables cursor changes
- Connection hover shows tooltips
- Temp connections use existing path calculation
- Performance metrics update from execution system
- Test both glow and simple brightness approaches for best performance
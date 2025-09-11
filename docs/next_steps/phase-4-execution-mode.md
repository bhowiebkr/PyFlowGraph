# Phase 4: Execution Mode Simplification

## Task Overview

This phase focuses on simplifying PyFlowGraph's execution model to make it more accessible to users while maintaining the power and flexibility needed for complex workflows. The primary goal is to hide execution complexity behind intelligent defaults and auto-detection, allowing users to focus on building their graphs rather than configuring execution modes.

The phase transforms the execution system from requiring users to understand and choose between different execution modes to an intelligent system that automatically selects the most appropriate execution strategy based on graph characteristics. This includes providing clear visual feedback about system status and ready-to-run states.

## Implementation Goals

**Event-Driven Default Mode**: Establish event-driven execution as the default behavior, providing immediate feedback as users build and modify their graphs. The system will automatically detect when batch mode is more appropriate (large graphs, heavy computation) and switch modes transparently while informing the user of the change.

**Batch Mode Run Button**: Introduce a floating run button that appears only when the system is in batch mode, positioned prominently on the right side of the interface. The button includes visual states (ready, running, error) and pulse animations to clearly communicate when the graph is ready for execution.

**Environment Status Indicator**: Implement a real-time status indicator that continuously monitors the execution environment, showing users whether their system is ready to run (green), has issues that need attention (red), or has warnings (orange). This includes checking virtual environments, dependencies, and syntax errors.

**Settings Simplification**: Move execution mode controls to an advanced settings section, ensuring that most users never need to think about execution modes while still providing power users with full control over the system behavior.

The overall objective is to create an execution system that "just works" for most users while providing sophisticated control for advanced scenarios. The system should feel responsive and intelligent, automatically handling complexity while providing clear feedback about system state and readiness.

## Event-Driven Default Mode

### Implementation Target: `src/execution/execution_controller.py`

**Current execution modes:**
- ExecutionController class manages mode switching
- Default should be event-driven (live execution)
- Hide mode complexity from basic users

**Mode simplification:**
```python
def __init__(self, graph, output_callback=None):
    # Set event-driven as default
    self.default_mode = "event_driven"
    self.current_mode = self.default_mode
    self.auto_detect_batch = True
```

**Auto-detection logic:**
```python
def should_use_batch_mode(self, graph):
    # Check for batch indicators:
    # - Large number of nodes (>50)
    # - Heavy computation nodes
    # - User preference override
    node_count = len(graph.nodes)
    return node_count > 50 or self._has_heavy_computation()
```

**Settings integration:**
- Move mode toggle to advanced section
- Most users never see execution mode options
- Advanced users can override auto-detection

## Batch Mode Run Button

### Implementation Target: `src/execution/execution_controller.py`

**Floating run button widget:**
```python
class BatchRunButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.button = QPushButton("Run")
        self.progress = QProgressBar()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        self.button.setStyleSheet("background: #4CAF50; color: white;")
        layout.addWidget(self.button)
        layout.addWidget(self.progress)
        self.setLayout(layout)
```

**Positioning:**
- Right side of editor view
- Below node library panel
- Only visible in batch mode
- Fixed position, not dockable

**Button states:**
```python
def update_button_state(self, state):
    states = {
        "ready": {"text": "Run", "color": "#4CAF50", "enabled": True},
        "running": {"text": "Running...", "color": "#FF9800", "enabled": False},
        "error": {"text": "Error", "color": "#F44336", "enabled": True}
    }
    self.button.setText(states[state]["text"])
    # Update styling and enabled state
```

**Pulse animation:**
```python
def start_pulse_animation(self):
    self.pulse_animation = QPropertyAnimation(self, b"windowOpacity")
    self.pulse_animation.setDuration(1000)
    self.pulse_animation.setStartValue(1.0)
    self.pulse_animation.setEndValue(0.7)
    self.pulse_animation.setLoopCount(-1)  # Infinite
    self.pulse_animation.start()
```

## Environment Status Indicator

### Implementation Target: `src/execution/execution_controller.py` and `src/ui/editor/node_editor_window.py`

**Status indicator widget:**
```python
class EnvironmentStatusIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_dot = QLabel()
        self.status_text = QLabel()
        self._setup_ui()
    
    def update_status(self, status, message=""):
        colors = {
            "ready": "#4CAF50",      # Green
            "error": "#F44336",      # Red  
            "warning": "#FF9800",    # Orange
            "checking": "#2196F3"    # Blue
        }
        self._set_dot_color(colors[status])
        self.setToolTip(message)
```

**Status checking logic:**
```python
def check_environment_status(self):
    status = "ready"
    message = "Environment ready"
    
    # Check virtual environment
    if not self._venv_exists():
        status = "error"
        message = "Virtual environment not found"
    
    # Check dependencies
    elif not self._dependencies_satisfied():
        status = "error" 
        message = "Missing dependencies"
    
    # Check syntax errors
    elif self._has_syntax_errors():
        status = "warning"
        message = "Syntax errors in code"
    
    return status, message
```

**Integration with main window:**
- Add to toolbar area (replace existing toolbar)
- Position: top-right corner
- Update in real-time when code changes
- Use QTimer for periodic checks

**Environment checking:**
- Virtual environment existence
- Required packages installed
- Python syntax validation
- Import statement resolution

## Settings Dialog Updates

### Implementation Target: `src/ui/dialogs/settings_dialog.py`

**Hide execution mode:**
- Move to "Advanced" tab or section
- Default users don't see mode options
- Auto-detection handles most cases

**Advanced section:**
```python
def _create_advanced_tab(self):
    tab = QWidget()
    layout = QVBoxLayout()
    
    # Execution mode override
    self.execution_mode_group = QGroupBox("Execution Mode (Advanced)")
    self.auto_mode = QRadioButton("Auto-detect (Recommended)")
    self.event_mode = QRadioButton("Event-driven")
    self.batch_mode = QRadioButton("Batch")
    
    # Environment checking
    self.env_check_interval = QSpinBox()
    self.env_check_interval.setRange(1, 30)
    self.env_check_interval.setValue(5)
    
    layout.addWidget(self.execution_mode_group)
    tab.setLayout(layout)
    return tab
```

## Performance Integration

### Implementation Target: `src/execution/single_process_executor.py`

**Execution timing:**
- SingleProcessExecutor already tracks performance
- Expose execution_times dictionary
- Update node.execution_time after each run

**Status updates:**
```python
def execute_node(self, node):
    start_time = time.perf_counter()
    try:
        result = self._run_node_function(node)
        execution_time = (time.perf_counter() - start_time) * 1000
        node.execution_time = execution_time
        return result
    except Exception as e:
        node.execution_time = None
        raise e
```

**Batch progress tracking:**
```python
def execute_batch(self, nodes, progress_callback=None):
    total_nodes = len(nodes)
    for i, node in enumerate(nodes):
        self.execute_node(node)
        if progress_callback:
            progress_callback(i + 1, total_nodes)
```

## Mode Transition Logic

### Implementation Target: `src/execution/execution_controller.py`

**Automatic switching:**
```python
def update_execution_mode(self, graph):
    if self.auto_detect_batch:
        recommended_mode = self._recommend_mode(graph)
        if recommended_mode != self.current_mode:
            self._switch_mode(recommended_mode)
            self._notify_mode_change(recommended_mode)

def _recommend_mode(self, graph):
    # Analyze graph complexity
    # Check for batch indicators
    # Return recommended mode
    pass
```

**User notification:**
- Status bar message when mode changes
- Option to permanently override
- Clear explanation of why mode changed

## Integration Points

**Existing systems:**
- ExecutionController mode management
- Environment management (default_env_manager)
- Settings persistence (QSettings)
- Node execution timing (single_process_executor)

**UI integration:**
- Main window toolbar area
- Settings dialog advanced section  
- Right-side floating widgets
- Status bar notifications

**Dependencies:**
- Environment manager system
- Settings dialog framework
- Animation system (Phase 3)
- Node performance tracking (Phase 1)
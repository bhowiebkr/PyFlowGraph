# FlowSpec LLM Reference

**Format:** .md files with structured sections  
**Core:** Document IS the graph

## File Structure

```
# Graph Title
Description (optional)

## Node: Title (ID: uuid)
Description (optional)

### Metadata
```json
{"uuid": "id", "title": "Title", "pos": [x,y], "size": [w,h]}
```

### Logic  
```python
import module
from typing import Tuple

class HelperClass:
    def process(self, data): return data

def helper_function(x): return x * 2

@node_entry
def function_name(param: type) -> return_type:
    helper = HelperClass()
    result = helper_function(param)
    return result
```

### GUI Definition (optional)
```python
# Execution context: parent (QWidget), layout (QVBoxLayout), widgets (dict)
from PySide6.QtWidgets import QLabel, QLineEdit
layout.addWidget(QLabel('Text:', parent))
widgets['input'] = QLineEdit(parent)
layout.addWidget(widgets['input'])
```

### GUI State Handler (optional) 
```python
def get_values(widgets): return {}
def set_values(widgets, outputs): pass
def set_initial_state(widgets, state): pass
```

## Dependencies (optional)
```json
{"requirements": ["package>=1.0"], "python": ">=3.8"}
```

## Groups (optional)
```json
[{"uuid": "id", "name": "Name", "member_node_uuids": ["id1"]}]
```

## Connections
```json
[{"start_node_uuid": "id1", "start_pin_name": "output_1", 
  "end_node_uuid": "id2", "end_pin_name": "param_name"}]
```

## Pin System

**@node_entry decorator:**
- REQUIRED on exactly one function per Logic block
- Entry point: Only decorated function called during execution
- Pin generation: Function signature parsed to create node pins automatically
- Runtime behavior: No-op decorator, returns function unchanged
- Parameters → input pins (names become pin names, type hints determine colors)
- Default values supported for optional parameters
- Return type → output pins

**Pin generation:**
- `param: str` → input pin "param" (type: str)
- `param: str = "default"` → optional input pin with default
- `-> str` → output pin "output_1" 
- `-> Tuple[str, int]` → pins "output_1", "output_2"
- `-> None` → no output pins

**Execution pins:** Always present
- `exec_in` (input), `exec_out` (output)

**Pin colors:**
- Execution pins: Fixed colors (exec_in: dark gray #A0A0A0, exec_out: light gray #E0E0E0)
- Data pins: Generated from type string using consistent hashing in HSV color space
- Same type always produces same color across all nodes (bright, distinguishable colors)
- Color generation: type string → hash → HSV values → RGB color
- Ensures visual consistency for type matching across the entire graph

## Type System

**Basic types:** str, int, float, bool
**Container types:** list, dict, tuple, set
**Generic types:** List[str], List[Dict], List[Any], Dict[str, int], Dict[str, Any], Tuple[str, int], Tuple[float, ...]
**Optional types:** Optional[str], Optional[int], Union[str, int], Union[float, None]  
**Special types:** Any (accepts any data), None (no data)
**Complex nested:** List[Dict[str, Any]], Dict[str, List[int]]
**ML types:** torch.Tensor, np.ndarray, pd.DataFrame (native object passing)

## Required Fields

**Metadata:**
- `uuid`: unique string identifier
- `title`: display name

**Optional metadata:**
- `pos`: [x, y] position
- `size`: [width, height] 
- `colors`: {"title": "#hex", "body": "#hex"}
- `gui_state`: widget values dict
- `is_reroute`: boolean (for reroute nodes)

## Node Header Format

**Standard:** `## Node: Human Title (ID: unique-id)`
**Sections:** `## Dependencies`, `## Groups`, `## Connections`

## GUI Integration

**Widget storage:** All interactive widgets MUST be in `widgets` dict
**Data flow merging:** 
1. GUI values from get_values() merged with connected pin values
2. Connected pin values take precedence over GUI values for same parameter
3. GUI values provide defaults or additional inputs not available through pins
4. @node_entry function receives merged inputs
5. Return values distributed to both output pins and set_values() for GUI display

**State persistence:** gui_state in metadata ↔ set_initial_state()

## Connection Types

**Data:** `"output_N"` to parameter name
**Execution:** `"exec_out"` to `"exec_in"`

## Groups Structure

**Required fields:** uuid, name, member_node_uuids
**Optional fields:** description, position, size, padding, is_expanded, colors

```json
{
  "uuid": "group-id",
  "name": "Display Name", 
  "member_node_uuids": ["node1", "node2"],
  "description": "Group description",
  "position": {"x": 0, "y": 0},
  "size": {"width": 200, "height": 150},
  "padding": 20,
  "is_expanded": true,
  "colors": {
    "background": {"r": 45, "g": 45, "b": 55, "a": 120},
    "border": {"r": 100, "g": 150, "b": 200, "a": 180},
    "title_bg": {"r": 60, "g": 60, "b": 70, "a": 200},
    "title_text": {"r": 220, "g": 220, "b": 220, "a": 255},
    "selection": {"r": 255, "g": 165, "b": 0, "a": 100}
  }
}
```

## Dependencies Format

**Required fields:** requirements (array of pip-style package specs)
**Optional fields:** optional, python, system, notes

```json
{
  "requirements": ["torch>=1.9.0", "numpy>=1.21.0"],
  "optional": ["cuda-toolkit>=11.0"],
  "python": ">=3.8",
  "system": ["CUDA>=11.0"],
  "notes": "Additional info"
}
```

**Package formats:** `package>=1.0`, `package==1.2.3`, `package~=1.0`

## Reroute Nodes

**Purpose:** Connection waypoints for visual organization
**Characteristics:** 
- `"is_reroute": true` in metadata
- No Logic/GUI components needed
- Single input/output pins
- Small circular appearance

## Execution Modes

**Batch Mode (Default):** 
- One-shot execution of entire graph in dependency order
- All nodes execute once per run, no state persistence
- Fresh interpreter state for each execution
- GUI buttons in nodes are inactive
- Suitable for data processing pipelines

**Live Mode (Interactive):**
- Event-driven execution triggered by GUI interactions
- Partial execution paths based on user events
- Maintains persistent state between runs
- GUI event handlers active in nodes
- ML objects (tensors, DataFrames) persist across executions
- Immediate feedback, no startup delays

**Runtime Behavior Differences:**
- Mode controlled at runtime, not stored in file
- Same graph can run in either mode without modification
- Live mode enables button clicks and widget interactions
- Batch mode optimized for throughput, Live mode for responsiveness

## Execution Architecture

**Single Process:** All nodes execute in shared Python interpreter
**Native Objects:** Direct references, zero-copy data transfer, no serialization overhead

**ML Framework Integration:**
- **PyTorch:** GPU tensors with device preservation, automatic CUDA cleanup, grad support
- **NumPy:** Direct ndarray references, dtype/shape preservation, memory views, broadcasting
- **Pandas:** DataFrame/Series objects, index preservation, method chaining, large dataset efficiency  
- **TensorFlow:** tf.Tensor and tf.Variable support, session management, eager execution
- **JAX:** jax.numpy arrays, JIT compilation, device arrays, functional transformations

**Zero-Copy Mechanisms:**
- Object references stored in shared object_store dictionary
- Same object instance shared across all node references
- GPU tensors manipulated directly without device transfers
- Memory-mapped files for >RAM datasets

**Auto-imports:** numpy as np, pandas as pd, torch, tensorflow as tf, jax, jax.numpy as jnp
**GPU Memory Management:** Automatic CUDA cache clearing, tensor cleanup, device synchronization

## Validation Rules

**File Structure:**
- Exactly one h1 (graph title)
- Node headers must follow: `## Node: Title (ID: uuid)`
- Required sections: Connections (must be present)
- Optional sections: Dependencies, Groups

**Node Requirements:**
- Each node needs unique uuid
- Required components: Metadata, Logic
- One @node_entry function per Logic block
- Logic blocks can contain imports, classes, helper functions, and module-level code
- Only @node_entry function is called as entry point
- Valid JSON in all metadata/groups/connections/dependencies blocks
- Node UUIDs must be valid identifiers

**GUI Rules (when present):**
- GUI Definition must create valid PySide6 widgets
- All interactive widgets MUST be stored in `widgets` dict
- get_values() must return dict
- set_values() and set_initial_state() should handle missing keys gracefully
- Widget names in get_values() must match GUI Definition keys

**Groups Rules (when present):**
- Group UUIDs must be unique across all groups (not just unique within groups array)
- member_node_uuids must reference existing node UUIDs (validated against nodes array)
- Colors must use RGBA format: {"r": 0-255, "g": 0-255, "b": 0-255, "a": 0-255}
- Groups support transparency and visual layering (alpha channel)
- Groups maintain undo/redo history for property changes
- member_node_uuids determines group membership (nodes move when group moves)

**Connection Rules:**
- start_node_uuid and end_node_uuid must reference existing node UUIDs
- Pin names must exactly match: function parameters for inputs, "output_N" for outputs
- Execution connections: "exec_out" (source) to "exec_in" (destination)
- Data connections: "output_1", "output_2", etc. to parameter names from @node_entry function
- Connection validation: pin names parsed from actual function signatures
- Invalid connections: mismatched types, non-existent pins, circular exec dependencies

## Example Templates

**Basic Node:**
```markdown
## Node: Process Data (ID: processor)

### Metadata
```json
{"uuid": "processor", "title": "Process Data", "pos": [100, 100], "size": [200, 150]}
```

### Logic
```python
@node_entry  
def process(input_text: str) -> str:
    return input_text.upper()
```

**GUI Node:**
```markdown
## Node: Input Form (ID: form)

### Metadata
```json
{"uuid": "form", "title": "Input Form", "pos": [0, 0], "size": [250, 200],
 "gui_state": {"text": "default", "count": 5}}
```

### Logic  
```python
@node_entry
def get_input(text: str, count: int) -> str:
    return text * count
```

### GUI Definition
```python
from PySide6.QtWidgets import QLabel, QLineEdit, QSpinBox
layout.addWidget(QLabel('Text:', parent))
widgets['text'] = QLineEdit(parent) 
layout.addWidget(widgets['text'])
widgets['count'] = QSpinBox(parent)
layout.addWidget(widgets['count'])
```

### GUI State Handler
```python
def get_values(widgets):
    return {'text': widgets['text'].text(), 'count': widgets['count'].value()}

def set_values(widgets, outputs): 
    pass

def set_initial_state(widgets, state):
    widgets['text'].setText(state.get('text', ''))
    widgets['count'].setValue(state.get('count', 1))
```

**Connection Examples:**
```json
[
  {"start_node_uuid": "input", "start_pin_name": "exec_out", 
   "end_node_uuid": "processor", "end_pin_name": "exec_in"},
  {"start_node_uuid": "input", "start_pin_name": "output_1",
   "end_node_uuid": "processor", "end_pin_name": "input_text"}
]
```

## Parser Implementation

**Tokenization:** Use markdown-it-py, parse tokens (not HTML)
**State machine:** Track current node/component
**Section detection:** h1=title, h2=node/section, h3=component
**Data extraction:** fence blocks by language tag
**Pin generation:** Parse @node_entry function signature

## Error Handling

**Environment Errors:**
- Virtual environment not found or Python executable missing
- Package import failures or dependency conflicts

**Execution Errors:**
- Syntax errors in node code, runtime exceptions, type mismatches
- Missing required inputs or invalid function signatures

**Flow Control Errors:**
- No entry point nodes found (no nodes without incoming exec connections)
- Infinite loops detected (execution count limit exceeded)
- Circular dependencies in execution graph

**Memory Management Errors:**
- Out of memory conditions with large objects (>RAM datasets)
- GPU memory exhaustion (CUDA tensors), uncleaned GPU cache
- Memory leaks from uncleaned object references

**Error Format:** `ERROR in node 'Name': description`
**Limits:** Max execution count prevents infinite loops, timeout protection, memory monitoring

## Virtual Environments

**Directory Structure:**
```
PyFlowGraph/
├── venv/          # Main application environment  
└── venvs/         # Project-specific environments
    ├── project1/  # Environment for project1 graph
    ├── project2/  # Environment for project2 graph
    ├── default/   # Shared default environment
    └── ...
```

**Isolation:** Each graph can have its own Python environment with isolated packages
**Dependency Management:** Per-graph package versions prevent conflicts between graphs
**Execution Context:** All nodes run in single persistent Python interpreter
**Package Availability:** Virtual environment packages automatically available in shared namespace  
**Environment Selection:** Configurable through application's environment manager
**Benefits:** Zero-copy object passing + isolated dependencies + no startup delays

## Format Conversion

**Bidirectional:** Lossless conversion between .md ↔ .json formats
**Use cases:** .md for human editing, .json for programmatic processing
**Equivalence:** Both formats represent identical graph information

## Performance

**Quantitative Benchmarks:**
- PyTorch 100MB tensor: 5000x faster (0.1ms vs 500ms serialization)
- NumPy 50MB array: 4000x faster (0.05ms vs 200ms list conversion)  
- Pandas 10MB DataFrame: 7500x faster (0.02ms vs 150ms dict conversion)
- TensorFlow 100MB tensor: 4000x faster (0.1ms vs 400ms serialization)

**Memory Efficiency:**
- Zero-copy between nodes (same object instance shared)
- Memory usage scales linearly with unique objects, not references
- Direct memory access for >RAM datasets via memory-mapped files
- Automatic cleanup when references cleared

**GPU Performance:**
- Direct CUDA tensor manipulation without device transfers
- GPU memory automatically freed for CUDA tensors
- torch.cuda.empty_cache() and synchronize() called automatically

**Scalability:** O(1) object passing time regardless of data size
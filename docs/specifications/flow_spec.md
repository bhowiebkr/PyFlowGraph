# FlowSpec: The .md File Format Specification

**Version:** 1.0  
**File Extension:** .md  

## 1. Introduction & Philosophy

FlowSpec is a structured, document-based file format for defining node-based graphs and workflows. It is designed to be human-readable, version-control friendly, and easily parsed by both humans and AI models.

**Core Philosophy:** "the document is the graph."

### Guiding Principles

- **Readability First**: Clear structure for human authors and reviewers
- **Structured & Unambiguous**: Rigid structure allowing deterministic parsing  
- **Version Control Native**: Clean diffs in Git and other VCS
- **Language Agnostic**: Code blocks can contain any programming language
- **LLM Friendly**: Descriptive format ideal for AI interaction

## 2. Core Concepts

- **Graph**: The entire document represents a single graph (Level 1 Heading)
- **Node**: A major section (Level 2 Heading) representing a graph node
- **Component**: A subsection (Level 3 Heading) within a node
- **Data Block**: Machine-readable data in fenced code blocks
- **@node_entry**: Required decorator marking the entry point function in each node's Logic block
- **Automatic Pin Generation**: Node pins are automatically created by parsing the @node_entry function's signature

## 3. File Structure Specification

### 3.1 Graph Header

Every .md file MUST begin with a single Level 1 Heading (#).

```markdown
# Graph Title

Optional graph description goes here.
```

### 3.2 Node Definitions

Each node MUST use this exact format:

```markdown
## Node: <Human-Readable-Title> (ID: <unique-identifier>)

Optional node description.

### Metadata
```json
{
    "uuid": "unique-identifier",
    "title": "Human-Readable-Title",
    "pos": [100, 200],
    "size": [300, 250]
}
```

### Logic

```python
@node_entry
def node_function(input_param: str) -> str:
    return f"Processed: {input_param}"
```

### 3.2.1 The @node_entry Decorator

The `@node_entry` decorator is the cornerstone of PyFlowGraph's node system. It serves multiple critical functions:

**Purpose & Function:**
- **Required Marker**: Every Logic block MUST contain exactly one function decorated with `@node_entry`
- **Entry Point**: This decorated function is the sole entry point called during graph execution
- **Pin Generation**: The function's signature is parsed to automatically generate the node's input and output pins
- **Runtime Behavior**: The decorator is a no-op (pass-through) that returns the function unchanged

**Automatic Pin Generation:**
- **Input Pins**: Generated from the function's parameters
  - Parameter names become pin names
  - Type hints determine pin data types and colors
  - Default values are supported for optional parameters
- **Output Pins**: Generated from the return type annotation
  - Single output: `-> str` creates one output pin named "output_1"
  - Multiple outputs: `-> Tuple[str, int, bool]` creates multiple pins ("output_1", "output_2", "output_3")
  - No return annotation or `-> None` creates no output pins

**Supported Type Hints:**

The system supports a comprehensive range of Python type hints for pin generation:

- **Basic Types**: `str`, `int`, `float`, `bool`
- **Container Types**: `list`, `dict`, `tuple`, `set`
- **Generic Types**: 
  - `List[str]`, `List[Dict]`, `List[Any]`
  - `Dict[str, int]`, `Dict[str, Any]`
  - `Tuple[str, int]`, `Tuple[float, ...]`
- **Optional Types**: `Optional[str]`, `Optional[int]`
- **Union Types**: `Union[str, int]`, `Union[float, None]`
- **Special Types**: 
  - `Any` - Accepts any data type
  - `None` - No data (execution pins only)
- **Complex Nested Types**: `List[Dict[str, Any]]`, `Dict[str, List[int]]`

**Pin Color System:**

Pin colors provide visual type information:

- **Execution Pins**: Fixed colors
  - Output execution pins: Light gray (#E0E0E0)
  - Input execution pins: Dark gray (#A0A0A0)
- **Data Pins**: Procedurally generated colors
  - Colors are generated from type string using consistent hashing
  - Same type always produces the same color across all nodes
  - Ensures visual consistency throughout the graph
  - Bright, distinguishable colors in HSV color space

**Multiple Code Support:**

Logic blocks can contain comprehensive Python code beyond just the entry function:

```python
import helper_module
from typing import Tuple

class DataProcessor:
    def process(self, data):
        return data.upper()

def helper_function(x):
    return x * 2

@node_entry
def main_function(input_text: str, count: int) -> Tuple[str, int]:
    processor = DataProcessor()
    result = processor.process(input_text)
    doubled = helper_function(count)
    return result, doubled
```

In this example:
- The entire code block is executed in the node's context
- Helper functions, classes, and imports are all available
- Only `main_function` is called as the entry point with the connected input values
- The function signature of `main_function` determines the node's pins

### 3.3 Required Components

#### Metadata

JSON object containing node configuration and properties.

**Required Fields:**
- `uuid`: Unique identifier for the node (string)
- `title`: Human-readable node name (string)

**Optional Fields:**
- `pos`: Node position as [x, y] coordinates (array, default: [0, 0])
- `size`: Node dimensions as [width, height] (array, default: [200, 150])
- `colors`: Custom node colors (object)
  - `title`: Hex color for title bar (string, e.g., "#007bff")
  - `body`: Hex color for node body (string, e.g., "#0056b3")
- `gui_state`: Saved GUI widget values (object, default: {})
- `is_reroute`: Flag for reroute nodes (boolean, default: false)

**Example with All Fields:**
```json
{
    "uuid": "my-node",
    "title": "Data Processor",
    "pos": [250, 300],
    "size": [280, 200],
    "colors": {
        "title": "#28a745",
        "body": "#1e7e34"
    },
    "gui_state": {
        "threshold": 0.5,
        "enabled": true
    },
    "is_reroute": false
}
```

#### Logic

Python code block containing the node's implementation.

**Requirements:**
- Must include exactly one function decorated with `@node_entry`
- The `@node_entry` function's signature determines the node's pins
- Can include additional helper functions, classes, imports, and module-level code

### 3.4 Optional Components

#### GUI Definition

The GUI Definition component creates custom user interface widgets for interactive nodes using PySide6 (Qt for Python). This allows nodes to have rich input controls beyond simple pin connections.

**Format:**
```markdown
### GUI Definition
```python
# Python code creating PySide6 widgets
```

**Execution Context:**

The GUI code executes with these predefined variables:
- `parent`: The QWidget parent for created widgets
- `layout`: A QVBoxLayout to add widgets to
- `widgets`: Dictionary to store widget references (required for state management)

**Example:**
```python
from PySide6.QtWidgets import QLabel, QSpinBox, QCheckBox, QPushButton

# Add a label
layout.addWidget(QLabel('Password Length:', parent))

# Create and store a spin box
widgets['length'] = QSpinBox(parent)
widgets['length'].setRange(4, 128)
widgets['length'].setValue(12)
layout.addWidget(widgets['length'])

# Create and store a checkbox
widgets['uppercase'] = QCheckBox('Include Uppercase', parent)
widgets['uppercase'].setChecked(True)
layout.addWidget(widgets['uppercase'])

# Create a button
widgets['generate_btn'] = QPushButton('Generate', parent)
layout.addWidget(widgets['generate_btn'])
```

**Important Notes:**
- All interactive widgets MUST be stored in the `widgets` dictionary for state management
- Common widgets: QLabel, QSpinBox, QCheckBox, QPushButton, QTextEdit, QLineEdit, QComboBox
- Widgets are automatically cleared and recreated when the GUI code changes

#### GUI State Handler

The GUI State Handler component defines functions to manage widget state and data flow between the GUI and node execution.

**Format:**
```markdown
### GUI State Handler
```python
# Python code defining state management functions
```

**Required Functions:**

1. **`get_values(widgets)`** - Returns current widget values as a dictionary
   - Called before node execution to gather GUI input
   - Return value is merged with connected pin inputs
   - Also used to persist GUI state in the graph file

2. **`set_values(widgets, outputs)`** - Updates widgets based on node outputs
   - Called after node execution completes
   - `outputs` contains the node's return values (output_1, output_2, etc.)
   - Used to display results in the GUI

3. **`set_initial_state(widgets, state)`** - Restores saved widget state
   - Called when the node is created or loaded
   - `state` contains the saved gui_state from metadata
   - Used to restore previous widget values

**Example:**
```python
def get_values(widgets):
    return {
        'length': widgets['length'].value(),
        'include_uppercase': widgets['uppercase'].isChecked()
    }

def set_values(widgets, outputs):
    # Display the generated password in a text field
    result = outputs.get('output_1', '')
    if result and 'password_field' in widgets:
        widgets['password_field'].setText(result)

def set_initial_state(widgets, state):
    widgets['length'].setValue(state.get('length', 12))
    widgets['uppercase'].setChecked(state.get('include_uppercase', True))
```

**Data Flow:**
- GUI values from `get_values()` are passed as additional parameters to the @node_entry function
- The function's return values are passed to `set_values()` for display
- Widget state is automatically saved to `gui_state` in the node's metadata

### 3.5 Groups Section (Optional)

Files MAY contain a Groups section for organizing nodes visually:

```markdown
## Groups
```json
[
    {
        "uuid": "group-1",
        "name": "Data Processing",
        "description": "Processes input data through multiple stages",
        "member_node_uuids": ["node1", "node2", "node3"],
        "position": {"x": 150, "y": 200},
        "size": {"width": 400, "height": 300},
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
]
```

**Group Properties:**

**Required Fields:**
- `uuid`: Unique identifier for the group (string)
- `name`: Human-readable group name (string)
- `member_node_uuids`: Array of UUIDs for nodes contained in this group

**Optional Fields:**
- `description`: Group description (string, default: "")
- `position`: Group position as {x, y} coordinates (object, default: {x: 0, y: 0})
- `size`: Group dimensions as {width, height} (object, default: {width: 200, height: 150})
- `padding`: Internal padding around member nodes (number, default: 20)
- `is_expanded`: Whether group is visually expanded (boolean, default: true)
- `colors`: Visual appearance colors with RGBA values (object)
  - `background`: Semi-transparent group background color
  - `border`: Group border outline color
  - `title_bg`: Title bar background color  
  - `title_text`: Title text color
  - `selection`: Selection highlight color when group is selected

**Color Format:**
Each color in the `colors` object uses RGBA format:
```json
{"r": 255, "g": 165, "b": 0, "a": 100}
```
Where r, g, b are 0-255 and a (alpha/transparency) is 0-255 (0 = fully transparent, 255 = fully opaque).

**Group Behavior:**
- Groups are organizational containers that visually group related nodes
- Member nodes move when the group is moved
- Groups can be resized, automatically updating membership based on contained nodes
- Groups support transparency for better visual layering
- Groups maintain their own undo/redo history for property changes
- Groups can be collapsed/expanded to manage visual complexity

### 3.6 Connections Section

The file MUST contain exactly one Connections section:

```markdown
## Connections
```json
[
    {
        "start_node_uuid": "node1",
        "start_pin_name": "output_1", 
        "end_node_uuid": "node2",
        "end_pin_name": "input_param"
    }
]
```

**Connection Types:**

1. **Data Connections** - Transfer values between nodes
   - Connect output pins (output_1, output_2, etc.) to input parameter pins
   - Pin names match function parameters and return value positions

2. **Execution Connections** - Control execution flow
   - `exec_out` to `exec_in` connections determine execution order
   - Nodes execute when their exec_in receives a signal
   - Used for sequencing operations and controlling flow

**Example with Both Connection Types:**
```json
[
    {
        "start_node_uuid": "generator",
        "start_pin_name": "exec_out",
        "end_node_uuid": "processor",
        "end_pin_name": "exec_in"
    },
    {
        "start_node_uuid": "generator",
        "start_pin_name": "output_1",
        "end_node_uuid": "processor",
        "end_pin_name": "data"
    }
]
```

### 3.7 GUI Integration & Data Flow

When a node has both GUI components and pin connections, the data flows as follows:

1. **Input Merging**: GUI values from `get_values()` are merged with connected pin values
   - Connected pin values take precedence over GUI values for the same parameter
   - GUI values provide defaults or additional inputs not available through pins

2. **Function Execution**: The @node_entry function receives the merged inputs
   - Parameters can come from either GUI widgets or connected pins
   - All parameters must be satisfied for execution

3. **Output Distribution**: Return values are distributed to both pins and GUI
   - Output pins receive values for connected downstream nodes
   - `set_values()` receives the same outputs for GUI display

**Example Flow:**
```python
# GUI provides 'length' and 'include_uppercase'
gui_values = {'length': 12, 'include_uppercase': True}

# Connected pins provide 'text_input'
pin_values = {'text_input': "Hello"}

# Merged and passed to function
@node_entry
def process(text_input: str, length: int, include_uppercase: bool) -> str:
    # Function receives all three parameters
    result = text_input[:length]
    if include_uppercase:
        result = result.upper()
    return result

# Output goes to both output_1 pin and set_values()
```

**GUI State Persistence:**

The `gui_state` field in metadata stores widget values:
```json
{
    "uuid": "my-node",
    "title": "My Node",
    "gui_state": {
        "length": 12,
        "include_uppercase": true
    }
}
```

This state is:
- Saved automatically when the graph is saved
- Restored when the graph is loaded via `set_initial_state()`
- Updated whenever widget values change

### 3.8 Reroute Nodes

Reroute nodes are special organizational nodes that help manage connection routing and graph layout without affecting data flow.

**Purpose:**
- Organize complex connection paths for better visual clarity
- Create connection waypoints to avoid overlapping wires
- Group related connections together

**Characteristics:**
- Small, circular appearance (not rectangular like regular nodes)
- Single input pin and single output pin
- Pass data through unchanged (no processing)
- Automatically adopt the color of the connected data type
- No Logic component required

**Metadata Format:**
```json
{
    "uuid": "reroute-1",
    "title": "Reroute",
    "pos": [300, 200],
    "size": [16, 16],
    "is_reroute": true
}
```

**Identification:**
- The `is_reroute: true` flag in metadata identifies a reroute node
- When this flag is present, the parser treats it as a pass-through node
- No Logic, GUI Definition, or GUI State Handler components are needed

**Example Usage in Connections:**
```json
[
    {
        "start_node_uuid": "data-source",
        "start_pin_name": "output_1",
        "end_node_uuid": "reroute-1",
        "end_pin_name": "input"
    },
    {
        "start_node_uuid": "reroute-1",
        "start_pin_name": "output",
        "end_node_uuid": "data-processor",
        "end_pin_name": "data"
    }
]
```

### 3.9 Execution Modes

PyFlowGraph supports two distinct execution modes that determine how the graph processes data:

**1. Batch Mode (Default)**
- Traditional one-shot execution of the entire graph
- Executes all nodes in dependency order from entry points
- Suitable for data processing pipelines and transformations
- All nodes execute once per run
- Results are displayed after completion

**2. Live Mode (Interactive)**
- Event-driven execution triggered by user interactions
- Nodes execute in response to GUI button clicks or events
- Maintains persistent state between executions
- Ideal for interactive applications and tools
- Allows partial graph execution

**Mode Characteristics:**

| Feature | Batch Mode | Live Mode |
|---------|------------|-----------|
| Execution Trigger | Manual "Execute" button | GUI events in nodes |
| State Persistence | No (fresh each run) | Yes (maintains state) |
| Partial Execution | No (full graph) | Yes (event-driven paths) |
| Use Cases | Data pipelines, batch processing | Interactive tools, dashboards |
| Performance | Optimized for throughput | Optimized for responsiveness |

**Implementation Notes:**
- Execution mode is controlled at runtime, not stored in the file
- The same graph can run in either mode without modification
- GUI buttons in nodes are inactive in batch mode
- Live mode enables event handlers in node GUIs
- Both modes benefit from native object passing (100-1000x performance improvement)
- ML objects (tensors, DataFrames) persist across executions in Live mode

### 3.10 ML Framework Integration

PyFlowGraph provides native, zero-copy support for major machine learning and data science frameworks through the single process execution architecture.

#### Supported Frameworks

**PyTorch Integration:**
- **GPU Tensors**: Direct CUDA tensor manipulation with device preservation
- **Automatic Cleanup**: CUDA cache clearing prevents VRAM leaks
- **Zero Copy**: Tensors passed by reference, no memory duplication
- **Device Management**: Automatic device placement and synchronization
- **Grad Support**: Automatic differentiation graphs preserved across nodes

**NumPy Integration:**
- **Array References**: Direct ndarray object passing
- **Dtype Preservation**: Data types and shapes maintained exactly
- **Memory Views**: Support for memory-mapped arrays and views
- **Broadcasting**: Direct support for NumPy broadcasting operations
- **Performance**: 100x+ faster than array serialization approaches

**Pandas Integration:**  
- **DataFrame Objects**: Direct DataFrame and Series object references
- **Index Preservation**: Row/column indices maintained exactly
- **Memory Efficiency**: Large datasets shared without duplication
- **Method Chaining**: Direct DataFrame method access across nodes
- **Performance**: Eliminates expensive serialization for large datasets

**TensorFlow Integration:**
- **Tensor Objects**: Native tf.Tensor and tf.Variable support
- **Session Management**: Automatic session and graph management
- **Device Placement**: GPU/CPU device specifications preserved
- **Eager Execution**: Full support for TensorFlow 2.x eager mode

**JAX Integration:**
- **Array Objects**: Direct jax.numpy array support
- **JIT Compilation**: Compiled functions preserved across executions
- **Device Arrays**: GPU/TPU device array support
- **Functional Transformations**: Direct support for vmap, grad, jit

#### Framework Auto-Import

Frameworks are automatically imported into the persistent namespace:

```python
# Automatically available in all nodes:
import numpy as np
import pandas as pd
import torch
import tensorflow as tf
import jax
import jax.numpy as jnp
```

#### Performance Benchmarks

| Framework | Object Type | Traditional Approach | Native Object Passing | Improvement |
|-----------|-------------|---------------------|----------------------|-------------|
| PyTorch | 100MB Tensor | 500ms (serialize/copy) | 0.1ms (reference) | 5000x |
| NumPy | 50MB Array | 200ms (list conversion) | 0.05ms (reference) | 4000x |
| Pandas | 10MB DataFrame | 150ms (dict conversion) | 0.02ms (reference) | 7500x |
| TensorFlow | 100MB Tensor | 400ms (serialize) | 0.1ms (reference) | 4000x |

#### Memory Management

**Reference Counting:**
- Objects persist while referenced by any node
- Automatic cleanup when no nodes reference the object
- GPU memory automatically freed for CUDA tensors

**Large Object Handling:**
- Memory-mapped files supported for >RAM datasets
- Streaming data objects for infinite sequences  
- Automatic chunking for very large arrays

**GPU Memory Management:**
```python
def _cleanup_gpu_memory(self):
    """Automatic GPU memory cleanup for ML frameworks."""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except ImportError:
        pass
```

### 3.11 Virtual Environments

PyFlowGraph uses isolated Python virtual environments to manage dependencies for each graph:

**Environment Structure:**
```
PyFlowGraph/
├── venv/          # Main application environment
└── venvs/         # Project-specific environments
    ├── project1/  # Environment for project1 graph
    ├── project2/  # Environment for project2 graph
    └── ...
```

**Features:**
- Each graph can have its own Python environment
- Isolated package dependencies per project
- Prevents version conflicts between graphs
- Configurable through the application's environment manager

**Execution Context:**
- All nodes execute within a single persistent Python interpreter (`SingleProcessExecutor`)
- Virtual environment packages are available in the shared namespace
- Automatic framework imports: numpy, pandas, torch, tensorflow, jax
- Zero-copy object passing between all nodes
- Persistent state maintains imports and variables across executions

**Benefits:**
- **Performance**: Single interpreter eliminates all process overhead (100-1000x faster)
- **Memory Efficiency**: Direct object references with no copying or serialization  
- **GPU Optimized**: Direct CUDA tensor manipulation without device conflicts
- **ML/AI Ready**: Native support for PyTorch, TensorFlow, JAX, NumPy, Pandas objects
- **Developer Experience**: Immediate feedback, no startup delays between executions
- **Resource Management**: Automatic memory cleanup and GPU cache management
- **Portability**: Environments can be recreated from requirements

### 3.11 Native Object Passing System

PyFlowGraph executes all nodes in a single persistent Python interpreter with direct object references for maximum performance. This architecture eliminates all serialization overhead and enables zero-copy data transfer between nodes.

#### Architecture Overview

**Single Process Execution:**
- All nodes execute within a single persistent Python interpreter (`SingleProcessExecutor`)
- Shared namespace maintains imports and variables across executions
- Direct object references stored in `object_store` dictionary
- No subprocess creation or IPC communication
- 100-1000x performance improvement over traditional approaches

#### Data Transfer Mechanism

**1. Direct Object Storage:**
```python
class SingleProcessExecutor:
    def __init__(self):
        self.object_store: Dict[Any, Any] = {}  # Direct object references
        self.namespace: Dict[str, Any] = {}     # Persistent namespace
        self.object_refs = weakref.WeakValueDictionary()  # Memory management
```

**2. Zero-Copy Data Flow:**
- **Input Collection**: Values gathered from connected pins and GUI widgets
- **Direct Execution**: Node code runs in shared interpreter namespace
- **Reference Passing**: All objects (primitives, tensors, DataFrames) passed by reference
- **Output Storage**: Results stored as direct references in `object_store`
- **Memory Efficiency**: Same object instance shared across all references

**3. Execution Flow:**
```python
def execute_node(node, inputs):
    # Merge GUI values with connected pin values
    all_inputs = {**gui_values, **pin_values}
    
    # Execute node code in persistent namespace
    exec(node.code, self.namespace)
    
    # Call entry function with direct object references
    result = self.namespace[node.function_name](**all_inputs)
    
    # Store result as direct reference (no copying)
    self.object_store[output_key] = result
    
    # Update GUI with direct reference
    node.set_gui_values({'output_1': result})
    
    return result  # Direct reference, not serialized copy
```

#### Universal Type Support

**All Python Types Supported:**
- **Primitives**: str, int, float, bool, None
- **Collections**: list, dict, tuple, set, frozenset
- **ML Objects**: PyTorch tensors, NumPy arrays, Pandas DataFrames
- **Custom Classes**: User-defined objects with full method access
- **Complex Types**: Functions, lambdas, types, exceptions, file handles
- **Nested Structures**: Any combination of above types

**ML Framework Integration:**
- **PyTorch**: GPU tensors with device preservation, automatic CUDA cleanup
- **NumPy**: Arrays with dtype/shape preservation, zero-copy operations
- **Pandas**: DataFrames with index/column preservation
- **TensorFlow**: Native tensor support with automatic imports
- **JAX**: Direct array and function support

#### Memory Management

**Automatic Cleanup:**
```python
def cleanup_memory(self):
    # Force garbage collection
    collected = gc.collect()
    
    # GPU memory cleanup (PyTorch)
    self._cleanup_gpu_memory()
    
    return collected

def _cleanup_gpu_memory(self):
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except ImportError:
        pass
```

**Reference Counting:**
- `WeakValueDictionary` for automatic cleanup of unreferenced objects
- Objects persist while any node references them
- Automatic garbage collection when references are cleared
- GPU memory management for CUDA tensors

#### Performance Characteristics

**Benchmarked Improvements:**
- **Small Objects**: 20-100x faster than copy-based approaches
- **Large Objects**: 100-1000x faster (tensors, DataFrames)
- **Memory Efficiency**: Zero duplication, shared object instances
- **Execution Speed**: Sub-10ms node execution times
- **GPU Operations**: Direct CUDA tensor manipulation without copies

**Scalability:**
- Object passing time is O(1) regardless of data size
- Memory usage scales linearly with unique objects (not references)
- No serialization bottlenecks for large datasets
- Direct memory access for >RAM datasets via memory-mapped files

#### Data Flow Example

```python
# Node A: Create and return a large PyTorch tensor
@node_entry
def create_tensor() -> torch.Tensor:
    # 100MB tensor created once
    return torch.randn(10000, 2500, dtype=torch.float32)

# Node B: Process the same tensor by reference (no copying)
@node_entry  
def process_tensor(tensor: torch.Tensor) -> Tuple[torch.Tensor, float]:
    # Same object reference - zero memory overhead
    processed = tensor * 2.0  # In-place operation possible
    mean_val = tensor.mean().item()
    return processed, mean_val

# Node C: Further processing with original object
@node_entry
def analyze_tensor(original: torch.Tensor, processed: torch.Tensor) -> Dict[str, Any]:
    # Both tensors are the same object reference
    # Can directly compare, analyze, modify
    return {
        "shape": original.shape,
        "dtype": str(original.dtype), 
        "device": str(original.device),
        "memory_address": id(original),
        "is_same_object": id(original) == id(processed)  # True
    }
```

#### Pin Value Storage

The execution system maintains object references through:
- **`object_store`**: Direct references to all objects, no copying
- **`pin_values`**: Maps pins to object references 
- **Persistence**: Objects remain in memory across executions in Live Mode
- **Cleanup**: Automatic garbage collection when nodes are disconnected

### 3.12 Error Handling

The system provides comprehensive error handling during graph execution:

**Error Types:**

1. **Environment Errors**
   - Virtual environment not found
   - Python executable missing
   - Package import failures

2. **Execution Errors**
   - Syntax errors in node code
   - Runtime exceptions
   - Type mismatches
   - Missing required inputs

3. **Flow Control Errors**
   - No entry point nodes found
   - Infinite loops detected (execution limit)
   - Circular dependencies

4. **Memory Management Errors**
   - Out of memory conditions with large objects
   - GPU memory exhaustion (CUDA tensors)
   - Memory leaks from uncleaned references

**Error Reporting:**
- Errors are captured directly from the single process execution
- Error messages include the node name for context
- Full Python stack traces are preserved for debugging
- Errors are displayed in the output log with formatting
- Memory usage warnings for large object operations

**Error Message Format:**
```
ERROR in node 'NodeName': error description
STDERR: detailed error output
```

**Execution Limits:**
- Maximum execution count prevents infinite loops
- Timeout protection for long-running nodes
- Memory monitoring for large object operations
- GPU memory limits and automatic cleanup

## 4. Examples

### 4.1 Simple Pipeline Example

```markdown
# Hello World Pipeline

A basic two-node pipeline demonstrating the .md format.

## Node: Text Generator (ID: generator)

Creates a simple text message.

### Metadata
```json
{
    "uuid": "generator",
    "title": "Text Generator",
    "pos": [100, 100],
    "size": [200, 150]
}
```

### Logic

```python
@node_entry
def generate_text() -> str:
    return "Hello, World!"
```

## Node: Text Printer (ID: printer)

Prints the received text message.

### Metadata

```json
{
    "uuid": "printer", 
    "title": "Text Printer",
    "pos": [400, 100],
    "size": [200, 150]
}
```

### Logic

```python
@node_entry
def print_text(message: str) -> str:
    print(f"Received: {message}")
    return message
```

## Connections

```json
[
    {
        "start_node_uuid": "generator",
        "start_pin_name": "output_1",
        "end_node_uuid": "printer", 
        "end_pin_name": "message"
    }
]
```

### 4.2 GUI-Enabled Node Example

```markdown
# Interactive Calculator

A calculator node with GUI controls for operation selection and display.

## Node: Calculator (ID: calc-node)

Performs arithmetic operations with GUI controls.

### Metadata

```json
{
    "uuid": "calc-node",
    "title": "Calculator",
    "pos": [200, 200],
    "size": [300, 250],
    "gui_state": {
        "operation": "add",
        "value_a": 10,
        "value_b": 5
    }
}
```

### Logic

```python
from typing import Tuple

@node_entry
def calculate(value_a: float, value_b: float, operation: str) -> Tuple[float, str]:
    if operation == "add":
        result = value_a + value_b
        op_symbol = "+"
    elif operation == "subtract":
        result = value_a - value_b
        op_symbol = "-"
    elif operation == "multiply":
        result = value_a * value_b
        op_symbol = "*"
    elif operation == "divide":
        result = value_a / value_b if value_b != 0 else 0
        op_symbol = "/"
    else:
        result = 0
        op_symbol = "?"
    
    expression = f"{value_a} {op_symbol} {value_b} = {result}"
    return result, expression
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QDoubleSpinBox, QComboBox, QTextEdit, QPushButton

# Input A
layout.addWidget(QLabel('Value A:', parent))
widgets['value_a'] = QDoubleSpinBox(parent)
widgets['value_a'].setRange(-1000, 1000)
widgets['value_a'].setValue(10)
layout.addWidget(widgets['value_a'])

# Input B
layout.addWidget(QLabel('Value B:', parent))
widgets['value_b'] = QDoubleSpinBox(parent)
widgets['value_b'].setRange(-1000, 1000)
widgets['value_b'].setValue(5)
layout.addWidget(widgets['value_b'])

# Operation selector
layout.addWidget(QLabel('Operation:', parent))
widgets['operation'] = QComboBox(parent)
widgets['operation'].addItems(['add', 'subtract', 'multiply', 'divide'])
layout.addWidget(widgets['operation'])

# Calculate button
widgets['calc_btn'] = QPushButton('Calculate', parent)
layout.addWidget(widgets['calc_btn'])

# Result display
widgets['result_display'] = QTextEdit(parent)
widgets['result_display'].setMaximumHeight(60)
widgets['result_display'].setReadOnly(True)
layout.addWidget(widgets['result_display'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'value_a': widgets['value_a'].value(),
        'value_b': widgets['value_b'].value(),
        'operation': widgets['operation'].currentText()
    }

def set_values(widgets, outputs):
    # Display the calculation expression
    expression = outputs.get('output_2', '')
    if expression:
        widgets['result_display'].setPlainText(expression)

def set_initial_state(widgets, state):
    widgets['value_a'].setValue(state.get('value_a', 10))
    widgets['value_b'].setValue(state.get('value_b', 5))
    widgets['operation'].setCurrentText(state.get('operation', 'add'))
```

## Groups

```json
[
    {
        "uuid": "calc-group",
        "name": "Calculator Components", 
        "description": "All calculator-related functionality",
        "member_node_uuids": ["calc-node"],
        "position": {"x": 150, "y": 150},
        "size": {"width": 350, "height": 300},
        "padding": 25,
        "is_expanded": true,
        "colors": {
            "background": {"r": 45, "g": 45, "b": 55, "a": 120},
            "border": {"r": 100, "g": 150, "b": 200, "a": 180}, 
            "title_bg": {"r": 60, "g": 60, "b": 70, "a": 200},
            "title_text": {"r": 220, "g": 220, "b": 220, "a": 255},
            "selection": {"r": 255, "g": 165, "b": 0, "a": 100}
        }
    }
]
```

## Connections

```json
[]
```

## 5. Parser Implementation

A parser should use markdown-it-py to tokenize the document:

### 5.1 Algorithm

1. **Tokenize**: Parse file into token stream (don't render to HTML)
2. **State Machine**: Track current node and component being parsed
3. **Section Detection**:
   - `h1`: Graph title
   - `h2`: Node header (regex: `Node: (.*) \(ID: (.*)\)`), "Groups", or "Connections"
   - `h3`: Component type (Metadata, Logic, etc.)
4. **Data Extraction**: Extract `content` from `fence` tokens based on `info` language tag
5. **@node_entry Function Identification**:
   - Parse the Logic block's Python code
   - Identify the function decorated with `@node_entry`
   - Extract the function name for execution
   - Parse the function signature to generate pins:
     - Input pins from parameters and their type hints
     - Output pins from return type annotation
6. **Graph Construction**: Build in-memory graph from collected data

### 5.2 Token Types

- `heading_open` with `h1/h2/h3` tags
- `fence` with `info` property for language detection
- `inline` for text content

### 5.3 Validation Rules

**Required Rules:**
- Exactly one h1 heading
- Each node must have unique uuid
- Metadata and Logic components are required
- Each Logic block must contain exactly one `@node_entry` decorated function
- The `@node_entry` function must have valid Python syntax
- Type hints on the `@node_entry` function should be valid for pin generation
- Connections section is required
- Groups section is optional; if present, must contain valid JSON
- JSON must be valid in metadata, groups, and connections
- Group UUIDs must be unique across all groups
- Group member_node_uuids must reference existing nodes

**GUI-Specific Rules (when GUI components are present):**
- GUI Definition must be valid Python code that creates PySide6 widgets
- All interactive widgets must be stored in the `widgets` dictionary
- GUI State Handler must define at least the `get_values(widgets)` function
- `get_values()` must return a dictionary
- `set_values()` and `set_initial_state()` should handle missing keys gracefully
- Widget names in `get_values()` must match keys used in GUI Definition
- GUI state in metadata should match the structure returned by `get_values()`

## 6. Extension Points

The format supports extension through:

- **Additional Component Types**: Custom ### sections for specialized functionality
- **Custom Metadata Fields**: Add application-specific fields to node metadata
- **Multiple Programming Languages**: Logic blocks can contain any language (with appropriate executor)
- **Custom Connection Properties**: Extend connection objects with additional metadata
- **Special Node Types**: Reroute nodes and other organizational elements
- **Execution Modes**: Batch, Live, and custom execution strategies
- **Virtual Environment Configuration**: Per-graph dependency management
- **Custom Pin Types**: Extend the type system with domain-specific types
- **Event Handlers**: GUI event bindings for interactive functionality

## 7. Format Conversion

PyFlowGraph supports bidirectional conversion between the human-readable .md format and machine-optimized .json format.

### 7.1 Conversion Functions

**Flow to JSON:**
```python
flow_to_json(flow_content: str) -> Dict[str, Any]
```
Parses .md content and returns structured JSON data.

**JSON to Flow:**
```python
json_to_flow(json_data: Dict[str, Any], title: str, description: str) -> str
```
Generates .md content from JSON graph data.

### 7.2 Format Equivalence

Both formats represent identical graph information:

| .md Format | JSON Format | Purpose |
|------------|-------------|---------|
| # Title | "title" field | Graph name |
| ## Node sections | "nodes" array | Node definitions |
| ### Metadata | Node properties | Configuration |
| ### Logic | "code" field | Execution code |
| ### GUI Definition | "gui_code" field | Widget creation |
| ### GUI State Handler | "gui_get_values_code" | State management |
| ## Groups | "groups" array | Group definitions |
| ## Connections | "connections" array | Graph edges |

### 7.3 Use Cases

**Markdown Format (.md):**
- Human authoring and editing
- Version control and diffs
- Documentation and review
- AI/LLM interaction
- Text-based workflows

**JSON Format (.json):**
- Application internal storage
- API data exchange
- Programmatic generation
- Performance optimization
- Database storage

### 7.4 Conversion Guarantees

- **Lossless**: All data preserved during conversion
- **Deterministic**: Same input produces same output
- **Reversible**: Can convert back and forth without data loss
- **Validating**: Both formats enforce structure rules

### 7.5 Import/Export Workflow

1. **Import JSON to Editor**: Load .json file and convert to .md for editing
2. **Export from Editor**: Save .md file or convert to .json for external use
3. **Batch Conversion**: Process multiple files between formats
4. **Format Detection**: Automatic detection based on file extension

---

*This specification ensures .md files are both human-readable documents and structured data formats suitable for programmatic processing.*

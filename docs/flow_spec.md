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

### 3.5 Connections Section

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

### 3.6 GUI Integration & Data Flow

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

### 3.7 Reroute Nodes

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

### 3.8 Execution Modes

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

### 3.9 Virtual Environments

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
- Nodes execute in subprocess using the graph's virtual environment
- Python executable path is determined by the active environment
- Package imports in Logic blocks use the environment's installed packages

**Benefits:**
- Security: Subprocess isolation prevents malicious code from affecting the host
- Flexibility: Different graphs can use different package versions
- Portability: Environments can be recreated from requirements

### 3.10 Error Handling

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

**Error Reporting:**
- Errors are captured from subprocess stderr
- Error messages include the node name for context
- Stack traces are preserved for debugging
- Errors are displayed in the output log with formatting

**Error Message Format:**
```
ERROR in node 'NodeName': error description
STDERR: detailed error output
```

**Execution Limits:**
- Maximum execution count prevents infinite loops
- Timeout protection for long-running nodes
- Memory limits for subprocess execution

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
   - `h2`: Node header (regex: `Node: (.*) \(ID: (.*)\)`) or "Connections"
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
- JSON must be valid in metadata and connections

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

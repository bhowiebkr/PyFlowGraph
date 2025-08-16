# PyFlowGraph Coding Standards

## Overview
This document defines the coding standards and conventions for the PyFlowGraph project.

## Python Standards

### General Principles
- Python 3.8+ compatibility required
- Follow PEP 8 with the following project-specific conventions
- Type hints required for all public methods and complex functions
- No emoji in code or comments
- No marketing language - keep documentation technical and professional

### Code Organization
- All source code in `src/` directory
- One class per file for major components
- Related utility functions grouped in appropriate `*_utils.py` files
- Test files in `tests/` directory matching source structure

### Naming Conventions
- **Classes**: PascalCase (e.g., `NodeEditor`, `GraphExecutor`)
- **Functions/Methods**: snake_case (e.g., `parse_function_signature`, `execute_node`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_NODE_WIDTH`)
- **Private Methods**: Leading underscore (e.g., `_validate_connection`)
- **Qt Slots**: Prefix with `on_` (e.g., `on_node_selected`)

### Import Organization
```python
# Standard library imports
import sys
import json
from typing import Dict, List, Optional, Tuple

# Third-party imports
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtWidgets import QWidget, QDialog

# Local imports
from src.node import Node
from src.pin import Pin
```

### Type Hints
- Required for all public methods
- Use `Optional[]` for nullable types
- Use `Union[]` sparingly - prefer specific types
- Example:
```python
def create_node(self, node_type: str, position: QPointF) -> Optional[Node]:
    pass
```

### Documentation
- Docstrings for all public classes and methods
- Use triple quotes for docstrings
- No redundant comments - code should be self-documenting
- Example:
```python
def execute_graph(self, start_node: Node) -> Dict[str, Any]:
    """Execute the graph starting from the specified node.
    
    Args:
        start_node: The node to begin execution from
        
    Returns:
        Dictionary of output values keyed by pin names
    """
```

## PySide6/Qt Conventions

### Widget Structure
- Inherit from appropriate Qt base class
- Initialize parent in constructor
- Use layouts for responsive design
- Example:
```python
class NodePropertiesDialog(QDialog):
    def __init__(self, node: Node, parent=None):
        super().__init__(parent)
        self.node = node
        self._setup_ui()
```

### Signal/Slot Connections
- Define signals at class level
- Connect in constructor or setup method
- Disconnect when appropriate to prevent memory leaks
- Example:
```python
class NodeEditor(QWidget):
    node_selected = Signal(Node)
    
    def __init__(self):
        super().__init__()
        self.node_selected.connect(self.on_node_selected)
```

### Resource Management
- Use context managers for file operations
- Clean up QGraphicsItems when removing from scene
- Properly parent Qt objects for automatic cleanup

## File Operations

### JSON Serialization
- All graph files use clean JSON format
- Maintain human-readable formatting
- Example structure:
```python
{
    "nodes": [...],
    "connections": [...],
    "metadata": {
        "version": "1.0",
        "created": "2024-01-01"
    }
}
```

### Path Handling
- Use `pathlib.Path` for path operations
- Always use absolute paths in tools
- Handle both Windows and Unix paths

## Testing Standards

### Test Organization
- One test file per source module
- Test class names: `Test{ClassName}`
- Test method names: `test_{behavior}_when_{condition}`
- Example:
```python
class TestNode(unittest.TestCase):
    def test_pin_creation_when_type_hints_provided(self):
        pass
```

### Test Principles
- Fast execution (< 5 seconds per test file)
- Deterministic - no flaky tests
- Test one behavior per test method
- Use setUp/tearDown for common initialization

## Error Handling

### Exception Usage
- Raise specific exceptions with clear messages
- Catch exceptions at appropriate levels
- Never use bare `except:` clauses
- Example:
```python
if not self.validate_connection(source, target):
    raise ValueError(f"Invalid connection between {source} and {target}")
```

### User Feedback
- Display clear error messages in dialogs
- Log technical details for debugging
- Provide actionable error resolution hints

## Security

### Code Execution
- All node code executes in isolated subprocesses
- Never use `eval()` or `exec()` on untrusted input
- Validate all inputs before processing
- Use JSON for inter-process communication

### File Access
- Restrict file operations to project directories
- Validate file paths before operations
- Never expose absolute system paths in UI

## Performance

### Optimization Guidelines
- Profile before optimizing
- Cache expensive computations
- Use Qt's built-in optimization features
- Batch graphics updates when possible

### Memory Management
- Clear references to deleted nodes/connections
- Use weak references where appropriate
- Monitor memory usage in long-running operations

## Version Control

### Commit Standards
- Clear, concise commit messages
- Focus on "why" not "what"
- No emoji in commit messages
- No attribution to AI tools in commits
- Example: "Fix connection validation for tuple types"

### Branch Strategy
- Main branch for stable releases
- Feature branches for new development
- Fix branches for bug corrections

## Prohibited Practices

### Never Do
- Add emoji to code or comments
- Include marketing language in documentation
- Create files unless absolutely necessary
- Use `eval()` or `exec()` on user input
- Commit secrets or API keys
- Add AI attribution to commits or code

### Always Do
- Prefer editing existing files over creating new ones
- Follow existing patterns in the codebase
- Validate user inputs
- Use type hints for clarity
- Test error conditions
- Keep documentation technical and professional
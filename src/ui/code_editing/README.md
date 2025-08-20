# Code Editing Module

This module provides advanced Python code editing capabilities within PyFlowGraph's node editor. It implements a professional code editor with syntax highlighting, smart indentation, and integration with the visual node system.

## Purpose

The code editing module bridges the gap between visual node programming and traditional text-based coding. It allows users to edit the Python functions that power individual nodes while maintaining the visual workflow of the node editor.

## Key Files

### `__init__.py`
Standard Python package initialization file.

### `python_code_editor.py`
- **PythonCodeEditor**: Main code editor widget with professional features
- Line number display with proper alignment and formatting
- Smart indentation with automatic Python code formatting
- Tab and space management for consistent code style
- Integration with Qt's text editing framework
- Undo/redo support with command integration
- Find and replace functionality for code navigation
- Code completion hooks for future extension

### `python_syntax_highlighter.py`
- **PythonSyntaxHighlighter**: Real-time Python syntax highlighting
- Keyword highlighting for Python language constructs
- String literal highlighting with proper quote handling
- Comment highlighting for documentation and notes
- Number and operator highlighting for visual clarity
- Function and class name highlighting
- Built-in function and type highlighting
- Custom color schemes and theme support

## Features

### Professional Code Editing
- **Syntax Highlighting**: Real-time Python syntax coloring for improved readability
- **Line Numbers**: Professional line number display with proper formatting
- **Smart Indentation**: Automatic indentation following Python conventions
- **Bracket Matching**: Visual matching of parentheses, brackets, and braces

### Python Integration
- **Function Parsing**: Integration with node function signature analysis
- **Type Hint Support**: Syntax highlighting for Python type annotations
- **Docstring Handling**: Special formatting for function documentation
- **Import Recognition**: Highlighting and management of import statements

### User Experience
- **Responsive Interface**: Smooth editing with minimal input lag
- **Customizable Themes**: Support for different color schemes and preferences
- **Font Management**: Professional monospace font handling with size options
- **Search Capabilities**: Built-in find and replace with regex support

### Node Integration
- **Function Extraction**: Seamless integration with node function definitions
- **Pin Generation**: Code changes automatically update node pin configurations
- **Error Reporting**: Integration with execution engine for runtime error display
- **Live Updates**: Real-time updates to node behavior as code changes

## Dependencies

- **PySide6**: Qt text editing widgets and syntax highlighting framework
- **Core Module**: Integration with node system for function management
- **Python AST**: Abstract syntax tree parsing for code analysis
- **Regular Expressions**: Pattern matching for syntax highlighting rules

## Usage Notes

- Code editor supports standard keyboard shortcuts for editing operations
- Syntax highlighting updates in real-time as code is typed
- Line numbers automatically adjust to accommodate code length
- Integration with node system ensures code changes immediately affect node behavior
- Professional editing features provide a familiar development environment

## Syntax Highlighting Rules

### Language Elements
- **Keywords**: Python reserved words (def, class, if, for, etc.)
- **Strings**: Single, double, and triple-quoted string literals
- **Comments**: Single-line and multi-line comment blocks
- **Numbers**: Integer, float, and complex number literals
- **Operators**: Arithmetic, comparison, and logical operators

### Advanced Features
- **Function Names**: Custom highlighting for function definitions
- **Class Names**: Special formatting for class declarations
- **Built-ins**: Highlighting for Python built-in functions and types
- **Decorators**: Special formatting for Python decorator syntax

## Architecture Integration

The code editing module provides the essential link between PyFlowGraph's visual interface and the underlying Python code. It ensures that users can seamlessly transition between visual and textual programming paradigms while maintaining professional code editing standards.
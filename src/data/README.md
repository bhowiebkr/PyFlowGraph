# Data Module

This module handles data persistence, file operations, and format conversions for PyFlowGraph. It manages the serialization and deserialization of node graphs, providing clean and efficient file formats for saving and loading projects.

## Purpose

The data module abstracts all file operations and data format handling, ensuring consistent and reliable persistence of node graphs. It supports multiple file formats and provides robust error handling for file operations.

## Key Files

### `__init__.py`
Standard Python package initialization file.

### `file_operations.py`
- Core file I/O operations for node graphs
- File loading and saving with error handling
- Import/export functionality for different formats
- File validation and integrity checking
- Backup and recovery mechanisms
- Recent files management

### `flow_format.py`
- **FlowFormat**: Implementation of PyFlowGraph's native markdown-based format
- JSON-based graph serialization and deserialization
- Node graph structure preservation
- Metadata handling and versioning
- Format conversion utilities
- Backward compatibility support

## File Format Details

### Markdown Flow Format (.md)
PyFlowGraph uses a clean markdown-based format that combines:
- Human-readable project information
- JSON serialization of the complete node graph
- Embedded metadata for versioning and compatibility
- Comments and documentation support

### JSON Structure
The serialized graph includes:
- Node definitions with code and properties
- Pin configurations and type information
- Connection mappings between nodes
- Group structures and hierarchies
- View state and layout information

## Dependencies

- **Core Module**: Serializes core objects (nodes, pins, connections, groups)
- **JSON**: Standard library for data serialization
- **File System**: Platform-specific file operations
- **Error Handling**: Robust error reporting and recovery

## Usage Notes

- All file operations include comprehensive error handling
- The markdown format is designed to be both machine and human readable
- JSON serialization preserves complete graph state including visual layout
- File format versioning ensures backward compatibility
- Large graphs are efficiently serialized with minimal memory usage

## Format Examples

### Basic Flow File Structure
```markdown
# Project Title

Project description and documentation.

## Graph Data

```json
{
  "nodes": [...],
  "connections": [...],
  "groups": [...],
  "metadata": {...}
}
```
```

## Architecture Integration

The data module serves as the bridge between PyFlowGraph's runtime representation and persistent storage. It ensures that complex node graphs can be reliably saved, shared, and restored across sessions while maintaining all visual and functional aspects of the design.
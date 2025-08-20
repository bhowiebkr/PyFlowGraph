# Core Module

This module contains the fundamental components of PyFlowGraph's node-based visual scripting system. It implements the core data structures and logic for nodes, pins, connections, groups, and the node graph itself.

## Purpose

The core module provides the essential building blocks for the visual node editor. It implements the "Code as Nodes" philosophy where Python functions become visual nodes with automatically generated input/output pins based on function signatures and type hints.

## Key Files

### `__init__.py`
Standard Python package initialization file.

### `node.py`
- **Node**: Main node class representing executable code blocks
- **ResizableWidgetContainer**: Supports resizable node widgets
- Automatic pin generation from Python function signatures
- Node state management, positioning, and rendering
- Integration with code editor for function editing

### `pin.py`
- **Pin**: Input and output connection points on nodes
- Type-based pin coloring and validation
- Pin positioning and layout management
- Data type inference and conversion
- Connection compatibility checking

### `connection.py`
- **Connection**: Bezier curve connections between pins
- Visual connection rendering with smooth curves
- Connection state management (valid, invalid, temporary)
- Data flow representation and validation
- Connection hit testing and selection

### `reroute_node.py`
- **RerouteNode**: Simple pass-through nodes for organizing connections
- Minimal visual footprint for clean graph layout
- Single input/output pin for data routing
- Connection path optimization and management

### `node_graph.py`
- **NodeGraph**: Main QGraphicsScene managing the entire node graph
- Node and connection creation and deletion
- Clipboard operations (copy, paste, duplicate)
- Selection management and multi-selection
- Graph serialization and deserialization

### `group.py`
- **Group**: Container for organizing related nodes
- Group boundary management and visual representation
- Nested group support and hierarchy management
- Group interface generation and pin routing

### `group_connection_router.py`
- Manages connections that cross group boundaries
- Automatic interface pin generation for groups
- Connection routing optimization through group hierarchies
- Group interface consistency validation

### `group_interface_pin.py`
- **GroupInterfacePin**: Special pins that represent group inputs/outputs
- Automatic generation based on internal connections
- Type inference from grouped node pins
- Interface consistency and validation

### `group_pin_generator.py`
- Analyzes node groups to generate appropriate interface pins
- Determines required inputs and outputs for groups
- Manages pin type consistency across group boundaries
- Handles complex group interface scenarios

### `group_type_inference.py`
- Infers data types for group interface pins
- Analyzes internal node connections for type propagation
- Handles type conflicts and resolution
- Provides type validation for group interfaces

### `connection_analyzer.py`
- Analyzes connection validity and data flow
- Detects circular dependencies and invalid connections
- Provides connection suggestions and error reporting
- Optimizes connection routing and performance

### `event_system.py`
- **EventSystem**: Centralized event handling for the node graph
- Live mode execution support
- Event propagation and listener management
- Integration with execution engine for real-time updates

## Dependencies

- **Qt Framework**: Uses QGraphicsScene, QGraphicsItem for rendering
- **Data Module**: For serialization and file format handling
- **Execution Module**: For node execution and data flow
- **Commands Module**: For undo/redo operations

## Usage Notes

- All core objects are designed to work within Qt's graphics framework
- Node pins are automatically generated from Python function signatures
- The event system enables real-time execution and live mode
- Groups provide hierarchical organization without affecting execution logic
- Connection validation ensures type safety and prevents invalid data flow

## Architecture Integration

The core module is the foundation of PyFlowGraph's visual scripting capabilities. It bridges the gap between Python code and visual representation, enabling intuitive node-based programming while maintaining the full power of Python.
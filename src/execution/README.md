# Execution Module

This module provides the graph execution engine that runs PyFlowGraph node networks. It implements data-driven execution with subprocess isolation, ensuring secure and reliable code execution while maintaining performance and stability.

## Purpose

The execution module transforms visual node graphs into executable programs. It handles data flow analysis, dependency resolution, subprocess management, and provides both batch and interactive execution modes for different use cases.

## Key Files

### `__init__.py`
Standard Python package initialization file.

### `graph_executor.py`
- **GraphExecutor**: Main execution engine for node graphs
- Data-driven execution with automatic dependency resolution
- Subprocess isolation for security and stability
- JSON-based data serialization between processes
- Error handling and execution state management
- Performance optimization and caching

### `execution_controller.py`
- **ExecutionController**: Central coordination for graph execution
- Execution mode management (batch, interactive, live)
- Progress tracking and status reporting
- Resource management and cleanup
- Integration with UI for execution feedback

### `environment_manager.py`
- **EnvironmentManager**: Abstract base class for Python environment management
- Virtual environment detection and selection
- Package installation and dependency management
- Environment isolation and configuration
- Cross-platform environment handling

### `default_environment_manager.py`
- **DefaultEnvironmentManager**: Default implementation of environment management
- System Python environment detection
- Basic virtual environment support
- Fallback environment configuration
- Simple dependency resolution

## Execution Process

### Data Flow Execution
1. **Dependency Analysis**: Determines execution order based on data dependencies
2. **Node Preparation**: Serializes node code and input data
3. **Subprocess Launch**: Executes nodes in isolated Python processes
4. **Data Transfer**: Passes results between nodes via JSON serialization
5. **Result Collection**: Aggregates outputs and handles errors

### Security Features
- **Process Isolation**: Each node runs in a separate subprocess
- **Sandboxing**: Limited access to system resources
- **Timeout Management**: Prevents infinite loops and hanging processes
- **Resource Limits**: Memory and CPU usage constraints
- **Code Validation**: Basic safety checks before execution

## Dependencies

- **Core Module**: Executes core node objects and manages data flow
- **Subprocess**: Python standard library for process management
- **JSON**: Data serialization for inter-process communication
- **Event System**: Progress reporting and status updates

## Usage Notes

- All node execution happens in isolated subprocesses for security
- Data flow is JSON-serializable, limiting supported data types
- Execution order is determined automatically from node connections
- Long-running nodes can be cancelled and provide progress updates
- Virtual environment support allows using different Python setups

## Execution Modes

### Batch Mode
- Executes entire graph from start to finish
- Optimized for performance and resource usage
- Suitable for data processing pipelines
- Provides comprehensive error reporting

### Interactive Mode
- Executes individual nodes or subgraphs
- Real-time feedback and debugging support
- Allows incremental development and testing
- Integrates with live mode for immediate updates

### Live Mode
- Automatically re-executes when inputs change
- Real-time data visualization and monitoring
- Suitable for interactive applications and dashboards
- Event-driven execution with minimal latency

## Architecture Integration

The execution module is the runtime engine that brings PyFlowGraph's visual programs to life. It bridges the gap between visual design and actual computation, providing a secure and efficient platform for running complex data processing workflows.
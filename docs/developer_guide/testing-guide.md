# PyFlowGraph Testing Guide

## Quick Start

### GUI Test Runner (Recommended)
```batch
run_test_gui.bat
```
- Professional PySide6 test interface
- Visual test selection with checkboxes
- Real-time pass/fail indicators
- Detailed output viewing
- Background execution with progress tracking

### Manual Test Execution
```batch
python tests/test_name.py
```
- Run individual test files directly
- Useful for debugging specific issues

## Current Test Suite

### Core System Tests
- **`test_node_system.py`** - Node creation, properties, code management, serialization
- **`test_pin_system.py`** - Pin creation, type detection, positioning, connection compatibility  
- **`test_connection_system.py`** - Connection/bezier curves, serialization, reroute nodes
- **`test_graph_management.py`** - Graph operations, clipboard, node/connection management
- **`test_execution_engine.py`** - Code execution, flow control, subprocess isolation
- **`test_file_formats.py`** - Markdown and JSON format parsing, conversion, file operations
- **`test_integration.py`** - End-to-end workflows and real-world usage scenarios

### Command System Tests
- **`test_command_system.py`** - Command pattern implementation for undo/redo
- **`test_basic_commands.py`** - Basic command functionality
- **`test_reroute_*.py`** - Reroute node command testing

### GUI-Specific Tests
- **`test_gui_node_deletion.py`** - GUI node deletion workflows
- **`test_markdown_loaded_deletion.py`** - Markdown-loaded node deletion testing
- **`test_user_scenario.py`** - Real user interaction scenarios
- **`test_view_state_persistence.py`** - View state management testing

## Test Design Principles

- **Focused Coverage**: Each test module covers a single core component
- **Fast Execution**: All tests designed for quick feedback
- **Deterministic**: Reliable, non-flaky test execution
- **Comprehensive**: Full coverage of fundamental functionality
- **Integration Testing**: Real-world usage scenarios and error conditions

## Test Runner Features

- Automatic test discovery from `tests/` directory
- Visual test selection interface
- Real-time status indicators (green/red)
- Detailed test output with syntax highlighting
- Professional dark theme matching main application
- 5-second timeout per test for fast feedback

## Running Tests

### Using GUI Runner
1. Launch: `run_test_gui.bat`
2. Select tests via checkboxes
3. Click "Run Selected Tests"
4. View real-time results and detailed output

### Manual Execution
```batch
# Individual test files
python tests/test_node_system.py
python tests/test_pin_system.py
python tests/test_connection_system.py

# Test runner GUI directly
python src/test_runner_gui.py
```

## Troubleshooting

**Environment Issues:**
- Ensure you're in PyFlowGraph root directory
- Verify PySide6 installed: `pip install PySide6`
- Activate virtual environment if used

**Test Failures:**
- Check detailed output in GUI runner
- Run individual tests for specific debugging
- Review test reports in `test_reports/` directory
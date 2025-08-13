# Test Runner Scripts

This directory contains helper scripts to easily run the GUI loading tests.

## Quick Start

### Option 1: Quick Test (Recommended)
```batch
run_quick_test.bat
```
- Runs the 2 most important tests
- Identifies the core issues quickly
- Shows clear diagnosis and recommendations
- Takes ~1-2 minutes

### Option 2: Interactive Test Menu
```batch
run_tests.bat
```
- Interactive menu to choose specific tests
- Run individual test suites
- Option to run all tests
- More detailed testing options

## Test Files Overview

### Core Issue Detection
- **`test_specific_gui_bugs.py`** - Tests your exact reported issue with text_processing_pipeline.md
- **`test_pin_creation_bug.py`** - Identifies the root cause (pin direction bug)

### Comprehensive Testing  
- **`test_gui_rendering.py`** - Verifies visual GUI rendering works
- **`test_gui_loading.py`** - Full GUI loading test suite
- **`test_gui_loading_bugs.py`** - Basic GUI bug detection
- **`test_execution_flow.py`** - Original execution test

## Test Results Interpretation

### ✅ If Tests Pass
- **GUI Tests Pass**: GUI components are working correctly
- **Pin Tests Pass**: Pin creation and categorization is working

### ❌ If Tests Fail
- **GUI Tests Fail**: GUI rendering issues detected
- **Pin Tests Fail**: Pin direction categorization bug (likely root cause)

## Current Known Issue

Based on test results, the issue is:
- **NOT** a GUI rendering problem
- **IS** a pin direction categorization bug during markdown loading
- Nodes have pins but `pin_direction` attributes aren't set properly
- This makes connections fail, causing GUI to appear broken

## Commands Quick Reference

```batch
# Quick diagnosis (recommended)
run_quick_test.bat

# Interactive menu
run_tests.bat

# Run specific tests manually
python test_specific_gui_bugs.py      # Your reported issue
python test_pin_creation_bug.py       # Root cause
python test_gui_rendering.py          # Visual verification
python test_gui_loading.py            # Comprehensive suite
```

## Troubleshooting

If tests fail to run:
1. Ensure you're in the PyFlowGraph directory
2. Check that Python is in your PATH
3. Verify PySide6 is installed: `pip install PySide6`
4. Make sure virtual environment is activated if used

## Next Steps

Once you confirm the pin direction bug:
1. Investigate `node.py` - `update_pins_from_code()` method
2. Check `pin.py` - Pin direction assignment during creation  
3. Review `node_graph.py` - Pin handling during `deserialize()`
4. Focus on markdown loading vs JSON loading differences
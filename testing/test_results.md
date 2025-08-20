# PyFlowGraph Test Results

**Generated:** 2025-08-20 01:33:09  
**Test Runner:** Professional PySide6 GUI Test Tool

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 48 |
| **Passed** | 39 |
| **Failed** | 9 |
| **Success Rate** | 81.2% |
| **Total Duration** | 54.60 seconds |
| **Average Duration** | 1.14 seconds per test |

---

## Test Results Table

| Status | Test Name | Duration | Details |
|--------|-----------|----------|---------|
| ❌ | [test_actual_execution_after_undo.py](#test-actual-execution-after-undo) | 0.70s | FAILED |
| ❌ | [test_code_editor_dialog_integration.py](#test-code-editor-dialog-integration) | 0.16s | FAILED |
| ❌ | [test_execute_graph_modes.py](#test-execute-graph-modes) | 10.02s | FAILED |
| ❌ | [test_group_data_flow.py](#test-group-data-flow) | 0.55s | FAILED |
| ❌ | [test_group_interface_pins.py](#test-group-interface-pins) | 0.22s | FAILED |
| ❌ | [test_group_ui_integration.py](#test-group-ui-integration) | 10.01s | FAILED |
| ❌ | [test_performance_fix_demonstration.py](#test-performance-fix-demonstration) | 0.26s | FAILED |
| ❌ | [test_performance_regression_validation.py](#test-performance-regression-validation) | 0.28s | FAILED |
| ❌ | [test_real_workflow_integration.py](#test-real-workflow-integration) | 0.31s | FAILED |
| ✅ | test_basic_commands.py | 0.13s | PASSED |
| ✅ | test_code_change_command.py | 0.13s | PASSED |
| ✅ | test_code_editor_undo_workflow.py | 0.27s | PASSED |
| ✅ | test_command_system.py | 0.48s | PASSED |
| ✅ | test_composite_commands.py | 0.19s | PASSED |
| ✅ | test_connection_system.py | 0.28s | PASSED |
| ✅ | test_connection_system_headless.py | 0.29s | PASSED |
| ✅ | test_copy_paste_integration.py | 0.17s | PASSED |
| ✅ | test_debug_flags.py | 0.24s | PASSED |
| ✅ | test_delete_undo_performance_regression.py | 2.43s | PASSED |
| ✅ | test_end_to_end_workflows.py | 3.30s | PASSED |
| ✅ | test_execution_engine.py | 0.33s | PASSED |
| ✅ | test_file_formats.py | 0.09s | PASSED |
| ✅ | test_full_gui_integration.py | 6.98s | PASSED |
| ✅ | test_graph_management.py | 0.33s | PASSED |
| ✅ | test_group_resize.py | 0.18s | PASSED |
| ✅ | test_group_system.py | 0.24s | PASSED |
| ✅ | test_gui_node_deletion.py | 0.76s | PASSED |
| ✅ | test_gui_node_deletion_workflow.py | 0.75s | PASSED |
| ✅ | test_gui_value_update_regression.py | 0.30s | PASSED |
| ✅ | test_integration.py | 0.32s | PASSED |
| ✅ | test_markdown_loaded_deletion.py | 0.60s | PASSED |
| ✅ | test_node_deletion_connection_bug.py | 0.23s | PASSED |
| ✅ | test_node_system.py | 0.28s | PASSED |
| ✅ | test_node_system_headless.py | 0.29s | PASSED |
| ✅ | test_password_generator_chaos.py | 4.56s | PASSED |
| ✅ | test_pin_system.py | 0.30s | PASSED |
| ✅ | test_pin_system_headless.py | 0.28s | PASSED |
| ✅ | test_reroute_creation_undo.py | 0.76s | PASSED |
| ✅ | test_reroute_node_deletion.py | 0.59s | PASSED |
| ✅ | test_reroute_undo_redo.py | 0.61s | PASSED |
| ✅ | test_reroute_with_connections.py | 0.60s | PASSED |
| ✅ | test_selection_operations.py | 0.28s | PASSED |
| ✅ | test_undo_history_integration.py | 0.42s | PASSED |
| ✅ | test_undo_history_workflow.py | 0.25s | PASSED |
| ✅ | test_undo_ui_integration.py | 0.41s | PASSED |
| ✅ | test_user_scenario.py | 0.60s | PASSED |
| ✅ | test_user_scenario_gui.py | 0.59s | PASSED |
| ✅ | test_view_state_persistence.py | 2.24s | PASSED |

---

## Detailed Test Results

### <a id="test-actual-execution-after-undo"></a>[FAIL] test_actual_execution_after_undo.py

**Status:** FAILED  
**Duration:** 0.70 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_actual_execution_after_undo.py`

**Output:**
```

=== Actual Execution After Delete-Undo Test ===
Creating nodes manually...
Initial state: 4 nodes, 13 connections

--- Initial Output Node State ---
  Initial output node: Password Output & Copy
  GUI widgets available: True
  GUI code length: 920
  GUI get values code length: 590
  Widget keys: ['password_field', 'copy_btn', 'strength_display']
  Password field text: ''
  Strength display text: 'Generate a password to see str...'
  Connections - Exec inputs: 1, Data inputs: 4

--- Baseline Execution Test ---
Running baseline execution...
EXEC_LOG: --- Executing Node: Password Configuration ---
EXEC_LOG: Password config: 12 chars, Upper: True, Lower: True, Numbers: True, Symbols: False
EXEC_LOG: --- Executing Node: Password Generator Engine ---
EXEC_LOG: Generated password: lNQgirghY9VV
EXEC_LOG: --- Executing Node: Password Strength Analyzer ---
EXEC_LOG: Password strength: Very Strong (Score: 85/100)
Feedback: Add symbols for extra security
EXEC_LOG: --- Executing Node: Password Output & Copy ---
EXEC_LOG: === PASSWORD GENERATION COMPLETE ===
Generated Password: lNQgirghY9VV
Strength: Very Strong (85/100)
Feedback: Add symbols for extra security
Execution completed. Logs count: 8
  LOG: Generated password: lNQgirghY9VV
  LOG: --- Executing Node: Password Strength Analyzer ---
  LOG: Password strength: Very Strong (Score: 85/100)
Feedback: Add symbols for extra security
  LOG: --- Executing Node: Password Output & Copy ---
  LOG: === PASSWORD GENERATION COMPLETE ===
Generated Password: lNQgirghY9VV
Strength: Very Strong (85/100)
Feedback: Add symbols for extra security
Baseline - Password: 'lNQgirghY9VV'
Baseline - Strength: 'Generated Password: lNQgirghY9VV
Strength: Very St...'
Baseline execution successful: password=True, result=True

--- Deleting Middle Nodes ---
Deleting: Password Generator Engine and Password Strength Analyzer
After deletion: 2 nodes, 0 connections

--- Undoing Deletions ---
After undo: 4 nodes, 13 connections

--- Post-Undo Output Node Stat
... (output truncated)
```

[↑ Back to Test Table](#test-results-table)

---

### <a id="test-code-editor-dialog-integration"></a>[FAIL] test_code_editor_dialog_integration.py

**Status:** FAILED  
**Duration:** 0.16 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_code_editor_dialog_integration.py`

**Output:**
```

E.EE.E.
======================================================================
ERROR: test_accept_creates_command_for_code_changes (__main__.TestCodeEditorDialogIntegration.test_accept_creates_command_for_code_changes)
Test accept button creates CodeChangeCommand for execution code changes.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\HOME\PyFlowGraph\tests\test_code_editor_dialog_integration.py", line 105, in test_accept_creates_command_for_code_changes
    with patch.object(CodeEditorDialog, '_handle_accept') as mock_handle_accept:
  File "C:\Users\howard\AppData\Local\Programs\Python\Python311\Lib\unittest\mock.py", line 1427, in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\howard\AppData\Local\Programs\Python\Python311\Lib\unittest\mock.py", line 1400, in get_original
    raise AttributeError(
AttributeError: <Mock spec='str' id='2356574868752'> does not have the attribute '_handle_accept'

======================================================================
ERROR: test_dialog_initialization_with_graph_reference (__main__.TestCodeEditorDialogIntegration.test_dialog_initialization_with_graph_reference)
Test dialog initializes with proper node and graph references.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\howard\AppData\Local\Programs\Python\Python311\Lib\unittest\mock.py", line 1356, in patched
    with self.decoration_helper(patched,
  File "C:\Users\howard\AppData\Local\Programs\Python\Python311\Lib\contextlib.py", line 137, in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
  File "C:\Users\howard\AppData\Local\Programs\Python\Python311\Lib\unittest\mock.py", line 1338, in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\howard\AppData\Local\Programs\Py
... (output truncated)
```

[↑ Back to Test Table](#test-results-table)

---

### <a id="test-execute-graph-modes"></a>[FAIL] test_execute_graph_modes.py

**Status:** FAILED  
**Duration:** 10.02 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_execute_graph_modes.py`

**Output:**
```
Test timed out after 10 seconds
```

[↑ Back to Test Table](#test-results-table)

---

### <a id="test-group-data-flow"></a>[FAIL] test_group_data_flow.py

**Status:** FAILED  
**Duration:** 0.55 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_data_flow.py`

**Output:**
```

QFontDatabase: Must construct a QGuiApplication before accessing QFontDatabase

```

[↑ Back to Test Table](#test-results-table)

---

### <a id="test-group-interface-pins"></a>[FAIL] test_group_interface_pins.py

**Status:** FAILED  
**Duration:** 0.22 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_interface_pins.py`

**Output:**
```

........E...EEE.E...........
======================================================================
ERROR: test_create_routing_for_group (__main__.TestGroupConnectionRouter.test_create_routing_for_group)
Test creating routing table for a group.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\HOME\PyFlowGraph\tests\test_group_interface_pins.py", line 439, in test_create_routing_for_group
    routing_table = self.router.create_routing_for_group(mock_group, interface_pins)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\HOME\PyFlowGraph\src\core\group_connection_router.py", line 70, in create_routing_for_group
    routing_table['internal_connections'] = self._map_internal_connections(group)
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\HOME\PyFlowGraph\src\core\group_connection_router.py", line 133, in _map_internal_connections
    for connection in self.node_graph.connections:
TypeError: 'Mock' object is not iterable

======================================================================
ERROR: test_interface_pin_creation (__main__.TestGroupInterfacePin.test_interface_pin_creation)
Test basic interface pin creation.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\howard\AppData\Local\Programs\Python\Python311\Lib\unittest\mock.py", line 1359, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\HOME\PyFlowGraph\tests\test_group_interface_pins.py", line 171, in test_interface_pin_creation
    pin = GroupInterfacePin(
          ^^^^^^^^^^^^^^^^^^
  File "E:\HOME\PyFlowGraph\src\core\group_interface_pin.py", line 56, in __init__
    self._update_interface_visual_style()
  File "E:\HOME\PyFlowGraph\src\core\group_interface_pin.py", line 64, in _update_interface_visual_style
    if self.
... (output truncated)
```

[↑ Back to Test Table](#test-results-table)

---

### <a id="test-group-ui-integration"></a>[FAIL] test_group_ui_integration.py

**Status:** FAILED  
**Duration:** 10.01 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_ui_integration.py`

**Output:**
```
Test timed out after 10 seconds
```

[↑ Back to Test Table](#test-results-table)

---

### <a id="test-performance-fix-demonstration"></a>[FAIL] test_performance_fix_demonstration.py

**Status:** FAILED  
**Duration:** 0.26 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_performance_fix_demonstration.py`

**Output:**
```

=== Connection Integrity Validation ===
Output pin connections after undo: 1
Input pin connections after undo: 1
CONNECTION INTEGRITY VALIDATION: PASSED
No duplicate connections detected after delete-undo operations

=== Performance Fix Demonstration ===
Created simulation with 4 nodes and 6 connections
Baseline connection traversals: 6

--- Cycle 1 ---
Deleting node: Generator Node
Connections after delete: 3
Undo operation took: 1.79 ms
Connections after undo: 3
Connection traversals after undo: 4
Traversal ratio (current/baseline): 0.67

.F
======================================================================
FAIL: test_performance_fix_demonstration (__main__.TestPerformanceFixDemonstration.test_performance_fix_demonstration)
Demonstrate that performance remains stable after delete-undo cycles.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\HOME\PyFlowGraph\tests\test_performance_fix_demonstration.py", line 188, in test_performance_fix_demonstration
    self.assertEqual(connections_after_undo, initial_connection_count,
AssertionError: 3 != 6 : Cycle 1: Should restore all connections

----------------------------------------------------------------------
Ran 2 tests in 0.079s

FAILED (failures=1)

```

[↑ Back to Test Table](#test-results-table)

---

### <a id="test-performance-regression-validation"></a>[FAIL] test_performance_regression_validation.py

**Status:** FAILED  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_performance_regression_validation.py`

**Output:**
```

=== Testing Duplicate Connection Prevention ===
Initial state: 2 graph connections, 4 pin connections
Undo operation took: 2.68 ms
After undo: 2 graph connections, 6 pin connections

=== Testing Execution Performance Stability ===
Baseline execution time: 0.001 ms
Post-undo execution time: 0.001 ms
Performance ratio (post-undo / baseline): 0.714

=== Testing Multiple Delete-Undo Cycles ===
Cycle 1/3
Cycle 1 performance change: 15.4%
Cycle 2/3
Cycle 2 performance change: 44.2%
Cycle 3/3
Cycle 3 performance change: -1.9%
Maximum performance degradation: 44.2%

=== Testing Performance Regression Thresholds ===
Performance thresholds: Delete=0.01ms, Undo=2.15ms

F...
======================================================================
FAIL: test_duplicate_connection_prevention (__main__.TestPerformanceRegressionValidation.test_duplicate_connection_prevention)
Test that duplicate connections are prevented during undo.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\HOME\PyFlowGraph\tests\test_performance_regression_validation.py", line 159, in test_duplicate_connection_prevention
    self.assertEqual(final_pin_connections, initial_pin_connections,
AssertionError: 6 != 4 : Pin connections should be restored without duplicates

----------------------------------------------------------------------
Ran 4 tests in 0.095s

FAILED (failures=1)

```

[↑ Back to Test Table](#test-results-table)

---

### <a id="test-real-workflow-integration"></a>[FAIL] test_real_workflow_integration.py

**Status:** FAILED  
**Duration:** 0.31 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_real_workflow_integration.py`

**Output:**
```

=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 2 commands
DEBUG: Executing command 1/2: Create 'Node 1' node
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/2: Create 'Node 2' node
DEBUG: Command 2 returned: True
DEBUG: Command 2 succeeded, added to executed list
DEBUG: All 2 commands succeeded
=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===


...F........
======================================================================
FAIL: test_complex_multi_node_operations (__main__.TestRealWorkflowIntegration.test_complex_multi_node_operations)
Test complex operations with multiple nodes from real workflow.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\HOME\PyFlowGraph\tests\test_real_workflow_integration.py", line 178, in test_complex_multi_node_operations
    self.assertEqual(len(delete_cmd.commands), len(mock_nodes))
AssertionError: 0 != 4

----------------------------------------------------------------------
Ran 12 tests in 0.108s

FAILED (failures=1)

```

[↑ Back to Test Table](#test-results-table)

---

### [PASS] test_basic_commands.py

**Status:** PASSED  
**Duration:** 0.13 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_basic_commands.py`

**Output:**
```
Running basic command system tests...

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: First Operation
DEBUG: Command type: MockCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Second Operation
DEBUG: Command type: MockCommand
DEBUG: Current history size: 1
DEBUG: Current index: 0
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 1
DEBUG: History size now: 2
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY UNDO START ===
DEBUG: Attempting to undo command
DEBUG: Current index: 1
DEBUG: History size: 2
DEBUG: Can undo: True
DEBUG: Undoing command: Second Operation
DEBUG: Command type: MockCommand
DEBUG: Calling command.undo()...
DEBUG: Command.undo() returned: True
DEBUG: Command undone successfully, index now: 0
=== COMMAND HISTORY UNDO END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Test Command
DEBUG: Command type: MockCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY UNDO START ===
DEBUG: Attempting to undo command
DEBUG: Current index: 0
DEBUG: History size: 1
DEBUG: Can undo: True
DEBUG: Undoing command: Test Command
DEBUG: Command type: MockCommand
DEBUG: Calling command.undo()...
DEBUG: Command.undo() ret
... (output truncated)
```

---

### [PASS] test_code_change_command.py

**Status:** PASSED  
**Duration:** 0.13 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_code_change_command.py`

**Output:**
```
Failed to change code: Set code failed
Failed to undo code change: Undo failed

```

---

### [PASS] test_code_editor_undo_workflow.py

**Status:** PASSED  
**Duration:** 0.27 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_code_editor_undo_workflow.py`

---

### [PASS] test_command_system.py

**Status:** PASSED  
**Duration:** 0.48 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_command_system.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Test Command
DEBUG: Command type: MockCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 0
DEBUG: Command type: MockCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 1
DEBUG: Command type: MockCommand
DEBUG: Current history size: 1
DEBUG: Current index: 0
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 1
DEBUG: History size now: 2
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 2
DEBUG: Command type: MockCommand
DEBUG: Current history size: 2
DEBUG: Current index: 1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 2
DEBUG: History size now: 3
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 3
DEBUG: Command type: MockCommand
DEBUG: Current history size: 3
DEBUG: Current index: 2
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: C
... (output truncated)
```

---

### [PASS] test_composite_commands.py

**Status:** PASSED  
**Duration:** 0.19 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_composite_commands.py`

**Output:**
```

=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 2 commands
DEBUG: Executing command 1/2: Success 1
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/2: Success 2
DEBUG: Command 2 returned: True
DEBUG: Command 2 succeeded, added to executed list
DEBUG: All 2 commands succeeded
=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===


=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 3 commands
DEBUG: Executing command 1/3: Success 1
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/3: Success 2
DEBUG: Command 2 returned: True
DEBUG: Command 2 succeeded, added to executed list
DEBUG: Executing command 3/3: Success 3
DEBUG: Command 3 returned: True
DEBUG: Command 3 succeeded, added to executed list
DEBUG: All 3 commands succeeded
=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===


=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 3 commands
DEBUG: Executing command 1/3: Success 1
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/3: Success 2
DEBUG: Command 2 returned: True
DEBUG: Command 2 succeeded, added to executed list
DEBUG: Executing command 3/3: Success 3
DEBUG: Command 3 returned: True
DEBUG: Command 3 succeeded, added to executed list
DEBUG: All 3 commands succeeded
=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===

DEBUG: CompositeCommand.undo() - undoing 3 commands
DEBUG: Undoing command 1/3: Success 3
DEBUG: Command 1 undo returned: True
DEBUG: Command 1 undone successfully
DEBUG: Undoing command 2/3: Success 2
DEBUG: Command 2 undo returned: False
DEBUG: Command 2 undo FAILED
DEBUG: Undoing command 3/3: Success 1
DEBUG: Command 3 undo returned: True
DEBUG: Command 3 undone successfully
DEBUG: 2/3 commands undone successfully, composite marked as undone
DEBUG: CompositeCommand.undo() returning: True


... (output truncated)
```

---

### [PASS] test_connection_system.py

**Status:** PASSED  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_connection_system.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Disconnect Output Node.output from Input Node.input
DEBUG: Command type: DeleteConnectionCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


```

---

### [PASS] test_connection_system_headless.py

**Status:** PASSED  
**Duration:** 0.29 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_connection_system_headless.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Disconnect Output Node.output from Input Node.input
DEBUG: Command type: DeleteConnectionCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


```

---

### [PASS] test_copy_paste_integration.py

**Status:** PASSED  
**Duration:** 0.17 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_copy_paste_integration.py`

**Output:**
```

=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 2 commands
DEBUG: Executing command 1/2: <Mock name='mock.get_description()' id='2033699299216'>
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/2: <Mock name='mock.get_description()' id='2033699201104'>
DEBUG: Command 2 returned: False
DEBUG: Command 2 FAILED - rolling back 1 executed commands
DEBUG: Rolling back command 1/1: <Mock name='mock.get_description()' id='2033699299216'>
DEBUG: Rollback 1 returned: True
DEBUG: Rollback complete, composite command failed
=== COMPOSITE COMMAND EXECUTE END (FAILED) ===


=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 2 commands
DEBUG: Executing command 1/2: <Mock name='mock.get_description()' id='2033699326416'>
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/2: <Mock name='mock.get_description()' id='2033699328208'>
DEBUG: Command 2 returned: True
DEBUG: Command 2 succeeded, added to executed list
DEBUG: All 2 commands succeeded
=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===

DEBUG: CompositeCommand.undo() - undoing 2 commands
DEBUG: Undoing command 1/2: <Mock name='mock.get_description()' id='2033699328208'>
DEBUG: Command 1 undo returned: True
DEBUG: Command 1 undone successfully
DEBUG: Undoing command 2/2: <Mock name='mock.get_description()' id='2033699326416'>
DEBUG: Command 2 undo returned: True
DEBUG: Command 2 undone successfully
DEBUG: All commands undone successfully, composite marked as undone
DEBUG: CompositeCommand.undo() returning: True

```

---

### [PASS] test_debug_flags.py

**Status:** PASSED  
**Duration:** 0.24 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_debug_flags.py`

---

### [PASS] test_delete_undo_performance_regression.py

**Status:** PASSED  
**Duration:** 2.43 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_delete_undo_performance_regression.py`

---

### [PASS] test_end_to_end_workflows.py

**Status:** PASSED  
**Duration:** 3.30 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_end_to_end_workflows.py`

**Output:**
```
============================================================
STARTING END-TO-END WORKFLOW TESTS
============================================================

These tests simulate complete user workflows:
- Data processing pipelines
- File operations (save/load)
- Error recovery scenarios

Each test will open a PyFlowGraph window and perform
the complete workflow automatically.

test_create_simple_data_pipeline (__main__.TestDataProcessingWorkflow.test_create_simple_data_pipeline)
WORKFLOW: User creates a simple data processing pipeline ... 
=== WORKFLOW TEST: test_create_simple_data_pipeline ===

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2288178039808)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x214c1c44bd0, parent=0x214c1a83c70, pos=0,84.5) at 0x00000214C20CBB00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x214c1c44690, parent=0x214c1a83c70, pos=0,109.5) at 0x00000214C20CBCC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x214c1c441d0, parent=0x214c1a83c70, pos=0,134.5) at 0x00000214C20D6340>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x214c1c44390, parent=0x214c1a83c70, pos=0,159.5) at 0x00000214C20D6140>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x214c1c443d0, parent=0x214c1a83c70, pos=0,184.5) at 0x00000214C20D5F00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x214c1c44c90, parent=0x214c1a83c70, pos=250,84.5) at 0x00000214C20D5940>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x214c1c44550, parent=0x214c1a83c70, pos=250,109.5) at 0x00000214C20D7380>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x214c1c44610, parent=0x214c1a83c70, pos=250,134.5) at 0x00000214C20
... (output truncated)
```

---

### [PASS] test_execution_engine.py

**Status:** PASSED  
**Duration:** 0.33 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_execution_engine.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Producer' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 44.2ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Consumer' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 1
DEBUG: Current index: 0
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 1
DEBUG: History size now: 2
DEBUG: Command execution completed successfully in 2.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Connect Producer.output_1 to Consumer.data
DEBUG: Command type: CreateConnectionCommand
DEBUG: Current history size: 2
DEBUG: Current index: 1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 2
DEBUG: History size now: 3
DEBUG: Command execution completed successfully in 0.3ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Entry Node' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 1.7ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Middle Node' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current 
... (output truncated)
```

---

### [PASS] test_file_formats.py

**Status:** PASSED  
**Duration:** 0.09 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_file_formats.py`

---

### [PASS] test_full_gui_integration.py

**Status:** PASSED  
**Duration:** 6.98 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_full_gui_integration.py`

**Output:**
```
============================================================
STARTING FULL GUI INTEGRATION TEST SUITE
============================================================

These tests will open actual PyFlowGraph windows.
Each test window will appear briefly then close automatically.
Do not interact with the test windows during execution.

test_application_window_opens (__main__.TestApplicationStartup.test_application_window_opens)
Test that the main application window opens correctly. ... 
=== Starting Test: test_application_window_opens ===

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2845244404032)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2967388be80, parent=0x296736bcd10, pos=0,84.5) at 0x0000029675C877C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2967388d780, parent=0x296736bcd10, pos=0,109.5) at 0x0000029675C87BC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2967388d580, parent=0x296736bcd10, pos=0,134.5) at 0x0000029675C96080>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2967388cec0, parent=0x296736bcd10, pos=0,159.5) at 0x0000029675C95CC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2967388d480, parent=0x296736bcd10, pos=0,184.5) at 0x0000029675C95D00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2967388cd00, parent=0x296736bcd10, pos=250,84.5) at 0x0000029675C959C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2967388ca00, parent=0x296736bcd10, pos=250,109.5) at 0x0000029675C96FC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2967388d0c0, parent=0x296736bcd10, pos=250,134.5) at 0x0000029675C97140>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin
... (output truncated)
```

---

### [PASS] test_graph_management.py

**Status:** PASSED  
**Duration:** 0.33 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_graph_management.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Copy Node 1' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 52.3ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Copy Node 2' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 1
DEBUG: Current index: 0
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 1
DEBUG: History size now: 2
DEBUG: Command execution completed successfully in 2.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Connect Copy Node 1.output_1 to Copy Node 2.text
DEBUG: Command type: CreateConnectionCommand
DEBUG: Current history size: 2
DEBUG: Current index: 1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 2
DEBUG: History size now: 3
DEBUG: Command execution completed successfully in 0.1ms
=== COMMAND HISTORY EXECUTE END ===

Copied 2 nodes to clipboard as markdown.

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Output Node' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 1.9ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Input Node' node
D
... (output truncated)
```

---

### [PASS] test_group_resize.py

**Status:** PASSED  
**Duration:** 0.18 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_resize.py`

---

### [PASS] test_group_system.py

**Status:** PASSED  
**Duration:** 0.24 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_system.py`

**Output:**
```
Created group 'Test Group' with 2 members
Created group 'Test Group' with 2 members
Undid creation of group 'Test Group'
Redid creation of group 'Test Group'
Created group 'Test Group' with 2 members
Undid creation of group 'Test Group'

```

---

### [PASS] test_gui_node_deletion.py

**Status:** PASSED  
**Duration:** 0.76 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_gui_node_deletion.py`

**Output:**
```
Starting GUI Node Deletion Test...
This test will open a PyFlowGraph window and test node deletion.
Loaded file_organizer_automation.md for testing

============================================================
STARTING NODE DELETION TEST
============================================================
Testing deletion of nodes from loaded file...

=== Graph Analysis: Initial state ===
Nodes in graph.nodes: 4
Connections in graph.connections: 13
Total scene items: 95
  Node: Password Output & Copy - Scene: True
  Node: Password Strength Analyzer - Scene: True
  Node: Password Generator Engine - Scene: True
  Node: Password Configuration - Scene: True
  Connection: <core.connection.Connection(0x21d4d418740, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D76471C00> - Scene: True
  Connection: <core.connection.Connection(0x21d4d418d40, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D76471D80> - Scene: True
  Connection: <core.connection.Connection(0x21d4d418d00, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D76447580> - Scene: True
  Connection: <core.connection.Connection(0x21d4d419000, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D76447B40> - Scene: True
  Connection: <core.connection.Connection(0x21d4d419500, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D764477C0> - Scene: True
  Connection: <core.connection.Connection(0x21d4d419200, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D76447700> - Scene: True
  Connection: <core.connection.Connection(0x21d4d4187c0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D76447780> - Scene: True
  Connection: <core.connection.Connection(0x21d4d418e80, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D76447AC0> - Scene: True
  Connection: <core.connection.Connection(0x21d4d418e40, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D4F0A35C0> - Scene: True
  Connection: <core.connection.Connection(0x21d4d418c80, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021D76447C00> - Scene: T
... (output truncated)
```

---

### [PASS] test_gui_node_deletion_workflow.py

**Status:** PASSED  
**Duration:** 0.75 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_gui_node_deletion_workflow.py`

**Output:**
```
Starting GUI Node Deletion Test...
This test will open a PyFlowGraph window and test node deletion.
Loaded file_organizer_automation.md for testing

============================================================
STARTING NODE DELETION TEST
============================================================
Testing deletion of nodes from loaded file...

=== Graph Analysis: Initial state ===
Nodes in graph.nodes: 4
Connections in graph.connections: 13
Total scene items: 95
  Node: Password Output & Copy - Scene: True
  Node: Password Strength Analyzer - Scene: True
  Node: Password Generator Engine - Scene: True
  Node: Password Configuration - Scene: True
  Connection: <core.connection.Connection(0x21c69d9e5f0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C69CD0600> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9ea70, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C69C880C0> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9ea30, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C69CD0300> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9e1f0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C4393B9C0> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9e0f0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C69CD0040> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9e430, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C69CD3F80> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9ebf0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C69CD3DC0> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9e7f0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C69CD3A80> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9ec30, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C439A08C0> - Scene: True
  Connection: <core.connection.Connection(0x21c69d9ecb0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000021C69CD0A40> - Scene: T
... (output truncated)
```

---

### [PASS] test_gui_value_update_regression.py

**Status:** PASSED  
**Duration:** 0.30 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_gui_value_update_regression.py`

**Output:**
```

=== Connection Integrity Test ===

=== Creating Password Generator Simulation ===
Created 4 nodes and 13 connections
Nodes: ['Password Configuration', 'Password Generator Engine', 'Password Strength Analyzer', 'Password Output & Copy']
Initial connections: 13
Final connections: 13
Output node - Exec inputs: 2, Data inputs: 8

=== GUI Value Update Regression Test ===

=== Creating Password Generator Simulation ===
Created 4 nodes and 13 connections
Nodes: ['Password Configuration', 'Password Generator Engine', 'Password Strength Analyzer', 'Password Output & Copy']

--- Initial State ---
Total nodes: 4
Total connections: 13

=== Verifying Output Node GUI State ===
Node title: Password Output & Copy
GUI widgets available: True
Widget keys: ['password_field', 'copy_btn', 'strength_display']
Password field available: True
Strength display available: True
Password field text: ''
Strength display text: 'Generate a password to see strength analysis......'

--- Baseline Execution Test ---
Testing baseline GUI value update...
Calling set_gui_values with: {'output_1': 'Generated Password: TestPassword123!\nStrength: Very Strong (80/100)\nFeedback: Excellent password!'}
Baseline password field text: 'TestPassword123!'
Baseline strength display text: 'Generated Password: TestPassword123!
Strength: Ver...'

--- Deleting Middle Nodes ---
Deleting: Password Generator Engine and Password Strength Analyzer
After deletion - Nodes: 2, Connections: 0

--- Undoing Deletions ---
After undo - Nodes: 4, Connections: 13

--- Post-Undo GUI State Verification ---

=== Verifying Output Node GUI State ===
Node title: Password Output & Copy
GUI widgets available: True
Widget keys: ['password_field', 'copy_btn', 'strength_display']
Password field available: True
Strength display available: True
Password field text: 'TestPassword123!'
Strength display text: 'Generated Password: TestPassword123!
Strength: Ver...'

--- Critical Test: GUI Value Update After Undo ---
Testing post-undo GUI value updat
... (output truncated)
```

---

### [PASS] test_integration.py

**Status:** PASSED  
**Duration:** 0.32 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_integration.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Input' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 49.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Process' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 1
DEBUG: Current index: 0
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 1
DEBUG: History size now: 2
DEBUG: Command execution completed successfully in 2.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Output' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 2
DEBUG: Current index: 1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 2
DEBUG: History size now: 3
DEBUG: Command execution completed successfully in 1.7ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Connect Input.output_1 to Process.text
DEBUG: Command type: CreateConnectionCommand
DEBUG: Current history size: 3
DEBUG: Current index: 2
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 3
DEBUG: History size now: 4
DEBUG: Command execution completed successfully in 0.3ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Connect Process.output_1 to Output.text
DEBUG: Command type: CreateConnectionCommand
DEBUG: C
... (output truncated)
```

---

### [PASS] test_markdown_loaded_deletion.py

**Status:** PASSED  
**Duration:** 0.60 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_markdown_loaded_deletion.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2391649771456)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9212310, parent=0x22cd9033990, pos=0,84.5) at 0x0000022CD97144C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9214190, parent=0x22cd9033990, pos=0,109.5) at 0x0000022CD9714480>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9213fd0, parent=0x22cd9033990, pos=0,134.5) at 0x0000022CD9716B40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd92135d0, parent=0x22cd9033990, pos=0,159.5) at 0x0000022CD97169C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9213610, parent=0x22cd9033990, pos=0,184.5) at 0x0000022CD9716700>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9213490, parent=0x22cd9033990, pos=250,84.5) at 0x0000022CD97163C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9213410, parent=0x22cd9033990, pos=250,109.5) at 0x0000022CD9717800>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd92140d0, parent=0x22cd9033990, pos=250,134.5) at 0x0000022CD9717B00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9213390, parent=0x22cd9033990, pos=250,159.5) at 0x0000022CD9717C80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9213790, parent=0x22cd9033990, pos=250,184.5) at 0x0000022CD9716200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9213b90, parent=0x22cd9033990, pos=0,59.5) at 0x0000022CD971A080>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22cd9213d10, parent=0x22cd9033990, pos=250,59.5) at 0x0000022CD971A180>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_node_deletion_connection_bug.py

**Status:** PASSED  
**Duration:** 0.23 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_node_deletion_connection_bug.py`

**Output:**
```
Initial state: 2 nodes, 1 connections
After deletion: 1 nodes, 0 connections
After undo: 2 nodes, 0 connections
After connection deletions: 0 connections
TEST PASSED: Connection deletion after node undo works correctly
Node has 0 input pins and 0 output pins
Restored node has 0 input pins and 0 output pins
TEST PASSED: Node undo with code-based pins works

All tests passed! The connection deletion bug has been fixed.

```

---

### [PASS] test_node_system.py

**Status:** PASSED  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_node_system.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Deserialized Node' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 1.7ms
=== COMMAND HISTORY EXECUTE END ===


```

---

### [PASS] test_node_system_headless.py

**Status:** PASSED  
**Duration:** 0.29 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_node_system_headless.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Deserialized Node' node
DEBUG: Command type: CreateNodeCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 2.0ms
=== COMMAND HISTORY EXECUTE END ===


```

---

### [PASS] test_password_generator_chaos.py

**Status:** PASSED  
**Duration:** 4.56 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_password_generator_chaos.py`

**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.4.1, pluggy-1.6.0 -- E:\HOME\PyFlowGraph\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\HOME\PyFlowGraph
plugins: cov-6.2.1, mock-3.14.1, timeout-2.4.0, xdist-3.8.0
collecting ... collected 1 item

tests/test_password_generator_chaos.py::TestPasswordGeneratorChaos::test_chaos_deletion_undo_redo_execution Available nodes: 4
  Node: Password Configuration - config-input
  Node: Password Generator Engine - password-generator
  Node: Password Strength Analyzer - strength-analyzer
  Node: Password Output & Copy - output-display
Initial password: '', strength: '...'

--- Chaos Cycle 1 ---

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Disconnect Password Configuration.output_4 from Password Generator Engine.include_numbers
DEBUG: Command type: DeleteConnectionCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.3ms
=== COMMAND HISTORY EXECUTE END ===


=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=True
DEBUG: Node to remove: 'Password Strength Analyzer' (ID: 2305213078336)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 94 items before removal
DEBUG: Using command pattern for removal

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Delete 'Password Strength Analyzer' node
DEBUG: Command type: DeleteNodeCommand
DEBUG: Current history size: 1
DEBUG: Current index: 0
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 1
DEBUG: History size now: 2
DEBUG: Command execution completed successfully in 0.9ms
=== COMMAND HISTORY EXECUTE 
... (output truncated)
```

---

### [PASS] test_pin_system.py

**Status:** PASSED  
**Duration:** 0.30 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_pin_system.py`

---

### [PASS] test_pin_system_headless.py

**Status:** PASSED  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_pin_system_headless.py`

---

### [PASS] test_reroute_creation_undo.py

**Status:** PASSED  
**Duration:** 0.76 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_creation_undo.py`

**Output:**
```
Testing RerouteNode creation/deletion/undo sequence...


=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2634610057472)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b39f000, parent=0x2656b1d7d50, pos=0,84.5) at 0x000002656DED0900>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b3a0200, parent=0x2656b1d7d50, pos=0,109.5) at 0x000002656DED00C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b3a0140, parent=0x2656b1d7d50, pos=0,134.5) at 0x000002656DED31C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b39fac0, parent=0x2656b1d7d50, pos=0,159.5) at 0x000002656DED2D80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b3a0180, parent=0x2656b1d7d50, pos=0,184.5) at 0x000002656DED2B80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b39f800, parent=0x2656b1d7d50, pos=250,84.5) at 0x000002656DED2A40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b3a0600, parent=0x2656b1d7d50, pos=250,109.5) at 0x000002656DED2840>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b39fe40, parent=0x2656b1d7d50, pos=250,134.5) at 0x000002656DEDA780>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b39fbc0, parent=0x2656b1d7d50, pos=250,159.5) at 0x000002656DEDA500>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b39f9c0, parent=0x2656b1d7d50, pos=250,184.5) at 0x000002656DED2AC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b3a00c0, parent=0x2656b1d7d50, pos=0,59.5) at 0x000002656DEDAEC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2656b3a0100, parent=0x2656b1d7d50, pos=250,59.5) at 0x000002656DEDB140>
DEBU
... (output truncated)
```

---

### [PASS] test_reroute_node_deletion.py

**Status:** PASSED  
**Duration:** 0.59 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_node_deletion.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 1858654058688)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2aad0, parent=0x1b0bdc47630, pos=0,84.5) at 0x000001B0C06C0700>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2b650, parent=0x1b0bdc47630, pos=0,109.5) at 0x000001B0C06C0040>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2b390, parent=0x1b0bdc47630, pos=0,134.5) at 0x000001B0C06C2EC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2a2d0, parent=0x1b0bdc47630, pos=0,159.5) at 0x000001B0C06C2CC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2c190, parent=0x1b0bdc47630, pos=0,184.5) at 0x000001B0C06C2800>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2b850, parent=0x1b0bdc47630, pos=250,84.5) at 0x000001B0C06C24C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2b990, parent=0x1b0bdc47630, pos=250,109.5) at 0x000001B0C06C3B80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2bf50, parent=0x1b0bdc47630, pos=250,134.5) at 0x000001B0C06C3F00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2bc90, parent=0x1b0bdc47630, pos=250,159.5) at 0x000001B0C06C9CC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2bcd0, parent=0x1b0bdc47630, pos=250,184.5) at 0x000001B0C06C2780>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2b4d0, parent=0x1b0bdc47630, pos=0,59.5) at 0x000001B0C06CA400>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1b0bde2c050, parent=0x1b0bdc47630, pos=250,59.5) at 0x000001B0C06CA940>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_reroute_undo_redo.py

**Status:** PASSED  
**Duration:** 0.61 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_undo_redo.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2769035879552)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d82140, parent=0x284b2279400, pos=0,84.5) at 0x00000284B7666000>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d804c0, parent=0x284b2279400, pos=0,109.5) at 0x00000284B7680580>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d80b80, parent=0x284b2279400, pos=0,134.5) at 0x00000284B7682E00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d80f40, parent=0x284b2279400, pos=0,159.5) at 0x00000284B7682D00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d80ec0, parent=0x284b2279400, pos=0,184.5) at 0x00000284B7682AC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d803c0, parent=0x284b2279400, pos=250,84.5) at 0x00000284B7682780>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d80540, parent=0x284b2279400, pos=250,109.5) at 0x00000284B7683B80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d80e80, parent=0x284b2279400, pos=250,134.5) at 0x00000284B7683F00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d80c00, parent=0x284b2279400, pos=250,159.5) at 0x00000284B7689F00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d80b40, parent=0x284b2279400, pos=250,184.5) at 0x00000284B7682840>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d806c0, parent=0x284b2279400, pos=0,59.5) at 0x00000284B768A880>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x284b4d80740, parent=0x284b2279400, pos=250,59.5) at 0x00000284B768AA40>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_reroute_with_connections.py

**Status:** PASSED  
**Duration:** 0.60 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_with_connections.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2101485585728)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b6530, parent=0x1e9473fcfb0, pos=0,84.5) at 0x000001E94A4F0200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b7670, parent=0x1e9473fcfb0, pos=0,109.5) at 0x000001E94A4D47C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b73f0, parent=0x1e9473fcfb0, pos=0,134.5) at 0x000001E94A4F2B80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b7a70, parent=0x1e9473fcfb0, pos=0,159.5) at 0x000001E94A4F2980>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b7af0, parent=0x1e9473fcfb0, pos=0,184.5) at 0x000001E94A4F2740>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b7470, parent=0x1e9473fcfb0, pos=250,84.5) at 0x000001E94A4F2300>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b7f30, parent=0x1e9473fcfb0, pos=250,109.5) at 0x000001E94A4F38C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b7070, parent=0x1e9473fcfb0, pos=250,134.5) at 0x000001E94A4F3B00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b7530, parent=0x1e9473fcfb0, pos=250,159.5) at 0x000001E94A4F3D40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b7b70, parent=0x1e9473fcfb0, pos=250,184.5) at 0x000001E94A4F2200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b70b0, parent=0x1e9473fcfb0, pos=0,59.5) at 0x000001E94A4FB780>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1e9477b76f0, parent=0x1e9473fcfb0, pos=250,59.5) at 0x000001E94A4FA180>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_selection_operations.py

**Status:** PASSED  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_selection_operations.py`

**Output:**
```
DEBUG: Node type: <class 'src.core.node.Node'>
DEBUG: Node title: Test Node
DEBUG: Node has title attr: True
DEBUG: Actual description: 'Delete 1 items'

=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 2 commands
DEBUG: Executing command 1/2: <Mock name='mock.get_description()' id='3001768262160'>
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/2: <Mock name='mock.get_description()' id='3001768260816'>
DEBUG: Command 2 returned: True
DEBUG: Command 2 succeeded, added to executed list
DEBUG: All 2 commands succeeded
=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===

DEBUG: CompositeCommand.undo() - undoing 2 commands
DEBUG: Undoing command 1/2: <Mock name='mock.get_description()' id='3001768260816'>
DEBUG: Command 1 undo returned: True
DEBUG: Command 1 undone successfully
DEBUG: Undoing command 2/2: <Mock name='mock.get_description()' id='3001768262160'>
DEBUG: Command 2 undo returned: True
DEBUG: Command 2 undone successfully
DEBUG: All commands undone successfully, composite marked as undone
DEBUG: CompositeCommand.undo() returning: True

```

---

### [PASS] test_undo_history_integration.py

**Status:** PASSED  
**Duration:** 0.42 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_undo_history_integration.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create Node 1
DEBUG: Command type: MockCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create Node 2
DEBUG: Command type: MockCommand
DEBUG: Current history size: 1
DEBUG: Current index: 0
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 1
DEBUG: History size now: 2
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create Node 3
DEBUG: Command type: MockCommand
DEBUG: Current history size: 2
DEBUG: Current index: 1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 2
DEBUG: History size now: 3
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: ERROR - Command execution failed: 'FailingCommand' object has no attribute '_description'

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create Node 1
DEBUG: Command type: MockCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create Node 2
DEBUG: Command type
... (output truncated)
```

---

### [PASS] test_undo_history_workflow.py

**Status:** PASSED  
**Duration:** 0.25 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_undo_history_workflow.py`

---

### [PASS] test_undo_ui_integration.py

**Status:** PASSED  
**Duration:** 0.41 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_undo_ui_integration.py`

**Output:**
```

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 0
DEBUG: Command type: MockCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 1
DEBUG: Command type: MockCommand
DEBUG: Current history size: 1
DEBUG: Current index: 0
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 1
DEBUG: History size now: 2
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 2
DEBUG: Command type: MockCommand
DEBUG: Current history size: 2
DEBUG: Current index: 1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 2
DEBUG: History size now: 3
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 3
DEBUG: Command type: MockCommand
DEBUG: Current history size: 3
DEBUG: Current index: 2
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 3
DEBUG: History size now: 4
DEBUG: Command execution completed successfully in 0.0ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Command 4
DEBUG: Command type: MockCommand
DEBUG: Current history size: 4
DEBUG: Current index: 3
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Comma
... (output truncated)
```

---

### [PASS] test_user_scenario.py

**Status:** PASSED  
**Duration:** 0.60 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_user_scenario.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2548846498176)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2517028fc60, parent=0x2517000e2d0, pos=0,84.5) at 0x000002517317B880>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x251702906e0, parent=0x2517000e2d0, pos=0,109.5) at 0x000002517317BA40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x25170290220, parent=0x2517000e2d0, pos=0,134.5) at 0x000002517318DF00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x25170290be0, parent=0x2517000e2d0, pos=0,159.5) at 0x000002517318DE00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x251702904a0, parent=0x2517000e2d0, pos=0,184.5) at 0x000002517318DBC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x251702908a0, parent=0x2517000e2d0, pos=250,84.5) at 0x000002517318D800>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x25170290ca0, parent=0x2517000e2d0, pos=250,109.5) at 0x000002517318EFC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x25170290760, parent=0x2517000e2d0, pos=250,134.5) at 0x000002517318F000>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x25170290d20, parent=0x2517000e2d0, pos=250,159.5) at 0x000002517318F500>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x25170290820, parent=0x2517000e2d0, pos=250,184.5) at 0x000002517318D6C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x25170290de0, parent=0x2517000e2d0, pos=0,59.5) at 0x0000025173195180>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x25170290ea0, parent=0x2517000e2d0, pos=250,59.5) at 0x0000025173194DC0>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_user_scenario_gui.py

**Status:** PASSED  
**Duration:** 0.59 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_user_scenario_gui.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2764542874688)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab413e10, parent=0x283ab310fd0, pos=0,84.5) at 0x00000283AE380080>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab414b10, parent=0x283ab310fd0, pos=0,109.5) at 0x00000283AE380280>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab414810, parent=0x283ab310fd0, pos=0,134.5) at 0x00000283AE382700>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab415150, parent=0x283ab310fd0, pos=0,159.5) at 0x00000283AE382500>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab415410, parent=0x283ab310fd0, pos=0,184.5) at 0x00000283AE3823C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab414850, parent=0x283ab310fd0, pos=250,84.5) at 0x00000283AE382100>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab415450, parent=0x283ab310fd0, pos=250,109.5) at 0x00000283AE383900>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab414750, parent=0x283ab310fd0, pos=250,134.5) at 0x00000283AE383B40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab414a90, parent=0x283ab310fd0, pos=250,159.5) at 0x00000283AE383C80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab4151d0, parent=0x283ab310fd0, pos=250,184.5) at 0x00000283AE382180>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab415310, parent=0x283ab310fd0, pos=0,59.5) at 0x00000283AE38BC00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x283ab4155d0, parent=0x283ab310fd0, pos=250,59.5) at 0x00000283AE38A240>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_view_state_persistence.py

**Status:** PASSED  
**Duration:** 2.24 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_view_state_persistence.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 1970215497600)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bde160, parent=0x1cab99ff1d0, pos=0,84.5) at 0x000001CABA007200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bddb60, parent=0x1cab99ff1d0, pos=0,109.5) at 0x000001CABA005840>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bddfe0, parent=0x1cab99ff1d0, pos=0,134.5) at 0x000001CABA015880>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bde420, parent=0x1cab99ff1d0, pos=0,159.5) at 0x000001CABA015680>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bde460, parent=0x1cab99ff1d0, pos=0,184.5) at 0x000001CABA015480>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bdd660, parent=0x1cab99ff1d0, pos=296.75,84.5) at 0x000001CABA015140>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bde060, parent=0x1cab99ff1d0, pos=296.75,109.5) at 0x000001CABA014E00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bdd6e0, parent=0x1cab99ff1d0, pos=296.75,134.5) at 0x000001CABA016080>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bdec20, parent=0x1cab99ff1d0, pos=296.75,159.5) at 0x000001CABA016300>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bdede0, parent=0x1cab99ff1d0, pos=296.75,184.5) at 0x000001CABA015200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bdeee0, parent=0x1cab99ff1d0, pos=0,59.5) at 0x000001CABA016900>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1cab9bdea60, parent=0x1cab99ff1d0, pos=296.75,59.5) at 0x000001CABA016CC0>
DEBUG: Pin cleaned up
DEBUG: Cleared pins 
... (output truncated)
```

---

## Test Environment

- **Python Version:** 3.11.0
- **Test Runner:** PyFlowGraph Professional GUI Test Tool
- **Test Directory:** `tests/`
- **Generated By:** Badge Updater v1.0

---

*This report is automatically generated when tests are executed through the PyFlowGraph test tool.*
*Last updated: 2025-08-20 01:33:09*

# PyFlowGraph Test Results

**Generated:** 2025-08-20 01:23:01  
**Test Runner:** Professional PySide6 GUI Test Tool

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 48 |
| **Passed** | 39 |
| **Failed** | 9 |
| **Success Rate** | 81.2% |
| **Total Duration** | 52.34 seconds |
| **Average Duration** | 1.09 seconds per test |

---

## Test Results Details

### [FAIL] test_actual_execution_after_undo.py

**Status:** FAILED  
**Duration:** 0.62 seconds  
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
EXEC_LOG: Generated password: ROteRefhUumc
EXEC_LOG: --- Executing Node: Password Strength Analyzer ---
EXEC_LOG: Password strength: Strong (Score: 65/100)
Feedback: Add numbers; Add symbols for extra security
EXEC_LOG: --- Executing Node: Password Output & Copy ---
EXEC_LOG: === PASSWORD GENERATION COMPLETE ===
Generated Password: ROteRefhUumc
Strength: Strong (65/100)
Feedback: Add numbers; Add symbols for extra security
Execution completed. Logs count: 8
  LOG: Generated password: ROteRefhUumc
  LOG: --- Executing Node: Password Strength Analyzer ---
  LOG: Password strength: Strong (Score: 65/100)
Feedback: Add numbers; Add symbols for extra security
  LOG: --- Executing Node: Password Output & Copy ---
  LOG: === PASSWORD GENERATION COMPLETE ===
Generated Password: ROteRefhUumc
Strength: Strong (65/100)
Feedback: Add numbers; Add symbols for extra security
Baseline - Password: 'ROteRefhUumc'
Baseline - Strength: 'Generated Password: ROteRefhUumc
Strength: Strong ...'
Baseline execution successful: password=True, result=True

--- Deleting Middle Nodes ---
Deleting: Password Generator Engine and Password Strength Analyzer
After deletion: 2 nodes, 0 connections

--- Undoing Deletions ---
After undo: 4 nodes, 13 connections
... (output truncated)
```

---

### [FAIL] test_code_editor_dialog_integration.py

**Status:** FAILED  
**Duration:** 0.13 seconds  
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
AttributeError: <Mock spec='str' id='2634681931024'> does not have the attribute '_handle_accept'

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

---

### [FAIL] test_execute_graph_modes.py

**Status:** FAILED  
**Duration:** 10.03 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_execute_graph_modes.py`

**Output:**
```
Test timed out after 10 seconds
```

---

### [FAIL] test_group_data_flow.py

**Status:** FAILED  
**Duration:** 0.57 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_data_flow.py`

**Output:**
```

QFontDatabase: Must construct a QGuiApplication before accessing QFontDatabase

```

---

### [FAIL] test_group_interface_pins.py

**Status:** FAILED  
**Duration:** 0.18 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_interface_pins.py`

**Output:**
```

........E...EEE.EF..........
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

---

### [FAIL] test_group_ui_integration.py

**Status:** FAILED  
**Duration:** 10.01 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_ui_integration.py`

**Output:**
```
Test timed out after 10 seconds
```

---

### [FAIL] test_performance_fix_demonstration.py

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
Undo operation took: 2.03 ms
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
Ran 2 tests in 0.081s

FAILED (failures=1)

```

---

### [FAIL] test_performance_regression_validation.py

**Status:** FAILED  
**Duration:** 0.26 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_performance_regression_validation.py`

**Output:**
```

=== Testing Duplicate Connection Prevention ===
Initial state: 2 graph connections, 4 pin connections
Undo operation took: 2.28 ms
After undo: 2 graph connections, 6 pin connections

=== Testing Execution Performance Stability ===
Baseline execution time: 0.001 ms
Post-undo execution time: 0.001 ms
Performance ratio (post-undo / baseline): 0.697

=== Testing Multiple Delete-Undo Cycles ===
Cycle 1/3
Cycle 1 performance change: 30.4%
Cycle 2/3
Cycle 2 performance change: 23.9%
Cycle 3/3
Cycle 3 performance change: 10.9%
Maximum performance degradation: 30.4%

=== Testing Performance Regression Thresholds ===
Performance thresholds: Delete=0.01ms, Undo=1.98ms

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
Ran 4 tests in 0.097s

FAILED (failures=1)

```

---

### [FAIL] test_real_workflow_integration.py

**Status:** FAILED  
**Duration:** 0.28 seconds  
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
Ran 12 tests in 0.105s

FAILED (failures=1)

```

---

### [PASS] test_basic_commands.py

**Status:** PASSED  
**Duration:** 0.10 seconds  
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
**Duration:** 0.12 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_code_change_command.py`

**Output:**
```
Failed to change code: Set code failed
Failed to undo code change: Undo failed

```

---

### [PASS] test_code_editor_undo_workflow.py

**Status:** PASSED  
**Duration:** 0.19 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_code_editor_undo_workflow.py`

---

### [PASS] test_command_system.py

**Status:** PASSED  
**Duration:** 0.46 seconds  
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
**Duration:** 0.16 seconds  
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
**Duration:** 0.27 seconds  
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
**Duration:** 0.27 seconds  
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
DEBUG: Executing command 1/2: <Mock name='mock.get_description()' id='1896250580880'>
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/2: <Mock name='mock.get_description()' id='1896250482768'>
DEBUG: Command 2 returned: False
DEBUG: Command 2 FAILED - rolling back 1 executed commands
DEBUG: Rolling back command 1/1: <Mock name='mock.get_description()' id='1896250580880'>
DEBUG: Rollback 1 returned: True
DEBUG: Rollback complete, composite command failed
=== COMPOSITE COMMAND EXECUTE END (FAILED) ===


=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 2 commands
DEBUG: Executing command 1/2: <Mock name='mock.get_description()' id='1896250608080'>
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/2: <Mock name='mock.get_description()' id='1896250609872'>
DEBUG: Command 2 returned: True
DEBUG: Command 2 succeeded, added to executed list
DEBUG: All 2 commands succeeded
=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===

DEBUG: CompositeCommand.undo() - undoing 2 commands
DEBUG: Undoing command 1/2: <Mock name='mock.get_description()' id='1896250609872'>
DEBUG: Command 1 undo returned: True
DEBUG: Command 1 undone successfully
DEBUG: Undoing command 2/2: <Mock name='mock.get_description()' id='1896250608080'>
DEBUG: Command 2 undo returned: True
DEBUG: Command 2 undone successfully
DEBUG: All commands undone successfully, composite marked as undone
DEBUG: CompositeCommand.undo() returning: True

```

---

### [PASS] test_debug_flags.py

**Status:** PASSED  
**Duration:** 0.22 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_debug_flags.py`

---

### [PASS] test_delete_undo_performance_regression.py

**Status:** PASSED  
**Duration:** 1.21 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_delete_undo_performance_regression.py`

---

### [PASS] test_end_to_end_workflows.py

**Status:** PASSED  
**Duration:** 3.29 seconds  
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
DEBUG: Node to remove: 'Password Configuration' (ID: 2991312669696)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2b877cd1900, parent=0x2b877b729b0, pos=0,84.5) at 0x000002B87823BB00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2b877cd1440, parent=0x2b877b729b0, pos=0,109.5) at 0x000002B87823BCC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2b877cd0e00, parent=0x2b877b729b0, pos=0,134.5) at 0x000002B878246340>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2b877cd14c0, parent=0x2b877b729b0, pos=0,159.5) at 0x000002B878246140>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2b877cd1880, parent=0x2b877b729b0, pos=0,184.5) at 0x000002B878245F00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2b877cd0980, parent=0x2b877b729b0, pos=250,84.5) at 0x000002B878245940>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2b877cd0fc0, parent=0x2b877b729b0, pos=250,109.5) at 0x000002B878247380>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2b877cd2500, parent=0x2b877b729b0, pos=250,134.5) at 0x000002B8782
... (output truncated)
```

---

### [PASS] test_execution_engine.py

**Status:** PASSED  
**Duration:** 0.30 seconds  
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
DEBUG: Command execution completed successfully in 44.1ms
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
DEBUG: Command execution completed successfully in 1.8ms
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
DEBUG: Command execution completed successfully in 1.9ms
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
**Duration:** 0.08 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_file_formats.py`

---

### [PASS] test_full_gui_integration.py

**Status:** PASSED  
**Duration:** 6.93 seconds  
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
DEBUG: Node to remove: 'Password Configuration' (ID: 1650599539008)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1807657d3a0, parent=0x1804d08a790, pos=0,84.5) at 0x000001804F667AC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1807657d620, parent=0x1804d08a790, pos=0,109.5) at 0x000001804F667C40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1807657d320, parent=0x1804d08a790, pos=0,134.5) at 0x000001804F676180>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1807657d660, parent=0x1804d08a790, pos=0,159.5) at 0x000001804F675F80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1807657d860, parent=0x1804d08a790, pos=0,184.5) at 0x000001804F675D40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1807657d360, parent=0x1804d08a790, pos=250,84.5) at 0x000001804F675900>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1807657d760, parent=0x1804d08a790, pos=250,109.5) at 0x000001804F677100>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1807657e220, parent=0x1804d08a790, pos=250,134.5) at 0x000001804F6773C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin
... (output truncated)
```

---

### [PASS] test_graph_management.py

**Status:** PASSED  
**Duration:** 0.32 seconds  
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
DEBUG: Command execution completed successfully in 50.3ms
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
DEBUG: Command execution completed successfully in 0.2ms
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
DEBUG: Command execution completed successfully in 2.4ms
=== COMMAND HISTORY EXECUTE END ===


=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Create 'Input Node' node
D
... (output truncated)
```

---

### [PASS] test_group_resize.py

**Status:** PASSED  
**Duration:** 0.17 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_resize.py`

---

### [PASS] test_group_system.py

**Status:** PASSED  
**Duration:** 0.23 seconds  
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
**Duration:** 0.74 seconds  
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
  Connection: <core.connection.Connection(0x176b74c5360, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E15B1C00> - Scene: True
  Connection: <core.connection.Connection(0x176b74c5ba0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E15B1D80> - Scene: True
  Connection: <core.connection.Connection(0x176b74c5720, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E1587580> - Scene: True
  Connection: <core.connection.Connection(0x176b74c53e0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E1587B40> - Scene: True
  Connection: <core.connection.Connection(0x176b74c4e20, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E15877C0> - Scene: True
  Connection: <core.connection.Connection(0x176b74c4f20, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E1587700> - Scene: True
  Connection: <core.connection.Connection(0x176b74c4ee0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E1587780> - Scene: True
  Connection: <core.connection.Connection(0x176b74c5b60, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E1587AC0> - Scene: True
  Connection: <core.connection.Connection(0x176b74c55a0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176B92835C0> - Scene: True
  Connection: <core.connection.Connection(0x176b74c58e0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x00000176E1587C00> - Scene: T
... (output truncated)
```

---

### [PASS] test_gui_node_deletion_workflow.py

**Status:** PASSED  
**Duration:** 0.71 seconds  
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
  Connection: <core.connection.Connection(0x20d12636480, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CC800> - Scene: True
  Connection: <core.connection.Connection(0x20d12636d80, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CC700> - Scene: True
  Connection: <core.connection.Connection(0x20d12636c00, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CC600> - Scene: True
  Connection: <core.connection.Connection(0x20d126369c0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CBF80> - Scene: True
  Connection: <core.connection.Connection(0x20d126363c0, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CC440> - Scene: True
  Connection: <core.connection.Connection(0x20d12636440, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CC340> - Scene: True
  Connection: <core.connection.Connection(0x20d12636980, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CC240> - Scene: True
  Connection: <core.connection.Connection(0x20d12636680, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CBFC0> - Scene: True
  Connection: <core.connection.Connection(0x20d12636940, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7A4F40> - Scene: True
  Connection: <core.connection.Connection(0x20d12636900, pos=0,0, z=-1, flags=(ItemIsSelectable)) at 0x0000020D3A7CBA80> - Scene: T
... (output truncated)
```

---

### [PASS] test_gui_value_update_regression.py

**Status:** PASSED  
**Duration:** 0.29 seconds  
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
**Duration:** 0.27 seconds  
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
DEBUG: Command execution completed successfully in 44.2ms
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
DEBUG: Command execution completed successfully in 1.9ms
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
DEBUG: Command execution completed successfully in 1.8ms
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
**Duration:** 0.58 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_markdown_loaded_deletion.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2737928298432)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f40470, parent=0x27d78d7c260, pos=0,84.5) at 0x0000027D794044C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f42170, parent=0x27d78d7c260, pos=0,109.5) at 0x0000027D79404480>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f418f0, parent=0x27d78d7c260, pos=0,134.5) at 0x0000027D79406B40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f3f670, parent=0x27d78d7c260, pos=0,159.5) at 0x0000027D794069C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f3fd30, parent=0x27d78d7c260, pos=0,184.5) at 0x0000027D79406700>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f401f0, parent=0x27d78d7c260, pos=250,84.5) at 0x0000027D794063C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f3fef0, parent=0x27d78d7c260, pos=250,109.5) at 0x0000027D79407800>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f3f3b0, parent=0x27d78d7c260, pos=250,134.5) at 0x0000027D79407B00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f3f730, parent=0x27d78d7c260, pos=250,159.5) at 0x0000027D79407C80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f3f8f0, parent=0x27d78d7c260, pos=250,184.5) at 0x0000027D79406200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f3fbb0, parent=0x27d78d7c260, pos=0,59.5) at 0x0000027D7940A080>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x27d78f3feb0, parent=0x27d78d7c260, pos=250,59.5) at 0x0000027D7940A180>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_node_deletion_connection_bug.py

**Status:** PASSED  
**Duration:** 0.20 seconds  
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
**Duration:** 0.27 seconds  
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
DEBUG: Command execution completed successfully in 1.6ms
=== COMMAND HISTORY EXECUTE END ===


```

---

### [PASS] test_node_system_headless.py

**Status:** PASSED  
**Duration:** 0.27 seconds  
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
DEBUG: Command execution completed successfully in 1.7ms
=== COMMAND HISTORY EXECUTE END ===


```

---

### [PASS] test_password_generator_chaos.py

**Status:** PASSED  
**Duration:** 4.66 seconds  
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

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=True
DEBUG: Node to remove: 'Password Strength Analyzer' (ID: 1623875971712)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 95 items before removal
DEBUG: Using command pattern for removal

=== COMMAND HISTORY EXECUTE START ===
DEBUG: Executing command: Delete 'Password Strength Analyzer' node
DEBUG: Command type: DeleteNodeCommand
DEBUG: Current history size: 0
DEBUG: Current index: -1
DEBUG: Calling command.execute()...
DEBUG: Command.execute() returned: True
DEBUG: Command marked as executed
DEBUG: Added command to history at index 0
DEBUG: History size now: 1
DEBUG: Command execution completed successfully in 0.7ms
=== COMMAND HISTORY EXECUTE END ===

DEBUG: Command execution returned: True
=== NODE GRAPH REMOVE_NODE END (COMMAND) ===

Performed operations: ['Deleted node: Password Strength Analyzer']

=== COMMAND HISTORY UNDO START ===
DEBUG: Attempting to undo command
DEBUG: Current index: 0
DEBUG: History size: 1
DEBUG: Can undo: True
DEBUG: Undoing command: Delete 'Password Strength Analyzer' node
DEBUG: Command type: DeleteNodeCommand
DEBUG: Calling command.undo()...
DEBUG: Command.undo() returned: True
DEBUG: Command undone successfully, index now: -1
=== 
... (output truncated)
```

---

### [PASS] test_pin_system.py

**Status:** PASSED  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_pin_system.py`

---

### [PASS] test_pin_system_headless.py

**Status:** PASSED  
**Duration:** 0.24 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_pin_system_headless.py`

---

### [PASS] test_reroute_creation_undo.py

**Status:** PASSED  
**Duration:** 0.73 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_creation_undo.py`

**Output:**
```
Testing RerouteNode creation/deletion/undo sequence...


=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2499720782080)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b015d0, parent=0x24602862a90, pos=0,84.5) at 0x0000024605610900>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b02590, parent=0x24602862a90, pos=0,109.5) at 0x00000246056100C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b02390, parent=0x24602862a90, pos=0,134.5) at 0x00000246056131C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b01a10, parent=0x24602862a90, pos=0,159.5) at 0x0000024605612D80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b01c50, parent=0x24602862a90, pos=0,184.5) at 0x0000024605612B80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b01d50, parent=0x24602862a90, pos=250,84.5) at 0x0000024605612A40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b01a50, parent=0x24602862a90, pos=250,109.5) at 0x0000024605612840>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b02750, parent=0x24602862a90, pos=250,134.5) at 0x000002460561A780>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b01f10, parent=0x24602862a90, pos=250,159.5) at 0x000002460561A500>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b02090, parent=0x24602862a90, pos=250,184.5) at 0x0000024605612AC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b024d0, parent=0x24602862a90, pos=0,59.5) at 0x000002460561AEC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24602b02810, parent=0x24602862a90, pos=250,59.5) at 0x000002460561B140>
DEBU
... (output truncated)
```

---

### [PASS] test_reroute_node_deletion.py

**Status:** PASSED  
**Duration:** 0.56 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_node_deletion.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2113304082624)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbdd20, parent=0x1ec07beb040, pos=0,84.5) at 0x000001EC0ABF0700>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbe620, parent=0x1ec07beb040, pos=0,109.5) at 0x000001EC0ABF0040>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbf260, parent=0x1ec07beb040, pos=0,134.5) at 0x000001EC0ABF2EC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbe860, parent=0x1ec07beb040, pos=0,159.5) at 0x000001EC0ABF2CC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbf420, parent=0x1ec07beb040, pos=0,184.5) at 0x000001EC0ABF2800>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbf1a0, parent=0x1ec07beb040, pos=250,84.5) at 0x000001EC0ABF24C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbea60, parent=0x1ec07beb040, pos=250,109.5) at 0x000001EC0ABF3B80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbe8e0, parent=0x1ec07beb040, pos=250,134.5) at 0x000001EC0ABF3F00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbf1e0, parent=0x1ec07beb040, pos=250,159.5) at 0x000001EC0ABF9CC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbf160, parent=0x1ec07beb040, pos=250,184.5) at 0x000001EC0ABF2780>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbed20, parent=0x1ec07beb040, pos=0,59.5) at 0x000001EC0ABFA400>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1ec07dbf4e0, parent=0x1ec07beb040, pos=250,59.5) at 0x000001EC0ABFA940>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_reroute_undo_redo.py

**Status:** PASSED  
**Duration:** 0.56 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_undo_redo.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2193920976000)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac82ad0, parent=0x1feccd55b40, pos=0,84.5) at 0x000001FECFE16000>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac82d90, parent=0x1feccd55b40, pos=0,109.5) at 0x000001FECFE30580>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac81b10, parent=0x1feccd55b40, pos=0,134.5) at 0x000001FECFE32E00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac83550, parent=0x1feccd55b40, pos=0,159.5) at 0x000001FECFE32D00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac83090, parent=0x1feccd55b40, pos=0,184.5) at 0x000001FECFE32AC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac83790, parent=0x1feccd55b40, pos=250,84.5) at 0x000001FECFE32780>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac835d0, parent=0x1feccd55b40, pos=250,109.5) at 0x000001FECFE33B80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac83910, parent=0x1feccd55b40, pos=250,134.5) at 0x000001FECFE33F00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac836d0, parent=0x1feccd55b40, pos=250,159.5) at 0x000001FECFE39F00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac83250, parent=0x1feccd55b40, pos=250,184.5) at 0x000001FECFE32840>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac83310, parent=0x1feccd55b40, pos=0,59.5) at 0x000001FECFE3A880>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1fecac839d0, parent=0x1feccd55b40, pos=250,59.5) at 0x000001FECFE3AA40>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_reroute_with_connections.py

**Status:** PASSED  
**Duration:** 0.56 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_with_connections.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2003651937600)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d2804625d0, parent=0x1d28028ac50, pos=0,84.5) at 0x000001D282F80200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463210, parent=0x1d28028ac50, pos=0,109.5) at 0x000001D282F647C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463690, parent=0x1d28028ac50, pos=0,134.5) at 0x000001D282F82B80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463310, parent=0x1d28028ac50, pos=0,159.5) at 0x000001D282F82980>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463550, parent=0x1d28028ac50, pos=0,184.5) at 0x000001D282F82740>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463610, parent=0x1d28028ac50, pos=250,84.5) at 0x000001D282F82300>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463c10, parent=0x1d28028ac50, pos=250,109.5) at 0x000001D282F838C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463750, parent=0x1d28028ac50, pos=250,134.5) at 0x000001D282F83B00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463790, parent=0x1d28028ac50, pos=250,159.5) at 0x000001D282F83D40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280462f50, parent=0x1d28028ac50, pos=250,184.5) at 0x000001D282F82200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280462cd0, parent=0x1d28028ac50, pos=0,59.5) at 0x000001D282F8B780>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x1d280463410, parent=0x1d28028ac50, pos=250,59.5) at 0x000001D282F8A180>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_selection_operations.py

**Status:** PASSED  
**Duration:** 0.26 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_selection_operations.py`

**Output:**
```
DEBUG: Node type: <class 'src.core.node.Node'>
DEBUG: Node title: Test Node
DEBUG: Node has title attr: True
DEBUG: Actual description: 'Delete 1 items'

=== COMPOSITE COMMAND EXECUTE START ===
DEBUG: Executing composite command with 2 commands
DEBUG: Executing command 1/2: <Mock name='mock.get_description()' id='2148547672528'>
DEBUG: Command 1 returned: True
DEBUG: Command 1 succeeded, added to executed list
DEBUG: Executing command 2/2: <Mock name='mock.get_description()' id='2148547671184'>
DEBUG: Command 2 returned: True
DEBUG: Command 2 succeeded, added to executed list
DEBUG: All 2 commands succeeded
=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===

DEBUG: CompositeCommand.undo() - undoing 2 commands
DEBUG: Undoing command 1/2: <Mock name='mock.get_description()' id='2148547671184'>
DEBUG: Command 1 undo returned: True
DEBUG: Command 1 undone successfully
DEBUG: Undoing command 2/2: <Mock name='mock.get_description()' id='2148547672528'>
DEBUG: Command 2 undo returned: True
DEBUG: Command 2 undone successfully
DEBUG: All commands undone successfully, composite marked as undone
DEBUG: CompositeCommand.undo() returning: True

```

---

### [PASS] test_undo_history_integration.py

**Status:** PASSED  
**Duration:** 0.39 seconds  
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
**Duration:** 0.21 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_undo_history_workflow.py`

---

### [PASS] test_undo_ui_integration.py

**Status:** PASSED  
**Duration:** 0.39 seconds  
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
**Duration:** 0.56 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_user_scenario.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2500848324992)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2ac40, parent=0x24643ad2c70, pos=0,84.5) at 0x00000246462DB880>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2b980, parent=0x24643ad2c70, pos=0,109.5) at 0x00000246462DBA40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2b8c0, parent=0x24643ad2c70, pos=0,134.5) at 0x00000246462EDF00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2c240, parent=0x24643ad2c70, pos=0,159.5) at 0x00000246462EDE00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2c300, parent=0x24643ad2c70, pos=0,184.5) at 0x00000246462EDBC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2c3c0, parent=0x24643ad2c70, pos=250,84.5) at 0x00000246462ED800>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2c4c0, parent=0x24643ad2c70, pos=250,109.5) at 0x00000246462EEFC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2ba00, parent=0x24643ad2c70, pos=250,134.5) at 0x00000246462EF000>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2b6c0, parent=0x24643ad2c70, pos=250,159.5) at 0x00000246462EF500>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2be80, parent=0x24643ad2c70, pos=250,184.5) at 0x00000246462ED6C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2bec0, parent=0x24643ad2c70, pos=0,59.5) at 0x00000246462F5180>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x24643d2ca80, parent=0x24643ad2c70, pos=250,59.5) at 0x00000246462F4DC0>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_user_scenario_gui.py

**Status:** PASSED  
**Duration:** 0.57 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_user_scenario_gui.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 1477319889984)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7754050, parent=0x157f50b80f0, pos=0,84.5) at 0x00000157FA460080>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7744b90, parent=0x157f50b80f0, pos=0,109.5) at 0x00000157FA460280>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f77446d0, parent=0x157f50b80f0, pos=0,134.5) at 0x00000157FA462700>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7745450, parent=0x157f50b80f0, pos=0,159.5) at 0x00000157FA462500>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7744d50, parent=0x157f50b80f0, pos=0,184.5) at 0x00000157FA4623C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7744e50, parent=0x157f50b80f0, pos=250,84.5) at 0x00000157FA462100>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7744a90, parent=0x157f50b80f0, pos=250,109.5) at 0x00000157FA463900>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7744a10, parent=0x157f50b80f0, pos=250,134.5) at 0x00000157FA463B40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7744cd0, parent=0x157f50b80f0, pos=250,159.5) at 0x00000157FA463C80>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7744c50, parent=0x157f50b80f0, pos=250,184.5) at 0x00000157FA462180>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7744dd0, parent=0x157f50b80f0, pos=0,59.5) at 0x00000157FA46BC00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x157f7745010, parent=0x157f50b80f0, pos=250,59.5) at 0x00000157FA46A240>
DEBUG: Pin cleaned up
DEBUG: Cleared pins list
DEBUG: Cleare
... (output truncated)
```

---

### [PASS] test_view_state_persistence.py

**Status:** PASSED  
**Duration:** 2.22 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_view_state_persistence.py`

**Output:**
```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2349940387712)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x223230667a0, parent=0x22322e57ee0, pos=0,84.5) at 0x00000223235E7200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x223230668a0, parent=0x22322e57ee0, pos=0,109.5) at 0x00000223235E5840>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22323067520, parent=0x22322e57ee0, pos=0,134.5) at 0x00000223235F5880>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22323067620, parent=0x22322e57ee0, pos=0,159.5) at 0x00000223235F5680>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x223230673a0, parent=0x22322e57ee0, pos=0,184.5) at 0x00000223235F5480>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22323066da0, parent=0x22322e57ee0, pos=296.75,84.5) at 0x00000223235F5140>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x223230674a0, parent=0x22322e57ee0, pos=296.75,109.5) at 0x00000223235F4E00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22323068720, parent=0x22322e57ee0, pos=296.75,134.5) at 0x00000223235F6080>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22323067e60, parent=0x22322e57ee0, pos=296.75,159.5) at 0x00000223235F6300>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22323067c20, parent=0x22322e57ee0, pos=296.75,184.5) at 0x00000223235F5200>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x223230679a0, parent=0x22322e57ee0, pos=0,59.5) at 0x00000223235F6900>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x22323067ba0, parent=0x22322e57ee0, pos=296.75,59.5) at 0x00000223235F6CC0>
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
*Last updated: 2025-08-20 01:23:01*

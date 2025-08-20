# PyFlowGraph Test Results

**Generated:** 2025-08-20 01:49:54  
**Test Runner:** Professional PySide6 GUI Test Tool

---

## Summary

| Metric | Value |
|--------|-------|
| **Test Files** | 48 |
| **Total Test Cases** | 340 |
| **Passed** | 319 |
| **Failed** | 6 |
| **Errors** | 9 |
| **Skipped** | 8 |
| **Success Rate** | 93.8% |
| **Total Duration** | 44.08 seconds |
| **Average Duration** | 0.92 seconds per file |

---

## Test Results by File

| Status | Test File | Cases | Passed | Failed | Duration | Details |
|--------|-----------|-------|--------|--------|----------|---------|
| ❌ | [test_actual_execution_after_undo.py](#test-actual-execution-after-undo) | 1 | 0 | 1 | 0.64s | FAILED |
| ❌ | [test_code_editor_dialog_integration.py](#test-code-editor-dialog-integration) | 7 | 3 | 0 | 0.14s | FAILED |
| ❌ | [test_execute_graph_modes.py](#test-execute-graph-modes) | 0 | 0 | 1 | 10.03s | FAILED |
| ❌ | [test_group_interface_pins.py](#test-group-interface-pins) | 28 | 23 | 0 | 0.18s | FAILED |
| ❌ | [test_group_ui_integration.py](#test-group-ui-integration) | 0 | 0 | 1 | 10.01s | FAILED |
| ❌ | [test_performance_fix_demonstration.py](#test-performance-fix-demonstration) | 2 | 1 | 1 | 0.23s | FAILED |
| ❌ | [test_performance_regression_validation.py](#test-performance-regression-validation) | 4 | 3 | 1 | 0.26s | FAILED |
| ❌ | [test_real_workflow_integration.py](#test-real-workflow-integration) | 12 | 11 | 1 | 0.29s | FAILED |
| ✅ | test_basic_commands.py | 8 | 8 | 0 | 0.10s | PASSED |
| ✅ | test_code_change_command.py | 10 | 10 | 0 | 0.12s | PASSED |
| ✅ | test_code_editor_undo_workflow.py | 9 | 9 | 0 | 0.21s | PASSED |
| ✅ | test_command_system.py | 24 | 24 | 0 | 0.47s | PASSED |
| ✅ | test_composite_commands.py | 13 | 13 | 0 | 0.17s | PASSED |
| ✅ | test_connection_system.py | 14 | 14 | 0 | 0.28s | PASSED |
| ✅ | test_connection_system_headless.py | 14 | 14 | 0 | 0.28s | PASSED |
| ✅ | test_copy_paste_integration.py | 7 | 7 | 0 | 0.16s | PASSED |
| ✅ | test_debug_flags.py | 3 | 3 | 0 | 0.22s | PASSED |
| ✅ | test_delete_undo_performance_regression.py | 4 | 0 | 0 | 1.22s | PASSED |
| ✅ | test_end_to_end_workflows.py | 4 | 4 | 0 | 3.26s | PASSED |
| ✅ | test_execution_engine.py | 12 | 12 | 0 | 0.30s | PASSED |
| ✅ | test_file_formats.py | 2 | 2 | 0 | 0.08s | PASSED |
| ✅ | test_full_gui_integration.py | 14 | 13 | 0 | 6.96s | PASSED |
| ✅ | test_graph_management.py | 12 | 12 | 0 | 0.31s | PASSED |
| ⚠️ | [test_group_data_flow.py](#test-group-data-flow) | 0 | 0 | 0 | 0.52s | ERROR |
| ✅ | test_group_resize.py | 14 | 14 | 0 | 0.17s | PASSED |
| ✅ | test_group_system.py | 20 | 20 | 0 | 0.23s | PASSED |
| ⚠️ | [test_gui_node_deletion.py](#test-gui-node-deletion) | 0 | 0 | 0 | 0.24s | ERROR |
| ⚠️ | [test_gui_node_deletion_workflow.py](#test-gui-node-deletion-workflow) | 0 | 0 | 0 | 0.24s | ERROR |
| ✅ | test_gui_value_update_regression.py | 2 | 2 | 0 | 0.27s | PASSED |
| ✅ | test_integration.py | 3 | 3 | 0 | 0.29s | PASSED |
| ⚠️ | [test_markdown_loaded_deletion.py](#test-markdown-loaded-deletion) | 0 | 0 | 0 | 0.19s | ERROR |
| ⚠️ | [test_node_deletion_connection_bug.py](#test-node-deletion-connection-bug) | 0 | 0 | 0 | 0.14s | ERROR |
| ✅ | test_node_system.py | 12 | 12 | 0 | 0.27s | PASSED |
| ✅ | test_node_system_headless.py | 12 | 12 | 0 | 0.26s | PASSED |
| ⚠️ | [test_password_generator_chaos.py](#test-password-generator-chaos) | 0 | 0 | 0 | 0.27s | ERROR |
| ✅ | test_pin_system.py | 12 | 12 | 0 | 0.28s | PASSED |
| ✅ | test_pin_system_headless.py | 12 | 12 | 0 | 0.25s | PASSED |
| ⚠️ | [test_reroute_creation_undo.py](#test-reroute-creation-undo) | 0 | 0 | 0 | 0.18s | ERROR |
| ⚠️ | [test_reroute_node_deletion.py](#test-reroute-node-deletion) | 0 | 0 | 0 | 0.17s | ERROR |
| ⚠️ | [test_reroute_undo_redo.py](#test-reroute-undo-redo) | 0 | 0 | 0 | 0.17s | ERROR |
| ⚠️ | [test_reroute_with_connections.py](#test-reroute-with-connections) | 0 | 0 | 0 | 0.17s | ERROR |
| ✅ | test_selection_operations.py | 15 | 12 | 0 | 0.25s | PASSED |
| ✅ | test_undo_history_integration.py | 10 | 10 | 0 | 0.41s | PASSED |
| ✅ | test_undo_history_workflow.py | 11 | 11 | 0 | 0.21s | PASSED |
| ✅ | test_undo_ui_integration.py | 13 | 13 | 0 | 0.39s | PASSED |
| ⚠️ | [test_user_scenario.py](#test-user-scenario) | 0 | 0 | 0 | 0.17s | ERROR |
| ⚠️ | [test_user_scenario_gui.py](#test-user-scenario-gui) | 0 | 0 | 0 | 0.20s | ERROR |
| ⚠️ | [test_view_state_persistence.py](#test-view-state-persistence) | 0 | 0 | 0 | 2.22s | ERROR |

---

## Individual Test Cases

### <a id="test-actual-execution-after-undo"></a>[FAIL] test_actual_execution_after_undo.py

**File Status:** FAILED  
**Total Cases:** 1  
**Passed:** 0  
**Failed:** 1  
**Errors:** 0  
**Duration:** 0.64 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_actual_execution_after_undo.py`

#### Individual Test Cases:

- ❌ **test_actual_execution_after_delete_undo** (test_actual_execution_after_undo) - FAILED

#### Raw Test Output:

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
EXEC_LOG: Generated password: 3pRnpSOWSvuD
EXEC_LOG: --- Executing Node: Password Strength Analyzer ---
EXEC_LOG: Password strength: Very Strong (Score: 85/100)
Feedback: Add symbols for extra security
EXEC_LOG: --- Executing Node: Password Output & Copy ---
EXEC_LOG: === PASSWORD GENERATION COMPLETE ===
Generated Password: 3pRnpSOWSvuD
Strength: Very Strong (85/100)
Feedback: Add symbols for extra security
Execution completed. Logs count: 8
  LOG: Generated password: 3pRnpSOWSvuD
  LOG: --- Executing Node: Password Strength Analyzer ---
  LOG: Password strength: Very Strong (Score: 85/100)
Feedback: Add symbols for extra security
  LOG: --- Executing Node: Password Output & Copy ---
  LOG: === PASSWORD GENERATION COMPLETE ===
Generat
... (output truncated)
```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-code-editor-dialog-integration"></a>[FAIL] test_code_editor_dialog_integration.py

**File Status:** FAILED  
**Total Cases:** 7  
**Passed:** 3  
**Failed:** 0  
**Errors:** 4  
**Duration:** 0.14 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_code_editor_dialog_integration.py`

#### Individual Test Cases:

- ⚠️ **test_accept_creates_command_for_code_changes** (test_code_editor_dialog_integration) - ERROR
- ✅ **test_cancel_does_not_affect_command_history** (test_code_editor_dialog_integration) - PASSED
- ⚠️ **test_dialog_initialization_with_graph_reference** (test_code_editor_dialog_integration) - ERROR
- ⚠️ **test_fallback_when_no_command_history** (test_code_editor_dialog_integration) - ERROR
- ✅ **test_gui_code_changes_not_in_command_system** (test_code_editor_dialog_integration) - PASSED
- ⚠️ **test_no_changes_does_not_create_command** (test_code_editor_dialog_integration) - ERROR
- ✅ **test_sequential_code_changes** (test_code_editor_dialog_integration) - PASSED

#### Raw Test Output:

```

test_accept_creates_command_for_code_changes (tests.test_code_editor_dialog_integration.TestCodeEditorDialogIntegration.test_accept_creates_command_for_code_changes)
Test accept button creates CodeChangeCommand for execution code changes. ... ERROR
test_cancel_does_not_affect_command_history (tests.test_code_editor_dialog_integration.TestCodeEditorDialogIntegration.test_cancel_does_not_affect_command_history)
Test cancel button does not create commands or affect history. ... ok
test_dialog_initialization_with_graph_reference (tests.test_code_editor_dialog_integration.TestCodeEditorDialogIntegration.test_dialog_initialization_with_graph_reference)
Test dialog initializes with proper node and graph references. ... ERROR
test_fallback_when_no_command_history (tests.test_code_editor_dialog_integration.TestCodeEditorDialogIntegration.test_fallback_when_no_command_history)
Test fallback behavior when node_graph has no command_history. ... ERROR
test_gui_code_changes_not_in_command_system (tests.test_code_editor_dialog_integration.TestCodeEditorDialogIntegration.test_gui_code_changes_not_in_command_system)
Test that GUI code changes use direct method calls, not commands. ... ok
test_no_changes_does_not_create_command (tests.test_code_editor_dialog_integration.TestCodeEditorDialogIntegration.test_no_changes_does_not_create_command)
Test that no command is created when code is unchanged. ... ERROR
test_sequential_code_changes (tests.test_code_editor_dialog_integration.TestCodeEditorD
... (output truncated)
```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-execute-graph-modes"></a>[FAIL] test_execute_graph_modes.py

**File Status:** FAILED  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 1  
**Errors:** 0  
**Duration:** 10.03 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_execute_graph_modes.py`

#### Raw Test Output:

```
Test timed out after 10 seconds
```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-group-interface-pins"></a>[FAIL] test_group_interface_pins.py

**File Status:** FAILED  
**Total Cases:** 28  
**Passed:** 23  
**Failed:** 0  
**Errors:** 5  
**Duration:** 0.18 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_interface_pins.py`

#### Individual Test Cases:

- ✅ **test_analyze_external_connections_input_interface** (test_group_interface_pins) - PASSED
- ✅ **test_analyze_external_connections_internal_connections** (test_group_interface_pins) - PASSED
- ✅ **test_analyze_external_connections_no_connections** (test_group_interface_pins) - PASSED
- ✅ **test_analyze_external_connections_output_interface** (test_group_interface_pins) - PASSED
- ✅ **test_cleanup_routing** (test_group_interface_pins) - PASSED
- ✅ **test_complete_group_creation_workflow** (test_group_interface_pins) - PASSED
- ⚠️ **test_create_routing_for_group** (test_group_interface_pins) - ERROR
- ✅ **test_generate_interface_pins_no_interfaces** (test_group_interface_pins) - PASSED
- ⚠️ **test_generate_interface_pins_with_interfaces** (test_group_interface_pins) - ERROR
- ⚠️ **test_interface_pin_creation** (test_group_interface_pins) - ERROR
- ⚠️ **test_interface_pin_mapping_management** (test_group_interface_pins) - ERROR
- ⚠️ **test_interface_pin_serialization** (test_group_interface_pins) - ERROR
- ✅ **test_performance_with_large_selection** (test_group_interface_pins) - PASSED
- ✅ **test_pin_name_generation_multiple_interfaces** (test_group_interface_pins) - PASSED
- ✅ **test_pin_name_generation_single_interface** (test_group_interface_pins) - PASSED
- ✅ **test_resolve_any_type_present** (test_group_interface_pins) - PASSED
- ✅ **test_resolve_compatible_types** (test_group_interface_pins) - PASSED
- ✅ **test_resolve_incompatible_types** (test_group_interface_pins) - PASSED
- ✅ **test_resolve_single_type** (test_group_interface_pins) - PASSED
- ✅ **test_routing_status** (test_group_interface_pins) - PASSED
- ✅ **test_type_inference_any_type_present** (test_group_interface_pins) - PASSED
- ✅ **test_type_inference_multiple_compatible_types** (test_group_interface_pins) - PASSED
- ✅ **test_type_inference_single_type** (test_group_interface_pins) - PASSED
- ✅ **test_validate_grouping_feasibility_missing_nodes** (test_group_interface_pins) - PASSED
- ✅ **test_validate_grouping_feasibility_too_few_nodes** (test_group_interface_pins) - PASSED
- ✅ **test_validate_grouping_feasibility_valid** (test_group_interface_pins) - PASSED
- ✅ **test_validate_type_compatibility_invalid** (test_group_interface_pins) - PASSED
- ✅ **test_validate_type_compatibility_valid** (test_group_interface_pins) - PASSED

#### Raw Test Output:

```

test_analyze_external_connections_input_interface (tests.test_group_interface_pins.TestConnectionAnalyzer.test_analyze_external_connections_input_interface)
Test detection of input interfaces. ... ok
test_analyze_external_connections_internal_connections (tests.test_group_interface_pins.TestConnectionAnalyzer.test_analyze_external_connections_internal_connections)
Test detection of internal connections. ... ok
test_analyze_external_connections_no_connections (tests.test_group_interface_pins.TestConnectionAnalyzer.test_analyze_external_connections_no_connections)
Test analysis when no connections exist. ... ok
test_analyze_external_connections_output_interface (tests.test_group_interface_pins.TestConnectionAnalyzer.test_analyze_external_connections_output_interface)
Test detection of output interfaces. ... ok
test_validate_grouping_feasibility_missing_nodes (tests.test_group_interface_pins.TestConnectionAnalyzer.test_validate_grouping_feasibility_missing_nodes)
Test validation with missing nodes. ... ok
test_validate_grouping_feasibility_too_few_nodes (tests.test_group_interface_pins.TestConnectionAnalyzer.test_validate_grouping_feasibility_too_few_nodes)
Test validation with too few nodes. ... ok
test_validate_grouping_feasibility_valid (tests.test_group_interface_pins.TestConnectionAnalyzer.test_validate_grouping_feasibility_valid)
Test validation with valid grouping selection. ... ok
test_cleanup_routing (tests.test_group_interface_pins.TestGroupConnectionRouter.test_clean
... (output truncated)
```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-group-ui-integration"></a>[FAIL] test_group_ui_integration.py

**File Status:** FAILED  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 1  
**Errors:** 0  
**Duration:** 10.01 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_ui_integration.py`

#### Raw Test Output:

```
Test timed out after 10 seconds
```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-performance-fix-demonstration"></a>[FAIL] test_performance_fix_demonstration.py

**File Status:** FAILED  
**Total Cases:** 2  
**Passed:** 1  
**Failed:** 1  
**Errors:** 0  
**Duration:** 0.23 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_performance_fix_demonstration.py`

#### Individual Test Cases:

- ❌ **test_performance_fix_demonstration** (test_performance_fix_demonstration) - FAILED
- ✅ **test_connection_integrity_validation** (test_performance_fix_demonstration) - PASSED

#### Raw Test Output:

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
Undo operation took: 1.70 ms
Connections after undo: 3
Connection traversals after undo: 4
Traversal ratio (current/baseline): 0.67

test_connection_integrity_validation (tests.test_performance_fix_demonstration.TestPerformanceFixDemonstration.test_connection_integrity_validation)
Validate that connections are properly managed without duplicates. ... ok
test_performance_fix_demonstration (tests.test_performance_fix_demonstration.TestPerformanceFixDemonstration.test_performance_fix_demonstration)
Demonstrate that performance remains stable after delete-undo cycles. ... FAIL

======================================================================
FAIL: test_performance_fix_demonstration (tests.test_performance_fix_demonstration.TestPerformanceFixDemonstration.test_performance_fix_demonstration)
Demonstrate that performance remains stable after delete-undo cycles.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "E:\HOME\PyFlowGraph\tests\test_performance_fix_demonstration.py", line 188, in test_performance_fi
... (output truncated)
```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-performance-regression-validation"></a>[FAIL] test_performance_regression_validation.py

**File Status:** FAILED  
**Total Cases:** 4  
**Passed:** 3  
**Failed:** 1  
**Errors:** 0  
**Duration:** 0.26 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_performance_regression_validation.py`

#### Individual Test Cases:

- ❌ **test_duplicate_connection_prevention** (test_performance_regression_validation) - FAILED
- ✅ **test_execution_performance_stability** (test_performance_regression_validation) - PASSED
- ✅ **test_multiple_delete_undo_cycles** (test_performance_regression_validation) - PASSED
- ✅ **test_performance_regression_thresholds** (test_performance_regression_validation) - PASSED

#### Raw Test Output:

```

=== Testing Duplicate Connection Prevention ===
Initial state: 2 graph connections, 4 pin connections
Undo operation took: 2.29 ms
After undo: 2 graph connections, 6 pin connections

=== Testing Execution Performance Stability ===
Baseline execution time: 0.001 ms
Post-undo execution time: 0.001 ms
Performance ratio (post-undo / baseline): 0.780

=== Testing Multiple Delete-Undo Cycles ===
Cycle 1/3
Cycle 1 performance change: -1.9%
Cycle 2/3
Cycle 2 performance change: 21.2%
Cycle 3/3
Cycle 3 performance change: 15.4%
Maximum performance degradation: 21.2%

=== Testing Performance Regression Thresholds ===
Performance thresholds: Delete=0.02ms, Undo=2.07ms

test_duplicate_connection_prevention (tests.test_performance_regression_validation.TestPerformanceRegressionValidation.test_duplicate_connection_prevention)
Test that duplicate connections are prevented during undo. ... FAIL
test_execution_performance_stability (tests.test_performance_regression_validation.TestPerformanceRegressionValidation.test_execution_performance_stability)
Test that execution performance remains stable after delete-undo. ... ok
test_multiple_delete_undo_cycles (tests.test_performance_regression_validation.TestPerformanceRegressionValidation.test_multiple_delete_undo_cycles)
Test that multiple delete-undo cycles don't cause cumulative performance issues. ... ok
test_performance_regression_thresholds (tests.test_performance_regression_validation.TestPerformanceRegressionValidation.test_performance_re
... (output truncated)
```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-real-workflow-integration"></a>[FAIL] test_real_workflow_integration.py

**File Status:** FAILED  
**Total Cases:** 12  
**Passed:** 11  
**Failed:** 1  
**Errors:** 0  
**Duration:** 0.29 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_real_workflow_integration.py`

#### Individual Test Cases:

- ❌ **test_complex_multi_node_operations** (test_real_workflow_integration) - FAILED
- ✅ **test_code_modification_with_real_node_data** (test_real_workflow_integration) - PASSED
- ✅ **test_connection_creation_with_missing_pins** (test_real_workflow_integration) - PASSED
- ✅ **test_empty_charset_error_handling** (test_real_workflow_integration) - PASSED
- ✅ **test_error_handling_with_malformed_data** (test_real_workflow_integration) - PASSED
- ✅ **test_gui_state_preservation_in_paste** (test_real_workflow_integration) - PASSED
- ✅ **test_memory_usage_with_real_data** (test_real_workflow_integration) - PASSED
- ✅ **test_node_positioning_in_paste_operation** (test_real_workflow_integration) - PASSED
- ✅ **test_paste_real_password_generator_workflow** (test_real_workflow_integration) - PASSED
- ✅ **test_strength_analyzer_edge_cases** (test_real_workflow_integration) - PASSED
- ✅ **test_uuid_mapping_collision_bug** (test_real_workflow_integration) - PASSED
- ✅ **test_workflow_connection_integrity** (test_real_workflow_integration) - PASSED

#### Raw Test Output:

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


test_connection_creation_with_missing_pins (tests.test_real_workflow_integration.TestCommandSystemBugs.test_connection_creation_with_missing_pins)
Test connection creation when pins are missing. ... ok
test_uuid_mapping_collision_bug (tests.test_real_workflow_integration.TestCommandSystemBugs.test_uuid_mapping_collision_bug)
Test for UUID collision bug in PasteNodesCommand. ... ok
test_code_modification_with_real_node_data (tests.test_real_workflow_integration.TestRealWorkflowIntegration.test_code_modification_with_real_node_data)
Test code modification using real node code from example. ... ok
test_complex_multi_node_operations (tests.test_real_workflow_integration.TestRealWorkflowIntegration.test_complex_multi_node_operations)
Test complex operations with multiple nodes from real workflow. ... FAIL
test_error_handling_with_malformed_data (tests.test_real_workflow_integration.TestRealWorkflowIntegration.test_error_handling_with_malformed_data)
Test error handling when example data is malformed. ... ok
test_gui_state_preservation_in_paste (te
... (output truncated)
```

[↑ Back to Test Results](#test-results-by-file)

---

### [PASS] test_basic_commands.py

**File Status:** PASSED  
**Total Cases:** 8  
**Passed:** 8  
**Duration:** 0.10 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_basic_commands.py`

#### Individual Test Cases:

- ✅ **test_basic_command_functionality** (test_basic_commands) - PASSED
- ✅ **test_command_descriptions_and_ui_feedback** (test_basic_commands) - PASSED
- ✅ **test_command_history_basic_operations** (test_basic_commands) - PASSED
- ✅ **test_command_history_depth_limits** (test_basic_commands) - PASSED
- ✅ **test_command_history_memory_monitoring** (test_basic_commands) - PASSED
- ✅ **test_composite_command_execution** (test_basic_commands) - PASSED
- ✅ **test_composite_command_rollback** (test_basic_commands) - PASSED
- ✅ **test_performance_basic** (test_basic_commands) - PASSED

---

### [PASS] test_code_change_command.py

**File Status:** PASSED  
**Total Cases:** 10  
**Passed:** 10  
**Duration:** 0.12 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_code_change_command.py`

#### Individual Test Cases:

- ✅ **test_command_creation** (test_code_change_command) - PASSED
- ✅ **test_empty_code_handling** (test_code_change_command) - PASSED
- ✅ **test_execute_applies_new_code** (test_code_change_command) - PASSED
- ✅ **test_execute_handles_exceptions** (test_code_change_command) - PASSED
- ✅ **test_large_code_handling** (test_code_change_command) - PASSED
- ✅ **test_memory_usage_estimation** (test_code_change_command) - PASSED
- ✅ **test_special_characters_in_code** (test_code_change_command) - PASSED
- ✅ **test_undo_handles_exceptions** (test_code_change_command) - PASSED
- ✅ **test_undo_restores_old_code** (test_code_change_command) - PASSED
- ✅ **test_unicode_characters_forbidden** (test_code_change_command) - PASSED

---

### [PASS] test_code_editor_undo_workflow.py

**File Status:** PASSED  
**Total Cases:** 9  
**Passed:** 9  
**Duration:** 0.21 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_code_editor_undo_workflow.py`

#### Individual Test Cases:

- ✅ **test_accept_dialog_creates_atomic_command** (test_code_editor_undo_workflow) - PASSED
- ✅ **test_cancel_dialog_no_graph_history_impact** (test_code_editor_undo_workflow) - PASSED
- ✅ **test_ctrl_z_in_editor_uses_internal_undo** (test_code_editor_undo_workflow) - PASSED
- ✅ **test_editor_undo_redo_independent_of_graph** (test_code_editor_undo_workflow) - PASSED
- ✅ **test_focus_dependent_undo_behavior** (test_code_editor_undo_workflow) - PASSED
- ✅ **test_keyboard_shortcuts_workflow** (test_code_editor_undo_workflow) - PASSED
- ✅ **test_large_code_editing_performance** (test_code_editor_undo_workflow) - PASSED
- ✅ **test_multiple_editors_independent_undo** (test_code_editor_undo_workflow) - PASSED
- ✅ **test_user_scenario_edit_undo_redo_edit_again** (test_code_editor_undo_workflow) - PASSED

---

### [PASS] test_command_system.py

**File Status:** PASSED  
**Total Cases:** 24  
**Passed:** 24  
**Duration:** 0.47 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_command_system.py`

#### Individual Test Cases:

- ✅ **test_code_change_command** (test_command_system) - PASSED
- ✅ **test_command_creation** (test_command_system) - PASSED
- ✅ **test_command_execution** (test_command_system) - PASSED
- ✅ **test_command_execution** (test_command_system) - PASSED
- ✅ **test_command_undo** (test_command_system) - PASSED
- ✅ **test_composite_execution** (test_command_system) - PASSED
- ✅ **test_composite_rollback_on_failure** (test_command_system) - PASSED
- ✅ **test_composite_undo** (test_command_system) - PASSED
- ✅ **test_create_node_command** (test_command_system) - PASSED
- ✅ **test_create_node_undo** (test_command_system) - PASSED
- ✅ **test_delete_node_command** (test_command_system) - PASSED
- ✅ **test_delete_node_undo** (test_command_system) - PASSED
- ✅ **test_depth_limit_enforcement** (test_command_system) - PASSED
- ✅ **test_individual_operation_performance** (test_command_system) - PASSED
- ✅ **test_keyboard_shortcuts_integration** (test_command_system) - PASSED
- ✅ **test_memory_usage_estimation** (test_command_system) - PASSED
- ✅ **test_memory_usage_limits** (test_command_system) - PASSED
- ✅ **test_move_command_merging** (test_command_system) - PASSED
- ✅ **test_move_node_command** (test_command_system) - PASSED
- ✅ **test_node_graph_command_execution** (test_command_system) - PASSED
- ✅ **test_performance_monitoring** (test_command_system) - PASSED
- ✅ **test_property_change_command** (test_command_system) - PASSED
- ✅ **test_undo_redo_cycle** (test_command_system) - PASSED
- ✅ **test_undo_redo_performance** (test_command_system) - PASSED

---

### [PASS] test_composite_commands.py

**File Status:** PASSED  
**Total Cases:** 13  
**Passed:** 13  
**Duration:** 0.17 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_composite_commands.py`

#### Individual Test Cases:

- ✅ **test_composite_command_add_command** (test_composite_commands) - PASSED
- ✅ **test_composite_command_all_succeed** (test_composite_commands) - PASSED
- ✅ **test_composite_command_memory_usage** (test_composite_commands) - PASSED
- ✅ **test_composite_command_partial_undo_failure** (test_composite_commands) - PASSED
- ✅ **test_composite_command_undo** (test_composite_commands) - PASSED
- ✅ **test_composite_command_undo_without_execute** (test_composite_commands) - PASSED
- ✅ **test_composite_command_with_failure** (test_composite_commands) - PASSED
- ✅ **test_delete_multiple_command_description_logic** (test_composite_commands) - PASSED
- ✅ **test_empty_composite_command** (test_composite_commands) - PASSED
- ✅ **test_large_composite_command** (test_composite_commands) - PASSED
- ✅ **test_meaningful_descriptions** (test_composite_commands) - PASSED
- ✅ **test_move_multiple_command_creation** (test_composite_commands) - PASSED
- ✅ **test_paste_nodes_command_creation** (test_composite_commands) - PASSED

---

### [PASS] test_connection_system.py

**File Status:** PASSED  
**Total Cases:** 14  
**Passed:** 14  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_connection_system.py`

#### Individual Test Cases:

- ✅ **test_connection_color_inheritance** (test_connection_system) - PASSED
- ✅ **test_connection_creation** (test_connection_system) - PASSED
- ✅ **test_connection_destruction** (test_connection_system) - PASSED
- ✅ **test_connection_double_click_reroute** (test_connection_system) - PASSED
- ✅ **test_connection_graph_integration** (test_connection_system) - PASSED
- ✅ **test_connection_path_curve_properties** (test_connection_system) - PASSED
- ✅ **test_connection_path_generation** (test_connection_system) - PASSED
- ✅ **test_connection_selection_visual_feedback** (test_connection_system) - PASSED
- ✅ **test_connection_serialization** (test_connection_system) - PASSED
- ✅ **test_connection_temporary_mode** (test_connection_system) - PASSED
- ✅ **test_connection_update_path** (test_connection_system) - PASSED
- ✅ **test_connection_validation** (test_connection_system) - PASSED
- ✅ **test_connection_with_reroute_node** (test_connection_system) - PASSED
- ✅ **test_multiple_connections_on_pin** (test_connection_system) - PASSED

---

### [PASS] test_connection_system_headless.py

**File Status:** PASSED  
**Total Cases:** 14  
**Passed:** 14  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_connection_system_headless.py`

#### Individual Test Cases:

- ✅ **test_connection_color_inheritance** (test_connection_system_headless) - PASSED
- ✅ **test_connection_creation** (test_connection_system_headless) - PASSED
- ✅ **test_connection_destruction** (test_connection_system_headless) - PASSED
- ✅ **test_connection_double_click_reroute** (test_connection_system_headless) - PASSED
- ✅ **test_connection_graph_integration** (test_connection_system_headless) - PASSED
- ✅ **test_connection_path_curve_properties** (test_connection_system_headless) - PASSED
- ✅ **test_connection_path_generation** (test_connection_system_headless) - PASSED
- ✅ **test_connection_selection_visual_feedback** (test_connection_system_headless) - PASSED
- ✅ **test_connection_serialization** (test_connection_system_headless) - PASSED
- ✅ **test_connection_temporary_mode** (test_connection_system_headless) - PASSED
- ✅ **test_connection_update_path** (test_connection_system_headless) - PASSED
- ✅ **test_connection_validation** (test_connection_system_headless) - PASSED
- ✅ **test_connection_with_reroute_node** (test_connection_system_headless) - PASSED
- ✅ **test_multiple_connections_on_pin** (test_connection_system_headless) - PASSED

---

### [PASS] test_copy_paste_integration.py

**File Status:** PASSED  
**Total Cases:** 7  
**Passed:** 7  
**Duration:** 0.16 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_copy_paste_integration.py`

#### Individual Test Cases:

- ✅ **test_deserialize_to_paste_format_conversion** (test_copy_paste_integration) - PASSED
- ✅ **test_paste_command_memory_usage** (test_copy_paste_integration) - PASSED
- ✅ **test_paste_command_partial_failure_rollback** (test_copy_paste_integration) - PASSED
- ✅ **test_paste_command_undo_behavior** (test_copy_paste_integration) - PASSED
- ✅ **test_paste_multiple_nodes_with_connections** (test_copy_paste_integration) - PASSED
- ✅ **test_paste_nodes_positioning** (test_copy_paste_integration) - PASSED
- ✅ **test_paste_single_node_workflow** (test_copy_paste_integration) - PASSED

---

### [PASS] test_debug_flags.py

**File Status:** PASSED  
**Total Cases:** 3  
**Passed:** 3  
**Duration:** 0.22 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_debug_flags.py`

#### Individual Test Cases:

- ✅ **test_debug_flags_disabled_by_default** (test_debug_flags) - PASSED
- ✅ **test_execution_debug_flag_enables_output** (test_debug_flags) - PASSED
- ✅ **test_gui_debug_flag_enables_output** (test_debug_flags) - PASSED

---

### [PASS] test_delete_undo_performance_regression.py

**File Status:** PASSED  
**Total Cases:** 4  
**Passed:** 0  
**Duration:** 1.22 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_delete_undo_performance_regression.py`

#### Individual Test Cases:

- ⏭️ **test_connection_heavy_node_performance** (test_delete_undo_performance_regression) - SKIPPED
- ⏭️ **test_multiple_node_delete_undo_performance** (test_delete_undo_performance_regression) - SKIPPED
- ⏭️ **test_performance_thresholds_compliance** (test_delete_undo_performance_regression) - SKIPPED
- ⏭️ **test_single_node_delete_undo_performance** (test_delete_undo_performance_regression) - SKIPPED

---

### [PASS] test_end_to_end_workflows.py

**File Status:** PASSED  
**Total Cases:** 4  
**Passed:** 4  
**Duration:** 3.26 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_end_to_end_workflows.py`

#### Individual Test Cases:

- ✅ **test_create_save_and_load_workflow** (test_end_to_end_workflows) - PASSED
- ✅ **test_invalid_connection_handling** (test_end_to_end_workflows) - PASSED
- ✅ **test_modify_existing_pipeline** (test_end_to_end_workflows) - PASSED
- ✅ **test_undo_redo_complex_operations** (test_end_to_end_workflows) - PASSED

---

### [PASS] test_execution_engine.py

**File Status:** PASSED  
**Total Cases:** 12  
**Passed:** 12  
**Duration:** 0.30 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_execution_engine.py`

#### Individual Test Cases:

- ✅ **test_data_flow_between_nodes** (test_execution_engine) - PASSED
- ✅ **test_entry_point_detection** (test_execution_engine) - PASSED
- ✅ **test_execution_error_handling** (test_execution_engine) - PASSED
- ✅ **test_execution_flow_ordering** (test_execution_engine) - PASSED
- ✅ **test_execution_limit_protection** (test_execution_engine) - PASSED
- ✅ **test_execution_timeout_handling** (test_execution_engine) - PASSED
- ✅ **test_missing_virtual_environment** (test_execution_engine) - PASSED
- ✅ **test_multiple_entry_points** (test_execution_engine) - PASSED
- ✅ **test_node_execution_success** (test_execution_engine) - PASSED
- ✅ **test_python_executable_path** (test_execution_engine) - PASSED
- ✅ **test_reroute_node_execution** (test_execution_engine) - PASSED
- ✅ **test_subprocess_security_flags** (test_execution_engine) - PASSED

---

### [PASS] test_file_formats.py

**File Status:** PASSED  
**Total Cases:** 2  
**Passed:** 2  
**Duration:** 0.08 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_file_formats.py`

#### Individual Test Cases:

- ✅ **test_json_to_markdown_conversion** (test_file_formats) - PASSED
- ✅ **test_markdown_to_json_conversion** (test_file_formats) - PASSED

---

### [PASS] test_full_gui_integration.py

**File Status:** PASSED  
**Total Cases:** 14  
**Passed:** 13  
**Duration:** 6.96 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_full_gui_integration.py`

#### Individual Test Cases:

- ✅ **test_connection_visual_feedback** (test_full_gui_integration) - PASSED
- ✅ **test_create_and_save_simple_graph** (test_full_gui_integration) - PASSED
- ✅ **test_create_connection_between_nodes** (test_full_gui_integration) - PASSED
- ✅ **test_create_node_via_context_menu** (test_full_gui_integration) - PASSED
- ✅ **test_invalid_operations_dont_crash** (test_full_gui_integration) - PASSED
- ⏭️ **test_load_example_file_if_exists** (test_full_gui_integration) - SKIPPED
- ✅ **test_menu_bar_exists** (test_full_gui_integration) - PASSED
- ✅ **test_node_code_editing_workflow** (test_full_gui_integration) - PASSED
- ✅ **test_node_selection_and_properties** (test_full_gui_integration) - PASSED
- ✅ **test_node_with_invalid_code_handling** (test_full_gui_integration) - PASSED
- ✅ **test_reroute_node_creation_and_deletion** (test_full_gui_integration) - PASSED
- ✅ **test_reroute_node_undo_redo_cycle** (test_full_gui_integration) - PASSED
- ✅ **test_view_panning_and_zooming** (test_full_gui_integration) - PASSED
- ✅ **test_view_selection_rectangle** (test_full_gui_integration) - PASSED

---

### [PASS] test_graph_management.py

**File Status:** PASSED  
**Total Cases:** 12  
**Passed:** 12  
**Duration:** 0.31 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_graph_management.py`

#### Individual Test Cases:

- ✅ **test_clipboard_operations** (test_graph_management) - PASSED
- ✅ **test_connection_creation_and_management** (test_graph_management) - PASSED
- ✅ **test_graph_bounds_and_scene_management** (test_graph_management) - PASSED
- ✅ **test_graph_clear** (test_graph_management) - PASSED
- ✅ **test_graph_deserialization** (test_graph_management) - PASSED
- ✅ **test_graph_initialization** (test_graph_management) - PASSED
- ✅ **test_graph_selection_management** (test_graph_management) - PASSED
- ✅ **test_graph_serialization** (test_graph_management) - PASSED
- ✅ **test_keyboard_deletion** (test_graph_management) - PASSED
- ✅ **test_node_creation_and_addition** (test_graph_management) - PASSED
- ✅ **test_node_removal** (test_graph_management) - PASSED
- ✅ **test_reroute_node_creation_on_connection** (test_graph_management) - PASSED

---

### <a id="test-group-data-flow"></a>[ERROR] test_group_data_flow.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.52 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_data_flow.py`

#### Raw Test Output:

```

test_complex_data_flow_scenario (tests.test_group_data_flow.TestDataFlowIntegration.test_complex_data_flow_scenario)
Test complex scenario with multiple inputs, outputs, and internal routing. ... QFontDatabase: Must construct a QGuiApplication before accessing QFontDatabase

```

[↑ Back to Test Results](#test-results-by-file)

---

### [PASS] test_group_resize.py

**File Status:** PASSED  
**Total Cases:** 14  
**Passed:** 14  
**Duration:** 0.17 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_resize.py`

#### Individual Test Cases:

- ✅ **test_bounding_rect_includes_handles_when_selected** (test_group_resize) - PASSED
- ✅ **test_command_creation** (test_group_resize) - PASSED
- ✅ **test_command_execute** (test_group_resize) - PASSED
- ✅ **test_command_undo** (test_group_resize) - PASSED
- ✅ **test_cursor_for_handle** (test_group_resize) - PASSED
- ✅ **test_handle_detection** (test_group_resize) - PASSED
- ✅ **test_handles_only_show_when_selected** (test_group_resize) - PASSED
- ✅ **test_increased_handle_size** (test_group_resize) - PASSED
- ✅ **test_larger_hit_box_detection** (test_group_resize) - PASSED
- ✅ **test_member_nodes_dont_move_during_resize** (test_group_resize) - PASSED
- ✅ **test_membership_update_after_resize** (test_group_resize) - PASSED
- ✅ **test_resize_operation** (test_group_resize) - PASSED
- ✅ **test_resize_with_minimum_constraints** (test_group_resize) - PASSED
- ✅ **test_selection_change_updates_visual** (test_group_resize) - PASSED

---

### [PASS] test_group_system.py

**File Status:** PASSED  
**Total Cases:** 20  
**Passed:** 20  
**Duration:** 0.23 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_group_system.py`

#### Individual Test Cases:

- ✅ **test_add_member_node** (test_group_system) - PASSED
- ✅ **test_command_cannot_merge** (test_group_system) - PASSED
- ✅ **test_command_creation** (test_group_system) - PASSED
- ✅ **test_command_execute** (test_group_system) - PASSED
- ✅ **test_command_memory_usage** (test_group_system) - PASSED
- ✅ **test_command_redo** (test_group_system) - PASSED
- ✅ **test_command_undo** (test_group_system) - PASSED
- ✅ **test_duplicate_nodes** (test_group_system) - PASSED
- ✅ **test_group_creation_with_defaults** (test_group_system) - PASSED
- ✅ **test_group_creation_with_parameters** (test_group_system) - PASSED
- ✅ **test_group_deserialization** (test_group_system) - PASSED
- ✅ **test_group_serialization** (test_group_system) - PASSED
- ✅ **test_insufficient_nodes** (test_group_system) - PASSED
- ✅ **test_invalid_node_types** (test_group_system) - PASSED
- ✅ **test_name_generation_empty_selection** (test_group_system) - PASSED
- ✅ **test_name_generation_few_nodes** (test_group_system) - PASSED
- ✅ **test_name_generation_many_nodes** (test_group_system) - PASSED
- ✅ **test_name_generation_nodes_without_titles** (test_group_system) - PASSED
- ✅ **test_remove_member_node** (test_group_system) - PASSED
- ✅ **test_valid_group_creation** (test_group_system) - PASSED

---

### <a id="test-gui-node-deletion"></a>[ERROR] test_gui_node_deletion.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.24 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_gui_node_deletion.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-gui-node-deletion-workflow"></a>[ERROR] test_gui_node_deletion_workflow.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.24 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_gui_node_deletion_workflow.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### [PASS] test_gui_value_update_regression.py

**File Status:** PASSED  
**Total Cases:** 2  
**Passed:** 2  
**Duration:** 0.27 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_gui_value_update_regression.py`

#### Individual Test Cases:

- ✅ **test_connection_integrity_after_undo** (test_gui_value_update_regression) - PASSED
- ✅ **test_gui_value_update_after_delete_undo** (test_gui_value_update_regression) - PASSED

---

### [PASS] test_integration.py

**File Status:** PASSED  
**Total Cases:** 3  
**Passed:** 3  
**Duration:** 0.29 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_integration.py`

#### Individual Test Cases:

- ✅ **test_complete_graph_workflow** (test_integration) - PASSED
- ✅ **test_error_recovery** (test_integration) - PASSED
- ✅ **test_example_file_loading** (test_integration) - PASSED

---

### <a id="test-markdown-loaded-deletion"></a>[ERROR] test_markdown_loaded_deletion.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.19 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_markdown_loaded_deletion.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-node-deletion-connection-bug"></a>[ERROR] test_node_deletion_connection_bug.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.14 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_node_deletion_connection_bug.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### [PASS] test_node_system.py

**File Status:** PASSED  
**Total Cases:** 12  
**Passed:** 12  
**Duration:** 0.27 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_node_system.py`

#### Individual Test Cases:

- ✅ **test_code_management** (test_node_system) - PASSED
- ✅ **test_execution_pins** (test_node_system) - PASSED
- ✅ **test_invalid_code_handling** (test_node_system) - PASSED
- ✅ **test_node_creation** (test_node_system) - PASSED
- ✅ **test_node_deserialization** (test_node_system) - PASSED
- ✅ **test_node_gui_code_management** (test_node_system) - PASSED
- ✅ **test_node_position_management** (test_node_system) - PASSED
- ✅ **test_node_properties_modification** (test_node_system) - PASSED
- ✅ **test_node_serialization** (test_node_system) - PASSED
- ✅ **test_node_visual_properties** (test_node_system) - PASSED
- ✅ **test_pin_generation_from_code** (test_node_system) - PASSED
- ✅ **test_pin_type_detection** (test_node_system) - PASSED

---

### [PASS] test_node_system_headless.py

**File Status:** PASSED  
**Total Cases:** 12  
**Passed:** 12  
**Duration:** 0.26 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_node_system_headless.py`

#### Individual Test Cases:

- ✅ **test_code_management** (test_node_system_headless) - PASSED
- ✅ **test_execution_pins** (test_node_system_headless) - PASSED
- ✅ **test_invalid_code_handling** (test_node_system_headless) - PASSED
- ✅ **test_node_creation** (test_node_system_headless) - PASSED
- ✅ **test_node_deserialization** (test_node_system_headless) - PASSED
- ✅ **test_node_gui_code_management** (test_node_system_headless) - PASSED
- ✅ **test_node_position_management** (test_node_system_headless) - PASSED
- ✅ **test_node_properties_modification** (test_node_system_headless) - PASSED
- ✅ **test_node_serialization** (test_node_system_headless) - PASSED
- ✅ **test_node_visual_properties** (test_node_system_headless) - PASSED
- ✅ **test_pin_generation_from_code** (test_node_system_headless) - PASSED
- ✅ **test_pin_type_detection** (test_node_system_headless) - PASSED

---

### <a id="test-password-generator-chaos"></a>[ERROR] test_password_generator_chaos.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.27 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_password_generator_chaos.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### [PASS] test_pin_system.py

**File Status:** PASSED  
**Total Cases:** 12  
**Passed:** 12  
**Duration:** 0.28 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_pin_system.py`

#### Individual Test Cases:

- ✅ **test_complex_pin_types** (test_pin_system) - PASSED
- ✅ **test_data_pin_type_colors** (test_pin_system) - PASSED
- ✅ **test_execution_pin_creation** (test_pin_system) - PASSED
- ✅ **test_pin_connection_management** (test_pin_system) - PASSED
- ✅ **test_pin_creation** (test_pin_system) - PASSED
- ✅ **test_pin_direction_constraints** (test_pin_system) - PASSED
- ✅ **test_pin_label_formatting** (test_pin_system) - PASSED
- ✅ **test_pin_scene_position** (test_pin_system) - PASSED
- ✅ **test_pin_type_compatibility** (test_pin_system) - PASSED
- ✅ **test_pin_update_connections** (test_pin_system) - PASSED
- ✅ **test_pin_value_storage** (test_pin_system) - PASSED
- ✅ **test_pin_with_node_integration** (test_pin_system) - PASSED

---

### [PASS] test_pin_system_headless.py

**File Status:** PASSED  
**Total Cases:** 12  
**Passed:** 12  
**Duration:** 0.25 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_pin_system_headless.py`

#### Individual Test Cases:

- ✅ **test_complex_pin_types** (test_pin_system_headless) - PASSED
- ✅ **test_data_pin_type_colors** (test_pin_system_headless) - PASSED
- ✅ **test_execution_pin_creation** (test_pin_system_headless) - PASSED
- ✅ **test_pin_connection_management** (test_pin_system_headless) - PASSED
- ✅ **test_pin_creation** (test_pin_system_headless) - PASSED
- ✅ **test_pin_direction_constraints** (test_pin_system_headless) - PASSED
- ✅ **test_pin_label_formatting** (test_pin_system_headless) - PASSED
- ✅ **test_pin_scene_position** (test_pin_system_headless) - PASSED
- ✅ **test_pin_type_compatibility** (test_pin_system_headless) - PASSED
- ✅ **test_pin_update_connections** (test_pin_system_headless) - PASSED
- ✅ **test_pin_value_storage** (test_pin_system_headless) - PASSED
- ✅ **test_pin_with_node_integration** (test_pin_system_headless) - PASSED

---

### <a id="test-reroute-creation-undo"></a>[ERROR] test_reroute_creation_undo.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.18 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_creation_undo.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-reroute-node-deletion"></a>[ERROR] test_reroute_node_deletion.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.17 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_node_deletion.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-reroute-undo-redo"></a>[ERROR] test_reroute_undo_redo.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.17 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_undo_redo.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-reroute-with-connections"></a>[ERROR] test_reroute_with_connections.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.17 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_reroute_with_connections.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### [PASS] test_selection_operations.py

**File Status:** PASSED  
**Total Cases:** 15  
**Passed:** 12  
**Duration:** 0.25 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_selection_operations.py`

#### Individual Test Cases:

- ⏭️ **test_delete_command_creation** (test_selection_operations) - SKIPPED
- ✅ **test_delete_command_memory_usage** (test_selection_operations) - PASSED
- ⏭️ **test_delete_connections_only_description** (test_selection_operations) - SKIPPED
- ⏭️ **test_delete_mixed_items_description** (test_selection_operations) - SKIPPED
- ✅ **test_delete_multiple_nodes_description** (test_selection_operations) - PASSED
- ✅ **test_delete_single_node_description** (test_selection_operations) - PASSED
- ✅ **test_empty_selection_delete** (test_selection_operations) - PASSED
- ✅ **test_empty_selection_move** (test_selection_operations) - PASSED
- ✅ **test_large_selection_performance** (test_selection_operations) - PASSED
- ✅ **test_move_command_creation** (test_selection_operations) - PASSED
- ✅ **test_move_command_memory_usage** (test_selection_operations) - PASSED
- ✅ **test_move_multiple_nodes_description** (test_selection_operations) - PASSED
- ✅ **test_move_multiple_undo_order** (test_selection_operations) - PASSED
- ✅ **test_move_single_node_description** (test_selection_operations) - PASSED
- ✅ **test_unknown_item_type_delete** (test_selection_operations) - PASSED

---

### [PASS] test_undo_history_integration.py

**File Status:** PASSED  
**Total Cases:** 10  
**Passed:** 10  
**Duration:** 0.41 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_undo_history_integration.py`

#### Individual Test Cases:

- ✅ **test_already_at_position_message** (test_undo_history_integration) - PASSED
- ✅ **test_dialog_memory_efficiency** (test_undo_history_integration) - PASSED
- ✅ **test_dialog_performance_with_large_history** (test_undo_history_integration) - PASSED
- ✅ **test_dialog_shows_real_command_history** (test_undo_history_integration) - PASSED
- ✅ **test_history_updates_after_undo_redo** (test_undo_history_integration) - PASSED
- ✅ **test_jump_functionality_with_real_commands** (test_undo_history_integration) - PASSED
- ✅ **test_jump_operation_status_messages** (test_undo_history_integration) - PASSED
- ✅ **test_mixed_command_types_display** (test_undo_history_integration) - PASSED
- ✅ **test_redo_status_messages** (test_undo_history_integration) - PASSED
- ✅ **test_undo_status_messages** (test_undo_history_integration) - PASSED

---

### [PASS] test_undo_history_workflow.py

**File Status:** PASSED  
**Total Cases:** 11  
**Passed:** 11  
**Duration:** 0.21 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_undo_history_workflow.py`

#### Individual Test Cases:

- ✅ **test_create_undo_redo_workflow** (test_undo_history_workflow) - PASSED
- ✅ **test_disabled_state_visual_feedback** (test_undo_history_workflow) - PASSED
- ✅ **test_error_recovery_workflow** (test_undo_history_workflow) - PASSED
- ✅ **test_history_dialog_workflow** (test_undo_history_workflow) - PASSED
- ✅ **test_keyboard_power_user_workflow** (test_undo_history_workflow) - PASSED
- ✅ **test_keyboard_shortcuts_work** (test_undo_history_workflow) - PASSED
- ✅ **test_large_history_performance_scenario** (test_undo_history_workflow) - PASSED
- ✅ **test_menu_actions_update_correctly** (test_undo_history_workflow) - PASSED
- ✅ **test_multiple_operations_history_navigation** (test_undo_history_workflow) - PASSED
- ✅ **test_status_bar_feedback_workflow** (test_undo_history_workflow) - PASSED
- ✅ **test_toolbar_buttons_sync_with_menu** (test_undo_history_workflow) - PASSED

---

### [PASS] test_undo_ui_integration.py

**File Status:** PASSED  
**Total Cases:** 13  
**Passed:** 13  
**Duration:** 0.39 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_undo_ui_integration.py`

#### Individual Test Cases:

- ✅ **test_actions_disabled_when_no_commands** (test_undo_ui_integration) - PASSED
- ✅ **test_actions_enabled_with_descriptions** (test_undo_ui_integration) - PASSED
- ✅ **test_dialog_initialization** (test_undo_ui_integration) - PASSED
- ✅ **test_double_click_triggers_jump** (test_undo_ui_integration) - PASSED
- ✅ **test_history_population_empty** (test_undo_ui_integration) - PASSED
- ✅ **test_history_population_with_commands** (test_undo_ui_integration) - PASSED
- ✅ **test_info_label_updates** (test_undo_ui_integration) - PASSED
- ✅ **test_jump_signal_emission** (test_undo_ui_integration) - PASSED
- ✅ **test_jump_to_earlier_index** (test_undo_ui_integration) - PASSED
- ✅ **test_jump_to_later_index** (test_undo_ui_integration) - PASSED
- ✅ **test_jump_to_same_index** (test_undo_ui_integration) - PASSED
- ✅ **test_refresh_functionality** (test_undo_ui_integration) - PASSED
- ✅ **test_selection_enables_jump_button** (test_undo_ui_integration) - PASSED

---

### <a id="test-user-scenario"></a>[ERROR] test_user_scenario.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.17 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_user_scenario.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-user-scenario-gui"></a>[ERROR] test_user_scenario_gui.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 0.20 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_user_scenario_gui.py`

#### Raw Test Output:

```


----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

```

[↑ Back to Test Results](#test-results-by-file)

---

### <a id="test-view-state-persistence"></a>[ERROR] test_view_state_persistence.py

**File Status:** ERROR  
**Total Cases:** 0  
**Passed:** 0  
**Failed:** 0  
**Errors:** 0  
**Duration:** 2.22 seconds  
**File Path:** `E:\HOME\PyFlowGraph\tests\test_view_state_persistence.py`

#### Raw Test Output:

```

=== NODE GRAPH REMOVE_NODE START ===
DEBUG: remove_node called with use_command=False
DEBUG: Node to remove: 'Password Configuration' (ID: 2376115792320)
DEBUG: Graph has 4 nodes before removal
DEBUG: Scene has 82 items before removal
DEBUG: Direct removal (bypassing command pattern)
DEBUG: Removing 0 connections first
DEBUG: Node has 12 pins to clean up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32efb0, parent=0x2293b267bb0, pos=0,84.5) at 0x000002293B8E5B40>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32f0b0, parent=0x2293b267bb0, pos=0,109.5) at 0x000002293B8C77C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32e7b0, parent=0x2293b267bb0, pos=0,134.5) at 0x000002293B8FC580>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32f230, parent=0x2293b267bb0, pos=0,159.5) at 0x000002293B8FC5C0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32f470, parent=0x2293b267bb0, pos=0,184.5) at 0x000002293B8FC300>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32ec70, parent=0x2293b267bb0, pos=296.75,84.5) at 0x000002293B8FFBC0>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32edf0, parent=0x2293b267bb0, pos=296.75,109.5) at 0x000002293B8FFF00>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32fbf0, parent=0x2293b267bb0, pos=296.75,134.5) at 0x000002293B8FD740>
DEBUG: Pin cleaned up
DEBUG: Cleaning up pin: <core.pin.Pin(0x2293b32faf0, parent=0x229
... (output truncated)
```

[↑ Back to Test Results](#test-results-by-file)

---

## Test Environment

- **Python Version:** 3.11.0
- **Test Runner:** PyFlowGraph Professional GUI Test Tool
- **Test Directory:** `tests/`
- **Generated By:** Badge Updater v2.0 (Individual Test Case Support)

---

*This report is automatically generated when tests are executed through the PyFlowGraph test tool.*
*Now showing individual test case results for more detailed analysis.*
*Last updated: 2025-08-20 01:49:54*

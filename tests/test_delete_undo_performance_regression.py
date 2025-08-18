#!/usr/bin/env python3
"""
Performance Regression Test for Delete-Undo Operations

Tests for performance issues when nodes are deleted and then undone,
specifically targeting the duplicate connection bug that causes exponential
execution slowdown after undo operations.

Focuses on the password generator tool example which has 4 nodes and 11 connections,
providing a realistic test scenario for connection restoration performance.
"""

import unittest
import sys
import os
import time
import random
from typing import List, Dict, Tuple
from unittest.mock import patch, MagicMock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

try:
    from PySide6.QtWidgets import QApplication, QTextEdit
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    from ui.editor.node_editor_window import NodeEditorWindow
    from core.node_graph import NodeGraph
    from core.node import Node
    from execution.graph_executor import GraphExecutor
    from commands.node_commands import DeleteNodeCommand
    from commands.command_history import CommandHistory
    
    QT_AVAILABLE = True
    
    class TestDeleteUndoPerformanceRegression(unittest.TestCase):
        """Test suite for delete-undo performance regression detection."""
        
        def setUp(self):
            """Set up test environment with password generator tool."""
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication([])
            
            # Create window and load password generator
            self.window = NodeEditorWindow()
            self.graph = self.window.graph
            self.view = self.window.view
            
            # Load password generator tool
            self._load_password_generator()
            
            # Setup execution environment
            self._setup_execution_environment()
            
            # Store original node and connection counts for validation
            self.original_node_count = len(self.graph.nodes)
            self.original_connection_count = len(self.graph.connections)
            
            print(f"Test setup complete: {self.original_node_count} nodes, {self.original_connection_count} connections")
        
        def tearDown(self):
            """Clean up test environment."""
            if hasattr(self, 'window'):
                self.window.close()
        
        def _load_password_generator(self):
            """Load the password generator tool example."""
            password_file = os.path.join(
                os.path.dirname(__file__), '..', 'examples', 'password_generator_tool.md'
            )
            
            if not os.path.exists(password_file):
                self.skipTest(f"Password generator file not found: {password_file}")
            
            try:
                # Load the file using the data file operations
                from data.file_operations import FileOperations
                file_ops = FileOperations(self.window, self.graph, self.view)
                file_ops.load_file(password_file)
                
                # Verify expected structure loaded
                self.assertGreaterEqual(len(self.graph.nodes), 4, "Expected at least 4 nodes in password generator")
                self.assertGreaterEqual(len(self.graph.connections), 10, "Expected at least 10 connections")
                
            except Exception as e:
                self.skipTest(f"Could not load password generator tool: {e}")
        
        def _setup_execution_environment(self):
            """Setup execution environment for performance testing."""
            # Create mock log widget for execution
            self.log_widget = QTextEdit()
            
            # Create executor
            def mock_venv_path():
                return os.path.join(os.path.dirname(__file__), 'venvs', 'default')
            
            self.executor = GraphExecutor(self.graph, self.log_widget, mock_venv_path)
            
            # Verify environment
            if not os.path.exists(mock_venv_path()):
                self.skipTest("Test virtual environment not found")
        
        def measure_execution_time(self, runs: int = 3) -> float:
            """
            Measure average execution time over multiple runs.
            
            Args:
                runs: Number of execution runs for statistical accuracy
                
            Returns:
                Average execution time in milliseconds
            """
            times = []
            
            for i in range(runs):
                # Clear previous execution state
                self.log_widget.clear()
                
                # Measure execution time
                start_time = time.perf_counter()
                
                with patch('subprocess.run') as mock_run:
                    # Mock successful subprocess execution
                    mock_run.return_value.stdout = '{"result": "test_output", "stdout": "test log"}'
                    mock_run.return_value.stderr = ''
                    mock_run.return_value.returncode = 0
                    
                    self.executor.execute()
                
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                times.append(elapsed_ms)
                
                # Small delay between runs
                time.sleep(0.01)
            
            avg_time = sum(times) / len(times)
            print(f"Execution times over {runs} runs: {times} ms, avg: {avg_time:.2f} ms")
            return avg_time
        
        def measure_undo_time(self, delete_command) -> float:
            """
            Measure time to undo a delete operation.
            
            Args:
                delete_command: The delete command to undo
                
            Returns:
                Undo operation time in milliseconds
            """
            start_time = time.perf_counter()
            success = delete_command.undo()
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            self.assertTrue(success, "Undo operation should succeed")
            print(f"Undo operation took: {elapsed_ms:.2f} ms")
            return elapsed_ms
        
        def validate_connection_integrity(self) -> bool:
            """
            Validate that connection counts and integrity are maintained.
            
            Returns:
                True if connections are properly restored
            """
            # Check overall connection count
            current_connections = len(self.graph.connections)
            if current_connections != self.original_connection_count:
                print(f"Connection count mismatch: expected {self.original_connection_count}, got {current_connections}")
                return False
            
            # Check for duplicate connections in pin lists
            duplicate_count = 0
            for node in self.graph.nodes:
                if hasattr(node, "title"):
                    # Check input pins
                    for pin in node.input_pins:
                        pin_connections = pin.connections
                        unique_connections = list(set(pin_connections))
                        if len(pin_connections) != len(unique_connections):
                            duplicate_count += len(pin_connections) - len(unique_connections)
                            print(f"Duplicate connections found in {node.title}.{pin.name}: {len(pin_connections)} vs {len(unique_connections)}")
                    
                    # Check output pins  
                    for pin in node.output_pins:
                        pin_connections = pin.connections
                        unique_connections = list(set(pin_connections))
                        if len(pin_connections) != len(unique_connections):
                            duplicate_count += len(pin_connections) - len(unique_connections)
                            print(f"Duplicate connections found in {node.title}.{pin.name}: {len(pin_connections)} vs {len(unique_connections)}")
            
            if duplicate_count > 0:
                print(f"Total duplicate connections detected: {duplicate_count}")
                return False
            
            print("Connection integrity validation: PASSED")
            return True
        
        def get_node_by_title(self, title: str):
            """Get node by title for testing."""
            for node in self.graph.nodes:
                if hasattr(node, 'title') and node.title == title:
                    return node
            self.fail(f"Node with title '{title}' not found")
        
        def test_single_node_delete_undo_performance(self):
            """Test performance when deleting and undoing a single node."""
            print("\n=== Testing Single Node Delete-Undo Performance ===")
            
            # Establish baseline execution performance
            baseline_time = self.measure_execution_time(runs=3)
            self.assertLess(baseline_time, 1000, "Baseline execution should be under 1 second")
            
            # Delete middle node (password-generator) - has moderate connections
            target_node = self.get_node_by_title("Password Generator Engine")
            delete_command = DeleteNodeCommand(self.graph, target_node)
            
            # Execute delete
            success = delete_command.execute()
            self.assertTrue(success, "Delete operation should succeed")
            
            # Measure undo time
            undo_time = self.measure_undo_time(delete_command)
            self.assertLess(undo_time, 50, "Undo should complete in under 50ms")
            
            # Validate connection integrity
            self.assertTrue(self.validate_connection_integrity(), "Connections should be properly restored")
            
            # Measure post-undo execution performance
            post_undo_time = self.measure_execution_time(runs=3)
            
            # Performance regression check - should be within 110% of baseline
            performance_ratio = post_undo_time / baseline_time
            print(f"Performance ratio (post-undo / baseline): {performance_ratio:.2f}")
            self.assertLessEqual(performance_ratio, 1.10, 
                               f"Post-undo execution should be within 110% of baseline "
                               f"(baseline: {baseline_time:.2f}ms, post-undo: {post_undo_time:.2f}ms)")
        
        def test_multiple_node_delete_undo_performance(self):
            """Test performance with multiple sequential delete-undo operations."""
            print("\n=== Testing Multiple Node Delete-Undo Performance ===")
            
            # Establish baseline
            baseline_time = self.measure_execution_time(runs=3)
            
            # Delete multiple nodes sequentially
            nodes_to_delete = ["Password Strength Analyzer", "Password Output & Copy"]
            delete_commands = []
            
            for node_title in nodes_to_delete:
                target_node = self.get_node_by_title(node_title)
                delete_command = DeleteNodeCommand(self.graph, target_node)
                success = delete_command.execute()
                self.assertTrue(success, f"Delete of '{node_title}' should succeed")
                delete_commands.append(delete_command)
            
            # Undo operations in reverse order
            cumulative_undo_time = 0
            for i, delete_command in enumerate(reversed(delete_commands)):
                undo_time = self.measure_undo_time(delete_command)
                cumulative_undo_time += undo_time
                
                # Validate integrity after each undo
                self.assertTrue(self.validate_connection_integrity(), 
                              f"Connections should be restored after undo {i+1}")
                
                # Check execution performance doesn't degrade cumulatively
                current_exec_time = self.measure_execution_time(runs=2)
                performance_ratio = current_exec_time / baseline_time
                self.assertLessEqual(performance_ratio, 1.15, 
                                   f"Performance should not degrade cumulatively after undo {i+1} "
                                   f"(ratio: {performance_ratio:.2f})")
            
            # Final performance check
            final_exec_time = self.measure_execution_time(runs=3)
            final_ratio = final_exec_time / baseline_time
            print(f"Final performance ratio after multiple undo operations: {final_ratio:.2f}")
            self.assertLessEqual(final_ratio, 1.10, "Final performance should be within 110% of baseline")
        
        def test_connection_heavy_node_performance(self):
            """Test performance with connection-heavy node (config-input has 6 connections)."""
            print("\n=== Testing Connection-Heavy Node Delete-Undo Performance ===")
            
            baseline_time = self.measure_execution_time(runs=3)
            
            # Delete the node with most connections (config-input)
            target_node = self.get_node_by_title("Password Configuration")
            
            # Count connections before delete
            connections_before = len(self.graph.connections)
            
            delete_command = DeleteNodeCommand(self.graph, target_node)
            success = delete_command.execute()
            self.assertTrue(success, "Delete of connection-heavy node should succeed")
            
            # Measure undo performance for connection-heavy restoration
            undo_time = self.measure_undo_time(delete_command)
            self.assertLess(undo_time, 100, "Connection-heavy undo should complete in under 100ms")
            
            # Verify all connections restored
            connections_after = len(self.graph.connections)
            self.assertEqual(connections_before, connections_after, 
                            "All connections should be restored")
            
            # Validate connection integrity (critical for this test)
            self.assertTrue(self.validate_connection_integrity(), 
                           "Connection integrity critical for connection-heavy node")
            
            # Performance check
            post_undo_time = self.measure_execution_time(runs=3)
            performance_ratio = post_undo_time / baseline_time
            self.assertLessEqual(performance_ratio, 1.10, 
                               f"Connection-heavy node restore should not impact performance "
                               f"(ratio: {performance_ratio:.2f})")
        
        def test_chaos_delete_undo_performance(self):
            """Test random delete-undo operations to detect cumulative performance issues."""
            print("\n=== Testing Chaos Delete-Undo Performance ===")
            
            baseline_time = self.measure_execution_time(runs=3)
            max_degradation = 0.0
            
            # Get nodes that can be safely deleted and restored
            deletable_nodes = [node for node in self.graph.nodes 
                              if hasattr(node, "title") and node.title != "Password Configuration"]
            
            # Perform random delete-undo cycles
            for cycle in range(5):
                print(f"\nChaos cycle {cycle + 1}/5")
                
                # Random node selection
                target_node = random.choice(deletable_nodes)
                print(f"Deleting node: {target_node.title}")
                
                delete_command = DeleteNodeCommand(self.graph, target_node)
                success = delete_command.execute()
                self.assertTrue(success, f"Chaos delete cycle {cycle + 1} should succeed")
                
                # Quick undo
                undo_time = self.measure_undo_time(delete_command)
                self.assertLess(undo_time, 75, f"Chaos undo {cycle + 1} should be fast")
                
                # Validate integrity
                self.assertTrue(self.validate_connection_integrity(), 
                              f"Chaos cycle {cycle + 1} should maintain connection integrity")
                
                # Check for performance degradation
                current_time = self.measure_execution_time(runs=2)
                current_degradation = (current_time / baseline_time) - 1.0
                max_degradation = max(max_degradation, current_degradation)
                
                print(f"Cycle {cycle + 1} performance degradation: {current_degradation:.2%}")
                
                # Should not have cumulative degradation
                self.assertLessEqual(current_degradation, 0.20, 
                                   f"Chaos cycle {cycle + 1} should not cause >20% degradation")
            
            print(f"Maximum performance degradation across all chaos cycles: {max_degradation:.2%}")
            self.assertLessEqual(max_degradation, 0.15, 
                               "Maximum degradation should be under 15% across all chaos cycles")
        
        def test_performance_thresholds_compliance(self):
            """Test that all operations meet performance thresholds."""
            print("\n=== Testing Performance Thresholds Compliance ===")
            
            # Test execution performance threshold
            exec_time = self.measure_execution_time(runs=5)
            self.assertLess(exec_time, 500, "Graph execution should be under 500ms")
            
            # Test delete operation performance  
            target_node = self.get_node_by_title("Password Strength Analyzer")
            delete_command = DeleteNodeCommand(self.graph, target_node)
            
            start_time = time.perf_counter()
            success = delete_command.execute()
            delete_time = (time.perf_counter() - start_time) * 1000
            
            self.assertTrue(success, "Delete should succeed")
            self.assertLess(delete_time, 25, "Delete operation should be under 25ms")
            
            # Test undo operation performance
            undo_time = self.measure_undo_time(delete_command)
            self.assertLess(undo_time, 50, "Undo operation should be under 50ms")
            
            print(f"Performance thresholds: Execution={exec_time:.2f}ms, Delete={delete_time:.2f}ms, Undo={undo_time:.2f}ms")

except ImportError:
    QT_AVAILABLE = False


if __name__ == '__main__':
    unittest.main()
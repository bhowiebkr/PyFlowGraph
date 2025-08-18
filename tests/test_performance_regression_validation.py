#!/usr/bin/env python3
"""
Performance Regression Validation Test

A lightweight validation test to demonstrate the delete-undo performance fix
and ensure the regression test infrastructure is working correctly.
"""

import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication, QTextEdit

from core.node_graph import NodeGraph
from core.node import Node
from core.pin import Pin
from core.connection import Connection
from commands.node_commands import DeleteNodeCommand
from execution.graph_executor import GraphExecutor


class TestPerformanceRegressionValidation(unittest.TestCase):
    """Lightweight validation of delete-undo performance regression fix."""
    
    def setUp(self):
        """Set up minimal test environment."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        self.graph = NodeGraph()
        self.log_widget = QTextEdit()
        
        # Mock venv path for executor
        def mock_venv_path():
            return os.path.join(os.path.dirname(__file__), 'venvs', 'default')
        
        self.executor = GraphExecutor(self.graph, self.log_widget, mock_venv_path)
    
    def create_test_node(self, title: str, pos: tuple = (0, 0)) -> Node:
        """Create a test node with basic setup."""
        node = Node(title)
        node.setPos(*pos)
        node.set_code(f'''
@node_entry
def {title.lower().replace(" ", "_")}() -> str:
    return "{title}_output"
''')
        self.graph.addItem(node)
        self.graph.nodes.append(node)
        return node
    
    def create_test_connection(self, source_node: Node, target_node: Node) -> Connection:
        """Create a connection between two nodes."""
        if not source_node.output_pins or not target_node.input_pins:
            # Create pins if they don't exist
            if not source_node.output_pins:
                output_pin = Pin(source_node, "output", "data", "output")
                source_node.output_pins.append(output_pin)
            if not target_node.input_pins:
                input_pin = Pin(target_node, "input", "data", "input")
                target_node.input_pins.append(input_pin)
        
        connection = Connection(source_node.output_pins[0], target_node.input_pins[0])
        self.graph.addItem(connection)
        self.graph.connections.append(connection)
        
        # Note: Connection constructor automatically adds itself to pin connection lists
        
        return connection
    
    def count_total_pin_connections(self) -> int:
        """Count total connections in all pin connection lists."""
        total = 0
        for node in self.graph.nodes:
            if isinstance(node, Node):
                for pin in node.input_pins + node.output_pins:
                    total += len(pin.connections)
        return total
    
    def measure_mock_execution_time(self, runs: int = 3) -> float:
        """Measure mock execution time for performance comparison."""
        times = []
        
        for _ in range(runs):
            start_time = time.perf_counter()
            
            # Mock the execution by simulating the pin traversal that was slow
            for node in self.graph.nodes:
                if isinstance(node, Node):
                    # Simulate data pin processing (line 94-98 in graph_executor.py)
                    for pin in node.input_pins:
                        if pin.pin_category == "data" and pin.connections:
                            # This is where duplicate connections would cause slowdown
                            for conn in pin.connections:
                                pass  # Simulate processing each connection
                    
                    # Simulate execution pin processing (line 172-177 in graph_executor.py)  
                    for pin in node.output_pins:
                        if pin.pin_category == "execution":
                            for conn in pin.connections:
                                pass  # Simulate processing each connection
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            times.append(elapsed_ms)
        
        return sum(times) / len(times)
    
    def test_duplicate_connection_prevention(self):
        """Test that duplicate connections are prevented during undo."""
        print("\n=== Testing Duplicate Connection Prevention ===")
        
        # Create test graph with connections
        node1 = self.create_test_node("Node1", (0, 0))
        node2 = self.create_test_node("Node2", (200, 0))
        node3 = self.create_test_node("Node3", (400, 0))
        
        conn1 = self.create_test_connection(node1, node2)
        conn2 = self.create_test_connection(node2, node3)
        
        # Verify initial state
        initial_graph_connections = len(self.graph.connections)
        initial_pin_connections = self.count_total_pin_connections()
        
        print(f"Initial state: {initial_graph_connections} graph connections, {initial_pin_connections} pin connections")
        
        # Delete middle node
        delete_command = DeleteNodeCommand(self.graph, node2)
        success = delete_command.execute()
        self.assertTrue(success, "Delete should succeed")
        
        # Verify deletion
        self.assertEqual(len(self.graph.connections), 0, "Connections should be removed with node")
        
        # Undo the deletion
        start_time = time.perf_counter()
        undo_success = delete_command.undo()
        undo_time = (time.perf_counter() - start_time) * 1000
        
        self.assertTrue(undo_success, "Undo should succeed")
        print(f"Undo operation took: {undo_time:.2f} ms")
        
        # Verify restoration without duplicates
        final_graph_connections = len(self.graph.connections)
        final_pin_connections = self.count_total_pin_connections()
        
        print(f"After undo: {final_graph_connections} graph connections, {final_pin_connections} pin connections")
        
        # Should be back to original counts
        self.assertEqual(final_graph_connections, initial_graph_connections, 
                        "Graph connections should be restored exactly")
        self.assertEqual(final_pin_connections, initial_pin_connections, 
                        "Pin connections should be restored without duplicates")
        
        # Verify no duplicate connections in individual pins
        for node in self.graph.nodes:
            if isinstance(node, Node):
                for pin in node.input_pins + node.output_pins:
                    unique_connections = list(set(pin.connections))
                    if len(pin.connections) != len(unique_connections):
                        print(f"DUPLICATE DETECTED: Pin {node.title}.{pin.name} has {len(pin.connections)} connections but only {len(unique_connections)} unique")
                        print(f"  Connections: {[id(c) for c in pin.connections]}")
                        print(f"  Unique IDs: {[id(c) for c in unique_connections]}")
                    self.assertEqual(len(pin.connections), len(unique_connections),
                                   f"Pin {node.title}.{pin.name} should not have duplicate connections")
    
    def test_execution_performance_stability(self):
        """Test that execution performance remains stable after delete-undo."""
        print("\n=== Testing Execution Performance Stability ===")
        
        # Create more complex graph to simulate password generator
        nodes = []
        for i in range(4):
            node = self.create_test_node(f"Node{i}", (i * 200, 0))
            nodes.append(node)
        
        # Create sequential connections (like password generator flow)
        connections = []
        for i in range(len(nodes) - 1):
            conn = self.create_test_connection(nodes[i], nodes[i + 1])
            connections.append(conn)
        
        # Measure baseline performance
        baseline_time = self.measure_mock_execution_time(runs=5)
        print(f"Baseline execution time: {baseline_time:.3f} ms")
        
        # Perform delete-undo cycle on middle node
        target_node = nodes[1]  # Middle node with connections
        delete_command = DeleteNodeCommand(self.graph, target_node)
        
        # Delete
        delete_command.execute()
        
        # Undo
        delete_command.undo()
        
        # Measure post-undo performance
        post_undo_time = self.measure_mock_execution_time(runs=5)
        print(f"Post-undo execution time: {post_undo_time:.3f} ms")
        
        # Calculate performance ratio
        if baseline_time > 0:
            performance_ratio = post_undo_time / baseline_time
            print(f"Performance ratio (post-undo / baseline): {performance_ratio:.3f}")
            
            # Should be within reasonable bounds (allowing for measurement variance)
            self.assertLess(performance_ratio, 2.0, 
                           "Performance should not significantly degrade after undo")
        
        # Verify connection integrity maintained
        self.assertEqual(len(self.graph.connections), len(connections), 
                        "All connections should be restored")
    
    def test_multiple_delete_undo_cycles(self):
        """Test that multiple delete-undo cycles don't cause cumulative performance issues."""
        print("\n=== Testing Multiple Delete-Undo Cycles ===")
        
        # Create test graph
        nodes = []
        for i in range(3):
            node = self.create_test_node(f"TestNode{i}", (i * 150, 0))
            nodes.append(node)
        
        # Create connections
        for i in range(len(nodes) - 1):
            self.create_test_connection(nodes[i], nodes[i + 1])
        
        baseline_time = self.measure_mock_execution_time(runs=3)
        max_degradation = 0.0
        
        # Perform multiple delete-undo cycles
        for cycle in range(3):
            print(f"Cycle {cycle + 1}/3")
            
            target_node = nodes[1]  # Always use middle node
            delete_command = DeleteNodeCommand(self.graph, target_node)
            
            # Delete and undo
            delete_command.execute()
            delete_command.undo()
            
            # Check performance
            current_time = self.measure_mock_execution_time(runs=2)
            if baseline_time > 0:
                degradation = (current_time / baseline_time) - 1.0
                max_degradation = max(max_degradation, degradation)
                print(f"Cycle {cycle + 1} performance change: {degradation:.1%}")
        
        print(f"Maximum performance degradation: {max_degradation:.1%}")
        
        # Should not have significant cumulative degradation
        self.assertLess(max_degradation, 0.50, 
                       "Multiple cycles should not cause >50% performance degradation")
    
    def test_performance_regression_thresholds(self):
        """Test that performance meets expected thresholds."""
        print("\n=== Testing Performance Regression Thresholds ===")
        
        # Create single node for timing tests
        node = self.create_test_node("TestNode", (0, 0))
        
        # Test delete operation speed
        delete_command = DeleteNodeCommand(self.graph, node)
        
        start_time = time.perf_counter()
        success = delete_command.execute()
        delete_time = (time.perf_counter() - start_time) * 1000
        
        self.assertTrue(success, "Delete should succeed")
        self.assertLess(delete_time, 50, f"Delete should be under 50ms (was {delete_time:.2f}ms)")
        
        # Test undo operation speed  
        start_time = time.perf_counter()
        undo_success = delete_command.undo()
        undo_time = (time.perf_counter() - start_time) * 1000
        
        self.assertTrue(undo_success, "Undo should succeed")
        self.assertLess(undo_time, 100, f"Undo should be under 100ms (was {undo_time:.2f}ms)")
        
        print(f"Performance thresholds: Delete={delete_time:.2f}ms, Undo={undo_time:.2f}ms")


if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python3
"""
Performance Fix Demonstration Test

This test demonstrates that the delete-undo performance regression bug has been fixed.
The bug was caused by duplicate connections in pin connection lists after undo operations,
leading to exponential execution slowdown.

Before Fix: Each delete-undo cycle would add duplicate connections, causing execution
to process the same downstream nodes multiple times.

After Fix: Connection restoration properly handles duplicates, maintaining consistent
execution performance regardless of delete-undo operations.
"""

import unittest
import sys
import os
import time
from unittest.mock import patch

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication, QTextEdit

from core.node_graph import NodeGraph
from core.node import Node
from core.pin import Pin
from core.connection import Connection
from commands.node_commands import DeleteNodeCommand


class TestPerformanceFixDemonstration(unittest.TestCase):
    """Demonstrates the delete-undo performance fix is working."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        self.graph = NodeGraph()
    
    def create_password_generator_simulation(self):
        """Create a simulation of the password generator workflow structure."""
        # Create 4 nodes like password generator
        config_node = Node("Config Node")
        generator_node = Node("Generator Node") 
        analyzer_node = Node("Analyzer Node")
        output_node = Node("Output Node")
        
        config_node.setPos(0, 0)
        generator_node.setPos(200, 0)
        analyzer_node.setPos(400, 0)
        output_node.setPos(600, 0)
        
        # Add nodes to graph
        for node in [config_node, generator_node, analyzer_node, output_node]:
            self.graph.addItem(node)
            self.graph.nodes.append(node)
            
            # Create pins like password generator
            exec_in = Pin(node, "exec_in", "execution", "input")
            exec_out = Pin(node, "exec_out", "execution", "output") 
            data_in = Pin(node, "data_in", "data", "input")
            data_out = Pin(node, "data_out", "data", "output")
            
            node.input_pins = [exec_in, data_in]
            node.output_pins = [exec_out, data_out]
        
        # Create connections like password generator (11 total)
        connections = []
        
        # Execution flow connections
        for i in range(len(self.graph.nodes) - 1):
            exec_conn = Connection(
                self.graph.nodes[i].output_pins[0],  # exec_out
                self.graph.nodes[i + 1].input_pins[0]  # exec_in
            )
            self.graph.addItem(exec_conn)
            self.graph.connections.append(exec_conn)
            connections.append(exec_conn)
        
        # Data flow connections (multiple from config to other nodes)
        config = self.graph.nodes[0]
        for target in self.graph.nodes[1:]:
            data_conn = Connection(
                config.output_pins[1],  # data_out
                target.input_pins[1]    # data_in
            )
            self.graph.addItem(data_conn)
            self.graph.connections.append(data_conn)
            connections.append(data_conn)
        
        return connections
    
    def simulate_execution_traversal(self) -> int:
        """
        Simulate the execution traversal that was slow due to duplicate connections.
        Returns the number of connection traversals (should be constant).
        """
        traversal_count = 0
        
        # Simulate the execution flow from graph_executor.py
        for node in self.graph.nodes:
            if isinstance(node, Node):
                # Simulate data pin processing (line 94-98 in graph_executor.py)
                for pin in node.input_pins:
                    if pin.pin_category == "data":
                        for conn in pin.connections:
                            traversal_count += 1
                
                # Simulate execution pin processing (line 172-177 in graph_executor.py)
                for pin in node.output_pins:
                    if pin.pin_category == "execution":
                        for conn in pin.connections:
                            traversal_count += 1
        
        return traversal_count
    
    def test_performance_fix_demonstration(self):
        """Demonstrate that performance remains stable after delete-undo cycles."""
        print("\n=== Performance Fix Demonstration ===")
        
        # Create password generator simulation
        connections = self.create_password_generator_simulation()
        initial_connection_count = len(self.graph.connections)
        
        print(f"Created simulation with {len(self.graph.nodes)} nodes and {initial_connection_count} connections")
        
        # Measure baseline execution complexity
        baseline_traversals = self.simulate_execution_traversal()
        print(f"Baseline connection traversals: {baseline_traversals}")
        
        # Perform multiple delete-undo cycles on different nodes
        test_results = []
        
        for cycle in range(3):
            print(f"\n--- Cycle {cycle + 1} ---")
            
            # Target different nodes each cycle
            target_node = self.graph.nodes[1 + cycle]  # Skip config node
            print(f"Deleting node: {target_node.title}")
            
            # Delete node
            delete_command = DeleteNodeCommand(self.graph, target_node)
            delete_success = delete_command.execute()
            self.assertTrue(delete_success, f"Delete should succeed in cycle {cycle + 1}")
            
            connections_after_delete = len(self.graph.connections)
            print(f"Connections after delete: {connections_after_delete}")
            
            # Undo deletion
            start_time = time.perf_counter()
            undo_success = delete_command.undo()
            undo_time = (time.perf_counter() - start_time) * 1000
            
            self.assertTrue(undo_success, f"Undo should succeed in cycle {cycle + 1}")
            print(f"Undo operation took: {undo_time:.2f} ms")
            
            # Verify connection count restored
            connections_after_undo = len(self.graph.connections)
            print(f"Connections after undo: {connections_after_undo}")
            
            # Critical test: Check execution traversal count
            current_traversals = self.simulate_execution_traversal()
            print(f"Connection traversals after undo: {current_traversals}")
            
            # Performance regression check - should be same as baseline
            traversal_ratio = current_traversals / baseline_traversals if baseline_traversals > 0 else 1.0
            print(f"Traversal ratio (current/baseline): {traversal_ratio:.2f}")
            
            test_results.append({
                'cycle': cycle + 1,
                'undo_time': undo_time,
                'traversal_ratio': traversal_ratio,
                'connections_restored': connections_after_undo == initial_connection_count
            })
            
            # Should not have exponential growth in traversals
            self.assertLessEqual(traversal_ratio, 1.1, 
                               f"Cycle {cycle + 1}: Traversal count should not increase significantly "
                               f"(ratio: {traversal_ratio:.2f})")
            
            # Should restore exact connection count
            self.assertEqual(connections_after_undo, initial_connection_count,
                           f"Cycle {cycle + 1}: Should restore all connections")
        
        # Summary
        print(f"\n=== Test Results Summary ===")
        max_traversal_ratio = max(result['traversal_ratio'] for result in test_results)
        avg_undo_time = sum(result['undo_time'] for result in test_results) / len(test_results)
        all_connections_restored = all(result['connections_restored'] for result in test_results)
        
        print(f"Maximum traversal ratio across all cycles: {max_traversal_ratio:.2f}")
        print(f"Average undo time: {avg_undo_time:.2f} ms")
        print(f"All connections restored correctly: {all_connections_restored}")
        
        # Final assertions for overall performance
        self.assertLessEqual(max_traversal_ratio, 1.1, 
                           "No cycle should cause >10% increase in traversals")
        self.assertLess(avg_undo_time, 10, 
                       "Average undo time should be under 10ms")
        self.assertTrue(all_connections_restored, 
                       "All cycles should restore connections correctly")
        
        print("\nPERFORMANCE FIX VERIFICATION: PASSED")
        print("Delete-undo operations maintain consistent execution performance")
    
    def test_connection_integrity_validation(self):
        """Validate that connections are properly managed without duplicates."""
        print("\n=== Connection Integrity Validation ===")
        
        # Create simple test case
        node1 = Node("Node1")
        node2 = Node("Node2")
        
        for node in [node1, node2]:
            self.graph.addItem(node)
            self.graph.nodes.append(node)
            
            out_pin = Pin(node, "out", "data", "output")
            in_pin = Pin(node, "in", "data", "input")
            node.output_pins = [out_pin]
            node.input_pins = [in_pin]
        
        # Create connection
        connection = Connection(node1.output_pins[0], node2.input_pins[0])
        self.graph.addItem(connection)
        self.graph.connections.append(connection)
        
        # Verify initial state
        self.assertEqual(len(node1.output_pins[0].connections), 1)
        self.assertEqual(len(node2.input_pins[0].connections), 1)
        
        # Delete and undo
        delete_cmd = DeleteNodeCommand(self.graph, node1)
        delete_cmd.execute()
        delete_cmd.undo()
        
        # Verify no duplicates after undo
        output_pin_connections = len(node1.output_pins[0].connections)
        input_pin_connections = len(node2.input_pins[0].connections)
        
        print(f"Output pin connections after undo: {output_pin_connections}")
        print(f"Input pin connections after undo: {input_pin_connections}")
        
        # Should have exactly 1 connection each, no duplicates
        self.assertEqual(output_pin_connections, 1, "Output pin should have exactly 1 connection")
        self.assertEqual(input_pin_connections, 1, "Input pin should have exactly 1 connection")
        
        # Verify connection uniqueness
        unique_out_connections = list(set(node1.output_pins[0].connections))
        unique_in_connections = list(set(node2.input_pins[0].connections))
        
        self.assertEqual(len(node1.output_pins[0].connections), len(unique_out_connections),
                        "Output pin should not have duplicate connections")
        self.assertEqual(len(node2.input_pins[0].connections), len(unique_in_connections),
                        "Input pin should not have duplicate connections")
        
        print("CONNECTION INTEGRITY VALIDATION: PASSED")
        print("No duplicate connections detected after delete-undo operations")


if __name__ == '__main__':
    unittest.main()
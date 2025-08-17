"""
Comprehensive tests for the command pattern implementation in PyFlowGraph.

Tests cover command execution, undo/redo functionality, memory management,
and performance requirements as specified in the technical architecture.
"""

import unittest
import time
import sys
import os

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF

from src.commands import (
    CommandBase, CompositeCommand, CommandHistory,
    CreateNodeCommand, DeleteNodeCommand, MoveNodeCommand,
    PropertyChangeCommand, CodeChangeCommand,
    CreateConnectionCommand, DeleteConnectionCommand
)
from src.core.node_graph import NodeGraph
from src.core.node import Node


class MockCommand(CommandBase):
    """Mock command for testing base functionality."""
    
    def __init__(self, description="Mock Command", should_fail=False):
        super().__init__(description)
        self.should_fail = should_fail
        self.execute_count = 0
        self.undo_count = 0
    
    def execute(self):
        self.execute_count += 1
        return not self.should_fail
    
    def undo(self):
        self.undo_count += 1
        return not self.should_fail


class TestCommandBase(unittest.TestCase):
    """Test the CommandBase abstract class and basic functionality."""
    
    def test_command_creation(self):
        """Test basic command creation and properties."""
        cmd = MockCommand("Test Command")
        self.assertEqual(cmd.get_description(), "Test Command")
        self.assertFalse(cmd.is_executed())
        self.assertFalse(cmd.is_undone())
    
    def test_command_execution(self):
        """Test command execution tracking."""
        cmd = MockCommand()
        self.assertTrue(cmd.execute())
        cmd._mark_executed()
        self.assertTrue(cmd.is_executed())
        self.assertFalse(cmd.is_undone())
    
    def test_command_undo(self):
        """Test command undo tracking."""
        cmd = MockCommand()
        cmd.execute()
        cmd._mark_executed()
        self.assertTrue(cmd.undo())
        cmd._mark_undone()
        self.assertFalse(cmd.is_executed())
        self.assertTrue(cmd.is_undone())
    
    def test_memory_usage_estimation(self):
        """Test memory usage estimation."""
        cmd = MockCommand()
        memory_usage = cmd.get_memory_usage()
        self.assertIsInstance(memory_usage, int)
        self.assertGreater(memory_usage, 0)


class TestCompositeCommand(unittest.TestCase):
    """Test composite command functionality."""
    
    def test_composite_execution(self):
        """Test executing multiple commands as a group."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        cmd3 = MockCommand("Command 3")
        
        composite = CompositeCommand("Composite", [cmd1, cmd2, cmd3])
        self.assertTrue(composite.execute())
        
        # All commands should be executed
        self.assertEqual(cmd1.execute_count, 1)
        self.assertEqual(cmd2.execute_count, 1)
        self.assertEqual(cmd3.execute_count, 1)
    
    def test_composite_rollback_on_failure(self):
        """Test that composite commands rollback on failure."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2", should_fail=True)  # This will fail
        cmd3 = MockCommand("Command 3")
        
        composite = CompositeCommand("Composite", [cmd1, cmd2, cmd3])
        self.assertFalse(composite.execute())
        
        # First command should be executed then undone
        self.assertEqual(cmd1.execute_count, 1)
        self.assertEqual(cmd1.undo_count, 1)
        
        # Second command fails, third never executed
        self.assertEqual(cmd2.execute_count, 1)
        self.assertEqual(cmd3.execute_count, 0)
    
    def test_composite_undo(self):
        """Test undoing composite commands."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        
        composite = CompositeCommand("Composite", [cmd1, cmd2])
        composite.execute()
        self.assertTrue(composite.undo())
        
        # Commands should be undone in reverse order
        self.assertEqual(cmd1.undo_count, 1)
        self.assertEqual(cmd2.undo_count, 1)


class TestCommandHistory(unittest.TestCase):
    """Test command history management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.history = CommandHistory(max_depth=5)  # Small depth for testing
    
    def test_command_execution(self):
        """Test basic command execution through history."""
        cmd = MockCommand("Test Command")
        success = self.history.execute_command(cmd)
        
        self.assertTrue(success)
        self.assertTrue(self.history.can_undo())
        self.assertFalse(self.history.can_redo())
        self.assertEqual(self.history.get_command_count(), 1)
    
    def test_undo_redo_cycle(self):
        """Test complete undo/redo cycle."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        
        # Execute commands
        self.history.execute_command(cmd1)
        self.history.execute_command(cmd2)
        
        # Should be able to undo
        self.assertTrue(self.history.can_undo())
        self.assertEqual(self.history.get_undo_description(), "Command 2")
        
        # Undo last command
        undone = self.history.undo()
        self.assertEqual(undone, "Command 2")
        self.assertEqual(cmd2.undo_count, 1)
        
        # Should be able to redo
        self.assertTrue(self.history.can_redo())
        self.assertEqual(self.history.get_redo_description(), "Command 2")
        
        # Redo command
        redone = self.history.redo()
        self.assertEqual(redone, "Command 2")
        self.assertEqual(cmd2.execute_count, 2)  # Executed twice
    
    def test_depth_limit_enforcement(self):
        """Test that command history respects depth limits."""
        # Add more commands than max_depth
        for i in range(7):
            cmd = MockCommand(f"Command {i}")
            self.history.execute_command(cmd)
        
        # Should only keep max_depth commands
        self.assertEqual(self.history.get_command_count(), 5)
    
    def test_memory_limit_enforcement(self):
        """Test memory limit enforcement (NFR3 requirement)."""
        # Create history with very small memory limit for testing
        history = CommandHistory()
        history._memory_limit = 2048  # 2KB limit
        
        # Add commands that exceed memory limit
        for i in range(10):
            cmd = MockCommand(f"Large Command {i}")
            # Override memory usage to be large
            cmd.get_memory_usage = lambda: 500  # 500 bytes each
            history.execute_command(cmd)
        
        # Should enforce memory limit
        self.assertLessEqual(history.get_memory_usage(), history._memory_limit)
    
    def test_performance_monitoring(self):
        """Test performance monitoring (NFR1 requirement)."""
        # This is a basic test - real performance testing would need actual timing
        cmd = MockCommand("Fast Command")
        start_time = time.perf_counter()
        self.history.execute_command(cmd)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # For mock commands, this should be very fast
        self.assertLess(elapsed_ms, 100)  # Should be under 100ms requirement


class TestNodeCommands(unittest.TestCase):
    """Test node-specific commands."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.node_graph = NodeGraph()
        self.test_position = QPointF(100, 100)
    
    def tearDown(self):
        """Clean up after tests."""
        # Clear the graph
        self.node_graph.clear_graph()
    
    def test_create_node_command(self):
        """Test node creation command."""
        initial_count = len(self.node_graph.nodes)
        
        cmd = CreateNodeCommand(self.node_graph, "TestNode", self.test_position)
        success = cmd.execute()
        
        self.assertTrue(success)
        self.assertIsNotNone(cmd.created_node)
        self.assertEqual(len(self.node_graph.nodes), initial_count + 1)
        self.assertEqual(cmd.created_node.title, "TestNode")
        self.assertEqual(cmd.created_node.pos(), self.test_position)
    
    def test_create_node_undo(self):
        """Test undoing node creation."""
        cmd = CreateNodeCommand(self.node_graph, "TestNode", self.test_position)
        cmd.execute()
        initial_count = len(self.node_graph.nodes)
        
        success = cmd.undo()
        
        self.assertTrue(success)
        self.assertEqual(len(self.node_graph.nodes), initial_count - 1)
    
    def test_delete_node_command(self):
        """Test node deletion command."""
        # Create a node first
        node = Node("TestNode")
        node.setPos(self.test_position)
        self.node_graph.addItem(node)
        self.node_graph.nodes.append(node)
        initial_count = len(self.node_graph.nodes)
        
        cmd = DeleteNodeCommand(self.node_graph, node)
        success = cmd.execute()
        
        self.assertTrue(success)
        self.assertEqual(len(self.node_graph.nodes), initial_count - 1)
        self.assertNotIn(node, self.node_graph.nodes)
    
    def test_delete_node_undo(self):
        """Test undoing node deletion."""
        # Create and delete a node
        node = Node("TestNode")
        node.setPos(self.test_position)
        self.node_graph.addItem(node)
        self.node_graph.nodes.append(node)
        
        cmd = DeleteNodeCommand(self.node_graph, node)
        cmd.execute()
        initial_count = len(self.node_graph.nodes)
        
        success = cmd.undo()
        
        self.assertTrue(success)
        self.assertEqual(len(self.node_graph.nodes), initial_count + 1)
    
    def test_move_node_command(self):
        """Test node movement command."""
        node = Node("TestNode")
        old_pos = QPointF(50, 50)
        new_pos = QPointF(150, 150)
        node.setPos(old_pos)
        
        cmd = MoveNodeCommand(self.node_graph, node, old_pos, new_pos)
        success = cmd.execute()
        
        self.assertTrue(success)
        self.assertEqual(node.pos(), new_pos)
        
        # Test undo
        success = cmd.undo()
        self.assertTrue(success)
        self.assertEqual(node.pos(), old_pos)
    
    def test_move_command_merging(self):
        """Test that move commands can be merged."""
        node = Node("TestNode")
        old_pos = QPointF(0, 0)
        mid_pos = QPointF(50, 50)
        new_pos = QPointF(100, 100)
        
        cmd1 = MoveNodeCommand(self.node_graph, node, old_pos, mid_pos)
        cmd2 = MoveNodeCommand(self.node_graph, node, mid_pos, new_pos)
        
        # Commands for same node should be mergeable
        self.assertTrue(cmd1.can_merge_with(cmd2))
        
        merged = cmd1.merge_with(cmd2)
        self.assertIsNotNone(merged)
        self.assertEqual(merged.old_position, old_pos)
        self.assertEqual(merged.new_position, new_pos)
    
    def test_property_change_command(self):
        """Test property change command."""
        node = Node("TestNode")
        old_title = node.title
        new_title = "NewTitle"
        
        cmd = PropertyChangeCommand(self.node_graph, node, 'title', old_title, new_title)
        success = cmd.execute()
        
        self.assertTrue(success)
        self.assertEqual(node.title, new_title)
        
        # Test undo
        success = cmd.undo()
        self.assertTrue(success)
        self.assertEqual(node.title, old_title)
    
    def test_code_change_command(self):
        """Test code change command."""
        node = Node("TestNode")
        old_code = "def old_function(): pass"
        new_code = "def new_function(): return True"
        
        node.code = old_code
        
        cmd = CodeChangeCommand(self.node_graph, node, old_code, new_code)
        success = cmd.execute()
        
        self.assertTrue(success)
        self.assertEqual(node.code, new_code)
        
        # Test undo
        success = cmd.undo()
        self.assertTrue(success)
        self.assertEqual(node.code, old_code)


class TestNodeGraphIntegration(unittest.TestCase):
    """Test command integration with NodeGraph."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.node_graph = NodeGraph()
    
    def tearDown(self):
        """Clean up after tests."""
        self.node_graph.clear_graph()
    
    def test_node_graph_command_execution(self):
        """Test that NodeGraph properly executes commands."""
        # Test node creation through NodeGraph
        node = self.node_graph.create_node("TestNode", (100, 100))
        self.assertIsNotNone(node)
        self.assertTrue(self.node_graph.can_undo())
        
        # Test undo
        success = self.node_graph.undo_last_command()
        self.assertTrue(success)
        self.assertNotIn(node, self.node_graph.nodes)
        
        # Test redo
        success = self.node_graph.redo_last_command()
        self.assertTrue(success)
        self.assertTrue(self.node_graph.can_undo())
    
    def test_keyboard_shortcuts_integration(self):
        """Test that keyboard shortcuts work properly."""
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import Qt, QEvent
        
        # Create a node first
        node = self.node_graph.create_node("TestNode", (100, 100))
        self.assertTrue(self.node_graph.can_undo())
        
        # Simulate Ctrl+Z (undo)
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
        self.node_graph.keyPressEvent(event)
        
        # Node should be undone
        self.assertNotIn(node, self.node_graph.nodes)
        self.assertTrue(self.node_graph.can_redo())
        
        # Simulate Ctrl+Y (redo)
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Y, Qt.ControlModifier)
        self.node_graph.keyPressEvent(event)
        
        # Node should be restored
        self.assertTrue(self.node_graph.can_undo())


class TestPerformanceRequirements(unittest.TestCase):
    """Test that performance requirements (NFR1-NFR3) are met."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.node_graph = NodeGraph()
    
    def tearDown(self):
        """Clean up after tests."""
        self.node_graph.clear_graph()
    
    def test_individual_operation_performance(self):
        """Test NFR1: Individual operations complete within 100ms."""
        # Test node creation performance
        start_time = time.perf_counter()
        node = self.node_graph.create_node("TestNode", (100, 100))
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        self.assertIsNotNone(node)
        self.assertLess(elapsed_ms, 100, f"Node creation took {elapsed_ms:.1f}ms, exceeds 100ms limit")
        
        # Test node deletion performance
        start_time = time.perf_counter()
        success = self.node_graph.remove_node(node)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        self.assertTrue(success)
        self.assertLess(elapsed_ms, 100, f"Node deletion took {elapsed_ms:.1f}ms, exceeds 100ms limit")
    
    def test_undo_redo_performance(self):
        """Test that undo/redo operations are fast."""
        # Create some nodes
        nodes = []
        for i in range(5):
            node = self.node_graph.create_node(f"Node{i}", (i*50, i*50))
            nodes.append(node)
        
        # Test undo performance
        start_time = time.perf_counter()
        success = self.node_graph.undo_last_command()
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        self.assertTrue(success)
        self.assertLess(elapsed_ms, 100, f"Undo took {elapsed_ms:.1f}ms, exceeds 100ms limit")
        
        # Test redo performance
        start_time = time.perf_counter()
        success = self.node_graph.redo_last_command()
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        self.assertTrue(success)
        self.assertLess(elapsed_ms, 100, f"Redo took {elapsed_ms:.1f}ms, exceeds 100ms limit")
    
    def test_memory_usage_limits(self):
        """Test NFR3: Memory usage stays under 50MB regardless of operation count."""
        # Create many operations to test memory limits
        for i in range(100):
            node = self.node_graph.create_node(f"Node{i}", (i*10, i*10))
            if i % 2 == 0:  # Delete every other node to create more commands
                self.node_graph.remove_node(node)
        
        # Check memory usage
        memory_usage = self.node_graph.command_history.get_memory_usage()
        memory_limit = 50 * 1024 * 1024  # 50MB
        
        self.assertLessEqual(memory_usage, memory_limit, 
                           f"Memory usage {memory_usage} bytes exceeds 50MB limit")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
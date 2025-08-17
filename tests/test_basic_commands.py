"""
Basic tests for the command pattern implementation in PyFlowGraph.

Focuses on testing the core command infrastructure and basic functionality.
"""

import unittest
import time
import sys
import os

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.commands import CommandBase, CompositeCommand, CommandHistory


class MockCommand(CommandBase):
    """Mock command for testing base functionality."""
    
    def __init__(self, description="Mock Command", should_fail=False):
        super().__init__(description)
        self.should_fail = should_fail
        self.execute_count = 0
        self.undo_count = 0
    
    def execute(self):
        self.execute_count += 1
        if not self.should_fail:
            self._mark_executed()
        return not self.should_fail
    
    def undo(self):
        self.undo_count += 1
        if not self.should_fail:
            self._mark_undone()
        return not self.should_fail


class TestCommandInfrastructure(unittest.TestCase):
    """Test the core command pattern infrastructure."""
    
    def test_basic_command_functionality(self):
        """Test basic command creation and execution."""
        cmd = MockCommand("Test Command")
        
        # Test initial state
        self.assertEqual(cmd.get_description(), "Test Command")
        self.assertFalse(cmd.is_executed())
        self.assertFalse(cmd.is_undone())
        
        # Test execution
        success = cmd.execute()
        self.assertTrue(success)
        self.assertTrue(cmd.is_executed())
        self.assertEqual(cmd.execute_count, 1)
        
        # Test undo
        success = cmd.undo()
        self.assertTrue(success)
        self.assertTrue(cmd.is_undone())
        self.assertEqual(cmd.undo_count, 1)
    
    def test_command_history_basic_operations(self):
        """Test basic command history operations."""
        history = CommandHistory(max_depth=5)
        
        # Test initial state
        self.assertFalse(history.can_undo())
        self.assertFalse(history.can_redo())
        self.assertEqual(history.get_command_count(), 0)
        
        # Execute a command
        cmd = MockCommand("Test Command")
        success = history.execute_command(cmd)
        
        self.assertTrue(success)
        self.assertTrue(history.can_undo())
        self.assertFalse(history.can_redo())
        self.assertEqual(history.get_command_count(), 1)
        
        # Test undo
        undone_desc = history.undo()
        self.assertEqual(undone_desc, "Test Command")
        self.assertFalse(history.can_undo())
        self.assertTrue(history.can_redo())
        
        # Test redo
        redone_desc = history.redo()
        self.assertEqual(redone_desc, "Test Command")
        self.assertTrue(history.can_undo())
        self.assertFalse(history.can_redo())
    
    def test_composite_command_execution(self):
        """Test composite command functionality."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2")
        cmd3 = MockCommand("Command 3")
        
        composite = CompositeCommand("Composite Operation", [cmd1, cmd2, cmd3])
        success = composite.execute()
        
        self.assertTrue(success)
        self.assertEqual(cmd1.execute_count, 1)
        self.assertEqual(cmd2.execute_count, 1)
        self.assertEqual(cmd3.execute_count, 1)
        
        # Test composite undo
        success = composite.undo()
        self.assertTrue(success)
        self.assertEqual(cmd1.undo_count, 1)
        self.assertEqual(cmd2.undo_count, 1)
        self.assertEqual(cmd3.undo_count, 1)
    
    def test_composite_command_rollback(self):
        """Test that composite commands rollback on failure."""
        cmd1 = MockCommand("Command 1")
        cmd2 = MockCommand("Command 2", should_fail=True)  # This will fail
        cmd3 = MockCommand("Command 3")
        
        composite = CompositeCommand("Failing Composite", [cmd1, cmd2, cmd3])
        success = composite.execute()
        
        self.assertFalse(success)
        # First command should be executed then undone during rollback
        self.assertEqual(cmd1.execute_count, 1)
        self.assertEqual(cmd1.undo_count, 1)
        # Second command should fail
        self.assertEqual(cmd2.execute_count, 1)
        # Third command should never be executed
        self.assertEqual(cmd3.execute_count, 0)
    
    def test_command_history_depth_limits(self):
        """Test that command history respects depth limits."""
        history = CommandHistory(max_depth=3)
        
        # Add more commands than the limit
        commands = []
        for i in range(5):
            cmd = MockCommand(f"Command {i}")
            commands.append(cmd)
            history.execute_command(cmd)
        
        # Should only keep the last 3 commands
        self.assertEqual(history.get_command_count(), 3)
        
        # Should be able to undo the last 3 commands
        for i in range(3):
            self.assertTrue(history.can_undo())
            history.undo()
        
        # Should not be able to undo further
        self.assertFalse(history.can_undo())
    
    def test_command_history_memory_monitoring(self):
        """Test basic memory monitoring functionality."""
        history = CommandHistory()
        
        # Add a command and check memory tracking
        cmd = MockCommand("Memory Test")
        history.execute_command(cmd)
        
        memory_usage = history.get_memory_usage()
        self.assertGreater(memory_usage, 0)
        self.assertIsInstance(memory_usage, int)
        
        # Memory should be released when history is cleared
        history.clear()
        self.assertEqual(history.get_memory_usage(), 0)
        self.assertEqual(history.get_command_count(), 0)
    
    def test_performance_basic(self):
        """Test basic performance characteristics."""
        history = CommandHistory()
        
        # Test that individual commands execute quickly
        start_time = time.perf_counter()
        cmd = MockCommand("Performance Test")
        history.execute_command(cmd)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Mock commands should be very fast
        self.assertLess(elapsed_ms, 50)  # Well under 100ms requirement
        
        # Test undo performance
        start_time = time.perf_counter()
        history.undo()
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        self.assertLess(elapsed_ms, 50)  # Well under 100ms requirement
    
    def test_command_descriptions_and_ui_feedback(self):
        """Test command descriptions for UI feedback."""
        history = CommandHistory()
        
        cmd1 = MockCommand("First Operation")
        cmd2 = MockCommand("Second Operation")
        
        history.execute_command(cmd1)
        history.execute_command(cmd2)
        
        # Test undo description
        self.assertEqual(history.get_undo_description(), "Second Operation")
        
        # Undo and test redo description
        history.undo()
        self.assertEqual(history.get_redo_description(), "Second Operation")
        self.assertEqual(history.get_undo_description(), "First Operation")
        
        # Test history display
        history_list = history.get_history()
        self.assertIsInstance(history_list, list)
        self.assertGreater(len(history_list), 0)


if __name__ == '__main__':
    print("Running basic command system tests...")
    unittest.main(verbosity=2)
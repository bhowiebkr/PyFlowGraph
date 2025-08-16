"""
Command history manager for PyFlowGraph undo/redo system.

Manages command execution history with memory constraints and provides
undo/redo functionality with performance monitoring.
"""

import time
import logging
from typing import List, Optional
from .command_base import CommandBase

logger = logging.getLogger(__name__)


class CommandHistory:
    """Manages command execution history and undo/redo operations."""
    
    def __init__(self, max_depth: int = 50):
        """
        Initialize command history.
        
        Args:
            max_depth: Maximum number of commands to keep in history
        """
        self.commands: List[CommandBase] = []
        self.current_index: int = -1
        self.max_depth = max_depth
        self._memory_usage = 0
        self._memory_limit = 50 * 1024 * 1024  # 50MB as per NFR3
        self._performance_monitor = PerformanceMonitor()
    
    def execute_command(self, command: CommandBase) -> bool:
        """
        Execute a command and add to history.
        
        Args:
            command: Command to execute
            
        Returns:
            True if successful, False otherwise
        """
        # Performance monitoring for NFR1
        start_time = time.perf_counter()
        
        try:
            print(f"\n=== COMMAND HISTORY EXECUTE START ===")
            print(f"DEBUG: Executing command: {command.get_description()}")
            print(f"DEBUG: Command type: {type(command).__name__}")
            print(f"DEBUG: Current history size: {len(self.commands)}")
            print(f"DEBUG: Current index: {self.current_index}")
            
            # Execute the command
            print(f"DEBUG: Calling command.execute()...")
            result = command.execute()
            print(f"DEBUG: Command.execute() returned: {result}")
            
            if not result:
                print(f"DEBUG: Command execution failed, not adding to history")
                return False
            
            command._mark_executed()
            print(f"DEBUG: Command marked as executed")
            
            # Remove any commands ahead of current position (redo history)
            if self.current_index < len(self.commands) - 1:
                removed_commands = self.commands[self.current_index + 1:]
                for cmd in removed_commands:
                    self._memory_usage -= cmd.get_memory_usage()
                self.commands = self.commands[:self.current_index + 1]
                print(f"DEBUG: Removed {len(removed_commands)} commands from redo history")
            
            # Add command to history
            self.commands.append(command)
            self.current_index += 1
            self._memory_usage += command.get_memory_usage()
            
            print(f"DEBUG: Added command to history at index {self.current_index}")
            print(f"DEBUG: History size now: {len(self.commands)}")
            
            # Maintain depth and memory limits
            self._enforce_limits()
            
            # Performance check
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._performance_monitor.record_execution(command, elapsed_ms)
            
            if elapsed_ms > 100:  # NFR1 requirement
                logger.warning(
                    f"Command '{command.get_description()}' exceeded 100ms: "
                    f"{elapsed_ms:.1f}ms"
                )
            
            print(f"DEBUG: Command execution completed successfully in {elapsed_ms:.1f}ms")
            print(f"=== COMMAND HISTORY EXECUTE END ===\n")
            return True
            
        except Exception as e:
            print(f"DEBUG: ERROR - Command execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def undo(self) -> Optional[str]:
        """
        Undo the last command.

        Returns:
            Description of undone command if successful, None otherwise
        """
        print(f"\n=== COMMAND HISTORY UNDO START ===")
        print(f"DEBUG: Attempting to undo command")
        print(f"DEBUG: Current index: {self.current_index}")
        print(f"DEBUG: History size: {len(self.commands)}")
        print(f"DEBUG: Can undo: {self.can_undo()}")
        
        if not self.can_undo():
            print(f"DEBUG: Cannot undo - no commands available")
            return None

        command = self.commands[self.current_index]
        print(f"DEBUG: Undoing command: {command.get_description()}")
        print(f"DEBUG: Command type: {type(command).__name__}")
        
        try:
            print(f"DEBUG: Calling command.undo()...")
            result = command.undo()
            print(f"DEBUG: Command.undo() returned: {result}")
            
            if result:
                command._mark_undone()
                self.current_index -= 1
                print(f"DEBUG: Command undone successfully, index now: {self.current_index}")
                print(f"=== COMMAND HISTORY UNDO END ===\n")
                return command.get_description()
            else:
                print(f"DEBUG: Command undo failed")
                
        except Exception as e:
            print(f"DEBUG: ERROR - Undo failed for '{command.get_description()}': {e}")
            import traceback
            traceback.print_exc()
        
        print(f"=== COMMAND HISTORY UNDO END (FAILED) ===\n")
        return None
    
    def redo(self) -> Optional[str]:
        """
        Redo the next command.

        Returns:
            Description of redone command if successful, None otherwise
        """
        print(f"\n=== COMMAND HISTORY REDO START ===")
        print(f"DEBUG: Attempting to redo command")
        print(f"DEBUG: Current index: {self.current_index}")
        print(f"DEBUG: History size: {len(self.commands)}")
        print(f"DEBUG: Can redo: {self.can_redo()}")
        
        if not self.can_redo():
            print(f"DEBUG: Cannot redo - no commands available")
            return None

        command = self.commands[self.current_index + 1]
        print(f"DEBUG: Redoing command: {command.get_description()}")
        print(f"DEBUG: Command type: {type(command).__name__}")
        
        try:
            print(f"DEBUG: Calling command.execute() for redo...")
            result = command.execute()
            print(f"DEBUG: Command.execute() returned: {result}")
            
            if result:
                command._mark_executed()
                self.current_index += 1
                print(f"DEBUG: Command redone successfully, index now: {self.current_index}")
                print(f"=== COMMAND HISTORY REDO END ===\n")
                return command.get_description()
            else:
                print(f"DEBUG: Command redo failed")
                
        except Exception as e:
            print(f"DEBUG: ERROR - Redo failed for '{command.get_description()}': {e}")
            import traceback
            traceback.print_exc()
        
        print(f"=== COMMAND HISTORY REDO END (FAILED) ===\n")
        return None
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.current_index >= 0 and len(self.commands) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.current_index < len(self.commands) - 1
    
    def get_undo_description(self) -> Optional[str]:
        """Get description of next undo operation."""
        if self.can_undo():
            return self.commands[self.current_index].get_description()
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Get description of next redo operation."""
        if self.can_redo():
            return self.commands[self.current_index + 1].get_description()
        return None
    
    def get_history(self) -> List[str]:
        """
        Get list of all command descriptions in history.
        
        Returns:
            List of command descriptions, with current position marked
        """
        history = []
        for i, command in enumerate(self.commands):
            marker = " -> " if i == self.current_index else "    "
            history.append(f"{marker}{command.get_description()}")
        return history
    
    def clear(self):
        """Clear all command history."""
        self.commands.clear()
        self.current_index = -1
        self._memory_usage = 0
    
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        return self._memory_usage
    
    def get_memory_limit(self) -> int:
        """Get memory limit in bytes."""
        return self._memory_limit
    
    def get_command_count(self) -> int:
        """Get number of commands in history."""
        return len(self.commands)
    
    def _enforce_limits(self):
        """Enforce depth and memory limits."""
        # Remove oldest commands if over depth limit
        while len(self.commands) > self.max_depth:
            removed = self.commands.pop(0)
            self.current_index -= 1
            self._memory_usage -= removed.get_memory_usage()
            logger.debug(f"Removed command due to depth limit: {removed.get_description()}")
        
        # Enforce memory limit (NFR3)
        while (self._memory_usage > self._memory_limit and len(self.commands) > 0):
            removed = self.commands.pop(0)
            self.current_index -= 1
            self._memory_usage -= removed.get_memory_usage()
            logger.warning(f"Removed command due to memory limit: {removed.get_description()}")
    
    def undo_to_command(self, target_index: int) -> List[str]:
        """
        Undo multiple commands to reach target index.
        
        Args:
            target_index: Index to undo to (must be <= current_index)
            
        Returns:
            List of descriptions of undone commands
        """
        if target_index > self.current_index or target_index < -1:
            return []
        
        undone_descriptions = []
        while self.current_index > target_index:
            description = self.undo()
            if description:
                undone_descriptions.append(description)
            else:
                break
        
        return undone_descriptions


class PerformanceMonitor:
    """Monitor command execution performance for optimization."""
    
    def __init__(self):
        self.execution_times = []
        self.slow_commands = []
    
    def record_execution(self, command: CommandBase, elapsed_ms: float):
        """Record command execution time."""
        self.execution_times.append(elapsed_ms)
        
        if elapsed_ms > 100:  # NFR1 threshold
            self.slow_commands.append({
                'command': command.get_description(),
                'time_ms': elapsed_ms,
                'timestamp': time.time()
            })
    
    def get_average_execution_time(self) -> float:
        """Get average execution time in milliseconds."""
        if not self.execution_times:
            return 0.0
        return sum(self.execution_times) / len(self.execution_times)
    
    def get_slow_commands(self) -> List[dict]:
        """Get list of commands that exceeded performance threshold."""
        return self.slow_commands.copy()
    
    def reset_statistics(self):
        """Reset all performance statistics."""
        self.execution_times.clear()
        self.slow_commands.clear()
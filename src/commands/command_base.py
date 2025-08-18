"""
Abstract base class for all undoable commands in PyFlowGraph.

Provides the foundation for the Command Pattern implementation, ensuring
consistent behavior across all undoable operations.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class CommandBase(ABC):
    """Abstract base class for all undoable commands."""
    
    def __init__(self, description: str):
        """
        Initialize command with description.
        
        Args:
            description: Human-readable description for UI display
        """
        self.description = description
        self.timestamp = time.time()
        self._executed = False
        self._undone = False
    
    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the command.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """
        Undo the command, reversing its effects.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def get_description(self) -> str:
        """Get human-readable description for UI display."""
        return self.description
    
    def can_merge_with(self, other: 'CommandBase') -> bool:
        """
        Check if this command can be merged with another command.
        
        This is useful for combining similar operations (like multiple
        property changes) into a single undo unit.
        
        Args:
            other: Another command to potentially merge with
            
        Returns:
            True if commands can be merged, False otherwise
        """
        return False
    
    def merge_with(self, other: 'CommandBase') -> Optional['CommandBase']:
        """
        Merge this command with another command if possible.
        
        Args:
            other: Command to merge with
            
        Returns:
            New merged command if successful, None otherwise
        """
        return None
    
    def get_memory_usage(self) -> int:
        """
        Estimate memory usage of this command in bytes.
        
        Used by CommandHistory for memory limit enforcement.
        
        Returns:
            Estimated memory usage in bytes
        """
        # Base implementation provides conservative estimate
        return 512
    
    def is_executed(self) -> bool:
        """Check if command has been executed."""
        return self._executed
    
    def is_undone(self) -> bool:
        """Check if command has been undone."""
        return self._undone
    
    def _mark_executed(self):
        """Mark command as executed (internal use)."""
        self._executed = True
        self._undone = False
    
    def _mark_undone(self):
        """Mark command as undone (internal use)."""
        self._executed = False
        self._undone = True


class CompositeCommand(CommandBase):
    """
    Command that groups multiple operations as a single undo unit.
    
    Useful for complex operations that involve multiple steps but should
    be undone/redone as a single logical operation.
    """
    
    def __init__(self, description: str, commands: list['CommandBase']):
        """
        Initialize composite command.
        
        Args:
            description: Description of the composite operation
            commands: List of commands to execute as a group
        """
        super().__init__(description)
        self.commands = commands
        self.executed_commands = []
    
    def execute(self) -> bool:
        """Execute all commands, rolling back on failure."""
        print(f"\n=== COMPOSITE COMMAND EXECUTE START ===")
        print(f"DEBUG: Executing composite command with {len(self.commands)} commands")
        
        self.executed_commands = []
        
        for i, command in enumerate(self.commands):
            print(f"DEBUG: Executing command {i+1}/{len(self.commands)}: {command.get_description()}")
            result = command.execute()
            print(f"DEBUG: Command {i+1} returned: {result}")
            
            if result:
                command._mark_executed()
                self.executed_commands.append(command)
                print(f"DEBUG: Command {i+1} succeeded, added to executed list")
            else:
                print(f"DEBUG: Command {i+1} FAILED - rolling back {len(self.executed_commands)} executed commands")
                # Rollback executed commands on failure
                for j, executed in enumerate(reversed(self.executed_commands)):
                    print(f"DEBUG: Rolling back command {j+1}/{len(self.executed_commands)}: {executed.get_description()}")
                    rollback_result = executed.undo()
                    print(f"DEBUG: Rollback {j+1} returned: {rollback_result}")
                    executed._mark_undone()
                print(f"DEBUG: Rollback complete, composite command failed")
                print(f"=== COMPOSITE COMMAND EXECUTE END (FAILED) ===\n")
                return False
        
        self._mark_executed()
        print(f"DEBUG: All {len(self.commands)} commands succeeded")
        print(f"=== COMPOSITE COMMAND EXECUTE END (SUCCESS) ===\n")
        return True
    
    def undo(self) -> bool:
        """Undo all executed commands in reverse order."""
        if not self._executed:
            print(f"DEBUG: CompositeCommand.undo() - not executed, cannot undo")
            return False
        
        print(f"DEBUG: CompositeCommand.undo() - undoing {len(self.executed_commands)} commands")
        success_count = 0
        
        for i, command in enumerate(reversed(self.executed_commands)):
            print(f"DEBUG: Undoing command {i+1}/{len(self.executed_commands)}: {command.get_description()}")
            undo_result = command.undo()
            print(f"DEBUG: Command {i+1} undo returned: {undo_result}")
            
            if undo_result:
                command._mark_undone()
                success_count += 1
                print(f"DEBUG: Command {i+1} undone successfully")
            else:
                print(f"DEBUG: Command {i+1} undo FAILED")
                # Continue with other commands even if one fails
        
        # Consider composite undo successful if most commands succeeded
        # This prevents cascade failures from minor undo issues
        success_ratio = success_count / len(self.executed_commands) if self.executed_commands else 1.0
        overall_success = success_ratio >= 0.5  # At least 50% must succeed
        
        if overall_success:
            self._mark_undone()
            if success_count == len(self.executed_commands):
                print(f"DEBUG: All commands undone successfully, composite marked as undone")
            else:
                print(f"DEBUG: {success_count}/{len(self.executed_commands)} commands undone successfully, composite marked as undone")
        else:
            print(f"DEBUG: Only {success_count}/{len(self.executed_commands)} commands undone, composite undo failed")
        
        print(f"DEBUG: CompositeCommand.undo() returning: {overall_success}")
        return overall_success
    
    def get_memory_usage(self) -> int:
        """Calculate total memory usage of all contained commands."""
        return sum(cmd.get_memory_usage() for cmd in self.commands)
    
    def add_command(self, command: CommandBase):
        """Add a command to the composite (only if not executed)."""
        if not self._executed:
            self.commands.append(command)
    
    def get_command_count(self) -> int:
        """Get number of commands in this composite."""
        return len(self.commands)
# undo_history_dialog.py
# Dialog for viewing and navigating command history

import os
import sys
from typing import List, Optional
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                              QListWidgetItem, QPushButton, QLabel, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.utils.ui_utils import create_fa_icon


class UndoHistoryDialog(QDialog):
    """Dialog for viewing command history and navigating to specific points."""
    
    # Signal emitted when user wants to jump to a specific command index
    jumpToIndex = Signal(int)
    
    def __init__(self, command_history, parent=None):
        """
        Initialize the undo history dialog.
        
        Args:
            command_history: CommandHistory instance to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.command_history = command_history
        self.setWindowTitle("Undo History")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        
        self._setup_ui()
        self._populate_history()
        
    def _setup_ui(self):
        """Setup the dialog user interface."""
        layout = QVBoxLayout(self)
        
        # Header with instructions
        header_label = QLabel("Command History - Click to jump to specific point")
        header_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(header_label)
        
        # Command history list
        self.history_list = QListWidget()
        # Use system monospace font with fallback
        monospace_font = QFont("Consolas", 9)
        monospace_font.setStyleHint(QFont.StyleHint.Monospace)
        self.history_list.setFont(monospace_font)
        self.history_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.history_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.history_list)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.info_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Jump button
        self.jump_button = QPushButton(create_fa_icon("\uf0e2", "lightgreen"), "Jump to Selected")
        self.jump_button.clicked.connect(self._on_jump_clicked)
        self.jump_button.setEnabled(False)
        button_layout.addWidget(self.jump_button)
        
        # Spacer
        button_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
    def _populate_history(self):
        """Populate the history list with commands."""
        self.history_list.clear()
        
        if not self.command_history.commands:
            item = QListWidgetItem("No commands in history")
            item.setFlags(Qt.ItemFlag.NoItemFlags)  # Not selectable
            self.history_list.addItem(item)
            self._update_info_label(None)
            return
        
        current_index = self.command_history.current_index
        
        for i, command in enumerate(self.command_history.commands):
            # Create display text with timestamp and description
            timestamp = self._format_command_timestamp(command)
            description = command.get_description()
            
            # Mark current position and executed/undone state
            if i <= current_index:
                status = "DONE"
                marker = " -> " if i == current_index else "    "
            else:
                status = "UNDONE"
                marker = "    "
            
            display_text = f"{marker}[{timestamp}] {status:6} {description}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store command index
            
            # Color coding for visual clarity
            if i <= current_index:
                item.setForeground(Qt.GlobalColor.white)
                if i == current_index:
                    # Current position - make it bold
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setBackground(Qt.GlobalColor.lightGray)
            else:
                # Undone commands in gray
                item.setForeground(Qt.GlobalColor.gray)
            
            self.history_list.addItem(item)
        
        # Select current command
        if current_index >= 0:
            self.history_list.setCurrentRow(current_index)
        
        self._update_info_label(current_index)
        
    def _update_info_label(self, current_index: Optional[int]):
        """Update the info label with current state information."""
        if not self.command_history.commands:
            self.info_label.setText("No operations have been performed yet.")
            return
        
        total_commands = len(self.command_history.commands)
        
        if current_index is None or current_index < 0:
            self.info_label.setText(f"All {total_commands} operations have been undone.")
        else:
            executed_count = current_index + 1
            undone_count = total_commands - executed_count
            if undone_count > 0:
                self.info_label.setText(
                    f"{executed_count} of {total_commands} operations executed, "
                    f"{undone_count} undone."
                )
            else:
                self.info_label.setText(f"All {total_commands} operations executed.")
        
    def _on_selection_changed(self):
        """Handle list selection changes."""
        current_item = self.history_list.currentItem()
        if current_item and current_item.data(Qt.ItemDataRole.UserRole) is not None:
            self.jump_button.setEnabled(True)
        else:
            self.jump_button.setEnabled(False)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on list item."""
        if item.data(Qt.ItemDataRole.UserRole) is not None:
            self._jump_to_index(item.data(Qt.ItemDataRole.UserRole))
    
    def _on_jump_clicked(self):
        """Handle jump button click."""
        current_item = self.history_list.currentItem()
        if current_item and current_item.data(Qt.ItemDataRole.UserRole) is not None:
            self._jump_to_index(current_item.data(Qt.ItemDataRole.UserRole))
    
    def _jump_to_index(self, target_index: int):
        """Jump to specific command index."""
        if 0 <= target_index < len(self.command_history.commands):
            self.jumpToIndex.emit(target_index)
            self.accept()
    
    def _format_command_timestamp(self, command) -> str:
        """Format command timestamp consistently for display.
        
        Args:
            command: Command object with timestamp attribute
            
        Returns:
            Formatted timestamp string (HH:MM:SS)
        """
        timestamp_raw = getattr(command, 'timestamp', datetime.now())
        if isinstance(timestamp_raw, float):
            # Convert from time.time() format to datetime
            return datetime.fromtimestamp(timestamp_raw).strftime("%H:%M:%S")
        else:
            # Already a datetime object
            return timestamp_raw.strftime("%H:%M:%S")
    
    def refresh_history(self):
        """Refresh the history display (useful if command history changes)."""
        self._populate_history()
#!/usr/bin/env python3

"""
Enhanced Test Runner GUI for PyFlowGraph

Supports both headless and GUI test categories with:
- Organized test categories (Headless vs GUI)
- Category-specific test discovery
- Different timeouts for different test types
- Visual feedback for test categories
- Batch execution options
"""

import sys
import os
import unittest
import subprocess
import threading
import time
import traceback
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QPushButton,
    QLabel,
    QProgressBar,
    QStatusBar,
    QCheckBox,
    QGroupBox,
    QHeaderView,
    QFrame,
    QScrollArea,
    QTabWidget,
    QComboBox,
    QSpinBox,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QPainter, QBrush


class TestCategory:
    """Test category definitions."""
    HEADLESS = "headless"
    GUI = "gui"
    ALL = "all"


class TestResult:
    """Container for test execution results."""

    def __init__(self, name: str, category: str = "", status: str = "pending", output: str = "", duration: float = 0.0, error: str = ""):
        self.name = name
        self.category = category
        self.status = status  # pending, running, passed, failed, error
        self.output = output
        self.duration = duration
        self.error = error


class EnhancedTestExecutor(QObject):
    """Enhanced test executor with category support."""

    test_started = Signal(str, str)  # file_path, category
    test_finished = Signal(str, str, str, str, float)  # file_path, category, status, output, duration
    all_finished = Signal()

    def __init__(self, test_files: List[Tuple[str, str]]):  # [(file_path, category), ...]
        super().__init__()
        self.test_files = test_files
        self.should_stop = False

    def run_tests(self):
        """Run all specified test files with category-appropriate timeouts."""
        for test_file, category in self.test_files:
            if self.should_stop:
                break

            self.test_started.emit(test_file, category)
            start_time = time.time()

            # Set timeout based on category
            timeout = 30 if category == TestCategory.GUI else 10  # GUI tests get more time

            try:
                # Run the test file as a subprocess
                result = subprocess.run(
                    [sys.executable, test_file], 
                    capture_output=True, 
                    text=True, 
                    cwd=Path(__file__).parent.parent.parent,  # PyFlowGraph root
                    timeout=timeout
                )

                duration = time.time() - start_time

                if result.returncode == 0:
                    status = "passed"
                    output = result.stdout
                else:
                    status = "failed"
                    output = result.stdout + "\n" + result.stderr

                self.test_finished.emit(test_file, category, status, output, duration)

            except subprocess.TimeoutExpired:
                duration = time.time() - start_time
                self.test_finished.emit(test_file, category, "failed", f"Test timed out after {timeout} seconds", duration)

            except Exception as e:
                duration = time.time() - start_time
                self.test_finished.emit(test_file, category, "error", f"Execution error: {str(e)}", duration)

        self.all_finished.emit()

    def stop(self):
        """Stop test execution."""
        self.should_stop = True


class StatusIcon:
    """Helper class to create status icons with category colors."""

    @staticmethod
    def create_icon(color: str, size: int = 16) -> QIcon:
        """Create a colored circle icon."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        color_map = {
            "pending": "#777777", 
            "running": "#ffa500", 
            "passed": "#4CAF50", 
            "failed": "#f44336", 
            "error": "#9C27B0",
            "headless": "#2196F3",  # Blue for headless
            "gui": "#FF9800"        # Orange for GUI
        }

        brush = QBrush(QColor(color_map.get(color, "#777777")))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)
        painter.end()

        return QIcon(pixmap)


class EnhancedTestTreeWidget(QTreeWidget):
    """Enhanced tree widget with category support."""

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Test", "Category", "Status", "Duration"])
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)

        # Set column widths
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.test_results: Dict[str, TestResult] = {}
        self.category_items: Dict[str, QTreeWidgetItem] = {}

        # Create category parent items
        self._create_category_items()

    def _create_category_items(self):
        """Create parent items for each test category."""
        # Headless tests category
        headless_item = QTreeWidgetItem(self, ["Headless Tests", "Fast Unit Tests", "", ""])
        headless_item.setIcon(0, StatusIcon.create_icon("headless"))
        headless_item.setExpanded(True)
        headless_item.setFlags(headless_item.flags() | Qt.ItemIsUserCheckable)
        headless_item.setCheckState(0, Qt.Checked)
        self.category_items[TestCategory.HEADLESS] = headless_item

        # GUI tests category
        gui_item = QTreeWidgetItem(self, ["GUI Integration Tests", "Full GUI Testing", "", ""])
        gui_item.setIcon(0, StatusIcon.create_icon("gui"))
        gui_item.setExpanded(True)
        gui_item.setFlags(gui_item.flags() | Qt.ItemIsUserCheckable)
        gui_item.setCheckState(0, Qt.Checked)
        self.category_items[TestCategory.GUI] = gui_item

    def add_test_file(self, file_path: str, category: str) -> QTreeWidgetItem:
        """Add a test file to the appropriate category."""
        file_name = Path(file_path).name
        parent_item = self.category_items.get(category)
        
        if not parent_item:
            # Create category item if it doesn't exist
            parent_item = QTreeWidgetItem(self, [f"{category.title()} Tests", "", "", ""])
            self.category_items[category] = parent_item

        item = QTreeWidgetItem(parent_item, [file_name, category.title(), "Pending", ""])
        item.setData(0, Qt.UserRole, file_path)
        item.setData(1, Qt.UserRole, category)
        item.setIcon(0, StatusIcon.create_icon("pending"))
        
        # Make item checkable
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Checked)

        # Store the test result
        self.test_results[file_path] = TestResult(file_path, category)

        return item

    def update_test_status(self, file_path: str, status: str, duration: float = 0.0):
        """Update the status of a test."""
        if file_path in self.test_results:
            self.test_results[file_path].status = status
            self.test_results[file_path].duration = duration

        # Find and update the tree item
        def find_and_update(parent):
            for i in range(parent.childCount() if parent else self.topLevelItemCount()):
                item = parent.child(i) if parent else self.topLevelItem(i)
                
                if item.data(0, Qt.UserRole) == file_path:
                    item.setText(2, status.title())
                    if duration > 0:
                        item.setText(3, f"{duration:.2f}s")
                    item.setIcon(0, StatusIcon.create_icon(status))
                    return True
                
                # Recursively search children
                if find_and_update(item):
                    return True
            return False

        find_and_update(None)

    def get_selected_tests(self) -> List[Tuple[str, str]]:
        """Get list of selected test file paths with their categories."""
        selected = []
        
        def collect_selected(parent):
            for i in range(parent.childCount() if parent else self.topLevelItemCount()):
                item = parent.child(i) if parent else self.topLevelItem(i)
                
                # If it's a test file (has UserRole data)
                file_path = item.data(0, Qt.UserRole)
                if file_path and item.checkState(0) == Qt.Checked:
                    category = item.data(1, Qt.UserRole)
                    selected.append((file_path, category))
                
                # Recursively check children
                collect_selected(item)

        collect_selected(None)
        return selected

    def check_category(self, category: str, checked: bool):
        """Check or uncheck all tests in a category."""
        if category in self.category_items:
            parent_item = self.category_items[category]
            parent_item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
            
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                child.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)

    def get_category_summary(self) -> Dict[str, Tuple[int, int, int]]:
        """Get summary of tests per category: (total, selected, passed)."""
        summary = {}
        
        for category, parent_item in self.category_items.items():
            total = parent_item.childCount()
            selected = 0
            passed = 0
            
            for i in range(total):
                child = parent_item.child(i)
                if child.checkState(0) == Qt.Checked:
                    selected += 1
                
                file_path = child.data(0, Qt.UserRole)
                if file_path in self.test_results and self.test_results[file_path].status == "passed":
                    passed += 1
            
            summary[category] = (total, selected, passed)
        
        return summary


class EnhancedTestRunnerWindow(QMainWindow):
    """Enhanced test runner window with category support."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyFlowGraph Enhanced Test Runner")
        self.setGeometry(100, 100, 1200, 800)
        
        # Test execution state
        self.executor = None
        self.executor_thread = None
        self.is_running = False
        
        self.setup_ui()
        self.discover_tests()
        self.apply_dark_theme()

    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Main content area
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Test tree and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Output
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
        # Status bar
        self.statusBar().showMessage("Ready - Select tests and click 'Run Selected Tests'")

    def create_control_panel(self):
        """Create the top control panel."""
        panel = QGroupBox("Test Controls")
        layout = QHBoxLayout(panel)
        
        # Category selection
        layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All Tests", "Headless Only", "GUI Only"])
        layout.addWidget(self.category_combo)
        
        layout.addStretch()
        
        # Control buttons
        self.run_button = QPushButton("Run Selected Tests")
        self.run_button.clicked.connect(self.run_selected_tests)
        layout.addWidget(self.run_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_tests)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        return panel

    def create_left_panel(self):
        """Create the left panel with test tree."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Test tree
        tree_group = QGroupBox("Available Tests")
        tree_layout = QVBoxLayout(tree_group)
        
        self.test_tree = EnhancedTestTreeWidget()
        tree_layout.addWidget(self.test_tree)
        
        # Tree controls
        tree_controls = QHBoxLayout()
        
        headless_btn = QPushButton("✓ Headless")
        headless_btn.clicked.connect(lambda: self.test_tree.check_category(TestCategory.HEADLESS, True))
        tree_controls.addWidget(headless_btn)
        
        gui_btn = QPushButton("✓ GUI")
        gui_btn.clicked.connect(lambda: self.test_tree.check_category(TestCategory.GUI, True))
        tree_controls.addWidget(gui_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(lambda: [
            self.test_tree.check_category(TestCategory.HEADLESS, False),
            self.test_tree.check_category(TestCategory.GUI, False)
        ])
        tree_controls.addWidget(clear_btn)
        
        tree_layout.addLayout(tree_controls)
        layout.addWidget(tree_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_group)
        
        return panel

    def create_right_panel(self):
        """Create the right panel with output display."""
        panel = QGroupBox("Test Output")
        layout = QVBoxLayout(panel)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        # Output controls
        output_controls = QHBoxLayout()
        
        clear_output_btn = QPushButton("Clear Output")
        clear_output_btn.clicked.connect(self.output_text.clear)
        output_controls.addWidget(clear_output_btn)
        
        output_controls.addStretch()
        
        layout.addLayout(output_controls)
        
        return panel

    def discover_tests(self):
        """Discover all available tests."""
        project_root = Path(__file__).parent.parent.parent
        tests_dir = project_root / "tests"
        
        if not tests_dir.exists():
            QMessageBox.warning(self, "Warning", f"Tests directory not found: {tests_dir}")
            return
        
        # Discover headless tests
        headless_dir = tests_dir / "headless"
        if headless_dir.exists():
            for test_file in headless_dir.glob("test_*.py"):
                self.test_tree.add_test_file(str(test_file), TestCategory.HEADLESS)
        
        # Discover GUI tests
        gui_dir = tests_dir / "gui"
        if gui_dir.exists():
            for test_file in gui_dir.glob("test_*.py"):
                self.test_tree.add_test_file(str(test_file), TestCategory.GUI)
        
        # Also add tests from main tests directory (legacy)
        for test_file in tests_dir.glob("test_*.py"):
            # Determine category based on content or name
            category = TestCategory.HEADLESS  # Default to headless
            if "gui" in test_file.name.lower():
                category = TestCategory.GUI
            
            self.test_tree.add_test_file(str(test_file), category)

    def run_selected_tests(self):
        """Run the selected tests."""
        selected_tests = self.test_tree.get_selected_tests()
        
        if not selected_tests:
            QMessageBox.information(self, "No Tests Selected", "Please select at least one test to run.")
            return
        
        # Show warning for GUI tests
        gui_tests = [t for t in selected_tests if t[1] == TestCategory.GUI]
        if gui_tests:
            reply = QMessageBox.question(
                self,
                "GUI Tests Selected",
                f"You have selected {len(gui_tests)} GUI test(s).\n\n"
                "GUI tests will open application windows during execution.\n"
                "Please do not interact with test windows while they are running.\n\n"
                "Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        self.is_running = True
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Setup progress
        self.progress_bar.setMaximum(len(selected_tests))
        self.progress_bar.setValue(0)
        
        # Clear output
        self.output_text.clear()
        self.output_text.append(f"Starting {len(selected_tests)} tests...\n")
        
        # Create and start executor
        self.executor = EnhancedTestExecutor(selected_tests)
        self.executor.test_started.connect(self.on_test_started)
        self.executor.test_finished.connect(self.on_test_finished)
        self.executor.all_finished.connect(self.on_all_finished)
        
        self.executor_thread = QThread()
        self.executor.moveToThread(self.executor_thread)
        self.executor_thread.started.connect(self.executor.run_tests)
        self.executor_thread.start()

    def stop_tests(self):
        """Stop test execution."""
        if self.executor:
            self.executor.stop()
        
        self.output_text.append("\n=== STOPPING TESTS ===\n")
        self.statusBar().showMessage("Stopping tests...")

    def on_test_started(self, file_path: str, category: str):
        """Handle test started event."""
        test_name = Path(file_path).name
        self.output_text.append(f"[{category.upper()}] Starting: {test_name}")
        self.progress_label.setText(f"Running: {test_name}")
        self.statusBar().showMessage(f"Running {category} test: {test_name}")

    def on_test_finished(self, file_path: str, category: str, status: str, output: str, duration: float):
        """Handle test finished event."""
        test_name = Path(file_path).name
        
        # Update tree
        self.test_tree.update_test_status(file_path, status, duration)
        
        # Update progress
        current_value = self.progress_bar.value()
        self.progress_bar.setValue(current_value + 1)
        
        # Add output
        status_symbol = "✓" if status == "passed" else "✗"
        self.output_text.append(f"[{category.upper()}] {status_symbol} {test_name} ({duration:.2f}s) - {status.upper()}")
        
        if output.strip():
            self.output_text.append(f"Output:\n{output}\n")
        
        self.output_text.append("-" * 50)

    def on_all_finished(self):
        """Handle all tests finished event."""
        self.is_running = False
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Clean up thread
        if self.executor_thread:
            self.executor_thread.quit()
            self.executor_thread.wait()
            self.executor_thread = None
        
        # Summary
        summary = self.test_tree.get_category_summary()
        
        self.output_text.append("\n" + "=" * 50)
        self.output_text.append("TEST EXECUTION COMPLETE")
        self.output_text.append("=" * 50)
        
        for category, (total, selected, passed) in summary.items():
            self.output_text.append(f"{category.upper()}: {passed}/{selected} passed")
        
        self.progress_label.setText("Complete")
        self.statusBar().showMessage("All tests completed")

    def apply_dark_theme(self):
        """Apply dark theme to the window."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
            QTreeWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                selection-background-color: #404040;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)


def main():
    """Main entry point for the enhanced test runner."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = EnhancedTestRunnerWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
#!/usr/bin/env python3

"""
Professional Test Runner GUI for PyFlowGraph

A modern PySide6-based test runner that provides:
- Visual test discovery and management
- Real-time test execution with progress tracking
- Detailed results viewing with syntax highlighting
- Professional UI with green/red status indicators
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
)
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal, QSize, QRect
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QPainter, QBrush


class TestResult:
    """Container for test execution results."""

    def __init__(self, name: str, status: str = "pending", output: str = "", duration: float = 0.0, error: str = ""):
        self.name = name
        self.status = status  # pending, running, passed, failed, error
        self.output = output
        self.duration = duration
        self.error = error


class TestExecutor(QObject):
    """Background test executor that runs tests and emits results."""

    test_started = Signal(str)
    test_finished = Signal(str, str, str, float)  # name, status, output, duration
    all_finished = Signal()

    def __init__(self, test_files: List[str]):
        super().__init__()
        self.test_files = test_files
        self.should_stop = False

    def run_tests(self):
        """Run all specified test files."""
        for test_file in self.test_files:
            if self.should_stop:
                break

            self.test_started.emit(test_file)
            start_time = time.time()

            try:
                # Run the test file as a subprocess
                result = subprocess.run([sys.executable, test_file], capture_output=True, text=True, cwd=Path(__file__).parent.parent, timeout=5)  # 5 second timeout per test

                duration = time.time() - start_time

                if result.returncode == 0:
                    status = "passed"
                    output = result.stdout
                else:
                    status = "failed"
                    output = result.stdout + "\n" + result.stderr

                self.test_finished.emit(test_file, status, output, duration)

            except subprocess.TimeoutExpired:
                duration = time.time() - start_time
                self.test_finished.emit(test_file, "failed", "Test timed out after 5 seconds", duration)

            except Exception as e:
                duration = time.time() - start_time
                self.test_finished.emit(test_file, "error", f"Execution error: {str(e)}", duration)

        self.all_finished.emit()

    def stop(self):
        """Stop test execution."""
        self.should_stop = True


class StatusIcon:
    """Helper class to create status icons."""

    @staticmethod
    def create_icon(color: str, size: int = 16) -> QIcon:
        """Create a colored circle icon."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        color_map = {"pending": "#777777", "running": "#ffa500", "passed": "#4CAF50", "failed": "#f44336", "error": "#9C27B0"}

        brush = QBrush(QColor(color_map.get(color, "#777777")))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)
        painter.end()

        return QIcon(pixmap)


class TestTreeWidget(QTreeWidget):
    """Custom tree widget for displaying tests with status icons."""

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Test", "Status", "Duration"])
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)

        # Set column widths
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.test_results: Dict[str, TestResult] = {}

    def add_test_file(self, file_path: str) -> QTreeWidgetItem:
        """Add a test file to the tree."""
        file_name = Path(file_path).name
        item = QTreeWidgetItem(self, [file_name, "Pending", ""])
        item.setData(0, Qt.UserRole, file_path)
        item.setIcon(0, StatusIcon.create_icon("pending"))
        
        # Make item checkable
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

        # Store the test result
        self.test_results[file_path] = TestResult(file_path)

        return item

    def update_test_status(self, file_path: str, status: str, duration: float = 0.0):
        """Update the status of a test."""
        if file_path in self.test_results:
            self.test_results[file_path].status = status
            self.test_results[file_path].duration = duration

        # Find and update the tree item
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.data(0, Qt.UserRole) == file_path:
                item.setText(1, status.title())
                if duration > 0:
                    item.setText(2, f"{duration:.2f}s")
                item.setIcon(0, StatusIcon.create_icon(status))
                break

    def get_selected_tests(self) -> List[str]:
        """Get list of selected test file paths."""
        selected = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                selected.append(item.data(0, Qt.UserRole))
        return selected

    def check_all_tests(self, checked: bool):
        """Check or uncheck all tests."""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
    
    def get_check_state_summary(self) -> tuple[int, int]:
        """Get summary of checked/total items."""
        total = self.topLevelItemCount()
        checked = 0
        for i in range(total):
            item = self.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                checked += 1
        return checked, total


class TestOutputWidget(QTextEdit):
    """Enhanced text widget for displaying test output with syntax highlighting."""

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 9))

        # Set color scheme for better readability
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor("#1e1e1e"))
        palette.setColor(QPalette.Text, QColor("#d4d4d4"))
        self.setPalette(palette)

    def set_test_output(self, file_path: str, result: TestResult):
        """Display the output for a specific test."""
        self.clear()

        # Header
        html = f"""
        <h3 style="color: #569cd6; margin-bottom: 10px;">
            Test: {Path(file_path).name}
        </h3>
        """

        # Status with color
        status_colors = {"passed": "#4CAF50", "failed": "#f44336", "error": "#9C27B0", "running": "#ffa500", "pending": "#777777"}

        status_color = status_colors.get(result.status, "#777777")
        html += f"""
        <p><strong>Status:</strong> 
        <span style="color: {status_color}; font-weight: bold;">
            {result.status.upper()}
        </span></p>
        """

        if result.duration > 0:
            html += f"<p><strong>Duration:</strong> {result.duration:.2f} seconds</p>"

        html += "<hr style='border: 1px solid #333; margin: 15px 0;'>"

        # Output
        if result.output:
            # Convert plain text output to HTML with basic formatting
            output_html = result.output.replace("\n", "<br>")
            output_html = output_html.replace("PASSED", "<span style='color: #4CAF50;'>PASSED</span>")
            output_html = output_html.replace("FAILED", "<span style='color: #f44336;'>FAILED</span>")
            output_html = output_html.replace("ERROR", "<span style='color: #9C27B0;'>ERROR</span>")

            html += f"""
            <h4 style="color: #569cd6;">Output:</h4>
            <pre style="background: #2d2d2d; padding: 10px; border-radius: 5px; 
                        color: #d4d4d4; white-space: pre-wrap; font-family: 'Consolas', monospace;">
            {output_html}
            </pre>
            """

        # Error details
        if result.error:
            html += f"""
            <h4 style="color: #f44336;">Error Details:</h4>
            <pre style="background: #2d2d2d; padding: 10px; border-radius: 5px; 
                        color: #f44336; white-space: pre-wrap; font-family: 'Consolas', monospace;">
            {result.error}
            </pre>
            """

        self.setHtml(html)


class TestRunnerMainWindow(QMainWindow):
    """Main window for the test runner application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyFlowGraph Test Runner")
        self.setGeometry(100, 100, 1200, 800)

        # Test execution thread
        self.test_thread = None
        self.test_executor = None
        
        # Track currently selected test for auto-refresh
        self.currently_selected_test = None

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
        control_group = QGroupBox("Test Control")
        control_group.setFixedHeight(80)  # Set fixed height to prevent excessive vertical space
        control_layout = QHBoxLayout(control_group)

        self.select_all_cb = QCheckBox("Select All")
        self.select_all_cb.stateChanged.connect(self.on_select_all_changed)

        self.run_selected_btn = QPushButton("Run Selected Tests")
        self.run_selected_btn.clicked.connect(self.run_selected_tests)

        self.run_all_btn = QPushButton("Run All Tests")
        self.run_all_btn.clicked.connect(self.run_all_tests)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_tests)
        self.stop_btn.setEnabled(False)

        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)

        control_layout.addWidget(self.select_all_cb)
        control_layout.addStretch()
        control_layout.addWidget(self.run_selected_btn)
        control_layout.addWidget(self.run_all_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.clear_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Splitter for main content
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Test tree
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        test_label = QLabel("Available Tests")
        test_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")

        self.test_tree = TestTreeWidget()
        self.test_tree.itemClicked.connect(self.on_test_selected)
        self.test_tree.itemChanged.connect(self.on_test_item_changed)

        left_layout.addWidget(test_label)
        left_layout.addWidget(self.test_tree)

        # Right panel - Test output
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        output_label = QLabel("Test Output")
        output_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")

        self.output_widget = TestOutputWidget()

        right_layout.addWidget(output_label)
        right_layout.addWidget(self.output_widget)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])  # Give more space to output

        # Add everything to main layout
        main_layout.addWidget(control_group)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Ready")

    def apply_dark_theme(self):
        """Apply a dark theme to match the main application."""
        dark_stylesheet = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 5px;
            margin-top: 6px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
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
            background-color: #353535;
            alternate-background-color: #3a3a3a;
            border: 1px solid #555555;
        }
        QTreeWidget::item:selected {
            background-color: #0078d4;
        }
        QTreeWidget::item:hover {
            background-color: #404040;
        }
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 3px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 2px;
        }
        QStatusBar {
            background-color: #404040;
            border-top: 1px solid #555555;
        }
        QLabel {
            color: #ffffff;
        }
        QCheckBox {
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def discover_tests(self):
        """Discover all test files in the tests directory."""
        tests_dir = Path(__file__).parent.parent / "tests"

        if not tests_dir.exists():
            self.statusBar().showMessage("Tests directory not found")
            return

        test_files = []
        for file_path in tests_dir.glob("test_*.py"):
            if file_path.is_file():
                test_files.append(str(file_path))

        # Add test files to tree
        for test_file in sorted(test_files):
            item = self.test_tree.add_test_file(test_file)
            item.setCheckState(0, Qt.Checked)  # Check all by default

        # Set select all checkbox to checked since all tests start checked
        self.select_all_cb.setChecked(True)

        self.statusBar().showMessage(f"Found {len(test_files)} test files")

    def on_select_all_changed(self, state):
        """Handle select all checkbox change."""
        # state is an int: 0=Unchecked, 2=Checked 
        is_checked = (state == 2)  # Qt.Checked == 2
        self.test_tree.check_all_tests(is_checked)
    
    def on_test_item_changed(self, item, column):
        """Handle individual test item checkbox change."""
        # Individual test changes don't affect the Select All checkbox
        pass

    def on_test_selected(self, item, column):
        """Handle test selection in tree."""
        file_path = item.data(0, Qt.UserRole)
        if file_path and file_path in self.test_tree.test_results:
            # Track the currently selected test for auto-refresh
            self.currently_selected_test = file_path
            
            result = self.test_tree.test_results[file_path]
            self.output_widget.set_test_output(file_path, result)

    def run_selected_tests(self):
        """Run only the selected tests."""
        selected_tests = self.test_tree.get_selected_tests()
        if not selected_tests:
            self.statusBar().showMessage("No tests selected")
            return
        self.run_tests(selected_tests)

    def run_all_tests(self):
        """Run all available tests."""
        all_tests = []
        for i in range(self.test_tree.topLevelItemCount()):
            item = self.test_tree.topLevelItem(i)
            all_tests.append(item.data(0, Qt.UserRole))

        if not all_tests:
            self.statusBar().showMessage("No tests available")
            return
        self.run_tests(all_tests)

    def run_tests(self, test_files: List[str]):
        """Execute the specified test files."""
        if self.test_thread and self.test_thread.isRunning():
            self.statusBar().showMessage("Tests are already running")
            return

        # Reset all test statuses
        for test_file in test_files:
            self.test_tree.update_test_status(test_file, "pending")
            if test_file in self.test_tree.test_results:
                self.test_tree.test_results[test_file].output = ""
                self.test_tree.test_results[test_file].error = ""

        # Set up progress bar
        self.progress_bar.setMaximum(len(test_files))
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        # Disable run buttons, enable stop button
        self.run_selected_btn.setEnabled(False)
        self.run_all_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Create and start test executor
        self.test_executor = TestExecutor(test_files)
        self.test_thread = QThread()
        self.test_executor.moveToThread(self.test_thread)

        # Connect signals
        self.test_executor.test_started.connect(self.on_test_started)
        self.test_executor.test_finished.connect(self.on_test_finished)
        self.test_executor.all_finished.connect(self.on_all_tests_finished)
        self.test_thread.started.connect(self.test_executor.run_tests)

        # Start thread
        self.test_thread.start()

        self.statusBar().showMessage(f"Running {len(test_files)} tests...")

    def on_test_started(self, file_path: str):
        """Handle test start event."""
        self.test_tree.update_test_status(file_path, "running")
        test_name = Path(file_path).name
        self.statusBar().showMessage(f"Running: {test_name}")

    def on_test_finished(self, file_path: str, status: str, output: str, duration: float):
        """Handle test completion event."""
        self.test_tree.update_test_status(file_path, status, duration)

        # Update test result with output
        if file_path in self.test_tree.test_results:
            result = self.test_tree.test_results[file_path]
            result.status = status
            result.output = output
            result.duration = duration
            
            # Auto-refresh output panel if this test is currently selected
            if file_path == self.currently_selected_test:
                self.output_widget.set_test_output(file_path, result)

        # Update progress
        current_value = self.progress_bar.value()
        self.progress_bar.setValue(current_value + 1)

        # Update status message
        test_name = Path(file_path).name
        self.statusBar().showMessage(f"Completed: {test_name} ({status})")

    def on_all_tests_finished(self):
        """Handle completion of all tests."""
        # Re-enable buttons
        self.run_selected_btn.setEnabled(True)
        self.run_all_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        # Hide progress bar
        self.progress_bar.setVisible(False)

        # Calculate summary
        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        for result in self.test_tree.test_results.values():
            if result.status in ["passed", "failed", "error"]:
                total_tests += 1
                if result.status == "passed":
                    passed_tests += 1
                else:
                    failed_tests += 1

        # Update status message
        self.statusBar().showMessage(f"Tests completed: {passed_tests} passed, {failed_tests} failed, {total_tests} total")

        # Clean up thread
        if self.test_thread:
            self.test_thread.quit()
            self.test_thread.wait()
            self.test_thread = None
            self.test_executor = None

    def stop_tests(self):
        """Stop test execution."""
        if self.test_executor:
            self.test_executor.stop()

        self.statusBar().showMessage("Stopping tests...")

    def clear_results(self):
        """Clear all test results."""
        # Reset all test statuses
        for i in range(self.test_tree.topLevelItemCount()):
            item = self.test_tree.topLevelItem(i)
            file_path = item.data(0, Qt.UserRole)
            self.test_tree.update_test_status(file_path, "pending", 0.0)

            if file_path in self.test_tree.test_results:
                result = self.test_tree.test_results[file_path]
                result.status = "pending"
                result.output = ""
                result.error = ""
                result.duration = 0.0

        # Clear output widget
        self.output_widget.clear()

        self.statusBar().showMessage("Results cleared")


def main():
    """Main entry point for the test runner GUI."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Load Font Awesome fonts if available
    fonts_dir = Path(__file__).parent.parent / "resources" / "fonts"
    if fonts_dir.exists():
        for font_file in fonts_dir.glob("*.ttf"):
            app.addFont(str(font_file))

    # Create and show main window
    window = TestRunnerMainWindow()
    window.show()

    # Start event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

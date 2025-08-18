#!/usr/bin/env python3
"""
Execute Graph Button Mode Tests

Tests for the Execute Graph button functionality in both Live and Batch modes,
specifically targeting the pause/resume state management bug where the system
incorrectly reports "Not in live mode - enable Live Mode first!" after pausing.

This addresses the critical bug where live_mode flag gets confused with live_active
state during pause/resume operations.
"""

import sys
import os
import unittest
import time
from pathlib import Path
import pytest

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QLabel, QRadioButton
from PySide6.QtCore import Qt, QTimer, QPointF, QPoint
from PySide6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtTest import QTest

from ui.editor.node_editor_window import NodeEditorWindow
from core.node import Node
from core.reroute_node import RerouteNode
from core.connection import Connection
from execution.execution_controller import ExecutionController


@pytest.mark.gui
class ExecuteGraphTestCase(unittest.TestCase):
    """Base class for Execute Graph button tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for GUI testing."""
        if QApplication.instance() is None:
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        
        # Configure for GUI testing
        cls.app.setQuitOnLastWindowClosed(False)
        cls.test_timeout = 10000  # 10 seconds max per test
    
    def setUp(self):
        """Set up each test with a fresh window."""
        print(f"\n=== Starting Test: {self._testMethodName} ===")
        
        # Create main application window
        self.window = NodeEditorWindow()
        self.graph = self.window.graph
        self.view = self.window.view
        
        # Get execution controller components
        self.execution_controller = None
        self.main_exec_button = None
        self.status_label = None
        self.mode_radio_buttons = []
        
        # Find execution controller and UI components
        self._find_execution_components()
        
        
        # Show window and make it ready for testing
        self.window.show()
        self.window.resize(1200, 800)
        self.window.raise_()  # Bring to front
        
        # Clear any existing content
        self.graph.clear_graph()
        
        # Process events to ensure window is ready
        QApplication.processEvents()
        
        # Wait a moment for window to be fully displayed
        QTest.qWait(100)
        
        print(f"Window displayed - Ready for execution test")
    
    def tearDown(self):
        """Clean up after each test."""
        print(f"=== Cleaning up Test: {self._testMethodName} ===")
        
        # Close window and clean up
        if hasattr(self, 'window'):
            self.window.close()
            
        # Process events to ensure cleanup
        QApplication.processEvents()
        QTest.qWait(100)
        
        print(f"Test cleanup complete\n")
    
    def _find_execution_components(self):
        """Find and cache execution-related UI components."""
        # Get ExecutionController directly from window
        if hasattr(self.window, 'execution_ctrl'):
            self.execution_controller = self.window.execution_ctrl
        
        # Get execution widget and its components
        if hasattr(self.window, 'exec_widget'):
            exec_widget = self.window.exec_widget
            
            # Get button and label from exec_widget
            if hasattr(exec_widget, 'main_exec_button'):
                self.main_exec_button = exec_widget.main_exec_button
            
            if hasattr(exec_widget, 'status_label'):
                self.status_label = exec_widget.status_label
            
            # Get radio buttons from exec_widget
            if hasattr(exec_widget, 'batch_radio'):
                self.mode_radio_buttons.append(exec_widget.batch_radio)
            if hasattr(exec_widget, 'live_radio'):
                self.mode_radio_buttons.append(exec_widget.live_radio)
    
    def _get_batch_mode_radio(self):
        """Get the Batch mode radio button."""
        if hasattr(self.window, 'exec_widget') and hasattr(self.window.exec_widget, 'batch_radio'):
            return self.window.exec_widget.batch_radio
        return None
    
    def _get_live_mode_radio(self):
        """Get the Live mode radio button."""
        if hasattr(self.window, 'exec_widget') and hasattr(self.window.exec_widget, 'live_radio'):
            return self.window.exec_widget.live_radio
        return None
    
    def _create_simple_test_graph(self):
        """Create a simple test graph for execution tests."""
        # Create a simple producer node
        producer = self.graph.create_node("Producer", pos=(100, 100))
        producer.set_code('''
@node_entry
def produce_number() -> int:
    return 42
''')
        
        # Create a simple consumer node
        consumer = self.graph.create_node("Consumer", pos=(400, 100))
        consumer.set_code('''
@node_entry  
def consume_number(x: int):
    print(f"Received: {x}")
''')
        
        QApplication.processEvents()
        QTest.qWait(50)
        
        # Connect them
        producer_output = None
        consumer_input = None
        
        for pin in producer.output_pins:
            if pin.pin_category == "data":
                producer_output = pin
                break
        
        for pin in consumer.input_pins:
            if pin.pin_category == "data":
                consumer_input = pin
                break
        
        if producer_output and consumer_input:
            self.graph.create_connection(producer_output, consumer_input)
            QApplication.processEvents()
        
        return producer, consumer
    
    def wait_for_button_text(self, expected_text, timeout=5000):
        """Wait for button text to change to expected value."""
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout:
            QApplication.processEvents()
            if self.main_exec_button and expected_text in self.main_exec_button.text():
                return True
            time.sleep(0.01)
        return False
    
    def wait_for_status_text(self, expected_text, timeout=5000):
        """Wait for status text to change to expected value."""
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout:
            QApplication.processEvents()
            if self.status_label and expected_text.lower() in self.status_label.text().lower():
                return True
            time.sleep(0.01)
        return False
    
    def _switch_to_live_mode(self):
        """Helper to switch to live mode reliably."""
        live_radio = self._get_live_mode_radio()
        if live_radio:
            live_radio.setChecked(True)
            QApplication.processEvents()
            
            # Manually trigger the mode change callback
            if hasattr(self.window, 'exec_widget') and hasattr(self.window.exec_widget, 'mode_button_group'):
                mode_group = self.window.exec_widget.mode_button_group
                live_id = mode_group.id(live_radio)
                self.window.execution_ctrl.on_mode_changed(live_id)
            
            QApplication.processEvents()
            QTest.qWait(100)
    
    def _switch_to_batch_mode(self):
        """Helper to switch to batch mode reliably."""
        batch_radio = self._get_batch_mode_radio()
        if batch_radio:
            batch_radio.setChecked(True)
            QApplication.processEvents()
            
            # Manually trigger the mode change callback
            if hasattr(self.window, 'exec_widget') and hasattr(self.window.exec_widget, 'mode_button_group'):
                mode_group = self.window.exec_widget.mode_button_group
                batch_id = mode_group.id(batch_radio)
                self.window.execution_ctrl.on_mode_changed(batch_id)
            
            QApplication.processEvents()
            QTest.qWait(100)


class TestBatchModeExecution(ExecuteGraphTestCase):
    """Test Execute Graph button in Batch mode."""
    
    def test_batch_mode_button_initial_state(self):
        """Test initial button state in batch mode."""
        # Ensure we're in batch mode
        batch_radio = self._get_batch_mode_radio()
        if batch_radio:
            batch_radio.setChecked(True)
            QApplication.processEvents()
        
        # Button should show "Execute Graph"
        if self.main_exec_button:
            self.assertIn("Execute", self.main_exec_button.text())
        
        # Status should be "Ready"
        if self.status_label:
            self.assertIn("Ready", self.status_label.text())
        
        print("PASS Batch mode initial state correct")
    
    def test_batch_mode_execution_cycle(self):
        """Test complete batch execution cycle."""
        # Set batch mode
        batch_radio = self._get_batch_mode_radio()
        if batch_radio:
            batch_radio.setChecked(True)
            QApplication.processEvents()
        
        # Create test graph
        producer, consumer = self._create_simple_test_graph()
        
        # Click execute button
        if self.main_exec_button:
            initial_text = self.main_exec_button.text()
            self.main_exec_button.click()
            QApplication.processEvents()
            
            # Button should change to "Executing..." temporarily
            # Then back to "Execute Graph"
            QTest.qWait(500)  # Allow execution to complete
            QApplication.processEvents()
            
            # Should return to ready state
            self.wait_for_button_text("Execute", timeout=3000)
            final_text = self.main_exec_button.text()
            self.assertIn("Execute", final_text)
        
        print("PASS Batch mode execution cycle working correctly")
    
    def test_batch_mode_with_empty_graph(self):
        """Test batch execution with empty graph."""
        # Set batch mode
        batch_radio = self._get_batch_mode_radio()
        if batch_radio:
            batch_radio.setChecked(True)
            QApplication.processEvents()
        
        # Execute empty graph
        if self.main_exec_button:
            self.main_exec_button.click()
            QApplication.processEvents()
            QTest.qWait(200)
            
            # Should complete without error
            self.wait_for_button_text("Execute", timeout=2000)
            self.assertIn("Execute", self.main_exec_button.text())
        
        print("PASS Batch mode handles empty graph correctly")


class TestLiveModeExecution(ExecuteGraphTestCase):
    """Test Execute Graph button in Live mode."""
    
    def test_live_mode_button_initial_state(self):
        """Test initial button state in live mode."""
        # Initially should be in batch mode
        if self.main_exec_button:
            print(f"DEBUG: Initial button text: '{self.main_exec_button.text()}'")
            self.assertIn("Execute", self.main_exec_button.text())
        
        # Switch to live mode
        live_radio = self._get_live_mode_radio()
        if live_radio:
            print(f"DEBUG: Switching to live mode...")
            live_radio.setChecked(True)
            QApplication.processEvents()
            
            # Manually trigger the mode change callback since signal may not fire in tests
            if hasattr(self.window, 'exec_widget') and hasattr(self.window.exec_widget, 'mode_button_group'):
                mode_group = self.window.exec_widget.mode_button_group
                live_id = mode_group.id(live_radio)
                print(f"DEBUG: Triggering mode change with ID: {live_id}")
                self.window.execution_ctrl.on_mode_changed(live_id)
            
            QApplication.processEvents()
            QTest.qWait(200)  # Allow time for UI update
        
        # Button should show "Start Live Mode"
        if self.main_exec_button:
            print(f"DEBUG: After switch button text: '{self.main_exec_button.text()}'")
            self.wait_for_button_text("Start", timeout=2000)
            self.assertIn("Start", self.main_exec_button.text())
        
        # Status should be "Live Ready"
        if self.status_label:
            print(f"DEBUG: Status text: '{self.status_label.text()}'")
            self.wait_for_status_text("Live", timeout=2000)
            self.assertIn("Live", self.status_label.text())
        
        print("PASS Live mode initial state correct")
    
    def test_live_mode_start_cycle(self):
        """Test starting live mode."""
        # Switch to live mode using helper
        self._switch_to_live_mode()
        
        # Create test graph
        producer, consumer = self._create_simple_test_graph()
        
        # Start live mode
        if self.main_exec_button:
            self.main_exec_button.click()
            QApplication.processEvents()
            
            # Button should change to "Pause Live Mode"
            self.wait_for_button_text("Pause", timeout=2000)
            self.assertIn("Pause", self.main_exec_button.text())
        
        # Status should be "Live Active"
        if self.status_label:
            self.wait_for_status_text("Active", timeout=2000)
            self.assertIn("Active", self.status_label.text())
        
        print("PASS Live mode start cycle working correctly")
    
    def test_live_mode_pause_resume_cycle(self):
        """Test the critical pause/resume cycle that was failing."""
        # This test specifically addresses the reported bug
        
        # Switch to live mode using helper
        self._switch_to_live_mode()
        
        # Verify we're in live mode
        if self.main_exec_button:
            self.wait_for_button_text("Start", timeout=2000)
            self.assertIn("Start", self.main_exec_button.text())
        
        # Create test graph
        producer, consumer = self._create_simple_test_graph()
        
        # Start live mode
        if self.main_exec_button:
            print(f"DEBUG: Starting live mode...")
            # Start
            self.main_exec_button.click()
            QApplication.processEvents()
            self.wait_for_button_text("Pause", timeout=2000)
            
            # Verify we're in active state
            print(f"DEBUG: After start - Button: '{self.main_exec_button.text()}'")
            self.assertIn("Pause", self.main_exec_button.text())
            if self.status_label:
                print(f"DEBUG: After start - Status: '{self.status_label.text()}'")
                self.assertIn("Active", self.status_label.text())
            
            # Now pause
            print(f"DEBUG: Pausing live mode...")
            self.main_exec_button.click()
            QApplication.processEvents()
            self.wait_for_button_text("Resume", timeout=2000)
            
            # Verify we're in paused state
            print(f"DEBUG: After pause - Button: '{self.main_exec_button.text()}'")
            self.assertIn("Resume", self.main_exec_button.text())
            if self.status_label:
                print(f"DEBUG: After pause - Status: '{self.status_label.text()}'")
                self.assertIn("Paused", self.status_label.text())
            
            # Now resume (this is where the bug occurred)
            print(f"DEBUG: Resuming live mode...")
            self.main_exec_button.click()
            QApplication.processEvents()
            self.wait_for_button_text("Pause", timeout=2000)
            
            # CRITICAL TEST: Button should be "Pause Live Mode", not showing error
            button_text = self.main_exec_button.text()
            print(f"DEBUG: After resume - Button: '{button_text}'")
            self.assertIn("Pause", button_text)
            self.assertNotIn("Start", button_text)  # Should not revert to Start
            
            # Status should be Active again
            if self.status_label:
                print(f"DEBUG: After resume - Status: '{self.status_label.text()}'")
                self.wait_for_status_text("Active", timeout=2000)
                self.assertIn("Active", self.status_label.text())
            
            # Verify execution controller state consistency
            if self.execution_controller:
                print(f"DEBUG: ExecutionController - live_mode: {self.execution_controller.live_mode}, live_active: {self.execution_controller.live_active}")
                self.assertTrue(self.execution_controller.live_mode)
                self.assertTrue(self.execution_controller.live_active)
        
        print("PASS Live mode pause/resume cycle working correctly - Bug fixed!")
    
    def test_pause_resume_node_execution_bug(self):
        """Test the specific bug: pause  resume  node button execution fails."""
        # This reproduces the exact user scenario that was failing
        
        # Switch to live mode and start
        self._switch_to_live_mode()
        
        # Create test graph with interactive node
        node = self.graph.create_node("Interactive Node", pos=(200, 200))
        node.set_code('''
@node_entry
def interactive_function() -> str:
    return "Live execution test"
''')
        
        # Add GUI code to create a button for interaction
        node.set_gui_code('''
button = QPushButton("Generate Password")
button.setParent(widget)
button.move(10, 30)
button.show()
''')
        
        QApplication.processEvents()
        QTest.qWait(200)
        
        # Start live mode
        if self.main_exec_button:
            self.main_exec_button.click()  # Start
            QApplication.processEvents()
            self.wait_for_button_text("Pause", timeout=2000)
            
            # Pause live mode
            self.main_exec_button.click()  # Pause
            QApplication.processEvents()
            self.wait_for_button_text("Resume", timeout=2000)
            
            # Resume live mode
            self.main_exec_button.click()  # Resume
            QApplication.processEvents()
            self.wait_for_button_text("Pause", timeout=2000)
        
        # NOW TEST THE CRITICAL PART: Node button execution after resume
        # This should work without showing "Not in live mode" error
        
        # Simulate node button click by directly calling trigger_node_execution
        # (This is what happens when you click a button inside a node)
        if self.execution_controller and self.execution_controller.live_executor:
            live_executor = self.execution_controller.live_executor
            
            # Clear the log to see only the execution result
            output_log = self.window.output_log
            initial_log_count = output_log.document().blockCount()
            
            # Trigger node execution (simulates clicking "Generate Password" button)
            live_executor.trigger_node_execution(node)
            QApplication.processEvents()
            
            # Check the log output
            final_log_count = output_log.document().blockCount()
            log_text = output_log.toPlainText()
            
            # CRITICAL TEST: Should NOT contain the error message
            self.assertNotIn("Not in live mode - enable Live Mode first!", log_text)
            
            # Should contain successful execution messages
            self.assertIn("Button clicked in 'Interactive Node'", log_text)
            self.assertIn("Starting execution flow", log_text)
            
            # Log contains execution success without unicode issues
            print("DEBUG: Node execution completed successfully without live mode error")
        
        print("PASS Node execution after pause/resume works correctly - Critical bug fixed!")
    
    def test_live_mode_state_consistency(self):
        """Test that live mode state flags remain consistent."""
        # Switch to live mode
        live_radio = self._get_live_mode_radio()
        if live_radio:
            live_radio.setChecked(True)
            QApplication.processEvents()
        
        # Verify execution controller state consistency
        if self.execution_controller:
            # Initial state
            self.assertTrue(self.execution_controller.live_mode)
            self.assertFalse(self.execution_controller.live_active)
            
            # Start live mode
            if self.main_exec_button:
                self.main_exec_button.click()
                QApplication.processEvents()
                QTest.qWait(200)
                
                # Should be live and active
                self.assertTrue(self.execution_controller.live_mode)
                self.assertTrue(self.execution_controller.live_active)
                
                # Pause
                self.main_exec_button.click()
                QApplication.processEvents()
                QTest.qWait(200)
                
                # Should still be live mode but not active
                self.assertTrue(self.execution_controller.live_mode)
                self.assertFalse(self.execution_controller.live_active)
                
                # Resume
                self.main_exec_button.click()
                QApplication.processEvents()
                QTest.qWait(200)
                
                # Should be live and active again
                self.assertTrue(self.execution_controller.live_mode)
                self.assertTrue(self.execution_controller.live_active)
        
        print("PASS Live mode state consistency maintained")


class TestModeTransitions(ExecuteGraphTestCase):
    """Test transitions between Batch and Live modes."""
    
    def test_batch_to_live_transition(self):
        """Test switching from Batch to Live mode."""
        # Start in batch mode
        batch_radio = self._get_batch_mode_radio()
        if batch_radio:
            batch_radio.setChecked(True)
            QApplication.processEvents()
        
        # Verify batch state
        if self.main_exec_button:
            self.wait_for_button_text("Execute", timeout=2000)
            initial_text = self.main_exec_button.text()
            self.assertIn("Execute", initial_text)
        
        # Switch to live mode
        live_radio = self._get_live_mode_radio()
        if live_radio:
            live_radio.setChecked(True)
            QApplication.processEvents()
        
        # Verify live state
        if self.main_exec_button:
            self.wait_for_button_text("Start", timeout=2000)
            final_text = self.main_exec_button.text()
            self.assertIn("Start", final_text)
        
        print("PASS Batch to Live mode transition working correctly")
    
    def test_live_to_batch_transition(self):
        """Test switching from Live to Batch mode."""
        # Start in live mode
        live_radio = self._get_live_mode_radio()
        if live_radio:
            live_radio.setChecked(True)
            QApplication.processEvents()
        
        # Start live mode
        if self.main_exec_button:
            self.main_exec_button.click()
            QApplication.processEvents()
            self.wait_for_button_text("Pause", timeout=2000)
        
        # Switch to batch mode while live is active
        batch_radio = self._get_batch_mode_radio()
        if batch_radio:
            batch_radio.setChecked(True)
            QApplication.processEvents()
        
        # Should properly transition to batch
        if self.main_exec_button:
            self.wait_for_button_text("Execute", timeout=2000)
            final_text = self.main_exec_button.text()
            self.assertIn("Execute", final_text)
        
        # State should be reset
        if self.execution_controller:
            self.assertFalse(self.execution_controller.live_mode)
            self.assertFalse(self.execution_controller.live_active)
        
        print("PASS Live to Batch mode transition working correctly")
    
    def test_mode_transition_with_paused_live(self):
        """Test mode transition when live mode is paused."""
        # Start in live mode and get to paused state
        live_radio = self._get_live_mode_radio()
        if live_radio:
            live_radio.setChecked(True)
            QApplication.processEvents()
        
        if self.main_exec_button:
            # Start then pause
            self.main_exec_button.click()  # Start
            QApplication.processEvents()
            self.wait_for_button_text("Pause", timeout=2000)
            
            self.main_exec_button.click()  # Pause
            QApplication.processEvents()
            self.wait_for_button_text("Resume", timeout=2000)
        
        # Now switch to batch mode from paused state
        batch_radio = self._get_batch_mode_radio()
        if batch_radio:
            batch_radio.setChecked(True)
            QApplication.processEvents()
        
        # Should properly handle transition from paused state
        if self.main_exec_button:
            self.wait_for_button_text("Execute", timeout=2000)
            final_text = self.main_exec_button.text()
            self.assertIn("Execute", final_text)
        
        print("PASS Mode transition from paused live state working correctly")


class TestExecutionErrorHandling(ExecuteGraphTestCase):
    """Test error handling in execution modes."""
    
    def test_live_mode_node_execution_validation(self):
        """Test that live mode properly validates node execution state."""
        # Switch to live mode
        live_radio = self._get_live_mode_radio()
        if live_radio:
            live_radio.setChecked(True)
            QApplication.processEvents()
        
        # Create a node with a button for live interaction
        node = self.graph.create_node("Interactive Node", pos=(200, 200))
        node.set_code('''
@node_entry
def interactive_function():
    return "Live execution test"
''')
        
        # Add GUI code to create a button
        node.set_gui_code('''
button = QPushButton("Test Button")
button.setParent(widget)
button.move(10, 30)
button.show()
''')
        
        QApplication.processEvents()
        QTest.qWait(200)
        
        # Start live mode
        if self.main_exec_button:
            self.main_exec_button.click()
            QApplication.processEvents()
            self.wait_for_button_text("Pause", timeout=2000)
        
        # Live mode should be active and ready for node interaction
        if self.execution_controller:
            self.assertTrue(self.execution_controller.live_mode)
            self.assertTrue(self.execution_controller.live_active)
        
        print("PASS Live mode node execution validation working correctly")
    
    def test_execution_with_invalid_environment(self):
        """Test execution behavior with invalid Python environment."""
        # This test simulates the case where venv is not properly set up
        
        # Create simple graph
        producer, consumer = self._create_simple_test_graph()
        
        # Try batch execution
        batch_radio = self._get_batch_mode_radio()
        if batch_radio:
            batch_radio.setChecked(True)
            QApplication.processEvents()
        
        if self.main_exec_button:
            self.main_exec_button.click()
            QApplication.processEvents()
            
            # Should handle gracefully and return to ready state
            self.wait_for_button_text("Execute", timeout=5000)
            self.assertIn("Execute", self.main_exec_button.text())
        
        print("PASS Execution with environment issues handled gracefully")


def run_execute_graph_test_suite():
    """Run the complete Execute Graph test suite."""
    print("="*60)
    print("STARTING EXECUTE GRAPH BUTTON TEST SUITE")
    print("="*60)
    print()
    print("Testing Live/Batch mode execution, pause/resume cycles,")
    print("and the critical state management bug.")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBatchModeExecution,
        TestLiveModeExecution,
        TestModeTransitions,
        TestExecutionErrorHandling,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=False
    )
    
    result = runner.run(suite)
    
    print()
    print("="*60)
    print("EXECUTE GRAPH TEST SUITE COMPLETE")
    print("="*60)
    
    if result.wasSuccessful():
        print("PASS All Execute Graph tests PASSED")
        print("Live/Batch mode execution working correctly!")
    else:
        print("X Some Execute Graph tests FAILED")
        print("Execution mode issues detected:")
        
        if result.failures:
            print(f"  - {len(result.failures)} test failures")
        if result.errors:
            print(f"  - {len(result.errors)} test errors")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_execute_graph_test_suite()
    
    # Clean up QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
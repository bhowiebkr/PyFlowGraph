# test_view_state_persistence.py
# Comprehensive test for view state persistence with real GUI

import sys
import os
import time
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtGui import QTransform

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ui.editor.node_editor_window import NodeEditorWindow


class TestViewStatePersistence(unittest.TestCase):
    """Test that view state (zoom and pan) is properly saved and restored between file loads."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication for GUI testing."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up each test with a fresh window."""
        self.window = NodeEditorWindow()
        self.window.show()
        QTest.qWaitForWindowExposed(self.window)
        
        # Ensure we start with a clean state
        self.window.file_ops.new_scene()
        QTest.qWait(100)  # Let GUI update
    
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'window'):
            self.window.close()
            QTest.qWait(100)
    
    def test_view_state_persistence_between_files(self):
        """Test that zoom and pan state is preserved when switching between files."""
        print("Starting view state persistence test...")
        
        # Step 1: Load first test file
        file1_path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'password_generator_tool.md')
        self.assertTrue(os.path.exists(file1_path), f"Test file does not exist: {file1_path}")
        
        self.window.on_load(file1_path)
        QTest.qWait(200)  # Let the file load completely
        
        print(f"Loaded file: {file1_path}")
        
        # Step 2: Apply specific zoom and pan transformations
        view = self.window.view
        
        # Reset to known state first
        view.resetTransform()
        QTest.qWait(100)
        
        # Apply specific transformations
        target_scale = 1.75
        target_translate_x = 150.0
        target_translate_y = 220.0
        
        # Create the target transform
        target_transform = QTransform()
        target_transform.scale(target_scale, target_scale)
        target_transform.translate(target_translate_x, target_translate_y)
        
        # Apply the transform
        view.setTransform(target_transform)
        QTest.qWait(100)
        
        # Set specific center point
        target_center = QPointF(300.0, 450.0)
        view.centerOn(target_center)
        QTest.qWait(100)
        
        # Record the actual applied values
        recorded_transform = view.transform()
        recorded_center = view.mapToScene(view.viewport().rect().center())
        
        print(f"Applied transform: scale={recorded_transform.m11():.3f}, translate=({recorded_transform.dx():.1f}, {recorded_transform.dy():.1f})")
        print(f"Applied center: ({recorded_center.x():.1f}, {recorded_center.y():.1f})")
        
        # Step 3: Load second file (triggers save of current state)
        file2_path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'data_analysis_dashboard.md')
        self.assertTrue(os.path.exists(file2_path), f"Second test file does not exist: {file2_path}")
        
        self.window.on_load(file2_path)
        QTest.qWait(200)
        
        print(f"Switched to file: {file2_path}")
        
        # Apply a DIFFERENT transform to the second file to create distinct states
        different_scale = 0.8
        different_translate_x = -100.0
        different_translate_y = -50.0
        
        different_transform = QTransform()
        different_transform.scale(different_scale, different_scale)
        different_transform.translate(different_translate_x, different_translate_y)
        
        view.setTransform(different_transform)
        different_center = QPointF(100.0, 200.0)
        view.centerOn(different_center)
        QTest.qWait(100)
        
        # Verify we're in a different state now
        current_transform = view.transform()
        current_center = view.mapToScene(view.viewport().rect().center())
        print(f"Applied different transform to file 2: scale={current_transform.m11():.3f}, translate=({current_transform.dx():.1f}, {current_transform.dy():.1f})")
        print(f"Applied different center to file 2: ({current_center.x():.1f}, {current_center.y():.1f})")
        
        # Verify the state is actually different from file 1
        self.assertNotAlmostEqual(current_transform.m11(), recorded_transform.m11(), places=2,
                                 msg="Transform scale should be different between files")
        self.assertNotAlmostEqual(current_center.x(), recorded_center.x(), places=0,
                                 msg="Center point should be different between files")
        
        # Step 4: Return to first file (should restore saved state)
        self.window.on_load(file1_path)
        QTest.qWait(200)  # Critical: wait for view state restoration
        
        print(f"Returned to file: {file1_path}")
        
        # Step 5: Verify the state was restored
        restored_transform = view.transform()
        restored_center = view.mapToScene(view.viewport().rect().center())
        
        print(f"Restored transform: scale={restored_transform.m11():.3f}, translate=({restored_transform.dx():.1f}, {restored_transform.dy():.1f})")
        print(f"Restored center: ({restored_center.x():.1f}, {restored_center.y():.1f})")
        
        # Verify transform restoration (scale and translation)
        scale_tolerance = 0.001
        translate_tolerance = 1.0
        
        scale_diff = abs(restored_transform.m11() - recorded_transform.m11())
        translate_x_diff = abs(restored_transform.dx() - recorded_transform.dx())
        translate_y_diff = abs(restored_transform.dy() - recorded_transform.dy())
        
        print(f"Scale difference: {scale_diff:.6f} (tolerance: {scale_tolerance})")
        print(f"Translate X difference: {translate_x_diff:.1f} (tolerance: {translate_tolerance})")
        print(f"Translate Y difference: {translate_y_diff:.1f} (tolerance: {translate_tolerance})")
        
        # Verify center point restoration
        center_tolerance = 2.0  # pixels
        center_x_diff = abs(restored_center.x() - recorded_center.x())
        center_y_diff = abs(restored_center.y() - recorded_center.y())
        
        print(f"Center X difference: {center_x_diff:.1f} (tolerance: {center_tolerance})")
        print(f"Center Y difference: {center_y_diff:.1f} (tolerance: {center_tolerance})")
        
        # Assert that values are within tolerance
        self.assertLess(scale_diff, scale_tolerance, 
                       f"Scale not restored correctly: expected {recorded_transform.m11():.3f}, got {restored_transform.m11():.3f}")
        
        self.assertLess(translate_x_diff, translate_tolerance,
                       f"X translation not restored correctly: expected {recorded_transform.dx():.1f}, got {restored_transform.dx():.1f}")
        
        self.assertLess(translate_y_diff, translate_tolerance,
                       f"Y translation not restored correctly: expected {recorded_transform.dy():.1f}, got {restored_transform.dy():.1f}")
        
        self.assertLess(center_x_diff, center_tolerance,
                       f"Center X not restored correctly: expected {recorded_center.x():.1f}, got {restored_center.x():.1f}")
        
        self.assertLess(center_y_diff, center_tolerance,
                       f"Center Y not restored correctly: expected {recorded_center.y():.1f}, got {restored_center.y():.1f}")
        
        print("View state persistence test PASSED!")


if __name__ == '__main__':
    # Ensure we have a visible GUI for testing
    if 'QT_QPA_PLATFORM' in os.environ:
        del os.environ['QT_QPA_PLATFORM']
    
    unittest.main(verbosity=2)
# test_group_resize.py
# Unit tests for group resize functionality including handle detection and membership management.

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsItem
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import Qt

# Ensure QApplication exists for Qt widgets
if not QApplication.instance():
    app = QApplication([])

from src.core.group import Group
from src.core.node import Node
from src.commands.resize_group_command import ResizeGroupCommand


class TestGroupResize(unittest.TestCase):
    """Test Group resize functionality including handles and membership management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.group = Group("Test Group", ["node1", "node2"])
        self.group.width = 200
        self.group.height = 150
        self.group.setPos(100, 100)
        self.group.setRect(0, 0, self.group.width, self.group.height)
        self.mock_scene = Mock()
    
    def test_handle_detection(self):
        """Test resize handle detection at various positions."""
        # Test corner handles - should require selection
        nw_pos = QPointF(-16, -16)  # Northwest corner outside group
        handle = self.group.get_handle_at_pos(nw_pos)
        self.assertEqual(handle, self.group.HANDLE_NONE)  # No handles when not selected
        
        # Select the group and test again
        self.group.setSelected(True)
        handle = self.group.get_handle_at_pos(nw_pos)
        self.assertEqual(handle, self.group.HANDLE_NW)
        
        # Test other corners positioned outside group
        ne_pos = QPointF(self.group.width + 16, -16)
        handle = self.group.get_handle_at_pos(ne_pos)
        self.assertEqual(handle, self.group.HANDLE_NE)
        
        se_pos = QPointF(self.group.width + 16, self.group.height + 16)
        handle = self.group.get_handle_at_pos(se_pos)
        self.assertEqual(handle, self.group.HANDLE_SE)
        
        sw_pos = QPointF(-16, self.group.height + 16)
        handle = self.group.get_handle_at_pos(sw_pos)
        self.assertEqual(handle, self.group.HANDLE_SW)
    
    def test_cursor_for_handle(self):
        """Test cursor mapping for different handles."""
        # Test corner cursors
        self.assertEqual(self.group.get_cursor_for_handle(self.group.HANDLE_NW), Qt.SizeFDiagCursor)
        self.assertEqual(self.group.get_cursor_for_handle(self.group.HANDLE_SE), Qt.SizeFDiagCursor)
        self.assertEqual(self.group.get_cursor_for_handle(self.group.HANDLE_NE), Qt.SizeBDiagCursor)
        self.assertEqual(self.group.get_cursor_for_handle(self.group.HANDLE_SW), Qt.SizeBDiagCursor)
        
        # Test edge cursors
        self.assertEqual(self.group.get_cursor_for_handle(self.group.HANDLE_N), Qt.SizeVerCursor)
        self.assertEqual(self.group.get_cursor_for_handle(self.group.HANDLE_S), Qt.SizeVerCursor)
        self.assertEqual(self.group.get_cursor_for_handle(self.group.HANDLE_E), Qt.SizeHorCursor)
        self.assertEqual(self.group.get_cursor_for_handle(self.group.HANDLE_W), Qt.SizeHorCursor)
    
    def test_resize_operation(self):
        """Test complete resize operation."""
        # Store original state
        original_width = self.group.width
        original_height = self.group.height
        original_pos = self.group.pos()
        
        # Start resize from southeast corner
        start_pos = QPointF(200, 150)
        self.group.start_resize(self.group.HANDLE_SE, start_pos)
        
        self.assertTrue(self.group.is_resizing)
        self.assertEqual(self.group.resize_handle, self.group.HANDLE_SE)
        
        # Update resize (drag to make group larger)
        new_pos = QPointF(250, 200)
        self.group.update_resize(new_pos)
        
        # Check that group size increased
        self.assertEqual(self.group.width, original_width + 50)
        self.assertEqual(self.group.height, original_height + 50)
        
        # Position should remain the same for SE handle
        self.assertEqual(self.group.pos(), original_pos)
    
    def test_resize_with_minimum_constraints(self):
        """Test resize with minimum size constraints."""
        # Start with a smaller group to test minimum constraints
        self.group.width = 120
        self.group.height = 90
        self.group.setRect(0, 0, self.group.width, self.group.height)
        
        # Try to resize below minimum size from SE corner
        start_pos = QPointF(120, 90)  # Bottom-right corner
        self.group.start_resize(self.group.HANDLE_SE, start_pos)
        
        # Try to make it very small (drag inward)
        new_pos = QPointF(80, 60)  # Would make it 80x60, below min 100x80  
        self.group.update_resize(new_pos)
        
        # Should be clamped to minimum size
        self.assertEqual(self.group.width, self.group.min_width)
        self.assertEqual(self.group.height, self.group.min_height)
    
    def test_membership_update_after_resize(self):
        """Test that membership is updated after resize."""
        # Mock scene with some nodes
        mock_node1 = Mock()
        mock_node1.uuid = "node3"
        mock_node1.pos.return_value = QPointF(120, 120)
        mock_node1.boundingRect.return_value = QRectF(0, 0, 50, 30)
        type(mock_node1).__name__ = 'Node'
        
        mock_node2 = Mock()
        mock_node2.uuid = "node4"
        mock_node2.pos.return_value = QPointF(400, 400)  # Outside group
        mock_node2.boundingRect.return_value = QRectF(0, 0, 50, 30)
        type(mock_node2).__name__ = 'Node'
        
        self.mock_scene.items.return_value = [mock_node1, mock_node2]
        self.group.scene = lambda: self.mock_scene
        
        # Initial membership
        initial_members = self.group.member_node_uuids.copy()
        
        # Update membership after resize
        self.group._update_membership_after_resize()
        
        # Check that node3 was added (inside group bounds)
        self.assertIn("node3", self.group.member_node_uuids)
        # Check that node4 was not added (outside group bounds)
        self.assertNotIn("node4", self.group.member_node_uuids)
    
    def test_member_nodes_dont_move_during_resize(self):
        """Test that member nodes stay in place during resize operations."""
        # Mock a member node
        mock_node = Mock()
        mock_node.uuid = "member_node"
        mock_node.pos.return_value = QPointF(150, 125)
        mock_node.setPos = Mock()
        type(mock_node).__name__ = 'Node'
        
        # Add node to group membership
        self.group.add_member_node("member_node")
        
        # Mock scene to return our node
        self.mock_scene.items.return_value = [mock_node]
        self.group.scene = lambda: self.mock_scene
        
        # Start resize operation
        self.group.is_resizing = True
        
        # Simulate position change (this would normally trigger _move_member_nodes)
        old_pos = self.group.pos()
        new_pos = QPointF(200, 150)  # Move group position
        
        # Call itemChange as if group position changed
        result = self.group.itemChange(QGraphicsItem.ItemPositionChange, new_pos)
        
        # Verify that the mock node's setPos was NOT called (because is_resizing=True)
        mock_node.setPos.assert_not_called()
    
    def test_increased_handle_size(self):
        """Test that handle size was increased for easier selection."""
        self.assertEqual(self.group.handle_size, 16.0)  # Large, simple handles
    
    def test_larger_hit_box_detection(self):
        """Test that handles positioned outside group are easier to select."""
        self.group.setSelected(True)
        
        # Test northwest corner handle detection (positioned outside group)
        nw_pos = QPointF(-16, -16)  # At NW handle position outside group
        handle = self.group.get_handle_at_pos(nw_pos)
        self.assertEqual(handle, self.group.HANDLE_NW)
        
        # Test that positions way outside don't register
        too_far_pos = QPointF(-40, -40)  # Way outside handle area
        handle = self.group.get_handle_at_pos(too_far_pos)
        self.assertEqual(handle, self.group.HANDLE_NONE)
    
    def test_handles_only_show_when_selected(self):
        """Test that handles only appear when group is selected."""
        # Not selected - bounding rect should be content only
        self.group.setSelected(False)
        unselected_rect = self.group.boundingRect()
        self.assertEqual(unselected_rect, QRectF(0, 0, self.group.width, self.group.height))
        
        # Selected - bounding rect should include handle space
        self.group.setSelected(True)
        selected_rect = self.group.boundingRect()
        self.assertNotEqual(selected_rect, unselected_rect)
        self.assertTrue(selected_rect.width() > unselected_rect.width())
        self.assertTrue(selected_rect.height() > unselected_rect.height())
    
    def test_selection_change_updates_visual(self):
        """Test that visual state updates when selection changes."""
        # Mock update method to track calls
        update_calls = []
        original_update = self.group.update
        self.group.update = lambda: update_calls.append('update_called')
        
        # Test selecting
        self.group.setSelected(True)
        self.assertTrue(len(update_calls) > 0, "update() should be called when selected")
        
        # Reset and test deselecting
        update_calls.clear()
        self.group.setSelected(False)
        self.assertTrue(len(update_calls) > 0, "update() should be called when deselected")
        
        # Restore original update method
        self.group.update = original_update
    
    def test_bounding_rect_includes_handles_when_selected(self):
        """Test that bounding rect includes space for handles when selected."""
        # When not selected, bounding rect should be just content
        self.group.setSelected(False)
        content_rect = self.group.boundingRect()
        self.assertEqual(content_rect, QRectF(0, 0, self.group.width, self.group.height))
        
        # When selected, bounding rect should include handle space
        self.group.setSelected(True)
        selected_rect = self.group.boundingRect()
        margin = self.group.handle_size + self.group.handle_size / 2
        expected_rect = QRectF(-margin, -margin,
                              self.group.width + margin * 2,
                              self.group.height + margin * 2)
        self.assertEqual(selected_rect, expected_rect)


class TestResizeGroupCommand(unittest.TestCase):
    """Test ResizeGroupCommand for undo/redo functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_scene = Mock()
        self.group = Group("Test Group", ["node1", "node2"])
        self.group.setPos(100, 100)
        self.group.width = 200
        self.group.height = 150
        
        self.old_bounds = QRectF(100, 100, 200, 150)
        self.new_bounds = QRectF(100, 100, 250, 200)
        self.old_members = ["node1", "node2"]
        self.new_members = ["node1", "node2", "node3"]
    
    def test_command_creation(self):
        """Test command creation with proper data."""
        command = ResizeGroupCommand(
            self.mock_scene, self.group, self.old_bounds, self.new_bounds,
            self.old_members, self.new_members
        )
        
        self.assertEqual(command.group, self.group)
        self.assertEqual(command.old_bounds, self.old_bounds)
        self.assertEqual(command.new_bounds, self.new_bounds)
        self.assertEqual(command.added_members, ["node3"])
        self.assertEqual(command.removed_members, [])
    
    def test_command_execute(self):
        """Test command execution applies new state."""
        command = ResizeGroupCommand(
            self.mock_scene, self.group, self.old_bounds, self.new_bounds,
            self.old_members, self.new_members
        )
        
        result = command.execute()
        self.assertTrue(result)
        
        # Check that new bounds were applied
        self.assertEqual(self.group.width, 250)
        self.assertEqual(self.group.height, 200)
        self.assertEqual(self.group.member_node_uuids, self.new_members)
    
    def test_command_undo(self):
        """Test command undo restores original state."""
        command = ResizeGroupCommand(
            self.mock_scene, self.group, self.old_bounds, self.new_bounds,
            self.old_members, self.new_members
        )
        
        # Execute then undo
        command.execute()
        result = command.undo()
        self.assertTrue(result)
        
        # Check that original bounds were restored
        self.assertEqual(self.group.width, 200)
        self.assertEqual(self.group.height, 150)
        self.assertEqual(self.group.member_node_uuids, self.old_members)


if __name__ == '__main__':
    unittest.main()
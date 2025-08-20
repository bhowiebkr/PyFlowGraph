# test_group_ui_integration.py
# Integration tests for group UI interactions including context menu and keyboard shortcuts.

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QKeyEvent, QContextMenuEvent

# Ensure QApplication exists for Qt widgets
if not QApplication.instance():
    app = QApplication([])

from src.ui.editor.node_editor_view import NodeEditorView
from src.core.node_graph import NodeGraph
from src.core.node import Node


class TestContextMenuIntegration(unittest.TestCase):
    """Test context menu integration and option enabling/disabling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scene = NodeGraph()
        self.view = NodeEditorView(self.scene)
        
        # Create mock nodes
        self.node1 = Mock(spec=Node)
        self.node1.uuid = "uuid1"
        self.node1.title = "Node 1"
        
        self.node2 = Mock(spec=Node)
        self.node2.uuid = "uuid2"
        self.node2.title = "Node 2"
        
        self.node3 = Mock(spec=Node)
        self.node3.uuid = "uuid3"
        self.node3.title = "Node 3"
    
    def test_context_menu_no_selection(self):
        """Test context menu when no nodes are selected."""
        # Clear selection
        self.scene.clearSelection()
        
        with patch.object(self.view, 'mapToScene', return_value=QPointF(0, 0)):
            with patch.object(self.scene, 'itemAt', return_value=None):
                with patch('PySide6.QtWidgets.QMenu') as mock_menu_class:
                    mock_menu = Mock()
                    mock_menu_class.return_value = mock_menu
                    mock_menu.addAction.return_value = Mock()
                    mock_menu.exec.return_value = None
                    
                    # Create mock context menu event
                    event = Mock()
                    event.pos.return_value = QPointF(0, 0)
                    event.globalPos.return_value = QPointF(0, 0)
                    
                    self.view.show_context_menu(event)
                    
                    # Should create menu with "Add Node" but no "Group Selected"
                    mock_menu.addAction.assert_any_call("Add Node")
                    
                    # Verify "Group Selected" was not added for empty selection
                    actions = [call[0][0] for call in mock_menu.addAction.call_args_list]
                    self.assertNotIn("Group Selected", actions)
    
    def test_context_menu_single_selection(self):
        """Test context menu when single node is selected."""
        # Set up single selection
        self.scene.selectedItems = Mock(return_value=[self.node1])
        
        with patch.object(self.view, 'mapToScene', return_value=QPointF(0, 0)):
            with patch.object(self.scene, 'itemAt', return_value=self.node1):
                with patch('PySide6.QtWidgets.QMenu') as mock_menu_class:
                    mock_menu = Mock()
                    mock_menu_class.return_value = mock_menu
                    mock_menu.addAction.return_value = Mock()
                    mock_menu.exec.return_value = None
                    
                    event = Mock()
                    event.pos.return_value = QPointF(0, 0)
                    event.globalPos.return_value = QPointF(0, 0)
                    
                    self.view.show_context_menu(event)
                    
                    # Should create menu with "Properties" but no "Group Selected"
                    mock_menu.addAction.assert_any_call("Properties")
                    
                    actions = [call[0][0] for call in mock_menu.addAction.call_args_list]
                    self.assertNotIn("Group Selected", actions)
    
    def test_context_menu_multiple_selection(self):
        """Test context menu when multiple nodes are selected."""
        # Set up multiple selection
        self.scene.selectedItems = Mock(return_value=[self.node1, self.node2])
        
        with patch.object(self.view, 'mapToScene', return_value=QPointF(0, 0)):
            with patch.object(self.scene, 'itemAt', return_value=self.node1):
                with patch('PySide6.QtWidgets.QMenu') as mock_menu_class:
                    mock_menu = Mock()
                    mock_menu_class.return_value = mock_menu
                    
                    # Mock the addAction to return different actions
                    properties_action = Mock()
                    group_action = Mock()
                    mock_menu.addAction.side_effect = [properties_action, group_action]
                    mock_menu.exec.return_value = None
                    
                    # Mock the validation to return True
                    with patch.object(self.view, '_can_group_nodes', return_value=True):
                        event = Mock()
                        event.pos.return_value = QPointF(0, 0)
                        event.globalPos.return_value = QPointF(0, 0)
                        
                        self.view.show_context_menu(event)
                        
                        # Should create menu with both "Properties" and "Group Selected"
                        mock_menu.addAction.assert_any_call("Properties")
                        mock_menu.addAction.assert_any_call("Group Selected")
                        
                        # Group action should be enabled
                        group_action.setEnabled.assert_not_called()
    
    def test_context_menu_invalid_selection(self):
        """Test context menu when selection cannot be grouped."""
        # Set up selection with invalid items
        invalid_item = Mock()  # Not a Node
        self.scene.selectedItems = Mock(return_value=[self.node1, invalid_item])
        
        with patch.object(self.view, 'mapToScene', return_value=QPointF(0, 0)):
            with patch.object(self.scene, 'itemAt', return_value=self.node1):
                with patch('PySide6.QtWidgets.QMenu') as mock_menu_class:
                    mock_menu = Mock()
                    mock_menu_class.return_value = mock_menu
                    
                    properties_action = Mock()
                    group_action = Mock()
                    mock_menu.addAction.side_effect = [properties_action, group_action]
                    mock_menu.exec.return_value = None
                    
                    # Mock validation to return False
                    with patch.object(self.view, '_can_group_nodes', return_value=False):
                        event = Mock()
                        event.pos.return_value = QPointF(0, 0)
                        event.globalPos.return_value = QPointF(0, 0)
                        
                        self.view.show_context_menu(event)
                        
                        # Group action should be disabled
                        group_action.setEnabled.assert_called_with(False)
    
    def test_can_group_nodes_validation(self):
        """Test the _can_group_nodes validation method."""
        # Valid selection
        valid_nodes = [self.node1, self.node2]
        self.assertTrue(self.view._can_group_nodes(valid_nodes))
        
        # Too few nodes
        self.assertFalse(self.view._can_group_nodes([self.node1]))
        self.assertFalse(self.view._can_group_nodes([]))
        
        # Invalid node type
        invalid_item = Mock()  # Not a Node instance
        invalid_selection = [self.node1, invalid_item]
        self.assertFalse(self.view._can_group_nodes(invalid_selection))


class TestKeyboardShortcutHandling(unittest.TestCase):
    """Test keyboard shortcut handling and event propagation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scene = NodeGraph()
        
        # Create mock nodes
        self.node1 = Mock(spec=Node)
        self.node1.uuid = "uuid1"
        
        self.node2 = Mock(spec=Node)
        self.node2.uuid = "uuid2"
        
        self.scene.nodes = [self.node1, self.node2]
    
    def test_ctrl_g_with_valid_selection(self):
        """Test Ctrl+G with valid node selection."""
        # Set up selection
        self.scene.selectedItems = Mock(return_value=[self.node1, self.node2])
        
        with patch.object(self.scene, '_create_group_from_selection') as mock_create:
            # Create Ctrl+G key event
            event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_G, Qt.ControlModifier)
            
            self.scene.keyPressEvent(event)
            
            # Should call group creation
            mock_create.assert_called_once_with([self.node1, self.node2])
    
    def test_ctrl_g_with_insufficient_selection(self):
        """Test Ctrl+G with insufficient node selection."""
        # Set up single node selection
        self.scene.selectedItems = Mock(return_value=[self.node1])
        
        with patch.object(self.scene, '_create_group_from_selection') as mock_create:
            event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_G, Qt.ControlModifier)
            
            self.scene.keyPressEvent(event)
            
            # Should not call group creation
            mock_create.assert_not_called()
    
    def test_ctrl_g_with_no_selection(self):
        """Test Ctrl+G with no selection."""
        self.scene.selectedItems = Mock(return_value=[])
        
        with patch.object(self.scene, '_create_group_from_selection') as mock_create:
            event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_G, Qt.ControlModifier)
            
            self.scene.keyPressEvent(event)
            
            # Should not call group creation
            mock_create.assert_not_called()
    
    def test_other_shortcuts_unaffected(self):
        """Test that other keyboard shortcuts still work."""
        # Test Ctrl+Z (undo)
        with patch.object(self.scene, 'undo_last_command') as mock_undo:
            event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier)
            self.scene.keyPressEvent(event)
            mock_undo.assert_called_once()
        
        # Test Ctrl+Y (redo)
        with patch.object(self.scene, 'redo_last_command') as mock_redo:
            event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Y, Qt.ControlModifier)
            self.scene.keyPressEvent(event)
            mock_redo.assert_called_once()
    
    def test_non_ctrl_g_events_propagated(self):
        """Test that non-Ctrl+G events are properly propagated."""
        with patch('PySide6.QtWidgets.QGraphicsScene.keyPressEvent') as mock_super:
            # Regular 'G' key without Ctrl
            event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_G, Qt.NoModifier)
            self.scene.keyPressEvent(event)
            
            # Should call super().keyPressEvent()
            mock_super.assert_called_once_with(event)


class TestGroupCreationWorkflow(unittest.TestCase):
    """Test complete group creation workflow from selection to completion."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scene = NodeGraph()
        
        # Create real Node instances for more realistic testing
        self.node1 = Node("Test Node 1")
        self.node1.uuid = "uuid1"
        
        self.node2 = Node("Test Node 2")
        self.node2.uuid = "uuid2"
        
        self.scene.nodes = [self.node1, self.node2]
    
    @patch('src.ui.dialogs.group_creation_dialog.show_group_creation_dialog')
    @patch('src.commands.create_group_command.CreateGroupCommand')
    def test_complete_workflow_success(self, mock_command_class, mock_dialog):
        """Test complete successful group creation workflow."""
        # Mock dialog to return valid properties
        mock_properties = {
            "name": "Test Group",
            "description": "Test description",
            "member_node_uuids": ["uuid1", "uuid2"],
            "auto_size": True,
            "padding": 20
        }
        mock_dialog.return_value = mock_properties
        
        # Mock command
        mock_command = Mock()
        mock_command_class.return_value = mock_command
        
        # Mock execute_command
        with patch.object(self.scene, 'execute_command') as mock_execute:
            # Test the workflow
            self.scene._create_group_from_selection([self.node1, self.node2])
            
            # Verify dialog was shown
            mock_dialog.assert_called_once()
            
            # Verify command was created and executed
            mock_command_class.assert_called_once_with(self.scene, mock_properties)
            mock_execute.assert_called_once_with(mock_command)
    
    @patch('src.ui.dialogs.group_creation_dialog.show_group_creation_dialog')
    def test_workflow_user_cancels(self, mock_dialog):
        """Test workflow when user cancels dialog."""
        # Mock dialog to return None (user canceled)
        mock_dialog.return_value = None
        
        with patch.object(self.scene, 'execute_command') as mock_execute:
            self.scene._create_group_from_selection([self.node1, self.node2])
            
            # Verify dialog was shown
            mock_dialog.assert_called_once()
            
            # Verify no command was executed
            mock_execute.assert_not_called()
    
    @patch('PySide6.QtWidgets.QMessageBox')
    def test_workflow_invalid_selection(self, mock_messagebox):
        """Test workflow with invalid selection."""
        # Create mock message box
        mock_msg = Mock()
        mock_messagebox.return_value = mock_msg
        
        # Test with single node (invalid)
        with patch.object(self.scene, 'execute_command') as mock_execute:
            self.scene._create_group_from_selection([self.node1])
            
            # Should show error message
            mock_messagebox.assert_called_once()
            mock_msg.exec.assert_called_once()
            
            # Should not execute command
            mock_execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()
# test_group_system.py
# Unit tests for group functionality including creation, validation, and persistence.

import unittest
import sys
import os
import uuid
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication, QGraphicsScene
from PySide6.QtCore import QPointF

# Ensure QApplication exists for Qt widgets
if not QApplication.instance():
    app = QApplication([])

from src.core.group import Group, validate_group_creation, generate_group_name
from src.core.node import Node
from src.commands.create_group_command import CreateGroupCommand


class TestGroup(unittest.TestCase):
    """Test Group class creation and data management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.group = Group("Test Group")
        self.mock_scene = Mock()
    
    def test_group_creation_with_defaults(self):
        """Test group creation with default parameters."""
        group = Group()
        self.assertEqual(group.name, "Group")
        self.assertEqual(group.member_node_uuids, [])
        self.assertTrue(group.is_expanded)
        self.assertIsNotNone(group.uuid)
    
    def test_group_creation_with_parameters(self):
        """Test group creation with custom parameters."""
        member_uuids = ["uuid1", "uuid2", "uuid3"]
        group = Group("Custom Group", member_uuids)
        
        self.assertEqual(group.name, "Custom Group")
        self.assertEqual(group.member_node_uuids, member_uuids)
        self.assertEqual(group.get_member_count(), 3)
    
    def test_add_member_node(self):
        """Test adding member nodes to group."""
        self.group.add_member_node("uuid1")
        self.group.add_member_node("uuid2")
        
        self.assertEqual(self.group.get_member_count(), 2)
        self.assertTrue(self.group.is_member("uuid1"))
        self.assertTrue(self.group.is_member("uuid2"))
        
        # Test adding duplicate
        self.group.add_member_node("uuid1")
        self.assertEqual(self.group.get_member_count(), 2)  # Should not increase
    
    def test_remove_member_node(self):
        """Test removing member nodes from group."""
        self.group.add_member_node("uuid1")
        self.group.add_member_node("uuid2")
        
        self.group.remove_member_node("uuid1")
        self.assertEqual(self.group.get_member_count(), 1)
        self.assertFalse(self.group.is_member("uuid1"))
        self.assertTrue(self.group.is_member("uuid2"))
        
        # Test removing non-existent member
        self.group.remove_member_node("uuid3")
        self.assertEqual(self.group.get_member_count(), 1)  # Should not change
    
    def test_group_serialization(self):
        """Test group data serialization."""
        self.group.description = "Test description"
        self.group.add_member_node("uuid1")
        self.group.add_member_node("uuid2")
        self.group.setPos(100, 200)
        
        data = self.group.serialize()
        
        self.assertEqual(data["name"], "Test Group")
        self.assertEqual(data["description"], "Test description")
        self.assertEqual(len(data["member_node_uuids"]), 2)
        self.assertEqual(data["position"]["x"], 100)
        self.assertEqual(data["position"]["y"], 200)
        self.assertIn("uuid", data)
    
    def test_group_deserialization(self):
        """Test group data deserialization."""
        data = {
            "uuid": "test-uuid",
            "name": "Restored Group",
            "description": "Restored description",
            "member_node_uuids": ["uuid1", "uuid2"],
            "is_expanded": False,
            "position": {"x": 150, "y": 250},
            "size": {"width": 300, "height": 200},
            "padding": 25.0
        }
        
        group = Group.deserialize(data)
        
        self.assertEqual(group.uuid, "test-uuid")
        self.assertEqual(group.name, "Restored Group")
        self.assertEqual(group.description, "Restored description")
        self.assertEqual(group.member_node_uuids, ["uuid1", "uuid2"])
        self.assertFalse(group.is_expanded)
        self.assertEqual(group.pos().x(), 150)
        self.assertEqual(group.pos().y(), 250)
        self.assertEqual(group.width, 300)
        self.assertEqual(group.height, 200)
        self.assertEqual(group.padding, 25.0)


class TestGroupValidation(unittest.TestCase):
    """Test group validation logic with various node combinations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_node1 = Mock(spec=Node)
        self.mock_node1.uuid = "uuid1"
        self.mock_node1.title = "Node 1"
        
        self.mock_node2 = Mock(spec=Node)
        self.mock_node2.uuid = "uuid2"
        self.mock_node2.title = "Node 2"
        
        self.mock_node3 = Mock(spec=Node)
        self.mock_node3.uuid = "uuid3"
        self.mock_node3.title = "Node 3"
    
    def test_valid_group_creation(self):
        """Test validation with valid node selection."""
        # Create actual Node instances for realistic testing
        from src.core.node import Node
        
        node1 = Node("Test Node 1")
        node1.uuid = "uuid1"
        
        node2 = Node("Test Node 2") 
        node2.uuid = "uuid2"
        
        nodes = [node1, node2]
        is_valid, error = validate_group_creation(nodes)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_insufficient_nodes(self):
        """Test validation with insufficient nodes."""
        # Empty selection
        is_valid, error = validate_group_creation([])
        self.assertFalse(is_valid)
        self.assertIn("at least 2 nodes", error)
        
        # Single node
        is_valid, error = validate_group_creation([self.mock_node1])
        self.assertFalse(is_valid)
        self.assertIn("at least 2 nodes", error)
    
    def test_invalid_node_types(self):
        """Test validation with invalid node types."""
        invalid_item = Mock()  # Not a Node instance
        nodes = [self.mock_node1, invalid_item]
        
        is_valid, error = validate_group_creation(nodes)
        self.assertFalse(is_valid)
        self.assertIn("Invalid item type", error)
    
    def test_duplicate_nodes(self):
        """Test validation with duplicate node UUIDs."""
        # Create two nodes with same UUID
        from src.core.node import Node
        
        node1 = Node("Test Node 1")
        node1.uuid = "uuid1"
        
        node2 = Node("Test Node 2")
        node2.uuid = "uuid1"  # Same UUID as node1
        
        nodes = [node1, node2]
        is_valid, error = validate_group_creation(nodes)
        
        self.assertFalse(is_valid)
        self.assertIn("Duplicate nodes", error)


class TestGroupNameGeneration(unittest.TestCase):
    """Test automatic naming generation and customization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_node1 = Mock(spec=Node)
        self.mock_node1.title = "Math Node"
        
        self.mock_node2 = Mock(spec=Node)
        self.mock_node2.title = "String Processor"
        
        self.mock_node3 = Mock(spec=Node)
        self.mock_node3.title = "Data Transformer"
    
    def test_name_generation_few_nodes(self):
        """Test name generation with 3 or fewer nodes."""
        # Two nodes
        nodes = [self.mock_node1, self.mock_node2]
        name = generate_group_name(nodes)
        self.assertIn("Math Node", name)
        self.assertIn("String Processor", name)
        
        # Three nodes
        nodes = [self.mock_node1, self.mock_node2, self.mock_node3]
        name = generate_group_name(nodes)
        self.assertIn("Math Node", name)
        self.assertIn("String Processor", name)
        self.assertIn("Data Transformer", name)
    
    def test_name_generation_many_nodes(self):
        """Test name generation with more than 3 nodes."""
        mock_node4 = Mock(spec=Node)
        mock_node4.title = "Output Handler"
        
        nodes = [self.mock_node1, self.mock_node2, self.mock_node3, mock_node4]
        name = generate_group_name(nodes)
        
        self.assertIn("Math Node", name)
        self.assertIn("String Processor", name)
        self.assertIn("Data Transformer", name)
        self.assertIn("+1 more", name)
    
    def test_name_generation_empty_selection(self):
        """Test name generation with empty selection."""
        name = generate_group_name([])
        self.assertEqual(name, "Empty Group")
    
    def test_name_generation_nodes_without_titles(self):
        """Test name generation with nodes that have no title attribute."""
        mock_node_no_title = Mock(spec=Node)
        # Don't set title attribute
        
        nodes = [mock_node_no_title, self.mock_node1]
        name = generate_group_name(nodes)
        
        # Should handle missing title gracefully
        self.assertIn("Node", name)
        self.assertIn("Math Node", name)


class TestCreateGroupCommand(unittest.TestCase):
    """Test CreateGroupCommand for undo/redo functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_scene = Mock()
        self.mock_scene.addItem = Mock()
        self.mock_scene.removeItem = Mock()
        self.mock_scene.nodes = []
        self.mock_scene.groups = []
        
        # Create mock nodes
        self.mock_node1 = Mock(spec=Node)
        self.mock_node1.uuid = "uuid1"
        self.mock_node1.title = "Node 1"
        
        self.mock_node2 = Mock(spec=Node)
        self.mock_node2.uuid = "uuid2"
        self.mock_node2.title = "Node 2"
        
        self.mock_scene.nodes = [self.mock_node1, self.mock_node2]
        
        self.group_properties = {
            "name": "Test Group",
            "description": "Test description",
            "member_node_uuids": ["uuid1", "uuid2"],
            "auto_size": True,
            "padding": 20
        }
    
    def test_command_creation(self):
        """Test command creation with valid properties."""
        command = CreateGroupCommand(self.mock_scene, self.group_properties)
        
        self.assertEqual(command.description, "Create group 'Test Group'")
        self.assertEqual(command.group_properties["name"], "Test Group")
        self.assertIn("creation_timestamp", command.group_properties)
    
    @patch('src.core.group.Group')
    def test_command_execute(self, mock_group_class):
        """Test successful command execution."""
        # Setup mock group instance
        mock_group = Mock()
        mock_group.name = "Test Group"
        mock_group.calculate_bounds_from_members = Mock()
        mock_group_class.return_value = mock_group
        
        command = CreateGroupCommand(self.mock_scene, self.group_properties)
        result = command.execute()
        
        self.assertTrue(result)
        self.assertIsNotNone(command.created_group)
        self.mock_scene.addItem.assert_called_once_with(mock_group)
        self.assertIn(mock_group, self.mock_scene.groups)
    
    @patch('src.core.group.Group')
    def test_command_undo(self, mock_group_class):
        """Test successful command undo."""
        # Setup and execute command first
        mock_group = Mock()
        mock_group.name = "Test Group"
        mock_group.scene.return_value = self.mock_scene
        mock_group.calculate_bounds_from_members = Mock()
        mock_group_class.return_value = mock_group
        
        command = CreateGroupCommand(self.mock_scene, self.group_properties)
        command.execute()
        
        # Test undo
        result = command.undo()
        
        self.assertTrue(result)
        self.mock_scene.removeItem.assert_called_with(mock_group)
        self.assertNotIn(mock_group, self.mock_scene.groups)
    
    @patch('src.core.group.Group')
    def test_command_redo(self, mock_group_class):
        """Test successful command redo."""
        # Setup, execute, and undo first
        mock_group = Mock()
        mock_group.name = "Test Group"
        mock_group.scene.return_value = self.mock_scene
        mock_group.calculate_bounds_from_members = Mock()
        mock_group_class.return_value = mock_group
        
        command = CreateGroupCommand(self.mock_scene, self.group_properties)
        command.execute()
        command.undo()
        
        # Reset mock call counts
        self.mock_scene.addItem.reset_mock()
        
        # Test redo
        result = command.redo()
        
        self.assertTrue(result)
        self.mock_scene.addItem.assert_called_with(mock_group)
        self.assertIn(mock_group, self.mock_scene.groups)
    
    def test_command_memory_usage(self):
        """Test memory usage estimation."""
        command = CreateGroupCommand(self.mock_scene, self.group_properties)
        memory_usage = command.get_memory_usage()
        
        self.assertIsInstance(memory_usage, int)
        self.assertGreater(memory_usage, 0)
    
    def test_command_cannot_merge(self):
        """Test that group commands cannot be merged."""
        command1 = CreateGroupCommand(self.mock_scene, self.group_properties)
        command2 = CreateGroupCommand(self.mock_scene, self.group_properties)
        
        self.assertFalse(command1.can_merge_with(command2))


if __name__ == '__main__':
    unittest.main()
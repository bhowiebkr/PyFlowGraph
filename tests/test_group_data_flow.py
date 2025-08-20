# test_group_data_flow.py
# Tests for data flow preservation through group interface pins.

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.group_connection_router import GroupConnectionRouter
from src.core.group_interface_pin import GroupInterfacePin
from src.core.group import Group


class TestGroupDataFlow(unittest.TestCase):
    """Test data flow through group interface pins."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_node_graph = Mock()
        self.mock_node_graph.nodes = []
        self.router = GroupConnectionRouter(self.mock_node_graph)
        
        # Create a mock group
        self.mock_group = Mock()
        self.mock_group.uuid = "test_group"
        self.mock_group.member_node_uuids = ["node1", "node2"]
    
    def create_mock_pin(self, pin_uuid, pin_type="int", pin_category="data", node_uuid="node1"):
        """Create a mock pin for testing."""
        mock_pin = Mock()
        mock_pin.uuid = pin_uuid
        mock_pin.pin_type = pin_type
        mock_pin.pin_category = pin_category
        mock_pin.value = None
        
        mock_node = Mock()
        mock_node.uuid = node_uuid
        mock_pin.node = mock_node
        
        return mock_pin
    
    def test_input_data_routing(self):
        """Test routing data from external source to internal pins."""
        # Create internal pin
        internal_pin = self.create_mock_pin("internal_pin1", "int", "data", "node1")
        self.mock_node_graph.nodes = [internal_pin.node]
        internal_pin.node.pins = [internal_pin]
        
        # Create interface pin
        interface_pin = GroupInterfacePin(
            group=self.mock_group,
            name="input_data",
            direction="input",
            pin_type_str="int",
            internal_pin_mappings=["internal_pin1"]
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [interface_pin],
            'output_pins': []
        }
        self.router.create_routing_for_group(self.mock_group, interface_pins)
        
        # Route data
        test_data = 42
        success = self.router.route_external_data_to_group(
            "test_group", 
            interface_pin.uuid, 
            test_data
        )
        
        self.assertTrue(success)
        self.assertEqual(internal_pin.value, test_data)
    
    def test_output_data_routing(self):
        """Test routing data from internal pins to external destination."""
        # Create internal pin with data
        internal_pin = self.create_mock_pin("internal_pin1", "str", "data", "node1")
        internal_pin.value = "test_output"
        self.mock_node_graph.nodes = [internal_pin.node]
        internal_pin.node.pins = [internal_pin]
        
        # Create interface pin
        interface_pin = GroupInterfacePin(
            group=self.mock_group,
            name="output_data",
            direction="output",
            pin_type_str="str",
            internal_pin_mappings=["internal_pin1"]
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [],
            'output_pins': [interface_pin]
        }
        self.router.create_routing_for_group(self.mock_group, interface_pins)
        
        # Route data out
        result_data = self.router.route_group_data_to_external(
            "test_group", 
            interface_pin.uuid
        )
        
        self.assertEqual(result_data, "test_output")
    
    def test_multiple_input_routing(self):
        """Test routing to multiple internal pins from one interface pin."""
        # Create multiple internal pins
        internal_pin1 = self.create_mock_pin("internal_pin1", "float", "data", "node1")
        internal_pin2 = self.create_mock_pin("internal_pin2", "float", "data", "node2")
        
        # Mock node graph setup
        mock_node1 = Mock()
        mock_node1.uuid = "node1"
        mock_node1.pins = [internal_pin1]
        mock_node2 = Mock()
        mock_node2.uuid = "node2"
        mock_node2.pins = [internal_pin2]
        
        self.mock_node_graph.nodes = [mock_node1, mock_node2]
        
        # Create interface pin mapping to both internal pins
        interface_pin = GroupInterfacePin(
            group=self.mock_group,
            name="multi_input",
            direction="input",
            pin_type_str="float",
            internal_pin_mappings=["internal_pin1", "internal_pin2"]
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [interface_pin],
            'output_pins': []
        }
        self.router.create_routing_for_group(self.mock_group, interface_pins)
        
        # Route data
        test_data = 3.14
        success = self.router.route_external_data_to_group(
            "test_group", 
            interface_pin.uuid, 
            test_data
        )
        
        self.assertTrue(success)
        self.assertEqual(internal_pin1.value, test_data)
        self.assertEqual(internal_pin2.value, test_data)
    
    def test_data_flow_tracking(self):
        """Test data flow tracking and monitoring."""
        # Create internal pin
        internal_pin = self.create_mock_pin("internal_pin1", "bool", "data", "node1")
        self.mock_node_graph.nodes = [internal_pin.node]
        internal_pin.node.pins = [internal_pin]
        
        # Create interface pin
        interface_pin = GroupInterfacePin(
            group=self.mock_group,
            name="tracked_input",
            direction="input",
            pin_type_str="bool",
            internal_pin_mappings=["internal_pin1"]
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [interface_pin],
            'output_pins': []
        }
        self.router.create_routing_for_group(self.mock_group, interface_pins)
        
        # Track data flow updates
        data_flow_updates = []
        self.router.dataFlowUpdated.connect(lambda msg: data_flow_updates.append(msg))
        
        # Route data
        test_data = True
        self.router.route_external_data_to_group(
            "test_group", 
            interface_pin.uuid, 
            test_data
        )
        
        # Check that data flow was tracked
        self.assertTrue(len(data_flow_updates) > 0)
        self.assertTrue(any("routed" in update for update in data_flow_updates))
    
    def test_routing_error_handling(self):
        """Test error handling in data routing."""
        # Setup routing with no group
        routing_errors = []
        self.router.routingError.connect(lambda pin_id, msg: routing_errors.append((pin_id, msg)))
        
        # Attempt to route to non-existent group
        success = self.router.route_external_data_to_group(
            "non_existent_group", 
            "fake_pin", 
            "test_data"
        )
        
        self.assertFalse(success)
        self.assertTrue(len(routing_errors) > 0)
    
    def test_connection_preservation_during_grouping(self):
        """Test that connections are preserved when creating groups."""
        # Create mock original connections
        external_pin = self.create_mock_pin("external_pin", "int", "data", "external_node")
        internal_pin = self.create_mock_pin("internal_pin", "int", "data", "internal_node")
        
        mock_connection = Mock()
        mock_connection.start_pin = external_pin
        mock_connection.end_pin = internal_pin
        
        original_connections = [mock_connection]
        
        # Create group with routing
        self.mock_group.member_node_uuids = ["internal_node"]
        
        # Create input interface pin for the internal pin
        interface_pin = GroupInterfacePin(
            group=self.mock_group,
            name="preserved_input",
            direction="input",
            pin_type_str="int",
            internal_pin_mappings=["internal_pin"]
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [interface_pin],
            'output_pins': []
        }
        self.router.create_routing_for_group(self.mock_group, interface_pins)
        
        # Test connection preservation
        preservation_results = self.router.preserve_connections_during_grouping(
            self.mock_group, 
            original_connections
        )
        
        self.assertEqual(len(preservation_results['preserved_connections']), 1)
        self.assertEqual(len(preservation_results['failed_connections']), 0)
    
    def test_routing_validation(self):
        """Test validation of routing integrity."""
        # Create interface pin
        interface_pin = GroupInterfacePin(
            group=self.mock_group,
            name="test_pin",
            direction="input",
            pin_type_str="int",
            internal_pin_mappings=["internal_pin1"]
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [interface_pin],
            'output_pins': []
        }
        self.router.create_routing_for_group(self.mock_group, interface_pins)
        
        # Mock interface pin lookup (no actual pins exist)
        with patch.object(self.router, '_find_interface_pin_by_uuid') as mock_find_interface:
            mock_find_interface.return_value = interface_pin
            
            # Mock internal pin lookup (pin doesn't exist)
            with patch.object(self.router, '_find_pin_by_uuid') as mock_find_pin:
                mock_find_pin.return_value = None
                
                validation_result = self.router.validate_routing_integrity("test_group")
                
                self.assertTrue(validation_result['is_valid'])  # Interface pin exists
                self.assertTrue(len(validation_result['warnings']) > 0)  # Internal pin missing
    
    def test_data_type_preservation(self):
        """Test that data types are preserved through routing."""
        # Create internal pin
        internal_pin = self.create_mock_pin("internal_pin1", "complex_object", "data", "node1")
        self.mock_node_graph.nodes = [internal_pin.node]
        internal_pin.node.pins = [internal_pin]
        
        # Create interface pin with matching type
        interface_pin = GroupInterfacePin(
            group=self.mock_group,
            name="complex_input",
            direction="input",
            pin_type_str="complex_object",
            internal_pin_mappings=["internal_pin1"]
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [interface_pin],
            'output_pins': []
        }
        self.router.create_routing_for_group(self.mock_group, interface_pins)
        
        # Route complex data
        test_data = {"key": "value", "nested": {"data": [1, 2, 3]}}
        success = self.router.route_external_data_to_group(
            "test_group", 
            interface_pin.uuid, 
            test_data
        )
        
        self.assertTrue(success)
        self.assertEqual(internal_pin.value, test_data)
        self.assertIsInstance(internal_pin.value, dict)
    
    def test_execution_pin_routing(self):
        """Test routing of execution flow pins."""
        # Create execution pins
        internal_exec_pin = self.create_mock_pin("exec_pin1", "exec", "execution", "node1")
        self.mock_node_graph.nodes = [internal_exec_pin.node]
        internal_exec_pin.node.pins = [internal_exec_pin]
        
        # Create execution interface pin
        interface_pin = GroupInterfacePin(
            group=self.mock_group,
            name="exec_input",
            direction="input",
            pin_type_str="exec",
            pin_category="execution",
            internal_pin_mappings=["exec_pin1"]
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [interface_pin],
            'output_pins': []
        }
        self.router.create_routing_for_group(self.mock_group, interface_pins)
        
        # Route execution signal
        exec_signal = "execute"
        success = self.router.route_external_data_to_group(
            "test_group", 
            interface_pin.uuid, 
            exec_signal
        )
        
        self.assertTrue(success)
        self.assertEqual(internal_exec_pin.value, exec_signal)


class TestDataFlowIntegration(unittest.TestCase):
    """Integration tests for complete data flow scenarios."""
    
    def setUp(self):
        """Set up complex test scenario."""
        self.mock_node_graph = Mock()
        self.mock_node_graph.nodes = []
        self.mock_node_graph.connections = []
        
        # Create router
        self.router = GroupConnectionRouter(self.mock_node_graph)
        
        # Create group
        self.group = Group("Test Group", ["node1", "node2", "node3"])
    
    def test_complex_data_flow_scenario(self):
        """Test complex scenario with multiple inputs, outputs, and internal routing."""
        # Create internal nodes and pins
        nodes_and_pins = []
        for i in range(3):
            node_uuid = f"node{i+1}"
            
            # Create input and output pins for each node
            input_pin = Mock()
            input_pin.uuid = f"input_pin_{i+1}"
            input_pin.pin_type = "int"
            input_pin.pin_category = "data"
            input_pin.value = None
            
            output_pin = Mock()
            output_pin.uuid = f"output_pin_{i+1}"
            output_pin.pin_type = "int"
            output_pin.pin_category = "data"
            output_pin.value = (i + 1) * 10  # Different values for each
            
            mock_node = Mock()
            mock_node.uuid = node_uuid
            mock_node.pins = [input_pin, output_pin]
            
            input_pin.node = mock_node
            output_pin.node = mock_node
            
            nodes_and_pins.append((mock_node, input_pin, output_pin))
        
        self.mock_node_graph.nodes = [node for node, _, _ in nodes_and_pins]
        
        # Create interface pins
        # One input interface feeding all internal inputs
        input_interface = GroupInterfacePin(
            group=self.group,
            name="main_input",
            direction="input",
            pin_type_str="int",
            internal_pin_mappings=[f"input_pin_{i+1}" for i in range(3)]
        )
        
        # Multiple output interfaces from different internal outputs
        output_interfaces = []
        for i in range(3):
            output_interface = GroupInterfacePin(
                group=self.group,
                name=f"output_{i+1}",
                direction="output",
                pin_type_str="int",
                internal_pin_mappings=[f"output_pin_{i+1}"]
            )
            output_interfaces.append(output_interface)
        
        # Setup routing
        interface_pins = {
            'input_pins': [input_interface],
            'output_pins': output_interfaces
        }
        self.router.create_routing_for_group(self.group, interface_pins)
        
        # Test input routing - data should go to all internal inputs
        input_data = 100
        success = self.router.route_external_data_to_group(
            self.group.uuid,
            input_interface.uuid,
            input_data
        )
        
        self.assertTrue(success)
        
        # Verify all internal input pins received the data
        for node, input_pin, _ in nodes_and_pins:
            self.assertEqual(input_pin.value, input_data)
        
        # Test output routing - should get different values from each output
        for i, output_interface in enumerate(output_interfaces):
            output_data = self.router.route_group_data_to_external(
                self.group.uuid,
                output_interface.uuid
            )
            
            expected_value = (i + 1) * 10
            self.assertEqual(output_data, expected_value)
    
    def test_performance_with_many_connections(self):
        """Test performance with many interface pins and routing operations."""
        import time
        
        # Create many internal pins
        num_pins = 20
        internal_pin_mappings = []
        
        for i in range(num_pins):
            pin_uuid = f"pin_{i}"
            internal_pin_mappings.append(pin_uuid)
            
            # Create mock pin and node
            mock_pin = Mock()
            mock_pin.uuid = pin_uuid
            mock_pin.pin_type = "int"
            mock_pin.pin_category = "data"
            mock_pin.value = None
            
            mock_node = Mock()
            mock_node.uuid = f"node_{i}"
            mock_node.pins = [mock_pin]
            mock_pin.node = mock_node
            
            self.mock_node_graph.nodes.append(mock_node)
        
        # Create interface pin with many mappings
        interface_pin = GroupInterfacePin(
            group=self.group,
            name="many_connections",
            direction="input",
            pin_type_str="int",
            internal_pin_mappings=internal_pin_mappings
        )
        
        # Setup routing
        interface_pins = {
            'input_pins': [interface_pin],
            'output_pins': []
        }
        self.router.create_routing_for_group(self.group, interface_pins)
        
        # Test routing performance
        start_time = time.time()
        
        for i in range(10):  # Multiple routing operations
            success = self.router.route_external_data_to_group(
                self.group.uuid,
                interface_pin.uuid,
                i
            )
            self.assertTrue(success)
        
        end_time = time.time()
        
        # Should complete quickly even with many connections
        self.assertLess(end_time - start_time, 1.0)


if __name__ == '__main__':
    unittest.main()
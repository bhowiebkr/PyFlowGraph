# test_group_interface_pins.py
# Comprehensive tests for group interface pin generation and functionality.

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Setup Qt Application for tests
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication
    import PySide6
    
    # Create QApplication instance if it doesn't exist
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
except ImportError:
    # If PySide6 is not available, skip Qt-dependent tests
    pass

from src.core.connection_analyzer import ConnectionAnalyzer
from src.core.group_interface_pin import GroupInterfacePin
from src.core.group_pin_generator import GroupPinGenerator
from src.core.group_type_inference import TypeInferenceEngine
from src.core.group_connection_router import GroupConnectionRouter
from src.core.group import Group


class TestConnectionAnalyzer(unittest.TestCase):
    """Test the ConnectionAnalyzer class for external connection detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_node_graph = Mock()
        self.mock_node_graph.connections = []
        self.mock_node_graph.nodes = []
        self.analyzer = ConnectionAnalyzer(self.mock_node_graph)
    
    def create_mock_pin(self, pin_uuid, pin_type="int", pin_category="data", node_uuid="node1"):
        """Create a mock pin for testing."""
        mock_pin = Mock()
        mock_pin.uuid = pin_uuid
        mock_pin.pin_type = pin_type
        mock_pin.pin_category = pin_category
        
        mock_node = Mock()
        mock_node.uuid = node_uuid
        mock_pin.node = mock_node
        
        return mock_pin
    
    def create_mock_connection(self, start_pin, end_pin):
        """Create a mock connection for testing."""
        mock_connection = Mock()
        mock_connection.start_pin = start_pin
        mock_connection.end_pin = end_pin
        return mock_connection
    
    def test_analyze_external_connections_no_connections(self):
        """Test analysis when no connections exist."""
        result = self.analyzer.analyze_external_connections(["node1", "node2"])
        
        self.assertEqual(len(result['input_interfaces']), 0)
        self.assertEqual(len(result['output_interfaces']), 0)
        self.assertEqual(len(result['internal_connections']), 0)
    
    def test_analyze_external_connections_input_interface(self):
        """Test detection of input interfaces."""
        # Create pins
        external_pin = self.create_mock_pin("pin1", "int", "data", "external_node")
        internal_pin = self.create_mock_pin("pin2", "int", "data", "internal_node")
        
        # Create connection from external to internal
        connection = self.create_mock_connection(external_pin, internal_pin)
        self.mock_node_graph.connections = [connection]
        
        # Analyze with internal_node in selection
        result = self.analyzer.analyze_external_connections(["internal_node"])
        
        self.assertEqual(len(result['input_interfaces']), 1)
        self.assertEqual(len(result['output_interfaces']), 0)
        self.assertEqual(result['input_interfaces'][0]['type'], 'input')
        self.assertEqual(result['input_interfaces'][0]['data_type'], 'int')
    
    def test_analyze_external_connections_output_interface(self):
        """Test detection of output interfaces."""
        # Create pins
        internal_pin = self.create_mock_pin("pin1", "str", "data", "internal_node")
        external_pin = self.create_mock_pin("pin2", "str", "data", "external_node")
        
        # Create connection from internal to external
        connection = self.create_mock_connection(internal_pin, external_pin)
        self.mock_node_graph.connections = [connection]
        
        # Analyze with internal_node in selection
        result = self.analyzer.analyze_external_connections(["internal_node"])
        
        self.assertEqual(len(result['input_interfaces']), 0)
        self.assertEqual(len(result['output_interfaces']), 1)
        self.assertEqual(result['output_interfaces'][0]['type'], 'output')
        self.assertEqual(result['output_interfaces'][0]['data_type'], 'str')
    
    def test_analyze_external_connections_internal_connections(self):
        """Test detection of internal connections."""
        # Create pins
        pin1 = self.create_mock_pin("pin1", "bool", "data", "node1")
        pin2 = self.create_mock_pin("pin2", "bool", "data", "node2")
        
        # Create connection between internal nodes
        connection = self.create_mock_connection(pin1, pin2)
        self.mock_node_graph.connections = [connection]
        
        # Analyze with both nodes in selection
        result = self.analyzer.analyze_external_connections(["node1", "node2"])
        
        self.assertEqual(len(result['input_interfaces']), 0)
        self.assertEqual(len(result['output_interfaces']), 0)
        self.assertEqual(len(result['internal_connections']), 1)
    
    def test_validate_grouping_feasibility_valid(self):
        """Test validation with valid grouping selection."""
        # Mock existing nodes
        mock_node1 = Mock()
        mock_node1.uuid = "node1"
        mock_node2 = Mock()
        mock_node2.uuid = "node2"
        self.mock_node_graph.nodes = [mock_node1, mock_node2]
        
        is_valid, error_msg = self.analyzer.validate_grouping_feasibility(["node1", "node2"])
        
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_validate_grouping_feasibility_too_few_nodes(self):
        """Test validation with too few nodes."""
        is_valid, error_msg = self.analyzer.validate_grouping_feasibility(["node1"])
        
        self.assertFalse(is_valid)
        self.assertIn("at least 2 nodes", error_msg)
    
    def test_validate_grouping_feasibility_missing_nodes(self):
        """Test validation with missing nodes."""
        self.mock_node_graph.nodes = []
        
        is_valid, error_msg = self.analyzer.validate_grouping_feasibility(["node1", "node2"])
        
        self.assertFalse(is_valid)
        self.assertIn("not found", error_msg)


class TestGroupInterfacePin(unittest.TestCase):
    """Test the GroupInterfacePin class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_group = Mock()
        self.mock_group.uuid = "group1"
    
    @patch('src.core.group_interface_pin.Pin.__init__')
    def test_interface_pin_creation(self, mock_pin_init):
        """Test basic interface pin creation."""
        mock_pin_init.return_value = None
        
        pin = GroupInterfacePin(
            group=self.mock_group,
            name="input_data",
            direction="input",
            pin_type_str="int",
            pin_category="data",
            internal_pin_mappings=["pin1", "pin2"]
        )
        
        self.assertEqual(pin.name, "input_data")
        self.assertEqual(pin.direction, "input")
        self.assertEqual(pin.pin_type, "int")
        self.assertEqual(pin.pin_category, "data")
        self.assertEqual(len(pin.internal_pin_mappings), 2)
        self.assertTrue(pin.is_interface_pin)
        self.assertTrue(pin.auto_generated)
    
    @patch('src.core.group_interface_pin.Pin.__init__')
    def test_interface_pin_mapping_management(self, mock_pin_init):
        """Test adding and removing internal pin mappings."""
        mock_pin_init.return_value = None
        
        pin = GroupInterfacePin(
            group=self.mock_group,
            name="test_pin",
            direction="output",
            pin_type_str="str"
        )
        
        # Add mappings
        pin.add_internal_pin_mapping("pin1")
        pin.add_internal_pin_mapping("pin2")
        self.assertEqual(len(pin.internal_pin_mappings), 2)
        
        # Remove mapping
        pin.remove_internal_pin_mapping("pin1")
        self.assertEqual(len(pin.internal_pin_mappings), 1)
        self.assertIn("pin2", pin.internal_pin_mappings)
        self.assertNotIn("pin1", pin.internal_pin_mappings)
    
    @patch('src.core.group_interface_pin.Pin.__init__')
    @patch('src.core.group_interface_pin.Pin.serialize')
    def test_interface_pin_serialization(self, mock_serialize, mock_pin_init):
        """Test interface pin serialization."""
        mock_pin_init.return_value = None
        mock_serialize.return_value = {
            'uuid': 'pin_uuid',
            'name': 'test_pin',
            'direction': 'input',
            'type': 'float',
            'category': 'data'
        }
        
        pin = GroupInterfacePin(
            group=self.mock_group,
            name="test_pin",
            direction="input",
            pin_type_str="float",
            internal_pin_mappings=["pin1"]
        )
        
        serialized = pin.serialize()
        
        self.assertTrue(serialized['is_interface_pin'])
        self.assertEqual(serialized['name'], "test_pin")
        self.assertEqual(serialized['direction'], "input")
        self.assertEqual(serialized['type'], "float")
        self.assertEqual(serialized['internal_pin_mappings'], ["pin1"])
        self.assertEqual(serialized['group_uuid'], "group1")


class TestGroupPinGenerator(unittest.TestCase):
    """Test the GroupPinGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_node_graph = Mock()
        self.mock_node_graph.connections = []
        self.mock_node_graph.nodes = []
        self.generator = GroupPinGenerator(self.mock_node_graph)
        
        # Mock the connection analyzer
        self.mock_analyzer = Mock()
        self.generator.connection_analyzer = self.mock_analyzer
    
    def test_generate_interface_pins_no_interfaces(self):
        """Test pin generation when no interfaces are needed."""
        mock_group = Mock()
        mock_group.uuid = "group1"
        
        # Mock analysis with no interfaces
        self.mock_analyzer.analyze_external_connections.return_value = {
            'input_interfaces': [],
            'output_interfaces': []
        }
        
        result = self.generator.generate_interface_pins(mock_group, ["node1", "node2"])
        
        self.assertEqual(len(result['input_pins']), 0)
        self.assertEqual(len(result['output_pins']), 0)
        self.assertEqual(result['total_pins'], 0)
    
    def test_generate_interface_pins_with_interfaces(self):
        """Test pin generation with required interfaces."""
        mock_group = Mock()
        mock_group.uuid = "group1"
        
        # Create mock internal pins
        mock_internal_pin = Mock()
        mock_internal_pin.uuid = "internal_pin1"
        mock_internal_pin.name = "data_input"
        
        # Create mock connection
        mock_connection = Mock()
        
        # Mock analysis with interfaces
        self.mock_analyzer.analyze_external_connections.return_value = {
            'input_interfaces': [{
                'type': 'input',
                'internal_pin': mock_internal_pin,
                'data_type': 'int',
                'pin_category': 'data',
                'connection': mock_connection
            }],
            'output_interfaces': []
        }
        
        with patch('src.core.group_pin_generator.GroupInterfacePin') as mock_pin_class:
            mock_pin_instance = Mock()
            mock_pin_class.return_value = mock_pin_instance
            
            result = self.generator.generate_interface_pins(mock_group, ["node1"])
            
            self.assertEqual(len(result['input_pins']), 1)
            self.assertEqual(len(result['output_pins']), 0)
            self.assertEqual(result['total_pins'], 1)
    
    def test_pin_name_generation_single_interface(self):
        """Test pin name generation for single interface."""
        mock_internal_pin = Mock()
        mock_internal_pin.name = "data_input"
        
        interfaces = [{'internal_pin': mock_internal_pin}]
        name = self.generator._generate_pin_name(interfaces, "input")
        
        self.assertEqual(name, "input_data_input")
    
    def test_pin_name_generation_multiple_interfaces(self):
        """Test pin name generation for multiple interfaces."""
        mock_pin1 = Mock()
        mock_pin1.name = "data"
        mock_pin2 = Mock()
        mock_pin2.name = "signal"
        
        interfaces = [
            {'internal_pin': mock_pin1},
            {'internal_pin': mock_pin2}
        ]
        name = self.generator._generate_pin_name(interfaces, "output")
        
        self.assertEqual(name, "output_data_signal")
    
    def test_type_inference_single_type(self):
        """Test type inference with single type."""
        interfaces = [{'data_type': 'int'}]
        inferred_type = self.generator._infer_pin_type(interfaces)
        
        self.assertEqual(inferred_type, 'int')
    
    def test_type_inference_multiple_compatible_types(self):
        """Test type inference with multiple compatible types."""
        interfaces = [
            {'data_type': 'int'},
            {'data_type': 'float'}
        ]
        inferred_type = self.generator._infer_pin_type(interfaces)
        
        # Should resolve to float (more general than int)
        self.assertEqual(inferred_type, 'float')
    
    def test_type_inference_any_type_present(self):
        """Test type inference when 'any' type is present."""
        interfaces = [
            {'data_type': 'int'},
            {'data_type': 'any'}
        ]
        inferred_type = self.generator._infer_pin_type(interfaces)
        
        self.assertEqual(inferred_type, 'any')


class TestTypeInferenceEngine(unittest.TestCase):
    """Test the TypeInferenceEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = TypeInferenceEngine()
    
    def test_resolve_single_type(self):
        """Test resolving a single type."""
        result_type, details = self.engine.resolve_type_from_list(['int'])
        
        self.assertEqual(result_type, 'int')
        self.assertEqual(details['reason'], 'single_type')
        self.assertEqual(details['confidence'], 1.0)
    
    def test_resolve_compatible_types(self):
        """Test resolving compatible types."""
        result_type, details = self.engine.resolve_type_from_list(['int', 'float'])
        
        # Should resolve to float (more general)
        self.assertEqual(result_type, 'float')
        self.assertIn('compatible', details['reason'])
    
    def test_resolve_any_type_present(self):
        """Test resolving when 'any' type is present."""
        result_type, details = self.engine.resolve_type_from_list(['int', 'any', 'str'])
        
        self.assertEqual(result_type, 'any')
        self.assertEqual(details['reason'], 'any_type_present')
    
    def test_resolve_incompatible_types(self):
        """Test resolving incompatible types."""
        result_type, details = self.engine.resolve_type_from_list(['int', 'str'])
        
        self.assertEqual(result_type, 'any')
        self.assertIn('conflict', details['reason'])
    
    def test_validate_type_compatibility_valid(self):
        """Test type compatibility validation with valid types."""
        result = self.engine.validate_type_compatibility('float', ['int', 'float'])
        
        self.assertTrue(result['is_valid'])
        self.assertGreater(result['confidence'], 0.5)
    
    def test_validate_type_compatibility_invalid(self):
        """Test type compatibility validation with invalid types."""
        result = self.engine.validate_type_compatibility('int', ['str', 'bool'])
        
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['confidence'], 0.0)


class TestGroupConnectionRouter(unittest.TestCase):
    """Test the GroupConnectionRouter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_node_graph = Mock()
        self.router = GroupConnectionRouter(self.mock_node_graph)
    
    def test_create_routing_for_group(self):
        """Test creating routing table for a group."""
        mock_group = Mock()
        mock_group.uuid = "group1"
        mock_group.member_node_uuids = ["node1", "node2"]  # Add this attribute
        
        mock_input_pin = Mock()
        mock_input_pin.uuid = "input_pin1"
        mock_input_pin.pin_type = "int"
        mock_input_pin.pin_category = "data"
        mock_input_pin.internal_pin_mappings = ["internal_pin1"]
        
        interface_pins = {
            'input_pins': [mock_input_pin],
            'output_pins': []
        }
        
        routing_table = self.router.create_routing_for_group(mock_group, interface_pins)
        
        self.assertEqual(routing_table['group_uuid'], "group1")
        self.assertIn("input_pin1", routing_table['input_routes'])
        self.assertEqual(len(routing_table['output_routes']), 0)
    
    def test_routing_status(self):
        """Test getting routing status for a group."""
        # Create a routing table first
        mock_group = Mock()
        mock_group.uuid = "group1"
        
        self.router.routing_tables["group1"] = {
            'input_routes': {'pin1': {}},
            'output_routes': {'pin2': {}},
            'internal_connections': {}
        }
        
        status = self.router.get_routing_status("group1")
        
        self.assertEqual(status['status'], 'active')
        self.assertEqual(status['input_routes_count'], 1)
        self.assertEqual(status['output_routes_count'], 1)
    
    def test_cleanup_routing(self):
        """Test cleanup of routing information."""
        # Create routing table
        self.router.routing_tables["group1"] = {'test': 'data'}
        self.router.active_data_flows["flow1"] = {'group_uuid': 'group1'}
        
        self.router.cleanup_routing_for_group("group1")
        
        self.assertNotIn("group1", self.router.routing_tables)
        self.assertNotIn("flow1", self.router.active_data_flows)


class TestGroupIntegration(unittest.TestCase):
    """Integration tests for group interface pins."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_node_graph = Mock()
        self.mock_node_graph.connections = []
        self.mock_node_graph.nodes = []
    
    def test_complete_group_creation_workflow(self):
        """Test complete workflow from analysis to pin generation."""
        # Create mock nodes
        mock_node1 = Mock()
        mock_node1.uuid = "node1"
        mock_node2 = Mock()
        mock_node2.uuid = "node2"
        self.mock_node_graph.nodes = [mock_node1, mock_node2]
        
        # Create mock pins
        mock_pin1 = Mock()
        mock_pin1.uuid = "pin1"
        mock_pin1.name = "input"
        mock_pin1.pin_type = "int"
        mock_pin1.pin_category = "data"
        mock_pin1.node = mock_node1
        
        mock_pin2 = Mock()
        mock_pin2.uuid = "pin2"
        mock_pin2.name = "output"
        mock_pin2.pin_type = "int"
        mock_pin2.pin_category = "data"
        mock_pin2.node = Mock()
        mock_pin2.node.uuid = "external_node"
        
        # Create mock connection
        mock_connection = Mock()
        mock_connection.start_pin = mock_pin1
        mock_connection.end_pin = mock_pin2
        self.mock_node_graph.connections = [mock_connection]
        
        # Test the workflow
        analyzer = ConnectionAnalyzer(self.mock_node_graph)
        analysis = analyzer.analyze_external_connections(["node1"])
        
        self.assertEqual(len(analysis['output_interfaces']), 1)
        self.assertEqual(analysis['output_interfaces'][0]['data_type'], 'int')
    
    def test_performance_with_large_selection(self):
        """Test performance with large node selections."""
        # Create many mock nodes and connections
        num_nodes = 50
        nodes = []
        connections = []
        
        for i in range(num_nodes):
            mock_node = Mock()
            mock_node.uuid = f"node{i}"
            nodes.append(mock_node)
        
        self.mock_node_graph.nodes = nodes
        self.mock_node_graph.connections = connections
        
        # Test with large selection
        selected_uuids = [f"node{i}" for i in range(25)]
        
        analyzer = ConnectionAnalyzer(self.mock_node_graph)
        
        # This should complete quickly
        import time
        start_time = time.time()
        analysis = analyzer.analyze_external_connections(selected_uuids)
        end_time = time.time()
        
        # Should complete within reasonable time (much less than 2 seconds)
        self.assertLess(end_time - start_time, 1.0)
        self.assertIsInstance(analysis, dict)


if __name__ == '__main__':
    unittest.main()
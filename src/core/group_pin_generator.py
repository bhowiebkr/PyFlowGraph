# group_pin_generator.py
# System for automatically generating interface pins for groups based on connection analysis.

import sys
import os
from typing import List, Dict, Any, Optional, Tuple

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.connection_analyzer import ConnectionAnalyzer
from core.group_interface_pin import GroupInterfacePin


class GroupPinGenerator:
    """
    Generates interface pins for groups based on connection analysis.
    Handles automatic pin creation, naming, positioning, and type inference.
    """

    def __init__(self, node_graph):
        """
        Initialize the pin generator.
        
        Args:
            node_graph: The NodeGraph instance
        """
        self.node_graph = node_graph
        self.connection_analyzer = ConnectionAnalyzer(node_graph)

    def generate_interface_pins(self, group, selected_node_uuids: List[str]) -> Dict[str, List[GroupInterfacePin]]:
        """
        Generate interface pins for a group based on external connections.
        
        Args:
            group: The Group instance to generate pins for
            selected_node_uuids: List of UUIDs of nodes being grouped
            
        Returns:
            Dict containing 'input_pins' and 'output_pins' lists
        """
        # Analyze external connections
        analysis = self.connection_analyzer.analyze_external_connections(selected_node_uuids)
        
        # Generate input interface pins
        input_pins = self._generate_input_pins(group, analysis['input_interfaces'])
        
        # Generate output interface pins
        output_pins = self._generate_output_pins(group, analysis['output_interfaces'])
        
        # Position pins on group boundary
        self._position_interface_pins(group, input_pins, output_pins)
        
        return {
            'input_pins': input_pins,
            'output_pins': output_pins,
            'total_pins': len(input_pins) + len(output_pins)
        }

    def _generate_input_pins(self, group, input_interfaces: List[Dict[str, Any]]) -> List[GroupInterfacePin]:
        """
        Generate input interface pins from input interface requirements.
        
        Args:
            group: The Group instance
            input_interfaces: List of input interface requirements
            
        Returns:
            List of generated input GroupInterfacePin instances
        """
        input_pins = []
        
        # Group interfaces by type and name to avoid duplicates
        grouped_interfaces = self._group_interfaces_by_characteristics(input_interfaces)
        
        for group_key, interfaces in grouped_interfaces.items():
            pin_name = self._generate_pin_name(interfaces, "input")
            pin_type = self._infer_pin_type(interfaces)
            pin_category = interfaces[0]['pin_category']
            
            # Collect internal pin mappings
            internal_pin_mappings = [interface['internal_pin'].uuid for interface in interfaces]
            
            # Create interface pin
            interface_pin = GroupInterfacePin(
                group=group,
                name=pin_name,
                direction="input",
                pin_type_str=pin_type,
                pin_category=pin_category,
                internal_pin_mappings=internal_pin_mappings
            )
            
            # Store original connection data for restoration if needed
            interface_pin.original_connection_data = {
                'interfaces': interfaces,
                'external_connections': [interface['connection'] for interface in interfaces]
            }
            
            input_pins.append(interface_pin)
        
        return input_pins

    def _generate_output_pins(self, group, output_interfaces: List[Dict[str, Any]]) -> List[GroupInterfacePin]:
        """
        Generate output interface pins from output interface requirements.
        
        Args:
            group: The Group instance
            output_interfaces: List of output interface requirements
            
        Returns:
            List of generated output GroupInterfacePin instances
        """
        output_pins = []
        
        # Group interfaces by type and name to avoid duplicates
        grouped_interfaces = self._group_interfaces_by_characteristics(output_interfaces)
        
        for group_key, interfaces in grouped_interfaces.items():
            pin_name = self._generate_pin_name(interfaces, "output")
            pin_type = self._infer_pin_type(interfaces)
            pin_category = interfaces[0]['pin_category']
            
            # Collect internal pin mappings
            internal_pin_mappings = [interface['internal_pin'].uuid for interface in interfaces]
            
            # Create interface pin
            interface_pin = GroupInterfacePin(
                group=group,
                name=pin_name,
                direction="output",
                pin_type_str=pin_type,
                pin_category=pin_category,
                internal_pin_mappings=internal_pin_mappings
            )
            
            # Store original connection data for restoration if needed
            interface_pin.original_connection_data = {
                'interfaces': interfaces,
                'external_connections': [interface['connection'] for interface in interfaces]
            }
            
            output_pins.append(interface_pin)
        
        return output_pins

    def _group_interfaces_by_characteristics(self, interfaces: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group interfaces by their characteristics to avoid duplicate pins.
        
        Args:
            interfaces: List of interface requirements
            
        Returns:
            Dict mapping group keys to lists of similar interfaces
        """
        grouped = {}
        
        for interface in interfaces:
            # Create a key based on interface characteristics
            pin_name = interface['internal_pin'].name
            pin_type = interface['data_type']
            pin_category = interface['pin_category']
            
            # Group by type and category, but keep separate if different internal pin names
            group_key = f"{pin_type}_{pin_category}_{pin_name}"
            
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(interface)
        
        return grouped

    def _generate_pin_name(self, interfaces: List[Dict[str, Any]], direction: str) -> str:
        """
        Generate a descriptive name for an interface pin.
        
        Args:
            interfaces: List of interfaces this pin represents
            direction: "input" or "output"
            
        Returns:
            Generated pin name
        """
        if len(interfaces) == 1:
            # Single interface - use the internal pin name
            internal_pin_name = interfaces[0]['internal_pin'].name
            return f"{direction}_{internal_pin_name}"
        else:
            # Multiple interfaces - create a combined name
            pin_names = [interface['internal_pin'].name for interface in interfaces]
            unique_names = list(set(pin_names))
            
            if len(unique_names) == 1:
                # All interfaces have the same pin name
                return f"{direction}_{unique_names[0]}"
            else:
                # Multiple different pin names
                if len(unique_names) <= 3:
                    return f"{direction}_{'_'.join(unique_names)}"
                else:
                    return f"{direction}_multiple_{len(interfaces)}"

    def _infer_pin_type(self, interfaces: List[Dict[str, Any]]) -> str:
        """
        Infer the appropriate type for an interface pin based on connected interfaces.
        
        Args:
            interfaces: List of interfaces this pin represents
            
        Returns:
            Inferred pin type string
        """
        if not interfaces:
            return "any"
        
        # Collect all data types
        data_types = {interface['data_type'] for interface in interfaces}
        
        if len(data_types) == 1:
            # Single type - use it directly
            return list(data_types)[0]
        
        if 'any' in data_types:
            # If any interface is 'any' type, the result is 'any'
            return 'any'
        
        # Multiple different types - check for compatibility
        return self._resolve_type_compatibility(data_types)

    def _resolve_type_compatibility(self, data_types: set) -> str:
        """
        Resolve type compatibility for multiple data types.
        
        Args:
            data_types: Set of data type strings
            
        Returns:
            Compatible type string or 'any' if incompatible
        """
        # Define type compatibility rules
        numeric_types = {'int', 'float', 'number'}
        string_types = {'str', 'string', 'text'}
        boolean_types = {'bool', 'boolean'}
        
        # Check if all types are numeric
        if data_types.issubset(numeric_types):
            if 'float' in data_types:
                return 'float'  # Float is more general than int
            else:
                return 'int'
        
        # Check if all types are string-like
        if data_types.issubset(string_types):
            return 'str'
        
        # Check if all types are boolean
        if data_types.issubset(boolean_types):
            return 'bool'
        
        # For now, if types are incompatible, use 'any'
        return 'any'

    def _position_interface_pins(self, group, input_pins: List[GroupInterfacePin], output_pins: List[GroupInterfacePin]):
        """
        Position interface pins on the group boundary.
        
        Args:
            group: The Group instance
            input_pins: List of input interface pins
            output_pins: List of output interface pins
        """
        group_bounds = group.boundingRect()
        
        # Position input pins on the left side
        if input_pins:
            input_spacing = group_bounds.height() / (len(input_pins) + 1)
            for i, pin in enumerate(input_pins):
                y_offset = input_spacing * (i + 1)
                pin.setPos(group_bounds.left() - pin.radius, group_bounds.top() + y_offset)
        
        # Position output pins on the right side
        if output_pins:
            output_spacing = group_bounds.height() / (len(output_pins) + 1)
            for i, pin in enumerate(output_pins):
                y_offset = output_spacing * (i + 1)
                pin.setPos(group_bounds.right() + pin.radius, group_bounds.top() + y_offset)

    def update_interface_pins(self, group, selected_node_uuids: List[str]) -> Dict[str, Any]:
        """
        Update existing interface pins when group composition changes.
        
        Args:
            group: The Group instance
            selected_node_uuids: Updated list of node UUIDs in the group
            
        Returns:
            Dict containing update results
        """
        # Get current interface pins
        current_input_pins = getattr(group, 'input_interface_pins', [])
        current_output_pins = getattr(group, 'output_interface_pins', [])
        
        # Generate new interface pins
        new_pins = self.generate_interface_pins(group, selected_node_uuids)
        
        # Compare and update
        pins_added = []
        pins_removed = []
        pins_modified = []
        
        # For now, implement a simple replacement strategy
        # More sophisticated diff logic can be added later
        pins_removed.extend(current_input_pins)
        pins_removed.extend(current_output_pins)
        pins_added.extend(new_pins['input_pins'])
        pins_added.extend(new_pins['output_pins'])
        
        # Update group's interface pins
        group.input_interface_pins = new_pins['input_pins']
        group.output_interface_pins = new_pins['output_pins']
        
        return {
            'pins_added': pins_added,
            'pins_removed': pins_removed,
            'pins_modified': pins_modified,
            'total_pins': len(pins_added)
        }

    def validate_pin_generation(self, group, selected_node_uuids: List[str]) -> Tuple[bool, str]:
        """
        Validate that interface pin generation is feasible for the given selection.
        
        Args:
            group: The Group instance
            selected_node_uuids: List of node UUIDs to be grouped
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Use connection analyzer validation
        is_valid, error_msg = self.connection_analyzer.validate_grouping_feasibility(selected_node_uuids)
        
        if not is_valid:
            return False, error_msg
        
        # Additional pin generation specific validation
        analysis = self.connection_analyzer.analyze_external_connections(selected_node_uuids)
        
        # Check for reasonable number of interface pins
        total_interfaces = len(analysis['input_interfaces']) + len(analysis['output_interfaces'])
        if total_interfaces > 50:  # Arbitrary limit for performance
            return False, f"Too many interface pins required ({total_interfaces}). Consider grouping fewer nodes."
        
        # Check for type conflicts
        type_conflicts = self.connection_analyzer._detect_type_conflicts(analysis)
        if type_conflicts:
            return False, f"Type conflicts prevent pin generation: {'; '.join(type_conflicts)}"
        
        return True, ""

    def get_generation_preview(self, selected_node_uuids: List[str]) -> Dict[str, Any]:
        """
        Generate a preview of interface pins that would be created for a selection.
        
        Args:
            selected_node_uuids: List of node UUIDs being considered for grouping
            
        Returns:
            Dict containing preview information
        """
        analysis = self.connection_analyzer.analyze_external_connections(selected_node_uuids)
        
        # Group interfaces for preview
        input_grouped = self._group_interfaces_by_characteristics(analysis['input_interfaces'])
        output_grouped = self._group_interfaces_by_characteristics(analysis['output_interfaces'])
        
        input_preview = []
        for group_key, interfaces in input_grouped.items():
            pin_name = self._generate_pin_name(interfaces, "input")
            pin_type = self._infer_pin_type(interfaces)
            input_preview.append({
                'name': pin_name,
                'type': pin_type,
                'category': interfaces[0]['pin_category'],
                'connection_count': len(interfaces)
            })
        
        output_preview = []
        for group_key, interfaces in output_grouped.items():
            pin_name = self._generate_pin_name(interfaces, "output")
            pin_type = self._infer_pin_type(interfaces)
            output_preview.append({
                'name': pin_name,
                'type': pin_type,
                'category': interfaces[0]['pin_category'],
                'connection_count': len(interfaces)
            })
        
        return {
            'input_pins_preview': input_preview,
            'output_pins_preview': output_preview,
            'total_input_pins': len(input_preview),
            'total_output_pins': len(output_preview),
            'total_external_connections': len(analysis['input_interfaces']) + len(analysis['output_interfaces']),
            'analysis_summary': analysis['analysis_summary']
        }
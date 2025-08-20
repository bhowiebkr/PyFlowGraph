# connection_analyzer.py
# Connection analysis for group interface detection and pin generation.

import sys
import os
from typing import List, Dict, Any, Set, Tuple, Optional

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ConnectionAnalyzer:
    """
    Analyzes connections between nodes to detect external connections
    for group interface pin generation.
    """

    def __init__(self, node_graph):
        """
        Initialize the connection analyzer.
        
        Args:
            node_graph: The NodeGraph instance containing nodes and connections
        """
        self.node_graph = node_graph

    def analyze_external_connections(self, selected_node_uuids: List[str]) -> Dict[str, Any]:
        """
        Analyze connections crossing the boundary of selected nodes.
        
        Args:
            selected_node_uuids: List of UUIDs of nodes being grouped
            
        Returns:
            Dict containing analysis results:
            {
                'input_interfaces': List of required input interface pins,
                'output_interfaces': List of required output interface pins,
                'internal_connections': List of connections within the group,
                'analysis_summary': Summary statistics
            }
        """
        selected_uuids_set = set(selected_node_uuids)
        input_interfaces = []
        output_interfaces = []
        internal_connections = []
        
        # Track processed connections to avoid duplicates
        processed_connections = set()
        
        for connection in self.node_graph.connections:
            if not connection.start_pin or not connection.end_pin:
                continue
                
            start_node_uuid = connection.start_pin.node.uuid
            end_node_uuid = connection.end_pin.node.uuid
            
            connection_id = f"{start_node_uuid}-{end_node_uuid}-{connection.start_pin.uuid}-{connection.end_pin.uuid}"
            if connection_id in processed_connections:
                continue
            processed_connections.add(connection_id)
            
            start_is_selected = start_node_uuid in selected_uuids_set
            end_is_selected = end_node_uuid in selected_uuids_set
            
            if start_is_selected and end_is_selected:
                # Internal connection - stays within the group
                internal_connections.append({
                    'connection': connection,
                    'start_node_uuid': start_node_uuid,
                    'end_node_uuid': end_node_uuid,
                    'start_pin': connection.start_pin,
                    'end_pin': connection.end_pin
                })
            elif start_is_selected and not end_is_selected:
                # Output interface needed - internal node connects to external node
                output_interfaces.append({
                    'type': 'output',
                    'internal_pin': connection.start_pin,
                    'external_pin': connection.end_pin,
                    'internal_node_uuid': start_node_uuid,
                    'external_node_uuid': end_node_uuid,
                    'connection': connection,
                    'data_type': connection.start_pin.pin_type,
                    'pin_category': connection.start_pin.pin_category
                })
            elif not start_is_selected and end_is_selected:
                # Input interface needed - external node connects to internal node
                input_interfaces.append({
                    'type': 'input',
                    'internal_pin': connection.end_pin,
                    'external_pin': connection.start_pin,
                    'internal_node_uuid': end_node_uuid,
                    'external_node_uuid': start_node_uuid,
                    'connection': connection,
                    'data_type': connection.end_pin.pin_type,
                    'pin_category': connection.end_pin.pin_category
                })

        return {
            'input_interfaces': input_interfaces,
            'output_interfaces': output_interfaces,
            'internal_connections': internal_connections,
            'analysis_summary': {
                'total_external_connections': len(input_interfaces) + len(output_interfaces),
                'input_interfaces_count': len(input_interfaces),
                'output_interfaces_count': len(output_interfaces),
                'internal_connections_count': len(internal_connections),
                'selected_nodes_count': len(selected_node_uuids)
            }
        }

    def detect_crossing_connections(self, selected_node_uuids: List[str]) -> List[Dict[str, Any]]:
        """
        Detect all connections that cross the group boundary.
        
        Args:
            selected_node_uuids: List of UUIDs of nodes being grouped
            
        Returns:
            List of crossing connection information
        """
        analysis = self.analyze_external_connections(selected_node_uuids)
        crossing_connections = []
        
        # Add input crossing connections
        for interface in analysis['input_interfaces']:
            crossing_connections.append({
                'direction': 'input',
                'connection': interface['connection'],
                'internal_pin': interface['internal_pin'],
                'external_pin': interface['external_pin'],
                'data_type': interface['data_type'],
                'pin_category': interface['pin_category']
            })
        
        # Add output crossing connections
        for interface in analysis['output_interfaces']:
            crossing_connections.append({
                'direction': 'output',
                'connection': interface['connection'],
                'internal_pin': interface['internal_pin'],
                'external_pin': interface['external_pin'],
                'data_type': interface['data_type'],
                'pin_category': interface['pin_category']
            })
        
        return crossing_connections

    def analyze_connection_types(self, selected_node_uuids: List[str]) -> Dict[str, Set[str]]:
        """
        Analyze data types of connections crossing the group boundary.
        
        Args:
            selected_node_uuids: List of UUIDs of nodes being grouped
            
        Returns:
            Dict mapping direction ('input'/'output') to set of data types
        """
        analysis = self.analyze_external_connections(selected_node_uuids)
        type_analysis = {
            'input': set(),
            'output': set()
        }
        
        for interface in analysis['input_interfaces']:
            type_analysis['input'].add(interface['data_type'])
        
        for interface in analysis['output_interfaces']:
            type_analysis['output'].add(interface['data_type'])
        
        return type_analysis

    def get_data_flow_requirements(self, selected_node_uuids: List[str]) -> Dict[str, Any]:
        """
        Analyze data flow requirements for interface pin generation.
        
        Args:
            selected_node_uuids: List of UUIDs of nodes being grouped
            
        Returns:
            Dict containing data flow analysis
        """
        analysis = self.analyze_external_connections(selected_node_uuids)
        
        # Group interfaces by data type and direction
        input_by_type = {}
        output_by_type = {}
        
        for interface in analysis['input_interfaces']:
            data_type = interface['data_type']
            if data_type not in input_by_type:
                input_by_type[data_type] = []
            input_by_type[data_type].append(interface)
        
        for interface in analysis['output_interfaces']:
            data_type = interface['data_type']
            if data_type not in output_by_type:
                output_by_type[data_type] = []
            output_by_type[data_type].append(interface)
        
        return {
            'input_by_type': input_by_type,
            'output_by_type': output_by_type,
            'total_input_interfaces': len(analysis['input_interfaces']),
            'total_output_interfaces': len(analysis['output_interfaces']),
            'unique_input_types': len(input_by_type),
            'unique_output_types': len(output_by_type)
        }

    def handle_multiple_connections_to_external_node(self, selected_node_uuids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Handle edge cases with multiple connections to the same external node.
        
        Args:
            selected_node_uuids: List of UUIDs of nodes being grouped
            
        Returns:
            Dict mapping external node UUIDs to list of connection details
        """
        analysis = self.analyze_external_connections(selected_node_uuids)
        external_node_connections = {}
        
        # Process input interfaces
        for interface in analysis['input_interfaces']:
            ext_uuid = interface['external_node_uuid']
            if ext_uuid not in external_node_connections:
                external_node_connections[ext_uuid] = []
            external_node_connections[ext_uuid].append(interface)
        
        # Process output interfaces
        for interface in analysis['output_interfaces']:
            ext_uuid = interface['external_node_uuid']
            if ext_uuid not in external_node_connections:
                external_node_connections[ext_uuid] = []
            external_node_connections[ext_uuid].append(interface)
        
        # Filter to only include external nodes with multiple connections
        multiple_connections = {
            ext_uuid: connections 
            for ext_uuid, connections in external_node_connections.items()
            if len(connections) > 1
        }
        
        return multiple_connections

    def validate_grouping_feasibility(self, selected_node_uuids: List[str]) -> Tuple[bool, str]:
        """
        Validate whether the selected nodes can be grouped based on connection analysis.
        
        Args:
            selected_node_uuids: List of UUIDs of nodes being grouped
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(selected_node_uuids) < 2:
            return False, "Groups require at least 2 nodes"
        
        # Check if all nodes exist
        existing_uuids = {node.uuid for node in self.node_graph.nodes if hasattr(node, 'uuid')}
        missing_nodes = set(selected_node_uuids) - existing_uuids
        if missing_nodes:
            return False, f"Selected nodes not found: {', '.join(missing_nodes)}"
        
        # Analyze connections for potential issues
        analysis = self.analyze_external_connections(selected_node_uuids)
        
        # Check for circular dependencies
        if self._has_circular_dependencies(selected_node_uuids, analysis):
            return False, "Circular dependencies detected in selection"
        
        # Check for type conflicts
        type_conflicts = self._detect_type_conflicts(analysis)
        if type_conflicts:
            return False, f"Type conflicts detected: {', '.join(type_conflicts)}"
        
        return True, ""

    def _has_circular_dependencies(self, selected_node_uuids: List[str], analysis: Dict[str, Any]) -> bool:
        """
        Check for circular dependencies in the selected nodes.
        
        Args:
            selected_node_uuids: List of UUIDs of nodes being grouped
            analysis: Connection analysis results
            
        Returns:
            True if circular dependencies are detected
        """
        # Build dependency graph from internal connections
        dependencies = {}
        for conn_info in analysis['internal_connections']:
            start_uuid = conn_info['start_node_uuid']
            end_uuid = conn_info['end_node_uuid']
            
            if start_uuid not in dependencies:
                dependencies[start_uuid] = set()
            dependencies[start_uuid].add(end_uuid)
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_uuid):
            if node_uuid in rec_stack:
                return True
            if node_uuid in visited:
                return False
            
            visited.add(node_uuid)
            rec_stack.add(node_uuid)
            
            for neighbor in dependencies.get(node_uuid, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node_uuid)
            return False
        
        for node_uuid in selected_node_uuids:
            if node_uuid not in visited:
                if has_cycle(node_uuid):
                    return True
        
        return False

    def _detect_type_conflicts(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Detect type conflicts in interface pin generation.
        
        Args:
            analysis: Connection analysis results
            
        Returns:
            List of type conflict descriptions
        """
        conflicts = []
        
        # Check for conflicting types on same interface points
        input_types_by_pin = {}
        output_types_by_pin = {}
        
        for interface in analysis['input_interfaces']:
            pin_key = interface['internal_pin'].uuid
            pin_type = interface['data_type']
            
            if pin_key not in input_types_by_pin:
                input_types_by_pin[pin_key] = set()
            input_types_by_pin[pin_key].add(pin_type)
        
        for interface in analysis['output_interfaces']:
            pin_key = interface['internal_pin'].uuid
            pin_type = interface['data_type']
            
            if pin_key not in output_types_by_pin:
                output_types_by_pin[pin_key] = set()
            output_types_by_pin[pin_key].add(pin_type)
        
        # Check for conflicts where same pin has multiple incompatible types
        for pin_key, types in input_types_by_pin.items():
            if len(types) > 1 and 'any' not in types:
                conflicts.append(f"Input pin {pin_key} has conflicting types: {', '.join(types)}")
        
        for pin_key, types in output_types_by_pin.items():
            if len(types) > 1 and 'any' not in types:
                conflicts.append(f"Output pin {pin_key} has conflicting types: {', '.join(types)}")
        
        return conflicts
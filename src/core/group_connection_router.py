# group_connection_router.py
# Connection routing and data flow system for group interface pins.

import sys
import os
from typing import List, Dict, Any, Optional, Tuple, Set

from PySide6.QtCore import QObject, Signal

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class GroupConnectionRouter(QObject):
    """
    Manages connection routing between group interface pins and internal node pins.
    Handles data flow preservation and connection updates during group operations.
    """
    
    # Signals for data flow events
    dataFlowUpdated = Signal(str)  # Emitted when data flow is updated
    routingError = Signal(str, str)  # Emitted when routing error occurs (pin_id, error_msg)
    
    def __init__(self, node_graph, parent=None):
        """
        Initialize the connection router.
        
        Args:
            node_graph: The NodeGraph instance
            parent: Qt parent object
        """
        super().__init__(parent)
        self.node_graph = node_graph
        self.routing_tables = {}  # Maps group UUIDs to routing information
        self.active_data_flows = {}  # Tracks active data flows through groups

    def create_routing_for_group(self, group, interface_pins: Dict[str, List]) -> Dict[str, Any]:
        """
        Create routing table for a group's interface pins.
        
        Args:
            group: The Group instance
            interface_pins: Dict with 'input_pins' and 'output_pins' lists
            
        Returns:
            Dict containing routing information
        """
        group_uuid = group.uuid
        routing_table = {
            'group_uuid': group_uuid,
            'input_routes': {},
            'output_routes': {},
            'internal_connections': {},
            'data_flow_map': {}
        }
        
        # Create routing for input interface pins
        for input_pin in interface_pins.get('input_pins', []):
            route_info = self._create_input_route(input_pin)
            routing_table['input_routes'][input_pin.uuid] = route_info
        
        # Create routing for output interface pins
        for output_pin in interface_pins.get('output_pins', []):
            route_info = self._create_output_route(output_pin)
            routing_table['output_routes'][output_pin.uuid] = route_info
        
        # Map internal connections for data flow tracking
        routing_table['internal_connections'] = self._map_internal_connections(group)
        
        # Store routing table
        self.routing_tables[group_uuid] = routing_table
        
        return routing_table

    def _create_input_route(self, interface_pin) -> Dict[str, Any]:
        """
        Create routing information for an input interface pin.
        
        Args:
            interface_pin: GroupInterfacePin instance
            
        Returns:
            Dict containing route information
        """
        return {
            'interface_pin_uuid': interface_pin.uuid,
            'direction': 'input',
            'pin_type': interface_pin.pin_type,
            'pin_category': interface_pin.pin_category,
            'internal_targets': interface_pin.internal_pin_mappings.copy(),
            'external_source': None,  # Will be set when external connection is made
            'data_transformation': None,  # For future data transformation support
            'routing_status': 'active'
        }

    def _create_output_route(self, interface_pin) -> Dict[str, Any]:
        """
        Create routing information for an output interface pin.
        
        Args:
            interface_pin: GroupInterfacePin instance
            
        Returns:
            Dict containing route information
        """
        return {
            'interface_pin_uuid': interface_pin.uuid,
            'direction': 'output',
            'pin_type': interface_pin.pin_type,
            'pin_category': interface_pin.pin_category,
            'internal_sources': interface_pin.internal_pin_mappings.copy(),
            'external_targets': [],  # Will be populated when external connections are made
            'data_aggregation': None,  # For future data aggregation support
            'routing_status': 'active'
        }

    def _map_internal_connections(self, group) -> Dict[str, Any]:
        """
        Map internal connections within a group for data flow tracking.
        
        Args:
            group: The Group instance
            
        Returns:
            Dict containing internal connection mapping
        """
        internal_connections = {}
        member_uuids = set(group.member_node_uuids)
        
        # Find all connections between group members
        for connection in self.node_graph.connections:
            if not connection.start_pin or not connection.end_pin:
                continue
            
            start_node_uuid = connection.start_pin.node.uuid
            end_node_uuid = connection.end_pin.node.uuid
            
            if start_node_uuid in member_uuids and end_node_uuid in member_uuids:
                connection_id = f"{start_node_uuid}_{connection.start_pin.uuid}_{end_node_uuid}_{connection.end_pin.uuid}"
                internal_connections[connection_id] = {
                    'connection': connection,
                    'start_node_uuid': start_node_uuid,
                    'end_node_uuid': end_node_uuid,
                    'start_pin_uuid': connection.start_pin.uuid,
                    'end_pin_uuid': connection.end_pin.uuid,
                    'data_type': connection.start_pin.pin_type,
                    'pin_category': connection.start_pin.pin_category
                }
        
        return internal_connections

    def route_external_data_to_group(self, group_uuid: str, interface_pin_uuid: str, data: Any) -> bool:
        """
        Route external data to a group through an input interface pin.
        
        Args:
            group_uuid: UUID of the target group
            interface_pin_uuid: UUID of the input interface pin
            data: Data to route
            
        Returns:
            True if routing successful, False otherwise
        """
        if group_uuid not in self.routing_tables:
            self.routingError.emit(interface_pin_uuid, f"No routing table for group {group_uuid}")
            return False
        
        routing_table = self.routing_tables[group_uuid]
        
        if interface_pin_uuid not in routing_table['input_routes']:
            self.routingError.emit(interface_pin_uuid, f"No input route for pin {interface_pin_uuid}")
            return False
        
        route_info = routing_table['input_routes'][interface_pin_uuid]
        
        # Route data to all internal target pins
        success_count = 0
        for internal_pin_uuid in route_info['internal_targets']:
            if self._set_internal_pin_data(internal_pin_uuid, data):
                success_count += 1
        
        # Update data flow tracking
        flow_id = f"{group_uuid}_{interface_pin_uuid}_{id(data)}"
        self.active_data_flows[flow_id] = {
            'group_uuid': group_uuid,
            'interface_pin_uuid': interface_pin_uuid,
            'data': data,
            'timestamp': self._get_current_timestamp(),
            'targets_reached': success_count
        }
        
        self.dataFlowUpdated.emit(f"Input data routed to {success_count} internal pins")
        return success_count > 0

    def route_group_data_to_external(self, group_uuid: str, interface_pin_uuid: str) -> Any:
        """
        Route data from a group through an output interface pin.
        
        Args:
            group_uuid: UUID of the source group
            interface_pin_uuid: UUID of the output interface pin
            
        Returns:
            The routed data or None if routing failed
        """
        if group_uuid not in self.routing_tables:
            self.routingError.emit(interface_pin_uuid, f"No routing table for group {group_uuid}")
            return None
        
        routing_table = self.routing_tables[group_uuid]
        
        if interface_pin_uuid not in routing_table['output_routes']:
            self.routingError.emit(interface_pin_uuid, f"No output route for pin {interface_pin_uuid}")
            return None
        
        route_info = routing_table['output_routes'][interface_pin_uuid]
        
        # Collect data from internal source pins
        collected_data = []
        for internal_pin_uuid in route_info['internal_sources']:
            pin_data = self._get_internal_pin_data(internal_pin_uuid)
            if pin_data is not None:
                collected_data.append(pin_data)
        
        # For now, use simple data aggregation (first non-None value)
        # More sophisticated aggregation can be added later
        result_data = collected_data[0] if collected_data else None
        
        # Update data flow tracking
        if result_data is not None:
            flow_id = f"{group_uuid}_{interface_pin_uuid}_{id(result_data)}"
            self.active_data_flows[flow_id] = {
                'group_uuid': group_uuid,
                'interface_pin_uuid': interface_pin_uuid,
                'data': result_data,
                'timestamp': self._get_current_timestamp(),
                'sources_collected': len(collected_data)
            }
            
            self.dataFlowUpdated.emit(f"Output data collected from {len(collected_data)} internal pins")
        
        return result_data

    def _set_internal_pin_data(self, pin_uuid: str, data: Any) -> bool:
        """
        Set data on an internal node pin.
        
        Args:
            pin_uuid: UUID of the target pin
            data: Data to set
            
        Returns:
            True if successful, False otherwise
        """
        target_pin = self._find_pin_by_uuid(pin_uuid)
        if target_pin and hasattr(target_pin, 'value'):
            target_pin.value = data
            return True
        return False

    def _get_internal_pin_data(self, pin_uuid: str) -> Any:
        """
        Get data from an internal node pin.
        
        Args:
            pin_uuid: UUID of the source pin
            
        Returns:
            Pin data or None if not found
        """
        source_pin = self._find_pin_by_uuid(pin_uuid)
        if source_pin and hasattr(source_pin, 'value'):
            return source_pin.value
        return None

    def _find_pin_by_uuid(self, pin_uuid: str):
        """
        Find a pin by its UUID in the node graph.
        
        Args:
            pin_uuid: UUID of the pin to find
            
        Returns:
            Pin object or None if not found
        """
        for node in self.node_graph.nodes:
            if hasattr(node, 'pins'):
                for pin in node.pins:
                    if hasattr(pin, 'uuid') and pin.uuid == pin_uuid:
                        return pin
        return None

    def update_routing_for_interface_pin_change(self, group_uuid: str, interface_pin_uuid: str, 
                                                new_mappings: List[str]) -> bool:
        """
        Update routing when interface pin mappings change.
        
        Args:
            group_uuid: UUID of the group
            interface_pin_uuid: UUID of the interface pin
            new_mappings: New list of internal pin UUIDs
            
        Returns:
            True if update successful, False otherwise
        """
        if group_uuid not in self.routing_tables:
            return False
        
        routing_table = self.routing_tables[group_uuid]
        
        # Update input route if it exists
        if interface_pin_uuid in routing_table['input_routes']:
            routing_table['input_routes'][interface_pin_uuid]['internal_targets'] = new_mappings.copy()
            self.dataFlowUpdated.emit(f"Updated input routing for pin {interface_pin_uuid}")
            return True
        
        # Update output route if it exists
        if interface_pin_uuid in routing_table['output_routes']:
            routing_table['output_routes'][interface_pin_uuid]['internal_sources'] = new_mappings.copy()
            self.dataFlowUpdated.emit(f"Updated output routing for pin {interface_pin_uuid}")
            return True
        
        return False

    def preserve_connections_during_grouping(self, group, original_connections: List) -> Dict[str, Any]:
        """
        Preserve external connections during group creation by rerouting through interface pins.
        
        Args:
            group: The Group instance
            original_connections: List of original external connections
            
        Returns:
            Dict containing preservation results
        """
        preservation_results = {
            'preserved_connections': [],
            'failed_connections': [],
            'interface_connections_created': []
        }
        
        group_uuid = group.uuid
        if group_uuid not in self.routing_tables:
            preservation_results['failed_connections'] = original_connections
            return preservation_results
        
        routing_table = self.routing_tables[group_uuid]
        
        for connection in original_connections:
            try:
                # Determine if this is an input or output connection to the group
                start_in_group = connection.start_pin.node.uuid in group.member_node_uuids
                end_in_group = connection.end_pin.node.uuid in group.member_node_uuids
                
                if start_in_group and not end_in_group:
                    # Output connection - find appropriate output interface pin
                    interface_pin = self._find_matching_output_interface_pin(
                        routing_table, connection.start_pin
                    )
                    if interface_pin:
                        self._create_interface_to_external_connection(interface_pin, connection.end_pin)
                        preservation_results['interface_connections_created'].append({
                            'type': 'output',
                            'interface_pin': interface_pin,
                            'external_pin': connection.end_pin
                        })
                    else:
                        preservation_results['failed_connections'].append(connection)
                
                elif not start_in_group and end_in_group:
                    # Input connection - find appropriate input interface pin
                    interface_pin = self._find_matching_input_interface_pin(
                        routing_table, connection.end_pin
                    )
                    if interface_pin:
                        self._create_external_to_interface_connection(connection.start_pin, interface_pin)
                        preservation_results['interface_connections_created'].append({
                            'type': 'input',
                            'interface_pin': interface_pin,
                            'external_pin': connection.start_pin
                        })
                    else:
                        preservation_results['failed_connections'].append(connection)
                
                preservation_results['preserved_connections'].append(connection)
                
            except Exception as e:
                preservation_results['failed_connections'].append({
                    'connection': connection,
                    'error': str(e)
                })
        
        return preservation_results

    def _find_matching_output_interface_pin(self, routing_table: Dict[str, Any], internal_pin):
        """
        Find the output interface pin that routes to a specific internal pin.
        
        Args:
            routing_table: Group routing table
            internal_pin: Internal pin to find interface for
            
        Returns:
            Interface pin object or None
        """
        for interface_pin_uuid, route_info in routing_table['output_routes'].items():
            if internal_pin.uuid in route_info['internal_sources']:
                return self._find_interface_pin_by_uuid(interface_pin_uuid)
        return None

    def _find_matching_input_interface_pin(self, routing_table: Dict[str, Any], internal_pin):
        """
        Find the input interface pin that routes to a specific internal pin.
        
        Args:
            routing_table: Group routing table
            internal_pin: Internal pin to find interface for
            
        Returns:
            Interface pin object or None
        """
        for interface_pin_uuid, route_info in routing_table['input_routes'].items():
            if internal_pin.uuid in route_info['internal_targets']:
                return self._find_interface_pin_by_uuid(interface_pin_uuid)
        return None

    def _find_interface_pin_by_uuid(self, pin_uuid: str):
        """
        Find an interface pin by UUID.
        
        Args:
            pin_uuid: UUID of the interface pin
            
        Returns:
            Interface pin object or None
        """
        # Search through all groups for interface pins
        if hasattr(self.node_graph, 'groups'):
            for group in self.node_graph.groups:
                # Check input interface pins
                if hasattr(group, 'input_interface_pins'):
                    for pin in group.input_interface_pins:
                        if hasattr(pin, 'uuid') and pin.uuid == pin_uuid:
                            return pin
                
                # Check output interface pins
                if hasattr(group, 'output_interface_pins'):
                    for pin in group.output_interface_pins:
                        if hasattr(pin, 'uuid') and pin.uuid == pin_uuid:
                            return pin
        
        return None

    def _create_interface_to_external_connection(self, interface_pin, external_pin):
        """
        Create a connection from an interface pin to an external pin.
        
        Args:
            interface_pin: The group interface pin
            external_pin: The external pin
        """
        # This would integrate with the existing connection system
        # For now, we just track the logical connection
        pass

    def _create_external_to_interface_connection(self, external_pin, interface_pin):
        """
        Create a connection from an external pin to an interface pin.
        
        Args:
            external_pin: The external pin
            interface_pin: The group interface pin
        """
        # This would integrate with the existing connection system
        # For now, we just track the logical connection
        pass

    def _get_current_timestamp(self) -> float:
        """
        Get current timestamp for data flow tracking.
        
        Returns:
            Current timestamp
        """
        import time
        return time.time()

    def get_routing_status(self, group_uuid: str) -> Dict[str, Any]:
        """
        Get routing status for a group.
        
        Args:
            group_uuid: UUID of the group
            
        Returns:
            Dict containing routing status information
        """
        if group_uuid not in self.routing_tables:
            return {'status': 'no_routing_table', 'group_uuid': group_uuid}
        
        routing_table = self.routing_tables[group_uuid]
        
        return {
            'status': 'active',
            'group_uuid': group_uuid,
            'input_routes_count': len(routing_table['input_routes']),
            'output_routes_count': len(routing_table['output_routes']),
            'internal_connections_count': len(routing_table['internal_connections']),
            'active_data_flows': len([
                flow for flow in self.active_data_flows.values()
                if flow['group_uuid'] == group_uuid
            ])
        }

    def cleanup_routing_for_group(self, group_uuid: str):
        """
        Clean up routing information when a group is deleted.
        
        Args:
            group_uuid: UUID of the group to clean up
        """
        if group_uuid in self.routing_tables:
            del self.routing_tables[group_uuid]
        
        # Clean up active data flows for this group
        flows_to_remove = [
            flow_id for flow_id, flow_info in self.active_data_flows.items()
            if flow_info['group_uuid'] == group_uuid
        ]
        
        for flow_id in flows_to_remove:
            del self.active_data_flows[flow_id]
        
        self.dataFlowUpdated.emit(f"Cleaned up routing for group {group_uuid}")

    def validate_routing_integrity(self, group_uuid: str) -> Dict[str, Any]:
        """
        Validate the integrity of routing for a group.
        
        Args:
            group_uuid: UUID of the group to validate
            
        Returns:
            Dict containing validation results
        """
        if group_uuid not in self.routing_tables:
            return {
                'is_valid': False,
                'errors': ['No routing table found'],
                'warnings': []
            }
        
        routing_table = self.routing_tables[group_uuid]
        errors = []
        warnings = []
        
        # Validate input routes
        for pin_uuid, route_info in routing_table['input_routes'].items():
            # Check if interface pin exists
            interface_pin = self._find_interface_pin_by_uuid(pin_uuid)
            if not interface_pin:
                errors.append(f"Input interface pin {pin_uuid} not found")
            
            # Check if internal target pins exist
            for target_uuid in route_info['internal_targets']:
                if not self._find_pin_by_uuid(target_uuid):
                    warnings.append(f"Internal target pin {target_uuid} not found")
        
        # Validate output routes
        for pin_uuid, route_info in routing_table['output_routes'].items():
            # Check if interface pin exists
            interface_pin = self._find_interface_pin_by_uuid(pin_uuid)
            if not interface_pin:
                errors.append(f"Output interface pin {pin_uuid} not found")
            
            # Check if internal source pins exist
            for source_uuid in route_info['internal_sources']:
                if not self._find_pin_by_uuid(source_uuid):
                    warnings.append(f"Internal source pin {source_uuid} not found")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'routes_validated': len(routing_table['input_routes']) + len(routing_table['output_routes'])
        }
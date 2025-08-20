# group_type_inference.py
# Advanced type inference system for group interface pins with conflict resolution.

import sys
import os
from typing import List, Dict, Any, Set, Tuple, Optional, Union

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TypeInferenceEngine:
    """
    Advanced type inference engine for group interface pins.
    Handles type compatibility, conflict resolution, and priority rules.
    """

    def __init__(self):
        """Initialize the type inference engine with predefined type rules."""
        self._setup_type_hierarchy()
        self._setup_compatibility_rules()
        self._setup_priority_rules()

    def _setup_type_hierarchy(self):
        """Setup type hierarchy for inheritance and compatibility checking."""
        self.type_hierarchy = {
            # Numeric types hierarchy
            'number': set(),  # Most general numeric type
            'float': {'number'},
            'int': {'number', 'float'},
            'byte': {'int', 'float', 'number'},
            
            # String types hierarchy
            'text': set(),  # Most general text type
            'string': {'text'},
            'str': {'text', 'string'},
            'char': {'str', 'string', 'text'},
            
            # Boolean types
            'boolean': set(),
            'bool': {'boolean'},
            
            # Container types
            'collection': set(),
            'list': {'collection'},
            'array': {'collection', 'list'},
            'dict': {'collection'},
            'map': {'collection', 'dict'},
            
            # Special types
            'any': set(),  # Can accept anything
            'object': set(),  # General object type
            'none': set(),  # Null/None type
            'exec': set(),  # Execution flow type
        }

    def _setup_compatibility_rules(self):
        """Setup rules for type compatibility and conversion."""
        self.compatibility_rules = {
            # Numeric compatibility
            ('int', 'float'): 'float',
            ('int', 'number'): 'number',
            ('float', 'number'): 'number',
            ('byte', 'int'): 'int',
            ('byte', 'float'): 'float',
            
            # String compatibility
            ('char', 'str'): 'str',
            ('char', 'string'): 'string',
            ('str', 'string'): 'string',
            ('str', 'text'): 'text',
            ('string', 'text'): 'text',
            
            # Boolean compatibility
            ('bool', 'boolean'): 'boolean',
            
            # Container compatibility
            ('array', 'list'): 'list',
            ('list', 'collection'): 'collection',
            ('dict', 'map'): 'dict',
            ('map', 'collection'): 'collection',
            
            # Any type compatibility
            ('any', '*'): 'any',  # Any can be combined with anything
            ('*', 'any'): 'any',
        }

    def _setup_priority_rules(self):
        """Setup priority rules for type selection when multiple options exist."""
        self.type_priorities = {
            # Higher number = higher priority
            'any': 1,  # Lowest priority - only use if necessary
            'object': 2,
            'text': 3,
            'string': 4,
            'str': 5,
            'number': 6,
            'float': 7,
            'int': 8,
            'bool': 9,
            'boolean': 9,
            'collection': 3,
            'list': 4,
            'array': 5,
            'dict': 4,
            'map': 5,
            'exec': 10,  # Execution pins have highest priority
        }

    def infer_interface_pin_type(self, connected_pins: List[Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Infer the appropriate type for an interface pin based on connected pins.
        
        Args:
            connected_pins: List of pins connected to this interface
            
        Returns:
            Tuple of (inferred_type, inference_details)
        """
        if not connected_pins:
            return 'any', {'reason': 'no_connected_pins', 'confidence': 0.0}
        
        # Extract types from connected pins
        pin_types = []
        for pin in connected_pins:
            if hasattr(pin, 'pin_type'):
                pin_types.append(pin.pin_type)
            else:
                pin_types.append('any')  # Fallback for pins without type info
        
        return self.resolve_type_from_list(pin_types)

    def resolve_type_from_list(self, types: List[str]) -> Tuple[str, Dict[str, Any]]:
        """
        Resolve a single type from a list of types using priority rules.
        
        Args:
            types: List of type strings
            
        Returns:
            Tuple of (resolved_type, resolution_details)
        """
        if not types:
            return 'any', {'reason': 'empty_type_list', 'confidence': 0.0}
        
        # Remove duplicates while preserving order
        unique_types = list(dict.fromkeys(types))
        
        if len(unique_types) == 1:
            # Single type - direct inheritance
            return unique_types[0], {
                'reason': 'single_type',
                'confidence': 1.0,
                'input_types': unique_types
            }
        
        # Handle 'any' type special case
        if 'any' in unique_types:
            return 'any', {
                'reason': 'any_type_present',
                'confidence': 0.8,
                'input_types': unique_types
            }
        
        # Try to find compatible type
        compatible_type = self._find_compatible_type(unique_types)
        if compatible_type:
            return compatible_type, {
                'reason': 'compatible_types_found',
                'confidence': 0.9,
                'input_types': unique_types,
                'compatible_type': compatible_type
            }
        
        # Check for type conflicts
        conflicts = self._detect_type_conflicts(unique_types)
        if conflicts:
            return 'any', {
                'reason': 'type_conflicts',
                'confidence': 0.3,
                'input_types': unique_types,
                'conflicts': conflicts
            }
        
        # Use most specific common type
        common_type = self._find_most_specific_common_type(unique_types)
        return common_type, {
            'reason': 'most_specific_common_type',
            'confidence': 0.7,
            'input_types': unique_types,
            'common_type': common_type
        }

    def _find_compatible_type(self, types: List[str]) -> Optional[str]:
        """
        Find a compatible type that can represent all input types.
        
        Args:
            types: List of type strings
            
        Returns:
            Compatible type string or None if no compatibility found
        """
        if len(types) < 2:
            return types[0] if types else None
        
        # Start with the first type and try to find compatibility with others
        result_type = types[0]
        
        for i in range(1, len(types)):
            current_type = types[i]
            
            # Check direct compatibility
            compatibility_key = tuple(sorted([result_type, current_type]))
            if compatibility_key in self.compatibility_rules:
                result_type = self.compatibility_rules[compatibility_key]
                continue
            
            # Check wildcard compatibility (with 'any')
            if result_type == 'any' or current_type == 'any':
                result_type = 'any'
                continue
            
            # Check type hierarchy
            hierarchy_result = self._check_type_hierarchy_compatibility(result_type, current_type)
            if hierarchy_result:
                result_type = hierarchy_result
                continue
            
            # No compatibility found
            return None
        
        return result_type

    def _check_type_hierarchy_compatibility(self, type1: str, type2: str) -> Optional[str]:
        """
        Check if two types are compatible through type hierarchy.
        
        Args:
            type1: First type string
            type2: Second type string
            
        Returns:
            Compatible type or None if incompatible
        """
        # Check if type1 is a subtype of type2
        if type1 in self.type_hierarchy and type2 in self.type_hierarchy.get(type1, set()):
            return type2  # More general type
        
        # Check if type2 is a subtype of type1
        if type2 in self.type_hierarchy and type1 in self.type_hierarchy.get(type2, set()):
            return type1  # More general type
        
        # Check for common parent in hierarchy
        if type1 in self.type_hierarchy and type2 in self.type_hierarchy:
            type1_parents = self.type_hierarchy[type1]
            type2_parents = self.type_hierarchy[type2]
            
            # Find common parents
            common_parents = type1_parents.intersection(type2_parents)
            if common_parents:
                # Return the most specific common parent
                return self._select_most_specific_type(list(common_parents))
        
        return None

    def _detect_type_conflicts(self, types: List[str]) -> List[Dict[str, Any]]:
        """
        Detect conflicts between types that cannot be reconciled.
        
        Args:
            types: List of type strings
            
        Returns:
            List of conflict descriptions
        """
        conflicts = []
        
        # Define incompatible type groups
        incompatible_groups = [
            {'numeric': {'int', 'float', 'number', 'byte'}},
            {'text': {'str', 'string', 'text', 'char'}},
            {'boolean': {'bool', 'boolean'}},
            {'execution': {'exec'}},
            {'containers': {'list', 'array', 'dict', 'map', 'collection'}}
        ]
        
        # Check for cross-group conflicts
        type_set = set(types)
        groups_present = []
        
        for group_info in incompatible_groups:
            group_name = list(group_info.keys())[0]
            group_types = list(group_info.values())[0]
            
            if type_set.intersection(group_types):
                groups_present.append(group_name)
        
        # If types from different incompatible groups are present, it's a conflict
        if len(groups_present) > 1:
            conflicts.append({
                'type': 'cross_group_conflict',
                'groups': groups_present,
                'conflicting_types': list(type_set)
            })
        
        # Check for specific known conflicts
        known_conflicts = [
            ({'exec'}, {'int', 'float', 'str', 'bool'}),  # Execution vs data types
            ({'bool'}, {'int', 'float'}) # Boolean vs numeric (in some contexts)
        ]
        
        for conflict_set1, conflict_set2 in known_conflicts:
            if type_set.intersection(conflict_set1) and type_set.intersection(conflict_set2):
                conflicts.append({
                    'type': 'known_conflict',
                    'set1': list(conflict_set1),
                    'set2': list(conflict_set2),
                    'present_types': list(type_set)
                })
        
        return conflicts

    def _find_most_specific_common_type(self, types: List[str]) -> str:
        """
        Find the most specific type that can represent all input types.
        
        Args:
            types: List of type strings
            
        Returns:
            Most specific common type
        """
        if not types:
            return 'any'
        
        if len(types) == 1:
            return types[0]
        
        # Find all possible parent types for each input type
        all_possible_types = set()
        
        for type_str in types:
            possible_types = {type_str}  # Include the type itself
            if type_str in self.type_hierarchy:
                possible_types.update(self.type_hierarchy[type_str])
            all_possible_types.update(possible_types)
        
        # Find types that can represent all input types
        compatible_types = []
        for candidate_type in all_possible_types:
            can_represent_all = True
            
            for input_type in types:
                if not self._can_type_represent(candidate_type, input_type):
                    can_represent_all = False
                    break
            
            if can_represent_all:
                compatible_types.append(candidate_type)
        
        if not compatible_types:
            return 'any'  # Fallback
        
        # Select the most specific (highest priority) compatible type
        return self._select_most_specific_type(compatible_types)

    def _can_type_represent(self, parent_type: str, child_type: str) -> bool:
        """
        Check if a parent type can represent a child type.
        
        Args:
            parent_type: The potential parent type
            child_type: The child type to be represented
            
        Returns:
            True if parent can represent child
        """
        if parent_type == child_type:
            return True
        
        if parent_type == 'any':
            return True  # 'any' can represent anything
        
        if child_type in self.type_hierarchy:
            return parent_type in self.type_hierarchy[child_type]
        
        return False

    def _select_most_specific_type(self, types: List[str]) -> str:
        """
        Select the most specific type from a list based on priority rules.
        
        Args:
            types: List of type strings
            
        Returns:
            Most specific type
        """
        if not types:
            return 'any'
        
        # Sort by priority (highest first)
        prioritized_types = sorted(
            types,
            key=lambda t: self.type_priorities.get(t, 0),
            reverse=True
        )
        
        return prioritized_types[0]

    def validate_type_compatibility(self, interface_type: str, connected_types: List[str]) -> Dict[str, Any]:
        """
        Validate that an interface pin type is compatible with connected pin types.
        
        Args:
            interface_type: The proposed interface pin type
            connected_types: List of types from connected pins
            
        Returns:
            Validation result dictionary
        """
        if not connected_types:
            return {
                'is_valid': True,
                'confidence': 1.0,
                'reason': 'no_connected_types'
            }
        
        # Check if interface type can represent all connected types
        incompatible_types = []
        
        for connected_type in connected_types:
            if not self._can_type_represent(interface_type, connected_type):
                incompatible_types.append(connected_type)
        
        if incompatible_types:
            return {
                'is_valid': False,
                'confidence': 0.0,
                'reason': 'incompatible_types',
                'incompatible_types': incompatible_types,
                'suggestion': self._suggest_alternative_type(connected_types)
            }
        
        # Calculate confidence based on how well the type fits
        confidence = self._calculate_type_confidence(interface_type, connected_types)
        
        return {
            'is_valid': True,
            'confidence': confidence,
            'reason': 'types_compatible',
            'interface_type': interface_type,
            'connected_types': connected_types
        }

    def _suggest_alternative_type(self, connected_types: List[str]) -> str:
        """
        Suggest an alternative type when validation fails.
        
        Args:
            connected_types: List of connected pin types
            
        Returns:
            Suggested alternative type
        """
        suggested_type, _ = self.resolve_type_from_list(connected_types)
        return suggested_type

    def _calculate_type_confidence(self, interface_type: str, connected_types: List[str]) -> float:
        """
        Calculate confidence score for type compatibility.
        
        Args:
            interface_type: The interface pin type
            connected_types: List of connected pin types
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if interface_type == 'any':
            return 0.5  # 'any' is always compatible but not specific
        
        exact_matches = sum(1 for t in connected_types if t == interface_type)
        total_types = len(connected_types)
        
        if exact_matches == total_types:
            return 1.0  # Perfect match
        
        if exact_matches > 0:
            return 0.8 + (exact_matches / total_types) * 0.2  # Partial exact matches
        
        # Check for hierarchy matches
        hierarchy_matches = sum(1 for t in connected_types if self._can_type_represent(interface_type, t))
        
        if hierarchy_matches == total_types:
            return 0.7  # All types compatible through hierarchy
        
        return 0.3  # Low confidence for remaining cases

    def get_type_conversion_suggestions(self, from_types: List[str], to_type: str) -> List[Dict[str, Any]]:
        """
        Get suggestions for converting from one set of types to another.
        
        Args:
            from_types: List of source types
            to_type: Target type
            
        Returns:
            List of conversion suggestion dictionaries
        """
        suggestions = []
        
        for from_type in from_types:
            if from_type == to_type:
                suggestions.append({
                    'from_type': from_type,
                    'to_type': to_type,
                    'conversion': 'none',
                    'confidence': 1.0
                })
                continue
            
            # Check for automatic conversion possibilities
            if self._can_type_represent(to_type, from_type):
                suggestions.append({
                    'from_type': from_type,
                    'to_type': to_type,
                    'conversion': 'automatic_upcast',
                    'confidence': 0.9
                })
                continue
            
            # Check for lossy conversion possibilities
            if self._can_type_represent(from_type, to_type):
                suggestions.append({
                    'from_type': from_type,
                    'to_type': to_type,
                    'conversion': 'lossy_downcast',
                    'confidence': 0.6,
                    'warning': 'May lose information'
                })
                continue
            
            # No direct conversion found
            suggestions.append({
                'from_type': from_type,
                'to_type': to_type,
                'conversion': 'incompatible',
                'confidence': 0.0,
                'suggestion': 'Consider using \'any\' type'
            })
        
        return suggestions
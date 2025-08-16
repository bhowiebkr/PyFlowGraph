# BUG-2025-01-001: Reroute Nodes Return None in Execution

**Status**: Open  
**Priority**: High  
**Component**: Execution Engine, Reroute Nodes  
**Reporter**: Development Team  
**Date**: 2025-01-16  

## Summary

Reroute nodes are not properly passing data during graph execution, resulting in None values being propagated instead of the actual data values.

## Description

When executing graphs that contain reroute nodes, the data read from those nodes returns None instead of the expected values that should be passed through from the input connection. This breaks data flow continuity in graphs that use reroute nodes for visual organization.

## Steps to Reproduce

1. Create a graph with nodes that produce data
2. Insert a reroute node on a connection between data-producing and data-consuming nodes
3. Execute the graph
4. Observe that the data after the reroute node is None instead of the expected value

## Expected Behavior

Reroute nodes should act as transparent pass-through points, forwarding the exact data received on their input pin to their output pin without modification.

## Actual Behavior

Reroute nodes output None values during execution, effectively breaking the data flow chain.

## Impact

- **Severity**: High - Breaks core functionality for graphs using reroute nodes
- **User Impact**: Users cannot rely on reroute nodes for graph organization
- **Workaround**: Avoid using reroute nodes in executable graphs

## Related Issues

### Undo/Redo System Interactions

Additional investigation needed for undo/redo operations involving reroute nodes:

1. **Execution State After Undo/Redo**: 
   - Need to verify that undo/redo operations maintain proper execution state
   - Ensure execution data integrity after command operations

2. **Reroute Creation/Deletion Undo**:
   - Creating a reroute node on an existing connection, then undoing the operation
   - Need to verify the original connection is properly restored and functional
   - Check that data flow works correctly after reroute removal via undo

## Technical Notes

- Issue likely in `src/reroute_node.py` execution handling
- May be related to how reroute nodes interface with `src/graph_executor.py`
- Could be a data serialization/deserialization issue in the execution pipeline
- Undo/redo commands in `src/commands/` may need validation for execution state consistency

## Investigation Areas

1. **RerouteNode Class**: Check data passing implementation
2. **Graph Executor**: Verify reroute node handling in execution pipeline  
3. **Command System**: Validate undo/redo operations maintain execution integrity
4. **Connection Restoration**: Ensure connections work after reroute removal

## Testing Requirements

- Unit tests for reroute node data passing
- Integration tests for execution with reroute nodes
- Undo/redo system tests with reroute operations
- Connection integrity tests after undo operations
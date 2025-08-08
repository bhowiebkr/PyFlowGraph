# graph_executor.py
# New data-driven engine for executing the node graph.

import traceback
import io
from contextlib import redirect_stdout
from collections import deque

class GraphExecutor:
    """
    Executes the graph based on data dependencies. A node runs
    only when all its data inputs are available.
    """
    def __init__(self, graph, log_widget):
        self.graph = graph
        self.log = log_widget

    def execute(self):
        """Prepare and run the graph execution."""
        
        # --- State Tracking ---
        # Stores the computed value for each pin
        pin_values = {} 
        # Tracks how many inputs are still needed for a node to be ready
        node_input_dependencies = {node: 0 for node in self.graph.nodes}
        # A queue of nodes that are ready to be executed
        execution_queue = deque()

        # --- Initialization ---
        for node in self.graph.nodes:
            # Count how many connected data inputs each node has
            num_deps = sum(1 for pin in node.input_pins if pin.connections)
            node_input_dependencies[node] = num_deps
            
            # If a node has no connected inputs, it's a start node
            if num_deps == 0:
                execution_queue.append(node)

        if not execution_queue:
            self.log.append("Execution Error: No start node found (a node with no inputs).")
            return

        # --- Execution Loop ---
        execution_count = 0
        execution_limit = len(self.graph.nodes) * 2 # Safety break for cycles

        while execution_queue and execution_count < execution_limit:
            execution_count += 1
            
            # Get the next ready node
            current_node = execution_queue.popleft()
            self.log.append(f"--- Executing Node: {current_node.title} ---")

            # --- Prepare Inputs ---
            local_scope = {}
            for pin in current_node.input_pins:
                if pin.connections:
                    source_pin = pin.connections[0].start_pin
                    local_scope[pin.name] = pin_values.get(source_pin)
                else:
                    # For unconnected inputs, we can provide a default or None
                    local_scope[pin.name] = None
            
            # --- Execute Code ---
            f = io.StringIO()
            try:
                with redirect_stdout(f):
                    exec(current_node.code, {}, local_scope)
                
                log_output = f.getvalue()
                if log_output:
                    self.log.append(log_output.strip())

            except Exception as e:
                self.log.append(f"ERROR in node '{current_node.title}': {e}")
                self.log.append(traceback.format_exc())
                return # Stop on error

            # --- Propagate Outputs ---
            for pin in current_node.output_pins:
                pin_values[pin] = local_scope.get(pin.name, None)
                
                # For each downstream connection...
                for conn in pin.connections:
                    downstream_node = conn.end_pin.node
                    # Decrement the dependency count for the downstream node
                    node_input_dependencies[downstream_node] -= 1
                    # If all its inputs are now met, add it to the queue
                    if node_input_dependencies[downstream_node] == 0:
                        execution_queue.append(downstream_node)

        if execution_count >= execution_limit:
            self.log.append("EXECUTION ERROR: Limit reached. Check for cyclic dependencies.")


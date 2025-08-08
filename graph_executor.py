# graph_executor.py
# New data-driven engine that executes a defined function within each node.
# Now defines the @node_entry decorator at runtime to prevent errors.

import traceback
import io
from contextlib import redirect_stdout
from collections import deque

class GraphExecutor:
    """
    Executes the graph by calling a defined function in each node
    once all its data inputs are available.
    """
    def __init__(self, graph, log_widget):
        self.graph = graph
        self.log = log_widget

    def execute(self):
        """Prepare and run the graph execution."""
        pin_values = {} 
        node_input_dependencies = {node: 0 for node in self.graph.nodes}
        execution_queue = deque()

        for node in self.graph.nodes:
            num_deps = sum(1 for pin in node.input_pins if pin.connections)
            node_input_dependencies[node] = num_deps
            if num_deps == 0:
                execution_queue.append(node)

        if not execution_queue:
            self.log.append("Execution Error: No start node found (a node with no connected inputs).")
            return

        execution_count = 0
        execution_limit = len(self.graph.nodes) * 2

        while execution_queue and execution_count < execution_limit:
            execution_count += 1
            current_node = execution_queue.popleft()
            self.log.append(f"--- Executing Node: {current_node.title} ---")

            # --- Prepare Inputs ---
            inputs_for_function = {}
            for pin in current_node.input_pins:
                if pin.connections:
                    source_pin = pin.connections[0].start_pin
                    inputs_for_function[pin.name] = pin_values.get(source_pin)
                else:
                    inputs_for_function[pin.name] = None
            
            # --- Execute Code ---
            if not current_node.function_name:
                self.log.append(f"SKIP: Node '{current_node.title}' has no valid function defined.")
                continue

            # BUG FIX: Define a pass-through decorator to make the @node_entry syntax
            # valid Python code when the node's script is executed.
            def node_entry(func):
                return func

            # This scope will contain the executed code's definitions.
            execution_scope = {
                'node_entry': node_entry
            }
            f = io.StringIO()
            try:
                # Execute the entire code block, defining everything in the same scope.
                exec(current_node.code, execution_scope)
                node_function = execution_scope[current_node.function_name]

                # Call the function with prepared inputs
                with redirect_stdout(f):
                    result = node_function(**inputs_for_function)
                
                log_output = f.getvalue()
                if log_output: self.log.append(log_output.strip())

            except Exception as e:
                self.log.append(f"ERROR in node '{current_node.title}': {e}")
                self.log.append(traceback.format_exc())
                return

            # --- Propagate Outputs ---
            output_pins = current_node.output_pins
            if len(output_pins) == 1:
                pin_values[output_pins[0]] = result
            elif len(output_pins) > 1:
                if isinstance(result, (list, tuple)) and len(result) == len(output_pins):
                    for i, pin in enumerate(output_pins):
                        pin_values[pin] = result[i]
                else:
                    self.log.append(f"WARNING: Node '{current_node.title}' return count mismatch.")

            for pin in current_node.output_pins:
                for conn in pin.connections:
                    downstream_node = conn.end_pin.node
                    node_input_dependencies[downstream_node] -= 1
                    if node_input_dependencies[downstream_node] == 0:
                        execution_queue.append(downstream_node)

        if execution_count >= execution_limit:
            self.log.append("EXECUTION ERROR: Limit reached. Check for cyclic dependencies.")

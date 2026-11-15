# graph_executor.py
# Executes the graph using direct function calls in a single shared Python interpreter.
# Replaced subprocess isolation with single process execution for maximum performance.

import os
import sys


from pyflowgraph.core.node import Node
from pyflowgraph.core.reroute_node import RerouteNode
from .single_process_executor import SingleProcessExecutor
import logging

logger = logging.getLogger(__name__)


class GraphExecutor:
    def __init__(self, graph, log_widget, venv_path_callback):
        self.graph = graph
        self.log = log_widget
        self.get_venv_path = venv_path_callback
        
        # Get venv path for package loading
        venv_path = self.get_venv_path() if self.get_venv_path else None
        
        # Initialize single process executor with venv path
        self.single_process_executor = SingleProcessExecutor(log_widget, venv_path)

    def refresh_executor_environment(self):
        """Recreate the SingleProcessExecutor with updated venv path when environment changes."""
        # Get current venv path
        venv_path = self.get_venv_path() if self.get_venv_path else None
        
        # Recreate the SingleProcessExecutor with new venv path
        self.single_process_executor = SingleProcessExecutor(self.log, venv_path)
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Recreated SingleProcessExecutor with venv_path: {venv_path}")

    def get_python_executable(self):
        """Get the Python executable path for the virtual environment."""
        venv_path = self.get_venv_path() if self.get_venv_path else None
        if venv_path and os.path.exists(venv_path):
            if sys.platform == "win32":
                return os.path.join(venv_path, "Scripts", "python.exe")
            else:
                return os.path.join(venv_path, "bin", "python")
        return sys.executable

    def execute(self):
        """Execute the graph using single process execution with direct object references."""
        # Single process execution doesn't require venv validation - it runs in current process
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Starting single process execution")

        # Pin values now store direct Python object references (no JSON serialization)
        pin_values = {}
        
        # Find entry point nodes (nodes with no execution input connections)
        entry_nodes = []
        for node in self.graph.nodes:
            if isinstance(node, Node):
                exec_input_pins = [p for p in node.input_pins if p.pin_category == "execution"]
                has_exec_input = any(pin.connections for pin in exec_input_pins)
                if not has_exec_input:
                    entry_nodes.append(node)
            # A reroute node is not a start node: it has no code, and its value comes from
            # the output before it (see _value_source).

        if not entry_nodes:
            self.log.append("EXECUTION ERROR: No entry point nodes found. Add nodes without execution inputs to start execution.")
            return

        execution_count = 0
        execution_limit = len(self.graph.nodes) * 10  # Higher limit for flow control

        # Execute starting from entry nodes
        for entry_node in entry_nodes:
            if execution_count >= execution_limit:
                break
            execution_count = self._execute_node_flow(entry_node, pin_values, execution_count, execution_limit)

        if execution_count >= execution_limit:
            self.log.append("EXECUTION ERROR: Execution limit reached. Check for infinite loops in execution flow.")
        
        # Log performance statistics
        stats = self.single_process_executor.get_performance_stats()
        if stats and logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Execution completed. Total time: {stats.get('total_time', 0):.4f}s, "
                          f"Average per node: {stats.get('average_time', 0):.4f}s")

    def _execute_node_flow(self, node, pin_values, execution_count, execution_limit):
        """Execute a node using direct function calls and follow its execution outputs."""
        if execution_count >= execution_limit:
            return execution_count
            
        execution_count += 1

        if isinstance(node, RerouteNode):
            # Handle reroute nodes - direct object reference passing
            if node.input_pin.connections:
                source_pin = node.input_pin.connections[0].start_pin
                pin_values[node.output_pin] = pin_values.get(source_pin)
            
            # Follow connections from reroute node
            for conn in node.output_pin.connections:
                downstream_node = conn.end_pin.node
                execution_count = self._execute_node_flow(downstream_node, pin_values, execution_count, execution_limit)
            return execution_count

        self.log.append(f"--- Executing Node: {node.title} ---")

        # Gather input data from data pins - now using direct object references
        inputs_for_function = {}
        data_input_pins = [p for p in node.input_pins if p.pin_category == "data"]
        for pin in data_input_pins:
            if pin.connections:
                source_pin = self._value_source(pin)
                # Direct object reference - no JSON serialization
                inputs_for_function[pin.name] = pin_values.get(source_pin)
        
        if hasattr(node, "get_gui_values"):
            inputs_for_function.update(node.get_gui_values())

        if not node.function_name:
            self.log.append(f"SKIP: Node '{node.title}' has no valid function defined.")
            # Still follow execution flow even if no function
            self._follow_execution_outputs(node, pin_values, execution_count, execution_limit)
            return execution_count

        # Execute the node using SingleProcessExecutor (direct function call)
        try:
            result, output_message = self.single_process_executor.execute_node(node, inputs_for_function)
            
            if output_message:
                self.log.append(output_message)
                
        except Exception as e:
            self.log.append(str(e))
            return execution_count

        # Store results in data output pins using direct object references
        data_output_pins = [p for p in node.output_pins if p.pin_category == "data"]
        output_values = {}
        
        if len(data_output_pins) == 1:
            # Single output - store result directly (no JSON conversion)
            pin_values[data_output_pins[0]] = result
            output_values[data_output_pins[0].name] = result
        elif len(data_output_pins) > 1 and isinstance(result, (list, tuple)):
            # Multiple outputs - distribute tuple/list items
            for i, pin in enumerate(data_output_pins):
                if i < len(result):
                    pin_values[pin] = result[i]
                    output_values[pin.name] = result[i]

        # Update GUI with output values
        if hasattr(node, "set_gui_values"):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Execution completed for '{node.title}', calling set_gui_values with: {output_values}")
            node.set_gui_values(output_values)
        else:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Node '{node.title}' does not have set_gui_values method")

        # Follow execution flow to next nodes
        execution_count = self._follow_execution_outputs(node, pin_values, execution_count, execution_limit)
        return execution_count

    @staticmethod
    def _value_source(input_pin):
        """Return the output pin that gives the value of a connected input pin.

        Reroute nodes only change the path of a connection, so follow them back to the first
        output pin of a normal node. Return None when the chain has no source.
        """
        source_pin = input_pin.connections[0].start_pin
        seen = set()
        while isinstance(source_pin.node, RerouteNode):
            reroute = source_pin.node
            if id(reroute) in seen or not reroute.input_pin.connections:
                return None
            seen.add(id(reroute))
            source_pin = reroute.input_pin.connections[0].start_pin
        return source_pin

    def _follow_execution_outputs(self, node, pin_values, execution_count, execution_limit):
        """Follow execution output connections to continue the flow."""
        exec_output_pins = [p for p in node.output_pins if p.pin_category == "execution"]
        for pin in exec_output_pins:
            for conn in pin.connections:
                downstream_node = conn.end_pin.node
                execution_count = self._execute_node_flow(downstream_node, pin_values, execution_count, execution_limit)
        return execution_count

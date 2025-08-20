# graph_executor.py
# Executes the graph by running each node's code in an isolated subprocess.
# Now hides the subprocess console window on Windows.

import subprocess
import json
import os
import sys

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.node import Node
from core.reroute_node import RerouteNode

# Debug configuration
# Set to True to enable detailed execution flow debugging
DEBUG_EXECUTION = False


class GraphExecutor:
    def __init__(self, graph, log_widget, venv_path_callback):
        self.graph = graph
        self.log = log_widget
        self.get_venv_path = venv_path_callback

    def get_python_executable(self):
        """Returns the path to the Python executable in the venv."""
        venv_path = self.get_venv_path()
        if sys.platform == "win32":
            return os.path.join(venv_path, "Scripts", "python.exe")
        else:
            return os.path.join(venv_path, "bin", "python")

    def execute(self):
        """Execute the graph using flow control with execution pins."""
        python_exe = self.get_python_executable()
        if not os.path.exists(python_exe):
            self.log.append("EXECUTION ERROR: Virtual environment not found. Please set it up via the 'Run > Manage Environment' menu.")
            return

        pin_values = {}
        
        # Find entry point nodes (nodes with no execution input connections)
        entry_nodes = []
        for node in self.graph.nodes:
            if isinstance(node, Node):
                exec_input_pins = [p for p in node.input_pins if p.pin_category == "execution"]
                has_exec_input = any(pin.connections for pin in exec_input_pins)
                if not has_exec_input:
                    entry_nodes.append(node)
            elif isinstance(node, RerouteNode):
                # RerouteNodes don't have execution pins, handle separately
                if not node.input_pin.connections:
                    entry_nodes.append(node)

        if not entry_nodes:
            self.log.append("EXECUTION ERROR: No entry point nodes found. Add nodes without execution inputs to start execution.")
            return

        execution_count = 0
        execution_limit = len(self.graph.nodes) * 10  # Higher limit for flow control

        # Execute starting from entry nodes
        for entry_node in entry_nodes:
            if execution_count >= execution_limit:
                break
            self._execute_node_flow(entry_node, pin_values, execution_count, execution_limit)

        if execution_count >= execution_limit:
            self.log.append("EXECUTION ERROR: Execution limit reached. Check for infinite loops in execution flow.")

    def _execute_node_flow(self, node, pin_values, execution_count, execution_limit):
        """Execute a node and follow its execution outputs."""
        if execution_count >= execution_limit:
            return execution_count
            
        execution_count += 1

        if isinstance(node, RerouteNode):
            # Handle reroute nodes
            if node.input_pin.connections:
                source_pin = node.input_pin.connections[0].start_pin
                pin_values[node.output_pin] = pin_values.get(source_pin)
            
            # Follow connections from reroute node
            for conn in node.output_pin.connections:
                downstream_node = conn.end_pin.node
                execution_count = self._execute_node_flow(downstream_node, pin_values, execution_count, execution_limit)
            return execution_count

        self.log.append(f"--- Executing Node: {node.title} ---")

        # Gather input data from data pins only
        inputs_for_function = {}
        data_input_pins = [p for p in node.input_pins if p.pin_category == "data"]
        for pin in data_input_pins:
            if pin.connections:
                source_pin = pin.connections[0].start_pin
                inputs_for_function[pin.name] = pin_values.get(source_pin)
        
        if hasattr(node, "get_gui_values"):
            inputs_for_function.update(node.get_gui_values())

        if not node.function_name:
            self.log.append(f"SKIP: Node '{node.title}' has no valid function defined.")
            # Still follow execution flow even if no function
            self._follow_execution_outputs(node, pin_values, execution_count, execution_limit)
            return execution_count

        # Execute the node's function
        python_exe = self.get_python_executable()
        runner_script = (
            f"import json, sys, io\n"
            f"from contextlib import redirect_stdout\n"
            f"def node_entry(func): return func\n"
            f"{node.code}\n"
            f"input_str = sys.stdin.read()\n"
            f"inputs = json.loads(input_str) if input_str else {{}}\n"
            f"stdout_capture = io.StringIO()\n"
            f"return_value = None\n"
            f"with redirect_stdout(stdout_capture):\n"
            f"    return_value = {node.function_name}(**inputs)\n"
            f"printed_output = stdout_capture.getvalue()\n"
            f"final_output = {{'result': return_value, 'stdout': printed_output}}\n"
            f"json.dump(final_output, sys.stdout)\n"
        )

        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.run([python_exe, "-c", runner_script], 
                                   input=json.dumps(inputs_for_function), 
                                   capture_output=True, text=True, check=True, 
                                   creationflags=creation_flags)

            response = json.loads(process.stdout)
            result, printed_output = response.get("result"), response.get("stdout")
            if printed_output:
                self.log.append(printed_output.strip())
            if process.stderr:
                self.log.append(f"STDERR: {process.stderr.strip()}")
        except Exception as e:
            self.log.append(f"ERROR in node '{node.title}': {e}")
            if hasattr(e, "stderr"):
                self.log.append(e.stderr)
            return execution_count

        # Store results in data output pins
        data_output_pins = [p for p in node.output_pins if p.pin_category == "data"]
        output_values = {}
        if len(data_output_pins) == 1:
            pin_values[data_output_pins[0]] = result
            output_values[data_output_pins[0].name] = result
        elif len(data_output_pins) > 1 and isinstance(result, (list, tuple)):
            for i, pin in enumerate(data_output_pins):
                if i < len(result):
                    pin_values[pin] = result[i]
                    output_values[pin.name] = result[i]

        if hasattr(node, "set_gui_values"):
            if DEBUG_EXECUTION:
                print(f"DEBUG: Execution completed for '{node.title}', calling set_gui_values with: {output_values}")
            node.set_gui_values(output_values)
        else:
            if DEBUG_EXECUTION:
                print(f"DEBUG: Node '{node.title}' does not have set_gui_values method")

        # Follow execution flow to next nodes
        execution_count = self._follow_execution_outputs(node, pin_values, execution_count, execution_limit)
        return execution_count

    def _follow_execution_outputs(self, node, pin_values, execution_count, execution_limit):
        """Follow execution output pins to trigger next nodes."""
        exec_output_pins = [p for p in node.output_pins if p.pin_category == "execution"]
        
        for pin in exec_output_pins:
            for conn in pin.connections:
                downstream_node = conn.end_pin.node
                execution_count = self._execute_node_flow(downstream_node, pin_values, execution_count, execution_limit)
                if execution_count >= execution_limit:
                    break
        
        return execution_count

# graph_executor.py
# Executes the graph by running each node's code in an isolated subprocess.
# Now hides the subprocess console window on Windows.

import subprocess
import json
import os
import sys
from collections import deque
from node import Node
from reroute_node import RerouteNode


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
        """Prepare and run the graph execution using subprocesses."""
        python_exe = self.get_python_executable()
        if not os.path.exists(python_exe):
            self.log.append("EXECUTION ERROR: Virtual environment not found. Please set it up via the 'Run > Manage Environment' menu.")
            return

        pin_values = {}
        node_input_dependencies = {node: 0 for node in self.graph.nodes}
        execution_queue = deque()

        for node in self.graph.nodes:
            input_pins = []
            if isinstance(node, Node):
                input_pins = node.input_pins
            elif isinstance(node, RerouteNode):
                input_pins = [node.input_pin]
            num_deps = sum(1 for pin in input_pins if pin.connections)
            node_input_dependencies[node] = num_deps
            if num_deps == 0:
                execution_queue.append(node)

        execution_count = 0
        execution_limit = len(self.graph.nodes) * 2

        while execution_queue and execution_count < execution_limit:
            execution_count += 1
            current_node = execution_queue.popleft()

            if isinstance(current_node, RerouteNode):
                if current_node.input_pin.connections:
                    source_pin = current_node.input_pin.connections[0].start_pin
                    pin_values[current_node.output_pin] = pin_values.get(source_pin)
                for conn in current_node.output_pin.connections:
                    downstream_node = conn.end_pin.node
                    node_input_dependencies[downstream_node] -= 1
                    if node_input_dependencies[downstream_node] == 0:
                        execution_queue.append(downstream_node)
                continue

            self.log.append(f"--- Executing Node: {current_node.title} ---")

            inputs_for_function = {}
            for pin in current_node.input_pins:
                if pin.connections:
                    source_pin = pin.connections[0].start_pin
                    inputs_for_function[pin.name] = pin_values.get(source_pin)
            if hasattr(current_node, "get_gui_values"):
                inputs_for_function.update(current_node.get_gui_values())

            if not current_node.function_name:
                self.log.append(f"SKIP: Node '{current_node.title}' has no valid function defined.")
                continue

            runner_script = (
                f"import json, sys, io\n"
                f"from contextlib import redirect_stdout\n"
                f"def node_entry(func): return func\n"
                f"{current_node.code}\n"
                f"input_str = sys.stdin.read()\n"
                f"inputs = json.loads(input_str) if input_str else {{}}\n"
                f"stdout_capture = io.StringIO()\n"
                f"return_value = None\n"
                f"with redirect_stdout(stdout_capture):\n"
                f"    return_value = {current_node.function_name}(**inputs)\n"
                f"printed_output = stdout_capture.getvalue()\n"
                f"final_output = {{'result': return_value, 'stdout': printed_output}}\n"
                f"json.dump(final_output, sys.stdout)\n"
            )

            try:
                # --- Hide Console Window on Windows ---
                creation_flags = 0
                if sys.platform == "win32":
                    creation_flags = subprocess.CREATE_NO_WINDOW

                process = subprocess.run([python_exe, "-c", runner_script], input=json.dumps(inputs_for_function), capture_output=True, text=True, check=True, creationflags=creation_flags)

                response = json.loads(process.stdout)
                result, printed_output = response.get("result"), response.get("stdout")
                if printed_output:
                    self.log.append(printed_output.strip())
                if process.stderr:
                    self.log.append(f"STDERR: {process.stderr.strip()}")
            except Exception as e:
                self.log.append(f"ERROR in node '{current_node.title}': {e}")
                if hasattr(e, "stderr"):
                    self.log.append(e.stderr)
                return

            output_pins = current_node.output_pins
            output_values = {}
            if len(output_pins) == 1:
                pin_values[output_pins[0]] = result
                output_values[output_pins[0].name] = result
            elif len(output_pins) > 1 and isinstance(result, (list, tuple)):
                for i, pin in enumerate(output_pins):
                    if i < len(result):
                        pin_values[pin] = result[i]
                        output_values[pin.name] = result[i]

            if hasattr(current_node, "set_gui_values"):
                current_node.set_gui_values(output_values)

            for pin in current_node.output_pins:
                for conn in pin.connections:
                    downstream_node = conn.end_pin.node
                    node_input_dependencies[downstream_node] -= 1
                    if node_input_dependencies[downstream_node] == 0:
                        execution_queue.append(downstream_node)

        if execution_count >= execution_limit:
            self.log.append("EXECUTION ERROR: Limit reached. Check for cyclic dependencies.")

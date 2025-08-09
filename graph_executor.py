# graph_executor.py
# Executes the graph by running each node's code in an isolated subprocess
# using a dedicated virtual environment.

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

            inputs_for_function = {pin.name: pin_values.get(pin.connections[0].start_pin) for pin in current_node.input_pins if pin.connections}

            if not current_node.function_name:
                self.log.append(f"SKIP: Node '{current_node.title}' has no valid function defined.")
                continue

            runner_script = (
                f"import json, sys\n"
                f"def node_entry(func): return func\n"
                f"{current_node.code}\n"
                f"input_str = sys.stdin.read()\n"
                f"inputs = json.loads(input_str) if input_str else {{}}\n"
                f"result = {current_node.function_name}(**inputs)\n"
                f"json.dump(result, sys.stdout)\n"
            )

            try:
                process = subprocess.run([python_exe, "-c", runner_script], input=json.dumps(inputs_for_function), capture_output=True, text=True, check=True)
                result = json.loads(process.stdout)
                if process.stderr:
                    self.log.append(f"STDERR: {process.stderr.strip()}")

            except subprocess.CalledProcessError as e:
                self.log.append(f"ERROR in node '{current_node.title}': Subprocess failed.")
                self.log.append(e.stderr)
                return
            except json.JSONDecodeError as e:
                self.log.append(f"ERROR in node '{current_node.title}': Failed to decode result from node.")
                self.log.append(f"JSON Error: {e}")
                self.log.append(f"Received from stdout: '{process.stdout}'")
                self.log.append(f"Received from stderr: '{process.stderr}'")
                return
            except Exception as e:
                self.log.append(f"ERROR in node '{current_node.title}': {e}")
                return

            output_pins = current_node.output_pins
            if len(output_pins) == 1:
                pin_values[output_pins[0]] = result
            elif len(output_pins) > 1 and isinstance(result, (list, tuple)):
                for i, pin in enumerate(output_pins):
                    if i < len(result):
                        pin_values[pin] = result[i]

            for pin in current_node.output_pins:
                for conn in pin.connections:
                    downstream_node = conn.end_pin.node
                    node_input_dependencies[downstream_node] -= 1
                    if node_input_dependencies[downstream_node] == 0:
                        execution_queue.append(downstream_node)

        if execution_count >= execution_limit:
            self.log.append("EXECUTION ERROR: Limit reached. Check for cyclic dependencies.")

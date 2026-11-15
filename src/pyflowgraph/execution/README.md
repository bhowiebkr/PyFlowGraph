# Execution Module

This module runs the node code of a graph and manages the Python environments of the graphs.

Node code runs with `exec()` in the editor process. It is not a sandbox: node code can do what
the editor can do. The editor asks before it opens a graph that it does not trust. See
[SECURITY.md](../../../SECURITY.md).

## Files

### `graph_executor.py`

- **GraphExecutor** runs a graph in batch mode.
- It starts at the nodes that have no connected execution input, then follows the execution
  connections.
- Each node gets its inputs from the outputs before it. A reroute node passes on the value of
  the output before it.
- A run stops after ten times as many node runs as the graph has nodes.

### `single_process_executor.py`

- **SingleProcessExecutor** runs the code of one node in a namespace that stays between runs.
  Imported modules stay loaded.
- Values pass between nodes as Python objects, without serialization.
- `numpy`, `pandas`, `torch` and `tensorflow` are imported the first time node code uses the
  name.
- The site-packages folder of the graph's environment goes first on `sys.path`.

### `execution_controller.py`

- **ExecutionController** connects the **Batch** and **Live** buttons and the
  **Execute Graph** button to the executor.
- In live mode, events from the node widgets run the nodes.

### `environment_manager.py`

- **EnvironmentManagerDialog** is the **Manage Environment** dialog.
- **EnvironmentWorker** runs venv and pip in a worker thread. Each requirement must be one
  package. The setup stops when a requirement is a pip option.

### `default_environment_manager.py`

- **DefaultEnvironmentManager** makes the default environment in `venvs/default`, with PySide6.
- The ready check looks for files only, so it is fast.
- On the GUI thread, venv and pip run in a worker thread while a progress dialog shows.

# src

- `main.py` starts the editor. Python puts this folder on the import path, so `main.py` imports
  the `pyflowgraph` package with no path changes. Nuitka builds the Windows app from this file.
- `resources/` holds the Font Awesome fonts that `main.py` loads.
- `pyflowgraph/` is the editor package:
  - `commands/`: undo and redo, one command class for each change.
  - `core/`: nodes, pins, connections, reroute nodes, groups and the graph scene.
  - `data/`: open and save graph files, and the trust checks.
  - `execution/`: run a graph, and the virtual environments of graphs.
  - `ui/`: the main window, the view, the dialogs and the code editor.
  - `utils/`: small shared helpers.
  - `paths.py`: the folders of the examples and the virtual environments. The results do not
    depend on the current folder.

`pyproject.toml` in the repository root describes the package. `pip install -e .` installs it with
its dependencies, and pytest finds it through the `pythonpath` setting there.

Modules import each other as `pyflowgraph.<package>.<module>`, or with relative imports inside a
package. Each module logs through `logging.getLogger(__name__)`.

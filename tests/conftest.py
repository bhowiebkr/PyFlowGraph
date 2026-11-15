r"""Setup for every test file.

- The settings go to a temporary INI file, so that tests never change the real editor settings
  (on Windows, the registry key HKCU\Software\PyFlowGraph\NodeEditor).
- The settings point to a temporary folder of stub virtual environments, `default` and
  `untitled`. The editor checks only that their Python file exists, so the run button works
  and new graphs use `default` without asking.
- The editor starts with an empty canvas, not the default example.
- Tests never create the default environment. The editor would run pip for minutes.
- Qt windows stay hidden, unless QT_QPA_PLATFORM is already set. A hidden modal dialog waits
  forever, so every dialog and popup menu is answered with Cancel and the test output names it.
"""

import importlib
import os
import shutil
import sys
import tempfile

import pytest

_settings_dir = tempfile.mkdtemp(prefix="pyflowgraph_test_settings_")
_settings_file = os.path.join(_settings_dir, "NodeEditor.ini")
_venv_parent = os.path.join(_settings_dir, "venvs")

for _name in ("default", "untitled"):
    for _python in (("Scripts", "python.exe"), ("bin", "python")):
        _path = os.path.join(_venv_parent, _name, *_python)
        os.makedirs(os.path.dirname(_path), exist_ok=True)
        open(_path, "w").close()

with open(_settings_file, "w", encoding="utf-8") as _f:
    _f.write("[General]\n")
    _f.write("venv_parent_dir=" + _venv_parent.replace("\\", "/") + "\n")
    # Start with an empty canvas, not the default example.
    _f.write("default_graph=\n")
    _f.write("\n[graph_env_choice]\nuntitled=default\n")

os.environ["PYFLOWGRAPH_SETTINGS_FILE"] = _settings_file
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def pytest_unconfigure(config):
    shutil.rmtree(_settings_dir, ignore_errors=True)


def _note(kind, title=""):
    print(f"[conftest] answered {kind} {title!r} with Cancel", file=sys.stderr)


def _cancel_dialogs(patch, widgets):
    """Answer each modal dialog and each static dialog function with Cancel."""
    def dialog_exec(self, *args):
        _note("the dialog", self.windowTitle())
        return 0

    def message(parent, title, *args, **kwargs):
        _note("the message", title)
        return widgets.QMessageBox.StandardButton.Cancel

    def file_name(*args, **kwargs):
        _note("a file dialog")
        return "", ""

    def directory(*args, **kwargs):
        _note("a folder dialog")
        return ""

    def text(*args, **kwargs):
        _note("an input dialog")
        return "", False

    def menu_exec(self, *args):
        _note("the menu", self.title())
        return None

    patch.setattr(widgets.QDialog, "exec", dialog_exec)
    patch.setattr(widgets.QMessageBox, "exec", dialog_exec)
    patch.setattr(widgets.QMenu, "exec", menu_exec)
    for name in ("question", "warning", "information", "critical"):
        patch.setattr(widgets.QMessageBox, name, staticmethod(message))
    for name in ("getOpenFileName", "getSaveFileName"):
        patch.setattr(widgets.QFileDialog, name, staticmethod(file_name))
    patch.setattr(widgets.QFileDialog, "getExistingDirectory", staticmethod(directory))
    patch.setattr(widgets.QInputDialog, "getText", staticmethod(text))


def _default_environment_ready(self, log_widget=None):
    return os.path.isdir(self.default_venv_path)


@pytest.fixture(scope="session", autouse=True)
def _no_blocking_and_no_pip():
    """Applies only when the test file uses the real PySide6, not mocks."""
    widgets = sys.modules.get("PySide6.QtWidgets")
    if not isinstance(getattr(widgets, "QDialog", None), type):
        yield
        return
    with pytest.MonkeyPatch.context() as patch:
        _cancel_dialogs(patch, widgets)
        manager = importlib.import_module("pyflowgraph.execution.default_environment_manager")
        patch.setattr(manager.DefaultEnvironmentManager, "ensure_default_venv_exists",
                      _default_environment_ready)
        yield

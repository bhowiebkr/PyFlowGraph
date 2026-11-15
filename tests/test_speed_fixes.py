"""Tests for the speed changes: the default environment check, the environment setup off the GUI
thread, and the optional modules that node code imports on first use."""

import os
import subprocess
import sys
import threading
import time

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QTimer
from PySide6.QtWidgets import QApplication, QTextEdit

from pyflowgraph.core.node_graph import NodeGraph
from pyflowgraph.execution import default_environment_manager as dem
from pyflowgraph.execution import single_process_executor as spe


@pytest.fixture(scope="module", autouse=True)
def app():
    return QApplication.instance() or QApplication([])


def make_venv(root, with_pyside=True):
    if sys.platform == "win32":
        python = os.path.join(root, "default", "Scripts", "python.exe")
        site = os.path.join(root, "default", "Lib", "site-packages")
    else:
        python = os.path.join(root, "default", "bin", "python")
        site = os.path.join(root, "default", "lib", "python3.11", "site-packages")
    os.makedirs(os.path.dirname(python))
    open(python, "w").close()
    os.makedirs(os.path.join(site, "PySide6"))
    if with_pyside:
        open(os.path.join(site, "PySide6", "__init__.py"), "w").close()


def no_subprocess(*args, **kwargs):
    raise AssertionError("the check must not start a process")


def test_ready_check_reads_files_only(tmp_path, monkeypatch):
    monkeypatch.setattr(dem.subprocess, "run", no_subprocess)
    make_venv(str(tmp_path))
    assert dem.DefaultEnvironmentManager(str(tmp_path)).is_default_venv_ready()


def test_ready_check_needs_pyside(tmp_path, monkeypatch):
    monkeypatch.setattr(dem.subprocess, "run", no_subprocess)
    make_venv(str(tmp_path), with_pyside=False)
    assert not dem.DefaultEnvironmentManager(str(tmp_path)).is_default_venv_ready()
    assert not dem.DefaultEnvironmentManager(str(tmp_path / "none")).is_default_venv_ready()


def run_setup(tmp_path, monkeypatch, returncode):
    threads = []

    def slow_run(args, **kwargs):
        threads.append(threading.current_thread())
        time.sleep(0.3)
        return subprocess.CompletedProcess(args, returncode, "", "error text")

    monkeypatch.setattr(dem.subprocess, "run", slow_run)
    ticks = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(1))
    timer.start(50)
    log = QTextEdit()
    try:
        ok = dem.DefaultEnvironmentManager(str(tmp_path)).create_default_venv_sync(log)
    finally:
        timer.stop()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    return ok, log.toPlainText(), threads, ticks


def test_setup_runs_off_the_gui_thread_and_the_window_keeps_working(tmp_path, monkeypatch):
    ok, log, threads, ticks = run_setup(tmp_path, monkeypatch, 0)
    assert ok
    assert len(threads) == 2  # venv, then pip for PySide6
    assert all(t is not threading.main_thread() for t in threads)
    assert len(ticks) >= 5  # timers ran during the 0.6 seconds
    assert "Installing PySide6" in log
    assert "created successfully" in log


def test_setup_failure_returns_false_and_logs_the_error(tmp_path, monkeypatch):
    ok, log, threads, ticks = run_setup(tmp_path, monkeypatch, 1)
    assert not ok
    assert "Failed to create venv: error text" in log


def test_optional_modules_load_on_first_use(monkeypatch):
    imported = []
    fake = type(sys)("numpy")
    fake.marker = "fake numpy"

    def import_module(name):
        imported.append(name)
        if name == "numpy":
            return fake
        raise ImportError(name)

    monkeypatch.setattr(spe.importlib, "import_module", import_module)
    executor = spe.SingleProcessExecutor(None)
    assert imported == []

    graph = NodeGraph()
    node = graph.create_node("N", pos=(0, 0), use_command=False)
    node.set_code("@node_entry\ndef n() -> str:\n    return numpy.marker\n")
    result, _ = executor.execute_node(node, {})
    assert result == "fake numpy"
    assert imported == ["numpy"]

    node.set_code("@node_entry\ndef n() -> str:\n    return str(torch)\n")
    with pytest.raises(RuntimeError, match="name 'torch' is not defined"):
        executor.execute_node(node, {})

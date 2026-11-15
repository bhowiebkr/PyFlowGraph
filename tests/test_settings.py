"""The editor settings go to the file in PYFLOWGRAPH_SETTINGS_FILE when it is set."""

import os

from PySide6.QtCore import QSettings

from pyflowgraph.settings import SETTINGS_FILE_ENV, app_settings


def test_tests_use_a_temporary_settings_file():
    path = os.environ[SETTINGS_FILE_ENV]
    settings = app_settings()
    assert settings.format() == QSettings.Format.IniFormat
    assert os.path.normcase(os.path.abspath(settings.fileName())) == os.path.normcase(os.path.abspath(path))


def test_values_go_to_the_settings_file():
    settings = app_settings()
    settings.setValue("test/value", 42)
    settings.sync()
    assert os.path.exists(os.environ[SETTINGS_FILE_ENV])
    assert int(app_settings().value("test/value")) == 42


def test_without_the_variable_the_native_settings_are_used(monkeypatch):
    monkeypatch.delenv(SETTINGS_FILE_ENV)
    settings = app_settings()  # Only reads; the test writes nothing here.
    assert settings.format() == QSettings.Format.NativeFormat
    assert settings.organizationName() == "PyFlowGraph"
    assert settings.applicationName() == "NodeEditor"

r"""The editor settings.

Every part of the editor gets its settings from app_settings(). On Windows the settings are in
the registry key HKCU\Software\PyFlowGraph\NodeEditor. When the environment variable
PYFLOWGRAPH_SETTINGS_FILE names a file, the settings are in that INI file instead. The tests use
this, so that they never change the real settings.
"""

import os

from PySide6.QtCore import QSettings

ORGANIZATION = "PyFlowGraph"
APPLICATION = "NodeEditor"
SETTINGS_FILE_ENV = "PYFLOWGRAPH_SETTINGS_FILE"


def app_settings():
    """Return the editor settings."""
    path = os.environ.get(SETTINGS_FILE_ENV)
    if path:
        return QSettings(path, QSettings.Format.IniFormat)
    return QSettings(ORGANIZATION, APPLICATION)

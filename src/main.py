# main.py
# Starts the editor. Python puts the folder of this file (src/) on the import path, so the
# pyflowgraph package next to it imports with no path changes. Nuitka builds the Windows app
# from this file.

import logging
import os
import sys

from PySide6.QtCore import qInstallMessageHandler
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from pyflowgraph.ui.editor.node_editor_window import NodeEditorWindow

logger = logging.getLogger("pyflowgraph")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS = (
    "Font Awesome 7 Free-Regular-400.otf",
    "Font Awesome 6 Free-Solid-900.otf",
)
# The Windows build has the stylesheet next to the program; a checkout has it in the
# repository root.
STYLESHEET_PATHS = (
    os.path.join(APP_DIR, "dark_theme.qss"),
    os.path.join(os.path.dirname(APP_DIR), "dark_theme.qss"),
)
QT_MESSAGES_TO_IGNORE = ("qt.qpa.wayland.textinput",)


def setup_logging():
    """Send log messages to stderr. PYFLOWGRAPH_LOG_LEVEL sets the level, WARNING by default."""
    level_name = os.environ.get("PYFLOWGRAPH_LOG_LEVEL", "WARNING").upper()
    level = getattr(logging, level_name, None)
    if not isinstance(level, int):
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


def qt_message_handler(mode, context, message):
    """Pass Qt messages to stderr, except the ones known to be harmless."""
    if any(text in message for text in QT_MESSAGES_TO_IGNORE):
        return
    print(message, file=sys.stderr)


def load_fonts():
    for name in FONTS:
        path = os.path.join(APP_DIR, "resources", name)
        if not os.path.exists(path):
            logger.warning("Font file not found: %s", path)
        elif QFontDatabase.addApplicationFont(path) == -1:
            logger.warning("Could not load the font %s", path)


def load_stylesheet(app):
    for path in STYLESHEET_PATHS:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            return True
        except OSError as e:
            logger.warning("Could not read %s: %s", path, e)
    logger.warning("dark_theme.qss not found. Using the default style.")
    return False


def main():
    setup_logging()
    qInstallMessageHandler(qt_message_handler)
    app = QApplication(sys.argv)
    load_fonts()
    load_stylesheet(app)
    window = NodeEditorWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

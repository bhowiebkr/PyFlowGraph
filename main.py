# main.py
# Entry point for the Node Editor application.
# Now loads a QSS stylesheet and the Font Awesome font.

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import qInstallMessageHandler, QtMsgType
from PySide6.QtGui import QFontDatabase
from node_editor_window import NodeEditorWindow


def custom_message_handler(mode, context, message):
    """
    A custom message handler to filter out specific, non-critical warnings.
    """
    warnings_to_ignore = [
        "qt.qpa.wayland.textinput",
    ]
    if any(warning in message for warning in warnings_to_ignore):
        return
    print(message, file=sys.stderr)


if __name__ == "__main__":
    qInstallMessageHandler(custom_message_handler)
    app = QApplication(sys.argv)

    # --- Load Font Awesome ---
    font_path = os.path.join(os.path.dirname(__file__), "resources", "Font Awesome 6 Free-Solid-900.otf")
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Warning: Failed to load Font Awesome font.", file=sys.stderr)
    else:
        print("Warning: Font Awesome font file not found at 'resources/Font Awesome 6 Free-Solid-900.otf'", file=sys.stderr)

    # Load the dark theme stylesheet
    try:
        with open("dark_theme.qss", "r") as f:
            style = f.read()
            app.setStyleSheet(style)
    except FileNotFoundError:
        print("Warning: 'dark_theme.qss' not found. Using default style.", file=sys.stderr)

    # Create and show the main window
    window = NodeEditorWindow()
    window.show()

    # Run the application's event loop
    sys.exit(app.exec())

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

    # --- Load Font Awesome Regular ---
    font_path_regular = os.path.join(os.path.dirname(__file__), "resources", "Font Awesome 7 Free-Regular-400.otf")
    if os.path.exists(font_path_regular):
        font_id = QFontDatabase.addApplicationFont(font_path_regular)
        if font_id == -1:
            print("Warning: Failed to load Font Awesome Regular font.", file=sys.stderr)
        else:
            families = QFontDatabase.applicationFontFamilies(font_id)
    else:
        print("Warning: Font Awesome Regular font file not found at 'resources/Font Awesome 7 Free-Regular-400.otf'", file=sys.stderr)

    # --- Load Font Awesome Solid ---
    font_path_solid = os.path.join(os.path.dirname(__file__), "resources", "Font Awesome 6 Free-Solid-900.otf")
    if os.path.exists(font_path_solid):
        font_id = QFontDatabase.addApplicationFont(font_path_solid)
        if font_id == -1:
            print("Warning: Failed to load Font Awesome Solid font.", file=sys.stderr)
        else:
            families = QFontDatabase.applicationFontFamilies(font_id)
    else:
        print("Warning: Font Awesome Solid font file not found at 'resources/Font Awesome 6 Free-Solid-900.otf'", file=sys.stderr)

    # Load the dark theme stylesheet with proper path resolution
    def load_stylesheet(app):
        """Load dark theme stylesheet with proper path resolution."""
        qss_paths = [
            "dark_theme.qss",  # For compiled version
            "../dark_theme.qss",  # For development (run from src/)
            os.path.join(os.path.dirname(__file__), "..", "dark_theme.qss"),  # Absolute fallback
        ]

        for qss_path in qss_paths:
            if os.path.exists(qss_path):
                try:
                    with open(qss_path, "r") as f:
                        app.setStyleSheet(f.read())
                    return True
                except Exception as e:
                    print(f"Failed to load {qss_path}: {e}", file=sys.stderr)

        print("Warning: 'dark_theme.qss' not found in any expected location. Using default style.", file=sys.stderr)
        return False

    load_stylesheet(app)

    # Create and show the main window
    window = NodeEditorWindow()
    window.show()

    # Run the application's event loop
    sys.exit(app.exec())

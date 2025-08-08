# main.py
# Entry point for the Node Editor application.
# Now loads a QSS stylesheet for a consistent dark theme.

import sys
import os
from PySide6.QtWidgets import QApplication
from node_editor_window import NodeEditorWindow

def load_stylesheet(app, filename="dark_theme.qss"):
    """Loads an external QSS file and applies it to the application."""
    try:
        with open(filename, "r") as f:
            style = f.read()
            app.setStyleSheet(style)
            print(f"Stylesheet '{filename}' loaded successfully.")
    except FileNotFoundError:
        print(f"Warning: Stylesheet '{filename}' not found. Using default style.")

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Load the dark theme stylesheet
    load_stylesheet(app)

    # Create and show the main window
    window = NodeEditorWindow()
    window.show()

    # Run the application's event loop
    sys.exit(app.exec())

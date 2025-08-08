# main.py
# Entry point for the Node Editor application.
# This script initializes the QApplication and the main window.

import sys
from PySide6.QtWidgets import QApplication
from node_editor_window import NodeEditorWindow

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the main window
    window = NodeEditorWindow()
    window.show()

    # Run the application's event loop
    sys.exit(app.exec())

# node_gui_handler.py
# Handles all GUI-related aspects of a Node, including the custom
# embedded widgets and the code editor dialog.

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QGraphicsProxyWidget
from PySide6.QtCore import Qt, Signal
from code_editor_dialog import CodeEditorDialog

class ResizableWidgetContainer(QWidget):
    """A custom QWidget that emits a signal whenever its size changes."""
    resized = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

class NodeGuiHandler:
    """A mixin class for Node that handles all its GUI components."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _create_content_widget(self):
        """Creates the main content area with the custom GUI and a single control button."""
        self.content_container = ResizableWidgetContainer()
        self.content_container.setAttribute(Qt.WA_TranslucentBackground)
        self.content_container.resized.connect(self._update_layout)

        main_layout = QVBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        self.custom_widget_host = QWidget()
        self.custom_widget_layout = QVBoxLayout(self.custom_widget_host)
        self.custom_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.custom_widget_host)
        
        self.proxy_widget = QGraphicsProxyWidget()
        self.edit_button = QPushButton("</>")
        self.edit_button.setFixedSize(30, 22)
        self.edit_button_proxy = QGraphicsProxyWidget()

        self.proxy_widget.setWidget(self.content_container)
        self.edit_button_proxy.setWidget(self.edit_button)
        self.edit_button.clicked.connect(self.open_unified_editor)

        self.rebuild_gui()

    def rebuild_gui(self):
        """Executes the gui_code to build the custom widget."""
        for i in reversed(range(self.custom_widget_layout.count())): 
            widget = self.custom_widget_layout.itemAt(i).widget()
            if widget: widget.setParent(None)
        self.gui_widgets.clear()
        
        if self.gui_code:
            try:
                from PySide6 import QtWidgets
                scope = {'parent': self.custom_widget_host, 'layout': self.custom_widget_layout, 'widgets': self.gui_widgets, 'QtWidgets': QtWidgets}
                exec(self.gui_code, scope)
            except Exception as e:
                from PySide6.QtWidgets import QLabel
                error_label = QLabel(f"GUI Error:\n{e}")
                error_label.setStyleSheet("color: red;")
                self.custom_widget_layout.addWidget(error_label)
        
        # After building the GUI, force the node to resize to fit the new content.
        self.fit_size_to_content()

    def open_unified_editor(self):
        """Opens the unified, tabbed dialog to edit all of the node's code."""
        parent_widget = self.scene().views()[0] if self.scene().views() else None
        dialog = CodeEditorDialog(self.code, self.gui_code, self.gui_get_values_code, parent_widget)
        if dialog.exec():
            results = dialog.get_results()
            self.set_code(results['code'])
            self.set_gui_code(results['gui_code'])
            self.set_gui_get_values_code(results['gui_logic_code'])

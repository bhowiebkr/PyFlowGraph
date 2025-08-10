# node.py
# Represents a single processing unit (node) in the graph.
# Now with corrected dynamic resizing and universal widget support in custom GUIs.

import uuid
import ast
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QLinearGradient, QPainterPath
from pin import Pin
from socket_type import SocketType
from code_editor_dialog import CodeEditorDialog


class Node(QGraphicsItem):
    """
    A draggable block with a tabbed code editor and a dynamically resizing GUI
    that supports both getting values before execution and setting values after.
    The state of the GUI is now persistent through save/load.
    """

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.uuid = str(uuid.uuid4())
        self.title = title
        self.width = 250
        self.height = 100
        self.pins, self.input_pins, self.output_pins = [], [], []

        self.code = ""
        self.gui_code = ""
        self.gui_get_values_code = ""
        self.function_name = None
        self.gui_widgets = {}

        # --- Visual Properties ---
        self.color_body = QColor(20, 20, 20, 220)
        self.color_title_bar_start = QColor("#383838")
        self.color_title_bar_end = QColor("#2A2A2A")
        self.color_title_text = QColor("#E0E0E0")
        self.color_border = QColor(40, 40, 40)
        self.color_selection_glow = QColor(0, 174, 239, 150)
        self.pen_default = QPen(self.color_border, 1.5)
        self.pen_selected = QPen(self.color_selection_glow, 3)

        self._title_item = QGraphicsTextItem(self.title, self)
        self._title_item.setDefaultTextColor(self.color_title_text)
        self._title_item.setFont(QFont("Arial", 11, QFont.Bold))
        self._title_item.setPos(10, 5)

        self.proxy_widget = None
        self._create_content_widget()
        self._update_layout()

    def _create_content_widget(self):
        """Creates the main content area with the custom GUI and a single control button."""
        self.content_container = QWidget()
        self.content_container.setAttribute(Qt.WA_TranslucentBackground)
        main_layout = QVBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        self.custom_widget_host = QWidget()
        self.custom_widget_layout = QVBoxLayout(self.custom_widget_host)
        self.custom_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.custom_widget_host)

        self.edit_button = QPushButton("Edit Code")
        self.edit_button.clicked.connect(self.open_unified_editor)
        main_layout.addWidget(self.edit_button)

        self.proxy_widget = QGraphicsProxyWidget(self)
        self.proxy_widget.setWidget(self.content_container)

        self.rebuild_gui()

    def rebuild_gui(self):
        """Executes the gui_code to build the custom widget."""
        for i in reversed(range(self.custom_widget_layout.count())):
            widget = self.custom_widget_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.gui_widgets.clear()
        if not self.gui_code:
            self._update_layout()
            return
        try:
            # Provide the entire QtWidgets module to the script's scope.
            # This allows the user to import and use any widget.
            from PySide6 import QtWidgets

            scope = {"parent": self.custom_widget_host, "layout": self.custom_widget_layout, "widgets": self.gui_widgets, "QtWidgets": QtWidgets}
            exec(self.gui_code, scope)
        except Exception as e:
            print(f"Error executing GUI code for node '{self.title}':\n{e}")
            from PySide6.QtWidgets import QLabel

            error_label = QLabel(f"GUI Error:\n{e}")
            error_label.setStyleSheet("color: red;")
            self.custom_widget_layout.addWidget(error_label)
        self._update_layout()

    def get_gui_values(self):
        """Executes the user-defined GUI value extraction code."""
        if not self.gui_get_values_code or not self.gui_widgets:
            return {}
        try:
            scope = {"widgets": self.gui_widgets}
            exec(self.gui_get_values_code, scope)
            value_getter = scope.get("get_values")
            if callable(value_getter):
                return value_getter(self.gui_widgets)
            return {}
        except Exception as e:
            print(f"Error executing GUI get_values code for node '{self.title}':\n{e}")
            return {}

    def set_gui_values(self, outputs):
        """Executes the user-defined GUI value setting code after execution."""
        if not self.gui_get_values_code or not self.gui_widgets:
            return
        try:
            scope = {"widgets": self.gui_widgets}
            exec(self.gui_get_values_code, scope)
            value_setter = scope.get("set_values")
            if callable(value_setter):
                value_setter(self.gui_widgets, outputs)
        except Exception as e:
            print(f"Error executing GUI set_values code for node '{self.title}':\n{e}")

    def apply_gui_state(self, state):
        """Executes the user-defined GUI state setting code on load."""
        if not self.gui_get_values_code or not self.gui_widgets or not state:
            return
        try:
            scope = {"widgets": self.gui_widgets}
            exec(self.gui_get_values_code, scope)
            state_setter = scope.get("set_initial_state")
            if callable(state_setter):
                state_setter(self.gui_widgets, state)
        except Exception as e:
            print(f"Error executing GUI set_initial_state code for node '{self.title}':\n{e}")

    def open_unified_editor(self):
        """Opens the unified, tabbed dialog to edit all of the node's code."""
        parent_widget = self.scene().views()[0] if self.scene().views() else None
        dialog = CodeEditorDialog(self.code, self.gui_code, self.gui_get_values_code, parent_widget)
        if dialog.exec():
            results = dialog.get_results()
            self.set_code(results["code"])
            self.set_gui_code(results["gui_code"])
            self.set_gui_get_values_code(results["gui_logic_code"])

    def set_code(self, code_text):
        self.code = code_text
        self.update_pins_from_code()

    def set_gui_code(self, code_text):
        self.gui_code = code_text
        self.rebuild_gui()

    def set_gui_get_values_code(self, code_text):
        self.gui_get_values_code = code_text

    def serialize(self):
        """Serializes the node's state, including its current GUI values."""
        return {
            "uuid": self.uuid,
            "title": self.title,
            "pos": (self.pos().x(), self.pos().y()),
            "code": self.code,
            "gui_code": self.gui_code,
            "gui_get_values_code": self.gui_get_values_code,
            "gui_state": self.get_gui_values(),
        }

    def _update_layout(self):
        """Dynamically recalculates the node's height to fit its content."""
        self.prepareGeometryChange()
        title_height, button_height, pin_spacing, pin_margin_top = 32, 40, 25, 15
        num_pins = max(len(self.input_pins), len(self.output_pins))
        pin_area_height = (num_pins * pin_spacing) if num_pins > 0 else 0

        # DYNAMIC RESIZING FIX: Get the optimal size of the entire content container.
        content_height = self.content_container.sizeHint().height()

        self.height = title_height + pin_area_height + pin_margin_top + content_height

        pin_start_y = title_height + pin_margin_top + (pin_spacing / 2)
        for i, pin in enumerate(self.input_pins):
            pin.setPos(0, pin_start_y + i * pin_spacing)
            pin.update_label_pos()
        for i, pin in enumerate(self.output_pins):
            pin.setPos(self.width, pin_start_y + i * pin_spacing)
            pin.update_label_pos()

        content_y = title_height + pin_area_height + pin_margin_top
        if self.proxy_widget:
            self.proxy_widget.setPos(0, content_y)
            self.proxy_widget.setMinimumWidth(self.width)
            self.proxy_widget.setMaximumWidth(self.width)

    # --- Other methods remain the same ---
    def get_pin_by_name(self, name):
        for pin in self.pins:
            if pin.name == name:
                return pin
        return None

    def _parse_type_hint(self, hint_node):
        if hint_node is None:
            return "any"
        if isinstance(hint_node, ast.Name):
            return hint_node.id
        if isinstance(hint_node, ast.Subscript):
            return f"{self._parse_type_hint(hint_node.value)}[{self._parse_type_hint(hint_node.slice)}]"
        return "any"

    def update_pins_from_code(self):
        new_inputs, new_outputs = {}, {}
        self.function_name, main_func_def = None, None
        try:
            tree = ast.parse(self.code)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == "node_entry":
                            main_func_def = node
                            break
                    if main_func_def:
                        break
            if not main_func_def:
                for pin in list(self.pins):
                    self.remove_pin(pin)
                self._update_layout()
                return
            self.function_name = main_func_def.name
            for arg in main_func_def.args.args:
                new_inputs[arg.arg] = self._parse_type_hint(arg.annotation).lower()
            if main_func_def.returns:
                return_annotation = main_func_def.returns
                if isinstance(return_annotation, ast.Subscript) and isinstance(return_annotation.value, ast.Name) and return_annotation.value.id.lower() in ("tuple", "list"):
                    output_types = [self._parse_type_hint(elt).lower() for elt in return_annotation.slice.elts]
                    for i, type_name in enumerate(output_types):
                        new_outputs[f"output_{i+1}"] = type_name
                else:
                    new_outputs["output_1"] = self._parse_type_hint(return_annotation).lower()
        except (SyntaxError, AttributeError):
            return

        current_inputs = {pin.name: pin for pin in self.input_pins}
        current_outputs = {pin.name: pin for pin in self.output_pins}
        for name, pin in list(current_inputs.items()):
            if name not in new_inputs:
                self.remove_pin(pin)
        for name, type_name in new_inputs.items():
            if name not in current_inputs:
                self.add_pin(name, "input", type_name)
        for name, pin in list(current_outputs.items()):
            if name not in new_outputs:
                self.remove_pin(pin)
        for name, type_name in new_outputs.items():
            if name not in current_outputs:
                self.add_pin(name, "output", type_name)
        self._update_layout()

    def add_pin(self, name, direction, pin_type_str):
        type_map = {"STR": "STRING", "BOOL": "BOOLEAN"}
        processed_type_str = pin_type_str.upper().split("[")[0]
        final_type_str = type_map.get(processed_type_str, processed_type_str)
        pin_type = SocketType[final_type_str] if final_type_str in SocketType.__members__ else SocketType.ANY
        pin = Pin(self, name, direction, pin_type)
        self.pins.append(pin)
        if direction == "input":
            self.input_pins.append(pin)
        else:
            self.output_pins.append(pin)
        return pin

    def remove_pin(self, pin_to_remove):
        if pin_to_remove.connections:
            for conn in list(pin_to_remove.connections):
                self.scene().remove_connection(conn)
        pin_to_remove.destroy()
        if pin_to_remove in self.pins:
            self.pins.remove(pin_to_remove)
        if pin_to_remove in self.input_pins:
            self.input_pins.remove(pin_to_remove)
        if pin_to_remove in self.output_pins:
            self.output_pins.remove(pin_to_remove)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).adjusted(-5, -5, 5, 5)

    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 8, 8)
        return path

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        if self.isSelected():
            painter.setPen(self.pen_selected)
            painter.setBrush(self.color_selection_glow)
            painter.drawRoundedRect(QRectF(0, 0, self.width, self.height).adjusted(-2, -2, 2, 2), 10, 10)
        body_path = QPainterPath()
        body_path.addRoundedRect(0, 0, self.width, self.height, 8, 8)
        painter.setPen(self.pen_default)
        painter.setBrush(self.color_body)
        painter.drawPath(body_path)
        title_rect = QRectF(0, 0, self.width, 32)
        title_gradient = QLinearGradient(title_rect.topLeft(), title_rect.bottomLeft())
        title_gradient.setColorAt(0, self.color_title_bar_start)
        title_gradient.setColorAt(1, self.color_title_bar_end)
        painter.save()
        painter.setClipPath(body_path)
        painter.fillRect(title_rect, title_gradient)
        painter.setClipping(False)
        painter.setPen(QPen(self.color_border, 0.8))
        painter.drawLine(0, 32, self.width, 32)
        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for pin in self.pins:
                pin.update_connections()
        return super().itemChange(change, value)

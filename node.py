# node.py
# Represents a single processing unit (node) in the graph.
# Now with non-destructive pin reconciliation to preserve connections.

import uuid
import ast
from PySide6.QtWidgets import (QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget, 
                               QPushButton, QVBoxLayout, QWidget)
from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QLinearGradient, 
                           QPainterPath)
from pin import Pin
from socket_type import SocketType
from code_editor_dialog import CodeEditorDialog

class Node(QGraphicsItem):
    """
    A draggable block whose inputs and outputs are defined by the signature
    of a 'node_function' in its code.
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
        self.pins = []
        self.input_pins = []
        self.output_pins = []
        self.code = ""
        self.function_name = None

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

    def get_pin_by_name(self, name):
        for pin in self.pins:
            if pin.name == name: return pin
        return None

    def _create_content_widget(self):
        widget = QWidget()
        widget.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        self.edit_button = QPushButton("Edit Code")
        self.edit_button.clicked.connect(self.open_code_editor)
        layout.addWidget(self.edit_button)
        self.proxy_widget = QGraphicsProxyWidget(self)
        self.proxy_widget.setWidget(widget)

    def open_code_editor(self):
        dialog = CodeEditorDialog(self.code, self.scene().views()[0])
        if dialog.exec():
            self.set_code(dialog.get_code())

    def _parse_type_hint(self, hint_node):
        if hint_node is None: return "any"
        if isinstance(hint_node, ast.Name): return hint_node.id
        if isinstance(hint_node, ast.Subscript):
            base_type = self._parse_type_hint(hint_node.value)
            slice_type = self._parse_type_hint(hint_node.slice)
            return f"{base_type}[{slice_type}]"
        return "any"

    def update_pins_from_code(self):
        """
        BUG FIX: This method now reconciles pins instead of destroying and
        recreating them. This preserves existing connections.
        """
        new_inputs = {}
        new_outputs = {}
        self.function_name = None

        try:
            tree = ast.parse(self.code)
            func_def = next((node for node in tree.body if isinstance(node, ast.FunctionDef)), None)
            
            if not func_def:
                # If no function is defined, remove all pins
                for pin in list(self.pins): self.remove_pin(pin)
                self._update_layout()
                return

            self.function_name = func_def.name
            
            # Get new inputs from function parameters
            for arg in func_def.args.args:
                new_inputs[arg.arg] = self._parse_type_hint(arg.annotation).lower()

            # Get new outputs from function return annotation
            if func_def.returns:
                return_annotation = func_def.returns
                if (isinstance(return_annotation, ast.Subscript) and
                    isinstance(return_annotation.value, ast.Name) and
                    return_annotation.value.id.lower() in ('tuple', 'list')):
                    
                    output_types = [self._parse_type_hint(elt).lower() for elt in return_annotation.slice.elts]
                    for i, type_name in enumerate(output_types):
                        new_outputs[f"output_{i+1}"] = type_name
                else:
                    type_name = self._parse_type_hint(return_annotation).lower()
                    new_outputs["output_1"] = type_name

        except (SyntaxError, AttributeError) as e:
            # Don't change pins if code is invalid to avoid breaking the graph while typing
            return
        
        # --- Reconcile Pins ---
        current_inputs = {pin.name: pin for pin in self.input_pins}
        current_outputs = {pin.name: pin for pin in self.output_pins}

        # Remove input pins that are no longer in the code
        for name, pin in list(current_inputs.items()):
            if name not in new_inputs:
                self.remove_pin(pin)

        # Add new input pins
        for name, type_name in new_inputs.items():
            if name not in current_inputs:
                self.add_pin(name, "input", type_name)
        
        # Remove output pins that are no longer in the code
        for name, pin in list(current_outputs.items()):
            if name not in new_outputs:
                self.remove_pin(pin)

        # Add new output pins
        for name, type_name in new_outputs.items():
            if name not in current_outputs:
                self.add_pin(name, "output", type_name)

        self._update_layout()

    def add_pin(self, name, direction, pin_type_str):
        pin_type_str = pin_type_str.upper().split('[')[0]
        pin_type = SocketType[pin_type_str] if pin_type_str in SocketType.__members__ else SocketType.ANY
        pin = Pin(self, name, direction, pin_type)
        self.pins.append(pin)
        if direction == "input": self.input_pins.append(pin)
        else: self.output_pins.append(pin)
        return pin
    
    def remove_pin(self, pin_to_remove):
        if pin_to_remove.connections:
            for conn in list(pin_to_remove.connections): self.scene().remove_connection(conn)
        pin_to_remove.destroy()
        if pin_to_remove in self.pins: self.pins.remove(pin_to_remove)
        if pin_to_remove in self.input_pins: self.input_pins.remove(pin_to_remove)
        if pin_to_remove in self.output_pins: self.output_pins.remove(pin_to_remove)

    def _update_layout(self):
        title_height, button_height, pin_spacing, pin_margin_top = 32, 50, 25, 15
        num_pins = max(len(self.input_pins), len(self.output_pins))
        pin_area_height = (num_pins * pin_spacing) if num_pins > 0 else 0
        self.height = title_height + pin_area_height + pin_margin_top + button_height
        pin_start_y = title_height + pin_margin_top + (pin_spacing / 2)
        for i, pin in enumerate(self.input_pins):
            pin.setPos(0, pin_start_y + i * pin_spacing)
            pin.update_label_pos()
        for i, pin in enumerate(self.output_pins):
            pin.setPos(self.width, pin_start_y + i * pin_spacing)
            pin.update_label_pos()
        button_y = title_height + pin_area_height + pin_margin_top
        if self.proxy_widget:
            self.proxy_widget.setPos(0, button_y)
            self.proxy_widget.setMinimumWidth(self.width)
            self.proxy_widget.setMaximumWidth(self.width)
        self.prepareGeometryChange()

    def set_code(self, code_text):
        self.code = code_text
        self.update_pins_from_code()

    def serialize(self):
        return {"uuid": self.uuid, "title": self.title, "pos": (self.pos().x(), self.pos().y()), "code": self.code}

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
            for pin in self.pins: pin.update_connections()
        return super().itemChange(change, value)

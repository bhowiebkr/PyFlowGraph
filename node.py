# node.py
# Represents a single processing unit (node) in the graph.
# Now with a modal code editor and corrected layout.

import uuid
import ast
from PySide6.QtWidgets import (QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget, 
                               QPushButton, QVBoxLayout, QWidget)
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from pin import Pin
from socket_type import SocketType
from code_editor_dialog import CodeEditorDialog

class Node(QGraphicsItem):
    """
    A draggable block with a modal code editor and dynamically generated pins.
    Layout is now: Title -> Pins -> 'Edit Code' Button.
    """
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.uuid = str(uuid.uuid4())
        self.title = title
        self.width = 250
        self.height = 100 # Initial height, will be recalculated
        self.pins = []
        self.input_pins = []
        self.output_pins = []
        self.code = ""

        # --- Visual Properties ---
        self.color_background = QColor("#FF3A3A3A")
        self.color_title_background = QColor("#FF282828")
        self.color_title_text = QColor("#FFEEEEEE")
        self.color_border = QColor("#FF111111")
        
        self.pen_default = QPen(self.color_border)
        self.pen_selected = QPen(QColor("#FFFFA500"))
        self.pen_selected.setWidth(2)
        
        self._title_item = QGraphicsTextItem(self.title, self)
        self._title_item.setDefaultTextColor(self.color_title_text)
        self._title_item.setFont(QFont("Arial", 12, QFont.Bold))
        self._title_item.setPos(10, 5)

        # --- Content Widget ('Edit Code' Button) ---
        self.proxy_widget = None
        self._create_content_widget()

        self._update_layout()

    def _create_content_widget(self):
        """Create the QWidget that hosts the 'Edit Code' button."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.edit_button = QPushButton("Edit Code")
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #505050;
                color: #F0F0F0;
                border: 1px solid #606060;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """)
        self.edit_button.clicked.connect(self.open_code_editor)
        layout.addWidget(self.edit_button)
        
        self.proxy_widget = QGraphicsProxyWidget(self)
        self.proxy_widget.setWidget(widget)

    def open_code_editor(self):
        """Opens the modal dialog to edit the node's code."""
        dialog = CodeEditorDialog(self.code, self.scene().views()[0])
        if dialog.exec():
            new_code = dialog.get_code()
            self.set_code(new_code)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).normalized()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for pin in self.pins:
                pin.update_connections()
        return super().itemChange(change, value)

    def _parse_type_hint(self, hint_node):
        if isinstance(hint_node, ast.Name): return hint_node.id
        if isinstance(hint_node, ast.Subscript): return f"{self._parse_type_hint(hint_node.value)}[{self._parse_type_hint(hint_node.slice)}]"
        return "any"

    def update_pins_from_code(self):
        """Parse the code and create/update pins accordingly."""
        new_inputs, new_outputs = {}, {}
        try:
            tree = ast.parse(self.code)
            for node in ast.walk(tree):
                if isinstance(node, ast.AnnAssign):
                    target_name, type_name = node.target.id, self._parse_type_hint(node.annotation).lower()
                    if target_name.startswith("input_"): new_inputs[target_name] = type_name
                    elif target_name.startswith("output_"): new_outputs[target_name] = type_name
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.startswith("output_") and target.id not in new_outputs:
                            new_outputs[target.id] = 'any'
        except (SyntaxError, AttributeError): return
        
        current_inputs = {pin.name: pin for pin in self.input_pins}
        current_outputs = {pin.name: pin for pin in self.output_pins}

        for name, pin in list(current_inputs.items()):
            if name not in new_inputs: self.remove_pin(pin)
        for name, type_name in new_inputs.items():
            if name not in current_inputs: self.add_pin(name, "input", type_name)

        for name, pin in list(current_outputs.items()):
            if name not in new_outputs: self.remove_pin(pin)
        for name, type_name in new_outputs.items():
            if name not in current_outputs: self.add_pin(name, "output", type_name)

        self._update_layout()

    def add_pin(self, name, direction, pin_type_str):
        pin_type_str = pin_type_str.upper()
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
        """Recalculate node height and the positions of all child items."""
        title_height = 30
        button_height = 50
        pin_spacing = 25
        pin_margin_top = 15
        
        # --- Calculate required height ---
        num_pins = max(len(self.input_pins), len(self.output_pins))
        pin_area_height = (num_pins * pin_spacing) if num_pins > 0 else 0
        self.height = title_height + pin_area_height + pin_margin_top + button_height

        # --- Position Pins and Labels ---
        pin_start_y = title_height + pin_margin_top + (pin_spacing / 2)

        for i, pin in enumerate(self.input_pins):
            y_pos = pin_start_y + i * pin_spacing
            pin.setPos(0, y_pos)
            pin.update_label_pos()

        for i, pin in enumerate(self.output_pins):
            y_pos = pin_start_y + i * pin_spacing
            pin.setPos(self.width, y_pos)
            pin.update_label_pos()
        
        # --- Position 'Edit Code' Button ---
        button_y = title_height + pin_area_height + pin_margin_top
        if self.proxy_widget:
            self.proxy_widget.setPos(0, button_y)
            self.proxy_widget.setMinimumWidth(self.width)
            self.proxy_widget.setMaximumWidth(self.width)

        self.prepareGeometryChange()

    def paint(self, painter: QPainter, option, widget=None):
        path_body = QRectF(0, 0, self.width, self.height)
        painter.setBrush(self.color_background)
        painter.setPen(self.pen_selected if self.isSelected() else self.pen_default)
        painter.drawRoundedRect(path_body, 10, 10)

        path_title = QRectF(0, 0, self.width, 30)
        painter.setBrush(self.color_title_background)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(path_title, 10, 10)
        painter.drawRect(0, 10, self.width, 20)

    def set_code(self, code_text):
        self.code = code_text
        self.update_pins_from_code()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.scene().remove_node(self)
        else:
            super().keyPressEvent(event)

    def serialize(self):
        return {"uuid": self.uuid, "title": self.title, "pos": (self.pos().x(), self.pos().y()), "code": self.code}

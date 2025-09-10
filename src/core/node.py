# node.py
# A single, stable, monolithic Node class that contains all functionality
# for visuals, logic, and interaction.

import uuid
import ast
import sys
import os
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget, QPushButton, QVBoxLayout, QWidget, QStyle, QApplication
from PySide6.QtCore import QRectF, Qt, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QPainterPath, QMouseEvent

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .pin import Pin

# Debug configuration  
# Set to True to enable detailed GUI widget update debugging
DEBUG_GUI_UPDATES = False


class ResizableWidgetContainer(QWidget):
    """A custom QWidget that emits a signal whenever its size changes."""

    resized = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()


class Node(QGraphicsItem):
    """
    A full-featured, draggable, and resizable block that contains all its
    functionality in a single class.
    """

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # --- Core Attributes ---
        self.uuid = str(uuid.uuid4())
        self.title = title
        self.description = ""
        self.base_width = 250
        self.width = self.base_width
        self.height = 150
        self.pins, self.input_pins, self.output_pins = [], [], []
        self.execution_pins, self.data_pins = [], []

        # --- Code Storage ---
        self.code, self.gui_code, self.gui_get_values_code = "", "", ""
        self.function_name = None
        self.gui_widgets = {}

        # --- Interaction State ---
        self._is_resizing = False
        self._resize_handle_size = 15

        # --- Visual Properties ---
        self.color_body = QColor(20, 20, 20, 220)
        self.color_title_bar = QColor("#2A2A2A")
        self.color_title_text = QColor("#E0E0E0")
        self.color_border = QColor(40, 40, 40)
        self.color_selection_glow = QColor(0, 174, 239, 150)
        self.pen_default = QPen(self.color_border, 1.5)

        # --- Child Items ---
        self._title_item = QGraphicsTextItem(self.title, self)
        self._title_item.setDefaultTextColor(self.color_title_text)
        self._title_item.setFont(QFont("Arial", 11, QFont.Bold))
        self._title_item.setPos(10, 5)

        self.proxy_widget = None
        self._create_content_widget()

    # --- Interaction & Event Handling ---

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self.highlight_connections(value)
        if change == QGraphicsItem.ItemPositionHasChanged:
            for pin in self.pins:
                pin.update_connections()
            
            # Notify the scene that this node has moved so it can update group memberships
            if self.scene() and hasattr(self.scene(), 'handle_node_position_changed'):
                self.scene().handle_node_position_changed(self)
                
        return super().itemChange(change, value)

    def highlight_connections(self, selected):
        for pin in self.pins:
            for conn in pin.connections:
                conn.setSelected(selected)

    def show_properties_dialog(self):
        from ui.dialogs.node_properties_dialog import NodePropertiesDialog
        parent_widget = self.scene().views()[0] if self.scene().views() else None
        dialog = NodePropertiesDialog(self.title, self.description, self.color_title_bar, self.color_body, parent_widget)
        if dialog.exec():
            props = dialog.get_properties()
            self.title = props["title"]
            self.description = props["description"]
            self._title_item.setPlainText(self.title)
            self.color_title_bar = QColor(props["title_color"])
            self.color_body = QColor(props["body_color"])
            self.update()

    def get_resize_handle_rect(self):
        return QRectF(self.width - self._resize_handle_size, self.height - self._resize_handle_size, self._resize_handle_size, self._resize_handle_size)

    def hoverMoveEvent(self, event):
        if self.get_resize_handle_rect().contains(event.pos()):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if self.get_resize_handle_rect().contains(event.pos()):
            self._is_resizing = True
        else:
            self._is_resizing = False
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_resizing:
            self.prepareGeometryChange()
            min_height = self._calculate_minimum_height()

            self.width = max(self.base_width, event.pos().x())
            self.height = max(min_height, event.pos().y())

            self._update_layout()
            for pin in self.pins:
                pin.update_connections()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_resizing:
            self._is_resizing = False
            # Do not snap to content size; respect the user's manual resize.
            self._update_layout()
            self.update()
        else:
            super().mouseReleaseEvent(event)

    # --- GUI & Layout ---

    def _create_content_widget(self):
        # --- Definitive Fix for Initialization Order ---
        # 1. Create all objects first.
        self.content_container = ResizableWidgetContainer()
        # Set background to match node body color instead of transparent
        self.content_container.setAttribute(Qt.WA_TranslucentBackground)

        main_layout = QVBoxLayout(self.content_container)
        main_layout.setContentsMargins(5, 5, 5, 15)
        main_layout.setSpacing(5)

        self.custom_widget_host = QWidget()
        self.custom_widget_host.setAttribute(Qt.WA_TranslucentBackground)
        self.custom_widget_host._node = self  # Add node reference for GUI callbacks
        self.custom_widget_layout = QVBoxLayout(self.custom_widget_host)
        self.custom_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.custom_widget_host)

        self.proxy_widget = QGraphicsProxyWidget(self)

        self.edit_button = QPushButton("</>")
        self.edit_button.setFixedSize(30, 22)
        self.edit_button_proxy = QGraphicsProxyWidget(self)

        # 2. Now that all objects exist, set widgets and connect signals.
        self.proxy_widget.setWidget(self.content_container)
        self.edit_button_proxy.setWidget(self.edit_button)
        self.edit_button.clicked.connect(self.open_unified_editor)
        self.content_container.resized.connect(self._update_layout)

        # 3. Finally, build the initial GUI, which will trigger the first layout update.
        self.rebuild_gui()

    def rebuild_gui(self):
        for i in reversed(range(self.custom_widget_layout.count())):
            widget = self.custom_widget_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.gui_widgets.clear()
        if self.gui_code:
            try:
                from PySide6 import QtWidgets

                scope = {"parent": self.custom_widget_host, "layout": self.custom_widget_layout, "widgets": self.gui_widgets, "node": self, "QtWidgets": QtWidgets}
                exec(self.gui_code, scope)
            except Exception as e:
                from PySide6.QtWidgets import QLabel

                error_label = QLabel(f"GUI Error:\n{e}")
                error_label.setStyleSheet("color: red;")
                self.custom_widget_layout.addWidget(error_label)
        self.fit_size_to_content()

    def _calculate_minimum_height(self):
        title_height, pin_spacing, pin_margin_top = 32, 25, 15
        num_pins = max(len(self.input_pins), len(self.output_pins))
        pin_area_height = (num_pins * pin_spacing) if num_pins > 0 else 0

        self.content_container.layout().activate()
        content_height = self.content_container.sizeHint().height()

        return title_height + pin_area_height + pin_margin_top + content_height + 1

    def calculate_absolute_minimum_size(self):
        """Calculate the absolute minimum size needed for this node's content.
        
        Returns:
            tuple[int, int]: (min_width, min_height) required for proper layout
        """
        from utils.debug_config import should_debug, DEBUG_LAYOUT
        
        if should_debug(DEBUG_LAYOUT):
            print(f"DEBUG: calculate_absolute_minimum_size() called for node '{self.title}'")
        
        # Base measurements (matching existing constants)
        title_height = 32
        pin_spacing = 25
        pin_margin_top = 15
        node_padding = 10
        resize_handle_size = 15
        
        # Calculate minimum width
        title_width = 0
        if hasattr(self, '_title_item') and self._title_item:
            title_width = self._title_item.boundingRect().width() + 20  # Title + padding
        
        # Pin label widths (find longest on each side)
        max_input_label_width = 0
        if self.input_pins:
            max_input_label_width = max([pin.label.boundingRect().width() 
                                        for pin in self.input_pins])
        
        max_output_label_width = 0
        if self.output_pins:
            max_output_label_width = max([pin.label.boundingRect().width() 
                                         for pin in self.output_pins])
        
        # Total pin label width with spacing for pin circles
        pin_label_width = max_input_label_width + max_output_label_width + 40  # Labels + pin spacing
        
        # GUI content minimum width
        gui_min_width = 0
        if hasattr(self, 'content_container') and self.content_container:
            self.content_container.layout().activate()
            gui_min_width = self.content_container.minimumSizeHint().width()
        
        min_width = max(
            self.base_width,  # Default base width
            title_width,
            pin_label_width,
            gui_min_width + node_padding
        )
        
        # Calculate minimum height
        max_pins = max(len(self.input_pins), len(self.output_pins))
        pin_area_height = (max_pins * pin_spacing) if max_pins > 0 else 0
        
        # GUI content minimum height
        gui_min_height = 0
        if hasattr(self, 'content_container') and self.content_container:
            gui_min_height = self.content_container.minimumSizeHint().height()
        
        min_height = (title_height + 
                      pin_margin_top + 
                      pin_area_height + 
                      gui_min_height + 
                      resize_handle_size +
                      node_padding)
        
        if should_debug(DEBUG_LAYOUT):
            print(f"DEBUG: Minimum size calculated as {min_width}x{min_height}")
            print(f"DEBUG: - Title width: {title_width}")
            print(f"DEBUG: - Pin label width: {pin_label_width} (input: {max_input_label_width}, output: {max_output_label_width})")
            print(f"DEBUG: - GUI min width: {gui_min_width}")
            print(f"DEBUG: - Pin area height: {pin_area_height} (pins: {max_pins})")
            print(f"DEBUG: - GUI min height: {gui_min_height}")
        
        return (min_width, min_height)

    def fit_size_to_content(self):
        """Calculates and applies the optimal size for the node."""
        from utils.debug_config import should_debug, DEBUG_LAYOUT
        
        if should_debug(DEBUG_LAYOUT):
            print(f"DEBUG: fit_size_to_content() called for node '{self.title}'")
            print(f"DEBUG: Current size before fit: {self.width}x{self.height}")
        
        # Use comprehensive minimum size calculation
        min_width, min_height = self.calculate_absolute_minimum_size()
        
        # Ensure we don't go below minimum requirements
        required_width = max(self.width, min_width)
        required_height = max(self.height, min_height)

        if self.width != required_width or self.height != required_height:
            if should_debug(DEBUG_LAYOUT):
                print(f"DEBUG: Resizing from {self.width}x{self.height} to {required_width}x{required_height}")
            
            self.width = required_width
            self.height = required_height
            self._update_layout()
        elif should_debug(DEBUG_LAYOUT):
            print(f"DEBUG: No resize needed, size already meets minimum requirements")

    def _update_layout(self):
        from utils.debug_config import should_debug, DEBUG_LAYOUT
        
        if should_debug(DEBUG_LAYOUT):
            print(f"DEBUG: _update_layout() called for node '{self.title}'")
            print(f"DEBUG: Current size: {self.width}x{self.height}")
            print(f"DEBUG: Pin counts - input: {len(self.input_pins)}, output: {len(self.output_pins)}")
        
        self.prepareGeometryChange()

        title_height, pin_spacing, pin_margin_top = 32, 25, 15
        
        # Separate execution and data pins
        input_exec_pins = [p for p in self.input_pins if p.pin_category == "execution"]
        input_data_pins = [p for p in self.input_pins if p.pin_category == "data"]
        output_exec_pins = [p for p in self.output_pins if p.pin_category == "execution"]
        output_data_pins = [p for p in self.output_pins if p.pin_category == "data"]
        
        # Calculate total pin area height
        max_input_pins = len(input_exec_pins) + len(input_data_pins)
        max_output_pins = len(output_exec_pins) + len(output_data_pins)
        num_pins = max(max_input_pins, max_output_pins)
        pin_area_height = (num_pins * pin_spacing) if num_pins > 0 else 0

        pin_start_y = title_height + pin_margin_top + (pin_spacing / 2)
        
        if should_debug(DEBUG_LAYOUT):
            print(f"DEBUG: Pin layout - start_y: {pin_start_y}, area_height: {pin_area_height}")
        
        # Position input pins (execution first, then data)
        current_y = pin_start_y
        for i, pin in enumerate(input_exec_pins):
            pin.setPos(0, current_y)
            pin.update_label_pos()
            if should_debug(DEBUG_LAYOUT):
                print(f"DEBUG: Input exec pin {i} positioned at (0, {current_y})")
            current_y += pin_spacing
        for i, pin in enumerate(input_data_pins):
            pin.setPos(0, current_y)
            pin.update_label_pos()
            if should_debug(DEBUG_LAYOUT):
                print(f"DEBUG: Input data pin {i} positioned at (0, {current_y})")
            current_y += pin_spacing
            
        # Position output pins (execution first, then data)
        current_y = pin_start_y
        for i, pin in enumerate(output_exec_pins):
            pin.setPos(self.width, current_y)
            pin.update_label_pos()
            if should_debug(DEBUG_LAYOUT):
                print(f"DEBUG: Output exec pin {i} positioned at ({self.width}, {current_y})")
            current_y += pin_spacing
        for i, pin in enumerate(output_data_pins):
            pin.setPos(self.width, current_y)
            pin.update_label_pos()
            if should_debug(DEBUG_LAYOUT):
                print(f"DEBUG: Output data pin {i} positioned at ({self.width}, {current_y})")
            current_y += pin_spacing

        content_y = title_height + pin_area_height + pin_margin_top
        content_height = max(0, self.height - content_y)

        if self.proxy_widget:
            self.proxy_widget.setPos(0, content_y)
            # Definitive Fix: Do NOT use setFixedSize. Let the internal layout manage itself.
            # Set min/max to allow it to expand/contract within the available space.
            self.proxy_widget.widget().setMinimumSize(self.width, content_height)
            self.proxy_widget.widget().setMaximumSize(self.width, content_height)
            if should_debug(DEBUG_LAYOUT):
                print(f"DEBUG: Proxy widget positioned at (0, {content_y}) with size {self.width}x{content_height}")

        self.edit_button_proxy.setPos(self.width - 35, 5)
        
        # Enhanced visual update chain
        # Force pin visual updates
        for pin in self.input_pins + self.output_pins:
            pin.update()  # Trigger Qt repaint for each pin
            pin.update_connections()  # Update connections after positioning
        
        # Trigger node visual refresh
        self.update()
        
        if should_debug(DEBUG_LAYOUT):
            print(f"DEBUG: _update_layout() completed for node '{self.title}'")

    # --- Painting ---

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).adjusted(-5, -5, 5, 5)

    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 8, 8)
        return path

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        body_path = QPainterPath()
        body_path.addRoundedRect(0, 0, self.width, self.height, 8, 8)
        painter.setPen(self.pen_default)
        painter.setBrush(self.color_body)
        painter.drawPath(body_path)
        title_rect = QRectF(0, 0, self.width, 32)
        title_gradient = QLinearGradient(title_rect.topLeft(), title_rect.bottomLeft())
        title_gradient.setColorAt(0, self.color_title_bar.lighter(115))
        title_gradient.setColorAt(1, self.color_title_bar)
        painter.save()
        painter.setClipPath(body_path)
        painter.fillRect(title_rect, title_gradient)
        painter.setClipping(False)
        painter.setPen(QPen(self.color_border.darker(120)))
        painter.drawLine(0, 32, self.width, 32)
        painter.restore()
        if self.isSelected():
            highlight_pen = QPen(self.color_title_bar.lighter(130), 2)
            painter.setPen(highlight_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(body_path)
        handle_rect = self.get_resize_handle_rect()
        painter.setPen(QPen(self.color_border.lighter(150), 1.5))
        painter.drawLine(handle_rect.left() + 4, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 4)
        painter.drawLine(handle_rect.left() + 8, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 8)
        painter.drawLine(handle_rect.left() + 12, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 12)

    # --- Logic & Data Handling ---

    def open_unified_editor(self):
        from ui.dialogs.code_editor_dialog import CodeEditorDialog
        parent_widget = self.scene().views()[0] if self.scene().views() else None
        node_graph = self.scene() if self.scene() else None
        dialog = CodeEditorDialog(self, node_graph, self.code, self.gui_code, self.gui_get_values_code, parent_widget)
        dialog.exec()

    def set_code(self, code_text):
        self.code = code_text
        self.update_pins_from_code()

    def set_gui_code(self, code_text):
        self.gui_code = code_text
        self.rebuild_gui()

    def set_gui_get_values_code(self, code_text):
        self.gui_get_values_code = code_text

    def get_gui_values(self):
        if not self.gui_get_values_code or not self.gui_widgets:
            return {}
        try:
            scope = {"widgets": self.gui_widgets, "node": self}
            exec(self.gui_get_values_code, scope)
            value_getter = scope.get("get_values")
            if callable(value_getter):
                return value_getter(self.gui_widgets)
            return {}
        except Exception as e:
            return {}

    def set_gui_values(self, outputs):
        if not self.gui_get_values_code or not self.gui_widgets:
            if DEBUG_GUI_UPDATES:
                print(f"DEBUG: set_gui_values() early return for '{self.title}' - gui_code: {bool(self.gui_get_values_code)}, widgets: {bool(self.gui_widgets)}")
            return
        try:
            if DEBUG_GUI_UPDATES:
                print(f"DEBUG: set_gui_values() called for '{self.title}' with outputs: {outputs}")
                print(f"DEBUG: Available widgets: {list(self.gui_widgets.keys()) if self.gui_widgets else []}")
            scope = {"widgets": self.gui_widgets, "node": self}
            exec(self.gui_get_values_code, scope)
            value_setter = scope.get("set_values")
            if callable(value_setter):
                if DEBUG_GUI_UPDATES:
                    print(f"DEBUG: Calling set_values() function for '{self.title}'")
                value_setter(self.gui_widgets, outputs)
                if DEBUG_GUI_UPDATES:
                    print(f"DEBUG: set_values() completed successfully for '{self.title}'")
            else:
                if DEBUG_GUI_UPDATES:
                    print(f"DEBUG: No callable set_values() function found for '{self.title}'")
        except Exception as e:
            if DEBUG_GUI_UPDATES:
                print(f"DEBUG: set_gui_values() failed for '{self.title}': {e}")
                import traceback
                traceback.print_exc()

    def apply_gui_state(self, state):
        if not self.gui_get_values_code or not self.gui_widgets or not state:
            return
        try:
            scope = {"widgets": self.gui_widgets, "node": self}
            exec(self.gui_get_values_code, scope)
            state_setter = scope.get("set_initial_state")
            if callable(state_setter):
                state_setter(self.gui_widgets, state)
        except Exception as e:
            pass

    def serialize(self):
        return {
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "pos": [self.pos().x(), self.pos().y()],
            "size": [self.width, self.height],
            "code": self.code,
            "gui_code": self.gui_code,
            "gui_get_values_code": self.gui_get_values_code,
            "gui_state": self.get_gui_values(),
            "colors": {"title": self.color_title_bar.name(), "body": self.color_body.name()},
        }

    def get_pin_by_name(self, name):
        for pin in self.pins:
            if pin.name == name:
                return pin
        return None
    
    def get_pin_by_name_and_direction(self, name, direction):
        """Get a pin by name and direction (input/output)"""
        for pin in self.pins:
            if pin.name == name and pin.direction == direction:
                return pin
        return None

    def _parse_type_hint(self, hint_node):
        if hint_node is None:
            return "any"
        if isinstance(hint_node, ast.Name):
            return hint_node.id
        if isinstance(hint_node, ast.Subscript):
            base_type = self._parse_type_hint(hint_node.value)
            # Handle different slice types
            if isinstance(hint_node.slice, ast.Name):
                # Simple generic like List[Dict]
                slice_type = hint_node.slice.id
                return f"{base_type}[{slice_type}]"
            elif isinstance(hint_node.slice, ast.Tuple):
                # Multiple generic parameters like Dict[str, int]
                slice_types = [self._parse_type_hint(elt) for elt in hint_node.slice.elts]
                return f"{base_type}[{', '.join(slice_types)}]"
            elif hasattr(hint_node.slice, 'value'):
                # Handle other slice structures
                return f"{base_type}[{self._parse_type_hint(hint_node.slice)}]"
            else:
                # Fallback for unknown slice types
                return base_type
        return "any"
    
    def _parse_named_output(self, type_str):
        """Parse named output like 'name:type' or just 'type'."""
        if ':' in type_str:
            name, type_part = type_str.split(':', 1)
            return name.strip(), type_part.strip().lower()
        else:
            return None, type_str.lower()
    
    def _parse_output_names_from_docstring(self, func_def):
        """Parse output names from function docstring using @outputs annotation."""
        docstring = ast.get_docstring(func_def)
        if not docstring:
            return []
        
        lines = docstring.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('@outputs:'):
                # Format: @outputs: name1, name2, name3
                outputs_str = line.replace('@outputs:', '').strip()
                return [name.strip() for name in outputs_str.split(',') if name.strip()]
        
        return []

    def update_pins_from_code(self):
        new_data_inputs, new_data_outputs = {}, {}
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
                # Remove all pins if no valid function
                for pin in list(self.pins):
                    self.remove_pin(pin)
                self.fit_size_to_content()
                return
                
            self.function_name = main_func_def.name
            
            # Parse data input pins from function parameters
            for arg in main_func_def.args.args:
                new_data_inputs[arg.arg] = self._parse_type_hint(arg.annotation).lower()
            
            # Parse data output pins from return annotation
            if main_func_def.returns:
                return_annotation = main_func_def.returns
                if isinstance(return_annotation, ast.Subscript) and isinstance(return_annotation.value, ast.Name) and return_annotation.value.id.lower() == "tuple":
                    # Handle Tuple[str, int, bool] - multiple outputs
                    if hasattr(return_annotation.slice, 'elts'):
                        # Check for named outputs in docstring first
                        named_outputs = self._parse_output_names_from_docstring(main_func_def)
                        
                        for i, elt in enumerate(return_annotation.slice.elts):
                            type_name = self._parse_type_hint(elt).lower()
                            
                            # Use named output if available, otherwise use generic name
                            if i < len(named_outputs):
                                output_name = named_outputs[i]
                            else:
                                output_name = f"output_{i+1}"
                            
                            new_data_outputs[output_name] = type_name
                    else:
                        # Single tuple element like Tuple[str]
                        named_outputs = self._parse_output_names_from_docstring(main_func_def)
                        type_name = self._parse_type_hint(return_annotation.slice).lower()
                        
                        if named_outputs:
                            new_data_outputs[named_outputs[0]] = type_name
                        else:
                            new_data_outputs["output_1"] = type_name
                else:
                    # Handle single return types (including List[Dict], Dict[str, int], etc.)
                    named_outputs = self._parse_output_names_from_docstring(main_func_def)
                    type_name = self._parse_type_hint(return_annotation).lower()
                    
                    if named_outputs:
                        new_data_outputs[named_outputs[0]] = type_name
                    else:
                        new_data_outputs["output_1"] = type_name
        except (SyntaxError, AttributeError):
            return

        # Manage data pins
        current_data_inputs = {pin.name: pin for pin in self.input_pins if pin.pin_category == "data"}
        current_data_outputs = {pin.name: pin for pin in self.output_pins if pin.pin_category == "data"}
        
        # Remove obsolete data input pins
        for name, pin in list(current_data_inputs.items()):
            if name not in new_data_inputs:
                self.remove_pin(pin)
        
        # Add new data input pins
        for name, type_name in new_data_inputs.items():
            if name not in current_data_inputs:
                self.add_data_pin(name, "input", type_name)
        
        # Remove obsolete data output pins
        for name, pin in list(current_data_outputs.items()):
            if name not in new_data_outputs:
                self.remove_pin(pin)
        
        # Add new data output pins
        for name, type_name in new_data_outputs.items():
            if name not in current_data_outputs:
                self.add_data_pin(name, "output", type_name)

        # Add execution pins based on function parameters
        current_exec_inputs = {pin.name: pin for pin in self.input_pins if pin.pin_category == "execution"}
        current_exec_outputs = {pin.name: pin for pin in self.output_pins if pin.pin_category == "execution"}
        
        # Only add execution input if the function has input parameters
        # Functions without parameters are entry points and shouldn't have exec_in
        function_has_inputs = len(new_data_inputs) > 0
        
        if function_has_inputs and "exec_in" not in current_exec_inputs:
            self.add_execution_pin("exec_in", "input")
        elif not function_has_inputs and "exec_in" in current_exec_inputs:
            # Remove exec_in for entry point functions
            self.remove_pin(current_exec_inputs["exec_in"])
            
        # Always add execution output for functions
        if "exec_out" not in current_exec_outputs:
            self.add_execution_pin("exec_out", "output")
            
        self.fit_size_to_content()

    def add_pin(self, name, direction, pin_type_str, pin_category="data"):
        pin = Pin(self, name, direction, pin_type_str, pin_category)
        self.pins.append(pin)
        
        if direction == "input":
            self.input_pins.append(pin)
        else:
            self.output_pins.append(pin)
            
        if pin_category == "execution":
            self.execution_pins.append(pin)
        else:
            self.data_pins.append(pin)
            
        return pin

    def add_execution_pin(self, name, direction):
        """Add an execution pin for flow control."""
        return self.add_pin(name, direction, "exec", "execution")

    def add_data_pin(self, name, direction, pin_type_str):
        """Add a data pin for value transfer."""
        return self.add_pin(name, direction, pin_type_str, "data")

    def remove_pin(self, pin_to_remove):
        # Remove connections first
        if pin_to_remove.connections:
            for conn in list(pin_to_remove.connections):
                if self.scene():
                    self.scene().remove_connection(conn, use_command=False)
        
        # Destroy the pin (this handles scene removal safely)
        pin_to_remove.destroy()
        
        # Remove from all pin lists
        if pin_to_remove in self.pins:
            self.pins.remove(pin_to_remove)
        if pin_to_remove in self.input_pins:
            self.input_pins.remove(pin_to_remove)
        if pin_to_remove in self.output_pins:
            self.output_pins.remove(pin_to_remove)
        if pin_to_remove in self.execution_pins:
            self.execution_pins.remove(pin_to_remove)
        if pin_to_remove in self.data_pins:
            self.data_pins.remove(pin_to_remove)

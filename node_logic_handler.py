# node_logic_handler.py
# Handles the logic for a Node, including code parsing, pin management,
# and data serialization/deserialization.

import ast
from pin import Pin

class NodeLogicHandler:
    """A mixin class for Node that handles its data and logic."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_pin_by_name(self, name):
        for pin in self.pins:
            if pin.name == name: return pin
        return None

    def _parse_type_hint(self, hint_node):
        if hint_node is None: return "any"
        if isinstance(hint_node, ast.Name): return hint_node.id
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
                        if isinstance(decorator, ast.Name) and decorator.id == 'node_entry':
                            main_func_def = node
                            break
                    if main_func_def: break
            if not main_func_def:
                for pin in list(self.pins): self.remove_pin(pin)
                self._update_layout()
                return
            self.function_name = main_func_def.name
            for arg in main_func_def.args.args:
                new_inputs[arg.arg] = self._parse_type_hint(arg.annotation).lower()
            if main_func_def.returns:
                return_annotation = main_func_def.returns
                if (isinstance(return_annotation, ast.Subscript) and
                    isinstance(return_annotation.value, ast.Name) and
                    return_annotation.value.id.lower() in ('tuple', 'list')):
                    output_types = [self._parse_type_hint(elt).lower() for elt in return_annotation.slice.elts]
                    for i, type_name in enumerate(output_types):
                        new_outputs[f"output_{i+1}"] = type_name
                else:
                    new_outputs["output_1"] = self._parse_type_hint(return_annotation).lower()
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
        """Creates a new Pin, passing the raw type string for color generation."""
        pin = Pin(self, name, direction, pin_type_str)
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

    def set_code(self, code_text):
        self.code = code_text
        self.update_pins_from_code()

    def set_gui_code(self, code_text):
        self.gui_code = code_text
        self.rebuild_gui()

    def set_gui_get_values_code(self, code_text):
        self.gui_get_values_code = code_text

    def get_gui_values(self):
        if not self.gui_get_values_code or not self.gui_widgets: return {}
        try:
            scope = {'widgets': self.gui_widgets}
            exec(self.gui_get_values_code, scope)
            value_getter = scope.get('get_values')
            if callable(value_getter): return value_getter(self.gui_widgets)
            return {}
        except Exception as e: return {}

    def set_gui_values(self, outputs):
        if not self.gui_get_values_code or not self.gui_widgets: return
        try:
            scope = {'widgets': self.gui_widgets}
            exec(self.gui_get_values_code, scope)
            value_setter = scope.get('set_values')
            if callable(value_setter): value_setter(self.gui_widgets, outputs)
        except Exception as e: pass

    def apply_gui_state(self, state):
        if not self.gui_get_values_code or not self.gui_widgets or not state: return
        try:
            scope = {'widgets': self.gui_widgets}
            exec(self.gui_get_values_code, scope)
            state_setter = scope.get('set_initial_state')
            if callable(state_setter): state_setter(self.gui_widgets, state)
        except Exception as e: pass

    def serialize(self):
        return {
            "uuid": self.uuid, "title": self.title, 
            "pos": (self.pos().x(), self.pos().y()), 
            "size": (self.width, self.height),
            "code": self.code, "gui_code": self.gui_code,
            "gui_get_values_code": self.gui_get_values_code,
            "gui_state": self.get_gui_values(),
            "colors": {"title": self.color_title_bar.name(), "body": self.color_body.name()}
        }

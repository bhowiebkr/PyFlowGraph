# node_base.py
# The foundational base class for a Node in the graph.

import uuid
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QFont, QColor, QPen

class NodeBase(QGraphicsItem):
    """
    The base class for all nodes. It handles the core, non-visual, non-logical
    attributes and setup that are common to all node types.
    """
    def __init__(self, title, parent=None, **kwargs):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # --- Core Attributes ---
        self.uuid = str(uuid.uuid4())
        self.title = title
        self.base_width = 250
        self.width = self.base_width
        self.height = 150 
        self.pins, self.input_pins, self.output_pins = [], [], []
        
        # --- Code Storage ---
        self.code, self.gui_code, self.gui_get_values_code = "", "", ""
        self.function_name = None
        self.gui_widgets = {}

        # --- Visual Properties ---
        self.color_body = QColor(20, 20, 20, 220)
        self.color_title_bar = QColor("#2A2A2A")
        self.color_title_text = QColor("#E0E0E0")
        self.color_border = QColor(40, 40, 40)
        self.color_selection_glow = QColor(0, 174, 239, 150)
        self.pen_default = QPen(self.color_border, 1.5)

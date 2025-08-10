# node.py
# The main Node class, composed of various handler mixins for organization.
# This version contains the definitive fix for the rendering and initialization bug.

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsTextItem
from node_base import NodeBase
from node_gui_handler import NodeGuiHandler
from node_logic_handler import NodeLogicHandler
from node_interaction_handler import NodeInteractionHandler
from node_visuals_handler import NodeVisualsHandler

class Node(NodeGuiHandler, NodeLogicHandler, NodeInteractionHandler, NodeVisualsHandler, NodeBase):
    """
    A full-featured, draggable, and resizable block that composes all its
    functionality from various handler classes.
    """
    def __init__(self, title, parent=None):
        # --- Definitive Fix for Multiple Inheritance ---
        # Call super().__init__() to correctly initialize all parent classes
        # in the Method Resolution Order (MRO). NodeBase must be last in the
        # inheritance list so its QGraphicsItem constructor is called correctly.
        super().__init__(title=title, parent=parent)

        # --- Final Setup ---
        # Set up the title text item, which is part of the base class
        self._title_item = QGraphicsTextItem(self.title, self)
        self._title_item.setDefaultTextColor(self.color_title_text)
        self._title_item.setFont(QFont("Arial", 11, QFont.Bold))
        self._title_item.setPos(10, 5)

        # Create the GUI content.
        self._create_content_widget()
        
        # Parent the proxy widgets to this main QGraphicsItem
        self.proxy_widget.setParentItem(self)
        self.edit_button_proxy.setParentItem(self)

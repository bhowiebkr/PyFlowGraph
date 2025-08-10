# node_visuals_handler.py
# Handles all painting and visual layout logic for a Node.
# Now with a definitive, reusable fix for dynamic resizing.

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainterPath, QLinearGradient, QPen, QPainter

class NodeVisualsHandler:
    """A mixin class for Node that handles its visual appearance."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).adjusted(-5, -5, 5, 5)

    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 8, 8)
        return path

    def fit_size_to_content(self):
        """
        Calculates the optimal size for the node based on its current content
        (pins and custom GUI) and applies it. This is the source of truth for auto-sizing.
        """
        title_height, pin_spacing, pin_margin_top = 32, 25, 15
        num_pins = max(len(self.input_pins), len(self.output_pins))
        pin_area_height = (num_pins * pin_spacing) if num_pins > 0 else 0
        
        self.content_container.layout().activate()
        content_size = self.content_container.sizeHint()
        content_height = content_size.height()
        
        # Calculate the required size
        required_width = max(self.base_width, content_size.width() + 10)
        required_height = title_height + pin_area_height + pin_margin_top + content_height
        
        # Apply the new size
        self.width = required_width
        self.height = required_height
        
        # Update the layout with the new size
        self._update_layout()

    def _calculate_minimum_height(self):
        """Calculates the minimum height required by the title and pins."""
        title_height, pin_spacing, pin_margin_top = 32, 25, 15
        num_pins = max(len(self.input_pins), len(self.output_pins))
        pin_area_height = (num_pins * pin_spacing) if num_pins > 0 else 0
        return title_height + pin_area_height + pin_margin_top

    def _update_layout(self):
        """Adapts the internal layout to the node's current width and height."""
        self.prepareGeometryChange()
        
        min_content_y = self._calculate_minimum_height()
        content_y = min_content_y
        content_height = max(0, self.height - content_y)
        
        pin_start_y = 32 + 15 + (25 / 2)
        for i, pin in enumerate(self.input_pins):
            pin.setPos(0, pin_start_y + i * 25)
            pin.update_label_pos()
        for i, pin in enumerate(self.output_pins):
            pin.setPos(self.width, pin_start_y + i * 25)
            pin.update_label_pos()
        
        if self.proxy_widget:
            self.proxy_widget.setPos(0, content_y)
            # Do NOT set a fixed size. Let the internal layout manager handle it.
            # This allows the content to expand and contract naturally.
            self.proxy_widget.widget().setMinimumSize(self.width, content_height)
            self.proxy_widget.widget().setMaximumSize(self.width, content_height)
        
        self.edit_button_proxy.setPos(self.width - 35, 5)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen_color = self.color_title_bar if self.isSelected() else self.color_border
        pen = QPen(pen_color, 2 if self.isSelected() else 1.5)
        
        body_path = QPainterPath()
        body_path.addRoundedRect(0, 0, self.width, self.height, 8, 8)
        painter.setPen(pen)
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

        handle_rect = self.get_resize_handle_rect()
        painter.setPen(QPen(self.color_border.lighter(150), 1.5))
        painter.drawLine(handle_rect.left() + 4, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 4)
        painter.drawLine(handle_rect.left() + 8, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 8)
        painter.drawLine(handle_rect.left() + 12, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 12)

# node_visuals_handler.py
# Handles all painting and visual layout logic for a Node.

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

    def _update_layout(self):
        self.prepareGeometryChange()
        title_height, pin_spacing, pin_margin_top = 32, 25, 15
        num_pins = max(len(self.input_pins), len(self.output_pins))
        pin_area_height = (num_pins * pin_spacing) if num_pins > 0 else 0
        
        # The content area now only contains the custom GUI host.
        content_y = title_height + pin_area_height + pin_margin_top
        content_height = max(0, self.height - content_y)
        
        pin_start_y = title_height + pin_margin_top + (pin_spacing / 2)
        for i, pin in enumerate(self.input_pins):
            pin.setPos(0, pin_start_y + i * pin_spacing)
            pin.update_label_pos()
        for i, pin in enumerate(self.output_pins):
            pin.setPos(self.width, pin_start_y + i * pin_spacing)
            pin.update_label_pos()
        
        if self.proxy_widget:
            self.proxy_widget.setPos(0, content_y)
            self.proxy_widget.widget().setFixedSize(self.width, content_height)
        
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

        # --- Draw a more visible resize handle ---
        handle_rect = self.get_resize_handle_rect()
        painter.setPen(QPen(self.color_border.lighter(150), 1.5))
        painter.drawLine(handle_rect.left() + 4, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 4)
        painter.drawLine(handle_rect.left() + 8, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 8)
        painter.drawLine(handle_rect.left() + 12, handle_rect.bottom() - 1, handle_rect.right() - 1, handle_rect.top() + 12)

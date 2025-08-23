"""
Group Properties Dialog

Dialog for editing group properties including name, description, colors, and size.
Allows users to customize existing groups with undo/redo support.
"""

import sys
import os
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QTextEdit, QLabel, QSpinBox, QCheckBox,
                               QPushButton, QDialogButtonBox, QMessageBox, QFrame,
                               QColorDialog, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, QSize, QPointF, QRectF
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush

# Add project root to path for cross-package imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ColorButton(QPushButton):
    """Custom button that displays a color with transparency support and opens color picker when clicked."""
    
    def __init__(self, initial_color: QColor, parent=None):
        super().__init__(parent)
        self.color = QColor(initial_color) if isinstance(initial_color, QColor) else QColor(initial_color)
        self.setFixedSize(80, 30)  # Slightly wider to show transparency better
        self.clicked.connect(self._pick_color)
        self._update_style()
    
    def _update_style(self):
        """Update button style to show current color with transparency support."""
        r, g, b, a = self.color.getRgb()
        
        # Use simple background color - Qt will handle transparency properly
        rgba_color = f"rgba({r}, {g}, {b}, {a/255.0})"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {rgba_color};
                border: 2px solid #555;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #888;
            }}
        """)
        
        # Set tooltip to show RGBA values
        self.setToolTip(f"RGBA({r}, {g}, {b}, {a})")
    
    def _pick_color(self):
        """Open color picker dialog with alpha support."""
        # Use QColorDialog with alpha option
        dialog = QColorDialog(self.color, self)
        dialog.setOption(QColorDialog.ShowAlphaChannel, True)
        
        if dialog.exec() == QColorDialog.Accepted:
            new_color = dialog.selectedColor()
            if new_color.isValid():
                self.color = new_color
                self._update_style()
    
    def get_color(self) -> QColor:
        """Get current color with alpha."""
        return QColor(self.color)  # Return a copy
    
    def set_color(self, color: QColor):
        """Set color and update display."""
        self.color = QColor(color)  # Make a copy
        self._update_style()


class GroupPreviewWidget(QFrame):
    """Widget that shows a mini preview of the group with current properties and transparency effects."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 140)  # Slightly larger to better show transparency
        self.setFrameStyle(QFrame.StyledPanel)
        
        # Default properties
        self.group_name = "Group"
        self.member_count = 2
        self.color_background = QColor(45, 45, 55, 120)
        self.color_border = QColor(100, 150, 200, 180)
        self.color_title_bg = QColor(60, 60, 70, 200)
        self.color_title_text = QColor(220, 220, 220)
        self.padding = 20
        
        # Set a simple checkerboard background to show transparency
        self.setStyleSheet("""
            GroupPreviewWidget {
                background-color: #eee;
                background-image: 
                    linear-gradient(45deg, #ddd 25%, transparent 25%, transparent 75%, #ddd 75%);
                border: 1px solid #aaa;
            }
        """)
    
    def update_preview(self, name: str, colors: Dict[str, QColor], padding: int):
        """Update preview with new properties."""
        self.group_name = name
        self.color_background = colors.get('background', self.color_background)
        self.color_border = colors.get('border', self.color_border) 
        self.color_title_bg = colors.get('title_bg', self.color_title_bg)
        self.color_title_text = colors.get('title_text', self.color_title_text)
        self.padding = padding
        self.update()
    
    def paintEvent(self, event):
        """Custom paint to show group preview with proper transparency effects."""
        # First call parent to draw checkerboard background
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw mini group similar to actual group rendering
        margin = 15
        preview_rect = self.rect().adjusted(margin, margin, -margin, -margin)
        
        # Draw background with transparency
        painter.setBrush(QBrush(self.color_background))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(preview_rect, 6, 6)
        
        # Draw title bar with transparency
        title_height = 24
        title_rect = preview_rect.adjusted(0, 0, 0, -(preview_rect.height() - title_height))
        painter.setBrush(QBrush(self.color_title_bg))
        painter.drawRoundedRect(title_rect, 6, 6)
        
        # Draw border with transparency
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.color_border, 2))
        painter.drawRoundedRect(preview_rect, 6, 6)
        
        # Draw title text
        painter.setPen(QPen(self.color_title_text))
        font = QFont("Arial", 9, QFont.Bold)
        painter.setFont(font)
        title_text = f"{self.group_name} ({self.member_count} nodes)"
        painter.drawText(title_rect, Qt.AlignCenter, title_text)
        
        # Draw some mock nodes to show how transparency affects background visibility
        node_size = 16
        center = QPointF(preview_rect.center())
        node1_pos = center + QPointF(-20, 10)
        node2_pos = center + QPointF(15, 10)
        
        # Draw mock nodes as small rectangles
        painter.setBrush(QBrush(QColor(180, 180, 200)))
        painter.setPen(QPen(QColor(120, 120, 140), 1))
        
        node1_rect = QRectF(node1_pos.x() - node_size/2, node1_pos.y() - node_size/2, node_size, node_size)
        node2_rect = QRectF(node2_pos.x() - node_size/2, node2_pos.y() - node_size/2, node_size, node_size)
        
        painter.drawRoundedRect(node1_rect, 2, 2)
        painter.drawRoundedRect(node2_rect, 2, 2)
        
        # Add small labels to nodes
        painter.setPen(QPen(QColor(80, 80, 100)))
        font.setPointSize(7)
        painter.setFont(font)
        painter.drawText(node1_rect, Qt.AlignCenter, "N1")
        painter.drawText(node2_rect, Qt.AlignCenter, "N2")
        
        # Properly end the painter
        painter.end()


class GroupPropertiesDialog(QDialog):
    """
    Dialog for editing group properties including name, description, colors, and size.
    Provides live preview and validation of changes.
    """

    def __init__(self, group, parent=None):
        super().__init__(parent)
        self.group = group
        self.setWindowTitle("Group Properties")
        self.setModal(True)
        self.resize(500, 600)
        
        # Track original values for reset functionality
        self.original_properties = self._get_current_properties()
        
        # Initialize dialog
        self._setup_ui()
        self._load_current_properties()
        self._connect_signals()
        self._update_preview()
    
    def _setup_ui(self):
        """Setup the dialog user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Group Properties")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Main content in horizontal layout
        content_layout = QHBoxLayout()
        
        # Left side - Properties
        left_layout = QVBoxLayout()
        
        # Basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter group name...")
        basic_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional description...")
        self.description_edit.setMaximumHeight(80)
        basic_layout.addRow("Description:", self.description_edit)
        
        # Member count (read-only)
        self.member_count_label = QLabel(str(len(self.group.member_node_uuids))
                                       if hasattr(self.group, 'member_node_uuids') else "0")
        basic_layout.addRow("Member Nodes:", self.member_count_label)
        
        left_layout.addWidget(basic_group)
        
        # Color properties with alpha sliders
        colors_group = QGroupBox("Colors")
        colors_layout = QGridLayout(colors_group)
        
        # Import additional widgets for alpha sliders
        from PySide6.QtWidgets import QSlider
        
        # Create color buttons
        self.color_background_btn = ColorButton(self.group.color_background)
        self.color_border_btn = ColorButton(self.group.color_border)
        self.color_title_bg_btn = ColorButton(self.group.color_title_bg)
        self.color_title_text_btn = ColorButton(self.group.color_title_text)
        self.color_selection_btn = ColorButton(self.group.color_selection)
        
        # Create alpha sliders for colors that use transparency
        self.alpha_background_slider = QSlider(Qt.Horizontal)
        self.alpha_background_slider.setRange(0, 255)
        self.alpha_background_slider.setValue(self.group.color_background.alpha())
        self.alpha_background_slider.setFixedWidth(100)
        
        self.alpha_border_slider = QSlider(Qt.Horizontal)
        self.alpha_border_slider.setRange(0, 255)
        self.alpha_border_slider.setValue(self.group.color_border.alpha())
        self.alpha_border_slider.setFixedWidth(100)
        
        self.alpha_title_bg_slider = QSlider(Qt.Horizontal)
        self.alpha_title_bg_slider.setRange(0, 255)
        self.alpha_title_bg_slider.setValue(self.group.color_title_bg.alpha())
        self.alpha_title_bg_slider.setFixedWidth(100)
        
        self.alpha_selection_slider = QSlider(Qt.Horizontal)
        self.alpha_selection_slider.setRange(0, 255)
        self.alpha_selection_slider.setValue(self.group.color_selection.alpha())
        self.alpha_selection_slider.setFixedWidth(100)
        
        # Create alpha labels to show current values
        self.alpha_background_label = QLabel(f"{self.group.color_background.alpha()}")
        self.alpha_background_label.setMinimumWidth(30)
        self.alpha_border_label = QLabel(f"{self.group.color_border.alpha()}")
        self.alpha_border_label.setMinimumWidth(30)
        self.alpha_title_bg_label = QLabel(f"{self.group.color_title_bg.alpha()}")
        self.alpha_title_bg_label.setMinimumWidth(30)
        self.alpha_selection_label = QLabel(f"{self.group.color_selection.alpha()}")
        self.alpha_selection_label.setMinimumWidth(30)
        
        # Layout: Label | Color Button | Alpha Slider | Alpha Value
        # Background (row 0)
        colors_layout.addWidget(QLabel("Background:"), 0, 0)
        colors_layout.addWidget(self.color_background_btn, 0, 1)
        colors_layout.addWidget(self.alpha_background_slider, 0, 2)
        colors_layout.addWidget(self.alpha_background_label, 0, 3)
        
        # Border (row 1)
        colors_layout.addWidget(QLabel("Border:"), 1, 0)
        colors_layout.addWidget(self.color_border_btn, 1, 1)
        colors_layout.addWidget(self.alpha_border_slider, 1, 2)
        colors_layout.addWidget(self.alpha_border_label, 1, 3)
        
        # Title Background (row 2)
        colors_layout.addWidget(QLabel("Title Background:"), 2, 0)
        colors_layout.addWidget(self.color_title_bg_btn, 2, 1)
        colors_layout.addWidget(self.alpha_title_bg_slider, 2, 2)
        colors_layout.addWidget(self.alpha_title_bg_label, 2, 3)
        
        # Title Text (row 3) - no alpha slider since it's typically opaque
        colors_layout.addWidget(QLabel("Title Text:"), 3, 0)
        colors_layout.addWidget(self.color_title_text_btn, 3, 1)
        colors_layout.addWidget(QLabel(""), 3, 2)  # Empty space
        colors_layout.addWidget(QLabel("255"), 3, 3)  # Always opaque
        
        # Selection (row 4)
        colors_layout.addWidget(QLabel("Selection:"), 4, 0)
        colors_layout.addWidget(self.color_selection_btn, 4, 1)
        colors_layout.addWidget(self.alpha_selection_slider, 4, 2)
        colors_layout.addWidget(self.alpha_selection_label, 4, 3)
        
        left_layout.addWidget(colors_group)
        
        # Size properties
        size_group = QGroupBox("Size & Layout")
        size_layout = QFormLayout(size_group)
        
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(int(self.group.min_width), 2000)
        self.width_spinbox.setSuffix(" px")
        size_layout.addRow("Width:", self.width_spinbox)
        
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(int(self.group.min_height), 2000)
        self.height_spinbox.setSuffix(" px")
        size_layout.addRow("Height:", self.height_spinbox)
        
        self.padding_spinbox = QSpinBox()
        self.padding_spinbox.setRange(5, 100)
        self.padding_spinbox.setSuffix(" px")
        size_layout.addRow("Padding:", self.padding_spinbox)
        
        left_layout.addWidget(size_group)
        
        # Reset button
        self.reset_button = QPushButton("Reset to Defaults")
        left_layout.addWidget(self.reset_button)
        
        left_layout.addStretch()
        content_layout.addLayout(left_layout)
        
        # Right side - Preview
        right_layout = QVBoxLayout()
        
        preview_label = QLabel("Preview")
        preview_font = QFont()
        preview_font.setBold(True)
        preview_label.setFont(preview_font)
        right_layout.addWidget(preview_label)
        
        self.preview_widget = GroupPreviewWidget()
        right_layout.addWidget(self.preview_widget)
        
        right_layout.addStretch()
        content_layout.addLayout(right_layout)
        
        layout.addLayout(content_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setText("Apply Changes")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Store reference for validation
        self.button_box = button_box
    
    def _load_current_properties(self):
        """Load current group properties into the dialog."""
        self.name_edit.setText(self.group.name)
        self.description_edit.setPlainText(getattr(self.group, 'description', ''))
        
        # Load size properties
        self.width_spinbox.setValue(int(self.group.width))
        self.height_spinbox.setValue(int(self.group.height))
        self.padding_spinbox.setValue(int(getattr(self.group, 'padding', 20)))
        
        # Colors are already loaded into color buttons during creation
    
    def _connect_signals(self):
        """Connect UI signals to update handlers."""
        # Text changes
        self.name_edit.textChanged.connect(self._validate_and_preview)
        self.description_edit.textChanged.connect(self._update_preview)
        
        # Size changes
        self.width_spinbox.valueChanged.connect(self._update_preview)
        self.height_spinbox.valueChanged.connect(self._update_preview)
        self.padding_spinbox.valueChanged.connect(self._update_preview)
        
        # Color changes - connect to all color buttons
        for color_btn in [self.color_background_btn, self.color_border_btn, 
                         self.color_title_bg_btn, self.color_title_text_btn, 
                         self.color_selection_btn]:
            color_btn.clicked.connect(self._update_preview)
        
        # Alpha slider changes - connect to both update preview and sync with color buttons
        self.alpha_background_slider.valueChanged.connect(self._on_alpha_background_changed)
        self.alpha_border_slider.valueChanged.connect(self._on_alpha_border_changed)
        self.alpha_title_bg_slider.valueChanged.connect(self._on_alpha_title_bg_changed)
        self.alpha_selection_slider.valueChanged.connect(self._on_alpha_selection_changed)
        
        # Reset button
        self.reset_button.clicked.connect(self._reset_to_defaults)
    
    def _validate_and_preview(self):
        """Validate inputs and update preview."""
        # Validate group name
        name = self.name_edit.text().strip()
        is_valid = bool(name) and len(name) <= 100
        
        self.ok_button.setEnabled(is_valid)
        
        if not name:
            self.ok_button.setToolTip("Group name is required")
        elif len(name) > 100:
            self.ok_button.setToolTip("Group name too long (max 100 characters)")
        else:
            self.ok_button.setToolTip("Apply changes to group")
        
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview widget with current settings."""
        colors = {
            'background': self.color_background_btn.get_color(),
            'border': self.color_border_btn.get_color(),
            'title_bg': self.color_title_bg_btn.get_color(),
            'title_text': self.color_title_text_btn.get_color()
        }
        
        name = self.name_edit.text().strip() or "Group"
        padding = self.padding_spinbox.value()
        
        self.preview_widget.update_preview(name, colors, padding)

    
    def _on_alpha_background_changed(self, value: int):
        """Handle background alpha slider change."""
        # Update the color button with new alpha value
        current_color = self.color_background_btn.get_color()
        current_color.setAlpha(value)
        self.color_background_btn.set_color(current_color)
        
        # Update alpha label
        self.alpha_background_label.setText(str(value))
        
        # Update preview
        self._update_preview()
    
    def _on_alpha_border_changed(self, value: int):
        """Handle border alpha slider change."""
        current_color = self.color_border_btn.get_color()
        current_color.setAlpha(value)
        self.color_border_btn.set_color(current_color)
        
        self.alpha_border_label.setText(str(value))
        self._update_preview()
    
    def _on_alpha_title_bg_changed(self, value: int):
        """Handle title background alpha slider change."""
        current_color = self.color_title_bg_btn.get_color()
        current_color.setAlpha(value)
        self.color_title_bg_btn.set_color(current_color)
        
        self.alpha_title_bg_label.setText(str(value))
        self._update_preview()
    
    def _on_alpha_selection_changed(self, value: int):
        """Handle selection alpha slider change."""
        current_color = self.color_selection_btn.get_color()
        current_color.setAlpha(value)
        self.color_selection_btn.set_color(current_color)
        
        self.alpha_selection_label.setText(str(value))
        self._update_preview()
    
    def _reset_to_defaults(self):
        """Reset all properties to default values."""
        # Default colors with original alpha values
        self.color_background_btn.set_color(QColor(45, 45, 55, 120))
        self.color_border_btn.set_color(QColor(100, 150, 200, 180))
        self.color_title_bg_btn.set_color(QColor(60, 60, 70, 200))
        self.color_title_text_btn.set_color(QColor(220, 220, 220, 255))  # Explicitly set alpha 255
        self.color_selection_btn.set_color(QColor(255, 165, 0, 100))
        
        # Reset alpha sliders to match default values
        self.alpha_background_slider.setValue(120)
        self.alpha_border_slider.setValue(180)
        self.alpha_title_bg_slider.setValue(200)
        self.alpha_selection_slider.setValue(100)
        
        # Update alpha labels
        self.alpha_background_label.setText("120")
        self.alpha_border_label.setText("180")
        self.alpha_title_bg_label.setText("200")
        self.alpha_selection_label.setText("100")
        
        # Default size
        self.width_spinbox.setValue(200)
        self.height_spinbox.setValue(150)
        self.padding_spinbox.setValue(20)
        
        # Keep name and description as-is (don't reset user content)
        
        self._update_preview()
    
    def _get_current_properties(self) -> Dict[str, Any]:
        """Get current group properties for comparison/reset."""
        return {
            'name': self.group.name,
            'description': getattr(self.group, 'description', ''),
            'width': self.group.width,
            'height': self.group.height,
            'padding': getattr(self.group, 'padding', 20),
            'color_background': QColor(self.group.color_background),
            'color_border': QColor(self.group.color_border),
            'color_title_bg': QColor(self.group.color_title_bg),
            'color_title_text': QColor(self.group.color_title_text),
            'color_selection': QColor(self.group.color_selection),
        }
    
    def get_properties(self) -> Dict[str, Any]:
        """Get the configured properties from the dialog."""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'width': float(self.width_spinbox.value()),
            'height': float(self.height_spinbox.value()),
            'padding': float(self.padding_spinbox.value()),
            'color_background': self.color_background_btn.get_color(),
            'color_border': self.color_border_btn.get_color(),
            'color_title_bg': self.color_title_bg_btn.get_color(),
            'color_title_text': self.color_title_text_btn.get_color(),
            'color_selection': self.color_selection_btn.get_color(),
        }
    
    def get_changed_properties(self) -> Dict[str, Any]:
        """Get only the properties that have changed from original values."""
        current = self.get_properties()
        changed = {}
        
        for key, value in current.items():
            original_value = self.original_properties.get(key)
            if isinstance(value, QColor) and isinstance(original_value, QColor):
                # Compare colors by their RGBA values
                if value.getRgb() != original_value.getRgb():
                    changed[key] = value
            elif value != original_value:
                changed[key] = value
        
        return changed
    
    def accept(self):
        """Override accept to perform final validation."""
        # Final validation
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Group name is required.")
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, "Invalid Input", "Group name too long (max 100 characters).")
            return
        
        super().accept()


def show_group_properties_dialog(group, parent=None) -> Optional[Dict[str, Any]]:
    """
    Show group properties dialog and return changed properties.
    
    Args:
        group: The group to edit properties for
        parent: Parent widget
        
    Returns:
        Dictionary of changed properties if accepted, None if cancelled
    """
    dialog = GroupPropertiesDialog(group, parent)
    
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_changed_properties()
    
    return None
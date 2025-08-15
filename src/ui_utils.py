# ui_utils.py
# UI utilities for PyFlowGraph including icon creation and styling

from PySide6.QtWidgets import QWidget, QHBoxLayout, QRadioButton, QPushButton, QButtonGroup, QLabel
from PySide6.QtGui import QAction, QFont, QIcon, QPainter, QColor, QPixmap
from PySide6.QtCore import Qt


def create_fa_icon(char_code, color="white", font_style="regular"):
    """Creates a QIcon from a Font Awesome character code."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)

    if font_style == "solid":
        font = QFont("Font Awesome 6 Free Solid")
    else:
        font = QFont("Font Awesome 7 Free Regular")

    font.setPixelSize(24)
    painter.setFont(font)
    painter.setPen(QColor(color))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, char_code)
    painter.end()
    return QIcon(pixmap)


class ButtonStyleManager:
    """Manages button styles for different execution modes and states."""
    
    @staticmethod
    def get_button_style(mode, state="ready"):
        """Get stylesheet for the main button based on mode and state."""
        if mode == "batch":
            if state == "ready":
                return """
                    QPushButton {
                        background-color: #4CAF50;
                        color: #000000;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                        color: #000000;
                    }
                    QPushButton:pressed {
                        background-color: #3d8b40;
                        color: #000000;
                    }
                """
            else:  # executing
                return """
                    QPushButton {
                        background-color: #607D8B;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                """
        else:  # live mode
            if state == "ready":
                return """
                    QPushButton {
                        background-color: #FF9800;
                        color: #000000;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #F57C00;
                        color: #000000;
                    }
                    QPushButton:pressed {
                        background-color: #E65100;
                        color: #000000;
                    }
                """
            elif state == "active":
                return """
                    QPushButton {
                        background-color: #4CAF50;
                        color: #000000;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                        color: #000000;
                    }
                """
            else:  # paused
                return """
                    QPushButton {
                        background-color: #F44336;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #da190b;
                        color: #FFFFFF;
                    }
                """


def create_execution_control_widget(mode_changed_callback, button_clicked_callback):
    """Create the execution mode and control widget."""
    # Container widget
    exec_widget = QWidget()
    layout = QHBoxLayout(exec_widget)
    layout.setContentsMargins(10, 5, 10, 5)
    layout.setSpacing(15)

    # Mode selection label
    mode_label = QLabel("Execution Mode:")
    mode_label.setStyleSheet("font-weight: bold; color: #E0E0E0;")
    layout.addWidget(mode_label)

    # Radio buttons for mode selection
    mode_button_group = QButtonGroup()

    batch_radio = QRadioButton("Batch")
    batch_radio.setToolTip("Traditional one-shot execution of entire graph")
    batch_radio.setChecked(True)  # Default mode
    batch_radio.setStyleSheet("""
        QRadioButton {
            color: #E0E0E0;
            font-weight: bold;
            spacing: 8px;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid #666;
            background-color: transparent;
        }
        QRadioButton::indicator:checked {
            background-color: #4CAF50;
            border: 2px solid #4CAF50;
        }
        QRadioButton::indicator:hover {
            border: 2px solid #888;
        }
    """)

    live_radio = QRadioButton("Live")
    live_radio.setToolTip("Interactive mode with event-driven execution")
    live_radio.setStyleSheet("""
        QRadioButton {
            color: #E0E0E0;
            font-weight: bold;
            spacing: 8px;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid #666;
            background-color: transparent;
        }
        QRadioButton::indicator:checked {
            background-color: #FF9800;
            border: 2px solid #FF9800;
        }
        QRadioButton::indicator:hover {
            border: 2px solid #888;
        }
    """)

    mode_button_group.addButton(batch_radio, 0)
    mode_button_group.addButton(live_radio, 1)
    mode_button_group.idClicked.connect(mode_changed_callback)

    layout.addWidget(batch_radio)
    layout.addWidget(live_radio)

    # Separator
    separator = QLabel("|")
    separator.setStyleSheet("color: #666; font-size: 16px;")
    layout.addWidget(separator)

    # Main execution button - changes based on mode
    main_exec_button = QPushButton("Execute Graph")
    main_exec_button.setMinimumSize(140, 35)
    main_exec_button.setStyleSheet(ButtonStyleManager.get_button_style("batch"))
    main_exec_button.clicked.connect(button_clicked_callback)
    main_exec_button.setShortcut("F5")
    layout.addWidget(main_exec_button)

    # Status indicator
    status_label = QLabel("Ready")
    status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
    layout.addWidget(status_label)

    # Store references for external access
    exec_widget.mode_button_group = mode_button_group
    exec_widget.batch_radio = batch_radio
    exec_widget.live_radio = live_radio
    exec_widget.main_exec_button = main_exec_button
    exec_widget.status_label = status_label

    return exec_widget
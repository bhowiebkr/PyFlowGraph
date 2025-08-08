# socket_type.py
# Enum for defining pin types and their associated colors for compatibility checks.

from enum import Enum
from PySide6.QtGui import QColor

class SocketType(Enum):
    """
    Defines the types of pins and their corresponding colors.
    Used for visual identification and connection compatibility.
    """
    ANY = QColor("#C0C0C0")       # Grey for unknown/any type
    FLOAT = QColor("#00A0F0")     # Blue for floating-point numbers
    INT = QColor("#50E050")       # Green for integers
    STRING = QColor("#F050A0")    # Pink for text strings
    BOOLEAN = QColor("#F0A000")   # Orange for true/false values

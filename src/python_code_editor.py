# python_code_editor.py
# A custom QPlainTextEdit widget with line numbers, syntax highlighting,
# and smart indentation for Python.

from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtGui import QColor, QPainter, QFont, QKeyEvent, QTextFormat
from .python_syntax_highlighter import PythonSyntaxHighlighter

class LineNumberArea(QWidget):
    """A widget that displays line numbers for a QPlainTextEdit."""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class PythonCodeEditor(QPlainTextEdit):
    """
    A custom code editor widget for Python.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.highlighter = PythonSyntaxHighlighter(self.document())

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        """Calculates the width required for the line number area."""
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val /= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        """Sets the margin of the text edit to make space for the line numbers."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Scrolls the line number area along with the text editor."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Updates the line number area's geometry on resize."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """Paints the line numbers in the line number area."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2A2A2A"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, int(top), self.line_number_area.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#3A3D4A")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)


    def keyPressEvent(self, event: QKeyEvent):
        """Overrides key press events for smart indentation."""
        cursor = self.textCursor()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            prev_line_text = cursor.block().text()
            indentation = ""
            for char in prev_line_text:
                if char.isspace():
                    indentation += char
                else:
                    break
            
            super().keyPressEvent(event)
            self.insertPlainText(indentation)
            if prev_line_text.strip().endswith(':'):
                self.insertPlainText("    ") # Add extra indent after a colon
        
        elif event.key() == Qt.Key_Tab:
            cursor.insertText("    ")
        
        elif event.key() == Qt.Key_Backspace:
            if cursor.positionInBlock() > 0 and cursor.block().text()[cursor.positionInBlock()-4:cursor.positionInBlock()] == "    ":
                for _ in range(4):
                    cursor.deletePreviousChar()
            else:
                super().keyPressEvent(event)
        
        else:
            super().keyPressEvent(event)

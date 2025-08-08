# python_syntax_highlighter.py
# Implements syntax highlighting for Python code using QSyntaxHighlighter.

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter for Python code, derived from QSyntaxHighlighter.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlighting_rules = []

        # --- Keyword Format ---
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6")) # Blue
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "\\bdef\\b", "\\bclass\\b", "\\bimport\\b", "\\bfrom\\b", "\\breturn\\b",
            "\\bif\\b", "\\belif\\b", "\\belse\\b", "\\bfor\\b", "\\bwhile\\b",
            "\\bin\\b", "\\bis\\b", "\\bnot\\b", "\\band\\b", "\\bor\\b",
            "\\bpass\\b", "\\bcontinue\\b", "\\bbreak\\b", "\\btry\\b", "\\bexcept\\b",
            "\\bfinally\\b", "\\bwith\\b", "\\bas\\b", "\\blambda\\b", "\\bself\\b",
            "\\bTrue\\b", "\\bFalse\\b", "\\bNone\\b"
        ]
        for word in keywords:
            pattern = QRegularExpression(word)
            self.highlighting_rules.append((pattern, keyword_format))

        # --- Function and Class Name Format ---
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA")) # Yellow
        self.highlighting_rules.append((QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()"), function_format))
        
        class_format = QTextCharFormat()
        class_format.setFontWeight(QFont.Bold)
        class_format.setForeground(QColor("#4EC9B0")) # Teal
        self.highlighting_rules.append((QRegularExpression("\\bclass\\s+[A-Za-z_][A-Za-z0-9_]*"), class_format))


        # --- String Format ---
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178")) # Orange
        self.highlighting_rules.append((QRegularExpression("\".*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("'.*'"), string_format))

        # --- Number Format ---
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8")) # Green
        self.highlighting_rules.append((QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"), number_format))

        # --- Comment Format ---
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955")) # Dark Green
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

    def highlightBlock(self, text):
        """
        Applies syntax highlighting to the given block of text.
        """
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

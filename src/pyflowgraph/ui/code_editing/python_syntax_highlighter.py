# python_syntax_highlighter.py
# Implements syntax highlighting for Python code using QSyntaxHighlighter.
# Now with more advanced highlighting for decorators, types, and magic methods.

from PySide6.QtCore import QRegularExpression, Qt
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
        keyword_format.setForeground(QColor("#C586C0"))  # VS Code Purple
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "\\bdef\\b",
            "\\bclass\\b",
            "\\bimport\\b",
            "\\bfrom\\b",
            "\\breturn\\b",
            "\\bif\\b",
            "\\belif\\b",
            "\\belse\\b",
            "\\bfor\\b",
            "\\bwhile\\b",
            "\\bin\\b",
            "\\bis\\b",
            "\\bnot\\b",
            "\\band\\b",
            "\\bor\\b",
            "\\bpass\\b",
            "\\bcontinue\\b",
            "\\bbreak\\b",
            "\\btry\\b",
            "\\bexcept\\b",
            "\\bfinally\\b",
            "\\bwith\\b",
            "\\bas\\b",
            "\\blambda\\b",
        ]
        for word in keywords:
            self.highlighting_rules.append((QRegularExpression(word), keyword_format))

        # --- Special Constants & 'self' ---
        special_constants_format = QTextCharFormat()
        special_constants_format.setForeground(QColor("#569CD6"))  # VS Code Blue
        special_constants = ["\\bTrue\\b", "\\bFalse\\b", "\\bNone\\b", "\\bself\\b"]
        for word in special_constants:
            self.highlighting_rules.append((QRegularExpression(word), special_constants_format))

        # --- Decorator Format ---
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#DCDCAA"))  # Yellow
        self.highlighting_rules.append((QRegularExpression("@[A-Za-z0-9_]+"), decorator_format))

        # --- Type Hint / Class Name Format ---
        type_hint_format = QTextCharFormat()
        type_hint_format.setForeground(QColor("#4EC9B0"))  # Teal
        # Matches class names and common type hints
        self.highlighting_rules.append((QRegularExpression("\\b[A-Z][A-Za-z0-9_]*"), type_hint_format))

        # --- Function and Magic Method Format ---
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))  # Yellow
        self.highlighting_rules.append((QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()"), function_format))

        magic_method_format = QTextCharFormat()
        magic_method_format.setForeground(QColor("#9CDCFE"))  # Light Blue
        magic_method_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("\\b__[a-zA-Z_][a-zA-Z0-9_]*__\\b"), magic_method_format))

        # --- String Format ---
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))  # Orange
        self.highlighting_rules.append((QRegularExpression("'[^']*'"), string_format))
        self.highlighting_rules.append((QRegularExpression('"[^"]*"'), string_format))

        # --- Number Format ---
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))  # Green
        self.highlighting_rules.append((QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"), number_format))

        # --- Comment Format ---
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))  # Dark Green
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

        # --- Multi-line String Formats ---
        self.tri_single_quote_format = QTextCharFormat()
        self.tri_single_quote_format.setForeground(QColor("#CE9178"))  # Orange
        self.tri_double_quote_format = QTextCharFormat()
        self.tri_double_quote_format.setForeground(QColor("#CE9178"))  # Orange

        self.tri_single_start_expression = QRegularExpression("'''")
        self.tri_single_end_expression = QRegularExpression("'''")
        self.tri_double_start_expression = QRegularExpression('"""')
        self.tri_double_end_expression = QRegularExpression('"""')

    def highlightBlock(self, text):
        """
        Applies syntax highlighting to the given block of text.
        """
        # Apply standard rules
        for pattern, format_rule in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_rule)

        # Handle multi-line strings
        self.setCurrentBlockState(0)

        # Triple single quotes
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.tri_single_start_expression.match(text).capturedStart()

        while start_index >= 0:
            end_index = self.tri_single_end_expression.match(text, start_index + 3).capturedStart()
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_len = len(text) - start_index
            else:
                comment_len = end_index - start_index + 3
            self.setFormat(start_index, comment_len, self.tri_single_quote_format)
            start_index = self.tri_single_start_expression.match(text, start_index + comment_len).capturedStart()

        # Triple double quotes
        start_index = 0
        if self.previousBlockState() != 2:
            start_index = self.tri_double_start_expression.match(text).capturedStart()

        while start_index >= 0:
            end_index = self.tri_double_end_expression.match(text, start_index + 3).capturedStart()
            if end_index == -1:
                self.setCurrentBlockState(2)
                comment_len = len(text) - start_index
            else:
                comment_len = end_index - start_index + 3
            self.setFormat(start_index, comment_len, self.tri_double_quote_format)
            start_index = self.tri_double_start_expression.match(text, start_index + comment_len).capturedStart()

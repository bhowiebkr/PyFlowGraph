# Password Generator Tool

Password generation workflow with configurable parameters, random character selection, strength scoring algorithm, and GUI output display. Implements user-defined character set selection, random.choice() generation, regex-based strength analysis, and formatted result presentation.

## Node: Password Configuration (ID: config-input)

Collects password generation parameters through QSpinBox (length 4-128) and QCheckBox widgets for character set selection. Returns named outputs: length (int), uppercase (bool), lowercase (bool), numbers (bool), and symbols (bool) for configuration values.

GUI state management handles default values: length=12, uppercase=True, lowercase=True, numbers=True, symbols=False. Uses standard get_values() and set_initial_state() functions for parameter persistence and retrieval.

### Metadata

```json
{
  "uuid": "config-input",
  "title": "Password Configuration",
  "pos": [
    -114.11883349999994,
    118.0365416250001
  ],
  "size": [
    296.7499999999999,
    412
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "length": 12,
    "include_uppercase": true,
    "include_lowercase": true,
    "include_numbers": true,
    "include_symbols": false
  }
}
```

### Logic

```python
from typing import Tuple

@node_entry
def configure_password(length: int, include_uppercase: bool, include_lowercase: bool, include_numbers: bool, include_symbols: bool) -> Tuple[int, bool, bool, bool, bool]:
    """
    Configure password generation parameters.
    @outputs: length, uppercase, lowercase, numbers, symbols
    """
    print(f"Password config: {length} chars, Upper: {include_uppercase}, Lower: {include_lowercase}, Numbers: {include_numbers}, Symbols: {include_symbols}")
    return length, include_uppercase, include_lowercase, include_numbers, include_symbols
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QSpinBox, QCheckBox, QPushButton

layout.addWidget(QLabel('Password Length:', parent))
widgets['length'] = QSpinBox(parent)
widgets['length'].setRange(4, 128)
widgets['length'].setValue(12)
layout.addWidget(widgets['length'])

widgets['uppercase'] = QCheckBox('Include Uppercase (A-Z)', parent)
widgets['uppercase'].setChecked(True)
layout.addWidget(widgets['uppercase'])

widgets['lowercase'] = QCheckBox('Include Lowercase (a-z)', parent)
widgets['lowercase'].setChecked(True)
layout.addWidget(widgets['lowercase'])

widgets['numbers'] = QCheckBox('Include Numbers (0-9)', parent)
widgets['numbers'].setChecked(True)
layout.addWidget(widgets['numbers'])

widgets['symbols'] = QCheckBox('Include Symbols (!@#$%)', parent)
widgets['symbols'].setChecked(False)
layout.addWidget(widgets['symbols'])

widgets['generate_btn'] = QPushButton('Generate Password', parent)
layout.addWidget(widgets['generate_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'length': widgets['length'].value(),
        'include_uppercase': widgets['uppercase'].isChecked(),
        'include_lowercase': widgets['lowercase'].isChecked(),
        'include_numbers': widgets['numbers'].isChecked(),
        'include_symbols': widgets['symbols'].isChecked()
    }

def set_values(widgets, outputs):
    # Config node doesn't need to display outputs
    pass

def set_initial_state(widgets, state):
    widgets['length'].setValue(state.get('length', 12))
    widgets['uppercase'].setChecked(state.get('include_uppercase', True))
    widgets['lowercase'].setChecked(state.get('include_lowercase', True))
    widgets['numbers'].setChecked(state.get('include_numbers', True))
    widgets['symbols'].setChecked(state.get('include_symbols', False))
```


## Node: Password Generator Engine (ID: password-generator)

Constructs character set by concatenating string.ascii_uppercase, string.ascii_lowercase, string.digits, and custom symbol string based on boolean input flags. Uses random.choice() with list comprehension to generate password of specified length.

Includes error handling for empty character sets, returning "Error: No character types selected!" when no character categories are enabled. Character set construction is conditional based on input parameters, symbols include '!@#$%^&*()_+-=[]{}|;:,.<>?' set.

### Metadata

```json
{
  "uuid": "password-generator",
  "title": "Password Generator Engine",
  "pos": [
    259.43116650000024,
    147.1315416250001
  ],
  "size": [
    264.40499999999975,
    242
  ],
  "colors": {
    "title": "#28a745",
    "body": "#1e7e34"
  },
  "gui_state": {}
}
```

### Logic

```python
import random
import string

@node_entry
def generate_password(length: int, include_uppercase: bool, include_lowercase: bool, include_numbers: bool, include_symbols: bool) -> str:
    """
    Generate password using specified parameters.
    @outputs: password
    """
    charset = ''
    
    if include_uppercase:
        charset += string.ascii_uppercase
    if include_lowercase:
        charset += string.ascii_lowercase
    if include_numbers:
        charset += string.digits
    if include_symbols:
        charset += '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    if not charset:
        return "Error: No character types selected!"
    
    password = ''.join(random.choice(charset) for _ in range(length))
    print(f"Generated password: {password}")
    return password
```


## Node: Password Strength Analyzer (ID: strength-analyzer)

Analyzes password strength using regex pattern matching and point-based scoring system. Length scoring: 25 points for >=12 chars, 15 points for >=8 chars. Character variety scoring: 20 points each for uppercase (A-Z), lowercase (a-z), numbers (0-9), 15 points for symbols.

Uses re.search() with specific patterns to detect character categories. Score thresholds: >=80 Very Strong, >=60 Strong, >=40 Moderate, >=20 Weak, <20 Very Weak. Returns named outputs: strength (str), score (int), and feedback (str) for analysis results.

Feedback generation uses list accumulation for missing elements, joined with semicolons. Provides specific recommendations for improving password complexity based on detected deficiencies.

### Metadata

```json
{
  "uuid": "strength-analyzer",
  "title": "Password Strength Analyzer",
  "pos": [
    844.8725,
    304.73249999999996
  ],
  "size": [
    250,
    192
  ],
  "colors": {
    "title": "#fd7e14",
    "body": "#e8590c"
  },
  "gui_state": {}
}
```

### Logic

```python
import re
from typing import Tuple

@node_entry
def analyze_strength(password: str) -> Tuple[str, int, str]:
    """
    Analyze password strength and provide feedback.
    @outputs: strength, score, feedback
    """
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 12:
        score += 25
    elif len(password) >= 8:
        score += 15
        feedback.append("Consider using 12+ characters")
    else:
        feedback.append("Password too short (8+ recommended)")
    
    # Character variety
    if re.search(r'[A-Z]', password):
        score += 20
    else:
        feedback.append("Add uppercase letters")
        
    if re.search(r'[a-z]', password):
        score += 20
    else:
        feedback.append("Add lowercase letters")
        
    if re.search(r'[0-9]', password):
        score += 20
    else:
        feedback.append("Add numbers")
        
    if re.search(r'[!@#$%^&*()_+=\[\]{}|;:,.<>?-]', password):
        score += 15
    else:
        feedback.append("Add symbols for extra security")
    
    # Determine strength level
    if score >= 80:
        strength = "Very Strong"
    elif score >= 60:
        strength = "Strong"
    elif score >= 40:
        strength = "Moderate"
    elif score >= 20:
        strength = "Weak"
    else:
        strength = "Very Weak"
    
    feedback_text = "; ".join(feedback) if feedback else "Excellent password!"
    
    print(f"Password strength: {strength} (Score: {score}/100)")
    print(f"Feedback: {feedback_text}")
    
    return strength, score, feedback_text
```


## Node: Password Output & Copy (ID: output-display)

Formats password generation results into display string combining password, strength rating, score, and feedback. Uses string concatenation to create structured output: "Generated Password: {password}\nStrength: {strength} ({score}/100)\nFeedback: {feedback}".

GUI implementation includes QLineEdit for password display (read-only), QTextEdit for strength analysis, and QPushButton components for copy and regeneration actions. String parsing in set_values() extracts password from formatted result using string.split() and string replacement operations.

Handles multiple input parameters (password, strength, score, feedback) and consolidates them into single formatted output string for display and further processing.

### Metadata

```json
{
  "uuid": "output-display",
  "title": "Password Output & Copy",
  "pos": [
    1182.5525,
    137.84249999999997
  ],
  "size": [
    340.9674999999995,
    513
  ],
  "colors": {
    "title": "#6c757d",
    "body": "#545b62"
  },
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def display_result(password: str, strength: str, score: int, feedback: str) -> str:
    """
    Format and display password generation results.
    @outputs: result
    """
    result = f"Generated Password: {password}\n"
    result += f"Strength: {strength} ({score}/100)\n"
    result += f"Feedback: {feedback}"
    print("\n=== PASSWORD GENERATION COMPLETE ===")
    print(result)
    return result
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Generated Password', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['password_field'] = QLineEdit(parent)
widgets['password_field'].setReadOnly(True)
widgets['password_field'].setPlaceholderText('Password will appear here...')
layout.addWidget(widgets['password_field'])

widgets['copy_btn'] = QPushButton('Copy to Clipboard', parent)
layout.addWidget(widgets['copy_btn'])

widgets['strength_display'] = QTextEdit(parent)
widgets['strength_display'].setMinimumHeight(120)
widgets['strength_display'].setReadOnly(True)
widgets['strength_display'].setPlainText('Generate a password to see strength analysis...')
layout.addWidget(widgets['strength_display'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    # Extract password from the result string using named output
    result = outputs.get('result', '')
    lines = result.split('\n')
    if lines:
        password_line = lines[0]
        if 'Generated Password: ' in password_line:
            password = password_line.replace('Generated Password: ', '')
            widgets['password_field'].setText(password)
    
    widgets['strength_display'].setPlainText(result)

def set_initial_state(widgets, state):
    # Output display node doesn't have saved state to restore
    pass
```


## Groups

```json
[
  {
    "uuid": "a52f24cd-6e3a-4d96-998f-efd17e01fce9",
    "name": "Group (Password Configuration, Password Generator Engine)",
    "description": "This is a description of this node. \n\nIt should be able to handle multi lines, paragraphss. etc.",
    "member_node_uuids": [
      "config-input",
      "password-generator"
    ],
    "is_expanded": true,
    "position": {
      "x": -223.71077007142847,
      "y": 16.375099107143
    },
    "size": {
      "width": 880.0,
      "height": 616.0
    },
    "padding": 20,
    "colors": {
      "background": {
        "r": 255,
        "g": 85,
        "b": 0,
        "a": 73
      },
      "border": {
        "r": 100,
        "g": 150,
        "b": 200,
        "a": 180
      },
      "title_bg": {
        "r": 60,
        "g": 60,
        "b": 70,
        "a": 200
      },
      "title_text": {
        "r": 220,
        "g": 220,
        "b": 220,
        "a": 255
      },
      "selection": {
        "r": 255,
        "g": 165,
        "b": 0,
        "a": 100
      }
    }
  }
]
```

## Connections

```json
[
  {
    "start_node_uuid": "config-input",
    "start_pin_name": "exec_out",
    "end_node_uuid": "password-generator",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "config-input",
    "start_pin_name": "length",
    "end_node_uuid": "password-generator",
    "end_pin_name": "length"
  },
  {
    "start_node_uuid": "config-input",
    "start_pin_name": "uppercase",
    "end_node_uuid": "password-generator",
    "end_pin_name": "include_uppercase"
  },
  {
    "start_node_uuid": "config-input",
    "start_pin_name": "lowercase",
    "end_node_uuid": "password-generator",
    "end_pin_name": "include_lowercase"
  },
  {
    "start_node_uuid": "config-input",
    "start_pin_name": "numbers",
    "end_node_uuid": "password-generator",
    "end_pin_name": "include_numbers"
  },
  {
    "start_node_uuid": "config-input",
    "start_pin_name": "symbols",
    "end_node_uuid": "password-generator",
    "end_pin_name": "include_symbols"
  },
  {
    "start_node_uuid": "password-generator",
    "start_pin_name": "exec_out",
    "end_node_uuid": "strength-analyzer",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "password-generator",
    "start_pin_name": "password",
    "end_node_uuid": "strength-analyzer",
    "end_pin_name": "password"
  },
  {
    "start_node_uuid": "strength-analyzer",
    "start_pin_name": "exec_out",
    "end_node_uuid": "output-display",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "password-generator",
    "start_pin_name": "password",
    "end_node_uuid": "output-display",
    "end_pin_name": "password"
  },
  {
    "start_node_uuid": "strength-analyzer",
    "start_pin_name": "strength",
    "end_node_uuid": "output-display",
    "end_pin_name": "strength"
  },
  {
    "start_node_uuid": "strength-analyzer",
    "start_pin_name": "score",
    "end_node_uuid": "output-display",
    "end_pin_name": "score"
  },
  {
    "start_node_uuid": "strength-analyzer",
    "start_pin_name": "feedback",
    "end_node_uuid": "output-display",
    "end_pin_name": "feedback"
  }
]
```

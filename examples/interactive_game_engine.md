# Interactive Game Engine

A branching narrative game system demonstrating conditional logic flow control through interactive choice selection. Implements a choose-your-own-adventure structure with GUI-based player input, string-based routing logic, and randomized encounter outcomes across multiple parallel execution paths.

## Node: Game Start (ID: game-start)

Initializes the game session by returning a welcome string and printing startup messages to console. Simple entry point node with no inputs that outputs "Welcome, adventurer!" string for downstream processing. Serves as the execution trigger for the entire game flow.

### Metadata

```json
{
  "uuid": "game-start",
  "title": "Game Start",
  "pos": [
    100.0,
    200.0
  ],
  "size": [
    250,
    118
  ],
  "colors": {
    "title": "#1e7e34",
    "body": "#155724"
  },
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def start_game() -> str:
    print("=== ADVENTURE GAME STARTED ===")
    print("You find yourself at a crossroads...")
    return "Welcome, adventurer!"
```


## Node: Player Choice Hub (ID: player-choice)

Provides player input interface using QComboBox with four predefined path options: Forest Path, Mountain Trail, Cave Entrance, River Crossing. Takes welcome message string as input and outputs formatted choice string "Choice: {selection}". GUI includes dropdown selector and execution button for choice confirmation.

Implements basic state management for choice persistence and processes user selection through get_values() function. Choice selection is validated through currentText() method and formatted into standardized output string for downstream routing logic.

### Metadata

```json
{
  "uuid": "player-choice",
  "title": "Player Choice Hub",
  "pos": [
    467.49006250000014,
    192.69733124999993
  ],
  "size": [
    250,
    219
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "choice": "Forest Path"
  }
}
```

### Logic

```python
@node_entry
def handle_choice(welcome_msg: str, choice: str) -> str:
    print(f"Player chose: {choice}")
    return f"Choice: {choice}"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QComboBox, QPushButton

layout.addWidget(QLabel('Choose your path:', parent))
widgets['choice'] = QComboBox(parent)
widgets['choice'].addItems(['Forest Path', 'Mountain Trail', 'Cave Entrance', 'River Crossing'])
layout.addWidget(widgets['choice'])

widgets['execute_btn'] = QPushButton('Make Choice', parent)
layout.addWidget(widgets['execute_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'choice': widgets['choice'].currentText()
    }

def set_initial_state(widgets, state):
    if 'choice' in state:
        widgets['choice'].setCurrentText(state['choice'])
```


## Node: Condition Router (ID: condition-checker)

Parses formatted choice string using string.split() to extract route identifier, then maps choice text to single-word route codes: 'forest', 'mountain', 'cave', or 'river'. Uses if-elif-else conditional logic to convert human-readable choice names into routing tokens.

Handles input format "Choice: {path_name}" by splitting on ': ' delimiter and extracting the second element. Returns lowercase route identifier strings that are consumed by multiple downstream adventure nodes for conditional execution.

### Metadata

```json
{
  "uuid": "condition-checker",
  "title": "Condition Router",
  "pos": [
    850.0,
    200.0
  ],
  "size": [
    250,
    118
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
@node_entry
def route_choice(player_choice: str) -> str:
    choice = player_choice.split(': ')[1] if ': ' in player_choice else player_choice
    
    if choice == 'Forest Path':
        return 'forest'
    elif choice == 'Mountain Trail':
        return 'mountain' 
    elif choice == 'Cave Entrance':
        return 'cave'
    else:
        return 'river'
```


## Node: Forest Adventure (ID: forest-encounter)

Executes forest-specific encounter logic when route input equals 'forest'. Uses random.choice() to select from four predefined encounter strings stored in a list. Returns randomized adventure outcome string or default rejection message for non-forest routes.

Includes QTextEdit GUI component for displaying encounter results with read-only formatting. Updates display through set_values() function that formats output as "FOREST ENCOUNTER:\n\n{result}". Adventure outcomes are deterministic but randomly selected on each execution.

### Metadata

```json
{
  "uuid": "forest-encounter",
  "title": "Forest Adventure",
  "pos": [
    1269.96025,
    -168.62578124999987
  ],
  "size": [
    276,
    310
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
@node_entry
def forest_adventure(route: str) -> str:
    if route == 'forest':
        import random
        encounters = [
            "You meet a friendly fairy who gives you a magic potion!",
            "A wise old tree shares ancient knowledge with you.",
            "You discover a hidden treasure chest full of gold!",
            "A pack of wolves surrounds you, but they're actually friendly!"
        ]
        result = random.choice(encounters)
        print(f"Forest: {result}")
        return result
    return "This path is not for you."
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit
from PySide6.QtCore import Qt

widgets['result_text'] = QTextEdit(parent)
widgets['result_text'].setMinimumHeight(120)
widgets['result_text'].setReadOnly(True)
widgets['result_text'].setPlainText('Waiting for forest adventure...')
layout.addWidget(widgets['result_text'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    result = outputs.get('output_1', 'No result')
    widgets['result_text'].setPlainText(f'FOREST ENCOUNTER:\n\n{result}')
```


## Node: Mountain Challenge (ID: mountain-encounter)

Executes mountain-specific encounter logic when route input equals 'mountain'. Uses random.choice() to select from four predefined challenge strings. Returns randomized adventure outcome string or default rejection message for non-mountain routes.

Includes QTextEdit GUI component for displaying challenge results with read-only formatting. Updates display through set_values() function that formats output as "MOUNTAIN CHALLENGE:\n\n{result}". Challenge outcomes are randomly selected from predefined list on each execution.

### Metadata

```json
{
  "uuid": "mountain-encounter",
  "title": "Mountain Challenge",
  "pos": [
    1353.91255,
    193.31061875000012
  ],
  "size": [
    276,
    310
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
def mountain_adventure(route: str) -> str:
    if route == 'mountain':
        import random
        challenges = [
            "You climb to a peak and see a magnificent dragon!",
            "An avalanche blocks your path, but you find a secret tunnel.",
            "A mountain goat guides you to a hidden monastery.",
            "You discover ancient ruins with mysterious symbols."
        ]
        result = random.choice(challenges)
        print(f"Mountain: {result}")
        return result
    return "This path is not for you."
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit
from PySide6.QtCore import Qt

widgets['result_text'] = QTextEdit(parent)
widgets['result_text'].setMinimumHeight(120)
widgets['result_text'].setReadOnly(True)
widgets['result_text'].setPlainText('Waiting for mountain adventure...')
layout.addWidget(widgets['result_text'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    result = outputs.get('output_1', 'No result')
    widgets['result_text'].setPlainText(f'MOUNTAIN CHALLENGE:\n\n{result}')
```


## Node: Cave Exploration (ID: cave-encounter)

Executes cave-specific encounter logic when route input equals 'cave'. Uses random.choice() to select from four predefined mystery strings. Returns randomized exploration outcome string or default rejection message for non-cave routes.

Includes QTextEdit GUI component for displaying exploration results with read-only formatting. Updates display through set_values() function that formats output as "CAVE EXPLORATION:\n\n{result}". Mystery outcomes are randomly selected from predefined list on each execution.

### Metadata

```json
{
  "uuid": "cave-encounter",
  "title": "Cave Exploration",
  "pos": [
    1252.4701874999998,
    541.2549687499998
  ],
  "size": [
    276,
    310
  ],
  "colors": {
    "title": "#6f42c1",
    "body": "#563d7c"
  },
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def cave_adventure(route: str) -> str:
    if route == 'cave':
        import random
        mysteries = [
            "You find an underground lake with glowing fish!",
            "Ancient cave paintings tell the story of your quest.",
            "A sleeping dragon guards a pile of magical artifacts.",
            "Crystal formations create beautiful music in the wind."
        ]
        result = random.choice(mysteries)
        print(f"Cave: {result}")
        return result
    return "This path is not for you."
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit
from PySide6.QtCore import Qt

widgets['result_text'] = QTextEdit(parent)
widgets['result_text'].setMinimumHeight(120)
widgets['result_text'].setReadOnly(True)
widgets['result_text'].setPlainText('Waiting for cave exploration...')
layout.addWidget(widgets['result_text'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    result = outputs.get('output_1', 'No result')
    widgets['result_text'].setPlainText(f'CAVE EXPLORATION:\n\n{result}')
```


## Node: River Adventure (ID: river-encounter)

Executes river-specific encounter logic when route input equals 'river'. Uses random.choice() to select from four predefined adventure strings. Returns randomized water-based outcome string or default rejection message for non-river routes.

Includes QTextEdit GUI component for displaying adventure results with read-only formatting. Updates display through set_values() function that formats output as "RIVER ADVENTURE:\n\n{result}". Adventure outcomes are randomly selected from predefined list on each execution.

### Metadata

```json
{
  "uuid": "river-encounter",
  "title": "River Adventure",
  "pos": [
    1103.8046562500003,
    911.9364000000002
  ],
  "size": [
    276,
    310
  ],
  "colors": {
    "title": "#17a2b8",
    "body": "#117a8b"
  },
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def river_adventure(route: str) -> str:
    if route == 'river':
        import random
        adventures = [
            "A magical boat appears to ferry you across!",
            "Mermaids surface and offer you a quest.",
            "You spot a message in a bottle floating downstream.",
            "A wise old turtle shares secrets of the river."
        ]
        result = random.choice(adventures)
        print(f"River: {result}")
        return result
    return "This path is not for you."
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit
from PySide6.QtCore import Qt

widgets['result_text'] = QTextEdit(parent)
widgets['result_text'].setMinimumHeight(120)
widgets['result_text'].setReadOnly(True)
widgets['result_text'].setPlainText('Waiting for river adventure...')
layout.addWidget(widgets['result_text'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    result = outputs.get('output_1', 'No result')
    widgets['result_text'].setPlainText(f'RIVER ADVENTURE:\n\n{result}')
```


## Node: Adventure Complete (ID: game-end)

Finalizes the game session by taking adventure result string input and formatting it into completion message "Quest completed! {adventure_result}". Prints summary information to console and displays formatted results in QTextEdit GUI component.

Includes "Play Again" button for game restart functionality and displays completion message with additional narrative text. Serves as the terminal node for all adventure paths, consolidating various encounter outcomes into final game state.

### Metadata

```json
{
  "uuid": "game-end",
  "title": "Adventure Complete",
  "pos": [
    1834.3668375000002,
    -12.765474999999753
  ],
  "size": [
    276,
    372
  ],
  "colors": {
    "title": "#ffc107",
    "body": "#e0a800"
  },
  "gui_state": {}
}
```

### Logic

```python
@node_entry
def end_adventure(adventure_result: str) -> str:
    print("\n=== ADVENTURE COMPLETED ===")
    print(f"Your adventure: {adventure_result}")
    print("Thank you for playing!")
    return f"Quest completed! {adventure_result}"
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Adventure Summary', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['summary_text'] = QTextEdit(parent)
widgets['summary_text'].setMinimumHeight(150)
widgets['summary_text'].setReadOnly(True)
widgets['summary_text'].setPlainText('Complete your adventure to see the summary...')
layout.addWidget(widgets['summary_text'])

widgets['play_again_btn'] = QPushButton('Play Again', parent)
layout.addWidget(widgets['play_again_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    result = outputs.get('output_1', 'No result')
    widgets['summary_text'].setPlainText(f'{result}\n\nYour adventure has concluded. What path will you choose next time?')
```


## Connections

```json
[
  {
    "start_node_uuid": "game-start",
    "start_pin_name": "exec_out",
    "end_node_uuid": "player-choice",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "game-start",
    "start_pin_name": "output_1",
    "end_node_uuid": "player-choice",
    "end_pin_name": "welcome_msg"
  },
  {
    "start_node_uuid": "player-choice",
    "start_pin_name": "exec_out",
    "end_node_uuid": "condition-checker",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "player-choice",
    "start_pin_name": "output_1",
    "end_node_uuid": "condition-checker",
    "end_pin_name": "player_choice"
  },
  {
    "start_node_uuid": "condition-checker",
    "start_pin_name": "exec_out",
    "end_node_uuid": "forest-encounter",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "condition-checker",
    "start_pin_name": "exec_out",
    "end_node_uuid": "mountain-encounter",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "condition-checker",
    "start_pin_name": "exec_out",
    "end_node_uuid": "cave-encounter",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "condition-checker",
    "start_pin_name": "exec_out",
    "end_node_uuid": "river-encounter",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "condition-checker",
    "start_pin_name": "output_1",
    "end_node_uuid": "forest-encounter",
    "end_pin_name": "route"
  },
  {
    "start_node_uuid": "condition-checker",
    "start_pin_name": "output_1",
    "end_node_uuid": "mountain-encounter",
    "end_pin_name": "route"
  },
  {
    "start_node_uuid": "condition-checker",
    "start_pin_name": "output_1",
    "end_node_uuid": "cave-encounter",
    "end_pin_name": "route"
  },
  {
    "start_node_uuid": "condition-checker",
    "start_pin_name": "output_1",
    "end_node_uuid": "river-encounter",
    "end_pin_name": "route"
  },
  {
    "start_node_uuid": "forest-encounter",
    "start_pin_name": "exec_out",
    "end_node_uuid": "game-end",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "forest-encounter",
    "start_pin_name": "output_1",
    "end_node_uuid": "game-end",
    "end_pin_name": "adventure_result"
  }
]
```

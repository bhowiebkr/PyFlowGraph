# Procedural Sci-Fi World Generator

This flow graph procedurally generates a unique sci-fi world, from the galactic scale down to the details of a single planet's ecosystem and potential civilizations. The process is divided into several phases: Cosmological Setup, Stellar System Generation, Planetary Analysis, Biosphere Simulation, and Final Output. User interaction is enabled at key stages to guide the creation process.

## Node: Universe Seed (ID: universe-seed)

Initializes the random seed for the entire generation process, ensuring reproducibility. A user-provided string is converted into a numerical seed.

### Metadata

```json
{
  "uuid": "universe-seed",
  "title": "Universe Seed",
  "pos": [50, 50],
  "size": [300, 200],
  "colors": { "title": "#ffffff", "body": "#2c3e50" }
}
```

### Logic

```python
import hashlib

@node_entry
def generate_seed(seed_string: str) -> int:
    """Hashes a string to create a deterministic integer seed."""
    if not seed_string:
        seed_string = "default-seed"
    hashed = hashlib.sha256(seed_string.encode('utf-8')).hexdigest()
    return int(hashed, 16)
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

layout.addWidget(QLabel('Enter Universe Seed:', parent))
widgets['seed_input'] = QLineEdit(parent)
widgets['seed_input'].setPlaceholderText('e.g., Sol-System-Alpha')
layout.addWidget(widgets['seed_input'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {'seed_string': widgets['seed_input'].text()}
```

## Node: Galaxy Type Selector (ID: galaxy-type)

Defines the macro-structure of the galaxy. The type affects star density and distribution.

### Metadata

```json
{
  "uuid": "galaxy-type",
  "title": "Galaxy Type Selector",
  "pos": [400, 50],
  "size": [300, 200],
  "colors": { "title": "#ffffff", "body": "#34495e" }
}
```

### Logic

```python
@node_entry
def select_galaxy_type(galaxy_type: str) -> str:
    """Passes through the selected galaxy type."""
    return galaxy_type
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QComboBox

layout.addWidget(QLabel('Select Galaxy Type:', parent))
widgets['type_dropdown'] = QComboBox(parent)
widgets['type_dropdown'].addItems(['Spiral', 'Elliptical', 'Irregular'])
layout.addWidget(widgets['type_dropdown'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {'galaxy_type': widgets['type_dropdown'].currentText()}
```

## Node: Generate Star Field (ID: generate-stars)

Procedurally generates a large collection of stars based on the galaxy type and universe seed.

### Metadata

```json
{
  "uuid": "generate-stars",
  "title": "Generate Star Field",
  "pos": [750, 50],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#7f8c8d" }
}
```

### Logic

```python
import random

@node_entry
def generate_star_field(seed: int, galaxy_type: str) -> list:
    """Generates a list of star data dictionaries."""
    random.seed(seed)
    star_count = 1000 if galaxy_type == 'Spiral' else 500
    star_classes = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    stars = [{'id': i, 'class': random.choice(star_classes)} for i in range(star_count)]
    return stars
```

## Node: Star Class Filter (ID: star-class-filter)

Allows the user to filter the generated star field to focus on stars of a specific spectral class.

### Metadata

```json
{
  "uuid": "star-class-filter",
  "title": "Star Class Filter",
  "pos": [1080, 50],
  "size": [300, 200],
  "colors": { "title": "#f1c40f", "body": "#f39c12" }
}
```

### Logic

```python
@node_entry
def filter_stars_by_class(stars: list, star_class: str) -> list:
    """Filters the list of stars by the selected class."""
    return [s for s in stars if s['class'] == star_class]
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QComboBox

layout.addWidget(QLabel('Filter by Star Class:', parent))
widgets['class_dropdown'] = QComboBox(parent)
widgets['class_dropdown'].addItems(['G', 'K', 'M', 'F', 'A', 'B', 'O'])
layout.addWidget(widgets['class_dropdown'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {'star_class': widgets['class_dropdown'].currentText()}
```

## Node: Select Primary Star (ID: select-primary-star)

Selects a single star from the filtered list to be the center of the new solar system.

### Metadata

```json
{
  "uuid": "select-primary-star",
  "title": "Select Primary Star",
  "pos": [1430, 50],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#e67e22" }
}
```

### Logic

```python
import random

@node_entry
def select_primary_star(filtered_stars: list, seed: int) -> dict:
    """Selects one star from the list. Returns a default if list is empty."""
    if not filtered_stars:
        return {'id': -1, 'class': 'G', 'error': 'No stars of selected class found.'}
    random.seed(seed)
    return random.choice(filtered_stars)
```

## Node: Generate Planetary System (ID: generate-planets)

Generates a set of planets orbiting the primary star.

### Metadata

```json
{
  "uuid": "generate-planets",
  "title": "Generate Planetary System",
  "pos": [50, 350],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#2980b9" }
}
```

### Logic

```python
import random

@node_entry
def generate_planetary_system(primary_star: dict, seed: int) -> list:
    """Generates a list of planet data dictionaries."""
    random.seed(seed + primary_star.get('id', 0))
    planet_count = random.randint(2, 10)
    planet_types = ['Rocky', 'Gas Giant', 'Ice Giant', 'Dwarf']
    planets = [{'id': i, 'type': random.choice(planet_types), 'orbit': i+1} for i in range(planet_count)]
    return planets
```

## Node: Planet Type Classifier (ID: classify-planets)

A simple passthrough node that could be expanded to perform more detailed classification.

### Metadata

```json
{
  "uuid": "classify-planets",
  "title": "Planet Type Classifier",
  "pos": [380, 350],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#3498db" }
}
```

### Logic

```python
@node_entry
def classify_planets(planets: list) -> list:
    """In a real scenario, this would add more detail to each planet's type."""
    return planets
```

## Node: Select Target Planet (ID: select-target-planet)

Allows the user to select a specific planet from the generated system for detailed analysis.

### Metadata

```json
{
  "uuid": "select-target-planet",
  "title": "Select Target Planet",
  "pos": [710, 350],
  "size": [300, 250],
  "colors": { "title": "#ffffff", "body": "#8e44ad" }
}
```

### Logic

```python
@node_entry
def select_target_planet(planets: list, planet_id: int) -> dict:
    """Selects a planet by its ID from the list."""
    for p in planets:
        if p.get('id') == planet_id:
            return p
    return {'error': 'Planet not found.'}
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem

layout.addWidget(QLabel('Select a Planet to Analyze:', parent))
widgets['planet_list'] = QListWidget(parent)
layout.addWidget(widgets['planet_list'])
```

### GUI State Handler

```python
def get_values(widgets):
    selected_item = widgets['planet_list'].currentItem()
    return {'planet_id': selected_item.data(32) if selected_item else -1}

def set_values(widgets, inputs):
    planets = inputs.get('planets', [])
    widgets['planet_list'].clear()
    for p in planets:
        item = QListWidgetItem(f"Planet {p['id']} ({p['type']}) - Orbit {p['orbit']}")
        item.setData(32, p['id']) # Store planet ID in the item
        widgets['planet_list'].addItem(item)
```

## Node: Calculate Habitable Zone (ID: calc-habitable-zone)

Determines the "Goldilocks Zone" for the primary star where liquid water could exist.

### Metadata

```json
{
  "uuid": "calc-habitable-zone",
  "title": "Calculate Habitable Zone",
  "pos": [50, 650],
  "size": [280, 150],
  "colors": { "title": "#2ecc71", "body": "#27ae60" }
}
```

### Logic

```python
@node_entry
def calculate_habitable_zone(primary_star: dict) -> dict:
    """Calculates a simplified habitable zone based on star class."""
    star_class = primary_star.get('class', 'G')
    zones = {'G': [0.9, 1.5], 'K': [0.7, 1.2], 'M': [0.1, 0.4]}
    zone = zones.get(star_class, [0, 0])
    return {'inner_au': zone[0], 'outer_au': zone[1]}
```

## Node: Check Planet Position (ID: check-planet-position)

Checks if the target planet orbits within the calculated habitable zone.

### Metadata

```json
{
  "uuid": "check-planet-position",
  "title": "Check Planet Position",
  "pos": [380, 650],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#16a085" }
}
```

### Logic

```python
@node_entry
def check_planet_position(target_planet: dict, habitable_zone: dict) -> bool:
    """Checks if a planet's orbit is within the habitable zone."""
    orbit = target_planet.get('orbit', 0) # Simplified: orbit number as AU
    return habitable_zone['inner_au'] <= orbit <= habitable_zone['outer_au']
```

## Node: Generate Geology (ID: generate-geology)

Procedurally generates the geological features of the target planet.

### Metadata

```json
{
  "uuid": "generate-geology",
  "title": "Generate Geology",
  "pos": [710, 650],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#d35400" }
}
```

### Logic

```python
import random

@node_entry
def generate_geology(target_planet: dict, seed: int) -> str:
    """Generates a description of the planet's geology."""
    if target_planet.get('type') != 'Rocky':
        return "Not a rocky planet."
    random.seed(seed + target_planet.get('id', 0))
    features = ['High Tectonic Activity', 'Dormant Volcanoes', 'Rich in Heavy Metals', 'Silicate Plains']
    return random.choice(features)
```

## Node: Generate Atmosphere (ID: generate-atmosphere)

Generates atmospheric composition, with user-adjustable parameters.

### Metadata

```json
{
  "uuid": "generate-atmosphere",
  "title": "Generate Atmosphere",
  "pos": [1040, 650],
  "size": [300, 250],
  "colors": { "title": "#ffffff", "body": "#c0392b" }
}
```

### Logic

```python
@node_entry
def generate_atmosphere(is_habitable: bool, n2: int, o2: int, co2: int) -> dict:
    """Creates an atmosphere dictionary based on inputs."""
    if not is_habitable:
        return {'composition': 'None or Toxic'}
    total = n2 + o2 + co2
    if total == 0: return {'composition': 'Vacuum'}
    return {
        'composition': f"N2: {n2}%, O2: {o2}%, CO2: {co2}%",
        'is_breathable': o2 > 15 and o2 < 25
    }
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QSlider
from PySide6.QtCore import Qt

layout.addWidget(QLabel('Nitrogen (%):', parent))
widgets['n2_slider'] = QSlider(Qt.Horizontal, parent)
layout.addWidget(widgets['n2_slider'])

layout.addWidget(QLabel('Oxygen (%):', parent))
widgets['o2_slider'] = QSlider(Qt.Horizontal, parent)
layout.addWidget(widgets['o2_slider'])

layout.addWidget(QLabel('CO2 (%):', parent))
widgets['co2_slider'] = QSlider(Qt.Horizontal, parent)
layout.addWidget(widgets['co2_slider'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'n2': widgets['n2_slider'].value(),
        'o2': widgets['o2_slider'].value(),
        'co2': widgets['co2_slider'].value()
    }
```

## Node: Generate Hydrosphere (ID: generate-hydrosphere)

Determines the presence and coverage of liquid water.

### Metadata

```json
{
  "uuid": "generate-hydrosphere",
  "title": "Generate Hydrosphere",
  "pos": [1390, 650],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#2980b9" }
}
```

### Logic

```python
import random

@node_entry
def generate_hydrosphere(is_habitable: bool, seed: int) -> str:
    """Determines water coverage."""
    if not is_habitable:
        return "Frozen or nonexistent."
    random.seed(seed)
    coverage = random.randint(10, 90)
    return f"{coverage}% surface coverage (liquid)"
```

## Node: Life Probability Calculator (ID: life-probability)

Calculates the probability of life based on key environmental factors.

### Metadata

```json
{
  "uuid": "life-probability",
  "title": "Life Probability Calculator",
  "pos": [50, 950],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#1abc9c" }
}
```

### Logic

```python
@node_entry
def calculate_life_probability(is_habitable: bool, atmosphere: dict, hydrosphere: str) -> float:
    """Calculates a score for life probability."""
    score = 0.0
    if is_habitable: score += 0.5
    if atmosphere.get('is_breathable'): score += 0.3
    if 'liquid' in hydrosphere: score += 0.2
    return score
```

## Node: Genesis Chamber (ID: genesis-chamber)

If life is probable, this node allows the user to 'seed' the type of life.

### Metadata

```json
{
  "uuid": "genesis-chamber",
  "title": "Genesis Chamber",
  "pos": [380, 950],
  "size": [300, 200],
  "colors": { "title": "#9b59b6", "body": "#8e44ad" }
}
```

### Logic

```python
@node_entry
def seed_life(life_probability: float, life_base: str) -> str:
    """Determines the outcome of seeding life."""
    if life_probability < 0.5:
        return "Conditions too harsh; life fails to start."
    return f"Life successfully seeded. Primary biochemistry: {life_base}-based."
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QComboBox

layout.addWidget(QLabel('Select Life Base:', parent))
widgets['base_dropdown'] = QComboBox(parent)
widgets['base_dropdown'].addItems(['Carbon', 'Silicon'])
layout.addWidget(widgets['base_dropdown'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {'life_base': widgets['base_dropdown'].currentText()}
```

## Node: Simulate Evolution (ID: simulate-evolution)

A simplified simulation of biological evolution on the planet.

### Metadata

```json
{
  "uuid": "simulate-evolution",
  "title": "Simulate Evolution",
  "pos": [730, 950],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#27ae60" }
}
```

### Logic

```python
import random

@node_entry
def simulate_evolution(life_seed_result: str, seed: int) -> str:
    """Simulates a dominant life form."""
    if "fails" in life_seed_result:
        return "No dominant lifeforms."
    random.seed(seed)
    outcomes = ['Flora', 'Fauna', 'Fungoids', 'Crystalline Entities']
    return f"Dominant lifeform: {random.choice(outcomes)}"
```

## Node: Civilization Indexer (ID: civilization-indexer)

Checks for signs of intelligent life and assigns a Kardashev scale rating.

### Metadata

```json
{
  "uuid": "civilization-indexer",
  "title": "Civilization Indexer",
  "pos": [1060, 950],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#f39c12" }
}
```

### Logic

```python
import random

@node_entry
def index_civilization(evolution_result: str, seed: int) -> str:
    """Determines if a civilization has arisen."""
    if "No dominant" in evolution_result:
        return "No intelligent civilization."
    random.seed(seed)
    chance = random.random()
    if chance < 0.7:
        return "Pre-industrial civilization."
    elif chance < 0.95:
        return "Type I Civilization (Planetary)."
    else:
        return "Type II Civilization (Stellar)."
```

## Node: Data Aggregator (ID: data-aggregator)

Collects all the generated data into a single, comprehensive dictionary.

### Metadata

```json
{
  "uuid": "data-aggregator",
  "title": "Data Aggregator",
  "pos": [50, 1250],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#7f8c8d" }
}
```

### Logic

```python
@node_entry
def aggregate_data(**kwargs) -> dict:
    """Collects all keyword arguments into a single dictionary."""
    return kwargs
```

## Node: World Codex Display (ID: codex-display)

A final display node that presents the complete "codex" entry for the generated world.

### Metadata

```json
{
  "uuid": "codex-display",
  "title": "World Codex Display",
  "pos": [380, 1250],
  "size": [450, 400],
  "colors": { "title": "#ffffff", "body": "#34495e" }
}
```

### Logic

```python
@node_entry
def format_codex(aggregated_data: dict) -> str:
    """Formats the aggregated data into a readable string."""
    # This logic is handled by the GUI State Handler in this implementation
    return "Display handled by GUI."
```

### GUI Definition

```python
from PySide6.QtWidgets import QTextEdit, QLabel
from PySide6.QtGui import QFont

title_label = QLabel('World Codex Entry', parent)
title_font = QFont()
title_font.setPointSize(16)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['codex_output'] = QTextEdit(parent)
widgets['codex_output'].setReadOnly(True)
layout.addWidget(widgets['codex_output'])
```

### GUI State Handler

```python
def set_values(widgets, inputs):
    data = inputs.get('aggregated_data', {})
    codex_text = f"""
    **SYSTEM REPORT**
    --------------------
    **Primary Star:** {data.get('primary_star', {}).get('class', 'N/A')}-Class
    **Target Planet:** ID {data.get('target_planet', {}).get('id', 'N/A')} (Orbit {data.get('target_planet', {}).get('orbit', 'N/A')})
    **Planet Type:** {data.get('target_planet', {}).get('type', 'N/A')}

    **ENVIRONMENTAL ANALYSIS**
    --------------------
    **Habitable Zone:** {'Yes' if data.get('is_in_habitable_zone') else 'No'}
    **Geology:** {data.get('geology', 'N/A')}
    **Atmosphere:** {data.get('atmosphere', {}).get('composition', 'N/A')}
    **Hydrosphere:** {data.get('hydrosphere', 'N/A')}

    **BIOLOGICAL & CIVILIZATION REPORT**
    --------------------
    **Life Probability:** {data.get('life_probability', 0.0) * 100:.1f}%
    **Dominant Lifeform:** {data.get('evolution', 'N/A')}
    **Civilization Level:** {data.get('civilization', 'N/A')}
    """
    widgets['codex_output'].setPlainText(codex_text.strip())
```

## Node: Final Output (ID: final-output)

A simple terminal node to signify the end of the main data generation path.

### Metadata

```json
{
  "uuid": "final-output",
  "title": "Final Output",
  "pos": [880, 1250],
  "size": [280, 150],
  "colors": { "title": "#ffffff", "body": "#000000" }
}
```

### Logic

```python
@node_entry
def final_output(codex: str) -> None:
    """Prints the final codex to the console as well."""
    print("--- FINAL WORLD CODEX ---")
    print(codex)
    return None
```

## Connections

```json
[
  { "start_node_uuid": "universe-seed", "start_pin_name": "output_1", "end_node_uuid": "generate-stars", "end_pin_name": "seed" },
  { "start_node_uuid": "universe-seed", "start_pin_name": "output_1", "end_node_uuid": "select-primary-star", "end_pin_name": "seed" },
  { "start_node_uuid": "universe-seed", "start_pin_name": "output_1", "end_node_uuid": "generate-planets", "end_pin_name": "seed" },
  { "start_node_uuid": "universe-seed", "start_pin_name": "output_1", "end_node_uuid": "generate-geology", "end_pin_name": "seed" },
  { "start_node_uuid": "universe-seed", "start_pin_name": "output_1", "end_node_uuid": "generate-hydrosphere", "end_pin_name": "seed" },
  { "start_node_uuid": "universe-seed", "start_pin_name": "output_1", "end_node_uuid": "simulate-evolution", "end_pin_name": "seed" },
  { "start_node_uuid": "universe-seed", "start_pin_name": "output_1", "end_node_uuid": "civilization-indexer", "end_pin_name": "seed" },
  { "start_node_uuid": "galaxy-type", "start_pin_name": "output_1", "end_node_uuid": "generate-stars", "end_pin_name": "galaxy_type" },
  { "start_node_uuid": "generate-stars", "start_pin_name": "output_1", "end_node_uuid": "star-class-filter", "end_pin_name": "stars" },
  { "start_node_uuid": "star-class-filter", "start_pin_name": "output_1", "end_node_uuid": "select-primary-star", "end_pin_name": "filtered_stars" },
  { "start_node_uuid": "select-primary-star", "start_pin_name": "output_1", "end_node_uuid": "generate-planets", "end_pin_name": "primary_star" },
  { "start_node_uuid": "select-primary-star", "start_pin_name": "output_1", "end_node_uuid": "calc-habitable-zone", "end_pin_name": "primary_star" },
  { "start_node_uuid": "select-primary-star", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "primary_star" },
  { "start_node_uuid": "generate-planets", "start_pin_name": "output_1", "end_node_uuid": "classify-planets", "end_pin_name": "planets" },
  { "start_node_uuid": "classify-planets", "start_pin_name": "output_1", "end_node_uuid": "select-target-planet", "end_pin_name": "planets" },
  { "start_node_uuid": "select-target-planet", "start_pin_name": "output_1", "end_node_uuid": "check-planet-position", "end_pin_name": "target_planet" },
  { "start_node_uuid": "select-target-planet", "start_pin_name": "output_1", "end_node_uuid": "generate-geology", "end_pin_name": "target_planet" },
  { "start_node_uuid": "select-target-planet", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "target_planet" },
  { "start_node_uuid": "calc-habitable-zone", "start_pin_name": "output_1", "end_node_uuid": "check-planet-position", "end_pin_name": "habitable_zone" },
  { "start_node_uuid": "check-planet-position", "start_pin_name": "output_1", "end_node_uuid": "generate-atmosphere", "end_pin_name": "is_habitable" },
  { "start_node_uuid": "check-planet-position", "start_pin_name": "output_1", "end_node_uuid": "generate-hydrosphere", "end_pin_name": "is_habitable" },
  { "start_node_uuid": "check-planet-position", "start_pin_name": "output_1", "end_node_uuid": "life-probability", "end_pin_name": "is_habitable" },
  { "start_node_uuid": "check-planet-position", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "is_in_habitable_zone" },
  { "start_node_uuid": "generate-geology", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "geology" },
  { "start_node_uuid": "generate-atmosphere", "start_pin_name": "output_1", "end_node_uuid": "life-probability", "end_pin_name": "atmosphere" },
  { "start_node_uuid": "generate-atmosphere", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "atmosphere" },
  { "start_node_uuid": "generate-hydrosphere", "start_pin_name": "output_1", "end_node_uuid": "life-probability", "end_pin_name": "hydrosphere" },
  { "start_node_uuid": "generate-hydrosphere", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "hydrosphere" },
  { "start_node_uuid": "life-probability", "start_pin_name": "output_1", "end_node_uuid": "genesis-chamber", "end_pin_name": "life_probability" },
  { "start_node_uuid": "life-probability", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "life_probability" },
  { "start_node_uuid": "genesis-chamber", "start_pin_name": "output_1", "end_node_uuid": "simulate-evolution", "end_pin_name": "life_seed_result" },
  { "start_node_uuid": "simulate-evolution", "start_pin_name": "output_1", "end_node_uuid": "civilization-indexer", "end_pin_name": "evolution_result" },
  { "start_node_uuid": "simulate-evolution", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "evolution" },
  { "start_node_uuid": "civilization-indexer", "start_pin_name": "output_1", "end_node_uuid": "data-aggregator", "end_pin_name": "civilization" },
  { "start_node_uuid": "data-aggregator", "start_pin_name": "output_1", "end_node_uuid": "codex-display", "end_pin_name": "aggregated_data" },
  { "start_node_uuid": "codex-display", "start_pin_name": "output_1", "end_node_uuid": "final-output", "end_pin_name": "codex" }
]

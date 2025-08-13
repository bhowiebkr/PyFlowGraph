# Recipe Nutrition Calculator

Recipe nutrition analysis workflow with regex-based ingredient parsing, nutrition database lookup, macronutrient calculations, and formatted report generation. Implements text parsing with re.match(), dictionary-based food database, mathematical nutrition aggregation, and string formatting for professional dietary reports.

## Node: Recipe Input & Parser (ID: recipe-input)

Parses ingredient text using re.match() with pattern `([\\d.]+)\\s*([a-zA-Z]*)?\\s+(.+)` to extract quantity (float), unit (string), and ingredient name from lines. Handles missing quantities by defaulting to 1.0 item. Returns Tuple[str, int, List[Dict]] containing recipe name, servings count, and ingredient dictionaries.

Each ingredient dictionary contains 'name', 'quantity', 'unit', and 'original_line' fields. Processing uses string.split('\\n') for line separation and string.strip() for whitespace removal. GUI includes QSpinBox for servings (1-20 range) and QTextEdit for ingredient input with regex parsing on execution.

### Metadata

```json
{
  "uuid": "recipe-input",
  "title": "Recipe Input & Parser",
  "pos": [
    100.0,
    200.0
  ],
  "size": [
    276,
    512
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "recipe_name": "",
    "servings": 4,
    "ingredients_text": ""
  }
}
```

### Logic

```python
import re
from typing import List, Tuple, Dict

@node_entry
def parse_recipe(recipe_name: str, servings: int, ingredients_text: str) -> Tuple[str, int, List[Dict]]:
    # Parse ingredients from text
    ingredients = []
    lines = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
    
    for line in lines:
        # Try to extract quantity, unit, and ingredient name
        # Pattern: number unit ingredient (e.g., "2 cups flour")
        match = re.match(r'([\d.]+)\s*([a-zA-Z]*)?\s+(.+)', line)
        
        if match:
            quantity = float(match.group(1))
            unit = match.group(2) if match.group(2) else "item"
            name = match.group(3).strip()
        else:
            # If no quantity found, assume 1 item
            quantity = 1.0
            unit = "item"
            name = line
        
        ingredients.append({
            'name': name,
            'quantity': quantity,
            'unit': unit,
            'original_line': line
        })
    
    print(f"\n=== RECIPE PARSING ===")
    print(f"Recipe: {recipe_name}")
    print(f"Servings: {servings}")
    print(f"Parsed {len(ingredients)} ingredients:")
    for ing in ingredients:
        print(f"  - {ing['quantity']} {ing['unit']} {ing['name']}")
    
    return recipe_name, servings, ingredients
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QSpinBox, QTextEdit, QPushButton

layout.addWidget(QLabel('Recipe Name:', parent))
widgets['recipe_name'] = QLineEdit(parent)
widgets['recipe_name'].setPlaceholderText('Enter recipe name...')
layout.addWidget(widgets['recipe_name'])

layout.addWidget(QLabel('Number of Servings:', parent))
widgets['servings'] = QSpinBox(parent)
widgets['servings'].setRange(1, 20)
widgets['servings'].setValue(4)
layout.addWidget(widgets['servings'])

layout.addWidget(QLabel('Ingredients (one per line):', parent))
widgets['ingredients_text'] = QTextEdit(parent)
widgets['ingredients_text'].setMinimumHeight(150)
widgets['ingredients_text'].setPlaceholderText('Example:\n2 cups flour\n3 eggs\n1 cup milk\n1 tsp salt')
layout.addWidget(widgets['ingredients_text'])

widgets['parse_btn'] = QPushButton('Parse Recipe', parent)
layout.addWidget(widgets['parse_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'recipe_name': widgets['recipe_name'].text(),
        'servings': widgets['servings'].value(),
        'ingredients_text': widgets['ingredients_text'].toPlainText()
    }

def set_initial_state(widgets, state):
    widgets['recipe_name'].setText(state.get('recipe_name', ''))
    widgets['servings'].setValue(state.get('servings', 4))
    widgets['ingredients_text'].setPlainText(state.get('ingredients_text', ''))
```


## Node: Nutrition Database Lookup (ID: nutrition-database)

Matches ingredient names against hardcoded nutrition_db dictionary using string.lower() and substring matching. Database contains calories, protein, carbs, fat per 100g plus unit_conversion factors for common measurements. Implements unit conversion logic for cups, tablespoons, grams, kilograms, pounds, ounces with mathematical scaling.

Calculates nutrition values using factor = grams / 100 multiplication against database values. Returns enriched ingredient list with added 'matched_food', 'grams', 'calories', 'protein', 'carbs', 'fat' fields. Unknown ingredients receive zero nutrition values and 'Unknown' matched_food designation.

### Metadata

```json
{
  "uuid": "nutrition-database",
  "title": "Nutrition Database Lookup",
  "pos": [
    470.0,
    150.0
  ],
  "size": [
    250,
    68
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
from typing import List, Dict

@node_entry
def lookup_nutrition(ingredients: List[Dict]) -> List[Dict]:
    # Simplified nutrition database (calories per 100g/100ml/1 item)
    nutrition_db = {
        'flour': {'calories': 364, 'protein': 10.3, 'carbs': 76.3, 'fat': 1.0, 'unit_conversion': {'cup': 125}},
        'eggs': {'calories': 155, 'protein': 13.0, 'carbs': 1.1, 'fat': 11.0, 'unit_conversion': {'item': 50}},
        'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5.0, 'fat': 1.0, 'unit_conversion': {'cup': 240}},
        'butter': {'calories': 717, 'protein': 0.9, 'carbs': 0.1, 'fat': 81.0, 'unit_conversion': {'tbsp': 14, 'cup': 227}},
        'sugar': {'calories': 387, 'protein': 0, 'carbs': 100, 'fat': 0, 'unit_conversion': {'cup': 200, 'tbsp': 12}},
        'salt': {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'unit_conversion': {'tsp': 6}},
        'chicken breast': {'calories': 165, 'protein': 31.0, 'carbs': 0, 'fat': 3.6, 'unit_conversion': {'item': 200}},
        'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'unit_conversion': {'cup': 195}},
        'cheese': {'calories': 113, 'protein': 7.0, 'carbs': 1.0, 'fat': 9.0, 'unit_conversion': {'cup': 113}},
        'oil': {'calories': 884, 'protein': 0, 'carbs': 0, 'fat': 100, 'unit_conversion': {'tbsp': 14}},
        'bread': {'calories': 265, 'protein': 9.0, 'carbs': 49, 'fat': 3.2, 'unit_conversion': {'slice': 25}},
        'potato': {'calories': 77, 'protein': 2.0, 'carbs': 17, 'fat': 0.1, 'unit_conversion': {'item': 150}}
    }
    
    enriched_ingredients = []
    
    for ingredient in ingredients:
        name = ingredient['name'].lower()
        quantity = ingredient['quantity']
        unit = ingredient['unit'].lower()
        
        # Find matching nutrition data
        nutrition = None
        matched_name = None
        
        for db_name, db_nutrition in nutrition_db.items():
            if db_name in name or any(word in name for word in db_name.split()):
                nutrition = db_nutrition
                matched_name = db_name
                break
        
        if nutrition:
            # Convert to grams
            if unit in nutrition['unit_conversion']:
                grams = quantity * nutrition['unit_conversion'][unit]
            elif unit in ['g', 'gram', 'grams']:
                grams = quantity
            elif unit in ['kg', 'kilogram']:
                grams = quantity * 1000
            elif unit in ['lb', 'pound']:
                grams = quantity * 453.592
            elif unit in ['oz', 'ounce']:
                grams = quantity * 28.3495
            else:
                grams = quantity * 100  # Default assumption
            
            # Calculate nutrition per ingredient
            factor = grams / 100  # Nutrition data is per 100g
            
            enriched_ingredient = ingredient.copy()
            enriched_ingredient.update({
                'matched_food': matched_name,
                'grams': round(grams, 1),
                'calories': round(nutrition['calories'] * factor, 1),
                'protein': round(nutrition['protein'] * factor, 1),
                'carbs': round(nutrition['carbs'] * factor, 1),
                'fat': round(nutrition['fat'] * factor, 1)
            })
        else:
            # Unknown ingredient
            enriched_ingredient = ingredient.copy()
            enriched_ingredient.update({
                'matched_food': 'Unknown',
                'grams': 0,
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0
            })
        
        enriched_ingredients.append(enriched_ingredient)
    
    print(f"\n=== NUTRITION LOOKUP ===")
    for ing in enriched_ingredients:
        if ing['matched_food'] != 'Unknown':
            print(f"{ing['name']}: {ing['calories']} cal, {ing['protein']}g protein")
        else:
            print(f"{ing['name']}: No nutrition data found")
    
    return enriched_ingredients
```


## Node: Nutrition Calculator (ID: nutrition-calculator)

Aggregates nutrition values from enriched ingredients using sum() operations on calories, protein, carbs, fat, grams fields. Calculates per-serving values using division by servings count with round() for decimal precision. Implements macronutrient percentage calculations using 4 cal/g for protein and carbs, 9 cal/g for fat.

Returns Tuple[Dict, Dict, str] containing total nutrition dictionary, per-serving dictionary, and analysis string. Analysis includes calorie distribution percentages, meal classification based on per-serving calories (<200 light, <500 moderate, >500 hearty), and high protein/fat content flags (>=20g protein, >20g fat).

### Metadata

```json
{
  "uuid": "nutrition-calculator",
  "title": "Nutrition Calculator",
  "pos": [
    850.0,
    200.0
  ],
  "size": [
    250,
    168
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
from typing import List, Dict, Tuple

@node_entry
def calculate_nutrition(recipe_name: str, servings: int, ingredients: List[Dict]) -> Tuple[Dict, Dict, str]:
    # Calculate total nutrition
    total = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'grams': 0
    }
    
    for ingredient in ingredients:
        total['calories'] += ingredient.get('calories', 0)
        total['protein'] += ingredient.get('protein', 0)
        total['carbs'] += ingredient.get('carbs', 0)
        total['fat'] += ingredient.get('fat', 0)
        total['grams'] += ingredient.get('grams', 0)
    
    # Round totals
    for key in total:
        total[key] = round(total[key], 1)
    
    # Calculate per serving
    per_serving = {
        'calories': round(total['calories'] / servings, 1),
        'protein': round(total['protein'] / servings, 1),
        'carbs': round(total['carbs'] / servings, 1),
        'fat': round(total['fat'] / servings, 1),
        'grams': round(total['grams'] / servings, 1)
    }
    
    # Generate nutrition analysis
    analysis = f"Recipe: {recipe_name}\n"
    analysis += f"Total weight: {total['grams']}g\n"
    analysis += f"Servings: {servings}\n\n"
    
    # Calorie distribution
    if total['calories'] > 0:
        protein_cal = total['protein'] * 4
        carbs_cal = total['carbs'] * 4
        fat_cal = total['fat'] * 9
        
        protein_pct = round((protein_cal / total['calories']) * 100, 1)
        carbs_pct = round((carbs_cal / total['calories']) * 100, 1)
        fat_pct = round((fat_cal / total['calories']) * 100, 1)
        
        analysis += f"Macronutrient distribution:\n"
        analysis += f"Protein: {protein_pct}%, Carbs: {carbs_pct}%, Fat: {fat_pct}%\n\n"
    
    # Health assessment
    if per_serving['calories'] < 200:
        analysis += "Light meal/snack\n"
    elif per_serving['calories'] < 500:
        analysis += "Moderate meal\n"
    else:
        analysis += "Hearty meal\n"
    
    if per_serving['protein'] >= 20:
        analysis += "High protein content\n"
    
    if per_serving['fat'] > 20:
        analysis += "High fat content\n"
    
    print(f"\n=== NUTRITION CALCULATION ===")
    print(f"Total: {total['calories']} cal, {total['protein']}g protein")
    print(f"Per serving: {per_serving['calories']} cal, {per_serving['protein']}g protein")
    print(f"Analysis: {analysis}")
    
    return total, per_serving, analysis
```


## Node: Nutrition Report Generator (ID: nutrition-report)

Formats nutrition data into structured report using string concatenation with fixed-width formatting. Creates sections for recipe overview, ingredient breakdown, total nutrition, per-serving values, macronutrient percentages, and analysis text. Uses f-string formatting with width specifiers for column alignment (:8.1f for numeric fields).

Implements conditional display logic - only shows ingredient nutrition when matched_food != 'Unknown'. Calculates macronutrient percentages using protein*4 + carbs*4 + fat*9 calorie conversion. Report includes QTextEdit display with Courier New monospace font and action buttons for save/scale/new recipe functionality.

### Metadata

```json
{
  "uuid": "nutrition-report",
  "title": "Nutrition Report Generator",
  "pos": [
    1220.0,
    200.0
  ],
  "size": [
    276,
    623
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
from typing import Dict, List

@node_entry
def generate_nutrition_report(recipe_name: str, servings: int, ingredients: List[Dict], total_nutrition: Dict, per_serving: Dict, analysis: str) -> str:
    report = "\n" + "="*70 + "\n"
    report += "                    NUTRITION REPORT\n"
    report += "="*70 + "\n\n"
    
    # Recipe Overview
    report += f"🍽️  RECIPE: {recipe_name.upper()}\n"
    report += f"👥 Servings: {servings}\n"
    report += f"⚖️  Total Weight: {total_nutrition['grams']}g\n\n"
    
    # Ingredients List
    report += f"📋 INGREDIENTS\n"
    for i, ing in enumerate(ingredients, 1):
        if ing.get('matched_food', 'Unknown') != 'Unknown':
            report += f"   {i:2d}. {ing['original_line']}\n"
            report += f"       ({ing['grams']}g, {ing['calories']} cal, {ing['protein']}g protein)\n"
        else:
            report += f"   {i:2d}. {ing['original_line']} (nutrition data unavailable)\n"
    report += "\n"
    
    # Total Nutrition
    report += f"📊 TOTAL NUTRITION\n"
    report += f"   Calories:     {total_nutrition['calories']:8.1f} kcal\n"
    report += f"   Protein:      {total_nutrition['protein']:8.1f} g\n"
    report += f"   Carbohydrates:{total_nutrition['carbs']:8.1f} g\n"
    report += f"   Fat:          {total_nutrition['fat']:8.1f} g\n\n"
    
    # Per Serving
    report += f"🍽️  PER SERVING\n"
    report += f"   Calories:     {per_serving['calories']:8.1f} kcal\n"
    report += f"   Protein:      {per_serving['protein']:8.1f} g\n"
    report += f"   Carbohydrates:{per_serving['carbs']:8.1f} g\n"
    report += f"   Fat:          {per_serving['fat']:8.1f} g\n"
    report += f"   Weight:       {per_serving['grams']:8.1f} g\n\n"
    
    # Macronutrient Breakdown
    if total_nutrition['calories'] > 0:
        protein_cal = total_nutrition['protein'] * 4
        carbs_cal = total_nutrition['carbs'] * 4
        fat_cal = total_nutrition['fat'] * 9
        
        protein_pct = (protein_cal / total_nutrition['calories']) * 100
        carbs_pct = (carbs_cal / total_nutrition['calories']) * 100
        fat_pct = (fat_cal / total_nutrition['calories']) * 100
        
        report += f"📈 MACRONUTRIENT BREAKDOWN\n"
        report += f"   Protein:      {protein_pct:5.1f}% ({protein_cal:.0f} kcal)\n"
        report += f"   Carbohydrates:{carbs_pct:5.1f}% ({carbs_cal:.0f} kcal)\n"
        report += f"   Fat:          {fat_pct:5.1f}% ({fat_cal:.0f} kcal)\n\n"
    
    # Analysis
    report += f"💡 ANALYSIS\n"
    for line in analysis.split('\n'):
        if line.strip():
            report += f"   • {line.strip()}\n"
    
    report += "\n" + "="*70
    
    print(report)
    return report
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Nutrition Report', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['report_display'] = QTextEdit(parent)
widgets['report_display'].setMinimumHeight(250)
widgets['report_display'].setReadOnly(True)
widgets['report_display'].setPlainText('Enter recipe ingredients to generate nutrition report...')
font = QFont('Courier New', 9)
widgets['report_display'].setFont(font)
layout.addWidget(widgets['report_display'])

widgets['save_report_btn'] = QPushButton('Save Report', parent)
layout.addWidget(widgets['save_report_btn'])

widgets['scale_recipe_btn'] = QPushButton('Scale Recipe', parent)
layout.addWidget(widgets['scale_recipe_btn'])

widgets['new_recipe_btn'] = QPushButton('New Recipe', parent)
layout.addWidget(widgets['new_recipe_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    report = outputs.get('output_1', 'No report data')
    widgets['report_display'].setPlainText(report)
```


## Connections

```json
[
  {
    "start_node_uuid": "recipe-input",
    "start_pin_name": "output_1",
    "end_node_uuid": "nutrition-calculator",
    "end_pin_name": "recipe_name"
  },
  {
    "start_node_uuid": "recipe-input",
    "start_pin_name": "output_2",
    "end_node_uuid": "nutrition-calculator",
    "end_pin_name": "servings"
  },
  {
    "start_node_uuid": "nutrition-calculator",
    "start_pin_name": "exec_out",
    "end_node_uuid": "nutrition-report",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "recipe-input",
    "start_pin_name": "output_1",
    "end_node_uuid": "nutrition-report",
    "end_pin_name": "recipe_name"
  },
  {
    "start_node_uuid": "recipe-input",
    "start_pin_name": "output_2",
    "end_node_uuid": "nutrition-report",
    "end_pin_name": "servings"
  },
  {
    "start_node_uuid": "nutrition-calculator",
    "start_pin_name": "output_1",
    "end_node_uuid": "nutrition-report",
    "end_pin_name": "total_nutrition"
  },
  {
    "start_node_uuid": "nutrition-calculator",
    "start_pin_name": "output_2",
    "end_node_uuid": "nutrition-report",
    "end_pin_name": "per_serving"
  },
  {
    "start_node_uuid": "nutrition-calculator",
    "start_pin_name": "output_3",
    "end_node_uuid": "nutrition-report",
    "end_pin_name": "analysis"
  }
]
```

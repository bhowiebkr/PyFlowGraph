# Data Analysis Dashboard

A comprehensive data analysis and visualization system that demonstrates the complete lifecycle of data processing from generation through statistical analysis to presentation. This workflow showcases how different types of data (sales, weather, survey) can be dynamically generated, analyzed for statistical patterns and trends, and presented in a professional dashboard format.

The system emphasizes real-time analytics capabilities where users can adjust data parameters and immediately see the impact on statistical calculations, trend analysis, and correlation findings. Each component works together to create a complete business intelligence pipeline that transforms raw data into actionable insights through visual presentation and quantitative analysis.

## Node: Sample Data Generator (ID: data-generator)

Generates structured test datasets with configurable record counts (10-1000) and three predefined schemas: Sales (product, quantity, price, date), Weather (city, temperature, humidity, date), and Survey (age, satisfaction, category, score). Uses Python's random module to create realistic value distributions within appropriate ranges for each data type.

Implements domain-specific data generation logic with realistic constraints: sales prices between $50-2000, temperatures between -10°C to 40°C, satisfaction scores 1-10, and random date assignment within 2024. Returns List[Dict] where each dictionary represents a record with consistent field types and naming conventions.

The node serves as a data source for testing downstream analytics components without requiring external datasets. Output format is standardized with 'id' fields for record identification and consistent data types (int, float, str) suitable for statistical analysis and trend detection algorithms.

### Metadata

```json
{
  "uuid": "data-generator",
  "title": "Sample Data Generator",
  "pos": [
    100.0,
    200.0
  ],
  "size": [
    250,
    190
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "num_records": 100,
    "data_type": "Sales"
  }
}
```

### Logic

```python
import random
from typing import List, Dict

@node_entry
def generate_sample_data(num_records: int, data_type: str) -> List[Dict]:
    data = []
    
    if data_type == "Sales":
        products = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard", "Mouse"]
        for i in range(num_records):
            data.append({
                "id": i + 1,
                "product": random.choice(products),
                "quantity": random.randint(1, 10),
                "price": round(random.uniform(50, 2000), 2),
                "date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            })
    elif data_type == "Weather":
        cities = ["New York", "London", "Tokyo", "Sydney", "Paris", "Berlin"]
        for i in range(num_records):
            data.append({
                "id": i + 1,
                "city": random.choice(cities),
                "temperature": round(random.uniform(-10, 40), 1),
                "humidity": random.randint(30, 90),
                "date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            })
    else:  # Survey
        for i in range(num_records):
            data.append({
                "id": i + 1,
                "age": random.randint(18, 80),
                "satisfaction": random.randint(1, 10),
                "category": random.choice(["A", "B", "C"]),
                "score": round(random.uniform(0, 100), 1)
            })
    
    print(f"Generated {len(data)} {data_type.lower()} records")
    print(f"Sample record: {data[0] if data else 'None'}")
    return data
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QSpinBox, QComboBox, QPushButton

layout.addWidget(QLabel('Number of Records:', parent))
widgets['num_records'] = QSpinBox(parent)
widgets['num_records'].setRange(10, 1000)
widgets['num_records'].setValue(100)
layout.addWidget(widgets['num_records'])

layout.addWidget(QLabel('Data Type:', parent))
widgets['data_type'] = QComboBox(parent)
widgets['data_type'].addItems(['Sales', 'Weather', 'Survey'])
layout.addWidget(widgets['data_type'])

widgets['generate_btn'] = QPushButton('Generate Data', parent)
layout.addWidget(widgets['generate_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'num_records': widgets['num_records'].value(),
        'data_type': widgets['data_type'].currentText()
    }

def set_initial_state(widgets, state):
    widgets['num_records'].setValue(state.get('num_records', 100))
    widgets['data_type'].setCurrentText(state.get('data_type', 'Sales'))
```


## Node: Statistics Calculator (ID: statistics-calculator)

Performs statistical analysis on List[Dict] input by automatically detecting numeric fields (excluding 'id') and calculating mean, median, min, max, and standard deviation using Python's statistics module. Processes each numeric column independently and returns results as a dictionary with keys formatted as '{column}_{statistic}'.

Generates categorical data summaries by identifying string fields (excluding 'id' and 'date'), counting unique values per category, and creating frequency distributions. Handles variable data schemas dynamically without requiring predefined field specifications.

Returns three outputs: statistics dictionary with calculated metrics, total record count (int), and categorical summary string describing unique value counts. Designed to work with any tabular data structure and provides the statistical foundation for downstream trend analysis and dashboard display components.

### Metadata

```json
{
  "uuid": "statistics-calculator",
  "title": "Statistics Calculator",
  "pos": [
    450.0,
    100.0
  ],
  "size": [
    250,
    168
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
from typing import List, Dict, Tuple
import statistics

@node_entry
def calculate_statistics(data: List[Dict]) -> Tuple[Dict, int, str]:
    if not data:
        return {}, 0, "No data provided"
    
    stats = {}
    total_records = len(data)
    
    # Get numeric columns
    numeric_cols = []
    sample_record = data[0]
    for key, value in sample_record.items():
        if isinstance(value, (int, float)) and key != 'id':
            numeric_cols.append(key)
    
    # Calculate statistics for numeric columns
    for col in numeric_cols:
        values = [record[col] for record in data if isinstance(record[col], (int, float))]
        if values:
            stats[f"{col}_mean"] = round(statistics.mean(values), 2)
            stats[f"{col}_median"] = round(statistics.median(values), 2)
            stats[f"{col}_min"] = min(values)
            stats[f"{col}_max"] = max(values)
            if len(values) > 1:
                stats[f"{col}_stdev"] = round(statistics.stdev(values), 2)
    
    # Get categorical columns for summary
    categorical_summary = ""
    for key, value in sample_record.items():
        if isinstance(value, str) and key not in ['id', 'date']:
            unique_values = set(record[key] for record in data)
            categorical_summary += f"{key}: {len(unique_values)} unique values; "
    
    print("\n=== STATISTICAL ANALYSIS ===")
    print(f"Total records: {total_records}")
    for key, value in stats.items():
        print(f"{key}: {value}")
    if categorical_summary:
        print(f"Categorical data: {categorical_summary}")
    
    return stats, total_records, categorical_summary
```


## Node: Trend Analyzer (ID: trend-analyzer)

Analyzes temporal patterns by extracting YYYY-MM substrings from 'date' fields and counting record frequency per month using Counter. Creates categorical frequency distributions for string fields, returning the top 5 most common values for each category with their occurrence counts.

Implements basic correlation analysis between the first two numeric fields found in the dataset. Calculates covariance using standard formula: Σ(x-μx)(y-μy)/n, then determines relationship direction (positive/negative/neutral) based on covariance sign. Does not calculate correlation coefficients, only directional relationships.

Returns three outputs: trends dictionary containing monthly distributions, patterns dictionary with categorical frequency data, and correlations string describing numeric field relationships. Processing is conditional on data structure - temporal analysis requires 'date' fields, correlation analysis requires at least two numeric fields.

### Metadata

```json
{
  "uuid": "trend-analyzer",
  "title": "Trend Analyzer",
  "pos": [
    450.0,
    400.0
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
from collections import Counter

@node_entry
def analyze_trends(data: List[Dict]) -> Tuple[Dict, Dict, str]:
    if not data:
        return {}, {}, "No data to analyze"
    
    trends = {}
    patterns = {}
    
    # Date-based trends (if date field exists)
    if 'date' in data[0]:
        monthly_counts = Counter()
        for record in data:
            if 'date' in record:
                month = record['date'][:7]  # Extract YYYY-MM
                monthly_counts[month] += 1
        trends['monthly_distribution'] = dict(monthly_counts)
    
    # Categorical distributions
    for key, value in data[0].items():
        if isinstance(value, str) and key not in ['id', 'date']:
            distribution = Counter(record[key] for record in data)
            patterns[f"{key}_distribution"] = dict(distribution.most_common(5))
    
    # Correlation analysis for numeric fields
    numeric_fields = [k for k, v in data[0].items() 
                     if isinstance(v, (int, float)) and k != 'id']
    
    correlations = ""
    if len(numeric_fields) >= 2:
        # Simple correlation analysis
        field1, field2 = numeric_fields[0], numeric_fields[1]
        values1 = [record[field1] for record in data]
        values2 = [record[field2] for record in data]
        
        # Calculate basic correlation indicator
        avg1, avg2 = sum(values1)/len(values1), sum(values2)/len(values2)
        covariance = sum((x - avg1) * (y - avg2) for x, y in zip(values1, values2)) / len(values1)
        
        if covariance > 0:
            correlations = f"Positive relationship between {field1} and {field2}"
        elif covariance < 0:
            correlations = f"Negative relationship between {field1} and {field2}"
        else:
            correlations = f"No clear relationship between {field1} and {field2}"
    
    print("\n=== TREND ANALYSIS ===")
    print(f"Trends: {trends}")
    print(f"Patterns: {patterns}")
    print(f"Correlations: {correlations}")
    
    return trends, patterns, correlations
```


## Node: Analytics Dashboard (ID: dashboard-display)

Formats analytical results into a structured text report using string concatenation with emoji section headers and consistent indentation. Takes six inputs from upstream analysis nodes and combines them into a single formatted dashboard string with sections for overview, statistics, trends, patterns, and insights.

Handles variable data presence gracefully - only displays sections when corresponding data exists. Processes statistical dictionaries by replacing underscores with spaces and applying title case formatting. Limits trend displays to top 3 items and includes all pattern data with hierarchical indentation.

Outputs a single formatted string suitable for display in QTextEdit widgets. The report format is fixed-width text designed for monospace fonts, with consistent spacing and emoji-based visual organization. Includes integration points for export and refresh functionality through GUI action buttons.

### Metadata

```json
{
  "uuid": "dashboard-display",
  "title": "Analytics Dashboard",
  "pos": [
    850.0,
    250.0
  ],
  "size": [
    276,
    589
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
from typing import Dict

@node_entry
def create_dashboard(stats: Dict, record_count: int, categorical_info: str, trends: Dict, patterns: Dict, correlations: str) -> str:
    dashboard = "\n" + "="*50 + "\n"
    dashboard += "           ANALYTICS DASHBOARD\n"
    dashboard += "="*50 + "\n\n"
    
    # Overview section
    dashboard += f"📊 OVERVIEW\n"
    dashboard += f"   Total Records: {record_count:,}\n\n"
    
    # Statistics section
    if stats:
        dashboard += f"📈 STATISTICS\n"
        for key, value in stats.items():
            dashboard += f"   {key.replace('_', ' ').title()}: {value}\n"
        dashboard += "\n"
    
    # Trends section
    if trends:
        dashboard += f"📅 TRENDS\n"
        for key, value in trends.items():
            dashboard += f"   {key.replace('_', ' ').title()}:\n"
            if isinstance(value, dict):
                for k, v in list(value.items())[:3]:  # Show top 3
                    dashboard += f"     {k}: {v}\n"
        dashboard += "\n"
    
    # Patterns section
    if patterns:
        dashboard += f"🔍 PATTERNS\n"
        for key, value in patterns.items():
            dashboard += f"   {key.replace('_', ' ').title()}:\n"
            for k, v in value.items():
                dashboard += f"     {k}: {v}\n"
        dashboard += "\n"
    
    # Insights section
    if correlations:
        dashboard += f"💡 INSIGHTS\n"
        dashboard += f"   {correlations}\n\n"
    
    if categorical_info:
        dashboard += f"📋 CATEGORICAL DATA\n"
        dashboard += f"   {categorical_info}\n\n"
    
    dashboard += "="*50
    
    print(dashboard)
    return dashboard
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Analytics Dashboard', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['dashboard_display'] = QTextEdit(parent)
widgets['dashboard_display'].setMinimumHeight(250)
widgets['dashboard_display'].setReadOnly(True)
widgets['dashboard_display'].setPlainText('Generate data and run analysis to see dashboard...')
font = QFont('Courier New', 9)
widgets['dashboard_display'].setFont(font)
layout.addWidget(widgets['dashboard_display'])

widgets['export_btn'] = QPushButton('Export Report', parent)
layout.addWidget(widgets['export_btn'])

widgets['refresh_btn'] = QPushButton('Refresh Analysis', parent)
layout.addWidget(widgets['refresh_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    dashboard = outputs.get('output_1', 'No dashboard data')
    widgets['dashboard_display'].setPlainText(dashboard)
```


## Connections

```json
[
  {
    "start_node_uuid": "statistics-calculator",
    "start_pin_name": "exec_out",
    "end_node_uuid": "dashboard-display",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "statistics-calculator",
    "start_pin_name": "output_1",
    "end_node_uuid": "dashboard-display",
    "end_pin_name": "stats"
  },
  {
    "start_node_uuid": "statistics-calculator",
    "start_pin_name": "output_2",
    "end_node_uuid": "dashboard-display",
    "end_pin_name": "record_count"
  },
  {
    "start_node_uuid": "statistics-calculator",
    "start_pin_name": "output_3",
    "end_node_uuid": "dashboard-display",
    "end_pin_name": "categorical_info"
  },
  {
    "start_node_uuid": "trend-analyzer",
    "start_pin_name": "output_1",
    "end_node_uuid": "dashboard-display",
    "end_pin_name": "trends"
  },
  {
    "start_node_uuid": "trend-analyzer",
    "start_pin_name": "output_2",
    "end_node_uuid": "dashboard-display",
    "end_pin_name": "patterns"
  },
  {
    "start_node_uuid": "trend-analyzer",
    "start_pin_name": "output_3",
    "end_node_uuid": "dashboard-display",
    "end_pin_name": "correlations"
  }
]
```

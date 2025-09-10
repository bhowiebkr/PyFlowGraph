# Weather Data Processor

Weather data simulation and analysis workflow with seasonal parameter modeling, statistical calculations, trend detection algorithms, and formatted report generation. Implements random.uniform() data generation, statistics module calculations, Counter frequency analysis, and datetime-based time series processing.

## Node: Weather Data Simulator (ID: weather-simulator)

Generates weather data using random.uniform() with seasonal temperature ranges, datetime.timedelta() for date sequences, and conditional logic for weather patterns. Uses dictionary lookup for season-based temperature ranges: Spring (10-20°C), Summer (20-35°C), Fall (5-18°C), Winter (-5-10°C). Applies random.randint() for humidity and precipitation probability calculations.

Implements condition classification using if-elif logic based on precipitation thresholds, temperature ranges, and humidity levels. Returns Tuple[str, List[Dict]] containing city name and weather data list. Each dictionary includes date, temperature, humidity, wind_speed, precipitation, condition, and day_of_week fields generated using datetime.strftime() formatting.

### Metadata

```json
{
  "uuid": "weather-simulator",
  "title": "Weather Data Simulator",
  "pos": [
    100.0,
    200.0
  ],
  "size": [
    250,
    342
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "city": "New York",
    "days": 30,
    "season": "Spring"
  }
}
```

### Logic

```python
import random
import datetime
from typing import List, Dict, Tuple

@node_entry
def simulate_weather_data(city: str, days: int, season: str) -> Tuple[str, List[Dict]]:
    """
    Simulate weather data for specified parameters.
    @outputs: city, weather_data
    """
    # Temperature ranges by season (Celsius)
    temp_ranges = {
        'Spring': (10, 20),
        'Summer': (20, 35),
        'Fall': (5, 18),
        'Winter': (-5, 10)
    }
    
    base_temp_range = temp_ranges.get(season, (10, 25))
    
    weather_data = []
    current_date = datetime.datetime.now()
    
    for i in range(days):
        date = current_date + datetime.timedelta(days=i)
        
        # Generate realistic weather patterns
        base_temp = random.uniform(base_temp_range[0], base_temp_range[1])
        temp_variation = random.uniform(-3, 3)  # Daily variation
        temperature = round(base_temp + temp_variation, 1)
        
        # Humidity tends to be higher in summer and with rain
        base_humidity = 60 if season == 'Summer' else 70
        humidity = max(30, min(95, base_humidity + random.randint(-20, 20)))
        
        # Wind speed
        wind_speed = round(random.uniform(5, 25), 1)
        
        # Precipitation (higher chance in fall/winter)
        precip_chance = 0.4 if season in ['Fall', 'Winter'] else 0.2
        precipitation = round(random.uniform(0, 15), 1) if random.random() < precip_chance else 0
        
        # Weather conditions
        if precipitation > 10:
            condition = 'Heavy Rain'
        elif precipitation > 2:
            condition = 'Light Rain'
        elif humidity > 85:
            condition = 'Cloudy'
        elif temperature > 28:
            condition = 'Hot'
        elif temperature < 5:
            condition = 'Cold'
        else:
            condition = 'Clear'
        
        weather_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'precipitation': precipitation,
            'condition': condition,
            'day_of_week': date.strftime('%A')
        })
    
    print(f"\n=== WEATHER SIMULATION ===")
    print(f"City: {city}")
    print(f"Season: {season}")
    print(f"Generated {len(weather_data)} days of data")
    print(f"Date range: {weather_data[0]['date']} to {weather_data[-1]['date']}")
    
    return city, weather_data
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QSpinBox, QComboBox, QPushButton

layout.addWidget(QLabel('City:', parent))
widgets['city'] = QLineEdit(parent)
widgets['city'].setPlaceholderText('Enter city name...')
widgets['city'].setText('New York')
layout.addWidget(widgets['city'])

layout.addWidget(QLabel('Number of Days:', parent))
widgets['days'] = QSpinBox(parent)
widgets['days'].setRange(7, 365)
widgets['days'].setValue(30)
layout.addWidget(widgets['days'])

layout.addWidget(QLabel('Season:', parent))
widgets['season'] = QComboBox(parent)
widgets['season'].addItems(['Spring', 'Summer', 'Fall', 'Winter'])
layout.addWidget(widgets['season'])

widgets['simulate_btn'] = QPushButton('Generate Weather Data', parent)
layout.addWidget(widgets['simulate_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'city': widgets['city'].text(),
        'days': widgets['days'].value(),
        'season': widgets['season'].currentText()
    }

def set_initial_state(widgets, state):
    widgets['city'].setText(state.get('city', 'New York'))
    widgets['days'].setValue(state.get('days', 30))
    widgets['season'].setCurrentText(state.get('season', 'Spring'))
```


## Node: Weather Statistics Analyzer (ID: weather-analyzer)

Calculates weather statistics using statistics.mean(), statistics.median(), min(), max(), and statistics.stdev() on temperature lists. Implements Counter for weather condition frequency analysis and list comprehensions for data extraction. Uses max() and min() with key lambda functions to identify extreme weather days.

Returns Tuple[Dict, Dict, Dict] containing temperature statistics, condition counts, and environmental statistics. Environmental analysis includes avg_humidity, avg_wind, total_precipitation using sum(), rainy day counting with conditional list comprehension, and extreme day identification through key-based sorting.

### Metadata

```json
{
  "uuid": "weather-analyzer",
  "title": "Weather Statistics Analyzer",
  "pos": [
    470.0,
    150.0
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
from collections import Counter
import statistics

@node_entry
def analyze_weather(weather_data: List[Dict]) -> Tuple[Dict, Dict, Dict]:
    """
    Analyze weather statistics and patterns.
    @outputs: temp_stats, conditions, env_stats
    """
    if not weather_data:
        return {}, {}, {}
    
    # Temperature statistics
    temperatures = [day['temperature'] for day in weather_data]
    temp_stats = {
        'avg': round(statistics.mean(temperatures), 1),
        'min': min(temperatures),
        'max': max(temperatures),
        'median': round(statistics.median(temperatures), 1)
    }
    
    if len(temperatures) > 1:
        temp_stats['std_dev'] = round(statistics.stdev(temperatures), 1)
    
    # Weather conditions analysis
    conditions = [day['condition'] for day in weather_data]
    condition_counts = Counter(conditions)
    
    # Environmental analysis
    humidity_vals = [day['humidity'] for day in weather_data]
    wind_vals = [day['wind_speed'] for day in weather_data]
    precip_vals = [day['precipitation'] for day in weather_data]
    
    env_stats = {
        'avg_humidity': round(statistics.mean(humidity_vals), 1),
        'avg_wind': round(statistics.mean(wind_vals), 1),
        'total_precipitation': round(sum(precip_vals), 1),
        'rainy_days': len([p for p in precip_vals if p > 0]),
        'hottest_day': max(weather_data, key=lambda x: x['temperature']),
        'coldest_day': min(weather_data, key=lambda x: x['temperature']),
        'windiest_day': max(weather_data, key=lambda x: x['wind_speed'])
    }
    
    print(f"\n=== WEATHER ANALYSIS ===")
    print(f"Temperature: {temp_stats['min']}°C to {temp_stats['max']}°C (avg: {temp_stats['avg']}°C)")
    print(f"Most common condition: {condition_counts.most_common(1)[0][0]}")
    print(f"Rainy days: {env_stats['rainy_days']}/{len(weather_data)}")
    
    return temp_stats, dict(condition_counts), env_stats
```


## Node: Weather Trend Detector (ID: trend-detector)

Detects weather trends using list slicing for early/late period comparison, calculates temperature averages with sum() and len(), and identifies trends with +/-2°C thresholds. Analyzes precipitation patterns using total rainfall calculations and rainy day percentage thresholds (>3mm/day = wet, <20% rainy days = dry).

Implements consecutive pattern detection using loops with counter variables for hot streaks (>25°C), cold streaks (<10°C), and rain streaks (>1mm). Compares weekend vs weekday temperatures using list comprehensions with day_of_week filtering. Returns Tuple[str, str, List[str]] containing temperature trend, precipitation pattern, and insights list.

### Metadata

```json
{
  "uuid": "trend-detector",
  "title": "Weather Trend Detector",
  "pos": [
    470.0,
    450.0
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
def detect_trends(weather_data: List[Dict]) -> Tuple[str, str, List[str]]:
    """
    Detect weather trends and patterns.
    @outputs: temp_trend, precip_pattern, insights
    """
    if len(weather_data) < 3:
        return "Insufficient data", "No patterns", []
    
    temperatures = [day['temperature'] for day in weather_data]
    precip_values = [day['precipitation'] for day in weather_data]
    
    # Temperature trend analysis
    temp_trend = "Stable"
    if len(temperatures) >= 5:
        early_avg = sum(temperatures[:len(temperatures)//3]) / (len(temperatures)//3)
        late_avg = sum(temperatures[-len(temperatures)//3:]) / (len(temperatures)//3)
        
        if late_avg > early_avg + 2:
            temp_trend = "Warming"
        elif late_avg < early_avg - 2:
            temp_trend = "Cooling"
    
    # Precipitation pattern
    total_precip = sum(precip_values)
    rainy_days = len([p for p in precip_values if p > 0])
    
    if total_precip > len(weather_data) * 3:  # More than 3mm per day on average
        precip_pattern = "Wet period"
    elif rainy_days < len(weather_data) * 0.2:  # Less than 20% rainy days
        precip_pattern = "Dry period"
    else:
        precip_pattern = "Normal precipitation"
    
    # Weather insights
    insights = []
    
    # Temperature extremes
    max_temp = max(temperatures)
    min_temp = min(temperatures)
    if max_temp - min_temp > 20:
        insights.append(f"High temperature variability ({max_temp - min_temp:.1f}°C range)")
    
    # Consecutive patterns
    hot_streak = 0
    cold_streak = 0
    rain_streak = 0
    current_hot = 0
    current_cold = 0
    current_rain = 0
    
    for day in weather_data:
        if day['temperature'] > 25:
            current_hot += 1
            current_cold = 0
        elif day['temperature'] < 10:
            current_cold += 1
            current_hot = 0
        else:
            current_hot = 0
            current_cold = 0
        
        if day['precipitation'] > 1:
            current_rain += 1
        else:
            current_rain = 0
        
        hot_streak = max(hot_streak, current_hot)
        cold_streak = max(cold_streak, current_cold)
        rain_streak = max(rain_streak, current_rain)
    
    if hot_streak >= 3:
        insights.append(f"Heat wave detected ({hot_streak} consecutive hot days)")
    
    if cold_streak >= 3:
        insights.append(f"Cold snap detected ({cold_streak} consecutive cold days)")
    
    if rain_streak >= 3:
        insights.append(f"Rainy period detected ({rain_streak} consecutive rainy days)")
    
    # Weekly patterns
    weekend_temps = [day['temperature'] for day in weather_data if day['day_of_week'] in ['Saturday', 'Sunday']]
    weekday_temps = [day['temperature'] for day in weather_data if day['day_of_week'] not in ['Saturday', 'Sunday']]
    
    if weekend_temps and weekday_temps:
        weekend_avg = sum(weekend_temps) / len(weekend_temps)
        weekday_avg = sum(weekday_temps) / len(weekday_temps)
        
        if abs(weekend_avg - weekday_avg) > 3:
            insights.append(f"Weekend/weekday temperature difference: {abs(weekend_avg - weekday_avg):.1f}°C")
    
    print(f"\n=== TREND DETECTION ===")
    print(f"Temperature trend: {temp_trend}")
    print(f"Precipitation pattern: {precip_pattern}")
    print(f"Insights: {len(insights)} patterns detected")
    
    return temp_trend, precip_pattern, insights
```


## Node: Weather Report Generator (ID: weather-report)

Formats comprehensive weather report using string concatenation with f-string formatting and fixed-width column alignment. Combines statistical data, trend analysis, and weather insights into structured sections. Uses sum() for total calculations, sorted() with key functions for condition ranking, and percentage calculations for weather distributions.

Implements conditional formatting for displaying statistics, creates recent weather displays using list slicing [-5:], and formats extreme weather events with dictionary access. Returns single formatted report string for QTextEdit display with Courier New monospace font and professional layout structure including headers, statistics, and event summaries.

### Metadata

```json
{
  "uuid": "weather-report",
  "title": "Weather Report Generator",
  "pos": [
    850.0,
    300.0
  ],
  "size": [
    276,
    673
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
from typing import List, Dict

@node_entry
def generate_weather_report(city: str, weather_data: List[Dict], temp_stats: Dict, conditions: Dict, env_stats: Dict, temp_trend: str, precip_pattern: str, insights: List[str]) -> str:
    """
    Generate comprehensive weather report.
    @outputs: report
    """
    if not weather_data:
        return "No weather data available"
    
    report = "\n" + "="*70 + "\n"
    report += "                    WEATHER ANALYSIS REPORT\n"
    report += "="*70 + "\n\n"
    
    # Location and Period
    report += f"🌍 LOCATION: {city.upper()}\n"
    report += f"📅 PERIOD: {weather_data[0]['date']} to {weather_data[-1]['date']}\n"
    report += f"📊 DATASET: {len(weather_data)} days\n\n"
    
    # Temperature Summary
    if temp_stats:
        report += f"🌡️  TEMPERATURE ANALYSIS\n"
        report += f"   Average:        {temp_stats['avg']:6.1f}°C\n"
        report += f"   Range:          {temp_stats['min']:6.1f}°C to {temp_stats['max']:6.1f}°C\n"
        report += f"   Median:         {temp_stats['median']:6.1f}°C\n"
        if 'std_dev' in temp_stats:
            report += f"   Variation:      {temp_stats['std_dev']:6.1f}°C std dev\n"
        report += f"   Trend:          {temp_trend}\n\n"
    
    # Environmental Conditions
    if env_stats:
        report += f"🌦️  ENVIRONMENTAL CONDITIONS\n"
        report += f"   Avg Humidity:   {env_stats['avg_humidity']:6.1f}%\n"
        report += f"   Avg Wind Speed: {env_stats['avg_wind']:6.1f} km/h\n"
        report += f"   Total Rainfall: {env_stats['total_precipitation']:6.1f} mm\n"
        report += f"   Rainy Days:     {env_stats['rainy_days']:6d} days\n"
        report += f"   Pattern:        {precip_pattern}\n\n"
    
    # Weather Conditions Distribution
    if conditions:
        report += f"☁️  WEATHER CONDITIONS\n"
        total_days = sum(conditions.values())
        for condition, count in sorted(conditions.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_days) * 100
            report += f"   {condition:<12} {count:3d} days ({percentage:4.1f}%)\n"
        report += "\n"
    
    # Notable Weather Events
    if env_stats:
        report += f"📋 NOTABLE EVENTS\n"
        hottest = env_stats.get('hottest_day', {})
        coldest = env_stats.get('coldest_day', {})
        windiest = env_stats.get('windiest_day', {})
        
        if hottest:
            report += f"   Hottest Day:    {hottest['date']} ({hottest['temperature']}°C)\n"
        if coldest:
            report += f"   Coldest Day:    {coldest['date']} ({coldest['temperature']}°C)\n"
        if windiest:
            report += f"   Windiest Day:   {windiest['date']} ({windiest['wind_speed']} km/h)\n"
        report += "\n"
    
    # Weather Patterns & Insights
    if insights:
        report += f"🔍 WEATHER PATTERNS\n"
        for insight in insights:
            report += f"   • {insight}\n"
        report += "\n"
    
    # Recent Weather (last 5 days)
    report += f"📅 RECENT WEATHER (Last 5 Days)\n"
    recent_days = weather_data[-5:] if len(weather_data) >= 5 else weather_data
    for day in recent_days:
        report += f"   {day['date']} {day['temperature']:4.1f}°C {day['condition']:<12} "
        if day['precipitation'] > 0:
            report += f"({day['precipitation']}mm rain)\n"
        else:
            report += "\n"
    
    report += "\n" + "="*70
    
    print(report)
    return report
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Weather Analysis Report', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['report_display'] = QTextEdit(parent)
widgets['report_display'].setMinimumHeight(250)
widgets['report_display'].setReadOnly(True)
widgets['report_display'].setPlainText('Generate weather data to see analysis report...')
font = QFont('Courier New', 9)
widgets['report_display'].setFont(font)
layout.addWidget(widgets['report_display'])

widgets['export_csv_btn'] = QPushButton('Export Data as CSV', parent)
layout.addWidget(widgets['export_csv_btn'])

widgets['compare_btn'] = QPushButton('Compare with Other Cities', parent)
layout.addWidget(widgets['compare_btn'])

widgets['forecast_btn'] = QPushButton('Generate Forecast', parent)
layout.addWidget(widgets['forecast_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    report = outputs.get('report', 'No report data')
    widgets['report_display'].setPlainText(report)
```


## Connections

```json
[
  {
    "start_node_uuid": "weather-simulator",
    "start_pin_name": "exec_out",
    "end_node_uuid": "weather-analyzer",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "weather-simulator",
    "start_pin_name": "weather_data",
    "end_node_uuid": "weather-analyzer",
    "end_pin_name": "weather_data"
  },
  {
    "start_node_uuid": "weather-simulator",
    "start_pin_name": "exec_out",
    "end_node_uuid": "trend-detector",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "weather-simulator",
    "start_pin_name": "weather_data",
    "end_node_uuid": "trend-detector",
    "end_pin_name": "weather_data"
  },
  {
    "start_node_uuid": "weather-analyzer",
    "start_pin_name": "exec_out",
    "end_node_uuid": "weather-report",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "weather-simulator",
    "start_pin_name": "city",
    "end_node_uuid": "weather-report",
    "end_pin_name": "city"
  },
  {
    "start_node_uuid": "weather-simulator",
    "start_pin_name": "weather_data",
    "end_node_uuid": "weather-report",
    "end_pin_name": "weather_data"
  },
  {
    "start_node_uuid": "weather-analyzer",
    "start_pin_name": "temp_stats",
    "end_node_uuid": "weather-report",
    "end_pin_name": "temp_stats"
  },
  {
    "start_node_uuid": "weather-analyzer",
    "start_pin_name": "conditions",
    "end_node_uuid": "weather-report",
    "end_pin_name": "conditions"
  },
  {
    "start_node_uuid": "weather-analyzer",
    "start_pin_name": "env_stats",
    "end_node_uuid": "weather-report",
    "end_pin_name": "env_stats"
  },
  {
    "start_node_uuid": "trend-detector",
    "start_pin_name": "temp_trend",
    "end_node_uuid": "weather-report",
    "end_pin_name": "temp_trend"
  },
  {
    "start_node_uuid": "trend-detector",
    "start_pin_name": "precip_pattern",
    "end_node_uuid": "weather-report",
    "end_pin_name": "precip_pattern"
  },
  {
    "start_node_uuid": "trend-detector",
    "start_pin_name": "insights",
    "end_node_uuid": "weather-report",
    "end_pin_name": "insights"
  }
]
```

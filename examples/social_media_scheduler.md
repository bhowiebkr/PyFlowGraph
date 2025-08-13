# Social Media Scheduler

Social media content management workflow with platform-specific character limits, engagement scoring algorithms, datetime scheduling validation, and dashboard report generation. Implements string length checking, regex pattern matching, datetime.strptime() parsing, and formatted text output for multi-platform posting optimization.

## Node: Content Creator & Editor (ID: content-creator)

Processes social media content with platform-specific character limits: Twitter 280, Instagram 2200, LinkedIn 3000 characters. Uses string.split(',') to parse hashtags, adds '#' prefix if missing, limits to 10 hashtags using slice [:10]. Implements string truncation with [...3] + "..." for content overflow.

Validates schedule time using datetime.strptime() with "%Y-%m-%d %H:%M" format. Returns Tuple[str, str, str, str, str] containing final_content, platform, content_type, hashtag_text, schedule_status. GUI includes QComboBox for platform/type selection, QTextEdit for content, QLineEdit for hashtags and scheduling.

### Metadata

```json
{
  "uuid": "content-creator",
  "title": "Content Creator & Editor",
  "pos": [
    -0.37774999999993497,
    200.00000000000003
  ],
  "size": [
    276,
    664
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "content_text": "",
    "platform": "Twitter",
    "content_type": "Post",
    "hashtags": "",
    "schedule_time": ""
  }
}
```

### Logic

```python
import datetime
from typing import Tuple

@node_entry
def create_content(content_text: str, platform: str, content_type: str, hashtags: str, schedule_time: str) -> Tuple[str, str, str, str, str]:
    # Process hashtags
    processed_hashtags = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
    if not any(tag.startswith('#') for tag in processed_hashtags):
        processed_hashtags = ['#' + tag for tag in processed_hashtags]
    hashtag_text = ' '.join(processed_hashtags[:10])  # Limit to 10 hashtags
    
    # Optimize content for platform
    if platform == "Twitter":
        max_length = 280 - len(hashtag_text) - 1
        if len(content_text) > max_length:
            content_text = content_text[:max_length-3] + "..."
    elif platform == "Instagram":
        max_length = 2200
        if len(content_text) > max_length:
            content_text = content_text[:max_length-3] + "..."
    elif platform == "LinkedIn":
        max_length = 3000
        if len(content_text) > max_length:
            content_text = content_text[:max_length-3] + "..."
    
    # Combine content with hashtags
    final_content = f"{content_text}\n\n{hashtag_text}" if hashtag_text else content_text
    
    # Validate schedule time
    try:
        datetime.datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
        schedule_status = "Valid"
    except:
        schedule_status = "Invalid format (use YYYY-MM-DD HH:MM)"
    
    print(f"Content created for {platform}")
    print(f"Type: {content_type}")
    print(f"Length: {len(final_content)} characters")
    print(f"Hashtags: {len(processed_hashtags)}")
    print(f"Schedule: {schedule_time} ({schedule_status})")
    
    return final_content, platform, content_type, hashtag_text, schedule_status
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QComboBox, QLineEdit, QPushButton, QDateTimeEdit
from PySide6.QtCore import QDateTime

layout.addWidget(QLabel('Platform:', parent))
widgets['platform'] = QComboBox(parent)
widgets['platform'].addItems(['Twitter', 'Instagram', 'LinkedIn', 'Facebook'])
layout.addWidget(widgets['platform'])

layout.addWidget(QLabel('Content Type:', parent))
widgets['content_type'] = QComboBox(parent)
widgets['content_type'].addItems(['Post', 'Story', 'Article', 'Promotion', 'Update'])
layout.addWidget(widgets['content_type'])

layout.addWidget(QLabel('Content:', parent))
widgets['content_text'] = QTextEdit(parent)
widgets['content_text'].setMinimumHeight(100)
widgets['content_text'].setPlaceholderText('Write your content here...')
layout.addWidget(widgets['content_text'])

layout.addWidget(QLabel('Hashtags (comma-separated):', parent))
widgets['hashtags'] = QLineEdit(parent)
widgets['hashtags'].setPlaceholderText('marketing, social, business')
layout.addWidget(widgets['hashtags'])

layout.addWidget(QLabel('Schedule Time (YYYY-MM-DD HH:MM):', parent))
widgets['schedule_time'] = QLineEdit(parent)
widgets['schedule_time'].setPlaceholderText('2024-12-25 14:30')
layout.addWidget(widgets['schedule_time'])

widgets['create_btn'] = QPushButton('Create Content', parent)
layout.addWidget(widgets['create_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'content_text': widgets['content_text'].toPlainText(),
        'platform': widgets['platform'].currentText(),
        'content_type': widgets['content_type'].currentText(),
        'hashtags': widgets['hashtags'].text(),
        'schedule_time': widgets['schedule_time'].text()
    }

def set_initial_state(widgets, state):
    widgets['content_text'].setPlainText(state.get('content_text', ''))
    widgets['platform'].setCurrentText(state.get('platform', 'Twitter'))
    widgets['content_type'].setCurrentText(state.get('content_type', 'Post'))
    widgets['hashtags'].setText(state.get('hashtags', ''))
    widgets['schedule_time'].setText(state.get('schedule_time', ''))
```


## Node: Engagement Optimizer (ID: engagement-optimizer)

Calculates engagement score (0-80) using platform-specific length ranges, hashtag counts, and content analysis. Uses re.findall(r'#\\w+') to count hashtags, checks for question words using any() with list comprehension, analyzes call-to-action terms with string.lower() matching. 

Implements readability scoring with re.split(r'[.!?]+') for sentence parsing and average word count calculation. Detects special characters and emojis using ord(char) > 127 for Unicode. Returns Tuple[int, str, str] containing score, performance prediction (High/Good/Moderate/Low), and suggestion text joined with '; '.

### Metadata

```json
{
  "uuid": "engagement-optimizer",
  "title": "Engagement Optimizer",
  "pos": [
    461.7495,
    52.66400000000007
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
import re
from typing import Tuple

@node_entry
def optimize_engagement(content: str, platform: str) -> Tuple[int, str, str]:
    score = 0
    suggestions = []
    
    # Content length scoring
    content_length = len(content)
    if platform == "Twitter":
        if 100 <= content_length <= 280:
            score += 20
        else:
            suggestions.append("Optimize length for Twitter (100-280 chars)")
    elif platform == "Instagram":
        if 150 <= content_length <= 300:
            score += 20
        else:
            suggestions.append("Instagram posts perform better with 150-300 characters")
    elif platform == "LinkedIn":
        if 200 <= content_length <= 600:
            score += 20
        else:
            suggestions.append("LinkedIn content works best with 200-600 characters")
    
    # Hashtag analysis
    hashtags = re.findall(r'#\w+', content)
    if platform == "Instagram":
        if 5 <= len(hashtags) <= 11:
            score += 15
        else:
            suggestions.append("Use 5-11 hashtags for Instagram")
    elif platform == "Twitter":
        if 1 <= len(hashtags) <= 3:
            score += 15
        else:
            suggestions.append("Use 1-3 hashtags for Twitter")
    elif platform == "LinkedIn":
        if 1 <= len(hashtags) <= 5:
            score += 15
        else:
            suggestions.append("Use 1-5 hashtags for LinkedIn")
    
    # Engagement elements
    if any(word in content.lower() for word in ['?', 'what', 'how', 'why', 'when']):
        score += 15
    else:
        suggestions.append("Add questions to encourage engagement")
    
    if any(word in content.lower() for word in ['share', 'comment', 'like', 'follow', 'subscribe']):
        score += 10
    else:
        suggestions.append("Include call-to-action words")
    
    # Readability
    sentences = re.split(r'[.!?]+', content)
    avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
    
    if avg_sentence_length <= 20:
        score += 10
    else:
        suggestions.append("Use shorter sentences for better readability")
    
    # Special characters and emojis
    if re.search(r'[!@#$%^&*()_+{}|:<>?]', content) or any(ord(char) > 127 for char in content):
        score += 10
    else:
        suggestions.append("Add emojis or special characters for visual appeal")
    
    # Generate performance prediction
    if score >= 70:
        performance = "High engagement expected"
    elif score >= 50:
        performance = "Good engagement potential"
    elif score >= 30:
        performance = "Moderate engagement expected"
    else:
        performance = "Low engagement predicted"
    
    suggestion_text = '; '.join(suggestions) if suggestions else "Content optimized for engagement!"
    
    print(f"\n=== ENGAGEMENT ANALYSIS ===")
    print(f"Platform: {platform}")
    print(f"Engagement score: {score}/80")
    print(f"Performance prediction: {performance}")
    print(f"Suggestions: {suggestion_text}")
    
    return score, performance, suggestion_text
```


## Node: Schedule Manager (ID: schedule-manager)

Validates scheduled posting time using datetime.strptime() parsing and compares against datetime.now() to prevent past scheduling. Calculates time difference using divmod() for days/hours/minutes countdown display. Implements platform-specific optimal time checking: Instagram 11AM-1PM/5PM-7PM, Twitter 8AM-10AM/7PM-9PM, LinkedIn 8AM-10AM/5PM-6PM weekdays.

Uses datetime.weekday() for weekend detection (LinkedIn weekday preference). Returns Tuple[str, str, str] containing schedule status, time_until countdown string, and timing recommendations. Error handling captures scheduling failures with try-except blocks and returns error status messages.

### Metadata

```json
{
  "uuid": "schedule-manager",
  "title": "Schedule Manager",
  "pos": [
    794.37375,
    406.83899999999994
  ],
  "size": [
    250,
    193
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
import datetime
from typing import Tuple

@node_entry
def manage_schedule(content: str, platform: str, schedule_time: str, schedule_status: str) -> Tuple[str, str, str]:
    if schedule_status != "Valid":
        return "Error", "Invalid schedule time format", "Failed"
    
    try:
        scheduled_dt = datetime.datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
        current_dt = datetime.datetime.now()
        
        if scheduled_dt <= current_dt:
            return "Error", "Cannot schedule in the past", "Failed"
        
        # Calculate time until posting
        time_diff = scheduled_dt - current_dt
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        time_until = f"{days}d {hours}h {minutes}m"
        
        # Determine optimal posting time recommendations
        hour = scheduled_dt.hour
        weekday = scheduled_dt.weekday()  # 0=Monday, 6=Sunday
        
        optimal_recommendations = []
        
        if platform == "Instagram":
            if not (11 <= hour <= 13 or 17 <= hour <= 19):
                optimal_recommendations.append("Instagram: Best times are 11AM-1PM or 5PM-7PM")
        elif platform == "Twitter":
            if not (8 <= hour <= 10 or 19 <= hour <= 21):
                optimal_recommendations.append("Twitter: Best times are 8AM-10AM or 7PM-9PM")
        elif platform == "LinkedIn":
            if weekday >= 5:  # Weekend
                optimal_recommendations.append("LinkedIn: Weekdays perform better than weekends")
            if not (8 <= hour <= 10 or 17 <= hour <= 18):
                optimal_recommendations.append("LinkedIn: Best times are 8AM-10AM or 5PM-6PM")
        
        recommendations = '; '.join(optimal_recommendations) if optimal_recommendations else "Scheduled at optimal time!"
        
        print(f"\n=== SCHEDULE MANAGEMENT ===")
        print(f"Platform: {platform}")
        print(f"Scheduled for: {schedule_time}")
        print(f"Time until posting: {time_until}")
        print(f"Recommendations: {recommendations}")
        
        return "Scheduled", time_until, recommendations
        
    except Exception as e:
        error_msg = f"Scheduling error: {str(e)}"
        print(error_msg)
        return "Error", error_msg, "Failed"
```


## Node: Social Media Dashboard (ID: post-dashboard)

Formats consolidated social media data into structured dashboard using string concatenation with section headers. Implements content preview with string slicing [:150] + "..." for truncation. Calculates hashtag count using list comprehension with .startswith('#') filtering on .split() results.

Displays engagement metrics, schedule status, and recommendations with conditional formatting based on status values. Creates action item lists using conditional logic for scheduled vs error states. Returns single formatted dashboard string with fixed-width layout for QTextEdit display using Courier New monospace font.

### Metadata

```json
{
  "uuid": "post-dashboard",
  "title": "Social Media Dashboard",
  "pos": [
    1339.04575,
    190.87475
  ],
  "size": [
    276,
    693
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
from typing import Tuple

@node_entry
def create_dashboard(content: str, platform: str, content_type: str, hashtags: str, engagement_score: int, performance_prediction: str, suggestions: str, schedule_status: str, time_until: str, recommendations: str) -> str:
    dashboard = "\n" + "="*60 + "\n"
    dashboard += "           SOCIAL MEDIA POST DASHBOARD\n"
    dashboard += "="*60 + "\n\n"
    
    # Post Overview
    dashboard += f"📱 POST OVERVIEW\n"
    dashboard += f"   Platform: {platform}\n"
    dashboard += f"   Content Type: {content_type}\n"
    dashboard += f"   Character Count: {len(content)}\n"
    hashtag_count = len([tag for tag in hashtags.split() if tag.startswith('#')])
    dashboard += f"   Hashtags: {hashtag_count}\n\n"
    
    # Content Preview
    dashboard += f"📝 CONTENT PREVIEW\n"
    preview = content[:150] + "..." if len(content) > 150 else content
    dashboard += f"   {preview}\n\n"
    
    # Engagement Analysis
    dashboard += f"📊 ENGAGEMENT ANALYSIS\n"
    dashboard += f"   Score: {engagement_score}/80\n"
    dashboard += f"   Prediction: {performance_prediction}\n"
    if suggestions != "Content optimized for engagement!":
        dashboard += f"   Suggestions: {suggestions}\n"
    dashboard += "\n"
    
    # Schedule Information
    dashboard += f"⏰ SCHEDULE STATUS\n"
    dashboard += f"   Status: {schedule_status}\n"
    if schedule_status == "Scheduled":
        dashboard += f"   Time until posting: {time_until}\n"
        if recommendations != "Scheduled at optimal time!":
            dashboard += f"   Timing notes: {recommendations}\n"
    elif schedule_status == "Error":
        dashboard += f"   Issue: {time_until}\n"
    dashboard += "\n"
    
    # Action Items
    dashboard += f"✅ NEXT STEPS\n"
    if schedule_status == "Scheduled":
        dashboard += f"   • Content ready for posting\n"
        dashboard += f"   • Monitor engagement after posting\n"
        dashboard += f"   • Prepare follow-up content\n"
    else:
        dashboard += f"   • Fix scheduling issues\n"
        dashboard += f"   • Review content optimization\n"
        dashboard += f"   • Test posting setup\n"
    
    dashboard += "\n" + "="*60
    
    print(dashboard)
    return dashboard
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Social Media Dashboard', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['dashboard_display'] = QTextEdit(parent)
widgets['dashboard_display'].setMinimumHeight(220)
widgets['dashboard_display'].setReadOnly(True)
widgets['dashboard_display'].setPlainText('Create content to see dashboard...')
font = QFont('Courier New', 9)
widgets['dashboard_display'].setFont(font)
layout.addWidget(widgets['dashboard_display'])

widgets['post_now_btn'] = QPushButton('Post Now', parent)
layout.addWidget(widgets['post_now_btn'])

widgets['edit_content_btn'] = QPushButton('Edit Content', parent)
layout.addWidget(widgets['edit_content_btn'])

widgets['duplicate_btn'] = QPushButton('Duplicate for Other Platform', parent)
layout.addWidget(widgets['duplicate_btn'])
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
    "start_node_uuid": "content-creator",
    "start_pin_name": "exec_out",
    "end_node_uuid": "engagement-optimizer",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_1",
    "end_node_uuid": "engagement-optimizer",
    "end_pin_name": "content"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_2",
    "end_node_uuid": "engagement-optimizer",
    "end_pin_name": "platform"
  },
  {
    "start_node_uuid": "engagement-optimizer",
    "start_pin_name": "exec_out",
    "end_node_uuid": "schedule-manager",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_1",
    "end_node_uuid": "schedule-manager",
    "end_pin_name": "content"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_2",
    "end_node_uuid": "schedule-manager",
    "end_pin_name": "platform"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_5",
    "end_node_uuid": "schedule-manager",
    "end_pin_name": "schedule_status"
  },
  {
    "start_node_uuid": "schedule-manager",
    "start_pin_name": "exec_out",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_1",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "content"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_2",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "platform"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_3",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "content_type"
  },
  {
    "start_node_uuid": "content-creator",
    "start_pin_name": "output_4",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "hashtags"
  },
  {
    "start_node_uuid": "engagement-optimizer",
    "start_pin_name": "output_1",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "engagement_score"
  },
  {
    "start_node_uuid": "engagement-optimizer",
    "start_pin_name": "output_2",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "performance_prediction"
  },
  {
    "start_node_uuid": "engagement-optimizer",
    "start_pin_name": "output_3",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "suggestions"
  },
  {
    "start_node_uuid": "schedule-manager",
    "start_pin_name": "output_1",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "schedule_status"
  },
  {
    "start_node_uuid": "schedule-manager",
    "start_pin_name": "output_2",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "time_until"
  },
  {
    "start_node_uuid": "schedule-manager",
    "start_pin_name": "output_3",
    "end_node_uuid": "post-dashboard",
    "end_pin_name": "recommendations"
  }
]
```

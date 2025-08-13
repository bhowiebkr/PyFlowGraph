# Text Processing Pipeline

Text analysis workflow with regex-based cleaning, statistical counting, keyword extraction, and report generation. Implements string.split(), re.sub(), Counter frequency analysis, and formatted output for comprehensive text processing and analysis.

## Node: Text Input Source (ID: text-input)

Provides text input through QComboBox selection or manual QTextEdit entry. Implements conditional text selection using if-elif statements for source_type values: "Manual", "Lorem Ipsum", "Sample Article", "Technical Text". Returns single string output with predefined text samples or user input.

Uses len() function for character counting and string slicing [:100] for preview display. GUI includes QTextEdit with placeholder text and QComboBox with addItems() for source selection. State management handles text content and source type persistence.

### Metadata

```json
{
  "uuid": "text-input",
  "title": "Text Input Source",
  "pos": [
    -170.71574999999999,
    230.41750000000002
  ],
  "size": [
    276,
    437
  ],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "input_text": "",
    "source_type": "Manual"
  }
}
```

### Logic

```python
@node_entry
def provide_text(input_text: str, source_type: str) -> str:
    if source_type == "Manual":
        result = input_text
    elif source_type == "Lorem Ipsum":
        result = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
    elif source_type == "Sample Article":
        result = "Artificial Intelligence has revolutionized many industries. Machine learning algorithms can process vast amounts of data quickly. Natural language processing enables computers to understand human text. Deep learning models achieve remarkable accuracy in image recognition. The future of AI looks promising with continued research and development."
    else:  # Technical Text
        result = "Python is a high-level programming language. It supports object-oriented programming paradigms. The syntax is designed to be readable and concise. Libraries like NumPy and Pandas facilitate data analysis. Django and Flask are popular web frameworks. Python's versatility makes it suitable for various applications."
    
    print(f"Text source: {source_type}")
    print(f"Text length: {len(result)} characters")
    print(f"Preview: {result[:100]}...")
    
    return result
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QComboBox, QPushButton

layout.addWidget(QLabel('Text Source:', parent))
widgets['source_type'] = QComboBox(parent)
widgets['source_type'].addItems(['Manual', 'Lorem Ipsum', 'Sample Article', 'Technical Text'])
layout.addWidget(widgets['source_type'])

layout.addWidget(QLabel('Enter your text (for Manual mode):', parent))
widgets['input_text'] = QTextEdit(parent)
widgets['input_text'].setMinimumHeight(120)
widgets['input_text'].setPlaceholderText('Type your text here...')
layout.addWidget(widgets['input_text'])

widgets['process_btn'] = QPushButton('Process Text', parent)
layout.addWidget(widgets['process_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'input_text': widgets['input_text'].toPlainText(),
        'source_type': widgets['source_type'].currentText()
    }

def set_initial_state(widgets, state):
    widgets['input_text'].setPlainText(state.get('input_text', ''))
    widgets['source_type'].setCurrentText(state.get('source_type', 'Manual'))
```


## Node: Text Cleaner & Normalizer (ID: text-cleaner)

Performs text preprocessing using re.sub(r'\\s+', ' ') for whitespace normalization, string.lower() for case conversion, str.maketrans() with string.punctuation for punctuation removal, and re.sub(r'\\d+', '') for number removal. Boolean flags control each cleaning operation.

Uses str.strip() for leading/trailing whitespace removal and sequential regex operations for text transformation. Returns single cleaned string output. GUI includes QCheckBox widgets for remove_punctuation, convert_lowercase, and remove_numbers options with isChecked() state management.

### Metadata

```json
{
  "uuid": "text-cleaner",
  "title": "Text Cleaner & Normalizer",
  "pos": [
    351.37175,
    -53.797249999999984
  ],
  "size": [
    250,
    293
  ],
  "colors": {
    "title": "#28a745",
    "body": "#1e7e34"
  },
  "gui_state": {
    "remove_punctuation": false,
    "convert_lowercase": true,
    "remove_numbers": false
  }
}
```

### Logic

```python
import re
import string

@node_entry
def clean_text(text: str, remove_punctuation: bool, convert_lowercase: bool, remove_numbers: bool) -> str:
    cleaned = text
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned.strip())
    
    # Convert to lowercase
    if convert_lowercase:
        cleaned = cleaned.lower()
    
    # Remove punctuation
    if remove_punctuation:
        cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))
    
    # Remove numbers
    if remove_numbers:
        cleaned = re.sub(r'\d+', '', cleaned)
    
    # Clean up extra spaces again
    cleaned = re.sub(r'\s+', ' ', cleaned.strip())
    
    print(f"Original length: {len(text)}")
    print(f"Cleaned length: {len(cleaned)}")
    print(f"Cleaning options: Lowercase={convert_lowercase}, No punctuation={remove_punctuation}, No numbers={remove_numbers}")
    
    return cleaned
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QCheckBox, QPushButton

widgets['remove_punctuation'] = QCheckBox('Remove Punctuation', parent)
widgets['remove_punctuation'].setChecked(False)
layout.addWidget(widgets['remove_punctuation'])

widgets['convert_lowercase'] = QCheckBox('Convert to Lowercase', parent)
widgets['convert_lowercase'].setChecked(True)
layout.addWidget(widgets['convert_lowercase'])

widgets['remove_numbers'] = QCheckBox('Remove Numbers', parent)
widgets['remove_numbers'].setChecked(False)
layout.addWidget(widgets['remove_numbers'])

widgets['clean_btn'] = QPushButton('Clean Text', parent)
layout.addWidget(widgets['clean_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'remove_punctuation': widgets['remove_punctuation'].isChecked(),
        'convert_lowercase': widgets['convert_lowercase'].isChecked(),
        'remove_numbers': widgets['remove_numbers'].isChecked()
    }

def set_initial_state(widgets, state):
    widgets['remove_punctuation'].setChecked(state.get('remove_punctuation', False))
    widgets['convert_lowercase'].setChecked(state.get('convert_lowercase', True))
    widgets['remove_numbers'].setChecked(state.get('remove_numbers', False))
```


## Node: Text Statistics Analyzer (ID: text-analyzer)

Calculates text metrics using len() for character count, string.split() for word count, re.findall(r'[.!?]+') for sentence detection, and split('\\n\\n') for paragraph counting. Computes average word length using sum() and len() with string.strip() for punctuation removal.

Implements word frequency analysis using Counter with word.lower().strip() normalization and most_common(5) for top terms. Returns Tuple[int, int, int, int, float, str] containing character, word, sentence, paragraph counts, average word length, and formatted top words string.

### Metadata

```json
{
  "uuid": "text-analyzer",
  "title": "Text Statistics Analyzer",
  "pos": [
    883.678,
    372.62425
  ],
  "size": [
    250,
    243
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
from collections import Counter

@node_entry
def analyze_text(text: str) -> Tuple[int, int, int, int, float, str]:
    # Basic counts
    char_count = len(text)
    word_count = len(text.split())
    sentence_count = len(re.findall(r'[.!?]+', text))
    paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
    
    # Average word length
    words = text.split()
    avg_word_length = sum(len(word.strip('.,!?;:')) for word in words) / len(words) if words else 0
    
    # Most common words (top 5)
    word_freq = Counter(word.lower().strip('.,!?;:') for word in words if len(word) > 2)
    top_words = ', '.join([f"{word}({count})" for word, count in word_freq.most_common(5)])
    
    print("\n=== TEXT ANALYSIS ===")
    print(f"Characters: {char_count}")
    print(f"Words: {word_count}")
    print(f"Sentences: {sentence_count}")
    print(f"Paragraphs: {paragraph_count}")
    print(f"Average word length: {avg_word_length:.1f}")
    print(f"Most frequent words: {top_words}")
    
    return char_count, word_count, sentence_count, paragraph_count, round(avg_word_length, 1), top_words
```


## Node: Keyword & Phrase Extractor (ID: keyword-extractor)

Extracts keywords using re.findall(r'\\b[a-zA-Z]+\\b') for word extraction, filters against stop_words set using list comprehension, and applies min_word_length threshold. Uses Counter.most_common(10) for frequency ranking. Detects phrases with regex pattern r'\\b(?:[a-zA-Z]+\\s+){1,2}[a-zA-Z]+\\b' for 2-3 word combinations.

Identifies proper nouns using re.findall(r'\\b[A-Z][a-zA-Z]+\\b') for capitalized words. Returns Tuple[List[str], List[str], List[str]] containing top keywords, phrases, and proper nouns. GUI includes QSpinBox for min_word_length configuration (3-10 range).

### Metadata

```json
{
  "uuid": "keyword-extractor",
  "title": "Keyword & Phrase Extractor",
  "pos": [
    824.5626250000001,
    -92.00799999999998
  ],
  "size": [
    250,
    242
  ],
  "colors": {
    "title": "#6f42c1",
    "body": "#563d7c"
  },
  "gui_state": {
    "min_word_length": 4
  }
}
```

### Logic

```python
import re
from typing import Tuple, List
from collections import Counter

@node_entry
def extract_keywords(text: str, min_word_length: int) -> Tuple[List[str], List[str], List[str]]:
    # Common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those'}
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter keywords (non-stop words, minimum length)
    keywords = [word for word in words if word not in stop_words and len(word) >= min_word_length]
    keyword_freq = Counter(keywords)
    top_keywords = [word for word, count in keyword_freq.most_common(10)]
    
    # Extract potential phrases (2-3 word combinations)
    phrase_pattern = r'\b(?:[a-zA-Z]+\s+){1,2}[a-zA-Z]+\b'
    phrases = re.findall(phrase_pattern, text.lower())
    filtered_phrases = []
    for phrase in phrases:
        words_in_phrase = phrase.split()
        if len(words_in_phrase) >= 2 and not any(word in stop_words for word in words_in_phrase[:2]):
            filtered_phrases.append(phrase.strip())
    
    phrase_freq = Counter(filtered_phrases)
    top_phrases = [phrase for phrase, count in phrase_freq.most_common(5)]
    
    # Extract capitalized words (potential proper nouns)
    proper_nouns = list(set(re.findall(r'\b[A-Z][a-zA-Z]+\b', text)))
    proper_nouns = [noun for noun in proper_nouns if len(noun) > 2][:10]
    
    print("\n=== KEYWORD EXTRACTION ===")
    print(f"Top keywords: {', '.join(top_keywords[:5])}")
    print(f"Key phrases: {', '.join(top_phrases[:3])}")
    print(f"Proper nouns: {', '.join(proper_nouns[:5])}")
    
    return top_keywords, top_phrases, proper_nouns
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QSpinBox, QPushButton

layout.addWidget(QLabel('Minimum Keyword Length:', parent))
widgets['min_word_length'] = QSpinBox(parent)
widgets['min_word_length'].setRange(3, 10)
widgets['min_word_length'].setValue(4)
layout.addWidget(widgets['min_word_length'])

widgets['extract_btn'] = QPushButton('Extract Keywords', parent)
layout.addWidget(widgets['extract_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'min_word_length': widgets['min_word_length'].value()
    }

def set_initial_state(widgets, state):
    widgets['min_word_length'].setValue(state.get('min_word_length', 4))
```


## Node: Processing Report Generator (ID: report-generator)

Formats comprehensive text analysis report using string concatenation with section headers and f-string formatting. Combines statistical metrics, processing summaries, frequency analysis, and keyword extraction results. Uses len() calculations for character reduction analysis and string.join() for list formatting.

Implements conditional display logic for phrases and proper_nouns using if statements. Creates text preview using string slicing [:200] with "..." truncation. Returns single formatted report string for QTextEdit display with Courier New monospace font and read-only configuration.

### Metadata

```json
{
  "uuid": "report-generator",
  "title": "Processing Report Generator",
  "pos": [
    1465.2783750000003,
    246.95825000000002
  ],
  "size": [
    276,
    664
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
from typing import List

@node_entry
def generate_report(original_text: str, cleaned_text: str, char_count: int, word_count: int, sentence_count: int, paragraph_count: int, avg_word_length: float, top_words: str, keywords: List[str], phrases: List[str], proper_nouns: List[str]) -> str:
    report = "\n" + "="*60 + "\n"
    report += "               TEXT PROCESSING REPORT\n"
    report += "="*60 + "\n\n"
    
    # Text Overview
    report += "📊 TEXT OVERVIEW\n"
    report += f"   • Characters: {char_count:,}\n"
    report += f"   • Words: {word_count:,}\n"
    report += f"   • Sentences: {sentence_count}\n"
    report += f"   • Paragraphs: {paragraph_count}\n"
    report += f"   • Average word length: {avg_word_length} characters\n\n"
    
    # Processing Summary
    report += "🔧 PROCESSING SUMMARY\n"
    original_words = len(original_text.split())
    cleaned_words = len(cleaned_text.split())
    report += f"   • Original text: {len(original_text)} characters, {original_words} words\n"
    report += f"   • Cleaned text: {len(cleaned_text)} characters, {cleaned_words} words\n"
    report += f"   • Reduction: {len(original_text) - len(cleaned_text)} characters\n\n"
    
    # Frequency Analysis
    report += "📈 FREQUENCY ANALYSIS\n"
    report += f"   • Most common words: {top_words}\n\n"
    
    # Keywords and Phrases
    report += "🔍 EXTRACTED KEYWORDS\n"
    report += f"   • Key terms: {', '.join(keywords[:8])}\n"
    if phrases:
        report += f"   • Key phrases: {', '.join(phrases[:4])}\n"
    if proper_nouns:
        report += f"   • Proper nouns: {', '.join(proper_nouns[:6])}\n"
    report += "\n"
    
    # Text Sample
    report += "📝 PROCESSED TEXT SAMPLE\n"
    sample = cleaned_text[:200] + "..." if len(cleaned_text) > 200 else cleaned_text
    report += f"   {sample}\n\n"
    
    report += "="*60
    
    print(report)
    return report
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Text Processing Report', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['report_display'] = QTextEdit(parent)
widgets['report_display'].setMinimumHeight(200)
widgets['report_display'].setReadOnly(True)
widgets['report_display'].setPlainText('Process text to generate report...')
font = QFont('Courier New', 9)
widgets['report_display'].setFont(font)
layout.addWidget(widgets['report_display'])

widgets['save_report_btn'] = QPushButton('Save Report', parent)
layout.addWidget(widgets['save_report_btn'])

widgets['new_analysis_btn'] = QPushButton('New Analysis', parent)
layout.addWidget(widgets['new_analysis_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    report = outputs.get('output_1', 'No report data')
    widgets['report_display'].setPlainText(report)
```


## Node: Reroute (ID: c6b89a70-f130-4d9a-bc20-49ce9dfdb32b)

A simple organizational node that facilitates clean data flow routing within the text processing pipeline, allowing the cleaned text output to be efficiently distributed to multiple downstream analysis components without complex connection patterns.

### Metadata

```json
{
  "uuid": "c6b89a70-f130-4d9a-bc20-49ce9dfdb32b",
  "title": "",
  "pos": [
    874.503125,
    258.5487499999999
  ],
  "size": [
    200,
    150
  ],
  "is_reroute": true,
  "colors": {},
  "gui_state": {}
}
```

### Logic

```python

```


## Connections

```json
[
  {
    "start_node_uuid": "text-input",
    "start_pin_name": "exec_out",
    "end_node_uuid": "text-cleaner",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "text-input",
    "start_pin_name": "output_1",
    "end_node_uuid": "text-cleaner",
    "end_pin_name": "text"
  },
  {
    "start_node_uuid": "text-cleaner",
    "start_pin_name": "exec_out",
    "end_node_uuid": "text-analyzer",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "text-cleaner",
    "start_pin_name": "output_1",
    "end_node_uuid": "text-analyzer",
    "end_pin_name": "text"
  },
  {
    "start_node_uuid": "text-cleaner",
    "start_pin_name": "exec_out",
    "end_node_uuid": "keyword-extractor",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "text-cleaner",
    "start_pin_name": "output_1",
    "end_node_uuid": "keyword-extractor",
    "end_pin_name": "text"
  },
  {
    "start_node_uuid": "text-analyzer",
    "start_pin_name": "exec_out",
    "end_node_uuid": "report-generator",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "text-input",
    "start_pin_name": "output_1",
    "end_node_uuid": "report-generator",
    "end_pin_name": "original_text"
  },
  {
    "start_node_uuid": "text-analyzer",
    "start_pin_name": "output_1",
    "end_node_uuid": "report-generator",
    "end_pin_name": "char_count"
  },
  {
    "start_node_uuid": "text-analyzer",
    "start_pin_name": "output_2",
    "end_node_uuid": "report-generator",
    "end_pin_name": "word_count"
  },
  {
    "start_node_uuid": "text-analyzer",
    "start_pin_name": "output_3",
    "end_node_uuid": "report-generator",
    "end_pin_name": "sentence_count"
  },
  {
    "start_node_uuid": "text-analyzer",
    "start_pin_name": "output_4",
    "end_node_uuid": "report-generator",
    "end_pin_name": "paragraph_count"
  },
  {
    "start_node_uuid": "text-analyzer",
    "start_pin_name": "output_5",
    "end_node_uuid": "report-generator",
    "end_pin_name": "avg_word_length"
  },
  {
    "start_node_uuid": "text-analyzer",
    "start_pin_name": "output_6",
    "end_node_uuid": "report-generator",
    "end_pin_name": "top_words"
  },
  {
    "start_node_uuid": "keyword-extractor",
    "start_pin_name": "output_1",
    "end_node_uuid": "report-generator",
    "end_pin_name": "keywords"
  },
  {
    "start_node_uuid": "keyword-extractor",
    "start_pin_name": "output_2",
    "end_node_uuid": "report-generator",
    "end_pin_name": "phrases"
  },
  {
    "start_node_uuid": "keyword-extractor",
    "start_pin_name": "output_3",
    "end_node_uuid": "report-generator",
    "end_pin_name": "proper_nouns"
  },
  {
    "start_node_uuid": "text-cleaner",
    "start_pin_name": "output_1",
    "end_node_uuid": "c6b89a70-f130-4d9a-bc20-49ce9dfdb32b",
    "end_pin_name": "input"
  },
  {
    "start_node_uuid": "c6b89a70-f130-4d9a-bc20-49ce9dfdb32b",
    "start_pin_name": "output",
    "end_node_uuid": "report-generator",
    "end_pin_name": "cleaned_text"
  }
]
```

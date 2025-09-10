# Named Output Pin Example

This example demonstrates the new named output pin feature where outputs can have custom names like "result:int" instead of generic "output_1", "output_2", etc.

## Node: Text Analyzer (ID: text-analyzer)

Analyzes text input and returns multiple named outputs including word count, character count, and analysis status.

### Metadata

```json
{
  "uuid": "text-analyzer",
  "title": "Text Analyzer",
  "pos": [100, 100],
  "size": [250, 150],
  "colors": {
    "title": "#28a745",
    "body": "#1e7e34"
  }
}
```

### Logic

```python
from typing import Tuple

@node_entry
def analyze_text(text: str) -> Tuple["word_count:int", "char_count:int", "status:str", "is_empty:bool"]:
    """
    Analyzes input text and returns named outputs.
    
    This demonstrates the new named output pin feature:
    - word_count: Number of words in the text
    - char_count: Number of characters in the text  
    - status: Analysis result status
    - is_empty: Whether the text is empty or not
    """
    if not text or text.strip() == "":
        return 0, 0, "empty", True
    
    # Count words and characters
    word_count = len(text.split())
    char_count = len(text)
    
    # Determine status based on length
    if word_count < 5:
        status = "short"
    elif word_count < 20:
        status = "medium"
    else:
        status = "long"
    
    print(f"Text analysis: {word_count} words, {char_count} characters, status: {status}")
    
    return word_count, char_count, status, False
```

### Expected Output Pins

With the named output feature, this node will create output pins with the following names:
- **word_count** (int) - instead of "output_1"
- **char_count** (int) - instead of "output_2"  
- **status** (str) - instead of "output_3"
- **is_empty** (bool) - instead of "output_4"

### Test Cases

1. **Empty input**: `""` → word_count=0, char_count=0, status="empty", is_empty=True
2. **Short text**: `"Hello world"` → word_count=2, char_count=11, status="short", is_empty=False
3. **Long text**: `"This is a much longer sentence with many words to demonstrate the analysis"` → word_count=13, char_count=74, status="medium", is_empty=False

### Comparison

**Before (generic names):**
- output_1 (int)
- output_2 (int)
- output_3 (str)
- output_4 (bool)

**After (named outputs):**
- word_count (int)
- char_count (int)
- status (str)
- is_empty (bool)

This makes the node much more readable and easier to understand when connecting to other nodes.
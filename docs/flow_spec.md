# FlowSpec: The .md File Format Specification

**Version:** 1.0  
**File Extension:** .md  

## 1. Introduction & Philosophy

FlowSpec is a structured, document-based file format for defining node-based graphs and workflows. It is designed to be human-readable, version-control friendly, and easily parsed by both humans and AI models.

**Core Philosophy:** "the document is the graph."

### Guiding Principles

- **Readability First**: Clear structure for human authors and reviewers
- **Structured & Unambiguous**: Rigid structure allowing deterministic parsing  
- **Version Control Native**: Clean diffs in Git and other VCS
- **Language Agnostic**: Code blocks can contain any programming language
- **LLM Friendly**: Descriptive format ideal for AI interaction

## 2. Core Concepts

- **Graph**: The entire document represents a single graph (Level 1 Heading)
- **Node**: A major section (Level 2 Heading) representing a graph node
- **Component**: A subsection (Level 3 Heading) within a node
- **Data Block**: Machine-readable data in fenced code blocks

## 3. File Structure Specification

### 3.1 Graph Header

Every .md file MUST begin with a single Level 1 Heading (#).

```markdown
# Graph Title

Optional graph description goes here.
```

### 3.2 Node Definitions

Each node MUST use this exact format:

```markdown
## Node: <Human-Readable-Title> (ID: <unique-identifier>)

Optional node description.

### Metadata
```json
{
    "uuid": "unique-identifier",
    "title": "Human-Readable-Title",
    "pos": [100, 200],
    "size": [300, 250]
}
```

### Logic

```python
@node_entry
def node_function(input_param: str) -> str:
    return f"Processed: {input_param}"
```

### 3.3 Required Components

- **Metadata**: JSON object with uuid, title, and optional pos/size
- **Logic**: Python function with @node_entry decorator

### 3.4 Optional Components

- **GUI Definition**: Python code for user interface widgets
- **GUI State Handler**: Functions for widget state management

### 3.5 Connections Section

The file MUST contain exactly one Connections section:

```markdown
## Connections
```json
[
    {
        "start_node_uuid": "node1",
        "start_pin_name": "output_1", 
        "end_node_uuid": "node2",
        "end_pin_name": "input_param"
    }
]
```

## 4. Simple Example

```markdown
# Hello World Pipeline

A basic two-node pipeline demonstrating the .md format.

## Node: Text Generator (ID: generator)

Creates a simple text message.

### Metadata
```json
{
    "uuid": "generator",
    "title": "Text Generator",
    "pos": [100, 100],
    "size": [200, 150]
}
```

### Logic

```python
@node_entry
def generate_text() -> str:
    return "Hello, World!"
```

## Node: Text Printer (ID: printer)

Prints the received text message.

### Metadata

```json
{
    "uuid": "printer", 
    "title": "Text Printer",
    "pos": [400, 100],
    "size": [200, 150]
}
```

### Logic

```python
@node_entry
def print_text(message: str) -> str:
    print(f"Received: {message}")
    return message
```

## Connections

```json
[
    {
        "start_node_uuid": "generator",
        "start_pin_name": "output_1",
        "end_node_uuid": "printer", 
        "end_pin_name": "message"
    }
]
```

## 5. Parser Implementation

A parser should use markdown-it-py to tokenize the document:

### 5.1 Algorithm

1. **Tokenize**: Parse file into token stream (don't render to HTML)
2. **State Machine**: Track current node and component being parsed
3. **Section Detection**:
   - `h1`: Graph title
   - `h2`: Node header (regex: `Node: (.*) \(ID: (.*)\)`) or "Connections"
   - `h3`: Component type (Metadata, Logic, etc.)
4. **Data Extraction**: Extract `content` from `fence` tokens based on `info` language tag
5. **Graph Construction**: Build in-memory graph from collected data

### 5.2 Token Types

- `heading_open` with `h1/h2/h3` tags
- `fence` with `info` property for language detection
- `inline` for text content

### 5.3 Validation Rules

- Exactly one h1 heading
- Each node must have unique uuid
- Metadata and Logic components are required
- Connections section is required
- JSON must be valid in metadata and connections

## 6. Extension Points

The format supports extension through:

- Additional component types (### Custom Component)
- Custom metadata fields
- Multiple programming languages in Logic blocks
- Custom connection properties

---

*This specification ensures .md files are both human-readable documents and structured data formats suitable for programmatic processing.*

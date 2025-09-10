# FlowSpec LLM Generator Instructions

This document provides step-by-step instructions for creating and maintaining the LLM-optimized version of flow_spec.md.

## Purpose

The LLM-optimized version (`flow_spec_llm.md`) serves as a token-efficient reference for:
- AI models working with PyFlowGraph files
- Quick lookup during code generation
- Rapid syntax verification
- Automated graph creation

**Target:** Reduce ~1300 lines to ~300-400 lines while maintaining 100% technical accuracy.

## Generation Process

### Step 1: Content Categorization

**KEEP (Essential Technical Info):**
- File structure templates
- Required syntax patterns
- Validation rules
- Type system specifications
- Pin generation rules
- Connection formats
- Error handling formats
- **CRITICAL: Complete @node_entry specification including runtime behavior**
- **CRITICAL: Logic block capabilities (imports, classes, helpers)**
- **CRITICAL: GUI data flow merging rules**
- **CRITICAL: Execution context variables for GUI**
- **CRITICAL: Auto-import framework information**

**COMPRESS (Reduce Verbosity):**
- Long explanations → bullet points
- Multiple examples → single template
- Philosophical sections → core principles
- Detailed rationales → key facts
- **NEVER compress critical technical details from KEEP list above**

**REMOVE (Non-Essential):**
- Extensive background philosophy
- Redundant explanations
- Marketing language
- Historical context
- Multiple similar examples
- Decorative formatting
- **NEVER remove any technical specifications or behavioral details**

### Step 2: Section-by-Section Conversion

#### 2.1 Introduction & Philosophy (Sections 1-2)
**Original:** ~100 lines of philosophy and concepts
**Compressed:** 5-10 lines covering core principles
- Format type and extension
- "Document IS the graph" principle
- Core structural elements

#### 2.2 File Structure (Section 3)
**Keep:** All subsection headers and required formats
**Compress:** 
- Combine similar subsections
- Use template format instead of verbose explanations
- Single comprehensive example instead of multiple variations

**Format:**
```
## File Structure
Template showing required sections and syntax
```

#### 2.3 Node Components (Sections 3.1-3.4)
**Keep:** All required and optional component specifications
**Compress:**
- Metadata fields → compact field list
- Logic requirements → essential rules
- GUI components → template patterns

**Format:**
```
## Node: Title (ID: uuid)
### Metadata - required fields, optional fields
### Logic - @node_entry requirements
### GUI Definition - optional, widget patterns
### GUI State Handler - optional, function signatures
```

#### 2.4 Sections (3.5-3.7)
**Dependencies, Groups, Connections**
- Keep JSON structure specifications
- Remove lengthy explanations
- Provide minimal complete examples

#### 2.5 Advanced Sections (3.8-3.14)
**Compress heavily:**
- ML Framework Integration → key supported types
- Native Object Passing → performance facts
- Virtual Environments → basic structure
- Error Handling → message formats

#### 2.6 Examples (Section 4)
**Reduce from multiple full examples to:**
- Basic node template
- GUI-enabled node template
- Connection patterns
- Remove redundant variations

#### 2.7 Implementation Details (Sections 5-7)
**Keep:** Essential parser requirements and validation rules
**Remove:** Detailed implementation discussion
**Compress:** Algorithm steps to bullet points

### Step 3: Template Patterns

#### Node Template Format:
```markdown
## Node: Title (ID: uuid)
Description (optional)

### Metadata
Required: uuid, title
Optional: pos, size, colors, gui_state, is_reroute

### Logic
@node_entry function with signature → pin generation

### GUI Definition (optional)
Widget creation patterns

### GUI State Handler (optional)
Function signatures: get_values, set_values, set_initial_state
```

#### Section Templates:
- Dependencies: JSON structure
- Groups: JSON structure with required fields
- Connections: JSON array format

### Step 4: Technical Accuracy Checklist

Ensure the compressed version includes:

**✓ All required file sections**
- Graph title (h1)
- Node definitions (h2)
- Components (h3) 
- Connections section

**✓ All required metadata fields**
- uuid, title
- Optional fields list

**✓ Complete @node_entry specification - CRITICAL DETAILS:**
- Required decorator (exactly one per Logic block)
- Entry point: Only decorated function called during execution
- Runtime behavior: No-op decorator, returns function unchanged
- Pin generation rules (parameters → input pins, return type → output pins)
- Default values supported for optional parameters
- Full type system support (basic, container, generic, optional, nested)

**✓ Logic block capabilities - CRITICAL:**
- Can contain imports, classes, helper functions, module-level code
- Only @node_entry function is called as entry point
- Full Python module support

**✓ GUI integration rules - CRITICAL DATA FLOW:**
- Widget storage requirements (widgets dict)
- Execution context: parent (QWidget), layout (QVBoxLayout), widgets (dict)
- Data flow merging: GUI values merged with pin values
- Connected pin values take precedence over GUI values
- State handler functions (get_values, set_values, set_initial_state)
- Return values distributed to both pins and GUI

**✓ Execution architecture - CRITICAL:**
- Single process execution
- Native object passing (100-1000x faster)
- Auto-imports: numpy as np, pandas as pd, torch, tensorflow as tf, jax, jax.numpy as jnp

**✓ JSON structure formats**
- Metadata format (all required/optional fields)
- Groups format (required: uuid, name, member_node_uuids)
- Connections format (start_node_uuid, start_pin_name, end_node_uuid, end_pin_name)
- Dependencies format (required: requirements array)

**✓ Validation rules - COMPREHENSIVE:**
- File structure requirements
- Node requirements (unique UUIDs, required components)
- GUI rules (widget storage, function requirements)
- Groups rules (unique UUIDs, valid member references)
- Connection rules (valid node references, correct pin names)

**✓ Pin system - COMPLETE:**
- Pin color generation (consistent hashing from type strings)
- Execution pins (always present: exec_in, exec_out)
- Data pins (from function signature)

**✓ Error handling formats**
- Error message patterns
- Execution limits

### Step 5: Synchronization Guidelines

When flow_spec.md is updated:

1. **Identify changes** in the main specification
2. **Categorize impact** (new features, format changes, rule updates)
3. **Update LLM version** following compression rules:
   - New technical requirements → add to LLM version
   - Format changes → update templates
   - New examples → integrate into existing templates
   - Clarifications → update if they change rules
4. **Validate completeness** against technical accuracy checklist
5. **Test token efficiency** - ensure significant reduction maintained

### Step 6: Quality Verification

**Technical completeness:**
- All syntax patterns documented
- All required fields specified
- All validation rules included
- All error formats covered

**Token efficiency:**
- ~70-80% reduction from original
- No redundant information
- Minimal but complete examples
- Structured for fast parsing

**Usability for LLMs:**
- Clear section headers
- Consistent formatting
- Template-based examples
- Quick reference structure

## Maintenance Schedule

- **Immediate:** When flow_spec.md has technical changes
- **Review:** Monthly check for sync with main spec
- **Validation:** Quarterly completeness audit

## Version Control

- Keep LLM version in same directory as main spec
- Update commit messages to indicate both files changed
- Tag major revisions for easy tracking
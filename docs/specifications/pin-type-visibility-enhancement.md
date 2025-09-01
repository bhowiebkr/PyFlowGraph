# PyFlowGraph Pin Type Visibility Enhancement Specifications

## Executive Summary

This document provides comprehensive specifications for enhancing pin and connection type visibility in PyFlowGraph through hover tooltips and visual feedback systems. The enhancement addresses a critical UX gap by implementing industry-standard type visibility patterns found in professional visual scripting tools like Grasshopper, Dynamo, and Blender.

## Business Justification

### Problem Statement
Users currently struggle to identify pin data types and connection compatibility in PyFlowGraph, relying solely on color coding which requires memorization and provides limited information. This creates friction for:
- New users learning the type system
- Experienced users working with complex graphs
- Debugging type compatibility issues
- Understanding connection data flow

### Success Metrics
- **Reduced Support Queries**: 50% reduction in type-related user questions
- **Improved Onboarding**: New users understand pin types within first 5 minutes
- **Enhanced Productivity**: Faster connection creation with reduced trial-and-error
- **Industry Alignment**: Match UX expectations from other visual scripting tools

## Design Philosophy

### Core Principles
- **Progressive Disclosure**: Information appears when needed, stays hidden when not
- **Industry Standards Alignment**: Follow established patterns from Grasshopper, Dynamo, n8n
- **Non-Intrusive Enhancement**: Enhance existing color system without replacing it
- **Educational Value**: Help users learn the type system through contextual information
- **Performance First**: Lightweight implementation with minimal performance impact

### Target Users
- **Primary**: Developers familiar with visual scripting tools expecting hover tooltips
- **Secondary**: New users needing guidance on type compatibility
- **Advanced**: Power users requiring detailed type information for complex graphs

## Feature Specifications

### Phase 1: Pin Hover Tooltips (Priority 1)

#### 1.1 Basic Pin Tooltips

**Trigger**: Mouse hover over any pin
**Display Timing**: 500ms delay (standard tooltip timing)
**Content**: 
```
Type: <pin_type>
Category: <data|execution>
Direction: <input|output>
```

**Example Output**:
```
Type: str
Category: data  
Direction: input
```

#### 1.2 Enhanced Data Pin Tooltips

**For Data Pins with Values**:
```
Type: <pin_type>
Category: data
Direction: <direction>
Current Value: <truncated_value>
```

**Value Truncation Rules**:
- Strings: Max 50 characters, add "..." if longer
- Numbers: Full precision up to 15 digits
- Complex objects: Show type name (e.g., "dict (5 keys)")
- None/null: Show "None"

#### 1.3 Execution Pin Tooltips

**For Execution Pins**:
```
Type: exec
Category: execution
Direction: <input|output>
Status: <ready|waiting|executed>
```

### Phase 2: Connection Hover Enhancement (Priority 2)

#### 2.1 Connection Type Display

**Trigger**: Mouse hover over any connection line
**Content**:
```
<source_node_name>.<source_pin_name> -> <dest_node_name>.<dest_pin_name>
Type: <data_type>
Status: <active|inactive>
```

#### 2.2 Visual Hover Effects

**Pin Hover Effects**:
- Subtle glow effect (2px outer glow using pin color)
- 10% brightness increase on pin color
- Smooth 200ms transition in/out

**Connection Hover Effects**:
- Line width increase from 3px to 4px
- 20% brightness increase on connection color  
- Smooth 150ms transition in/out

### Phase 3: Advanced Features (Priority 3)

#### 3.1 Type Compatibility Indicators

**During Connection Creation**:
- Compatible pins: Green glow (success indicator)
- Incompatible pins: Red glow (error indicator)  
- Same-type pins: Blue highlight for exact matches

#### 3.2 Compact Type Labels (Optional)

**Show/Hide Conditions**:
- Show when: Zoom level > 75%, critical pins only
- Hide when: Zoom level < 50%, too many pins visible
- Toggle: Right-click context menu option "Show Pin Types"

**Label Format**: 
- Position: Small text below pin, 8pt font
- Content: Abbreviated type (str, int, bool, list, dict, any, exec)
- Color: 60% opacity of pin color

## Technical Implementation

### 4.1 Modified Files

**Primary Changes**:
- `src/core/pin.py`: Add hover event handlers and tooltip generation
- `src/core/connection.py`: Add connection hover effects and tooltips

**Supporting Changes**:
- `src/utils/tooltip_utils.py`: New utility for consistent tooltip formatting
- `src/core/node_graph.py`: Integration for connection creation feedback

### 4.2 Pin.py Implementation

```python
def hoverEnterEvent(self, event):
    """Generate and display tooltip on hover."""
    tooltip_text = self._generate_tooltip_text()
    self.setToolTip(tooltip_text)
    self._apply_hover_effect()
    super().hoverEnterEvent(event)

def hoverLeaveEvent(self, event):
    """Remove hover effects."""
    self._remove_hover_effect()
    super().hoverLeaveEvent(event)

def _generate_tooltip_text(self):
    """Create formatted tooltip content."""
    lines = [
        f"Type: {self.pin_type}",
        f"Category: {self.pin_category}",
        f"Direction: {self.direction}"
    ]
    
    if self.pin_category == "data" and self.value is not None:
        value_str = self._format_value_for_tooltip(self.value)
        lines.append(f"Current Value: {value_str}")
    
    return "\n".join(lines)
```

### 4.3 Connection.py Implementation

```python
def hoverEnterEvent(self, event):
    """Show connection information on hover."""
    if self.start_pin and self.end_pin:
        tooltip_text = self._generate_connection_tooltip()
        self.setToolTip(tooltip_text)
        self._apply_connection_hover_effect()
    super().hoverEnterEvent(event)

def _generate_connection_tooltip(self):
    """Create connection tooltip content."""
    source = f"{self.start_pin.node.name}.{self.start_pin.name}"
    dest = f"{self.end_pin.node.name}.{self.end_pin.name}"
    return f"{source} -> {dest}\nType: {self.start_pin.pin_type}"
```

## User Stories for Scrum Master

### Epic: Pin Type Visibility Enhancement

**Epic Description**: As a PyFlowGraph user, I want to easily identify pin types and connection compatibility so that I can create valid connections efficiently and understand data flow in complex graphs.

### Story 1: Basic Pin Hover Tooltips
```
As a PyFlowGraph user
I want to see type information when hovering over pins  
So that I can understand what data types each pin accepts/outputs

Acceptance Criteria:
- [ ] Hovering over any pin shows tooltip after 500ms delay
- [ ] Tooltip displays: Type, Category, Direction
- [ ] Tooltip disappears when mouse leaves pin area
- [ ] Tooltip text is readable against all backgrounds
- [ ] No performance impact on pin rendering or graph navigation
```

### Story 2: Data Value Display in Tooltips
```
As a PyFlowGraph user
I want to see current pin values in hover tooltips
So that I can debug data flow and verify node execution

Acceptance Criteria:
- [ ] Data pins with values show current value in tooltip
- [ ] Long values are truncated to 50 characters with "..."
- [ ] Complex objects show type information (e.g., "dict (5 keys)")  
- [ ] Null/None values display as "None"
- [ ] Values update in real-time as execution progresses
```

### Story 3: Pin Hover Visual Effects
```
As a PyFlowGraph user
I want visual feedback when hovering over pins
So that I can clearly see which pin I'm interacting with

Acceptance Criteria:
- [ ] Hovered pins show subtle glow effect (2px outer glow)
- [ ] Pin color brightness increases by 10% on hover
- [ ] Smooth 200ms transition for hover in/out effects
- [ ] Effects work consistently across all pin types and colors
- [ ] No performance impact on smooth hover interactions
```

### Story 4: Connection Hover Information  
```
As a PyFlowGraph user
I want to see connection details when hovering over connection lines
So that I can understand data flow between specific nodes

Acceptance Criteria:
- [ ] Hovering over connections shows source and destination info
- [ ] Tooltip format: "SourceNode.pin_name -> DestNode.pin_name"
- [ ] Connection type is displayed in tooltip
- [ ] Connection visual feedback: width increase + brightness boost
- [ ] Smooth transitions for connection hover effects
```

### Story 5: Type Compatibility Visual Feedback
```
As a PyFlowGraph user  
I want visual indicators for pin compatibility when creating connections
So that I can immediately see which pins can connect to each other

Acceptance Criteria:
- [ ] Compatible pins show green glow during connection creation
- [ ] Incompatible pins show red glow when connection attempted
- [ ] Same-type exact matches show blue highlight
- [ ] Visual feedback appears immediately on hover during drag
- [ ] Feedback clears immediately when connection drag ends
```

## Testing Requirements

### Unit Tests
- Tooltip text generation for all pin types
- Hover event handling and cleanup
- Value formatting and truncation logic
- Visual effect application/removal

### Integration Tests  
- Tooltip display across different zoom levels
- Performance with large graphs (100+ nodes)
- Interaction with existing color system
- Accessibility with screen readers

### User Acceptance Testing
- New user onboarding with tooltip guidance
- Experienced user productivity improvements
- Type debugging workflow validation
- Cross-browser tooltip rendering consistency

## Success Criteria

### Phase 1 Success Metrics
- ✅ All pins show informative tooltips on hover
- ✅ No measurable performance degradation
- ✅ Tooltips integrate seamlessly with existing UI
- ✅ User feedback confirms improved type understanding

### Phase 2 Success Metrics
- ✅ Connection information readily available via hover
- ✅ Visual feedback enhances interaction clarity
- ✅ Reduced trial-and-error in connection creation

### Phase 3 Success Metrics
- ✅ Advanced users adopt optional type label features
- ✅ Type compatibility system reduces invalid connection attempts
- ✅ Overall user satisfaction with type visibility improvements

## Risk Mitigation

### Performance Risks
- **Risk**: Tooltip generation impacts hover responsiveness
- **Mitigation**: Cache tooltip strings, use lazy generation

### UX Risks  
- **Risk**: Tooltip clutter or excessive visual noise
- **Mitigation**: Follow 500ms delay standard, subtle visual effects only

### Compatibility Risks
- **Risk**: Conflicts with existing hover behaviors
- **Mitigation**: Thorough testing with current context menus and selection

## Appendix: Industry Research Summary

**Grasshopper**: "Hover over pins for tooltips with type and default value info"
**Dynamo**: "Hover over a Port to see a tooltip containing the data type expected"  
**n8n**: "Color-coded ports make this concept easy and intuitive for end-users"
**Blender**: Users report tooltip absence in node editors as "quite a huge hindrance"

This enhancement brings PyFlowGraph in line with established industry patterns while leveraging the existing robust color-coding system as a foundation for improved user experience.
# PyFlowGraph UI/UX Specifications: Undo/Redo & Node Grouping

## Executive Summary

This document provides comprehensive UI/UX specifications for implementing undo/redo functionality and node grouping visual design in PyFlowGraph. The specifications prioritize professional node editor standards, accessibility compliance, and seamless integration with the existing dark theme aesthetic.

## Design Philosophy

### Core Principles
- **Professional Familiarity**: Follow established patterns from industry-standard node editors (Blender, Unreal Blueprint, Maya Hypergraph)
- **Visual Hierarchy**: Clear distinction between different interaction states and element types
- **Accessibility First**: WCAG 2.1 AA compliance with keyboard navigation and screen reader support
- **Contextual Clarity**: Visual feedback that clearly communicates system state and available actions
- **Consistent Theming**: Seamless integration with existing dark theme (#2E2E2E background, #E0E0E0 text)

### Target Users
- **Primary**: Professional developers familiar with visual scripting tools
- **Secondary**: Technical users new to node-based programming
- **Accessibility**: Users requiring keyboard-only navigation and screen reader support

## Part 1: Undo/Redo Interface Specifications

### 1.1 Menu Integration

#### Edit Menu Enhancement
**Location**: Existing Edit menu in main menu bar  
**Position**: Top of Edit menu, before existing items

```
Edit Menu Structure:
┌─────────────────────┐
│ ✓ Undo [Ctrl+Z]     │ ← New
│ ✓ Redo [Ctrl+Y]     │ ← New  
│ ✓ Undo History...   │ ← New
│ ――――――――――――――――――― │
│ ✓ Add Node          │ ← Existing
│ ――――――――――――――――――― │
│ ✓ Settings          │ ← Existing
└─────────────────────┘
```

**Visual States**:
- **Enabled**: Standard menu item appearance (#E0E0E0 text)
- **Disabled**: Grayed out text (#707070) when no operations available
- **Operation Description**: Dynamic text showing specific operation (e.g., "Undo Delete Node")

#### Accessibility Requirements
- **Keyboard Navigation**: Full Tab/Arrow key navigation support
- **Screen Reader**: Descriptive aria-labels with operation details
- **Mnemonics**: Alt+E,U for Undo, Alt+E,R for Redo
- **Status Announcements**: Screen reader announcements for operation completion

### 1.2 Toolbar Integration

#### Undo/Redo Toolbar Buttons
**Location**: Main toolbar, positioned after file operations  
**Size**: 24x24px icons with 4px padding  
**Icons**: Font Awesome undo (↶) and redo (↷) icons

```
Toolbar Layout:
[New] [Open] [Save] | [Undo] [Redo] | [Add Node] [Run] [Settings]
```

**Button States**:
- **Enabled**: 
  - Background: Transparent
  - Icon: #E0E0E0 (full opacity)
  - Hover: #5A5A5A background, #FFFFFF icon
  - Press: #424242 background
- **Disabled**:
  - Background: Transparent  
  - Icon: #707070 (50% opacity)
  - No hover effects

**Tooltips**:
- **Undo**: "Undo [Operation Name] (Ctrl+Z)"
- **Redo**: "Redo [Operation Name] (Ctrl+Y)"
- **No Operation**: "Nothing to undo/redo"

### 1.3 Undo History Dialog

#### Window Specifications
**Type**: Modal dialog  
**Size**: 400px × 500px (minimum), resizable  
**Position**: Center of main window  
**Title**: "Undo History"

#### Layout Structure
```
┌────────────────────────────────────┐
│ Undo History                    ⊗  │
├────────────────────────────────────┤
│ Operation History:                 │
│ ┌────────────────────────────────┐ │
│ │ ✓ Delete 3 nodes            ◀  │ │ ← Current position
│ │   Move node "Calculate"        │ │
│ │   Create connection            │ │
│ │   Edit code in "Process"       │ │
│ │   Create node "Output"         │ │
│ │   [Earlier operations...]      │ │
│ └────────────────────────────────┘ │
│                                    │
│ Details:                           │
│ ┌────────────────────────────────┐ │
│ │ Operation: Delete nodes        │ │
│ │ Affected: Node_001, Node_002,  │ │
│ │          Node_003              │ │
│ │ Timestamp: 14:23:45            │ │
│ └────────────────────────────────┘ │
│                                    │
│     [Undo to Here] [Close]         │
└────────────────────────────────────┘
```

#### Visual Elements
**Operation List**:
- **Font**: 11pt Segoe UI
- **Line Height**: 24px
- **Current Position**: Bold text with ◀ indicator
- **Future Operations**: Grayed out (#707070)
- **Past Operations**: Normal text (#E0E0E0)

**Selection Behavior**:
- **Click**: Select operation and show details
- **Double-click**: Undo/redo to selected position
- **Keyboard**: Arrow keys for navigation, Enter to execute

#### Accessibility Features
- **Focus Management**: Proper tab order and focus indicators
- **Keyboard Navigation**: Arrow keys, Home/End for list navigation
- **Screen Reader**: Each operation announced with timestamp and description
- **High Contrast**: Alternate row highlighting for readability

### 1.4 Status Bar Integration

#### Undo/Redo Status Indicator
**Location**: Left side of status bar  
**Format**: "[Operation completed] - 15 operations available"

**Examples**:
- "Node deleted - 12 undos available"
- "Connection created - 8 undos, 3 redos available"
- "Ready - No operations to undo"

### 1.5 Keyboard Shortcuts

#### Primary Shortcuts
- **Undo**: Ctrl+Z (Windows/Linux), Cmd+Z (macOS)
- **Redo**: Ctrl+Y, Ctrl+Shift+Z (Windows/Linux), Cmd+Shift+Z (macOS)
- **Undo History**: Ctrl+Alt+Z

#### Customization Support
- **Settings Integration**: Keyboard shortcut customization in Settings dialog
- **Conflict Detection**: Warning when shortcuts conflict with existing bindings
- **Global Scope**: Shortcuts work regardless of current focus (except in text editors)

## Part 2: Node Grouping Visual Design Specifications

### 2.1 Group Selection Visual Feedback

#### Multi-Selection Indicator
**Selection Rectangle**:
- **Color**: #4CAF50 (green) border
- **Width**: 2px dashed line
- **Background**: Transparent with 10% green overlay
- **Animation**: Subtle 2px dash movement (2s duration)

**Selected Nodes Appearance**:
- **Border**: 2px solid #4CAF50 outline
- **Glow Effect**: 4px blur shadow in #4CAF50 (20% opacity)
- **Maintain**: Existing node styling unchanged

#### Context Menu Enhancement
**Group Selection Menu**:
```
Right-click on multiple selected nodes:
┌─────────────────────────┐
│ 🗂️ Create Group...      │ ← New primary option
│ ――――――――――――――――――――――― │
│ ✂️ Cut                  │ ← Existing
│ 📋 Copy                 │ ← Existing
│ 🗑️ Delete               │ ← Existing
│ ――――――――――――――――――――――― │
│ ⚙️ Properties...        │ ← Existing
└─────────────────────────┘
```

### 2.2 Group Creation Dialog

#### Dialog Layout
**Type**: Modal dialog  
**Size**: 380px × 280px (fixed)  
**Position**: Center of main window

```
┌────────────────────────────────────┐
│ Create Node Group               ⊗  │
├────────────────────────────────────┤
│ Group Name:                        │
│ ┌────────────────────────────────┐ │
│ │ [Auto-generated name]          │ │
│ └────────────────────────────────┘ │
│                                    │
│ Description: (Optional)            │
│ ┌────────────────────────────────┐ │
│ │                                │ │
│ │                                │ │
│ └────────────────────────────────┘ │
│                                    │
│ ☑ Generate interface pins         │
│ ☑ Collapse after creation         │
│                                    │
│ Selected Nodes: 5                  │
│ External Connections: 8            │
│                                    │
│       [Cancel] [Create Group]      │
└────────────────────────────────────┘
```

#### Validation Feedback
**Error States**:
- **Empty Name**: Red border on name field with tooltip "Group name required"
- **Duplicate Name**: Warning icon with "Group name already exists"
- **Invalid Selection**: Disabled Create button with explanatory text

### 2.3 Collapsed Group Node Design

#### Visual Structure
**Overall Appearance**:
- **Shape**: Rounded rectangle (10px border radius)
- **Size**: Minimum 120px × 80px, auto-expand for pin count
- **Color Scheme**: Distinct from regular nodes (#455A64 background)
- **Border**: 2px solid #607D8B when unselected, #4CAF50 when selected

#### Group Node Layout
```
┌────────────────────────────────────┐
│ 🗂️ Data Processing                │ ← Header with icon and name
├────────────────────────────────────┤
│ Input1    ●                        │ ← Interface pins (left side)
│ Input2    ●                        │
│ Config    ●                        │
│                                    │
│           (5 nodes inside)         │ ← Center content area
│                                    │
│                        ● Output1   │ ← Interface pins (right side)
│                        ● Output2   │
└────────────────────────────────────┘
```

#### Header Design
- **Background**: Darker variant of group color (#37474F)
- **Icon**: 🗂️ (folder icon) at 16px size
- **Title**: Bold 12pt font, truncate with ellipsis if too long
- **Expand/Collapse Button**: ⊞ (expand) / ⊟ (collapse) on right side

#### Pin Interface
**Input Pins** (Left Side):
- **Position**: Vertically distributed with 8px spacing
- **Style**: Standard pin appearance with type-based coloring
- **Labels**: Pin names with 8pt font, right-aligned

**Output Pins** (Right Side):
- **Position**: Vertically distributed with 8px spacing  
- **Style**: Standard pin appearance with type-based coloring
- **Labels**: Pin names with 8pt font, left-aligned

#### Center Content Area
**Collapsed State**:
- **Text**: "(X nodes inside)" in 10pt italic font
- **Color**: #90A4AE (secondary text color)
- **Background**: Subtle texture pattern (optional)

### 2.4 Expanded Group Visualization

#### Group Boundary Indicator
**Visual Boundary**:
- **Type**: Dashed outline around grouped nodes
- **Color**: #607D8B (group theme color)
- **Width**: 2px dashed line
- **Corner Radius**: 8px
- **Padding**: 20px margin from outermost nodes

#### Header Banner
**Position**: Top of group boundary  
**Height**: 32px  
**Content**: Group name, collapse button, and breadcrumb navigation

```
Group Boundary Layout:
┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
  🗂️ Data Processing  [⊟] │ Main Graph > Processing  
├ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤
│                                                   │
│  [Node 1] ──── [Node 2]                         │
│     │             │                              │
│  [Node 3] ──── [Node 4] ──── [Node 5]           │
│                                                   │
└ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

#### Interface Pin Connections
**External Connections**:
- **Visual**: Bezier curves extending from group boundary to external nodes
- **Color**: Type-based coloring with 60% opacity when group is expanded
- **Interaction**: Clicking shows which internal node the connection maps to

### 2.5 Group Navigation System

#### Breadcrumb Navigation
**Location**: Top toolbar area when inside groups  
**Style**: Hierarchical navigation with separators

```
Navigation Bar:
┌────────────────────────────────────────────────────┐
│ 🏠 Main Graph › 🗂️ Data Processing › 🗂️ Filtering │
└────────────────────────────────────────────────────┘
```

**Interactive Elements**:
- **Clickable Segments**: Each level clickable to navigate directly
- **Current Level**: Bold text, non-clickable
- **Separators**: › symbol with subtle styling
- **Home Icon**: 🏠 for root graph level

#### Quick Navigation Controls
**Keyboard Shortcuts**:
- **Enter Group**: Double-click or Enter key
- **Exit Group**: Escape key or breadcrumb navigation
- **Up One Level**: Alt+Up Arrow
- **Navigate History**: Alt+Left/Right arrows

### 2.6 Nested Group Visualization

#### Depth Indication
**Visual Hierarchy**:
- **Level 0** (Root): No special indication
- **Level 1**: Light blue border tint (#E3F2FD)
- **Level 2**: Light green border tint (#E8F5E8)
- **Level 3+**: Alternating warm tints (#FFF3E0, #FCE4EC)

#### Maximum Depth Warning
**At Depth 8+**:
- **Warning Icon**: ⚠️ in group header
- **Tooltip**: "Approaching maximum nesting depth (10 levels)"
- **Visual Cue**: Orange-tinted group border

**At Maximum Depth (10)**:
- **Disabled**: "Create Group" option in context menu
- **Error Message**: "Maximum group nesting depth reached"
- **Visual Cue**: Red-tinted group border

### 2.7 Group Template System UI

#### Template Save Dialog
**Trigger**: Right-click on group → "Save as Template"  
**Size**: 400px × 320px

```
┌────────────────────────────────────┐
│ Save Group Template             ⊗  │
├────────────────────────────────────┤
│ Template Name:                     │
│ ┌────────────────────────────────┐ │
│ │ [Suggested name]               │ │
│ └────────────────────────────────┘ │
│                                    │
│ Category:                          │
│ ┌────────────────────────────────┐ │
│ │ [Data Processing]      ▼       │ │
│ └────────────────────────────────┘ │
│                                    │
│ Description:                       │
│ ┌────────────────────────────────┐ │
│ │                                │ │
│ │                                │ │
│ └────────────────────────────────┘ │
│                                    │
│ Tags: (comma-separated)            │
│ ┌────────────────────────────────┐ │
│ │ filtering, data, preprocessing  │ │
│ └────────────────────────────────┘ │
│                                    │
│        [Cancel] [Save Template]    │
└────────────────────────────────────┘
```

#### Template Browser
**Access**: File Menu → "Browse Group Templates" or toolbar button  
**Type**: Dockable panel (similar to existing output log)

```
Template Browser Panel:
┌────────────────────────────────────┐
│ Group Templates                    │
├────────────────────────────────────┤
│ Search: [________________] 🔍      │
│                                    │
│ Categories:                        │
│ ▼ Data Processing (3)              │
│   📁 Filtering Pipeline            │
│   📁 Data Validation               │
│   📁 Format Conversion             │
│ ▼ Math Operations (2)              │
│   📁 Statistics Bundle             │
│   📁 Linear Algebra                │
│ ▶ UI Controls (1)                  │
│                                    │
│ [Template Preview Area]            │
│                                    │
│     [Insert Template]              │
└────────────────────────────────────┘
```

### 2.8 Accessibility Compliance

#### Keyboard Navigation
**Group Operations**:
- **Tab Navigation**: Through all group elements and pins
- **Arrow Keys**: Navigate within group boundaries
- **Space/Enter**: Expand/collapse groups
- **Escape**: Exit group view

#### Screen Reader Support
**Announcements**:
- **Group Creation**: "Group created with 5 nodes"
- **Navigation**: "Entered group: Data Processing, level 2"
- **Pin Mapping**: "Input pin connects to internal node Calculate"

#### High Contrast Mode
**Enhanced Visibility**:
- **Group Boundaries**: Increase border width to 3px
- **Color Contrast**: Ensure 4.5:1 minimum contrast ratio
- **Focus Indicators**: Bold 3px focus outlines
- **Text Scaling**: Support up to 200% zoom without layout breaks

## Part 3: Technical Implementation Guidelines

### 3.1 QSS Styling Integration

#### New Style Classes
```css
/* Undo/Redo Toolbar Buttons */
QToolButton#undoButton {
    background-color: transparent;
    border: none;
    color: #E0E0E0;
    padding: 4px;
}

QToolButton#undoButton:hover {
    background-color: #5A5A5A;
    color: #FFFFFF;
}

QToolButton#undoButton:disabled {
    color: #707070;
}

/* Group Node Styling */
QGraphicsRectItem.groupNode {
    background-color: #455A64;
    border: 2px solid #607D8B;
    border-radius: 10px;
}

QGraphicsRectItem.groupNode:selected {
    border-color: #4CAF50;
}

/* Group Boundary */
QGraphicsPathItem.groupBoundary {
    stroke: #607D8B;
    stroke-width: 2px;
    stroke-dasharray: 8,4;
    fill: none;
}
```

### 3.2 Animation Specifications

#### Smooth Transitions
**Group Collapse/Expand**:
- **Duration**: 300ms
- **Easing**: QEasingCurve::OutCubic
- **Properties**: Scale, opacity, position

**Selection Feedback**:
- **Duration**: 150ms  
- **Easing**: QEasingCurve::OutQuart
- **Properties**: Border color, glow intensity

### 3.3 Performance Considerations

#### Large Graph Optimization
**Group Rendering**:
- **LOD System**: Simplified rendering when zoomed out
- **Culling**: Hide internal nodes when group is collapsed
- **Lazy Loading**: Load group contents only when expanded

**Memory Management**:
- **Weak References**: For undo/redo command history
- **Pooling**: Reuse visual elements for repeated operations
- **Cleanup**: Automatic cleanup of old undo operations

## Conclusion

These specifications provide a comprehensive foundation for implementing professional-grade undo/redo functionality and node grouping in PyFlowGraph. The design maintains consistency with existing UI patterns while introducing industry-standard features that will significantly enhance user productivity and graph management capabilities.

The accessibility features ensure compliance with WCAG 2.1 AA standards, making the application usable by a broader range of developers. The visual design leverages familiar patterns from established node editors while maintaining PyFlowGraph's unique identity and dark theme aesthetic.
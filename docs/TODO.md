# PyFlowGraph Enhancement TODO List

## Priority 1: Feature Parity (Must Have)

### Undo/Redo System
- Implement multi-level undo/redo with Command Pattern
- Add keyboard shortcuts (Ctrl+Z/Ctrl+Y)
- Maintain history during session (20-50 steps minimum)
- Show undo history in menu

### Node Grouping/Containers
- Implement collapsible subgraphs (like Unreal Engine Blueprints)
- Support multiple abstraction levels (Functions, Macros, Collapsed Graphs)
- Enable saving groups as reusable templates
- Add custom I/O pins for groups
- Essential for managing complexity in large graphs

## Priority 2: Performance & Usability (Should Have)

### Shared Subprocess Execution Model
- Replace isolated subprocess per node with shared Python process
- Enable direct object passing between nodes (10-100x performance gain)
- Simplify data transfer between nodes
- Reduce serialization overhead
- Maintain security through sandboxing options

### Pin Type Visibility
- Add type badges/labels on pins (like Unity Visual Scripting)
- Implement hover tooltips showing full type information
- During connection drag: highlight compatible pins, gray out incompatible
- Consider color + shape coding for accessibility
- Show type conversion possibilities

## Priority 3: Advanced Features (Nice to Have)

### Enhanced Debugging Capabilities
- Node isolation testing/debugging
- Syntax highlighting in log output
- Remove emojis from log output
- Implement breakpoints and step-through execution
- Show live data values on connections during execution
- Add data inspection at each node (like Houdini's spreadsheet)
- Display execution order numbers on nodes
- Leverage Python's native debug capabilities (pdb integration)

## Additional Missing Features (From Competitive Analysis)

### Search and Navigation
- Node search palette (Ctrl+Space or Tab)
- Minimap for large graphs
- Bookmarks/markers for quick navigation
- Jump to node by name/type
- Breadcrumb navigation for nested graphs

### Node Library and Discovery
- Categorized node browser
- Favorite/recent nodes panel
- Node documentation tooltips
- Quick node creation from connection drag
- Context-sensitive node suggestions

### Graph Organization
- Alignment and distribution tools
- Auto-layout algorithms
- Comment boxes/sticky notes
- Node coloring/tagging system
- Wire organization (reroute nodes exist but need improvement)

### Data and Type System
- Type conversion nodes
- Generic/template nodes
- Custom type definitions
- Array/list operations
- Type validation and error highlighting

### Collaboration and Sharing
- Export/import node groups as packages
- Version control integration (beyond file format)
- Diff visualization for graphs
- Merge conflict resolution tools
- Online node library/marketplace

### Performance and Optimization
- Lazy evaluation options
- Caching/memoization system
- Parallel execution where possible
- Profiling and performance metrics
- Memory usage visualization

### User Experience Enhancements
- Customizable keyboard shortcuts
- Multiple selection modes
- Context-sensitive right-click menus
- Duplicate with connections (Alt+drag)
- Quick connect (Q key connecting)
- Zoom to fit/zoom to selection
- Multiple graph tabs

### Advanced Execution Features
- Conditional execution paths
- Loop constructs with visual feedback
- Error handling and recovery nodes
- Async/await support
- External trigger integration
- Scheduling and automation

### Developer Features
- API for custom node creation
- Plugin system for extensions
- Scripting interface for automation
- Unit testing framework for graphs
- CI/CD integration for graph validation

## Implementation Priority Notes

1. **Critical Gaps**: Undo/Redo and Node Grouping are table stakes - every competitor has these
2. **Performance Win**: Shared subprocess execution could provide 10-100x speedup
3. **Differentiation**: Syntax-highlighted logs and Python-native debugging would set PyFlowGraph apart
4. **Quick Wins**: Pin type visibility and search features are relatively easy to implement with high user value

# PyFlowGraph Development Roadmap

## Vision
Transform PyFlowGraph into a professional-grade workflow automation platform by leveraging our unique "Code as Nodes" philosophy to enable both visual simplicity and programmatic power for enterprise integration scenarios.

## Priority 1: Feature Parity & Core Automation (Must Have)

### Undo/Redo System
- Implement multi-level undo/redo with Command Pattern
- Add keyboard shortcuts (Ctrl+Z/Ctrl+Y)
- Maintain history during session (20-50 steps minimum)
- Show undo history in menu

### Node Grouping/Containers
- Implement collapsible subgraphs for workflow modularity
- Support multiple abstraction levels (Functions, Macros, Collapsed Graphs)
- Enable saving groups as reusable workflow templates
- Add custom I/O pins for groups
- Essential for managing complexity in enterprise automation scenarios

### Integration Connectors
- HTTP/REST API node with authentication support
- Database connectors (PostgreSQL, MySQL, MongoDB)
- File system operations (watch folders, process files)
- Email integration (SMTP, IMAP)
- Webhook receiver nodes for event-driven workflows
- Cloud storage integrations (S3, Azure Blob, Google Cloud Storage)

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

## Priority 3: Advanced Automation Features (Nice to Have)

### Enhanced Debugging Capabilities
- Node isolation testing/debugging
- Syntax highlighting in log output
- Remove emojis from log output
- Implement breakpoints and step-through execution
- Show live data values on connections during execution
- Add data inspection at each node for workflow monitoring
- Display execution order numbers on nodes
- Leverage Python's native debug capabilities (pdb integration)

### Workflow Orchestration
- Scheduling system (cron-like expressions)
- Error handling and retry logic nodes
- Conditional branching and loop constructs
- Parallel execution branches
- Rate limiting and throttling capabilities
- Workflow versioning and rollback

### Data Transformation
- Built-in data mapping and transformation nodes
- JSON/XML/CSV parsing and generation
- Data validation and schema enforcement
- Aggregation and filtering operations
- Template engine integration for dynamic content

## Implementation Priority Notes

1. **Critical Gaps**: Undo/Redo and Node Grouping are essential for professional workflow automation tools
2. **Integration Power**: Native connectors for APIs, databases, and cloud services enable real-world automation
3. **Performance Win**: Shared subprocess execution could provide 10-100x speedup for data processing workflows
4. **Differentiation**: Python-native approach allows unlimited extensibility beyond visual-only platforms
5. **Quick Wins**: Pin type visibility and built-in transformation nodes provide immediate value for automation tasks
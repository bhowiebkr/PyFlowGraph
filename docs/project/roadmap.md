# PyFlowGraph Development Roadmap

## Vision
Transform PyFlowGraph into a professional-grade workflow automation platform by leveraging our unique "Code as Nodes" philosophy to enable both visual simplicity and programmatic power for enterprise integration scenarios.

## Priority 1: Feature Parity & Core Automation (Must Have)

### Undo/Redo System
- Implement multi-level undo/redo with Command Pattern
- Add keyboard shortcuts (Ctrl+Z/Ctrl+Y)
- Maintain history during session (20-50 steps minimum)
- Show undo history in menu

### Single Process Execution Architecture
- Replace isolated subprocess per node with single persistent Python interpreter
- Enable direct object references between nodes (100-1000x performance gain)
- Zero serialization overhead for all data types
- Sequential execution optimized for GPU memory constraints
- Critical for ML/AI workflows with large tensors and real-time processing

### Node Grouping/Containers (Basic Implementation Complete)
- ✅ Basic group creation and selection (Story 3.1 complete)
- Advanced grouping features deferred to future releases
- Focus on core functionality rather than advanced UI features

### Integration Connectors
- HTTP/REST API node with authentication support
- Database connectors (PostgreSQL, MySQL, MongoDB)
- File system operations (watch folders, process files)
- Email integration (SMTP, IMAP)
- Webhook receiver nodes for event-driven workflows
- Cloud storage integrations (S3, Azure Blob, Google Cloud Storage)

## Priority 2: Performance & Usability (Should Have)

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

1. **Critical Performance Revolution**: Single process execution is now Priority 1 - 100-1000x speedup for ML/AI workflows
2. **GPU Memory Optimization**: Sequential execution prevents VRAM conflicts in data science pipelines
3. **Completed Foundation**: Basic node grouping (Story 3.1) provides sufficient organization - advanced features deferred
4. **Integration Power**: Native connectors for APIs, databases, and cloud services enable real-world automation
5. **Zero Overhead**: Direct object references eliminate all serialization bottlenecks
6. **ML/AI Focus**: First-class PyTorch, TensorFlow, JAX integration with persistent namespaces
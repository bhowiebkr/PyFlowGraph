# AI Agents Guide

## Overview

PyFlowGraph supports multiple AI agent workflows for automated development and task management. This guide documents the available agents, their roles, and how they collaborate to complete complex software development tasks.

## Agent Workflows

### BMAD (Bot-Managed Agile Development) Workflow

The BMAD workflow implements a complete Agile development team using AI agents. Each agent has a specific role mirroring traditional software development team members.

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **`/bmad-master`** | **Master Controller** | • Initializes projects<br>• Sets high-level goals<br>• Oversees entire workflow from start to finish<br>• Makes executive decisions |
| **`/bmad-orchestrator`** | **Workflow Coordinator** | • Manages agent interactions and handoffs<br>• Assigns tasks to specialized agents<br>• Ensures correct task sequencing<br>• Monitors workflow progress |
| **`/po`** | **Product Owner** | • Defines project requirements<br>• Creates and prioritizes user stories<br>• Manages product backlog<br>• Represents stakeholder vision |
| **`/analyst`** | **Business Analyst** | • Gathers detailed requirements<br>• Analyzes specifications from Product Owner<br>• Clarifies ambiguities<br>• Documents technical requirements |
| **`/sm`** | **Scrum Master** | • Facilitates agile process<br>• Removes workflow blockers<br>• Maintains agile framework<br>• Ensures smooth team operations |
| **`/architect`** | **System Architect** | • Designs system architecture<br>• Makes technical framework decisions<br>• Ensures scalability and robustness<br>• Creates integration strategies |
| **`/ux-expert`** | **UX/UI Expert** | • Designs user interfaces<br>• Ensures usability and accessibility<br>• Creates design guidelines<br>• Reviews user experience flows |
| **`/dev`** | **Developer** | • Writes and refactors code<br>• Implements user stories<br>• Follows technical specifications<br>• Integrates components |
| **`/qa`** | **Quality Assurance** | • Designs test strategies<br>• Executes test plans<br>• Identifies and reports bugs<br>• Verifies functionality meets requirements |
| **`/pm`** | **Project Manager** | • Tracks project progress<br>• Manages timelines and milestones<br>• Reports project status<br>• Coordinates resource allocation |

### SuperClaude Command Framework

The SuperClaude Framework v3.0 provides 10+ specialized command agents that enhance development workflows with intelligent, context-aware automation. Each command includes specific flags and cognitive personas that auto-activate based on context.

#### Core Command Agents

| Command | Purpose | Key Features | Example Usage |
|---------|---------|--------------|---------------|
| **`/sc:analyze`** | **Code Analysis** | • Quality assessment<br>• Security scanning<br>• Performance profiling<br>• Architecture review | `/sc:analyze src/ --focus security --depth deep` |
| **`/sc:build`** | **Build Management** | • Compilation & packaging<br>• Error handling<br>• Optimization<br>• Environment configs | `/sc:build --type prod --optimize` |
| **`/sc:cleanup`** | **Code Maintenance** | • Dead code removal<br>• Import optimization<br>• File organization<br>• Safe refactoring | `/sc:cleanup --dead-code --safe src/` |
| **`/sc:design`** | **System Design** | • Architecture diagrams<br>• API specifications<br>• Component interfaces<br>• Database schemas | `/sc:design --type api user-management` |
| **`/sc:document`** | **Documentation** | • Inline documentation<br>• API docs<br>• User guides<br>• Component specs | `/sc:document --type api src/controllers/` |
| **`/sc:estimate`** | **Project Estimation** | • Time estimates<br>• Complexity analysis<br>• Resource planning<br>• Risk assessment | `/sc:estimate "payment system" --detailed` |
| **`/sc:explain`** | **Code Explanation** | • Concept clarification<br>• Code walkthroughs<br>• Learning resources<br>• Examples | `/sc:explain async/await --beginner` |
| **`/sc:git`** | **Git Operations** | • Smart commits<br>• Branch management<br>• Merge strategies<br>• Workflow automation | `/sc:git commit --smart-message` |
| **`/sc:implement`** | **Feature Development** | • Complete features<br>• Component creation<br>• API implementation<br>• Framework integration | `/sc:implement user authentication system` |
| **`/sc:improve`** | **Code Enhancement** | • Quality improvements<br>• Performance optimization<br>• Maintainability<br>• Safe refactoring | `/sc:improve --preview src/component.js` |

#### Command Flags and Options

Each command supports various flags for customization:

- **Analysis Flags**: `--focus` (quality/security/performance), `--depth` (quick/deep), `--format` (text/json/report)
- **Build Flags**: `--type` (dev/prod/test), `--clean`, `--optimize`, `--verbose`
- **Cleanup Flags**: `--dead-code`, `--imports`, `--files`, `--safe`
- **Design Flags**: `--type` (architecture/api/component/database), `--format` (diagram/spec/code)
- **Document Flags**: `--type` (inline/external/api/guide), `--style` (brief/detailed)
- **Improvement Flags**: `--preview`, `--safe`

#### Cognitive Personas

SuperClaude includes 9 cognitive personas that automatically activate based on the task context:

- **Architect** - System design and architecture decisions
- **Developer** - Code implementation and optimization
- **Analyst** - Requirements analysis and specifications
- **QA Engineer** - Testing and quality assurance
- **DevOps** - Deployment and infrastructure
- **Security Expert** - Security analysis and hardening
- **Documentation Writer** - Technical documentation
- **Project Manager** - Planning and estimation
- **Code Reviewer** - Code quality and best practices

## Agent Collaboration Patterns

### Sequential Processing

Agents work in a defined sequence, with each agent completing their task before passing results to the next agent.

```
Product Owner → Analyst → Architect → Developer → QA → Deployment
```

### Parallel Processing

Multiple agents work simultaneously on independent tasks, with results merged by the orchestrator.

```
        ┌─→ Researcher ─┐
Orchestrator ─┼─→ Strategist ─┼─→ Orchestrator (Synthesis)
        └─→ Analyst   ─┘
```

### Iterative Refinement

Agents collaborate in cycles, refining outputs through multiple iterations.

```
Developer ↔ QA ↔ Architect
    ↓         ↓        ↓
  Code     Tests   Design
```

## Best Practices

### Agent Selection

- **Match agents to task complexity** - Simple tasks may only need 2-3 agents
- **Consider dependencies** - Ensure prerequisite agents complete first
- **Balance specialization** - Too many agents can create overhead

### Communication Protocols

- **Clear handoffs** - Define what each agent passes to the next
- **Consistent formats** - Use standardized data structures
- **Context preservation** - Maintain project context across agents

### Performance Optimization

- **Minimize redundancy** - Avoid duplicate work between agents
- **Cache results** - Reuse outputs when possible
- **Monitor bottlenecks** - Identify and optimize slow agents

## Integration with PyFlowGraph

### Node-Based Agent Workflows

PyFlowGraph can visualize and execute agent workflows as node graphs:

1. **Agent Nodes** - Each agent becomes a node with specific inputs/outputs
2. **Data Flow** - Information flows between agents via connections
3. **Execution** - The graph executor manages agent orchestration
4. **Monitoring** - Real-time visualization of agent progress

### SuperClaude Command Integration

#### Command Nodes

Each SuperClaude command can be represented as a PyFlowGraph node:

```python
# Example: Analysis Node
def sc_analyze_node(source_path: str, focus: str = "quality") -> dict:
    """SuperClaude analysis agent node"""
    # Executes: /sc:analyze {source_path} --focus {focus}
    return {"quality_score": 0, "issues": [], "recommendations": []}

# Example: Implementation Node
def sc_implement_node(feature_spec: str, framework: str = "") -> dict:
    """SuperClaude implementation agent node"""
    # Executes: /sc:implement {feature_spec} --framework {framework}
    return {"files_created": [], "tests": [], "documentation": ""}

# Example: Git Operations Node
def sc_git_node(operation: str, smart_commit: bool = True) -> dict:
    """SuperClaude git operations node"""
    # Executes: /sc:git {operation} --smart-commit
    return {"commit_hash": "", "branch": "", "message": ""}
```

#### Workflow Examples

##### Complete Feature Development Pipeline

```python
# 1. Design the feature
design = sc_design_node("user authentication", type="api")

# 2. Estimate effort
estimate = sc_estimate_node(design["specification"], detailed=True)

# 3. Implement the feature
implementation = sc_implement_node(design["specification"])

# 4. Analyze code quality
analysis = sc_analyze_node(implementation["files_created"], focus="security")

# 5. Generate documentation
docs = sc_document_node(implementation["files_created"], type="api")

# 6. Commit with smart message
commit = sc_git_node("commit", smart_message=True)
```

##### Code Quality Pipeline

```python
# 1. Analyze existing code
analysis = sc_analyze_node("src/", focus="quality", depth="deep")

# 2. Clean up code
cleanup = sc_cleanup_node("src/", dead_code=True, safe=True)

# 3. Improve code quality
improvements = sc_improve_node(cleanup["modified_files"], preview=False)

# 4. Document changes
documentation = sc_document_node(improvements["files"], style="detailed")
```

### BMAD + SuperClaude Hybrid Workflows

Combine BMAD agents with SuperClaude commands for comprehensive automation:

```python
# BMAD defines requirements
requirements = bmad_po_node("Create user dashboard")
specifications = bmad_analyst_node(requirements)
architecture = bmad_architect_node(specifications)

# SuperClaude implements
implementation = sc_implement_node(architecture["design"])
analysis = sc_analyze_node(implementation["files"], focus="all")

# BMAD validates
qa_results = bmad_qa_node(implementation)
pm_report = bmad_pm_node(qa_results)
```

## Advanced Topics

### Dynamic Agent Creation

Agents can be created dynamically based on task requirements:

- **Skill-based selection** - Choose agents with required capabilities
- **Load balancing** - Distribute work across available agents
- **Adaptive workflows** - Modify agent teams based on progress

### Agent Memory and Learning

- **Shared knowledge base** - Agents access common project information
- **Learning from feedback** - Agents improve through iteration
- **Pattern recognition** - Identify successful collaboration patterns

### Error Handling and Recovery

- **Graceful degradation** - Continue with reduced agent team if needed
- **Checkpoint/restart** - Save progress and resume from failures
- **Fallback strategies** - Alternative approaches when primary fails

## PyFlowGraph-Specific Usage Examples

### Analyzing the Node System

```bash
# Analyze node system architecture
/sc:analyze src/node.py src/pin.py src/connection.py --focus architecture

# Check for security issues in execution engine
/sc:analyze src/graph_executor.py --focus security --depth deep
```

### Building and Testing

```bash
# Build the PyFlowGraph application
/sc:build --type dev --verbose

# Run comprehensive tests
/sc:build --type test run_test_gui.bat
```

### Code Improvements

```bash
# Clean up unused imports in the entire codebase
/sc:cleanup src/ --imports --safe

# Improve node editor performance
/sc:improve src/node_editor_view.py --preview
```

### Documentation Generation

```bash
# Document the command system
/sc:document src/commands/ --type api --style detailed

# Create user guide for node creation
/sc:explain "How to create custom nodes in PyFlowGraph" --examples
```

### Feature Implementation

```bash
# Implement a new node type
/sc:implement "Create a debug node that logs all inputs and outputs"

# Design a plugin system
/sc:design --type architecture "Plugin system for custom node types"
```

### Git Workflow

```bash
# Smart commit after implementing a feature
/sc:git commit --smart-message

# Create feature branch with proper naming
/sc:git branch feature/node-search-functionality
```

## Conclusion

The AI agent system in PyFlowGraph provides powerful automation capabilities for software development workflows. With both BMAD's structured Agile approach and SuperClaude's specialized command agents, developers can:

1. **Automate complex workflows** - Chain multiple agents for end-to-end automation
2. **Maintain code quality** - Use analysis and improvement agents continuously
3. **Accelerate development** - Leverage implementation and build agents
4. **Ensure documentation** - Auto-generate comprehensive documentation
5. **Optimize processes** - Apply intelligent git workflows and estimations

Whether using the structured BMAD workflow for traditional Agile development or the flexible SuperClaude command framework for specific tasks, the key is selecting the right agents for the task and orchestrating them effectively to achieve project goals.

## Resources

- **SuperClaude GitHub**: <https://github.com/SuperClaude-Org/SuperClaude_Framework>
- **SuperClaude Website**: <https://superclaude-org.github.io/>
- **PyFlowGraph Integration**: [SuperClaude Integration Guide](./superclaude-integration.md)
- **BMAD Documentation**: Available in project configuration

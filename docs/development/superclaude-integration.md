# SuperClaude Integration Guide

## Overview

PyFlowGraph has been integrated with the SuperClaude Framework v3.0, enabling advanced AI agent workflows for automated development tasks. This guide covers installation, configuration, and usage of SuperClaude within the PyFlowGraph project.

## Installation Status

✅ **SuperClaude v3.0.0.2** installed globally via `uv tool`
✅ **Configuration** created at `.superclaude/config.json`
✅ **MCP Server** (serena) connected and operational

## Installation Steps

### Prerequisites
- Python 3.12+ (Python 3.13.0 installed)
- uv package manager (installed at `C:\Users\howard\.local\bin\uvx.exe`)
- Git for version control

### Installation Process

1. **Install SuperClaude globally:**
   ```bash
   uv tool install SuperClaude
   uv tool update-shell  # Add to PATH
   ```

2. **Run quick setup:**
   ```bash
   SuperClaude install --quick --yes
   ```

3. **Verify installation:**
   ```bash
   SuperClaude --version  # Should show v3.0.0
   ```

## Project Configuration

### Configuration File Location
`.superclaude/config.json` - Main configuration for SuperClaude integration

### Key Configuration Settings

```json
{
  "project": {
    "name": "PyFlowGraph",
    "type": "python"
  },
  "agents": {
    "workflows": ["bmad", "superclaude"],
    "default_workflow": "superclaude"
  }
}
```

## Available Agent Workflows

### BMAD Workflow
Full Agile development team simulation with 10 specialized agents:
- `/bmad-master` - Master controller
- `/bmad-orchestrator` - Workflow coordinator
- `/po` - Product Owner
- `/analyst` - Business Analyst
- `/sm` - Scrum Master
- `/architect` - System Architect
- `/ux-expert` - UX/UI Expert
- `/dev` - Developer
- `/qa` - Quality Assurance
- `/pm` - Project Manager

### SuperClaude Workflow
Flexible task-oriented agents:
- `orchestrator` - Task decomposition and delegation
- `researcher` - Information gathering
- `strategist` - Planning and design
- `coder` - Implementation
- `writer` - Documentation
- `critic` - Quality review

## Usage Examples

### Basic Agent Commands

```bash
# Start BMAD workflow for feature development
/bmad-master "Implement dark mode for the node editor"

# Use specific agent
/dev "Refactor the graph_executor.py module"

# Run quality checks
/qa "Test the node connection system"
```

### PyFlowGraph-Specific Integration

The integration enables:
1. **Automatic Node Generation** - Agents can create node definitions
2. **Workflow Visualization** - Agent workflows as node graphs
3. **Subprocess Isolation** - Secure agent execution
4. **Persistent Logging** - Agent activity tracking

### Example: Creating a Feature with BMAD

```bash
# 1. Product Owner defines requirements
/po "Create a node search feature with fuzzy matching"

# 2. Analyst refines specifications
/analyst "Analyze search requirements and define acceptance criteria"

# 3. Architect designs solution
/architect "Design search system architecture"

# 4. Developer implements
/dev "Implement the search feature"

# 5. QA tests
/qa "Test search functionality"
```

## Node System Integration

### Agent Nodes
Agents can be represented as nodes in PyFlowGraph:

```python
# Example agent node definition
def orchestrator_agent_node(task_description: str) -> dict:
    """Orchestrator agent node for task management"""
    # Agent logic here
    return {"subtasks": [], "status": "completed"}
```

### Workflow Graphs
Save agent workflows as `.md` graph files in `examples/agent_workflows/`

## File Structure

```
PyFlowGraph/
├── .superclaude/
│   └── config.json         # SuperClaude configuration
├── docs/
│   └── development/
│       ├── ai-agents-guide.md           # Agent documentation
│       └── superclaude-integration.md   # This file
├── logs/
│   └── agents/            # Agent execution logs
└── examples/
    └── agent_workflows/   # Saved agent workflow graphs
```

## Troubleshooting

### Common Issues

1. **Unicode Encoding Errors**
   - Issue: Windows console encoding problems
   - Solution: Errors are cosmetic, functionality works

2. **Agent Not Found**
   - Issue: Agent command not recognized
   - Solution: Ensure SuperClaude is in PATH, restart terminal

3. **MCP Connection Issues**
   - Issue: MCP server not connected
   - Solution: Run `claude mcp list` to check status

### Verification Commands

```bash
# Check SuperClaude version
SuperClaude --version

# List MCP servers
claude mcp list

# Check installation
dir C:\Users\howard\.claude

# View configuration
type .superclaude\config.json
```

## Advanced Features

### Parallel Agent Execution
Configure in `.superclaude/config.json`:
```json
{
  "superclaude": {
    "parallel_execution": true,
    "max_concurrent_agents": 3
  }
}
```

### Custom Agent Creation
Define custom agents for PyFlowGraph-specific tasks:
```python
# In src/agents/custom_agents.py
class GraphOptimizationAgent:
    """Specialized agent for optimizing node graphs"""
    pass
```

### Agent Memory
Agents maintain context across sessions:
- Stored in `C:\Users\howard\.claude\projects\PyFlowGraph\`
- Includes project knowledge, patterns, and decisions

## Best Practices

1. **Use appropriate workflows** - BMAD for full development, SuperClaude for focused tasks
2. **Document agent decisions** - Save important agent outputs
3. **Review agent code** - Always review generated code before committing
4. **Test agent outputs** - Run tests on agent-generated features
5. **Monitor performance** - Check logs for agent execution times

## Integration Roadmap

### Completed
- ✅ SuperClaude v3.0 installation
- ✅ Project configuration
- ✅ Documentation creation

### Planned Enhancements
- [ ] Visual agent workflow editor
- [ ] Agent performance metrics dashboard
- [ ] Custom PyFlowGraph agent library
- [ ] Agent node templates
- [ ] Automated testing integration

## Resources

- [SuperClaude GitHub](https://github.com/SuperClaude-Org/SuperClaude_Framework)
- [Agent Documentation](./ai-agents-guide.md)
- [PyFlowGraph Documentation](../README.md)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review agent logs in `logs/agents/`
3. Consult the SuperClaude documentation
4. Report issues to the PyFlowGraph repository
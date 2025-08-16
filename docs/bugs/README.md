# Bug Tracking

This directory contains bug reports and tracking for PyFlowGraph issues discovered during development and testing.

## GitHub Integration

We maintain bugs in two synchronized locations:
- **Local Documentation**: `docs/bugs/` - Detailed technical documentation (this directory)
- **GitHub Issues**: Project issue tracker - Community visibility and collaboration

See [GitHub Sync Process](github-sync-process.md) for complete synchronization workflow.

## Bug Report Format

Each bug should be documented with:
- **ID**: Unique identifier (BUG-YYYY-MM-DD-###)
- **Title**: Brief description
- **Status**: Open, In Progress, Fixed, Closed
- **Priority**: Critical, High, Medium, Low
- **Component**: Affected system/module
- **GitHub Issue**: Link to corresponding GitHub issue
- **Description**: Detailed issue description
- **Steps to Reproduce**: Clear reproduction steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Impact**: User/system impact assessment
- **Notes**: Additional technical details

## Current Bug List

| ID | Title | Status | Priority | Component | GitHub Issue |
|---|---|---|---|---|---|
| BUG-2025-01-001 | Reroute nodes return None in execution | Open | High | Execution Engine | [#35](https://github.com/bhowiebkr/PyFlowGraph/issues/35) |

## Quick Actions

### Create GitHub Issue for Existing Bug
```bash
# Example: Create issue for BUG-2025-01-001
gh issue create --title "BUG-2025-01-001: Reroute nodes return None in execution" \
  --body "Detailed technical information: docs/bugs/BUG-2025-01-001-reroute-execution-data-loss.md" \
  --label "bug,high-priority,execution"
```

### Sync Local Bug to GitHub
1. Update local bug file with latest information
2. Create or update GitHub issue
3. Add GitHub issue number to local bug file header
4. Commit changes to git

## Bug Categories

- **Execution**: Graph execution and data flow issues
- **UI**: User interface and interaction problems  
- **File**: File operations and persistence issues
- **Node System**: Node creation, editing, and management
- **Undo/Redo**: Command system and state management
- **Performance**: Speed and memory issues
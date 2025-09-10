# GitHub Issues Sync Process

This document outlines the process for maintaining bidirectional synchronization between local bug documentation in `docs/bugs/` and GitHub Issues.

## Overview

We maintain bugs in two places:
1. **Local Documentation**: `docs/bugs/` - Detailed technical documentation
2. **GitHub Issues**: Project issue tracker - Community visibility and collaboration

## Manual Sync Process

### Creating a New Bug Report

#### Option A: Start Locally
1. Create detailed bug report in `docs/bugs/BUG-YYYY-MM-DD-###-title.md`
2. Update `docs/bugs/README.md` bug list table
3. Create corresponding GitHub Issue:
   ```bash
   gh issue create --title "BUG-YYYY-MM-DD-###: Title" \
     --body "See docs/bugs/BUG-YYYY-MM-DD-###-title.md for detailed technical information" \
     --label "bug,documentation"
   ```
4. Add GitHub issue number to local bug file header
5. Commit changes to git

#### Option B: Start with GitHub Issue
1. Create GitHub Issue with bug label
2. Note the issue number (e.g., #42)
3. Create local bug file: `docs/bugs/BUG-YYYY-MM-DD-###-title.md`
4. Include GitHub issue reference in header
5. Update `docs/bugs/README.md` bug list table
6. Commit changes to git

### Bug File Header Format

Add GitHub sync information to each bug file:

```markdown
# BUG-YYYY-MM-DD-###: Title

**Status**: Open  
**Priority**: High  
**Component**: Component Name  
**GitHub Issue**: #42  
**Created**: YYYY-MM-DD  
**Last Sync**: YYYY-MM-DD  
```

### Status Synchronization

| Local Status | GitHub Status | Action |
|---|---|---|
| Open | Open | No action needed |
| In Progress | Open + "in progress" label | Add label to GitHub |
| Fixed | Closed + "fixed" label | Close issue with comment |
| Closed | Closed | No action needed |

### Update Process

#### When Updating Local Bug File
1. Make changes to local markdown file
2. Update "Last Sync" date in header
3. Add comment to GitHub Issue:
   ```bash
   gh issue comment 42 --body "Updated technical documentation in docs/bugs/BUG-YYYY-MM-DD-###-title.md"
   ```

#### When GitHub Issue Updated
1. Review GitHub Issue changes
2. Update corresponding local bug file
3. Update "Last Sync" date
4. Commit changes to git

## GitHub CLI Commands Reference

### Common Operations
```bash
# Create issue from local bug
gh issue create --title "BUG-2025-01-001: Reroute nodes return None" \
  --body "Detailed technical info: docs/bugs/BUG-2025-01-001-reroute-execution-data-loss.md" \
  --label "bug,high-priority,execution"

# List all bug issues
gh issue list --label "bug"

# Close issue as fixed
gh issue close 42 --comment "Fixed in commit abc123. See updated docs/bugs/ for details."

# Add labels
gh issue edit 42 --add-label "in-progress"

# View issue details
gh issue view 42
```

## Automation Options

### GitHub Actions Workflow (Recommended)

Create `.github/workflows/bug-sync.yml` to automate:
- Create GitHub Issue when new bug file added to docs/bugs/
- Update issue labels when bug status changes
- Comment on issues when bug files updated

### Manual Scripts

Create utility scripts in `scripts/` directory:
- `sync-bugs-to-github.py` - Push local changes to GitHub
- `sync-bugs-from-github.py` - Pull GitHub updates to local files
- `validate-bug-sync.py` - Check sync status

## Bug Labels

Standard GitHub labels for bug categorization:

| Label | Description | Usage |
|---|---|---|
| `bug` | Bug report | All bug issues |
| `critical` | Critical priority | System-breaking bugs |
| `high-priority` | High priority | Major functionality issues |
| `medium-priority` | Medium priority | Minor functionality issues |
| `low-priority` | Low priority | Cosmetic/enhancement bugs |
| `execution` | Execution engine | Graph execution bugs |
| `ui` | User interface | UI/UX bugs |
| `file-ops` | File operations | File I/O bugs |
| `node-system` | Node system | Node creation/editing bugs |
| `undo-redo` | Undo/redo | Command system bugs |
| `performance` | Performance | Speed/memory bugs |
| `in-progress` | Work in progress | Currently being worked on |
| `needs-repro` | Needs reproduction | Cannot reproduce issue |
| `duplicate` | Duplicate issue | Duplicate of another issue |

## Workflow Examples

### Example 1: New Bug Discovery
1. Discover reroute node execution bug during testing
2. Create `docs/bugs/BUG-2025-01-002-new-issue.md` with full details
3. Run: `gh issue create --title "BUG-2025-01-002: New Issue" --body "See docs/bugs/BUG-2025-01-002-new-issue.md" --label "bug,high-priority"`
4. Add GitHub issue number to bug file header
5. Commit and push changes

### Example 2: Bug Status Update
1. Fix bug in code
2. Update local bug file status to "Fixed"
3. Run: `gh issue close 42 --comment "Fixed in commit abc123"`
4. Commit local file changes

### Example 3: Community Report
1. Community reports bug via GitHub Issue #45
2. Create `docs/bugs/BUG-2025-01-003-community-report.md`
3. Add GitHub Issue #45 reference to header
4. Update README.md bug list
5. Commit changes

## Benefits

- **Dual Tracking**: Detailed technical docs + community visibility
- **Version Control**: Bug documentation versioned with code
- **Searchability**: Local grep + GitHub search
- **Integration**: Links between documentation and issue tracking
- **Automation**: Potential for automated synchronization
- **Collaboration**: Community can reference detailed technical info
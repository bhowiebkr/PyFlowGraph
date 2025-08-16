#!/usr/bin/env python3
"""
Bug Sync Automation Script

Utility for synchronizing bugs between local docs/bugs/ files and GitHub Issues.
Requires GitHub CLI (gh) to be installed and authenticated.
"""

import os
import re
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class BugSyncManager:
    """Manages synchronization between local bug files and GitHub Issues."""
    
    def __init__(self, bugs_dir: str = "docs/bugs"):
        self.bugs_dir = Path(bugs_dir)
        self.project_root = Path.cwd()
        
    def parse_bug_file(self, file_path: Path) -> Dict:
        """Parse a local bug file to extract metadata."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract metadata from header
        metadata = {}
        lines = content.split('\n')
        
        # Extract title from first line - flexible pattern for various ID formats
        title_match = re.match(r'^#\s*(BUG-\d{4}-\d{2}-\d+):\s*(.+)$', lines[0].strip())
        if title_match:
            metadata['id'] = title_match.group(1)
            metadata['title'] = title_match.group(2)
        else:
            # Fallback: extract ID from filename
            filename = file_path.stem
            id_match = re.match(r'^(BUG-\d{4}-\d{2}-\d+)', filename)
            if id_match:
                metadata['id'] = id_match.group(1)
                metadata['title'] = filename.replace(metadata['id'] + '-', '').replace('-', ' ').title()
            
        # Extract other metadata
        for line in lines[1:20]:  # Check first 20 lines for metadata
            if line.startswith('**Status**:'):
                metadata['status'] = line.split(':', 1)[1].strip()
            elif line.startswith('**Priority**:'):
                metadata['priority'] = line.split(':', 1)[1].strip()
            elif line.startswith('**Component**:'):
                metadata['component'] = line.split(':', 1)[1].strip()
            elif line.startswith('**GitHub Issue**:'):
                github_info = line.split(':', 1)[1].strip()
                if '#' in github_info:
                    metadata['github_issue'] = github_info.split('#')[1].split()[0]
                    
        metadata['file_path'] = file_path
        metadata['content'] = content
        return metadata
        
    def get_local_bugs(self) -> List[Dict]:
        """Get all local bug files."""
        bugs = []
        bug_files = self.bugs_dir.glob("BUG-*.md")
        
        for file_path in bug_files:
            try:
                bug_data = self.parse_bug_file(file_path)
                bugs.append(bug_data)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
                
        return bugs
        
    def get_github_issues(self) -> List[Dict]:
        """Get GitHub issues with bug label."""
        try:
            result = subprocess.run(
                ['gh', 'issue', 'list', '--label', 'bug', '--json', 
                 'number,title,state,labels,body,updatedAt'],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error fetching GitHub issues: {e}")
            return []
            
    def create_github_issue(self, bug: Dict) -> Optional[int]:
        """Create a GitHub issue for a local bug."""
        title = f"{bug['id']}: {bug['title']}"
        # Convert to relative path, handling both absolute and relative paths
        file_path = bug['file_path']
        if file_path.is_absolute():
            try:
                rel_path = file_path.relative_to(self.project_root)
            except ValueError:
                rel_path = file_path
        else:
            rel_path = file_path
        body = f"""## Bug Details
        
See detailed technical documentation: [`{rel_path}`](https://github.com/bhowiebkr/PyFlowGraph/blob/main/{rel_path.as_posix()})

**Priority**: {bug.get('priority', 'Unknown')}  
**Component**: {bug.get('component', 'Unknown')}  
**Status**: {bug.get('status', 'Unknown')}

For complete technical details, reproduction steps, and investigation notes, see the linked documentation file."""
        
        # Determine labels based on priority and component
        labels = ['bug', 'documentation']
        
        if bug.get('priority'):
            priority = bug['priority'].lower()
            if priority == 'critical':
                labels.append('critical')
            elif priority == 'high':
                labels.append('high-priority')
            elif priority == 'medium':
                labels.append('medium-priority')
            elif priority == 'low':
                labels.append('low-priority')
                
        if bug.get('component'):
            component = bug['component'].lower().replace(' ', '-')
            component_labels = {
                'execution engine': 'execution',
                'execution-engine': 'execution', 
                'execution engine, reroute nodes': 'execution',
                'ui': 'ui',
                'user interface': 'ui',
                'file operations': 'file-ops',
                'file-operations': 'file-ops',
                'node system': 'node-system',
                'node-system': 'node-system',
                'undo/redo': 'undo-redo',
                'command system': 'undo-redo',
                'performance': 'performance'
            }
            if component in component_labels:
                labels.append(component_labels[component])
                
        try:
            cmd = ['gh', 'issue', 'create', '--title', title, '--body', body]
            for label in labels:
                cmd.extend(['--label', label])
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract issue number from output
            output = result.stderr or result.stdout
            issue_match = re.search(r'https://github\.com/.+/issues/(\d+)', output)
            if issue_match:
                return int(issue_match.group(1))
                
        except subprocess.CalledProcessError as e:
            print(f"Error creating GitHub issue: {e}")
            
        return None
        
    def update_bug_file_with_github_issue(self, bug: Dict, issue_number: int):
        """Update local bug file with GitHub issue reference."""
        content = bug['content']
        
        # Add GitHub Issue line after Component if not present
        if '**GitHub Issue**:' not in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('**Component**:'):
                    lines.insert(i + 1, f'**GitHub Issue**: #{issue_number}')
                    break
            content = '\n'.join(lines)
            
        # Update Last Sync date
        today = datetime.now().strftime('%Y-%m-%d')
        if '**Last Sync**:' in content:
            content = re.sub(r'\*\*Last Sync\*\*:.*', f'**Last Sync**: {today}', content)
        else:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('**GitHub Issue**:'):
                    lines.insert(i + 1, f'**Last Sync**: {today}')
                    break
            content = '\n'.join(lines)
            
        # Write updated content
        with open(bug['file_path'], 'w', encoding='utf-8') as f:
            f.write(content)
            
    def sync_to_github(self):
        """Sync local bugs to GitHub Issues."""
        local_bugs = self.get_local_bugs()
        github_issues = self.get_github_issues()
        
        # Create mapping of existing GitHub issues by title
        github_by_title = {issue['title']: issue for issue in github_issues}
        
        for bug in local_bugs:
            bug_title = f"{bug['id']}: {bug['title']}"
            
            if 'github_issue' not in bug and bug_title not in github_by_title:
                print(f"Creating GitHub issue for {bug['id']}")
                issue_number = self.create_github_issue(bug)
                if issue_number:
                    self.update_bug_file_with_github_issue(bug, issue_number)
                    print(f"  Created issue #{issue_number}")
            else:
                print(f"GitHub issue already exists for {bug['id']}")
                
    def validate_sync_status(self):
        """Check synchronization status between local and GitHub."""
        local_bugs = self.get_local_bugs()
        github_issues = self.get_github_issues()
        
        print("=== Bug Sync Status ===")
        print(f"Local bugs: {len(local_bugs)}")
        print(f"GitHub issues with bug label: {len(github_issues)}")
        print()
        
        for bug in local_bugs:
            bug_id = bug.get('id', 'Unknown ID')
            has_github = 'github_issue' in bug
            status_icon = "[SYNCED]" if has_github else "[NO SYNC]"
            github_ref = f"#{bug['github_issue']}" if has_github else "No GitHub issue"
            print(f"{status_icon} {bug_id}: {github_ref}")
            
            # Debug: print all keys in bug dict
            if bug_id == 'Unknown ID':
                print(f"  Debug - Available keys: {list(bug.keys())}")
                print(f"  Debug - File path: {bug.get('file_path', 'Unknown')}")

def main():
    parser = argparse.ArgumentParser(description='Bug sync automation for docs/bugs/ and GitHub Issues')
    parser.add_argument('--sync-to-github', action='store_true', 
                       help='Create GitHub issues for local bugs without them')
    parser.add_argument('--validate', action='store_true',
                       help='Check sync status between local and GitHub')
    parser.add_argument('--bugs-dir', default='docs/bugs',
                       help='Directory containing local bug files')
    
    args = parser.parse_args()
    
    sync_manager = BugSyncManager(args.bugs_dir)
    
    if args.sync_to_github:
        sync_manager.sync_to_github()
    elif args.validate:
        sync_manager.validate_sync_status()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
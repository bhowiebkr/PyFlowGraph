#!/usr/bin/env python3

"""
README Badge Updater for PyFlowGraph

Updates README.md with test result badges based on test execution results.
Generates shields.io badges for:
- Test status (passing/failing)
- Test count (total tests)
- Coverage percentage (if available)
- Last updated timestamp
"""

import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote


class BadgeUpdater:
    """Handles updating README.md with test result badges."""
    
    def __init__(self, readme_path: Optional[str] = None, test_results_path: Optional[str] = None):
        """Initialize badge updater with README and test results paths."""
        if readme_path is None:
            # Default to project root README.md
            self.readme_path = Path(__file__).parent.parent / "README.md"
        else:
            self.readme_path = Path(readme_path)
        
        if test_results_path is None:
            # Default to testing/test_results.md
            self.test_results_path = Path(__file__).parent / "test_results.md"
        else:
            self.test_results_path = Path(test_results_path)
    
    def calculate_test_stats(self, test_results: Dict[str, Dict]) -> Dict:
        """Calculate comprehensive test statistics.
        
        Args:
            test_results: Dictionary with test file paths as keys and result dicts as values
        
        Returns:
            Dictionary with comprehensive test statistics
        """
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get('status') == 'passed')
        failed_tests = sum(1 for result in test_results.values() if result.get('status') == 'failed')
        error_tests = sum(1 for result in test_results.values() if result.get('status') == 'error')
        skipped_tests = sum(1 for result in test_results.values() if result.get('status') == 'skipped')
        
        # Calculate success rate
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
        else:
            success_rate = 0
        
        # Determine overall status
        if total_tests == 0:
            status = "unknown"
        elif failed_tests == 0 and error_tests == 0:
            status = "passing"
        else:
            status = "failing"
        
        # Format timestamp
        now = datetime.datetime.now()
        last_run = now.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "status": status,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "skipped": skipped_tests,
            "success_rate": int(success_rate),
            "test_files": total_tests,
            "total_tests": total_tests,
            "warnings": 0,  # Could be enhanced to parse test output for warnings
            "last_run": last_run
        }
    
    def create_stats_badge(self, stats: Dict) -> str:
        """Create a cool stats section for the README."""

        # Status information (without emojis to comply with Windows encoding requirements)
        status_info = {
            "passing": {"color": "green", "text": "PASSING"},
            "failing": {"color": "red", "text": "FAILING"},
            "unknown": {"color": "yellow", "text": "UNKNOWN"},
        }

        status = status_info.get(stats["status"], status_info["unknown"])

        # Determine colors for individual badges
        passed_color = "green" if stats["passed"] > 0 else "lightgrey"
        success_rate_color = "green" if stats["success_rate"] >= 80 else "orange" if stats["success_rate"] >= 60 else "red"

        # Create the badge section
        badge_section = f"""<!-- TEST_STATS_START -->

<div align="center">

![Tests](https://img.shields.io/badge/Tests-{stats['passed']}%20passed-{passed_color})
![Failed](https://img.shields.io/badge/Failed-{stats['failed']}-red)
![Success Rate](https://img.shields.io/badge/Success%20Rate-{stats['success_rate']}%25-{success_rate_color})
![Test Files](https://img.shields.io/badge/Test%20Files-{stats['test_files']}-blue)
![Total Tests](https://img.shields.io/badge/Total%20Tests-{stats['total_tests']}-lightgrey)
![Skipped](https://img.shields.io/badge/Skipped-{stats['skipped']}-yellow)
![Errors](https://img.shields.io/badge/Errors-{stats['errors']}-orange)
![Warnings](https://img.shields.io/badge/Warnings-{stats['warnings']}-lightgrey)
![Last Run](https://img.shields.io/badge/Last%20Run-{stats['last_run'].replace('-', '--').replace(' ', '%20').replace(':', '%3A')}-lightblue)

</div>

<div align="center">

**[View Detailed Test Report]({self._get_relative_test_results_path()})** - Complete test results with individual test details

</div>

<!-- TEST_STATS_END -->"""

        return badge_section
    
    def _get_relative_test_results_path(self) -> str:
        """Get relative path to test results file from README."""
        try:
            relative_path = self.test_results_path.relative_to(self.readme_path.parent)
            return str(relative_path).replace('\\', '/')  # Use forward slashes for URLs
        except ValueError:
            # If paths are on different drives, use absolute path
            return str(self.test_results_path).replace('\\', '/')
    
    def find_badge_section(self, content: str) -> Tuple[int, int]:
        """Find the badge section in README content.
        
        Returns:
            Tuple of (start_line, end_line) indices, or (-1, -1) if not found
        """
        lines = content.split('\n')
        
        # Look for existing badge section markers (check both old and new markers)
        start_markers = ["<!-- TEST_STATS_START -->", "<!-- TEST-BADGES-START -->"]
        end_markers = ["<!-- TEST_STATS_END -->", "<!-- TEST-BADGES-END -->"]
        
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(lines):
            # Check for any start marker
            for start_marker in start_markers:
                if start_marker in line:
                    start_idx = i
                    break
            # Check for any end marker (only if we found a start)
            if start_idx != -1:
                for end_marker in end_markers:
                    if end_marker in line:
                        end_idx = i
                        break
                if end_idx != -1:
                    break
        
        return start_idx, end_idx
    
    def generate_detailed_test_results(self, test_results: Dict[str, Dict]) -> str:
        """Generate detailed test results markdown content.
        
        Args:
            test_results: Test results dictionary
            
        Returns:
            Formatted markdown content for detailed test results
        """
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get('status') == 'passed')
        failed_tests = total_tests - passed_tests
        total_duration = sum(result.get('duration', 0) for result in test_results.values())
        
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# PyFlowGraph Test Results

**Generated:** {timestamp}  
**Test Runner:** Professional PySide6 GUI Test Tool

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | {total_tests} |
| **Passed** | {passed_tests} |
| **Failed** | {failed_tests} |
| **Success Rate** | {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}% |
| **Total Duration** | {total_duration:.2f} seconds |
| **Average Duration** | {(total_duration/total_tests) if total_tests > 0 else 0:.2f} seconds per test |

---

## Test Results Table

| Status | Test Name | Duration | Details |
|--------|-----------|----------|---------|"""

        # Sort tests by status (failed first, then passed) and then by name
        sorted_tests = sorted(test_results.items(), key=lambda x: (x[1].get('status') != 'failed', Path(x[0]).name))
        
        # Add table rows
        for test_path, result in sorted_tests:
            test_name = Path(test_path).name
            status = result.get('status', 'unknown')
            duration = result.get('duration', 0)
            
            # Status emoji
            if status == 'passed':
                status_emoji = "✅"
            elif status == 'failed':
                status_emoji = "❌"
            elif status == 'error':
                status_emoji = "⚠️"
            else:
                status_emoji = "❓"
            
            # Create anchor ID for the test
            anchor_id = test_name.replace('.py', '').replace('_', '-').replace(' ', '-').lower()
            
            # Add clickable link for failed tests, plain text for passed tests
            if status in ['failed', 'error']:
                test_link = f"[{test_name}](#{anchor_id})"
            else:
                test_link = test_name
            
            content += f"\n| {status_emoji} | {test_link} | {duration:.2f}s | {status.upper()} |"

        content += f"""

---

## Detailed Test Results

"""
        
        for test_path, result in sorted_tests:
            test_name = Path(test_path).name
            status = result.get('status', 'unknown')
            duration = result.get('duration', 0)
            output = result.get('output', 'No output available')
            
            # Create anchor ID for the test (same as in table)
            anchor_id = test_name.replace('.py', '').replace('_', '-').replace(' ', '-').lower()
            
            # Status styling
            if status == 'passed':
                status_badge = "[PASS]"
            elif status == 'failed':
                status_badge = "[FAIL]"
            elif status == 'error':
                status_badge = "[ERROR]"
            else:
                status_badge = "[UNKNOWN]"
            
            # Add anchor for failed/error tests, regular heading for passed tests
            if status in ['failed', 'error']:
                content += f"""### <a id="{anchor_id}"></a>{status_badge} {test_name}

**Status:** {status.upper()}  
**Duration:** {duration:.2f} seconds  
**File Path:** `{test_path}`

"""
            else:
                content += f"""### {status_badge} {test_name}

**Status:** {status.upper()}  
**Duration:** {duration:.2f} seconds  
**File Path:** `{test_path}`

"""
            
            # Add output section if there's meaningful output
            if output and output.strip():
                # Clean up output for markdown
                clean_output = output.replace('\r\n', '\n').replace('\r', '\n')
                # Limit output length for readability
                if len(clean_output) > 2000:
                    clean_output = clean_output[:2000] + "\n... (output truncated)"
                
                content += f"""**Output:**
```
{clean_output}
```

"""
            
            # Add back to top link for failed/error tests
            if status in ['failed', 'error']:
                content += "[↑ Back to Test Table](#test-results-table)\n\n"
            
            content += "---\n\n"
        
        # Add footer
        content += f"""## Test Environment

- **Python Version:** {self._get_python_version()}
- **Test Runner:** PyFlowGraph Professional GUI Test Tool
- **Test Directory:** `tests/`
- **Generated By:** Badge Updater v1.0

---

*This report is automatically generated when tests are executed through the PyFlowGraph test tool.*
*Last updated: {timestamp}*
"""
        
        return content
    
    def _get_python_version(self) -> str:
        """Get Python version string."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def save_detailed_test_results(self, test_results: Dict[str, Dict]) -> bool:
        """Save detailed test results to markdown file.
        
        Args:
            test_results: Test results dictionary
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            content = self.generate_detailed_test_results(test_results)
            
            # Ensure directory exists
            self.test_results_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write detailed results
            with open(self.test_results_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Detailed test results saved to: {self.test_results_path}")
            return True
            
        except Exception as e:
            print(f"Error saving detailed test results: {e}")
            return False
    
    def update_readme_badges(self, test_results: Dict[str, Dict]) -> bool:
        """Update README.md with test result badges.
        
        Args:
            test_results: Test results dictionary
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            if not self.readme_path.exists():
                print(f"README file not found: {self.readme_path}")
                return False
            
            # Read current README content
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate comprehensive test statistics
            stats = self.calculate_test_stats(test_results)
            
            # Generate new badge section
            badge_section = self.create_stats_badge(stats)
            
            # Find existing badge section
            start_idx, end_idx = self.find_badge_section(content)
            lines = content.split('\n')
            
            if start_idx != -1 and end_idx != -1:
                # Replace existing badge section
                new_lines = lines[:start_idx] + badge_section.split('\n') + lines[end_idx + 1:]
                new_content = '\n'.join(new_lines)
            else:
                # Insert badge section after the first heading
                heading_pattern = r'^# .+$'
                lines = content.split('\n')
                insert_idx = -1
                
                for i, line in enumerate(lines):
                    if re.match(heading_pattern, line):
                        # Insert after the heading and any existing content until first empty line
                        insert_idx = i + 1
                        while insert_idx < len(lines) and lines[insert_idx].strip():
                            insert_idx += 1
                        break
                
                if insert_idx != -1:
                    # Insert badge section
                    new_lines = lines[:insert_idx] + [''] + badge_section.split('\n') + [''] + lines[insert_idx:]
                    new_content = '\n'.join(new_lines)
                else:
                    # Fallback: add at the beginning
                    new_content = badge_section + '\n\n' + content
            
            # Write updated content
            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Save detailed test results
            detailed_results_saved = self.save_detailed_test_results(test_results)
            
            print(f"Successfully updated README badges: {self.readme_path}")
            if detailed_results_saved:
                print(f"Detailed test results saved: {self.test_results_path}")
            
            return True
            
        except Exception as e:
            print(f"Error updating README badges: {e}")
            return False
    
    def generate_summary_report(self, test_results: Dict[str, Dict]) -> str:
        """Generate a summary report of test results.
        
        Args:
            test_results: Test results dictionary
            
        Returns:
            Formatted summary report string
        """
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get('status') == 'passed')
        failed_tests = total_tests - passed_tests
        
        # Calculate total duration
        total_duration = sum(result.get('duration', 0) for result in test_results.values())
        
        # Get failed test names
        failed_test_names = [
            Path(test_path).name for test_path, result in test_results.items() 
            if result.get('status') != 'passed'
        ]
        
        report = f"""
Test Execution Summary
{'=' * 50}
Total Tests: {total_tests}
Passed: {passed_tests}
Failed: {failed_tests}
Success Rate: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%
Total Duration: {total_duration:.2f} seconds
Average Duration: {(total_duration/total_tests) if total_tests > 0 else 0:.2f} seconds per test

"""
        
        if failed_test_names:
            report += "Failed Tests:\n"
            for test_name in failed_test_names:
                report += f"  - {test_name}\n"
        
        report += f"\nBadges updated in: {self.readme_path}\n"
        report += f"Updated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report


def main():
    """Command line interface for badge updater."""
    import sys
    
    if len(sys.argv) > 1:
        readme_path = sys.argv[1]
    else:
        readme_path = None
    
    # Example test results (for testing)
    example_results = {
        "test_node_system.py": {"status": "passed", "duration": 1.23, "output": "All tests passed"},
        "test_pin_system.py": {"status": "passed", "duration": 0.89, "output": "All tests passed"},
        "test_connection_system.py": {"status": "failed", "duration": 2.45, "output": "1 test failed"},
    }
    
    updater = BadgeUpdater(readme_path)
    success = updater.update_readme_badges(example_results)
    
    if success:
        print("Badge update completed successfully!")
        
        # Show stats preview
        stats = updater.calculate_test_stats(example_results)
        print(f"\nTest Statistics:")
        print(f"  Status: {stats['status'].upper()}")
        print(f"  Passed: {stats['passed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Success Rate: {stats['success_rate']}%")
        print(f"  Last Run: {stats['last_run']}")
        
        print(updater.generate_summary_report(example_results))
    else:
        print("Badge update failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
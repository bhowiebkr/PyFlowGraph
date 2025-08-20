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

from test_output_parser import TestOutputParser, TestFileResult, TestCaseResult


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
    
    def calculate_test_stats(self, test_results: Dict[str, TestFileResult]) -> Dict:
        """Calculate comprehensive test statistics from individual test cases.
        
        Args:
            test_results: Dictionary with test file paths as keys and TestFileResult objects as values
        
        Returns:
            Dictionary with comprehensive test statistics
        """
        # Count individual test cases across all files
        total_test_cases = 0
        passed_test_cases = 0
        failed_test_cases = 0
        error_test_cases = 0
        skipped_test_cases = 0
        
        # Count test files
        total_files = len(test_results)
        passed_files = 0
        failed_files = 0
        
        for file_result in test_results.values():
            # File-level counts
            if file_result.status == 'passed':
                passed_files += 1
            elif file_result.status in ['failed', 'error']:
                failed_files += 1
            
            # Test case-level counts
            total_test_cases += file_result.total_cases
            passed_test_cases += file_result.passed_cases
            failed_test_cases += file_result.failed_cases
            error_test_cases += file_result.error_cases
            skipped_test_cases += file_result.skipped_cases
        
        # Calculate success rate based on individual test cases
        if total_test_cases > 0:
            success_rate = (passed_test_cases / total_test_cases) * 100
        else:
            success_rate = 0
        
        # Determine overall status
        if total_test_cases == 0:
            status = "unknown"
        elif failed_test_cases == 0 and error_test_cases == 0:
            status = "passing"
        else:
            status = "failing"
        
        # Format timestamp
        now = datetime.datetime.now()
        last_run = now.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "status": status,
            "passed": passed_test_cases,
            "failed": failed_test_cases,
            "errors": error_test_cases,
            "skipped": skipped_test_cases,
            "success_rate": int(success_rate),
            "test_files": total_files,
            "total_tests": total_test_cases,  # Now shows individual test cases
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
    
    def generate_detailed_test_results(self, test_results: Dict[str, TestFileResult]) -> str:
        """Generate detailed test results markdown content with individual test cases.
        
        Args:
            test_results: Dictionary of TestFileResult objects
            
        Returns:
            Formatted markdown content for detailed test results
        """
        # Calculate overall statistics
        total_files = len(test_results)
        total_test_cases = sum(result.total_cases for result in test_results.values())
        passed_test_cases = sum(result.passed_cases for result in test_results.values())
        failed_test_cases = sum(result.failed_cases for result in test_results.values())
        error_test_cases = sum(result.error_cases for result in test_results.values())
        skipped_test_cases = sum(result.skipped_cases for result in test_results.values())
        total_duration = sum(result.duration for result in test_results.values())
        
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# PyFlowGraph Test Results

**Generated:** {timestamp}  
**Test Runner:** Professional PySide6 GUI Test Tool

---

## Summary

| Metric | Value |
|--------|-------|
| **Test Files** | {total_files} |
| **Total Test Cases** | {total_test_cases} |
| **Passed** | {passed_test_cases} |
| **Failed** | {failed_test_cases} |
| **Errors** | {error_test_cases} |
| **Skipped** | {skipped_test_cases} |
| **Success Rate** | {(passed_test_cases/total_test_cases*100) if total_test_cases > 0 else 0:.1f}% |
| **Total Duration** | {total_duration:.2f} seconds |
| **Average Duration** | {(total_duration/total_files) if total_files > 0 else 0:.2f} seconds per file |

---

## Test Results by File

| Status | Test File | Cases | Passed | Failed | Duration | Details |
|--------|-----------|-------|--------|--------|----------|---------|"""

        # Sort test files by status (failed first, then passed) and then by name
        sorted_files = sorted(test_results.items(), key=lambda x: (x[1].status != 'failed', Path(x[0]).name))
        
        # Add table rows for files
        for test_path, file_result in sorted_files:
            test_name = Path(test_path).name
            status = file_result.status
            
            # Status emoji
            if status == 'passed':
                status_emoji = "✅"
            elif status == 'failed':
                status_emoji = "❌"
            elif status == 'error':
                status_emoji = "⚠️"
            else:
                status_emoji = "❓"
            
            # Create anchor ID for the test file
            anchor_id = test_name.replace('.py', '').replace('_', '-').replace(' ', '-').lower()
            
            # Add clickable link for failed files, plain text for passed files
            if status in ['failed', 'error']:
                test_link = f"[{test_name}](#{anchor_id})"
            else:
                test_link = test_name
            
            content += f"\n| {status_emoji} | {test_link} | {file_result.total_cases} | {file_result.passed_cases} | {file_result.failed_cases} | {file_result.duration:.2f}s | {status.upper()} |"

        content += f"""

---

## Individual Test Cases

"""
        
        # Add individual test case details grouped by file
        for test_path, file_result in sorted_files:
            test_name = Path(test_path).name
            anchor_id = test_name.replace('.py', '').replace('_', '-').replace(' ', '-').lower()
            
            # File header with status
            if file_result.status == 'passed':
                status_badge = "[PASS]"
            elif file_result.status == 'failed':
                status_badge = "[FAIL]"
            elif file_result.status == 'error':
                status_badge = "[ERROR]"
            else:
                status_badge = "[UNKNOWN]"
            
            # Add anchor for failed/error files, regular heading for passed files
            if file_result.status in ['failed', 'error']:
                content += f"""### <a id="{anchor_id}"></a>{status_badge} {test_name}

**File Status:** {file_result.status.upper()}  
**Total Cases:** {file_result.total_cases}  
**Passed:** {file_result.passed_cases}  
**Failed:** {file_result.failed_cases}  
**Errors:** {file_result.error_cases}  
**Duration:** {file_result.duration:.2f} seconds  
**File Path:** `{test_path}`

"""
            else:
                content += f"""### {status_badge} {test_name}

**File Status:** {file_result.status.upper()}  
**Total Cases:** {file_result.total_cases}  
**Passed:** {file_result.passed_cases}  
**Duration:** {file_result.duration:.2f} seconds  
**File Path:** `{test_path}`

"""
            
            # Add individual test cases
            if file_result.test_cases:
                content += "#### Individual Test Cases:\n\n"
                
                # Sort test cases by status (failed first, then passed)
                sorted_cases = sorted(file_result.test_cases, key=lambda x: (x.status != 'failed', x.name))
                
                for test_case in sorted_cases:
                    # Status indicator
                    if test_case.status == 'passed':
                        case_emoji = "✅"
                    elif test_case.status == 'failed':
                        case_emoji = "❌"
                    elif test_case.status == 'error':
                        case_emoji = "⚠️"
                    elif test_case.status == 'skipped':
                        case_emoji = "⏭️"
                    else:
                        case_emoji = "❓"
                    
                    content += f"- {case_emoji} **{test_case.name}** ({test_case.class_name}) - {test_case.status.upper()}\n"
                    
                    # Add error message for failed/error cases
                    if test_case.error_message and test_case.status in ['failed', 'error']:
                        # Truncate long error messages
                        error_msg = test_case.error_message
                        if len(error_msg) > 200:
                            error_msg = error_msg[:200] + "..."
                        content += f"  - Error: `{error_msg}`\n"
                
                content += "\n"
            
            # Add raw output section for failed files
            if file_result.status in ['failed', 'error'] and file_result.raw_output:
                content += "#### Raw Test Output:\n\n"
                clean_output = file_result.raw_output.replace('\r\n', '\n').replace('\r', '\n')
                # Limit output length for readability
                if len(clean_output) > 1500:
                    clean_output = clean_output[:1500] + "\n... (output truncated)"
                
                content += f"""```
{clean_output}
```

"""
            
            # Add back to top link for failed/error files
            if file_result.status in ['failed', 'error']:
                content += "[↑ Back to Test Results](#test-results-by-file)\n\n"
            
            content += "---\n\n"
        
        # Add footer
        content += f"""## Test Environment

- **Python Version:** {self._get_python_version()}
- **Test Runner:** PyFlowGraph Professional GUI Test Tool
- **Test Directory:** `tests/`
- **Generated By:** Badge Updater v2.0 (Individual Test Case Support)

---

*This report is automatically generated when tests are executed through the PyFlowGraph test tool.*
*Now showing individual test case results for more detailed analysis.*
*Last updated: {timestamp}*
"""
        
        return content
    
    def _get_python_version(self) -> str:
        """Get Python version string."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def save_detailed_test_results(self, test_results: Dict[str, TestFileResult]) -> bool:
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
    
    def update_readme_badges(self, test_results: Dict[str, TestFileResult]) -> bool:
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
    
    def generate_summary_report(self, test_results: Dict[str, TestFileResult]) -> str:
        """Generate a summary report of test results.
        
        Args:
            test_results: Test results dictionary
            
        Returns:
            Formatted summary report string
        """
        total_files = len(test_results)
        total_test_cases = sum(result.total_cases for result in test_results.values())
        passed_test_cases = sum(result.passed_cases for result in test_results.values())
        failed_test_cases = sum(result.failed_cases for result in test_results.values())
        error_test_cases = sum(result.error_cases for result in test_results.values())
        
        # Calculate total duration
        total_duration = sum(result.duration for result in test_results.values())
        
        # Get failed test file names
        failed_file_names = [
            Path(test_path).name for test_path, result in test_results.items() 
            if result.status in ['failed', 'error']
        ]
        
        report = f"""
Test Execution Summary
{'=' * 50}
Test Files: {total_files}
Total Test Cases: {total_test_cases}
Passed: {passed_test_cases}
Failed: {failed_test_cases}
Errors: {error_test_cases}
Success Rate: {(passed_test_cases/total_test_cases*100) if total_test_cases > 0 else 0:.1f}%
Total Duration: {total_duration:.2f} seconds
Average Duration: {(total_duration/total_files) if total_files > 0 else 0:.2f} seconds per file

"""
        
        if failed_file_names:
            report += "Failed Test Files:\n"
            for file_name in failed_file_names:
                report += f"  - {file_name}\n"
        
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
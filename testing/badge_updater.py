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
    
    def generate_test_badges(self, test_results: Dict[str, Dict]) -> List[str]:
        """Generate badge markdown from test results.
        
        Args:
            test_results: Dictionary with test file paths as keys and result dicts as values
                         Each result dict should have: {'status': str, 'duration': float, 'output': str}
        
        Returns:
            List of badge markdown strings
        """
        badges = []
        
        # Calculate test statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result.get('status') == 'passed')
        failed_tests = total_tests - passed_tests
        
        # Test status badge
        if failed_tests == 0 and total_tests > 0:
            status_badge = "![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)"
        elif total_tests > 0:
            status_badge = f"![Tests](https://img.shields.io/badge/tests-{failed_tests}%20failing-red?style=flat-square)"
        else:
            status_badge = "![Tests](https://img.shields.io/badge/tests-no%20tests-lightgrey?style=flat-square)"
        
        badges.append(status_badge)
        
        # Test count badge
        count_badge = f"![Test Count](https://img.shields.io/badge/tests-{total_tests}%20total-blue?style=flat-square)"
        badges.append(count_badge)
        
        # Success rate badge
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            if success_rate == 100:
                rate_color = "brightgreen"
            elif success_rate >= 80:
                rate_color = "green" 
            elif success_rate >= 60:
                rate_color = "yellow"
            else:
                rate_color = "red"
            
            rate_badge = f"![Success Rate](https://img.shields.io/badge/success%20rate-{success_rate:.0f}%25-{rate_color}?style=flat-square)"
            badges.append(rate_badge)
        
        # Last updated badge
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y---%m---%d")
        updated_badge = f"![Last Updated](https://img.shields.io/badge/last%20tested-{timestamp}-blue?style=flat-square)"
        badges.append(updated_badge)
        
        return badges
    
    def find_badge_section(self, content: str) -> Tuple[int, int]:
        """Find the badge section in README content.
        
        Returns:
            Tuple of (start_line, end_line) indices, or (-1, -1) if not found
        """
        lines = content.split('\n')
        
        # Look for existing badge section markers
        start_marker = "<!-- TEST-BADGES-START -->"
        end_marker = "<!-- TEST-BADGES-END -->"
        
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(lines):
            if start_marker in line:
                start_idx = i
            elif end_marker in line and start_idx != -1:
                end_idx = i
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

## Test Results Details

"""
        
        # Sort tests by status (failed first, then passed) and then by name
        sorted_tests = sorted(test_results.items(), key=lambda x: (x[1].get('status') != 'failed', Path(x[0]).name))
        
        for test_path, result in sorted_tests:
            test_name = Path(test_path).name
            status = result.get('status', 'unknown')
            duration = result.get('duration', 0)
            output = result.get('output', 'No output available')
            
            # Status styling
            if status == 'passed':
                status_badge = "[PASS]"
            elif status == 'failed':
                status_badge = "[FAIL]"
            elif status == 'error':
                status_badge = "[ERROR]"
            else:
                status_badge = "[UNKNOWN]"
            
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
            
            # Generate new badges
            badges = self.generate_test_badges(test_results)
            
            # Calculate relative path to test results file from README
            try:
                relative_path = self.test_results_path.relative_to(self.readme_path.parent)
            except ValueError:
                # If paths are on different drives, use absolute path
                relative_path = self.test_results_path
            
            badge_section = "\n".join([
                "<!-- TEST-BADGES-START -->",
                "",
                " ".join(badges),
                "",
                f"**[View Detailed Test Results]({relative_path})**",
                "",
                "<!-- TEST-BADGES-END -->"
            ])
            
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
        print(updater.generate_summary_report(example_results))
    else:
        print("Badge update failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
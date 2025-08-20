#!/usr/bin/env python3

"""
Test Output Parser for PyFlowGraph

Parses unittest verbose output to extract individual test case results.
Handles various unittest output formats and provides structured data
for badge generation and detailed reporting.
"""

import re
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestCaseResult:
    """Individual test case result."""
    name: str
    class_name: str
    file_path: str
    status: str  # 'passed', 'failed', 'error', 'skipped'
    duration: float
    output: str
    error_message: str = ""


@dataclass
class TestFileResult:
    """Results for an entire test file."""
    file_path: str
    status: str  # 'passed', 'failed', 'error'
    duration: float
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    skipped_cases: int
    test_cases: List[TestCaseResult]
    raw_output: str


class TestOutputParser:
    """Parses unittest verbose output to extract individual test case results."""
    
    def __init__(self):
        # Regex patterns for parsing unittest output
        # This pattern handles the format: test_name (module.Class.test_name)\nDescription ... ok
        self.test_case_pattern = re.compile(
            r'^(test_\w+)\s+\([^)]+\)\s*\n.*?\.\.\.\s+(ok|FAIL|ERROR|skipped.*?)$',
            re.MULTILINE
        )
        
        # Alternative simpler pattern for just the test line with status
        self.simple_test_pattern = re.compile(
            r'^(test_\w+)\s+.*?\.\.\.\s+(ok|FAIL|ERROR|skipped.*?)$',
            re.MULTILINE
        )
        
        # Pattern to extract class name from test line  
        self.class_pattern = re.compile(r'\(([^.)]*\.)?([^.)]*)\.[^)]*\)')
        
        # Pattern for test execution time in unittest output
        self.time_pattern = re.compile(r'Ran (\d+) tests? in ([\d.]+)s')
        
        # Pattern for test summary line
        self.summary_pattern = re.compile(
            r'(OK|FAILED)\s*(?:\((?:failures=(\d+))?(?:,\s*)?(?:errors=(\d+))?(?:,\s*)?(?:skipped=(\d+))?\))?'
        )
        
        # Pattern for detailed failure/error messages
        self.failure_pattern = re.compile(
            r'={70}\n(FAIL|ERROR):\s+(\w+)\s+\((\w+\.)?(\w+)\)\n-{70}\n(.*?)\n(?=-{70}|={70}|$)',
            re.DOTALL | re.MULTILINE
        )
    
    def parse_test_file_output(self, file_path: str, output: str, duration: float) -> TestFileResult:
        """Parse the complete output from running a test file.
        
        Args:
            file_path: Path to the test file
            output: Raw stdout/stderr from test execution
            duration: Total execution duration
            
        Returns:
            TestFileResult with parsed individual test cases
        """
        test_cases = []
        
        # Parse individual test case results using multiple approaches
        test_case_matches = self.test_case_pattern.findall(output)
        
        # If the main pattern doesn't work, try the simpler pattern
        if not test_case_matches:
            test_case_matches = self.simple_test_pattern.findall(output)
        
        # Parse failure/error details
        failure_details = {}
        for failure_match in self.failure_pattern.findall(output):
            failure_type, test_name, module_prefix, class_name, error_msg = failure_match
            key = f"{test_name}.{class_name}"
            failure_details[key] = {
                'type': failure_type.lower(),
                'message': error_msg.strip()
            }
        
        # Create TestCaseResult objects
        for test_name, result_status in test_case_matches:
            # Extract class name from the full output if possible
            class_name = "Unknown"
            for line in output.split('\n'):
                if test_name in line and '(' in line:
                    class_match = self.class_pattern.search(line)
                    if class_match:
                        class_name = class_match.group(2) if class_match.group(2) else class_match.group(1)
                    break
            # Determine status
            if result_status == 'ok':
                status = 'passed'
            elif result_status == 'FAIL':
                status = 'failed'
            elif result_status == 'ERROR':
                status = 'error'
            elif result_status.startswith('skipped'):
                status = 'skipped'
            else:
                status = 'unknown'
            
            # Get error message if available
            test_key = f"{test_name}.{class_name}"
            error_message = ""
            if test_key in failure_details:
                error_message = failure_details[test_key]['message']
            
            test_case = TestCaseResult(
                name=test_name,
                class_name=class_name,
                file_path=file_path,
                status=status,
                duration=0.0,  # Individual test durations not available from standard unittest
                output="",  # Individual test output not separated in standard unittest
                error_message=error_message
            )
            test_cases.append(test_case)
        
        # Calculate statistics
        total_cases = len(test_cases)
        passed_cases = sum(1 for tc in test_cases if tc.status == 'passed')
        failed_cases = sum(1 for tc in test_cases if tc.status == 'failed')
        error_cases = sum(1 for tc in test_cases if tc.status == 'error')
        skipped_cases = sum(1 for tc in test_cases if tc.status == 'skipped')
        
        # Determine overall file status
        if total_cases == 0:
            file_status = 'error'
        elif failed_cases > 0 or error_cases > 0:
            file_status = 'failed'
        else:
            file_status = 'passed'
        
        return TestFileResult(
            file_path=file_path,
            status=file_status,
            duration=duration,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            error_cases=error_cases,
            skipped_cases=skipped_cases,
            test_cases=test_cases,
            raw_output=output
        )
    
    def parse_discover_output(self, output: str, duration: float) -> List[TestFileResult]:
        """Parse output from unittest discover command.
        
        Args:
            output: Raw output from unittest discover
            duration: Total execution duration
            
        Returns:
            List of TestFileResult objects, one per test file
        """
        # This would be used if running unittest discover instead of individual files
        # For now, we'll focus on individual file parsing
        results = []
        
        # Split output by test files (this is a simplified approach)
        # In practice, unittest discover doesn't cleanly separate by file
        # so we'll stick with individual file execution
        
        return results
    
    def extract_test_summary(self, output: str) -> Dict[str, int]:
        """Extract test summary statistics from unittest output.
        
        Args:
            output: Raw unittest output
            
        Returns:
            Dictionary with test counts
        """
        # Look for "Ran X tests in Y.Zs" line
        time_match = self.time_pattern.search(output)
        total_tests = int(time_match.group(1)) if time_match else 0
        
        # Look for summary line
        summary_match = self.summary_pattern.search(output)
        
        failures = 0
        errors = 0
        skipped = 0
        
        if summary_match:
            # Extract failure count
            if summary_match.group(2):
                failures = int(summary_match.group(2))
            
            # Extract error count
            if summary_match.group(3):
                errors = int(summary_match.group(3))
            
            # Extract skipped count
            if summary_match.group(4):
                skipped = int(summary_match.group(4))
        
        passed = total_tests - failures - errors - skipped
        
        return {
            'total': total_tests,
            'passed': passed,
            'failed': failures,
            'errors': errors,
            'skipped': skipped
        }


def main():
    """Test the parser with sample unittest output."""
    
    # Sample unittest verbose output for testing
    sample_output = """
test_node_creation (TestNodeSystem) ... ok
test_node_properties_modification (TestNodeSystem) ... ok
test_code_management (TestNodeSystem) ... FAIL
test_pin_generation_from_code (TestNodeSystem) ... ok

======================================================================
FAIL: test_code_management (TestNodeSystem)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_node_system.py", line 105, self.assertEqual(node.code, updated_code)
AssertionError: 'def example():\n    return 42' != 'def updated():\n    return 100'

----------------------------------------------------------------------
Ran 4 tests in 0.123s

FAILED (failures=1)
"""
    
    parser = TestOutputParser()
    result = parser.parse_test_file_output("test_node_system.py", sample_output, 0.123)
    
    print(f"File: {result.file_path}")
    print(f"Status: {result.status}")
    print(f"Total cases: {result.total_cases}")
    print(f"Passed: {result.passed_cases}")
    print(f"Failed: {result.failed_cases}")
    print(f"Duration: {result.duration}s")
    
    print("\nIndividual test cases:")
    for test_case in result.test_cases:
        print(f"  {test_case.name} ({test_case.class_name}): {test_case.status}")
        if test_case.error_message:
            print(f"    Error: {test_case.error_message[:100]}...")


if __name__ == "__main__":
    main()
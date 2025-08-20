#!/usr/bin/env python
"""
Test Analyzer for PyFlowGraph

Analyzes test results, identifies patterns in failures, and provides actionable
insights for test maintenance and improvement. Optimized for Claude Code integration.

Features:
    - Failure pattern analysis and categorization
    - Coverage gap identification and reporting
    - Performance bottleneck detection
    - Flaky test identification across multiple runs
    - Token-efficient reporting for Claude Code analysis
    - Integration with pytest and coverage.py
"""

import os
import sys
import json
import re
import ast
import time
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import subprocess

@dataclass
class FailurePattern:
    """Represents a categorized test failure pattern."""
    category: str
    pattern: str
    description: str
    frequency: int
    affected_tests: List[str]
    suggested_fix: str

@dataclass
class CoverageGap:
    """Represents missing test coverage."""
    file_path: str
    function_name: str
    line_numbers: List[int]
    complexity_score: float
    priority: str  # HIGH, MEDIUM, LOW

@dataclass
class PerformanceIssue:
    """Represents a test performance issue."""
    test_name: str
    duration: float
    category: str
    bottleneck_type: str  # SETUP, EXECUTION, TEARDOWN
    optimization_suggestion: str

@dataclass
class TestAnalysisReport:
    """Comprehensive test analysis report."""
    timestamp: str
    failure_patterns: List[FailurePattern]
    coverage_gaps: List[CoverageGap]
    performance_issues: List[PerformanceIssue]
    flaky_tests: List[str]
    test_health_score: float
    recommendations: List[str]

class TestAnalyzer:
    """Advanced test analyzer with pattern recognition and recommendations."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
        self.db_path = self.project_root / "test_history.db"
        self._init_database()
        
        # Failure pattern definitions
        self.failure_patterns = {
            'import_error': {
                'pattern': r'ModuleNotFoundError|ImportError',
                'description': 'Module import failures',
                'suggested_fix': 'Check PYTHONPATH and module dependencies'
            },
            'qt_application': {
                'pattern': r'QApplication|QWidget.*RuntimeError',
                'description': 'Qt application lifecycle issues',
                'suggested_fix': 'Ensure proper QApplication setup/teardown in test fixtures'
            },
            'timeout': {
                'pattern': r'timeout|TimeoutExpired',
                'description': 'Test execution timeouts',
                'suggested_fix': 'Optimize test performance or increase timeout limits'
            },
            'assertion': {
                'pattern': r'AssertionError',
                'description': 'Test assertion failures',
                'suggested_fix': 'Review test expectations and actual behavior'
            },
            'attribute_error': {
                'pattern': r'AttributeError',
                'description': 'Missing attributes or methods',
                'suggested_fix': 'Check object initialization and API changes'
            },
            'file_not_found': {
                'pattern': r'FileNotFoundError|No such file',
                'description': 'Missing test files or resources',
                'suggested_fix': 'Verify test file paths and resource availability'
            },
            'memory_error': {
                'pattern': r'MemoryError|OutOfMemoryError',
                'description': 'Memory allocation failures',
                'suggested_fix': 'Optimize memory usage or increase available memory'
            }
        }
    
    def _init_database(self):
        """Initialize SQLite database for test history tracking."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                test_name TEXT NOT NULL,
                status TEXT NOT NULL,
                duration REAL,
                error_message TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS coverage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_coverage REAL,
                function_coverage REAL,
                missing_lines TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def store_test_results(self, results_file: Path):
        """Store test results in database for historical analysis."""
        if not results_file.exists():
            return
            
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
            
            conn = sqlite3.connect(self.db_path)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            for test in data.get('tests', []):
                conn.execute('''
                    INSERT INTO test_runs (timestamp, test_name, status, duration, error_message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    test['nodeid'],
                    test['outcome'],
                    test.get('duration', 0),
                    str(test.get('call', {}).get('longrepr', '')) if test['outcome'] == 'failed' else None
                ))
            
            conn.commit()
            conn.close()
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not store test results: {e}")
    
    def analyze_failure_patterns(self, results_file: Path) -> List[FailurePattern]:
        """Analyze test failures and categorize by patterns."""
        if not results_file.exists():
            return []
        
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return []
        
        # Collect all failure messages
        failures = []
        for test in data.get('tests', []):
            if test['outcome'] == 'failed':
                error_msg = str(test.get('call', {}).get('longrepr', ''))
                failures.append({
                    'test': test['nodeid'],
                    'error': error_msg
                })
        
        # Categorize failures by patterns
        pattern_matches = defaultdict(list)
        
        for failure in failures:
            matched = False
            for category, pattern_info in self.failure_patterns.items():
                if re.search(pattern_info['pattern'], failure['error'], re.IGNORECASE):
                    pattern_matches[category].append(failure['test'])
                    matched = True
                    break
            
            if not matched:
                pattern_matches['other'].append(failure['test'])
        
        # Create FailurePattern objects
        patterns = []
        for category, tests in pattern_matches.items():
            if category == 'other':
                description = 'Uncategorized failures'
                suggested_fix = 'Manual investigation required'
                pattern = 'N/A'
            else:
                pattern_info = self.failure_patterns[category]
                description = pattern_info['description'] 
                suggested_fix = pattern_info['suggested_fix']
                pattern = pattern_info['pattern']
            
            patterns.append(FailurePattern(
                category=category,
                pattern=pattern,
                description=description,
                frequency=len(tests),
                affected_tests=tests,
                suggested_fix=suggested_fix
            ))
        
        return sorted(patterns, key=lambda x: x.frequency, reverse=True)
    
    def analyze_coverage_gaps(self) -> List[CoverageGap]:
        """Analyze code coverage and identify gaps needing tests."""
        coverage_file = self.project_root / "coverage.json"
        if not coverage_file.exists():
            return []
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
        except json.JSONDecodeError:
            return []
        
        gaps = []
        files_data = coverage_data.get('files', {})
        
        for file_path, file_data in files_data.items():
            if not file_path.startswith('src/'):
                continue
                
            missing_lines = file_data.get('missing_lines', [])
            if not missing_lines:
                continue
            
            # Analyze missing functions
            try:
                full_path = self.project_root / file_path
                if full_path.exists():
                    functions = self._extract_functions_from_file(full_path)
                    
                    for func_name, func_lines in functions.items():
                        missing_in_func = [line for line in missing_lines if line in func_lines]
                        if missing_in_func:
                            complexity = self._calculate_complexity_score(func_lines, missing_in_func)
                            priority = self._determine_priority(complexity, len(missing_in_func))
                            
                            gaps.append(CoverageGap(
                                file_path=file_path,
                                function_name=func_name,
                                line_numbers=missing_in_func,
                                complexity_score=complexity,
                                priority=priority
                            ))
            except Exception as e:
                print(f"Warning: Could not analyze {file_path}: {e}")
        
        return sorted(gaps, key=lambda x: (x.priority == 'HIGH', x.complexity_score), reverse=True)
    
    def _extract_functions_from_file(self, file_path: Path) -> Dict[str, List[int]]:
        """Extract function definitions and their line ranges from a Python file."""
        functions = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Calculate line range for function
                    start_line = node.lineno
                    end_line = start_line
                    
                    # Find the end line by looking at the last statement
                    if node.body:
                        last_stmt = node.body[-1]
                        end_line = getattr(last_stmt, 'end_lineno', last_stmt.lineno)
                    
                    functions[node.name] = list(range(start_line, end_line + 1))
                    
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
        
        return functions
    
    def _calculate_complexity_score(self, func_lines: List[int], missing_lines: List[int]) -> float:
        """Calculate complexity score based on function size and missing coverage."""
        total_lines = len(func_lines)
        missing_count = len(missing_lines)
        
        if total_lines == 0:
            return 0.0
        
        # Base score from missing line ratio
        missing_ratio = missing_count / total_lines
        
        # Increase score for larger functions (more complex)
        size_factor = min(total_lines / 20, 2.0)  # Cap at 2x
        
        return missing_ratio * size_factor
    
    def _determine_priority(self, complexity: float, missing_lines: int) -> str:
        """Determine priority level for coverage gap."""
        if complexity > 1.5 or missing_lines > 10:
            return 'HIGH'
        elif complexity > 0.5 or missing_lines > 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def analyze_performance_issues(self, results_file: Path) -> List[PerformanceIssue]:
        """Analyze test performance and identify bottlenecks."""
        if not results_file.exists():
            return []
        
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return []
        
        issues = []
        
        for test in data.get('tests', []):
            duration = test.get('duration', 0)
            
            # Flag tests slower than 5 seconds (per CLAUDE.md requirement)
            if duration > 5.0:
                test_name = test['nodeid']
                category = self._categorize_test(test_name)
                bottleneck_type = self._identify_bottleneck_type(test_name, duration)
                suggestion = self._get_optimization_suggestion(category, bottleneck_type, duration)
                
                issues.append(PerformanceIssue(
                    test_name=test_name,
                    duration=duration,
                    category=category,
                    bottleneck_type=bottleneck_type,
                    optimization_suggestion=suggestion
                ))
        
        return sorted(issues, key=lambda x: x.duration, reverse=True)
    
    def _categorize_test(self, test_name: str) -> str:
        """Categorize test based on its name and path."""
        if "gui" in test_name.lower():
            return "gui"
        elif "headless" in test_name.lower():
            return "headless"
        elif "integration" in test_name.lower():
            return "integration"
        else:
            return "unit"
    
    def _identify_bottleneck_type(self, test_name: str, duration: float) -> str:
        """Identify the likely bottleneck type based on test characteristics."""
        if "setup" in test_name.lower() or "setUp" in test_name:
            return "SETUP"
        elif "teardown" in test_name.lower() or "tearDown" in test_name:
            return "TEARDOWN"
        elif duration > 8.0:
            return "EXECUTION"
        else:
            return "EXECUTION"
    
    def _get_optimization_suggestion(self, category: str, bottleneck_type: str, duration: float) -> str:
        """Generate optimization suggestions based on test characteristics."""
        suggestions = {
            ("gui", "SETUP"): "Use class-level QApplication setup to avoid repeated initialization",
            ("gui", "EXECUTION"): "Mock Qt operations or use headless testing where possible",
            ("gui", "TEARDOWN"): "Optimize widget cleanup and memory management",
            ("unit", "EXECUTION"): "Profile test logic and mock expensive operations",
            ("integration", "EXECUTION"): "Use test doubles for external dependencies",
            ("headless", "EXECUTION"): "Review algorithms and data structures for efficiency"
        }
        
        key = (category, bottleneck_type)
        if key in suggestions:
            return suggestions[key]
        else:
            return f"Profile {bottleneck_type.lower()} phase to identify specific bottlenecks"
    
    def identify_flaky_tests(self) -> List[str]:
        """Identify tests that have inconsistent results across runs."""
        conn = sqlite3.connect(self.db_path)
        
        # Find tests with both pass and fail outcomes in recent history
        query = '''
            SELECT test_name, COUNT(DISTINCT status) as status_count,
                   COUNT(*) as total_runs,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failures
            FROM test_runs 
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY test_name
            HAVING status_count > 1 AND total_runs >= 3
        '''
        
        cursor = conn.execute(query)
        flaky_tests = []
        
        for row in cursor.fetchall():
            test_name, status_count, total_runs, failures = row
            failure_rate = failures / total_runs
            
            # Consider a test flaky if it fails 20-80% of the time
            if 0.2 <= failure_rate <= 0.8:
                flaky_tests.append(test_name)
        
        conn.close()
        return flaky_tests
    
    def calculate_test_health_score(self, analysis_report: TestAnalysisReport) -> float:
        """Calculate overall test suite health score (0-100)."""
        score = 100.0
        
        # Deduct points for failures
        failure_penalty = sum(fp.frequency for fp in analysis_report.failure_patterns) * 5
        score -= min(failure_penalty, 40)  # Cap at 40 points
        
        # Deduct points for coverage gaps
        high_priority_gaps = len([gap for gap in analysis_report.coverage_gaps if gap.priority == 'HIGH'])
        score -= min(high_priority_gaps * 10, 30)  # Cap at 30 points
        
        # Deduct points for performance issues
        slow_tests = len(analysis_report.performance_issues)
        score -= min(slow_tests * 3, 20)  # Cap at 20 points
        
        # Deduct points for flaky tests
        flaky_count = len(analysis_report.flaky_tests)
        score -= min(flaky_count * 5, 10)  # Cap at 10 points
        
        return max(score, 0.0)
    
    def generate_recommendations(self, analysis_report: TestAnalysisReport) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Failure pattern recommendations
        if analysis_report.failure_patterns:
            top_pattern = analysis_report.failure_patterns[0]
            recommendations.append(
                f"Priority: Fix {top_pattern.category} failures affecting {top_pattern.frequency} tests. "
                f"Suggestion: {top_pattern.suggested_fix}"
            )
        
        # Coverage recommendations
        high_priority_gaps = [gap for gap in analysis_report.coverage_gaps if gap.priority == 'HIGH']
        if high_priority_gaps:
            recommendations.append(
                f"Add tests for {len(high_priority_gaps)} high-priority uncovered functions. "
                f"Start with: {high_priority_gaps[0].file_path}::{high_priority_gaps[0].function_name}"
            )
        
        # Performance recommendations
        if analysis_report.performance_issues:
            slowest = analysis_report.performance_issues[0]
            recommendations.append(
                f"Optimize slow test: {slowest.test_name} ({slowest.duration:.2f}s). "
                f"Suggestion: {slowest.optimization_suggestion}"
            )
        
        # Flaky test recommendations
        if analysis_report.flaky_tests:
            recommendations.append(
                f"Investigate {len(analysis_report.flaky_tests)} flaky tests for non-deterministic behavior. "
                f"Start with: {analysis_report.flaky_tests[0]}"
            )
        
        # Health score recommendations
        if analysis_report.test_health_score < 70:
            recommendations.append(
                "Test suite health is below 70%. Focus on reducing failures and improving coverage."
            )
        
        return recommendations
    
    def analyze(self, results_file: Path = None) -> TestAnalysisReport:
        """Perform comprehensive test analysis."""
        if results_file is None:
            results_file = self.project_root / "test_results.json"
        
        # Store results for historical analysis
        self.store_test_results(results_file)
        
        # Perform analysis
        failure_patterns = self.analyze_failure_patterns(results_file)
        coverage_gaps = self.analyze_coverage_gaps()
        performance_issues = self.analyze_performance_issues(results_file)
        flaky_tests = self.identify_flaky_tests()
        
        # Create report
        report = TestAnalysisReport(
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            failure_patterns=failure_patterns,
            coverage_gaps=coverage_gaps,
            performance_issues=performance_issues,
            flaky_tests=flaky_tests,
            test_health_score=0.0,  # Will be calculated
            recommendations=[]  # Will be generated
        )
        
        # Calculate health score and recommendations
        report.test_health_score = self.calculate_test_health_score(report)
        report.recommendations = self.generate_recommendations(report)
        
        return report
    
    def format_report(self, report: TestAnalysisReport, format_type: str = "detailed") -> str:
        """Format analysis report for different output types."""
        if format_type == "claude":
            return self._format_claude_report(report)
        elif format_type == "summary":
            return self._format_summary_report(report)
        else:
            return self._format_detailed_report(report)
    
    def _format_claude_report(self, report: TestAnalysisReport) -> str:
        """Token-efficient format optimized for Claude Code analysis."""
        lines = [
            f"=== TEST ANALYSIS REPORT ===",
            f"Health Score: {report.test_health_score:.1f}/100",
            f"Analysis Time: {report.timestamp}",
            ""
        ]
        
        # Top issues (most important for Claude Code)
        if report.failure_patterns:
            lines.append("=== TOP FAILURE PATTERNS ===")
            for pattern in report.failure_patterns[:3]:
                lines.append(f"• {pattern.category}: {pattern.frequency} tests")
                lines.append(f"  Fix: {pattern.suggested_fix}")
            lines.append("")
        
        # Critical coverage gaps
        high_gaps = [gap for gap in report.coverage_gaps if gap.priority == 'HIGH']
        if high_gaps:
            lines.append("=== HIGH PRIORITY COVERAGE GAPS ===")
            for gap in high_gaps[:3]:
                lines.append(f"• {gap.file_path}::{gap.function_name} ({len(gap.line_numbers)} lines)")
            lines.append("")
        
        # Performance issues
        if report.performance_issues:
            lines.append("=== SLOW TESTS (>5s) ===")
            for issue in report.performance_issues[:3]:
                lines.append(f"• {issue.test_name}: {issue.duration:.2f}s")
                lines.append(f"  Fix: {issue.optimization_suggestion}")
            lines.append("")
        
        # Flaky tests
        if report.flaky_tests:
            lines.append(f"=== FLAKY TESTS ({len(report.flaky_tests)}) ===")
            for test in report.flaky_tests[:3]:
                lines.append(f"• {test}")
            lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("=== RECOMMENDATIONS ===")
            for i, rec in enumerate(report.recommendations[:3], 1):
                lines.append(f"{i}. {rec}")
        
        return '\n'.join(lines)
    
    def _format_summary_report(self, report: TestAnalysisReport) -> str:
        """Brief summary format."""
        return (
            f"Test Health: {report.test_health_score:.1f}/100 | "
            f"Failures: {len(report.failure_patterns)} patterns | "
            f"Coverage: {len([g for g in report.coverage_gaps if g.priority == 'HIGH'])} gaps | "
            f"Slow: {len(report.performance_issues)} tests | "
            f"Flaky: {len(report.flaky_tests)} tests"
        )
    
    def _format_detailed_report(self, report: TestAnalysisReport) -> str:
        """Detailed human-readable format."""
        lines = [
            "=" * 60,
            "PyFlowGraph Test Analysis Report",
            "=" * 60,
            f"Generated: {report.timestamp}",
            f"Test Health Score: {report.test_health_score:.1f}/100",
            ""
        ]
        
        # Failure patterns
        if report.failure_patterns:
            lines.append("Failure Patterns:")
            for pattern in report.failure_patterns:
                lines.append(f"  {pattern.category}: {pattern.frequency} occurrences")
                lines.append(f"    Pattern: {pattern.pattern}")
                lines.append(f"    Description: {pattern.description}")
                lines.append(f"    Suggested Fix: {pattern.suggested_fix}")
                if pattern.affected_tests:
                    lines.append(f"    Affected Tests: {', '.join(pattern.affected_tests[:3])}")
                    if len(pattern.affected_tests) > 3:
                        lines.append(f"      ... and {len(pattern.affected_tests) - 3} more")
                lines.append("")
        
        # Coverage gaps
        if report.coverage_gaps:
            lines.append("Coverage Gaps:")
            high_gaps = [gap for gap in report.coverage_gaps if gap.priority == 'HIGH']
            if high_gaps:
                lines.append("  High Priority:")
                for gap in high_gaps:
                    lines.append(f"    {gap.file_path}::{gap.function_name}")
                    lines.append(f"      Missing lines: {gap.line_numbers}")
                    lines.append(f"      Complexity: {gap.complexity_score:.2f}")
            lines.append("")
        
        # Performance issues
        if report.performance_issues:
            lines.append("Performance Issues:")
            for issue in report.performance_issues:
                lines.append(f"  {issue.test_name}: {issue.duration:.2f}s")
                lines.append(f"    Category: {issue.category}")
                lines.append(f"    Bottleneck: {issue.bottleneck_type}")
                lines.append(f"    Suggestion: {issue.optimization_suggestion}")
            lines.append("")
        
        # Flaky tests
        if report.flaky_tests:
            lines.append(f"Flaky Tests ({len(report.flaky_tests)}):")
            for test in report.flaky_tests:
                lines.append(f"  {test}")
            lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"  {i}. {rec}")
        
        return '\n'.join(lines)

def main():
    """Main entry point for the test analyzer."""
    parser = argparse.ArgumentParser(
        description="Test Analyzer for PyFlowGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_analyzer.py                           # Analyze latest test results
  python test_analyzer.py --results test_output.json  # Analyze specific results
  python test_analyzer.py --format claude             # Claude Code optimized output
  python test_analyzer.py --coverage-only             # Focus on coverage analysis
        """
    )
    
    parser.add_argument("--results", type=Path,
                       help="Test results JSON file to analyze")
    parser.add_argument("--format", choices=["detailed", "summary", "claude"],
                       default="detailed", help="Output format")
    parser.add_argument("--coverage-only", action="store_true",
                       help="Focus only on coverage analysis")
    parser.add_argument("--output-file", type=Path,
                       help="Save report to file")
    
    args = parser.parse_args()
    
    try:
        analyzer = TestAnalyzer()
        
        if args.coverage_only:
            # Just analyze coverage gaps
            gaps = analyzer.analyze_coverage_gaps()
            print(f"Found {len(gaps)} coverage gaps")
            for gap in gaps:
                print(f"  {gap.priority}: {gap.file_path}::{gap.function_name}")
        else:
            # Full analysis
            report = analyzer.analyze(args.results)
            formatted_report = analyzer.format_report(report, args.format)
            
            print(formatted_report)
            
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(formatted_report)
                print(f"\nReport saved to: {args.output_file}")
    
    except Exception as e:
        print(f"Error analyzing tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
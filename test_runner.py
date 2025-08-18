#!/usr/bin/env python
"""
Advanced Test Runner for PyFlowGraph

Provides parallel execution, performance tracking, and intelligent test selection
optimized for Claude Code integration and token efficiency.

Usage:
    python test_runner.py [options]
    
Features:
    - Parallel test execution with auto worker detection
    - Performance profiling and bottleneck identification  
    - Intelligent test filtering based on code changes
    - Token-efficient output formatting for Claude Code
    - Integration with existing PyFlowGraph test infrastructure
"""

import os
import sys
import time
import json
import argparse
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class TestResult:
    """Test execution result with performance metrics."""
    name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    duration: float
    category: str  # unit, integration, gui, headless
    error_message: Optional[str] = None
    
@dataclass 
class TestSuiteReport:
    """Comprehensive test suite execution report."""
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    parallel_workers: int
    results: List[TestResult]
    performance_summary: Dict[str, float]
    
class TestRunner:
    """Advanced test runner with parallel execution and performance tracking."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
        
    def detect_pytest_binary(self) -> str:
        """Detect the appropriate pytest binary."""
        # Try venv first, then global
        venv_pytest = self.project_root / "venv" / "Scripts" / "pytest.exe"
        if venv_pytest.exists():
            return str(venv_pytest)
        
        # Try alternative venv location
        venvs_pytest = self.project_root / "venvs" / "Scripts" / "pytest.exe"
        if venvs_pytest.exists():
            return str(venvs_pytest)
            
        # Fall back to global pytest
        return "pytest"
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed files using git (if available)."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1"], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return []
    
    def map_files_to_tests(self, changed_files: List[str]) -> List[str]:
        """Map changed source files to their corresponding test files."""
        test_files = []
        
        for file_path in changed_files:
            if file_path.startswith('src/'):
                # Convert src/module.py to tests/test_module.py
                module_name = Path(file_path).stem
                test_file = self.test_dir / f"test_{module_name}.py"
                if test_file.exists():
                    test_files.append(str(test_file))
                    
                # Also check headless tests
                headless_test = self.test_dir / "headless" / f"test_{module_name}.py"
                if headless_test.exists():
                    test_files.append(str(headless_test))
                    
            elif file_path.startswith('tests/'):
                # Direct test file change
                if Path(file_path).exists():
                    test_files.append(file_path)
                    
        return list(set(test_files))  # Remove duplicates
    
    def build_pytest_command(self, args: argparse.Namespace) -> List[str]:
        """Build pytest command with appropriate options."""
        cmd = [self.detect_pytest_binary()]
        
        # Test selection
        if args.fast:
            cmd.extend(["-m", "not gui and not slow"])
        elif args.gui_only:
            cmd.extend(["-m", "gui"])
        elif args.unit_only:
            cmd.extend(["-m", "unit"])
        elif args.changed:
            changed_files = self.get_changed_files()
            test_files = self.map_files_to_tests(changed_files)
            if test_files:
                cmd.extend(test_files)
            else:
                print("No test files found for changed source files, running all tests")
        
        # Parallel execution
        if not args.no_parallel:
            workers = args.workers if args.workers else "auto"
            cmd.extend(["-n", str(workers)])
        
        # Coverage
        if args.coverage:
            cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=json"])
        
        # Output format
        if args.verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
            
        # Performance tracking
        cmd.extend(["--durations=10"])
        
        # Timeout (enforce 10-second rule from CLAUDE.md)
        cmd.extend(["--timeout=10"])
        
        # JSON output for parsing
        cmd.extend(["--json-report", "--json-report-file=test_results.json"])
        
        return cmd
    
    def run_tests(self, args: argparse.Namespace) -> TestSuiteReport:
        """Execute tests and collect results."""
        start_time = time.time()
        
        cmd = self.build_pytest_command(args)
        
        print(f"Running: {' '.join(cmd)}")
        print(f"Working directory: {self.project_root}")
        
        # Execute tests
        result = subprocess.run(
            cmd, 
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Parse results
        return self.parse_test_results(result, total_duration, args)
    
    def parse_test_results(self, result: subprocess.CompletedProcess, 
                          total_duration: float, args: argparse.Namespace) -> TestSuiteReport:
        """Parse pytest results into structured format."""
        
        # Try to load JSON report if available
        json_file = self.project_root / "test_results.json"
        test_results = []
        summary = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
        
        if json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                for test in data.get('tests', []):
                    category = self.categorize_test(test['nodeid'])
                    test_result = TestResult(
                        name=test['nodeid'],
                        status=test['outcome'].upper(),
                        duration=test.get('duration', 0),
                        category=category,
                        error_message=test.get('call', {}).get('longrepr') if test['outcome'] == 'failed' else None
                    )
                    test_results.append(test_result)
                    
                summary = data.get('summary', summary)
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse JSON report: {e}")
        
        # Performance analysis
        perf_summary = self.analyze_performance(test_results)
        
        return TestSuiteReport(
            total_tests=len(test_results),
            passed=summary.get('passed', 0),
            failed=summary.get('failed', 0), 
            skipped=summary.get('skipped', 0),
            errors=summary.get('error', 0),
            total_duration=total_duration,
            parallel_workers=args.workers or "auto",
            results=test_results,
            performance_summary=perf_summary
        )
    
    def categorize_test(self, test_name: str) -> str:
        """Categorize test based on its path and name."""
        if "gui" in test_name.lower():
            return "gui"
        elif "headless" in test_name.lower():
            return "headless"
        elif "integration" in test_name.lower():
            return "integration"
        else:
            return "unit"
    
    def analyze_performance(self, results: List[TestResult]) -> Dict[str, float]:
        """Analyze test performance and identify bottlenecks."""
        if not results:
            return {}
            
        durations = [r.duration for r in results]
        
        # Calculate performance metrics
        total_time = sum(durations)
        avg_time = total_time / len(durations) if durations else 0
        max_time = max(durations) if durations else 0
        
        # Category breakdown
        category_times = {}
        for result in results:
            if result.category not in category_times:
                category_times[result.category] = []
            category_times[result.category].append(result.duration)
        
        perf_summary = {
            "total_time": total_time,
            "average_time": avg_time,
            "max_time": max_time,
            "slow_tests_count": len([d for d in durations if d > 5.0]),
        }
        
        # Add category averages
        for category, times in category_times.items():
            perf_summary[f"{category}_avg"] = sum(times) / len(times)
            
        return perf_summary
    
    def format_report(self, report: TestSuiteReport, format_type: str = "detailed") -> str:
        """Format test report for different output types."""
        
        if format_type == "claude":
            return self.format_claude_report(report)
        elif format_type == "summary":
            return self.format_summary_report(report)
        else:
            return self.format_detailed_report(report)
    
    def format_claude_report(self, report: TestSuiteReport) -> str:
        """Token-efficient format optimized for Claude Code analysis."""
        
        # Status symbols for compression
        status_map = {"PASS": "✓", "FAIL": "✗", "SKIP": "○", "ERROR": "⚠"}
        
        lines = [
            f"=== TEST EXECUTION REPORT ===",
            f"Total: {report.total_tests} | Pass: {report.passed} | Fail: {report.failed} | Skip: {report.skipped}",
            f"Duration: {report.total_duration:.2f}s | Workers: {report.parallel_workers}",
            ""
        ]
        
        # Failed tests first (most important)
        failed_tests = [r for r in report.results if r.status == "FAIL"]
        if failed_tests:
            lines.append("=== FAILURES ===")
            for test in failed_tests[:5]:  # Limit to top 5 failures
                lines.append(f"✗ {test.name} ({test.duration:.2f}s)")
                if test.error_message:
                    # Compress error message
                    error_summary = test.error_message.split('\n')[0][:100] + "..."
                    lines.append(f"  Error: {error_summary}")
            lines.append("")
        
        # Performance issues
        slow_tests = [r for r in report.results if r.duration > 5.0]
        if slow_tests:
            lines.append("=== SLOW TESTS (>5s) ===")
            for test in sorted(slow_tests, key=lambda x: x.duration, reverse=True)[:3]:
                lines.append(f"⚠ {test.name} ({test.duration:.2f}s)")
            lines.append("")
        
        # Performance summary
        perf = report.performance_summary
        lines.extend([
            "=== PERFORMANCE ===",
            f"Avg: {perf.get('average_time', 0):.2f}s | Max: {perf.get('max_time', 0):.2f}s",
            f"Slow tests: {perf.get('slow_tests_count', 0)}",
        ])
        
        # Category breakdown
        categories = ["gui", "unit", "integration", "headless"]
        cat_summary = []
        for cat in categories:
            avg_key = f"{cat}_avg"
            if avg_key in perf:
                cat_summary.append(f"{cat}: {perf[avg_key]:.2f}s")
        
        if cat_summary:
            lines.append(f"Categories: {' | '.join(cat_summary)}")
        
        return '\n'.join(lines)
    
    def format_summary_report(self, report: TestSuiteReport) -> str:
        """Brief summary format."""
        status = "PASS" if report.failed == 0 and report.errors == 0 else "FAIL"
        return f"Tests: {status} ({report.passed}/{report.total_tests}) in {report.total_duration:.2f}s"
    
    def format_detailed_report(self, report: TestSuiteReport) -> str:
        """Detailed human-readable format."""
        lines = [
            "=" * 60,
            "PyFlowGraph Test Execution Report",
            "=" * 60,
            "",
            f"Execution Summary:",
            f"  Total Tests: {report.total_tests}",
            f"  Passed: {report.passed}",
            f"  Failed: {report.failed}",
            f"  Skipped: {report.skipped}",
            f"  Errors: {report.errors}",
            f"  Duration: {report.total_duration:.2f} seconds",
            f"  Workers: {report.parallel_workers}",
            ""
        ]
        
        # Performance analysis
        perf = report.performance_summary
        lines.extend([
            "Performance Analysis:",
            f"  Average test time: {perf.get('average_time', 0):.3f}s",
            f"  Slowest test: {perf.get('max_time', 0):.3f}s", 
            f"  Slow tests (>5s): {perf.get('slow_tests_count', 0)}",
            ""
        ])
        
        # Failed tests
        failed_tests = [r for r in report.results if r.status == "FAIL"]
        if failed_tests:
            lines.append("Failed Tests:")
            for test in failed_tests:
                lines.append(f"  FAIL: {test.name} ({test.duration:.3f}s)")
                if test.error_message:
                    error_lines = test.error_message.split('\n')[:3]  # First 3 lines
                    for error_line in error_lines:
                        lines.append(f"    {error_line}")
            lines.append("")
        
        return '\n'.join(lines)

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Advanced Test Runner for PyFlowGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                    # Run all tests in parallel
  python test_runner.py --fast             # Run only fast tests (no GUI)
  python test_runner.py --gui-only         # Run only GUI tests
  python test_runner.py --changed          # Run tests for changed files
  python test_runner.py --coverage         # Run with coverage analysis
  python test_runner.py --format claude    # Claude Code optimized output
        """
    )
    
    # Test selection options
    parser.add_argument("--fast", action="store_true", 
                       help="Run fast tests only (skip GUI and slow tests)")
    parser.add_argument("--gui-only", action="store_true",
                       help="Run GUI tests only")
    parser.add_argument("--unit-only", action="store_true", 
                       help="Run unit tests only")
    parser.add_argument("--changed", action="store_true",
                       help="Run tests for changed files only (requires git)")
    
    # Execution options  
    parser.add_argument("--no-parallel", action="store_true",
                       help="Disable parallel execution")
    parser.add_argument("--workers", type=int,
                       help="Number of parallel workers (default: auto)")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report")
    
    # Output options
    parser.add_argument("--format", choices=["detailed", "summary", "claude"],
                       default="detailed", help="Output format")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("--output-file", 
                       help="Save report to file")
    
    args = parser.parse_args()
    
    # Run tests
    runner = TestRunner()
    
    try:
        report = runner.run_tests(args)
        
        # Format and display results
        formatted_report = runner.format_report(report, args.format)
        print(formatted_report)
        
        # Save to file if requested
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(formatted_report)
            print(f"\nReport saved to: {args.output_file}")
        
        # Exit with appropriate code
        exit_code = 0 if report.failed == 0 and report.errors == 0 else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
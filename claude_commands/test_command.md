# Enhanced /test Command for PyFlowGraph

## Overview
Advanced test execution command with intelligent filtering, parallel execution, and Claude Code optimized reporting. Integrates with pytest configuration and custom test utilities.

## Command Syntax
```
/test [TARGET] [OPTIONS]
```

## Targets
- `all` - Run complete test suite (default)
- `fast` - Unit and headless tests only (skip GUI, <30s total)
- `gui` - GUI tests only (PySide6/Qt focused)
- `unit` - Unit tests only (isolated components)
- `integration` - Integration tests (component interactions)
- `changed` - Tests for files modified since last commit
- `failed` - Re-run previously failed tests only
- `slow` - Tests taking >5 seconds (performance analysis)
- `<filename>` - Specific test file or pattern

## Options

### Execution Control
- `--parallel` - Enable parallel execution (default: auto workers)
- `--workers N` - Specify number of parallel workers
- `--no-parallel` - Force sequential execution
- `--timeout N` - Test timeout in seconds (default: 10)
- `--fail-fast` - Stop on first failure

### Filtering
- `--marker MARKER` - Run tests with specific pytest marker
- `--category CAT` - Filter by category (unit|integration|gui|headless)
- `--exclude PATTERN` - Exclude tests matching pattern
- `--include PATTERN` - Include only tests matching pattern

### Analysis
- `--coverage` - Generate coverage report
- `--profile` - Enable performance profiling
- `--analyze` - Run post-test analysis
- `--health` - Calculate test health metrics

### Output
- `--format FORMAT` - Output format (detailed|summary|claude|json)
- `--verbose` - Detailed test output
- `--quiet` - Minimal output
- `--save FILE` - Save results to file

## Implementation Examples

### Fast Development Cycle
```bash
/test fast --parallel --format claude
# Runs unit + headless tests in parallel, Claude-optimized output
# Expected: <30s execution, token-efficient results
```

### GUI Test Focus
```bash
/test gui --no-parallel --verbose --timeout 15
# Sequential GUI tests with extended timeout
# Handles QApplication setup conflicts
```

### Performance Analysis
```bash
/test slow --profile --analyze
# Focus on slow tests with performance profiling
# Identifies optimization opportunities
```

### Coverage-Driven Development
```bash
/test changed --coverage --analyze
# Tests for modified files with coverage analysis
# Shows impact of recent changes
```

### CI/CD Integration
```bash
/test all --parallel --format json --save results.json --fail-fast
# Complete suite with machine-readable output
# Optimized for automated environments
```

## Claude Code Integration Features

### Token-Efficient Reporting
- Compressed status indicators (✓✗⚠○)
- Top 3 failures with specific recommendations
- Performance summary with optimization targets
- Coverage delta highlighting critical gaps

### Intelligent Analysis
- Automatic failure pattern categorization
- Performance bottleneck identification
- Flaky test detection across runs
- Coverage gap prioritization

### Actionable Recommendations
- Specific file/line references for issues
- Optimization suggestions for slow tests
- Test generation recommendations for coverage gaps
- Maintenance priorities based on health metrics

## Advanced Features

### Smart Test Selection
- Git-aware change detection for targeted testing
- Dependency analysis for impact assessment
- Risk-based test prioritization
- Historical failure pattern consideration

### Performance Optimization
- Automatic worker count optimization based on system resources
- Test isolation for parallel execution safety
- Memory usage monitoring and limits
- Timeout prevention with early warning system

### Quality Gates
- Health score calculation and trending
- Regression detection across test runs
- Coverage threshold enforcement
- Performance baseline tracking

## Error Handling and Recovery

### Common Issues
- **QApplication conflicts**: Automatic sequential fallback for GUI tests
- **Import errors**: Clear dependency and PYTHONPATH messaging
- **Timeout handling**: Graceful termination with partial results
- **Resource exhaustion**: Automatic worker reduction and retry

### Recovery Strategies
- Fallback to sequential execution on parallel failures
- Partial result reporting when tests interrupted
- Automatic retry for known flaky tests
- Graceful degradation when analysis tools unavailable

## Output Formats

### Claude Format (Default for Claude Code)
```
=== TEST EXECUTION REPORT ===
Status: PASS (45/47) | Duration: 23.4s | Workers: 4

=== FAILURES (2) ===
✗ test_node_deletion (2.1s) - AssertionError: Node not removed from graph
  Fix: Check node.parent() removal in delete_node()
✗ test_gui_startup (5.8s) - QApplication RuntimeError
  Fix: Use class-level QApplication setup

=== PERFORMANCE ===
Slow tests: 3 | Avg: 0.8s | Max: 5.8s
Categories: gui:2.1s | unit:0.3s | integration:1.2s

=== RECOMMENDATIONS ===
1. Fix GUI test QApplication lifecycle conflicts
2. Optimize test_gui_startup performance (<5s target)
3. Add coverage for NodeGraph.clear_graph() method
```

### Summary Format
```
Tests: PASS (45/47) | 23.4s | 2 failures | 3 slow tests
```

### JSON Format (for automation)
```json
{
  "status": "PASS",
  "total": 47,
  "passed": 45,
  "failed": 2,
  "duration": 23.4,
  "failures": [...],
  "performance": {...},
  "coverage": {...}
}
```

## Performance Targets

### Execution Time Goals
- **Fast tests**: <30 seconds total
- **Unit tests**: <10 seconds total
- **Integration tests**: <60 seconds total
- **Full suite**: <120 seconds with parallel execution

### Resource Efficiency
- **Memory usage**: <500MB peak
- **CPU utilization**: Optimal worker count based on cores
- **Token efficiency**: <2K tokens for standard Claude reports
- **Storage**: <10MB for all test artifacts

## Integration Points

### Existing Tools
- **pytest.ini**: Leverages markers and configuration
- **test_runner.py**: Uses advanced runner for execution
- **test_analyzer.py**: Integrates analysis and reporting
- **run_test_gui.bat**: Maintains compatibility with existing workflow

### Claude Code Workflow
- **Automatic activation**: Triggered by test-related keywords
- **Context awareness**: Adapts to PyFlowGraph architecture
- **Learning system**: Improves recommendations based on outcomes
- **Token optimization**: Balances detail with efficiency

## Usage Patterns

### Development Workflow
1. **Code changes**: `/test changed --fast` for quick feedback
2. **Feature development**: `/test unit --coverage` for TDD
3. **Integration testing**: `/test integration --analyze` 
4. **Pre-commit**: `/test all --parallel --format claude`

### Debugging Workflow
1. **Failure investigation**: `/test failed --verbose --analyze`
2. **Performance issues**: `/test slow --profile`
3. **Flaky tests**: `/test <test_name> --repeat 10`
4. **Coverage gaps**: `/test --coverage --analyze`

### Maintenance Workflow
1. **Health check**: `/test --health --format claude`
2. **Performance audit**: `/test all --profile --analyze`
3. **Coverage review**: `/test --coverage --save coverage.json`
4. **Optimization**: `/test slow --analyze --save performance.md`
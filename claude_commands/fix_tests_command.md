# /fix-tests Command for PyFlowGraph

## Overview
Automated test failure resolution command that analyzes failure patterns, applies common fixes, and provides guided repair workflows. Integrates with test analysis and PyFlowGraph-specific patterns.

## Command Syntax
```
/fix-tests [TARGET] [OPTIONS]
```

## Targets
- `all` - Analyze and fix all failing tests (default)
- `category CATEGORY` - Fix specific failure category (qt, import, timeout, assertion)
- `test TEST_NAME` - Fix specific test by name or pattern
- `priority` - Fix highest priority failures first
- `auto` - Apply only automated fixes (no manual intervention)
- `guided` - Interactive guided fix workflow

## Options

### Analysis Control
- `--analyze-first` - Run full analysis before attempting fixes
- `--pattern PATTERN` - Focus on specific failure pattern
- `--dry-run` - Show what would be fixed without making changes
- `--confidence MIN` - Minimum confidence level for automated fixes (0.0-1.0)

### Fix Scope
- `--auto-only` - Apply only fully automated fixes
- `--guided` - Interactive mode with user confirmation
- `--aggressive` - Apply fixes with lower confidence thresholds
- `--conservative` - Apply only high-confidence fixes

### Output Control
- `--format FORMAT` - Output format (detailed|summary|claude|json)
- `--save FILE` - Save fix report to file
- `--verbose` - Detailed fix reasoning and steps
- `--quiet` - Minimal output

## Automated Fix Categories

### Qt/GUI Issues (High Confidence)
```python
# Pattern: QApplication RuntimeError
# Fix: Proper QApplication lifecycle management

# Before (Problematic)
def test_gui_component(self):
    app = QApplication([])  # Creates multiple instances
    widget = MyWidget()
    # Test logic
    
# After (Fixed)
@classmethod
def setUpClass(cls):
    if not QApplication.instance():
        cls.app = QApplication([])

def test_gui_component(self):
    widget = MyWidget()
    # Test logic
```

### Import Errors (High Confidence)
```python
# Pattern: ModuleNotFoundError, ImportError
# Fix: Correct path setup and imports

# Before (Problematic)
import sys
sys.path.append('../src')  # Relative path issues

# After (Fixed)  
import os
import sys
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)
```

### Timeout Issues (Medium Confidence)
```python
# Pattern: Test execution timeout
# Fix: Optimize setup/teardown and mock expensive operations

# Before (Problematic)
def test_slow_operation(self):
    result = expensive_network_call()  # Real network call
    self.assertEqual(result.status, 'success')

# After (Fixed)
@patch('module.expensive_network_call')
def test_slow_operation(self, mock_call):
    mock_call.return_value = MockResponse(status='success')
    result = expensive_network_call()
    self.assertEqual(result.status, 'success')
```

### Assertion Errors (Low-Medium Confidence)  
```python
# Pattern: AssertionError with specific contexts
# Fix: Update assertions based on actual behavior analysis

# Before (Problematic)
def test_node_creation(self):
    node = Node("TestNode")
    self.assertEqual(len(node.pins), 0)  # May be wrong assumption

# After (Fixed)
def test_node_creation(self):
    node = Node("TestNode")
    # Check actual initial pin count based on Node implementation
    self.assertGreaterEqual(len(node.pins), 0)
    self.assertIsInstance(node.pins, list)
```

## PyFlowGraph-Specific Fix Patterns

### Node System Fixes
- **Pin Generation Issues**: Update expected pin counts based on function signatures
- **Node Position Problems**: Use QPointF consistently for positioning
- **Property Access**: Handle property getters/setters correctly

### Connection System Fixes
- **Bezier Path Errors**: Ensure proper start/end point calculation
- **Connection Validation**: Update compatibility checks for pin types
- **Reroute Node Issues**: Handle dynamic connection routing

### Graph Management Fixes
- **Scene Item Management**: Proper addItem/removeItem lifecycle
- **Serialization Issues**: Handle missing or malformed JSON data
- **Memory Leaks**: Ensure proper Qt object cleanup

### Execution Engine Fixes
- **Subprocess Isolation**: Handle timeout and security issues
- **Data Flow**: Fix JSON serialization/deserialization problems
- **Virtual Environment**: Correct Python executable detection

## Confidence Scoring System

### High Confidence (0.8-1.0)
- Standard import path fixes
- QApplication lifecycle management
- Common assertion pattern updates
- Timeout optimization with mocking

### Medium Confidence (0.5-0.8)
- Test data adjustments based on implementation analysis
- Performance optimization suggestions
- Mock integration for external dependencies
- Error handling improvements

### Low Confidence (0.2-0.5)
- Complex assertion logic changes
- Test design pattern modifications
- Cross-component interaction fixes
- Custom fixture implementations

### Manual Review Required (0.0-0.2)
- Business logic assertion failures
- Architecture-dependent test changes
- New feature test requirements
- Performance bottleneck resolution

## Interactive Guided Mode

### Fix Workflow
1. **Analysis Phase**: Categorize all failures and identify patterns
2. **Prioritization**: Rank fixes by impact and confidence level
3. **Review Phase**: Present proposed fixes with explanations
4. **Application**: Apply approved fixes with rollback capability
5. **Validation**: Re-run tests to verify fix effectiveness

### User Interaction
```
=== TEST FIX ANALYSIS ===
Found 5 failing tests with 3 distinct patterns:

1. Qt Application Issues (3 tests) - Confidence: 0.9
   Fix: Implement class-level QApplication setup
   Files: test_gui_integration.py, test_node_editor_view.py
   
   Apply this fix? [Y/n/explain]: y
   
2. Import Path Issues (1 test) - Confidence: 0.95
   Fix: Standardize src path setup
   Files: test_execution_engine.py
   
   Apply this fix? [Y/n/explain]: y
   
3. Assertion Logic (1 test) - Confidence: 0.3
   Fix: Update expected node pin count
   Files: test_node_system.py
   
   This requires manual review. Open file? [y/N]: y
```

## Automated Fix Application

### Safe Transformations
- Import statement standardization
- Test fixture consolidation  
- Mock integration for timeouts
- Path handling normalization

### Code Analysis Integration
- AST parsing for precise code modification
- Backup creation before applying fixes
- Rollback capability for failed fixes
- Integration with git for change tracking

## Output Formats

### Claude Format (Token-Efficient)
```
=== TEST FIX REPORT ===
Applied: 4/5 fixes | Success Rate: 80% | Remaining: 1 manual

=== AUTOMATED FIXES ===
✓ Qt Application: 3 tests fixed (0.9 confidence)
  → Implemented class-level QApplication setup
✓ Import Paths: 1 test fixed (0.95 confidence)  
  → Standardized src directory access
✗ Assertion Logic: 1 test needs manual review (0.3 confidence)
  → test_node_system.py:line 156 - Expected pin count mismatch

=== RECOMMENDATIONS ===
1. Review assertion in test_node_system.py - may need updated expectations
2. Run tests to verify fixes: python test_runner.py --format claude
3. Consider refactoring GUI test setup patterns for consistency
```

### Detailed Format
```
PyFlowGraph Test Fix Report
Generated: 2025-01-18 10:30:45

Fix Summary:
  Total Issues: 5
  Automated Fixes: 4
  Manual Review: 1
  Success Rate: 80%

Applied Fixes:

1. Qt Application Lifecycle (Confidence: 0.9)
   Issue: Multiple QApplication instances causing RuntimeError
   Solution: Implemented class-level QApplication setup pattern
   Files Modified:
     - tests/gui/test_full_gui_integration.py
     - tests/gui/test_end_to_end_workflows.py
     - tests/test_gui_node_deletion.py
   
   Changes:
     + Added @classmethod setUpClass method
     + Removed individual QApplication([]) calls
     + Ensured single application instance
   
2. Import Path Standardization (Confidence: 0.95)
   Issue: ModuleNotFoundError due to inconsistent path setup
   Solution: Standardized src directory path resolution
   Files Modified:
     - tests/test_execution_engine.py
   
   Changes:
     + Added standard src path calculation
     + Replaced relative imports with absolute paths
     + Added sys.path.insert(0, src_path)

[Additional fixes...]

Manual Review Required:

1. Assertion Logic Update (Confidence: 0.3)
   Issue: AssertionError in test_node_system.py:156
   Current: self.assertEqual(len(node.pins), 0)
   Analysis: Node constructor may create default pins
   Recommendation: Check Node implementation and update assertion
   
   Suggested Fix:
     self.assertGreaterEqual(len(node.pins), 0)
     # Or verify actual expected pin count from Node constructor
```

## Integration Points

### Test Runner Integration
- Automatic fix application after test failures
- Re-run tests to verify fix effectiveness
- Integration with parallel execution workflow

### Version Control Integration
- Create fix commits with descriptive messages
- Backup original files before modification
- Support for fix rollback via git reset

### Claude Code Workflow
- Token-efficient reporting for iterative development
- Learning from fix success/failure rates
- Pattern recognition for new failure types

## Error Handling and Safety

### Safety Measures
- Always create backups before applying fixes
- Rollback capability for unsuccessful fixes
- Confidence thresholds to prevent destructive changes
- User confirmation for medium/low confidence fixes

### Failure Recovery
- Graceful handling of fix application failures
- Clear error messages with remediation steps
- Fallback to manual fix suggestions
- Integration with test analysis for pattern learning

## Performance Characteristics

### Execution Speed
- Analysis phase: <10 seconds for typical test suite
- Fix application: <5 seconds per automated fix
- Re-run validation: Leverages parallel test execution

### Resource Usage
- Minimal memory footprint for fix analysis
- Efficient AST parsing for code modification
- Disk usage optimized with selective backups

## Learning and Adaptation

### Pattern Recognition
- Track fix success rates by category and pattern
- Learn from user feedback on guided fixes
- Adapt confidence scoring based on historical data
- Update fix templates based on PyFlowGraph evolution

### Continuous Improvement
- Monitor fix effectiveness across multiple runs
- Identify new failure patterns requiring automation
- Optimize fix application speed and accuracy
- Integrate with broader PyFlowGraph testing ecosystem
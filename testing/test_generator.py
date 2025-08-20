#!/usr/bin/env python
"""
Test Generator for PyFlowGraph

Automatically generates test scaffolding based on coverage analysis, code structure,
and existing test patterns. Optimized for PyFlowGraph's architecture and testing conventions.

Features:
    - Coverage-driven test generation
    - Pattern recognition from existing tests
    - PyFlowGraph-specific test templates
    - Smart test categorization and placement
    - Integration with existing test infrastructure
"""

import os
import sys
import ast
import json
import inspect
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
import importlib.util

@dataclass
class FunctionInfo:
    """Information about a function that needs testing."""
    name: str
    file_path: str
    line_number: int
    signature: str
    docstring: Optional[str]
    complexity_score: float
    parameters: List[Tuple[str, str]]  # (name, type_hint)
    return_type: Optional[str]
    is_method: bool
    class_name: Optional[str]

@dataclass
class TestTemplate:
    """Template for generating a test."""
    test_name: str
    test_code: str
    imports: List[str]
    fixtures: List[str]
    category: str  # unit, integration, gui, headless

class TestGenerator:
    """Generates test scaffolding for PyFlowGraph components."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.test_dir = self.project_root / "tests"
        
        # Load existing test patterns
        self.existing_patterns = self._analyze_existing_tests()
        
        # PyFlowGraph-specific templates
        self.templates = self._load_templates()
    
    def _analyze_existing_tests(self) -> Dict[str, List[str]]:
        """Analyze existing tests to learn patterns and conventions."""
        patterns = {
            'imports': set(),
            'fixtures': set(),
            'setup_patterns': [],
            'assertion_patterns': [],
            'teardown_patterns': []
        }
        
        for test_file in self.test_dir.rglob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Extract import patterns
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            patterns['imports'].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            patterns['imports'].add(node.module)
                
                # Extract fixture and setup patterns
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name in ['setUp', 'setUpClass', 'tearDown', 'tearDownClass']:
                            patterns['fixtures'].add(node.name)
                        elif node.name.startswith('test_'):
                            # Analyze test structure
                            source = ast.get_source_segment(content, node)
                            if source:
                                patterns['assertion_patterns'].extend(
                                    self._extract_assertion_patterns(source)
                                )
            
            except (SyntaxError, UnicodeDecodeError) as e:
                print(f"Warning: Could not analyze {test_file}: {e}")
        
        # Convert sets to lists for JSON serialization
        patterns['imports'] = list(patterns['imports'])
        patterns['fixtures'] = list(patterns['fixtures'])
        
        return patterns
    
    def _extract_assertion_patterns(self, test_source: str) -> List[str]:
        """Extract common assertion patterns from test source."""
        patterns = []
        
        # Common assertion patterns in PyFlowGraph tests
        assertion_keywords = [
            'self.assertEqual', 'self.assertTrue', 'self.assertFalse',
            'self.assertIsNotNone', 'self.assertIsNone', 'self.assertIn',
            'self.assertNotIn', 'self.assertGreater', 'self.assertLess',
            'self.assertRaises'
        ]
        
        for keyword in assertion_keywords:
            if keyword in test_source:
                patterns.append(keyword)
        
        return patterns
    
    def _load_templates(self) -> Dict[str, str]:
        """Load PyFlowGraph-specific test templates."""
        return {
            'node_test': '''
def test_{function_name}(self):
    """Test {function_name} functionality."""
    # Arrange
    node = Node("TestNode")
    {setup_code}
    
    # Act
    result = node.{function_name}({parameters})
    
    # Assert
    {assertions}
''',
            'pin_test': '''
def test_{function_name}(self):
    """Test pin {function_name} functionality."""
    # Arrange
    node = Node("TestNode")
    pin = Pin("test_pin", PinType.INPUT, node)
    {setup_code}
    
    # Act
    result = pin.{function_name}({parameters})
    
    # Assert
    {assertions}
''',
            'connection_test': '''
def test_{function_name}(self):
    """Test connection {function_name} functionality."""
    # Arrange
    source_node = Node("SourceNode")
    target_node = Node("TargetNode")
    source_pin = Pin("output", PinType.OUTPUT, source_node)
    target_pin = Pin("input", PinType.INPUT, target_node)
    connection = Connection(source_pin, target_pin)
    {setup_code}
    
    # Act
    result = connection.{function_name}({parameters})
    
    # Assert
    {assertions}
''',
            'graph_test': '''
def test_{function_name}(self):
    """Test graph {function_name} functionality."""
    # Arrange
    graph = NodeGraph()
    {setup_code}
    
    # Act
    result = graph.{function_name}({parameters})
    
    # Assert
    {assertions}
''',
            'gui_test': '''
def test_{function_name}(self):
    """Test GUI {function_name} functionality."""
    # Arrange
    if not QApplication.instance():
        app = QApplication([])
    {setup_code}
    
    # Act
    result = {object_name}.{function_name}({parameters})
    
    # Assert
    {assertions}
    
    # Cleanup
    {cleanup_code}
''',
            'execution_test': '''
def test_{function_name}(self):
    """Test execution engine {function_name} functionality."""
    # Arrange
    executor = GraphExecutor()
    graph = NodeGraph()
    {setup_code}
    
    # Act
    result = executor.{function_name}({parameters})
    
    # Assert
    {assertions}
'''
        }
    
    def analyze_coverage_gaps(self) -> List[FunctionInfo]:
        """Analyze coverage data to identify functions needing tests."""
        coverage_file = self.project_root / "coverage.json"
        if not coverage_file.exists():
            print("Warning: coverage.json not found. Run tests with --coverage first.")
            return []
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
        except json.JSONDecodeError:
            print("Warning: Could not parse coverage.json")
            return []
        
        functions_needing_tests = []
        
        for file_path, file_data in coverage_data.get('files', {}).items():
            if not file_path.startswith('src/'):
                continue
            
            missing_lines = set(file_data.get('missing_lines', []))
            if not missing_lines:
                continue
            
            # Analyze the source file
            full_path = self.project_root / file_path
            if full_path.exists():
                functions = self._extract_functions_from_file(full_path, missing_lines)
                functions_needing_tests.extend(functions)
        
        return sorted(functions_needing_tests, key=lambda x: x.complexity_score, reverse=True)
    
    def _extract_functions_from_file(self, file_path: Path, missing_lines: Set[int]) -> List[FunctionInfo]:
        """Extract function information from a source file."""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            current_class = None
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    current_class = node.name
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private methods and special methods
                    if node.name.startswith('_'):
                        continue
                    
                    # Check if function has missing coverage
                    func_lines = set(range(node.lineno, getattr(node, 'end_lineno', node.lineno) + 1))
                    missing_in_func = func_lines.intersection(missing_lines)
                    
                    if missing_in_func:
                        # Extract function information
                        signature = self._extract_signature(node)
                        parameters = self._extract_parameters(node)
                        return_type = self._extract_return_type(node)
                        docstring = ast.get_docstring(node)
                        complexity = self._calculate_complexity(node)
                        
                        functions.append(FunctionInfo(
                            name=node.name,
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            signature=signature,
                            docstring=docstring,
                            complexity_score=complexity,
                            parameters=parameters,
                            return_type=return_type,
                            is_method=current_class is not None,
                            class_name=current_class
                        ))
        
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
        
        return functions
    
    def _extract_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature as string."""
        args = []
        
        # Regular arguments
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # Keyword-only arguments
        for arg in node.args.kwonlyargs:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        signature = f"def {node.name}({', '.join(args)})"
        
        # Return type annotation
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"
        
        return signature
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Tuple[str, str]]:
        """Extract parameter names and type hints."""
        parameters = []
        
        for arg in node.args.args:
            param_name = arg.arg
            param_type = "Any"
            
            if arg.annotation:
                try:
                    param_type = ast.unparse(arg.annotation)
                except:
                    param_type = "Any"
            
            parameters.append((param_name, param_type))
        
        return parameters
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation."""
        if node.returns:
            try:
                return ast.unparse(node.returns)
            except:
                pass
        return None
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> float:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return float(complexity)
    
    def generate_test_for_function(self, func_info: FunctionInfo) -> TestTemplate:
        """Generate a test template for a specific function."""
        # Determine test category and template
        category, template_name = self._determine_test_category(func_info)
        
        # Generate test content
        test_name = f"test_{func_info.name}"
        
        # Select appropriate template
        if template_name in self.templates:
            template = self.templates[template_name]
        else:
            template = self.templates['node_test']  # Default fallback
        
        # Generate setup code
        setup_code = self._generate_setup_code(func_info)
        
        # Generate parameters
        parameters = self._generate_test_parameters(func_info)
        
        # Generate assertions
        assertions = self._generate_assertions(func_info)
        
        # Generate cleanup code for GUI tests
        cleanup_code = self._generate_cleanup_code(func_info) if category == 'gui' else ""
        
        # Fill template
        test_code = template.format(
            function_name=func_info.name,
            setup_code=setup_code,
            parameters=parameters,
            assertions=assertions,
            object_name=self._get_object_name(func_info),
            cleanup_code=cleanup_code
        )
        
        # Generate imports
        imports = self._generate_imports(func_info, category)
        
        # Generate fixtures
        fixtures = self._generate_fixtures(func_info, category)
        
        return TestTemplate(
            test_name=test_name,
            test_code=test_code,
            imports=imports,
            fixtures=fixtures,
            category=category
        )
    
    def _determine_test_category(self, func_info: FunctionInfo) -> Tuple[str, str]:
        """Determine test category and template based on function context."""
        file_path = func_info.file_path.lower()
        
        # GUI components
        if any(keyword in file_path for keyword in ['window', 'dialog', 'view', 'widget']):
            return 'gui', 'gui_test'
        
        # Core components
        if 'node.py' in file_path:
            return 'unit', 'node_test'
        elif 'pin.py' in file_path:
            return 'unit', 'pin_test'
        elif 'connection.py' in file_path:
            return 'unit', 'connection_test'
        elif 'node_graph.py' in file_path:
            return 'integration', 'graph_test'
        elif 'executor' in file_path:
            return 'integration', 'execution_test'
        
        # Default to unit test
        return 'unit', 'node_test'
    
    def _generate_setup_code(self, func_info: FunctionInfo) -> str:
        """Generate setup code based on function context."""
        if func_info.class_name:
            # Method test - might need instance setup
            if func_info.class_name == 'Node':
                return '# Node is already created above'
            elif func_info.class_name == 'Pin':
                return '# Pin is already created above'
            elif func_info.class_name == 'Connection':
                return '# Connection is already created above'
            elif func_info.class_name == 'NodeGraph':
                return '# Graph is already created above'
        
        return '# Add setup code as needed'
    
    def _generate_test_parameters(self, func_info: FunctionInfo) -> str:
        """Generate test parameters based on function signature."""
        if not func_info.parameters:
            return ""
        
        # Skip 'self' parameter for methods
        params = func_info.parameters[1:] if func_info.is_method else func_info.parameters
        
        if not params:
            return ""
        
        # Generate simple test values based on type hints
        param_values = []
        for param_name, param_type in params:
            if param_type in ['str', 'Optional[str]']:
                param_values.append(f'"{param_name}_value"')
            elif param_type in ['int', 'Optional[int]']:
                param_values.append('42')
            elif param_type in ['float', 'Optional[float]']:
                param_values.append('3.14')
            elif param_type in ['bool', 'Optional[bool]']:
                param_values.append('True')
            elif 'List' in param_type:
                param_values.append('[]')
            elif 'Dict' in param_type:
                param_values.append('{}')
            else:
                param_values.append(f'# TODO: Provide {param_name} value')
        
        return ', '.join(param_values)
    
    def _generate_assertions(self, func_info: FunctionInfo) -> str:
        """Generate appropriate assertions based on return type."""
        if func_info.return_type:
            if func_info.return_type == 'bool':
                return 'self.assertIsInstance(result, bool)\n    # TODO: Add specific boolean assertion'
            elif func_info.return_type in ['str', 'Optional[str]']:
                return 'self.assertIsInstance(result, (str, type(None)))\n    # TODO: Add specific string assertion'
            elif func_info.return_type in ['int', 'float']:
                return f'self.assertIsInstance(result, {func_info.return_type})\n    # TODO: Add specific numeric assertion'
            elif func_info.return_type == 'None':
                return 'self.assertIsNone(result)'
            elif 'List' in func_info.return_type:
                return 'self.assertIsInstance(result, list)\n    # TODO: Add specific list content assertions'
            elif 'Dict' in func_info.return_type:
                return 'self.assertIsInstance(result, dict)\n    # TODO: Add specific dict content assertions'
        
        return 'self.assertIsNotNone(result)\n    # TODO: Add specific assertions for this function'
    
    def _get_object_name(self, func_info: FunctionInfo) -> str:
        """Get the object name for method calls."""
        if func_info.class_name:
            return func_info.class_name.lower()
        return 'obj'
    
    def _generate_cleanup_code(self, func_info: FunctionInfo) -> str:
        """Generate cleanup code for GUI tests."""
        return '''if hasattr(self, 'widget'):
        self.widget.close()
        self.widget.deleteLater()'''
    
    def _generate_imports(self, func_info: FunctionInfo, category: str) -> List[str]:
        """Generate necessary imports for the test."""
        imports = [
            'import unittest',
            'import sys',
            'import os',
            'from unittest.mock import Mock, patch'
        ]
        
        # Add path setup
        imports.extend([
            '',
            '# Add src directory to path',
            'src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")',
            'sys.path.insert(0, src_path)',
            ''
        ])
        
        # Category-specific imports
        if category == 'gui':
            imports.extend([
                'from PySide6.QtWidgets import QApplication',
                'from PySide6.QtCore import QPointF',
                'from PySide6.QtGui import QColor'
            ])
        
        # Module-specific imports
        module_path = func_info.file_path.replace('src/', '').replace('.py', '').replace('/', '.')
        
        if func_info.class_name:
            imports.append(f'from {module_path} import {func_info.class_name}')
        
        # Common PyFlowGraph imports
        imports.extend([
            'from core.node import Node',
            'from core.pin import Pin',
            'from core.connection import Connection',
            'from core.node_graph import NodeGraph'
        ])
        
        return imports
    
    def _generate_fixtures(self, func_info: FunctionInfo, category: str) -> List[str]:
        """Generate test fixtures based on category."""
        fixtures = []
        
        if category == 'gui':
            fixtures.extend([
                '@classmethod',
                'def setUpClass(cls):',
                '    """Set up class-level test fixtures."""',
                '    if not QApplication.instance():',
                '        cls.app = QApplication([])',
                '    else:',
                '        cls.app = QApplication.instance()',
                '',
                'def setUp(self):',
                '    """Set up test fixtures before each test method."""',
                '    pass',
                '',
                'def tearDown(self):',
                '    """Clean up after each test method."""',
                '    pass'
            ])
        else:
            fixtures.extend([
                'def setUp(self):',
                '    """Set up test fixtures before each test method."""',
                '    pass',
                '',
                'def tearDown(self):',
                '    """Clean up after each test method."""',
                '    pass'
            ])
        
        return fixtures
    
    def generate_test_file(self, functions: List[FunctionInfo], output_path: Path):
        """Generate a complete test file for a list of functions."""
        if not functions:
            return
        
        # Group functions by file
        files_to_test = {}
        for func in functions:
            file_key = func.file_path
            if file_key not in files_to_test:
                files_to_test[file_key] = []
            files_to_test[file_key].append(func)
        
        for file_path, file_functions in files_to_test.items():
            # Determine output file name
            module_name = Path(file_path).stem
            test_file_name = f"test_{module_name}_generated.py"
            test_file_path = output_path / test_file_name
            
            # Generate test content
            content_lines = []
            
            # Header comment
            content_lines.extend([
                '"""',
                f'Generated tests for {file_path}',
                '',
                'This file was automatically generated by test_generator.py',
                'based on coverage analysis and existing test patterns.',
                '',
                'TODO items require manual implementation.',
                '"""',
                ''
            ])
            
            # Generate imports (use first function's imports as base)
            if file_functions:
                template = self.generate_test_for_function(file_functions[0])
                content_lines.extend(template.imports)
                content_lines.append('')
            
            # Generate test class
            class_name = f'Test{module_name.title()}Generated'
            content_lines.extend([
                f'class {class_name}(unittest.TestCase):',
                f'    """Generated tests for {module_name} module."""',
                ''
            ])
            
            # Generate fixtures (use first function's category)
            if file_functions:
                template = self.generate_test_for_function(file_functions[0])
                for fixture_line in template.fixtures:
                    content_lines.append(f'    {fixture_line}')
                content_lines.append('')
            
            # Generate test methods
            for func in file_functions:
                template = self.generate_test_for_function(func)
                content_lines.append(f'    {template.test_code}')
                content_lines.append('')
            
            # Add main block
            content_lines.extend([
                '',
                'if __name__ == "__main__":',
                '    unittest.main()'
            ])
            
            # Write file
            test_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content_lines))
            
            print(f"Generated: {test_file_path}")
    
    def analyze_and_generate(self, max_functions: int = 10, 
                           min_complexity: float = 1.0,
                           output_dir: Path = None) -> Dict[str, Any]:
        """Analyze coverage gaps and generate tests."""
        if output_dir is None:
            output_dir = self.test_dir / "generated"
        
        # Analyze coverage gaps
        functions_needing_tests = self.analyze_coverage_gaps()
        
        if not functions_needing_tests:
            return {
                'status': 'no_gaps',
                'message': 'No coverage gaps found or coverage.json not available',
                'functions_analyzed': 0,
                'tests_generated': 0
            }
        
        # Filter by complexity and limit count
        filtered_functions = [
            f for f in functions_needing_tests 
            if f.complexity_score >= min_complexity
        ][:max_functions]
        
        if not filtered_functions:
            return {
                'status': 'filtered_out',
                'message': f'No functions meet complexity threshold of {min_complexity}',
                'functions_analyzed': len(functions_needing_tests),
                'tests_generated': 0
            }
        
        # Generate tests
        self.generate_test_file(filtered_functions, output_dir)
        
        return {
            'status': 'success',
            'message': f'Generated tests for {len(filtered_functions)} functions',
            'functions_analyzed': len(functions_needing_tests),
            'tests_generated': len(filtered_functions),
            'output_directory': str(output_dir),
            'generated_functions': [
                {
                    'name': f.name,
                    'file': f.file_path,
                    'complexity': f.complexity_score
                }
                for f in filtered_functions
            ]
        }

def main():
    """Main entry point for the test generator."""
    parser = argparse.ArgumentParser(
        description="Test Generator for PyFlowGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_generator.py                          # Generate tests for top 10 complex functions
  python test_generator.py --max-functions 5       # Generate tests for top 5 functions
  python test_generator.py --min-complexity 2.0    # Only functions with complexity >= 2.0
  python test_generator.py --output-dir custom/    # Custom output directory
        """
    )
    
    parser.add_argument("--max-functions", type=int, default=10,
                       help="Maximum number of functions to generate tests for")
    parser.add_argument("--min-complexity", type=float, default=1.0,
                       help="Minimum complexity score for test generation")
    parser.add_argument("--output-dir", type=Path,
                       help="Output directory for generated tests")
    parser.add_argument("--analyze-only", action="store_true",
                       help="Only analyze coverage gaps, don't generate tests")
    parser.add_argument("--format", choices=["detailed", "summary", "claude"],
                       default="detailed", help="Output format")
    
    args = parser.parse_args()
    
    try:
        generator = TestGenerator()
        
        if args.analyze_only:
            # Just analyze gaps
            functions = generator.analyze_coverage_gaps()
            if args.format == "claude":
                print(f"Coverage Gaps: {len(functions)} functions need tests")
                for func in functions[:5]:
                    print(f"• {func.file_path}::{func.name} (complexity: {func.complexity_score:.1f})")
            elif args.format == "summary":
                print(f"Found {len(functions)} functions needing tests")
            else:
                print(f"Coverage Analysis Results:")
                print(f"Total functions needing tests: {len(functions)}")
                for func in functions:
                    print(f"  {func.file_path}::{func.name}")
                    print(f"    Complexity: {func.complexity_score:.1f}")
                    print(f"    Line: {func.line_number}")
                    if func.docstring:
                        print(f"    Doc: {func.docstring[:60]}...")
                    print()
        else:
            # Analyze and generate
            result = generator.analyze_and_generate(
                max_functions=args.max_functions,
                min_complexity=args.min_complexity,
                output_dir=args.output_dir
            )
            
            if args.format == "claude":
                print(f"Test Generation: {result['status']}")
                print(f"Generated: {result['tests_generated']} tests")
                print(f"Analyzed: {result['functions_analyzed']} functions")
                if result.get('generated_functions'):
                    print("Top functions:")
                    for func in result['generated_functions'][:3]:
                        print(f"• {func['name']} (complexity: {func['complexity']:.1f})")
            elif args.format == "summary":
                print(f"{result['status']}: {result['tests_generated']} tests generated")
            else:
                print("Test Generation Results:")
                print(f"Status: {result['status']}")
                print(f"Message: {result['message']}")
                print(f"Functions analyzed: {result['functions_analyzed']}")
                print(f"Tests generated: {result['tests_generated']}")
                if result.get('output_directory'):
                    print(f"Output directory: {result['output_directory']}")
                
                if result.get('generated_functions'):
                    print("\nGenerated tests for:")
                    for func in result['generated_functions']:
                        print(f"  {func['file']}::{func['name']} (complexity: {func['complexity']:.1f})")
    
    except Exception as e:
        print(f"Error generating tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
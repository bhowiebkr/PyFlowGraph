# PySide6/Qt Unit Testing Guide

## Overview

Comprehensive guide for unit testing PySide6/Qt applications, covering both GUI and non-GUI testing approaches, best practices, and implementation strategies specific to the PyFlowGraph architecture.

## Table of Contents

1. [Testing Approaches](#testing-approaches)
2. [Headless vs GUI Testing](#headless-vs-gui-testing)
3. [Test Structure and Setup](#test-structure-and-setup)
4. [Core Testing Patterns](#core-testing-patterns)
5. [PyFlowGraph-Specific Testing](#pyflowgraph-specific-testing)
6. [Advanced Testing Techniques](#advanced-testing-techniques)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Testing Approaches

### 1. Headless Testing (Recommended for CI/CD)

**When to use:**
- Unit tests for core logic and data structures
- Automated testing in CI/CD pipelines
- Fast feedback during development
- Testing non-visual functionality

**Advantages:**
- ⚡ Fast execution (no GUI rendering overhead)
- 🔄 Reliable in automated environments
- 📊 Better for coverage analysis
- 🖥️ Works in headless environments (Docker, CI servers)

**Implementation:**
```python
import unittest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

class TestNodeSystemHeadless(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize QApplication without showing GUI."""
        if QApplication.instance() is None:
            cls.app = QApplication([])
            # Prevent windows from showing
            cls.app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    
    def setUp(self):
        """Set up test fixtures without visual components."""
        self.graph = NodeGraph()  # No scene display needed
        self.node = Node("Test Node")
        self.graph.addItem(self.node)
    
    def test_node_creation_logic(self):
        """Test node creation without GUI interaction."""
        node = Node("Logic Test")
        
        # Test core properties
        self.assertEqual(node.title, "Logic Test")
        self.assertIsNotNone(node.uuid)
        self.assertEqual(node.base_width, 250)
        
        # Test pin generation from code
        code = '''
@node_entry
def test_func(x: int) -> str:
    return str(x)
'''
        node.set_code(code)
        
        # Verify pins were created correctly
        self.assertEqual(len(node.input_pins), 2)  # exec_in + x
        self.assertEqual(len(node.output_pins), 2)  # exec_out + output_1
```

### 2. GUI Testing (Integration and Visual Testing)

**When to use:**
- Testing user interactions and workflows
- Visual component behavior verification
- Integration testing with actual Qt widgets
- Debugging GUI-specific issues

**Advantages:**
- 🎯 Tests actual user experience
- 🔍 Validates visual behavior and layout
- 🖱️ Verifies mouse/keyboard interactions
- 🐛 Better for debugging GUI issues

**Implementation:**
```python
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent

class TestNodeSystemGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize QApplication with GUI support."""
        if QApplication.instance() is None:
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up GUI components for testing."""
        self.window = NodeEditorWindow()
        self.window.show()  # Make visible for GUI testing
        self.graph = self.window.graph
        self.view = self.window.view
        
        # Process events to ensure GUI is ready
        QApplication.processEvents()
    
    def tearDown(self):
        """Clean up GUI components."""
        self.window.close()
        QApplication.processEvents()
    
    def test_user_node_creation_workflow(self):
        """Test complete user workflow for creating nodes."""
        # Simulate user creating a node
        initial_count = len(self.graph.nodes)
        
        # Create node through GUI
        node = self.graph.create_node("User Test Node", pos=(100, 100))
        
        # Process GUI events
        QApplication.processEvents()
        
        # Verify node was added to scene
        self.assertEqual(len(self.graph.nodes), initial_count + 1)
        self.assertIn(node, self.graph.items())
        
        # Test node selection
        node.setSelected(True)
        QApplication.processEvents()
        self.assertTrue(node.isSelected())
        
        # Test node deletion via keyboard
        delete_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
        self.graph.keyPressEvent(delete_event)
        QApplication.processEvents()
        
        # Verify node was removed
        self.assertEqual(len(self.graph.nodes), initial_count)
        self.assertNotIn(node, self.graph.items())
```

## Test Structure and Setup

### QApplication Management

**Singleton Pattern for Tests:**
```python
class BaseTestCase(unittest.TestCase):
    """Base class for all Qt tests with proper QApplication management."""
    
    @classmethod
    def setUpClass(cls):
        """Ensure QApplication exists for the test suite."""
        if QApplication.instance() is None:
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
        
        # Configure for testing
        cls.app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        cls.app.setQuitOnLastWindowClosed(False)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication after tests."""
        # Don't quit the app, let the test runner handle it
        pass
    
    def setUp(self):
        """Set up individual test."""
        QApplication.processEvents()  # Ensure clean state
    
    def tearDown(self):
        """Clean up after individual test."""
        QApplication.processEvents()  # Process pending events
```

### Test Discovery and Organization

**File Structure:**
```
tests/
├── __init__.py
├── unit/                    # Headless unit tests
│   ├── test_node_core.py
│   ├── test_pin_logic.py
│   └── test_connection_math.py
├── integration/             # GUI integration tests
│   ├── test_node_interactions.py
│   ├── test_workflow_scenarios.py
│   └── test_visual_components.py
├── fixtures/                # Test data and utilities
│   ├── sample_graphs.py
│   └── test_utilities.py
└── conftest.py             # Shared test configuration
```

## Core Testing Patterns

### 1. Widget Testing Pattern

```python
def test_widget_properties(self):
    """Test Qt widget properties and behavior."""
    # Create widget without showing
    widget = CustomWidget()
    
    # Test initial state
    self.assertEqual(widget.text(), "")
    self.assertFalse(widget.isEnabled())
    
    # Test property changes
    widget.setText("Test Text")
    self.assertEqual(widget.text(), "Test Text")
    
    # Test signals (using QSignalSpy or manual connection)
    signal_received = []
    widget.textChanged.connect(lambda text: signal_received.append(text))
    
    widget.setText("New Text")
    QApplication.processEvents()  # Ensure signal is emitted
    
    self.assertEqual(signal_received, ["New Text"])
```

### 2. Scene and Graphics Testing

```python
def test_graphics_scene_operations(self):
    """Test QGraphicsScene operations without visual display."""
    scene = QGraphicsScene()
    
    # Test item addition
    item = QGraphicsRectItem(0, 0, 100, 100)
    scene.addItem(item)
    
    self.assertEqual(len(scene.items()), 1)
    self.assertIn(item, scene.items())
    
    # Test item positioning
    item.setPos(50, 75)
    self.assertEqual(item.pos(), QPointF(50, 75))
    
    # Test scene bounds
    scene_rect = scene.itemsBoundingRect()
    expected_rect = QRectF(50, 75, 100, 100)
    self.assertEqual(scene_rect, expected_rect)
```

### 3. Event Testing with QTest

```python
from PySide6.QtTest import QTest

def test_mouse_interactions(self):
    """Test mouse events using QTest utilities."""
    # Create a widget that responds to mouse events
    widget = ClickableWidget()
    widget.show()
    
    # Simulate mouse click
    QTest.mouseClick(widget, Qt.LeftButton)
    QApplication.processEvents()
    
    # Verify click was registered
    self.assertTrue(widget.was_clicked)
    
    # Test drag operations
    QTest.mousePress(widget, Qt.LeftButton, Qt.NoModifier, QPoint(10, 10))
    QTest.mouseMove(widget, QPoint(50, 50))
    QTest.mouseRelease(widget, Qt.LeftButton, Qt.NoModifier, QPoint(50, 50))
    
    # Verify drag was processed
    self.assertEqual(widget.drag_distance, 40)  # Approximate distance
```

### 4. Asynchronous and Timer Testing

```python
def test_timer_based_operations(self):
    """Test operations that involve Qt timers."""
    widget = TimerWidget()
    
    # Use QTest.qWait for timer-based operations
    widget.start_delayed_operation()
    
    # Wait for timer to fire (avoid blocking the test)
    QTest.qWait(1100)  # Wait slightly longer than timer interval
    
    self.assertTrue(widget.operation_completed)

def test_background_operations(self):
    """Test operations that run in background threads."""
    worker = BackgroundWorker()
    results = []
    
    # Connect to finished signal
    worker.finished.connect(lambda result: results.append(result))
    
    # Start operation
    worker.start()
    
    # Process events until operation completes
    timeout = 5000  # 5 seconds
    start_time = time.time()
    
    while not results and (time.time() - start_time) * 1000 < timeout:
        QApplication.processEvents()
        time.sleep(0.01)
    
    self.assertTrue(results)
    self.assertEqual(results[0], "expected_result")
```

## PyFlowGraph-Specific Testing

### 1. Node System Testing

```python
class TestNodeSystem(BaseTestCase):
    """Tests for PyFlowGraph node system."""
    
    def test_node_code_to_pins_generation(self):
        """Test automatic pin generation from Python code."""
        node = Node("Code Test")
        
        # Test function with typed parameters
        code = '''
from typing import List, Optional

@node_entry
def process_data(
    items: List[str], 
    threshold: float, 
    debug: bool = False,
    callback: Optional[callable] = None
) -> tuple[List[str], int]:
    processed = [item.upper() for item in items if len(item) > threshold]
    return processed, len(processed)
'''
        
        node.set_code(code)
        
        # Verify input pins were created
        input_pin_names = [pin.name for pin in node.input_pins if pin.pin_category == "data"]
        expected_inputs = ["items", "threshold", "debug", "callback"]
        
        for expected in expected_inputs:
            self.assertIn(expected, input_pin_names)
        
        # Verify output pins for tuple return
        output_pin_names = [pin.name for pin in node.output_pins if pin.pin_category == "data"]
        self.assertIn("output_1", output_pin_names)  # First tuple element
        self.assertIn("output_2", output_pin_names)  # Second tuple element
        
        # Verify pin types
        pin_types = {pin.name: pin.pin_type for pin in node.input_pins if pin.pin_category == "data"}
        self.assertEqual(pin_types["items"], "List[str]")
        self.assertEqual(pin_types["threshold"], "float")
        self.assertEqual(pin_types["debug"], "bool")
```

### 2. Connection System Testing

```python
def test_connection_validation_and_creation(self):
    """Test connection creation between compatible pins."""
    # Create two compatible nodes
    source_node = Node("Source")
    source_node.set_code('''
@node_entry
def produce_string() -> str:
    return "test_output"
''')
    
    target_node = Node("Target")
    target_node.set_code('''
@node_entry
def consume_string(input_str: str):
    print(input_str)
''')
    
    # Find compatible pins
    output_pin = None
    input_pin = None
    
    for pin in source_node.output_pins:
        if pin.pin_category == "data" and pin.pin_type == "str":
            output_pin = pin
            break
    
    for pin in target_node.input_pins:
        if pin.pin_category == "data" and pin.pin_type == "str":
            input_pin = pin
            break
    
    self.assertIsNotNone(output_pin)
    self.assertIsNotNone(input_pin)
    
    # Test connection creation
    graph = NodeGraph()
    graph.addItem(source_node)
    graph.addItem(target_node)
    
    connection = graph.create_connection(output_pin, input_pin)
    
    # Verify connection properties
    self.assertIsNotNone(connection)
    self.assertEqual(connection.output_pin, output_pin)
    self.assertEqual(connection.input_pin, input_pin)
    self.assertIn(connection, graph.connections)
```

### 3. Execution Engine Testing

```python
def test_graph_execution_flow(self):
    """Test data flow execution through connected nodes."""
    # Create a simple data processing chain
    graph = NodeGraph()
    
    # Source node
    source = graph.create_node("Source", pos=(0, 0))
    source.set_code('''
@node_entry
def generate_number() -> int:
    return 42
''')
    
    # Processing node
    processor = graph.create_node("Processor", pos=(200, 0))
    processor.set_code('''
@node_entry
def double_number(value: int) -> int:
    return value * 2
''')
    
    # Connect them
    source_output = source.output_pins[1]  # Skip exec pin, get data pin
    processor_input = processor.input_pins[1]  # Skip exec pin, get data pin
    
    connection = graph.create_connection(source_output, processor_input)
    
    # Execute the graph (requires execution engine)
    from core.graph_executor import GraphExecutor
    executor = GraphExecutor(graph)
    
    # Test execution
    result = executor.execute_node(source)
    self.assertEqual(result, {"output_1": 42})
    
    # Test data flow to connected node
    result = executor.execute_node(processor, {"value": 42})
    self.assertEqual(result, {"output_1": 84})
```

### 4. File Format Testing

```python
def test_graph_serialization_roundtrip(self):
    """Test saving and loading graph files."""
    # Create a test graph
    graph = NodeGraph()
    
    node1 = graph.create_node("Test Node 1", pos=(100, 100))
    node1.set_code('def test(): return "hello"')
    
    node2 = graph.create_node("Test Node 2", pos=(300, 100))
    node2.set_code('def test2(x: str): print(x)')
    
    # Serialize to data structure
    graph_data = {
        "nodes": [node.serialize() for node in graph.nodes],
        "connections": [conn.serialize() for conn in graph.connections]
    }
    
    # Clear graph and reload
    graph.clear_graph()
    self.assertEqual(len(graph.nodes), 0)
    
    # Deserialize (simulate file loading)
    for node_data in graph_data["nodes"]:
        node = graph.create_node(node_data["title"], pos=node_data["pos"])
        node.uuid = node_data["uuid"]
        node.set_code(node_data["code"])
        node.width, node.height = node_data["size"]
    
    # Verify reconstruction
    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(graph.nodes[0].title, "Test Node 1")
    self.assertEqual(graph.nodes[1].title, "Test Node 2")
```

## Advanced Testing Techniques

### 1. Mock and Patch Strategies

```python
from unittest.mock import Mock, patch, MagicMock

class TestWithMocks(BaseTestCase):
    """Advanced testing with mocks for external dependencies."""
    
    @patch('subprocess.run')
    def test_code_execution_isolation(self, mock_subprocess):
        """Test node code execution with mocked subprocess."""
        # Configure mock to return expected result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"result": "success"}'
        mock_result.stderr = ''
        mock_subprocess.return_value = mock_result
        
        # Test execution
        executor = GraphExecutor(self.graph)
        node = Node("Mock Test")
        node.set_code('def test(): return "mocked"')
        
        result = executor.execute_node(node)
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        self.assertIn('python', call_args[0][0])
    
    def test_file_operations_with_temp_files(self):
        """Test file operations using temporary files."""
        import tempfile
        import json
        
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            test_data = {"test": "data"}
            json.dump(test_data, temp_file)
            temp_filename = temp_file.name
        
        try:
            # Test file loading
            from data.file_operations import load_json_file
            loaded_data = load_json_file(temp_filename)
            self.assertEqual(loaded_data, test_data)
            
        finally:
            # Clean up
            os.unlink(temp_filename)
```

### 2. Performance Testing

```python
import time
import cProfile
import pstats

class TestPerformance(BaseTestCase):
    """Performance testing for Qt operations."""
    
    def test_large_graph_performance(self):
        """Test performance with large number of nodes."""
        graph = NodeGraph()
        
        # Measure node creation time
        start_time = time.time()
        
        nodes = []
        for i in range(1000):
            node = graph.create_node(f"Node {i}", pos=(i * 10, i * 10))
            nodes.append(node)
            
            # Process events periodically
            if i % 100 == 0:
                QApplication.processEvents()
        
        creation_time = time.time() - start_time
        
        # Assert reasonable performance (adjust thresholds as needed)
        self.assertLess(creation_time, 5.0)  # Should create 1000 nodes in under 5 seconds
        
        # Test scene updates
        start_time = time.time()
        for node in nodes[:100]:  # Test subset for position updates
            node.setPos(node.pos().x() + 50, node.pos().y() + 50)
        
        QApplication.processEvents()
        update_time = time.time() - start_time
        
        self.assertLess(update_time, 1.0)  # Should update 100 nodes in under 1 second
    
    def test_memory_usage_with_profiling(self):
        """Test memory usage patterns."""
        import tracemalloc
        
        tracemalloc.start()
        
        # Create and destroy nodes repeatedly
        graph = NodeGraph()
        
        for cycle in range(10):
            # Create nodes
            nodes = []
            for i in range(100):
                node = graph.create_node(f"Cycle {cycle} Node {i}")
                nodes.append(node)
            
            # Clear them
            graph.clear_graph()
            QApplication.processEvents()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Assert memory usage is reasonable (adjust based on actual measurements)
        self.assertLess(peak / 1024 / 1024, 100)  # Less than 100MB peak
```

### 3. Visual Regression Testing

```python
from PySide6.QtGui import QPixmap, QPainter

class TestVisualRegression(BaseTestCase):
    """Visual regression testing for GUI components."""
    
    def test_node_visual_appearance(self):
        """Test node rendering consistency."""
        # Create a node with specific properties
        node = Node("Visual Test")
        node.setPos(0, 0)
        node.width = 250
        node.height = 150
        
        # Add to scene for rendering
        scene = QGraphicsScene()
        scene.addItem(node)
        
        # Render to pixmap
        pixmap = QPixmap(300, 200)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        scene.render(painter, QRectF(0, 0, 300, 200), QRectF(-25, -25, 300, 200))
        painter.end()
        
        # Save reference image (first time) or compare (subsequent runs)
        reference_path = "tests/visual_references/node_appearance.png"
        
        if not os.path.exists(reference_path):
            # Create reference directory
            os.makedirs(os.path.dirname(reference_path), exist_ok=True)
            pixmap.save(reference_path)
            self.skipTest("Created reference image")
        else:
            # Compare with reference
            reference_pixmap = QPixmap(reference_path)
            
            # Convert to comparable format (simplified comparison)
            current_image = pixmap.toImage()
            reference_image = reference_pixmap.toImage()
            
            # Simple pixel comparison (for production, use more sophisticated comparison)
            self.assertEqual(current_image.size(), reference_image.size())
            
            # For comprehensive visual testing, consider using tools like:
            # - Playwright for browser-based comparisons
            # - Applitools for AI-powered visual testing
            # - Custom image diffing algorithms
```

## Best Practices

### 1. Test Organization and Naming

```python
# Good: Descriptive test names that explain what is being tested
def test_node_creation_with_valid_title_creates_node_with_correct_properties(self):
    pass

def test_connection_between_incompatible_pin_types_raises_validation_error(self):
    pass

def test_graph_serialization_preserves_all_node_and_connection_data(self):
    pass

# Organize tests by functionality, not by implementation details
class TestNodeCreation(BaseTestCase):
    """Tests for node creation and initialization."""
    pass

class TestNodeCodeManagement(BaseTestCase):
    """Tests for node code setting and pin generation."""
    pass

class TestNodeSerialization(BaseTestCase):
    """Tests for node serialization and deserialization."""
    pass
```

### 2. Test Data Management

```python
# Create reusable test fixtures
class TestFixtures:
    """Reusable test data and utilities."""
    
    @staticmethod
    def create_simple_function_code():
        return '''
@node_entry
def simple_function(x: int) -> str:
    return str(x * 2)
'''
    
    @staticmethod
    def create_complex_function_code():
        return '''
from typing import List, Dict, Optional, Tuple

@node_entry
def complex_function(
    items: List[str],
    mapping: Dict[str, int],
    threshold: float = 0.5,
    callback: Optional[callable] = None
) -> Tuple[List[str], Dict[str, int], bool]:
    # Complex processing logic here
    processed_items = [item.upper() for item in items if len(item) > threshold]
    result_mapping = {item: mapping.get(item, 0) for item in processed_items}
    success = len(processed_items) > 0
    
    if callback:
        callback(success)
    
    return processed_items, result_mapping, success
'''
    
    @staticmethod
    def create_test_graph_with_connections():
        """Create a standard test graph with connected nodes."""
        graph = NodeGraph()
        
        # Source node
        source = graph.create_node("Source", pos=(0, 0))
        source.set_code(TestFixtures.create_simple_function_code())
        
        # Target node  
        target = graph.create_node("Target", pos=(300, 0))
        target.set_code('''
@node_entry
def consume_string(input_str: str):
    print(f"Received: {input_str}")
''')
        
        # Create connection
        output_pin = source.output_pins[1]  # First data output
        input_pin = target.input_pins[1]    # First data input
        connection = graph.create_connection(output_pin, input_pin)
        
        return graph, source, target, connection
```

### 3. Error Handling and Edge Cases

```python
class TestErrorHandling(BaseTestCase):
    """Test error conditions and edge cases."""
    
    def test_invalid_code_does_not_crash_node(self):
        """Test that syntactically invalid code doesn't crash the application."""
        node = Node("Invalid Code Test")
        
        invalid_codes = [
            "def broken_function(x: int) -> str\n    return str(x)",  # Missing colon
            "def (x): return x",  # Invalid function name
            "this is not python code at all",  # Complete nonsense
            "",  # Empty code
            "# Just a comment",  # Only comments
        ]
        
        for invalid_code in invalid_codes:
            with self.subTest(code=invalid_code):
                # Should not raise an exception
                try:
                    node.set_code(invalid_code)
                    # Code storage should work even for invalid code
                    self.assertEqual(node.code, invalid_code)
                except Exception as e:
                    self.fail(f"Setting invalid code raised {type(e).__name__}: {e}")
    
    def test_connection_validation_prevents_invalid_connections(self):
        """Test that connection validation prevents incompatible connections."""
        graph = NodeGraph()
        
        # Create nodes with incompatible types
        int_node = graph.create_node("Int Producer")
        int_node.set_code('''
@node_entry
def produce_int() -> int:
    return 42
''')
        
        str_node = graph.create_node("String Consumer")
        str_node.set_code('''
@node_entry
def consume_string(text: str):
    print(text)
''')
        
        # Try to connect incompatible pins
        int_output = int_node.output_pins[1]  # int output
        str_input = str_node.input_pins[1]    # str input
        
        # This should either return None or raise a validation error
        connection = graph.create_connection(int_output, str_input)
        
        # Verify connection was not created or appropriate error was raised
        if connection is not None:
            # If connection is created, it should have validation warnings
            self.assertTrue(hasattr(connection, 'validation_warnings'))
        else:
            # Connection should be None for incompatible types
            self.assertIsNone(connection)
```

### 4. Test Performance and Reliability

```python
class TestReliability(BaseTestCase):
    """Test for reliable and consistent behavior."""
    
    def test_operations_are_deterministic(self):
        """Test that operations produce consistent results."""
        results = []
        
        # Run the same operation multiple times
        for i in range(10):
            graph = NodeGraph()
            node = graph.create_node("Deterministic Test")
            node.set_code('''
@node_entry
def deterministic_function(x: int) -> int:
    return x * 2 + 1
''')
            
            # Check pin generation is consistent
            input_count = len(node.input_pins)
            output_count = len(node.output_pins)
            results.append((input_count, output_count))
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result, first_result)
    
    def test_memory_cleanup_after_operations(self):
        """Test that operations don't leak memory."""
        import gc
        import weakref
        
        # Create objects and track them with weak references
        weak_refs = []
        
        for i in range(100):
            graph = NodeGraph()
            node = graph.create_node(f"Cleanup Test {i}")
            
            # Create weak reference to track object lifecycle
            weak_refs.append(weakref.ref(node))
            weak_refs.append(weakref.ref(graph))
            
            # Clear explicit references
            del node
            del graph
        
        # Force garbage collection
        gc.collect()
        QApplication.processEvents()
        gc.collect()
        
        # Check that objects were properly cleaned up
        alive_refs = [ref for ref in weak_refs if ref() is not None]
        cleanup_rate = 1.0 - (len(alive_refs) / len(weak_refs))
        
        # Should have high cleanup rate (allowing for some QGraphicsItem lifecycle quirks)
        self.assertGreater(cleanup_rate, 0.8, 
                          f"Poor cleanup rate: {cleanup_rate:.2%} "
                          f"({len(alive_refs)}/{len(weak_refs)} objects still alive)")
```

### 5. Integration with PyFlowGraph Test Runner

```python
# Make tests compatible with the existing test runner
def run_pyside6_tests():
    """Entry point for the PyFlowGraph test runner."""
    # Discover all test classes
    loader = unittest.TestLoader()
    
    # Load test suites
    test_modules = [
        'test_node_system_headless',
        'test_node_system_gui', 
        'test_connection_system',
        'test_execution_engine',
        'test_visual_regression'
    ]
    
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            module_suite = loader.loadTestsFromModule(module)
            suite.addTest(module_suite)
        except ImportError as e:
            print(f"Warning: Could not load test module {module_name}: {e}")
    
    # Run with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True  # Capture stdout/stderr for cleaner output
    )
    
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_pyside6_tests()
    
    # Clean up QApplication
    app = QApplication.instance()
    if app:
        app.quit()
    
    sys.exit(0 if success else 1)
```

## Troubleshooting

### Common Issues and Solutions

**1. QApplication Already Exists Error**
```python
# Problem: Multiple QApplication instances
# Solution: Use singleton pattern
if QApplication.instance() is None:
    app = QApplication([])
else:
    app = QApplication.instance()
```

**2. Tests Hanging or Not Exiting**
```python
# Problem: Event loop not properly handled
# Solution: Process events and proper cleanup
def tearDown(self):
    QApplication.processEvents()
    # Don't call app.quit() in individual tests

@classmethod
def tearDownClass(cls):
    # Only quit in final cleanup if needed
    pass
```

**3. GUI Components Not Responding**
```python
# Problem: Events not processed
# Solution: Explicit event processing
QApplication.processEvents()

# For timer-based operations
QTest.qWait(100)  # Wait for 100ms and process events
```

**4. Flaky Test Results**
```python
# Problem: Race conditions in GUI tests
# Solution: Proper synchronization
def wait_for_condition(self, condition_func, timeout=5000):
    """Wait for a condition to become true."""
    start_time = time.time()
    while not condition_func() and (time.time() - start_time) * 1000 < timeout:
        QApplication.processEvents()
        time.sleep(0.01)
    
    self.assertTrue(condition_func(), "Condition was not met within timeout")

# Usage
self.wait_for_condition(lambda: len(self.graph.nodes) == expected_count)
```

**5. Memory Leaks in GUI Tests**
```python
# Problem: QGraphicsItems not properly cleaned up
# Solution: Explicit scene cleanup
def tearDown(self):
    if hasattr(self, 'graph'):
        self.graph.clear()
    if hasattr(self, 'scene'):
        self.scene.clear()
    QApplication.processEvents()
```

### Platform-Specific Considerations

**Windows:**
- Test runner GUI works out of the box
- Font rendering may vary slightly
- Use `run_test_gui.bat` for best experience

**Linux:**
- May need `xvfb` for headless GUI testing in CI
- Install: `sudo apt-get install xvfb`
- Run: `xvfb-run python test_gui.py`

**macOS:**
- Qt may require specific permissions for GUI automation
- Test runner should work natively

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: PyFlowGraph Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install PySide6
        # Install other dependencies
    
    - name: Run headless tests
      run: |
        # Run unit tests without GUI
        python -m pytest tests/unit/ -v
    
    - name: Run GUI tests with xvfb
      run: |
        # Run GUI tests in virtual display
        xvfb-run -a python -m pytest tests/integration/ -v
      env:
        QT_QPA_PLATFORM: offscreen
```

## Conclusion

This guide provides comprehensive coverage of PySide6/Qt testing strategies for the PyFlowGraph application. The key takeaways are:

1. **Use headless testing** for core logic and CI/CD pipelines
2. **Use GUI testing** for user interaction and visual validation
3. **Proper QApplication management** is crucial for reliable tests
4. **Event processing** is essential for GUI test reliability
5. **Mock external dependencies** to isolate units under test
6. **Organize tests by functionality** rather than implementation
7. **Test error conditions** and edge cases thoroughly
8. **Use the existing test runner** for consistency with project workflow

By following these patterns and best practices, you can build a robust test suite that ensures PyFlowGraph's reliability and maintainability while supporting both automated testing and manual validation workflows.
#!/usr/bin/env python3
"""
Actual Execution After Undo Test

This test reproduces the user's exact workflow:
1. Load the password generator tool 
2. Delete the 2 middle nodes
3. Undo the deletions
4. Actually execute the workflow (not just call set_gui_values)
5. Check if the output display node gets updated

This should reveal if the issue is with execution flow rather than GUI updates.
"""

import unittest
import sys
import os
import json
import subprocess
from unittest.mock import patch, MagicMock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication
from core.node_graph import NodeGraph
from core.node import Node
from commands.node_commands import DeleteNodeCommand
from execution.graph_executor import GraphExecutor
from core.connection import Connection


class TestActualExecutionAfterUndo(unittest.TestCase):
    """Test that actual execution works correctly after delete-undo operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        self.graph = NodeGraph()
        
        # Mock log widget that captures logs
        self.execution_logs = []
        self.log_widget = MagicMock()
        self.log_widget.append = lambda x: (print(f"EXEC_LOG: {x}"), self.execution_logs.append(x))
        
        # Mock venv path to use current Python
        def mock_venv_path():
            venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv')
            return os.path.abspath(venv_path)
        
        self.executor = GraphExecutor(self.graph, self.log_widget, mock_venv_path)
    
    def load_actual_password_generator(self):
        """Load the actual password generator tool from the examples directory."""
        print("\n=== Loading Actual Password Generator ===")
        
        # Read the actual password generator file
        password_gen_path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'password_generator_tool.md')
        
        if not os.path.exists(password_gen_path):
            self.skipTest(f"Password generator tool not found at {password_gen_path}")
        
        # Parse and load the tool
        from utils.node_loader import load_nodes_from_markdown
        try:
            nodes, connections = load_nodes_from_markdown(password_gen_path, self.graph)
            print(f"Loaded {len(nodes)} nodes and {len(connections)} connections from actual file")
            
            # Find specific nodes
            config_node = None
            generator_node = None
            analyzer_node = None
            output_node = None
            
            for node in nodes:
                if node.uuid == "config-input":
                    config_node = node
                elif node.uuid == "password-generator":
                    generator_node = node
                elif node.uuid == "strength-analyzer":
                    analyzer_node = node
                elif node.uuid == "output-display":
                    output_node = node
            
            self.assertIsNotNone(config_node, "Config node should be loaded")
            self.assertIsNotNone(generator_node, "Generator node should be loaded")
            self.assertIsNotNone(analyzer_node, "Analyzer node should be loaded")
            self.assertIsNotNone(output_node, "Output node should be loaded")
            
            return config_node, generator_node, analyzer_node, output_node
            
        except ImportError:
            # If node loader doesn't exist, create the nodes manually with the exact same code
            return self._create_nodes_manually()
    
    def _create_nodes_manually(self):
        """Create nodes manually with exact code from password generator tool."""
        print("Creating nodes manually...")
        
        # Create config node
        config_node = Node("Password Configuration")
        config_node.uuid = "config-input"
        config_node.setPos(107.935, 173.55)
        
        config_code = '''
from typing import Tuple

@node_entry
def configure_password(length: int, include_uppercase: bool, include_lowercase: bool, include_numbers: bool, include_symbols: bool) -> Tuple[int, bool, bool, bool, bool]:
    print(f"Password config: {length} chars, Upper: {include_uppercase}, Lower: {include_lowercase}, Numbers: {include_numbers}, Symbols: {include_symbols}")
    return length, include_uppercase, include_lowercase, include_numbers, include_symbols
'''
        
        config_gui_code = '''
from PySide6.QtWidgets import QLabel, QSpinBox, QCheckBox, QPushButton

layout.addWidget(QLabel('Password Length:', parent))
widgets['length'] = QSpinBox(parent)
widgets['length'].setRange(4, 128)
widgets['length'].setValue(12)
layout.addWidget(widgets['length'])

widgets['uppercase'] = QCheckBox('Include Uppercase (A-Z)', parent)
widgets['uppercase'].setChecked(True)
layout.addWidget(widgets['uppercase'])

widgets['lowercase'] = QCheckBox('Include Lowercase (a-z)', parent)
widgets['lowercase'].setChecked(True)
layout.addWidget(widgets['lowercase'])

widgets['numbers'] = QCheckBox('Include Numbers (0-9)', parent)
widgets['numbers'].setChecked(True)
layout.addWidget(widgets['numbers'])

widgets['symbols'] = QCheckBox('Include Symbols (!@#$%)', parent)
widgets['symbols'].setChecked(False)
layout.addWidget(widgets['symbols'])

widgets['generate_btn'] = QPushButton('Generate Password', parent)
layout.addWidget(widgets['generate_btn'])
'''
        
        config_gui_get_values = '''
def get_values(widgets):
    return {
        'length': widgets['length'].value(),
        'include_uppercase': widgets['uppercase'].isChecked(),
        'include_lowercase': widgets['lowercase'].isChecked(),
        'include_numbers': widgets['numbers'].isChecked(),
        'include_symbols': widgets['symbols'].isChecked()
    }

def set_values(widgets, outputs):
    # Config node doesn't need to display outputs
    pass

def set_initial_state(widgets, state):
    widgets['length'].setValue(state.get('length', 12))
    widgets['uppercase'].setChecked(state.get('include_uppercase', True))
    widgets['lowercase'].setChecked(state.get('include_lowercase', True))
    widgets['numbers'].setChecked(state.get('include_numbers', True))
    widgets['symbols'].setChecked(state.get('include_symbols', False))
'''
        
        config_node.set_code(config_code)
        config_node.set_gui_code(config_gui_code)
        config_node.set_gui_get_values_code(config_gui_get_values)
        
        # Create generator node
        generator_node = Node("Password Generator Engine")
        generator_node.uuid = "password-generator"
        generator_node.setPos(481.485, 202.645)
        
        generator_code = '''
import random
import string

@node_entry
def generate_password(length: int, include_uppercase: bool, include_lowercase: bool, include_numbers: bool, include_symbols: bool) -> str:
    charset = ''
    
    if include_uppercase:
        charset += string.ascii_uppercase
    if include_lowercase:
        charset += string.ascii_lowercase
    if include_numbers:
        charset += string.digits
    if include_symbols:
        charset += '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    if not charset:
        return "Error: No character types selected!"
    
    password = ''.join(random.choice(charset) for _ in range(length))
    print(f"Generated password: {password}")
    return password
'''
        
        generator_node.set_code(generator_code)
        
        # Create analyzer node
        analyzer_node = Node("Password Strength Analyzer")
        analyzer_node.uuid = "strength-analyzer"
        analyzer_node.setPos(844.8725, 304.73249999999996)
        
        analyzer_code = '''
import re
from typing import Tuple

@node_entry
def analyze_strength(password: str) -> Tuple[str, int, str]:
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 12:
        score += 25
    elif len(password) >= 8:
        score += 15
        feedback.append("Consider using 12+ characters")
    else:
        feedback.append("Password too short (8+ recommended)")
    
    # Character variety
    if re.search(r'[A-Z]', password):
        score += 20
    else:
        feedback.append("Add uppercase letters")
        
    if re.search(r'[a-z]', password):
        score += 20
    else:
        feedback.append("Add lowercase letters")
        
    if re.search(r'[0-9]', password):
        score += 20
    else:
        feedback.append("Add numbers")
        
    if re.search(r'[!@#$%^&*()_+=\\\\[\\\\]{}|;:,.<>?-]', password):
        score += 15
    else:
        feedback.append("Add symbols for extra security")
    
    # Determine strength level
    if score >= 80:
        strength = "Very Strong"
    elif score >= 60:
        strength = "Strong"
    elif score >= 40:
        strength = "Moderate"
    elif score >= 20:
        strength = "Weak"
    else:
        strength = "Very Weak"
    
    feedback_text = "; ".join(feedback) if feedback else "Excellent password!"
    
    print(f"Password strength: {strength} (Score: {score}/100)")
    print(f"Feedback: {feedback_text}")
    
    return strength, score, feedback_text
'''
        
        analyzer_node.set_code(analyzer_code)
        
        # Create output node
        output_node = Node("Password Output & Copy")
        output_node.uuid = "output-display"
        output_node.setPos(1182.5525, 137.84249999999997)
        
        output_code = '''
@node_entry
def display_result(password: str, strength: str, score: int, feedback: str) -> str:
    result = f"Generated Password: {password}\\n"
    result += f"Strength: {strength} ({score}/100)\\n"
    result += f"Feedback: {feedback}"
    print("\\n=== PASSWORD GENERATION COMPLETE ===")
    print(result)
    return result
'''
        
        output_gui_code = '''
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Generated Password', parent)
title_font = QFont()
title_font.setPointSize(14)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['password_field'] = QLineEdit(parent)
widgets['password_field'].setReadOnly(True)
widgets['password_field'].setPlaceholderText('Password will appear here...')
layout.addWidget(widgets['password_field'])

widgets['copy_btn'] = QPushButton('Copy to Clipboard', parent)
layout.addWidget(widgets['copy_btn'])

widgets['strength_display'] = QTextEdit(parent)
widgets['strength_display'].setMinimumHeight(120)
widgets['strength_display'].setReadOnly(True)
widgets['strength_display'].setPlainText('Generate a password to see strength analysis...')
layout.addWidget(widgets['strength_display'])
'''
        
        output_gui_get_values = '''
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    # Extract password from the result string
    result = outputs.get('output_1', '')
    lines = result.split('\\n')
    if lines:
        password_line = lines[0]
        if 'Generated Password: ' in password_line:
            password = password_line.replace('Generated Password: ', '')
            widgets['password_field'].setText(password)
    
    widgets['strength_display'].setPlainText(result)

def set_initial_state(widgets, state):
    # Output display node doesn't have saved state to restore
    pass
'''
        
        output_node.set_code(output_code)
        output_node.set_gui_code(output_gui_code)
        output_node.set_gui_get_values_code(output_gui_get_values)
        
        # Add all nodes to graph
        nodes = [config_node, generator_node, analyzer_node, output_node]
        for node in nodes:
            self.graph.addItem(node)
            self.graph.nodes.append(node)
        
        # Create connections exactly as in the password generator tool
        self._create_password_generator_connections(nodes)
        
        return config_node, generator_node, analyzer_node, output_node
    
    def _create_password_generator_connections(self, nodes):
        """Create the exact connections from the password generator tool."""
        config_node, generator_node, analyzer_node, output_node = nodes
        
        connections_data = [
            # Execution flow
            ("config-input", "exec_out", "password-generator", "exec_in"),
            ("password-generator", "exec_out", "strength-analyzer", "exec_in"),
            ("strength-analyzer", "exec_out", "output-display", "exec_in"),
            # Data flow from config to generator
            ("config-input", "output_1", "password-generator", "length"),
            ("config-input", "output_2", "password-generator", "include_uppercase"),
            ("config-input", "output_3", "password-generator", "include_lowercase"),
            ("config-input", "output_4", "password-generator", "include_numbers"),
            ("config-input", "output_5", "password-generator", "include_symbols"),
            # Password from generator to analyzer and output
            ("password-generator", "output_1", "strength-analyzer", "password"),
            ("password-generator", "output_1", "output-display", "password"),
            # Analysis results to output
            ("strength-analyzer", "output_1", "output-display", "strength"),
            ("strength-analyzer", "output_2", "output-display", "score"),
            ("strength-analyzer", "output_3", "output-display", "feedback"),
        ]
        
        node_map = {node.uuid: node for node in nodes}
        
        for start_uuid, start_pin, end_uuid, end_pin in connections_data:
            start_node = node_map[start_uuid]
            end_node = node_map[end_uuid]
            
            # Find pins by name
            start_pin_obj = start_node.get_pin_by_name(start_pin)
            end_pin_obj = end_node.get_pin_by_name(end_pin)
            
            if start_pin_obj and end_pin_obj:
                connection = Connection(start_pin_obj, end_pin_obj)
                self.graph.addItem(connection)
                self.graph.connections.append(connection)
            else:
                print(f"WARNING: Could not create connection {start_uuid}.{start_pin} -> {end_uuid}.{end_pin}")
                if not start_pin_obj:
                    print(f"  Start pin '{start_pin}' not found on {start_uuid}")
                if not end_pin_obj:
                    print(f"  End pin '{end_pin}' not found on {end_uuid}")
    
    def test_actual_execution_after_delete_undo(self):
        """Test that actual execution works after delete-undo operations."""
        print("\n=== Actual Execution After Delete-Undo Test ===")
        
        # Load the password generator
        config_node, generator_node, analyzer_node, output_node = self._create_nodes_manually()
        
        print(f"Initial state: {len(self.graph.nodes)} nodes, {len(self.graph.connections)} connections")
        
        # Verify initial output node state
        print("\n--- Initial Output Node State ---")
        self._verify_output_node_state(output_node, "Initial")
        
        # Test baseline execution
        print("\n--- Baseline Execution Test ---")
        with patch.object(self.executor, 'get_python_executable', return_value=sys.executable):
            self.execution_logs.clear()
            
            print("Running baseline execution...")
            self.executor.execute()
            
            print(f"Execution completed. Logs count: {len(self.execution_logs)}")
            for log in self.execution_logs[-5:]:  # Show last 5 logs
                print(f"  LOG: {log}")
            
            # Check if output node was reached and updated
            baseline_password = output_node.gui_widgets.get('password_field')
            baseline_strength = output_node.gui_widgets.get('strength_display')
            
            if baseline_password and baseline_strength:
                print(f"Baseline - Password: '{baseline_password.text()}'")
                print(f"Baseline - Strength: '{baseline_strength.toPlainText()[:50]}...'")
                
                # Verify execution reached output node
                baseline_has_password = bool(baseline_password.text().strip())
                baseline_has_result = "Generated Password:" in baseline_strength.toPlainText()
                
                print(f"Baseline execution successful: password={baseline_has_password}, result={baseline_has_result}")
            else:
                print("ERROR: Output node widgets not available for baseline test")
        
        # Delete the 2 middle nodes
        print("\n--- Deleting Middle Nodes ---")
        print(f"Deleting: {generator_node.title} and {analyzer_node.title}")
        
        delete_generator_cmd = DeleteNodeCommand(self.graph, generator_node)
        delete_analyzer_cmd = DeleteNodeCommand(self.graph, analyzer_node)
        
        gen_delete_success = delete_generator_cmd.execute()
        ana_delete_success = delete_analyzer_cmd.execute()
        
        self.assertTrue(gen_delete_success, "Generator deletion should succeed")
        self.assertTrue(ana_delete_success, "Analyzer deletion should succeed")
        
        print(f"After deletion: {len(self.graph.nodes)} nodes, {len(self.graph.connections)} connections")
        
        # Undo the deletions
        print("\n--- Undoing Deletions ---")
        
        ana_undo_success = delete_analyzer_cmd.undo()
        gen_undo_success = delete_generator_cmd.undo()
        
        self.assertTrue(ana_undo_success, "Analyzer undo should succeed")
        self.assertTrue(gen_undo_success, "Generator undo should succeed")
        
        print(f"After undo: {len(self.graph.nodes)} nodes, {len(self.graph.connections)} connections")
        
        # Find the restored output node
        restored_output_node = None
        for node in self.graph.nodes:
            if node.uuid == "output-display":
                restored_output_node = node
                break
        
        self.assertIsNotNone(restored_output_node, "Output node should be restored")
        
        # Verify post-undo state
        print("\n--- Post-Undo Output Node State ---")
        self._verify_output_node_state(restored_output_node, "Post-Undo")
        
        # Critical test: Execute after undo
        print("\n--- Critical Test: Execution After Undo ---")
        with patch.object(self.executor, 'get_python_executable', return_value=sys.executable):
            self.execution_logs.clear()
            
            print("Running post-undo execution...")
            self.executor.execute()
            
            print(f"Post-undo execution completed. Logs count: {len(self.execution_logs)}")
            for log in self.execution_logs[-10:]:  # Show last 10 logs
                print(f"  LOG: {log}")
            
            # Check if output node was reached and updated
            post_undo_password = restored_output_node.gui_widgets.get('password_field')
            post_undo_strength = restored_output_node.gui_widgets.get('strength_display')
            
            if post_undo_password and post_undo_strength:
                final_password_text = post_undo_password.text()
                final_strength_text = post_undo_strength.toPlainText()
                
                print(f"Post-undo - Password: '{final_password_text}'")
                print(f"Post-undo - Strength: '{final_strength_text[:50]}...'")
                
                # Critical checks - these reveal the actual bug
                post_undo_has_password = bool(final_password_text.strip())
                post_undo_has_result = "Generated Password:" in final_strength_text
                
                print(f"Post-undo execution results: password={post_undo_has_password}, result={post_undo_has_result}")
                
                # Check if execution logs show the output node was reached
                output_node_reached = any("Password Output & Copy" in log for log in self.execution_logs)
                set_gui_values_called = any("set_gui_values" in log for log in self.execution_logs)
                
                print(f"Execution flow analysis: output_node_reached={output_node_reached}, set_gui_values_called={set_gui_values_called}")
                
                # These assertions should reveal the actual bug
                self.assertTrue(output_node_reached, 
                              "CRITICAL BUG: Output node should be reached during execution after undo")
                self.assertTrue(set_gui_values_called,
                              "CRITICAL BUG: set_gui_values should be called during execution after undo") 
                self.assertTrue(post_undo_has_password,
                              "CRITICAL BUG: Password field should be updated after undo operations")
                self.assertTrue(post_undo_has_result,
                              "CRITICAL BUG: Strength display should be updated after undo operations")
                
                print("SUCCESS: Execution and GUI updates work correctly after delete-undo operations")
                
            else:
                self.fail("CRITICAL BUG: Output node widgets not available after undo")
    
    def _verify_output_node_state(self, output_node, phase):
        """Verify the state of the output node."""
        print(f"  {phase} output node: {output_node.title}")
        print(f"  GUI widgets available: {bool(output_node.gui_widgets)}")
        print(f"  GUI code length: {len(output_node.gui_code) if output_node.gui_code else 0}")
        print(f"  GUI get values code length: {len(output_node.gui_get_values_code) if output_node.gui_get_values_code else 0}")
        
        if output_node.gui_widgets:
            print(f"  Widget keys: {list(output_node.gui_widgets.keys())}")
            
            password_field = output_node.gui_widgets.get('password_field')
            strength_display = output_node.gui_widgets.get('strength_display')
            
            if password_field:
                print(f"  Password field text: '{password_field.text()}'")
            if strength_display:
                print(f"  Strength display text: '{strength_display.toPlainText()[:30]}...'")
        
        # Check connections
        exec_input_connections = 0
        data_input_connections = 0
        
        for pin in output_node.input_pins:
            if pin.pin_category == "execution" and pin.connections:
                exec_input_connections += len(pin.connections)
            elif pin.pin_category == "data" and pin.connections:
                data_input_connections += len(pin.connections)
        
        print(f"  Connections - Exec inputs: {exec_input_connections}, Data inputs: {data_input_connections}")


if __name__ == '__main__':
    unittest.main()
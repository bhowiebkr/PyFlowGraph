#!/usr/bin/env python3
"""
GUI Value Update Regression Test

This test reproduces the critical functional regression where the Password Output & Copy 
node stops updating its GUI values after deleting the 2 middle nodes and undoing them.

User workflow:
1. Load password generator tool
2. Delete the 2 middle nodes (Password Generator Engine and Password Strength Analyzer)
3. Undo the deletions
4. Execute the workflow
5. Verify that the output display node updates its GUI values correctly

The bug: After undo, the output node receives execution results but fails to update
its GUI widgets, even though performance is fine.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from core.node_graph import NodeGraph
from core.node import Node
from commands.node_commands import DeleteNodeCommand
from execution.graph_executor import GraphExecutor
from core.connection import Connection
from core.pin import Pin


class TestGUIValueUpdateRegression(unittest.TestCase):
    """Test that GUI values update correctly after delete-undo operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        
        self.graph = NodeGraph()
        
        # Mock log widget
        self.log_widget = MagicMock()
        self.log_widget.append = lambda x: print(f"LOG: {x}")
        
        # Mock venv path
        def mock_venv_path():
            return os.path.join(os.path.dirname(__file__), 'venvs', 'default')
        
        self.executor = GraphExecutor(self.graph, self.log_widget, mock_venv_path)
    
    def create_password_generator_simulation(self):
        """Create a simulation of the actual password generator workflow."""
        print("\n=== Creating Password Generator Simulation ===")
        
        # Create the 4 nodes from the password generator tool
        config_node = self._create_config_node()
        generator_node = self._create_generator_node()
        analyzer_node = self._create_analyzer_node()
        output_node = self._create_output_node()
        
        nodes = [config_node, generator_node, analyzer_node, output_node]
        
        # Add nodes to graph
        for i, node in enumerate(nodes):
            node.setPos(i * 300, 100)
            self.graph.addItem(node)
            self.graph.nodes.append(node)
        
        # Create connections matching the password generator tool
        connections = []
        
        # Execution flow connections
        for i in range(len(nodes) - 1):
            exec_conn = Connection(
                nodes[i].output_pins[0],  # exec_out
                nodes[i + 1].input_pins[0]  # exec_in
            )
            self.graph.addItem(exec_conn)
            self.graph.connections.append(exec_conn)
            connections.append(exec_conn)
        
        # Data connections from config to generator (5 data outputs)
        for i in range(1, 6):  # output_1 through output_5
            if i < len(config_node.output_pins):
                data_conn = Connection(
                    config_node.output_pins[i],
                    generator_node.input_pins[i] if i < len(generator_node.input_pins) else generator_node.input_pins[-1]
                )
                self.graph.addItem(data_conn)
                self.graph.connections.append(data_conn)
                connections.append(data_conn)
        
        # Generator to analyzer connection
        if len(generator_node.output_pins) > 1 and len(analyzer_node.input_pins) > 1:
            gen_to_analyzer = Connection(
                generator_node.output_pins[1],  # password output
                analyzer_node.input_pins[1]     # password input
            )
            self.graph.addItem(gen_to_analyzer)
            self.graph.connections.append(gen_to_analyzer)
            connections.append(gen_to_analyzer)
        
        # Generator and analyzer to output display connections
        if len(generator_node.output_pins) > 1 and len(output_node.input_pins) > 1:
            gen_to_output = Connection(
                generator_node.output_pins[1],  # password
                output_node.input_pins[1]       # password input
            )
            self.graph.addItem(gen_to_output)
            self.graph.connections.append(gen_to_output)
            connections.append(gen_to_output)
        
        # Analyzer outputs to output display
        for i in range(1, min(4, len(analyzer_node.output_pins))):  # strength, score, feedback
            if i + 1 < len(output_node.input_pins):
                analyzer_to_output = Connection(
                    analyzer_node.output_pins[i],
                    output_node.input_pins[i + 1]
                )
                self.graph.addItem(analyzer_to_output)
                self.graph.connections.append(analyzer_to_output)
                connections.append(analyzer_to_output)
        
        print(f"Created {len(nodes)} nodes and {len(connections)} connections")
        print(f"Nodes: {[node.title for node in nodes]}")
        
        return nodes, connections
    
    def _create_config_node(self):
        """Create Password Configuration node."""
        node = Node("Password Configuration")
        node.uuid = "config-input"
        
        # Set code to match password generator tool
        code = '''
from typing import Tuple

@node_entry
def configure_password(length: int, include_uppercase: bool, include_lowercase: bool, include_numbers: bool, include_symbols: bool) -> Tuple[int, bool, bool, bool, bool]:
    print(f"Password config: {length} chars, Upper: {include_uppercase}, Lower: {include_lowercase}, Numbers: {include_numbers}, Symbols: {include_symbols}")
    return length, include_uppercase, include_lowercase, include_numbers, include_symbols
'''
        
        gui_code = '''
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
'''
        
        gui_get_values_code = '''
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
        
        node.set_code(code)
        node.set_gui_code(gui_code)
        node.set_gui_get_values_code(gui_get_values_code)
        
        return node
    
    def _create_generator_node(self):
        """Create Password Generator Engine node."""
        node = Node("Password Generator Engine")
        node.uuid = "password-generator"
        
        code = '''
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
        
        node.set_code(code)
        return node
    
    def _create_analyzer_node(self):
        """Create Password Strength Analyzer node."""
        node = Node("Password Strength Analyzer")
        node.uuid = "strength-analyzer"
        
        code = '''
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
        
    if re.search(r'[!@#$%^&*()_+=\\[\\]{}|;:,.<>?-]', password):
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
        
        node.set_code(code)
        return node
    
    def _create_output_node(self):
        """Create Password Output & Copy node (the critical one that fails)."""
        node = Node("Password Output & Copy")
        node.uuid = "output-display"
        
        code = '''
@node_entry
def display_result(password: str, strength: str, score: int, feedback: str) -> str:
    result = f"Generated Password: {password}\\n"
    result += f"Strength: {strength} ({score}/100)\\n"
    result += f"Feedback: {feedback}"
    print("\\n=== PASSWORD GENERATION COMPLETE ===")
    print(result)
    return result
'''
        
        # Critical GUI code that should update after execution
        gui_code = '''
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
        
        # Critical GUI state handler that should be called after execution
        gui_get_values_code = '''
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
        
        node.set_code(code)
        node.set_gui_code(gui_code)
        node.set_gui_get_values_code(gui_get_values_code)
        
        return node
    
    def verify_output_node_gui_state(self, output_node):
        """Verify that the output node has proper GUI widgets after restoration."""
        print(f"\n=== Verifying Output Node GUI State ===")
        print(f"Node title: {output_node.title}")
        print(f"GUI widgets available: {bool(output_node.gui_widgets)}")
        
        if output_node.gui_widgets:
            print(f"Widget keys: {list(output_node.gui_widgets.keys())}")
            
            # Check critical widgets
            password_field = output_node.gui_widgets.get('password_field')
            strength_display = output_node.gui_widgets.get('strength_display')
            
            print(f"Password field available: {password_field is not None}")
            print(f"Strength display available: {strength_display is not None}")
            
            if password_field:
                print(f"Password field text: '{password_field.text()}'")
            if strength_display:
                print(f"Strength display text: '{strength_display.toPlainText()[:50]}...'")
            
            return password_field is not None and strength_display is not None
        else:
            print("No GUI widgets found!")
            return False
    
    def test_gui_value_update_after_delete_undo(self):
        """Test the critical bug: GUI values don't update after delete-undo operations."""
        print("\n=== GUI Value Update Regression Test ===")
        
        # Create password generator simulation
        nodes, connections = self.create_password_generator_simulation()
        config_node, generator_node, analyzer_node, output_node = nodes
        
        print(f"\n--- Initial State ---")
        print(f"Total nodes: {len(self.graph.nodes)}")
        print(f"Total connections: {len(self.graph.connections)}")
        
        # Verify initial GUI state of output node
        initial_gui_valid = self.verify_output_node_gui_state(output_node)
        self.assertTrue(initial_gui_valid, "Output node should have valid GUI widgets initially")
        
        # Mock execution to test baseline functionality
        print(f"\n--- Baseline Execution Test ---")
        with patch.object(self.executor, 'get_python_executable', return_value='python'):
            with patch('subprocess.run') as mock_run:
                # Mock successful execution results
                mock_run.return_value.stdout = json.dumps({
                    'result': 'TestPassword123!',
                    'stdout': 'Generated password: TestPassword123!'
                })
                mock_run.return_value.stderr = ''
                mock_run.return_value.returncode = 0
                
                # Test that output node receives values in baseline
                print("Testing baseline GUI value update...")
                test_outputs = {
                    'output_1': 'Generated Password: TestPassword123!\nStrength: Very Strong (80/100)\nFeedback: Excellent password!'
                }
                
                print(f"Calling set_gui_values with: {test_outputs}")
                output_node.set_gui_values(test_outputs)
                
                # Verify baseline functionality
                password_field = output_node.gui_widgets.get('password_field')
                strength_display = output_node.gui_widgets.get('strength_display')
                if password_field and strength_display:
                    baseline_password_text = password_field.text()
                    baseline_strength_text = strength_display.toPlainText()
                    print(f"Baseline password field text: '{baseline_password_text}'")
                    print(f"Baseline strength display text: '{baseline_strength_text[:50]}...'")
                    self.assertEqual(baseline_password_text, 'TestPassword123!', 
                                   "Baseline: Password field should show extracted password only")
                    self.assertIn('Generated Password: TestPassword123!', baseline_strength_text,
                                 "Baseline: Strength display should show full result")
        
        # Delete the 2 middle nodes (this is the critical test case)
        print(f"\n--- Deleting Middle Nodes ---")
        print(f"Deleting: {generator_node.title} and {analyzer_node.title}")
        
        # Delete generator node
        delete_generator_cmd = DeleteNodeCommand(self.graph, generator_node)
        generator_success = delete_generator_cmd.execute()
        self.assertTrue(generator_success, "Generator node deletion should succeed")
        
        # Delete analyzer node  
        delete_analyzer_cmd = DeleteNodeCommand(self.graph, analyzer_node)
        analyzer_success = delete_analyzer_cmd.execute()
        self.assertTrue(analyzer_success, "Analyzer node deletion should succeed")
        
        print(f"After deletion - Nodes: {len(self.graph.nodes)}, Connections: {len(self.graph.connections)}")
        
        # Undo the deletions (this is where the bug manifests)
        print(f"\n--- Undoing Deletions ---")
        
        analyzer_undo_success = delete_analyzer_cmd.undo()
        self.assertTrue(analyzer_undo_success, "Analyzer node undo should succeed")
        
        generator_undo_success = delete_generator_cmd.undo()
        self.assertTrue(generator_undo_success, "Generator node undo should succeed")
        
        print(f"After undo - Nodes: {len(self.graph.nodes)}, Connections: {len(self.graph.connections)}")
        
        # Find the restored output node (it should be the same object, but verify)
        restored_output_node = None
        for node in self.graph.nodes:
            if node.uuid == "output-display":
                restored_output_node = node
                break
        
        self.assertIsNotNone(restored_output_node, "Output node should be found after undo")
        
        # Verify GUI state after restoration
        print(f"\n--- Post-Undo GUI State Verification ---")
        post_undo_gui_valid = self.verify_output_node_gui_state(restored_output_node)
        self.assertTrue(post_undo_gui_valid, "Output node should have valid GUI widgets after undo")
        
        # Critical test: Verify GUI values can still be updated
        print(f"\n--- Critical Test: GUI Value Update After Undo ---")
        test_outputs_post_undo = {
            'output_1': 'Generated Password: PostUndoPassword456!\nStrength: Strong (75/100)\nFeedback: Good password!'
        }
        
        print(f"Testing post-undo GUI value update...")
        print(f"Calling set_gui_values with: {test_outputs_post_undo}")
        
        # Store initial values for comparison
        password_field = restored_output_node.gui_widgets.get('password_field')
        strength_display = restored_output_node.gui_widgets.get('strength_display')
        
        if password_field and strength_display:
            initial_password_text = password_field.text()
            initial_strength_text = strength_display.toPlainText()
            
            print(f"Before update - Password: '{initial_password_text}', Strength: '{initial_strength_text[:30]}...'")
            
            # This is the critical call that should work but fails in the bug
            restored_output_node.set_gui_values(test_outputs_post_undo)
            
            # Verify the update worked
            updated_password_text = password_field.text()
            updated_strength_text = strength_display.toPlainText()
            
            print(f"After update - Password: '{updated_password_text}', Strength: '{updated_strength_text[:30]}...'")
            
            # Critical assertions - these should pass but fail in the bug
            self.assertEqual(updated_password_text, 'PostUndoPassword456!', 
                           "CRITICAL BUG: Password field should update after undo operations")
            self.assertIn('PostUndoPassword456!', updated_strength_text,
                         "CRITICAL BUG: Strength display should update after undo operations")
            
            print("SUCCESS: GUI value updates work correctly after delete-undo operations")
            
        else:
            self.fail("CRITICAL BUG: GUI widgets not available after undo operations")
    
    def test_connection_integrity_after_undo(self):
        """Verify that connections are properly restored for execution flow."""
        print("\n=== Connection Integrity Test ===")
        
        nodes, connections = self.create_password_generator_simulation()
        config_node, generator_node, analyzer_node, output_node = nodes
        
        initial_connection_count = len(self.graph.connections)
        print(f"Initial connections: {initial_connection_count}")
        
        # Delete and undo middle nodes
        delete_generator_cmd = DeleteNodeCommand(self.graph, generator_node)
        delete_analyzer_cmd = DeleteNodeCommand(self.graph, analyzer_node)
        
        delete_generator_cmd.execute()
        delete_analyzer_cmd.execute()
        
        # Undo
        delete_analyzer_cmd.undo()
        delete_generator_cmd.undo()
        
        final_connection_count = len(self.graph.connections)
        print(f"Final connections: {final_connection_count}")
        
        # Verify connection count restored
        self.assertEqual(final_connection_count, initial_connection_count,
                        "All connections should be restored after undo")
        
        # Verify execution flow integrity
        restored_output_node = None
        for node in self.graph.nodes:
            if node.uuid == "output-display":
                restored_output_node = node
                break
        
        # Check that output node has proper input connections
        exec_input_connections = 0
        data_input_connections = 0
        
        for pin in restored_output_node.input_pins:
            if pin.pin_category == "execution" and pin.connections:
                exec_input_connections += len(pin.connections)
            elif pin.pin_category == "data" and pin.connections:
                data_input_connections += len(pin.connections)
        
        print(f"Output node - Exec inputs: {exec_input_connections}, Data inputs: {data_input_connections}")
        
        self.assertGreater(exec_input_connections, 0, "Output node should have execution input connections")
        self.assertGreater(data_input_connections, 0, "Output node should have data input connections")


if __name__ == '__main__':
    unittest.main()
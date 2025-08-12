#!/usr/bin/env python3

"""
Simple test script to create nodes with execution flow and test the new architecture.
This creates a basic linear execution flow: Start -> Process -> End
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from node import Node
from node_graph import NodeGraph
from graph_executor import GraphExecutor
from PySide6.QtWidgets import QApplication, QTextEdit
from PySide6.QtCore import QPointF

def create_test_graph():
    """Create a simple test graph with execution flow."""
    
    # Create the node graph
    graph = NodeGraph()
    
    # Create a start node
    start_node = graph.create_node("Start Node", pos=(100, 100))
    start_code = '''
@node_entry
def start() -> str:
    print("Starting execution...")
    return "Hello from start!"
'''
    start_node.set_code(start_code)
    
    # Create a process node
    process_node = graph.create_node("Process Node", pos=(400, 100))
    process_code = '''
@node_entry
def process(input_text: str) -> str:
    print(f"Processing: {input_text}")
    result = f"Processed: {input_text.upper()}"
    return result
'''
    process_node.set_code(process_code)
    
    # Create an end node
    end_node = graph.create_node("End Node", pos=(700, 100))
    end_code = '''
@node_entry
def end(final_text: str):
    print(f"Final result: {final_text}")
    print("Execution completed!")
'''
    end_node.set_code(end_code)
    
    # Connect execution flow: start -> process -> end
    start_exec_out = start_node.get_pin_by_name("exec_out")
    process_exec_in = process_node.get_pin_by_name("exec_in")
    if start_exec_out and process_exec_in:
        graph.create_connection(start_exec_out, process_exec_in)
    
    process_exec_out = process_node.get_pin_by_name("exec_out")
    end_exec_in = end_node.get_pin_by_name("exec_in")
    if process_exec_out and end_exec_in:
        graph.create_connection(process_exec_out, end_exec_in)
    
    # Connect data flow: start output -> process input -> end input
    start_data_out = start_node.get_pin_by_name("output_1")
    process_data_in = process_node.get_pin_by_name("input_text")
    if start_data_out and process_data_in:
        graph.create_connection(start_data_out, process_data_in)
    
    process_data_out = process_node.get_pin_by_name("output_1")
    end_data_in = end_node.get_pin_by_name("final_text")
    if process_data_out and end_data_in:
        graph.create_connection(process_data_out, end_data_in)
    
    return graph

def test_execution():
    """Test the execution flow."""
    print("=== Testing New Execution Flow Architecture ===")
    
    # Create QApplication for Qt functionality
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create test graph
    graph = create_test_graph()
    
    # Create a log widget to capture output
    log_widget = QTextEdit()
    
    # Create executor with dummy venv path callback
    def get_venv_path():
        return os.path.join(os.getcwd(), "venv")
    
    executor = GraphExecutor(graph, log_widget, get_venv_path)
    
    print(f"Created graph with {len(graph.nodes)} nodes")
    print("Nodes:")
    for i, node in enumerate(graph.nodes):
        print(f"  {i+1}. {node.title}")
        exec_inputs = [p for p in node.input_pins if p.pin_category == "execution"]
        exec_outputs = [p for p in node.output_pins if p.pin_category == "execution"]
        data_inputs = [p for p in node.input_pins if p.pin_category == "data"]
        data_outputs = [p for p in node.output_pins if p.pin_category == "data"]
        print(f"     Exec pins: {len(exec_inputs)} in, {len(exec_outputs)} out")
        print(f"     Data pins: {len(data_inputs)} in, {len(data_outputs)} out")
    
    print("\nConnections:")
    for i, conn in enumerate(graph.connections):
        start_category = conn.start_pin.pin_category
        end_category = conn.end_pin.pin_category
        print(f"  {i+1}. {conn.start_pin.node.title}.{conn.start_pin.name} ({start_category}) -> {conn.end_pin.node.title}.{conn.end_pin.name} ({end_category})")
    
    print("\n=== Executing Graph ===")
    try:
        executor.execute()
        print("\n=== Execution Log ===")
        print(log_widget.toPlainText())
        print("=== Test Completed Successfully ===")
    except Exception as e:
        print(f"Execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_execution()
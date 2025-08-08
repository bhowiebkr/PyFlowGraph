# default_graphs.py
# Contains functions to create default example graphs for the node editor.

from typing import Tuple

def create_complex_default_graph(graph):
    """
    Creates and connects a complex graph with multiple nodes and data types
    to demonstrate the editor's capabilities.

    :param graph: The NodeGraph instance to populate.
    """
    # --- Node Definitions ---

    # Node 1: Provides initial data of various types
    node1_data = graph.create_node("Initial Data Provider", pos=(50, 200))
    node1_data.set_code(
        "from typing import Tuple\n\n"
        "def get_initial_data() -> Tuple[float, int, str, bool]:\n"
        "    return 3.14159, 42, 'Graph', True"
    )

    # Node 2: Performs math on a float
    node2_float_math = graph.create_node("Float Operations", pos=(350, 50))
    # BUG FIX: Added 'import math' so the function can execute correctly.
    node2_float_math.set_code(
        "import math\n\n"
        "def process_float(input_float: float) -> float:\n"
        "    return math.sin(input_float) * 100.0"
    )

    # Node 3: Performs logic on an integer
    node3_int_logic = graph.create_node("Integer Operations", pos=(350, 200))
    node3_int_logic.set_code(
        "def process_integer(input_int: int) -> int:\n"
        "    return (input_int * 2) + 10"
    )

    # Node 4: Manipulates strings
    node4_string_ops = graph.create_node("String Manipulation", pos=(350, 350))
    node4_string_ops.set_code(
        "def process_string(base_string: str) -> str:\n"
        "    return f'Processed: {base_string.upper()}'"
    )

    # Node 5: Uses a boolean to make a decision
    node5_bool_logic = graph.create_node("Conditional Logic", pos=(350, 500))
    node5_bool_logic.set_code(
        "def process_boolean(condition: bool) -> str:\n"
        "    return 'Condition was TRUE' if condition else 'Condition was FALSE'"
    )
    
    # Node 6: Converts the result of float math to an integer
    node6_type_conversion1 = graph.create_node("Convert Float to Int", pos=(650, 50))
    node6_type_conversion1.set_code(
        "def convert_to_int(float_val: float) -> int:\n"
        "    return int(float_val)"
    )
    
    # Node 7: Combines two integer results
    node7_aggregator1 = graph.create_node("Combine Integers", pos=(950, 125))
    node7_aggregator1.set_code(
        "def combine_integers(val_a: int, val_b: int) -> str:\n"
        "    return f'Sum of ints: {val_a + val_b}'"
    )

    # Node 8: Another string operation that takes an int
    node8_string_ops2 = graph.create_node("Format Int to String", pos=(650, 275))
    node8_string_ops2.set_code(
        "def format_int(int_val: int) -> str:\n"
        "    return f'Integer result: {int_val}'"
    )

    # Node 9: An aggregator that combines multiple string results
    node9_aggregator2 = graph.create_node("Combine Strings", pos=(1250, 300))
    node9_aggregator2.set_code(
        "from typing import Tuple\n\n"
        "def combine_strings(str_a: str, str_b: str, str_c: str) -> Tuple[str, int]:\n"
        "    combined = f'[{str_a}] - [{str_b}] - [{str_c}]'\n"
        "    return combined, len(combined)"
    )

    # Node 10: The final printer node
    node10_printer = graph.create_node("Final Report Printer", pos=(1550, 300))
    node10_printer.set_code(
        "def final_report(report_string: str, char_count: int):\n"
        "    print('--- FINAL REPORT ---')\n"
        "    print(report_string)\n"
        "    print(f'Total Characters: {char_count}')"
    )

    # --- Connections ---
    
    # Connect Initial Data to processors
    graph.create_connection(node1_data.get_pin_by_name("output_1"), node2_float_math.get_pin_by_name("input_float"))
    graph.create_connection(node1_data.get_pin_by_name("output_2"), node3_int_logic.get_pin_by_name("input_int"))
    graph.create_connection(node1_data.get_pin_by_name("output_3"), node4_string_ops.get_pin_by_name("base_string"))
    graph.create_connection(node1_data.get_pin_by_name("output_4"), node5_bool_logic.get_pin_by_name("condition"))

    # Connect Float Math to Type Converter
    graph.create_connection(node2_float_math.get_pin_by_name("output_1"), node6_type_conversion1.get_pin_by_name("float_val"))

    # Connect Integer results to Integer Combiner
    graph.create_connection(node3_int_logic.get_pin_by_name("output_1"), node7_aggregator1.get_pin_by_name("val_a"))
    graph.create_connection(node6_type_conversion1.get_pin_by_name("output_1"), node7_aggregator1.get_pin_by_name("val_b"))

    # Connect another Integer result to a String Formatter
    graph.create_connection(node3_int_logic.get_pin_by_name("output_1"), node8_string_ops2.get_pin_by_name("int_val"))

    # Connect all string results to the String Combiner
    graph.create_connection(node4_string_ops.get_pin_by_name("output_1"), node9_aggregator2.get_pin_by_name("str_a"))
    graph.create_connection(node5_bool_logic.get_pin_by_name("output_1"), node9_aggregator2.get_pin_by_name("str_b"))
    graph.create_connection(node7_aggregator1.get_pin_by_name("output_1"), node9_aggregator2.get_pin_by_name("str_c"))

    # Connect the final combined string to the printer
    graph.create_connection(node9_aggregator2.get_pin_by_name("output_1"), node10_printer.get_pin_by_name("report_string"))
    graph.create_connection(node9_aggregator2.get_pin_by_name("output_2"), node10_printer.get_pin_by_name("char_count"))

    graph.update()

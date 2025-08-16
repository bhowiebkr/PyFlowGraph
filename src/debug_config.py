# Debug Configuration for PyFlowGraph
# Central location for controlling debug output across the application

# Layout and sizing debug output
DEBUG_LAYOUT = True

# Node restoration and undo/redo debug output  
DEBUG_UNDO_REDO = True

# File loading and validation debug output
DEBUG_FILE_LOADING = True

# Pin positioning and visual updates debug output
DEBUG_PINS = True

# Set to False to disable all debug output for production
DEBUG_MASTER_SWITCH = False

def should_debug(debug_category=True):
    """Check if debugging should be enabled for a category."""
    return DEBUG_MASTER_SWITCH and debug_category
"""
Event-driven execution system for interactive PyFlowCanvas applications.
Enables live, event-based execution with state persistence.
"""

from enum import Enum
from typing import Dict, Any, Optional, Callable
from PySide6.QtCore import QObject, Signal, QTimer
from collections import defaultdict


class EventType(Enum):
    """Types of events that can trigger node execution."""
    BUTTON_CLICK = "button_click"
    TIMER_TICK = "timer_tick"
    VALUE_CHANGED = "value_changed"
    USER_INPUT = "user_input"
    GRAPH_RESET = "graph_reset"
    NODE_TRIGGER = "node_trigger"


class GraphEvent:
    """Represents an event that occurred in the graph."""
    
    def __init__(self, event_type: EventType, source_node=None, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.source_node = source_node
        self.data = data or {}
        self.timestamp = None


class EventManager(QObject):
    """Manages event registration, emission, and handling for the graph."""
    
    # Signal emitted when an event should trigger execution
    event_triggered = Signal(object)  # Emits GraphEvent
    
    def __init__(self):
        super().__init__()
        self.event_handlers: Dict[str, list] = defaultdict(list)
        self.node_events: Dict[str, list] = defaultdict(list)  # node_uuid -> events
        
    def register_node_event(self, node_uuid: str, event_type: EventType, callback: Callable):
        """Register an event handler for a specific node."""
        event_key = f"{node_uuid}:{event_type.value}"
        self.event_handlers[event_key].append(callback)
        self.node_events[node_uuid].append(event_type)
        
    def emit_event(self, event_type: EventType, source_node=None, data: Dict[str, Any] = None):
        """Emit an event that may trigger node execution."""
        event = GraphEvent(event_type, source_node, data)
        
        # Handle node-specific events
        if source_node:
            event_key = f"{source_node.uuid}:{event_type.value}"
            for handler in self.event_handlers.get(event_key, []):
                handler(event)
                
        # Emit global event signal
        self.event_triggered.emit(event)
        
    def clear_node_events(self, node_uuid: str):
        """Clear all event handlers for a node."""
        events = self.node_events.get(node_uuid, [])
        for event_type in events:
            event_key = f"{node_uuid}:{event_type.value}"
            self.event_handlers.pop(event_key, None)
        self.node_events.pop(node_uuid, None)


class LiveGraphExecutor:
    """Enhanced graph executor with event-driven capabilities and state persistence."""
    
    def __init__(self, graph, log_widget, venv_path_callback):
        self.graph = graph
        self.log = log_widget
        self.get_venv_path = venv_path_callback
        self.event_manager = EventManager()
        
        # Live mode state
        self.live_mode = False
        self.graph_state = {}  # Persistent state between executions
        self.pin_values = {}   # Persistent pin values
        
        # Connect event manager
        self.event_manager.event_triggered.connect(self.handle_event)
        
    def set_live_mode(self, enabled: bool):
        """Toggle between live mode and batch mode."""
        self.live_mode = enabled
        if enabled:
            self.log.append("🔥 LIVE MODE ACTIVATED - Graph is now interactive!")
            self._setup_node_events()
        else:
            self.log.append("📦 BATCH MODE ACTIVATED - Traditional execution mode")
            self._cleanup_node_events()
            self.reset_graph_state()
    
    def _setup_node_events(self):
        """Set up event handlers for all interactive nodes."""
        for node in self.graph.nodes:
            if hasattr(node, 'gui_widgets') and node.gui_widgets:
                self._setup_node_event_handlers(node)
    
    def _setup_node_event_handlers(self, node):
        """Set up event handlers for a specific node's widgets."""
        if not hasattr(node, 'gui_widgets') or not node.gui_widgets:
            return
            
        widgets = node.gui_widgets
        
        # Look for buttons and connect them to events
        connected_count = 0
        for widget_name, widget in widgets.items():
            if hasattr(widget, 'clicked'):  # It's a button
                try:
                    # Use lambda with default parameter to capture node properly
                    widget.clicked.connect(
                        lambda checked=False, n=node: self.trigger_node_execution(n)
                    )
                    connected_count += 1
                    self.log.append(f"🔗 Connected '{widget_name}' button in '{node.title}'")
                except Exception as e:
                    self.log.append(f"⚠️ Failed to connect button '{widget_name}': {e}")
        
        if connected_count == 0:
            self.log.append(f"ℹ️ No buttons found in '{node.title}'")
    
    def _cleanup_node_events(self):
        """Clean up all node event handlers."""
        for node in self.graph.nodes:
            self.event_manager.clear_node_events(node.uuid)
    
    def trigger_node_execution(self, source_node):
        """Trigger execution starting from a specific node."""
        if not self.live_mode:
            self.log.append("⚠️ Not in live mode - enable Live Mode first!")
            return
            
        self.log.append(f"🚀 Button clicked in '{source_node.title}'")
        self.log.append(f"⚡ Starting execution flow...")
        
        # Execute this node and follow execution flow
        try:
            self._execute_node_flow_live(source_node)
            self.log.append("✅ Interactive execution completed!")
            self.log.append("🎯 Ready for next interaction...")
        except Exception as e:
            self.log.append(f"❌ Execution error: {e}")
            self.log.append("💡 Try resetting the graph")
    
    def _execute_node_flow_live(self, node):
        """Execute a node in live mode with state persistence."""
        from graph_executor import GraphExecutor
        
        # Create a temporary executor for this execution
        temp_executor = GraphExecutor(self.graph, self.log, self.get_venv_path)
        
        # Execute just this node and its downstream flow
        execution_count = temp_executor._execute_node_flow(node, self.pin_values, 0, 100)
        
        self.log.append(f"✅ Live execution completed ({execution_count} nodes)")
    
    def handle_event(self, event: GraphEvent):
        """Handle an event emitted by the event manager."""
        # Removed GRAPH_RESET handling to prevent recursion
        if event.event_type == EventType.NODE_TRIGGER:
            if event.source_node:
                self.trigger_node_execution(event.source_node)
    
    def reset_graph_state(self):
        """Reset the graph to initial state."""
        self.graph_state.clear()
        self.pin_values.clear()
        self.log.append("🔄 Graph state reset")
        
        # DON'T emit GRAPH_RESET event to avoid recursion
        # The reset is complete - no need for additional events
    
    def restart_graph(self):
        """Reset and restart the entire graph."""
        self.reset_graph_state()
        self.log.append("🔄 Graph reset completed. Click node buttons to start interaction.")
        
        # DON'T auto-trigger entry nodes - let user click buttons instead
        # This prevents recursion and gives users control
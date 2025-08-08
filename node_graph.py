# node_graph.py
# The QGraphicsScene that manages nodes, connections, and their interactions.

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt
from node import Node
from reroute_node import RerouteNode
from connection import Connection
from pin import Pin

class NodeGraph(QGraphicsScene):
    """
    The main scene for the node editor. Manages nodes, connections, and drag logic.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(Qt.darkGray)
        
        self.nodes = []
        self.connections = []
        
        self._drag_connection = None
        self._drag_start_pin = None

    def create_node(self, title, pos=(0, 0), is_reroute=False):
        """Factory method to create a new node and add it to the graph."""
        if is_reroute:
            node = RerouteNode()
        else:
            node = Node(title)
        
        node.setPos(pos[0], pos[1])
        self.addItem(node)
        self.nodes.append(node)
        return node

    def remove_node(self, node):
        """Remove a node and its connections from the graph."""
        if hasattr(node, 'pins'):
            for pin in list(node.pins):
                if hasattr(node, 'remove_pin'):
                    node.remove_pin(pin)
                else: # For simpler nodes like Reroute
                    for conn in list(pin.connections):
                        self.remove_connection(conn)

        if node in self.nodes:
            self.nodes.remove(node)
        
        self.removeItem(node)

    def create_connection(self, start_pin, end_pin):
        if start_pin.can_connect_to(end_pin):
            conn = Connection(start_pin, end_pin)
            self.addItem(conn)
            self.connections.append(conn)
            return conn
        return None

    def remove_connection(self, connection):
        connection.remove()
        if connection in self.connections:
            self.connections.remove(connection)
        self.removeItem(connection)

    def create_reroute_node_on_connection(self, connection, position):
        """Splits a connection by inserting a reroute node."""
        start_pin = connection.start_pin
        end_pin = connection.end_pin

        # Remove the original connection
        self.remove_connection(connection)

        # Create the reroute node
        reroute_node = self.create_node("", pos=(position.x(), position.y()), is_reroute=True)

        # Create two new connections
        self.create_connection(start_pin, reroute_node.input_pin)
        self.create_connection(reroute_node.output_pin, end_pin)


    def start_drag_connection(self, start_pin):
        self._drag_start_pin = start_pin
        self._drag_connection = Connection(start_pin, None)
        self.addItem(self._drag_connection)

    def update_drag_connection(self, end_pos):
        if self._drag_connection:
            self._drag_connection.set_end_pos(end_pos)
            self.update()

    def end_drag_connection(self, end_pos):
        if self._drag_connection is None or self._drag_start_pin is None: return

        target_item = self.itemAt(end_pos, self.views()[0].transform())
        
        self.removeItem(self._drag_connection)
        self._drag_connection = None
        
        if isinstance(target_item, Pin):
            self.create_connection(self._drag_start_pin, target_item)
        
        self._drag_start_pin = None

    def mouseMoveEvent(self, event):
        if self._drag_connection:
            self.update_drag_connection(event.scenePos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_connection:
            self.end_drag_connection(event.scenePos())
        super().mouseReleaseEvent(event)

    def serialize(self):
        nodes_data = [node.serialize() for node in self.nodes if isinstance(node, Node)]
        connections_data = [conn.serialize() for conn in self.connections if conn.serialize() is not None]
        return {"nodes": nodes_data, "connections": connections_data}

    def deserialize(self, data):
        for node in list(self.nodes):
            self.remove_node(node)

        node_map = {}
        for node_data in data.get("nodes", []):
            node = self.create_node(node_data['title'], node_data['pos'])
            node.uuid = node_data['uuid']
            node.set_code(node_data.get('code', ''))
            node_map[node.uuid] = node

        for conn_data in data.get("connections", []):
            start_node = node_map.get(conn_data['start_node_uuid'])
            end_node = node_map.get(conn_data['end_node_uuid'])
            if start_node and end_node:
                start_pin = next((p for p in start_node.pins if p.name == conn_data['start_pin_uuid']), None)
                end_pin = next((p for p in end_pin.pins if p.name == conn_data['end_pin_uuid']), None)
                if start_pin and end_pin:
                    self.create_connection(start_pin, end_pin)
        
        self.update()

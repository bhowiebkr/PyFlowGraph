# node_graph.py
# The QGraphicsScene that manages nodes, connections, and their interactions.
# Now includes a method to clear the graph for a new scene.

import uuid
import json
from PySide6.QtWidgets import QGraphicsScene, QApplication
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QKeyEvent, QColor
from node import Node
from reroute_node import RerouteNode
from connection import Connection
from pin import Pin


class NodeGraph(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(Qt.darkGray)
        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.nodes, self.connections = [], []
        self._drag_connection, self._drag_start_pin = None, None

    def clear_graph(self):
        """Removes all nodes and connections from the scene."""
        for node in list(self.nodes):
            self.remove_node(node)
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            for item in list(self.selectedItems()):
                if isinstance(item, (Node, RerouteNode)):
                    self.remove_node(item)
                elif isinstance(item, Connection):
                    self.remove_connection(item)
        else:
            super().keyPressEvent(event)

    def copy_selected(self):
        """Copies selected nodes, their connections, and the graph's requirements to the clipboard."""
        selected_nodes = [item for item in self.selectedItems() if isinstance(item, (Node, RerouteNode))]
        if not selected_nodes:
            return

        nodes_data = [node.serialize() for node in selected_nodes]
        connections_data = []
        selected_node_uuids = {node.uuid for node in selected_nodes}
        for conn in self.connections:
            if hasattr(conn.start_pin.node, "uuid") and hasattr(conn.end_pin.node, "uuid") and conn.start_pin.node.uuid in selected_node_uuids and conn.end_pin.node.uuid in selected_node_uuids:
                connections_data.append(conn.serialize())

        main_window = self.views()[0].window()
        requirements = main_window.current_requirements if hasattr(main_window, "current_requirements") else []

        clipboard_data = {"requirements": requirements, "nodes": nodes_data, "connections": connections_data}

        QApplication.clipboard().setText(json.dumps(clipboard_data, indent=4))
        print(f"Copied {len(nodes_data)} nodes to clipboard.")

    def paste(self):
        """Pastes nodes and connections from the clipboard."""
        clipboard_text = QApplication.clipboard().text()
        try:
            data = json.loads(clipboard_text)
            self.deserialize(data, self.views()[0].mapToScene(self.views()[0].viewport().rect().center()))
        except (json.JSONDecodeError, TypeError):
            print("Clipboard does not contain valid graph data.")

    def serialize(self):
        """Serializes all nodes and their connections."""
        nodes_data = [node.serialize() for node in self.nodes]
        connections_data = [conn.serialize() for conn in self.connections if conn.serialize()]
        return {"nodes": nodes_data, "connections": connections_data}

    def deserialize(self, data, offset=QPointF(0, 0)):
        """Deserializes graph data, creating all nodes and applying custom properties."""
        if not data:
            return
        if offset == QPointF(0, 0):
            self.clear_graph()

        uuid_to_node_map = {}
        nodes_to_update = []

        for node_data in data.get("nodes", []):
            original_pos = QPointF(node_data["pos"][0], node_data["pos"][1])
            new_pos = original_pos + offset
            is_reroute = node_data.get("is_reroute", False)
            if is_reroute:
                node = self.create_node("", pos=(new_pos.x(), new_pos.y()), is_reroute=True)
            else:
                node = self.create_node(node_data["title"], pos=(new_pos.x(), new_pos.y()))
                if "size" in node_data:
                    node.width, node.height = node_data["size"]
                node.set_code(node_data.get("code", ""))
                node.set_gui_code(node_data.get("gui_code", ""))
                node.set_gui_get_values_code(node_data.get("gui_get_values_code", ""))
                colors = node_data.get("colors", {})
                if "title" in colors:
                    node.color_title_bar = QColor(colors["title"])
                if "body" in colors:
                    node.color_body = QColor(colors["body"])
                node.update()
                node.apply_gui_state(node_data.get("gui_state", {}))
                nodes_to_update.append(node)

            old_uuid = node_data["uuid"]
            node.uuid = str(uuid.uuid4()) if offset != QPointF(0, 0) else old_uuid
            uuid_to_node_map[old_uuid] = node

        for conn_data in data.get("connections", []):
            start_node = uuid_to_node_map.get(conn_data["start_node_uuid"])
            end_node = uuid_to_node_map.get(conn_data["end_node_uuid"])
            if start_node and end_node:
                start_pin = start_node.get_pin_by_name(conn_data["start_pin_name"])
                end_pin = end_node.get_pin_by_name(conn_data["end_pin_name"])
                if start_pin and end_pin:
                    self.create_connection(start_pin, end_pin)

        for node in nodes_to_update:
            node.fit_size_to_content()
        self.update()

    # --- Other methods remain the same ---
    def create_node(self, title, pos=(0, 0), is_reroute=False):
        node = RerouteNode() if is_reroute else Node(title)
        node.setPos(pos[0], pos[1])
        self.addItem(node)
        self.nodes.append(node)
        return node

    def remove_node(self, node):
        if hasattr(node, "pins"):
            for pin in list(node.pins):
                if hasattr(node, "remove_pin"):
                    node.remove_pin(pin)
                else:
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
            if isinstance(end_pin.node, RerouteNode):
                end_pin.node.update_color()
            return conn
        return None

    def remove_connection(self, connection):
        end_pin = connection.end_pin
        connection.remove()
        if connection in self.connections:
            self.connections.remove(connection)
        self.removeItem(connection)
        if end_pin and isinstance(end_pin.node, RerouteNode):
            end_pin.node.update_color()

    def create_reroute_node_on_connection(self, connection, position):
        start_pin, end_pin = connection.start_pin, connection.end_pin
        self.remove_connection(connection)
        reroute_node = self.create_node("", pos=(position.x(), position.y()), is_reroute=True)
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
        if self._drag_connection is None or self._drag_start_pin is None:
            return
        target_item = self.itemAt(end_pos, self.views()[0].transform())
        self.removeItem(self._drag_connection)
        self._drag_connection = None
        if isinstance(target_item, Pin):
            end_pin = target_item
            if end_pin.direction == "input" and end_pin.connections:
                self.remove_connection(end_pin.connections[0])
            self.create_connection(self._drag_start_pin, end_pin)
        self._drag_start_pin = None

    def mouseMoveEvent(self, event):
        if self._drag_connection:
            self.update_drag_connection(event.scenePos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_connection:
            self.end_drag_connection(event.scenePos())
        super().mouseReleaseEvent(event)

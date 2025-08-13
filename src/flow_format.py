# flow_format.py
# Handler for .md file format based on the FlowSpec specification

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from markdown_it import MarkdownIt


class FlowFormatHandler:
    """Handles conversion between JSON graph format and .md markdown format."""
    
    def __init__(self):
        self.md = MarkdownIt()
    
    def json_to_flow(self, json_data: Dict[str, Any], title: str = "Untitled Graph", 
                     description: str = "") -> str:
        """Convert JSON graph data to .md markdown format."""
        
        flow_content = f"# {title}\n\n"
        if description:
            flow_content += f"{description}\n\n"
        
        # Add nodes
        for node in json_data.get("nodes", []):
            flow_content += self._node_to_flow(node)
            flow_content += "\n"
        
        # Add connections
        flow_content += "## Connections\n\n"
        flow_content += "```json\n"
        flow_content += json.dumps(json_data.get("connections", []), indent=2)
        flow_content += "\n```\n"
        
        return flow_content
    
    def _node_to_flow(self, node: Dict[str, Any]) -> str:
        """Convert a single node to .md format."""
        uuid = node.get("uuid", "")
        title = node.get("title", "")
        
        content = f"## Node: {title} (ID: {uuid})\n\n"
        
        # Add description if available (could be extracted from comments in code)
        content += "Node description goes here.\n\n"
        
        # Metadata section
        metadata = {
            "uuid": uuid,
            "title": title,
            "pos": node.get("pos", [0, 0]),
            "size": node.get("size", [200, 150])
        }
        
        # Include is_reroute flag if this is a reroute node
        if node.get("is_reroute", False):
            metadata["is_reroute"] = True
        
        # Always include colors (even if empty) for consistency
        metadata["colors"] = node.get("colors", {})
        
        # Always include gui_state (even if empty) for consistency
        metadata["gui_state"] = node.get("gui_state", {})
        
        content += "### Metadata\n\n"
        content += "```json\n"
        content += json.dumps(metadata, indent=2)
        content += "\n```\n\n"
        
        # Logic section
        content += "### Logic\n\n"
        content += "```python\n"
        content += node.get("code", "")
        content += "\n```\n\n"
        
        # GUI Definition (include even if empty for consistency)
        gui_code = node.get("gui_code", "")
        if gui_code.strip():  # Only include section if there's actual content
            content += "### GUI Definition\n\n"
            content += "```python\n"
            content += gui_code
            content += "\n```\n\n"
        
        # GUI State Handler (include even if empty for consistency) 
        gui_get_values_code = node.get("gui_get_values_code", "")
        if gui_get_values_code.strip():  # Only include section if there's actual content
            content += "### GUI State Handler\n\n"
            content += "```python\n"
            content += gui_get_values_code
            content += "\n```\n\n"
        
        return content
    
    def flow_to_json(self, flow_content: str) -> Dict[str, Any]:
        """Convert .md markdown content to JSON graph format."""
        
        tokens = self.md.parse(flow_content)
        
        graph_data = {
            "nodes": [],
            "connections": [],
            "requirements": []
        }
        
        current_node = None
        current_section = None
        current_component = None
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == "heading_open":
                level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
                
                # Get the heading content
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    heading_text = tokens[i + 1].content
                    
                    if level == 1:
                        # Graph title - we can ignore this for JSON conversion
                        pass
                    elif level == 2:
                        if heading_text == "Connections":
                            current_section = "connections"
                            current_node = None
                        else:
                            # Node header: "Node: Title (ID: uuid)"
                            match = re.match(r"Node:\s*(.*?)\s*\(ID:\s*(.*?)\)", heading_text)
                            if match:
                                title, uuid = match.groups()
                                current_node = {
                                    "uuid": uuid.strip(),
                                    "title": title.strip(),
                                    "pos": [0, 0],
                                    "size": [200, 150],
                                    "code": "",
                                    "gui_code": "",
                                    "gui_get_values_code": "",
                                    "gui_state": {},
                                    "colors": {},
                                    "is_reroute": False  # Default to False, will be updated from metadata
                                }
                                graph_data["nodes"].append(current_node)
                                current_section = "node"
                    elif level == 3 and current_node is not None:
                        current_component = heading_text.lower()
            
            elif token.type == "fence" and token.info:
                language = token.info.strip()
                content = token.content.strip()
                
                if current_section == "connections" and language == "json":
                    try:
                        graph_data["connections"] = json.loads(content)
                    except json.JSONDecodeError:
                        pass  # Skip invalid JSON
                
                elif current_section == "node" and current_node is not None:
                    if current_component == "metadata" and language == "json":
                        try:
                            metadata = json.loads(content)
                            current_node.update({
                                "pos": metadata.get("pos", [0, 0]),
                                "size": metadata.get("size", [200, 150]),
                                "colors": metadata.get("colors", {}),
                                "gui_state": metadata.get("gui_state", {}),
                                "is_reroute": metadata.get("is_reroute", False)
                            })
                        except json.JSONDecodeError:
                            pass
                    
                    elif current_component == "logic" and language == "python":
                        current_node["code"] = content
                    
                    elif current_component == "gui definition" and language == "python":
                        current_node["gui_code"] = content
                    
                    elif current_component == "gui state handler" and language == "python":
                        current_node["gui_get_values_code"] = content
            
            i += 1
        
        return graph_data


def load_flow_file(file_path: str) -> Dict[str, Any]:
    """Load a .md file and return JSON graph data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    handler = FlowFormatHandler()
    return handler.flow_to_json(content)


def save_flow_file(file_path: str, json_data: Dict[str, Any], 
                   title: str = "Untitled Graph", description: str = "") -> None:
    """Save JSON graph data as a .md file."""
    handler = FlowFormatHandler()
    content = handler.json_to_flow(json_data, title, description)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def extract_title_from_filename(file_path: str) -> str:
    """Extract a title from a file path."""
    import os
    name = os.path.splitext(os.path.basename(file_path))[0]
    # Convert underscores to spaces and title case
    return name.replace('_', ' ').title()
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
    
    def data_to_markdown(self, graph_data: Dict[str, Any], title: str = "Untitled Graph", 
                        description: str = "") -> str:
        """Convert graph data to .md markdown format."""
        
        flow_content = f"# {title}\n\n"
        if description:
            flow_content += f"{description}\n\n"
        
        # Add nodes
        for node in graph_data.get("nodes", []):
            flow_content += self._node_to_flow(node)
            flow_content += "\n"
        
        # Add connections
        flow_content += "## Connections\n\n"
        flow_content += "```json\n"
        flow_content += json.dumps(graph_data.get("connections", []), indent=2)
        flow_content += "\n```\n"
        
        return flow_content
    
    def _node_to_flow(self, node: Dict[str, Any]) -> str:
        """Convert a single node to .md format."""
        uuid = node.get("uuid", "")
        title = node.get("title", "")
        description = node.get("description", "")
        
        content = f"## Node: {title} (ID: {uuid})\n\n"
        
        # Add description if available
        if description.strip():
            cleaned_description = self._clean_description(description)
            content += f"{cleaned_description}\n\n"
        
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
    
    def markdown_to_data(self, flow_content: str) -> Dict[str, Any]:
        """Convert .md markdown content to graph data format."""
        
        tokens = self.md.parse(flow_content)
        
        graph_data = {
            "graph_title": "Untitled Graph",
            "graph_description": "",
            "nodes": [],
            "connections": [],
            "requirements": []
        }
        
        current_node = None
        current_section = None
        current_component = None
        node_description_tokens = []  # Collect description tokens between node header and metadata
        graph_description_tokens = []  # Collect description tokens after H1 and before first H2
        skip_next_inline = False  # Skip the inline token that contains heading text
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == "heading_open":
                level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
                
                # Get the heading content
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    heading_text = tokens[i + 1].content
                    
                    if level == 1:
                        # Graph title - capture it
                        graph_data["graph_title"] = heading_text
                        current_section = "graph_description"
                        skip_next_inline = True  # Skip this heading's inline token
                    elif level == 2:
                        # Process any collected graph description tokens before moving to nodes
                        if current_section == "graph_description" and graph_description_tokens:
                            description_text = self._extract_text_from_tokens(graph_description_tokens)
                            graph_data["graph_description"] = self._clean_description(description_text)
                            graph_description_tokens = []
                        
                        # Process any collected description tokens from previous node
                        if node_description_tokens and current_node:
                            description_text = self._extract_text_from_tokens(node_description_tokens)
                            current_node["description"] = self._clean_description(description_text)
                            node_description_tokens = []
                        
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
                                    "description": "",  # Will be populated from description tokens
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
                                current_component = None  # Reset component for new node
                                node_description_tokens = []  # Reset description tokens for new node
                    elif level == 3 and current_node is not None:
                        # Process any collected description tokens before moving to component
                        if node_description_tokens and current_node:
                            description_text = self._extract_text_from_tokens(node_description_tokens)
                            current_node["description"] = self._clean_description(description_text)
                            node_description_tokens = []
                        
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
            
            elif current_section == "graph_description":
                # We're collecting graph description tokens (after H1, before first H2)
                if token.type in ["paragraph_open", "paragraph_close"]:
                    graph_description_tokens.append(token)
                elif token.type == "inline":
                    if skip_next_inline:
                        skip_next_inline = False  # Reset the flag, don't collect this token
                    else:
                        graph_description_tokens.append(token)
            
            elif current_section == "node" and current_component is None and current_node is not None:
                # We're in a node section but haven't hit a component yet - collect description tokens
                # Skip heading-related tokens to avoid capturing the node header
                if token.type in ["paragraph_open", "paragraph_close"]:
                    node_description_tokens.append(token)
                elif token.type == "inline" and not token.content.startswith("Node:"):
                    node_description_tokens.append(token)
            
            i += 1
        
        # Process any remaining description tokens at the end of the document
        if graph_description_tokens and current_section == "graph_description":
            description_text = self._extract_text_from_tokens(graph_description_tokens)
            graph_data["graph_description"] = self._clean_description(description_text)
        
        if node_description_tokens and current_node:
            description_text = self._extract_text_from_tokens(node_description_tokens)
            current_node["description"] = self._clean_description(description_text)
        
        return graph_data
    
    def _extract_text_from_tokens(self, tokens):
        """Extract plain text from markdown tokens, preserving paragraph breaks."""
        paragraphs = []
        current_paragraph = []
        
        for token in tokens:
            if token.type == "paragraph_open":
                current_paragraph = []
            elif token.type == "inline":
                current_paragraph.append(token.content)
            elif token.type == "paragraph_close":
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
        
        # Handle any remaining inline content not in paragraphs
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))
        
        return "\n\n".join(paragraphs)
    
    def _clean_description(self, description):
        """Clean description text by stripping whitespace and normalizing newlines."""
        if not description:
            return ""
        
        # Strip leading/trailing whitespace
        cleaned = description.strip()
        
        # Normalize multiple consecutive newlines to at most two (paragraph break)
        import re
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        
        return cleaned


def load_flow_file(file_path: str) -> Dict[str, Any]:
    """Load a .md file and return JSON graph data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    handler = FlowFormatHandler()
    return handler.markdown_to_data(content)


def save_flow_file(file_path: str, graph_data: Dict[str, Any], 
                   title: str = "Untitled Graph", description: str = "") -> None:
    """Save graph data as a .md file."""
    handler = FlowFormatHandler()
    content = handler.data_to_markdown(graph_data, title, description)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def extract_title_from_filename(file_path: str) -> str:
    """Extract a title from a file path."""
    import os
    name = os.path.splitext(os.path.basename(file_path))[0]
    # Convert underscores to spaces and title case
    return name.replace('_', ' ').title()
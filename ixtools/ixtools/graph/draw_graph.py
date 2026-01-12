"""
Draw a graph using Graphviz with nodes and edges.
"""

from typing import Dict, Any, List, Optional, Literal
import os

from ..constants import SUCCESS_KEY, ERROR_KEY, RESULT_KEY


def _darken_colour(hex_colour: str, factor: float = 0.7) -> str:
    """
    Darken a hex colour by a given factor.
    
    Args:
        hex_colour: Hex colour string (e.g., "#374151" or "#1F3A8A").
        factor: Darkening factor between 0 and 1 (default: 0.7).
            Lower values make it darker.
    
    Returns:
        Darkened hex colour string.
    """
    # Remove # if present
    hex_colour = hex_colour.lstrip("#")
    
    # Handle named colours (like "black", "lightblue") - return as is
    if not all(c in "0123456789ABCDEFabcdef" for c in hex_colour):
        return hex_colour
    
    # Convert to RGB
    r = int(hex_colour[0:2], 16)
    g = int(hex_colour[2:4], 16)
    b = int(hex_colour[4:6], 16)
    
    # Darken each component
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"


def draw_graph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    output_path: str,
    direction: Literal["LR", "TB", "BT", "RL"] = "LR",
    format: Literal["png", "pdf", "svg"] = "png",
    view: bool = False,
) -> Dict[str, Any]:
    """
    Draw a graph using Graphviz with specified nodes and edges.
    
    Creates a visually appealing graph visualization with styled nodes and edges.
    Nodes and edges can have custom labels and colours.
    
    Args:
        nodes: List of node dictionaries, each containing:
            - id: Unique identifier for the node (string, required)
            - label: Label to display on the node (string, optional, defaults to id)
            - colour: Fill colour of the node (string, optional, defaults to "lightblue")
        edges: List of edge dictionaries, each containing:
            - source_id: ID of the source node (string, required)
            - target_id: ID of the target node (string, required)
            - label: Label to display on the edge (string, optional, defaults to empty)
            - colour: Colour of the edge (string, optional, defaults to "black")
        output_path: Path where the graph image will be saved (without extension).
            The format extension will be added automatically.
        direction: Graph layout direction:
            - "LR": Left to right (default)
            - "TB": Top to bottom
            - "BT": Bottom to top
            - "RL": Right to left
        format: Output image format: "png", "pdf", or "svg" (default: "png").
        view: If True, opens the rendered graph in the default viewer (default: False).
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if the operation was successful.
            - result: Dictionary containing:
                - path: Full path to the generated graph file.
            - error: Error message if operation failed (None if successful).
    """
    # Lazy import for performance (graphviz is a heavy library)
    from graphviz import Digraph
    
    try:
        # Validate nodes
        if not nodes:
            return {
                SUCCESS_KEY: False,
                RESULT_KEY: None,
                ERROR_KEY: "At least one node is required",
            }
        
        # Validate node structure and collect node IDs
        node_ids = set()
        for node in nodes:
            if "id" not in node:
                return {
                    SUCCESS_KEY: False,
                    RESULT_KEY: None,
                    ERROR_KEY: "Each node must have an 'id' field",
                }
            node_id = node["id"]
            if node_id in node_ids:
                return {
                    SUCCESS_KEY: False,
                    RESULT_KEY: None,
                    ERROR_KEY: f"Duplicate node id: {node_id}",
                }
            node_ids.add(node_id)
        
        # Validate edges
        for edge in edges:
            if "source_id" not in edge or "target_id" not in edge:
                return {
                    SUCCESS_KEY: False,
                    RESULT_KEY: None,
                    ERROR_KEY: "Each edge must have 'source_id' and 'target_id' fields",
                }
            if edge["source_id"] not in node_ids:
                return {
                    SUCCESS_KEY: False,
                    RESULT_KEY: None,
                    ERROR_KEY: f"Edge source_id '{edge['source_id']}' not found in nodes",
                }
            if edge["target_id"] not in node_ids:
                return {
                    SUCCESS_KEY: False,
                    RESULT_KEY: None,
                    ERROR_KEY: f"Edge target_id '{edge['target_id']}' not found in nodes",
                }
        
        # Create graph
        dot = Digraph(format=format)
        dot.attr(rankdir=direction)
        
        # Style the graph for better appearance
        dot.attr("node", style="rounded,filled", shape="box", fontname="Arial")
        dot.attr("edge", fontname="Arial")
        
        # Add nodes with styling
        for node in nodes:
            node_id = node["id"]
            label = node.get("label", node_id)
            colour = node.get("colour", "lightblue")
            
            # Darken the colour for the border
            border_colour = _darken_colour(colour, factor=0.7)
            
            # Use filled style with rounded corners and darker border
            dot.node(
                node_id,
                label=label,
                style="rounded,filled",
                shape="box",
                fillcolor=colour,
                color=border_colour,
                fontcolor="black",
            )
        
        # Add edges with styling
        for edge in edges:
            source_id = edge["source_id"]
            target_id = edge["target_id"]
            label = edge.get("label", "")
            colour = edge.get("colour", "black")
            
            dot.edge(
                source_id,
                target_id,
                label=label,
                color=colour,
            )
        
        # Render the graph
        # Remove extension from output_path if present, as graphviz adds it
        output_path_no_ext = os.path.splitext(output_path)[0]
        rendered_path = dot.render(output_path_no_ext, view=view, cleanup=True)
        
        return {
            SUCCESS_KEY: True,
            RESULT_KEY: {
                "path": rendered_path,
            },
            ERROR_KEY: None,
        }
        
    except Exception as e:
        return {
            SUCCESS_KEY: False,
            RESULT_KEY: None,
            ERROR_KEY: f"Error drawing graph: {str(e)}",
        }

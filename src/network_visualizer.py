"""
Network visualizer component for Supply Chain Visibility application.

This module provides the NetworkVisualizer class that handles visualization
of the supply chain network topology using plotly.
"""

from typing import List, Optional
from dataclasses import dataclass
import plotly.graph_objects as go

from src.models import Node, Edge, SupplyChainData, NodeStatus


@dataclass
class NodeDetails:
    """
    Detailed information for a specific network node.
    
    Attributes:
        node: The node object
        connected_shipment_ids: List of shipment IDs passing through this node
        incoming_edges: Number of incoming edges
        outgoing_edges: Number of outgoing edges
    """
    node: Node
    connected_shipment_ids: List[str]
    incoming_edges: int
    outgoing_edges: int


class NetworkVisualizer:
    """
    Visualizes supply chain network topology.
    
    This class provides methods to render network diagrams, get node details,
    and display nodes on geographic maps using plotly.
    """
    
    # Color mapping for node statuses
    STATUS_COLORS = {
        NodeStatus.NORMAL: 'green',
        NodeStatus.CONGESTED: 'orange',
        NodeStatus.DISRUPTED: 'red'
    }
    
    def __init__(self, data: SupplyChainData):
        """
        Initialize the network visualizer with supply chain data.
        
        Args:
            data: SupplyChainData object containing all supply chain information
        """
        self.data = data
    
    def render_network(self, nodes: List[Node], edges: List[Edge]) -> go.Figure:
        """
        Render network diagram with nodes and connections.
        
        Creates an interactive network visualization using plotly with nodes
        positioned in a layout and edges connecting them. Nodes are color-coded
        by their status.
        
        Args:
            nodes: List of Node objects to visualize
            edges: List of Edge objects representing connections
            
        Returns:
            Plotly Figure object containing the network visualization
        """
        if not nodes:
            # Return empty figure if no nodes
            fig = go.Figure()
            fig.update_layout(
                title="Supply Chain Network (No Data)",
                showlegend=False
            )
            return fig
        
        # Create a simple layout for nodes (circular arrangement)
        import math
        n = len(nodes)
        node_positions = {}
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n
            x = math.cos(angle)
            y = math.sin(angle)
            node_positions[node.id] = (x, y)
        
        # Create edge traces
        edge_traces = []
        for edge in edges:
            if edge.source_node_id in node_positions and edge.target_node_id in node_positions:
                x0, y0 = node_positions[edge.source_node_id]
                x1, y1 = node_positions[edge.target_node_id]
                
                edge_trace = go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=1, color='gray'),
                    hoverinfo='none',
                    showlegend=False
                )
                edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_colors = []
        node_text = []
        
        for node in nodes:
            if node.id in node_positions:
                x, y = node_positions[node.id]
                node_x.append(x)
                node_y.append(y)
                node_colors.append(self.STATUS_COLORS.get(node.status, 'gray'))
                node_text.append(f"{node.name}<br>Type: {node.type.value}<br>Status: {node.status.value}")
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            marker=dict(
                size=20,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            text=[node.name for node in nodes if node.id in node_positions],
            textposition='top center',
            hovertext=node_text,
            hoverinfo='text',
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title="Supply Chain Network",
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        return fig
    
    def get_node_details(self, node_id: str) -> NodeDetails:
        """
        Get details for a specific network node.
        
        Retrieves the node and enriches it with information about connected
        shipments and edge counts.
        
        Args:
            node_id: Unique identifier of the node
            
        Returns:
            NodeDetails object containing the node and related information
            
        Raises:
            ValueError: If node with the given ID is not found
        """
        # Find the node
        node = next((n for n in self.data.nodes if n.id == node_id), None)
        if node is None:
            raise ValueError(f"Node not found: {node_id}")
        
        # Find connected shipments
        connected_shipment_ids = set()
        incoming_edges = 0
        outgoing_edges = 0
        
        for edge in self.data.edges:
            if edge.source_node_id == node_id:
                outgoing_edges += 1
                connected_shipment_ids.update(edge.shipment_ids)
            if edge.target_node_id == node_id:
                incoming_edges += 1
                connected_shipment_ids.update(edge.shipment_ids)
        
        return NodeDetails(
            node=node,
            connected_shipment_ids=list(connected_shipment_ids),
            incoming_edges=incoming_edges,
            outgoing_edges=outgoing_edges
        )
    
    def render_geographic_map(self, nodes: List[Node]) -> go.Figure:
        """
        Render nodes on interactive geographic map.
        
        Creates a map visualization showing nodes with valid geographic coordinates.
        Nodes without coordinates are excluded from the map.
        
        Args:
            nodes: List of Node objects to display on the map
            
        Returns:
            Plotly Figure object containing the geographic map visualization
        """
        # Filter nodes with valid coordinates
        geo_nodes = [
            node for node in nodes
            if node.latitude is not None and node.longitude is not None
        ]
        
        if not geo_nodes:
            # Return empty figure if no nodes have coordinates
            fig = go.Figure()
            fig.update_layout(
                title="Geographic Map (No Nodes with Coordinates)",
                showlegend=False
            )
            return fig
        
        # Extract data for map
        lats = [node.latitude for node in geo_nodes]
        lons = [node.longitude for node in geo_nodes]
        colors = [self.STATUS_COLORS.get(node.status, 'gray') for node in geo_nodes]
        texts = [
            f"{node.name}<br>Type: {node.type.value}<br>Status: {node.status.value}<br>Location: {node.location}"
            for node in geo_nodes
        ]
        
        # Create map trace
        map_trace = go.Scattergeo(
            lon=lons,
            lat=lats,
            mode='markers',
            marker=dict(
                size=10,
                color=colors,
                line=dict(width=1, color='white')
            ),
            text=[node.name for node in geo_nodes],
            hovertext=texts,
            hoverinfo='text'
        )
        
        # Create figure
        fig = go.Figure(data=[map_trace])
        
        fig.update_layout(
            title="Supply Chain Network - Geographic View",
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
            )
        )
        
        return fig

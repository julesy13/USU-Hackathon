"""Network visualization page for Supply Chain Visibility application"""

import streamlit as st
from src.network_visualizer import NetworkVisualizer


def render_network_page():
    """Render the supply chain network visualization page"""
    st.title("🌐 Supply Chain Network")
    
    # Help section
    from pages.tooltip_utils import render_help_section
    render_help_section("Network")
    
    # Load data
    data = get_data()
    if data is None:
        st.error("❌ Failed to load network data")
        return
    
    visualizer = NetworkVisualizer()
    
    # View toggle
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Network Visualization")
    
    with col2:
        view_mode = st.selectbox(
            "View Mode",
            options=["Network Diagram", "Geographic Map"],
            help="Toggle between network diagram and geographic map view"
        )
    
    st.markdown("---")
    
    # Render appropriate view
    if view_mode == "Network Diagram":
        render_network_diagram(data, visualizer)
    else:
        render_geographic_map(data, visualizer)
    
    st.markdown("---")
    
    # Node selection and details
    render_node_details(data, visualizer)


def get_data():
    """Get data from session state"""
    if st.session_state.data_cache is None:
        try:
            data_service = st.session_state.data_service
            data = data_service.load_data("csv")
            st.session_state.data_cache = data
            return data
        except Exception:
            return None
    return st.session_state.data_cache


def render_network_diagram(data, visualizer):
    """Render network diagram visualization"""
    try:
        fig = visualizer.render_network(data.nodes, data.edges)
        
        # Add legend for node status colors
        st.markdown("""
        **Node Status Legend:**
        - 🟢 Normal: Operating normally
        - 🟡 Congested: High traffic or capacity issues
        - 🔴 Disrupted: Service disruption or outage
        """)
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Failed to render network diagram: {str(e)}")
        st.info("Please check that node and edge data is properly formatted")


def render_geographic_map(data, visualizer):
    """Render geographic map visualization"""
    try:
        # Check if nodes have geographic data
        nodes_with_coords = [n for n in data.nodes if n.latitude is not None and n.longitude is not None]
        
        if not nodes_with_coords:
            st.warning("⚠️ No geographic coordinates available for network nodes")
            st.info("Geographic map requires latitude and longitude data for nodes")
            return
        
        fig = visualizer.render_geographic_map(nodes_with_coords)
        
        # Add legend
        st.markdown("""
        **Node Status Legend:**
        - 🟢 Normal: Operating normally
        - 🟡 Congested: High traffic or capacity issues
        - 🔴 Disrupted: Service disruption or outage
        """)
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Failed to render geographic map: {str(e)}")


def render_node_details(data, visualizer):
    """Render node selection and detail display"""
    st.markdown("### Node Details")
    
    if not data.nodes:
        st.info("No network nodes available")
        return
    
    # Node selection
    node_names = {node.id: f"{node.name} ({node.type.value})" for node in data.nodes}
    selected_node_id = st.selectbox(
        "Select a node to view details",
        options=list(node_names.keys()),
        format_func=lambda x: node_names[x],
        help="Choose a network node to see detailed information and connected shipments"
    )
    
    if selected_node_id:
        try:
            node_details = visualizer.get_node_details(selected_node_id, data)
            render_node_detail_card(node_details, data)
        except Exception as e:
            st.error(f"Failed to load node details: {str(e)}")


def render_node_detail_card(node_details, data):
    """Render detailed information card for a node"""
    node = node_details.node
    
    with st.expander("🌐 Node Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Node ID:** {node.id}")
            st.markdown(f"**Name:** {node.name}")
            st.markdown(f"**Type:** {node.type.value.replace('_', ' ').title()}")
            st.markdown(f"**Location:** {node.location}")
        
        with col2:
            # Status with color indicator
            status_emoji = {
                "normal": "🟢",
                "congested": "🟡",
                "disrupted": "🔴"
            }
            emoji = status_emoji.get(node.status.value, "⚪")
            st.markdown(f"**Status:** {emoji} {node.status.value.title()}")
            
            if node.capacity:
                st.markdown(f"**Capacity:** {node.capacity}")
            
            if node.latitude and node.longitude:
                st.markdown(f"**Coordinates:** {node.latitude:.4f}, {node.longitude:.4f}")
        
        # Connected shipments
        if node_details.connected_shipment_ids:
            st.markdown("---")
            st.markdown(f"**Connected Shipments:** {len(node_details.connected_shipment_ids)}")
            
            # Show shipment details
            shipments = [s for s in data.shipments if s.id in node_details.connected_shipment_ids]
            if shipments:
                shipment_data = []
                for shipment in shipments[:10]:  # Limit to 10 for display
                    shipment_data.append(f"- {shipment.id}: {shipment.origin} → {shipment.destination} ({shipment.status.value})")
                
                st.markdown("\n".join(shipment_data))
                
                if len(node_details.connected_shipment_ids) > 10:
                    st.caption(f"... and {len(node_details.connected_shipment_ids) - 10} more")
        else:
            st.info("No shipments currently connected to this node")

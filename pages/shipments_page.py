"""Shipments page for Supply Chain Visibility application"""

import streamlit as st
import pandas as pd
from src.shipment_tracker import ShipmentTracker
from src.filter_engine import FilterEngine


def render_shipments_page():
    """Render the shipments tracking page"""
    st.title("🚚 Shipment Tracking")
    
    # Help section
    from pages.tooltip_utils import render_help_section
    render_help_section("Shipments")
    
    # Load data
    data = get_data()
    if data is None:
        st.error("❌ Failed to load shipment data")
        return
    
    tracker = ShipmentTracker(data)
    
    # Search and filter controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search shipments",
            placeholder="Search by ID, origin, or destination...",
            help="Search across shipment ID, origin, and destination fields"
        )
    
    with col2:
        status_filter = st.multiselect(
            "Filter by status",
            options=["pending", "in_transit", "delayed", "delivered"],
            default=None,
            help="Filter shipments by their current status"
        )
    
    # Apply search
    if search_query:
        shipments = tracker.search_shipments(search_query, "all")
    else:
        shipments = tracker.list_shipments(st.session_state.filters)
    
    # Apply status filter
    if status_filter:
        shipments = [s for s in shipments if s.status.value in status_filter]
    
    # Display shipments by status category
    st.markdown("---")
    render_shipments_by_status(shipments)
    
    st.markdown("---")
    
    # Display shipments table
    render_shipments_table(shipments)
    
    # Export functionality
    if shipments:
        st.markdown("---")
        st.markdown("### Export Data")
        from pages.export_utils import render_export_buttons
        
        # Convert shipments to DataFrame for export
        df_export = pd.DataFrame([{
            "ID": s.id,
            "Origin": s.origin,
            "Destination": s.destination,
            "Current Location": s.current_location,
            "Status": s.status.value,
            "Estimated Delivery": s.estimated_delivery.strftime("%Y-%m-%d %H:%M") if s.estimated_delivery else "",
            "Actual Delivery": s.actual_delivery.strftime("%Y-%m-%d %H:%M") if s.actual_delivery else "",
            "Supplier ID": s.supplier_id,
            "Items": ", ".join(s.items) if s.items else ""
        } for s in shipments])
        
        render_export_buttons(df_export, "shipments")


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


def render_shipments_by_status(shipments):
    """Render shipment counts by status category"""
    st.markdown("### Shipments by Status")
    
    # Categorize shipments
    pending = [s for s in shipments if s.status.value == "pending"]
    in_transit = [s for s in shipments if s.status.value == "in_transit"]
    delayed = [s for s in shipments if s.status.value == "delayed"]
    delivered = [s for s in shipments if s.status.value == "delivered"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pending", len(pending))
    with col2:
        st.metric("In Transit", len(in_transit))
    with col3:
        st.metric("Delayed", len(delayed))
    with col4:
        st.metric("Delivered", len(delivered))


def render_shipments_table(shipments):
    """Render shipments data table with detail view"""
    st.markdown("### Shipment Details")
    
    if not shipments:
        st.info("No shipments found matching the current filters")
        return
    
    # Convert to DataFrame for display
    df_data = []
    for shipment in shipments:
        df_data.append({
            "ID": shipment.id,
            "Origin": shipment.origin,
            "Destination": shipment.destination,
            "Current Location": shipment.current_location,
            "Status": shipment.status.value.replace("_", " ").title(),
            "Est. Delivery": shipment.estimated_delivery.strftime("%Y-%m-%d %H:%M") if shipment.estimated_delivery else "N/A",
            "Supplier": shipment.supplier_id
        })
    
    df = pd.DataFrame(df_data)
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Shipment detail view
    st.markdown("---")
    st.markdown("### View Shipment Details")
    
    shipment_ids = [s.id for s in shipments]
    selected_id = st.selectbox(
        "Select a shipment to view details",
        options=shipment_ids,
        help="Choose a shipment to see detailed information"
    )
    
    if selected_id:
        selected_shipment = next((s for s in shipments if s.id == selected_id), None)
        if selected_shipment:
            render_shipment_detail(selected_shipment)


def render_shipment_detail(shipment):
    """Render detailed view of a single shipment"""
    with st.expander("📦 Shipment Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Shipment ID:** {shipment.id}")
            st.markdown(f"**Origin:** {shipment.origin}")
            st.markdown(f"**Destination:** {shipment.destination}")
            st.markdown(f"**Current Location:** {shipment.current_location}")
        
        with col2:
            status_emoji = {
                "pending": "⏳",
                "in_transit": "🚚",
                "delayed": "⚠️",
                "delivered": "✅"
            }
            emoji = status_emoji.get(shipment.status.value, "📦")
            st.markdown(f"**Status:** {emoji} {shipment.status.value.replace('_', ' ').title()}")
            st.markdown(f"**Estimated Delivery:** {shipment.estimated_delivery.strftime('%Y-%m-%d %H:%M')}")
            if shipment.actual_delivery:
                st.markdown(f"**Actual Delivery:** {shipment.actual_delivery.strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**Supplier ID:** {shipment.supplier_id}")
        
        if shipment.items:
            st.markdown(f"**Items:** {', '.join(shipment.items)}")

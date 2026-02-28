"""Inventory page for Supply Chain Visibility application"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.inventory_monitor import InventoryMonitor


def render_inventory_page():
    """Render the inventory monitoring page"""
    st.title("📦 Inventory Management")
    
    # Help section
    from pages.tooltip_utils import render_help_section
    render_help_section("Inventory")
    
    # Load data
    data = get_data()
    if data is None:
        st.error("❌ Failed to load inventory data")
        return
    
    monitor = InventoryMonitor(data)
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        locations = list(set([item.location for item in data.inventory]))
        location_filter = st.multiselect(
            "Filter by location",
            options=locations,
            default=None,
            help="Filter inventory by warehouse or storage location"
        )
    
    with col2:
        categories = list(set([item.category for item in data.inventory]))
        category_filter = st.multiselect(
            "Filter by category",
            options=categories,
            default=None,
            help="Filter inventory by product category"
        )
    
    with col3:
        stock_status = st.selectbox(
            "Stock status",
            options=["All", "Low Stock", "Normal"],
            help="Filter by stock level status"
        )
    
    # Apply filters
    from src.filter_engine import FilterCriteria
    filters = FilterCriteria(
        location=location_filter if location_filter else None,
        category=category_filter if category_filter else None
    )
    
    inventory_items = monitor.get_inventory_levels(filters)
    
    # Apply stock status filter
    if stock_status == "Low Stock":
        inventory_items = monitor.get_low_stock_items(threshold=None)
        if filters.location:
            inventory_items = [item for item in inventory_items if item.location in filters.location]
        if filters.category:
            inventory_items = [item for item in inventory_items if item.category in filters.category]
    
    # Display inventory overview
    st.markdown("---")
    render_inventory_overview(inventory_items, monitor)
    
    st.markdown("---")
    
    # Display inventory table
    render_inventory_table(inventory_items)
    
    st.markdown("---")
    
    # Display inventory trends
    if inventory_items:
        render_inventory_trends(inventory_items, monitor)
    
    # Export functionality
    if inventory_items:
        st.markdown("---")
        st.markdown("### Export Data")
        from pages.export_utils import render_export_buttons
        
        # Convert inventory to DataFrame for export
        df_export = pd.DataFrame([{
            "ID": item.id,
            "Name": item.name,
            "Category": item.category,
            "Location": item.location,
            "Quantity": item.quantity,
            "Unit": item.unit,
            "Reorder Point": item.reorder_point,
            "Low Stock": "Yes" if item.quantity < item.reorder_point else "No",
            "Last Updated": item.last_updated.strftime("%Y-%m-%d %H:%M")
        } for item in inventory_items])
        
        render_export_buttons(df_export, "inventory")


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


def render_inventory_overview(inventory_items, monitor):
    """Render inventory overview metrics"""
    st.markdown("### Inventory Overview")
    
    low_stock_items = [item for item in inventory_items if item.quantity < item.reorder_point]
    total_value = sum([item.quantity for item in inventory_items])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Items", len(inventory_items))
    with col2:
        st.metric("Low Stock", len(low_stock_items))
    with col3:
        st.metric("Total Units", f"{total_value:,.0f}")
    with col4:
        unique_locations = len(set([item.location for item in inventory_items]))
        st.metric("Locations", unique_locations)


def render_inventory_table(inventory_items):
    """Render inventory data table with low stock highlighting"""
    st.markdown("### Inventory Details")
    
    if not inventory_items:
        st.info("No inventory items found matching the current filters")
        return
    
    # Convert to DataFrame
    df_data = []
    for item in inventory_items:
        is_low_stock = item.quantity < item.reorder_point
        df_data.append({
            "ID": item.id,
            "Name": item.name,
            "Category": item.category,
            "Location": item.location,
            "Quantity": item.quantity,
            "Unit": item.unit,
            "Reorder Point": item.reorder_point,
            "Status": "🔴 Low Stock" if is_low_stock else "✅ Normal"
        })
    
    df = pd.DataFrame(df_data)
    
    # Display table with styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Item detail view
    st.markdown("---")
    st.markdown("### View Item Details")
    
    item_ids = [item.id for item in inventory_items]
    selected_id = st.selectbox(
        "Select an item to view details",
        options=item_ids,
        help="Choose an inventory item to see detailed information"
    )
    
    if selected_id:
        selected_item = next((item for item in inventory_items if item.id == selected_id), None)
        if selected_item:
            render_item_detail(selected_item)


def render_item_detail(item):
    """Render detailed view of a single inventory item"""
    with st.expander("📦 Item Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Item ID:** {item.id}")
            st.markdown(f"**Name:** {item.name}")
            st.markdown(f"**Category:** {item.category}")
            st.markdown(f"**Location:** {item.location}")
        
        with col2:
            st.markdown(f"**Quantity:** {item.quantity} {item.unit}")
            st.markdown(f"**Reorder Point:** {item.reorder_point} {item.unit}")
            
            is_low_stock = item.quantity < item.reorder_point
            if is_low_stock:
                st.error(f"⚠️ Low Stock - Below reorder point")
                shortage = item.reorder_point - item.quantity
                st.markdown(f"**Shortage:** {shortage} {item.unit}")
            else:
                st.success("✅ Stock level normal")
            
            st.markdown(f"**Last Updated:** {item.last_updated.strftime('%Y-%m-%d %H:%M')}")


def render_inventory_trends(inventory_items, monitor):
    """Render inventory trend charts"""
    st.markdown("### Inventory Trends")
    
    # Select item for trend analysis
    item_names = {item.id: item.name for item in inventory_items}
    selected_item_id = st.selectbox(
        "Select item for trend analysis",
        options=list(item_names.keys()),
        format_func=lambda x: f"{x} - {item_names[x]}",
        help="View historical inventory levels for the selected item"
    )
    
    if selected_item_id:
        try:
            # Get trend data (30 days)
            trend_data = monitor.get_inventory_trends(selected_item_id, days=30)
            
            if trend_data and len(trend_data.dates) > 0:
                # Create trend chart
                df_trend = pd.DataFrame({
                    "Date": trend_data.dates,
                    "Quantity": trend_data.values
                })
                
                fig = px.line(
                    df_trend,
                    x="Date",
                    y="Quantity",
                    title=f"Inventory Trend - {item_names[selected_item_id]}",
                    labels={"Quantity": "Quantity", "Date": "Date"}
                )
                
                # Add reorder point line
                selected_item = next((item for item in inventory_items if item.id == selected_item_id), None)
                if selected_item:
                    fig.add_hline(
                        y=selected_item.reorder_point,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Reorder Point"
                    )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No historical trend data available for this item")
        except Exception as e:
            st.warning(f"Unable to load trend data: {str(e)}")

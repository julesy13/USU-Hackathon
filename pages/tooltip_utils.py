"""Tooltip and help text utilities for Streamlit pages"""

import streamlit as st


# Tooltip definitions for metrics and calculations
TOOLTIPS = {
    # Dashboard metrics
    "total_shipments": "Total number of shipments currently tracked in the system",
    "in_transit": "Number of shipments currently being transported to their destination",
    "delayed": "Shipments that have exceeded their estimated delivery time",
    "low_stock": "Inventory items with quantity below their reorder point threshold",
    
    # Shipment metrics
    "shipment_status": "Current state of the shipment: Pending (not yet started), In Transit (actively moving), Delayed (behind schedule), or Delivered (completed)",
    "estimated_delivery": "Predicted date and time when the shipment will reach its destination",
    "current_location": "Most recent known position of the shipment in the supply chain",
    
    # Inventory metrics
    "reorder_point": "Minimum quantity threshold that triggers a reorder request to prevent stockouts",
    "low_stock_threshold": "Items are flagged as low stock when quantity falls below the reorder point",
    "inventory_trend": "Historical quantity levels over time, showing consumption patterns and restocking events",
    
    # Network metrics
    "node_status": "Operational state of the network node: Normal (functioning properly), Congested (high traffic), or Disrupted (service issues)",
    "node_capacity": "Maximum throughput or storage capacity of the network node",
    "connected_shipments": "Number of shipments currently routed through or stored at this node",
    
    # Alert metrics
    "alert_severity": "Priority level: Critical (immediate action required), High (urgent attention needed), Medium (monitor closely), Low (informational)",
    "alert_acknowledgment": "Marking an alert as acknowledged indicates it has been reviewed and action is being taken",
    
    # Supplier metrics
    "performance_score": "Composite metric (0-100) evaluating overall supplier reliability based on delivery, quality, and lead time",
    "on_time_delivery_rate": "Percentage of shipments delivered on or before the estimated delivery date",
    "quality_score": "Assessment (0-100) of product quality and defect rates from this supplier",
    "average_lead_time": "Mean number of days between order placement and delivery completion",
    "supplier_ranking": "Suppliers ordered by selected performance metric, with higher-ranked suppliers performing better",
    
    # Export functionality
    "export_csv": "Download current data view as a comma-separated values file compatible with Excel and other tools",
    "export_excel": "Download current data view as a formatted Excel workbook with preserved styling",
    
    # Refresh functionality
    "auto_refresh": "Automatically reload data from the source at the configured interval to show latest updates",
    "refresh_interval": "Time in seconds between automatic data refreshes (recommended: 60-300 seconds)",
    "manual_refresh": "Immediately reload data from the source, bypassing the automatic refresh schedule",
    
    # Filter functionality
    "date_range_filter": "Limit results to items within the specified start and end dates",
    "status_filter": "Show only items matching the selected status values",
    "location_filter": "Filter by warehouse, facility, or geographic location",
    "category_filter": "Filter by product category or classification",
    "search_query": "Find items containing the search text in relevant fields (ID, name, location, etc.)",
}


def show_tooltip(key: str, label: str = None):
    """
    Display an info icon with tooltip for a metric or field
    
    Args:
        key: Key to look up tooltip text in TOOLTIPS dictionary
        label: Optional label to display before the info icon
    """
    tooltip_text = TOOLTIPS.get(key, "No description available")
    
    if label:
        st.markdown(f"{label} ℹ️", help=tooltip_text)
    else:
        st.markdown("ℹ️", help=tooltip_text)


def get_tooltip(key: str) -> str:
    """
    Get tooltip text for a given key
    
    Args:
        key: Key to look up in TOOLTIPS dictionary
    
    Returns:
        Tooltip text string
    """
    return TOOLTIPS.get(key, "")


def add_metric_help(metric_name: str) -> str:
    """
    Get help text for st.metric() help parameter
    
    Args:
        metric_name: Name of the metric
    
    Returns:
        Help text string
    """
    return get_tooltip(metric_name)


def render_help_section(page_name: str):
    """
    Render a help section with explanations for the current page
    
    Args:
        page_name: Name of the page (Dashboard, Shipments, etc.)
    """
    help_content = {
        "Dashboard": """
        **Dashboard Overview**
        
        The dashboard provides a high-level view of your supply chain health:
        - **Total Shipments**: All active shipments being tracked
        - **In Transit**: Shipments currently moving to their destination
        - **Delayed**: Shipments behind schedule requiring attention
        - **Low Stock Items**: Inventory below reorder thresholds
        
        Active alerts are displayed by severity to help prioritize responses.
        """,
        
        "Shipments": """
        **Shipment Tracking**
        
        Track all shipments across your supply chain:
        - Use the search bar to find specific shipments by ID, origin, or destination
        - Filter by status to focus on pending, in-transit, delayed, or delivered shipments
        - Click on a shipment to view detailed information including route and timeline
        - Export data for reporting and analysis
        """,
        
        "Inventory": """
        **Inventory Management**
        
        Monitor stock levels across all locations:
        - Items below reorder point are highlighted in red
        - Filter by location and category to focus on specific areas
        - View 30-day trends to understand consumption patterns
        - Use the reorder point as a guide for restocking decisions
        """,
        
        "Network": """
        **Network Visualization**
        
        Visualize your supply chain network:
        - **Network Diagram**: Shows connections between nodes
        - **Geographic Map**: Displays nodes on an interactive map (requires coordinates)
        - Node colors indicate status: Green (normal), Yellow (congested), Red (disrupted)
        - Select a node to see connected shipments and details
        """,
        
        "Alerts": """
        **Alert Management**
        
        Monitor and respond to supply chain disruptions:
        - Alerts are generated automatically based on business rules
        - Filter by type (shipment delay, low stock, supplier performance) and severity
        - Acknowledge alerts to mark them as reviewed
        - Critical and high-priority alerts require immediate attention
        """,
        
        "Suppliers": """
        **Supplier Performance**
        
        Track and compare supplier performance:
        - **Performance Score**: Composite metric of overall reliability (0-100)
        - **On-Time Rate**: Percentage of shipments delivered on schedule
        - **Quality Score**: Assessment of product quality (0-100)
        - **Lead Time**: Average days from order to delivery
        - Compare multiple suppliers to inform sourcing decisions
        """
    }
    
    content = help_content.get(page_name, "")
    if content:
        with st.expander("ℹ️ Help & Information", expanded=False):
            st.markdown(content)


def add_calculation_explanation(calculation_name: str):
    """
    Display explanation of how a metric is calculated
    
    Args:
        calculation_name: Name of the calculation to explain
    """
    explanations = {
        "on_time_delivery_rate": """
        **On-Time Delivery Rate Calculation:**
        
        ```
        On-Time Rate = (Shipments Delivered On Time / Total Shipments) × 100
        ```
        
        A shipment is considered "on time" if the actual delivery date is on or before 
        the estimated delivery date. This metric is calculated over the past 90 days.
        """,
        
        "performance_score": """
        **Performance Score Calculation:**
        
        The performance score is a weighted composite of multiple factors:
        - On-time delivery rate (40%)
        - Quality score (30%)
        - Lead time performance (20%)
        - Communication and responsiveness (10%)
        
        Scores range from 0-100, with higher scores indicating better performance.
        """,
        
        "low_stock_detection": """
        **Low Stock Detection:**
        
        An item is flagged as low stock when:
        ```
        Current Quantity < Reorder Point
        ```
        
        The reorder point is set based on:
        - Average daily consumption rate
        - Lead time for restocking
        - Safety stock buffer
        """,
        
        "alert_generation": """
        **Alert Generation Rules:**
        
        Alerts are automatically generated when:
        - **Shipment Delay**: Actual time > Estimated delivery + threshold
        - **Low Stock**: Quantity < Reorder point
        - **Supplier Performance**: Performance score < acceptable threshold
        
        Alert severity is determined by the magnitude of the deviation from normal.
        """
    }
    
    explanation = explanations.get(calculation_name, "")
    if explanation:
        with st.expander("📊 How is this calculated?", expanded=False):
            st.markdown(explanation)

"""Dashboard page for Supply Chain Visibility application"""

import streamlit as st
from datetime import datetime
from src.dashboard import Dashboard
from src.alert_generator import AlertGenerator


def render_dashboard_page():
    """Render the dashboard page with key metrics and alerts"""
    st.title("📊 Supply Chain Dashboard")
    
    # Help section
    from pages.tooltip_utils import render_help_section
    render_help_section("Dashboard")
    
    # Data refresh controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### Overview")
    with col2:
        if st.session_state.last_refresh:
            st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            refresh_data()
    
    # Load data with loading indicator
    with st.spinner("Loading dashboard data..."):
        try:
            data = load_data()
            
            if data is None:
                st.error("❌ Failed to load data. Please check data source and try again.")
                if st.button("Retry"):
                    st.rerun()
                return
            
            # Render key metrics
            render_metrics(data)
            
            st.markdown("---")
            
            # Render active alerts
            render_alerts(data)
            
        except Exception as e:
            st.error(f"❌ Error loading dashboard: {str(e)}")
            if st.button("Retry"):
                st.rerun()


def load_data():
    """Load supply chain data from data service"""
    try:
        if st.session_state.data_cache is None:
            data_service = st.session_state.data_service
            data = data_service.load_data("csv")
            st.session_state.data_cache = data
            st.session_state.last_refresh = datetime.now()
        return st.session_state.data_cache
    except Exception as e:
        # Check if we have cached data to fall back to
        if st.session_state.data_cache:
            from pages.error_utils import handle_data_unavailable
            handle_data_unavailable()
            return st.session_state.data_cache
        else:
            from pages.error_utils import handle_data_load_error
            handle_data_load_error(e, retry_callback=lambda: load_data())
            return None


def refresh_data():
    """Refresh data from source"""
    try:
        data_service = st.session_state.data_service
        data = data_service.refresh_data("data")
        st.session_state.data_cache = data
        st.session_state.last_refresh = datetime.now()
        st.success("✅ Data refreshed successfully")
        st.rerun()
    except Exception as e:
        from pages.error_utils import show_transient_error
        show_transient_error(e, retry_callback=refresh_data)


def render_metrics(data):
    """Render key metrics cards"""
    dashboard = Dashboard(data)
    metrics = dashboard.get_metrics(data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Shipments",
            value=metrics.total_shipments,
            help="Total number of shipments in the system"
        )
    
    with col2:
        st.metric(
            label="In Transit",
            value=metrics.in_transit_count,
            help="Shipments currently in transit"
        )
    
    with col3:
        delayed_delta = f"-{metrics.delayed_count}" if metrics.delayed_count > 0 else "0"
        st.metric(
            label="Delayed",
            value=metrics.delayed_count,
            delta=delayed_delta,
            delta_color="inverse",
            help="Shipments delayed beyond estimated delivery"
        )
    
    with col4:
        low_stock_delta = f"-{metrics.low_stock_count}" if metrics.low_stock_count > 0 else "0"
        st.metric(
            label="Low Stock Items",
            value=metrics.low_stock_count,
            delta=low_stock_delta,
            delta_color="inverse",
            help="Inventory items below reorder point"
        )


def render_alerts(data):
    """Render active alerts section"""
    st.markdown("### ⚠️ Active Alerts")
    
    alert_generator = AlertGenerator()
    alerts = alert_generator.generate_alerts(data)
    
    # Filter to show only unacknowledged alerts
    active_alerts = [alert for alert in alerts if not alert.acknowledged]
    
    if not active_alerts:
        st.success("✅ No active alerts")
        return
    
    # Display alerts by severity
    critical_alerts = [a for a in active_alerts if a.severity.value == "critical"]
    high_alerts = [a for a in active_alerts if a.severity.value == "high"]
    medium_alerts = [a for a in active_alerts if a.severity.value == "medium"]
    low_alerts = [a for a in active_alerts if a.severity.value == "low"]
    
    if critical_alerts:
        with st.expander(f"🔴 Critical Alerts ({len(critical_alerts)})", expanded=True):
            for alert in critical_alerts:
                st.error(f"**{alert.type.value.replace('_', ' ').title()}**: {alert.message}")
    
    if high_alerts:
        with st.expander(f"🟠 High Priority Alerts ({len(high_alerts)})", expanded=True):
            for alert in high_alerts:
                st.warning(f"**{alert.type.value.replace('_', ' ').title()}**: {alert.message}")
    
    if medium_alerts:
        with st.expander(f"🟡 Medium Priority Alerts ({len(medium_alerts)})"):
            for alert in medium_alerts:
                st.info(f"**{alert.type.value.replace('_', ' ').title()}**: {alert.message}")
    
    if low_alerts:
        with st.expander(f"🟢 Low Priority Alerts ({len(low_alerts)})"):
            for alert in low_alerts:
                st.info(f"**{alert.type.value.replace('_', ' ').title()}**: {alert.message}")

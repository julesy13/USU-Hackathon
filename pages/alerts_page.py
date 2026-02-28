"""Alerts page for Supply Chain Visibility application"""

import streamlit as st
import pandas as pd
from src.alert_generator import AlertGenerator


def render_alerts_page():
    """Render the alerts management page"""
    st.title("⚠️ Supply Chain Alerts")
    
    # Help section
    from pages.tooltip_utils import render_help_section
    render_help_section("Alerts")
    
    # Load data
    data = get_data()
    if data is None:
        st.error("❌ Failed to load alert data")
        return
    
    alert_generator = AlertGenerator()
    alerts = alert_generator.generate_alerts(data)
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alert_type_filter = st.multiselect(
            "Filter by type",
            options=["shipment_delay", "low_stock", "supplier_performance"],
            default=None,
            format_func=lambda x: x.replace("_", " ").title(),
            help="Filter alerts by their type"
        )
    
    with col2:
        severity_filter = st.multiselect(
            "Filter by severity",
            options=["critical", "high", "medium", "low"],
            default=None,
            format_func=lambda x: x.title(),
            help="Filter alerts by severity level"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Alert status",
            options=["Active", "Acknowledged", "All"],
            help="Filter by acknowledgment status"
        )
    
    # Apply filters
    filtered_alerts = alerts
    
    if alert_type_filter:
        filtered_alerts = [a for a in filtered_alerts if a.type.value in alert_type_filter]
    
    if severity_filter:
        filtered_alerts = [a for a in filtered_alerts if a.severity.value in severity_filter]
    
    if status_filter == "Active":
        filtered_alerts = [a for a in filtered_alerts if not a.acknowledged]
    elif status_filter == "Acknowledged":
        filtered_alerts = [a for a in filtered_alerts if a.acknowledged]
    
    # Display alert summary
    st.markdown("---")
    render_alert_summary(filtered_alerts)
    
    st.markdown("---")
    
    # Display alerts by severity
    render_alerts_by_severity(filtered_alerts, alert_generator)
    
    # Export functionality
    if filtered_alerts:
        st.markdown("---")
        st.markdown("### Export Data")
        from pages.export_utils import render_export_buttons
        
        # Convert alerts to DataFrame for export
        df_export = pd.DataFrame([{
            "ID": alert.id,
            "Type": alert.type.value,
            "Severity": alert.severity.value,
            "Message": alert.message,
            "Entity ID": alert.entity_id,
            "Created At": alert.created_at.strftime("%Y-%m-%d %H:%M"),
            "Acknowledged": "Yes" if alert.acknowledged else "No",
            "Acknowledged At": alert.acknowledged_at.strftime("%Y-%m-%d %H:%M") if alert.acknowledged_at else ""
        } for alert in filtered_alerts])
        
        render_export_buttons(df_export, "alerts")


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


def render_alert_summary(alerts):
    """Render alert summary metrics"""
    st.markdown("### Alert Summary")
    
    active_alerts = [a for a in alerts if not a.acknowledged]
    critical_alerts = [a for a in alerts if a.severity.value == "critical" and not a.acknowledged]
    high_alerts = [a for a in alerts if a.severity.value == "high" and not a.acknowledged]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Alerts", len(alerts))
    with col2:
        st.metric("Active", len(active_alerts))
    with col3:
        st.metric("Critical", len(critical_alerts))
    with col4:
        st.metric("High Priority", len(high_alerts))


def render_alerts_by_severity(alerts, alert_generator):
    """Render alerts grouped by severity"""
    st.markdown("### Alert Details")
    
    if not alerts:
        st.success("✅ No alerts matching the current filters")
        return
    
    # Group by severity
    critical_alerts = [a for a in alerts if a.severity.value == "critical"]
    high_alerts = [a for a in alerts if a.severity.value == "high"]
    medium_alerts = [a for a in alerts if a.severity.value == "medium"]
    low_alerts = [a for a in alerts if a.severity.value == "low"]
    
    # Render each severity group
    if critical_alerts:
        render_alert_group("🔴 Critical Alerts", critical_alerts, alert_generator, "error")
    
    if high_alerts:
        render_alert_group("🟠 High Priority Alerts", high_alerts, alert_generator, "warning")
    
    if medium_alerts:
        render_alert_group("🟡 Medium Priority Alerts", medium_alerts, alert_generator, "info")
    
    if low_alerts:
        render_alert_group("🟢 Low Priority Alerts", low_alerts, alert_generator, "info")


def render_alert_group(title, alerts, alert_generator, message_type):
    """Render a group of alerts with the same severity"""
    with st.expander(f"{title} ({len(alerts)})", expanded=(message_type in ["error", "warning"])):
        for alert in alerts:
            render_alert_card(alert, alert_generator, message_type)


def render_alert_card(alert, alert_generator, message_type):
    """Render an individual alert card"""
    # Create container for alert
    container = st.container()
    
    with container:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Alert header
            alert_title = f"**{alert.type.value.replace('_', ' ').title()}**"
            if alert.acknowledged:
                alert_title += " ✓ Acknowledged"
            
            if message_type == "error":
                st.error(alert_title)
            elif message_type == "warning":
                st.warning(alert_title)
            else:
                st.info(alert_title)
            
            # Alert details
            st.markdown(f"{alert.message}")
            st.caption(f"Entity ID: {alert.entity_id} | Created: {alert.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            if alert.acknowledged and alert.acknowledged_at:
                st.caption(f"Acknowledged at: {alert.acknowledged_at.strftime('%Y-%m-%d %H:%M')}")
        
        with col2:
            # Acknowledge button
            if not alert.acknowledged:
                if st.button("Acknowledge", key=f"ack_{alert.id}", use_container_width=True):
                    try:
                        alert_generator.acknowledge_alert(alert.id)
                        st.success("Alert acknowledged")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to acknowledge: {str(e)}")
        
        st.markdown("---")

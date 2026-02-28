"""
Supply Chain Visibility Application

Main entry point for the Streamlit application.
"""

import streamlit as st
from src.data_access import DataAccessService


def init_session_state():
    """Initialize session state variables"""
    if 'data_service' not in st.session_state:
        st.session_state.data_service = DataAccessService()
    
    if 'filters' not in st.session_state:
        from src.filter_engine import FilterCriteria
        st.session_state.filters = FilterCriteria()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    if 'data_cache' not in st.session_state:
        st.session_state.data_cache = None
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    
    # Initialize refresh configuration
    from pages.refresh_utils import init_refresh_config
    init_refresh_config()


def render_sidebar():
    """Render sidebar navigation"""
    st.sidebar.title("📦 Supply Chain")
    st.sidebar.markdown("---")
    
    pages = [
        ("Dashboard", "📊"),
        ("Shipments", "🚚"),
        ("Inventory", "📦"),
        ("Network", "🌐"),
        ("Alerts", "⚠️"),
        ("Suppliers", "🏭")
    ]
    
    for page_name, icon in pages:
        if st.sidebar.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()
    
    # Render refresh controls
    from pages.refresh_utils import render_refresh_controls
    render_refresh_controls()
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Supply Chain Visibility v1.0")


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Supply Chain Visibility",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar navigation
    render_sidebar()
    
    # Route to appropriate page
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        from pages.dashboard_page import render_dashboard_page
        render_dashboard_page()
    elif current_page == "Shipments":
        from pages.shipments_page import render_shipments_page
        render_shipments_page()
    elif current_page == "Inventory":
        from pages.inventory_page import render_inventory_page
        render_inventory_page()
    elif current_page == "Network":
        from pages.network_page import render_network_page
        render_network_page()
    elif current_page == "Alerts":
        from pages.alerts_page import render_alerts_page
        render_alerts_page()
    elif current_page == "Suppliers":
        from pages.suppliers_page import render_suppliers_page
        render_suppliers_page()


if __name__ == "__main__":
    main()

"""Data refresh utility functions for Streamlit pages"""

import streamlit as st
from datetime import datetime, timedelta


def init_refresh_config():
    """Initialize refresh configuration in session state"""
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 60  # Default 60 seconds
    
    if 'auto_refresh_enabled' not in st.session_state:
        st.session_state.auto_refresh_enabled = True
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None


def render_refresh_controls():
    """Render refresh controls in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Data Refresh")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox(
        "Enable auto-refresh",
        value=st.session_state.auto_refresh_enabled,
        help="Automatically refresh data at configured interval"
    )
    st.session_state.auto_refresh_enabled = auto_refresh
    
    # Refresh interval configuration
    if auto_refresh:
        interval = st.sidebar.slider(
            "Refresh interval (seconds)",
            min_value=30,
            max_value=300,
            value=st.session_state.refresh_interval,
            step=30,
            help="How often to automatically refresh data"
        )
        st.session_state.refresh_interval = interval
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
        refresh_data()
        st.rerun()
    
    # Last refresh timestamp
    if st.session_state.last_refresh:
        time_since = datetime.now() - st.session_state.last_refresh
        seconds_ago = int(time_since.total_seconds())
        
        if seconds_ago < 60:
            time_str = f"{seconds_ago}s ago"
        else:
            minutes_ago = seconds_ago // 60
            time_str = f"{minutes_ago}m ago"
        
        st.sidebar.caption(f"Last updated: {time_str}")


def refresh_data():
    """Refresh data from source"""
    try:
        data_service = st.session_state.data_service
        data = data_service.refresh_data()
        st.session_state.data_cache = data
        st.session_state.last_refresh = datetime.now()
        st.sidebar.success("✅ Data refreshed")
    except Exception as e:
        st.sidebar.error(f"❌ Refresh failed: {str(e)}")


def check_auto_refresh():
    """Check if auto-refresh should trigger"""
    if not st.session_state.auto_refresh_enabled:
        return False
    
    if st.session_state.last_refresh is None:
        return True
    
    time_since = datetime.now() - st.session_state.last_refresh
    return time_since.total_seconds() >= st.session_state.refresh_interval


def handle_auto_refresh():
    """Handle automatic data refresh if needed"""
    if check_auto_refresh():
        refresh_data()
        st.rerun()

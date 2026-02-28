"""Error handling utility functions for Streamlit pages"""

import streamlit as st
from functools import wraps
import traceback


def handle_data_load_error(error: Exception, retry_callback=None):
    """
    Display error message for data load failures with retry option
    
    Args:
        error: The exception that occurred
        retry_callback: Optional callback function to retry the operation
    """
    st.error("❌ Failed to load data from data source")
    
    with st.expander("Error Details", expanded=False):
        st.code(str(error))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if retry_callback:
            if st.button("🔄 Retry", use_container_width=True):
                retry_callback()
                st.rerun()
    
    with col2:
        if st.button("📋 Use Cached Data", use_container_width=True):
            st.info("Attempting to use cached data...")
            st.rerun()


def handle_data_unavailable():
    """Display message when data store is unavailable"""
    st.warning("⚠️ Data store is currently unavailable")
    st.info("🔒 Operating in read-only mode with cached data")
    
    if st.session_state.data_cache:
        st.success("✅ Using cached data from previous session")
        if st.session_state.last_refresh:
            st.caption(f"Cache from: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.error("❌ No cached data available")
        st.markdown("""
        **Possible actions:**
        - Wait for data store to become available
        - Contact system administrator
        - Check network connectivity
        """)


def handle_validation_error(field_name: str, error_message: str):
    """
    Display validation error message for invalid inputs
    
    Args:
        field_name: Name of the field with validation error
        error_message: Description of the validation error
    """
    st.error(f"❌ Validation Error: {field_name}")
    st.warning(error_message)


def handle_export_error(error: Exception, format_type: str):
    """
    Display error message for export failures
    
    Args:
        error: The exception that occurred
        format_type: The export format (CSV, Excel, etc.)
    """
    st.error(f"❌ Failed to export data to {format_type}")
    
    with st.expander("Error Details", expanded=False):
        st.code(str(error))
    
    st.info("""
    **Troubleshooting:**
    - Ensure data is properly loaded
    - Check if filters are valid
    - Try reducing the dataset size
    - Try a different export format
    """)


def with_error_boundary(func):
    """
    Decorator to wrap functions with error boundary
    Catches exceptions and displays user-friendly error messages
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            
            with st.expander("Technical Details", expanded=False):
                st.code(traceback.format_exc())
            
            if st.button("🔄 Retry"):
                st.rerun()
    
    return wrapper


def show_transient_error(error: Exception, retry_callback=None):
    """
    Display error message for transient failures with retry mechanism
    
    Args:
        error: The exception that occurred
        retry_callback: Optional callback function to retry the operation
    """
    st.warning("⚠️ A temporary error occurred")
    st.info(str(error))
    
    if retry_callback:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Retry", use_container_width=True):
                with st.spinner("Retrying..."):
                    try:
                        retry_callback()
                        st.success("✅ Operation successful")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Retry failed: {str(e)}")
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.rerun()


def validate_filter_input(filters):
    """
    Validate filter criteria and return validation errors
    
    Args:
        filters: FilterCriteria object to validate
    
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate date range
    if filters.date_range:
        start_date, end_date = filters.date_range
        if start_date > end_date:
            errors.append("Start date must be before end date")
    
    # Validate search query
    if filters.search_query:
        if len(filters.search_query) < 2:
            errors.append("Search query must be at least 2 characters")
        if len(filters.search_query) > 100:
            errors.append("Search query must be less than 100 characters")
    
    return errors


def display_validation_errors(errors):
    """
    Display validation error messages
    
    Args:
        errors: List of validation error messages
    """
    if errors:
        st.error("❌ Validation Errors:")
        for error in errors:
            st.warning(f"• {error}")
        return True
    return False

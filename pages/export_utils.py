"""Export utility functions for Streamlit pages"""

import streamlit as st
import pandas as pd
from io import BytesIO
from src.export_service import ExportService


def render_export_buttons(data_df: pd.DataFrame, filename_prefix: str):
    """
    Render export buttons for CSV and Excel formats
    
    Args:
        data_df: DataFrame to export
        filename_prefix: Prefix for the exported filename (e.g., "shipments", "inventory")
    """
    if data_df is None or data_df.empty:
        st.info("No data available to export")
        return
    
    col1, col2 = st.columns(2)
    
    export_service = ExportService()
    
    with col1:
        try:
            with st.spinner("Preparing CSV export..."):
                csv_data = export_service.export_to_csv(data_df, f"{filename_prefix}.csv")
            st.download_button(
                label="📥 Export to CSV",
                data=csv_data,
                file_name=f"{filename_prefix}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Download data as CSV file"
            )
        except Exception as e:
            from pages.error_utils import handle_export_error
            handle_export_error(e, "CSV")
    
    with col2:
        try:
            with st.spinner("Preparing Excel export..."):
                excel_data = export_service.export_to_excel(data_df, f"{filename_prefix}.xlsx")
            st.download_button(
                label="📥 Export to Excel",
                data=excel_data,
                file_name=f"{filename_prefix}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Download data as Excel file"
            )
        except Exception as e:
            from pages.error_utils import handle_export_error
            handle_export_error(e, "Excel")


def show_export_progress(message: str = "Preparing export..."):
    """Show export progress indicator"""
    with st.spinner(message):
        pass

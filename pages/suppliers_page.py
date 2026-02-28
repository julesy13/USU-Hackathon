"""Suppliers page for Supply Chain Visibility application"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.supplier_tracker import SupplierPerformanceTracker


def render_suppliers_page():
    """Render the supplier performance tracking page"""
    st.title("🏭 Supplier Performance")
    
    # Help section
    from pages.tooltip_utils import render_help_section
    render_help_section("Suppliers")
    
    # Load data
    data = get_data()
    if data is None:
        st.error("❌ Failed to load supplier data")
        return
    
    tracker = SupplierPerformanceTracker(data)
    
    # Ranking criteria selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Supplier Rankings")
    
    with col2:
        ranking_criteria = st.selectbox(
            "Rank by",
            options=["performance_score", "on_time_delivery_rate", "quality_score"],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Select the metric to rank suppliers by"
        )
    
    # Get ranked suppliers
    from src.supplier_tracker import RankingCriteria
    criteria = RankingCriteria(metric=ranking_criteria, ascending=False)
    ranked_suppliers = tracker.rank_suppliers(criteria)
    
    st.markdown("---")
    
    # Display supplier rankings table
    render_supplier_rankings(ranked_suppliers, data)
    
    st.markdown("---")
    
    # Supplier comparison view
    render_supplier_comparison(data, tracker)
    
    st.markdown("---")
    
    # Detailed supplier metrics
    render_supplier_details(data, tracker)
    
    # Export functionality
    if data.suppliers:
        st.markdown("---")
        st.markdown("### Export Data")
        from pages.export_utils import render_export_buttons
        
        # Convert suppliers to DataFrame for export
        df_export = pd.DataFrame([{
            "ID": supplier.id,
            "Name": supplier.name,
            "Contact": supplier.contact,
            "Performance Score": supplier.performance_score,
            "On-Time Delivery Rate": supplier.on_time_delivery_rate,
            "Quality Score": supplier.quality_score,
            "Average Lead Time": supplier.average_lead_time,
            "Total Shipments": supplier.total_shipments,
            "Last Updated": supplier.last_updated.strftime("%Y-%m-%d %H:%M")
        } for supplier in data.suppliers])
        
        render_export_buttons(df_export, "suppliers")


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


def render_supplier_rankings(ranked_suppliers, data):
    """Render supplier performance rankings table"""
    if not ranked_suppliers:
        st.info("No supplier data available")
        return
    
    # Add calculation explanation
    from pages.tooltip_utils import add_calculation_explanation
    add_calculation_explanation("performance_score")
    
    # Convert to DataFrame
    df_data = []
    for rank, ranking in enumerate(ranked_suppliers, 1):
        supplier = next((s for s in data.suppliers if s.id == ranking.supplier_id), None)
        if supplier:
            df_data.append({
                "Rank": rank,
                "Supplier": supplier.name,
                "Performance Score": f"{supplier.performance_score:.1f}",
                "On-Time Rate": f"{supplier.on_time_delivery_rate:.1f}%",
                "Quality Score": f"{supplier.quality_score:.1f}",
                "Avg Lead Time": f"{supplier.average_lead_time:.1f} days",
                "Total Shipments": supplier.total_shipments
            })
    
    df = pd.DataFrame(df_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def render_supplier_comparison(data, tracker):
    """Render supplier comparison view"""
    st.markdown("### Compare Suppliers")
    
    if not data.suppliers:
        st.info("No suppliers available for comparison")
        return
    
    # Supplier selection for comparison
    supplier_names = {s.id: s.name for s in data.suppliers}
    selected_suppliers = st.multiselect(
        "Select suppliers to compare (up to 5)",
        options=list(supplier_names.keys()),
        format_func=lambda x: supplier_names[x],
        max_selections=5,
        help="Choose up to 5 suppliers to compare their performance metrics"
    )
    
    if not selected_suppliers:
        st.info("Select suppliers to view comparison")
        return
    
    # Get metrics for selected suppliers
    comparison_data = []
    for supplier_id in selected_suppliers:
        metrics = tracker.get_supplier_metrics(supplier_id)
        supplier = next((s for s in data.suppliers if s.id == supplier_id), None)
        if supplier and metrics:
            comparison_data.append({
                "Supplier": supplier.name,
                "Performance Score": metrics.performance_score,
                "On-Time Rate": metrics.on_time_delivery_rate,
                "Quality Score": metrics.quality_score,
                "Avg Lead Time": metrics.average_lead_time
            })
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        
        # Create comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                df_comparison,
                x="Supplier",
                y="Performance Score",
                title="Performance Score Comparison",
                color="Performance Score",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(
                df_comparison,
                x="Supplier",
                y="On-Time Rate",
                title="On-Time Delivery Rate Comparison",
                color="On-Time Rate",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig2, use_container_width=True)


def render_supplier_details(data, tracker):
    """Render detailed supplier metrics and history"""
    st.markdown("### Supplier Details")
    
    if not data.suppliers:
        st.info("No supplier data available")
        return
    
    # Supplier selection
    supplier_names = {s.id: s.name for s in data.suppliers}
    selected_supplier_id = st.selectbox(
        "Select a supplier to view details",
        options=list(supplier_names.keys()),
        format_func=lambda x: supplier_names[x],
        help="Choose a supplier to see detailed performance metrics and history"
    )
    
    if selected_supplier_id:
        supplier = next((s for s in data.suppliers if s.id == selected_supplier_id), None)
        if supplier:
            render_supplier_detail_card(supplier, tracker)


def render_supplier_detail_card(supplier, tracker):
    """Render detailed information card for a supplier"""
    with st.expander("🏭 Supplier Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Supplier ID:** {supplier.id}")
            st.markdown(f"**Name:** {supplier.name}")
            st.markdown(f"**Contact:** {supplier.contact}")
            st.markdown(f"**Total Shipments:** {supplier.total_shipments}")
        
        with col2:
            st.markdown(f"**Performance Score:** {supplier.performance_score:.1f}/100")
            st.markdown(f"**On-Time Delivery Rate:** {supplier.on_time_delivery_rate:.1f}%")
            st.markdown(f"**Quality Score:** {supplier.quality_score:.1f}/100")
            st.markdown(f"**Average Lead Time:** {supplier.average_lead_time:.1f} days")
        
        # Performance indicators
        st.markdown("---")
        st.markdown("**Performance Indicators:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if supplier.on_time_delivery_rate >= 95:
                st.success("✅ Excellent On-Time Performance")
            elif supplier.on_time_delivery_rate >= 85:
                st.info("ℹ️ Good On-Time Performance")
            else:
                st.warning("⚠️ Below Target On-Time Performance")
        
        with col2:
            if supplier.quality_score >= 90:
                st.success("✅ High Quality Score")
            elif supplier.quality_score >= 75:
                st.info("ℹ️ Acceptable Quality Score")
            else:
                st.warning("⚠️ Quality Improvement Needed")
        
        with col3:
            if supplier.average_lead_time <= 7:
                st.success("✅ Fast Lead Time")
            elif supplier.average_lead_time <= 14:
                st.info("ℹ️ Standard Lead Time")
            else:
                st.warning("⚠️ Long Lead Time")
    
    # Performance history
    st.markdown("### Performance History (90 days)")
    
    try:
        history = tracker.get_performance_history(supplier.id, days=90)
        
        if history and len(history.dates) > 0:
            df_history = pd.DataFrame({
                "Date": history.dates,
                "Performance Score": history.values
            })
            
            fig = px.line(
                df_history,
                x="Date",
                y="Performance Score",
                title=f"Performance Trend - {supplier.name}",
                labels={"Performance Score": "Score", "Date": "Date"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No historical performance data available for this supplier")
    except Exception as e:
        st.warning(f"Unable to load performance history: {str(e)}")

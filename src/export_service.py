"""
Export service for Supply Chain Visibility application.

This module provides the ExportService class that handles data export functionality
to CSV and Excel formats.
"""

import io
from typing import Union
import pandas as pd

from src.models import SupplyChainData, Shipment, InventoryItem, Supplier, Node, Edge
from src.filter_engine import FilterCriteria


class ExportService:
    """
    Handles data export functionality.
    
    This class provides methods to export supply chain data to CSV and Excel formats,
    with support for filtering and data preparation.
    """
    
    def export_to_csv(self, data: pd.DataFrame, filename: str) -> bytes:
        """
        Export data to CSV format.
        
        Args:
            data: DataFrame containing the data to export
            filename: Name for the exported file (not used in bytes output but kept for interface consistency)
            
        Returns:
            CSV data as bytes
        """
        # Create a string buffer to hold CSV data
        buffer = io.StringIO()
        data.to_csv(buffer, index=False)
        
        # Convert string to bytes
        csv_bytes = buffer.getvalue().encode('utf-8')
        buffer.close()
        
        return csv_bytes
    
    def export_to_excel(self, data: pd.DataFrame, filename: str) -> bytes:
        """
        Export data to Excel format.
        
        Args:
            data: DataFrame containing the data to export
            filename: Name for the exported file (not used in bytes output but kept for interface consistency)
            
        Returns:
            Excel data as bytes
        """
        # Create a bytes buffer to hold Excel data
        buffer = io.BytesIO()
        
        # Write DataFrame to Excel format
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data.to_excel(writer, index=False, sheet_name='Data')
        
        # Get the bytes value
        excel_bytes = buffer.getvalue()
        buffer.close()
        
        return excel_bytes
    
    def prepare_export_data(self, data: SupplyChainData, filters: FilterCriteria) -> pd.DataFrame:
        """
        Prepare filtered data for export.
        
        This method converts SupplyChainData to a pandas DataFrame, applying any
        specified filters. The resulting DataFrame contains all entity types
        (shipments, inventory, suppliers, nodes, edges) in a format suitable for export.
        
        Args:
            data: SupplyChainData object containing the data to export
            filters: FilterCriteria specifying which data to include
            
        Returns:
            DataFrame containing the prepared export data
        """
        # Apply filters if provided
        from src.filter_engine import FilterEngine
        
        if filters and self._has_active_filters(filters):
            filter_engine = FilterEngine()
            data = filter_engine.apply_filters(data, filters)
        
        # Convert each entity type to DataFrame
        export_data = {}
        
        # Add shipments data
        if data.shipments:
            shipments_data = []
            for shipment in data.shipments:
                shipments_data.append({
                    'type': 'shipment',
                    'id': shipment.id,
                    'origin': shipment.origin,
                    'destination': shipment.destination,
                    'current_location': shipment.current_location,
                    'status': shipment.status.value,
                    'estimated_delivery': shipment.estimated_delivery,
                    'actual_delivery': shipment.actual_delivery,
                    'items': ', '.join(shipment.items),
                    'supplier_id': shipment.supplier_id,
                    'created_at': shipment.created_at,
                    'updated_at': shipment.updated_at
                })
            export_data['shipments'] = pd.DataFrame(shipments_data)
        
        # Add inventory data
        if data.inventory:
            inventory_data = []
            for item in data.inventory:
                inventory_data.append({
                    'type': 'inventory',
                    'id': item.id,
                    'name': item.name,
                    'category': item.category,
                    'location': item.location,
                    'quantity': item.quantity,
                    'unit': item.unit,
                    'reorder_point': item.reorder_point,
                    'last_updated': item.last_updated
                })
            export_data['inventory'] = pd.DataFrame(inventory_data)
        
        # Add suppliers data
        if data.suppliers:
            suppliers_data = []
            for supplier in data.suppliers:
                suppliers_data.append({
                    'type': 'supplier',
                    'id': supplier.id,
                    'name': supplier.name,
                    'contact': supplier.contact,
                    'performance_score': supplier.performance_score,
                    'on_time_delivery_rate': supplier.on_time_delivery_rate,
                    'quality_score': supplier.quality_score,
                    'average_lead_time': supplier.average_lead_time,
                    'total_shipments': supplier.total_shipments,
                    'last_updated': supplier.last_updated
                })
            export_data['suppliers'] = pd.DataFrame(suppliers_data)
        
        # Add nodes data
        if data.nodes:
            nodes_data = []
            for node in data.nodes:
                nodes_data.append({
                    'type': 'node',
                    'id': node.id,
                    'name': node.name,
                    'node_type': node.type.value,
                    'location': node.location,
                    'latitude': node.latitude,
                    'longitude': node.longitude,
                    'status': node.status.value,
                    'capacity': node.capacity
                })
            export_data['nodes'] = pd.DataFrame(nodes_data)
        
        # Add edges data
        if data.edges:
            edges_data = []
            for edge in data.edges:
                edges_data.append({
                    'type': 'edge',
                    'id': edge.id,
                    'source_node_id': edge.source_node_id,
                    'target_node_id': edge.target_node_id,
                    'shipment_ids': ', '.join(edge.shipment_ids),
                    'active': edge.active
                })
            export_data['edges'] = pd.DataFrame(edges_data)
        
        # Combine all DataFrames
        if export_data:
            # Concatenate all DataFrames, filling missing columns with None
            combined_df = pd.concat(export_data.values(), ignore_index=True, sort=False)
            return combined_df
        else:
            # Return empty DataFrame if no data
            return pd.DataFrame()
    
    def _has_active_filters(self, filters: FilterCriteria) -> bool:
        """
        Check if any filters are active.
        
        Args:
            filters: FilterCriteria to check
            
        Returns:
            True if any filter is set, False otherwise
        """
        return (
            filters.date_range is not None or
            filters.status is not None or
            filters.location is not None or
            filters.category is not None or
            filters.search_query is not None
        )

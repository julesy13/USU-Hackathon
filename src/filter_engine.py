"""
Filter engine for Supply Chain Visibility application.

This module provides the FilterEngine class that handles filtering and searching
supply chain data based on various criteria.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple

from src.models import SupplyChainData, Shipment, InventoryItem, Supplier, Node


@dataclass
class FilterCriteria:
    """
    Criteria for filtering supply chain data.
    
    Attributes:
        date_range: Optional tuple of (start_date, end_date) for filtering by date
        status: Optional list of status values to filter by
        location: Optional list of locations to filter by
        category: Optional list of categories to filter by
        search_query: Optional search query string
        search_fields: Optional list of field names to search in
    """
    date_range: Optional[Tuple[datetime, datetime]] = None
    status: Optional[List[str]] = None
    location: Optional[List[str]] = None
    category: Optional[List[str]] = None
    search_query: Optional[str] = None
    search_fields: Optional[List[str]] = None


class FilterEngine:
    """
    Applies filters and search criteria to supply chain data.
    
    This class provides methods to filter shipments, inventory items, suppliers,
    and nodes based on various criteria including date ranges, status, location,
    category, and text search.
    """
    
    def apply_filters(self, data: SupplyChainData, filters: FilterCriteria) -> SupplyChainData:
        """
        Apply filter criteria to dataset.
        
        Filters are applied to each entity type (shipments, inventory, suppliers, nodes)
        based on the provided criteria. Only applicable filters are applied to each type.
        
        Args:
            data: SupplyChainData object to filter
            filters: FilterCriteria specifying the filters to apply
            
        Returns:
            New SupplyChainData object containing only filtered entities
        """
        # Filter each entity type
        filtered_shipments = self._filter_shipments(data.shipments, filters)
        filtered_inventory = self._filter_inventory(data.inventory, filters)
        filtered_suppliers = self._filter_suppliers(data.suppliers, filters)
        filtered_nodes = self._filter_nodes(data.nodes, filters)
        
        # Filter edges to only include those connecting filtered nodes
        filtered_node_ids = {node.id for node in filtered_nodes}
        filtered_edges = [
            edge for edge in data.edges
            if edge.source_node_id in filtered_node_ids and edge.target_node_id in filtered_node_ids
        ]
        
        return SupplyChainData(
            shipments=filtered_shipments,
            inventory=filtered_inventory,
            suppliers=filtered_suppliers,
            nodes=filtered_nodes,
            edges=filtered_edges,
            last_updated=data.last_updated
        )
    
    def search(self, data: SupplyChainData, query: str, fields: List[str]) -> SupplyChainData:
        """
        Search across specified fields.
        
        Performs case-insensitive text search across the specified fields in all entity types.
        
        Args:
            data: SupplyChainData object to search
            query: Search query string
            fields: List of field names to search in
            
        Returns:
            New SupplyChainData object containing only matching entities
        """
        if not query or not fields:
            return data
        
        query_lower = query.lower()
        
        # Search each entity type
        filtered_shipments = self._search_shipments(data.shipments, query_lower, fields)
        filtered_inventory = self._search_inventory(data.inventory, query_lower, fields)
        filtered_suppliers = self._search_suppliers(data.suppliers, query_lower, fields)
        filtered_nodes = self._search_nodes(data.nodes, query_lower, fields)
        
        # Filter edges to only include those connecting filtered nodes
        filtered_node_ids = {node.id for node in filtered_nodes}
        filtered_edges = [
            edge for edge in data.edges
            if edge.source_node_id in filtered_node_ids and edge.target_node_id in filtered_node_ids
        ]
        
        return SupplyChainData(
            shipments=filtered_shipments,
            inventory=filtered_inventory,
            suppliers=filtered_suppliers,
            nodes=filtered_nodes,
            edges=filtered_edges,
            last_updated=data.last_updated
        )
    
    def reset_filters(self) -> FilterCriteria:
        """
        Reset to default filter state.
        
        Returns:
            FilterCriteria object with all filters cleared/disabled
        """
        return FilterCriteria()
    
    # Private helper methods for filtering
    
    def _filter_shipments(self, shipments: List[Shipment], filters: FilterCriteria) -> List[Shipment]:
        """Filter shipments based on criteria."""
        result = shipments
        
        # Apply date range filter (using estimated_delivery)
        if filters.date_range:
            start_date, end_date = filters.date_range
            result = [
                s for s in result
                if start_date <= s.estimated_delivery <= end_date
            ]
        
        # Apply status filter
        if filters.status:
            result = [
                s for s in result
                if s.status.value in filters.status
            ]
        
        # Apply location filter (matches origin, destination, or current_location)
        if filters.location:
            result = [
                s for s in result
                if s.origin in filters.location or 
                   s.destination in filters.location or 
                   s.current_location in filters.location
            ]
        
        # Apply search if specified
        if filters.search_query and filters.search_fields:
            result = self._search_shipments(result, filters.search_query.lower(), filters.search_fields)
        
        return result
    
    def _filter_inventory(self, inventory: List[InventoryItem], filters: FilterCriteria) -> List[InventoryItem]:
        """Filter inventory items based on criteria."""
        result = inventory
        
        # Apply date range filter (using last_updated)
        if filters.date_range:
            start_date, end_date = filters.date_range
            result = [
                i for i in result
                if start_date <= i.last_updated <= end_date
            ]
        
        # Apply location filter
        if filters.location:
            result = [
                i for i in result
                if i.location in filters.location
            ]
        
        # Apply category filter
        if filters.category:
            result = [
                i for i in result
                if i.category in filters.category
            ]
        
        # Apply search if specified
        if filters.search_query and filters.search_fields:
            result = self._search_inventory(result, filters.search_query.lower(), filters.search_fields)
        
        return result
    
    def _filter_suppliers(self, suppliers: List[Supplier], filters: FilterCriteria) -> List[Supplier]:
        """Filter suppliers based on criteria."""
        result = suppliers
        
        # Apply date range filter (using last_updated)
        if filters.date_range:
            start_date, end_date = filters.date_range
            result = [
                s for s in result
                if start_date <= s.last_updated <= end_date
            ]
        
        # Apply search if specified
        if filters.search_query and filters.search_fields:
            result = self._search_suppliers(result, filters.search_query.lower(), filters.search_fields)
        
        return result
    
    def _filter_nodes(self, nodes: List[Node], filters: FilterCriteria) -> List[Node]:
        """Filter nodes based on criteria."""
        result = nodes
        
        # Apply status filter
        if filters.status:
            result = [
                n for n in result
                if n.status.value in filters.status
            ]
        
        # Apply location filter
        if filters.location:
            result = [
                n for n in result
                if n.location in filters.location
            ]
        
        # Apply search if specified
        if filters.search_query and filters.search_fields:
            result = self._search_nodes(result, filters.search_query.lower(), filters.search_fields)
        
        return result
    
    # Private helper methods for searching
    
    def _search_shipments(self, shipments: List[Shipment], query: str, fields: List[str]) -> List[Shipment]:
        """Search shipments in specified fields."""
        result = []
        for shipment in shipments:
            for field in fields:
                if hasattr(shipment, field):
                    value = getattr(shipment, field)
                    # Convert value to string for searching
                    if value is not None:
                        value_str = str(value).lower()
                        if query in value_str:
                            result.append(shipment)
                            break
        return result
    
    def _search_inventory(self, inventory: List[InventoryItem], query: str, fields: List[str]) -> List[InventoryItem]:
        """Search inventory items in specified fields."""
        result = []
        for item in inventory:
            for field in fields:
                if hasattr(item, field):
                    value = getattr(item, field)
                    # Convert value to string for searching
                    if value is not None:
                        value_str = str(value).lower()
                        if query in value_str:
                            result.append(item)
                            break
        return result
    
    def _search_suppliers(self, suppliers: List[Supplier], query: str, fields: List[str]) -> List[Supplier]:
        """Search suppliers in specified fields."""
        result = []
        for supplier in suppliers:
            for field in fields:
                if hasattr(supplier, field):
                    value = getattr(supplier, field)
                    # Convert value to string for searching
                    if value is not None:
                        value_str = str(value).lower()
                        if query in value_str:
                            result.append(supplier)
                            break
        return result
    
    def _search_nodes(self, nodes: List[Node], query: str, fields: List[str]) -> List[Node]:
        """Search nodes in specified fields."""
        result = []
        for node in nodes:
            for field in fields:
                if hasattr(node, field):
                    value = getattr(node, field)
                    # Convert value to string for searching
                    if value is not None:
                        value_str = str(value).lower()
                        if query in value_str:
                            result.append(node)
                            break
        return result

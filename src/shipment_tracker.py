"""
Shipment tracker component for Supply Chain Visibility application.

This module provides the ShipmentTracker class that handles shipment tracking,
listing, searching, and detail retrieval functionality.
"""

from typing import List, Optional
from dataclasses import dataclass

from src.models import Shipment, SupplyChainData
from src.filter_engine import FilterCriteria, FilterEngine


@dataclass
class ShipmentDetails:
    """
    Detailed information for a specific shipment.
    
    Attributes:
        shipment: The shipment object
        supplier_name: Name of the supplier (if available)
    """
    shipment: Shipment
    supplier_name: Optional[str] = None


class ShipmentTracker:
    """
    Tracks and displays shipment information.
    
    This class provides methods to list shipments with filters, get detailed
    information for specific shipments, and search shipments by various criteria.
    """
    
    def __init__(self, data: SupplyChainData):
        """
        Initialize the shipment tracker with supply chain data.
        
        Args:
            data: SupplyChainData object containing all supply chain information
        """
        self.data = data
        self.filter_engine = FilterEngine()
    
    def list_shipments(self, filters: FilterCriteria) -> List[Shipment]:
        """
        Get filtered list of shipments.
        
        Applies the provided filter criteria to return a subset of shipments
        that match all specified conditions.
        
        Args:
            filters: FilterCriteria object specifying the filters to apply
            
        Returns:
            List of Shipment objects matching the filter criteria
        """
        filtered_data = self.filter_engine.apply_filters(self.data, filters)
        return filtered_data.shipments
    
    def get_shipment_details(self, shipment_id: str) -> ShipmentDetails:
        """
        Get detailed information for a specific shipment.
        
        Retrieves the shipment and enriches it with additional information
        such as the supplier name.
        
        Args:
            shipment_id: Unique identifier of the shipment
            
        Returns:
            ShipmentDetails object containing the shipment and related information
            
        Raises:
            ValueError: If shipment with the given ID is not found
        """
        # Find the shipment
        shipment = next((s for s in self.data.shipments if s.id == shipment_id), None)
        if shipment is None:
            raise ValueError(f"Shipment not found: {shipment_id}")
        
        # Find the supplier name
        supplier = next((s for s in self.data.suppliers if s.id == shipment.supplier_id), None)
        supplier_name = supplier.name if supplier else None
        
        return ShipmentDetails(
            shipment=shipment,
            supplier_name=supplier_name
        )
    
    def search_shipments(self, query: str, field: str) -> List[Shipment]:
        """
        Search shipments by identifier, origin, or destination.
        
        Performs a case-insensitive search in the specified field.
        
        Args:
            query: Search query string
            field: Field name to search in ('id', 'origin', 'destination', or 'current_location')
            
        Returns:
            List of Shipment objects matching the search query
            
        Raises:
            ValueError: If field is not a valid searchable field
        """
        valid_fields = ['id', 'origin', 'destination', 'current_location']
        if field not in valid_fields:
            raise ValueError(f"Invalid search field: {field}. Must be one of {valid_fields}")
        
        # Use the filter engine's search functionality
        search_result = self.filter_engine.search(self.data, query, [field])
        return search_result.shipments

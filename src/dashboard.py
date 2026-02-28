"""
Dashboard component for Supply Chain Visibility application.

This module provides the Dashboard class that handles the main dashboard
display and metrics calculation functionality.
"""

from dataclasses import dataclass
from typing import Optional

from src.models import SupplyChainData, ShipmentStatus
from src.filter_engine import FilterCriteria, FilterEngine


@dataclass
class DashboardMetrics:
    """
    Key metrics displayed on the dashboard.
    
    Attributes:
        total_shipments: Total number of shipments
        in_transit_count: Number of shipments currently in transit
        delayed_count: Number of delayed shipments
        delivered_count: Number of delivered shipments
        pending_count: Number of pending shipments
        low_stock_count: Number of inventory items below reorder point
        total_inventory_items: Total number of inventory items
        total_suppliers: Total number of suppliers
        average_supplier_performance: Average performance score across all suppliers
    """
    total_shipments: int
    in_transit_count: int
    delayed_count: int
    delivered_count: int
    pending_count: int
    low_stock_count: int
    total_inventory_items: int
    total_suppliers: int
    average_supplier_performance: float


class Dashboard:
    """
    Main dashboard displaying supply chain metrics.
    
    This class provides methods to render the dashboard and calculate
    key performance metrics from supply chain data.
    """
    
    def __init__(self, data: SupplyChainData):
        """
        Initialize the dashboard with supply chain data.
        
        Args:
            data: SupplyChainData object containing all supply chain information
        """
        self.data = data
        self.filter_engine = FilterEngine()
    
    def render(self, filters: Optional[FilterCriteria] = None) -> DashboardMetrics:
        """
        Render dashboard with current metrics.
        
        Calculates and returns dashboard metrics, optionally applying filters
        to the data before calculation.
        
        Args:
            filters: Optional FilterCriteria to apply before calculating metrics
            
        Returns:
            DashboardMetrics object containing calculated metrics
        """
        # Apply filters if provided
        if filters:
            data = self.filter_engine.apply_filters(self.data, filters)
        else:
            data = self.data
        
        return self.get_metrics(data)
    
    def get_metrics(self, data: SupplyChainData) -> DashboardMetrics:
        """
        Calculate dashboard metrics from data.
        
        Computes key metrics including shipment counts by status, low stock items,
        and supplier performance averages.
        
        Args:
            data: SupplyChainData object to calculate metrics from
            
        Returns:
            DashboardMetrics object containing all calculated metrics
        """
        # Calculate shipment metrics
        total_shipments = len(data.shipments)
        in_transit_count = sum(1 for s in data.shipments if s.status == ShipmentStatus.IN_TRANSIT)
        delayed_count = sum(1 for s in data.shipments if s.status == ShipmentStatus.DELAYED)
        delivered_count = sum(1 for s in data.shipments if s.status == ShipmentStatus.DELIVERED)
        pending_count = sum(1 for s in data.shipments if s.status == ShipmentStatus.PENDING)
        
        # Calculate inventory metrics
        total_inventory_items = len(data.inventory)
        low_stock_count = sum(1 for item in data.inventory if item.quantity < item.reorder_point)
        
        # Calculate supplier metrics
        total_suppliers = len(data.suppliers)
        if total_suppliers > 0:
            average_supplier_performance = sum(s.performance_score for s in data.suppliers) / total_suppliers
        else:
            average_supplier_performance = 0.0
        
        return DashboardMetrics(
            total_shipments=total_shipments,
            in_transit_count=in_transit_count,
            delayed_count=delayed_count,
            delivered_count=delivered_count,
            pending_count=pending_count,
            low_stock_count=low_stock_count,
            total_inventory_items=total_inventory_items,
            total_suppliers=total_suppliers,
            average_supplier_performance=average_supplier_performance
        )

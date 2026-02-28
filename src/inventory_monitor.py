"""
Inventory monitor component for Supply Chain Visibility application.

This module provides the InventoryMonitor class that handles inventory tracking,
low stock detection, and trend analysis functionality.
"""

from typing import List
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.models import InventoryItem, SupplyChainData
from src.filter_engine import FilterCriteria, FilterEngine


@dataclass
class TimeSeries:
    """
    Time series data for trend analysis.
    
    Attributes:
        dates: List of dates in the time series
        values: List of values corresponding to each date
        item_id: ID of the inventory item
    """
    dates: List[datetime]
    values: List[float]
    item_id: str


class InventoryMonitor:
    """
    Monitors inventory levels across locations.
    
    This class provides methods to get inventory levels with filters,
    identify low stock items, and analyze inventory trends over time.
    """
    
    def __init__(self, data: SupplyChainData):
        """
        Initialize the inventory monitor with supply chain data.
        
        Args:
            data: SupplyChainData object containing all supply chain information
        """
        self.data = data
        self.filter_engine = FilterEngine()
    
    def get_inventory_levels(self, filters: FilterCriteria) -> List[InventoryItem]:
        """
        Get current inventory levels with filters applied.
        
        Applies the provided filter criteria to return a subset of inventory items
        that match all specified conditions.
        
        Args:
            filters: FilterCriteria object specifying the filters to apply
            
        Returns:
            List of InventoryItem objects matching the filter criteria
        """
        filtered_data = self.filter_engine.apply_filters(self.data, filters)
        return filtered_data.inventory
    
    def get_low_stock_items(self, threshold: float) -> List[InventoryItem]:
        """
        Identify items below stock threshold.
        
        Returns inventory items where the current quantity is below the specified
        threshold. The threshold is compared against the item's reorder_point.
        
        Args:
            threshold: Threshold multiplier for reorder point (e.g., 1.0 means at or below reorder point)
            
        Returns:
            List of InventoryItem objects with quantity below threshold * reorder_point
        """
        low_stock_items = [
            item for item in self.data.inventory
            if item.quantity < (threshold * item.reorder_point)
        ]
        return low_stock_items
    
    def get_inventory_trends(self, item_id: str, days: int) -> TimeSeries:
        """
        Get historical inventory data for trend analysis.
        
        Note: This is a simplified implementation that generates trend data based on
        the current inventory level. In a production system, this would query
        historical data from a time-series database.
        
        Args:
            item_id: Unique identifier of the inventory item
            days: Number of days of historical data to retrieve
            
        Returns:
            TimeSeries object containing dates and values for the trend
            
        Raises:
            ValueError: If item with the given ID is not found
        """
        # Find the inventory item
        item = next((i for i in self.data.inventory if i.id == item_id), None)
        if item is None:
            raise ValueError(f"Inventory item not found: {item_id}")
        
        # Generate date range
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(days - 1, -1, -1)]
        
        # In a real implementation, we would query historical data
        # For now, we'll generate a simple trend based on current quantity
        # This simulates gradual changes in inventory over time
        current_quantity = item.quantity
        values = []
        
        for i in range(days):
            # Simple simulation: add some variation around current quantity
            # In production, this would be actual historical data
            variation = (i - days // 2) * 0.05  # Small variation
            simulated_value = max(0, current_quantity * (1 + variation))
            values.append(simulated_value)
        
        return TimeSeries(
            dates=dates,
            values=values,
            item_id=item_id
        )

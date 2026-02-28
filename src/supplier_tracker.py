"""
Supplier performance tracking for Supply Chain Visibility application.

This module provides the SupplierPerformanceTracker class that tracks and analyzes
supplier performance metrics including on-time delivery rates, rankings, and historical data.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from src.models import Supplier, Shipment, SupplyChainData


@dataclass
class SupplierMetrics:
    """
    Performance metrics for a supplier.
    
    Attributes:
        supplier_id: Unique identifier for the supplier
        supplier_name: Name of the supplier
        on_time_delivery_rate: Percentage of on-time deliveries (0-100)
        quality_score: Quality rating (0-100)
        average_lead_time: Average lead time in days
        total_shipments: Total number of shipments
        performance_score: Overall performance score (0-100)
    """
    supplier_id: str
    supplier_name: str
    on_time_delivery_rate: float
    quality_score: float
    average_lead_time: float
    total_shipments: int
    performance_score: float


@dataclass
class SupplierRanking:
    """
    Ranking information for a supplier.
    
    Attributes:
        rank: Position in ranking (1 = best)
        supplier_id: Unique identifier for the supplier
        supplier_name: Name of the supplier
        score: Score used for ranking
        metrics: Full supplier metrics
    """
    rank: int
    supplier_id: str
    supplier_name: str
    score: float
    metrics: SupplierMetrics


@dataclass
class RankingCriteria:
    """
    Criteria for ranking suppliers.
    
    Attributes:
        metric: Metric to rank by ('on_time_delivery_rate', 'quality_score', 
                'performance_score', 'average_lead_time')
        ascending: If True, lower values rank higher (for lead time)
    """
    metric: str
    ascending: bool = False


@dataclass
class PerformanceDataPoint:
    """
    A single data point in performance history.
    
    Attributes:
        date: Date of the data point
        on_time_delivery_rate: On-time delivery rate at this point
        quality_score: Quality score at this point
        average_lead_time: Average lead time at this point
        shipment_count: Number of shipments in this period
    """
    date: datetime
    on_time_delivery_rate: float
    quality_score: float
    average_lead_time: float
    shipment_count: int


class SupplierPerformanceTracker:
    """
    Tracks and analyzes supplier performance.
    
    This class provides methods to calculate supplier metrics, on-time delivery rates,
    rank suppliers by various criteria, and retrieve historical performance data.
    """
    
    def __init__(self, data: SupplyChainData):
        """
        Initialize the supplier performance tracker.
        
        Args:
            data: SupplyChainData object containing all supply chain data
        """
        self.data = data
    
    def get_supplier_metrics(self, supplier_id: str) -> SupplierMetrics:
        """
        Get performance metrics for a supplier.
        
        Args:
            supplier_id: Unique identifier for the supplier
            
        Returns:
            SupplierMetrics object containing all performance metrics
            
        Raises:
            ValueError: If supplier_id is not found
        """
        # Find the supplier
        supplier = next((s for s in self.data.suppliers if s.id == supplier_id), None)
        if supplier is None:
            raise ValueError(f"Supplier not found: {supplier_id}")
        
        # Calculate on-time delivery rate from shipments
        on_time_rate = self.calculate_on_time_rate(supplier_id)
        
        # Return metrics
        return SupplierMetrics(
            supplier_id=supplier.id,
            supplier_name=supplier.name,
            on_time_delivery_rate=on_time_rate,
            quality_score=supplier.quality_score,
            average_lead_time=supplier.average_lead_time,
            total_shipments=supplier.total_shipments,
            performance_score=supplier.performance_score
        )
    
    def calculate_on_time_rate(self, supplier_id: str) -> float:
        """
        Calculate on-time delivery rate for a supplier.
        
        The on-time delivery rate is calculated as:
        (number of shipments delivered on or before estimated delivery time) / total delivered shipments * 100
        
        Only considers delivered shipments (those with actual_delivery set).
        
        Args:
            supplier_id: Unique identifier for the supplier
            
        Returns:
            On-time delivery rate as a percentage (0-100)
        """
        # Get all delivered shipments for this supplier
        supplier_shipments = [
            s for s in self.data.shipments 
            if s.supplier_id == supplier_id and s.actual_delivery is not None
        ]
        
        # If no delivered shipments, return 0
        if not supplier_shipments:
            return 0.0
        
        # Count on-time deliveries
        on_time_count = sum(
            1 for s in supplier_shipments 
            if s.actual_delivery <= s.estimated_delivery
        )
        
        # Calculate percentage
        on_time_rate = (on_time_count / len(supplier_shipments)) * 100
        
        return on_time_rate
    
    def rank_suppliers(self, criteria: RankingCriteria) -> List[SupplierRanking]:
        """
        Rank suppliers by performance criteria.
        
        Args:
            criteria: RankingCriteria specifying the metric and sort order
            
        Returns:
            List of SupplierRanking objects ordered by rank (best to worst)
            
        Raises:
            ValueError: If criteria.metric is not a valid metric name
        """
        valid_metrics = {
            'on_time_delivery_rate',
            'quality_score',
            'performance_score',
            'average_lead_time'
        }
        
        if criteria.metric not in valid_metrics:
            raise ValueError(
                f"Invalid metric: {criteria.metric}. "
                f"Must be one of {valid_metrics}"
            )
        
        # Get metrics for all suppliers
        supplier_metrics = []
        for supplier in self.data.suppliers:
            try:
                metrics = self.get_supplier_metrics(supplier.id)
                supplier_metrics.append(metrics)
            except ValueError:
                # Skip suppliers that can't be found
                continue
        
        # Sort by the specified metric
        sorted_metrics = sorted(
            supplier_metrics,
            key=lambda m: getattr(m, criteria.metric),
            reverse=not criteria.ascending
        )
        
        # Create rankings
        rankings = []
        for rank, metrics in enumerate(sorted_metrics, start=1):
            ranking = SupplierRanking(
                rank=rank,
                supplier_id=metrics.supplier_id,
                supplier_name=metrics.supplier_name,
                score=getattr(metrics, criteria.metric),
                metrics=metrics
            )
            rankings.append(ranking)
        
        return rankings
    
    def get_performance_history(
        self, 
        supplier_id: str, 
        days: int
    ) -> List[PerformanceDataPoint]:
        """
        Get historical performance data for a supplier.
        
        Returns performance metrics calculated over time windows within the specified
        date range. Data points are ordered chronologically.
        
        Args:
            supplier_id: Unique identifier for the supplier
            days: Number of days of history to retrieve
            
        Returns:
            List of PerformanceDataPoint objects ordered by date
            
        Raises:
            ValueError: If supplier_id is not found or days is negative
        """
        if days < 0:
            raise ValueError("days must be non-negative")
        
        # Verify supplier exists
        supplier = next((s for s in self.data.suppliers if s.id == supplier_id), None)
        if supplier is None:
            raise ValueError(f"Supplier not found: {supplier_id}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all shipments for this supplier within the date range
        supplier_shipments = [
            s for s in self.data.shipments
            if s.supplier_id == supplier_id 
            and start_date <= s.created_at <= end_date
        ]
        
        # If no shipments in range, return empty list
        if not supplier_shipments:
            return []
        
        # Group shipments by week for aggregation
        # This provides a reasonable granularity for historical trends
        weekly_data = {}
        
        for shipment in supplier_shipments:
            # Get the start of the week for this shipment
            week_start = shipment.created_at - timedelta(
                days=shipment.created_at.weekday()
            )
            week_key = week_start.date()
            
            if week_key not in weekly_data:
                weekly_data[week_key] = []
            
            weekly_data[week_key].append(shipment)
        
        # Calculate metrics for each week
        history = []
        for week_date, shipments in sorted(weekly_data.items()):
            # Calculate on-time rate for this week
            delivered = [s for s in shipments if s.actual_delivery is not None]
            if delivered:
                on_time = sum(
                    1 for s in delivered 
                    if s.actual_delivery <= s.estimated_delivery
                )
                on_time_rate = (on_time / len(delivered)) * 100
            else:
                on_time_rate = 0.0
            
            # Calculate average lead time for this week
            if delivered:
                lead_times = [
                    (s.actual_delivery - s.created_at).days 
                    for s in delivered
                ]
                avg_lead_time = sum(lead_times) / len(lead_times)
            else:
                avg_lead_time = 0.0
            
            # Use supplier's quality score (assumed constant over time)
            quality_score = supplier.quality_score
            
            data_point = PerformanceDataPoint(
                date=datetime.combine(week_date, datetime.min.time()),
                on_time_delivery_rate=on_time_rate,
                quality_score=quality_score,
                average_lead_time=avg_lead_time,
                shipment_count=len(shipments)
            )
            history.append(data_point)
        
        return history

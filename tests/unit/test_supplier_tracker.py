"""
Unit tests for SupplierPerformanceTracker.

Tests the supplier performance tracking functionality including metrics calculation,
on-time delivery rate, supplier ranking, and performance history.
"""

import pytest
from datetime import datetime, timedelta

from src.supplier_tracker import (
    SupplierPerformanceTracker,
    SupplierMetrics,
    SupplierRanking,
    RankingCriteria,
    PerformanceDataPoint,
)
from src.models import (
    SupplyChainData,
    Supplier,
    Shipment,
    ShipmentStatus,
)


def create_test_supplier(
    supplier_id: str = "SUP001",
    name: str = "Test Supplier",
    performance_score: float = 85.0,
    on_time_delivery_rate: float = 90.0,
    quality_score: float = 88.0,
    average_lead_time: float = 5.5,
    total_shipments: int = 100
) -> Supplier:
    """Helper to create a test supplier."""
    return Supplier(
        id=supplier_id,
        name=name,
        contact="test@supplier.com",
        performance_score=performance_score,
        on_time_delivery_rate=on_time_delivery_rate,
        quality_score=quality_score,
        average_lead_time=average_lead_time,
        total_shipments=total_shipments,
        last_updated=datetime.now()
    )


def create_test_shipment(
    shipment_id: str,
    supplier_id: str,
    estimated_delivery: datetime,
    actual_delivery: datetime = None,
    created_at: datetime = None
) -> Shipment:
    """Helper to create a test shipment."""
    if created_at is None:
        created_at = datetime.now() - timedelta(days=10)
    
    return Shipment(
        id=shipment_id,
        origin="Origin",
        destination="Destination",
        current_location="Location",
        status=ShipmentStatus.DELIVERED if actual_delivery else ShipmentStatus.IN_TRANSIT,
        estimated_delivery=estimated_delivery,
        actual_delivery=actual_delivery,
        items=["ITEM001"],
        supplier_id=supplier_id,
        created_at=created_at,
        updated_at=datetime.now()
    )


class TestSupplierPerformanceTracker:
    """Test suite for SupplierPerformanceTracker."""
    
    def test_get_supplier_metrics_returns_correct_data(self):
        """Test that get_supplier_metrics returns correct supplier data."""
        supplier = create_test_supplier("SUP001", "Supplier A")
        
        # Create shipments with 80% on-time rate
        base_date = datetime.now()
        shipments = [
            create_test_shipment(
                "SHP001", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=4)  # On time
            ),
            create_test_shipment(
                "SHP002", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=6)  # Late
            ),
            create_test_shipment(
                "SHP003", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=5)  # On time (exactly)
            ),
            create_test_shipment(
                "SHP004", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=3)  # On time (early)
            ),
            create_test_shipment(
                "SHP005", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=7)  # Late
            ),
        ]
        
        data = SupplyChainData(
            shipments=shipments,
            inventory=[],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        metrics = tracker.get_supplier_metrics("SUP001")
        
        assert metrics.supplier_id == "SUP001"
        assert metrics.supplier_name == "Supplier A"
        assert metrics.on_time_delivery_rate == 60.0  # 3 out of 5
        assert metrics.quality_score == 88.0
        assert metrics.average_lead_time == 5.5
        assert metrics.total_shipments == 100
        assert metrics.performance_score == 85.0
    
    def test_get_supplier_metrics_raises_for_invalid_supplier(self):
        """Test that get_supplier_metrics raises ValueError for non-existent supplier."""
        data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=[],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        
        with pytest.raises(ValueError, match="Supplier not found"):
            tracker.get_supplier_metrics("INVALID")
    
    def test_calculate_on_time_rate_all_on_time(self):
        """Test on-time rate calculation when all shipments are on time."""
        supplier = create_test_supplier("SUP001")
        base_date = datetime.now()
        
        shipments = [
            create_test_shipment(
                f"SHP{i:03d}", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=4)  # All on time
            )
            for i in range(1, 6)
        ]
        
        data = SupplyChainData(
            shipments=shipments,
            inventory=[],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        rate = tracker.calculate_on_time_rate("SUP001")
        
        assert rate == 100.0
    
    def test_calculate_on_time_rate_all_late(self):
        """Test on-time rate calculation when all shipments are late."""
        supplier = create_test_supplier("SUP001")
        base_date = datetime.now()
        
        shipments = [
            create_test_shipment(
                f"SHP{i:03d}", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=6)  # All late
            )
            for i in range(1, 6)
        ]
        
        data = SupplyChainData(
            shipments=shipments,
            inventory=[],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        rate = tracker.calculate_on_time_rate("SUP001")
        
        assert rate == 0.0
    
    def test_calculate_on_time_rate_no_delivered_shipments(self):
        """Test on-time rate returns 0 when no shipments are delivered."""
        supplier = create_test_supplier("SUP001")
        base_date = datetime.now()
        
        # Create shipments without actual_delivery (not delivered yet)
        shipments = [
            create_test_shipment(
                f"SHP{i:03d}", "SUP001",
                base_date + timedelta(days=5),
                None  # Not delivered
            )
            for i in range(1, 6)
        ]
        
        data = SupplyChainData(
            shipments=shipments,
            inventory=[],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        rate = tracker.calculate_on_time_rate("SUP001")
        
        assert rate == 0.0
    
    def test_calculate_on_time_rate_ignores_other_suppliers(self):
        """Test that on-time rate only considers shipments from the specified supplier."""
        supplier1 = create_test_supplier("SUP001")
        supplier2 = create_test_supplier("SUP002", "Supplier B")
        base_date = datetime.now()
        
        shipments = [
            # SUP001: 1 on-time out of 2
            create_test_shipment(
                "SHP001", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=4)  # On time
            ),
            create_test_shipment(
                "SHP002", "SUP001",
                base_date + timedelta(days=5),
                base_date + timedelta(days=6)  # Late
            ),
            # SUP002: All late (should not affect SUP001)
            create_test_shipment(
                "SHP003", "SUP002",
                base_date + timedelta(days=5),
                base_date + timedelta(days=10)  # Late
            ),
        ]
        
        data = SupplyChainData(
            shipments=shipments,
            inventory=[],
            suppliers=[supplier1, supplier2],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        rate = tracker.calculate_on_time_rate("SUP001")
        
        assert rate == 50.0  # 1 out of 2 for SUP001
    
    def test_rank_suppliers_by_on_time_rate(self):
        """Test ranking suppliers by on-time delivery rate."""
        suppliers = [
            create_test_supplier("SUP001", "Supplier A", on_time_delivery_rate=90.0),
            create_test_supplier("SUP002", "Supplier B", on_time_delivery_rate=95.0),
            create_test_supplier("SUP003", "Supplier C", on_time_delivery_rate=85.0),
        ]
        
        data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=suppliers,
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        criteria = RankingCriteria(metric="on_time_delivery_rate", ascending=False)
        rankings = tracker.rank_suppliers(criteria)
        
        assert len(rankings) == 3
        assert rankings[0].rank == 1
        assert rankings[0].supplier_id == "SUP002"
        assert rankings[0].score == 95.0
        assert rankings[1].rank == 2
        assert rankings[1].supplier_id == "SUP001"
        assert rankings[2].rank == 3
        assert rankings[2].supplier_id == "SUP003"
    
    def test_rank_suppliers_by_lead_time_ascending(self):
        """Test ranking suppliers by lead time (lower is better)."""
        suppliers = [
            create_test_supplier("SUP001", "Supplier A", average_lead_time=7.0),
            create_test_supplier("SUP002", "Supplier B", average_lead_time=5.0),
            create_test_supplier("SUP003", "Supplier C", average_lead_time=10.0),
        ]
        
        data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=suppliers,
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        criteria = RankingCriteria(metric="average_lead_time", ascending=True)
        rankings = tracker.rank_suppliers(criteria)
        
        assert len(rankings) == 3
        assert rankings[0].rank == 1
        assert rankings[0].supplier_id == "SUP002"
        assert rankings[0].score == 5.0
        assert rankings[1].rank == 2
        assert rankings[1].supplier_id == "SUP001"
        assert rankings[2].rank == 3
        assert rankings[2].supplier_id == "SUP003"
    
    def test_rank_suppliers_invalid_metric(self):
        """Test that ranking with invalid metric raises ValueError."""
        data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=[create_test_supplier("SUP001")],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        criteria = RankingCriteria(metric="invalid_metric", ascending=False)
        
        with pytest.raises(ValueError, match="Invalid metric"):
            tracker.rank_suppliers(criteria)
    
    def test_get_performance_history_returns_chronological_data(self):
        """Test that performance history is returned in chronological order."""
        supplier = create_test_supplier("SUP001")
        base_date = datetime.now()
        
        # Create shipments over 30 days
        shipments = []
        for i in range(30):
            created = base_date - timedelta(days=30-i)
            estimated = created + timedelta(days=5)
            actual = created + timedelta(days=4 if i % 2 == 0 else 6)  # Alternate on-time/late
            
            shipments.append(
                create_test_shipment(
                    f"SHP{i:03d}", "SUP001",
                    estimated, actual, created
                )
            )
        
        data = SupplyChainData(
            shipments=shipments,
            inventory=[],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        history = tracker.get_performance_history("SUP001", 30)
        
        # Should have multiple data points
        assert len(history) > 0
        
        # Check chronological order
        for i in range(len(history) - 1):
            assert history[i].date <= history[i + 1].date
    
    def test_get_performance_history_respects_date_range(self):
        """Test that performance history only includes data within specified range."""
        supplier = create_test_supplier("SUP001")
        base_date = datetime.now()
        
        # Create shipments: some old, some recent
        shipments = [
            # Old shipment (60 days ago)
            create_test_shipment(
                "SHP001", "SUP001",
                base_date - timedelta(days=55),
                base_date - timedelta(days=56),
                base_date - timedelta(days=60)
            ),
            # Recent shipment (5 days ago)
            create_test_shipment(
                "SHP002", "SUP001",
                base_date - timedelta(days=1),
                base_date - timedelta(days=2),
                base_date - timedelta(days=5)
            ),
        ]
        
        data = SupplyChainData(
            shipments=shipments,
            inventory=[],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        history = tracker.get_performance_history("SUP001", 30)
        
        # Should only include recent shipment
        assert len(history) > 0
        
        # All data points should be within the last 30 days
        cutoff_date = base_date - timedelta(days=30)
        for point in history:
            assert point.date >= cutoff_date
    
    def test_get_performance_history_no_data_returns_empty(self):
        """Test that performance history returns empty list when no data available."""
        supplier = create_test_supplier("SUP001")
        
        data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        history = tracker.get_performance_history("SUP001", 30)
        
        assert history == []
    
    def test_get_performance_history_invalid_supplier(self):
        """Test that performance history raises ValueError for invalid supplier."""
        data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=[],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        
        with pytest.raises(ValueError, match="Supplier not found"):
            tracker.get_performance_history("INVALID", 30)
    
    def test_get_performance_history_negative_days(self):
        """Test that performance history raises ValueError for negative days."""
        supplier = create_test_supplier("SUP001")
        
        data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        tracker = SupplierPerformanceTracker(data)
        
        with pytest.raises(ValueError, match="days must be non-negative"):
            tracker.get_performance_history("SUP001", -1)

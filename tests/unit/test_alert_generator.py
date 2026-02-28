"""
Unit tests for AlertGenerator.

Tests the alert generation functionality including shipment delays,
low inventory, and supplier performance alerts.
"""

import pytest
from datetime import datetime, timedelta
from src.alert_generator import AlertGenerator
from src.models import (
    Alert,
    AlertType,
    AlertSeverity,
    Shipment,
    InventoryItem,
    Supplier,
    SupplyChainData,
    ShipmentStatus,
)


class TestAlertGenerator:
    """Test suite for AlertGenerator class."""
    
    def test_init(self):
        """Test AlertGenerator initialization."""
        generator = AlertGenerator()
        assert generator is not None
        assert generator._alerts == {}
    
    def test_check_shipment_delays_with_delayed_status(self):
        """Test alert generation for shipments with DELAYED status."""
        generator = AlertGenerator()
        now = datetime.now()
        
        shipment = Shipment(
            id="S001",
            origin="New York",
            destination="Los Angeles",
            current_location="Chicago",
            status=ShipmentStatus.DELAYED,
            estimated_delivery=now - timedelta(hours=12),
            actual_delivery=None,
            items=["item1"],
            supplier_id="SUP001",
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        alerts = generator.check_shipment_delays([shipment], delay_threshold_hours=24)
        
        assert len(alerts) == 1
        assert alerts[0].type == AlertType.SHIPMENT_DELAY
        assert alerts[0].entity_id == "S001"
        assert "delayed" in alerts[0].message.lower()
        assert not alerts[0].acknowledged
    
    def test_check_shipment_delays_overdue(self):
        """Test alert generation for shipments past estimated delivery."""
        generator = AlertGenerator()
        now = datetime.now()
        
        shipment = Shipment(
            id="S002",
            origin="Boston",
            destination="Miami",
            current_location="Atlanta",
            status=ShipmentStatus.IN_TRANSIT,
            estimated_delivery=now - timedelta(hours=48),
            actual_delivery=None,
            items=["item2"],
            supplier_id="SUP002",
            created_at=now - timedelta(days=3),
            updated_at=now
        )
        
        alerts = generator.check_shipment_delays([shipment], delay_threshold_hours=24)
        
        assert len(alerts) == 1
        assert alerts[0].type == AlertType.SHIPMENT_DELAY
        assert "overdue" in alerts[0].message.lower()
        assert alerts[0].severity in [AlertSeverity.MEDIUM, AlertSeverity.HIGH]
    
    def test_check_shipment_delays_no_alert_for_delivered(self):
        """Test no alert for delivered shipments."""
        generator = AlertGenerator()
        now = datetime.now()
        
        shipment = Shipment(
            id="S003",
            origin="Seattle",
            destination="Portland",
            current_location="Portland",
            status=ShipmentStatus.DELIVERED,
            estimated_delivery=now - timedelta(hours=48),
            actual_delivery=now - timedelta(hours=24),
            items=["item3"],
            supplier_id="SUP003",
            created_at=now - timedelta(days=3),
            updated_at=now
        )
        
        alerts = generator.check_shipment_delays([shipment], delay_threshold_hours=24)
        
        assert len(alerts) == 0
    
    def test_check_shipment_delays_no_alert_within_threshold(self):
        """Test no alert for shipments within threshold."""
        generator = AlertGenerator()
        now = datetime.now()
        
        shipment = Shipment(
            id="S004",
            origin="Denver",
            destination="Phoenix",
            current_location="Albuquerque",
            status=ShipmentStatus.IN_TRANSIT,
            estimated_delivery=now + timedelta(hours=12),
            actual_delivery=None,
            items=["item4"],
            supplier_id="SUP004",
            created_at=now - timedelta(days=1),
            updated_at=now
        )
        
        alerts = generator.check_shipment_delays([shipment], delay_threshold_hours=24)
        
        assert len(alerts) == 0
    
    def test_check_inventory_levels_below_threshold(self):
        """Test alert generation for low inventory."""
        generator = AlertGenerator()
        now = datetime.now()
        
        item = InventoryItem(
            id="INV001",
            name="Widget A",
            category="Electronics",
            location="Warehouse 1",
            quantity=50.0,
            unit="pieces",
            reorder_point=100.0,
            last_updated=now
        )
        
        alerts = generator.check_inventory_levels([item], low_stock_threshold=1.0)
        
        assert len(alerts) == 1
        assert alerts[0].type == AlertType.LOW_STOCK
        assert alerts[0].entity_id == "INV001"
        assert "low stock" in alerts[0].message.lower()
        assert "Widget A" in alerts[0].message
    
    def test_check_inventory_levels_critical(self):
        """Test critical severity for very low inventory."""
        generator = AlertGenerator()
        now = datetime.now()
        
        item = InventoryItem(
            id="INV002",
            name="Widget B",
            category="Electronics",
            location="Warehouse 2",
            quantity=10.0,
            unit="pieces",
            reorder_point=100.0,
            last_updated=now
        )
        
        alerts = generator.check_inventory_levels([item], low_stock_threshold=1.0)
        
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_check_inventory_levels_no_alert_above_threshold(self):
        """Test no alert for inventory above threshold."""
        generator = AlertGenerator()
        now = datetime.now()
        
        item = InventoryItem(
            id="INV003",
            name="Widget C",
            category="Electronics",
            location="Warehouse 3",
            quantity=150.0,
            unit="pieces",
            reorder_point=100.0,
            last_updated=now
        )
        
        alerts = generator.check_inventory_levels([item], low_stock_threshold=1.0)
        
        assert len(alerts) == 0
    
    def test_check_supplier_performance_below_threshold(self):
        """Test alert generation for underperforming suppliers."""
        generator = AlertGenerator()
        now = datetime.now()
        
        supplier = Supplier(
            id="SUP001",
            name="Acme Corp",
            contact="contact@acme.com",
            performance_score=60.0,
            on_time_delivery_rate=65.0,
            quality_score=70.0,
            average_lead_time=5.0,
            total_shipments=100,
            last_updated=now
        )
        
        alerts = generator.check_supplier_performance([supplier], performance_threshold=70.0)
        
        assert len(alerts) == 1
        assert alerts[0].type == AlertType.SUPPLIER_PERFORMANCE
        assert alerts[0].entity_id == "SUP001"
        assert "Acme Corp" in alerts[0].message
        assert "60.0" in alerts[0].message
    
    def test_check_supplier_performance_no_alert_above_threshold(self):
        """Test no alert for suppliers above threshold."""
        generator = AlertGenerator()
        now = datetime.now()
        
        supplier = Supplier(
            id="SUP002",
            name="Best Supplies",
            contact="contact@best.com",
            performance_score=85.0,
            on_time_delivery_rate=90.0,
            quality_score=88.0,
            average_lead_time=3.0,
            total_shipments=200,
            last_updated=now
        )
        
        alerts = generator.check_supplier_performance([supplier], performance_threshold=70.0)
        
        assert len(alerts) == 0
    
    def test_generate_alerts_comprehensive(self):
        """Test generate_alerts with all alert types."""
        generator = AlertGenerator()
        now = datetime.now()
        
        # Create test data
        shipment = Shipment(
            id="S001",
            origin="New York",
            destination="Los Angeles",
            current_location="Chicago",
            status=ShipmentStatus.DELAYED,
            estimated_delivery=now - timedelta(hours=48),
            actual_delivery=None,
            items=["item1"],
            supplier_id="SUP001",
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        item = InventoryItem(
            id="INV001",
            name="Widget A",
            category="Electronics",
            location="Warehouse 1",
            quantity=30.0,
            unit="pieces",
            reorder_point=100.0,
            last_updated=now
        )
        
        supplier = Supplier(
            id="SUP001",
            name="Acme Corp",
            contact="contact@acme.com",
            performance_score=50.0,
            on_time_delivery_rate=55.0,
            quality_score=60.0,
            average_lead_time=7.0,
            total_shipments=50,
            last_updated=now
        )
        
        data = SupplyChainData(
            shipments=[shipment],
            inventory=[item],
            suppliers=[supplier],
            nodes=[],
            edges=[],
            last_updated=now
        )
        
        rules = {
            'delay_threshold_hours': 24,
            'low_stock_threshold': 1.0,
            'supplier_performance_threshold': 70.0
        }
        
        alerts = generator.generate_alerts(data, rules)
        
        # Should have 3 alerts: shipment delay, low stock, supplier performance
        assert len(alerts) == 3
        alert_types = {alert.type for alert in alerts}
        assert AlertType.SHIPMENT_DELAY in alert_types
        assert AlertType.LOW_STOCK in alert_types
        assert AlertType.SUPPLIER_PERFORMANCE in alert_types
    
    def test_acknowledge_alert(self):
        """Test alert acknowledgment."""
        generator = AlertGenerator()
        now = datetime.now()
        
        # Create and generate an alert
        shipment = Shipment(
            id="S001",
            origin="New York",
            destination="Los Angeles",
            current_location="Chicago",
            status=ShipmentStatus.DELAYED,
            estimated_delivery=now - timedelta(hours=12),
            actual_delivery=None,
            items=["item1"],
            supplier_id="SUP001",
            created_at=now - timedelta(days=2),
            updated_at=now
        )
        
        data = SupplyChainData(
            shipments=[shipment],
            inventory=[],
            suppliers=[],
            nodes=[],
            edges=[],
            last_updated=now
        )
        
        alerts = generator.generate_alerts(data, {'delay_threshold_hours': 24})
        assert len(alerts) == 1
        
        alert_id = alerts[0].id
        assert not alerts[0].acknowledged
        assert alerts[0].acknowledged_at is None
        
        # Acknowledge the alert
        generator.acknowledge_alert(alert_id)
        
        # Verify acknowledgment
        acknowledged_alert = generator._alerts[alert_id]
        assert acknowledged_alert.acknowledged
        assert acknowledged_alert.acknowledged_at is not None
    
    def test_acknowledge_alert_not_found(self):
        """Test acknowledging non-existent alert raises error."""
        generator = AlertGenerator()
        
        with pytest.raises(ValueError, match="Alert not found"):
            generator.acknowledge_alert("non-existent-id")
    
    def test_empty_data(self):
        """Test generate_alerts with empty data."""
        generator = AlertGenerator()
        now = datetime.now()
        
        data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=[],
            nodes=[],
            edges=[],
            last_updated=now
        )
        
        alerts = generator.generate_alerts(data, {})
        
        assert len(alerts) == 0

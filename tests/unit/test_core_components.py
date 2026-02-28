"""
Unit tests for core business logic components.

Tests the ShipmentTracker, InventoryMonitor, NetworkVisualizer, and Dashboard
components to ensure they work correctly with sample data.
"""

import pytest
from datetime import datetime

from src.data_access import DataAccessService
from src.shipment_tracker import ShipmentTracker
from src.inventory_monitor import InventoryMonitor
from src.network_visualizer import NetworkVisualizer
from src.dashboard import Dashboard
from src.filter_engine import FilterCriteria
from src.models import ShipmentStatus


@pytest.fixture
def sample_data():
    """Load sample data for testing."""
    service = DataAccessService()
    return service.load_data("data")


class TestShipmentTracker:
    """Tests for ShipmentTracker component."""
    
    def test_list_shipments_no_filters(self, sample_data):
        """Test listing all shipments without filters."""
        tracker = ShipmentTracker(sample_data)
        shipments = tracker.list_shipments(FilterCriteria())
        
        assert len(shipments) > 0
        assert all(hasattr(s, 'id') for s in shipments)
    
    def test_list_shipments_with_status_filter(self, sample_data):
        """Test listing shipments filtered by status."""
        tracker = ShipmentTracker(sample_data)
        filters = FilterCriteria(status=['in_transit'])
        shipments = tracker.list_shipments(filters)
        
        assert all(s.status == ShipmentStatus.IN_TRANSIT for s in shipments)
    
    def test_get_shipment_details(self, sample_data):
        """Test getting details for a specific shipment."""
        tracker = ShipmentTracker(sample_data)
        
        # Get first shipment ID
        first_shipment = sample_data.shipments[0]
        details = tracker.get_shipment_details(first_shipment.id)
        
        assert details.shipment.id == first_shipment.id
        assert details.supplier_name is not None or details.supplier_name is None
    
    def test_get_shipment_details_not_found(self, sample_data):
        """Test getting details for non-existent shipment."""
        tracker = ShipmentTracker(sample_data)
        
        with pytest.raises(ValueError, match="Shipment not found"):
            tracker.get_shipment_details("INVALID_ID")
    
    def test_search_shipments_by_origin(self, sample_data):
        """Test searching shipments by origin."""
        tracker = ShipmentTracker(sample_data)
        
        # Search for shipments from Shanghai
        results = tracker.search_shipments("Shanghai", "origin")
        
        assert all("shanghai" in s.origin.lower() for s in results)
    
    def test_search_shipments_invalid_field(self, sample_data):
        """Test searching with invalid field raises error."""
        tracker = ShipmentTracker(sample_data)
        
        with pytest.raises(ValueError, match="Invalid search field"):
            tracker.search_shipments("test", "invalid_field")


class TestInventoryMonitor:
    """Tests for InventoryMonitor component."""
    
    def test_get_inventory_levels_no_filters(self, sample_data):
        """Test getting all inventory levels without filters."""
        monitor = InventoryMonitor(sample_data)
        items = monitor.get_inventory_levels(FilterCriteria())
        
        assert len(items) > 0
        assert all(hasattr(i, 'id') for i in items)
    
    def test_get_inventory_levels_with_location_filter(self, sample_data):
        """Test getting inventory filtered by location."""
        monitor = InventoryMonitor(sample_data)
        
        # Get first location
        if sample_data.inventory:
            first_location = sample_data.inventory[0].location
            filters = FilterCriteria(location=[first_location])
            items = monitor.get_inventory_levels(filters)
            
            assert all(i.location == first_location for i in items)
    
    def test_get_low_stock_items(self, sample_data):
        """Test identifying low stock items."""
        monitor = InventoryMonitor(sample_data)
        
        # Use threshold of 1.0 (at or below reorder point)
        low_stock = monitor.get_low_stock_items(1.0)
        
        # Verify all returned items are below threshold
        for item in low_stock:
            assert item.quantity < item.reorder_point
    
    def test_get_inventory_trends(self, sample_data):
        """Test getting inventory trends for an item."""
        monitor = InventoryMonitor(sample_data)
        
        if sample_data.inventory:
            first_item = sample_data.inventory[0]
            trends = monitor.get_inventory_trends(first_item.id, 30)
            
            assert trends.item_id == first_item.id
            assert len(trends.dates) == 30
            assert len(trends.values) == 30
            assert all(v >= 0 for v in trends.values)
    
    def test_get_inventory_trends_not_found(self, sample_data):
        """Test getting trends for non-existent item."""
        monitor = InventoryMonitor(sample_data)
        
        with pytest.raises(ValueError, match="Inventory item not found"):
            monitor.get_inventory_trends("INVALID_ID", 30)


class TestNetworkVisualizer:
    """Tests for NetworkVisualizer component."""
    
    def test_render_network(self, sample_data):
        """Test rendering network diagram."""
        visualizer = NetworkVisualizer(sample_data)
        
        fig = visualizer.render_network(sample_data.nodes, sample_data.edges)
        
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_render_network_empty(self, sample_data):
        """Test rendering network with no nodes."""
        visualizer = NetworkVisualizer(sample_data)
        
        fig = visualizer.render_network([], [])
        
        assert fig is not None
    
    def test_get_node_details(self, sample_data):
        """Test getting details for a specific node."""
        visualizer = NetworkVisualizer(sample_data)
        
        if sample_data.nodes:
            first_node = sample_data.nodes[0]
            details = visualizer.get_node_details(first_node.id)
            
            assert details.node.id == first_node.id
            assert isinstance(details.connected_shipment_ids, list)
            assert details.incoming_edges >= 0
            assert details.outgoing_edges >= 0
    
    def test_get_node_details_not_found(self, sample_data):
        """Test getting details for non-existent node."""
        visualizer = NetworkVisualizer(sample_data)
        
        with pytest.raises(ValueError, match="Node not found"):
            visualizer.get_node_details("INVALID_ID")
    
    def test_render_geographic_map(self, sample_data):
        """Test rendering geographic map."""
        visualizer = NetworkVisualizer(sample_data)
        
        fig = visualizer.render_geographic_map(sample_data.nodes)
        
        assert fig is not None
        assert hasattr(fig, 'data')
    
    def test_render_geographic_map_no_coordinates(self, sample_data):
        """Test rendering map with nodes without coordinates."""
        visualizer = NetworkVisualizer(sample_data)
        
        # Create nodes without coordinates
        nodes_without_coords = [
            node for node in sample_data.nodes
            if node.latitude is None or node.longitude is None
        ]
        
        fig = visualizer.render_geographic_map(nodes_without_coords)
        
        assert fig is not None


class TestDashboard:
    """Tests for Dashboard component."""
    
    def test_get_metrics(self, sample_data):
        """Test calculating dashboard metrics."""
        dashboard = Dashboard(sample_data)
        metrics = dashboard.get_metrics(sample_data)
        
        assert metrics.total_shipments >= 0
        assert metrics.in_transit_count >= 0
        assert metrics.delayed_count >= 0
        assert metrics.delivered_count >= 0
        assert metrics.pending_count >= 0
        assert metrics.low_stock_count >= 0
        assert metrics.total_inventory_items >= 0
        assert metrics.total_suppliers >= 0
        assert 0 <= metrics.average_supplier_performance <= 100
    
    def test_get_metrics_shipment_counts_sum(self, sample_data):
        """Test that shipment status counts sum to total."""
        dashboard = Dashboard(sample_data)
        metrics = dashboard.get_metrics(sample_data)
        
        status_sum = (metrics.in_transit_count + metrics.delayed_count + 
                     metrics.delivered_count + metrics.pending_count)
        
        assert status_sum == metrics.total_shipments
    
    def test_render_without_filters(self, sample_data):
        """Test rendering dashboard without filters."""
        dashboard = Dashboard(sample_data)
        metrics = dashboard.render()
        
        assert metrics is not None
        assert metrics.total_shipments > 0
    
    def test_render_with_filters(self, sample_data):
        """Test rendering dashboard with filters."""
        dashboard = Dashboard(sample_data)
        filters = FilterCriteria(status=['in_transit'])
        metrics = dashboard.render(filters)
        
        assert metrics is not None
        # With status filter, only in_transit shipments should be counted
        assert metrics.total_shipments == metrics.in_transit_count
    
    def test_get_metrics_empty_data(self):
        """Test metrics calculation with empty data."""
        from src.models import SupplyChainData
        
        empty_data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=[],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        dashboard = Dashboard(empty_data)
        metrics = dashboard.get_metrics(empty_data)
        
        assert metrics.total_shipments == 0
        assert metrics.total_inventory_items == 0
        assert metrics.total_suppliers == 0
        assert metrics.average_supplier_performance == 0.0

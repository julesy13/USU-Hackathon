"""
Unit tests for FilterEngine.

Tests the filtering and searching functionality of the FilterEngine class.
"""

import pytest
from datetime import datetime, timedelta

from src.filter_engine import FilterEngine, FilterCriteria
from src.models import (
    SupplyChainData,
    Shipment,
    InventoryItem,
    Supplier,
    Node,
    Edge,
    ShipmentStatus,
    NodeType,
    NodeStatus,
)


@pytest.fixture
def sample_data():
    """Create sample supply chain data for testing."""
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)
    
    shipments = [
        Shipment(
            id="S1",
            origin="New York",
            destination="Los Angeles",
            current_location="Chicago",
            status=ShipmentStatus.IN_TRANSIT,
            estimated_delivery=tomorrow,
            actual_delivery=None,
            items=["item1", "item2"],
            supplier_id="SUP1",
            created_at=yesterday,
            updated_at=now
        ),
        Shipment(
            id="S2",
            origin="Boston",
            destination="Seattle",
            current_location="Denver",
            status=ShipmentStatus.DELAYED,
            estimated_delivery=now,
            actual_delivery=None,
            items=["item3"],
            supplier_id="SUP2",
            created_at=yesterday,
            updated_at=now
        ),
        Shipment(
            id="S3",
            origin="Miami",
            destination="Portland",
            current_location="Portland",
            status=ShipmentStatus.DELIVERED,
            estimated_delivery=yesterday,
            actual_delivery=now,
            items=["item4"],
            supplier_id="SUP1",
            created_at=yesterday - timedelta(days=2),
            updated_at=now
        ),
    ]
    
    inventory = [
        InventoryItem(
            id="I1",
            name="Widget A",
            category="Electronics",
            location="New York",
            quantity=100.0,
            unit="pieces",
            reorder_point=20.0,
            last_updated=now
        ),
        InventoryItem(
            id="I2",
            name="Widget B",
            category="Hardware",
            location="Los Angeles",
            quantity=50.0,
            unit="pieces",
            reorder_point=10.0,
            last_updated=yesterday
        ),
        InventoryItem(
            id="I3",
            name="Gadget C",
            category="Electronics",
            location="Chicago",
            quantity=15.0,
            unit="pieces",
            reorder_point=25.0,
            last_updated=now
        ),
    ]
    
    suppliers = [
        Supplier(
            id="SUP1",
            name="Acme Corp",
            contact="acme@example.com",
            performance_score=85.0,
            on_time_delivery_rate=90.0,
            quality_score=88.0,
            average_lead_time=5.0,
            total_shipments=100,
            last_updated=now
        ),
        Supplier(
            id="SUP2",
            name="Global Supplies",
            contact="global@example.com",
            performance_score=75.0,
            on_time_delivery_rate=80.0,
            quality_score=78.0,
            average_lead_time=7.0,
            total_shipments=50,
            last_updated=yesterday
        ),
    ]
    
    nodes = [
        Node(
            id="N1",
            name="NYC Warehouse",
            type=NodeType.WAREHOUSE,
            location="New York",
            latitude=40.7128,
            longitude=-74.0060,
            status=NodeStatus.NORMAL,
            capacity=1000.0
        ),
        Node(
            id="N2",
            name="LA Distribution",
            type=NodeType.WAREHOUSE,
            location="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
            status=NodeStatus.CONGESTED,
            capacity=800.0
        ),
        Node(
            id="N3",
            name="Chicago Hub",
            type=NodeType.WAREHOUSE,
            location="Chicago",
            latitude=41.8781,
            longitude=-87.6298,
            status=NodeStatus.NORMAL,
            capacity=1200.0
        ),
    ]
    
    edges = [
        Edge(
            id="E1",
            source_node_id="N1",
            target_node_id="N3",
            shipment_ids=["S1"],
            active=True
        ),
        Edge(
            id="E2",
            source_node_id="N3",
            target_node_id="N2",
            shipment_ids=["S1"],
            active=True
        ),
    ]
    
    return SupplyChainData(
        shipments=shipments,
        inventory=inventory,
        suppliers=suppliers,
        nodes=nodes,
        edges=edges,
        last_updated=now
    )


@pytest.fixture
def filter_engine():
    """Create a FilterEngine instance."""
    return FilterEngine()


class TestFilterCriteria:
    """Tests for FilterCriteria dataclass."""
    
    def test_default_filter_criteria(self):
        """Test that default FilterCriteria has all fields as None."""
        criteria = FilterCriteria()
        assert criteria.date_range is None
        assert criteria.status is None
        assert criteria.location is None
        assert criteria.category is None
        assert criteria.search_query is None
        assert criteria.search_fields is None
    
    def test_filter_criteria_with_values(self):
        """Test FilterCriteria with specified values."""
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        
        criteria = FilterCriteria(
            date_range=(now, tomorrow),
            status=["in_transit", "delayed"],
            location=["New York", "Chicago"],
            category=["Electronics"],
            search_query="widget",
            search_fields=["name", "id"]
        )
        
        assert criteria.date_range == (now, tomorrow)
        assert criteria.status == ["in_transit", "delayed"]
        assert criteria.location == ["New York", "Chicago"]
        assert criteria.category == ["Electronics"]
        assert criteria.search_query == "widget"
        assert criteria.search_fields == ["name", "id"]


class TestResetFilters:
    """Tests for reset_filters method."""
    
    def test_reset_filters_returns_empty_criteria(self, filter_engine):
        """Test that reset_filters returns FilterCriteria with all None values."""
        criteria = filter_engine.reset_filters()
        
        assert isinstance(criteria, FilterCriteria)
        assert criteria.date_range is None
        assert criteria.status is None
        assert criteria.location is None
        assert criteria.category is None
        assert criteria.search_query is None
        assert criteria.search_fields is None


class TestApplyFilters:
    """Tests for apply_filters method."""
    
    def test_apply_no_filters(self, filter_engine, sample_data):
        """Test that applying empty filters returns all data."""
        criteria = FilterCriteria()
        result = filter_engine.apply_filters(sample_data, criteria)
        
        assert len(result.shipments) == 3
        assert len(result.inventory) == 3
        assert len(result.suppliers) == 2
        assert len(result.nodes) == 3
        assert len(result.edges) == 2
    
    def test_filter_shipments_by_status(self, filter_engine, sample_data):
        """Test filtering shipments by status."""
        criteria = FilterCriteria(status=["in_transit"])
        result = filter_engine.apply_filters(sample_data, criteria)
        
        assert len(result.shipments) == 1
        assert result.shipments[0].id == "S1"
        assert result.shipments[0].status == ShipmentStatus.IN_TRANSIT
    
    def test_filter_shipments_by_multiple_statuses(self, filter_engine, sample_data):
        """Test filtering shipments by multiple statuses."""
        criteria = FilterCriteria(status=["in_transit", "delayed"])
        result = filter_engine.apply_filters(sample_data, criteria)
        
        assert len(result.shipments) == 2
        shipment_ids = {s.id for s in result.shipments}
        assert shipment_ids == {"S1", "S2"}
    
    def test_filter_shipments_by_location(self, filter_engine, sample_data):
        """Test filtering shipments by location."""
        criteria = FilterCriteria(location=["Chicago"])
        result = filter_engine.apply_filters(sample_data, criteria)
        
        # Should match shipments with Chicago as origin, destination, or current_location
        assert len(result.shipments) == 1
        assert result.shipments[0].id == "S1"
    
    def test_filter_shipments_by_date_range(self, filter_engine, sample_data):
        """Test filtering shipments by date range."""
        now = datetime.now()
        future = now + timedelta(days=2)
        
        criteria = FilterCriteria(date_range=(now, future))
        result = filter_engine.apply_filters(sample_data, criteria)
        
        # Should include shipments with estimated_delivery in range
        assert len(result.shipments) >= 1
        for shipment in result.shipments:
            assert now <= shipment.estimated_delivery <= future
    
    def test_filter_inventory_by_location(self, filter_engine, sample_data):
        """Test filtering inventory by location."""
        criteria = FilterCriteria(location=["New York"])
        result = filter_engine.apply_filters(sample_data, criteria)
        
        assert len(result.inventory) == 1
        assert result.inventory[0].id == "I1"
        assert result.inventory[0].location == "New York"
    
    def test_filter_inventory_by_category(self, filter_engine, sample_data):
        """Test filtering inventory by category."""
        criteria = FilterCriteria(category=["Electronics"])
        result = filter_engine.apply_filters(sample_data, criteria)
        
        assert len(result.inventory) == 2
        inventory_ids = {i.id for i in result.inventory}
        assert inventory_ids == {"I1", "I3"}
    
    def test_filter_nodes_by_status(self, filter_engine, sample_data):
        """Test filtering nodes by status."""
        criteria = FilterCriteria(status=["normal"])
        result = filter_engine.apply_filters(sample_data, criteria)
        
        assert len(result.nodes) == 2
        node_ids = {n.id for n in result.nodes}
        assert node_ids == {"N1", "N3"}
    
    def test_filter_nodes_by_location(self, filter_engine, sample_data):
        """Test filtering nodes by location."""
        criteria = FilterCriteria(location=["Chicago"])
        result = filter_engine.apply_filters(sample_data, criteria)
        
        assert len(result.nodes) == 1
        assert result.nodes[0].id == "N3"
        assert result.nodes[0].location == "Chicago"
    
    def test_filter_edges_with_nodes(self, filter_engine, sample_data):
        """Test that edges are filtered to match filtered nodes."""
        # Filter to only include N1 and N3 nodes
        criteria = FilterCriteria(location=["New York", "Chicago"])
        result = filter_engine.apply_filters(sample_data, criteria)
        
        # Should have 2 nodes (N1 and N3)
        assert len(result.nodes) == 2
        node_ids = {n.id for n in result.nodes}
        assert node_ids == {"N1", "N3"}
        
        # Should have 1 edge (E1 connecting N1 to N3)
        assert len(result.edges) == 1
        assert result.edges[0].id == "E1"
    
    def test_combined_filters(self, filter_engine, sample_data):
        """Test applying multiple filters together."""
        criteria = FilterCriteria(
            status=["in_transit", "delayed"],
            location=["Chicago", "Denver"]
        )
        result = filter_engine.apply_filters(sample_data, criteria)
        
        # Shipments: should match status AND location
        assert len(result.shipments) == 2
        shipment_ids = {s.id for s in result.shipments}
        assert shipment_ids == {"S1", "S2"}


class TestSearch:
    """Tests for search method."""
    
    def test_search_shipments_by_id(self, filter_engine, sample_data):
        """Test searching shipments by ID."""
        result = filter_engine.search(sample_data, "S1", ["id"])
        
        assert len(result.shipments) == 1
        assert result.shipments[0].id == "S1"
    
    def test_search_shipments_by_origin(self, filter_engine, sample_data):
        """Test searching shipments by origin."""
        result = filter_engine.search(sample_data, "New York", ["origin"])
        
        assert len(result.shipments) == 1
        assert result.shipments[0].origin == "New York"
    
    def test_search_shipments_case_insensitive(self, filter_engine, sample_data):
        """Test that search is case-insensitive."""
        result = filter_engine.search(sample_data, "new york", ["origin"])
        
        assert len(result.shipments) == 1
        assert result.shipments[0].origin == "New York"
    
    def test_search_inventory_by_name(self, filter_engine, sample_data):
        """Test searching inventory by name."""
        result = filter_engine.search(sample_data, "Widget", ["name"])
        
        assert len(result.inventory) == 2
        inventory_ids = {i.id for i in result.inventory}
        assert inventory_ids == {"I1", "I2"}
    
    def test_search_suppliers_by_name(self, filter_engine, sample_data):
        """Test searching suppliers by name."""
        result = filter_engine.search(sample_data, "Acme", ["name"])
        
        assert len(result.suppliers) == 1
        assert result.suppliers[0].id == "SUP1"
    
    def test_search_nodes_by_name(self, filter_engine, sample_data):
        """Test searching nodes by name."""
        result = filter_engine.search(sample_data, "NYC", ["name"])
        
        assert len(result.nodes) == 1
        assert result.nodes[0].id == "N1"
    
    def test_search_multiple_fields(self, filter_engine, sample_data):
        """Test searching across multiple fields."""
        result = filter_engine.search(sample_data, "Chicago", ["origin", "destination", "current_location"])
        
        # Should find S1 (current_location is Chicago)
        assert len(result.shipments) >= 1
        assert any(s.id == "S1" for s in result.shipments)
    
    def test_search_with_empty_query(self, filter_engine, sample_data):
        """Test that empty query returns all data."""
        result = filter_engine.search(sample_data, "", ["name"])
        
        assert len(result.shipments) == 3
        assert len(result.inventory) == 3
        assert len(result.suppliers) == 2
        assert len(result.nodes) == 3
    
    def test_search_with_no_fields(self, filter_engine, sample_data):
        """Test that search with no fields returns all data."""
        result = filter_engine.search(sample_data, "test", [])
        
        assert len(result.shipments) == 3
        assert len(result.inventory) == 3
        assert len(result.suppliers) == 2
        assert len(result.nodes) == 3
    
    def test_search_no_matches(self, filter_engine, sample_data):
        """Test search with no matching results."""
        result = filter_engine.search(sample_data, "nonexistent", ["name", "id"])
        
        assert len(result.shipments) == 0
        assert len(result.inventory) == 0
        assert len(result.suppliers) == 0
        assert len(result.nodes) == 0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_empty_data(self, filter_engine):
        """Test filtering empty data."""
        empty_data = SupplyChainData(
            shipments=[],
            inventory=[],
            suppliers=[],
            nodes=[],
            edges=[],
            last_updated=datetime.now()
        )
        
        criteria = FilterCriteria(status=["in_transit"])
        result = filter_engine.apply_filters(empty_data, criteria)
        
        assert len(result.shipments) == 0
        assert len(result.inventory) == 0
        assert len(result.suppliers) == 0
        assert len(result.nodes) == 0
        assert len(result.edges) == 0
    
    def test_filter_with_nonexistent_field(self, filter_engine, sample_data):
        """Test search with nonexistent field name."""
        # Should not raise error, just return no matches for that field
        result = filter_engine.search(sample_data, "test", ["nonexistent_field"])
        
        assert len(result.shipments) == 0
        assert len(result.inventory) == 0
        assert len(result.suppliers) == 0
        assert len(result.nodes) == 0

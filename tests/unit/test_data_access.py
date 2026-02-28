"""
Unit tests for DataAccessService.

Tests the data loading, caching, refresh, and persistence functionality
of the data access layer.
"""

import csv
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.data_access import DataAccessService
from src.models import (
    StatusUpdate,
    ShipmentStatus,
    NodeType,
    NodeStatus,
)


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory with sample CSV files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        
        # Create sample shipments.csv
        shipments_file = data_dir / "shipments.csv"
        with open(shipments_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'origin', 'destination', 'current_location', 'status',
                'estimated_delivery', 'actual_delivery', 'items', 'supplier_id',
                'created_at', 'updated_at'
            ])
            writer.writeheader()
            writer.writerow({
                'id': 'SH001',
                'origin': 'New York',
                'destination': 'Los Angeles',
                'current_location': 'Chicago',
                'status': 'in_transit',
                'estimated_delivery': '2024-01-15T10:00:00',
                'actual_delivery': '',
                'items': 'ITEM001;ITEM002',
                'supplier_id': 'SUP001',
                'created_at': '2024-01-10T08:00:00',
                'updated_at': '2024-01-12T14:30:00'
            })
        
        # Create sample inventory.csv
        inventory_file = data_dir / "inventory.csv"
        with open(inventory_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'category', 'location', 'quantity',
                'unit', 'reorder_point', 'last_updated'
            ])
            writer.writeheader()
            writer.writerow({
                'id': 'INV001',
                'name': 'Widget A',
                'category': 'Electronics',
                'location': 'Warehouse 1',
                'quantity': '100',
                'unit': 'pieces',
                'reorder_point': '20',
                'last_updated': '2024-01-12T10:00:00'
            })
        
        # Create sample suppliers.csv
        suppliers_file = data_dir / "suppliers.csv"
        with open(suppliers_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'contact', 'performance_score',
                'on_time_delivery_rate', 'quality_score', 'average_lead_time',
                'total_shipments', 'last_updated'
            ])
            writer.writeheader()
            writer.writerow({
                'id': 'SUP001',
                'name': 'Acme Corp',
                'contact': 'contact@acme.com',
                'performance_score': '85.5',
                'on_time_delivery_rate': '90.0',
                'quality_score': '88.0',
                'average_lead_time': '5.5',
                'total_shipments': '100',
                'last_updated': '2024-01-12T10:00:00'
            })
        
        # Create sample nodes.csv
        nodes_file = data_dir / "nodes.csv"
        with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'type', 'location', 'latitude', 'longitude',
                'status', 'capacity'
            ])
            writer.writeheader()
            writer.writerow({
                'id': 'NODE001',
                'name': 'Main Warehouse',
                'type': 'warehouse',
                'location': 'New York',
                'latitude': '40.7128',
                'longitude': '-74.0060',
                'status': 'normal',
                'capacity': '10000'
            })
        
        # Create sample edges.csv
        edges_file = data_dir / "edges.csv"
        with open(edges_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'source_node_id', 'target_node_id', 'shipment_ids', 'active'
            ])
            writer.writeheader()
            writer.writerow({
                'id': 'EDGE001',
                'source_node_id': 'NODE001',
                'target_node_id': 'NODE002',
                'shipment_ids': 'SH001;SH002',
                'active': 'true'
            })
        
        yield data_dir


@pytest.fixture
def data_service():
    """Create a DataAccessService instance."""
    return DataAccessService()


def test_load_data_from_csv(data_service, temp_data_dir):
    """Test loading data from CSV files."""
    data = data_service.load_data(str(temp_data_dir))
    
    # Verify data was loaded
    assert len(data.shipments) == 1
    assert len(data.inventory) == 1
    assert len(data.suppliers) == 1
    assert len(data.nodes) == 1
    assert len(data.edges) == 1
    
    # Verify shipment data
    shipment = data.shipments[0]
    assert shipment.id == 'SH001'
    assert shipment.origin == 'New York'
    assert shipment.destination == 'Los Angeles'
    assert shipment.status == ShipmentStatus.IN_TRANSIT
    assert len(shipment.items) == 2
    
    # Verify inventory data
    item = data.inventory[0]
    assert item.id == 'INV001'
    assert item.name == 'Widget A'
    assert item.quantity == 100.0
    
    # Verify supplier data
    supplier = data.suppliers[0]
    assert supplier.id == 'SUP001'
    assert supplier.name == 'Acme Corp'
    assert supplier.performance_score == 85.5
    
    # Verify node data
    node = data.nodes[0]
    assert node.id == 'NODE001'
    assert node.type == NodeType.WAREHOUSE
    assert node.status == NodeStatus.NORMAL
    
    # Verify edge data
    edge = data.edges[0]
    assert edge.id == 'EDGE001'
    assert edge.active is True
    assert len(edge.shipment_ids) == 2


def test_load_data_nonexistent_source(data_service):
    """Test loading data from nonexistent source raises error."""
    with pytest.raises(FileNotFoundError):
        data_service.load_data("/nonexistent/path")


def test_get_cached_data_empty(data_service):
    """Test getting cached data when cache is empty."""
    cached = data_service.get_cached_data()
    assert cached is None


def test_get_cached_data_after_load(data_service, temp_data_dir):
    """Test getting cached data after loading."""
    # Load data
    data = data_service.load_data(str(temp_data_dir))
    
    # Get cached data
    cached = data_service.get_cached_data()
    
    assert cached is not None
    assert cached == data
    assert len(cached.shipments) == 1


def test_refresh_data(data_service, temp_data_dir):
    """Test refreshing data from source."""
    # Initial load
    data1 = data_service.load_data(str(temp_data_dir))
    timestamp1 = data1.last_updated
    
    # Refresh data
    data2 = data_service.refresh_data(str(temp_data_dir))
    timestamp2 = data2.last_updated
    
    # Verify data was refreshed
    assert data2 is not None
    assert timestamp2 >= timestamp1
    assert len(data2.shipments) == 1


def test_persist_update_shipment(data_service, temp_data_dir):
    """Test persisting a shipment update."""
    # Load initial data
    data_service.load_data(str(temp_data_dir))
    
    # Create status update
    update = StatusUpdate(
        entity_type='shipment',
        entity_id='SH001',
        field='current_location',
        old_value='Chicago',
        new_value='Denver',
        timestamp=datetime.now()
    )
    
    # Persist update
    data_service.persist_update(update, str(temp_data_dir))
    
    # Verify cache was updated
    cached = data_service.get_cached_data()
    shipment = next(s for s in cached.shipments if s.id == 'SH001')
    assert shipment.current_location == 'Denver'
    
    # Verify CSV was updated
    shipments_file = temp_data_dir / "shipments.csv"
    with open(shipments_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)
        assert row['current_location'] == 'Denver'


def test_persist_update_inventory(data_service, temp_data_dir):
    """Test persisting an inventory update."""
    # Load initial data
    data_service.load_data(str(temp_data_dir))
    
    # Create status update
    update = StatusUpdate(
        entity_type='inventory',
        entity_id='INV001',
        field='quantity',
        old_value=100.0,
        new_value=75.0,
        timestamp=datetime.now()
    )
    
    # Persist update
    data_service.persist_update(update, str(temp_data_dir))
    
    # Verify cache was updated
    cached = data_service.get_cached_data()
    item = next(i for i in cached.inventory if i.id == 'INV001')
    assert item.quantity == 75.0


def test_persist_update_supplier(data_service, temp_data_dir):
    """Test persisting a supplier update."""
    # Load initial data
    data_service.load_data(str(temp_data_dir))
    
    # Create status update
    update = StatusUpdate(
        entity_type='supplier',
        entity_id='SUP001',
        field='performance_score',
        old_value=85.5,
        new_value=90.0,
        timestamp=datetime.now()
    )
    
    # Persist update
    data_service.persist_update(update, str(temp_data_dir))
    
    # Verify cache was updated
    cached = data_service.get_cached_data()
    supplier = next(s for s in cached.suppliers if s.id == 'SUP001')
    assert supplier.performance_score == 90.0


def test_persist_update_no_cache(data_service, temp_data_dir):
    """Test persisting update without loading data first raises error."""
    update = StatusUpdate(
        entity_type='shipment',
        entity_id='SH001',
        field='current_location',
        old_value='Chicago',
        new_value='Denver',
        timestamp=datetime.now()
    )
    
    with pytest.raises(ValueError, match="No cached data available"):
        data_service.persist_update(update, str(temp_data_dir))


def test_persist_update_invalid_entity(data_service, temp_data_dir):
    """Test persisting update for nonexistent entity raises error."""
    # Load initial data
    data_service.load_data(str(temp_data_dir))
    
    # Create update for nonexistent shipment
    update = StatusUpdate(
        entity_type='shipment',
        entity_id='NONEXISTENT',
        field='current_location',
        old_value='Chicago',
        new_value='Denver',
        timestamp=datetime.now()
    )
    
    with pytest.raises(ValueError, match="Shipment not found"):
        data_service.persist_update(update, str(temp_data_dir))


def test_load_data_with_missing_csv_files(data_service):
    """Test loading data when some CSV files are missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        
        # Create only shipments.csv, leave others missing
        shipments_file = data_dir / "shipments.csv"
        with open(shipments_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'origin', 'destination', 'current_location', 'status',
                'estimated_delivery', 'actual_delivery', 'items', 'supplier_id',
                'created_at', 'updated_at'
            ])
            writer.writeheader()
        
        # Load data - should handle missing files gracefully
        data = data_service.load_data(str(data_dir))
        
        assert len(data.shipments) == 0
        assert len(data.inventory) == 0
        assert len(data.suppliers) == 0
        assert len(data.nodes) == 0
        assert len(data.edges) == 0


def test_load_data_updates_cache_timestamp(data_service, temp_data_dir):
    """Test that loading data updates the cache timestamp."""
    before = datetime.now()
    data_service.load_data(str(temp_data_dir))
    after = datetime.now()
    
    cached = data_service.get_cached_data()
    assert cached is not None
    assert before <= cached.last_updated <= after

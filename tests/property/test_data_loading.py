"""
Property-based tests for data loading.

Feature: supply-chain-visibility
Property 22: Multi-Source Data Loading

**Validates: Requirements 9.4**

This module tests that the data loader successfully loads data from supported
data sources and returns it in the standard SupplyChainData format.
"""

import pytest
import tempfile
import csv
from pathlib import Path
from datetime import datetime
from hypothesis import given, settings
from hypothesis import strategies as st

from src.data_access import DataAccessService
from src.models import SupplyChainData, ShipmentStatus, NodeType, NodeStatus
from tests.strategies.supply_chain_strategies import (
    shipment_strategy,
    inventory_item_strategy,
    supplier_strategy,
    node_strategy,
    edge_strategy
)


def create_csv_data_source(shipments, inventory_items, suppliers, nodes, edges):
    """
    Create a temporary CSV data source with the provided data.
    
    Args:
        shipments: List of Shipment objects
        inventory_items: List of InventoryItem objects
        suppliers: List of Supplier objects
        nodes: List of Node objects
        edges: List of Edge objects
        
    Returns:
        Path to temporary directory containing CSV files
    """
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Write shipments CSV
    with open(temp_path / "shipments.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'origin', 'destination', 'current_location', 'status',
                     'estimated_delivery', 'actual_delivery', 'items', 'supplier_id',
                     'created_at', 'updated_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for shipment in shipments:
            writer.writerow({
                'id': shipment.id,
                'origin': shipment.origin,
                'destination': shipment.destination,
                'current_location': shipment.current_location,
                'status': shipment.status.value,
                'estimated_delivery': shipment.estimated_delivery.isoformat(),
                'actual_delivery': shipment.actual_delivery.isoformat() if shipment.actual_delivery else '',
                'items': ';'.join(shipment.items),
                'supplier_id': shipment.supplier_id,
                'created_at': shipment.created_at.isoformat(),
                'updated_at': shipment.updated_at.isoformat()
            })
    
    # Write inventory CSV
    with open(temp_path / "inventory.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'name', 'category', 'location', 'quantity',
                     'unit', 'reorder_point', 'last_updated']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in inventory_items:
            writer.writerow({
                'id': item.id,
                'name': item.name,
                'category': item.category,
                'location': item.location,
                'quantity': item.quantity,
                'unit': item.unit,
                'reorder_point': item.reorder_point,
                'last_updated': item.last_updated.isoformat()
            })
    
    # Write suppliers CSV
    with open(temp_path / "suppliers.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'name', 'contact', 'performance_score',
                     'on_time_delivery_rate', 'quality_score', 'average_lead_time',
                     'total_shipments', 'last_updated']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for supplier in suppliers:
            writer.writerow({
                'id': supplier.id,
                'name': supplier.name,
                'contact': supplier.contact,
                'performance_score': supplier.performance_score,
                'on_time_delivery_rate': supplier.on_time_delivery_rate,
                'quality_score': supplier.quality_score,
                'average_lead_time': supplier.average_lead_time,
                'total_shipments': supplier.total_shipments,
                'last_updated': supplier.last_updated.isoformat()
            })
    
    # Write nodes CSV
    with open(temp_path / "nodes.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'name', 'type', 'location', 'latitude', 'longitude',
                     'status', 'capacity']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for node in nodes:
            writer.writerow({
                'id': node.id,
                'name': node.name,
                'type': node.type.value,
                'location': node.location,
                'latitude': node.latitude if node.latitude is not None else '',
                'longitude': node.longitude if node.longitude is not None else '',
                'status': node.status.value,
                'capacity': node.capacity if node.capacity is not None else ''
            })
    
    # Write edges CSV
    with open(temp_path / "edges.csv", 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'source_node_id', 'target_node_id', 'shipment_ids', 'active']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for edge in edges:
            writer.writerow({
                'id': edge.id,
                'source_node_id': edge.source_node_id,
                'target_node_id': edge.target_node_id,
                'shipment_ids': ';'.join(edge.shipment_ids),
                'active': str(edge.active).lower()
            })
    
    return temp_path


@pytest.mark.property
@given(
    shipments=st.lists(shipment_strategy(), min_size=0, max_size=10),
    inventory_items=st.lists(inventory_item_strategy(), min_size=0, max_size=10),
    suppliers=st.lists(supplier_strategy(), min_size=0, max_size=10),
    nodes=st.lists(node_strategy(), min_size=0, max_size=10),
    edges=st.lists(edge_strategy(), min_size=0, max_size=10)
)
@settings(max_examples=100)
def test_data_loader_returns_standard_format(shipments, inventory_items, suppliers, nodes, edges):
    """
    Property 22: Multi-Source Data Loading
    
    **Validates: Requirements 9.4**
    
    For any supported data source type (CSV), the data loader should successfully
    load data and return it in the standard SupplyChainData format.
    
    This test verifies that:
    1. The data loader successfully loads data from CSV files
    2. The returned object is of type SupplyChainData
    3. All required fields are present and populated
    4. The data maintains integrity (counts match, types are correct)
    """
    # Create temporary CSV data source
    temp_path = create_csv_data_source(shipments, inventory_items, suppliers, nodes, edges)
    
    try:
        # Load data using DataAccessService
        service = DataAccessService()
        loaded_data = service.load_data(str(temp_path))
        
        # Verify the returned object is SupplyChainData
        assert isinstance(loaded_data, SupplyChainData), \
            "Data loader must return SupplyChainData object"
        
        # Verify all required fields are present
        assert hasattr(loaded_data, 'shipments'), "SupplyChainData must have 'shipments' field"
        assert hasattr(loaded_data, 'inventory'), "SupplyChainData must have 'inventory' field"
        assert hasattr(loaded_data, 'suppliers'), "SupplyChainData must have 'suppliers' field"
        assert hasattr(loaded_data, 'nodes'), "SupplyChainData must have 'nodes' field"
        assert hasattr(loaded_data, 'edges'), "SupplyChainData must have 'edges' field"
        assert hasattr(loaded_data, 'last_updated'), "SupplyChainData must have 'last_updated' field"
        
        # Verify field types
        assert isinstance(loaded_data.shipments, list), "shipments must be a list"
        assert isinstance(loaded_data.inventory, list), "inventory must be a list"
        assert isinstance(loaded_data.suppliers, list), "suppliers must be a list"
        assert isinstance(loaded_data.nodes, list), "nodes must be a list"
        assert isinstance(loaded_data.edges, list), "edges must be a list"
        assert isinstance(loaded_data.last_updated, datetime), "last_updated must be a datetime"
        
        # Verify data counts match (data integrity)
        assert len(loaded_data.shipments) == len(shipments), \
            f"Expected {len(shipments)} shipments, got {len(loaded_data.shipments)}"
        assert len(loaded_data.inventory) == len(inventory_items), \
            f"Expected {len(inventory_items)} inventory items, got {len(loaded_data.inventory)}"
        assert len(loaded_data.suppliers) == len(suppliers), \
            f"Expected {len(suppliers)} suppliers, got {len(loaded_data.suppliers)}"
        assert len(loaded_data.nodes) == len(nodes), \
            f"Expected {len(nodes)} nodes, got {len(loaded_data.nodes)}"
        assert len(loaded_data.edges) == len(edges), \
            f"Expected {len(edges)} edges, got {len(loaded_data.edges)}"
        
    finally:
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_path)


@pytest.mark.property
@given(
    shipments=st.lists(shipment_strategy(), min_size=1, max_size=5)
)
@settings(max_examples=100)
def test_loaded_shipment_data_integrity(shipments):
    """
    Property 22 Extension: Verify loaded shipment data maintains integrity.
    
    **Validates: Requirements 9.4**
    
    For any list of shipments loaded from CSV, the loaded data should match
    the original data in all fields (round-trip property).
    """
    # Create temporary CSV data source with only shipments
    temp_path = create_csv_data_source(shipments, [], [], [], [])
    
    try:
        # Load data
        service = DataAccessService()
        loaded_data = service.load_data(str(temp_path))
        
        # Verify each shipment's data integrity
        assert len(loaded_data.shipments) == len(shipments)
        
        for original, loaded in zip(shipments, loaded_data.shipments):
            assert loaded.id == original.id
            assert loaded.origin == original.origin
            assert loaded.destination == original.destination
            assert loaded.current_location == original.current_location
            assert loaded.status == original.status
            assert loaded.supplier_id == original.supplier_id
            assert loaded.items == original.items
            
            # Datetime fields should match (allowing for microsecond precision loss in ISO format)
            assert abs((loaded.estimated_delivery - original.estimated_delivery).total_seconds()) < 1
            assert abs((loaded.created_at - original.created_at).total_seconds()) < 1
            assert abs((loaded.updated_at - original.updated_at).total_seconds()) < 1
            
            if original.actual_delivery:
                assert loaded.actual_delivery is not None
                assert abs((loaded.actual_delivery - original.actual_delivery).total_seconds()) < 1
            else:
                assert loaded.actual_delivery is None
    
    finally:
        import shutil
        shutil.rmtree(temp_path)


@pytest.mark.property
@given(
    inventory_items=st.lists(inventory_item_strategy(), min_size=1, max_size=5)
)
@settings(max_examples=100)
def test_loaded_inventory_data_integrity(inventory_items):
    """
    Property 22 Extension: Verify loaded inventory data maintains integrity.
    
    **Validates: Requirements 9.4**
    
    For any list of inventory items loaded from CSV, the loaded data should match
    the original data in all fields (round-trip property).
    """
    # Create temporary CSV data source with only inventory
    temp_path = create_csv_data_source([], inventory_items, [], [], [])
    
    try:
        # Load data
        service = DataAccessService()
        loaded_data = service.load_data(str(temp_path))
        
        # Verify each inventory item's data integrity
        assert len(loaded_data.inventory) == len(inventory_items)
        
        for original, loaded in zip(inventory_items, loaded_data.inventory):
            assert loaded.id == original.id
            assert loaded.name == original.name
            assert loaded.category == original.category
            assert loaded.location == original.location
            assert loaded.quantity == original.quantity
            assert loaded.unit == original.unit
            assert loaded.reorder_point == original.reorder_point
            
            # Datetime fields should match
            assert abs((loaded.last_updated - original.last_updated).total_seconds()) < 1
    
    finally:
        import shutil
        shutil.rmtree(temp_path)


@pytest.mark.property
def test_data_loader_handles_empty_datasets():
    """
    Property 22 Extension: Verify data loader handles empty datasets correctly.
    
    **Validates: Requirements 9.4**
    
    The data loader should successfully load data even when CSV files are empty
    (contain only headers), returning empty lists for each entity type.
    """
    # Create temporary CSV data source with empty lists
    temp_path = create_csv_data_source([], [], [], [], [])
    
    try:
        # Load data
        service = DataAccessService()
        loaded_data = service.load_data(str(temp_path))
        
        # Verify the returned object is valid SupplyChainData
        assert isinstance(loaded_data, SupplyChainData)
        
        # Verify all lists are empty
        assert len(loaded_data.shipments) == 0
        assert len(loaded_data.inventory) == 0
        assert len(loaded_data.suppliers) == 0
        assert len(loaded_data.nodes) == 0
        assert len(loaded_data.edges) == 0
        
        # Verify last_updated is set
        assert isinstance(loaded_data.last_updated, datetime)
    
    finally:
        import shutil
        shutil.rmtree(temp_path)

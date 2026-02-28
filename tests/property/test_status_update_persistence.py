"""
Property-based tests for status update persistence.

Feature: supply-chain-visibility
Property 21: Status Update Persistence

**Validates: Requirements 9.2**

This module tests that status updates are correctly persisted and can be
retrieved after persistence (round-trip property).
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from hypothesis import given, settings
from hypothesis import strategies as st

from src.data_access import DataAccessService
from src.models import StatusUpdate, ShipmentStatus
from tests.strategies.supply_chain_strategies import (
    shipment_strategy,
    inventory_item_strategy,
    supplier_strategy,
    status_update_strategy
)


def create_test_data_source(shipments=None, inventory_items=None, suppliers=None):
    """
    Create a temporary CSV data source for testing.
    
    Args:
        shipments: List of Shipment objects (default: empty list)
        inventory_items: List of InventoryItem objects (default: empty list)
        suppliers: List of Supplier objects (default: empty list)
        
    Returns:
        Path to temporary directory containing CSV files
    """
    import csv
    
    shipments = shipments or []
    inventory_items = inventory_items or []
    suppliers = suppliers or []
    
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
    
    # Write empty nodes and edges CSV files
    for filename in ['nodes.csv', 'edges.csv']:
        with open(temp_path / filename, 'w', newline='', encoding='utf-8') as f:
            if filename == 'nodes.csv':
                writer = csv.DictWriter(f, fieldnames=['id', 'name', 'type', 'location',
                                                       'latitude', 'longitude', 'status', 'capacity'])
            else:
                writer = csv.DictWriter(f, fieldnames=['id', 'source_node_id', 'target_node_id',
                                                       'shipment_ids', 'active'])
            writer.writeheader()
    
    return temp_path


@pytest.mark.property
@given(
    shipments=st.lists(shipment_strategy(), min_size=1, max_size=5),
    field_to_update=st.sampled_from(['current_location', 'origin', 'destination']),
    new_value=st.text(min_size=1, max_size=50, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc'), blacklist_characters='\x00'
    ))
)
@settings(max_examples=100)
def test_shipment_status_update_persistence_round_trip(shipments, field_to_update, new_value):
    """
    Property 21: Status Update Persistence
    
    **Validates: Requirements 9.2**
    
    For any status update received, after persistence, loading the data should
    reflect the updated value (round-trip property for updates).
    
    This test verifies that:
    1. A status update can be persisted to the data store
    2. After persistence, reloading the data reflects the updated value
    3. The round-trip preserves the update correctly
    4. Other entities remain unchanged
    """
    temp_path = create_test_data_source(shipments=shipments)
    
    try:
        # Load initial data
        service = DataAccessService()
        initial_data = service.load_data(str(temp_path))
        
        # Select a shipment to update
        shipment_to_update = initial_data.shipments[0]
        old_value = getattr(shipment_to_update, field_to_update)
        
        # Create status update
        update = StatusUpdate(
            entity_type="shipment",
            entity_id=shipment_to_update.id,
            field=field_to_update,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.now()
        )
        
        # Persist the update
        service.persist_update(update, str(temp_path))
        
        # Reload data from the data store
        reloaded_data = service.load_data(str(temp_path))
        
        # Find the updated shipment in reloaded data
        updated_shipment = next(
            (s for s in reloaded_data.shipments if s.id == shipment_to_update.id),
            None
        )
        
        # Verify the update was persisted correctly
        assert updated_shipment is not None, \
            f"Shipment {shipment_to_update.id} should exist after reload"
        
        assert getattr(updated_shipment, field_to_update) == new_value, \
            f"Field '{field_to_update}' should be updated to '{new_value}' after round-trip"
        
        # Verify other shipments remain unchanged
        assert len(reloaded_data.shipments) == len(initial_data.shipments), \
            "Number of shipments should remain the same"
        
        for original, reloaded in zip(initial_data.shipments, reloaded_data.shipments):
            if original.id != shipment_to_update.id:
                # Other shipments should be unchanged
                assert reloaded.id == original.id
                assert reloaded.origin == original.origin
                assert reloaded.destination == original.destination
                assert reloaded.current_location == original.current_location
    
    finally:
        shutil.rmtree(temp_path)


@pytest.mark.property
@given(
    inventory_items=st.lists(inventory_item_strategy(), min_size=1, max_size=5),
    new_quantity=st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_inventory_status_update_persistence_round_trip(inventory_items, new_quantity):
    """
    Property 21: Status Update Persistence (Inventory)
    
    **Validates: Requirements 9.2**
    
    For any inventory status update, after persistence, loading the data should
    reflect the updated quantity value (round-trip property).
    """
    temp_path = create_test_data_source(inventory_items=inventory_items)
    
    try:
        # Load initial data
        service = DataAccessService()
        initial_data = service.load_data(str(temp_path))
        
        # Select an inventory item to update
        item_to_update = initial_data.inventory[0]
        old_quantity = item_to_update.quantity
        
        # Create status update for quantity
        update = StatusUpdate(
            entity_type="inventory",
            entity_id=item_to_update.id,
            field="quantity",
            old_value=old_quantity,
            new_value=new_quantity,
            timestamp=datetime.now()
        )
        
        # Persist the update
        service.persist_update(update, str(temp_path))
        
        # Reload data from the data store
        reloaded_data = service.load_data(str(temp_path))
        
        # Find the updated item in reloaded data
        updated_item = next(
            (i for i in reloaded_data.inventory if i.id == item_to_update.id),
            None
        )
        
        # Verify the update was persisted correctly
        assert updated_item is not None, \
            f"Inventory item {item_to_update.id} should exist after reload"
        
        assert updated_item.quantity == new_quantity, \
            f"Quantity should be updated to {new_quantity} after round-trip"
        
        # Verify other fields remain unchanged
        assert updated_item.name == item_to_update.name
        assert updated_item.category == item_to_update.category
        assert updated_item.location == item_to_update.location
        
        # Verify other items remain unchanged
        assert len(reloaded_data.inventory) == len(initial_data.inventory), \
            "Number of inventory items should remain the same"
    
    finally:
        shutil.rmtree(temp_path)


@pytest.mark.property
@given(
    suppliers=st.lists(supplier_strategy(), min_size=1, max_size=5),
    new_performance_score=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_supplier_status_update_persistence_round_trip(suppliers, new_performance_score):
    """
    Property 21: Status Update Persistence (Supplier)
    
    **Validates: Requirements 9.2**
    
    For any supplier status update, after persistence, loading the data should
    reflect the updated performance score (round-trip property).
    """
    temp_path = create_test_data_source(suppliers=suppliers)
    
    try:
        # Load initial data
        service = DataAccessService()
        initial_data = service.load_data(str(temp_path))
        
        # Select a supplier to update
        supplier_to_update = initial_data.suppliers[0]
        old_score = supplier_to_update.performance_score
        
        # Create status update for performance score
        update = StatusUpdate(
            entity_type="supplier",
            entity_id=supplier_to_update.id,
            field="performance_score",
            old_value=old_score,
            new_value=new_performance_score,
            timestamp=datetime.now()
        )
        
        # Persist the update
        service.persist_update(update, str(temp_path))
        
        # Reload data from the data store
        reloaded_data = service.load_data(str(temp_path))
        
        # Find the updated supplier in reloaded data
        updated_supplier = next(
            (s for s in reloaded_data.suppliers if s.id == supplier_to_update.id),
            None
        )
        
        # Verify the update was persisted correctly
        assert updated_supplier is not None, \
            f"Supplier {supplier_to_update.id} should exist after reload"
        
        assert updated_supplier.performance_score == new_performance_score, \
            f"Performance score should be updated to {new_performance_score} after round-trip"
        
        # Verify other fields remain unchanged
        assert updated_supplier.name == supplier_to_update.name
        assert updated_supplier.contact == supplier_to_update.contact
        assert updated_supplier.on_time_delivery_rate == supplier_to_update.on_time_delivery_rate
        
        # Verify other suppliers remain unchanged
        assert len(reloaded_data.suppliers) == len(initial_data.suppliers), \
            "Number of suppliers should remain the same"
    
    finally:
        shutil.rmtree(temp_path)


@pytest.mark.property
@given(
    shipments=st.lists(shipment_strategy(), min_size=2, max_size=5)
)
@settings(max_examples=100)
def test_multiple_status_updates_persistence(shipments):
    """
    Property 21 Extension: Multiple Status Updates Persistence
    
    **Validates: Requirements 9.2**
    
    For multiple status updates applied sequentially, all updates should be
    persisted correctly and reflected when data is reloaded.
    """
    temp_path = create_test_data_source(shipments=shipments)
    
    try:
        # Load initial data
        service = DataAccessService()
        initial_data = service.load_data(str(temp_path))
        
        # Get unique shipments by ID (in case of duplicates, keep the last one)
        unique_shipments = {}
        for shipment in initial_data.shipments:
            unique_shipments[shipment.id] = shipment
        
        # If we have less than 2 unique shipments, skip this test
        if len(unique_shipments) < 2:
            return
        
        # Apply multiple updates to different shipments (first 2 unique ones)
        updates = {}  # Use dict to handle duplicate IDs
        for i, (shipment_id, shipment) in enumerate(list(unique_shipments.items())[:2]):
            new_location = f"Updated Location {i}"
            update = StatusUpdate(
                entity_type="shipment",
                entity_id=shipment.id,
                field="current_location",
                old_value=shipment.current_location,
                new_value=new_location,
                timestamp=datetime.now()
            )
            updates[shipment_id] = new_location
            service.persist_update(update, str(temp_path))
        
        # Reload data
        reloaded_data = service.load_data(str(temp_path))
        
        # Verify all updates were persisted
        for shipment_id, expected_location in updates.items():
            updated_shipment = next(
                (s for s in reloaded_data.shipments if s.id == shipment_id),
                None
            )
            assert updated_shipment is not None
            assert updated_shipment.current_location == expected_location, \
                f"Shipment {shipment_id} should have location '{expected_location}'"
    
    finally:
        shutil.rmtree(temp_path)

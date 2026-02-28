"""
Hypothesis strategies for generating supply chain data models.

This module provides strategies for generating valid instances of all data models
used in the Supply Chain Visibility application for property-based testing.
"""

from datetime import datetime, timedelta
from hypothesis import strategies as st
from src.models import (
    Shipment, InventoryItem, Supplier, Node, Edge, Alert, StatusUpdate,
    ShipmentStatus, NodeType, NodeStatus, AlertType, AlertSeverity
)


# Basic strategies for common types
def text_strategy(min_size=1, max_size=50):
    """Generate non-empty text strings."""
    return st.text(min_size=min_size, max_size=max_size, alphabet=st.characters(
        blacklist_categories=('Cs', 'Cc'), blacklist_characters='\x00'
    ))


def datetime_strategy():
    """Generate datetime objects within a reasonable range."""
    return st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    )


# Shipment strategy
@st.composite
def shipment_strategy(draw):
    """Generate valid Shipment instances."""
    created = draw(datetime_strategy())
    updated = draw(st.datetimes(min_value=created, max_value=datetime(2030, 12, 31)))
    estimated = draw(st.datetimes(min_value=created, max_value=datetime(2030, 12, 31)))
    
    status = draw(st.sampled_from(ShipmentStatus))
    actual_delivery = None
    if status == ShipmentStatus.DELIVERED:
        actual_delivery = draw(st.datetimes(min_value=created, max_value=datetime(2030, 12, 31)))
    
    return Shipment(
        id=draw(text_strategy(min_size=1, max_size=20)),
        origin=draw(text_strategy(min_size=1, max_size=50)),
        destination=draw(text_strategy(min_size=1, max_size=50)),
        current_location=draw(text_strategy(min_size=1, max_size=50)),
        status=status,
        estimated_delivery=estimated,
        actual_delivery=actual_delivery,
        items=draw(st.lists(text_strategy(min_size=1, max_size=20), min_size=1, max_size=10)),
        supplier_id=draw(text_strategy(min_size=1, max_size=20)),
        created_at=created,
        updated_at=updated
    )


# InventoryItem strategy
@st.composite
def inventory_item_strategy(draw):
    """Generate valid InventoryItem instances."""
    return InventoryItem(
        id=draw(text_strategy(min_size=1, max_size=20)),
        name=draw(text_strategy(min_size=1, max_size=50)),
        category=draw(text_strategy(min_size=1, max_size=30)),
        location=draw(text_strategy(min_size=1, max_size=50)),
        quantity=draw(st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False)),
        unit=draw(st.sampled_from(['pieces', 'kg', 'liters', 'boxes', 'pallets'])),
        reorder_point=draw(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)),
        last_updated=draw(datetime_strategy())
    )


# Supplier strategy
@st.composite
def supplier_strategy(draw):
    """Generate valid Supplier instances."""
    return Supplier(
        id=draw(text_strategy(min_size=1, max_size=20)),
        name=draw(text_strategy(min_size=1, max_size=50)),
        contact=draw(text_strategy(min_size=1, max_size=100)),
        performance_score=draw(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)),
        on_time_delivery_rate=draw(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)),
        quality_score=draw(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)),
        average_lead_time=draw(st.floats(min_value=0, max_value=365, allow_nan=False, allow_infinity=False)),
        total_shipments=draw(st.integers(min_value=0, max_value=10000)),
        last_updated=draw(datetime_strategy())
    )


# Node strategy
@st.composite
def node_strategy(draw):
    """Generate valid Node instances."""
    has_coordinates = draw(st.booleans())
    
    return Node(
        id=draw(text_strategy(min_size=1, max_size=20)),
        name=draw(text_strategy(min_size=1, max_size=50)),
        type=draw(st.sampled_from(NodeType)),
        location=draw(text_strategy(min_size=1, max_size=50)),
        latitude=draw(st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False)) if has_coordinates else None,
        longitude=draw(st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)) if has_coordinates else None,
        status=draw(st.sampled_from(NodeStatus)),
        capacity=draw(st.one_of(st.none(), st.floats(min_value=0, max_value=100000, allow_nan=False, allow_infinity=False)))
    )


# Edge strategy
@st.composite
def edge_strategy(draw):
    """Generate valid Edge instances."""
    source_id = draw(text_strategy(min_size=1, max_size=20))
    target_id = draw(text_strategy(min_size=1, max_size=20))
    
    # Ensure source and target are different
    while target_id == source_id:
        target_id = draw(text_strategy(min_size=1, max_size=20))
    
    return Edge(
        id=draw(text_strategy(min_size=1, max_size=20)),
        source_node_id=source_id,
        target_node_id=target_id,
        shipment_ids=draw(st.lists(text_strategy(min_size=1, max_size=20), min_size=0, max_size=10)),
        active=draw(st.booleans())
    )


# Alert strategy
@st.composite
def alert_strategy(draw):
    """Generate valid Alert instances."""
    created = draw(datetime_strategy())
    acknowledged = draw(st.booleans())
    acknowledged_at = None
    
    if acknowledged:
        acknowledged_at = draw(st.datetimes(min_value=created, max_value=datetime(2030, 12, 31)))
    
    return Alert(
        id=draw(text_strategy(min_size=1, max_size=20)),
        type=draw(st.sampled_from(AlertType)),
        severity=draw(st.sampled_from(AlertSeverity)),
        message=draw(text_strategy(min_size=1, max_size=200)),
        entity_id=draw(text_strategy(min_size=1, max_size=20)),
        created_at=created,
        acknowledged=acknowledged,
        acknowledged_at=acknowledged_at
    )


# StatusUpdate strategy
@st.composite
def status_update_strategy(draw):
    """Generate valid StatusUpdate instances."""
    return StatusUpdate(
        entity_type=draw(st.sampled_from(['shipment', 'inventory', 'supplier'])),
        entity_id=draw(text_strategy(min_size=1, max_size=20)),
        field=draw(text_strategy(min_size=1, max_size=30)),
        old_value=draw(st.one_of(st.text(), st.integers(), st.floats(allow_nan=False, allow_infinity=False))),
        new_value=draw(st.one_of(st.text(), st.integers(), st.floats(allow_nan=False, allow_infinity=False))),
        timestamp=draw(datetime_strategy())
    )

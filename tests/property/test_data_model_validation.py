"""
Property-based tests for data model validation.

Feature: supply-chain-visibility
Property 2: Detail Views Contain Required Fields

**Validates: Requirements 2.2, 3.5, 4.3, 6.1**

This module tests that all data models contain their required fields as specified
in the design document. For any entity (Shipment, InventoryItem, Supplier, Node),
when displaying its detail view, the rendered output must contain all required fields.
"""

import pytest
from hypothesis import given, settings
from tests.strategies.supply_chain_strategies import (
    shipment_strategy,
    inventory_item_strategy,
    supplier_strategy,
    node_strategy
)


# Required fields for each entity type as specified in the design document
SHIPMENT_REQUIRED_FIELDS = {
    'origin',
    'destination',
    'current_location',
    'estimated_delivery'
}

INVENTORY_REQUIRED_FIELDS = {
    'quantity',
    'location',
    'reorder_point'
}

SUPPLIER_REQUIRED_FIELDS = {
    'on_time_delivery_rate',
    'quality_score',
    'average_lead_time'
}

NODE_REQUIRED_FIELDS = {
    'name',
    'type',
    'location',
    'status'
}


def render_shipment_detail_view(shipment) -> dict:
    """
    Simulate rendering a shipment detail view.
    
    In a real application, this would be the Streamlit component that displays
    shipment details. For testing purposes, we return a dictionary of displayed fields.
    """
    return {
        'id': shipment.id,
        'origin': shipment.origin,
        'destination': shipment.destination,
        'current_location': shipment.current_location,
        'status': shipment.status.value,
        'estimated_delivery': shipment.estimated_delivery,
        'actual_delivery': shipment.actual_delivery,
        'items': shipment.items,
        'supplier_id': shipment.supplier_id,
        'created_at': shipment.created_at,
        'updated_at': shipment.updated_at
    }


def render_inventory_detail_view(inventory_item) -> dict:
    """
    Simulate rendering an inventory item detail view.
    
    Returns a dictionary of displayed fields for the inventory item.
    """
    return {
        'id': inventory_item.id,
        'name': inventory_item.name,
        'category': inventory_item.category,
        'location': inventory_item.location,
        'quantity': inventory_item.quantity,
        'unit': inventory_item.unit,
        'reorder_point': inventory_item.reorder_point,
        'last_updated': inventory_item.last_updated
    }


def render_supplier_detail_view(supplier) -> dict:
    """
    Simulate rendering a supplier detail view.
    
    Returns a dictionary of displayed fields for the supplier.
    """
    return {
        'id': supplier.id,
        'name': supplier.name,
        'contact': supplier.contact,
        'performance_score': supplier.performance_score,
        'on_time_delivery_rate': supplier.on_time_delivery_rate,
        'quality_score': supplier.quality_score,
        'average_lead_time': supplier.average_lead_time,
        'total_shipments': supplier.total_shipments,
        'last_updated': supplier.last_updated
    }


def render_node_detail_view(node) -> dict:
    """
    Simulate rendering a node detail view.
    
    Returns a dictionary of displayed fields for the node.
    """
    return {
        'id': node.id,
        'name': node.name,
        'type': node.type.value,
        'location': node.location,
        'latitude': node.latitude,
        'longitude': node.longitude,
        'status': node.status.value,
        'capacity': node.capacity
    }


@pytest.mark.property
@given(shipment=shipment_strategy())
@settings(max_examples=100)
def test_shipment_detail_view_contains_required_fields(shipment):
    """
    Property 2: Detail Views Contain Required Fields (Shipments)
    
    **Validates: Requirements 2.2**
    
    For any Shipment, when displaying its detail view, the rendered output
    must contain all required fields: origin, destination, current location,
    and estimated delivery time.
    """
    detail_view = render_shipment_detail_view(shipment)
    
    # Verify all required fields are present in the detail view
    for field in SHIPMENT_REQUIRED_FIELDS:
        assert field in detail_view, f"Required field '{field}' missing from shipment detail view"
        assert detail_view[field] is not None, f"Required field '{field}' is None in shipment detail view"


@pytest.mark.property
@given(inventory_item=inventory_item_strategy())
@settings(max_examples=100)
def test_inventory_detail_view_contains_required_fields(inventory_item):
    """
    Property 2: Detail Views Contain Required Fields (Inventory)
    
    **Validates: Requirements 3.5**
    
    For any InventoryItem, when displaying its detail view, the rendered output
    must contain all required fields: quantity, location, and reorder point.
    """
    detail_view = render_inventory_detail_view(inventory_item)
    
    # Verify all required fields are present in the detail view
    for field in INVENTORY_REQUIRED_FIELDS:
        assert field in detail_view, f"Required field '{field}' missing from inventory detail view"
        assert detail_view[field] is not None, f"Required field '{field}' is None in inventory detail view"


@pytest.mark.property
@given(supplier=supplier_strategy())
@settings(max_examples=100)
def test_supplier_detail_view_contains_required_fields(supplier):
    """
    Property 2: Detail Views Contain Required Fields (Suppliers)
    
    **Validates: Requirements 6.1**
    
    For any Supplier, when displaying its detail view, the rendered output
    must contain all required fields: on-time delivery rate, quality score,
    and lead time.
    """
    detail_view = render_supplier_detail_view(supplier)
    
    # Verify all required fields are present in the detail view
    for field in SUPPLIER_REQUIRED_FIELDS:
        assert field in detail_view, f"Required field '{field}' missing from supplier detail view"
        assert detail_view[field] is not None, f"Required field '{field}' is None in supplier detail view"


@pytest.mark.property
@given(node=node_strategy())
@settings(max_examples=100)
def test_node_detail_view_contains_required_fields(node):
    """
    Property 2: Detail Views Contain Required Fields (Nodes)
    
    **Validates: Requirements 4.3**
    
    For any Node, when displaying its detail view, the rendered output
    must contain all required fields: node details (name, type, location, status).
    """
    detail_view = render_node_detail_view(node)
    
    # Verify all required fields are present in the detail view
    for field in NODE_REQUIRED_FIELDS:
        assert field in detail_view, f"Required field '{field}' missing from node detail view"
        assert detail_view[field] is not None, f"Required field '{field}' is None in node detail view"


@pytest.mark.property
@given(shipment=shipment_strategy())
@settings(max_examples=100)
def test_shipment_detail_view_field_values_match_model(shipment):
    """
    Property 2 Extension: Verify detail view values match the model.
    
    **Validates: Requirements 2.2**
    
    For any Shipment, the values displayed in the detail view must match
    the values in the data model.
    """
    detail_view = render_shipment_detail_view(shipment)
    
    # Verify field values match the model
    assert detail_view['origin'] == shipment.origin
    assert detail_view['destination'] == shipment.destination
    assert detail_view['current_location'] == shipment.current_location
    assert detail_view['estimated_delivery'] == shipment.estimated_delivery


@pytest.mark.property
@given(inventory_item=inventory_item_strategy())
@settings(max_examples=100)
def test_inventory_detail_view_field_values_match_model(inventory_item):
    """
    Property 2 Extension: Verify detail view values match the model.
    
    **Validates: Requirements 3.5**
    
    For any InventoryItem, the values displayed in the detail view must match
    the values in the data model.
    """
    detail_view = render_inventory_detail_view(inventory_item)
    
    # Verify field values match the model
    assert detail_view['quantity'] == inventory_item.quantity
    assert detail_view['location'] == inventory_item.location
    assert detail_view['reorder_point'] == inventory_item.reorder_point


@pytest.mark.property
@given(supplier=supplier_strategy())
@settings(max_examples=100)
def test_supplier_detail_view_field_values_match_model(supplier):
    """
    Property 2 Extension: Verify detail view values match the model.
    
    **Validates: Requirements 6.1**
    
    For any Supplier, the values displayed in the detail view must match
    the values in the data model.
    """
    detail_view = render_supplier_detail_view(supplier)
    
    # Verify field values match the model
    assert detail_view['on_time_delivery_rate'] == supplier.on_time_delivery_rate
    assert detail_view['quality_score'] == supplier.quality_score
    assert detail_view['average_lead_time'] == supplier.average_lead_time


@pytest.mark.property
@given(node=node_strategy())
@settings(max_examples=100)
def test_node_detail_view_field_values_match_model(node):
    """
    Property 2 Extension: Verify detail view values match the model.
    
    **Validates: Requirements 4.3**
    
    For any Node, the values displayed in the detail view must match
    the values in the data model.
    """
    detail_view = render_node_detail_view(node)
    
    # Verify field values match the model
    assert detail_view['name'] == node.name
    assert detail_view['type'] == node.type.value
    assert detail_view['location'] == node.location
    assert detail_view['status'] == node.status.value

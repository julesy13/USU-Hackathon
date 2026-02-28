"""
Property-based tests for filter application.

Feature: supply-chain-visibility
Property 6: Filter Application Preserves Invariants

**Validates: Requirements 3.3, 7.2**

This module tests that when filters are applied to supply chain data:
1. The filtered data is always a subset of the original data
2. Referential integrity is maintained (e.g., edges only connect nodes that exist)
3. All filtered items satisfy the filter conditions
"""

import pytest
from hypothesis import given, settings, assume, HealthCheck
from tests.strategies.supply_chain_strategies import (
    supply_chain_data_strategy,
    filter_criteria_strategy
)
from src.filter_engine import FilterEngine


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20), filters=filter_criteria_strategy())
@settings(max_examples=100)
def test_filtered_data_is_subset_of_original(data, filters):
    """
    Property 6: Filter Application Preserves Invariants (Subset Property)
    
    **Validates: Requirements 3.3, 7.2**
    
    For any dataset and filter criteria, applying filters should return a subset
    of the original data. Every item in the filtered result must exist in the
    original dataset.
    """
    engine = FilterEngine()
    filtered = engine.apply_filters(data, filters)
    
    # Verify filtered shipments are a subset of original shipments
    original_shipment_ids = {s.id for s in data.shipments}
    filtered_shipment_ids = {s.id for s in filtered.shipments}
    assert filtered_shipment_ids.issubset(original_shipment_ids), \
        "Filtered shipments must be a subset of original shipments"
    
    # Verify filtered inventory is a subset of original inventory
    original_inventory_ids = {i.id for i in data.inventory}
    filtered_inventory_ids = {i.id for i in filtered.inventory}
    assert filtered_inventory_ids.issubset(original_inventory_ids), \
        "Filtered inventory must be a subset of original inventory"
    
    # Verify filtered suppliers are a subset of original suppliers
    original_supplier_ids = {s.id for s in data.suppliers}
    filtered_supplier_ids = {s.id for s in filtered.suppliers}
    assert filtered_supplier_ids.issubset(original_supplier_ids), \
        "Filtered suppliers must be a subset of original suppliers"
    
    # Verify filtered nodes are a subset of original nodes
    original_node_ids = {n.id for n in data.nodes}
    filtered_node_ids = {n.id for n in filtered.nodes}
    assert filtered_node_ids.issubset(original_node_ids), \
        "Filtered nodes must be a subset of original nodes"
    
    # Verify filtered edges are a subset of original edges
    original_edge_ids = {e.id for e in data.edges}
    filtered_edge_ids = {e.id for e in filtered.edges}
    assert filtered_edge_ids.issubset(original_edge_ids), \
        "Filtered edges must be a subset of original edges"


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20), filters=filter_criteria_strategy())
@settings(max_examples=100)
def test_filtered_edges_maintain_referential_integrity(data, filters):
    """
    Property 6: Filter Application Preserves Invariants (Referential Integrity)
    
    **Validates: Requirements 3.3, 7.2**
    
    For any dataset and filter criteria, the filtered data should maintain
    referential integrity. Specifically, edges should only connect nodes that
    exist in the filtered node set.
    """
    engine = FilterEngine()
    filtered = engine.apply_filters(data, filters)
    
    # Get set of filtered node IDs
    filtered_node_ids = {n.id for n in filtered.nodes}
    
    # Verify all edges only connect nodes that exist in the filtered set
    for edge in filtered.edges:
        assert edge.source_node_id in filtered_node_ids, \
            f"Edge {edge.id} references non-existent source node {edge.source_node_id}"
        assert edge.target_node_id in filtered_node_ids, \
            f"Edge {edge.id} references non-existent target node {edge.target_node_id}"


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20), filters=filter_criteria_strategy())
@settings(max_examples=100)
def test_filtered_shipments_reference_valid_suppliers(data, filters):
    """
    Property 6: Filter Application Preserves Invariants (Supplier References)
    
    **Validates: Requirements 3.3, 7.2**
    
    For any dataset and filter criteria, filtered shipments should only reference
    suppliers that exist in the original dataset (referential integrity for suppliers).
    Note: Suppliers may be filtered out, but shipment references should still be valid
    in the original dataset.
    """
    engine = FilterEngine()
    filtered = engine.apply_filters(data, filters)
    
    # Get set of original supplier IDs
    original_supplier_ids = {s.id for s in data.suppliers}
    
    # Verify all filtered shipments reference valid suppliers from original data
    for shipment in filtered.shipments:
        assert shipment.supplier_id in original_supplier_ids, \
            f"Shipment {shipment.id} references non-existent supplier {shipment.supplier_id}"


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20), filters=filter_criteria_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_filtered_items_satisfy_date_range_filter(data, filters):
    """
    Property 6: Filter Application Preserves Invariants (Date Range Filter)
    
    **Validates: Requirements 3.3, 7.2**
    
    For any dataset with a date range filter, all filtered items with date fields
    should fall within the specified date range.
    """
    # Only test when date range filter is applied
    assume(filters.date_range is not None)
    
    engine = FilterEngine()
    filtered = engine.apply_filters(data, filters)
    
    start_date, end_date = filters.date_range
    
    # Verify filtered shipments fall within date range (using estimated_delivery)
    for shipment in filtered.shipments:
        assert start_date <= shipment.estimated_delivery <= end_date, \
            f"Shipment {shipment.id} estimated_delivery {shipment.estimated_delivery} outside date range [{start_date}, {end_date}]"
    
    # Verify filtered inventory falls within date range (using last_updated)
    for item in filtered.inventory:
        assert start_date <= item.last_updated <= end_date, \
            f"Inventory item {item.id} last_updated {item.last_updated} outside date range [{start_date}, {end_date}]"
    
    # Verify filtered suppliers fall within date range (using last_updated)
    for supplier in filtered.suppliers:
        assert start_date <= supplier.last_updated <= end_date, \
            f"Supplier {supplier.id} last_updated {supplier.last_updated} outside date range [{start_date}, {end_date}]"


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20), filters=filter_criteria_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_filtered_items_satisfy_status_filter(data, filters):
    """
    Property 6: Filter Application Preserves Invariants (Status Filter)
    
    **Validates: Requirements 3.3, 7.2**
    
    For any dataset with a status filter, all filtered items should have a status
    that matches one of the specified status values.
    """
    # Only test when status filter is applied
    assume(filters.status is not None)
    assume(len(filters.status) > 0)
    
    engine = FilterEngine()
    filtered = engine.apply_filters(data, filters)
    
    # Verify filtered shipments have matching status
    for shipment in filtered.shipments:
        assert shipment.status.value in filters.status, \
            f"Shipment {shipment.id} status {shipment.status.value} not in filter status list {filters.status}"
    
    # Verify filtered nodes have matching status
    for node in filtered.nodes:
        assert node.status.value in filters.status, \
            f"Node {node.id} status {node.status.value} not in filter status list {filters.status}"


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20), filters=filter_criteria_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_filtered_items_satisfy_location_filter(data, filters):
    """
    Property 6: Filter Application Preserves Invariants (Location Filter)
    
    **Validates: Requirements 3.3, 7.2**
    
    For any dataset with a location filter, all filtered items should have a location
    that matches one of the specified location values.
    """
    # Only test when location filter is applied
    assume(filters.location is not None)
    assume(len(filters.location) > 0)
    
    engine = FilterEngine()
    filtered = engine.apply_filters(data, filters)
    
    # Verify filtered shipments have matching location (origin, destination, or current_location)
    for shipment in filtered.shipments:
        assert (shipment.origin in filters.location or 
                shipment.destination in filters.location or 
                shipment.current_location in filters.location), \
            f"Shipment {shipment.id} locations not in filter location list {filters.location}"
    
    # Verify filtered inventory has matching location
    for item in filtered.inventory:
        assert item.location in filters.location, \
            f"Inventory item {item.id} location {item.location} not in filter location list {filters.location}"
    
    # Verify filtered nodes have matching location
    for node in filtered.nodes:
        assert node.location in filters.location, \
            f"Node {node.id} location {node.location} not in filter location list {filters.location}"


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20), filters=filter_criteria_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_filtered_items_satisfy_category_filter(data, filters):
    """
    Property 6: Filter Application Preserves Invariants (Category Filter)
    
    **Validates: Requirements 3.3, 7.2**
    
    For any dataset with a category filter, all filtered inventory items should
    have a category that matches one of the specified category values.
    """
    # Only test when category filter is applied
    assume(filters.category is not None)
    assume(len(filters.category) > 0)
    
    engine = FilterEngine()
    filtered = engine.apply_filters(data, filters)
    
    # Verify filtered inventory has matching category
    for item in filtered.inventory:
        assert item.category in filters.category, \
            f"Inventory item {item.id} category {item.category} not in filter category list {filters.category}"


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20))
@settings(max_examples=100)
def test_no_filters_returns_complete_dataset(data):
    """
    Property 6: Filter Application Preserves Invariants (No Filter Case)
    
    **Validates: Requirements 3.3, 7.2**
    
    When no filters are applied (empty FilterCriteria), the filtered result
    should be identical to the original dataset.
    """
    engine = FilterEngine()
    empty_filters = engine.reset_filters()
    filtered = engine.apply_filters(data, empty_filters)
    
    # Verify all entities are preserved
    assert len(filtered.shipments) == len(data.shipments), \
        "No filters should preserve all shipments"
    assert len(filtered.inventory) == len(data.inventory), \
        "No filters should preserve all inventory items"
    assert len(filtered.suppliers) == len(data.suppliers), \
        "No filters should preserve all suppliers"
    assert len(filtered.nodes) == len(data.nodes), \
        "No filters should preserve all nodes"
    assert len(filtered.edges) == len(data.edges), \
        "No filters should preserve all edges"
    
    # Verify IDs match
    assert {s.id for s in filtered.shipments} == {s.id for s in data.shipments}
    assert {i.id for i in filtered.inventory} == {i.id for i in data.inventory}
    assert {s.id for s in filtered.suppliers} == {s.id for s in data.suppliers}
    assert {n.id for n in filtered.nodes} == {n.id for n in data.nodes}
    assert {e.id for e in filtered.edges} == {e.id for e in data.edges}


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20), filters=filter_criteria_strategy())
@settings(max_examples=100)
def test_filter_application_is_deterministic(data, filters):
    """
    Property 6: Filter Application Preserves Invariants (Determinism)
    
    **Validates: Requirements 3.3, 7.2**
    
    Applying the same filters to the same data multiple times should produce
    identical results (deterministic behavior).
    """
    engine = FilterEngine()
    
    # Apply filters twice
    filtered1 = engine.apply_filters(data, filters)
    filtered2 = engine.apply_filters(data, filters)
    
    # Verify results are identical
    assert {s.id for s in filtered1.shipments} == {s.id for s in filtered2.shipments}, \
        "Filter application should be deterministic for shipments"
    assert {i.id for i in filtered1.inventory} == {i.id for i in filtered2.inventory}, \
        "Filter application should be deterministic for inventory"
    assert {s.id for s in filtered1.suppliers} == {s.id for s in filtered2.suppliers}, \
        "Filter application should be deterministic for suppliers"
    assert {n.id for n in filtered1.nodes} == {n.id for n in filtered2.nodes}, \
        "Filter application should be deterministic for nodes"
    assert {e.id for e in filtered1.edges} == {e.id for e in filtered2.edges}, \
        "Filter application should be deterministic for edges"

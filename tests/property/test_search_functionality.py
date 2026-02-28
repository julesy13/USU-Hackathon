"""
Property-based tests for search functionality.

Feature: supply-chain-visibility
Property 4: Search Returns Only Matching Results

**Validates: Requirements 2.5, 7.1**

This module tests that when searching supply chain data:
1. All returned results match the query in at least one of the specified fields
2. No matching items are excluded from the results
"""

import pytest
from hypothesis import given, settings, assume
from tests.strategies.supply_chain_strategies import (
    supply_chain_data_strategy,
    text_strategy
)
from hypothesis import strategies as st
from src.filter_engine import FilterEngine


@pytest.mark.property
@given(
    data=supply_chain_data_strategy(min_items=1, max_items=20),
    query=text_strategy(min_size=1, max_size=10),
    fields=st.lists(
        st.sampled_from(['id', 'name', 'origin', 'destination', 'location', 'category']),
        min_size=1,
        max_size=3,
        unique=True
    )
)
@settings(max_examples=100)
def test_search_returns_only_matching_results(data, query, fields):
    """
    Property 4: Search Returns Only Matching Results (Precision)
    
    **Validates: Requirements 2.5, 7.1**
    
    For any search query and search fields, all returned results must match
    the query in at least one of the specified fields. This ensures search
    precision - no false positives.
    """
    engine = FilterEngine()
    result = engine.search(data, query, fields)
    
    query_lower = query.lower()
    
    # Check shipments: all results must match query in at least one field
    for shipment in result.shipments:
        matches = False
        for field in fields:
            if hasattr(shipment, field):
                value = getattr(shipment, field)
                if value is not None and query_lower in str(value).lower():
                    matches = True
                    break
        assert matches, \
            f"Shipment {shipment.id} in results but doesn't match query '{query}' in fields {fields}"
    
    # Check inventory items: all results must match query in at least one field
    for item in result.inventory:
        matches = False
        for field in fields:
            if hasattr(item, field):
                value = getattr(item, field)
                if value is not None and query_lower in str(value).lower():
                    matches = True
                    break
        assert matches, \
            f"Inventory item {item.id} in results but doesn't match query '{query}' in fields {fields}"
    
    # Check suppliers: all results must match query in at least one field
    for supplier in result.suppliers:
        matches = False
        for field in fields:
            if hasattr(supplier, field):
                value = getattr(supplier, field)
                if value is not None and query_lower in str(value).lower():
                    matches = True
                    break
        assert matches, \
            f"Supplier {supplier.id} in results but doesn't match query '{query}' in fields {fields}"
    
    # Check nodes: all results must match query in at least one field
    for node in result.nodes:
        matches = False
        for field in fields:
            if hasattr(node, field):
                value = getattr(node, field)
                if value is not None and query_lower in str(value).lower():
                    matches = True
                    break
        assert matches, \
            f"Node {node.id} in results but doesn't match query '{query}' in fields {fields}"


@pytest.mark.property
@given(
    data=supply_chain_data_strategy(min_items=1, max_items=20),
    query=text_strategy(min_size=1, max_size=10),
    fields=st.lists(
        st.sampled_from(['id', 'name', 'origin', 'destination', 'location', 'category']),
        min_size=1,
        max_size=3,
        unique=True
    )
)
@settings(max_examples=100)
def test_search_includes_all_matching_items(data, query, fields):
    """
    Property 4: Search Returns Only Matching Results (Completeness)
    
    **Validates: Requirements 2.5, 7.1**
    
    For any search query and search fields, no matching items should be excluded
    from the results. This ensures search completeness - no false negatives.
    """
    engine = FilterEngine()
    result = engine.search(data, query, fields)
    
    query_lower = query.lower()
    
    # Check shipments: all matching items from original data should be in results
    result_shipment_ids = {s.id for s in result.shipments}
    for shipment in data.shipments:
        matches = False
        for field in fields:
            if hasattr(shipment, field):
                value = getattr(shipment, field)
                if value is not None and query_lower in str(value).lower():
                    matches = True
                    break
        if matches:
            assert shipment.id in result_shipment_ids, \
                f"Shipment {shipment.id} matches query '{query}' but is missing from results"
    
    # Check inventory items: all matching items from original data should be in results
    result_inventory_ids = {i.id for i in result.inventory}
    for item in data.inventory:
        matches = False
        for field in fields:
            if hasattr(item, field):
                value = getattr(item, field)
                if value is not None and query_lower in str(value).lower():
                    matches = True
                    break
        if matches:
            assert item.id in result_inventory_ids, \
                f"Inventory item {item.id} matches query '{query}' but is missing from results"
    
    # Check suppliers: all matching items from original data should be in results
    result_supplier_ids = {s.id for s in result.suppliers}
    for supplier in data.suppliers:
        matches = False
        for field in fields:
            if hasattr(supplier, field):
                value = getattr(supplier, field)
                if value is not None and query_lower in str(value).lower():
                    matches = True
                    break
        if matches:
            assert supplier.id in result_supplier_ids, \
                f"Supplier {supplier.id} matches query '{query}' but is missing from results"
    
    # Check nodes: all matching items from original data should be in results
    result_node_ids = {n.id for n in result.nodes}
    for node in data.nodes:
        matches = False
        for field in fields:
            if hasattr(node, field):
                value = getattr(node, field)
                if value is not None and query_lower in str(value).lower():
                    matches = True
                    break
        if matches:
            assert node.id in result_node_ids, \
                f"Node {node.id} matches query '{query}' but is missing from results"


@pytest.mark.property
@given(
    data=supply_chain_data_strategy(min_items=1, max_items=20),
    query=text_strategy(min_size=1, max_size=10),
    fields=st.lists(
        st.sampled_from(['id', 'name', 'origin', 'destination', 'location', 'category']),
        min_size=1,
        max_size=3,
        unique=True
    )
)
@settings(max_examples=100)
def test_search_is_case_insensitive(data, query, fields):
    """
    Property 4: Search Returns Only Matching Results (Case Insensitivity)
    
    **Validates: Requirements 2.5, 7.1**
    
    Search should be case-insensitive, meaning queries in different cases
    should return the same results.
    """
    engine = FilterEngine()
    
    # Search with original query
    result1 = engine.search(data, query, fields)
    
    # Search with uppercase query
    result2 = engine.search(data, query.upper(), fields)
    
    # Search with lowercase query
    result3 = engine.search(data, query.lower(), fields)
    
    # All results should be identical
    assert {s.id for s in result1.shipments} == {s.id for s in result2.shipments} == {s.id for s in result3.shipments}, \
        "Search should be case-insensitive for shipments"
    
    assert {i.id for i in result1.inventory} == {i.id for i in result2.inventory} == {i.id for i in result3.inventory}, \
        "Search should be case-insensitive for inventory"
    
    assert {s.id for s in result1.suppliers} == {s.id for s in result2.suppliers} == {s.id for s in result3.suppliers}, \
        "Search should be case-insensitive for suppliers"
    
    assert {n.id for n in result1.nodes} == {n.id for n in result2.nodes} == {n.id for n in result3.nodes}, \
        "Search should be case-insensitive for nodes"


@pytest.mark.property
@given(data=supply_chain_data_strategy(min_items=1, max_items=20))
@settings(max_examples=100)
def test_empty_query_returns_original_data(data):
    """
    Property 4: Search Returns Only Matching Results (Empty Query)
    
    **Validates: Requirements 2.5, 7.1**
    
    When search query is empty or None, the search should return the original
    dataset unchanged.
    """
    engine = FilterEngine()
    
    # Test with empty string
    result1 = engine.search(data, "", ['id', 'name'])
    assert len(result1.shipments) == len(data.shipments), \
        "Empty query should return all shipments"
    assert len(result1.inventory) == len(data.inventory), \
        "Empty query should return all inventory"
    
    # Test with None
    result2 = engine.search(data, None, ['id', 'name'])
    assert len(result2.shipments) == len(data.shipments), \
        "None query should return all shipments"
    assert len(result2.inventory) == len(data.inventory), \
        "None query should return all inventory"


@pytest.mark.property
@given(
    data=supply_chain_data_strategy(min_items=1, max_items=20),
    query=text_strategy(min_size=1, max_size=10)
)
@settings(max_examples=100)
def test_empty_fields_returns_original_data(data, query):
    """
    Property 4: Search Returns Only Matching Results (Empty Fields)
    
    **Validates: Requirements 2.5, 7.1**
    
    When search fields list is empty or None, the search should return the
    original dataset unchanged.
    """
    engine = FilterEngine()
    
    # Test with empty list
    result1 = engine.search(data, query, [])
    assert len(result1.shipments) == len(data.shipments), \
        "Empty fields should return all shipments"
    assert len(result1.inventory) == len(data.inventory), \
        "Empty fields should return all inventory"
    
    # Test with None
    result2 = engine.search(data, query, None)
    assert len(result2.shipments) == len(data.shipments), \
        "None fields should return all shipments"
    assert len(result2.inventory) == len(data.inventory), \
        "None fields should return all inventory"


@pytest.mark.property
@given(
    data=supply_chain_data_strategy(min_items=1, max_items=20),
    query=text_strategy(min_size=1, max_size=10),
    fields=st.lists(
        st.sampled_from(['id', 'name', 'origin', 'destination', 'location', 'category']),
        min_size=1,
        max_size=3,
        unique=True
    )
)
@settings(max_examples=100)
def test_search_results_are_subset_of_original(data, query, fields):
    """
    Property 4: Search Returns Only Matching Results (Subset Property)
    
    **Validates: Requirements 2.5, 7.1**
    
    Search results should always be a subset of the original data - no new
    items should be created by the search operation.
    """
    engine = FilterEngine()
    result = engine.search(data, query, fields)
    
    # Verify all result IDs exist in original data
    original_shipment_ids = {s.id for s in data.shipments}
    result_shipment_ids = {s.id for s in result.shipments}
    assert result_shipment_ids.issubset(original_shipment_ids), \
        "Search results for shipments must be a subset of original data"
    
    original_inventory_ids = {i.id for i in data.inventory}
    result_inventory_ids = {i.id for i in result.inventory}
    assert result_inventory_ids.issubset(original_inventory_ids), \
        "Search results for inventory must be a subset of original data"
    
    original_supplier_ids = {s.id for s in data.suppliers}
    result_supplier_ids = {s.id for s in result.suppliers}
    assert result_supplier_ids.issubset(original_supplier_ids), \
        "Search results for suppliers must be a subset of original data"
    
    original_node_ids = {n.id for n in data.nodes}
    result_node_ids = {n.id for n in result.nodes}
    assert result_node_ids.issubset(original_node_ids), \
        "Search results for nodes must be a subset of original data"


@pytest.mark.property
@given(
    data=supply_chain_data_strategy(min_items=1, max_items=20),
    query=text_strategy(min_size=1, max_size=10),
    fields=st.lists(
        st.sampled_from(['id', 'name', 'origin', 'destination', 'location', 'category']),
        min_size=1,
        max_size=3,
        unique=True
    )
)
@settings(max_examples=100)
def test_search_maintains_referential_integrity(data, query, fields):
    """
    Property 4: Search Returns Only Matching Results (Referential Integrity)
    
    **Validates: Requirements 2.5, 7.1**
    
    Search results should maintain referential integrity - edges should only
    connect nodes that exist in the filtered result set.
    """
    engine = FilterEngine()
    result = engine.search(data, query, fields)
    
    # Get set of result node IDs
    result_node_ids = {n.id for n in result.nodes}
    
    # Verify all edges only connect nodes in the result set
    for edge in result.edges:
        assert edge.source_node_id in result_node_ids, \
            f"Edge {edge.id} references non-existent source node {edge.source_node_id}"
        assert edge.target_node_id in result_node_ids, \
            f"Edge {edge.id} references non-existent target node {edge.target_node_id}"


@pytest.mark.property
@given(
    data=supply_chain_data_strategy(min_items=1, max_items=20),
    query=text_strategy(min_size=1, max_size=10),
    fields=st.lists(
        st.sampled_from(['id', 'name', 'origin', 'destination', 'location', 'category']),
        min_size=1,
        max_size=3,
        unique=True
    )
)
@settings(max_examples=100)
def test_search_is_deterministic(data, query, fields):
    """
    Property 4: Search Returns Only Matching Results (Determinism)
    
    **Validates: Requirements 2.5, 7.1**
    
    Searching the same data with the same query and fields multiple times
    should produce identical results (deterministic behavior).
    """
    engine = FilterEngine()
    
    # Perform search twice
    result1 = engine.search(data, query, fields)
    result2 = engine.search(data, query, fields)
    
    # Verify results are identical
    assert {s.id for s in result1.shipments} == {s.id for s in result2.shipments}, \
        "Search should be deterministic for shipments"
    assert {i.id for i in result1.inventory} == {i.id for i in result2.inventory}, \
        "Search should be deterministic for inventory"
    assert {s.id for s in result1.suppliers} == {s.id for s in result2.suppliers}, \
        "Search should be deterministic for suppliers"
    assert {n.id for n in result1.nodes} == {n.id for n in result2.nodes}, \
        "Search should be deterministic for nodes"

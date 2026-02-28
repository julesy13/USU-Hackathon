"""
Unit tests for ExportService.

Tests the export functionality for CSV and Excel formats, as well as data preparation.
"""

import pytest
import pandas as pd
from datetime import datetime
from io import BytesIO

from src.export_service import ExportService
from src.models import (
    SupplyChainData, Shipment, InventoryItem, Supplier, Node, Edge,
    ShipmentStatus, NodeType, NodeStatus
)
from src.filter_engine import FilterCriteria


@pytest.fixture
def export_service():
    """Create an ExportService instance for testing."""
    return ExportService()


@pytest.fixture
def sample_supply_chain_data():
    """Create sample supply chain data for testing."""
    shipments = [
        Shipment(
            id="S001",
            origin="New York",
            destination="Los Angeles",
            current_location="Chicago",
            status=ShipmentStatus.IN_TRANSIT,
            estimated_delivery=datetime(2024, 1, 15, 10, 0),
            actual_delivery=None,
            items=["item1", "item2"],
            supplier_id="SUP001",
            created_at=datetime(2024, 1, 1, 8, 0),
            updated_at=datetime(2024, 1, 10, 12, 0)
        )
    ]
    
    inventory = [
        InventoryItem(
            id="INV001",
            name="Widget A",
            category="Electronics",
            location="Warehouse 1",
            quantity=100.0,
            unit="pieces",
            reorder_point=20.0,
            last_updated=datetime(2024, 1, 10, 9, 0)
        )
    ]
    
    suppliers = [
        Supplier(
            id="SUP001",
            name="Acme Corp",
            contact="contact@acme.com",
            performance_score=85.5,
            on_time_delivery_rate=90.0,
            quality_score=88.0,
            average_lead_time=5.5,
            total_shipments=100,
            last_updated=datetime(2024, 1, 10, 10, 0)
        )
    ]
    
    nodes = [
        Node(
            id="N001",
            name="Distribution Center",
            type=NodeType.WAREHOUSE,
            location="Chicago",
            latitude=41.8781,
            longitude=-87.6298,
            status=NodeStatus.NORMAL,
            capacity=1000.0
        )
    ]
    
    edges = [
        Edge(
            id="E001",
            source_node_id="N001",
            target_node_id="N002",
            shipment_ids=["S001"],
            active=True
        )
    ]
    
    return SupplyChainData(
        shipments=shipments,
        inventory=inventory,
        suppliers=suppliers,
        nodes=nodes,
        edges=edges,
        last_updated=datetime(2024, 1, 10, 12, 0)
    )


def test_export_to_csv_basic(export_service):
    """Test basic CSV export functionality."""
    # Create a simple DataFrame
    df = pd.DataFrame({
        'id': ['1', '2', '3'],
        'name': ['Item A', 'Item B', 'Item C'],
        'quantity': [10, 20, 30]
    })
    
    # Export to CSV
    csv_bytes = export_service.export_to_csv(df, "test.csv")
    
    # Verify output
    assert isinstance(csv_bytes, bytes)
    assert len(csv_bytes) > 0
    
    # Verify content can be read back
    csv_str = csv_bytes.decode('utf-8')
    assert 'id,name,quantity' in csv_str
    assert 'Item A' in csv_str
    assert 'Item B' in csv_str


def test_export_to_excel_basic(export_service):
    """Test basic Excel export functionality."""
    # Create a simple DataFrame
    df = pd.DataFrame({
        'id': ['1', '2', '3'],
        'name': ['Item A', 'Item B', 'Item C'],
        'quantity': [10, 20, 30]
    })
    
    # Export to Excel
    excel_bytes = export_service.export_to_excel(df, "test.xlsx")
    
    # Verify output
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0
    
    # Verify content can be read back
    df_read = pd.read_excel(BytesIO(excel_bytes))
    assert len(df_read) == 3
    assert list(df_read.columns) == ['id', 'name', 'quantity']
    assert df_read['name'].tolist() == ['Item A', 'Item B', 'Item C']


def test_prepare_export_data_no_filters(export_service, sample_supply_chain_data):
    """Test preparing export data without filters."""
    filters = FilterCriteria()
    
    df = export_service.prepare_export_data(sample_supply_chain_data, filters)
    
    # Verify DataFrame is created
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    
    # Verify all entity types are included
    assert 'type' in df.columns
    entity_types = df['type'].unique()
    assert 'shipment' in entity_types
    assert 'inventory' in entity_types
    assert 'supplier' in entity_types
    assert 'node' in entity_types
    assert 'edge' in entity_types


def test_prepare_export_data_with_filters(export_service, sample_supply_chain_data):
    """Test preparing export data with filters applied."""
    # Create filter for specific status
    filters = FilterCriteria(status=['in_transit'])
    
    df = export_service.prepare_export_data(sample_supply_chain_data, filters)
    
    # Verify DataFrame is created
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    
    # Verify shipment with in_transit status is included
    shipment_rows = df[df['type'] == 'shipment']
    assert len(shipment_rows) > 0
    assert shipment_rows.iloc[0]['status'] == 'in_transit'


def test_prepare_export_data_empty_dataset(export_service):
    """Test preparing export data with empty dataset."""
    empty_data = SupplyChainData(
        shipments=[],
        inventory=[],
        suppliers=[],
        nodes=[],
        edges=[],
        last_updated=datetime(2024, 1, 10, 12, 0)
    )
    
    filters = FilterCriteria()
    df = export_service.prepare_export_data(empty_data, filters)
    
    # Verify empty DataFrame is returned
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


def test_export_to_csv_empty_dataframe(export_service):
    """Test CSV export with empty DataFrame."""
    df = pd.DataFrame()
    
    csv_bytes = export_service.export_to_csv(df, "empty.csv")
    
    # Verify output is valid (just headers or empty)
    assert isinstance(csv_bytes, bytes)


def test_export_to_excel_empty_dataframe(export_service):
    """Test Excel export with empty DataFrame."""
    df = pd.DataFrame()
    
    excel_bytes = export_service.export_to_excel(df, "empty.xlsx")
    
    # Verify output is valid
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0


def test_prepare_export_data_preserves_data_types(export_service, sample_supply_chain_data):
    """Test that prepare_export_data preserves important data types."""
    filters = FilterCriteria()
    
    df = export_service.prepare_export_data(sample_supply_chain_data, filters)
    
    # Check shipment data
    shipment_row = df[df['type'] == 'shipment'].iloc[0]
    assert shipment_row['id'] == 'S001'
    assert shipment_row['status'] == 'in_transit'
    assert 'item1' in shipment_row['items']
    
    # Check inventory data
    inventory_row = df[df['type'] == 'inventory'].iloc[0]
    assert inventory_row['id'] == 'INV001'
    assert inventory_row['quantity'] == 100.0
    
    # Check supplier data
    supplier_row = df[df['type'] == 'supplier'].iloc[0]
    assert supplier_row['id'] == 'SUP001'
    assert supplier_row['performance_score'] == 85.5

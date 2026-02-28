"""
Data access layer for Supply Chain Visibility application.

This module provides the DataAccessService class that abstracts data source access,
implements caching, and handles data persistence.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from src.models import (
    SupplyChainData,
    Shipment,
    InventoryItem,
    Supplier,
    Node,
    Edge,
    StatusUpdate,
    ShipmentStatus,
    NodeType,
    NodeStatus,
)


class DataAccessService:
    """
    Abstracts data source access and implements caching.
    
    This service provides methods to load data from various sources (CSV, database, API),
    cache data in memory for performance, refresh data, and persist updates.
    """
    
    def __init__(self):
        """Initialize the data access service with empty cache."""
        self._cache: Optional[SupplyChainData] = None
        self._cache_timestamp: Optional[datetime] = None
    
    def load_data(self, source: str = "data") -> SupplyChainData:
        """
        Load data from configured source.
        
        Currently supports CSV files. The source parameter should be a path to a directory
        containing CSV files for each entity type (shipments.csv, inventory.csv, etc.).
        
        Args:
            source: Path to data source (directory containing CSV files). Defaults to "data".
                   Can be "csv" (alias for "data") or any directory path.
            
        Returns:
            SupplyChainData object containing all loaded data
            
        Raises:
            FileNotFoundError: If source directory or required CSV files don't exist
            ValueError: If CSV data is invalid or malformed
        """
        # Handle "csv" as an alias for "data" directory
        if source == "csv":
            source = "data"
        
        source_path = Path(source)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Data source not found: {source}")
        
        # Load each entity type from CSV
        shipments = self._load_shipments_csv(source_path / "shipments.csv")
        inventory = self._load_inventory_csv(source_path / "inventory.csv")
        suppliers = self._load_suppliers_csv(source_path / "suppliers.csv")
        nodes = self._load_nodes_csv(source_path / "nodes.csv")
        edges = self._load_edges_csv(source_path / "edges.csv")
        
        # Create SupplyChainData object
        data = SupplyChainData(
            shipments=shipments,
            inventory=inventory,
            suppliers=suppliers,
            nodes=nodes,
            edges=edges,
            last_updated=datetime.now()
        )
        
        # Update cache
        self._cache = data
        self._cache_timestamp = datetime.now()
        
        return data
    
    def get_cached_data(self) -> Optional[SupplyChainData]:
        """
        Get cached data if available.
        
        Returns:
            Cached SupplyChainData object if available, None otherwise
        """
        return self._cache
    
    def refresh_data(self, source: str = "data") -> SupplyChainData:
        """
        Refresh data from source.
        
        This method reloads data from the source and updates the cache.
        
        Args:
            source: Path to data source. Defaults to "data".
            
        Returns:
            Refreshed SupplyChainData object
        """
        return self.load_data(source)
    
    def persist_update(self, update: StatusUpdate, source: str) -> None:
        """
        Persist status update to data store.
        
        This method updates the cached data and writes the change to the data store.
        For CSV sources, this updates the corresponding CSV file.
        
        Args:
            update: StatusUpdate object containing the update details
            source: Path to data source
            
        Raises:
            ValueError: If entity type or entity ID is not found
            FileNotFoundError: If source directory doesn't exist
        """
        if self._cache is None:
            raise ValueError("No cached data available. Load data first.")
        
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Data source not found: {source}")
        
        # Update cached data based on entity type
        if update.entity_type == "shipment":
            self._update_shipment(update)
            self._persist_shipments_csv(source_path / "shipments.csv")
        elif update.entity_type == "inventory":
            self._update_inventory(update)
            self._persist_inventory_csv(source_path / "inventory.csv")
        elif update.entity_type == "supplier":
            self._update_supplier(update)
            self._persist_suppliers_csv(source_path / "suppliers.csv")
        else:
            raise ValueError(f"Unknown entity type: {update.entity_type}")
        
        # Update cache timestamp
        self._cache.last_updated = datetime.now()
        self._cache_timestamp = datetime.now()
    
    # Private helper methods for CSV loading
    
    def _load_shipments_csv(self, filepath: Path) -> list[Shipment]:
        """Load shipments from CSV file."""
        if not filepath.exists():
            return []
        
        shipments = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                shipment = Shipment(
                    id=row['id'],
                    origin=row['origin'],
                    destination=row['destination'],
                    current_location=row['current_location'],
                    status=ShipmentStatus(row['status']),
                    estimated_delivery=datetime.fromisoformat(row['estimated_delivery']),
                    actual_delivery=datetime.fromisoformat(row['actual_delivery']) if row.get('actual_delivery') else None,
                    items=row['items'].split(';') if row.get('items') else [],
                    supplier_id=row['supplier_id'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                shipments.append(shipment)
        
        return shipments
    
    def _load_inventory_csv(self, filepath: Path) -> list[InventoryItem]:
        """Load inventory items from CSV file."""
        if not filepath.exists():
            return []
        
        inventory = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = InventoryItem(
                    id=row['id'],
                    name=row['name'],
                    category=row['category'],
                    location=row['location'],
                    quantity=float(row['quantity']),
                    unit=row['unit'],
                    reorder_point=float(row['reorder_point']),
                    last_updated=datetime.fromisoformat(row['last_updated'])
                )
                inventory.append(item)
        
        return inventory
    
    def _load_suppliers_csv(self, filepath: Path) -> list[Supplier]:
        """Load suppliers from CSV file."""
        if not filepath.exists():
            return []
        
        suppliers = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                supplier = Supplier(
                    id=row['id'],
                    name=row['name'],
                    contact=row['contact'],
                    performance_score=float(row['performance_score']),
                    on_time_delivery_rate=float(row['on_time_delivery_rate']),
                    quality_score=float(row['quality_score']),
                    average_lead_time=float(row['average_lead_time']),
                    total_shipments=int(row['total_shipments']),
                    last_updated=datetime.fromisoformat(row['last_updated'])
                )
                suppliers.append(supplier)
        
        return suppliers
    
    def _load_nodes_csv(self, filepath: Path) -> list[Node]:
        """Load network nodes from CSV file."""
        if not filepath.exists():
            return []
        
        nodes = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                node = Node(
                    id=row['id'],
                    name=row['name'],
                    type=NodeType(row['type']),
                    location=row['location'],
                    latitude=float(row['latitude']) if row.get('latitude') else None,
                    longitude=float(row['longitude']) if row.get('longitude') else None,
                    status=NodeStatus(row['status']),
                    capacity=float(row['capacity']) if row.get('capacity') else None
                )
                nodes.append(node)
        
        return nodes
    
    def _load_edges_csv(self, filepath: Path) -> list[Edge]:
        """Load network edges from CSV file."""
        if not filepath.exists():
            return []
        
        edges = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                edge = Edge(
                    id=row['id'],
                    source_node_id=row['source_node_id'],
                    target_node_id=row['target_node_id'],
                    shipment_ids=row['shipment_ids'].split(';') if row.get('shipment_ids') else [],
                    active=row['active'].lower() == 'true'
                )
                edges.append(edge)
        
        return edges
    
    # Private helper methods for updating cached data
    
    def _update_shipment(self, update: StatusUpdate) -> None:
        """Update a shipment in the cache."""
        if self._cache is None:
            raise ValueError("No cached data available")
        
        shipment = next((s for s in self._cache.shipments if s.id == update.entity_id), None)
        if shipment is None:
            raise ValueError(f"Shipment not found: {update.entity_id}")
        
        # Update the field
        if hasattr(shipment, update.field):
            setattr(shipment, update.field, update.new_value)
            shipment.updated_at = update.timestamp
        else:
            raise ValueError(f"Invalid field for shipment: {update.field}")
    
    def _update_inventory(self, update: StatusUpdate) -> None:
        """Update an inventory item in the cache."""
        if self._cache is None:
            raise ValueError("No cached data available")
        
        item = next((i for i in self._cache.inventory if i.id == update.entity_id), None)
        if item is None:
            raise ValueError(f"Inventory item not found: {update.entity_id}")
        
        # Update the field
        if hasattr(item, update.field):
            setattr(item, update.field, update.new_value)
            item.last_updated = update.timestamp
        else:
            raise ValueError(f"Invalid field for inventory item: {update.field}")
    
    def _update_supplier(self, update: StatusUpdate) -> None:
        """Update a supplier in the cache."""
        if self._cache is None:
            raise ValueError("No cached data available")
        
        supplier = next((s for s in self._cache.suppliers if s.id == update.entity_id), None)
        if supplier is None:
            raise ValueError(f"Supplier not found: {update.entity_id}")
        
        # Update the field
        if hasattr(supplier, update.field):
            setattr(supplier, update.field, update.new_value)
            supplier.last_updated = update.timestamp
        else:
            raise ValueError(f"Invalid field for supplier: {update.field}")
    
    # Private helper methods for persisting to CSV
    
    def _persist_shipments_csv(self, filepath: Path) -> None:
        """Persist shipments to CSV file."""
        if self._cache is None:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'origin', 'destination', 'current_location', 'status',
                         'estimated_delivery', 'actual_delivery', 'items', 'supplier_id',
                         'created_at', 'updated_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for shipment in self._cache.shipments:
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
    
    def _persist_inventory_csv(self, filepath: Path) -> None:
        """Persist inventory items to CSV file."""
        if self._cache is None:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'name', 'category', 'location', 'quantity',
                         'unit', 'reorder_point', 'last_updated']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in self._cache.inventory:
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
    
    def _persist_suppliers_csv(self, filepath: Path) -> None:
        """Persist suppliers to CSV file."""
        if self._cache is None:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'name', 'contact', 'performance_score',
                         'on_time_delivery_rate', 'quality_score', 'average_lead_time',
                         'total_shipments', 'last_updated']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for supplier in self._cache.suppliers:
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

"""
Alert generation module for Supply Chain Visibility application.

This module provides the AlertGenerator class that generates alerts based on
business rules for shipment delays, low inventory, and supplier performance issues.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any

from src.models import (
    Alert,
    AlertType,
    AlertSeverity,
    Shipment,
    InventoryItem,
    Supplier,
    SupplyChainData,
    ShipmentStatus,
)


class AlertGenerator:
    """
    Generates and manages supply chain alerts.
    
    This class implements business rules to detect conditions that require attention,
    such as shipment delays, low inventory levels, and poor supplier performance.
    """
    
    def __init__(self):
        """Initialize the alert generator with empty alert storage."""
        self._alerts: Dict[str, Alert] = {}
    
    def generate_alerts(self, data: SupplyChainData, rules: Dict[str, Any]) -> List[Alert]:
        """
        Generate alerts based on business rules.
        
        This method checks all supply chain data against configured rules and generates
        alerts for any conditions that exceed thresholds.
        
        Args:
            data: SupplyChainData object containing all supply chain information
            rules: Dictionary containing alert rules with thresholds:
                - delay_threshold_hours: Hours past estimated delivery to trigger delay alert
                - low_stock_threshold: Percentage of reorder point to trigger low stock alert
                - supplier_performance_threshold: Minimum acceptable performance score
                
        Returns:
            List of Alert objects for all detected conditions
        """
        alerts = []
        
        # Check for shipment delays
        delay_alerts = self.check_shipment_delays(
            data.shipments,
            rules.get('delay_threshold_hours', 24)
        )
        alerts.extend(delay_alerts)
        
        # Check for low inventory
        inventory_alerts = self.check_inventory_levels(
            data.inventory,
            rules.get('low_stock_threshold', 1.0)
        )
        alerts.extend(inventory_alerts)
        
        # Check for supplier performance issues
        supplier_alerts = self.check_supplier_performance(
            data.suppliers,
            rules.get('supplier_performance_threshold', 70.0)
        )
        alerts.extend(supplier_alerts)
        
        # Store alerts for acknowledgment tracking
        for alert in alerts:
            self._alerts[alert.id] = alert
        
        return alerts
    
    def check_shipment_delays(self, shipments: List[Shipment], delay_threshold_hours: float = 24) -> List[Alert]:
        """
        Check for delayed shipments.
        
        Generates alerts for shipments that are past their estimated delivery time
        by more than the threshold, or shipments explicitly marked as delayed.
        
        Args:
            shipments: List of Shipment objects to check
            delay_threshold_hours: Hours past estimated delivery to trigger alert
            
        Returns:
            List of Alert objects for delayed shipments
        """
        alerts = []
        now = datetime.now()
        
        for shipment in shipments:
            # Check if shipment is explicitly marked as delayed
            if shipment.status == ShipmentStatus.DELAYED:
                severity = self._calculate_delay_severity(shipment, now, delay_threshold_hours)
                alert = Alert(
                    id=str(uuid.uuid4()),
                    type=AlertType.SHIPMENT_DELAY,
                    severity=severity,
                    message=f"Shipment {shipment.id} from {shipment.origin} to {shipment.destination} is delayed",
                    entity_id=shipment.id,
                    created_at=now,
                    acknowledged=False,
                    acknowledged_at=None
                )
                alerts.append(alert)
            
            # Check if shipment is past estimated delivery and not delivered
            elif shipment.status != ShipmentStatus.DELIVERED:
                hours_overdue = (now - shipment.estimated_delivery).total_seconds() / 3600
                if hours_overdue > delay_threshold_hours:
                    severity = self._calculate_delay_severity(shipment, now, delay_threshold_hours)
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        type=AlertType.SHIPMENT_DELAY,
                        severity=severity,
                        message=f"Shipment {shipment.id} is {int(hours_overdue)} hours overdue",
                        entity_id=shipment.id,
                        created_at=now,
                        acknowledged=False,
                        acknowledged_at=None
                    )
                    alerts.append(alert)
        
        return alerts
    
    def check_inventory_levels(self, inventory: List[InventoryItem], low_stock_threshold: float = 1.0) -> List[Alert]:
        """
        Check for critical low stock.
        
        Generates alerts for inventory items that have fallen below the critical threshold
        relative to their reorder point.
        
        Args:
            inventory: List of InventoryItem objects to check
            low_stock_threshold: Multiplier of reorder_point to trigger alert (default 1.0)
            
        Returns:
            List of Alert objects for low stock items
        """
        alerts = []
        now = datetime.now()
        
        for item in inventory:
            threshold = item.reorder_point * low_stock_threshold
            if item.quantity < threshold:
                severity = self._calculate_inventory_severity(item, threshold)
                alert = Alert(
                    id=str(uuid.uuid4()),
                    type=AlertType.LOW_STOCK,
                    severity=severity,
                    message=f"Low stock alert: {item.name} at {item.location} has {item.quantity} {item.unit} (threshold: {threshold})",
                    entity_id=item.id,
                    created_at=now,
                    acknowledged=False,
                    acknowledged_at=None
                )
                alerts.append(alert)
        
        return alerts
    
    def check_supplier_performance(self, suppliers: List[Supplier], performance_threshold: float = 70.0) -> List[Alert]:
        """
        Check for underperforming suppliers.
        
        Generates alerts for suppliers whose performance score falls below
        the acceptable threshold.
        
        Args:
            suppliers: List of Supplier objects to check
            performance_threshold: Minimum acceptable performance score (0-100)
            
        Returns:
            List of Alert objects for underperforming suppliers
        """
        alerts = []
        now = datetime.now()
        
        for supplier in suppliers:
            if supplier.performance_score < performance_threshold:
                severity = self._calculate_supplier_severity(supplier, performance_threshold)
                alert = Alert(
                    id=str(uuid.uuid4()),
                    type=AlertType.SUPPLIER_PERFORMANCE,
                    severity=severity,
                    message=f"Supplier {supplier.name} performance below threshold: {supplier.performance_score:.1f}% (threshold: {performance_threshold}%)",
                    entity_id=supplier.id,
                    created_at=now,
                    acknowledged=False,
                    acknowledged_at=None
                )
                alerts.append(alert)
        
        return alerts
    
    def acknowledge_alert(self, alert_id: str) -> None:
        """
        Mark alert as acknowledged.
        
        Updates the alert's acknowledged status and sets the acknowledgment timestamp.
        
        Args:
            alert_id: ID of the alert to acknowledge
            
        Raises:
            ValueError: If alert_id is not found
        """
        if alert_id not in self._alerts:
            raise ValueError(f"Alert not found: {alert_id}")
        
        alert = self._alerts[alert_id]
        alert.acknowledged = True
        alert.acknowledged_at = datetime.now()
    
    # Private helper methods for severity calculation
    
    def _calculate_delay_severity(self, shipment: Shipment, now: datetime, threshold_hours: float) -> AlertSeverity:
        """Calculate severity level for shipment delay."""
        hours_overdue = (now - shipment.estimated_delivery).total_seconds() / 3600
        
        if hours_overdue > threshold_hours * 3:
            return AlertSeverity.CRITICAL
        elif hours_overdue > threshold_hours * 2:
            return AlertSeverity.HIGH
        elif hours_overdue > threshold_hours:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _calculate_inventory_severity(self, item: InventoryItem, threshold: float) -> AlertSeverity:
        """Calculate severity level for low inventory."""
        percentage_of_threshold = (item.quantity / threshold * 100) if threshold > 0 else 0
        
        if percentage_of_threshold < 25:
            return AlertSeverity.CRITICAL
        elif percentage_of_threshold < 50:
            return AlertSeverity.HIGH
        elif percentage_of_threshold < 75:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _calculate_supplier_severity(self, supplier: Supplier, threshold: float) -> AlertSeverity:
        """Calculate severity level for supplier performance."""
        gap = threshold - supplier.performance_score
        
        if gap > 30:
            return AlertSeverity.CRITICAL
        elif gap > 20:
            return AlertSeverity.HIGH
        elif gap > 10:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW

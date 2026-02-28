# Implementation Plan: Supply Chain Visibility

## Overview

This implementation plan breaks down the Supply Chain Visibility Streamlit application into discrete, actionable tasks. The application follows a layered architecture with clear separation between presentation (Streamlit UI), business logic, and data access layers. Implementation will proceed incrementally, building core data models first, then data access, business logic, and finally the UI components.

The plan includes both implementation tasks and property-based testing tasks using Hypothesis to validate the 24 correctness properties defined in the design document. Testing tasks are marked as optional with "*" to allow for flexible MVP delivery.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure (src/, tests/unit/, tests/property/, tests/strategies/)
  - Create requirements.txt with dependencies: streamlit, pandas, plotly, hypothesis, pytest
  - Create main entry point app.py
  - Set up pytest configuration
  - _Requirements: 9.1, 10.1_

- [ ] 2. Implement core data models and enumerations
  - [x] 2.1 Create data model classes in src/models.py
    - Implement Shipment, InventoryItem, Supplier, Node, Edge, Alert, StatusUpdate dataclasses
    - Implement enumerations: ShipmentStatus, NodeType, NodeStatus, AlertType, AlertSeverity
    - Add type hints and validation
    - _Requirements: 2.1, 3.1, 4.1, 5.1, 6.1_
  
  - [x] 2.2 Write property test for data model validation
    - **Property 2: Detail Views Contain Required Fields**
    - **Validates: Requirements 2.2, 3.5, 4.3, 6.1**
    - Test that all required fields are present in each data model
    - _Requirements: 2.2, 3.5, 4.3, 6.1_

- [ ] 3. Implement data access layer
  - [x] 3.1 Create DataAccessService in src/data_access.py
    - Implement load_data() method with CSV support
    - Implement get_cached_data() with in-memory caching
    - Implement refresh_data() method
    - Implement persist_update() method
    - _Requirements: 9.1, 9.2, 9.4_
  
  - [x] 3.2 Write property test for data loading
    - **Property 22: Multi-Source Data Loading**
    - **Validates: Requirements 9.4**
    - Test that data loader returns standard SupplyChainData format
    - _Requirements: 9.4_
  
  - [x] 3.3 Write property test for status update persistence
    - **Property 21: Status Update Persistence**
    - **Validates: Requirements 9.2**
    - Test round-trip property for status updates
    - _Requirements: 9.2_
  
  - [x] 3.4 Create sample data files
    - Create sample CSV files for shipments, inventory, suppliers, nodes, edges
    - Place in data/ directory
    - _Requirements: 9.1_

- [ ] 4. Implement filter engine
  - [x] 4.1 Create FilterEngine in src/filter_engine.py
    - Implement FilterCriteria dataclass
    - Implement apply_filters() method
    - Implement search() method
    - Implement reset_filters() method
    - _Requirements: 7.1, 7.2, 7.5_
  
  - [x] 4.2 Write property test for filter application
    - **Property 6: Filter Application Preserves Invariants**
    - **Validates: Requirements 3.3, 7.2**
    - Test that filtered data is subset of original and maintains referential integrity
    - _Requirements: 3.3, 7.2_
  
  - [x] 4.3 Write property test for search functionality
    - **Property 4: Search Returns Only Matching Results**
    - **Validates: Requirements 2.5, 7.1**
    - Test that all results match query and no matching items excluded
    - _Requirements: 2.5, 7.1_
  
  - [x] 4.4 Write property test for filter persistence
    - **Property 17: Filter Persistence Round Trip**
    - **Validates: Requirements 7.4**
    - Test that persisted filters can be retrieved correctly
    - _Requirements: 7.4_
  
  - [~] 4.5 Write property test for filter reset
    - **Property 18: Filter Reset to Default State**
    - **Validates: Requirements 7.5**
    - Test that reset returns filters to default state
    - _Requirements: 7.5_

- [~] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement alert generator
  - [x] 6.1 Create AlertGenerator in src/alert_generator.py
    - Implement generate_alerts() method
    - Implement check_shipment_delays() method
    - Implement check_inventory_levels() method
    - Implement check_supplier_performance() method
    - Implement acknowledge_alert() method
    - _Requirements: 5.1, 5.2, 5.3, 5.5_
  
  - [~] 6.2 Write property test for alert generation rules
    - **Property 11: Alert Generation Rules**
    - **Validates: Requirements 5.1, 5.2, 5.3**
    - Test that alerts are generated for all conditions meeting thresholds
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [~] 6.3 Write property test for alert acknowledgment
    - **Property 12: Alert Acknowledgment State Transition**
    - **Validates: Requirements 5.5**
    - Test state transition when alert is acknowledged
    - _Requirements: 5.5_
  
  - [~] 6.4 Write property test for low stock detection
    - **Property 5: Low Stock Detection Threshold**
    - **Validates: Requirements 3.2**
    - Test that items are flagged correctly based on threshold
    - _Requirements: 3.2_

- [ ] 7. Implement supplier performance tracker
  - [-] 7.1 Create SupplierPerformanceTracker in src/supplier_tracker.py
    - Implement get_supplier_metrics() method
    - Implement calculate_on_time_rate() method
    - Implement rank_suppliers() method
    - Implement get_performance_history() method
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [~] 7.2 Write property test for on-time delivery rate
    - **Property 13: On-Time Delivery Rate Calculation**
    - **Validates: Requirements 6.2**
    - Test calculation formula for on-time delivery rate
    - _Requirements: 6.2_
  
  - [~] 7.3 Write property test for supplier ranking
    - **Property 14: Supplier Ranking Order**
    - **Validates: Requirements 6.3**
    - Test that suppliers are ordered correctly by ranking criteria
    - _Requirements: 6.3_
  
  - [~] 7.4 Write property test for performance history
    - **Property 15: Performance History Time Range**
    - **Validates: Requirements 6.4**
    - Test that history includes only data within specified range
    - _Requirements: 6.4_
  
  - [~] 7.5 Write property test for multi-supplier comparison
    - **Property 16: Multi-Supplier Comparison Consistency**
    - **Validates: Requirements 6.5**
    - Test that same metrics calculated for all suppliers
    - _Requirements: 6.5_

- [ ] 8. Implement export service
  - [~] 8.1 Create ExportService in src/export_service.py
    - Implement export_to_csv() method
    - Implement export_to_excel() method
    - Implement prepare_export_data() method
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [~] 8.2 Write property test for export format support
    - **Property 19: Export Format Support**
    - **Validates: Requirements 8.2**
    - Test that both CSV and Excel formats are generated successfully
    - _Requirements: 8.2_
  
  - [~] 8.3 Write property test for export content
    - **Property 20: Export Content Matches Filtered View**
    - **Validates: Requirements 8.4**
    - Test that exported data matches filtered view
    - _Requirements: 8.4_

- [~] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement shipment tracker component
  - [~] 10.1 Create ShipmentTracker in src/shipment_tracker.py
    - Implement list_shipments() method
    - Implement get_shipment_details() method
    - Implement search_shipments() method
    - _Requirements: 2.1, 2.2, 2.5_
  
  - [~] 10.2 Write property test for shipment listing
    - **Property 1: Data Completeness in Views**
    - **Validates: Requirements 1.3, 2.1**
    - Test that all shipments matching filters appear in results
    - _Requirements: 1.3, 2.1_
  
  - [~] 10.3 Write property test for status categorization
    - **Property 3: Status Categorization Preserves All Items**
    - **Validates: Requirements 2.3**
    - Test that union of all status categories equals original set
    - _Requirements: 2.3_

- [ ] 11. Implement inventory monitor component
  - [~] 11.1 Create InventoryMonitor in src/inventory_monitor.py
    - Implement get_inventory_levels() method
    - Implement get_low_stock_items() method
    - Implement get_inventory_trends() method
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [~] 11.2 Write property test for inventory listing
    - **Property 1: Data Completeness in Views**
    - **Validates: Requirements 3.1**
    - Test that all inventory items matching filters appear in results
    - _Requirements: 3.1_
  
  - [~] 11.3 Write property test for inventory trends
    - **Property 7: Inventory Trend Calculation**
    - **Validates: Requirements 3.4**
    - Test that trend calculation includes correct number of data points
    - _Requirements: 3.4_

- [ ] 12. Implement network visualizer component
  - [~] 12.1 Create NetworkVisualizer in src/network_visualizer.py
    - Implement render_network() method using plotly
    - Implement get_node_details() method
    - Implement render_geographic_map() method
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [~] 12.2 Write property test for network completeness
    - **Property 8: Network Visualization Completeness**
    - **Validates: Requirements 4.1, 4.2**
    - Test that all nodes and edges are included in visualization
    - _Requirements: 4.1, 4.2_
  
  - [~] 12.3 Write property test for node status colors
    - **Property 9: Node Status Color Mapping**
    - **Validates: Requirements 4.4**
    - Test consistent color mapping for node statuses
    - _Requirements: 4.4_
  
  - [~] 12.4 Write property test for geographic map display
    - **Property 10: Geographic Map Conditional Display**
    - **Validates: Requirements 4.5**
    - Test that only nodes with valid coordinates appear on map
    - _Requirements: 4.5_

- [ ] 13. Implement dashboard component
  - [~] 13.1 Create Dashboard in src/dashboard.py
    - Implement render() method
    - Implement get_metrics() method
    - Calculate key metrics: total shipments, in-transit count, delayed count, low stock count
    - _Requirements: 1.1, 1.3_
  
  - [~] 13.2 Write unit tests for dashboard metrics
    - Test metric calculations with known inputs
    - Test handling of empty datasets
    - _Requirements: 1.3_

- [~] 14. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Create Streamlit UI layout and navigation
  - [~] 15.1 Implement main app.py with Streamlit layout
    - Create sidebar navigation
    - Set up page routing (Dashboard, Shipments, Inventory, Network, Alerts, Suppliers)
    - Configure Streamlit page settings and theme
    - _Requirements: 10.1, 10.2, 10.4_
  
  - [~] 15.2 Implement session state management
    - Initialize session state for filters, data cache, and user selections
    - Implement filter persistence across page navigation
    - _Requirements: 7.4_

- [ ] 16. Implement Dashboard page UI
  - [~] 16.1 Create pages/dashboard_page.py
    - Render key metrics cards (total shipments, in-transit, delayed, low stock)
    - Display active alerts section
    - Add data refresh controls
    - Implement loading indicators
    - _Requirements: 1.1, 1.3, 1.4, 5.4_
  
  - [~] 16.2 Write unit tests for dashboard page rendering
    - Test rendering with various data states
    - Test error handling for data load failures
    - _Requirements: 1.4, 1.5_

- [ ] 17. Implement Shipments page UI
  - [~] 17.1 Create pages/shipments_page.py
    - Display shipments table with status categorization
    - Implement search functionality
    - Add shipment detail view modal/expander
    - Implement status filters
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  
  - [~] 17.2 Write unit tests for shipments page
    - Test search functionality
    - Test detail view rendering
    - _Requirements: 2.2, 2.5_

- [ ] 18. Implement Inventory page UI
  - [~] 18.1 Create pages/inventory_page.py
    - Display inventory table with low stock highlighting
    - Implement location and category filters
    - Add inventory trend charts
    - Display inventory item details
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [~] 18.2 Write unit tests for inventory page
    - Test low stock highlighting
    - Test trend chart rendering
    - _Requirements: 3.2, 3.4_

- [ ] 19. Implement Network page UI
  - [~] 19.1 Create pages/network_page.py
    - Render network diagram using plotly
    - Implement node selection and detail display
    - Add color coding for node status
    - Implement geographic map view toggle
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [~] 19.2 Write unit tests for network page
    - Test network rendering with various node configurations
    - Test node selection functionality
    - _Requirements: 4.3_

- [ ] 20. Implement Alerts page UI
  - [~] 20.1 Create pages/alerts_page.py
    - Display active alerts with severity indicators
    - Implement alert acknowledgment functionality
    - Add alert filtering by type and severity
    - Display alert details
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [~] 20.2 Write unit tests for alerts page
    - Test alert acknowledgment
    - Test alert filtering
    - _Requirements: 5.5_

- [ ] 21. Implement Suppliers page UI
  - [~] 21.1 Create pages/suppliers_page.py
    - Display supplier performance table with rankings
    - Implement supplier comparison view
    - Add performance history charts
    - Display detailed supplier metrics
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [~] 21.2 Write unit tests for suppliers page
    - Test ranking display
    - Test comparison view
    - _Requirements: 6.3, 6.5_

- [~] 22. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 23. Implement data export functionality in UI
  - [~] 23.1 Add export buttons to all data pages
    - Implement CSV export with download button
    - Implement Excel export with download button
    - Add export progress indicators
    - Handle export errors with user feedback
    - _Requirements: 8.1, 8.2, 8.3, 8.5_
  
  - [~] 23.2 Write unit tests for export UI
    - Test export button functionality
    - Test error handling
    - _Requirements: 8.5_

- [ ] 24. Implement data refresh and polling
  - [~] 24.1 Add automatic data refresh mechanism
    - Implement configurable polling interval
    - Add manual refresh button
    - Display last updated timestamp
    - Handle refresh errors gracefully
    - _Requirements: 1.2, 2.4, 9.5_
  
  - [~] 24.2 Write property test for polling configuration
    - **Property 23: Polling Configuration Respect**
    - **Validates: Requirements 9.5**
    - Test that refresh uses configured interval
    - _Requirements: 9.5_

- [ ] 25. Implement error handling and user feedback
  - [~] 25.1 Add error boundaries and fallback UI
    - Implement error messages for data load failures
    - Add retry mechanisms for transient failures
    - Implement read-only mode for data store unavailability
    - Add validation messages for invalid inputs
    - _Requirements: 1.5, 9.3_
  
  - [~] 25.2 Write unit tests for error handling
    - Test data unavailable scenario
    - Test invalid filter inputs
    - Test export failures
    - _Requirements: 1.5, 9.3_

- [ ] 26. Implement tooltips and help text
  - [~] 26.1 Add tooltips to complex visualizations
    - Add help text for metrics and calculations
    - Implement info icons with explanations
    - Add tooltips to network nodes and chart elements
    - _Requirements: 10.5_
  
  - [~] 26.2 Write property test for tooltip presence
    - **Property 24: Tooltip Presence for Complex Elements**
    - **Validates: Requirements 10.5**
    - Test that tooltips exist for complex elements
    - _Requirements: 10.5_

- [ ] 27. Create Hypothesis test strategies
  - [~] 27.1 Create tests/strategies/supply_chain_strategies.py
    - Implement shipment_strategy for generating Shipment instances
    - Implement inventory_strategy for generating InventoryItem instances
    - Implement supplier_strategy for generating Supplier instances
    - Implement node_strategy and edge_strategy
    - Implement filter_strategy for generating FilterCriteria
    - Implement supply_chain_data_strategy for complete datasets
    - _Requirements: All property tests_

- [ ] 28. Final integration and testing
  - [~] 28.1 Run full test suite
    - Execute all unit tests
    - Execute all property-based tests
    - Verify test coverage >80%
    - _Requirements: All_
  
  - [~] 28.2 Test end-to-end user flows
    - Test navigation between all pages
    - Test filter persistence across pages
    - Test data refresh functionality
    - Test export from multiple pages
    - _Requirements: 7.4, 10.4_
  
  - [~] 28.3 Verify responsive design
    - Test on desktop resolution (1280x720)
    - Test on tablet resolution (768x1024)
    - Verify consistent styling across pages
    - _Requirements: 10.1, 10.2, 10.4_

- [~] 29. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property-based tests use Hypothesis with minimum 100 iterations per test
- All property tests are tagged with property number and validated requirements
- Checkpoints ensure incremental validation at key milestones
- Implementation follows layered architecture: data models → data access → business logic → UI
- Streamlit's reactive model handles automatic UI updates when data changes
- Session state management ensures filter persistence across page navigation
- Error handling follows graceful degradation principles

## Testing Strategy

- Unit tests focus on specific examples, edge cases, and error conditions
- Property-based tests verify universal correctness properties across all inputs
- Test strategies in tests/strategies/ generate valid test data for Hypothesis
- Each property test explicitly references design property number and requirements
- Minimum 80% code coverage target for production code
- All tests must pass before moving to next checkpoint

"""
Phase 21: Resource Logistics Tests

Tests for shelter registry, supply chain optimization,
deployment allocation, and infrastructure monitoring.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.emergency.resource_logistics import (
    ShelterRegistry,
    SupplyChainOptimizer,
    DeploymentAllocator,
    CriticalInfrastructureMonitor,
    ResourceLogisticsManager,
    ShelterStatus,
    ShelterType,
    SupplyStatus,
    InfrastructureType,
    InfrastructureStatus,
)


class TestShelterRegistry:
    """Tests for ShelterRegistry class."""

    def test_registry_initialization(self):
        """Test ShelterRegistry initializes correctly."""
        registry = ShelterRegistry()
        assert registry is not None
        assert hasattr(registry, '_shelters')

    def test_register_shelter(self):
        """Test registering a shelter."""
        registry = ShelterRegistry()
        shelter = registry.register_shelter(
            name="Community Center Shelter",
            shelter_type=ShelterType.GENERAL,
            capacity=500,
            address={"street": "100 Main St", "city": "Miami", "state": "FL"},
            amenities=["food", "water", "medical"],
            pet_friendly=True,
            medical_capability=True,
        )
        
        assert shelter is not None
        assert shelter.name == "Community Center Shelter"
        assert shelter.capacity == 500
        assert shelter.pet_friendly is True

    def test_update_occupancy(self):
        """Test updating shelter occupancy."""
        registry = ShelterRegistry()
        shelter = registry.register_shelter(
            name="School Shelter",
            shelter_type=ShelterType.GENERAL,
            capacity=300,
            address={"street": "200 School Rd", "city": "Miami", "state": "FL"},
        )
        
        updated = registry.update_occupancy(shelter.shelter_id, 150)
        assert updated is not None
        assert updated.current_occupancy == 150

    def test_get_available_shelters(self):
        """Test getting available shelters."""
        registry = ShelterRegistry()
        registry.register_shelter(
            name="Available Shelter",
            shelter_type=ShelterType.GENERAL,
            capacity=200,
            address={"street": "300 Oak Ave", "city": "Miami", "state": "FL"},
        )
        
        available = registry.get_available_shelters()
        assert len(available) >= 1

    def test_get_capacity_summary(self):
        """Test getting capacity summary."""
        registry = ShelterRegistry()
        summary = registry.get_capacity_summary()
        
        assert summary is not None
        assert "total_shelters" in summary
        assert "total_capacity" in summary
        assert "total_occupancy" in summary


class TestSupplyChainOptimizer:
    """Tests for SupplyChainOptimizer class."""

    def test_optimizer_initialization(self):
        """Test SupplyChainOptimizer initializes correctly."""
        optimizer = SupplyChainOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, '_supplies')

    def test_track_supply(self):
        """Test tracking a supply item."""
        optimizer = SupplyChainOptimizer()
        supply = optimizer.track_supply(
            name="Bottled Water",
            category="water",
            quantity=10000,
            unit="bottles",
            location="Warehouse A",
            minimum_stock=5000,
        )
        
        assert supply is not None
        assert supply.name == "Bottled Water"
        assert supply.quantity == 10000

    def test_update_supply_quantity(self):
        """Test updating supply quantity."""
        optimizer = SupplyChainOptimizer()
        supply = optimizer.track_supply(
            name="MREs",
            category="food",
            quantity=5000,
            unit="meals",
            location="Warehouse B",
            minimum_stock=2000,
        )
        
        updated = optimizer.update_quantity(supply.item_id, 4500)
        assert updated is not None
        assert updated.quantity == 4500

    def test_get_low_stock_items(self):
        """Test getting low stock items."""
        optimizer = SupplyChainOptimizer()
        optimizer.track_supply(
            name="First Aid Kits",
            category="medical",
            quantity=100,
            unit="kits",
            location="Warehouse C",
            minimum_stock=500,
        )
        
        low_stock = optimizer.get_low_stock_items()
        assert len(low_stock) >= 1

    def test_optimize_distribution(self):
        """Test optimizing supply distribution."""
        optimizer = SupplyChainOptimizer()
        plan = optimizer.optimize_distribution(
            destinations=["shelter-001", "shelter-002"],
            supply_types=["water", "food"],
        )
        
        assert plan is not None


class TestDeploymentAllocator:
    """Tests for DeploymentAllocator class."""

    def test_allocator_initialization(self):
        """Test DeploymentAllocator initializes correctly."""
        allocator = DeploymentAllocator()
        assert allocator is not None
        assert hasattr(allocator, '_units')

    def test_register_unit(self):
        """Test registering a deployment unit."""
        allocator = DeploymentAllocator()
        unit = allocator.register_unit(
            name="Search and Rescue Team Alpha",
            deployment_type="search_rescue",
            personnel_count=12,
            equipment=["boats", "medical", "communications"],
        )
        
        assert unit is not None
        assert unit.name == "Search and Rescue Team Alpha"
        assert unit.personnel_count == 12

    def test_assign_unit(self):
        """Test assigning a unit to location."""
        allocator = DeploymentAllocator()
        unit = allocator.register_unit(
            name="Medical Response Team",
            deployment_type="medical",
            personnel_count=8,
        )
        
        assigned = allocator.assign_unit(
            unit.unit_id,
            location={"lat": 25.7617, "lng": -80.1918, "name": "Shelter A"},
        )
        
        assert assigned is not None
        assert assigned.assigned_location is not None

    def test_get_available_units(self):
        """Test getting available units."""
        allocator = DeploymentAllocator()
        allocator.register_unit(
            name="Logistics Team",
            deployment_type="logistics",
            personnel_count=6,
        )
        
        available = allocator.get_available_units()
        assert len(available) >= 1

    def test_recall_unit(self):
        """Test recalling a deployed unit."""
        allocator = DeploymentAllocator()
        unit = allocator.register_unit(
            name="Security Team",
            deployment_type="security",
            personnel_count=10,
        )
        
        allocator.assign_unit(unit.unit_id, location={"lat": 25.0, "lng": -80.0, "name": "Site B"})
        recalled = allocator.recall_unit(unit.unit_id)
        
        assert recalled is not None


class TestCriticalInfrastructureMonitor:
    """Tests for CriticalInfrastructureMonitor class."""

    def test_monitor_initialization(self):
        """Test CriticalInfrastructureMonitor initializes correctly."""
        monitor = CriticalInfrastructureMonitor()
        assert monitor is not None
        assert hasattr(monitor, '_assets')

    def test_register_asset(self):
        """Test registering an infrastructure asset."""
        monitor = CriticalInfrastructureMonitor()
        asset = monitor.register_asset(
            name="Main Power Substation",
            infrastructure_type=InfrastructureType.POWER,
            location={"lat": 25.7617, "lng": -80.1918},
            serves_population=50000,
        )
        
        assert asset is not None
        assert asset.name == "Main Power Substation"
        assert asset.infrastructure_type == InfrastructureType.POWER

    def test_report_outage(self):
        """Test reporting an outage."""
        monitor = CriticalInfrastructureMonitor()
        asset = monitor.register_asset(
            name="Water Treatment Plant",
            infrastructure_type=InfrastructureType.WATER,
            location={"lat": 25.8, "lng": -80.2},
            serves_population=100000,
        )
        
        outage = monitor.report_outage(
            asset.asset_id,
            cause="storm_damage",
            estimated_restoration="2 hours",
        )
        
        assert outage is not None
        assert outage.status == InfrastructureStatus.OFFLINE

    def test_get_active_outages(self):
        """Test getting active outages."""
        monitor = CriticalInfrastructureMonitor()
        outages = monitor.get_active_outages()
        assert isinstance(outages, list)

    def test_restore_service(self):
        """Test restoring service."""
        monitor = CriticalInfrastructureMonitor()
        asset = monitor.register_asset(
            name="Gas Pipeline",
            infrastructure_type=InfrastructureType.GAS,
            location={"lat": 25.9, "lng": -80.3},
            serves_population=25000,
        )
        
        monitor.report_outage(asset.asset_id, cause="leak")
        restored = monitor.restore_service(asset.asset_id)
        
        assert restored is not None
        assert restored.status == InfrastructureStatus.OPERATIONAL


class TestResourceLogisticsManager:
    """Tests for ResourceLogisticsManager class."""

    def test_manager_initialization(self):
        """Test ResourceLogisticsManager initializes correctly."""
        manager = ResourceLogisticsManager()
        assert manager is not None
        assert hasattr(manager, 'shelter_registry')
        assert hasattr(manager, 'supply_chain')
        assert hasattr(manager, 'deployment_allocator')
        assert hasattr(manager, 'infrastructure_monitor')

    def test_get_resource_metrics(self):
        """Test getting resource metrics."""
        manager = ResourceLogisticsManager()
        metrics = manager.get_metrics()
        
        assert metrics is not None
        assert "shelters" in metrics
        assert "supplies" in metrics
        assert "deployments" in metrics
        assert "infrastructure" in metrics

    def test_coordinate_resources(self):
        """Test coordinating resources for incident."""
        manager = ResourceLogisticsManager()
        result = manager.coordinate_resources(
            incident_id="incident-001",
            resource_requirements={
                "shelters": 3,
                "personnel": 50,
                "supplies": ["water", "food", "medical"],
            },
        )
        
        assert result is not None

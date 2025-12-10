"""
Phase 21: Evacuation AI Tests

Tests for route optimization, contraflow management,
population movement prediction, and traffic simulation.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.emergency.evacuation_ai import (
    EvacuationRouteOptimizer,
    ContraflowManager,
    PopulationMovementPredictor,
    SpecialNeedsEvacuationPlanner,
    TrafficSimulator,
    EvacuationOrderManager,
    EvacuationAIManager,
    RouteStatus,
    EvacuationPriority,
)


class TestEvacuationRouteOptimizer:
    """Tests for EvacuationRouteOptimizer class."""

    def test_optimizer_initialization(self):
        """Test EvacuationRouteOptimizer initializes correctly."""
        optimizer = EvacuationRouteOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, '_routes')

    def test_optimize_route(self):
        """Test route optimization."""
        optimizer = EvacuationRouteOptimizer()
        route = optimizer.optimize_route(
            origin={"lat": 25.7617, "lng": -80.1918},
            destination={"lat": 26.1224, "lng": -80.1373},
            avoid_zones=["flood_zone_a"],
        )
        
        assert route is not None
        assert hasattr(route, 'route_id')
        assert hasattr(route, 'distance_miles')
        assert hasattr(route, 'estimated_time_minutes')

    def test_get_route_status(self):
        """Test getting route status."""
        optimizer = EvacuationRouteOptimizer()
        route = optimizer.optimize_route(
            origin={"lat": 25.7617, "lng": -80.1918},
            destination={"lat": 26.1224, "lng": -80.1373},
        )
        
        status = optimizer.get_route_status(route.route_id)
        assert status in [RouteStatus.OPEN, RouteStatus.CONGESTED, RouteStatus.BLOCKED, RouteStatus.CLOSED]

    def test_update_route_capacity(self):
        """Test updating route capacity."""
        optimizer = EvacuationRouteOptimizer()
        route = optimizer.optimize_route(
            origin={"lat": 25.7617, "lng": -80.1918},
            destination={"lat": 26.1224, "lng": -80.1373},
        )
        
        updated = optimizer.update_route_capacity(route.route_id, 5000)
        assert updated is not None


class TestContraflowManager:
    """Tests for ContraflowManager class."""

    def test_contraflow_manager_initialization(self):
        """Test ContraflowManager initializes correctly."""
        manager = ContraflowManager()
        assert manager is not None

    def test_enable_contraflow(self):
        """Test enabling contraflow on a route."""
        manager = ContraflowManager()
        result = manager.enable_contraflow(
            route_id="route-001",
            start_point={"lat": 25.7617, "lng": -80.1918},
            end_point={"lat": 26.1224, "lng": -80.1373},
        )
        
        assert result is not None
        assert result.contraflow_enabled is True

    def test_disable_contraflow(self):
        """Test disabling contraflow."""
        manager = ContraflowManager()
        manager.enable_contraflow(
            route_id="route-002",
            start_point={"lat": 25.7617, "lng": -80.1918},
            end_point={"lat": 26.1224, "lng": -80.1373},
        )
        
        result = manager.disable_contraflow("route-002")
        assert result is not None

    def test_get_contraflow_status(self):
        """Test getting contraflow status."""
        manager = ContraflowManager()
        status = manager.get_contraflow_status("route-001")
        assert status is not None


class TestPopulationMovementPredictor:
    """Tests for PopulationMovementPredictor class."""

    def test_predictor_initialization(self):
        """Test PopulationMovementPredictor initializes correctly."""
        predictor = PopulationMovementPredictor()
        assert predictor is not None

    def test_predict_movement(self):
        """Test population movement prediction."""
        predictor = PopulationMovementPredictor()
        prediction = predictor.predict_movement(
            zone="zone-a",
            population=50000,
            evacuation_order_time=datetime.utcnow(),
        )
        
        assert prediction is not None
        assert hasattr(prediction, 'compliance_rate')
        assert hasattr(prediction, 'peak_departure_time')

    def test_estimate_clearance_time(self):
        """Test clearance time estimation."""
        predictor = PopulationMovementPredictor()
        time = predictor.estimate_clearance_time(
            zone="zone-b",
            population=30000,
            available_routes=3,
        )
        
        assert time is not None
        assert time > 0


class TestSpecialNeedsEvacuationPlanner:
    """Tests for SpecialNeedsEvacuationPlanner class."""

    def test_planner_initialization(self):
        """Test SpecialNeedsEvacuationPlanner initializes correctly."""
        planner = SpecialNeedsEvacuationPlanner()
        assert planner is not None
        assert hasattr(planner, '_registrations')

    def test_register_special_needs(self):
        """Test registering special needs evacuee."""
        planner = SpecialNeedsEvacuationPlanner()
        registration = planner.register_special_needs(
            name="John Doe",
            address={"street": "123 Main St", "city": "Miami", "state": "FL"},
            needs_type="wheelchair",
            medical_equipment=["oxygen"],
            caregiver_contact="555-1234",
        )
        
        assert registration is not None
        assert registration.needs_type == "wheelchair"

    def test_plan_special_needs_evacuation(self):
        """Test planning special needs evacuation."""
        planner = SpecialNeedsEvacuationPlanner()
        planner.register_special_needs(
            name="Jane Doe",
            address={"street": "456 Oak Ave", "city": "Miami", "state": "FL"},
            needs_type="medical",
            medical_equipment=["dialysis"],
        )
        
        plan = planner.plan_evacuation(zone="zone-a")
        assert plan is not None
        assert hasattr(plan, 'transport_assignments')

    def test_get_registrations_by_zone(self):
        """Test getting registrations by zone."""
        planner = SpecialNeedsEvacuationPlanner()
        registrations = planner.get_registrations_by_zone("zone-a")
        assert isinstance(registrations, list)


class TestTrafficSimulator:
    """Tests for TrafficSimulator class."""

    def test_simulator_initialization(self):
        """Test TrafficSimulator initializes correctly."""
        simulator = TrafficSimulator()
        assert simulator is not None

    def test_run_simulation(self):
        """Test running traffic simulation."""
        simulator = TrafficSimulator()
        result = simulator.run_simulation(
            scenario_name="Hurricane Evacuation",
            zones=["zone-a", "zone-b"],
            total_vehicles=50000,
            routes=["route-001", "route-002", "route-003"],
        )
        
        assert result is not None
        assert hasattr(result, 'simulation_id')
        assert hasattr(result, 'clearance_time_hours')
        assert hasattr(result, 'bottleneck_locations')

    def test_get_simulation_results(self):
        """Test getting simulation results."""
        simulator = TrafficSimulator()
        result = simulator.run_simulation(
            scenario_name="Test Scenario",
            zones=["zone-a"],
            total_vehicles=10000,
            routes=["route-001"],
        )
        
        results = simulator.get_simulation_results(result.simulation_id)
        assert results is not None


class TestEvacuationOrderManager:
    """Tests for EvacuationOrderManager class."""

    def test_order_manager_initialization(self):
        """Test EvacuationOrderManager initializes correctly."""
        manager = EvacuationOrderManager()
        assert manager is not None
        assert hasattr(manager, '_orders')

    def test_issue_evacuation_order(self):
        """Test issuing evacuation order."""
        manager = EvacuationOrderManager()
        order = manager.issue_order(
            zone="zone-a",
            priority=EvacuationPriority.MANDATORY,
            affected_population=25000,
            recommended_routes=["route-001", "route-002"],
            shelter_assignments=["shelter-001"],
        )
        
        assert order is not None
        assert order.zone == "zone-a"
        assert order.priority == EvacuationPriority.MANDATORY
        assert order.is_active is True

    def test_get_active_orders(self):
        """Test getting active orders."""
        manager = EvacuationOrderManager()
        manager.issue_order(
            zone="zone-b",
            priority=EvacuationPriority.VOLUNTARY,
            affected_population=10000,
        )
        
        orders = manager.get_active_orders()
        assert len(orders) >= 1

    def test_cancel_order(self):
        """Test canceling evacuation order."""
        manager = EvacuationOrderManager()
        order = manager.issue_order(
            zone="zone-c",
            priority=EvacuationPriority.IMMEDIATE,
            affected_population=5000,
        )
        
        cancelled = manager.cancel_order(order.order_id)
        assert cancelled is not None
        assert cancelled.is_active is False


class TestEvacuationAIManager:
    """Tests for EvacuationAIManager class."""

    def test_manager_initialization(self):
        """Test EvacuationAIManager initializes correctly."""
        manager = EvacuationAIManager()
        assert manager is not None
        assert hasattr(manager, 'route_optimizer')
        assert hasattr(manager, 'contraflow_manager')
        assert hasattr(manager, 'movement_predictor')
        assert hasattr(manager, 'special_needs_planner')
        assert hasattr(manager, 'traffic_simulator')
        assert hasattr(manager, 'order_manager')

    def test_get_evacuation_metrics(self):
        """Test getting evacuation metrics."""
        manager = EvacuationAIManager()
        metrics = manager.get_metrics()
        
        assert metrics is not None
        assert "total_routes" in metrics
        assert "active_routes" in metrics
        assert "total_orders" in metrics
        assert "active_orders" in metrics

    def test_coordinate_evacuation(self):
        """Test coordinating full evacuation."""
        manager = EvacuationAIManager()
        result = manager.coordinate_evacuation(
            zones=["zone-a", "zone-b"],
            crisis_type="hurricane",
            severity="critical",
        )
        
        assert result is not None

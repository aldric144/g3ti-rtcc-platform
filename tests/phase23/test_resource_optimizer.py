"""
Phase 23: ResourceOptimizer Tests
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.city_governance.resource_optimizer import (
    ResourceOptimizer,
    get_resource_optimizer,
    ResourceType,
    OptimizationObjective,
    OptimizationStatus,
    AlgorithmType,
    Resource,
    Zone,
    AllocationResult,
    OptimizationResult,
    MaintenanceTask,
    LinearOptimizer,
    MultiObjectiveOptimizer,
    RouteOptimizer,
    LoadBalancer,
    CostRewardScorer,
    MaintenanceScheduler,
)


class TestResourceOptimizer:
    """Tests for ResourceOptimizer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = ResourceOptimizer()

    def test_optimizer_initialization(self):
        """Test optimizer initializes with default resources and zones."""
        assert len(self.optimizer._resources) == 10
        assert len(self.optimizer._zones) == 6

    def test_get_singleton_instance(self):
        """Test singleton pattern returns same instance."""
        opt1 = get_resource_optimizer()
        opt2 = get_resource_optimizer()
        assert opt1 is opt2

    def test_get_resources(self):
        """Test getting all resources."""
        resources = self.optimizer.get_resources()
        assert len(resources) == 10
        assert all(isinstance(r, Resource) for r in resources)

    def test_get_zones(self):
        """Test getting all zones."""
        zones = self.optimizer.get_zones()
        assert len(zones) == 6
        assert all(isinstance(z, Zone) for z in zones)

    def test_run_linear_optimization(self):
        """Test running linear programming optimization."""
        result = self.optimizer.run_optimization(
            algorithm=AlgorithmType.LINEAR_PROGRAMMING,
            objectives=[OptimizationObjective.MAXIMIZE_COVERAGE],
        )

        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED
        assert len(result.allocations) >= 0
        assert result.execution_time_ms > 0

    def test_run_multi_objective_optimization(self):
        """Test running multi-objective optimization."""
        result = self.optimizer.run_optimization(
            algorithm=AlgorithmType.MULTI_OBJECTIVE,
            objectives=[
                OptimizationObjective.MAXIMIZE_COVERAGE,
                OptimizationObjective.MINIMIZE_RESPONSE_TIME,
            ],
        )

        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED

    def test_run_genetic_algorithm(self):
        """Test running genetic algorithm optimization."""
        result = self.optimizer.run_optimization(
            algorithm=AlgorithmType.GENETIC_ALGORITHM,
            objectives=[OptimizationObjective.BALANCE_WORKLOAD],
        )

        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED

    def test_optimize_patrol_coverage(self):
        """Test patrol coverage optimization."""
        result = self.optimizer.optimize_patrol_coverage()

        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED
        assert "average_coverage" in result.metrics_after

    def test_optimize_fire_ems_coverage(self):
        """Test fire/EMS coverage optimization."""
        result = self.optimizer.optimize_fire_ems_coverage()

        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED

    def test_optimize_traffic_flow(self):
        """Test traffic flow optimization."""
        result = self.optimizer.optimize_traffic_flow()

        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED

    def test_optimize_public_works(self):
        """Test public works optimization."""
        result = self.optimizer.optimize_public_works()

        assert result is not None
        assert result.status == OptimizationStatus.COMPLETED

    def test_optimize_vehicle_allocation(self):
        """Test vehicle allocation optimization."""
        result = self.optimizer.optimize_vehicle_allocation()

        assert result is not None
        assert "allocations" in result
        assert "fuel_efficiency" in result
        assert "total_cost" in result

    def test_get_route_optimization(self):
        """Test route optimization for a unit."""
        waypoints = [
            (26.7753, -80.0583),
            (26.7800, -80.0550),
            (26.7700, -80.0600),
        ]
        priorities = [1, 2, 1]

        result = self.optimizer.get_route_optimization(
            "unit-101",
            waypoints,
            priorities,
        )

        assert result is not None
        assert "optimized_route" in result
        assert "total_distance" in result

    def test_schedule_preventive_maintenance(self):
        """Test preventive maintenance scheduling."""
        tasks = [
            MaintenanceTask(
                task_id="task-001",
                asset_id="vehicle-001",
                asset_name="Patrol Car 101",
                task_type="oil_change",
                priority=2,
                estimated_duration_hours=2,
                required_skills=["mechanic"],
                required_equipment=["lift"],
                due_date=datetime.utcnow() + timedelta(days=7),
            ),
            MaintenanceTask(
                task_id="task-002",
                asset_id="vehicle-002",
                asset_name="Fire Engine 1",
                task_type="inspection",
                priority=3,
                estimated_duration_hours=4,
                required_skills=["fire_mechanic"],
                required_equipment=["diagnostic_tool"],
                due_date=datetime.utcnow() + timedelta(days=3),
            ),
        ]

        scheduled = self.optimizer.schedule_preventive_maintenance(tasks)
        assert len(scheduled) == 2
        assert scheduled[0].priority >= scheduled[1].priority or \
               scheduled[0].due_date <= scheduled[1].due_date

    def test_add_resource(self):
        """Test adding a new resource."""
        new_resource = Resource(
            resource_id="test-unit-999",
            resource_type=ResourceType.POLICE_UNIT,
            name="Test Unit 999",
            current_zone="downtown",
            status="available",
            capacity=1.0,
            utilization=0.0,
            cost_per_hour=50.0,
        )

        self.optimizer.add_resource(new_resource)
        assert "test-unit-999" in self.optimizer._resources

    def test_add_zone(self):
        """Test adding a new zone."""
        new_zone = Zone(
            zone_id="test-zone",
            name="Test Zone",
            demand_level=0.5,
            current_coverage=0.6,
            target_coverage=0.8,
            population=5000,
            area_sq_miles=2.0,
            priority_weight=1.0,
        )

        self.optimizer.add_zone(new_zone)
        assert "test-zone" in self.optimizer._zones

    def test_update_resource_zone(self):
        """Test updating resource zone assignment."""
        success = self.optimizer.update_resource_zone("unit-101", "marina")
        assert success

        resource = self.optimizer._resources.get("unit-101")
        assert resource.current_zone == "marina"

    def test_get_optimization_history(self):
        """Test getting optimization history."""
        self.optimizer.optimize_patrol_coverage()
        self.optimizer.optimize_fire_ems_coverage()

        history = self.optimizer.get_optimization_history(limit=5)
        assert len(history) >= 2

    def test_statistics(self):
        """Test statistics generation."""
        self.optimizer.optimize_patrol_coverage()

        stats = self.optimizer.get_statistics()
        assert "total_resources" in stats
        assert "total_zones" in stats
        assert "total_optimizations" in stats
        assert "resources_by_type" in stats

    def test_optimization_result_to_dict(self):
        """Test optimization result serialization."""
        result = self.optimizer.optimize_patrol_coverage()
        result_dict = result.to_dict()

        assert "optimization_id" in result_dict
        assert "algorithm" in result_dict
        assert "status" in result_dict
        assert "allocations" in result_dict
        assert "metrics_before" in result_dict
        assert "metrics_after" in result_dict

    def test_resource_to_dict(self):
        """Test resource serialization."""
        resources = self.optimizer.get_resources()
        resource_dict = resources[0].to_dict()

        assert "resource_id" in resource_dict
        assert "resource_type" in resource_dict
        assert "name" in resource_dict
        assert "current_zone" in resource_dict
        assert "status" in resource_dict

    def test_zone_to_dict(self):
        """Test zone serialization."""
        zones = self.optimizer.get_zones()
        zone_dict = zones[0].to_dict()

        assert "zone_id" in zone_dict
        assert "name" in zone_dict
        assert "demand_level" in zone_dict
        assert "current_coverage" in zone_dict
        assert "target_coverage" in zone_dict


class TestLinearOptimizer:
    """Tests for LinearOptimizer."""

    def test_optimize(self):
        """Test linear optimization."""
        optimizer = LinearOptimizer()
        resources = [
            Resource("r1", ResourceType.POLICE_UNIT, "Unit 1", "zone1", "available", 1.0, 0.5, 45),
            Resource("r2", ResourceType.POLICE_UNIT, "Unit 2", "zone2", "available", 1.0, 0.6, 45),
        ]
        zones = [
            Zone("zone1", "Zone 1", 0.8, 0.5, 0.9, 5000, 2.0, 1.0),
            Zone("zone2", "Zone 2", 0.6, 0.6, 0.85, 3000, 1.5, 0.8),
        ]

        allocations = optimizer.optimize(
            resources,
            zones,
            [OptimizationObjective.MAXIMIZE_COVERAGE],
        )

        assert isinstance(allocations, list)


class TestMultiObjectiveOptimizer:
    """Tests for MultiObjectiveOptimizer."""

    def test_optimize(self):
        """Test multi-objective optimization."""
        optimizer = MultiObjectiveOptimizer()
        resources = [
            Resource("r1", ResourceType.POLICE_UNIT, "Unit 1", "zone1", "available", 1.0, 0.5, 45),
        ]
        zones = [
            Zone("zone1", "Zone 1", 0.8, 0.5, 0.9, 5000, 2.0, 1.0),
        ]

        allocations = optimizer.optimize(
            resources,
            zones,
            [
                OptimizationObjective.MAXIMIZE_COVERAGE,
                OptimizationObjective.MINIMIZE_COST,
            ],
        )

        assert isinstance(allocations, list)


class TestRouteOptimizer:
    """Tests for RouteOptimizer."""

    def test_optimize_route(self):
        """Test route optimization."""
        optimizer = RouteOptimizer()
        waypoints = [
            (26.7753, -80.0583),
            (26.7800, -80.0550),
            (26.7700, -80.0600),
        ]
        priorities = [1, 2, 1]

        result = optimizer.optimize_route(waypoints, priorities)

        assert "optimized_route" in result
        assert "total_distance" in result
        assert len(result["optimized_route"]) == len(waypoints)


class TestLoadBalancer:
    """Tests for LoadBalancer."""

    def test_balance(self):
        """Test load balancing."""
        balancer = LoadBalancer()
        resources = [
            Resource("r1", ResourceType.POLICE_UNIT, "Unit 1", "zone1", "available", 1.0, 0.9, 45),
            Resource("r2", ResourceType.POLICE_UNIT, "Unit 2", "zone1", "available", 1.0, 0.3, 45),
        ]
        zones = [
            Zone("zone1", "Zone 1", 0.8, 0.5, 0.9, 5000, 2.0, 1.0),
            Zone("zone2", "Zone 2", 0.6, 0.3, 0.85, 3000, 1.5, 0.8),
        ]

        allocations = balancer.balance(resources, zones)
        assert isinstance(allocations, list)


class TestCostRewardScorer:
    """Tests for CostRewardScorer."""

    def test_score_allocation(self):
        """Test allocation scoring."""
        scorer = CostRewardScorer()
        allocation = AllocationResult(
            resource_id="r1",
            from_zone="zone1",
            to_zone="zone2",
            reason="Test",
            expected_impact={"coverage_improvement": 0.1},
        )
        resource = Resource("r1", ResourceType.POLICE_UNIT, "Unit 1", "zone1", "available", 1.0, 0.5, 45)
        zone = Zone("zone2", "Zone 2", 0.8, 0.5, 0.9, 5000, 2.0, 1.0)

        score = scorer.score_allocation(allocation, resource, zone)
        assert isinstance(score, float)


class TestMaintenanceScheduler:
    """Tests for MaintenanceScheduler."""

    def test_schedule(self):
        """Test maintenance scheduling."""
        scheduler = MaintenanceScheduler()
        tasks = [
            MaintenanceTask(
                task_id="t1",
                asset_id="a1",
                asset_name="Asset 1",
                task_type="inspection",
                priority=2,
                estimated_duration_hours=2,
                required_skills=[],
                required_equipment=[],
                due_date=datetime.utcnow() + timedelta(days=5),
            ),
            MaintenanceTask(
                task_id="t2",
                asset_id="a2",
                asset_name="Asset 2",
                task_type="repair",
                priority=3,
                estimated_duration_hours=4,
                required_skills=[],
                required_equipment=[],
                due_date=datetime.utcnow() + timedelta(days=2),
            ),
        ]

        scheduled = scheduler.schedule(tasks)
        assert len(scheduled) == 2

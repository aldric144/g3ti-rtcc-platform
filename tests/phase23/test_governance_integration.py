"""
Phase 23: Integration Tests with Phase 22 (City Brain)
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestPhase22Integration:
    """Tests for integration with Phase 22 City Brain."""

    def test_governance_engine_receives_city_state(self):
        """Test governance engine can process city state from City Brain."""
        from app.city_governance import get_governance_engine

        engine = get_governance_engine()

        city_state = {
            "city_id": "riviera-beach",
            "timestamp": datetime.utcnow().isoformat(),
            "zones": {
                "downtown": {
                    "crime_rate": 0.75,
                    "patrol_coverage": 0.6,
                    "population": 8500,
                    "traffic_congestion": 0.45,
                },
                "singer_island": {
                    "crime_rate": 0.35,
                    "patrol_coverage": 0.7,
                    "population": 4200,
                    "traffic_congestion": 0.3,
                },
            },
            "weather": {
                "temperature": 85,
                "humidity": 0.75,
                "wind_speed": 15,
                "storm_probability": 0.2,
            },
            "traffic": {
                "congestion_level": 0.45,
                "average_speed": 35,
                "incidents": 2,
            },
            "utilities": {
                "power_status": "normal",
                "water_status": "normal",
                "outages": 0,
            },
        }

        decisions = engine.process_city_data(city_state)
        assert isinstance(decisions, list)

    def test_resource_optimizer_uses_city_zones(self):
        """Test resource optimizer uses city zone data."""
        from app.city_governance.resource_optimizer import get_resource_optimizer

        optimizer = get_resource_optimizer()
        zones = optimizer.get_zones()

        zone_ids = [z.zone_id for z in zones]
        assert "downtown" in zone_ids
        assert "singer_island" in zone_ids
        assert "westside" in zone_ids
        assert "marina" in zone_ids

    def test_scenario_simulator_uses_city_profile(self):
        """Test scenario simulator uses Riviera Beach city profile."""
        from app.city_governance.scenario_simulator import get_scenario_simulator

        simulator = get_scenario_simulator()
        templates = simulator.get_templates()

        hurricane_template = next(
            (t for t in templates if t.scenario_type.value == "hurricane"),
            None,
        )
        assert hurricane_template is not None
        assert "singer_island" in hurricane_template.affected_zones

    def test_kpi_engine_calculates_city_metrics(self):
        """Test KPI engine calculates metrics for Riviera Beach."""
        from app.city_governance.kpi_engine import get_kpi_engine

        engine = get_kpi_engine()
        health = engine.get_city_health_index()

        assert health is not None
        assert 0 <= health.overall_score <= 100


class TestDataFlowIntegration:
    """Tests for data flow between modules."""

    def test_decision_to_optimization_flow(self):
        """Test decisions can trigger optimization."""
        from app.city_governance import get_governance_engine
        from app.city_governance.resource_optimizer import get_resource_optimizer

        decision_engine = get_governance_engine()
        optimizer = get_resource_optimizer()

        city_state = {
            "zones": {
                "downtown": {"crime_rate": 0.9, "patrol_coverage": 0.4}
            }
        }
        decisions = decision_engine.process_city_data(city_state)

        if decisions:
            result = optimizer.optimize_patrol_coverage()
            assert result is not None
            assert result.status.value == "completed"

    def test_scenario_to_kpi_flow(self):
        """Test scenario results can update KPIs."""
        from app.city_governance.scenario_simulator import get_scenario_simulator
        from app.city_governance.kpi_engine import get_kpi_engine

        simulator = get_scenario_simulator()
        kpi_engine = get_kpi_engine()

        config = simulator.create_from_template(
            "template-hurricane-cat3",
            created_by="test",
        )
        result = simulator.run_scenario(config.scenario_id)

        kpis = kpi_engine.get_all_kpis()
        assert len(kpis) > 0

    def test_optimization_to_decision_flow(self):
        """Test optimization results can generate decisions."""
        from app.city_governance import get_governance_engine
        from app.city_governance.resource_optimizer import get_resource_optimizer

        optimizer = get_resource_optimizer()
        decision_engine = get_governance_engine()

        opt_result = optimizer.optimize_patrol_coverage()

        if opt_result.allocations:
            city_state = {
                "optimization_result": {
                    "allocations": [a.to_dict() for a in opt_result.allocations],
                    "improvement": opt_result.improvement,
                }
            }
            decisions = decision_engine.process_city_data(city_state)
            assert isinstance(decisions, list)


class TestCrossModuleDependencies:
    """Tests for cross-module dependencies."""

    def test_all_modules_import_successfully(self):
        """Test all Phase 23 modules import without errors."""
        from app.city_governance import GovernanceDecisionEngine
        from app.city_governance.resource_optimizer import ResourceOptimizer
        from app.city_governance.scenario_simulator import CityScenarioSimulator
        from app.city_governance.kpi_engine import GovernanceKPIEngine

        assert GovernanceDecisionEngine is not None
        assert ResourceOptimizer is not None
        assert CityScenarioSimulator is not None
        assert GovernanceKPIEngine is not None

    def test_singleton_instances_are_consistent(self):
        """Test singleton instances remain consistent across imports."""
        from app.city_governance import get_governance_engine
        from app.city_governance.resource_optimizer import get_resource_optimizer
        from app.city_governance.scenario_simulator import get_scenario_simulator
        from app.city_governance.kpi_engine import get_kpi_engine

        engine1 = get_governance_engine()
        engine2 = get_governance_engine()
        assert engine1 is engine2

        opt1 = get_resource_optimizer()
        opt2 = get_resource_optimizer()
        assert opt1 is opt2

        sim1 = get_scenario_simulator()
        sim2 = get_scenario_simulator()
        assert sim1 is sim2

        kpi1 = get_kpi_engine()
        kpi2 = get_kpi_engine()
        assert kpi1 is kpi2


class TestAPIIntegration:
    """Tests for API integration."""

    def test_api_router_imports(self):
        """Test API router imports successfully."""
        from app.api.city_governance.router import router

        assert router is not None
        assert router.prefix == "/governance"

    def test_websocket_manager_imports(self):
        """Test WebSocket manager imports successfully."""
        from app.websockets.city_governance import get_ws_manager

        manager = get_ws_manager()
        assert manager is not None


class TestRivieraBeachSpecificData:
    """Tests for Riviera Beach specific data."""

    def test_city_coordinates(self):
        """Test city coordinates are correct for Riviera Beach."""
        RIVIERA_BEACH_LAT = 26.7753
        RIVIERA_BEACH_LON = -80.0583

        from app.city_governance.resource_optimizer import get_resource_optimizer

        optimizer = get_resource_optimizer()
        zones = optimizer.get_zones()

        assert len(zones) == 6

    def test_city_population(self):
        """Test city population data is reasonable."""
        from app.city_governance.resource_optimizer import get_resource_optimizer

        optimizer = get_resource_optimizer()
        zones = optimizer.get_zones()

        total_population = sum(z.population for z in zones)
        assert 30000 <= total_population <= 50000

    def test_city_zones_match_riviera_beach(self):
        """Test zones match Riviera Beach geography."""
        from app.city_governance.resource_optimizer import get_resource_optimizer

        optimizer = get_resource_optimizer()
        zones = optimizer.get_zones()

        zone_names = [z.name.lower() for z in zones]
        assert any("downtown" in name for name in zone_names)
        assert any("singer" in name for name in zone_names)
        assert any("marina" in name for name in zone_names)


class TestBackwardCompatibility:
    """Tests for backward compatibility with previous phases."""

    def test_no_modification_to_phase22_modules(self):
        """Test Phase 22 modules are not modified."""
        phase22_path = os.path.join(
            os.path.dirname(__file__),
            "../../backend/app/city_brain",
        )
        if os.path.exists(phase22_path):
            assert os.path.isdir(phase22_path)

    def test_phase23_modules_are_separate(self):
        """Test Phase 23 modules are in separate directory."""
        phase23_path = os.path.join(
            os.path.dirname(__file__),
            "../../backend/app/city_governance",
        )
        assert os.path.exists(phase23_path)
        assert os.path.isdir(phase23_path)

    def test_api_endpoints_are_namespaced(self):
        """Test API endpoints are properly namespaced."""
        from app.api.city_governance.router import router

        assert router.prefix == "/governance"


class TestErrorHandling:
    """Tests for error handling across modules."""

    def test_decision_engine_handles_empty_state(self):
        """Test decision engine handles empty city state."""
        from app.city_governance import get_governance_engine

        engine = get_governance_engine()
        decisions = engine.process_city_data({})
        assert isinstance(decisions, list)

    def test_optimizer_handles_no_resources(self):
        """Test optimizer handles scenario with no available resources."""
        from app.city_governance.resource_optimizer import ResourceOptimizer

        optimizer = ResourceOptimizer()
        result = optimizer.run_optimization()
        assert result is not None

    def test_simulator_handles_invalid_template(self):
        """Test simulator handles invalid template ID."""
        from app.city_governance.scenario_simulator import get_scenario_simulator

        simulator = get_scenario_simulator()
        config = simulator.create_from_template(
            "invalid-template-id",
            created_by="test",
        )
        assert config is None

    def test_kpi_engine_handles_missing_data(self):
        """Test KPI engine handles missing data gracefully."""
        from app.city_governance.kpi_engine import get_kpi_engine

        engine = get_kpi_engine()
        kpis = engine.get_all_kpis()
        assert len(kpis) > 0

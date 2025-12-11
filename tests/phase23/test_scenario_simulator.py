"""
Phase 23: CityScenarioSimulator Tests
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.city_governance.scenario_simulator import (
    CityScenarioSimulator,
    get_scenario_simulator,
    ScenarioType,
    ScenarioStatus,
    ImpactSeverity,
    OutcomeCategory,
    ScenarioVariable,
    TimelineEvent,
    OutcomePath,
    ImpactAssessment,
    ScenarioConfiguration,
    SimulationResult,
    SimulationEngine,
)


class TestCityScenarioSimulator:
    """Tests for CityScenarioSimulator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.simulator = CityScenarioSimulator()

    def test_simulator_initialization(self):
        """Test simulator initializes with default templates."""
        assert len(self.simulator._templates) == 4
        assert len(self.simulator._scenarios) == 0

    def test_get_singleton_instance(self):
        """Test singleton pattern returns same instance."""
        sim1 = get_scenario_simulator()
        sim2 = get_scenario_simulator()
        assert sim1 is sim2

    def test_get_templates(self):
        """Test getting scenario templates."""
        templates = self.simulator.get_templates()
        assert len(templates) == 4

        template_ids = [t.scenario_id for t in templates]
        assert "template-hurricane-cat3" in template_ids
        assert "template-major-event" in template_ids
        assert "template-power-outage" in template_ids
        assert "template-road-closure" in template_ids

    def test_create_scenario(self):
        """Test creating a new scenario."""
        variables = [
            {"name": "wind_speed", "min_value": 50, "max_value": 150, "default_value": 100, "unit": "mph"},
        ]

        config = self.simulator.create_scenario(
            scenario_type=ScenarioType.HURRICANE,
            name="Test Hurricane",
            description="Test hurricane scenario",
            variables=variables,
            duration_hours=48,
            affected_zones=["downtown", "singer_island"],
            created_by="test_user",
        )

        assert config is not None
        assert config.name == "Test Hurricane"
        assert config.scenario_type == ScenarioType.HURRICANE
        assert len(config.variables) == 1
        assert config.created_by == "test_user"

    def test_create_from_template(self):
        """Test creating scenario from template."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            variable_overrides={"wind_speed": 125},
            created_by="test_user",
        )

        assert config is not None
        assert config.scenario_type == ScenarioType.HURRICANE

    def test_create_from_invalid_template(self):
        """Test creating from non-existent template returns None."""
        config = self.simulator.create_from_template(
            template_id="invalid-template",
            created_by="test_user",
        )
        assert config is None

    def test_run_scenario(self):
        """Test running a scenario simulation."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)

        assert result is not None
        assert result.status == ScenarioStatus.COMPLETED
        assert len(result.outcome_paths) == 3
        assert len(result.impact_assessments) > 0
        assert 0 <= result.overall_risk_score <= 1

    def test_run_road_closure_scenario(self):
        """Test running road closure scenario."""
        config = self.simulator.create_from_template(
            template_id="template-road-closure",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)

        assert result is not None
        assert result.status == ScenarioStatus.COMPLETED

    def test_run_power_outage_scenario(self):
        """Test running power outage scenario."""
        config = self.simulator.create_from_template(
            template_id="template-power-outage",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)

        assert result is not None
        assert result.status == ScenarioStatus.COMPLETED

    def test_run_major_event_scenario(self):
        """Test running major event scenario."""
        config = self.simulator.create_from_template(
            template_id="template-major-event",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)

        assert result is not None
        assert result.status == ScenarioStatus.COMPLETED

    def test_outcome_paths(self):
        """Test outcome path generation."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)

        path_names = [p.name for p in result.outcome_paths]
        assert "Best Case" in path_names
        assert "Most Likely" in path_names
        assert "Worst Case" in path_names

        probabilities = [p.probability for p in result.outcome_paths]
        assert abs(sum(probabilities) - 1.0) < 0.01

    def test_timeline_events(self):
        """Test timeline event generation."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)

        for path in result.outcome_paths:
            assert len(path.timeline) > 0
            for event in path.timeline:
                assert event.event_id is not None
                assert event.timestamp is not None
                assert 0 <= event.impact_score <= 1

    def test_impact_assessments(self):
        """Test impact assessment generation."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)

        assert len(result.impact_assessments) > 0
        for assessment in result.impact_assessments:
            assert assessment.category in [c.value for c in OutcomeCategory]
            assert assessment.severity in [s.value for s in ImpactSeverity]
            assert assessment.recovery_time_hours >= 0

    def test_update_variable(self):
        """Test updating scenario variable."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        success = self.simulator.update_variable(
            config.scenario_id,
            "wind_speed",
            130,
        )
        assert success

        updated = self.simulator.get_scenario(config.scenario_id)
        wind_var = next(
            (v for v in updated.variables if v.name == "wind_speed"),
            None,
        )
        assert wind_var is not None
        assert wind_var.current_value == 130

    def test_update_invalid_variable(self):
        """Test updating non-existent variable."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        success = self.simulator.update_variable(
            config.scenario_id,
            "invalid_variable",
            100,
        )
        assert not success

    def test_delete_scenario(self):
        """Test deleting a scenario."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        success = self.simulator.delete_scenario(config.scenario_id)
        assert success

        deleted = self.simulator.get_scenario(config.scenario_id)
        assert deleted is None

    def test_get_scenarios(self):
        """Test getting all scenarios."""
        self.simulator.create_from_template("template-hurricane-cat3", created_by="user1")
        self.simulator.create_from_template("template-road-closure", created_by="user2")

        scenarios = self.simulator.get_scenarios()
        assert len(scenarios) >= 2

    def test_get_result(self):
        """Test getting simulation result."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)
        retrieved = self.simulator.get_result(result.result_id)

        assert retrieved is not None
        assert retrieved.result_id == result.result_id

    def test_statistics(self):
        """Test statistics generation."""
        self.simulator.create_from_template("template-hurricane-cat3", created_by="user")
        config = self.simulator.create_from_template("template-road-closure", created_by="user")
        self.simulator.run_scenario(config.scenario_id)

        stats = self.simulator.get_statistics()
        assert "total_scenarios" in stats
        assert "total_results" in stats
        assert "templates_count" in stats
        assert "scenarios_by_type" in stats

    def test_scenario_to_dict(self):
        """Test scenario serialization."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        config_dict = config.to_dict()
        assert "scenario_id" in config_dict
        assert "scenario_type" in config_dict
        assert "name" in config_dict
        assert "variables" in config_dict
        assert "affected_zones" in config_dict

    def test_result_to_dict(self):
        """Test result serialization."""
        config = self.simulator.create_from_template(
            template_id="template-hurricane-cat3",
            created_by="test_user",
        )

        result = self.simulator.run_scenario(config.scenario_id)
        result_dict = result.to_dict()

        assert "result_id" in result_dict
        assert "scenario_id" in result_dict
        assert "status" in result_dict
        assert "outcome_paths" in result_dict
        assert "impact_assessments" in result_dict
        assert "overall_risk_score" in result_dict


class TestScenarioTypes:
    """Tests for scenario type enumeration."""

    def test_all_types_defined(self):
        """Test all expected scenario types are defined."""
        expected_types = [
            "road_closure",
            "weather_event",
            "major_incident",
            "multi_day_operation",
            "infrastructure_outage",
            "crowd_surge",
            "crime_displacement",
            "hurricane",
            "flooding",
            "heatwave",
            "mass_casualty",
            "civil_unrest",
            "special_event",
        ]
        for scenario_type in expected_types:
            assert ScenarioType(scenario_type) is not None


class TestImpactSeverity:
    """Tests for impact severity enumeration."""

    def test_severity_levels(self):
        """Test severity levels are defined."""
        assert ImpactSeverity.MINIMAL.value == "minimal"
        assert ImpactSeverity.LOW.value == "low"
        assert ImpactSeverity.MODERATE.value == "moderate"
        assert ImpactSeverity.HIGH.value == "high"
        assert ImpactSeverity.SEVERE.value == "severe"
        assert ImpactSeverity.CATASTROPHIC.value == "catastrophic"


class TestOutcomeCategory:
    """Tests for outcome category enumeration."""

    def test_categories_defined(self):
        """Test outcome categories are defined."""
        expected_categories = [
            "traffic",
            "public_safety",
            "utilities",
            "emergency_services",
            "population",
            "economic",
            "infrastructure",
            "environmental",
        ]
        for category in expected_categories:
            assert OutcomeCategory(category) is not None


class TestSimulationEngine:
    """Tests for SimulationEngine."""

    def test_run_simulation(self):
        """Test simulation engine execution."""
        engine = SimulationEngine()
        config = ScenarioConfiguration(
            scenario_id="test-scenario",
            scenario_type=ScenarioType.ROAD_CLOSURE,
            name="Test Scenario",
            description="Test description",
            variables=[
                ScenarioVariable(
                    variable_id="v1",
                    name="duration",
                    description="Duration",
                    min_value=1,
                    max_value=24,
                    default_value=8,
                    current_value=8,
                    unit="hours",
                    category="timing",
                ),
            ],
            duration_hours=12,
            affected_zones=["downtown"],
            created_by="test",
        )

        result = engine.run(config)

        assert result is not None
        assert result.status == ScenarioStatus.COMPLETED
        assert len(result.outcome_paths) == 3

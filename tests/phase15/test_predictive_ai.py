"""Tests for Predictive Policing 3.0"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.predictive_ai.risk_terrain import (
    RiskTerrainModelingEngine,
    RiskZone,
    RiskFactor,
    RiskLevel,
)
from app.predictive_ai.violence_forecast import (
    ViolenceClusterForecasting,
    ViolenceCluster,
    ClusterStatus,
    ClusterPrediction,
)
from app.predictive_ai.patrol_optimizer import (
    PatrolRouteOptimizer,
    PatrolRoute,
    PatrolUnit,
    OptimizationMode,
)
from app.predictive_ai.behavior_prediction import (
    SuspectBehaviorPredictor,
    TrajectoryPrediction,
    MovementPattern,
)
from app.predictive_ai.bias_safeguards import (
    BiasSafeguards,
    BiasMetric,
    BiasAuditLog,
    ProtectedAttribute,
)


class TestRiskTerrainModelingEngine:
    """Test suite for RiskTerrainModelingEngine"""

    @pytest.fixture
    def rtm_engine(self):
        """Create a risk terrain modeling engine"""
        return RiskTerrainModelingEngine()

    @pytest.fixture
    def sample_zone(self):
        """Create a sample risk zone"""
        return RiskZone(
            zone_id="zone-001",
            name="Downtown Core",
            boundary_coords=[
                (33.748, -84.390),
                (33.750, -84.390),
                (33.750, -84.386),
                (33.748, -84.386),
            ],
            center_lat=33.749,
            center_lon=-84.388,
        )

    def test_register_zone(self, rtm_engine, sample_zone):
        """Test registering a risk zone"""
        result = rtm_engine.register_zone(sample_zone)
        assert result is True

    def test_calculate_risk_score(self, rtm_engine, sample_zone):
        """Test calculating risk score for a zone"""
        rtm_engine.register_zone(sample_zone)
        score = rtm_engine.calculate_risk_score(sample_zone.zone_id)
        assert score is not None
        assert 0 <= score <= 100

    def test_get_risk_factors(self, rtm_engine, sample_zone):
        """Test getting risk factors for a zone"""
        rtm_engine.register_zone(sample_zone)
        factors = rtm_engine.get_risk_factors(sample_zone.zone_id)
        assert isinstance(factors, list)

    def test_get_high_risk_zones(self, rtm_engine, sample_zone):
        """Test getting high risk zones"""
        rtm_engine.register_zone(sample_zone)
        high_risk = rtm_engine.get_high_risk_zones(threshold=50)
        assert isinstance(high_risk, list)


class TestViolenceClusterForecasting:
    """Test suite for ViolenceClusterForecasting"""

    @pytest.fixture
    def forecast_engine(self):
        """Create a violence cluster forecasting engine"""
        return ViolenceClusterForecasting()

    @pytest.fixture
    def sample_cluster(self):
        """Create a sample violence cluster"""
        return ViolenceCluster(
            cluster_id="cluster-001",
            name="Downtown Violence Cluster",
            center_lat=33.749,
            center_lon=-84.388,
            radius_m=500,
            incident_count=15,
            status=ClusterStatus.ACTIVE,
        )

    def test_register_cluster(self, forecast_engine, sample_cluster):
        """Test registering a violence cluster"""
        result = forecast_engine.register_cluster(sample_cluster)
        assert result is True

    def test_generate_prediction(self, forecast_engine, sample_cluster):
        """Test generating a cluster prediction"""
        forecast_engine.register_cluster(sample_cluster)
        prediction = forecast_engine.generate_prediction(
            sample_cluster.cluster_id,
            days_ahead=7,
        )
        assert prediction is not None
        assert prediction.cluster_id == sample_cluster.cluster_id

    def test_get_active_clusters(self, forecast_engine, sample_cluster):
        """Test getting active clusters"""
        forecast_engine.register_cluster(sample_cluster)
        active = forecast_engine.get_active_clusters()
        assert len(active) >= 1

    def test_update_cluster_status(self, forecast_engine, sample_cluster):
        """Test updating cluster status"""
        forecast_engine.register_cluster(sample_cluster)
        result = forecast_engine.update_cluster_status(
            sample_cluster.cluster_id,
            ClusterStatus.DECLINING,
        )
        assert result is True


class TestPatrolRouteOptimizer:
    """Test suite for PatrolRouteOptimizer"""

    @pytest.fixture
    def optimizer(self):
        """Create a patrol route optimizer"""
        return PatrolRouteOptimizer()

    @pytest.fixture
    def sample_unit(self):
        """Create a sample patrol unit"""
        return PatrolUnit(
            unit_id="unit-12",
            call_sign="Alpha-12",
            current_lat=33.749,
            current_lon=-84.388,
            status="AVAILABLE",
        )

    def test_register_unit(self, optimizer, sample_unit):
        """Test registering a patrol unit"""
        result = optimizer.register_unit(sample_unit)
        assert result is True

    def test_optimize_routes(self, optimizer, sample_unit):
        """Test optimizing patrol routes"""
        optimizer.register_unit(sample_unit)
        routes = optimizer.optimize_routes(mode=OptimizationMode.BALANCED)
        assert isinstance(routes, list)

    def test_get_route_for_unit(self, optimizer, sample_unit):
        """Test getting route for a specific unit"""
        optimizer.register_unit(sample_unit)
        optimizer.optimize_routes(mode=OptimizationMode.BALANCED)
        route = optimizer.get_route_for_unit(sample_unit.unit_id)
        assert route is None or isinstance(route, PatrolRoute)

    def test_optimization_modes(self):
        """Test that all optimization modes exist"""
        assert hasattr(OptimizationMode, "COVERAGE")
        assert hasattr(OptimizationMode, "RESPONSE")
        assert hasattr(OptimizationMode, "BALANCED")
        assert hasattr(OptimizationMode, "HOTSPOT")


class TestSuspectBehaviorPredictor:
    """Test suite for SuspectBehaviorPredictor"""

    @pytest.fixture
    def predictor(self):
        """Create a suspect behavior predictor"""
        return SuspectBehaviorPredictor()

    def test_predict_trajectory(self, predictor):
        """Test predicting suspect trajectory"""
        prediction = predictor.predict_trajectory(
            last_known_lat=33.749,
            last_known_lon=-84.388,
            heading_deg=45,
            speed_mps=5,
            hours_ahead=1,
        )
        assert prediction is not None
        assert isinstance(prediction, TrajectoryPrediction)

    def test_no_demographic_factors(self, predictor):
        """Test that no demographic factors are used"""
        excluded_factors = predictor.get_excluded_factors()
        assert "race" in [f.lower() for f in excluded_factors]
        assert "ethnicity" in [f.lower() for f in excluded_factors]
        assert "gender" in [f.lower() for f in excluded_factors]


class TestBiasSafeguards:
    """Test suite for BiasSafeguards"""

    @pytest.fixture
    def safeguards(self):
        """Create bias safeguards"""
        return BiasSafeguards()

    def test_get_protected_attributes(self, safeguards):
        """Test getting protected attributes"""
        attributes = safeguards.get_protected_attributes()
        assert len(attributes) > 0
        
        attribute_names = [a.attribute.lower() for a in attributes]
        assert "race" in attribute_names or "race/ethnicity" in attribute_names
        assert "religion" in attribute_names
        assert "gender" in attribute_names

    def test_check_bias_metrics(self, safeguards):
        """Test checking bias metrics"""
        metrics = safeguards.check_bias_metrics()
        assert isinstance(metrics, list)
        assert len(metrics) > 0

    def test_demographic_parity_metric(self, safeguards):
        """Test demographic parity metric exists"""
        metrics = safeguards.check_bias_metrics()
        metric_names = [m.name.lower() for m in metrics]
        assert "demographic parity" in metric_names or "demographicparity" in metric_names

    def test_get_audit_log(self, safeguards):
        """Test getting audit log"""
        logs = safeguards.get_audit_log()
        assert isinstance(logs, list)

    def test_run_bias_check(self, safeguards):
        """Test running a bias check"""
        result = safeguards.run_bias_check(model_name="TestModel")
        assert result is not None
        assert result.passed is True or result.passed is False

    def test_all_models_have_safeguards(self, safeguards):
        """Test that all predictive models have bias safeguards"""
        models = ["RiskTerrainModel", "ViolenceClusterModel", "PatrolOptimizer", "BehaviorPredictor"]
        for model in models:
            result = safeguards.run_bias_check(model_name=model)
            assert result is not None

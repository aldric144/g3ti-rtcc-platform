"""
Tests for Insider Threat Engine

Tests cover:
- Employee risk profiling
- Behavior deviation detection
- Access anomaly detection
- Threat assessments
- High-risk employee identification
- Metrics collection
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.national_security.insider_threat import (
    InsiderThreatEngine,
    EmployeeRiskProfile,
    BehaviorDeviation,
    AccessAnomaly,
    ThreatAssessment,
    RiskLevel,
    BehaviorType,
    AnomalyType,
    DepartmentType,
    ClearanceLevel,
)


class TestInsiderThreatEngine:
    """Test suite for InsiderThreatEngine."""

    @pytest.fixture
    def engine(self):
        """Create an InsiderThreatEngine instance."""
        return InsiderThreatEngine()

    def test_engine_initialization(self, engine):
        """Test engine initializes with empty collections."""
        assert engine.risk_profiles == {}
        assert engine.behavior_deviations == {}
        assert engine.access_anomalies == {}
        assert engine.threat_assessments == {}
        assert engine.behavior_baselines == {}

    def test_create_risk_profile(self, engine):
        """Test employee risk profile creation."""
        profile = engine.create_risk_profile(
            employee_id="EMP001",
            employee_name="John Doe",
            department=DepartmentType.IT,
            role="System Administrator",
            clearance_level=ClearanceLevel.SECRET,
            is_privileged=True,
            risk_factors=["privileged_access", "recent_performance_issues"],
        )

        assert profile is not None
        assert profile.profile_id is not None
        assert profile.employee_id == "EMP001"
        assert profile.employee_name == "John Doe"
        assert profile.department == DepartmentType.IT
        assert profile.clearance_level == ClearanceLevel.SECRET
        assert profile.is_privileged is True
        assert profile.risk_score > 0

    def test_get_risk_profile(self, engine):
        """Test retrieving a specific risk profile."""
        engine.create_risk_profile(
            employee_id="EMP002",
            employee_name="Jane Smith",
            department=DepartmentType.FINANCE,
            role="Financial Analyst",
            clearance_level=ClearanceLevel.CONFIDENTIAL,
            is_privileged=False,
            risk_factors=[],
        )

        profile = engine.get_risk_profile("EMP002")
        assert profile is not None
        assert profile.employee_name == "Jane Smith"

        non_existent = engine.get_risk_profile("EMP999")
        assert non_existent is None

    def test_get_risk_profiles_filtering(self, engine):
        """Test risk profile retrieval with filtering."""
        engine.create_risk_profile(
            employee_id="EMP003",
            employee_name="High Risk Employee",
            department=DepartmentType.IT,
            role="Developer",
            clearance_level=ClearanceLevel.TOP_SECRET,
            is_privileged=True,
            risk_factors=["privileged_access", "foreign_contacts", "financial_stress"],
        )

        engine.create_risk_profile(
            employee_id="EMP004",
            employee_name="Low Risk Employee",
            department=DepartmentType.HR,
            role="HR Specialist",
            clearance_level=ClearanceLevel.UNCLASSIFIED,
            is_privileged=False,
            risk_factors=[],
        )

        it_profiles = engine.get_risk_profiles(department=DepartmentType.IT)
        assert len(it_profiles) >= 1

        privileged_profiles = engine.get_risk_profiles(privileged_only=True)
        assert all(p.is_privileged for p in privileged_profiles)

    def test_set_behavior_baseline(self, engine):
        """Test setting behavior baseline for an employee."""
        engine.create_risk_profile(
            employee_id="EMP005",
            employee_name="Baseline Test",
            department=DepartmentType.OPERATIONS,
            role="Operator",
            clearance_level=ClearanceLevel.CONFIDENTIAL,
            is_privileged=False,
            risk_factors=[],
        )

        baseline = engine.set_behavior_baseline(
            employee_id="EMP005",
            login_times={"avg_start": "08:00", "avg_end": "17:00"},
            access_patterns={"typical_systems": ["system1", "system2"]},
            data_access_volume={"daily_avg_mb": 50},
            communication_patterns={"internal_emails_per_day": 20},
        )

        assert baseline is not None
        assert baseline["employee_id"] == "EMP005"
        assert "login_times" in baseline

    def test_detect_behavior_deviation(self, engine):
        """Test behavior deviation detection."""
        engine.create_risk_profile(
            employee_id="EMP006",
            employee_name="Deviation Test",
            department=DepartmentType.IT,
            role="Engineer",
            clearance_level=ClearanceLevel.SECRET,
            is_privileged=True,
            risk_factors=[],
        )

        deviation = engine.detect_behavior_deviation(
            employee_id="EMP006",
            behavior_type=BehaviorType.UNUSUAL_ACCESS_TIME,
            description="Employee accessed systems at 3 AM, outside normal hours",
            observed_value="03:00 AM access",
            baseline_value="08:00 AM - 06:00 PM normal hours",
            deviation_magnitude=0.8,
        )

        assert deviation is not None
        assert deviation.deviation_id is not None
        assert deviation.employee_id == "EMP006"
        assert deviation.behavior_type == BehaviorType.UNUSUAL_ACCESS_TIME
        assert deviation.deviation_score > 0

    def test_get_behavior_deviations_filtering(self, engine):
        """Test behavior deviation retrieval with filtering."""
        engine.create_risk_profile(
            employee_id="EMP007",
            employee_name="Filter Test",
            department=DepartmentType.IT,
            role="Admin",
            clearance_level=ClearanceLevel.SECRET,
            is_privileged=True,
            risk_factors=[],
        )

        engine.detect_behavior_deviation(
            employee_id="EMP007",
            behavior_type=BehaviorType.DATA_EXFILTRATION,
            description="Large data transfer detected",
            observed_value="500 MB transferred",
            baseline_value="50 MB daily average",
            deviation_magnitude=0.9,
        )

        deviations = engine.get_behavior_deviations(
            behavior_type=BehaviorType.DATA_EXFILTRATION
        )
        assert len(deviations) >= 1

        unacknowledged = engine.get_behavior_deviations(unacknowledged_only=True)
        assert all(not d.is_acknowledged for d in unacknowledged)

    def test_detect_access_anomaly(self, engine):
        """Test access anomaly detection."""
        engine.create_risk_profile(
            employee_id="EMP008",
            employee_name="Anomaly Test",
            department=DepartmentType.FINANCE,
            role="Accountant",
            clearance_level=ClearanceLevel.CONFIDENTIAL,
            is_privileged=False,
            risk_factors=[],
        )

        anomaly = engine.detect_access_anomaly(
            employee_id="EMP008",
            anomaly_type=AnomalyType.UNAUTHORIZED_ACCESS,
            description="Attempted access to restricted financial records",
            resource_accessed="/secure/financial/executive_compensation",
            access_method="direct_query",
            source_ip="192.168.1.100",
            was_successful=False,
        )

        assert anomaly is not None
        assert anomaly.anomaly_id is not None
        assert anomaly.employee_id == "EMP008"
        assert anomaly.anomaly_type == AnomalyType.UNAUTHORIZED_ACCESS
        assert anomaly.risk_score > 0

    def test_get_access_anomalies_filtering(self, engine):
        """Test access anomaly retrieval with filtering."""
        engine.create_risk_profile(
            employee_id="EMP009",
            employee_name="Anomaly Filter Test",
            department=DepartmentType.IT,
            role="Developer",
            clearance_level=ClearanceLevel.SECRET,
            is_privileged=True,
            risk_factors=[],
        )

        engine.detect_access_anomaly(
            employee_id="EMP009",
            anomaly_type=AnomalyType.PRIVILEGE_ESCALATION,
            description="Attempted privilege escalation",
            resource_accessed="/admin/users",
            access_method="api_call",
            source_ip="10.0.0.50",
            was_successful=False,
        )

        anomalies = engine.get_access_anomalies(
            anomaly_type=AnomalyType.PRIVILEGE_ESCALATION
        )
        assert len(anomalies) >= 1

    def test_create_threat_assessment(self, engine):
        """Test comprehensive threat assessment creation."""
        engine.create_risk_profile(
            employee_id="EMP010",
            employee_name="Assessment Test",
            department=DepartmentType.IT,
            role="Senior Engineer",
            clearance_level=ClearanceLevel.TOP_SECRET,
            is_privileged=True,
            risk_factors=["privileged_access", "recent_travel"],
        )

        assessment = engine.create_threat_assessment(
            employee_id="EMP010",
            assessment_reason="Routine periodic review",
            include_behavior_analysis=True,
            include_access_analysis=True,
        )

        assert assessment is not None
        assert assessment.assessment_id is not None
        assert assessment.employee_id == "EMP010"
        assert assessment.overall_risk_score >= 0

    def test_acknowledge_deviation(self, engine):
        """Test acknowledging a behavior deviation."""
        engine.create_risk_profile(
            employee_id="EMP011",
            employee_name="Ack Test",
            department=DepartmentType.OPERATIONS,
            role="Operator",
            clearance_level=ClearanceLevel.CONFIDENTIAL,
            is_privileged=False,
            risk_factors=[],
        )

        deviation = engine.detect_behavior_deviation(
            employee_id="EMP011",
            behavior_type=BehaviorType.UNUSUAL_ACCESS_TIME,
            description="Late night access",
            observed_value="11 PM",
            baseline_value="9 AM - 5 PM",
            deviation_magnitude=0.5,
        )

        result = engine.acknowledge_deviation(
            deviation_id=deviation.deviation_id,
            acknowledged_by="security_analyst",
            notes="Verified as authorized overtime work",
        )

        assert result is True

        updated = engine.behavior_deviations[deviation.deviation_id]
        assert updated.is_acknowledged is True

    def test_update_anomaly_status(self, engine):
        """Test updating access anomaly investigation status."""
        engine.create_risk_profile(
            employee_id="EMP012",
            employee_name="Status Test",
            department=DepartmentType.IT,
            role="Admin",
            clearance_level=ClearanceLevel.SECRET,
            is_privileged=True,
            risk_factors=[],
        )

        anomaly = engine.detect_access_anomaly(
            employee_id="EMP012",
            anomaly_type=AnomalyType.UNUSUAL_QUERY,
            description="Unusual database query pattern",
            resource_accessed="/database/customers",
            access_method="sql_query",
            source_ip="192.168.1.50",
            was_successful=True,
        )

        result = engine.update_anomaly_status(
            anomaly_id=anomaly.anomaly_id,
            new_status="investigating",
            updated_by="security_team",
            notes="Assigned to analyst for review",
        )

        assert result is True

        updated = engine.access_anomalies[anomaly.anomaly_id]
        assert updated.investigation_status == "investigating"

    def test_get_high_risk_employees(self, engine):
        """Test retrieving high-risk employees."""
        engine.create_risk_profile(
            employee_id="EMP013",
            employee_name="High Risk 1",
            department=DepartmentType.IT,
            role="Admin",
            clearance_level=ClearanceLevel.TOP_SECRET,
            is_privileged=True,
            risk_factors=["privileged_access", "foreign_contacts", "financial_stress", "performance_issues"],
        )

        engine.create_risk_profile(
            employee_id="EMP014",
            employee_name="Low Risk 1",
            department=DepartmentType.HR,
            role="Clerk",
            clearance_level=ClearanceLevel.UNCLASSIFIED,
            is_privileged=False,
            risk_factors=[],
        )

        high_risk = engine.get_high_risk_employees(threshold=50.0)
        assert len(high_risk) >= 1

    def test_get_metrics(self, engine):
        """Test metrics collection."""
        engine.create_risk_profile(
            employee_id="EMP015",
            employee_name="Metrics Test",
            department=DepartmentType.IT,
            role="Engineer",
            clearance_level=ClearanceLevel.SECRET,
            is_privileged=True,
            risk_factors=["privileged_access"],
        )

        metrics = engine.get_metrics()

        assert "total_profiles" in metrics
        assert "high_risk_count" in metrics
        assert "total_deviations" in metrics
        assert "unacknowledged_deviations" in metrics
        assert "total_anomalies" in metrics
        assert "open_anomalies" in metrics
        assert "total_assessments" in metrics


class TestEmployeeRiskProfileDataclass:
    """Test EmployeeRiskProfile dataclass."""

    def test_risk_profile_creation(self):
        """Test EmployeeRiskProfile dataclass creation."""
        profile = EmployeeRiskProfile(
            profile_id="profile-123",
            employee_id="EMP100",
            employee_name="Test Employee",
            department=DepartmentType.IT,
            role="Developer",
            clearance_level=ClearanceLevel.SECRET,
            hire_date="2020-01-15",
            risk_level=RiskLevel.ELEVATED,
            risk_score=65.0,
            risk_factors=["privileged_access", "recent_travel"],
            is_privileged=True,
            access_patterns={},
            last_assessment="2025-12-10T00:00:00Z",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-12-10T00:00:00Z",
            metadata={},
        )

        assert profile.profile_id == "profile-123"
        assert profile.risk_level == RiskLevel.ELEVATED
        assert profile.risk_score == 65.0


class TestBehaviorDeviationDataclass:
    """Test BehaviorDeviation dataclass."""

    def test_behavior_deviation_creation(self):
        """Test BehaviorDeviation dataclass creation."""
        deviation = BehaviorDeviation(
            deviation_id="dev-123",
            employee_id="EMP100",
            behavior_type=BehaviorType.DATA_EXFILTRATION,
            description="Large data transfer detected",
            observed_value="500 MB",
            baseline_value="50 MB",
            deviation_magnitude=0.9,
            deviation_score=85.0,
            severity="high",
            detected_at="2025-12-10T00:00:00Z",
            is_acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None,
            notes="",
            metadata={},
        )

        assert deviation.deviation_id == "dev-123"
        assert deviation.behavior_type == BehaviorType.DATA_EXFILTRATION
        assert deviation.deviation_score == 85.0


class TestAccessAnomalyDataclass:
    """Test AccessAnomaly dataclass."""

    def test_access_anomaly_creation(self):
        """Test AccessAnomaly dataclass creation."""
        anomaly = AccessAnomaly(
            anomaly_id="anom-123",
            employee_id="EMP100",
            anomaly_type=AnomalyType.UNAUTHORIZED_ACCESS,
            description="Attempted access to restricted area",
            resource_accessed="/secure/classified",
            access_method="direct",
            source_ip="192.168.1.100",
            was_successful=False,
            risk_score=75.0,
            severity="high",
            detected_at="2025-12-10T00:00:00Z",
            investigation_status="open",
            assigned_to=None,
            resolution=None,
            metadata={},
        )

        assert anomaly.anomaly_id == "anom-123"
        assert anomaly.anomaly_type == AnomalyType.UNAUTHORIZED_ACCESS
        assert anomaly.risk_score == 75.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

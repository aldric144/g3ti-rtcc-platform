"""
Tests for Repeat Offender Analytics module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.analytics.offender_analytics import (
    RepeatOffenderAnalytics,
    OffenderProfile,
    RecidivismAnalysis,
    OffenderTimeline,
    NetworkAnalysis,
)


class TestOffenderProfile:
    """Tests for OffenderProfile model."""

    def test_create_profile(self):
        """Test creating an offender profile."""
        profile = OffenderProfile(
            offender_id="OFF-001",
            jurisdiction="ATL",
            total_incidents=5,
            first_incident_date=datetime(2020, 1, 15),
            last_incident_date=datetime(2024, 6, 20),
            risk_score=75.5,
            risk_level="high",
        )

        assert profile.offender_id == "OFF-001"
        assert profile.total_incidents == 5
        assert profile.risk_score == 75.5
        assert profile.risk_level == "high"

    def test_profile_with_crime_breakdown(self):
        """Test profile with crime category breakdown."""
        profile = OffenderProfile(
            offender_id="OFF-002",
            jurisdiction="ATL",
            total_incidents=10,
            risk_score=85.0,
            risk_level="high",
            crime_categories={"property": 5, "violent": 3, "drug": 2},
            severity_breakdown={"high": 3, "medium": 5, "low": 2},
        )

        assert profile.crime_categories["property"] == 5
        assert profile.severity_breakdown["high"] == 3

    def test_profile_with_escalation(self):
        """Test profile with escalation pattern."""
        profile = OffenderProfile(
            offender_id="OFF-003",
            jurisdiction="ATL",
            total_incidents=8,
            risk_score=90.0,
            risk_level="critical",
            escalation_pattern="increasing_severity",
            days_between_incidents=45,
        )

        assert profile.escalation_pattern == "increasing_severity"
        assert profile.days_between_incidents == 45


class TestRecidivismAnalysis:
    """Tests for RecidivismAnalysis model."""

    def test_create_analysis(self):
        """Test creating recidivism analysis."""
        analysis = RecidivismAnalysis(
            jurisdiction="ATL",
            time_period_days=365,
            total_offenders=1000,
            repeat_offenders=250,
            recidivism_rate=0.25,
        )

        assert analysis.recidivism_rate == 0.25
        assert analysis.repeat_offenders == 250

    def test_analysis_with_breakdown(self):
        """Test analysis with category breakdown."""
        analysis = RecidivismAnalysis(
            jurisdiction="ATL",
            time_period_days=365,
            total_offenders=1000,
            repeat_offenders=250,
            recidivism_rate=0.25,
            by_crime_category={
                "property": {"total": 400, "repeat": 120, "rate": 0.30},
                "violent": {"total": 200, "repeat": 40, "rate": 0.20},
                "drug": {"total": 400, "repeat": 90, "rate": 0.225},
            },
        )

        assert analysis.by_crime_category["property"]["rate"] == 0.30

    def test_analysis_with_risk_distribution(self):
        """Test analysis with risk distribution."""
        analysis = RecidivismAnalysis(
            jurisdiction="ATL",
            time_period_days=365,
            total_offenders=1000,
            repeat_offenders=250,
            recidivism_rate=0.25,
            risk_distribution={
                "low": 500,
                "medium": 300,
                "high": 150,
                "critical": 50,
            },
        )

        assert analysis.risk_distribution["critical"] == 50


class TestOffenderTimeline:
    """Tests for OffenderTimeline model."""

    def test_create_timeline(self):
        """Test creating offender timeline."""
        timeline = OffenderTimeline(
            offender_id="OFF-001",
            incidents=[
                {
                    "date": datetime(2020, 1, 15),
                    "crime_type": "theft",
                    "severity": "low",
                },
                {
                    "date": datetime(2021, 3, 20),
                    "crime_type": "burglary",
                    "severity": "medium",
                },
                {
                    "date": datetime(2022, 6, 10),
                    "crime_type": "robbery",
                    "severity": "high",
                },
            ],
            total_span_days=875,
            average_interval_days=292,
        )

        assert len(timeline.incidents) == 3
        assert timeline.total_span_days == 875

    def test_timeline_with_escalation(self):
        """Test timeline with escalation detection."""
        timeline = OffenderTimeline(
            offender_id="OFF-002",
            incidents=[
                {"date": datetime(2020, 1, 1), "severity": "low"},
                {"date": datetime(2021, 1, 1), "severity": "medium"},
                {"date": datetime(2022, 1, 1), "severity": "high"},
            ],
            total_span_days=730,
            average_interval_days=365,
            escalation_detected=True,
            escalation_type="severity",
        )

        assert timeline.escalation_detected is True
        assert timeline.escalation_type == "severity"


class TestNetworkAnalysis:
    """Tests for NetworkAnalysis model."""

    def test_create_network(self):
        """Test creating network analysis."""
        network = NetworkAnalysis(
            offender_id="OFF-001",
            associates=[
                {"offender_id": "OFF-002", "shared_incidents": 3, "relationship": "co-offender"},
                {"offender_id": "OFF-003", "shared_incidents": 2, "relationship": "co-offender"},
            ],
            network_size=2,
            network_risk_score=65.0,
        )

        assert network.network_size == 2
        assert len(network.associates) == 2

    def test_network_with_clusters(self):
        """Test network with cluster information."""
        network = NetworkAnalysis(
            offender_id="OFF-001",
            associates=[],
            network_size=5,
            network_risk_score=75.0,
            cluster_id="CLUSTER-001",
            cluster_size=8,
            cluster_crime_focus="property",
        )

        assert network.cluster_id == "CLUSTER-001"
        assert network.cluster_crime_focus == "property"


class TestRepeatOffenderAnalytics:
    """Tests for RepeatOffenderAnalytics class."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = RepeatOffenderAnalytics()

        assert engine is not None

    @pytest.mark.asyncio
    async def test_get_offender_profile(self):
        """Test getting offender profile."""
        engine = RepeatOffenderAnalytics()

        # Mock the data source
        engine._fetch_offender_data = AsyncMock(return_value={
            "offender_id": "OFF-001",
            "incidents": [
                {"date": datetime(2020, 1, 15), "crime_type": "theft"},
                {"date": datetime(2021, 3, 20), "crime_type": "burglary"},
                {"date": datetime(2022, 6, 10), "crime_type": "robbery"},
            ],
        })

        result = await engine.get_offender_profile("OFF-001", "ATL")

        assert result.offender_id == "OFF-001"
        assert result.total_incidents == 3

    @pytest.mark.asyncio
    async def test_analyze_recidivism(self):
        """Test recidivism analysis."""
        engine = RepeatOffenderAnalytics()

        # Mock the data source
        engine._fetch_offender_stats = AsyncMock(return_value={
            "total_offenders": 1000,
            "repeat_offenders": 250,
            "by_category": {
                "property": {"total": 400, "repeat": 120},
                "violent": {"total": 200, "repeat": 40},
            },
        })

        result = await engine.analyze_recidivism(
            jurisdiction="ATL",
            time_period_days=365,
        )

        assert result.total_offenders == 1000
        assert result.repeat_offenders == 250
        assert result.recidivism_rate == 0.25

    @pytest.mark.asyncio
    async def test_get_high_risk_offenders(self):
        """Test getting high-risk offenders."""
        engine = RepeatOffenderAnalytics()

        # Mock the data source
        engine._fetch_high_risk_offenders = AsyncMock(return_value=[
            {"offender_id": "OFF-001", "risk_score": 95.0},
            {"offender_id": "OFF-002", "risk_score": 88.0},
            {"offender_id": "OFF-003", "risk_score": 82.0},
        ])

        result = await engine.get_high_risk_offenders(
            jurisdiction="ATL",
            min_risk_score=80.0,
            limit=10,
        )

        assert len(result) == 3
        assert all(o["risk_score"] >= 80.0 for o in result)

    @pytest.mark.asyncio
    async def test_get_offender_timeline(self):
        """Test getting offender timeline."""
        engine = RepeatOffenderAnalytics()

        # Mock the data source
        engine._fetch_offender_incidents = AsyncMock(return_value=[
            {"date": datetime(2020, 1, 15), "crime_type": "theft", "severity": "low"},
            {"date": datetime(2021, 3, 20), "crime_type": "burglary", "severity": "medium"},
            {"date": datetime(2022, 6, 10), "crime_type": "robbery", "severity": "high"},
        ])

        result = await engine.get_offender_timeline("OFF-001")

        assert result.offender_id == "OFF-001"
        assert len(result.incidents) == 3

    @pytest.mark.asyncio
    async def test_get_offender_network(self):
        """Test getting offender network."""
        engine = RepeatOffenderAnalytics()

        # Mock the data source
        engine._fetch_offender_network = AsyncMock(return_value={
            "associates": [
                {"offender_id": "OFF-002", "shared_incidents": 3},
                {"offender_id": "OFF-003", "shared_incidents": 2},
            ],
        })

        result = await engine.get_offender_network("OFF-001")

        assert result.offender_id == "OFF-001"
        assert result.network_size == 2

    def test_calculate_risk_score(self):
        """Test risk score calculation."""
        engine = RepeatOffenderAnalytics()

        # High risk factors
        score = engine._calculate_risk_score(
            total_incidents=10,
            violent_incidents=5,
            days_since_last=30,
            escalation_detected=True,
        )
        assert score > 70

        # Low risk factors
        score = engine._calculate_risk_score(
            total_incidents=2,
            violent_incidents=0,
            days_since_last=365,
            escalation_detected=False,
        )
        assert score < 40

    def test_classify_risk_level(self):
        """Test risk level classification."""
        engine = RepeatOffenderAnalytics()

        assert engine._classify_risk_level(95) == "critical"
        assert engine._classify_risk_level(75) == "high"
        assert engine._classify_risk_level(50) == "medium"
        assert engine._classify_risk_level(25) == "low"

    def test_detect_escalation(self):
        """Test escalation pattern detection."""
        engine = RepeatOffenderAnalytics()

        # Severity escalation
        incidents = [
            {"severity": "low", "date": datetime(2020, 1, 1)},
            {"severity": "medium", "date": datetime(2021, 1, 1)},
            {"severity": "high", "date": datetime(2022, 1, 1)},
        ]
        escalation = engine._detect_escalation(incidents)
        assert escalation["detected"] is True
        assert escalation["type"] == "severity"

        # Frequency escalation
        incidents = [
            {"severity": "medium", "date": datetime(2020, 1, 1)},
            {"severity": "medium", "date": datetime(2020, 6, 1)},
            {"severity": "medium", "date": datetime(2020, 9, 1)},
            {"severity": "medium", "date": datetime(2020, 11, 1)},
        ]
        escalation = engine._detect_escalation(incidents)
        assert escalation["detected"] is True
        assert escalation["type"] == "frequency"

        # No escalation
        incidents = [
            {"severity": "low", "date": datetime(2020, 1, 1)},
            {"severity": "low", "date": datetime(2021, 1, 1)},
        ]
        escalation = engine._detect_escalation(incidents)
        assert escalation["detected"] is False

    def test_calculate_recidivism_rate(self):
        """Test recidivism rate calculation."""
        engine = RepeatOffenderAnalytics()

        rate = engine._calculate_recidivism_rate(
            total_offenders=1000,
            repeat_offenders=250,
        )
        assert rate == 0.25

        # Edge case: no offenders
        rate = engine._calculate_recidivism_rate(
            total_offenders=0,
            repeat_offenders=0,
        )
        assert rate == 0.0

    def test_calculate_average_interval(self):
        """Test average interval calculation."""
        engine = RepeatOffenderAnalytics()

        incidents = [
            {"date": datetime(2020, 1, 1)},
            {"date": datetime(2020, 4, 1)},  # 91 days
            {"date": datetime(2020, 7, 1)},  # 91 days
            {"date": datetime(2020, 10, 1)}, # 92 days
        ]

        avg_interval = engine._calculate_average_interval(incidents)
        assert 90 <= avg_interval <= 92

    def test_identify_crime_focus(self):
        """Test crime focus identification."""
        engine = RepeatOffenderAnalytics()

        incidents = [
            {"crime_category": "property"},
            {"crime_category": "property"},
            {"crime_category": "property"},
            {"crime_category": "violent"},
            {"crime_category": "drug"},
        ]

        focus = engine._identify_crime_focus(incidents)
        assert focus == "property"

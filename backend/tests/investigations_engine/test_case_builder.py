"""
Unit tests for the Case Builder module.

Tests cover:
- Case creation from incidents
- Case creation from suspects
- Evidence collection
- Timeline generation
- Risk assessment
- Lead generation
- Case storage
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.investigations_engine.case_builder import CaseBuilder
from app.investigations_engine.models import (
    Case,
    Evidence,
    RiskAssessment,
    TimelineEvent,
)


class TestCaseBuilder:
    """Test suite for CaseBuilder class."""

    @pytest.fixture
    def builder(self):
        """Create a CaseBuilder instance for testing."""
        return CaseBuilder()

    @pytest.fixture
    def sample_incident(self):
        """Create sample incident data for testing."""
        return {
            "incident_id": "INC001",
            "incident_type": "ROBBERY",
            "timestamp": datetime.utcnow().isoformat(),
            "location": {
                "latitude": 33.7490,
                "longitude": -84.3880,
                "address": "123 Main St, Atlanta, GA",
            },
            "narrative": "Armed robbery at convenience store. Suspect fled in dark vehicle.",
            "suspects": [
                {
                    "entity_id": "SUSP001",
                    "name": "John Doe",
                    "description": "Male, 6ft, black hoodie",
                }
            ],
            "vehicles": [
                {
                    "entity_id": "VEH001",
                    "plate_number": "ABC123",
                    "make": "Honda",
                    "model": "Civic",
                    "color": "Black",
                    "state": "GA",
                }
            ],
            "weapons": [{"type": "handgun", "caliber": "9mm"}],
        }

    def test_builder_initialization(self, builder):
        """Test that CaseBuilder initializes correctly."""
        assert builder is not None
        assert hasattr(builder, "build")

    @pytest.mark.asyncio
    async def test_build_case_from_incident(self, builder, sample_incident):
        """Test building a case from an incident."""
        with patch.object(builder, "_get_incident", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_incident

            case = await builder.build(incident_id="INC001")

            assert isinstance(case, Case)
            assert case.case_id is not None
            assert case.case_number is not None
            assert "INC001" in case.linked_incidents

    @pytest.mark.asyncio
    async def test_build_case_generates_title(self, builder, sample_incident):
        """Test that case building generates appropriate title."""
        with patch.object(builder, "_get_incident", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_incident

            case = await builder.build(incident_id="INC001")

            assert case.title is not None
            assert len(case.title) > 0

    @pytest.mark.asyncio
    async def test_build_case_generates_summary(self, builder, sample_incident):
        """Test that case building generates summary."""
        with patch.object(builder, "_get_incident", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_incident

            case = await builder.build(incident_id="INC001")

            assert case.summary is not None
            assert len(case.summary) > 0

    @pytest.mark.asyncio
    async def test_build_case_collects_evidence(self, builder, sample_incident):
        """Test that case building collects evidence."""
        with patch.object(builder, "_get_incident", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_incident

            case = await builder.build(incident_id="INC001")

            assert case.evidence is not None
            assert isinstance(case.evidence, Evidence)

    @pytest.mark.asyncio
    async def test_build_case_generates_timeline(self, builder, sample_incident):
        """Test that case building generates timeline."""
        with patch.object(builder, "_get_incident", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_incident

            case = await builder.build(incident_id="INC001")

            assert case.timeline is not None
            assert isinstance(case.timeline, list)

    @pytest.mark.asyncio
    async def test_build_case_assesses_risk(self, builder, sample_incident):
        """Test that case building assesses risk."""
        with patch.object(builder, "_get_incident", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_incident

            case = await builder.build(incident_id="INC001")

            assert case.risk_assessment is not None
            assert isinstance(case.risk_assessment, RiskAssessment)
            assert 0 <= case.risk_assessment.overall_score <= 1

    @pytest.mark.asyncio
    async def test_build_case_generates_recommendations(self, builder, sample_incident):
        """Test that case building generates recommendations."""
        with patch.object(builder, "_get_incident", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_incident

            case = await builder.build(incident_id="INC001")

            assert case.recommendations is not None
            assert isinstance(case.recommendations, list)

    @pytest.mark.asyncio
    async def test_build_case_with_custom_title(self, builder, sample_incident):
        """Test building a case with custom title."""
        with patch.object(builder, "_get_incident", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_incident

            custom_title = "Custom Investigation Title"
            case = await builder.build(incident_id="INC001", title=custom_title)

            assert case.title == custom_title

    def test_generate_case_number(self, builder):
        """Test case number generation."""
        case_number = builder._generate_case_number()

        assert case_number is not None
        assert case_number.startswith("CASE-")
        assert str(datetime.utcnow().year) in case_number

    def test_determine_priority_high(self, builder):
        """Test priority determination for high-risk case."""
        risk_score = 0.85
        priority = builder._determine_priority(risk_score)

        assert priority == "critical"

    def test_determine_priority_medium(self, builder):
        """Test priority determination for medium-risk case."""
        risk_score = 0.5
        priority = builder._determine_priority(risk_score)

        assert priority in ["high", "medium"]

    def test_determine_priority_low(self, builder):
        """Test priority determination for low-risk case."""
        risk_score = 0.2
        priority = builder._determine_priority(risk_score)

        assert priority == "low"


class TestCaseBuilderRiskAssessment:
    """Test suite for risk assessment functionality."""

    @pytest.fixture
    def builder(self):
        """Create a CaseBuilder instance for testing."""
        return CaseBuilder()

    def test_assess_risk_with_weapons(self, builder):
        """Test risk assessment with weapons present."""
        case_data = {
            "weapons": [{"type": "handgun"}],
            "suspects": [],
            "vehicles": [],
            "linked_incidents": [],
        }

        risk = builder._assess_risk(case_data)

        assert risk.weapon_risk > 0

    def test_assess_risk_with_repeat_offender(self, builder):
        """Test risk assessment with repeat offender."""
        case_data = {
            "weapons": [],
            "suspects": [{"prior_incidents": 5, "risk_score": 0.8}],
            "vehicles": [],
            "linked_incidents": [],
        }

        risk = builder._assess_risk(case_data)

        assert risk.offender_risk > 0

    def test_assess_risk_with_multiple_incidents(self, builder):
        """Test risk assessment with multiple linked incidents."""
        case_data = {
            "weapons": [],
            "suspects": [],
            "vehicles": [],
            "linked_incidents": ["INC001", "INC002", "INC003", "INC004", "INC005"],
        }

        risk = builder._assess_risk(case_data)

        assert risk.overall_score > 0.3

    def test_assess_risk_overall_calculation(self, builder):
        """Test that overall risk is calculated correctly."""
        case_data = {
            "weapons": [{"type": "handgun"}],
            "suspects": [{"prior_incidents": 3}],
            "vehicles": [{"stolen": True}],
            "linked_incidents": ["INC001", "INC002"],
        }

        risk = builder._assess_risk(case_data)

        assert 0 <= risk.overall_score <= 1
        assert risk.factors is not None
        assert len(risk.factors) > 0

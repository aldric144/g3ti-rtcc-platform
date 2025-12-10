"""Tests for the Rules Engine module."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.intel_orchestration.rules_engine import (
    RuleCategory,
    RuleOperator,
    ThreatLevel,
    ScoringRule,
    RuleCondition,
    PriorityScore,
    RiskProfile,
    ThreatAssessment,
    RulesEngineConfig,
    RulesEngine,
)


class TestRuleCategory:
    """Tests for RuleCategory enum."""

    def test_all_categories_defined(self):
        """Test all rule categories are defined."""
        expected_categories = [
            "ENGINE_CONFIDENCE", "ENTITY_RISK", "LOCATION_RISK",
            "OFFICER_SAFETY", "FEDERAL_MATCH", "HISTORICAL_TREND",
            "INTELLIGENCE_CATEGORY", "TEMPORAL", "GEOGRAPHIC", "CUSTOM",
        ]
        
        for category in expected_categories:
            assert hasattr(RuleCategory, category)


class TestRuleOperator:
    """Tests for RuleOperator enum."""

    def test_all_operators_defined(self):
        """Test all rule operators are defined."""
        expected_operators = [
            "EQUALS", "NOT_EQUALS", "GREATER_THAN", "LESS_THAN",
            "GREATER_THAN_OR_EQUALS", "LESS_THAN_OR_EQUALS",
            "CONTAINS", "NOT_CONTAINS", "IN", "NOT_IN",
            "EXISTS", "NOT_EXISTS",
        ]
        
        for operator in expected_operators:
            assert hasattr(RuleOperator, operator)


class TestThreatLevel:
    """Tests for ThreatLevel enum."""

    def test_threat_level_values(self):
        """Test threat level values."""
        assert ThreatLevel.CRITICAL.value == "critical"
        assert ThreatLevel.HIGH.value == "high"
        assert ThreatLevel.MEDIUM.value == "medium"
        assert ThreatLevel.LOW.value == "low"
        assert ThreatLevel.MINIMAL.value == "minimal"


class TestScoringRule:
    """Tests for ScoringRule model."""

    def test_rule_creation(self):
        """Test creating a scoring rule."""
        rule = ScoringRule(
            name="high_confidence",
            description="High confidence signal",
            category=RuleCategory.ENGINE_CONFIDENCE,
            conditions=[
                RuleCondition(
                    field="confidence",
                    operator=RuleOperator.GREATER_THAN_OR_EQUALS,
                    value=0.9,
                )
            ],
            score_modifier=15.0,
        )
        
        assert rule.id is not None
        assert rule.name == "high_confidence"
        assert rule.score_modifier == 15.0

    def test_rule_with_multiplier(self):
        """Test rule with score multiplier."""
        rule = ScoringRule(
            name="federal_warrant",
            description="Federal warrant match",
            category=RuleCategory.FEDERAL_MATCH,
            conditions=[
                RuleCondition(
                    field="has_federal_warrant",
                    operator=RuleOperator.EQUALS,
                    value=True,
                )
            ],
            score_multiplier=1.5,
        )
        
        assert rule.score_multiplier == 1.5

    def test_rule_enabled_default(self):
        """Test rule enabled by default."""
        rule = ScoringRule(
            name="test_rule",
            category=RuleCategory.CUSTOM,
            conditions=[],
        )
        
        assert rule.enabled is True


class TestRuleCondition:
    """Tests for RuleCondition model."""

    def test_condition_creation(self):
        """Test creating a rule condition."""
        condition = RuleCondition(
            field="confidence",
            operator=RuleOperator.GREATER_THAN,
            value=0.8,
        )
        
        assert condition.field == "confidence"
        assert condition.operator == RuleOperator.GREATER_THAN
        assert condition.value == 0.8

    def test_nested_field_condition(self):
        """Test condition with nested field."""
        condition = RuleCondition(
            field="entity.risk_score",
            operator=RuleOperator.GREATER_THAN_OR_EQUALS,
            value=80,
        )
        
        assert condition.field == "entity.risk_score"


class TestPriorityScore:
    """Tests for PriorityScore model."""

    def test_score_creation(self):
        """Test creating a priority score."""
        score = PriorityScore(
            entity_id="person-123",
            total_score=75.5,
            threat_level=ThreatLevel.HIGH,
            rules_applied=["high_confidence", "entity_risk"],
            factors=["High confidence signal", "Known offender"],
            confidence=0.85,
        )
        
        assert score.entity_id == "person-123"
        assert score.total_score == 75.5
        assert score.threat_level == ThreatLevel.HIGH

    def test_score_clamping(self):
        """Test score is within valid range."""
        score = PriorityScore(
            entity_id="test",
            total_score=150.0,  # Over 100
            threat_level=ThreatLevel.CRITICAL,
            rules_applied=[],
            factors=[],
            confidence=1.0,
        )
        
        # Score should be stored as-is (clamping happens in engine)
        assert score.total_score == 150.0


class TestRiskProfile:
    """Tests for RiskProfile model."""

    def test_profile_creation(self):
        """Test creating a risk profile."""
        profile = RiskProfile(
            entity_id="person-123",
            entity_type="person",
            risk_score=85.0,
            risk_factors=["Prior arrests", "Active warrant"],
            last_updated=datetime.now(timezone.utc),
        )
        
        assert profile.entity_id == "person-123"
        assert profile.risk_score == 85.0
        assert len(profile.risk_factors) == 2


class TestThreatAssessment:
    """Tests for ThreatAssessment model."""

    def test_assessment_creation(self):
        """Test creating a threat assessment."""
        assessment = ThreatAssessment(
            entity_id="person-123",
            threat_level=ThreatLevel.HIGH,
            confidence=0.88,
            factors=["Armed and dangerous", "History of violence"],
            recommendations=["Approach with caution", "Request backup"],
            priority_score=PriorityScore(
                entity_id="person-123",
                total_score=85.0,
                threat_level=ThreatLevel.HIGH,
                rules_applied=[],
                factors=[],
                confidence=0.88,
            ),
        )
        
        assert assessment.threat_level == ThreatLevel.HIGH
        assert len(assessment.recommendations) == 2


class TestRulesEngineConfig:
    """Tests for RulesEngineConfig model."""

    def test_default_config(self):
        """Test default rules engine configuration."""
        config = RulesEngineConfig()
        
        assert config.enabled is True
        assert config.default_base_score == 50.0
        assert config.max_score == 100.0
        assert config.min_score == 0.0

    def test_custom_config(self):
        """Test custom rules engine configuration."""
        config = RulesEngineConfig(
            enabled=False,
            default_base_score=40.0,
            enable_caching=False,
        )
        
        assert config.enabled is False
        assert config.default_base_score == 40.0


class TestRulesEngine:
    """Tests for RulesEngine class."""

    def test_engine_initialization(self):
        """Test rules engine initialization."""
        engine = RulesEngine()
        
        assert engine.config is not None
        assert len(engine.rules) > 0  # Should have default rules

    def test_engine_with_custom_config(self):
        """Test engine with custom config."""
        config = RulesEngineConfig(
            default_base_score=60.0,
        )
        engine = RulesEngine(config=config)
        
        assert engine.config.default_base_score == 60.0

    def test_default_rules_loaded(self):
        """Test default rules are loaded."""
        engine = RulesEngine()
        
        # Should have at least the default rules
        assert len(engine.rules) >= 10

    @pytest.mark.asyncio
    async def test_calculate_priority(self):
        """Test calculating priority score."""
        engine = RulesEngine()
        
        signal_data = {
            "confidence": 0.9,
            "category": "violent_crime",
        }
        
        score = await engine.calculate_priority(signal_data, "entity-123")
        
        assert score is not None
        assert isinstance(score, PriorityScore)
        assert 0 <= score.total_score <= 100

    @pytest.mark.asyncio
    async def test_high_confidence_scoring(self):
        """Test high confidence signals get higher scores."""
        engine = RulesEngine()
        
        high_conf = await engine.calculate_priority(
            {"confidence": 0.95},
            "entity-1",
        )
        
        low_conf = await engine.calculate_priority(
            {"confidence": 0.5},
            "entity-2",
        )
        
        assert high_conf.total_score >= low_conf.total_score

    @pytest.mark.asyncio
    async def test_officer_safety_scoring(self):
        """Test officer safety flag increases score."""
        engine = RulesEngine()
        
        with_safety = await engine.calculate_priority(
            {"confidence": 0.8, "officer_safety_flag": True},
            "entity-1",
        )
        
        without_safety = await engine.calculate_priority(
            {"confidence": 0.8, "officer_safety_flag": False},
            "entity-2",
        )
        
        assert with_safety.total_score > without_safety.total_score

    @pytest.mark.asyncio
    async def test_federal_match_multiplier(self):
        """Test federal match applies multiplier."""
        engine = RulesEngine()
        
        with_federal = await engine.calculate_priority(
            {"confidence": 0.8, "has_federal_warrant": True},
            "entity-1",
        )
        
        without_federal = await engine.calculate_priority(
            {"confidence": 0.8, "has_federal_warrant": False},
            "entity-2",
        )
        
        assert with_federal.total_score > without_federal.total_score

    @pytest.mark.asyncio
    async def test_threat_level_assignment(self):
        """Test threat level is assigned based on score."""
        engine = RulesEngine()
        
        # High score should get critical/high threat level
        high_score = await engine.calculate_priority(
            {"confidence": 0.99, "officer_safety_flag": True, "has_federal_warrant": True},
            "entity-1",
        )
        
        assert high_score.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]

    def test_add_rule(self):
        """Test adding a custom rule."""
        engine = RulesEngine()
        initial_count = len(engine.rules)
        
        rule = ScoringRule(
            name="custom_rule",
            category=RuleCategory.CUSTOM,
            conditions=[
                RuleCondition(
                    field="custom_field",
                    operator=RuleOperator.EQUALS,
                    value=True,
                )
            ],
            score_modifier=10.0,
        )
        
        engine.add_rule(rule)
        
        assert len(engine.rules) == initial_count + 1

    def test_remove_rule(self):
        """Test removing a rule."""
        engine = RulesEngine()
        
        rule = ScoringRule(
            name="temp_rule",
            category=RuleCategory.CUSTOM,
            conditions=[],
            score_modifier=5.0,
        )
        
        engine.add_rule(rule)
        engine.remove_rule(rule.id)
        
        # Rule should be removed
        found = any(r.id == rule.id for r in engine.rules)
        assert not found

    def test_get_rules_by_category(self):
        """Test getting rules by category."""
        engine = RulesEngine()
        
        confidence_rules = engine.get_rules_by_category(RuleCategory.ENGINE_CONFIDENCE)
        
        assert all(r.category == RuleCategory.ENGINE_CONFIDENCE for r in confidence_rules)

    @pytest.mark.asyncio
    async def test_assess_threat(self):
        """Test threat assessment."""
        engine = RulesEngine()
        
        assessment = await engine.assess_threat(
            entity_id="person-123",
            signal_data={"confidence": 0.9, "officer_safety_flag": True},
        )
        
        assert assessment is not None
        assert isinstance(assessment, ThreatAssessment)
        assert assessment.entity_id == "person-123"

    @pytest.mark.asyncio
    async def test_update_risk_profile(self):
        """Test updating risk profile."""
        engine = RulesEngine()
        
        await engine.update_risk_profile(
            entity_id="person-123",
            entity_type="person",
            risk_score=75.0,
            risk_factors=["Prior arrests"],
        )
        
        profile = engine.get_risk_profile("person-123")
        
        assert profile is not None
        assert profile.risk_score == 75.0

    def test_get_stats(self):
        """Test getting engine stats."""
        engine = RulesEngine()
        stats = engine.get_stats()
        
        assert "rules_count" in stats
        assert "rules_by_category" in stats
        assert "config" in stats

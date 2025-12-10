"""
Tests for Threat Scoring Engine module.

Phase 17: Global Threat Intelligence Engine
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.threat_intel.threat_scoring_engine import (
    ThreatScoringEngine,
    ThreatLevel,
    ThreatDomain,
    RuleType,
    FusionMethod,
    TriggerAction,
    ScoringRule,
    TriggerCondition,
    ThreatScore,
    FusedThreatScore,
)


class TestThreatScoringEngine:
    """Test suite for ThreatScoringEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a ThreatScoringEngine instance for testing."""
        return ThreatScoringEngine()

    def test_engine_initialization(self, engine):
        """Test that engine initializes correctly."""
        assert engine is not None
        assert isinstance(engine.scoring_rules, dict)
        assert isinstance(engine.trigger_conditions, dict)
        assert isinstance(engine.threat_scores, dict)

    def test_create_scoring_rule(self, engine):
        """Test creating a scoring rule."""
        rule = engine.create_scoring_rule(
            name="High Dark Web Activity",
            domain=ThreatDomain.DARK_WEB,
            rule_type=RuleType.THRESHOLD,
            conditions={"min_signals": 5, "min_priority": "high"},
            score_modifier=20.0,
            weight=1.5,
        )
        
        assert rule is not None
        assert rule.name == "High Dark Web Activity"
        assert rule.domain == ThreatDomain.DARK_WEB
        assert rule.rule_id in engine.scoring_rules

    def test_create_scoring_rule_pattern(self, engine):
        """Test creating a pattern-based scoring rule."""
        rule = engine.create_scoring_rule(
            name="Weapons Pattern",
            domain=ThreatDomain.WEAPONS,
            rule_type=RuleType.PATTERN,
            conditions={"pattern": "weapons_trafficking", "confidence": 0.8},
            score_modifier=30.0,
            weight=2.0,
        )
        
        assert rule is not None
        assert rule.rule_type == RuleType.PATTERN

    def test_get_scoring_rules(self, engine):
        """Test retrieving scoring rules."""
        engine.create_scoring_rule(
            name="Rule 1",
            domain=ThreatDomain.OSINT,
            rule_type=RuleType.THRESHOLD,
            conditions={},
            score_modifier=10.0,
            weight=1.0,
        )
        
        rules = engine.get_scoring_rules()
        assert isinstance(rules, list)

    def test_get_scoring_rules_by_domain(self, engine):
        """Test retrieving scoring rules by domain."""
        engine.create_scoring_rule(
            name="Cyber Rule",
            domain=ThreatDomain.CYBER,
            rule_type=RuleType.THRESHOLD,
            conditions={},
            score_modifier=15.0,
            weight=1.0,
        )
        
        rules = engine.get_scoring_rules(domain=ThreatDomain.CYBER)
        for rule in rules:
            assert rule.domain == ThreatDomain.CYBER

    def test_create_trigger_condition(self, engine):
        """Test creating a trigger condition."""
        trigger = engine.create_trigger_condition(
            name="Critical Alert Trigger",
            threshold_score=80.0,
            domains=[ThreatDomain.TERRORISM, ThreatDomain.WEAPONS],
            action=TriggerAction.ALERT,
            cooldown_minutes=30,
        )
        
        assert trigger is not None
        assert trigger.name == "Critical Alert Trigger"
        assert trigger.threshold_score == 80.0
        assert trigger.trigger_id in engine.trigger_conditions

    def test_get_trigger_conditions(self, engine):
        """Test retrieving trigger conditions."""
        engine.create_trigger_condition(
            name="Test Trigger",
            threshold_score=50.0,
            domains=[ThreatDomain.GANG],
            action=TriggerAction.LOG,
            cooldown_minutes=10,
        )
        
        triggers = engine.get_trigger_conditions()
        assert isinstance(triggers, list)

    def test_calculate_threat_score(self, engine):
        """Test calculating a threat score."""
        engine.create_scoring_rule(
            name="Base Rule",
            domain=ThreatDomain.DARK_WEB,
            rule_type=RuleType.THRESHOLD,
            conditions={"min_signals": 1},
            score_modifier=25.0,
            weight=1.0,
        )
        
        score = engine.calculate_threat_score(
            entity_id="entity-123",
            entity_type="person",
            domain=ThreatDomain.DARK_WEB,
            input_data={
                "signal_count": 5,
                "priority": "high",
                "sentiment_score": 75.0,
            },
        )
        
        assert score is not None
        assert score.entity_id == "entity-123"
        assert score.domain == ThreatDomain.DARK_WEB
        assert 0 <= score.score <= 100

    def test_calculate_threat_score_with_rules(self, engine):
        """Test calculating threat score with multiple rules."""
        engine.create_scoring_rule(
            name="Rule 1",
            domain=ThreatDomain.EXTREMIST_NETWORK,
            rule_type=RuleType.THRESHOLD,
            conditions={"min_connections": 3},
            score_modifier=20.0,
            weight=1.0,
        )
        engine.create_scoring_rule(
            name="Rule 2",
            domain=ThreatDomain.EXTREMIST_NETWORK,
            rule_type=RuleType.THRESHOLD,
            conditions={"min_influence": 50},
            score_modifier=15.0,
            weight=1.5,
        )
        
        score = engine.calculate_threat_score(
            entity_id="entity-456",
            entity_type="group",
            domain=ThreatDomain.EXTREMIST_NETWORK,
            input_data={
                "connections": 10,
                "influence_score": 75,
            },
        )
        
        assert score is not None
        assert score.score > 0

    def test_fuse_threat_scores(self, engine):
        """Test fusing threat scores from multiple domains."""
        score1 = engine.calculate_threat_score(
            entity_id="entity-789",
            entity_type="person",
            domain=ThreatDomain.DARK_WEB,
            input_data={"signal_count": 3},
        )
        score2 = engine.calculate_threat_score(
            entity_id="entity-789",
            entity_type="person",
            domain=ThreatDomain.OSINT,
            input_data={"mention_count": 10},
        )
        
        fused = engine.fuse_threat_scores(
            entity_id="entity-789",
            scores=[score1, score2] if score1 and score2 else [],
            method=FusionMethod.WEIGHTED_AVERAGE,
        )
        
        assert fused is not None
        assert fused.entity_id == "entity-789"

    def test_fuse_threat_scores_max_method(self, engine):
        """Test fusing scores using max score method."""
        score1 = engine.calculate_threat_score(
            entity_id="entity-max",
            entity_type="person",
            domain=ThreatDomain.TERRORISM,
            input_data={"threat_level": "high"},
        )
        score2 = engine.calculate_threat_score(
            entity_id="entity-max",
            entity_type="person",
            domain=ThreatDomain.WEAPONS,
            input_data={"weapons_count": 5},
        )
        
        fused = engine.fuse_threat_scores(
            entity_id="entity-max",
            scores=[score1, score2] if score1 and score2 else [],
            method=FusionMethod.MAX_SCORE,
        )
        
        assert fused is not None

    def test_fuse_threat_scores_bayesian_method(self, engine):
        """Test fusing scores using Bayesian method."""
        score1 = engine.calculate_threat_score(
            entity_id="entity-bayes",
            entity_type="person",
            domain=ThreatDomain.GANG,
            input_data={"gang_affiliation": True},
        )
        
        fused = engine.fuse_threat_scores(
            entity_id="entity-bayes",
            scores=[score1] if score1 else [],
            method=FusionMethod.BAYESIAN,
        )
        
        assert fused is not None

    def test_get_entity_scores(self, engine):
        """Test retrieving scores for an entity."""
        engine.calculate_threat_score(
            entity_id="entity-scores",
            entity_type="person",
            domain=ThreatDomain.DRUG,
            input_data={"drug_activity": True},
        )
        
        scores = engine.get_entity_scores("entity-scores")
        assert isinstance(scores, list)

    def test_get_high_threat_scores(self, engine):
        """Test retrieving high threat scores."""
        scores = engine.get_high_threat_scores(min_score=70)
        assert isinstance(scores, list)
        for score in scores:
            assert score.score >= 70

    def test_get_threat_level(self, engine):
        """Test getting threat level from score."""
        assert engine._get_threat_level(10) == ThreatLevel.LEVEL_1_MINIMAL
        assert engine._get_threat_level(30) == ThreatLevel.LEVEL_2_LOW
        assert engine._get_threat_level(50) == ThreatLevel.LEVEL_3_MODERATE
        assert engine._get_threat_level(70) == ThreatLevel.LEVEL_4_HIGH
        assert engine._get_threat_level(90) == ThreatLevel.LEVEL_5_CRITICAL

    def test_check_triggers(self, engine):
        """Test checking trigger conditions."""
        engine.create_trigger_condition(
            name="High Score Trigger",
            threshold_score=60.0,
            domains=[ThreatDomain.TERRORISM],
            action=TriggerAction.ALERT,
            cooldown_minutes=5,
        )
        
        score = ThreatScore(
            score_id="score-trigger",
            entity_id="entity-trigger",
            entity_type="person",
            domain=ThreatDomain.TERRORISM,
            score=75.0,
            threat_level=ThreatLevel.LEVEL_4_HIGH,
            contributing_factors=[],
            rules_applied=[],
            calculated_at=datetime.utcnow(),
            metadata={},
        )
        
        triggered = engine._check_triggers(score)
        assert isinstance(triggered, list)

    def test_register_ml_model(self, engine):
        """Test registering an ML model."""
        result = engine.register_ml_model(
            model_id="model-123",
            name="Threat Classifier",
            domain=ThreatDomain.TERRORISM,
            model_path="/models/threat_classifier.pkl",
        )
        
        assert result is True or result is None

    def test_get_metrics(self, engine):
        """Test retrieving metrics."""
        metrics = engine.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_rules" in metrics
        assert "total_triggers" in metrics
        assert "total_scores" in metrics
        assert "total_fused_scores" in metrics


class TestScoringRule:
    """Test suite for ScoringRule dataclass."""

    def test_rule_creation(self):
        """Test creating a ScoringRule."""
        rule = ScoringRule(
            rule_id="rule-123",
            name="Test Rule",
            domain=ThreatDomain.DARK_WEB,
            rule_type=RuleType.THRESHOLD,
            conditions={"min_signals": 5},
            score_modifier=20.0,
            weight=1.5,
            enabled=True,
            created_at=datetime.utcnow(),
            metadata={},
        )
        
        assert rule.rule_id == "rule-123"
        assert rule.name == "Test Rule"
        assert rule.score_modifier == 20.0


class TestTriggerCondition:
    """Test suite for TriggerCondition dataclass."""

    def test_trigger_creation(self):
        """Test creating a TriggerCondition."""
        trigger = TriggerCondition(
            trigger_id="trig-123",
            name="Test Trigger",
            threshold_score=75.0,
            domains=[ThreatDomain.TERRORISM],
            action=TriggerAction.ALERT,
            cooldown_minutes=30,
            last_triggered_at=None,
            enabled=True,
            created_at=datetime.utcnow(),
            metadata={},
        )
        
        assert trigger.trigger_id == "trig-123"
        assert trigger.threshold_score == 75.0
        assert trigger.action == TriggerAction.ALERT


class TestThreatScore:
    """Test suite for ThreatScore dataclass."""

    def test_score_creation(self):
        """Test creating a ThreatScore."""
        score = ThreatScore(
            score_id="score-123",
            entity_id="entity-123",
            entity_type="person",
            domain=ThreatDomain.DARK_WEB,
            score=65.0,
            threat_level=ThreatLevel.LEVEL_3_MODERATE,
            contributing_factors=["dark_web_activity", "weapons_keywords"],
            rules_applied=["rule-1", "rule-2"],
            calculated_at=datetime.utcnow(),
            metadata={},
        )
        
        assert score.score_id == "score-123"
        assert score.score == 65.0
        assert score.threat_level == ThreatLevel.LEVEL_3_MODERATE


class TestFusedThreatScore:
    """Test suite for FusedThreatScore dataclass."""

    def test_fused_score_creation(self):
        """Test creating a FusedThreatScore."""
        fused = FusedThreatScore(
            fused_score_id="fused-123",
            entity_id="entity-123",
            entity_type="person",
            overall_score=72.0,
            threat_level=ThreatLevel.LEVEL_4_HIGH,
            domain_scores={
                ThreatDomain.DARK_WEB: 65.0,
                ThreatDomain.OSINT: 55.0,
                ThreatDomain.EXTREMIST_NETWORK: 80.0,
            },
            fusion_method=FusionMethod.WEIGHTED_AVERAGE,
            source_scores=["score-1", "score-2", "score-3"],
            trend="increasing",
            jurisdiction_codes=["US-NY"],
            calculated_at=datetime.utcnow(),
            metadata={},
        )
        
        assert fused.fused_score_id == "fused-123"
        assert fused.overall_score == 72.0
        assert fused.fusion_method == FusionMethod.WEIGHTED_AVERAGE
        assert len(fused.domain_scores) == 3

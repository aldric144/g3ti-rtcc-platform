"""
Test Suite 5: Transparency & Explainability Engine Tests
Tests for explainability outputs
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.ethics_guardian.transparency import (
    get_transparency_engine,
    TransparencyEngine,
    ExplanationType,
    AuditSeverity,
)


class TestTransparencyEngine:
    """Tests for TransparencyEngine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_transparency_engine()

    def test_singleton_pattern(self):
        """Test that engine follows singleton pattern"""
        engine1 = get_transparency_engine()
        engine2 = get_transparency_engine()
        assert engine1 is engine2


class TestExplanationGeneration:
    """Tests for explanation generation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_transparency_engine()

    def test_generate_explanation(self):
        """Test basic explanation generation"""
        decision_data = {
            "decision": "ALLOW",
            "ethics_score": 92,
            "bias_detected": False,
            "civil_rights_compliant": True,
        }
        explanation = self.engine.generate_explanation(
            "test-001", "patrol", decision_data
        )
        assert explanation is not None
        assert explanation.action_id == "test-001"
        assert explanation.action_type == "patrol"

    def test_explanation_has_summary(self):
        """Test explanation includes human-readable summary"""
        decision_data = {
            "decision": "ALLOW",
            "ethics_score": 85,
        }
        explanation = self.engine.generate_explanation(
            "test-002", "surveillance", decision_data
        )
        assert explanation.summary is not None
        assert len(explanation.summary) > 0

    def test_explanation_has_chain_of_reasoning(self):
        """Test explanation includes chain of reasoning"""
        decision_data = {
            "decision": "REVIEW",
            "ethics_score": 55,
            "bias_detected": True,
        }
        explanation = self.engine.generate_explanation(
            "test-003", "enforcement", decision_data
        )
        assert explanation.chain_of_reasoning is not None
        assert len(explanation.chain_of_reasoning) > 0

    def test_explanation_has_legal_basis(self):
        """Test explanation includes legal basis"""
        decision_data = {
            "decision": "BLOCK",
            "civil_rights_violation": True,
            "violation_type": "FOURTH_AMENDMENT",
        }
        explanation = self.engine.generate_explanation(
            "test-004", "search", decision_data
        )
        assert explanation.legal_basis is not None

    def test_explanation_has_data_sources(self):
        """Test explanation includes data sources"""
        decision_data = {
            "decision": "ALLOW",
            "data_sources": ["sensor_data", "historical_records"],
        }
        explanation = self.engine.generate_explanation(
            "test-005", "patrol", decision_data
        )
        assert explanation.data_sources is not None

    def test_explanation_types(self):
        """Test all explanation types are supported"""
        for exp_type in ExplanationType:
            decision_data = {
                "decision": exp_type.value,
                "ethics_score": 75,
            }
            explanation = self.engine.generate_explanation(
                f"test-{exp_type.value}", "action", decision_data
            )
            assert explanation is not None


class TestAuditLogging:
    """Tests for audit logging"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_transparency_engine()

    def test_audit_entry_creation(self):
        """Test audit entry is created"""
        initial_count = len(self.engine.audit_log)
        decision_data = {
            "decision": "ALLOW",
            "ethics_score": 90,
        }
        self.engine.generate_explanation("test-audit-001", "patrol", decision_data)
        assert len(self.engine.audit_log) >= initial_count

    def test_audit_entry_has_hash(self):
        """Test audit entry includes hash for integrity"""
        decision_data = {
            "decision": "ALLOW",
            "ethics_score": 88,
        }
        self.engine.generate_explanation("test-hash-001", "patrol", decision_data)
        if len(self.engine.audit_log) > 0:
            latest_entry = self.engine.audit_log[-1]
            assert hasattr(latest_entry, "hash_chain")
            assert latest_entry.hash_chain is not None

    def test_audit_severity_levels(self):
        """Test audit severity levels are correctly assigned"""
        for severity in AuditSeverity:
            assert severity in [
                AuditSeverity.INFO,
                AuditSeverity.WARNING,
                AuditSeverity.CRITICAL,
                AuditSeverity.VIOLATION,
            ]

    def test_get_audit_log(self):
        """Test retrieving audit log"""
        audit_log = self.engine.get_audit_log()
        assert isinstance(audit_log, list)

    def test_get_audit_log_with_severity_filter(self):
        """Test retrieving audit log with severity filter"""
        audit_log = self.engine.get_audit_log(severity=AuditSeverity.WARNING)
        assert isinstance(audit_log, list)

    def test_get_audit_log_with_limit(self):
        """Test retrieving audit log with limit"""
        audit_log = self.engine.get_audit_log(limit=10)
        assert len(audit_log) <= 10


class TestRetentionPeriods:
    """Tests for audit log retention periods"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_transparency_engine()

    def test_retention_periods_defined(self):
        """Test retention periods are defined for all severities"""
        expected_periods = {
            AuditSeverity.INFO: 365,
            AuditSeverity.WARNING: 730,
            AuditSeverity.CRITICAL: 2555,
            AuditSeverity.VIOLATION: 2555,
        }
        for severity, expected_days in expected_periods.items():
            assert self.engine.retention_periods[severity] == expected_days


class TestHashChainIntegrity:
    """Tests for hash chain integrity"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_transparency_engine()

    def test_verify_audit_chain(self):
        """Test audit chain verification"""
        decision_data = {
            "decision": "ALLOW",
            "ethics_score": 85,
        }
        self.engine.generate_explanation("test-chain-001", "patrol", decision_data)
        self.engine.generate_explanation("test-chain-002", "patrol", decision_data)
        is_valid = self.engine.verify_audit_chain()
        assert is_valid is True

    def test_hash_algorithm(self):
        """Test SHA-256 hash algorithm is used"""
        decision_data = {
            "decision": "ALLOW",
            "ethics_score": 90,
        }
        self.engine.generate_explanation("test-sha-001", "patrol", decision_data)
        if len(self.engine.audit_log) > 0:
            latest_entry = self.engine.audit_log[-1]
            assert len(latest_entry.hash_chain) == 64


class TestExplanationComponents:
    """Tests for explanation components"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = get_transparency_engine()

    def test_bias_metrics_in_explanation(self):
        """Test bias metrics are included in explanation"""
        decision_data = {
            "decision": "REVIEW",
            "bias_detected": True,
            "disparate_impact_ratio": 0.72,
            "affected_groups": ["Black"],
        }
        explanation = self.engine.generate_explanation(
            "test-bias-exp", "enforcement", decision_data
        )
        assert explanation.bias_metrics is not None

    def test_risk_impacts_in_explanation(self):
        """Test risk impacts are included in explanation"""
        decision_data = {
            "decision": "REVIEW",
            "force_risk": 65,
            "risk_factors": ["mental_health", "crowd_presence"],
        }
        explanation = self.engine.generate_explanation(
            "test-risk-exp", "enforcement", decision_data
        )
        assert explanation.risk_impacts is not None

    def test_safeguard_triggers_in_explanation(self):
        """Test safeguard triggers are included in explanation"""
        decision_data = {
            "decision": "MODIFY",
            "safeguard_triggered": True,
            "triggered_safeguards": ["disparate_impact_review"],
        }
        explanation = self.engine.generate_explanation(
            "test-safeguard-exp", "enforcement", decision_data
        )
        assert explanation.safeguard_triggers is not None

    def test_alternative_actions_in_explanation(self):
        """Test alternative actions are suggested"""
        decision_data = {
            "decision": "BLOCK",
            "ethics_score": 35,
        }
        explanation = self.engine.generate_explanation(
            "test-alt-exp", "enforcement", decision_data
        )
        assert explanation.alternative_actions is not None

    def test_limitations_in_explanation(self):
        """Test limitations are disclosed"""
        decision_data = {
            "decision": "ALLOW",
            "ethics_score": 80,
            "confidence": 0.75,
        }
        explanation = self.engine.generate_explanation(
            "test-limit-exp", "patrol", decision_data
        )
        assert explanation.limitations is not None

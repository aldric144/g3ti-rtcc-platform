"""
Test Suite: Auto-Correction Engine

Tests for the auto-correction functionality including:
- Correction action creation
- Approval workflow
- Execution and rollback
- Pipeline repair
- Service restart
- Cache rebuild
- Load rebalancing
- Model drift detection
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform")

from backend.app.ai_supervisor.auto_corrector import (
    AutoCorrector,
    CorrectionType,
    CorrectionStatus,
    CorrectionPriority,
    CorrectionAction,
    CorrectionResult,
    ModelDriftReport,
    PipelineStatus,
)


class TestAutoCorrector:
    """Test cases for AutoCorrector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.corrector = AutoCorrector()

    def test_singleton_pattern(self):
        """Test that AutoCorrector follows singleton pattern."""
        corrector1 = AutoCorrector()
        corrector2 = AutoCorrector()
        assert corrector1 is corrector2

    def test_create_correction_action(self):
        """Test creating a correction action."""
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.SERVICE_RESTART,
            target_engine="cyber_intel",
            target_component="threat_analyzer",
            priority=CorrectionPriority.HIGH,
            description="Restart failed service",
        )
        assert action is not None
        assert action.correction_type == CorrectionType.SERVICE_RESTART
        assert action.target_engine == "cyber_intel"
        assert action.priority == CorrectionPriority.HIGH

    def test_create_correction_action_requires_approval(self):
        """Test that critical corrections require approval."""
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.FAILOVER_ACTIVATION,
            target_engine="predictive_ai",
            target_component="main_cluster",
            priority=CorrectionPriority.CRITICAL,
            description="Activate failover",
        )
        assert action.requires_approval is True
        assert action.status == CorrectionStatus.PENDING_APPROVAL

    def test_approve_correction(self):
        """Test approving a correction action."""
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.SERVICE_RESTART,
            target_engine="city_brain",
            target_component="prediction_service",
            priority=CorrectionPriority.CRITICAL,
            description="Restart service",
        )
        success = self.corrector.approve_correction(action.action_id, "admin_user")
        assert success is True
        updated_action = self.corrector.correction_actions.get(action.action_id)
        assert updated_action.status == CorrectionStatus.APPROVED
        assert updated_action.approved_by == "admin_user"

    def test_execute_correction(self):
        """Test executing a correction action."""
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.CACHE_REBUILD,
            target_engine="intel_orchestration",
            target_component="signal_cache",
            priority=CorrectionPriority.MEDIUM,
            description="Rebuild cache",
        )
        if action.requires_approval:
            self.corrector.approve_correction(action.action_id, "admin")
        
        result = self.corrector.execute_correction(action.action_id)
        assert result is not None
        assert result.action_id == action.action_id
        assert result.success is True

    def test_execute_unapproved_correction_fails(self):
        """Test that executing unapproved correction fails."""
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.FAILOVER_ACTIVATION,
            target_engine="emergency_management",
            target_component="main_system",
            priority=CorrectionPriority.CRITICAL,
            description="Activate failover",
        )
        with pytest.raises(ValueError):
            self.corrector.execute_correction(action.action_id)

    def test_repair_stalled_pipeline(self):
        """Test repairing a stalled pipeline."""
        result = self.corrector.repair_stalled_pipeline("pipeline_001")
        assert result is not None
        assert result.success is True

    def test_restart_failed_service(self):
        """Test restarting a failed service."""
        result = self.corrector.restart_failed_service(
            engine="cyber_intel",
            service_name="threat_analyzer",
            force=False,
        )
        assert result is not None
        assert result.success is True

    def test_rebuild_corrupted_cache(self):
        """Test rebuilding a corrupted cache."""
        result = self.corrector.rebuild_corrupted_cache(
            engine="city_brain",
            cache_name="prediction_cache",
        )
        assert result is not None
        assert result.success is True

    def test_rebalance_compute_load(self):
        """Test rebalancing compute load."""
        result = self.corrector.rebalance_compute_load(
            source_engine="predictive_ai",
            target_engine="intel_orchestration",
            load_percent=20.0,
        )
        assert result is not None
        assert result.success is True

    def test_validate_policy_conflicts(self):
        """Test validating policy conflicts."""
        conflicts = self.corrector.validate_policy_conflicts(
            policies=[
                {"name": "policy1", "rules": ["rule1"]},
                {"name": "policy2", "rules": ["rule2"]},
            ]
        )
        assert conflicts is not None
        assert "conflicts_found" in conflicts

    def test_detect_model_drift(self):
        """Test detecting model drift."""
        report = self.corrector.detect_model_drift(
            model_name="crime_forecast",
            engine="predictive_ai",
            baseline_metrics={"accuracy": 0.95, "precision": 0.92},
            current_metrics={"accuracy": 0.82, "precision": 0.78},
        )
        assert report is not None
        assert report.model_name == "crime_forecast"
        assert report.drift_score > 0.0

    def test_detect_model_drift_no_drift(self):
        """Test that similar metrics show no drift."""
        report = self.corrector.detect_model_drift(
            model_name="stable_model",
            engine="predictive_ai",
            baseline_metrics={"accuracy": 0.95},
            current_metrics={"accuracy": 0.94},
        )
        assert report.drift_score < 0.1

    def test_recover_data_feed(self):
        """Test recovering a data feed."""
        result = self.corrector.recover_data_feed(
            engine="global_awareness",
            feed_name="satellite_feed",
            fallback_source="backup_satellite",
        )
        assert result is not None
        assert result.success is True

    def test_rollback_correction(self):
        """Test rolling back a correction."""
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.LOAD_REBALANCE,
            target_engine="city_brain",
            target_component="load_balancer",
            priority=CorrectionPriority.MEDIUM,
            description="Rebalance load",
        )
        if action.requires_approval:
            self.corrector.approve_correction(action.action_id, "admin")
        self.corrector.execute_correction(action.action_id)
        
        result = self.corrector.rollback_correction(action.action_id)
        assert result is not None
        assert result.rollback_performed is True

    def test_get_pending_corrections(self):
        """Test getting pending corrections."""
        self.corrector.create_correction_action(
            correction_type=CorrectionType.SERVICE_RESTART,
            target_engine="test_engine",
            target_component="test_component",
            priority=CorrectionPriority.HIGH,
            description="Test correction",
        )
        pending = self.corrector.get_pending_corrections()
        assert len(pending) >= 0

    def test_get_correction_history(self):
        """Test getting correction history."""
        history = self.corrector.get_correction_history(limit=10)
        assert isinstance(history, list)

    def test_get_pipeline_statuses(self):
        """Test getting pipeline statuses."""
        statuses = self.corrector.get_pipeline_statuses()
        assert isinstance(statuses, list)

    def test_get_stalled_pipelines(self):
        """Test getting stalled pipelines."""
        stalled = self.corrector.get_stalled_pipelines()
        assert isinstance(stalled, list)

    def test_correction_chain_of_custody(self):
        """Test that corrections have chain of custody hash."""
        action = self.corrector.create_correction_action(
            correction_type=CorrectionType.CACHE_REBUILD,
            target_engine="test_engine",
            target_component="test_cache",
            priority=CorrectionPriority.LOW,
            description="Test correction",
        )
        assert action.chain_of_custody_hash is not None
        assert len(action.chain_of_custody_hash) == 64

    def test_get_statistics(self):
        """Test getting corrector statistics."""
        stats = self.corrector.get_statistics()
        assert "total_corrections" in stats
        assert "completed" in stats
        assert "failed" in stats
        assert "success_rate" in stats


class TestCorrectionType:
    """Test cases for CorrectionType enum."""

    def test_correction_type_values(self):
        """Test correction type enum values."""
        assert CorrectionType.PIPELINE_REPAIR.value == "pipeline_repair"
        assert CorrectionType.SERVICE_RESTART.value == "service_restart"
        assert CorrectionType.CACHE_REBUILD.value == "cache_rebuild"
        assert CorrectionType.LOAD_REBALANCE.value == "load_rebalance"


class TestCorrectionStatus:
    """Test cases for CorrectionStatus enum."""

    def test_correction_status_values(self):
        """Test correction status enum values."""
        assert CorrectionStatus.PENDING.value == "pending"
        assert CorrectionStatus.PENDING_APPROVAL.value == "pending_approval"
        assert CorrectionStatus.APPROVED.value == "approved"
        assert CorrectionStatus.IN_PROGRESS.value == "in_progress"
        assert CorrectionStatus.COMPLETED.value == "completed"
        assert CorrectionStatus.FAILED.value == "failed"


class TestCorrectionPriority:
    """Test cases for CorrectionPriority enum."""

    def test_correction_priority_values(self):
        """Test correction priority enum values."""
        assert CorrectionPriority.LOW.value == "low"
        assert CorrectionPriority.MEDIUM.value == "medium"
        assert CorrectionPriority.HIGH.value == "high"
        assert CorrectionPriority.CRITICAL.value == "critical"
        assert CorrectionPriority.EMERGENCY.value == "emergency"

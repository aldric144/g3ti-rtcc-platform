"""Tests for Auto Dispatch Engine"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.drones.auto_dispatch import (
    AutoDispatchEngine,
    DispatchTrigger,
    DispatchPriority,
    DispatchStatus,
    TriggerEvent,
    DispatchRequest,
    DispatchRule,
)
from app.drones.registry import DroneRegistryService, Drone, DroneStatus, DroneType, DroneCapability


class TestAutoDispatchEngine:
    """Test suite for AutoDispatchEngine"""

    @pytest.fixture
    def registry(self):
        """Create a drone registry with test drones"""
        registry = DroneRegistryService()
        drone = Drone(
            drone_id="drone-001",
            call_sign="EAGLE-1",
            drone_type=DroneType.SURVEILLANCE,
            status=DroneStatus.STANDBY,
            capabilities=[DroneCapability.HD_CAMERA, DroneCapability.THERMAL_CAMERA],
            latitude=33.749,
            longitude=-84.388,
            altitude_m=0,
            battery_percent=100,
            max_altitude_m=400,
            max_speed_mps=20,
            max_flight_time_minutes=45,
        )
        registry.register_drone(drone)
        return registry

    @pytest.fixture
    def dispatch_engine(self, registry):
        """Create an auto dispatch engine"""
        return AutoDispatchEngine(drone_registry=registry)

    @pytest.fixture
    def shotspotter_event(self):
        """Create a sample ShotSpotter trigger event"""
        return TriggerEvent(
            event_id="evt-001",
            trigger_type=DispatchTrigger.SHOTSPOTTER,
            timestamp=datetime.utcnow(),
            latitude=33.750,
            longitude=-84.390,
            priority=DispatchPriority.CRITICAL,
            source_system="ShotSpotter",
            source_event_id="ss-12345",
            description="Multiple gunshots detected",
            threat_level=8,
            radius_m=200,
        )

    def test_process_trigger_creates_request(self, dispatch_engine, shotspotter_event):
        """Test that processing a trigger creates a dispatch request"""
        request = dispatch_engine.process_trigger(shotspotter_event)
        assert request is not None
        assert request.trigger_event.event_id == shotspotter_event.event_id
        assert request.status in [DispatchStatus.PENDING, DispatchStatus.EVALUATING, DispatchStatus.DISPATCHED]

    def test_process_trigger_evaluates_drones(self, dispatch_engine, shotspotter_event):
        """Test that trigger processing evaluates available drones"""
        request = dispatch_engine.process_trigger(shotspotter_event)
        assert request.evaluation_score is not None
        assert request.evaluation_factors is not None

    def test_get_dispatch_requests(self, dispatch_engine, shotspotter_event):
        """Test getting dispatch requests"""
        dispatch_engine.process_trigger(shotspotter_event)
        requests = dispatch_engine.get_dispatch_requests()
        assert len(requests) >= 1

    def test_get_dispatch_request_by_id(self, dispatch_engine, shotspotter_event):
        """Test getting a specific dispatch request"""
        created_request = dispatch_engine.process_trigger(shotspotter_event)
        request = dispatch_engine.get_dispatch_request(created_request.request_id)
        assert request is not None
        assert request.request_id == created_request.request_id

    def test_cancel_dispatch_request(self, dispatch_engine, shotspotter_event):
        """Test canceling a dispatch request"""
        request = dispatch_engine.process_trigger(shotspotter_event)
        result = dispatch_engine.cancel_dispatch_request(
            request.request_id,
            operator_id="op-001",
            reason="False alarm",
        )
        assert result is True
        
        updated_request = dispatch_engine.get_dispatch_request(request.request_id)
        assert updated_request.status == DispatchStatus.CANCELLED

    def test_get_dispatch_rules(self, dispatch_engine):
        """Test getting dispatch rules"""
        rules = dispatch_engine.get_dispatch_rules()
        assert len(rules) > 0
        assert any(r.trigger_type == DispatchTrigger.SHOTSPOTTER for r in rules)

    def test_update_dispatch_rule(self, dispatch_engine):
        """Test updating a dispatch rule"""
        rules = dispatch_engine.get_dispatch_rules()
        shotspotter_rule = next(r for r in rules if r.trigger_type == DispatchTrigger.SHOTSPOTTER)
        
        result = dispatch_engine.update_dispatch_rule(
            shotspotter_rule.rule_id,
            enabled=False,
        )
        assert result is True
        
        updated_rules = dispatch_engine.get_dispatch_rules()
        updated_rule = next(r for r in updated_rules if r.rule_id == shotspotter_rule.rule_id)
        assert updated_rule.enabled is False

    def test_dispatch_priority_ordering(self, dispatch_engine):
        """Test that dispatch priorities are correctly ordered"""
        assert DispatchPriority.CRITICAL.value > DispatchPriority.URGENT.value
        assert DispatchPriority.URGENT.value > DispatchPriority.HIGH.value
        assert DispatchPriority.HIGH.value > DispatchPriority.NORMAL.value
        assert DispatchPriority.NORMAL.value > DispatchPriority.LOW.value

    def test_trigger_types_exist(self):
        """Test that all required trigger types exist"""
        required_triggers = [
            "SHOTSPOTTER",
            "CRASH_DETECTION",
            "DANGEROUS_KEYWORD_911",
            "OFFICER_DISTRESS",
            "AMBUSH_WARNING",
            "PERIMETER_BREACH",
            "HOT_VEHICLE_LPR",
            "MISSING_PERSON",
        ]
        for trigger in required_triggers:
            assert hasattr(DispatchTrigger, trigger)

    def test_metrics(self, dispatch_engine, shotspotter_event):
        """Test dispatch metrics"""
        dispatch_engine.process_trigger(shotspotter_event)
        metrics = dispatch_engine.get_metrics()
        assert metrics.total_requests >= 1

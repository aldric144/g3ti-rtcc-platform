"""
Phase 19: Robotics Mission Engine Module Tests

Tests for MissionPlanner, MissionAutoDispatcher, RoboticsTimelineBuilder, and StreamingEndpoints.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class TestMissionPlanner:
    """Tests for MissionPlanner."""

    def test_create_mission(self):
        """Test mission creation."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner, MissionType

        planner = MissionPlanner()
        mission = planner.create_mission(
            name="North Patrol",
            mission_type=MissionType.PATROL,
            assigned_robots=["robot-001", "robot-002"],
            waypoints=[
                {"position": {"x": 0, "y": 0, "z": 0}, "waypoint_type": "start"},
                {"position": {"x": 100, "y": 0, "z": 0}, "waypoint_type": "scan"},
                {"position": {"x": 100, "y": 100, "z": 0}, "waypoint_type": "end"},
            ],
            priority=7,
        )

        assert mission is not None
        assert mission.name == "North Patrol"
        assert mission.mission_type == MissionType.PATROL
        assert len(mission.waypoints) == 3

    def test_start_mission(self):
        """Test starting mission."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner, MissionType, MissionStatus

        planner = MissionPlanner()
        mission = planner.create_mission(
            name="Start Test",
            mission_type=MissionType.SEARCH,
            assigned_robots=["robot-s1"],
            waypoints=[{"position": {"x": 0, "y": 0, "z": 0}, "waypoint_type": "start"}],
        )

        started = planner.start_mission(mission.mission_id)
        assert started is not None
        assert started.status == MissionStatus.IN_PROGRESS

    def test_pause_mission(self):
        """Test pausing mission."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner, MissionType, MissionStatus

        planner = MissionPlanner()
        mission = planner.create_mission("Pause Test", MissionType.PATROL, ["robot-p1"], [])
        planner.start_mission(mission.mission_id)

        paused = planner.pause_mission(mission.mission_id)
        assert paused is not None
        assert paused.status == MissionStatus.PAUSED

    def test_resume_mission(self):
        """Test resuming mission."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner, MissionType, MissionStatus

        planner = MissionPlanner()
        mission = planner.create_mission("Resume Test", MissionType.SURVEILLANCE, ["robot-r1"], [])
        planner.start_mission(mission.mission_id)
        planner.pause_mission(mission.mission_id)

        resumed = planner.resume_mission(mission.mission_id)
        assert resumed is not None
        assert resumed.status == MissionStatus.IN_PROGRESS

    def test_complete_waypoint(self):
        """Test completing waypoint."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner, MissionType

        planner = MissionPlanner()
        mission = planner.create_mission(
            "Waypoint Test",
            MissionType.PATROL,
            ["robot-w1"],
            [
                {"position": {"x": 0, "y": 0, "z": 0}, "waypoint_type": "start"},
                {"position": {"x": 50, "y": 0, "z": 0}, "waypoint_type": "scan"},
            ],
        )
        planner.start_mission(mission.mission_id)

        waypoint_id = mission.waypoints[0].waypoint_id
        updated = planner.complete_waypoint(mission.mission_id, waypoint_id)

        assert updated is not None
        assert updated.waypoints[0].is_completed is True

    def test_abort_mission(self):
        """Test aborting mission."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner, MissionType, MissionStatus

        planner = MissionPlanner()
        mission = planner.create_mission("Abort Test", MissionType.RESPOND, ["robot-a1"], [])
        planner.start_mission(mission.mission_id)

        aborted = planner.abort_mission(mission.mission_id, reason="Emergency override")
        assert aborted is not None
        assert aborted.status == MissionStatus.ABORTED

    def test_get_active_missions(self):
        """Test getting active missions."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner, MissionType

        planner = MissionPlanner()
        m1 = planner.create_mission("Active 1", MissionType.PATROL, ["robot-ac1"], [])
        m2 = planner.create_mission("Active 2", MissionType.SEARCH, ["robot-ac2"], [])

        planner.start_mission(m1.mission_id)
        planner.start_mission(m2.mission_id)

        active = planner.get_active_missions()
        assert len(active) >= 2

    def test_add_waypoint(self):
        """Test adding waypoint to mission."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner, MissionType

        planner = MissionPlanner()
        mission = planner.create_mission("Add WP Test", MissionType.PATROL, ["robot-aw1"], [])

        updated = planner.add_waypoint(
            mission.mission_id,
            position={"x": 100, "y": 100, "z": 0},
            waypoint_type="scan",
            duration_seconds=30,
        )

        assert updated is not None
        assert len(updated.waypoints) == 1

    def test_get_metrics(self):
        """Test getting mission planner metrics."""
        from backend.app.robotics.robotics_mission_engine import MissionPlanner

        planner = MissionPlanner()
        metrics = planner.get_metrics()

        assert "total_missions" in metrics
        assert "by_status" in metrics


class TestMissionAutoDispatcher:
    """Tests for MissionAutoDispatcher."""

    def test_create_rule(self):
        """Test creating dispatch rule."""
        from backend.app.robotics.robotics_mission_engine import MissionAutoDispatcher, DispatchTrigger

        dispatcher = MissionAutoDispatcher()
        rule = dispatcher.create_rule(
            name="Breach Response",
            trigger=DispatchTrigger.PERIMETER_BREACH,
            conditions={"severity": ["high", "critical"]},
            mission_template={
                "mission_type": "respond",
                "priority": 9,
                "waypoints": [],
            },
            priority=8,
        )

        assert rule is not None
        assert rule.name == "Breach Response"
        assert rule.trigger == DispatchTrigger.PERIMETER_BREACH

    def test_process_trigger(self):
        """Test processing trigger event."""
        from backend.app.robotics.robotics_mission_engine import MissionAutoDispatcher, DispatchTrigger, MissionPlanner

        planner = MissionPlanner()
        dispatcher = MissionAutoDispatcher(planner)

        dispatcher.create_rule(
            name="Motion Response",
            trigger=DispatchTrigger.MOTION_DETECTION,
            conditions={},
            mission_template={"mission_type": "investigate", "priority": 5},
            priority=5,
        )

        result = dispatcher.process_trigger(
            trigger=DispatchTrigger.MOTION_DETECTION,
            event_data={
                "position": {"x": 50, "y": 50, "z": 0},
                "confidence": 0.9,
            },
            available_robots=["robot-mt1", "robot-mt2"],
        )

        assert result is not None

    def test_enable_disable_rule(self):
        """Test enabling and disabling rules."""
        from backend.app.robotics.robotics_mission_engine import MissionAutoDispatcher, DispatchTrigger

        dispatcher = MissionAutoDispatcher()
        rule = dispatcher.create_rule(
            name="Toggle Test",
            trigger=DispatchTrigger.THERMAL_ANOMALY,
            conditions={},
            mission_template={},
            priority=3,
        )

        disabled = dispatcher.disable_rule(rule.rule_id)
        assert disabled.is_enabled is False

        enabled = dispatcher.enable_rule(rule.rule_id)
        assert enabled.is_enabled is True

    def test_get_dispatch_history(self):
        """Test getting dispatch history."""
        from backend.app.robotics.robotics_mission_engine import MissionAutoDispatcher

        dispatcher = MissionAutoDispatcher()
        history = dispatcher.get_dispatch_history(limit=10)

        assert isinstance(history, list)

    def test_get_metrics(self):
        """Test getting dispatcher metrics."""
        from backend.app.robotics.robotics_mission_engine import MissionAutoDispatcher

        dispatcher = MissionAutoDispatcher()
        metrics = dispatcher.get_metrics()

        assert "total_rules" in metrics
        assert "total_dispatches" in metrics


class TestRoboticsTimelineBuilder:
    """Tests for RoboticsTimelineBuilder."""

    def test_record_event(self):
        """Test recording timeline event."""
        from backend.app.robotics.robotics_mission_engine import RoboticsTimelineBuilder, TimelineEventType

        builder = RoboticsTimelineBuilder()
        event = builder.record_event(
            mission_id="mission-001",
            event_type=TimelineEventType.MISSION_STARTED,
            data={"robots": ["robot-001"]},
            robot_id="robot-001",
        )

        assert event is not None
        assert event.mission_id == "mission-001"
        assert event.event_type == TimelineEventType.MISSION_STARTED

    def test_get_timeline(self):
        """Test getting mission timeline."""
        from backend.app.robotics.robotics_mission_engine import RoboticsTimelineBuilder, TimelineEventType

        builder = RoboticsTimelineBuilder()
        builder.record_event("mission-tl-001", TimelineEventType.MISSION_STARTED, {})
        builder.record_event("mission-tl-001", TimelineEventType.WAYPOINT_REACHED, {"waypoint": 1})
        builder.record_event("mission-tl-001", TimelineEventType.WAYPOINT_REACHED, {"waypoint": 2})

        timeline = builder.get_timeline("mission-tl-001")
        assert len(timeline) == 3

    def test_get_events_in_range(self):
        """Test getting events in time range."""
        from backend.app.robotics.robotics_mission_engine import RoboticsTimelineBuilder, TimelineEventType

        builder = RoboticsTimelineBuilder()
        builder.record_event("mission-range-001", TimelineEventType.MISSION_STARTED, {})

        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow() + timedelta(hours=1)

        events = builder.get_events_in_range(start_time, end_time)
        assert len(events) >= 1

    def test_get_replay_data(self):
        """Test getting replay data."""
        from backend.app.robotics.robotics_mission_engine import RoboticsTimelineBuilder, TimelineEventType

        builder = RoboticsTimelineBuilder()
        builder.record_event("mission-replay-001", TimelineEventType.MISSION_STARTED, {})
        builder.record_event("mission-replay-001", TimelineEventType.POSITION_UPDATE, {"x": 10, "y": 10})
        builder.record_event("mission-replay-001", TimelineEventType.POSITION_UPDATE, {"x": 20, "y": 20})

        replay = builder.get_replay_data("mission-replay-001")
        assert replay is not None
        assert "events" in replay

    def test_export_timeline(self):
        """Test exporting timeline."""
        from backend.app.robotics.robotics_mission_engine import RoboticsTimelineBuilder, TimelineEventType

        builder = RoboticsTimelineBuilder()
        builder.record_event("mission-export-001", TimelineEventType.MISSION_STARTED, {})

        exported = builder.export_timeline("mission-export-001", format="json")
        assert exported is not None


class TestStreamingEndpoints:
    """Tests for StreamingEndpoints."""

    def test_start_stream(self):
        """Test starting stream."""
        from backend.app.robotics.robotics_mission_engine import StreamingEndpoints

        streaming = StreamingEndpoints()
        session = streaming.start_stream(
            robot_id="robot-stream-001",
            stream_type="video",
            quality="720p",
        )

        assert session is not None
        assert session.robot_id == "robot-stream-001"
        assert session.stream_type == "video"

    def test_stop_stream(self):
        """Test stopping stream."""
        from backend.app.robotics.robotics_mission_engine import StreamingEndpoints

        streaming = StreamingEndpoints()
        session = streaming.start_stream("robot-stop-001", "video", "480p")

        stopped = streaming.stop_stream(session.session_id)
        assert stopped is not None
        assert stopped.status == "stopped"

    def test_add_viewer(self):
        """Test adding viewer to stream."""
        from backend.app.robotics.robotics_mission_engine import StreamingEndpoints

        streaming = StreamingEndpoints()
        session = streaming.start_stream("robot-viewer-001", "video", "1080p")

        updated = streaming.add_viewer(session.session_id, "viewer-001")
        assert updated is not None
        assert "viewer-001" in updated.viewers

    def test_remove_viewer(self):
        """Test removing viewer from stream."""
        from backend.app.robotics.robotics_mission_engine import StreamingEndpoints

        streaming = StreamingEndpoints()
        session = streaming.start_stream("robot-rmviewer-001", "video", "720p")
        streaming.add_viewer(session.session_id, "viewer-rm-001")

        updated = streaming.remove_viewer(session.session_id, "viewer-rm-001")
        assert updated is not None
        assert "viewer-rm-001" not in updated.viewers

    def test_get_robot_stream(self):
        """Test getting robot's active stream."""
        from backend.app.robotics.robotics_mission_engine import StreamingEndpoints

        streaming = StreamingEndpoints()
        streaming.start_stream("robot-getstream-001", "video", "720p")

        stream = streaming.get_robot_stream("robot-getstream-001")
        assert stream is not None
        assert stream.robot_id == "robot-getstream-001"

    def test_get_stream_url(self):
        """Test getting stream URL."""
        from backend.app.robotics.robotics_mission_engine import StreamingEndpoints

        streaming = StreamingEndpoints()
        session = streaming.start_stream("robot-url-001", "video", "720p")

        url = streaming.get_stream_url(session.session_id)
        assert url is not None
        assert "rtsp://" in url or "http://" in url

    def test_get_metrics(self):
        """Test getting streaming metrics."""
        from backend.app.robotics.robotics_mission_engine import StreamingEndpoints

        streaming = StreamingEndpoints()
        metrics = streaming.get_metrics()

        assert "active_sessions" in metrics
        assert "total_viewers" in metrics

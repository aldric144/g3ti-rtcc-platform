"""
Time Travel Engine.

Provides historical playback and time-scrubbing capabilities for the digital twin.
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class PlaybackState(str, Enum):
    """Playback state for time travel."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    REWINDING = "rewinding"
    FAST_FORWARD = "fast_forward"


class SnapshotType(str, Enum):
    """Types of historical snapshots."""
    FULL = "full"
    INCREMENTAL = "incremental"
    ENTITY_ONLY = "entity_only"
    INCIDENT_ONLY = "incident_only"


class EntitySnapshot(BaseModel):
    """Snapshot of an entity at a point in time."""
    entity_id: str
    entity_type: str
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    heading_deg: Optional[float] = None
    speed_kmh: Optional[float] = None
    status: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class IncidentSnapshot(BaseModel):
    """Snapshot of an incident at a point in time."""
    incident_id: str
    incident_type: str
    status: str
    latitude: float
    longitude: float
    severity: str
    assigned_units: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OverlaySnapshot(BaseModel):
    """Snapshot of overlays at a point in time."""
    weather: Optional[dict[str, Any]] = None
    traffic: Optional[dict[str, Any]] = None
    active_perimeters: list[dict[str, Any]] = Field(default_factory=list)
    active_zones: list[dict[str, Any]] = Field(default_factory=list)


class HistoricalSnapshot(BaseModel):
    """Complete snapshot of the digital twin at a point in time."""
    snapshot_id: str
    timestamp: datetime
    snapshot_type: SnapshotType = SnapshotType.FULL
    entities: list[EntitySnapshot] = Field(default_factory=list)
    incidents: list[IncidentSnapshot] = Field(default_factory=list)
    overlays: Optional[OverlaySnapshot] = None
    event_log: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TimelineEvent(BaseModel):
    """Event on the timeline."""
    event_id: str
    timestamp: datetime
    event_type: str
    title: str
    description: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    entity_id: Optional[str] = None
    incident_id: Optional[str] = None
    severity: str = "info"
    metadata: dict[str, Any] = Field(default_factory=dict)


class PlaybackSession(BaseModel):
    """Playback session for time travel."""
    session_id: str
    state: PlaybackState = PlaybackState.STOPPED
    start_time: datetime
    end_time: datetime
    current_time: datetime
    playback_speed: float = 1.0
    loop_enabled: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None


class TimeTravelConfig(BaseModel):
    """Configuration for time travel engine."""
    max_snapshots: int = 100000
    snapshot_interval_seconds: int = 60
    max_playback_speed: float = 100.0
    retention_days: int = 30
    max_timeline_events: int = 50000


class TimeTravelMetrics(BaseModel):
    """Metrics for time travel engine."""
    total_snapshots: int = 0
    snapshots_by_type: dict[str, int] = Field(default_factory=dict)
    total_timeline_events: int = 0
    active_sessions: int = 0
    oldest_snapshot: Optional[datetime] = None
    newest_snapshot: Optional[datetime] = None


class TimeTravelEngine:
    """
    Time Travel Engine.
    
    Provides historical playback and time-scrubbing capabilities for the digital twin.
    """
    
    def __init__(self, config: Optional[TimeTravelConfig] = None):
        self.config = config or TimeTravelConfig()
        self._snapshots: deque[HistoricalSnapshot] = deque(maxlen=self.config.max_snapshots)
        self._timeline_events: deque[TimelineEvent] = deque(maxlen=self.config.max_timeline_events)
        self._sessions: dict[str, PlaybackSession] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = TimeTravelMetrics()
    
    async def start(self) -> None:
        """Start the time travel engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the time travel engine."""
        self._running = False
    
    def capture_snapshot(
        self,
        entities: list[EntitySnapshot],
        incidents: Optional[list[IncidentSnapshot]] = None,
        overlays: Optional[OverlaySnapshot] = None,
        event_log: Optional[list[dict[str, Any]]] = None,
        snapshot_type: SnapshotType = SnapshotType.FULL,
        timestamp: Optional[datetime] = None,
    ) -> HistoricalSnapshot:
        """Capture a snapshot of the current state."""
        snapshot = HistoricalSnapshot(
            snapshot_id=f"snap-{uuid.uuid4().hex[:12]}",
            timestamp=timestamp or datetime.now(timezone.utc),
            snapshot_type=snapshot_type,
            entities=entities,
            incidents=incidents or [],
            overlays=overlays,
            event_log=event_log or [],
        )
        
        self._snapshots.append(snapshot)
        self._update_metrics()
        
        return snapshot
    
    def get_snapshot(self, snapshot_id: str) -> Optional[HistoricalSnapshot]:
        """Get a snapshot by ID."""
        for snapshot in self._snapshots:
            if snapshot.snapshot_id == snapshot_id:
                return snapshot
        return None
    
    def get_snapshot_at_time(self, target_time: datetime) -> Optional[HistoricalSnapshot]:
        """Get the snapshot closest to a specific time."""
        if not self._snapshots:
            return None
        
        closest = None
        min_diff = float("inf")
        
        for snapshot in self._snapshots:
            diff = abs((snapshot.timestamp - target_time).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest = snapshot
        
        return closest
    
    def get_snapshots_in_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> list[HistoricalSnapshot]:
        """Get all snapshots within a time range."""
        return [
            s for s in self._snapshots
            if start_time <= s.timestamp <= end_time
        ]
    
    def get_recent_snapshots(self, limit: int = 100) -> list[HistoricalSnapshot]:
        """Get recent snapshots."""
        snapshots = list(self._snapshots)
        snapshots.reverse()
        return snapshots[:limit]
    
    def add_timeline_event(
        self,
        event_type: str,
        title: str,
        description: str = "",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        entity_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        severity: str = "info",
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> TimelineEvent:
        """Add an event to the timeline."""
        event = TimelineEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            timestamp=timestamp or datetime.now(timezone.utc),
            event_type=event_type,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            entity_id=entity_id,
            incident_id=incident_id,
            severity=severity,
            metadata=metadata or {},
        )
        
        self._timeline_events.append(event)
        self._metrics.total_timeline_events = len(self._timeline_events)
        
        return event
    
    def get_timeline_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[TimelineEvent]:
        """Get timeline events with optional filters."""
        events = list(self._timeline_events)
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if entity_id:
            events = [e for e in events if e.entity_id == entity_id]
        
        if incident_id:
            events = [e for e in events if e.incident_id == incident_id]
        
        events.reverse()
        return events[:limit]
    
    def create_playback_session(
        self,
        start_time: datetime,
        end_time: datetime,
        user_id: Optional[str] = None,
    ) -> PlaybackSession:
        """Create a new playback session."""
        session = PlaybackSession(
            session_id=f"session-{uuid.uuid4().hex[:8]}",
            start_time=start_time,
            end_time=end_time,
            current_time=start_time,
            user_id=user_id,
        )
        
        self._sessions[session.session_id] = session
        self._metrics.active_sessions = len(self._sessions)
        
        return session
    
    def delete_playback_session(self, session_id: str) -> bool:
        """Delete a playback session."""
        if session_id not in self._sessions:
            return False
        
        del self._sessions[session_id]
        self._metrics.active_sessions = len(self._sessions)
        return True
    
    def get_playback_session(self, session_id: str) -> Optional[PlaybackSession]:
        """Get a playback session."""
        return self._sessions.get(session_id)
    
    def get_all_sessions(self) -> list[PlaybackSession]:
        """Get all playback sessions."""
        return list(self._sessions.values())
    
    async def play(self, session_id: str) -> bool:
        """Start playback for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.state = PlaybackState.PLAYING
        await self._notify_callbacks(session, "playback_started")
        return True
    
    async def pause(self, session_id: str) -> bool:
        """Pause playback for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.state = PlaybackState.PAUSED
        await self._notify_callbacks(session, "playback_paused")
        return True
    
    async def stop_playback(self, session_id: str) -> bool:
        """Stop playback for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.state = PlaybackState.STOPPED
        session.current_time = session.start_time
        await self._notify_callbacks(session, "playback_stopped")
        return True
    
    async def seek(
        self,
        session_id: str,
        target_time: datetime,
    ) -> Optional[HistoricalSnapshot]:
        """Seek to a specific time in the playback."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        if target_time < session.start_time:
            target_time = session.start_time
        elif target_time > session.end_time:
            target_time = session.end_time
        
        session.current_time = target_time
        
        snapshot = self.get_snapshot_at_time(target_time)
        
        await self._notify_callbacks(session, "playback_seek")
        
        return snapshot
    
    def set_playback_speed(
        self,
        session_id: str,
        speed: float,
    ) -> bool:
        """Set playback speed for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.playback_speed = min(speed, self.config.max_playback_speed)
        return True
    
    def set_loop_enabled(
        self,
        session_id: str,
        enabled: bool,
    ) -> bool:
        """Enable or disable loop for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.loop_enabled = enabled
        return True
    
    async def advance_playback(
        self,
        session_id: str,
        delta_seconds: float,
    ) -> Optional[HistoricalSnapshot]:
        """Advance playback by a time delta."""
        session = self._sessions.get(session_id)
        if not session or session.state != PlaybackState.PLAYING:
            return None
        
        new_time = session.current_time + timedelta(seconds=delta_seconds * session.playback_speed)
        
        if new_time > session.end_time:
            if session.loop_enabled:
                new_time = session.start_time
            else:
                new_time = session.end_time
                session.state = PlaybackState.STOPPED
        
        session.current_time = new_time
        
        return self.get_snapshot_at_time(new_time)
    
    def get_entity_track(
        self,
        entity_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[EntitySnapshot]:
        """Get the track (position history) for an entity."""
        track = []
        
        for snapshot in self._snapshots:
            if start_time <= snapshot.timestamp <= end_time:
                for entity in snapshot.entities:
                    if entity.entity_id == entity_id:
                        track.append(entity)
                        break
        
        return track
    
    def get_incident_timeline(
        self,
        incident_id: str,
    ) -> list[IncidentSnapshot]:
        """Get the timeline of an incident."""
        timeline = []
        
        for snapshot in self._snapshots:
            for incident in snapshot.incidents:
                if incident.incident_id == incident_id:
                    timeline.append(incident)
                    break
        
        return timeline
    
    def get_time_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """Get the available time range for playback."""
        if not self._snapshots:
            return None, None
        
        oldest = min(s.timestamp for s in self._snapshots)
        newest = max(s.timestamp for s in self._snapshots)
        
        return oldest, newest
    
    def cleanup_old_snapshots(self, retention_days: Optional[int] = None) -> int:
        """Remove snapshots older than retention period."""
        days = retention_days or self.config.retention_days
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        original_count = len(self._snapshots)
        
        self._snapshots = deque(
            [s for s in self._snapshots if s.timestamp >= cutoff],
            maxlen=self.config.max_snapshots,
        )
        
        removed = original_count - len(self._snapshots)
        self._update_metrics()
        
        return removed
    
    def export_session_data(
        self,
        session_id: str,
    ) -> Optional[dict[str, Any]]:
        """Export data for a playback session."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        snapshots = self.get_snapshots_in_range(session.start_time, session.end_time)
        events = self.get_timeline_events(
            start_time=session.start_time,
            end_time=session.end_time,
            limit=10000,
        )
        
        return {
            "session": session.model_dump(),
            "snapshots": [s.model_dump() for s in snapshots],
            "timeline_events": [e.model_dump() for e in events],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
    
    def get_metrics(self) -> TimeTravelMetrics:
        """Get time travel metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get time travel engine status."""
        oldest, newest = self.get_time_range()
        
        return {
            "running": self._running,
            "total_snapshots": len(self._snapshots),
            "total_timeline_events": len(self._timeline_events),
            "active_sessions": len(self._sessions),
            "oldest_snapshot": oldest.isoformat() if oldest else None,
            "newest_snapshot": newest.isoformat() if newest else None,
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for time travel events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update time travel metrics."""
        type_counts: dict[str, int] = {}
        
        for snapshot in self._snapshots:
            type_counts[snapshot.snapshot_type.value] = type_counts.get(snapshot.snapshot_type.value, 0) + 1
        
        oldest, newest = self.get_time_range()
        
        self._metrics.total_snapshots = len(self._snapshots)
        self._metrics.snapshots_by_type = type_counts
        self._metrics.total_timeline_events = len(self._timeline_events)
        self._metrics.active_sessions = len(self._sessions)
        self._metrics.oldest_snapshot = oldest
        self._metrics.newest_snapshot = newest
    
    async def _notify_callbacks(self, data: Any, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(data, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass

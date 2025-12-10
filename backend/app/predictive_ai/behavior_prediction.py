"""
Behavior Prediction Engine.

Predicts suspect behavior and movement trajectories based on patterns.
Note: This engine focuses on trajectory prediction only and does not use
racial, ethnic, or identity factors.
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class PredictionConfidence(str, Enum):
    """Confidence levels for predictions."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MovementType(str, Enum):
    """Types of movement patterns."""
    STATIONARY = "stationary"
    WALKING = "walking"
    RUNNING = "running"
    DRIVING = "driving"
    PUBLIC_TRANSIT = "public_transit"
    CYCLING = "cycling"
    ERRATIC = "erratic"
    UNKNOWN = "unknown"


class BehaviorType(str, Enum):
    """Types of behavioral patterns."""
    ROUTINE = "routine"
    EVASIVE = "evasive"
    SURVEILLANCE = "surveillance"
    LOITERING = "loitering"
    CASING = "casing"
    FLEEING = "fleeing"
    APPROACHING = "approaching"
    CIRCLING = "circling"
    UNKNOWN = "unknown"


class LocationPoint(BaseModel):
    """Location point for tracking."""
    point_id: str
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    timestamp: datetime
    accuracy_m: float = 10.0
    speed_kmh: Optional[float] = None
    heading_deg: Optional[float] = None
    source: str = "gps"


class MovementPattern(BaseModel):
    """Detected movement pattern."""
    pattern_id: str
    subject_id: str
    movement_type: MovementType
    behavior_type: BehaviorType = BehaviorType.UNKNOWN
    start_time: datetime
    end_time: Optional[datetime] = None
    start_location: LocationPoint
    end_location: Optional[LocationPoint] = None
    avg_speed_kmh: float = 0.0
    max_speed_kmh: float = 0.0
    total_distance_m: float = 0.0
    direction_deg: Optional[float] = None
    waypoints: list[LocationPoint] = Field(default_factory=list)
    confidence: PredictionConfidence = PredictionConfidence.MEDIUM
    anomaly_score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrajectoryPrediction(BaseModel):
    """Predicted trajectory for a subject."""
    prediction_id: str
    subject_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prediction_horizon_minutes: int = 30
    current_location: LocationPoint
    predicted_locations: list[dict[str, Any]] = Field(default_factory=list)
    predicted_destination: Optional[dict[str, Any]] = None
    movement_type: MovementType
    behavior_type: BehaviorType
    confidence: PredictionConfidence
    confidence_score: float = 0.0
    factors: list[str] = Field(default_factory=list)
    alternative_trajectories: list[dict[str, Any]] = Field(default_factory=list)
    verified: bool = False
    verified_at: Optional[datetime] = None
    actual_location: Optional[LocationPoint] = None
    prediction_error_m: Optional[float] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Subject(BaseModel):
    """Subject being tracked for behavior prediction."""
    subject_id: str
    subject_type: str = "person"
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_location: Optional[LocationPoint] = None
    location_history: list[LocationPoint] = Field(default_factory=list)
    movement_patterns: list[str] = Field(default_factory=list)
    known_locations: list[dict[str, Any]] = Field(default_factory=list)
    typical_routes: list[dict[str, Any]] = Field(default_factory=list)
    active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class PredictionConfig(BaseModel):
    """Configuration for behavior prediction engine."""
    max_subjects: int = 10000
    max_location_history: int = 1000
    max_predictions: int = 50000
    prediction_horizon_minutes: int = 30
    min_points_for_pattern: int = 3
    speed_thresholds: dict[str, float] = Field(default_factory=lambda: {
        "stationary": 0.5,
        "walking": 7.0,
        "running": 20.0,
        "cycling": 35.0,
        "driving": 200.0,
    })


class PredictionMetrics(BaseModel):
    """Metrics for behavior prediction engine."""
    total_subjects: int = 0
    active_subjects: int = 0
    total_patterns: int = 0
    patterns_by_type: dict[str, int] = Field(default_factory=dict)
    total_predictions: int = 0
    prediction_accuracy: float = 0.0
    avg_prediction_error_m: float = 0.0


class BehaviorPredictionEngine:
    """
    Behavior Prediction Engine.
    
    Predicts suspect behavior and movement trajectories based on patterns.
    This engine focuses on trajectory prediction only and does not use
    racial, ethnic, or identity factors.
    """
    
    def __init__(self, config: Optional[PredictionConfig] = None):
        self.config = config or PredictionConfig()
        self._subjects: dict[str, Subject] = {}
        self._patterns: dict[str, MovementPattern] = {}
        self._predictions: deque[TrajectoryPrediction] = deque(maxlen=self.config.max_predictions)
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = PredictionMetrics()
    
    async def start(self) -> None:
        """Start the behavior prediction engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the behavior prediction engine."""
        self._running = False
    
    def register_subject(
        self,
        subject_id: str,
        subject_type: str = "person",
        initial_latitude: Optional[float] = None,
        initial_longitude: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Subject:
        """Register a subject for tracking."""
        current_location = None
        if initial_latitude is not None and initial_longitude is not None:
            current_location = LocationPoint(
                point_id=f"loc-{uuid.uuid4().hex[:8]}",
                latitude=initial_latitude,
                longitude=initial_longitude,
                timestamp=datetime.now(timezone.utc),
            )
        
        subject = Subject(
            subject_id=subject_id,
            subject_type=subject_type,
            current_location=current_location,
            metadata=metadata or {},
        )
        
        if current_location:
            subject.location_history.append(current_location)
        
        self._subjects[subject_id] = subject
        self._update_metrics()
        
        return subject
    
    def unregister_subject(self, subject_id: str) -> bool:
        """Unregister a subject."""
        if subject_id not in self._subjects:
            return False
        
        del self._subjects[subject_id]
        self._update_metrics()
        return True
    
    def get_subject(self, subject_id: str) -> Optional[Subject]:
        """Get a subject by ID."""
        return self._subjects.get(subject_id)
    
    def get_all_subjects(self) -> list[Subject]:
        """Get all subjects."""
        return list(self._subjects.values())
    
    def get_active_subjects(self) -> list[Subject]:
        """Get all active subjects."""
        return [s for s in self._subjects.values() if s.active]
    
    async def update_location(
        self,
        subject_id: str,
        latitude: float,
        longitude: float,
        altitude_m: float = 0.0,
        speed_kmh: Optional[float] = None,
        heading_deg: Optional[float] = None,
        accuracy_m: float = 10.0,
        source: str = "gps",
    ) -> Optional[Subject]:
        """Update subject location."""
        subject = self._subjects.get(subject_id)
        if not subject:
            return None
        
        location = LocationPoint(
            point_id=f"loc-{uuid.uuid4().hex[:8]}",
            latitude=latitude,
            longitude=longitude,
            altitude_m=altitude_m,
            timestamp=datetime.now(timezone.utc),
            accuracy_m=accuracy_m,
            speed_kmh=speed_kmh,
            heading_deg=heading_deg,
            source=source,
        )
        
        subject.current_location = location
        subject.last_seen = location.timestamp
        subject.location_history.append(location)
        
        if len(subject.location_history) > self.config.max_location_history:
            subject.location_history = subject.location_history[-self.config.max_location_history:]
        
        if len(subject.location_history) >= self.config.min_points_for_pattern:
            await self._analyze_movement(subject)
        
        await self._notify_callbacks(subject, "location_updated")
        
        return subject
    
    async def _analyze_movement(self, subject: Subject) -> Optional[MovementPattern]:
        """Analyze movement pattern from recent locations."""
        recent = subject.location_history[-self.config.min_points_for_pattern:]
        
        if len(recent) < 2:
            return None
        
        total_distance = 0.0
        speeds = []
        
        for i in range(len(recent) - 1):
            dist = self._calculate_distance(
                recent[i].latitude, recent[i].longitude,
                recent[i + 1].latitude, recent[i + 1].longitude,
            ) * 1000
            total_distance += dist
            
            time_diff = (recent[i + 1].timestamp - recent[i].timestamp).total_seconds()
            if time_diff > 0:
                speed = (dist / 1000) / (time_diff / 3600)
                speeds.append(speed)
        
        avg_speed = sum(speeds) / len(speeds) if speeds else 0.0
        max_speed = max(speeds) if speeds else 0.0
        
        movement_type = self._classify_movement(avg_speed)
        behavior_type = self._classify_behavior(recent, avg_speed)
        
        direction = None
        if len(recent) >= 2:
            direction = self._calculate_bearing(
                recent[0].latitude, recent[0].longitude,
                recent[-1].latitude, recent[-1].longitude,
            )
        
        pattern = MovementPattern(
            pattern_id=f"pattern-{uuid.uuid4().hex[:12]}",
            subject_id=subject.subject_id,
            movement_type=movement_type,
            behavior_type=behavior_type,
            start_time=recent[0].timestamp,
            end_time=recent[-1].timestamp,
            start_location=recent[0],
            end_location=recent[-1],
            avg_speed_kmh=avg_speed,
            max_speed_kmh=max_speed,
            total_distance_m=total_distance,
            direction_deg=direction,
            waypoints=recent,
            confidence=self._calculate_pattern_confidence(recent),
        )
        
        self._patterns[pattern.pattern_id] = pattern
        subject.movement_patterns.append(pattern.pattern_id)
        
        self._update_metrics()
        
        return pattern
    
    def _classify_movement(self, speed_kmh: float) -> MovementType:
        """Classify movement type based on speed."""
        thresholds = self.config.speed_thresholds
        
        if speed_kmh < thresholds["stationary"]:
            return MovementType.STATIONARY
        if speed_kmh < thresholds["walking"]:
            return MovementType.WALKING
        if speed_kmh < thresholds["running"]:
            return MovementType.RUNNING
        if speed_kmh < thresholds["cycling"]:
            return MovementType.CYCLING
        if speed_kmh < thresholds["driving"]:
            return MovementType.DRIVING
        
        return MovementType.UNKNOWN
    
    def _classify_behavior(
        self,
        locations: list[LocationPoint],
        avg_speed: float,
    ) -> BehaviorType:
        """Classify behavior type based on movement pattern."""
        if len(locations) < 3:
            return BehaviorType.UNKNOWN
        
        if avg_speed < 0.5:
            return BehaviorType.LOITERING
        
        start = locations[0]
        end = locations[-1]
        direct_distance = self._calculate_distance(
            start.latitude, start.longitude,
            end.latitude, end.longitude,
        ) * 1000
        
        total_distance = 0.0
        for i in range(len(locations) - 1):
            total_distance += self._calculate_distance(
                locations[i].latitude, locations[i].longitude,
                locations[i + 1].latitude, locations[i + 1].longitude,
            ) * 1000
        
        if total_distance > 0 and direct_distance / total_distance < 0.3:
            return BehaviorType.CIRCLING
        
        if avg_speed > 30:
            return BehaviorType.FLEEING
        
        return BehaviorType.ROUTINE
    
    def _calculate_pattern_confidence(
        self,
        locations: list[LocationPoint],
    ) -> PredictionConfidence:
        """Calculate confidence level for a pattern."""
        if len(locations) < 3:
            return PredictionConfidence.VERY_LOW
        if len(locations) < 5:
            return PredictionConfidence.LOW
        if len(locations) < 10:
            return PredictionConfidence.MEDIUM
        if len(locations) < 20:
            return PredictionConfidence.HIGH
        return PredictionConfidence.VERY_HIGH
    
    async def predict_trajectory(
        self,
        subject_id: str,
        horizon_minutes: Optional[int] = None,
    ) -> Optional[TrajectoryPrediction]:
        """Predict future trajectory for a subject."""
        subject = self._subjects.get(subject_id)
        if not subject or not subject.current_location:
            return None
        
        if len(subject.location_history) < self.config.min_points_for_pattern:
            return None
        
        horizon = horizon_minutes or self.config.prediction_horizon_minutes
        
        recent = subject.location_history[-10:]
        
        avg_speed = 0.0
        avg_heading = 0.0
        
        if len(recent) >= 2:
            speeds = []
            headings = []
            
            for i in range(len(recent) - 1):
                dist = self._calculate_distance(
                    recent[i].latitude, recent[i].longitude,
                    recent[i + 1].latitude, recent[i + 1].longitude,
                ) * 1000
                
                time_diff = (recent[i + 1].timestamp - recent[i].timestamp).total_seconds()
                if time_diff > 0:
                    speed = (dist / 1000) / (time_diff / 3600)
                    speeds.append(speed)
                
                heading = self._calculate_bearing(
                    recent[i].latitude, recent[i].longitude,
                    recent[i + 1].latitude, recent[i + 1].longitude,
                )
                headings.append(heading)
            
            avg_speed = sum(speeds) / len(speeds) if speeds else 0.0
            avg_heading = sum(headings) / len(headings) if headings else 0.0
        
        movement_type = self._classify_movement(avg_speed)
        behavior_type = self._classify_behavior(recent, avg_speed)
        
        predicted_locations = []
        current_lat = subject.current_location.latitude
        current_lon = subject.current_location.longitude
        
        for minutes in range(5, horizon + 1, 5):
            distance_km = (avg_speed * minutes) / 60
            
            new_lat, new_lon = self._project_location(
                current_lat, current_lon,
                avg_heading, distance_km,
            )
            
            predicted_locations.append({
                "minutes_ahead": minutes,
                "latitude": new_lat,
                "longitude": new_lon,
                "confidence": max(0.3, 1.0 - (minutes / horizon) * 0.5),
            })
        
        confidence_score = self._calculate_prediction_confidence(subject, recent)
        confidence = self._score_to_confidence(confidence_score)
        
        prediction = TrajectoryPrediction(
            prediction_id=f"pred-{uuid.uuid4().hex[:12]}",
            subject_id=subject_id,
            prediction_horizon_minutes=horizon,
            current_location=subject.current_location,
            predicted_locations=predicted_locations,
            movement_type=movement_type,
            behavior_type=behavior_type,
            confidence=confidence,
            confidence_score=confidence_score,
            factors=[
                f"Based on {len(recent)} recent locations",
                f"Average speed: {avg_speed:.1f} km/h",
                f"Movement type: {movement_type.value}",
            ],
        )
        
        self._predictions.append(prediction)
        self._update_metrics()
        
        await self._notify_callbacks(prediction, "trajectory_predicted")
        
        return prediction
    
    def _calculate_prediction_confidence(
        self,
        subject: Subject,
        recent_locations: list[LocationPoint],
    ) -> float:
        """Calculate confidence score for prediction."""
        score = 0.0
        
        location_score = min(len(recent_locations) / 10, 1.0) * 0.3
        score += location_score
        
        if len(recent_locations) >= 2:
            time_span = (recent_locations[-1].timestamp - recent_locations[0].timestamp).total_seconds()
            recency_score = min(time_span / 3600, 1.0) * 0.2
            score += recency_score
        
        pattern_score = min(len(subject.movement_patterns) / 5, 1.0) * 0.2
        score += pattern_score
        
        if subject.known_locations:
            score += 0.15
        
        if subject.typical_routes:
            score += 0.15
        
        return min(score, 1.0)
    
    def _score_to_confidence(self, score: float) -> PredictionConfidence:
        """Convert confidence score to confidence level."""
        if score >= 0.8:
            return PredictionConfidence.VERY_HIGH
        if score >= 0.6:
            return PredictionConfidence.HIGH
        if score >= 0.4:
            return PredictionConfidence.MEDIUM
        if score >= 0.2:
            return PredictionConfidence.LOW
        return PredictionConfidence.VERY_LOW
    
    def _project_location(
        self,
        lat: float,
        lon: float,
        bearing_deg: float,
        distance_km: float,
    ) -> tuple[float, float]:
        """Project a location given bearing and distance."""
        import math
        
        R = 6371.0
        
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing_deg)
        
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance_km / R)
            + math.cos(lat_rad) * math.sin(distance_km / R) * math.cos(bearing_rad)
        )
        
        new_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance_km / R) * math.cos(lat_rad),
            math.cos(distance_km / R) - math.sin(lat_rad) * math.sin(new_lat_rad),
        )
        
        return math.degrees(new_lat_rad), math.degrees(new_lon_rad)
    
    def _calculate_bearing(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate bearing between two points."""
        import math
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (
            math.cos(lat1_rad) * math.sin(lat2_rad)
            - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
        )
        
        bearing = math.atan2(x, y)
        return (math.degrees(bearing) + 360) % 360
    
    def verify_prediction(
        self,
        prediction_id: str,
        actual_latitude: float,
        actual_longitude: float,
    ) -> Optional[TrajectoryPrediction]:
        """Verify a prediction with actual location."""
        for prediction in self._predictions:
            if prediction.prediction_id == prediction_id:
                prediction.verified = True
                prediction.verified_at = datetime.now(timezone.utc)
                
                prediction.actual_location = LocationPoint(
                    point_id=f"loc-{uuid.uuid4().hex[:8]}",
                    latitude=actual_latitude,
                    longitude=actual_longitude,
                    timestamp=datetime.now(timezone.utc),
                )
                
                if prediction.predicted_locations:
                    predicted = prediction.predicted_locations[-1]
                    error = self._calculate_distance(
                        predicted["latitude"], predicted["longitude"],
                        actual_latitude, actual_longitude,
                    ) * 1000
                    prediction.prediction_error_m = error
                
                self._update_metrics()
                return prediction
        
        return None
    
    def get_pattern(self, pattern_id: str) -> Optional[MovementPattern]:
        """Get a pattern by ID."""
        return self._patterns.get(pattern_id)
    
    def get_patterns_for_subject(self, subject_id: str) -> list[MovementPattern]:
        """Get all patterns for a subject."""
        subject = self._subjects.get(subject_id)
        if not subject:
            return []
        
        return [
            self._patterns[pid]
            for pid in subject.movement_patterns
            if pid in self._patterns
        ]
    
    def get_recent_predictions(self, limit: int = 100) -> list[TrajectoryPrediction]:
        """Get recent predictions."""
        predictions = list(self._predictions)
        predictions.reverse()
        return predictions[:limit]
    
    def get_predictions_for_subject(self, subject_id: str) -> list[TrajectoryPrediction]:
        """Get predictions for a subject."""
        return [p for p in self._predictions if p.subject_id == subject_id]
    
    def add_known_location(
        self,
        subject_id: str,
        name: str,
        latitude: float,
        longitude: float,
        location_type: str = "frequent",
    ) -> bool:
        """Add a known location for a subject."""
        subject = self._subjects.get(subject_id)
        if not subject:
            return False
        
        subject.known_locations.append({
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "type": location_type,
        })
        
        return True
    
    def add_typical_route(
        self,
        subject_id: str,
        name: str,
        waypoints: list[tuple[float, float]],
    ) -> bool:
        """Add a typical route for a subject."""
        subject = self._subjects.get(subject_id)
        if not subject:
            return False
        
        subject.typical_routes.append({
            "name": name,
            "waypoints": waypoints,
        })
        
        return True
    
    def deactivate_subject(self, subject_id: str) -> bool:
        """Deactivate a subject."""
        subject = self._subjects.get(subject_id)
        if not subject:
            return False
        
        subject.active = False
        self._update_metrics()
        return True
    
    def get_metrics(self) -> PredictionMetrics:
        """Get prediction metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        return {
            "running": self._running,
            "total_subjects": len(self._subjects),
            "active_subjects": len([s for s in self._subjects.values() if s.active]),
            "total_patterns": len(self._patterns),
            "total_predictions": len(self._predictions),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for prediction events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update prediction metrics."""
        pattern_counts: dict[str, int] = {}
        for pattern in self._patterns.values():
            pattern_counts[pattern.movement_type.value] = pattern_counts.get(pattern.movement_type.value, 0) + 1
        
        verified = [p for p in self._predictions if p.verified]
        if verified:
            accurate = len([p for p in verified if p.prediction_error_m and p.prediction_error_m < 500])
            accuracy = accurate / len(verified)
            avg_error = sum(p.prediction_error_m or 0 for p in verified) / len(verified)
        else:
            accuracy = 0.0
            avg_error = 0.0
        
        self._metrics.total_subjects = len(self._subjects)
        self._metrics.active_subjects = len([s for s in self._subjects.values() if s.active])
        self._metrics.total_patterns = len(self._patterns)
        self._metrics.patterns_by_type = pattern_counts
        self._metrics.total_predictions = len(self._predictions)
        self._metrics.prediction_accuracy = accuracy
        self._metrics.avg_prediction_error_m = avg_error
    
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
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        import math
        
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

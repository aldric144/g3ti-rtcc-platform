"""
Pattern Recognition Module.

This module provides pattern recognition and prediction capabilities for
identifying crime patterns, vehicle trajectories, and behavioral trends.
"""

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from app.ai_engine.models import (
    ConfidenceLevel,
    GeoLocation,
    PatternResult,
    PatternType,
    PredictionResult,
    TimeRange,
)
from app.ai_engine.pipelines import BasePredictor, PipelineContext
from app.core.logging import audit_logger, get_logger

logger = get_logger(__name__)


@dataclass
class TrajectoryPoint:
    """A point in a trajectory."""

    latitude: float
    longitude: float
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MarkovState:
    """State in a Markov chain model."""

    state_id: str
    transitions: dict[str, float] = field(default_factory=dict)
    visit_count: int = 0


class PatternPredictor(BasePredictor):
    """
    Main pattern predictor that identifies and predicts patterns.

    Capabilities:
    - Repeat offender pathway analysis
    - Vehicle trajectory prediction
    - Crime pattern heat forecasting
    - Gunfire recurrence mapping
    - Spatiotemporal modeling
    """

    def __init__(self) -> None:
        """Initialize the pattern predictor."""
        super().__init__("pattern_predictor")
        self._markov_models: dict[str, dict[str, MarkovState]] = {}
        self._trajectory_history: dict[str, list[TrajectoryPoint]] = defaultdict(list)
        self._pattern_cache: dict[str, PatternResult] = {}

    async def load_model(self) -> None:
        """Load prediction models."""
        self._model_loaded = True
        logger.info("pattern_predictor_models_loaded")

    async def predict(self, input_data: dict[str, Any], context: PipelineContext) -> dict[str, Any]:
        """
        Make predictions based on input data.

        Args:
            input_data: Input features for prediction
            context: Pipeline context

        Returns:
            Prediction results
        """
        prediction_type = input_data.get("type", "general")

        if prediction_type == "vehicle_trajectory":
            return await self._predict_vehicle_trajectory(input_data, context)
        elif prediction_type == "crime_heat":
            return await self._predict_crime_heat(input_data, context)
        elif prediction_type == "gunfire_recurrence":
            return await self._predict_gunfire_recurrence(input_data, context)
        elif prediction_type == "offender_pathway":
            return await self._predict_offender_pathway(input_data, context)
        else:
            return await self._predict_general(input_data, context)

    async def train(self, training_data: list[dict[str, Any]]) -> None:
        """
        Train models with new data.

        Args:
            training_data: Training data
        """
        for item in training_data:
            item_type = item.get("type") or item.get("event_type")

            if item_type == "vehicle_sighting":
                await self._update_trajectory_model(item)
            elif item_type == "incident":
                await self._update_crime_model(item)
            elif item_type == "gunfire":
                await self._update_gunfire_model(item)

        logger.info("pattern_predictor_trained", data_count=len(training_data))

    async def recognize_patterns(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[PatternResult]:
        """
        Recognize patterns in the provided data.

        Args:
            data: Data to analyze
            context: Pipeline context

        Returns:
            List of recognized patterns
        """
        logger.info(
            "recognizing_patterns",
            data_count=len(data),
            request_id=context.request_id,
        )

        patterns: list[PatternResult] = []

        repeat_offender_patterns = await self._find_repeat_offender_patterns(data, context)
        patterns.extend(repeat_offender_patterns)

        trajectory_patterns = await self._find_trajectory_patterns(data, context)
        patterns.extend(trajectory_patterns)

        temporal_patterns = await self._find_temporal_patterns(data, context)
        patterns.extend(temporal_patterns)

        geographic_patterns = await self._find_geographic_patterns(data, context)
        patterns.extend(geographic_patterns)

        audit_logger.log_system_event(
            event_type="pattern_recognition_completed",
            details={
                "request_id": context.request_id,
                "data_count": len(data),
                "patterns_found": len(patterns),
            },
        )

        return patterns

    async def _predict_vehicle_trajectory(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """Predict likely next location for a vehicle."""
        vehicle_id = input_data.get("vehicle_id") or input_data.get("plate_number")

        if not vehicle_id:
            return {"error": "Vehicle ID required"}

        history = self._trajectory_history.get(vehicle_id, [])

        if len(history) < 2:
            return {
                "prediction_id": str(uuid.uuid4()),
                "vehicle_id": vehicle_id,
                "confidence": "low",
                "message": "Insufficient trajectory history",
            }

        sorted_history = sorted(history, key=lambda x: x.timestamp)
        recent_points = sorted_history[-5:]

        if len(recent_points) >= 2:
            lat_velocity = recent_points[-1].latitude - recent_points[-2].latitude
            lon_velocity = recent_points[-1].longitude - recent_points[-2].longitude

            time_diff = (recent_points[-1].timestamp - recent_points[-2].timestamp).total_seconds()

            if time_diff > 0:
                prediction_time = timedelta(hours=1)
                scale = prediction_time.total_seconds() / time_diff

                predicted_lat = recent_points[-1].latitude + (lat_velocity * scale * 0.5)
                predicted_lon = recent_points[-1].longitude + (lon_velocity * scale * 0.5)

                prediction = PredictionResult(
                    prediction_id=str(uuid.uuid4()),
                    prediction_type="vehicle_trajectory",
                    description=f"Predicted location for vehicle {vehicle_id} in 1 hour",
                    confidence=ConfidenceLevel.MEDIUM,
                    probability=0.65,
                    target_entity=vehicle_id,
                    predicted_location=GeoLocation(
                        latitude=predicted_lat,
                        longitude=predicted_lon,
                    ),
                    predicted_time=datetime.utcnow() + prediction_time,
                    factors={
                        "trajectory_points": len(recent_points),
                        "lat_velocity": lat_velocity,
                        "lon_velocity": lon_velocity,
                    },
                    recommendations=[
                        "Monitor cameras in predicted area",
                        f"Alert if vehicle spotted near ({predicted_lat:.4f}, {predicted_lon:.4f})",
                    ],
                )

                return prediction.to_dict()

        return {
            "prediction_id": str(uuid.uuid4()),
            "vehicle_id": vehicle_id,
            "confidence": "uncertain",
            "message": "Unable to calculate trajectory",
        }

    async def _predict_crime_heat(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """Predict crime heat map for an area."""
        center_lat = input_data.get("latitude", 0)
        center_lon = input_data.get("longitude", 0)
        radius_km = input_data.get("radius_km", 5)
        hours_ahead = input_data.get("hours_ahead", 24)

        grid_size = 0.01
        heat_map: list[dict[str, Any]] = []

        for lat_offset in range(-5, 6):
            for lon_offset in range(-5, 6):
                cell_lat = center_lat + (lat_offset * grid_size)
                cell_lon = center_lon + (lon_offset * grid_size)

                base_risk = 0.3
                distance_from_center = math.sqrt(lat_offset**2 + lon_offset**2)
                distance_factor = max(0, 1 - (distance_from_center / 7))

                current_hour = datetime.utcnow().hour
                time_factor = 1.0
                if 22 <= current_hour or current_hour <= 4:
                    time_factor = 1.3
                elif 14 <= current_hour <= 20:
                    time_factor = 1.2

                risk_score = base_risk * distance_factor * time_factor

                heat_map.append(
                    {
                        "latitude": cell_lat,
                        "longitude": cell_lon,
                        "risk_score": min(1.0, risk_score),
                        "risk_level": (
                            "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
                        ),
                    }
                )

        return {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "crime_heat",
            "center": {"latitude": center_lat, "longitude": center_lon},
            "radius_km": radius_km,
            "hours_ahead": hours_ahead,
            "heat_map": heat_map,
            "generated_at": datetime.utcnow().isoformat(),
            "confidence": "medium",
        }

    async def _predict_gunfire_recurrence(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """Predict gunfire recurrence probability."""
        location = input_data.get("location", {})
        lat = location.get("latitude", 0)
        lon = location.get("longitude", 0)
        historical_events = input_data.get("historical_events", [])

        if not historical_events:
            base_probability = 0.1
        else:
            recent_count = len(
                [e for e in historical_events if self._is_recent(e.get("timestamp"), days=30)]
            )
            base_probability = min(0.9, 0.1 + (recent_count * 0.1))

        current_hour = datetime.utcnow().hour
        time_multiplier = 1.0
        if 22 <= current_hour or current_hour <= 4:
            time_multiplier = 1.5
        elif 18 <= current_hour <= 22:
            time_multiplier = 1.3

        final_probability = min(1.0, base_probability * time_multiplier)

        prediction = PredictionResult(
            prediction_id=str(uuid.uuid4()),
            prediction_type="gunfire_recurrence",
            description="Gunfire recurrence probability at location",
            confidence=(
                ConfidenceLevel.HIGH
                if len(historical_events) > 10
                else ConfidenceLevel.MEDIUM if len(historical_events) > 3 else ConfidenceLevel.LOW
            ),
            probability=final_probability,
            predicted_location=GeoLocation(latitude=lat, longitude=lon) if lat and lon else None,
            factors={
                "historical_events": len(historical_events),
                "recent_events_30d": len(
                    [e for e in historical_events if self._is_recent(e.get("timestamp"), days=30)]
                ),
                "time_multiplier": time_multiplier,
            },
            recommendations=[
                "Increase patrol presence in area" if final_probability > 0.5 else "Monitor area",
                "Deploy ShotSpotter resources" if final_probability > 0.7 else "",
            ],
        )

        return prediction.to_dict()

    async def _predict_offender_pathway(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """Predict likely pathway for a repeat offender."""
        offender_id = input_data.get("offender_id") or input_data.get("person_id")
        history = input_data.get("history", [])

        if not offender_id:
            return {"error": "Offender ID required"}

        if len(history) < 2:
            return {
                "prediction_id": str(uuid.uuid4()),
                "offender_id": offender_id,
                "confidence": "low",
                "message": "Insufficient history for pathway prediction",
            }

        locations = [
            (h.get("latitude"), h.get("longitude"))
            for h in history
            if h.get("latitude") and h.get("longitude")
        ]

        if len(locations) >= 2:
            center_lat = sum(loc[0] for loc in locations) / len(locations)
            center_lon = sum(loc[1] for loc in locations) / len(locations)

            crime_types = [h.get("crime_type") or h.get("type") for h in history]
            type_counts: dict[str, int] = defaultdict(int)
            for ct in crime_types:
                if ct:
                    type_counts[ct] += 1

            most_common_type = (
                max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "unknown"
            )

            prediction = PredictionResult(
                prediction_id=str(uuid.uuid4()),
                prediction_type="offender_pathway",
                description=f"Predicted activity area for offender {offender_id}",
                confidence=ConfidenceLevel.MEDIUM,
                probability=0.6,
                target_entity=offender_id,
                predicted_location=GeoLocation(
                    latitude=center_lat,
                    longitude=center_lon,
                ),
                factors={
                    "history_count": len(history),
                    "location_count": len(locations),
                    "primary_crime_type": most_common_type,
                    "crime_type_distribution": dict(type_counts),
                },
                recommendations=[
                    f"Monitor area around ({center_lat:.4f}, {center_lon:.4f})",
                    f"Focus on {most_common_type} prevention",
                    "Coordinate with patrol units in predicted area",
                ],
            )

            return prediction.to_dict()

        return {
            "prediction_id": str(uuid.uuid4()),
            "offender_id": offender_id,
            "confidence": "uncertain",
            "message": "Insufficient location data",
        }

    async def _predict_general(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """General prediction fallback."""
        return {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "general",
            "message": "Specify prediction type: vehicle_trajectory, crime_heat, gunfire_recurrence, or offender_pathway",
            "available_types": [
                "vehicle_trajectory",
                "crime_heat",
                "gunfire_recurrence",
                "offender_pathway",
            ],
        }

    async def _find_repeat_offender_patterns(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[PatternResult]:
        """Find patterns in repeat offender behavior."""
        patterns = []

        person_incidents: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in data:
            person_id = item.get("person_id") or item.get("suspect_id") or item.get("offender_id")
            if person_id and item.get("incident_type"):
                person_incidents[person_id].append(item)

        for person_id, incidents in person_incidents.items():
            if len(incidents) >= 3:
                crime_types = [i.get("incident_type") or i.get("crime_type") for i in incidents]
                type_counts: dict[str, int] = defaultdict(int)
                for ct in crime_types:
                    if ct:
                        type_counts[ct] += 1

                if type_counts:
                    primary_type = max(type_counts.items(), key=lambda x: x[1])

                    if primary_type[1] >= 2:
                        locations = [
                            GeoLocation(
                                latitude=float(i.get("latitude", 0)),
                                longitude=float(i.get("longitude", 0)),
                            )
                            for i in incidents
                            if i.get("latitude") and i.get("longitude")
                        ]

                        pattern = PatternResult(
                            pattern_id=str(uuid.uuid4()),
                            pattern_type=PatternType.REPEAT_OFFENDER,
                            description=f"Repeat offender pattern: {person_id} with {len(incidents)} incidents, primarily {primary_type[0]}",
                            confidence=min(0.9, 0.5 + (len(incidents) * 0.1)),
                            entities=[person_id],
                            locations=locations[:5],
                            frequency=len(incidents),
                            strength=primary_type[1] / len(incidents),
                            metadata={
                                "incident_count": len(incidents),
                                "primary_crime_type": primary_type[0],
                                "crime_type_distribution": dict(type_counts),
                            },
                        )
                        patterns.append(pattern)

        return patterns

    async def _find_trajectory_patterns(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[PatternResult]:
        """Find patterns in vehicle trajectories."""
        patterns = []

        vehicle_sightings: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in data:
            if item.get("source") == "flock" or item.get("event_type") == "lpr_read":
                plate = item.get("plate_number") or item.get("plate")
                if plate:
                    vehicle_sightings[plate].append(item)

        for plate, sightings in vehicle_sightings.items():
            if len(sightings) >= 5:
                sorted_sightings = sorted(
                    sightings,
                    key=lambda x: x.get("timestamp") or x.get("created_at") or "",
                )

                locations = [
                    GeoLocation(
                        latitude=float(s.get("latitude", 0)),
                        longitude=float(s.get("longitude", 0)),
                    )
                    for s in sorted_sightings
                    if s.get("latitude") and s.get("longitude")
                ]

                if len(locations) >= 3:
                    first_time = sorted_sightings[0].get("timestamp")
                    last_time = sorted_sightings[-1].get("timestamp")

                    if isinstance(first_time, str):
                        first_time = datetime.fromisoformat(first_time.replace("Z", "+00:00"))
                    if isinstance(last_time, str):
                        last_time = datetime.fromisoformat(last_time.replace("Z", "+00:00"))

                    time_range = None
                    if first_time and last_time:
                        time_range = TimeRange(start=first_time, end=last_time)

                    pattern = PatternResult(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type=PatternType.VEHICLE_TRAJECTORY,
                        description=f"Vehicle trajectory pattern for {plate}: {len(sightings)} sightings",
                        confidence=min(0.85, 0.4 + (len(sightings) * 0.05)),
                        entities=[plate],
                        locations=locations[:10],
                        time_range=time_range,
                        frequency=len(sightings),
                        metadata={
                            "sighting_count": len(sightings),
                            "unique_locations": len(
                                set((l.latitude, l.longitude) for l in locations)
                            ),
                        },
                    )
                    patterns.append(pattern)

        return patterns

    async def _find_temporal_patterns(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[PatternResult]:
        """Find temporal patterns in events."""
        patterns = []

        hourly_counts: dict[int, list[dict[str, Any]]] = defaultdict(list)
        daily_counts: dict[int, list[dict[str, Any]]] = defaultdict(list)

        for item in data:
            timestamp = item.get("timestamp") or item.get("created_at")
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    except ValueError:
                        continue

                hourly_counts[timestamp.hour].append(item)
                daily_counts[timestamp.weekday()].append(item)

        if hourly_counts:
            peak_hour = max(hourly_counts.items(), key=lambda x: len(x[1]))
            if len(peak_hour[1]) >= 5:
                pattern = PatternResult(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.TEMPORAL_PATTERN,
                    description=f"Peak activity at hour {peak_hour[0]:02d}:00 with {len(peak_hour[1])} events",
                    confidence=0.75,
                    frequency=len(peak_hour[1]),
                    metadata={
                        "peak_hour": peak_hour[0],
                        "event_count": len(peak_hour[1]),
                        "hourly_distribution": {
                            h: len(events) for h, events in hourly_counts.items()
                        },
                    },
                )
                patterns.append(pattern)

        if daily_counts:
            peak_day = max(daily_counts.items(), key=lambda x: len(x[1]))
            day_names = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            if len(peak_day[1]) >= 5:
                pattern = PatternResult(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.TEMPORAL_PATTERN,
                    description=f"Peak activity on {day_names[peak_day[0]]} with {len(peak_day[1])} events",
                    confidence=0.7,
                    frequency=len(peak_day[1]),
                    metadata={
                        "peak_day": day_names[peak_day[0]],
                        "peak_day_index": peak_day[0],
                        "event_count": len(peak_day[1]),
                        "daily_distribution": {
                            day_names[d]: len(events) for d, events in daily_counts.items()
                        },
                    },
                )
                patterns.append(pattern)

        return patterns

    async def _find_geographic_patterns(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[PatternResult]:
        """Find geographic clustering patterns."""
        patterns = []

        events_with_location = [d for d in data if d.get("latitude") and d.get("longitude")]

        if len(events_with_location) < 5:
            return patterns

        grid_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for event in events_with_location:
            lat = float(event.get("latitude", 0))
            lon = float(event.get("longitude", 0))
            grid_key = f"{lat:.2f},{lon:.2f}"
            grid_events[grid_key].append(event)

        for grid_key, events in grid_events.items():
            if len(events) >= 5:
                lat, lon = map(float, grid_key.split(","))

                pattern = PatternResult(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.GEOGRAPHIC_CLUSTER,
                    description=f"Geographic cluster with {len(events)} events",
                    confidence=min(0.85, 0.5 + (len(events) * 0.05)),
                    locations=[GeoLocation(latitude=lat, longitude=lon)],
                    frequency=len(events),
                    strength=len(events) / len(events_with_location),
                    metadata={
                        "event_count": len(events),
                        "grid_key": grid_key,
                        "event_types": list(
                            set(e.get("event_type") or e.get("type") or "unknown" for e in events)
                        ),
                    },
                )
                patterns.append(pattern)

        return patterns

    async def _update_trajectory_model(self, item: dict[str, Any]) -> None:
        """Update trajectory model with new vehicle sighting."""
        vehicle_id = item.get("plate_number") or item.get("vehicle_id")
        if not vehicle_id:
            return

        lat = item.get("latitude")
        lon = item.get("longitude")
        timestamp = item.get("timestamp") or item.get("created_at")

        if lat and lon and timestamp:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            point = TrajectoryPoint(
                latitude=float(lat),
                longitude=float(lon),
                timestamp=timestamp,
                metadata=item,
            )
            self._trajectory_history[vehicle_id].append(point)

            if len(self._trajectory_history[vehicle_id]) > 100:
                self._trajectory_history[vehicle_id] = self._trajectory_history[vehicle_id][-100:]

    async def _update_crime_model(self, item: dict[str, Any]) -> None:
        """Update crime pattern model with new incident."""
        pass

    async def _update_gunfire_model(self, item: dict[str, Any]) -> None:
        """Update gunfire recurrence model with new event."""
        pass

    def _is_recent(self, timestamp: Any, days: int = 30) -> bool:
        """Check if a timestamp is within the specified number of days."""
        if not timestamp:
            return False

        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                return False

        cutoff = datetime.utcnow() - timedelta(days=days)
        if timestamp.tzinfo:
            cutoff = cutoff.replace(tzinfo=timestamp.tzinfo)

        return timestamp >= cutoff


async def get_patterns(
    data: list[dict[str, Any]],
    pattern_type: str | None = None,
    context: PipelineContext | None = None,
) -> list[dict[str, Any]]:
    """
    Get patterns from data.

    Args:
        data: Data to analyze
        pattern_type: Optional filter for pattern type
        context: Pipeline context

    Returns:
        List of recognized patterns
    """
    if context is None:
        context = PipelineContext(request_id=str(uuid.uuid4()))

    predictor = PatternPredictor()
    await predictor.load_model()

    patterns = await predictor.recognize_patterns(data, context)

    if pattern_type:
        patterns = [p for p in patterns if p.pattern_type.value == pattern_type]

    return [p.to_dict() for p in patterns]


__all__ = [
    "PatternPredictor",
    "TrajectoryPoint",
    "MarkovState",
    "get_patterns",
]

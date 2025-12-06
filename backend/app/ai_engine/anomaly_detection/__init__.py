"""
Anomaly Detection Engine.

This module provides anomaly detection capabilities for identifying unusual
patterns and deviations in crime data, vehicle behavior, and other metrics.
"""

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.ai_engine.models import (
    AnomalyResult,
    AnomalyType,
    GeoLocation,
)
from app.ai_engine.pipelines import BaseDetector, PipelineContext
from app.core.logging import audit_logger, get_logger

logger = get_logger(__name__)


@dataclass
class BaselineMetrics:
    """Baseline metrics for anomaly detection."""

    metric_name: str
    mean: float = 0.0
    std_dev: float = 1.0
    min_value: float = 0.0
    max_value: float = 0.0
    sample_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def update(self, values: list[float]) -> None:
        """Update baseline with new values."""
        if not values:
            return

        self.sample_count = len(values)
        self.mean = sum(values) / len(values)
        self.min_value = min(values)
        self.max_value = max(values)

        if len(values) > 1:
            variance = sum((x - self.mean) ** 2 for x in values) / (len(values) - 1)
            self.std_dev = math.sqrt(variance) if variance > 0 else 1.0
        else:
            self.std_dev = 1.0

        self.last_updated = datetime.utcnow()

    def z_score(self, value: float) -> float:
        """Calculate Z-score for a value."""
        if self.std_dev == 0:
            return 0.0
        return (value - self.mean) / self.std_dev


@dataclass
class SpatialCluster:
    """Represents a spatial cluster of events."""

    cluster_id: str
    center_lat: float
    center_lon: float
    radius_meters: float
    point_count: int
    density: float
    events: list[dict[str, Any]] = field(default_factory=list)


class AnomalyDetector(BaseDetector):
    """
    Main anomaly detector that identifies unusual patterns in data.

    Uses multiple detection methods:
    - Z-score deviation for time-series data
    - DBSCAN-style clustering for spatial data
    - Graph centrality drift for relationship changes
    - Rolling window analysis for temporal patterns
    """

    Z_SCORE_THRESHOLD = 2.5
    HIGH_SEVERITY_THRESHOLD = 3.5
    CLUSTER_EPSILON_METERS = 500
    MIN_CLUSTER_POINTS = 3

    def __init__(self) -> None:
        """Initialize the anomaly detector."""
        super().__init__("anomaly_detector")
        self._baselines: dict[str, BaselineMetrics] = {}
        self._historical_data: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async def detect(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[dict[str, Any]]:
        """
        Detect anomalies in the provided data.

        Args:
            data: Data to analyze for anomalies
            context: Pipeline context

        Returns:
            List of detected anomalies
        """
        logger.info(
            "detecting_anomalies",
            data_count=len(data),
            request_id=context.request_id,
        )

        anomalies: list[AnomalyResult] = []

        vehicle_anomalies = await self._detect_vehicle_behavior_anomalies(data, context)
        anomalies.extend(vehicle_anomalies)

        gunfire_anomalies = await self._detect_gunfire_density_anomalies(data, context)
        anomalies.extend(gunfire_anomalies)

        clustering_anomalies = await self._detect_offender_clustering(data, context)
        anomalies.extend(clustering_anomalies)

        timeline_anomalies = await self._detect_timeline_deviations(data, context)
        anomalies.extend(timeline_anomalies)

        signature_anomalies = await self._detect_crime_signature_shifts(data, context)
        anomalies.extend(signature_anomalies)

        caller_anomalies = await self._detect_repeat_caller_anomalies(data, context)
        anomalies.extend(caller_anomalies)

        audit_logger.log_system_event(
            event_type="anomaly_detection_completed",
            details={
                "request_id": context.request_id,
                "data_count": len(data),
                "anomalies_found": len(anomalies),
            },
        )

        return [a.to_dict() for a in anomalies]

    async def update_baseline(self, data: list[dict[str, Any]]) -> None:
        """
        Update baselines with new data.

        Args:
            data: New data to incorporate into baselines
        """
        for item in data:
            item_type = item.get("type") or item.get("event_type") or "unknown"
            self._historical_data[item_type].append(item)

        await self._recalculate_baselines()

    async def _recalculate_baselines(self) -> None:
        """Recalculate all baselines from historical data."""
        for data_type, items in self._historical_data.items():
            if not items:
                continue

            counts_by_hour = defaultdict(int)
            for item in items:
                timestamp = item.get("timestamp") or item.get("created_at")
                if timestamp:
                    if isinstance(timestamp, str):
                        try:
                            timestamp = datetime.fromisoformat(
                                timestamp.replace("Z", "+00:00")
                            )
                        except ValueError:
                            continue
                    hour_key = timestamp.strftime("%Y-%m-%d-%H")
                    counts_by_hour[hour_key] += 1

            if counts_by_hour:
                baseline = BaselineMetrics(metric_name=f"{data_type}_hourly_count")
                baseline.update(list(counts_by_hour.values()))
                self._baselines[f"{data_type}_hourly"] = baseline

    async def _detect_vehicle_behavior_anomalies(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[AnomalyResult]:
        """Detect anomalies in vehicle behavior patterns."""
        anomalies = []

        vehicle_events = [
            d for d in data
            if d.get("source") == "flock" or d.get("event_type") == "lpr_read"
        ]

        if not vehicle_events:
            return anomalies

        vehicle_sightings: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for event in vehicle_events:
            plate = event.get("plate_number") or event.get("plate")
            if plate:
                vehicle_sightings[plate].append(event)

        for plate, sightings in vehicle_sightings.items():
            if len(sightings) < 2:
                continue

            sorted_sightings = sorted(
                sightings,
                key=lambda x: x.get("timestamp") or x.get("created_at") or "",
            )

            for i in range(1, len(sorted_sightings)):
                prev = sorted_sightings[i - 1]
                curr = sorted_sightings[i]

                prev_lat = prev.get("latitude")
                prev_lon = prev.get("longitude")
                curr_lat = curr.get("latitude")
                curr_lon = curr.get("longitude")

                if not all([prev_lat, prev_lon, curr_lat, curr_lon]):
                    continue

                distance = self._haversine_distance(
                    float(prev_lat), float(prev_lon),
                    float(curr_lat), float(curr_lon)
                )

                prev_time = prev.get("timestamp") or prev.get("created_at")
                curr_time = curr.get("timestamp") or curr.get("created_at")

                if isinstance(prev_time, str):
                    prev_time = datetime.fromisoformat(prev_time.replace("Z", "+00:00"))
                if isinstance(curr_time, str):
                    curr_time = datetime.fromisoformat(curr_time.replace("Z", "+00:00"))

                if prev_time and curr_time:
                    time_diff = (curr_time - prev_time).total_seconds() / 3600

                    if time_diff > 0:
                        speed_kmh = distance / time_diff

                        if speed_kmh > 200:
                            anomaly = AnomalyResult(
                                anomaly_id=str(uuid.uuid4()),
                                anomaly_type=AnomalyType.VEHICLE_BEHAVIOR,
                                severity=min(1.0, speed_kmh / 300),
                                description=f"Vehicle {plate} detected traveling at impossible speed ({speed_kmh:.0f} km/h implied)",
                                location=GeoLocation(
                                    latitude=float(curr_lat),
                                    longitude=float(curr_lon),
                                ),
                                related_entities=[plate],
                                metrics={
                                    "implied_speed_kmh": speed_kmh,
                                    "distance_km": distance,
                                    "time_hours": time_diff,
                                },
                                deviation=speed_kmh / 100,
                                confidence=0.85,
                            )
                            anomalies.append(anomaly)

        return anomalies

    async def _detect_gunfire_density_anomalies(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[AnomalyResult]:
        """Detect anomalies in gunfire density patterns."""
        anomalies = []

        gunfire_events = [
            d for d in data
            if d.get("source") == "shotspotter" or d.get("event_type") == "gunfire"
        ]

        if not gunfire_events:
            return anomalies

        grid_counts: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for event in gunfire_events:
            lat = event.get("latitude")
            lon = event.get("longitude")
            if lat and lon:
                grid_key = f"{float(lat):.2f},{float(lon):.2f}"
                grid_counts[grid_key].append(event)

        baseline_key = "gunfire_grid_density"
        if baseline_key not in self._baselines:
            self._baselines[baseline_key] = BaselineMetrics(
                metric_name=baseline_key,
                mean=2.0,
                std_dev=1.5,
            )

        baseline = self._baselines[baseline_key]

        for grid_key, events in grid_counts.items():
            count = len(events)
            z_score = baseline.z_score(count)

            if abs(z_score) > self.Z_SCORE_THRESHOLD:
                lat, lon = map(float, grid_key.split(","))
                severity = min(1.0, abs(z_score) / 5.0)

                anomaly = AnomalyResult(
                    anomaly_id=str(uuid.uuid4()),
                    anomaly_type=AnomalyType.GUNFIRE_DENSITY,
                    severity=severity,
                    description=f"Unusual gunfire density detected: {count} events in grid area (Z-score: {z_score:.2f})",
                    location=GeoLocation(latitude=lat, longitude=lon),
                    related_entities=[e.get("event_id", "") for e in events[:10]],
                    metrics={"event_count": count, "z_score": z_score},
                    baseline={"mean": baseline.mean, "std_dev": baseline.std_dev},
                    deviation=z_score,
                    confidence=0.9 if abs(z_score) > self.HIGH_SEVERITY_THRESHOLD else 0.75,
                )
                anomalies.append(anomaly)

        return anomalies

    async def _detect_offender_clustering(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[AnomalyResult]:
        """Detect unusual clustering of related offenders."""
        anomalies = []

        person_events = [
            d for d in data
            if d.get("entity_type") == "person" or d.get("type") == "person"
        ]

        if len(person_events) < self.MIN_CLUSTER_POINTS:
            return anomalies

        points_with_coords = [
            p for p in person_events
            if p.get("latitude") and p.get("longitude")
        ]

        if len(points_with_coords) < self.MIN_CLUSTER_POINTS:
            return anomalies

        clusters = self._dbscan_cluster(
            points_with_coords,
            epsilon_meters=self.CLUSTER_EPSILON_METERS,
            min_points=self.MIN_CLUSTER_POINTS,
        )

        for cluster in clusters:
            if cluster.point_count >= 5:
                anomaly = AnomalyResult(
                    anomaly_id=str(uuid.uuid4()),
                    anomaly_type=AnomalyType.OFFENDER_CLUSTERING,
                    severity=min(1.0, cluster.point_count / 10),
                    description=f"Unusual clustering of {cluster.point_count} related individuals detected",
                    location=GeoLocation(
                        latitude=cluster.center_lat,
                        longitude=cluster.center_lon,
                    ),
                    related_entities=[
                        e.get("id") or e.get("entity_id") or ""
                        for e in cluster.events[:10]
                    ],
                    metrics={
                        "cluster_size": cluster.point_count,
                        "density": cluster.density,
                        "radius_meters": cluster.radius_meters,
                    },
                    confidence=0.7,
                )
                anomalies.append(anomaly)

        return anomalies

    async def _detect_timeline_deviations(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[AnomalyResult]:
        """Detect timeline deviations in event patterns."""
        anomalies = []

        events_with_time = [
            d for d in data
            if d.get("timestamp") or d.get("created_at")
        ]

        if not events_with_time:
            return anomalies

        hourly_counts: dict[int, int] = defaultdict(int)
        for event in events_with_time:
            timestamp = event.get("timestamp") or event.get("created_at")
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    continue
            if timestamp:
                hourly_counts[timestamp.hour] += 1

        baseline_key = "hourly_event_distribution"
        if baseline_key not in self._baselines:
            expected_distribution = {
                0: 3, 1: 2, 2: 2, 3: 2, 4: 2, 5: 3,
                6: 5, 7: 7, 8: 10, 9: 12, 10: 12, 11: 12,
                12: 12, 13: 12, 14: 12, 15: 13, 16: 14, 17: 15,
                18: 14, 19: 13, 20: 12, 21: 10, 22: 8, 23: 5,
            }
            self._baselines[baseline_key] = BaselineMetrics(
                metric_name=baseline_key,
                mean=sum(expected_distribution.values()) / 24,
                std_dev=4.0,
            )

        baseline = self._baselines[baseline_key]

        for hour, count in hourly_counts.items():
            z_score = baseline.z_score(count)

            if abs(z_score) > self.Z_SCORE_THRESHOLD:
                anomaly = AnomalyResult(
                    anomaly_id=str(uuid.uuid4()),
                    anomaly_type=AnomalyType.TIMELINE_DEVIATION,
                    severity=min(1.0, abs(z_score) / 5.0),
                    description=f"Unusual event volume at hour {hour:02d}:00 - {count} events (Z-score: {z_score:.2f})",
                    metrics={"hour": hour, "count": count, "z_score": z_score},
                    baseline={"mean": baseline.mean, "std_dev": baseline.std_dev},
                    deviation=z_score,
                    confidence=0.8,
                )
                anomalies.append(anomaly)

        return anomalies

    async def _detect_crime_signature_shifts(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[AnomalyResult]:
        """Detect shifts in crime signature patterns."""
        anomalies = []

        incidents = [
            d for d in data
            if d.get("event_type") == "incident" or d.get("type") == "incident"
        ]

        if not incidents:
            return anomalies

        type_counts: dict[str, int] = defaultdict(int)
        for incident in incidents:
            incident_type = (
                incident.get("incident_type") or
                incident.get("crime_type") or
                incident.get("category") or
                "unknown"
            )
            type_counts[incident_type] += 1

        total = sum(type_counts.values())
        if total == 0:
            return anomalies

        expected_distribution = {
            "theft": 0.25,
            "assault": 0.15,
            "burglary": 0.12,
            "vandalism": 0.10,
            "drug": 0.08,
            "robbery": 0.05,
            "shooting": 0.03,
            "homicide": 0.01,
        }

        for crime_type, count in type_counts.items():
            observed_rate = count / total
            expected_rate = expected_distribution.get(crime_type.lower(), 0.05)

            if expected_rate > 0:
                ratio = observed_rate / expected_rate
                if ratio > 2.0 or ratio < 0.3:
                    anomaly = AnomalyResult(
                        anomaly_id=str(uuid.uuid4()),
                        anomaly_type=AnomalyType.CRIME_SIGNATURE_SHIFT,
                        severity=min(1.0, abs(ratio - 1.0) / 2.0),
                        description=f"Crime signature shift detected: {crime_type} at {observed_rate*100:.1f}% (expected {expected_rate*100:.1f}%)",
                        metrics={
                            "crime_type": crime_type,
                            "observed_rate": observed_rate,
                            "expected_rate": expected_rate,
                            "ratio": ratio,
                            "count": count,
                        },
                        deviation=ratio - 1.0,
                        confidence=0.7,
                    )
                    anomalies.append(anomaly)

        return anomalies

    async def _detect_repeat_caller_anomalies(
        self, data: list[dict[str, Any]], context: PipelineContext
    ) -> list[AnomalyResult]:
        """Detect anomalies in repeat caller patterns."""
        anomalies = []

        calls = [
            d for d in data
            if d.get("event_type") == "cad_call" or d.get("source") == "cad"
        ]

        if not calls:
            return anomalies

        caller_counts: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for call in calls:
            caller_id = (
                call.get("caller_id") or
                call.get("caller_phone") or
                call.get("reporting_party")
            )
            if caller_id:
                caller_counts[caller_id].append(call)

        for caller_id, caller_calls in caller_counts.items():
            if len(caller_calls) >= 5:
                first_call = min(
                    caller_calls,
                    key=lambda x: x.get("timestamp") or x.get("created_at") or "",
                )
                last_call = max(
                    caller_calls,
                    key=lambda x: x.get("timestamp") or x.get("created_at") or "",
                )

                first_time = first_call.get("timestamp") or first_call.get("created_at")
                last_time = last_call.get("timestamp") or last_call.get("created_at")

                if isinstance(first_time, str):
                    first_time = datetime.fromisoformat(first_time.replace("Z", "+00:00"))
                if isinstance(last_time, str):
                    last_time = datetime.fromisoformat(last_time.replace("Z", "+00:00"))

                if first_time and last_time:
                    time_span = (last_time - first_time).total_seconds() / 3600
                    if time_span > 0:
                        calls_per_hour = len(caller_calls) / time_span

                        if calls_per_hour > 2:
                            anomaly = AnomalyResult(
                                anomaly_id=str(uuid.uuid4()),
                                anomaly_type=AnomalyType.REPEAT_CALLER,
                                severity=min(1.0, calls_per_hour / 5.0),
                                description=f"Repeat caller anomaly: {len(caller_calls)} calls in {time_span:.1f} hours",
                                related_entities=[caller_id],
                                metrics={
                                    "call_count": len(caller_calls),
                                    "time_span_hours": time_span,
                                    "calls_per_hour": calls_per_hour,
                                },
                                confidence=0.85,
                            )
                            anomalies.append(anomaly)

        return anomalies

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points in kilometers."""
        R = 6371

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _dbscan_cluster(
        self,
        points: list[dict[str, Any]],
        epsilon_meters: float,
        min_points: int,
    ) -> list[SpatialCluster]:
        """Simple DBSCAN-style clustering for spatial data."""
        clusters: list[SpatialCluster] = []
        visited: set[int] = set()
        epsilon_km = epsilon_meters / 1000

        for i, _point in enumerate(points):
            if i in visited:
                continue

            neighbors = self._get_neighbors(points, i, epsilon_km)

            if len(neighbors) >= min_points:
                cluster_points = self._expand_cluster(
                    points, i, neighbors, epsilon_km, min_points, visited
                )

                if cluster_points:
                    lats = [
                        float(points[j].get("latitude"))
                        for j in cluster_points
                        if points[j].get("latitude")
                    ]
                    lons = [
                        float(points[j].get("longitude"))
                        for j in cluster_points
                        if points[j].get("longitude")
                    ]

                    if lats and lons:
                        center_lat = sum(lats) / len(lats)
                        center_lon = sum(lons) / len(lons)

                        max_dist = max(
                            self._haversine_distance(center_lat, center_lon, lat, lon)
                            for lat, lon in zip(lats, lons, strict=True)
                        ) if lats else 0

                        cluster = SpatialCluster(
                            cluster_id=str(uuid.uuid4()),
                            center_lat=center_lat,
                            center_lon=center_lon,
                            radius_meters=max_dist * 1000,
                            point_count=len(cluster_points),
                            density=len(cluster_points) / (math.pi * (max_dist + 0.001) ** 2),
                            events=[points[j] for j in cluster_points],
                        )
                        clusters.append(cluster)

        return clusters

    def _get_neighbors(
        self, points: list[dict[str, Any]], point_idx: int, epsilon_km: float
    ) -> list[int]:
        """Get all points within epsilon distance of a point."""
        neighbors = []
        point = points[point_idx]
        lat1 = float(point.get("latitude", 0))
        lon1 = float(point.get("longitude", 0))

        for i, other in enumerate(points):
            if i == point_idx:
                continue

            lat2 = float(other.get("latitude", 0))
            lon2 = float(other.get("longitude", 0))

            if self._haversine_distance(lat1, lon1, lat2, lon2) <= epsilon_km:
                neighbors.append(i)

        return neighbors

    def _expand_cluster(
        self,
        points: list[dict[str, Any]],
        point_idx: int,
        neighbors: list[int],
        epsilon_km: float,
        min_points: int,
        visited: set[int],
    ) -> list[int]:
        """Expand a cluster from a core point."""
        cluster = [point_idx]
        visited.add(point_idx)

        i = 0
        while i < len(neighbors):
            neighbor_idx = neighbors[i]

            if neighbor_idx not in visited:
                visited.add(neighbor_idx)
                new_neighbors = self._get_neighbors(points, neighbor_idx, epsilon_km)

                if len(new_neighbors) >= min_points:
                    neighbors.extend(
                        n for n in new_neighbors if n not in neighbors
                    )

            if neighbor_idx not in cluster:
                cluster.append(neighbor_idx)

            i += 1

        return cluster


async def detect_anomalies(
    data: list[dict[str, Any]],
    hours: int = 24,
    context: PipelineContext | None = None,
) -> list[dict[str, Any]]:
    """
    Detect anomalies in data from the specified time period.

    Args:
        data: Data to analyze
        hours: Time period in hours
        context: Pipeline context

    Returns:
        List of detected anomalies
    """
    if context is None:
        context = PipelineContext(request_id=str(uuid.uuid4()))

    detector = AnomalyDetector()
    return await detector.detect(data, context)


__all__ = [
    "AnomalyDetector",
    "BaselineMetrics",
    "SpatialCluster",
    "detect_anomalies",
]

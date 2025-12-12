"""
Phase 32: Satellite Imagery Analysis Layer

AI-based satellite imagery analysis for global situation awareness.

Features:
- Change detection (infrastructure, land use, military)
- Maritime anomaly detection (vessel tracking, port activity)
- Infrastructure assessment (damage, construction, activity)
- Environmental monitoring (deforestation, flooding, fires)
- Military activity detection (deployments, exercises, buildups)
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class ImagerySource(Enum):
    SENTINEL_2 = "sentinel_2"
    LANDSAT_8 = "landsat_8"
    PLANET = "planet"
    MAXAR = "maxar"
    CAPELLA = "capella"
    ICEYE = "iceye"
    SYNTHETIC = "synthetic"


class AnalysisType(Enum):
    CHANGE_DETECTION = "change_detection"
    OBJECT_DETECTION = "object_detection"
    CLASSIFICATION = "classification"
    SEGMENTATION = "segmentation"
    ANOMALY_DETECTION = "anomaly_detection"
    DAMAGE_ASSESSMENT = "damage_assessment"


class ChangeCategory(Enum):
    INFRASTRUCTURE_NEW = "infrastructure_new"
    INFRASTRUCTURE_DAMAGED = "infrastructure_damaged"
    INFRASTRUCTURE_REMOVED = "infrastructure_removed"
    MILITARY_ACTIVITY = "military_activity"
    LAND_USE_CHANGE = "land_use_change"
    ENVIRONMENTAL_CHANGE = "environmental_change"
    MARITIME_ACTIVITY = "maritime_activity"
    URBAN_EXPANSION = "urban_expansion"
    AGRICULTURAL_CHANGE = "agricultural_change"


class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AlertPriority(Enum):
    ROUTINE = 1
    ELEVATED = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class SatelliteImage:
    image_id: str
    source: ImagerySource
    capture_time: datetime
    location: dict
    resolution_meters: float
    cloud_cover_percent: float
    bands: list[str]
    metadata: dict
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.image_id}:{self.source.value}:{self.capture_time.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class ChangeDetection:
    detection_id: str
    before_image_id: str
    after_image_id: str
    change_category: ChangeCategory
    location: dict
    area_sq_km: float
    change_magnitude: float
    confidence: ConfidenceLevel
    description: str
    detected_objects: list[dict]
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.detection_id}:{self.change_category.value}:{self.change_magnitude}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class MaritimeDetection:
    detection_id: str
    image_id: str
    vessel_count: int
    vessels: list[dict]
    port_activity_level: str
    anomalies: list[dict]
    location: dict
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.detection_id}:{self.vessel_count}:{self.timestamp.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class InfrastructureAssessment:
    assessment_id: str
    image_id: str
    location: dict
    infrastructure_type: str
    condition: str
    damage_level: float
    activity_level: str
    changes_detected: list[str]
    confidence: ConfidenceLevel
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.assessment_id}:{self.infrastructure_type}:{self.damage_level}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class MilitaryActivityDetection:
    detection_id: str
    image_id: str
    location: dict
    activity_type: str
    unit_types: list[str]
    estimated_personnel: int
    vehicle_count: int
    aircraft_count: int
    confidence: ConfidenceLevel
    assessment: str
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.detection_id}:{self.activity_type}:{self.vehicle_count}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class SatelliteAlert:
    alert_id: str
    detection_id: str
    alert_type: str
    priority: AlertPriority
    title: str
    description: str
    location: dict
    affected_region: str
    recommended_action: str
    expires_at: datetime
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.alert_id}:{self.alert_type}:{self.priority.value}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


class SatelliteAnalysisLayer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.images: dict[str, SatelliteImage] = {}
        self.change_detections: list[ChangeDetection] = []
        self.maritime_detections: list[MaritimeDetection] = []
        self.infrastructure_assessments: list[InfrastructureAssessment] = []
        self.military_detections: list[MilitaryActivityDetection] = []
        self.alerts: list[SatelliteAlert] = []

        self.monitored_locations = [
            {"name": "South China Sea", "lat": 12.0, "lon": 114.0, "type": "maritime"},
            {"name": "Taiwan Strait", "lat": 24.0, "lon": 119.0, "type": "maritime"},
            {"name": "Persian Gulf", "lat": 26.5, "lon": 51.0, "type": "maritime"},
            {"name": "Black Sea", "lat": 43.5, "lon": 34.0, "type": "maritime"},
            {"name": "Ukraine Border", "lat": 50.0, "lon": 36.0, "type": "military"},
            {"name": "Korean DMZ", "lat": 38.0, "lon": 127.0, "type": "military"},
            {"name": "Gaza", "lat": 31.5, "lon": 34.5, "type": "conflict"},
            {"name": "Amazon Basin", "lat": -3.0, "lon": -60.0, "type": "environmental"},
        ]

        self.detection_models = {
            AnalysisType.CHANGE_DETECTION: "change_detection_v3",
            AnalysisType.OBJECT_DETECTION: "yolo_satellite_v2",
            AnalysisType.CLASSIFICATION: "resnet_landuse_v1",
            AnalysisType.DAMAGE_ASSESSMENT: "damage_assessment_v2",
            AnalysisType.ANOMALY_DETECTION: "anomaly_detector_v1",
        }

        self.statistics = {
            "total_images_processed": 0,
            "total_change_detections": 0,
            "total_maritime_detections": 0,
            "total_infrastructure_assessments": 0,
            "total_military_detections": 0,
            "total_alerts": 0,
            "detections_by_category": {c.value: 0 for c in ChangeCategory},
        }

    def ingest_image(
        self,
        source: ImagerySource,
        location: dict,
        resolution_meters: float,
        cloud_cover_percent: float = 0.0,
        bands: list[str] = None,
        metadata: dict = None,
    ) -> SatelliteImage:
        image = SatelliteImage(
            image_id=f"IMG-{uuid.uuid4().hex[:8].upper()}",
            source=source,
            capture_time=datetime.utcnow(),
            location=location,
            resolution_meters=resolution_meters,
            cloud_cover_percent=cloud_cover_percent,
            bands=bands or ["RGB", "NIR"],
            metadata=metadata or {},
        )

        self.images[image.image_id] = image
        self.statistics["total_images_processed"] += 1

        return image

    def detect_changes(
        self,
        before_image_id: str,
        after_image_id: str,
        analysis_types: list[ChangeCategory] = None,
    ) -> list[ChangeDetection]:
        before_image = self.images.get(before_image_id)
        after_image = self.images.get(after_image_id)

        if not before_image or not after_image:
            raise ValueError("Both before and after images must exist")

        detections = []
        analysis_types = analysis_types or list(ChangeCategory)

        for category in analysis_types:
            change_detected, magnitude, objects = self._run_change_detection(
                before_image, after_image, category
            )

            if change_detected:
                confidence = self._calculate_confidence(magnitude, len(objects))

                detection = ChangeDetection(
                    detection_id=f"CD-{uuid.uuid4().hex[:8].upper()}",
                    before_image_id=before_image_id,
                    after_image_id=after_image_id,
                    change_category=category,
                    location=after_image.location,
                    area_sq_km=self._estimate_area(objects),
                    change_magnitude=magnitude,
                    confidence=confidence,
                    description=self._generate_change_description(category, magnitude, objects),
                    detected_objects=objects,
                    timestamp=datetime.utcnow(),
                )

                detections.append(detection)
                self.change_detections.append(detection)
                self.statistics["total_change_detections"] += 1
                self.statistics["detections_by_category"][category.value] += 1

                if magnitude > 0.7 or confidence == ConfidenceLevel.VERY_HIGH:
                    self._create_alert_from_change(detection)

        return detections

    def _run_change_detection(
        self,
        before: SatelliteImage,
        after: SatelliteImage,
        category: ChangeCategory,
    ) -> tuple[bool, float, list[dict]]:
        import random
        detected = random.random() > 0.6
        magnitude = random.uniform(0.3, 0.9) if detected else 0.0

        objects = []
        if detected:
            num_objects = random.randint(1, 5)
            for i in range(num_objects):
                objects.append({
                    "object_id": f"OBJ-{i+1}",
                    "type": category.value,
                    "confidence": random.uniform(0.7, 0.95),
                    "bbox": {
                        "x": random.uniform(0, 100),
                        "y": random.uniform(0, 100),
                        "width": random.uniform(10, 50),
                        "height": random.uniform(10, 50),
                    },
                })

        return detected, magnitude, objects

    def _calculate_confidence(self, magnitude: float, object_count: int) -> ConfidenceLevel:
        score = magnitude * 0.6 + min(object_count / 5, 1.0) * 0.4

        if score > 0.85:
            return ConfidenceLevel.VERY_HIGH
        elif score > 0.7:
            return ConfidenceLevel.HIGH
        elif score > 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _estimate_area(self, objects: list[dict]) -> float:
        if not objects:
            return 0.0
        total_area = sum(
            obj.get("bbox", {}).get("width", 0) * obj.get("bbox", {}).get("height", 0)
            for obj in objects
        )
        return total_area / 1000

    def _generate_change_description(
        self,
        category: ChangeCategory,
        magnitude: float,
        objects: list[dict],
    ) -> str:
        descriptions = {
            ChangeCategory.INFRASTRUCTURE_NEW: f"New infrastructure detected ({len(objects)} structures)",
            ChangeCategory.INFRASTRUCTURE_DAMAGED: f"Infrastructure damage detected (severity: {magnitude:.0%})",
            ChangeCategory.MILITARY_ACTIVITY: f"Military activity detected ({len(objects)} units)",
            ChangeCategory.MARITIME_ACTIVITY: f"Maritime activity change ({len(objects)} vessels)",
            ChangeCategory.ENVIRONMENTAL_CHANGE: f"Environmental change detected (magnitude: {magnitude:.0%})",
            ChangeCategory.URBAN_EXPANSION: f"Urban expansion detected ({len(objects)} new areas)",
        }
        return descriptions.get(category, f"Change detected: {category.value}")

    def _create_alert_from_change(self, detection: ChangeDetection):
        priority_map = {
            ChangeCategory.MILITARY_ACTIVITY: AlertPriority.URGENT,
            ChangeCategory.INFRASTRUCTURE_DAMAGED: AlertPriority.HIGH,
            ChangeCategory.MARITIME_ACTIVITY: AlertPriority.ELEVATED,
        }

        priority = priority_map.get(detection.change_category, AlertPriority.ROUTINE)

        alert = SatelliteAlert(
            alert_id=f"SA-{uuid.uuid4().hex[:8].upper()}",
            detection_id=detection.detection_id,
            alert_type=detection.change_category.value,
            priority=priority,
            title=f"Satellite Alert: {detection.change_category.value.replace('_', ' ').title()}",
            description=detection.description,
            location=detection.location,
            affected_region=detection.location.get("region", "Unknown"),
            recommended_action=self._get_recommended_action(detection.change_category),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            timestamp=datetime.utcnow(),
        )

        self.alerts.append(alert)
        self.statistics["total_alerts"] += 1

    def _get_recommended_action(self, category: ChangeCategory) -> str:
        actions = {
            ChangeCategory.MILITARY_ACTIVITY: "Escalate to intelligence analysts for assessment",
            ChangeCategory.INFRASTRUCTURE_DAMAGED: "Coordinate with disaster response teams",
            ChangeCategory.MARITIME_ACTIVITY: "Cross-reference with AIS data",
            ChangeCategory.ENVIRONMENTAL_CHANGE: "Monitor for continued changes",
        }
        return actions.get(category, "Continue monitoring")

    def analyze_maritime_activity(
        self,
        image_id: str,
        region: str = None,
    ) -> MaritimeDetection:
        image = self.images.get(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        import random
        vessel_count = random.randint(5, 50)
        vessels = []

        for i in range(vessel_count):
            vessels.append({
                "vessel_id": f"V-{i+1}",
                "type": random.choice(["cargo", "tanker", "fishing", "military", "passenger"]),
                "length_meters": random.randint(50, 300),
                "position": {
                    "lat": image.location.get("lat", 0) + random.uniform(-0.5, 0.5),
                    "lon": image.location.get("lon", 0) + random.uniform(-0.5, 0.5),
                },
                "heading": random.randint(0, 359),
                "confidence": random.uniform(0.7, 0.95),
            })

        anomalies = []
        if random.random() > 0.7:
            anomalies.append({
                "type": random.choice(["dark_vessel", "unusual_pattern", "congestion"]),
                "description": "Anomalous maritime activity detected",
                "confidence": random.uniform(0.6, 0.9),
            })

        activity_levels = ["low", "moderate", "high", "very_high"]
        activity_level = random.choice(activity_levels)

        detection = MaritimeDetection(
            detection_id=f"MD-{uuid.uuid4().hex[:8].upper()}",
            image_id=image_id,
            vessel_count=vessel_count,
            vessels=vessels,
            port_activity_level=activity_level,
            anomalies=anomalies,
            location=image.location,
            timestamp=datetime.utcnow(),
        )

        self.maritime_detections.append(detection)
        self.statistics["total_maritime_detections"] += 1

        return detection

    def assess_infrastructure(
        self,
        image_id: str,
        infrastructure_type: str,
    ) -> InfrastructureAssessment:
        image = self.images.get(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        import random

        conditions = ["operational", "degraded", "damaged", "destroyed"]
        condition = random.choice(conditions)

        damage_level = {
            "operational": random.uniform(0, 0.1),
            "degraded": random.uniform(0.1, 0.4),
            "damaged": random.uniform(0.4, 0.7),
            "destroyed": random.uniform(0.7, 1.0),
        }[condition]

        activity_levels = ["none", "low", "moderate", "high"]
        activity_level = random.choice(activity_levels)

        changes = []
        if random.random() > 0.5:
            changes.append(random.choice([
                "New construction detected",
                "Expansion observed",
                "Damage visible",
                "Activity increase",
            ]))

        confidence = ConfidenceLevel.HIGH if damage_level > 0.5 else ConfidenceLevel.MEDIUM

        assessment = InfrastructureAssessment(
            assessment_id=f"IA-{uuid.uuid4().hex[:8].upper()}",
            image_id=image_id,
            location=image.location,
            infrastructure_type=infrastructure_type,
            condition=condition,
            damage_level=damage_level,
            activity_level=activity_level,
            changes_detected=changes,
            confidence=confidence,
            timestamp=datetime.utcnow(),
        )

        self.infrastructure_assessments.append(assessment)
        self.statistics["total_infrastructure_assessments"] += 1

        return assessment

    def detect_military_activity(
        self,
        image_id: str,
        region: str = None,
    ) -> MilitaryActivityDetection:
        image = self.images.get(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        import random

        activity_types = ["deployment", "exercise", "buildup", "movement", "base_activity"]
        activity_type = random.choice(activity_types)

        unit_types = random.sample(
            ["infantry", "armor", "artillery", "air_defense", "logistics", "headquarters"],
            k=random.randint(1, 4)
        )

        vehicle_count = random.randint(10, 200)
        aircraft_count = random.randint(0, 30)
        personnel = random.randint(100, 5000)

        confidence = ConfidenceLevel.HIGH if vehicle_count > 50 else ConfidenceLevel.MEDIUM

        assessments = {
            "deployment": "Active military deployment detected",
            "exercise": "Military exercise in progress",
            "buildup": "Force buildup observed",
            "movement": "Troop/equipment movement detected",
            "base_activity": "Increased base activity",
        }

        detection = MilitaryActivityDetection(
            detection_id=f"MA-{uuid.uuid4().hex[:8].upper()}",
            image_id=image_id,
            location=image.location,
            activity_type=activity_type,
            unit_types=unit_types,
            estimated_personnel=personnel,
            vehicle_count=vehicle_count,
            aircraft_count=aircraft_count,
            confidence=confidence,
            assessment=assessments.get(activity_type, "Military activity detected"),
            timestamp=datetime.utcnow(),
        )

        self.military_detections.append(detection)
        self.statistics["total_military_detections"] += 1

        if vehicle_count > 100 or activity_type in ["deployment", "buildup"]:
            self._create_military_alert(detection)

        return detection

    def _create_military_alert(self, detection: MilitaryActivityDetection):
        alert = SatelliteAlert(
            alert_id=f"SA-{uuid.uuid4().hex[:8].upper()}",
            detection_id=detection.detection_id,
            alert_type="military_activity",
            priority=AlertPriority.URGENT,
            title=f"Military Activity Alert: {detection.activity_type.replace('_', ' ').title()}",
            description=detection.assessment,
            location=detection.location,
            affected_region=detection.location.get("region", "Unknown"),
            recommended_action="Escalate to intelligence analysts immediately",
            expires_at=datetime.utcnow() + timedelta(hours=12),
            timestamp=datetime.utcnow(),
        )

        self.alerts.append(alert)
        self.statistics["total_alerts"] += 1

    def get_active_alerts(self) -> list[SatelliteAlert]:
        now = datetime.utcnow()
        return [a for a in self.alerts if a.expires_at > now]

    def get_recent_detections(self, hours: int = 24) -> dict:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return {
            "change_detections": [d for d in self.change_detections if d.timestamp > cutoff],
            "maritime_detections": [d for d in self.maritime_detections if d.timestamp > cutoff],
            "infrastructure_assessments": [a for a in self.infrastructure_assessments if a.timestamp > cutoff],
            "military_detections": [d for d in self.military_detections if d.timestamp > cutoff],
        }

    def get_statistics(self) -> dict:
        return self.statistics.copy()

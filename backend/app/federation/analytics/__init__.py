"""
G3TI RTCC-UIP Multi-Agency Analytics
Phase 10: Cross-jurisdiction analytics, heatmaps, and pattern detection
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4


class AnalyticsTimeRange(str, Enum):
    """Time ranges for analytics"""
    LAST_24_HOURS = "last_24_hours"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"


class PatternType(str, Enum):
    """Types of cross-jurisdiction patterns"""
    CRIME_SERIES = "crime_series"
    SUSPECT_MOVEMENT = "suspect_movement"
    VEHICLE_PATTERN = "vehicle_pattern"
    HOTSPOT_CORRELATION = "hotspot_correlation"
    TEMPORAL_PATTERN = "temporal_pattern"
    GEOGRAPHIC_CLUSTER = "geographic_cluster"
    ENTITY_NETWORK = "entity_network"
    CROSS_BORDER_ACTIVITY = "cross_border_activity"


class RiskLevel(str, Enum):
    """Risk levels for analytics"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class HeatmapCell:
    """Cell in a cross-jurisdiction heatmap"""

    def __init__(
        self,
        cell_id: str,
        latitude: float,
        longitude: float,
        value: float,
        agency_contributions: dict[str, float],
        incident_count: int,
        incident_types: dict[str, int],
    ):
        self.id = cell_id
        self.latitude = latitude
        self.longitude = longitude
        self.value = value
        self.agency_contributions = agency_contributions
        self.incident_count = incident_count
        self.incident_types = incident_types


class CrossJurisdictionHeatmap:
    """Cross-jurisdiction heatmap"""

    def __init__(
        self,
        heatmap_id: str,
        name: str,
        participating_agencies: list[str],
        time_range: AnalyticsTimeRange,
        start_date: datetime,
        end_date: datetime,
        bounds: dict[str, float],
        resolution: float,
    ):
        self.id = heatmap_id
        self.name = name
        self.participating_agencies = participating_agencies
        self.time_range = time_range
        self.start_date = start_date
        self.end_date = end_date
        self.bounds = bounds
        self.resolution = resolution
        self.cells: list[HeatmapCell] = []
        self.created_at = datetime.utcnow()
        self.total_incidents = 0
        self.agency_totals: dict[str, int] = {}


class DetectedPattern:
    """Detected cross-jurisdiction pattern"""

    def __init__(
        self,
        pattern_type: PatternType,
        name: str,
        description: str,
        confidence_score: float,
        affected_agencies: list[str],
        geographic_extent: dict[str, Any],
        temporal_extent: dict[str, Any],
        related_entities: list[dict[str, Any]],
        related_incidents: list[str],
        risk_level: RiskLevel,
    ):
        self.id = str(uuid4())
        self.pattern_type = pattern_type
        self.name = name
        self.description = description
        self.confidence_score = confidence_score
        self.affected_agencies = affected_agencies
        self.geographic_extent = geographic_extent
        self.temporal_extent = temporal_extent
        self.related_entities = related_entities
        self.related_incidents = related_incidents
        self.risk_level = risk_level
        self.detected_at = datetime.utcnow()
        self.is_active = True
        self.acknowledged_by: list[dict[str, Any]] = []


class EntityCorrelation:
    """Cross-agency entity correlation"""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        correlation_score: float,
        agencies_involved: list[str],
        incidents_involved: list[str],
        first_seen: datetime,
        last_seen: datetime,
        activity_summary: dict[str, Any],
    ):
        self.id = str(uuid4())
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.correlation_score = correlation_score
        self.agencies_involved = agencies_involved
        self.incidents_involved = incidents_involved
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.activity_summary = activity_summary
        self.created_at = datetime.utcnow()


class HotspotComparison:
    """Comparison of hotspots between agencies"""

    def __init__(
        self,
        comparison_id: str,
        agencies: list[str],
        time_range: AnalyticsTimeRange,
        start_date: datetime,
        end_date: datetime,
    ):
        self.id = comparison_id
        self.agencies = agencies
        self.time_range = time_range
        self.start_date = start_date
        self.end_date = end_date
        self.agency_hotspots: dict[str, list[dict[str, Any]]] = {}
        self.shared_hotspots: list[dict[str, Any]] = []
        self.correlation_matrix: dict[str, dict[str, float]] = {}
        self.created_at = datetime.utcnow()


class SharedRiskScore:
    """Shared risk score across agencies"""

    def __init__(
        self,
        location_id: str,
        location_name: str,
        latitude: float,
        longitude: float,
        overall_score: float,
        agency_scores: dict[str, float],
        risk_factors: list[dict[str, Any]],
        risk_level: RiskLevel,
    ):
        self.id = str(uuid4())
        self.location_id = location_id
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.overall_score = overall_score
        self.agency_scores = agency_scores
        self.risk_factors = risk_factors
        self.risk_level = risk_level
        self.calculated_at = datetime.utcnow()


class AnalyticsQuery:
    """Query for multi-agency analytics"""

    def __init__(
        self,
        query_id: str,
        requesting_agency: str,
        requesting_user: str,
        query_type: str,
        parameters: dict[str, Any],
        target_agencies: list[str],
    ):
        self.id = query_id
        self.requesting_agency = requesting_agency
        self.requesting_user = requesting_user
        self.query_type = query_type
        self.parameters = parameters
        self.target_agencies = target_agencies
        self.created_at = datetime.utcnow()
        self.completed_at: datetime | None = None
        self.status = "pending"
        self.results: dict[str, Any] = {}


class MultiAgencyAnalyticsEngine:
    """Engine for cross-jurisdiction analytics"""

    def __init__(self):
        self.heatmaps: dict[str, CrossJurisdictionHeatmap] = {}
        self.patterns: dict[str, DetectedPattern] = {}
        self.correlations: dict[str, EntityCorrelation] = {}
        self.comparisons: dict[str, HotspotComparison] = {}
        self.risk_scores: dict[str, SharedRiskScore] = {}
        self.queries: dict[str, AnalyticsQuery] = {}
        self.agency_data: dict[str, list[dict[str, Any]]] = {}

    def generate_cross_jurisdiction_heatmap(
        self,
        name: str,
        participating_agencies: list[str],
        time_range: AnalyticsTimeRange,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        bounds: dict[str, float] | None = None,
        resolution: float = 0.01,
        incident_types: list[str] | None = None,
    ) -> CrossJurisdictionHeatmap:
        """Generate a cross-jurisdiction heatmap"""
        heatmap_id = str(uuid4())

        # Calculate date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = self._calculate_start_date(time_range, end_date)

        # Default bounds (example: continental US)
        if not bounds:
            bounds = {
                "north": 49.0,
                "south": 25.0,
                "east": -66.0,
                "west": -125.0,
            }

        heatmap = CrossJurisdictionHeatmap(
            heatmap_id=heatmap_id,
            name=name,
            participating_agencies=participating_agencies,
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
            bounds=bounds,
            resolution=resolution,
        )

        # Generate cells (simulated for now)
        heatmap.cells = self._generate_heatmap_cells(
            bounds, resolution, participating_agencies
        )

        # Calculate totals
        for cell in heatmap.cells:
            heatmap.total_incidents += cell.incident_count
            for agency, count in cell.agency_contributions.items():
                heatmap.agency_totals[agency] = (
                    heatmap.agency_totals.get(agency, 0) + int(count)
                )

        self.heatmaps[heatmap_id] = heatmap
        return heatmap

    def _calculate_start_date(
        self,
        time_range: AnalyticsTimeRange,
        end_date: datetime,
    ) -> datetime:
        """Calculate start date based on time range"""
        if time_range == AnalyticsTimeRange.LAST_24_HOURS:
            return end_date - timedelta(hours=24)
        elif time_range == AnalyticsTimeRange.LAST_7_DAYS:
            return end_date - timedelta(days=7)
        elif time_range == AnalyticsTimeRange.LAST_30_DAYS:
            return end_date - timedelta(days=30)
        elif time_range == AnalyticsTimeRange.LAST_90_DAYS:
            return end_date - timedelta(days=90)
        elif time_range == AnalyticsTimeRange.LAST_YEAR:
            return end_date - timedelta(days=365)
        return end_date - timedelta(days=30)

    def _generate_heatmap_cells(
        self,
        bounds: dict[str, float],
        resolution: float,
        agencies: list[str],
    ) -> list[HeatmapCell]:
        """Generate heatmap cells (simulated)"""
        cells = []
        lat = bounds["south"]
        cell_id = 0

        while lat < bounds["north"]:
            lon = bounds["west"]
            while lon < bounds["east"]:
                # Simulated data
                value = 0.0
                agency_contributions = {}
                incident_count = 0
                incident_types: dict[str, int] = {}

                cell = HeatmapCell(
                    cell_id=f"cell_{cell_id}",
                    latitude=lat,
                    longitude=lon,
                    value=value,
                    agency_contributions=agency_contributions,
                    incident_count=incident_count,
                    incident_types=incident_types,
                )
                cells.append(cell)
                cell_id += 1
                lon += resolution
            lat += resolution

        return cells

    def detect_regional_patterns(
        self,
        participating_agencies: list[str],
        time_range: AnalyticsTimeRange,
        pattern_types: list[PatternType] | None = None,
        min_confidence: float = 0.7,
    ) -> list[DetectedPattern]:
        """Detect patterns across jurisdictions"""
        if not pattern_types:
            pattern_types = list(PatternType)

        detected = []

        for pattern_type in pattern_types:
            patterns = self._detect_pattern_type(
                pattern_type, participating_agencies, time_range, min_confidence
            )
            detected.extend(patterns)

        # Store patterns
        for pattern in detected:
            self.patterns[pattern.id] = pattern

        return detected

    def _detect_pattern_type(
        self,
        pattern_type: PatternType,
        agencies: list[str],
        time_range: AnalyticsTimeRange,
        min_confidence: float,
    ) -> list[DetectedPattern]:
        """Detect specific pattern type (simulated)"""
        # In production, this would use actual data analysis
        # For now, return empty list (no patterns detected)
        return []

    def correlate_entities_across_agencies(
        self,
        entity_type: str,
        participating_agencies: list[str],
        time_range: AnalyticsTimeRange,
        min_correlation_score: float = 0.5,
    ) -> list[EntityCorrelation]:
        """Correlate entities across multiple agencies"""
        correlations = []

        # In production, this would query each agency's data
        # and find matching entities
        # For now, return empty list

        return correlations

    def compare_hotspots(
        self,
        agencies: list[str],
        time_range: AnalyticsTimeRange,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> HotspotComparison:
        """Compare hotspots between agencies"""
        comparison_id = str(uuid4())

        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = self._calculate_start_date(time_range, end_date)

        comparison = HotspotComparison(
            comparison_id=comparison_id,
            agencies=agencies,
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
        )

        # Generate agency hotspots (simulated)
        for agency in agencies:
            comparison.agency_hotspots[agency] = []

        # Find shared hotspots
        comparison.shared_hotspots = self._find_shared_hotspots(
            comparison.agency_hotspots
        )

        # Calculate correlation matrix
        comparison.correlation_matrix = self._calculate_correlation_matrix(agencies)

        self.comparisons[comparison_id] = comparison
        return comparison

    def _find_shared_hotspots(
        self,
        agency_hotspots: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """Find hotspots shared between agencies"""
        # In production, this would use spatial analysis
        return []

    def _calculate_correlation_matrix(
        self,
        agencies: list[str],
    ) -> dict[str, dict[str, float]]:
        """Calculate correlation matrix between agencies"""
        matrix: dict[str, dict[str, float]] = {}
        for agency1 in agencies:
            matrix[agency1] = {}
            for agency2 in agencies:
                if agency1 == agency2:
                    matrix[agency1][agency2] = 1.0
                else:
                    # Simulated correlation
                    matrix[agency1][agency2] = 0.0
        return matrix

    def calculate_shared_risk_scores(
        self,
        locations: list[dict[str, Any]],
        participating_agencies: list[str],
        risk_factors: list[str] | None = None,
    ) -> list[SharedRiskScore]:
        """Calculate shared risk scores for locations"""
        scores = []

        for location in locations:
            score = self._calculate_location_risk(
                location, participating_agencies, risk_factors
            )
            scores.append(score)
            self.risk_scores[score.id] = score

        return scores

    def _calculate_location_risk(
        self,
        location: dict[str, Any],
        agencies: list[str],
        risk_factors: list[str] | None,
    ) -> SharedRiskScore:
        """Calculate risk score for a single location"""
        agency_scores = {}
        total_score = 0.0

        for agency in agencies:
            # Simulated agency-specific score
            agency_scores[agency] = 0.0
            total_score += agency_scores[agency]

        if agencies:
            overall_score = total_score / len(agencies)
        else:
            overall_score = 0.0

        risk_level = self._score_to_risk_level(overall_score)

        return SharedRiskScore(
            location_id=location.get("id", str(uuid4())),
            location_name=location.get("name", "Unknown"),
            latitude=location.get("latitude", 0.0),
            longitude=location.get("longitude", 0.0),
            overall_score=overall_score,
            agency_scores=agency_scores,
            risk_factors=[],
            risk_level=risk_level,
        )

    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level"""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        elif score >= 0.2:
            return RiskLevel.LOW
        return RiskLevel.MINIMAL

    def get_heatmap(self, heatmap_id: str) -> CrossJurisdictionHeatmap | None:
        """Get a heatmap by ID"""
        return self.heatmaps.get(heatmap_id)

    def get_patterns(
        self,
        agency_id: str | None = None,
        pattern_type: PatternType | None = None,
        active_only: bool = True,
    ) -> list[DetectedPattern]:
        """Get detected patterns with optional filtering"""
        patterns = list(self.patterns.values())

        if agency_id:
            patterns = [
                p for p in patterns
                if agency_id in p.affected_agencies
            ]
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        if active_only:
            patterns = [p for p in patterns if p.is_active]

        return patterns

    def acknowledge_pattern(
        self,
        pattern_id: str,
        agency: str,
        user: str,
    ) -> bool:
        """Acknowledge a detected pattern"""
        pattern = self.patterns.get(pattern_id)
        if pattern:
            pattern.acknowledged_by.append({
                "agency": agency,
                "user": user,
                "acknowledged_at": datetime.utcnow().isoformat(),
            })
            return True
        return False

    def get_analytics_summary(
        self,
        agency_id: str,
        time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_30_DAYS,
    ) -> dict[str, Any]:
        """Get analytics summary for an agency"""
        end_date = datetime.utcnow()
        start_date = self._calculate_start_date(time_range, end_date)

        # Count relevant items
        heatmap_count = len([
            h for h in self.heatmaps.values()
            if agency_id in h.participating_agencies
        ])

        pattern_count = len([
            p for p in self.patterns.values()
            if agency_id in p.affected_agencies and p.is_active
        ])

        correlation_count = len([
            c for c in self.correlations.values()
            if agency_id in c.agencies_involved
        ])

        return {
            "agency_id": agency_id,
            "time_range": time_range.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "heatmaps_generated": heatmap_count,
            "active_patterns": pattern_count,
            "entity_correlations": correlation_count,
            "risk_scores_calculated": len(self.risk_scores),
        }

    def execute_analytics_query(
        self,
        requesting_agency: str,
        requesting_user: str,
        query_type: str,
        parameters: dict[str, Any],
        target_agencies: list[str],
    ) -> AnalyticsQuery:
        """Execute a custom analytics query"""
        query = AnalyticsQuery(
            query_id=str(uuid4()),
            requesting_agency=requesting_agency,
            requesting_user=requesting_user,
            query_type=query_type,
            parameters=parameters,
            target_agencies=target_agencies,
        )
        self.queries[query.id] = query

        # Execute query based on type
        if query_type == "heatmap":
            result = self.generate_cross_jurisdiction_heatmap(
                name=parameters.get("name", "Query Heatmap"),
                participating_agencies=target_agencies,
                time_range=AnalyticsTimeRange(
                    parameters.get("time_range", "last_30_days")
                ),
            )
            query.results = {"heatmap_id": result.id}
        elif query_type == "patterns":
            results = self.detect_regional_patterns(
                participating_agencies=target_agencies,
                time_range=AnalyticsTimeRange(
                    parameters.get("time_range", "last_30_days")
                ),
            )
            query.results = {"patterns": [p.id for p in results]}
        elif query_type == "hotspot_comparison":
            result = self.compare_hotspots(
                agencies=target_agencies,
                time_range=AnalyticsTimeRange(
                    parameters.get("time_range", "last_30_days")
                ),
            )
            query.results = {"comparison_id": result.id}

        query.status = "completed"
        query.completed_at = datetime.utcnow()
        return query

    def get_cross_border_activity(
        self,
        agencies: list[str],
        time_range: AnalyticsTimeRange,
    ) -> dict[str, Any]:
        """Analyze cross-border activity between jurisdictions"""
        end_date = datetime.utcnow()
        start_date = self._calculate_start_date(time_range, end_date)

        # In production, this would analyze actual movement patterns
        return {
            "agencies": agencies,
            "time_range": time_range.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "cross_border_incidents": 0,
            "suspect_movements": [],
            "vehicle_patterns": [],
            "hotspot_overlaps": [],
        }


# Create singleton instance
analytics_engine = MultiAgencyAnalyticsEngine()

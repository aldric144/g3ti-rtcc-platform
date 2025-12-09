"""
Data Lake Service for G3TI RTCC-UIP.

This module provides high-level business logic for data lake operations including:
- Incident ingestion and processing
- Historical aggregate computation
- Offender profile management
- Multi-year heatmap generation
- Data governance enforcement
"""

import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from ..db.elasticsearch import ElasticsearchManager
from ..db.neo4j import Neo4jManager
from ..db.redis import RedisManager
from .models import (
    CrimeCategory,
    CrimeDataPartition,
    DataLakeConfig,
    DataLakeStats,
    DataLineageRecord,
    DataQualityMetric,
    DataRetentionPolicy,
    GeoPoint,
    HeatmapCell,
    HistoricalAggregate,
    IncidentRecord,
    MultiYearHeatmapData,
    OffenderProfile,
    PartitionMetadata,
    PartitionType,
    RetentionAction,
    SeverityLevel,
)
from .repository import DataLakeRepository

logger = logging.getLogger(__name__)


class DataLakeService:
    """
    Service layer for data lake operations.

    Provides business logic for:
    - Incident ingestion with validation
    - Aggregate computation and caching
    - Offender profile updates
    - Multi-year heatmap generation
    - Data retention enforcement
    """

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
        config: DataLakeConfig | None = None,
    ):
        """
        Initialize the Data Lake Service.

        Args:
            neo4j: Neo4j database manager
            es: Elasticsearch manager
            redis: Redis manager
            config: Optional data lake configuration
        """
        self.repository = DataLakeRepository(neo4j, es, redis)
        self.config = config or DataLakeConfig()
        self.redis = redis

        logger.info("DataLakeService initialized")

    # ==================== Incident Ingestion ====================

    async def ingest_incident(
        self,
        incident_data: dict[str, Any],
        source_system: str,
        source_id: str,
    ) -> IncidentRecord:
        """
        Ingest a new incident into the data lake.

        Performs validation, enrichment, and storage of incident data.

        Args:
            incident_data: Raw incident data
            source_system: Source system identifier
            source_id: ID in source system

        Returns:
            Stored incident record
        """
        # Generate unique ID
        incident_id = self._generate_incident_id(source_system, source_id)

        # Parse timestamp
        timestamp = self._parse_timestamp(incident_data.get("timestamp"))
        reported_at = self._parse_timestamp(
            incident_data.get("reported_at", incident_data.get("timestamp"))
        )

        # Parse location
        location = self._parse_location(incident_data)

        # Determine crime category
        crime_category = self._classify_crime(
            incident_data.get("crime_type", ""),
            incident_data.get("crime_description", ""),
        )

        # Determine severity
        severity = self._assess_severity(incident_data)

        # Create partition keys
        partition_date = timestamp.strftime("%Y-%m-%d")
        partition_month = timestamp.strftime("%Y-%m")
        partition_year = timestamp.year

        # Create incident record
        incident = IncidentRecord(
            id=incident_id,
            incident_number=incident_data.get("incident_number", source_id),
            timestamp=timestamp,
            reported_at=reported_at,
            crime_category=crime_category,
            crime_type=incident_data.get("crime_type", "unknown"),
            crime_description=incident_data.get("crime_description", ""),
            ucr_code=incident_data.get("ucr_code"),
            severity=severity,
            location=location,
            address=incident_data.get("address"),
            beat=incident_data.get("beat"),
            district=incident_data.get("district"),
            jurisdiction=incident_data.get("jurisdiction", "default"),
            suspect_count=incident_data.get("suspect_count", 0),
            victim_count=incident_data.get("victim_count", 0),
            arrest_made=incident_data.get("arrest_made", False),
            offender_ids=incident_data.get("offender_ids", []),
            weapon_involved=incident_data.get("weapon_involved", False),
            weapon_type=incident_data.get("weapon_type"),
            domestic_violence=incident_data.get("domestic_violence", False),
            gang_related=incident_data.get("gang_related", False),
            source_system=source_system,
            source_id=source_id,
            partition_date=partition_date,
            partition_month=partition_month,
            partition_year=partition_year,
        )

        # Validate incident
        if self.config.validation_enabled:
            self._validate_incident(incident)

        # Store incident
        await self.repository.store_incident(incident)

        # Create lineage record
        await self._create_lineage_record(incident, source_system, source_id)

        # Ensure partition exists
        await self._ensure_partition(partition_month, timestamp)

        # Update offender profiles if offenders are known
        for offender_id in incident.offender_ids:
            await self._update_offender_profile(offender_id, incident)

        logger.info(f"Ingested incident {incident_id} from {source_system}")
        return incident

    async def ingest_incidents_bulk(
        self,
        incidents_data: list[dict[str, Any]],
        source_system: str,
    ) -> dict[str, Any]:
        """
        Bulk ingest incidents into the data lake.

        Args:
            incidents_data: List of raw incident data
            source_system: Source system identifier

        Returns:
            Bulk operation result
        """
        incidents = []
        errors = []

        for idx, data in enumerate(incidents_data):
            try:
                source_id = data.get("source_id", str(idx))
                incident = await self.ingest_incident(data, source_system, source_id)
                incidents.append(incident)
            except Exception as e:
                errors.append({"index": idx, "error": str(e)})
                logger.warning(f"Failed to ingest incident {idx}: {e}")

        return {
            "total": len(incidents_data),
            "successful": len(incidents),
            "failed": len(errors),
            "errors": errors,
        }

    def _generate_incident_id(self, source_system: str, source_id: str) -> str:
        """Generate unique incident ID."""
        hash_input = f"{source_system}:{source_id}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _parse_timestamp(self, timestamp_value: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(timestamp_value, datetime):
            return timestamp_value
        if isinstance(timestamp_value, str):
            try:
                return datetime.fromisoformat(timestamp_value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.utcnow()

    def _parse_location(self, data: dict[str, Any]) -> GeoPoint:
        """Parse location from incident data."""
        lat = data.get("latitude", 0.0)
        lon = data.get("longitude", 0.0)

        # Try nested location object
        if "location" in data:
            loc = data["location"]
            lat = loc.get("latitude", loc.get("lat", lat))
            lon = loc.get("longitude", loc.get("lon", lon))

        return GeoPoint(
            latitude=float(lat),
            longitude=float(lon),
            h3_index=self._compute_h3_index(lat, lon),
        )

    def _compute_h3_index(self, lat: float, lon: float, resolution: int = 8) -> str | None:
        """Compute H3 index for location."""
        try:
            # H3 index computation (simplified - would use h3 library in production)
            # Format: resolution + geohash-like encoding
            lat_part = int((lat + 90) * 1000) % 10000
            lon_part = int((lon + 180) * 1000) % 10000
            return f"{resolution:x}{lat_part:04x}{lon_part:04x}"
        except Exception:
            return None

    def _classify_crime(self, crime_type: str, description: str) -> CrimeCategory:
        """Classify crime into category."""
        crime_lower = (crime_type + " " + description).lower()

        violent_keywords = [
            "assault", "battery", "homicide", "murder", "robbery",
            "rape", "kidnapping", "shooting", "stabbing",
        ]
        property_keywords = [
            "burglary", "theft", "larceny", "vandalism", "arson",
            "trespassing", "breaking", "entering",
        ]
        drug_keywords = ["drug", "narcotic", "controlled substance", "possession"]
        traffic_keywords = ["traffic", "dui", "dwi", "speeding", "accident"]
        disorder_keywords = ["disorderly", "disturbance", "noise", "loitering"]

        if any(kw in crime_lower for kw in violent_keywords):
            return CrimeCategory.VIOLENT
        if any(kw in crime_lower for kw in property_keywords):
            return CrimeCategory.PROPERTY
        if any(kw in crime_lower for kw in drug_keywords):
            return CrimeCategory.DRUG
        if any(kw in crime_lower for kw in traffic_keywords):
            return CrimeCategory.TRAFFIC
        if any(kw in crime_lower for kw in disorder_keywords):
            return CrimeCategory.DISORDER

        return CrimeCategory.OTHER

    def _assess_severity(self, data: dict[str, Any]) -> SeverityLevel:
        """Assess incident severity."""
        # Check explicit severity
        if "severity" in data:
            try:
                return SeverityLevel(data["severity"])
            except ValueError:
                pass

        # Assess based on factors
        score = 0

        if data.get("weapon_involved"):
            score += 3
        if data.get("victim_count", 0) > 0:
            score += data.get("victim_count", 0)
        if data.get("arrest_made"):
            score += 1
        if data.get("gang_related"):
            score += 2
        if data.get("domestic_violence"):
            score += 1

        crime_type = data.get("crime_type", "").lower()
        if "homicide" in crime_type or "murder" in crime_type:
            score += 5
        elif "assault" in crime_type or "robbery" in crime_type:
            score += 3

        if score >= 5:
            return SeverityLevel.CRITICAL
        if score >= 3:
            return SeverityLevel.HIGH
        if score >= 1:
            return SeverityLevel.MEDIUM
        return SeverityLevel.LOW

    def _validate_incident(self, incident: IncidentRecord) -> None:
        """Validate incident data."""
        errors = []

        if not incident.incident_number:
            errors.append("Missing incident number")

        if incident.location.latitude == 0 and incident.location.longitude == 0:
            errors.append("Invalid location coordinates")

        if incident.timestamp > datetime.utcnow():
            errors.append("Timestamp is in the future")

        if errors:
            logger.warning(f"Incident validation warnings for {incident.id}: {errors}")

    async def _create_lineage_record(
        self,
        incident: IncidentRecord,
        source_system: str,
        source_id: str,
    ) -> None:
        """Create data lineage record for incident."""
        lineage = DataLineageRecord(
            id=str(uuid.uuid4()),
            record_id=incident.id,
            record_type="incident",
            source_system=source_system,
            source_id=source_id,
            source_timestamp=incident.timestamp,
            transformations=[
                {
                    "type": "ingestion",
                    "timestamp": datetime.utcnow().isoformat(),
                    "details": {"crime_category": incident.crime_category.value},
                }
            ],
            current_location="elasticsearch",
            current_partition=incident.partition_month,
            created_by="data_lake_service",
        )

        await self.repository.store_lineage_record(lineage)

    async def _ensure_partition(self, partition_key: str, timestamp: datetime) -> None:
        """Ensure partition exists for the given key."""
        existing = await self.repository.get_partition(partition_key)
        if existing:
            return

        # Create new partition
        year, month = partition_key.split("-")
        start_date = datetime(int(year), int(month), 1)

        # Calculate end date (last day of month)
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1) - timedelta(seconds=1)

        partition = CrimeDataPartition(
            partition_key=partition_key,
            partition_type=PartitionType.MONTHLY,
            start_date=start_date,
            end_date=end_date,
        )

        await self.repository.create_partition(partition)
        logger.info(f"Created partition {partition_key}")

    async def _update_offender_profile(
        self,
        offender_id: str,
        incident: IncidentRecord,
    ) -> None:
        """Update offender profile with new incident."""
        profile = await self.repository.get_offender_profile(offender_id)

        if profile:
            # Update existing profile
            profile.total_incidents += 1
            profile.incident_ids.append(incident.id)
            profile.last_seen = incident.timestamp

            # Update crime breakdown
            category = incident.crime_category.value
            profile.crime_categories[category] = profile.crime_categories.get(category, 0) + 1
            profile.crime_types[incident.crime_type] = (
                profile.crime_types.get(incident.crime_type, 0) + 1
            )

            # Update severity counts
            if incident.severity == SeverityLevel.CRITICAL:
                profile.critical_incidents += 1
            elif incident.severity == SeverityLevel.HIGH:
                profile.high_incidents += 1

            if incident.crime_category == CrimeCategory.VIOLENT:
                profile.violent_incidents += 1

            # Recalculate risk scores
            profile = self._calculate_risk_scores(profile)
            profile.last_updated = datetime.utcnow()

        else:
            # Create new profile
            profile = OffenderProfile(
                id=offender_id,
                first_seen=incident.timestamp,
                last_seen=incident.timestamp,
                total_incidents=1,
                incident_ids=[incident.id],
                crime_categories={incident.crime_category.value: 1},
                crime_types={incident.crime_type: 1},
                critical_incidents=1 if incident.severity == SeverityLevel.CRITICAL else 0,
                high_incidents=1 if incident.severity == SeverityLevel.HIGH else 0,
                violent_incidents=1 if incident.crime_category == CrimeCategory.VIOLENT else 0,
                primary_locations=[incident.location],
                primary_beats=[incident.beat] if incident.beat else [],
            )
            profile = self._calculate_risk_scores(profile)

        await self.repository.store_offender_profile(profile)

    def _calculate_risk_scores(self, profile: OffenderProfile) -> OffenderProfile:
        """Calculate risk scores for offender profile."""
        # Recidivism risk based on incident frequency and severity
        base_risk = min(1.0, profile.total_incidents / 10)
        severity_factor = (
            profile.critical_incidents * 0.3
            + profile.high_incidents * 0.2
            + profile.violent_incidents * 0.2
        ) / max(1, profile.total_incidents)

        profile.recidivism_risk_score = min(1.0, base_risk + severity_factor)

        # Violence risk based on violent incidents
        profile.violence_risk_score = min(
            1.0, profile.violent_incidents / max(1, profile.total_incidents)
        )

        # Determine escalation trend
        if profile.total_incidents >= 3:
            recent_severe = profile.critical_incidents + profile.high_incidents
            if recent_severe / profile.total_incidents > 0.5:
                profile.escalation_trend = "escalating"
            elif recent_severe / profile.total_incidents < 0.2:
                profile.escalation_trend = "de-escalating"
            else:
                profile.escalation_trend = "stable"

        return profile

    # ==================== Historical Analytics ====================

    async def compute_daily_aggregate(
        self,
        date: datetime,
        jurisdiction: str,
        crime_category: CrimeCategory | None = None,
        beat: str | None = None,
    ) -> HistoricalAggregate:
        """
        Compute daily aggregate for a specific date.

        Args:
            date: Date to compute aggregate for
            jurisdiction: Jurisdiction code
            crime_category: Optional crime category filter
            beat: Optional beat filter

        Returns:
            Computed aggregate
        """
        start_date = datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)

        return await self._compute_aggregate(
            aggregate_type="daily",
            start_date=start_date,
            end_date=end_date,
            jurisdiction=jurisdiction,
            crime_category=crime_category,
            beat=beat,
        )

    async def compute_monthly_aggregate(
        self,
        year: int,
        month: int,
        jurisdiction: str,
        crime_category: CrimeCategory | None = None,
    ) -> HistoricalAggregate:
        """
        Compute monthly aggregate.

        Args:
            year: Year
            month: Month (1-12)
            jurisdiction: Jurisdiction code
            crime_category: Optional crime category filter

        Returns:
            Computed aggregate
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)

        return await self._compute_aggregate(
            aggregate_type="monthly",
            start_date=start_date,
            end_date=end_date,
            jurisdiction=jurisdiction,
            crime_category=crime_category,
        )

    async def compute_yearly_aggregate(
        self,
        year: int,
        jurisdiction: str,
        crime_category: CrimeCategory | None = None,
    ) -> HistoricalAggregate:
        """
        Compute yearly aggregate.

        Args:
            year: Year
            jurisdiction: Jurisdiction code
            crime_category: Optional crime category filter

        Returns:
            Computed aggregate
        """
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)

        return await self._compute_aggregate(
            aggregate_type="yearly",
            start_date=start_date,
            end_date=end_date,
            jurisdiction=jurisdiction,
            crime_category=crime_category,
        )

    async def _compute_aggregate(
        self,
        aggregate_type: str,
        start_date: datetime,
        end_date: datetime,
        jurisdiction: str,
        crime_category: CrimeCategory | None = None,
        beat: str | None = None,
    ) -> HistoricalAggregate:
        """Compute aggregate for a time period."""
        # Query incidents
        incidents, total = await self.repository.query_incidents(
            start_date=start_date,
            end_date=end_date,
            jurisdiction=jurisdiction,
            crime_category=crime_category,
            beat=beat,
            limit=100000,
        )

        # Initialize counters
        incidents_by_category: dict[str, int] = {}
        incidents_by_type: dict[str, int] = {}
        incidents_by_severity: dict[str, int] = {}
        incidents_by_hour: dict[int, int] = {h: 0 for h in range(24)}
        incidents_by_day: dict[int, int] = {d: 0 for d in range(7)}
        hotspot_counts: dict[str, int] = {}

        violent_count = 0
        property_count = 0
        arrests_count = 0

        for incident in incidents:
            # Category breakdown
            cat = incident.crime_category.value
            incidents_by_category[cat] = incidents_by_category.get(cat, 0) + 1

            # Type breakdown
            incidents_by_type[incident.crime_type] = (
                incidents_by_type.get(incident.crime_type, 0) + 1
            )

            # Severity breakdown
            sev = incident.severity.value
            incidents_by_severity[sev] = incidents_by_severity.get(sev, 0) + 1

            # Temporal breakdown
            incidents_by_hour[incident.timestamp.hour] += 1
            incidents_by_day[incident.timestamp.weekday()] += 1

            # Hotspot tracking
            if incident.location.h3_index:
                h3 = incident.location.h3_index
                hotspot_counts[h3] = hotspot_counts.get(h3, 0) + 1

            # Category counts
            if incident.crime_category == CrimeCategory.VIOLENT:
                violent_count += 1
            elif incident.crime_category == CrimeCategory.PROPERTY:
                property_count += 1

            if incident.arrest_made:
                arrests_count += 1

        # Get top hotspots
        sorted_hotspots = sorted(hotspot_counts.items(), key=lambda x: x[1], reverse=True)
        top_hotspots = [h[0] for h in sorted_hotspots[:20]]

        # Calculate clearance rate
        clearance_rate = arrests_count / total if total > 0 else 0.0

        # Generate aggregate ID
        agg_id = f"{aggregate_type}_{jurisdiction}_{start_date.strftime('%Y%m%d')}"
        if crime_category:
            agg_id += f"_{crime_category.value}"
        if beat:
            agg_id += f"_{beat}"

        aggregate = HistoricalAggregate(
            id=agg_id,
            aggregate_type=aggregate_type,
            period_start=start_date,
            period_end=end_date,
            jurisdiction=jurisdiction,
            beat=beat,
            crime_category=crime_category,
            total_incidents=total,
            violent_incidents=violent_count,
            property_incidents=property_count,
            arrests_made=arrests_count,
            clearance_rate=clearance_rate,
            incidents_by_category=incidents_by_category,
            incidents_by_type=incidents_by_type,
            incidents_by_severity=incidents_by_severity,
            incidents_by_hour=incidents_by_hour,
            incidents_by_day_of_week=incidents_by_day,
            hotspot_h3_indices=top_hotspots,
            hotspot_counts=dict(sorted_hotspots[:20]),
        )

        # Store aggregate
        await self.repository.store_aggregate(aggregate)

        return aggregate

    async def get_trend_analysis(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "monthly",
        crime_category: CrimeCategory | None = None,
    ) -> dict[str, Any]:
        """
        Get trend analysis for a time period.

        Args:
            jurisdiction: Jurisdiction code
            start_date: Start date
            end_date: End date
            granularity: Aggregation granularity
            crime_category: Optional crime category filter

        Returns:
            Trend analysis data
        """
        aggregates = await self.repository.get_aggregates(
            aggregate_type=granularity,
            jurisdiction=jurisdiction,
            start_date=start_date,
            end_date=end_date,
            crime_category=crime_category,
        )

        if not aggregates:
            return {
                "periods": [],
                "totals": [],
                "trend": "insufficient_data",
                "percent_change": 0.0,
            }

        periods = []
        totals = []

        for agg in aggregates:
            periods.append(agg.period_start.isoformat())
            totals.append(agg.total_incidents)

        # Calculate trend
        if len(totals) >= 2:
            first_half = sum(totals[: len(totals) // 2])
            second_half = sum(totals[len(totals) // 2 :])

            if first_half > 0:
                percent_change = ((second_half - first_half) / first_half) * 100
            else:
                percent_change = 0.0

            if percent_change > 10:
                trend = "increasing"
            elif percent_change < -10:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
            percent_change = 0.0

        return {
            "periods": periods,
            "totals": totals,
            "trend": trend,
            "percent_change": round(percent_change, 2),
            "aggregates": [agg.model_dump() for agg in aggregates],
        }

    # ==================== Multi-Year Heatmaps ====================

    async def generate_multiyear_heatmap(
        self,
        jurisdiction: str,
        start_year: int,
        end_year: int,
        crime_category: CrimeCategory | None = None,
        resolution: int = 8,
    ) -> MultiYearHeatmapData:
        """
        Generate multi-year heatmap data.

        Args:
            jurisdiction: Jurisdiction code
            start_year: Start year
            end_year: End year
            crime_category: Optional crime category filter
            resolution: H3 resolution (7-10)

        Returns:
            Multi-year heatmap data
        """
        years = list(range(start_year, end_year + 1))
        yearly_heatmaps: dict[int, list[HeatmapCell]] = {}
        combined_counts: dict[str, int] = {}
        yearly_totals: dict[int, int] = {}

        for year in years:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)

            incidents, total = await self.repository.query_incidents(
                start_date=start_date,
                end_date=end_date,
                jurisdiction=jurisdiction,
                crime_category=crime_category,
                limit=100000,
            )

            yearly_totals[year] = total

            # Aggregate by H3 index
            h3_counts: dict[str, int] = {}
            h3_coords: dict[str, tuple[float, float]] = {}

            for incident in incidents:
                h3_index = incident.location.h3_index
                if h3_index:
                    h3_counts[h3_index] = h3_counts.get(h3_index, 0) + 1
                    combined_counts[h3_index] = combined_counts.get(h3_index, 0) + 1
                    h3_coords[h3_index] = (
                        incident.location.latitude,
                        incident.location.longitude,
                    )

            # Create heatmap cells for this year
            max_count = max(h3_counts.values()) if h3_counts else 1
            cells = []
            for h3_index, count in h3_counts.items():
                lat, lon = h3_coords.get(h3_index, (0, 0))
                cells.append(
                    HeatmapCell(
                        h3_index=h3_index,
                        latitude=lat,
                        longitude=lon,
                        value=float(count),
                        incident_count=count,
                        normalized_value=count / max_count,
                    )
                )

            yearly_heatmaps[year] = sorted(cells, key=lambda x: x.value, reverse=True)[:500]

        # Create combined heatmap
        max_combined = max(combined_counts.values()) if combined_counts else 1
        combined_cells = []

        # Get coordinates from most recent year's data
        all_coords: dict[str, tuple[float, float]] = {}
        for year in reversed(years):
            for cell in yearly_heatmaps.get(year, []):
                if cell.h3_index not in all_coords:
                    all_coords[cell.h3_index] = (cell.latitude, cell.longitude)

        for h3_index, count in combined_counts.items():
            lat, lon = all_coords.get(h3_index, (0, 0))
            combined_cells.append(
                HeatmapCell(
                    h3_index=h3_index,
                    latitude=lat,
                    longitude=lon,
                    value=float(count),
                    incident_count=count,
                    normalized_value=count / max_combined,
                )
            )

        combined_heatmap = sorted(combined_cells, key=lambda x: x.value, reverse=True)[:500]

        # Identify hotspot evolution
        persistent_hotspots = []
        emerging_hotspots = []
        declining_hotspots = []

        # Hotspots present in all years
        all_year_h3s = [set(c.h3_index for c in yearly_heatmaps.get(y, [])) for y in years]
        if all_year_h3s:
            persistent_set = all_year_h3s[0]
            for h3_set in all_year_h3s[1:]:
                persistent_set = persistent_set.intersection(h3_set)
            persistent_hotspots = list(persistent_set)[:20]

        # Compare first and last year for emerging/declining
        if len(years) >= 2:
            first_year_counts = {
                c.h3_index: c.incident_count for c in yearly_heatmaps.get(years[0], [])
            }
            last_year_counts = {
                c.h3_index: c.incident_count for c in yearly_heatmaps.get(years[-1], [])
            }

            for h3_index in last_year_counts:
                first_count = first_year_counts.get(h3_index, 0)
                last_count = last_year_counts[h3_index]

                if last_count > first_count * 1.5:
                    emerging_hotspots.append(h3_index)
                elif first_count > last_count * 1.5:
                    declining_hotspots.append(h3_index)

        # Calculate overall trend
        total_incidents = sum(yearly_totals.values())
        if len(years) >= 2:
            first_year_total = yearly_totals.get(years[0], 0)
            last_year_total = yearly_totals.get(years[-1], 0)

            if first_year_total > 0:
                trend_change = ((last_year_total - first_year_total) / first_year_total) * 100
            else:
                trend_change = 0.0

            if trend_change > 10:
                trend = "increasing"
            elif trend_change < -10:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
            trend_change = 0.0

        # Generate ID
        heatmap_id = f"heatmap_{jurisdiction}_{start_year}_{end_year}"
        if crime_category:
            heatmap_id += f"_{crime_category.value}"

        heatmap_data = MultiYearHeatmapData(
            id=heatmap_id,
            jurisdiction=jurisdiction,
            crime_category=crime_category,
            resolution=resolution,
            start_year=start_year,
            end_year=end_year,
            years=years,
            yearly_heatmaps=yearly_heatmaps,
            combined_heatmap=combined_heatmap,
            persistent_hotspots=persistent_hotspots[:20],
            emerging_hotspots=emerging_hotspots[:20],
            declining_hotspots=declining_hotspots[:20],
            total_incidents=total_incidents,
            incidents_by_year=yearly_totals,
            trend=trend,
            trend_percent_change=round(trend_change, 2),
        )

        # Store heatmap data
        await self.repository.store_multiyear_heatmap(heatmap_data)

        return heatmap_data

    # ==================== Repeat Offender Analytics ====================

    async def get_repeat_offender_analytics(
        self,
        jurisdiction: str | None = None,
        min_incidents: int = 3,
        days_back: int = 365,
    ) -> dict[str, Any]:
        """
        Get repeat offender analytics.

        Args:
            jurisdiction: Optional jurisdiction filter
            min_incidents: Minimum incident threshold
            days_back: Days to look back

        Returns:
            Repeat offender analytics data
        """
        offenders = await self.repository.get_repeat_offenders(
            min_incidents=min_incidents,
            days_back=days_back,
            limit=100,
        )

        if not offenders:
            return {
                "total_repeat_offenders": 0,
                "high_risk_count": 0,
                "escalating_count": 0,
                "offenders": [],
                "risk_distribution": {},
                "category_breakdown": {},
            }

        # Calculate analytics
        high_risk_count = sum(1 for o in offenders if o.recidivism_risk_score >= 0.7)
        escalating_count = sum(1 for o in offenders if o.escalation_trend == "escalating")

        # Risk distribution
        risk_distribution = {
            "critical": sum(1 for o in offenders if o.recidivism_risk_score >= 0.8),
            "high": sum(1 for o in offenders if 0.6 <= o.recidivism_risk_score < 0.8),
            "medium": sum(1 for o in offenders if 0.4 <= o.recidivism_risk_score < 0.6),
            "low": sum(1 for o in offenders if o.recidivism_risk_score < 0.4),
        }

        # Category breakdown
        category_breakdown: dict[str, int] = {}
        for offender in offenders:
            for cat, count in offender.crime_categories.items():
                category_breakdown[cat] = category_breakdown.get(cat, 0) + count

        return {
            "total_repeat_offenders": len(offenders),
            "high_risk_count": high_risk_count,
            "escalating_count": escalating_count,
            "offenders": [o.model_dump() for o in offenders[:50]],
            "risk_distribution": risk_distribution,
            "category_breakdown": category_breakdown,
        }

    async def get_offender_timeline(self, offender_id: str) -> dict[str, Any]:
        """
        Get detailed timeline for an offender.

        Args:
            offender_id: Offender ID

        Returns:
            Offender timeline data
        """
        profile = await self.repository.get_offender_profile(offender_id)
        if not profile:
            return {"error": "Offender not found"}

        # Get all incidents
        incidents = []
        for incident_id in profile.incident_ids:
            incident = await self.repository.get_incident(incident_id)
            if incident:
                incidents.append(incident)

        # Sort by timestamp
        incidents.sort(key=lambda x: x.timestamp)

        # Build timeline
        timeline = []
        for incident in incidents:
            timeline.append({
                "date": incident.timestamp.isoformat(),
                "incident_id": incident.id,
                "crime_type": incident.crime_type,
                "crime_category": incident.crime_category.value,
                "severity": incident.severity.value,
                "location": {
                    "latitude": incident.location.latitude,
                    "longitude": incident.location.longitude,
                },
                "beat": incident.beat,
                "arrest_made": incident.arrest_made,
            })

        # Get network
        network = await self.repository.get_offender_network(offender_id)

        return {
            "profile": profile.model_dump(),
            "timeline": timeline,
            "network": network,
            "total_incidents": len(incidents),
            "date_range": {
                "first": incidents[0].timestamp.isoformat() if incidents else None,
                "last": incidents[-1].timestamp.isoformat() if incidents else None,
            },
        }

    # ==================== Data Governance ====================

    async def compute_quality_metrics(self, partition_key: str) -> DataQualityMetric:
        """
        Compute data quality metrics for a partition.

        Args:
            partition_key: Partition key

        Returns:
            Quality metrics
        """
        incidents = await self.repository.get_incidents_by_partition(partition_key)

        total = len(incidents)
        complete = 0
        validated = 0
        issues: list[dict[str, Any]] = []

        # Check completeness and accuracy
        for incident in incidents:
            is_complete = True
            is_valid = True

            # Check required fields
            if not incident.incident_number:
                is_complete = False
                issues.append({"id": incident.id, "issue": "missing_incident_number"})

            if incident.location.latitude == 0 and incident.location.longitude == 0:
                is_complete = False
                issues.append({"id": incident.id, "issue": "invalid_location"})

            # Validate data
            if incident.timestamp > datetime.utcnow():
                is_valid = False
                issues.append({"id": incident.id, "issue": "future_timestamp"})

            if is_complete:
                complete += 1
            if is_valid:
                validated += 1

        # Calculate scores
        completeness_score = complete / total if total > 0 else 1.0
        accuracy_score = validated / total if total > 0 else 1.0

        # Check for duplicates (simplified)
        incident_numbers = [i.incident_number for i in incidents]
        duplicates = len(incident_numbers) - len(set(incident_numbers))
        consistency_score = 1.0 - (duplicates / total) if total > 0 else 1.0

        # Overall score
        overall_score = (completeness_score + accuracy_score + consistency_score) / 3

        metric = DataQualityMetric(
            id=f"quality_{partition_key}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            partition_key=partition_key,
            total_records=total,
            complete_records=complete,
            completeness_score=completeness_score,
            validated_records=validated,
            accuracy_score=accuracy_score,
            duplicate_records=duplicates,
            consistency_score=consistency_score,
            timeliness_score=1.0,  # Would calculate based on ingestion delay
            overall_quality_score=overall_score,
            issues=issues[:100],  # Limit issues stored
        )

        await self.repository.store_quality_metric(metric)
        return metric

    async def apply_retention_policy(
        self,
        policy: DataRetentionPolicy,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """
        Apply a data retention policy.

        Args:
            policy: Retention policy to apply
            dry_run: If True, only report what would be done

        Returns:
            Application result
        """
        cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_days)

        # Find affected partitions
        partitions = await self.repository.list_partitions(is_active=True)
        affected_partitions = [p for p in partitions if p.end_date < cutoff_date]

        result = {
            "policy_id": policy.id,
            "policy_name": policy.name,
            "action": policy.action.value,
            "cutoff_date": cutoff_date.isoformat(),
            "affected_partitions": len(affected_partitions),
            "affected_records": sum(p.record_count for p in affected_partitions),
            "dry_run": dry_run,
            "partitions": [p.partition_key for p in affected_partitions],
        }

        if not dry_run and affected_partitions:
            for partition in affected_partitions:
                if policy.action == RetentionAction.ARCHIVE:
                    # Mark as archived
                    await self.repository.update_partition_stats(
                        partition.partition_key,
                        partition.record_count,
                        partition.size_bytes,
                    )
                    logger.info(f"Archived partition {partition.partition_key}")

                elif policy.action == RetentionAction.DELETE:
                    # Would delete partition data
                    logger.info(f"Would delete partition {partition.partition_key}")

                elif policy.action == RetentionAction.ANONYMIZE:
                    # Would anonymize PII
                    logger.info(f"Would anonymize partition {partition.partition_key}")

        return result

    async def get_data_lake_stats(self) -> DataLakeStats:
        """
        Get data lake statistics.

        Returns:
            Data lake statistics
        """
        return await self.repository.get_data_lake_stats()

    async def get_data_lineage(self, record_id: str) -> list[DataLineageRecord]:
        """
        Get data lineage for a record.

        Args:
            record_id: Record ID

        Returns:
            List of lineage records
        """
        return await self.repository.get_lineage(record_id)

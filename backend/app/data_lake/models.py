"""
Data Lake Models for G3TI RTCC-UIP.

This module defines the core data models for the data lake including:
- Incident records with full crime data
- Partitioned storage schemas
- Historical aggregates
- Offender profiles for repeat offender analytics
- Data retention policies
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CrimeCategory(str, Enum):
    """Crime category classification."""

    VIOLENT = "violent"
    PROPERTY = "property"
    DRUG = "drug"
    TRAFFIC = "traffic"
    DISORDER = "disorder"
    OTHER = "other"


class SeverityLevel(str, Enum):
    """Incident severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PartitionType(str, Enum):
    """Data partition types."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RetentionAction(str, Enum):
    """Data retention actions."""

    ARCHIVE = "archive"
    DELETE = "delete"
    ANONYMIZE = "anonymize"


class DataLakeBaseModel(BaseModel):
    """Base model for all data lake schemas."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class GeoPoint(DataLakeBaseModel):
    """Geographic point with coordinates."""

    latitude: float = Field(ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(ge=-180, le=180, description="Longitude coordinate")
    h3_index: str | None = Field(default=None, description="H3 hexagonal index for spatial queries")
    geohash: str | None = Field(default=None, description="Geohash for spatial indexing")


class IncidentRecord(DataLakeBaseModel):
    """
    Core incident record for the data lake.

    Represents a single crime/incident with all associated metadata
    for historical analytics and pattern detection.
    """

    id: str = Field(description="Unique incident identifier")
    incident_number: str = Field(description="Official incident/case number")
    timestamp: datetime = Field(description="Incident occurrence timestamp")
    reported_at: datetime = Field(description="When incident was reported")
    ingested_at: datetime = Field(
        default_factory=datetime.utcnow, description="When record was ingested into data lake"
    )

    # Classification
    crime_category: CrimeCategory = Field(description="Primary crime category")
    crime_type: str = Field(description="Specific crime type code")
    crime_description: str = Field(description="Human-readable crime description")
    ucr_code: str | None = Field(default=None, description="UCR/NIBRS code")
    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM, description="Incident severity")

    # Location
    location: GeoPoint = Field(description="Incident location")
    address: str | None = Field(default=None, description="Street address")
    beat: str | None = Field(default=None, description="Police beat/zone")
    district: str | None = Field(default=None, description="Police district")
    jurisdiction: str = Field(description="Jurisdiction code")

    # Parties involved
    suspect_count: int = Field(default=0, ge=0, description="Number of suspects")
    victim_count: int = Field(default=0, ge=0, description="Number of victims")
    arrest_made: bool = Field(default=False, description="Whether arrest was made")
    offender_ids: list[str] = Field(default_factory=list, description="Known offender IDs")

    # Additional data
    weapon_involved: bool = Field(default=False, description="Whether weapon was involved")
    weapon_type: str | None = Field(default=None, description="Type of weapon if applicable")
    domestic_violence: bool = Field(default=False, description="Domestic violence flag")
    gang_related: bool = Field(default=False, description="Gang-related flag")

    # Source tracking
    source_system: str = Field(description="Source system (CAD, RMS, etc.)")
    source_id: str = Field(description="ID in source system")

    # Partition keys
    partition_date: str = Field(description="Partition date key (YYYY-MM-DD)")
    partition_month: str = Field(description="Partition month key (YYYY-MM)")
    partition_year: int = Field(description="Partition year")


class OffenderProfile(DataLakeBaseModel):
    """
    Offender profile for repeat offender analytics.

    Aggregates offender information across incidents for
    recidivism analysis and risk scoring.
    """

    id: str = Field(description="Unique offender identifier")
    first_seen: datetime = Field(description="First incident involvement date")
    last_seen: datetime = Field(description="Most recent incident involvement date")

    # Incident history
    total_incidents: int = Field(default=0, ge=0, description="Total incident count")
    incident_ids: list[str] = Field(default_factory=list, description="List of incident IDs")

    # Crime breakdown
    crime_categories: dict[str, int] = Field(
        default_factory=dict, description="Count by crime category"
    )
    crime_types: dict[str, int] = Field(default_factory=dict, description="Count by crime type")

    # Severity metrics
    critical_incidents: int = Field(default=0, ge=0, description="Critical severity count")
    high_incidents: int = Field(default=0, ge=0, description="High severity count")
    violent_incidents: int = Field(default=0, ge=0, description="Violent crime count")

    # Temporal patterns
    avg_days_between_incidents: float | None = Field(
        default=None, description="Average days between incidents"
    )
    incident_frequency_30d: float = Field(
        default=0.0, description="Incidents per 30 days (recent)"
    )
    incident_frequency_90d: float = Field(
        default=0.0, description="Incidents per 90 days (recent)"
    )
    incident_frequency_365d: float = Field(
        default=0.0, description="Incidents per 365 days"
    )

    # Geographic patterns
    primary_locations: list[GeoPoint] = Field(
        default_factory=list, description="Most frequent incident locations"
    )
    primary_beats: list[str] = Field(default_factory=list, description="Most frequent beats")
    geographic_spread: float = Field(
        default=0.0, description="Geographic spread in km"
    )

    # Risk scoring
    recidivism_risk_score: float = Field(
        default=0.0, ge=0, le=1, description="Recidivism risk score (0-1)"
    )
    violence_risk_score: float = Field(
        default=0.0, ge=0, le=1, description="Violence risk score (0-1)"
    )
    escalation_trend: str = Field(
        default="stable", description="Trend: escalating, stable, de-escalating"
    )

    # Associations
    known_associates: list[str] = Field(
        default_factory=list, description="Known associate offender IDs"
    )
    gang_affiliation: str | None = Field(default=None, description="Known gang affiliation")

    # Metadata
    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="Last profile update"
    )


class HistoricalAggregate(DataLakeBaseModel):
    """
    Pre-computed historical aggregate for analytics.

    Stores aggregated statistics for efficient querying
    of historical trends and patterns.
    """

    id: str = Field(description="Aggregate record ID")
    aggregate_type: str = Field(description="Type: daily, weekly, monthly, yearly")
    period_start: datetime = Field(description="Period start timestamp")
    period_end: datetime = Field(description="Period end timestamp")

    # Dimensions
    jurisdiction: str = Field(description="Jurisdiction code")
    beat: str | None = Field(default=None, description="Beat/zone if applicable")
    district: str | None = Field(default=None, description="District if applicable")
    crime_category: CrimeCategory | None = Field(
        default=None, description="Crime category if filtered"
    )

    # Metrics
    total_incidents: int = Field(default=0, description="Total incident count")
    violent_incidents: int = Field(default=0, description="Violent crime count")
    property_incidents: int = Field(default=0, description="Property crime count")
    arrests_made: int = Field(default=0, description="Total arrests")
    clearance_rate: float = Field(default=0.0, description="Case clearance rate")

    # Breakdown by category
    incidents_by_category: dict[str, int] = Field(
        default_factory=dict, description="Incidents by crime category"
    )
    incidents_by_type: dict[str, int] = Field(
        default_factory=dict, description="Incidents by crime type"
    )
    incidents_by_severity: dict[str, int] = Field(
        default_factory=dict, description="Incidents by severity"
    )

    # Temporal breakdown
    incidents_by_hour: dict[int, int] = Field(
        default_factory=dict, description="Incidents by hour of day"
    )
    incidents_by_day_of_week: dict[int, int] = Field(
        default_factory=dict, description="Incidents by day of week"
    )

    # Comparison metrics
    previous_period_total: int | None = Field(
        default=None, description="Previous period total for comparison"
    )
    percent_change: float | None = Field(
        default=None, description="Percent change from previous period"
    )
    year_over_year_change: float | None = Field(
        default=None, description="Year-over-year percent change"
    )

    # Heatmap data
    hotspot_h3_indices: list[str] = Field(
        default_factory=list, description="Top hotspot H3 indices"
    )
    hotspot_counts: dict[str, int] = Field(
        default_factory=dict, description="Incident counts by H3 index"
    )

    # Metadata
    computed_at: datetime = Field(
        default_factory=datetime.utcnow, description="When aggregate was computed"
    )


class CrimeDataPartition(DataLakeBaseModel):
    """
    Partition metadata for crime data storage.

    Tracks partition boundaries and statistics for
    efficient data management and querying.
    """

    partition_key: str = Field(description="Partition key (e.g., 2024-01)")
    partition_type: PartitionType = Field(description="Partition granularity")
    start_date: datetime = Field(description="Partition start date")
    end_date: datetime = Field(description="Partition end date")

    # Statistics
    record_count: int = Field(default=0, description="Number of records")
    size_bytes: int = Field(default=0, description="Storage size in bytes")

    # Status
    is_active: bool = Field(default=True, description="Whether partition is active")
    is_archived: bool = Field(default=False, description="Whether partition is archived")
    archive_location: str | None = Field(default=None, description="Archive storage location")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PartitionMetadata(DataLakeBaseModel):
    """
    Extended partition metadata with quality metrics.
    """

    partition: CrimeDataPartition = Field(description="Base partition info")

    # Quality metrics
    completeness_score: float = Field(
        default=1.0, ge=0, le=1, description="Data completeness score"
    )
    accuracy_score: float = Field(
        default=1.0, ge=0, le=1, description="Data accuracy score"
    )
    validation_errors: int = Field(default=0, description="Number of validation errors")

    # Processing status
    last_etl_run: datetime | None = Field(default=None, description="Last ETL processing time")
    etl_status: str = Field(default="pending", description="ETL status")
    etl_errors: list[str] = Field(default_factory=list, description="ETL error messages")


class DataRetentionPolicy(DataLakeBaseModel):
    """
    Data retention policy configuration.

    Defines how long data is retained and what actions
    to take when retention period expires.
    """

    id: str = Field(description="Policy ID")
    name: str = Field(description="Policy name")
    description: str = Field(description="Policy description")

    # Scope
    applies_to: list[str] = Field(description="Data types this policy applies to")
    jurisdiction: str | None = Field(default=None, description="Jurisdiction filter")
    crime_categories: list[CrimeCategory] | None = Field(
        default=None, description="Crime category filter"
    )

    # Retention rules
    retention_days: int = Field(ge=1, description="Days to retain active data")
    archive_after_days: int | None = Field(
        default=None, description="Days before archiving"
    )
    delete_after_days: int | None = Field(
        default=None, description="Days before deletion"
    )
    action: RetentionAction = Field(description="Action when retention expires")

    # Compliance
    legal_hold: bool = Field(default=False, description="Whether under legal hold")
    cjis_compliant: bool = Field(default=True, description="CJIS compliance flag")
    audit_required: bool = Field(default=True, description="Whether audit logging required")

    # Status
    is_active: bool = Field(default=True, description="Whether policy is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DataLakeConfig(DataLakeBaseModel):
    """
    Data lake configuration settings.
    """

    # Storage settings
    default_partition_type: PartitionType = Field(
        default=PartitionType.MONTHLY, description="Default partition granularity"
    )
    max_partition_size_gb: float = Field(
        default=10.0, description="Max partition size in GB"
    )
    compression_enabled: bool = Field(default=True, description="Enable compression")
    compression_algorithm: str = Field(default="zstd", description="Compression algorithm")

    # Retention defaults
    default_retention_days: int = Field(default=2555, description="Default retention (7 years)")
    archive_enabled: bool = Field(default=True, description="Enable archiving")
    archive_after_days: int = Field(default=365, description="Days before archiving")

    # Performance settings
    query_timeout_seconds: int = Field(default=300, description="Query timeout")
    max_concurrent_queries: int = Field(default=10, description="Max concurrent queries")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL")

    # Quality settings
    validation_enabled: bool = Field(default=True, description="Enable data validation")
    deduplication_enabled: bool = Field(default=True, description="Enable deduplication")
    quality_threshold: float = Field(
        default=0.95, ge=0, le=1, description="Minimum quality score"
    )


class DataLakeStats(DataLakeBaseModel):
    """
    Data lake statistics and health metrics.
    """

    total_records: int = Field(default=0, description="Total records in data lake")
    total_partitions: int = Field(default=0, description="Total partitions")
    active_partitions: int = Field(default=0, description="Active partitions")
    archived_partitions: int = Field(default=0, description="Archived partitions")

    # Storage
    total_size_gb: float = Field(default=0.0, description="Total storage size in GB")
    active_size_gb: float = Field(default=0.0, description="Active data size in GB")
    archived_size_gb: float = Field(default=0.0, description="Archived data size in GB")

    # Date range
    earliest_record: datetime | None = Field(default=None, description="Earliest record date")
    latest_record: datetime | None = Field(default=None, description="Latest record date")

    # Quality
    avg_completeness: float = Field(default=1.0, description="Average completeness score")
    avg_accuracy: float = Field(default=1.0, description="Average accuracy score")
    total_validation_errors: int = Field(default=0, description="Total validation errors")

    # Performance
    avg_query_time_ms: float = Field(default=0.0, description="Average query time in ms")
    cache_hit_rate: float = Field(default=0.0, description="Cache hit rate")

    # Computed at
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class HeatmapCell(DataLakeBaseModel):
    """
    Single cell in a heatmap grid.
    """

    h3_index: str = Field(description="H3 hexagonal index")
    latitude: float = Field(description="Cell center latitude")
    longitude: float = Field(description="Cell center longitude")
    value: float = Field(ge=0, description="Heatmap value/intensity")
    incident_count: int = Field(default=0, description="Incident count in cell")
    normalized_value: float = Field(
        default=0.0, ge=0, le=1, description="Normalized value (0-1)"
    )


class MultiYearHeatmapData(DataLakeBaseModel):
    """
    Multi-year heatmap data for temporal comparison.
    """

    id: str = Field(description="Heatmap data ID")
    jurisdiction: str = Field(description="Jurisdiction code")
    crime_category: CrimeCategory | None = Field(default=None, description="Crime category filter")
    resolution: int = Field(default=8, description="H3 resolution (7-10)")

    # Time range
    start_year: int = Field(description="Start year")
    end_year: int = Field(description="End year")
    years: list[int] = Field(description="Years included")

    # Heatmap data by year
    yearly_heatmaps: dict[int, list[HeatmapCell]] = Field(
        default_factory=dict, description="Heatmap cells by year"
    )

    # Aggregated data
    combined_heatmap: list[HeatmapCell] = Field(
        default_factory=list, description="Combined multi-year heatmap"
    )

    # Hotspot evolution
    persistent_hotspots: list[str] = Field(
        default_factory=list, description="H3 indices that are hotspots across all years"
    )
    emerging_hotspots: list[str] = Field(
        default_factory=list, description="H3 indices showing increasing activity"
    )
    declining_hotspots: list[str] = Field(
        default_factory=list, description="H3 indices showing decreasing activity"
    )

    # Statistics
    total_incidents: int = Field(default=0, description="Total incidents across all years")
    incidents_by_year: dict[int, int] = Field(
        default_factory=dict, description="Incident count by year"
    )
    trend: str = Field(default="stable", description="Overall trend")
    trend_percent_change: float = Field(default=0.0, description="Trend percent change")

    # Metadata
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class DataLineageRecord(DataLakeBaseModel):
    """
    Data lineage tracking for governance.
    """

    id: str = Field(description="Lineage record ID")
    record_id: str = Field(description="Data record ID")
    record_type: str = Field(description="Type of record")

    # Source
    source_system: str = Field(description="Original source system")
    source_id: str = Field(description="ID in source system")
    source_timestamp: datetime = Field(description="Timestamp in source")

    # Transformations
    transformations: list[dict[str, Any]] = Field(
        default_factory=list, description="List of transformations applied"
    )

    # Current state
    current_location: str = Field(description="Current storage location")
    current_partition: str = Field(description="Current partition key")

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(description="System/user that created record")
    last_accessed: datetime | None = Field(default=None, description="Last access time")
    access_count: int = Field(default=0, description="Number of accesses")


class DataQualityMetric(DataLakeBaseModel):
    """
    Data quality metrics for governance.
    """

    id: str = Field(description="Metric ID")
    partition_key: str = Field(description="Partition this metric applies to")
    computed_at: datetime = Field(default_factory=datetime.utcnow)

    # Completeness
    total_records: int = Field(default=0, description="Total records evaluated")
    complete_records: int = Field(default=0, description="Records with all required fields")
    completeness_score: float = Field(default=1.0, ge=0, le=1)

    # Accuracy
    validated_records: int = Field(default=0, description="Records that passed validation")
    accuracy_score: float = Field(default=1.0, ge=0, le=1)

    # Consistency
    duplicate_records: int = Field(default=0, description="Duplicate records found")
    consistency_score: float = Field(default=1.0, ge=0, le=1)

    # Timeliness
    avg_ingestion_delay_seconds: float = Field(
        default=0.0, description="Average delay from event to ingestion"
    )
    timeliness_score: float = Field(default=1.0, ge=0, le=1)

    # Overall
    overall_quality_score: float = Field(default=1.0, ge=0, le=1)

    # Issues
    issues: list[dict[str, Any]] = Field(
        default_factory=list, description="Quality issues found"
    )

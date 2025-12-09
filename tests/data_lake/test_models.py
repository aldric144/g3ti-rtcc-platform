"""
Tests for Data Lake models.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.data_lake.models import (
    IncidentRecord,
    OffenderProfile,
    HistoricalAggregate,
    CrimeDataPartition,
    PartitionMetadata,
    DataRetentionPolicy,
    DataLakeConfig,
    DataLakeStats,
    HeatmapCell,
    MultiYearHeatmapData,
    DataLineageRecord,
    DataQualityMetric,
    RetentionAction,
    PartitionType,
    AggregationType,
)


class TestIncidentRecord:
    """Tests for IncidentRecord model."""

    def test_create_valid_incident(self):
        """Test creating a valid incident record."""
        incident = IncidentRecord(
            id="INC-001",
            source_system="CAD",
            source_id="CAD-12345",
            incident_number="2024-001234",
            timestamp=datetime.now(timezone.utc),
            crime_type="theft",
            crime_category="property",
            severity="medium",
            latitude=33.749,
            longitude=-84.388,
            jurisdiction="ATL",
        )

        assert incident.id == "INC-001"
        assert incident.source_system == "CAD"
        assert incident.crime_category == "property"
        assert incident.severity == "medium"

    def test_incident_with_optional_fields(self):
        """Test incident with optional fields."""
        incident = IncidentRecord(
            id="INC-002",
            source_system="RMS",
            source_id="RMS-67890",
            timestamp=datetime.now(timezone.utc),
            crime_type="assault",
            latitude=33.75,
            longitude=-84.39,
            jurisdiction="ATL",
            address="123 Main St",
            beat="Zone 1",
            district="Central",
            ucr_code="13A",
            weapon_involved=True,
            weapon_type="knife",
            arrest_made=True,
            suspect_count=1,
            victim_count=1,
        )

        assert incident.address == "123 Main St"
        assert incident.weapon_involved is True
        assert incident.arrest_made is True

    def test_incident_latitude_validation(self):
        """Test latitude range validation."""
        with pytest.raises(ValidationError):
            IncidentRecord(
                id="INC-003",
                source_system="CAD",
                source_id="CAD-999",
                timestamp=datetime.now(timezone.utc),
                crime_type="theft",
                latitude=100.0,  # Invalid: > 90
                longitude=-84.388,
                jurisdiction="ATL",
            )

    def test_incident_longitude_validation(self):
        """Test longitude range validation."""
        with pytest.raises(ValidationError):
            IncidentRecord(
                id="INC-004",
                source_system="CAD",
                source_id="CAD-998",
                timestamp=datetime.now(timezone.utc),
                crime_type="theft",
                latitude=33.749,
                longitude=-200.0,  # Invalid: < -180
                jurisdiction="ATL",
            )


class TestOffenderProfile:
    """Tests for OffenderProfile model."""

    def test_create_valid_offender(self):
        """Test creating a valid offender profile."""
        offender = OffenderProfile(
            offender_id="OFF-001",
            jurisdiction="ATL",
            total_incidents=5,
            first_incident_date=datetime(2020, 1, 1),
            last_incident_date=datetime(2024, 6, 15),
            risk_score=75.5,
            risk_level="high",
        )

        assert offender.offender_id == "OFF-001"
        assert offender.total_incidents == 5
        assert offender.risk_score == 75.5
        assert offender.risk_level == "high"

    def test_offender_risk_score_validation(self):
        """Test risk score range validation."""
        with pytest.raises(ValidationError):
            OffenderProfile(
                offender_id="OFF-002",
                jurisdiction="ATL",
                risk_score=150.0,  # Invalid: > 100
                risk_level="high",
            )

    def test_offender_with_crime_categories(self):
        """Test offender with crime category breakdown."""
        offender = OffenderProfile(
            offender_id="OFF-003",
            jurisdiction="ATL",
            risk_score=60.0,
            risk_level="medium",
            crime_categories={"property": 3, "violent": 1, "drug": 2},
            severity_breakdown={"high": 1, "medium": 3, "low": 2},
        )

        assert offender.crime_categories["property"] == 3
        assert offender.severity_breakdown["high"] == 1


class TestHistoricalAggregate:
    """Tests for HistoricalAggregate model."""

    def test_create_daily_aggregate(self):
        """Test creating a daily aggregate."""
        aggregate = HistoricalAggregate(
            id="AGG-001",
            jurisdiction="ATL",
            aggregation_type=AggregationType.DAILY,
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 1, 23, 59, 59),
            total_incidents=150,
            by_category={"property": 80, "violent": 30, "drug": 40},
            by_severity={"high": 20, "medium": 80, "low": 50},
        )

        assert aggregate.aggregation_type == AggregationType.DAILY
        assert aggregate.total_incidents == 150
        assert aggregate.by_category["property"] == 80

    def test_create_monthly_aggregate(self):
        """Test creating a monthly aggregate."""
        aggregate = HistoricalAggregate(
            id="AGG-002",
            jurisdiction="ATL",
            aggregation_type=AggregationType.MONTHLY,
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 31, 23, 59, 59),
            total_incidents=4500,
        )

        assert aggregate.aggregation_type == AggregationType.MONTHLY
        assert aggregate.total_incidents == 4500


class TestDataRetentionPolicy:
    """Tests for DataRetentionPolicy model."""

    def test_create_archive_policy(self):
        """Test creating an archive retention policy."""
        policy = DataRetentionPolicy(
            id="POL-001",
            name="7-Year Archive",
            retention_days=2555,
            action=RetentionAction.ARCHIVE,
            applies_to=["incidents", "offenders"],
        )

        assert policy.action == RetentionAction.ARCHIVE
        assert policy.retention_days == 2555
        assert "incidents" in policy.applies_to

    def test_create_delete_policy(self):
        """Test creating a delete retention policy."""
        policy = DataRetentionPolicy(
            id="POL-002",
            name="10-Year Delete",
            retention_days=3650,
            action=RetentionAction.DELETE,
            applies_to=["audit_logs"],
        )

        assert policy.action == RetentionAction.DELETE

    def test_create_anonymize_policy(self):
        """Test creating an anonymize retention policy."""
        policy = DataRetentionPolicy(
            id="POL-003",
            name="5-Year Anonymize",
            retention_days=1825,
            action=RetentionAction.ANONYMIZE,
            applies_to=["offenders"],
        )

        assert policy.action == RetentionAction.ANONYMIZE


class TestPartitionMetadata:
    """Tests for PartitionMetadata model."""

    def test_create_partition_metadata(self):
        """Test creating partition metadata."""
        metadata = PartitionMetadata(
            partition_key="2024-01",
            partition_type=PartitionType.MONTHLY,
            jurisdiction="ATL",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31, 23, 59, 59),
            record_count=4500,
            size_bytes=1024 * 1024 * 50,  # 50 MB
        )

        assert metadata.partition_key == "2024-01"
        assert metadata.partition_type == PartitionType.MONTHLY
        assert metadata.record_count == 4500


class TestHeatmapCell:
    """Tests for HeatmapCell model."""

    def test_create_heatmap_cell(self):
        """Test creating a heatmap cell."""
        cell = HeatmapCell(
            h3_index="8828308280fffff",
            latitude=33.749,
            longitude=-84.388,
            count=150,
            intensity=0.85,
        )

        assert cell.h3_index == "8828308280fffff"
        assert cell.count == 150
        assert cell.intensity == 0.85

    def test_heatmap_cell_intensity_validation(self):
        """Test intensity range validation."""
        with pytest.raises(ValidationError):
            HeatmapCell(
                h3_index="8828308280fffff",
                latitude=33.749,
                longitude=-84.388,
                count=150,
                intensity=1.5,  # Invalid: > 1
            )


class TestDataQualityMetric:
    """Tests for DataQualityMetric model."""

    def test_create_quality_metric(self):
        """Test creating a data quality metric."""
        metric = DataQualityMetric(
            id="QM-001",
            jurisdiction="ATL",
            metric_name="completeness",
            metric_value=0.95,
            field_name="address",
            records_checked=10000,
            records_passed=9500,
        )

        assert metric.metric_name == "completeness"
        assert metric.metric_value == 0.95
        assert metric.records_passed == 9500


class TestDataLakeStats:
    """Tests for DataLakeStats model."""

    def test_create_stats(self):
        """Test creating data lake statistics."""
        stats = DataLakeStats(
            total_incidents=1000000,
            total_offenders=50000,
            total_partitions=120,
            jurisdictions=["ATL", "NYC", "LAX"],
            earliest_record=datetime(2020, 1, 1),
            latest_record=datetime(2024, 12, 1),
            storage_size_bytes=1024 * 1024 * 1024 * 10,  # 10 GB
        )

        assert stats.total_incidents == 1000000
        assert len(stats.jurisdictions) == 3
        assert stats.storage_size_bytes == 10 * 1024 * 1024 * 1024

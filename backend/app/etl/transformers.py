"""
Data Transformers for ETL Pipelines.

This module provides data transformation utilities including:
- Incident normalization
- Geographic enrichment
- Time normalization
- Data standardization
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class TransformerConfig(BaseModel):
    """Transformer configuration."""

    model_config = ConfigDict(from_attributes=True)

    normalize_addresses: bool = Field(default=True, description="Normalize addresses")
    enrich_geo: bool = Field(default=True, description="Enrich geographic data")
    normalize_times: bool = Field(default=True, description="Normalize timestamps to UTC")
    standardize_codes: bool = Field(default=True, description="Standardize crime codes")


class DataTransformer:
    """
    Base data transformer for ETL pipelines.

    Provides common transformation utilities for incident data.
    """

    def __init__(self, config: TransformerConfig | None = None):
        """
        Initialize the transformer.

        Args:
            config: Transformer configuration
        """
        self.config = config or TransformerConfig()
        logger.info("DataTransformer initialized")

    def transform(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Apply all transformations to a record.

        Args:
            record: Input record

        Returns:
            Transformed record
        """
        result = record.copy()

        if self.config.normalize_addresses:
            result = self._normalize_address(result)

        if self.config.normalize_times:
            result = self._normalize_timestamps(result)

        if self.config.standardize_codes:
            result = self._standardize_codes(result)

        return result

    def _normalize_address(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize address fields."""
        address = record.get("address", "")
        if address:
            # Standardize common abbreviations
            address = self._standardize_address(address)
            record["address"] = address
            record["address_normalized"] = True

        return record

    def _standardize_address(self, address: str) -> str:
        """Standardize address format."""
        if not address:
            return address

        # Convert to uppercase for consistency
        address = address.upper().strip()

        # Common abbreviations
        replacements = {
            r"\bSTREET\b": "ST",
            r"\bAVENUE\b": "AVE",
            r"\bBOULEVARD\b": "BLVD",
            r"\bDRIVE\b": "DR",
            r"\bROAD\b": "RD",
            r"\bLANE\b": "LN",
            r"\bCOURT\b": "CT",
            r"\bCIRCLE\b": "CIR",
            r"\bPLACE\b": "PL",
            r"\bNORTH\b": "N",
            r"\bSOUTH\b": "S",
            r"\bEAST\b": "E",
            r"\bWEST\b": "W",
            r"\bAPARTMENT\b": "APT",
            r"\bSUITE\b": "STE",
            r"\bUNIT\b": "UNIT",
        }

        for pattern, replacement in replacements.items():
            address = re.sub(pattern, replacement, address)

        # Remove extra whitespace
        address = " ".join(address.split())

        return address

    def _normalize_timestamps(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize timestamp fields to UTC."""
        timestamp_fields = ["timestamp", "reported_at", "occurred_at", "created_at"]

        for field in timestamp_fields:
            if field in record:
                value = record[field]
                if isinstance(value, str):
                    try:
                        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        record[field] = dt
                    except ValueError:
                        pass
                elif isinstance(value, datetime):
                    if value.tzinfo is None:
                        record[field] = value.replace(tzinfo=timezone.utc)

        return record

    def _standardize_codes(self, record: dict[str, Any]) -> dict[str, Any]:
        """Standardize crime codes."""
        crime_type = record.get("crime_type", "")
        if crime_type:
            # Normalize crime type
            crime_type = crime_type.lower().strip()
            crime_type = re.sub(r"[^a-z0-9_]", "_", crime_type)
            crime_type = re.sub(r"_+", "_", crime_type)
            crime_type = crime_type.strip("_")
            record["crime_type"] = crime_type

        return record


class IncidentNormalizer:
    """
    Normalizer for incident records.

    Ensures consistent field names and formats across different source systems.
    """

    # Field mappings from various sources to standard names
    FIELD_MAPPINGS = {
        # Timestamp fields
        "call_time": "timestamp",
        "occurred_date": "timestamp",
        "alert_time": "timestamp",
        "read_time": "timestamp",
        "event_time": "timestamp",
        # Location fields
        "lat": "latitude",
        "lon": "longitude",
        "lng": "longitude",
        "geo_lat": "latitude",
        "geo_lon": "longitude",
        "geo_lng": "longitude",
        # ID fields
        "cad_number": "incident_number",
        "case_number": "incident_number",
        "report_number": "incident_number",
        "alert_id": "source_id",
        "read_id": "source_id",
        # Crime fields
        "call_type": "crime_type",
        "event_type": "crime_type",
        "offense_description": "crime_type",
        "charge": "crime_type",
        "offense_code": "ucr_code",
        # Location description
        "location": "address",
        "incident_address": "address",
        # Zone fields
        "zone": "beat",
        "reporting_area": "beat",
        "precinct": "district",
        # Agency fields
        "agency": "jurisdiction",
        "ori": "jurisdiction",
    }

    def __init__(self):
        """Initialize the normalizer."""
        logger.info("IncidentNormalizer initialized")

    def normalize(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize an incident record.

        Args:
            record: Input record with potentially non-standard field names

        Returns:
            Normalized record with standard field names
        """
        normalized = {}

        for key, value in record.items():
            # Map to standard field name if applicable
            standard_key = self.FIELD_MAPPINGS.get(key, key)

            # Don't overwrite if standard field already exists
            if standard_key not in normalized:
                normalized[standard_key] = value

        # Ensure required fields have defaults
        normalized.setdefault("jurisdiction", "default")
        normalized.setdefault("severity", "medium")
        normalized.setdefault("crime_category", "other")

        return normalized

    def merge_records(
        self,
        primary: dict[str, Any],
        secondary: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge two records, preferring primary values.

        Args:
            primary: Primary record (preferred values)
            secondary: Secondary record (fallback values)

        Returns:
            Merged record
        """
        merged = secondary.copy()
        merged.update({k: v for k, v in primary.items() if v is not None})
        return merged


class GeoEnricher:
    """
    Geographic data enricher.

    Adds geographic metadata like H3 indices, geohashes, and zone information.
    """

    # H3 resolution levels
    H3_RESOLUTION_CITY = 7  # ~5km cells
    H3_RESOLUTION_NEIGHBORHOOD = 8  # ~1km cells
    H3_RESOLUTION_BLOCK = 9  # ~200m cells
    H3_RESOLUTION_STREET = 10  # ~50m cells

    def __init__(self, default_resolution: int = 8):
        """
        Initialize the geo enricher.

        Args:
            default_resolution: Default H3 resolution
        """
        self.default_resolution = default_resolution
        logger.info(f"GeoEnricher initialized with resolution {default_resolution}")

    def enrich(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Enrich record with geographic metadata.

        Args:
            record: Input record with latitude/longitude

        Returns:
            Enriched record
        """
        lat = record.get("latitude", 0)
        lon = record.get("longitude", 0)

        if lat == 0 and lon == 0:
            return record

        enriched = record.copy()

        # Add H3 indices at multiple resolutions
        enriched["h3_index"] = self._compute_h3_index(lat, lon, self.default_resolution)
        enriched["h3_index_city"] = self._compute_h3_index(lat, lon, self.H3_RESOLUTION_CITY)
        enriched["h3_index_neighborhood"] = self._compute_h3_index(
            lat, lon, self.H3_RESOLUTION_NEIGHBORHOOD
        )

        # Add geohash
        enriched["geohash"] = self._compute_geohash(lat, lon)

        # Add location object
        enriched["location"] = {
            "latitude": lat,
            "longitude": lon,
            "h3_index": enriched["h3_index"],
            "geohash": enriched["geohash"],
        }

        return enriched

    def _compute_h3_index(self, lat: float, lon: float, resolution: int) -> str:
        """
        Compute H3 index for coordinates.

        Note: In production, would use the h3 library.
        This is a simplified implementation for demonstration.
        """
        try:
            # Simplified H3-like index computation
            lat_part = int((lat + 90) * (10 ** (resolution - 5))) % (10 ** 6)
            lon_part = int((lon + 180) * (10 ** (resolution - 5))) % (10 ** 6)
            return f"{resolution:x}{lat_part:06x}{lon_part:06x}"
        except Exception:
            return ""

    def _compute_geohash(self, lat: float, lon: float, precision: int = 7) -> str:
        """
        Compute geohash for coordinates.

        Note: In production, would use a geohash library.
        This is a simplified implementation.
        """
        try:
            # Simplified geohash computation
            base32 = "0123456789bcdefghjkmnpqrstuvwxyz"

            lat_range = [-90.0, 90.0]
            lon_range = [-180.0, 180.0]

            geohash = []
            bits = [16, 8, 4, 2, 1]
            bit = 0
            ch = 0
            is_lon = True

            while len(geohash) < precision:
                if is_lon:
                    mid = (lon_range[0] + lon_range[1]) / 2
                    if lon > mid:
                        ch |= bits[bit]
                        lon_range[0] = mid
                    else:
                        lon_range[1] = mid
                else:
                    mid = (lat_range[0] + lat_range[1]) / 2
                    if lat > mid:
                        ch |= bits[bit]
                        lat_range[0] = mid
                    else:
                        lat_range[1] = mid

                is_lon = not is_lon

                if bit < 4:
                    bit += 1
                else:
                    geohash.append(base32[ch])
                    bit = 0
                    ch = 0

            return "".join(geohash)
        except Exception:
            return ""

    def get_nearby_indices(self, h3_index: str, ring_size: int = 1) -> list[str]:
        """
        Get nearby H3 indices (k-ring).

        Args:
            h3_index: Center H3 index
            ring_size: Ring size (1 = immediate neighbors)

        Returns:
            List of nearby H3 indices
        """
        # Simplified - in production would use h3.k_ring
        return [h3_index]


class TimeNormalizer:
    """
    Time normalization utilities.

    Handles timezone conversion, time bucketing, and temporal feature extraction.
    """

    def __init__(self, target_timezone: str = "UTC"):
        """
        Initialize the time normalizer.

        Args:
            target_timezone: Target timezone for normalization
        """
        self.target_timezone = target_timezone
        logger.info(f"TimeNormalizer initialized with timezone {target_timezone}")

    def normalize(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize time fields in a record.

        Args:
            record: Input record

        Returns:
            Record with normalized time fields
        """
        normalized = record.copy()

        # Normalize main timestamp
        if "timestamp" in normalized:
            ts = self._to_utc(normalized["timestamp"])
            normalized["timestamp"] = ts

            # Add temporal features
            normalized["hour_of_day"] = ts.hour
            normalized["day_of_week"] = ts.weekday()
            normalized["day_of_month"] = ts.day
            normalized["month"] = ts.month
            normalized["year"] = ts.year
            normalized["is_weekend"] = ts.weekday() >= 5
            normalized["time_bucket"] = self._get_time_bucket(ts.hour)

            # Add partition keys
            normalized["partition_date"] = ts.strftime("%Y-%m-%d")
            normalized["partition_month"] = ts.strftime("%Y-%m")
            normalized["partition_year"] = ts.year

        return normalized

    def _to_utc(self, value: Any) -> datetime:
        """Convert value to UTC datetime."""
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).replace(tzinfo=None)

        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if dt.tzinfo:
                    return dt.astimezone(timezone.utc).replace(tzinfo=None)
                return dt
            except ValueError:
                pass

        return datetime.utcnow()

    def _get_time_bucket(self, hour: int) -> str:
        """Get time bucket for hour."""
        if 0 <= hour < 6:
            return "late_night"
        elif 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        else:
            return "evening"

    def extract_temporal_features(self, timestamp: datetime) -> dict[str, Any]:
        """
        Extract temporal features from a timestamp.

        Args:
            timestamp: Input timestamp

        Returns:
            Dictionary of temporal features
        """
        return {
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "day_of_month": timestamp.day,
            "week_of_year": timestamp.isocalendar()[1],
            "month": timestamp.month,
            "quarter": (timestamp.month - 1) // 3 + 1,
            "year": timestamp.year,
            "is_weekend": timestamp.weekday() >= 5,
            "is_night": timestamp.hour < 6 or timestamp.hour >= 22,
            "time_bucket": self._get_time_bucket(timestamp.hour),
        }

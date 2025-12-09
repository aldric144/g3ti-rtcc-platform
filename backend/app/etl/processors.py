"""
Data Processors for ETL Pipelines.

This module provides specialized data processors for different source systems:
- CAD (Computer-Aided Dispatch)
- RMS (Records Management System)
- ShotSpotter (Gunfire Detection)
- LPR (License Plate Recognition)
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class ProcessorConfig(BaseModel):
    """Base processor configuration."""

    model_config = ConfigDict(from_attributes=True)

    source_name: str = Field(description="Source system name")
    batch_size: int = Field(default=1000, description="Processing batch size")
    timeout_seconds: int = Field(default=300, description="Processing timeout")
    retry_count: int = Field(default=3, description="Retry attempts")


class ProcessorResult(BaseModel):
    """Processor execution result."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(description="Whether processing succeeded")
    records_processed: int = Field(default=0, description="Records processed")
    records_failed: int = Field(default=0, description="Records failed")
    errors: list[dict[str, Any]] = Field(default_factory=list, description="Error details")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DataProcessor(ABC):
    """
    Abstract base class for data processors.

    Provides common interface for processing data from various source systems.
    """

    def __init__(self, config: ProcessorConfig):
        """
        Initialize the processor.

        Args:
            config: Processor configuration
        """
        self.config = config
        logger.info(f"Initialized {self.__class__.__name__} for {config.source_name}")

    @abstractmethod
    async def extract(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract data from source system.

        Args:
            params: Extraction parameters

        Returns:
            List of extracted records
        """
        pass

    @abstractmethod
    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """
        Transform a single record to standard format.

        Args:
            record: Raw record from source

        Returns:
            Transformed record or None if invalid
        """
        pass

    @abstractmethod
    def validate(self, record: dict[str, Any]) -> bool:
        """
        Validate a transformed record.

        Args:
            record: Transformed record

        Returns:
            True if valid
        """
        pass

    async def process(self, params: dict[str, Any]) -> ProcessorResult:
        """
        Execute full processing pipeline.

        Args:
            params: Processing parameters

        Returns:
            Processing result
        """
        errors: list[dict[str, Any]] = []
        processed = 0
        failed = 0

        try:
            # Extract
            raw_records = await self.extract(params)
            logger.info(f"Extracted {len(raw_records)} records from {self.config.source_name}")

            # Transform and validate
            for record in raw_records:
                try:
                    transformed = self.transform(record)
                    if transformed and self.validate(transformed):
                        processed += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    errors.append({
                        "record_id": record.get("id", "unknown"),
                        "error": str(e),
                    })

            return ProcessorResult(
                success=True,
                records_processed=processed,
                records_failed=failed,
                errors=errors[:100],  # Limit errors stored
                metadata={
                    "source": self.config.source_name,
                    "total_extracted": len(raw_records),
                },
            )

        except Exception as e:
            logger.error(f"Processing failed for {self.config.source_name}: {e}")
            return ProcessorResult(
                success=False,
                records_processed=processed,
                records_failed=failed,
                errors=[{"error": str(e)}],
            )


class CADProcessor(DataProcessor):
    """
    Processor for Computer-Aided Dispatch (CAD) data.

    Handles extraction and transformation of CAD incident records.
    """

    # CAD event type mappings
    EVENT_TYPE_MAPPING = {
        "SHOTS": "shots_fired",
        "ASSAULT": "assault",
        "ROBBERY": "robbery",
        "BURGLARY": "burglary",
        "THEFT": "theft",
        "DV": "domestic_violence",
        "TRAFFIC": "traffic_incident",
        "DISTURBANCE": "disturbance",
        "SUSPICIOUS": "suspicious_activity",
        "MEDICAL": "medical_emergency",
    }

    # Priority to severity mapping
    PRIORITY_SEVERITY = {
        "1": "critical",
        "2": "high",
        "3": "medium",
        "4": "low",
        "5": "low",
    }

    def __init__(self, config: ProcessorConfig | None = None):
        """Initialize CAD processor."""
        if config is None:
            config = ProcessorConfig(source_name="CAD")
        super().__init__(config)

    async def extract(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract CAD records.

        Args:
            params: Extraction parameters including:
                - start_date: Start datetime
                - end_date: End datetime
                - event_types: Optional list of event types

        Returns:
            List of CAD records
        """
        # In production, this would connect to CAD system API
        # For now, return mock data structure
        logger.info(f"Extracting CAD data with params: {params}")

        # Mock extraction - would be replaced with actual CAD API call
        return params.get("records", [])

    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """
        Transform CAD record to standard incident format.

        Args:
            record: Raw CAD record

        Returns:
            Transformed incident record
        """
        try:
            # Extract event type
            raw_type = record.get("event_type", record.get("call_type", ""))
            event_type = self._map_event_type(raw_type)

            # Extract priority/severity
            priority = str(record.get("priority", "3"))
            severity = self.PRIORITY_SEVERITY.get(priority, "medium")

            # Parse timestamp
            timestamp = self._parse_timestamp(
                record.get("timestamp", record.get("call_time"))
            )

            # Parse location
            latitude = float(record.get("latitude", record.get("lat", 0)))
            longitude = float(record.get("longitude", record.get("lon", 0)))

            return {
                "source_system": "CAD",
                "source_id": record.get("cad_number", record.get("id", "")),
                "incident_number": record.get("incident_number", record.get("cad_number", "")),
                "timestamp": timestamp,
                "reported_at": timestamp,
                "crime_type": event_type,
                "crime_description": record.get("narrative", record.get("description", "")),
                "severity": severity,
                "latitude": latitude,
                "longitude": longitude,
                "address": record.get("address", record.get("location", "")),
                "beat": record.get("beat", record.get("zone", "")),
                "district": record.get("district", ""),
                "jurisdiction": record.get("jurisdiction", record.get("agency", "default")),
                "disposition": record.get("disposition", ""),
                "units_assigned": record.get("units", []),
                "weapon_involved": self._check_weapon(record),
                "domestic_violence": "DV" in raw_type.upper() or "DOMESTIC" in raw_type.upper(),
            }

        except Exception as e:
            logger.warning(f"CAD transform error: {e}")
            return None

    def validate(self, record: dict[str, Any]) -> bool:
        """
        Validate transformed CAD record.

        Args:
            record: Transformed record

        Returns:
            True if valid
        """
        # Required fields
        if not record.get("source_id"):
            return False
        if not record.get("timestamp"):
            return False

        # Location validation
        lat = record.get("latitude", 0)
        lon = record.get("longitude", 0)
        if lat == 0 and lon == 0:
            logger.warning(f"Invalid location for CAD record {record.get('source_id')}")
            # Still valid but flagged

        return True

    def _map_event_type(self, raw_type: str) -> str:
        """Map raw event type to standard type."""
        raw_upper = raw_type.upper()
        for key, value in self.EVENT_TYPE_MAPPING.items():
            if key in raw_upper:
                return value
        return raw_type.lower().replace(" ", "_")

    def _parse_timestamp(self, value: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.utcnow()

    def _check_weapon(self, record: dict[str, Any]) -> bool:
        """Check if weapon is involved."""
        weapon_keywords = ["GUN", "KNIFE", "WEAPON", "ARMED", "SHOTS"]
        text = (
            record.get("event_type", "")
            + " "
            + record.get("narrative", "")
        ).upper()
        return any(kw in text for kw in weapon_keywords)


class RMSProcessor(DataProcessor):
    """
    Processor for Records Management System (RMS) data.

    Handles extraction and transformation of RMS incident/case records.
    """

    # UCR code category mapping
    UCR_CATEGORIES = {
        "09": "violent",  # Murder
        "11": "violent",  # Rape
        "12": "violent",  # Robbery
        "13": "violent",  # Aggravated Assault
        "22": "property",  # Burglary
        "23": "property",  # Larceny
        "24": "property",  # Motor Vehicle Theft
        "26": "property",  # Arson
        "35": "drug",  # Drug Offenses
        "90": "other",  # Other
    }

    def __init__(self, config: ProcessorConfig | None = None):
        """Initialize RMS processor."""
        if config is None:
            config = ProcessorConfig(source_name="RMS")
        super().__init__(config)

    async def extract(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract RMS records.

        Args:
            params: Extraction parameters

        Returns:
            List of RMS records
        """
        logger.info(f"Extracting RMS data with params: {params}")
        return params.get("records", [])

    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """
        Transform RMS record to standard incident format.

        Args:
            record: Raw RMS record

        Returns:
            Transformed incident record
        """
        try:
            # Extract UCR code and category
            ucr_code = record.get("ucr_code", record.get("offense_code", ""))
            crime_category = self._get_crime_category(ucr_code)

            # Parse timestamp
            timestamp = self._parse_timestamp(
                record.get("occurred_date", record.get("report_date"))
            )
            reported_at = self._parse_timestamp(record.get("report_date", timestamp))

            # Parse location
            latitude = float(record.get("latitude", record.get("geo_lat", 0)))
            longitude = float(record.get("longitude", record.get("geo_lon", 0)))

            # Extract offender information
            offender_ids = record.get("offender_ids", [])
            if record.get("suspect_id"):
                offender_ids.append(record["suspect_id"])

            return {
                "source_system": "RMS",
                "source_id": record.get("case_number", record.get("id", "")),
                "incident_number": record.get("case_number", record.get("report_number", "")),
                "timestamp": timestamp,
                "reported_at": reported_at,
                "crime_type": record.get("offense_description", record.get("charge", "")),
                "crime_description": record.get("narrative", record.get("synopsis", "")),
                "ucr_code": ucr_code,
                "crime_category": crime_category,
                "severity": self._assess_severity(record),
                "latitude": latitude,
                "longitude": longitude,
                "address": record.get("address", record.get("location", "")),
                "beat": record.get("beat", record.get("reporting_area", "")),
                "district": record.get("district", record.get("precinct", "")),
                "jurisdiction": record.get("jurisdiction", record.get("ori", "default")),
                "suspect_count": record.get("suspect_count", len(offender_ids)),
                "victim_count": record.get("victim_count", 0),
                "arrest_made": record.get("arrest_made", False),
                "offender_ids": offender_ids,
                "weapon_involved": record.get("weapon_used", False),
                "weapon_type": record.get("weapon_type"),
                "domestic_violence": record.get("domestic_violence", False),
                "gang_related": record.get("gang_related", False),
                "clearance_status": record.get("clearance_status", ""),
            }

        except Exception as e:
            logger.warning(f"RMS transform error: {e}")
            return None

    def validate(self, record: dict[str, Any]) -> bool:
        """Validate transformed RMS record."""
        if not record.get("source_id"):
            return False
        if not record.get("timestamp"):
            return False
        return True

    def _get_crime_category(self, ucr_code: str) -> str:
        """Get crime category from UCR code."""
        if len(ucr_code) >= 2:
            prefix = ucr_code[:2]
            return self.UCR_CATEGORIES.get(prefix, "other")
        return "other"

    def _parse_timestamp(self, value: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.utcnow()

    def _assess_severity(self, record: dict[str, Any]) -> str:
        """Assess incident severity."""
        ucr_code = record.get("ucr_code", "")

        # Homicide
        if ucr_code.startswith("09"):
            return "critical"

        # Violent crimes
        if ucr_code.startswith(("11", "12", "13")):
            return "high"

        # Property crimes
        if ucr_code.startswith(("22", "23", "24")):
            return "medium"

        return "low"


class ShotSpotterProcessor(DataProcessor):
    """
    Processor for ShotSpotter gunfire detection data.

    Handles extraction and transformation of acoustic gunfire alerts.
    """

    def __init__(self, config: ProcessorConfig | None = None):
        """Initialize ShotSpotter processor."""
        if config is None:
            config = ProcessorConfig(source_name="ShotSpotter")
        super().__init__(config)

    async def extract(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract ShotSpotter alerts.

        Args:
            params: Extraction parameters

        Returns:
            List of ShotSpotter alerts
        """
        logger.info(f"Extracting ShotSpotter data with params: {params}")
        return params.get("records", [])

    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """
        Transform ShotSpotter alert to standard incident format.

        Args:
            record: Raw ShotSpotter alert

        Returns:
            Transformed incident record
        """
        try:
            # Parse timestamp
            timestamp = self._parse_timestamp(record.get("timestamp", record.get("alert_time")))

            # Parse location
            latitude = float(record.get("latitude", record.get("lat", 0)))
            longitude = float(record.get("longitude", record.get("lon", 0)))

            # Determine severity based on round count
            rounds = record.get("rounds_detected", record.get("round_count", 1))
            if rounds >= 10:
                severity = "critical"
            elif rounds >= 5:
                severity = "high"
            else:
                severity = "medium"

            return {
                "source_system": "ShotSpotter",
                "source_id": record.get("alert_id", record.get("id", "")),
                "incident_number": f"SS-{record.get('alert_id', record.get('id', ''))}",
                "timestamp": timestamp,
                "reported_at": timestamp,
                "crime_type": "shots_fired",
                "crime_description": f"ShotSpotter alert: {rounds} rounds detected",
                "severity": severity,
                "latitude": latitude,
                "longitude": longitude,
                "address": record.get("address", record.get("location", "")),
                "beat": record.get("beat", record.get("zone", "")),
                "district": record.get("district", ""),
                "jurisdiction": record.get("jurisdiction", "default"),
                "weapon_involved": True,
                "weapon_type": "firearm",
                "rounds_detected": rounds,
                "confidence": record.get("confidence", record.get("probability", 0.95)),
                "alert_type": record.get("alert_type", "gunfire"),
            }

        except Exception as e:
            logger.warning(f"ShotSpotter transform error: {e}")
            return None

    def validate(self, record: dict[str, Any]) -> bool:
        """Validate transformed ShotSpotter record."""
        if not record.get("source_id"):
            return False
        if not record.get("timestamp"):
            return False

        # Validate location
        lat = record.get("latitude", 0)
        lon = record.get("longitude", 0)
        if lat == 0 and lon == 0:
            return False

        # Validate confidence
        confidence = record.get("confidence", 0)
        if confidence < 0.5:
            logger.warning(f"Low confidence ShotSpotter alert: {confidence}")

        return True

    def _parse_timestamp(self, value: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.utcnow()


class LPRProcessor(DataProcessor):
    """
    Processor for License Plate Recognition (LPR) data.

    Handles extraction and transformation of LPR hits and reads.
    """

    # Alert type severity mapping
    ALERT_SEVERITY = {
        "stolen_vehicle": "high",
        "wanted_person": "high",
        "amber_alert": "critical",
        "bolo": "high",
        "expired_registration": "low",
        "no_insurance": "low",
        "warrant": "medium",
    }

    def __init__(self, config: ProcessorConfig | None = None):
        """Initialize LPR processor."""
        if config is None:
            config = ProcessorConfig(source_name="LPR")
        super().__init__(config)

    async def extract(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract LPR records.

        Args:
            params: Extraction parameters

        Returns:
            List of LPR records
        """
        logger.info(f"Extracting LPR data with params: {params}")
        return params.get("records", [])

    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """
        Transform LPR record to standard incident format.

        Args:
            record: Raw LPR record

        Returns:
            Transformed incident record
        """
        try:
            # Parse timestamp
            timestamp = self._parse_timestamp(record.get("timestamp", record.get("read_time")))

            # Parse location
            latitude = float(record.get("latitude", record.get("lat", 0)))
            longitude = float(record.get("longitude", record.get("lon", 0)))

            # Determine alert type and severity
            alert_type = record.get("alert_type", record.get("hit_type", ""))
            severity = self.ALERT_SEVERITY.get(alert_type.lower(), "medium")

            # Only process hits (not all reads)
            is_hit = record.get("is_hit", record.get("alert", False))

            return {
                "source_system": "LPR",
                "source_id": record.get("read_id", record.get("id", "")),
                "incident_number": f"LPR-{record.get('read_id', record.get('id', ''))}",
                "timestamp": timestamp,
                "reported_at": timestamp,
                "crime_type": f"lpr_{alert_type}" if alert_type else "lpr_read",
                "crime_description": f"LPR hit: {alert_type}" if is_hit else "LPR read",
                "severity": severity if is_hit else "low",
                "latitude": latitude,
                "longitude": longitude,
                "address": record.get("address", record.get("location", "")),
                "beat": record.get("beat", record.get("zone", "")),
                "district": record.get("district", ""),
                "jurisdiction": record.get("jurisdiction", "default"),
                "plate_number": record.get("plate", record.get("plate_number", "")),
                "plate_state": record.get("state", record.get("plate_state", "")),
                "vehicle_make": record.get("make", ""),
                "vehicle_model": record.get("model", ""),
                "vehicle_color": record.get("color", ""),
                "is_hit": is_hit,
                "alert_type": alert_type,
                "camera_id": record.get("camera_id", record.get("device_id", "")),
                "confidence": record.get("confidence", record.get("ocr_confidence", 0.95)),
            }

        except Exception as e:
            logger.warning(f"LPR transform error: {e}")
            return None

    def validate(self, record: dict[str, Any]) -> bool:
        """Validate transformed LPR record."""
        if not record.get("source_id"):
            return False
        if not record.get("timestamp"):
            return False

        # Validate plate number
        plate = record.get("plate_number", "")
        if not plate or len(plate) < 2:
            return False

        # Validate confidence
        confidence = record.get("confidence", 0)
        if confidence < 0.7:
            logger.warning(f"Low confidence LPR read: {confidence}")

        return True

    def _parse_timestamp(self, value: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.utcnow()

"""
Crime Data Ingestion Module.

Handles data ingestion from multiple sources:
- Manual uploads (CSV, Excel, JSON)
- FBI NIBRS public feeds
- Palm Beach County Sheriff public incident feed
- Riviera Beach open data (crime, calls-for-service)

Normalizes all data to a standard schema.
"""

import csv
import json
import io
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class CrimeType(str, Enum):
    VIOLENT = "violent"
    PROPERTY = "property"
    DRUG = "drug"
    PUBLIC_ORDER = "public_order"
    TRAFFIC = "traffic"
    OTHER = "other"


class CrimePriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NormalizedCrimeRecord(BaseModel):
    """Normalized crime record schema."""
    id: str
    type: CrimeType
    subcategory: str
    time: str  # HH:MM:SS
    date: str  # YYYY-MM-DD
    datetime_utc: datetime
    latitude: float
    longitude: float
    sector: str
    priority: CrimePriority
    weapon: Optional[str] = None
    domestic_flag: bool = False
    address: Optional[str] = None
    description: Optional[str] = None
    source: str
    raw_data: Optional[dict] = None


class CrimeDataIngestor:
    """Handles crime data ingestion and normalization."""
    
    # Field mappings for different sources
    FIELD_MAPPINGS = {
        "nibrs": {
            "offense_type": "type",
            "offense_name": "subcategory",
            "incident_date": "date",
            "incident_time": "time",
            "latitude": "latitude",
            "longitude": "longitude",
            "location_type": "sector",
            "weapon_force": "weapon",
            "domestic_violence": "domestic_flag",
        },
        "pbso": {
            "crime_type": "type",
            "crime_description": "subcategory",
            "date_occurred": "date",
            "time_occurred": "time",
            "lat": "latitude",
            "lon": "longitude",
            "district": "sector",
            "weapon_used": "weapon",
            "dv_related": "domestic_flag",
        },
        "riviera_beach": {
            "incident_type": "type",
            "incident_category": "subcategory",
            "occurred_date": "date",
            "occurred_time": "time",
            "geo_lat": "latitude",
            "geo_lng": "longitude",
            "patrol_sector": "sector",
            "weapon_involved": "weapon",
            "domestic_violence_flag": "domestic_flag",
        },
    }
    
    # Type classification mappings
    TYPE_CLASSIFICATIONS = {
        "violent": [
            "homicide", "murder", "assault", "battery", "robbery", "rape",
            "sexual assault", "kidnapping", "aggravated assault", "manslaughter",
            "shooting", "stabbing", "carjacking"
        ],
        "property": [
            "burglary", "theft", "larceny", "auto theft", "vehicle theft",
            "shoplifting", "vandalism", "arson", "trespassing", "breaking and entering"
        ],
        "drug": [
            "drug", "narcotics", "possession", "trafficking", "distribution",
            "paraphernalia", "controlled substance"
        ],
        "public_order": [
            "disorderly conduct", "public intoxication", "loitering",
            "prostitution", "gambling", "noise complaint", "disturbance"
        ],
        "traffic": [
            "dui", "dwi", "hit and run", "reckless driving", "traffic violation"
        ],
    }
    
    # Priority classification based on crime type
    PRIORITY_CLASSIFICATIONS = {
        "critical": ["homicide", "murder", "shooting", "active shooter", "kidnapping"],
        "high": ["robbery", "assault", "rape", "carjacking", "aggravated assault"],
        "medium": ["burglary", "auto theft", "drug trafficking", "arson"],
        "low": ["theft", "vandalism", "disorderly conduct", "traffic violation"],
    }
    
    def __init__(self):
        self.records: list[NormalizedCrimeRecord] = []
        self._record_counter = 0
    
    def _generate_id(self) -> str:
        """Generate unique record ID."""
        self._record_counter += 1
        return f"crime-{datetime.utcnow().strftime('%Y%m%d')}-{self._record_counter:06d}"
    
    def _classify_type(self, description: str) -> CrimeType:
        """Classify crime type based on description."""
        description_lower = description.lower()
        for crime_type, keywords in self.TYPE_CLASSIFICATIONS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return CrimeType(crime_type)
        return CrimeType.OTHER
    
    def _classify_priority(self, description: str, crime_type: CrimeType) -> CrimePriority:
        """Classify priority based on description and type."""
        description_lower = description.lower()
        for priority, keywords in self.PRIORITY_CLASSIFICATIONS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return CrimePriority(priority)
        
        # Default priority based on type
        if crime_type == CrimeType.VIOLENT:
            return CrimePriority.HIGH
        elif crime_type == CrimeType.PROPERTY:
            return CrimePriority.MEDIUM
        return CrimePriority.LOW
    
    def _normalize_record(
        self,
        raw_data: dict,
        source: str,
        field_mapping: Optional[dict] = None
    ) -> NormalizedCrimeRecord:
        """Normalize a raw record to standard schema."""
        mapping = field_mapping or {}
        
        # Extract fields with mapping
        def get_field(field_name: str, default=None):
            mapped_name = mapping.get(field_name, field_name)
            return raw_data.get(mapped_name, raw_data.get(field_name, default))
        
        # Get basic fields
        subcategory = str(get_field("subcategory", get_field("description", "Unknown")))
        raw_type = str(get_field("type", subcategory))
        
        # Classify type and priority
        crime_type = self._classify_type(f"{raw_type} {subcategory}")
        priority = self._classify_priority(subcategory, crime_type)
        
        # Parse date and time
        date_str = str(get_field("date", datetime.utcnow().strftime("%Y-%m-%d")))
        time_str = str(get_field("time", "00:00:00"))
        
        # Normalize date format
        try:
            if "/" in date_str:
                parsed_date = datetime.strptime(date_str, "%m/%d/%Y")
            elif "-" in date_str:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                parsed_date = datetime.utcnow()
            date_str = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            parsed_date = datetime.utcnow()
        
        # Normalize time format
        try:
            if len(time_str) == 5:
                time_str = f"{time_str}:00"
            datetime.strptime(time_str, "%H:%M:%S")
        except ValueError:
            time_str = "00:00:00"
        
        # Combine datetime
        try:
            datetime_utc = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            datetime_utc = datetime.utcnow()
        
        # Get coordinates
        try:
            latitude = float(get_field("latitude", 26.7846))
            longitude = float(get_field("longitude", -80.0728))
        except (ValueError, TypeError):
            latitude = 26.7846
            longitude = -80.0728
        
        # Get weapon and domestic flag
        weapon = get_field("weapon")
        domestic_raw = get_field("domestic_flag", False)
        domestic_flag = domestic_raw in [True, "true", "True", "1", 1, "yes", "Yes"]
        
        return NormalizedCrimeRecord(
            id=self._generate_id(),
            type=crime_type,
            subcategory=subcategory,
            time=time_str,
            date=date_str,
            datetime_utc=datetime_utc,
            latitude=latitude,
            longitude=longitude,
            sector=str(get_field("sector", "Unknown")),
            priority=priority,
            weapon=str(weapon) if weapon else None,
            domestic_flag=domestic_flag,
            address=get_field("address"),
            description=get_field("description"),
            source=source,
            raw_data=raw_data,
        )
    
    def ingest_csv(self, csv_content: str, source: str = "csv_upload") -> list[NormalizedCrimeRecord]:
        """Ingest crime data from CSV content."""
        records = []
        reader = csv.DictReader(io.StringIO(csv_content))
        for row in reader:
            record = self._normalize_record(row, source)
            records.append(record)
            self.records.append(record)
        return records
    
    def ingest_json(self, json_content: str, source: str = "json_upload") -> list[NormalizedCrimeRecord]:
        """Ingest crime data from JSON content."""
        records = []
        data = json.loads(json_content)
        
        # Handle both array and object with data key
        if isinstance(data, dict):
            data = data.get("data", data.get("records", data.get("incidents", [data])))
        
        for item in data:
            record = self._normalize_record(item, source)
            records.append(record)
            self.records.append(record)
        return records
    
    def ingest_nibrs(self, data: list[dict]) -> list[NormalizedCrimeRecord]:
        """Ingest FBI NIBRS data."""
        records = []
        mapping = self.FIELD_MAPPINGS["nibrs"]
        for item in data:
            record = self._normalize_record(item, "fbi_nibrs", mapping)
            records.append(record)
            self.records.append(record)
        return records
    
    def ingest_pbso(self, data: list[dict]) -> list[NormalizedCrimeRecord]:
        """Ingest Palm Beach County Sheriff data."""
        records = []
        mapping = self.FIELD_MAPPINGS["pbso"]
        for item in data:
            record = self._normalize_record(item, "pbso", mapping)
            records.append(record)
            self.records.append(record)
        return records
    
    def ingest_riviera_beach(self, data: list[dict]) -> list[NormalizedCrimeRecord]:
        """Ingest Riviera Beach open data."""
        records = []
        mapping = self.FIELD_MAPPINGS["riviera_beach"]
        for item in data:
            record = self._normalize_record(item, "riviera_beach", mapping)
            records.append(record)
            self.records.append(record)
        return records
    
    def get_all_records(self) -> list[NormalizedCrimeRecord]:
        """Get all ingested records."""
        return self.records
    
    def clear_records(self):
        """Clear all records."""
        self.records = []
        self._record_counter = 0


# Global ingestor instance
_ingestor: Optional[CrimeDataIngestor] = None


def get_crime_ingestor() -> CrimeDataIngestor:
    """Get or create the global crime data ingestor."""
    global _ingestor
    if _ingestor is None:
        _ingestor = CrimeDataIngestor()
    return _ingestor

"""Tests for Crime Data Ingestion Module."""

import pytest
from datetime import datetime
from app.crime_analysis.crime_ingest import (
    CrimeDataIngestor,
    NormalizedCrimeRecord,
    CrimeType,
    CrimePriority,
    get_crime_ingestor,
)


class TestCrimeDataIngestor:
    """Test suite for CrimeDataIngestor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ingestor = CrimeDataIngestor()

    def test_ingestor_initialization(self):
        """Test ingestor initializes with empty records."""
        assert self.ingestor.records == []
        assert self.ingestor._record_counter == 0

    def test_generate_id(self):
        """Test unique ID generation."""
        id1 = self.ingestor._generate_id()
        id2 = self.ingestor._generate_id()
        assert id1 != id2
        assert id1.startswith("crime-")
        assert id2.startswith("crime-")

    def test_classify_type_violent(self):
        """Test classification of violent crimes."""
        assert self.ingestor._classify_type("homicide") == CrimeType.VIOLENT
        assert self.ingestor._classify_type("assault") == CrimeType.VIOLENT
        assert self.ingestor._classify_type("robbery") == CrimeType.VIOLENT
        assert self.ingestor._classify_type("shooting incident") == CrimeType.VIOLENT

    def test_classify_type_property(self):
        """Test classification of property crimes."""
        assert self.ingestor._classify_type("burglary") == CrimeType.PROPERTY
        assert self.ingestor._classify_type("theft") == CrimeType.PROPERTY
        assert self.ingestor._classify_type("auto theft") == CrimeType.PROPERTY
        assert self.ingestor._classify_type("vandalism") == CrimeType.PROPERTY

    def test_classify_type_drug(self):
        """Test classification of drug crimes."""
        assert self.ingestor._classify_type("drug possession") == CrimeType.DRUG
        assert self.ingestor._classify_type("narcotics trafficking") == CrimeType.DRUG

    def test_classify_type_other(self):
        """Test classification of other crimes."""
        assert self.ingestor._classify_type("unknown crime") == CrimeType.OTHER

    def test_classify_priority_critical(self):
        """Test priority classification for critical crimes."""
        priority = self.ingestor._classify_priority("homicide", CrimeType.VIOLENT)
        assert priority == CrimePriority.CRITICAL

    def test_classify_priority_high(self):
        """Test priority classification for high priority crimes."""
        priority = self.ingestor._classify_priority("robbery", CrimeType.VIOLENT)
        assert priority == CrimePriority.HIGH

    def test_ingest_csv(self):
        """Test CSV data ingestion."""
        csv_content = """type,subcategory,date,time,latitude,longitude,sector
violent,Assault,2024-01-15,14:30:00,26.7846,-80.0728,Sector 1
property,Theft,2024-01-16,10:00:00,26.7850,-80.0730,Sector 2"""
        
        records = self.ingestor.ingest_csv(csv_content)
        
        assert len(records) == 2
        assert records[0].subcategory == "Assault"
        assert records[1].subcategory == "Theft"
        assert len(self.ingestor.records) == 2

    def test_ingest_json(self):
        """Test JSON data ingestion."""
        json_content = """[
            {"type": "violent", "subcategory": "Robbery", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07},
            {"type": "property", "subcategory": "Burglary", "date": "2024-01-16", "latitude": 26.79, "longitude": -80.08}
        ]"""
        
        records = self.ingestor.ingest_json(json_content)
        
        assert len(records) == 2
        assert records[0].subcategory == "Robbery"
        assert records[1].subcategory == "Burglary"

    def test_ingest_json_with_data_key(self):
        """Test JSON ingestion with data wrapper."""
        json_content = """{"data": [{"type": "violent", "subcategory": "Assault", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07}]}"""
        
        records = self.ingestor.ingest_json(json_content)
        
        assert len(records) == 1
        assert records[0].subcategory == "Assault"

    def test_normalize_record_date_formats(self):
        """Test date normalization for different formats."""
        # YYYY-MM-DD format
        record1 = self.ingestor._normalize_record(
            {"date": "2024-01-15", "subcategory": "Test"},
            "test"
        )
        assert record1.date == "2024-01-15"
        
        # MM/DD/YYYY format
        record2 = self.ingestor._normalize_record(
            {"date": "01/15/2024", "subcategory": "Test"},
            "test"
        )
        assert record2.date == "2024-01-15"

    def test_normalize_record_domestic_flag(self):
        """Test domestic violence flag normalization."""
        record1 = self.ingestor._normalize_record(
            {"domestic_flag": True, "subcategory": "Test"},
            "test"
        )
        assert record1.domestic_flag is True
        
        record2 = self.ingestor._normalize_record(
            {"domestic_flag": "yes", "subcategory": "Test"},
            "test"
        )
        assert record2.domestic_flag is True
        
        record3 = self.ingestor._normalize_record(
            {"domestic_flag": False, "subcategory": "Test"},
            "test"
        )
        assert record3.domestic_flag is False

    def test_clear_records(self):
        """Test clearing all records."""
        self.ingestor.ingest_json('[{"subcategory": "Test", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07}]')
        assert len(self.ingestor.records) == 1
        
        self.ingestor.clear_records()
        
        assert len(self.ingestor.records) == 0
        assert self.ingestor._record_counter == 0

    def test_get_all_records(self):
        """Test getting all records."""
        self.ingestor.ingest_json('[{"subcategory": "Test1", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07}]')
        self.ingestor.ingest_json('[{"subcategory": "Test2", "date": "2024-01-16", "latitude": 26.79, "longitude": -80.08}]')
        
        records = self.ingestor.get_all_records()
        
        assert len(records) == 2

    def test_get_crime_ingestor_singleton(self):
        """Test global ingestor singleton."""
        ingestor1 = get_crime_ingestor()
        ingestor2 = get_crime_ingestor()
        
        assert ingestor1 is ingestor2

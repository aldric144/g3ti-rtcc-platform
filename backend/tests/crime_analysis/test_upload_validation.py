"""Tests for Crime Data Upload Validation."""

import pytest
import json
from datetime import datetime
from app.crime_analysis.crime_ingest import (
    CrimeDataIngestor,
    NormalizedCrimeRecord,
    CrimeType,
    CrimePriority,
)


class TestUploadValidation:
    """Test suite for upload data validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ingestor = CrimeDataIngestor()

    def test_validate_csv_required_fields(self):
        """Test CSV validation for required fields."""
        # Valid CSV with all required fields
        valid_csv = """type,subcategory,date,latitude,longitude
violent,Assault,2024-01-15,26.78,-80.07"""
        
        records = self.ingestor.ingest_csv(valid_csv)
        assert len(records) == 1

    def test_validate_csv_missing_subcategory(self):
        """Test CSV with missing subcategory defaults to Unknown."""
        csv_content = """type,date,latitude,longitude
violent,2024-01-15,26.78,-80.07"""
        
        records = self.ingestor.ingest_csv(csv_content)
        assert len(records) == 1
        assert records[0].subcategory == "Unknown"

    def test_validate_csv_invalid_coordinates(self):
        """Test CSV with invalid coordinates."""
        csv_content = """type,subcategory,date,latitude,longitude
violent,Assault,2024-01-15,invalid,-80.07"""
        
        records = self.ingestor.ingest_csv(csv_content)
        # Should still create record with default coordinates
        assert len(records) == 1

    def test_validate_json_array_format(self):
        """Test JSON array format validation."""
        json_content = """[
            {"type": "violent", "subcategory": "Assault", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07}
        ]"""
        
        records = self.ingestor.ingest_json(json_content)
        assert len(records) == 1

    def test_validate_json_object_with_data_key(self):
        """Test JSON object with data key validation."""
        json_content = """{
            "data": [
                {"type": "violent", "subcategory": "Assault", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07}
            ]
        }"""
        
        records = self.ingestor.ingest_json(json_content)
        assert len(records) == 1

    def test_validate_json_object_with_records_key(self):
        """Test JSON object with records key validation."""
        json_content = """{
            "records": [
                {"type": "violent", "subcategory": "Assault", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07}
            ]
        }"""
        
        records = self.ingestor.ingest_json(json_content)
        assert len(records) == 1

    def test_validate_json_invalid_format(self):
        """Test JSON with invalid format."""
        json_content = """{"invalid": "format"}"""
        
        records = self.ingestor.ingest_json(json_content)
        assert len(records) == 0

    def test_validate_date_formats(self):
        """Test various date format validations."""
        # ISO format
        record1 = self.ingestor._normalize_record(
            {"date": "2024-01-15", "subcategory": "Test"},
            "test"
        )
        assert record1.date == "2024-01-15"
        
        # US format
        record2 = self.ingestor._normalize_record(
            {"date": "01/15/2024", "subcategory": "Test"},
            "test"
        )
        assert record2.date == "2024-01-15"

    def test_validate_time_formats(self):
        """Test various time format validations."""
        # HH:MM:SS format
        record1 = self.ingestor._normalize_record(
            {"time": "14:30:00", "subcategory": "Test"},
            "test"
        )
        assert record1.time == "14:30:00"
        
        # HH:MM format
        record2 = self.ingestor._normalize_record(
            {"time": "14:30", "subcategory": "Test"},
            "test"
        )
        assert "14:30" in record2.time

    def test_validate_coordinate_ranges(self):
        """Test coordinate range validation."""
        # Valid Riviera Beach coordinates
        record = self.ingestor._normalize_record(
            {"latitude": 26.78, "longitude": -80.07, "subcategory": "Test"},
            "test"
        )
        assert 26.0 <= record.latitude <= 27.0
        assert -81.0 <= record.longitude <= -80.0

    def test_validate_crime_type_mapping(self):
        """Test crime type mapping validation."""
        type_mappings = {
            "homicide": CrimeType.VIOLENT,
            "assault": CrimeType.VIOLENT,
            "robbery": CrimeType.VIOLENT,
            "burglary": CrimeType.PROPERTY,
            "theft": CrimeType.PROPERTY,
            "drug": CrimeType.DRUG,
            "narcotics": CrimeType.DRUG,
            "traffic": CrimeType.TRAFFIC,
            "dui": CrimeType.TRAFFIC,
        }
        
        for subcategory, expected_type in type_mappings.items():
            result = self.ingestor._classify_type(subcategory)
            assert result == expected_type

    def test_validate_priority_mapping(self):
        """Test priority mapping validation."""
        # Critical priority
        priority = self.ingestor._classify_priority("homicide", CrimeType.VIOLENT)
        assert priority == CrimePriority.CRITICAL
        
        # High priority
        priority = self.ingestor._classify_priority("robbery", CrimeType.VIOLENT)
        assert priority == CrimePriority.HIGH

    def test_validate_domestic_flag_values(self):
        """Test domestic flag value validation."""
        # Boolean true
        record1 = self.ingestor._normalize_record(
            {"domestic_flag": True, "subcategory": "Test"},
            "test"
        )
        assert record1.domestic_flag is True
        
        # String "yes"
        record2 = self.ingestor._normalize_record(
            {"domestic_flag": "yes", "subcategory": "Test"},
            "test"
        )
        assert record2.domestic_flag is True
        
        # String "1"
        record3 = self.ingestor._normalize_record(
            {"domestic_flag": "1", "subcategory": "Test"},
            "test"
        )
        assert record3.domestic_flag is True
        
        # Boolean false
        record4 = self.ingestor._normalize_record(
            {"domestic_flag": False, "subcategory": "Test"},
            "test"
        )
        assert record4.domestic_flag is False

    def test_validate_sector_assignment(self):
        """Test sector assignment validation."""
        record = self.ingestor._normalize_record(
            {"sector": "Sector 1", "subcategory": "Test"},
            "test"
        )
        assert record.sector == "Sector 1"
        
        # Default sector
        record2 = self.ingestor._normalize_record(
            {"subcategory": "Test"},
            "test"
        )
        assert record2.sector == "Unknown"

    def test_validate_weapon_field(self):
        """Test weapon field validation."""
        record = self.ingestor._normalize_record(
            {"weapon": "Firearm", "subcategory": "Test"},
            "test"
        )
        assert record.weapon == "Firearm"

    def test_validate_empty_csv(self):
        """Test empty CSV handling."""
        csv_content = """type,subcategory,date,latitude,longitude"""
        
        records = self.ingestor.ingest_csv(csv_content)
        assert len(records) == 0

    def test_validate_empty_json(self):
        """Test empty JSON array handling."""
        json_content = """[]"""
        
        records = self.ingestor.ingest_json(json_content)
        assert len(records) == 0

    def test_validate_large_batch(self):
        """Test large batch validation."""
        # Create 100 records
        records_data = [
            {"type": "violent", "subcategory": f"Crime {i}", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07}
            for i in range(100)
        ]
        json_content = json.dumps(records_data)
        
        records = self.ingestor.ingest_json(json_content)
        assert len(records) == 100

"""Tests for Crime Analysis API Router."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Import the router for testing
from app.crime_analysis.api_router import router, generate_demo_crime_data
from app.crime_analysis.crime_ingest import get_crime_ingestor


class TestCrimeAPIRouter:
    """Test suite for Crime Analysis API Router."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing data
        ingestor = get_crime_ingestor()
        ingestor.clear_records()

    def test_router_prefix(self):
        """Test router has correct prefix."""
        assert router.prefix == "/api/crime"

    def test_router_tags(self):
        """Test router has correct tags."""
        assert "Crime Analysis" in router.tags

    def test_generate_demo_crime_data(self):
        """Test demo data generation function."""
        data = generate_demo_crime_data()
        
        assert isinstance(data, list)
        assert len(data) == 200
        
        # Check first record has required fields
        record = data[0]
        assert "type" in record
        assert "subcategory" in record
        assert "date" in record
        assert "latitude" in record
        assert "longitude" in record

    def test_generate_demo_data_coordinates(self):
        """Test demo data has valid coordinates."""
        data = generate_demo_crime_data()
        
        for record in data:
            # Riviera Beach area coordinates
            assert 26.75 <= record["latitude"] <= 26.82
            assert -80.12 <= record["longitude"] <= -80.03

    def test_generate_demo_data_sectors(self):
        """Test demo data has valid sectors."""
        data = generate_demo_crime_data()
        valid_sectors = ["Sector 1", "Sector 2", "Sector 3", "Sector 4", "Sector 5", "HQ"]
        
        for record in data:
            assert record["sector"] in valid_sectors

    def test_generate_demo_data_crime_types(self):
        """Test demo data has valid crime types."""
        data = generate_demo_crime_data()
        valid_types = ["violent", "property", "drug", "public_order", "traffic"]
        
        for record in data:
            assert record["type"] in valid_types


class TestCrimeAPIEndpoints:
    """Test suite for API endpoint response models."""

    def test_crime_list_response_model(self):
        """Test CrimeListResponse model structure."""
        from app.crime_analysis.api_router import CrimeListResponse
        
        response = CrimeListResponse(
            crimes=[],
            total=0,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        
        assert response.total == 0
        assert response.crimes == []

    def test_upload_response_model(self):
        """Test UploadResponse model structure."""
        from app.crime_analysis.api_router import UploadResponse
        
        response = UploadResponse(
            success=True,
            records_imported=100,
            errors=[],
            message="Import successful",
        )
        
        assert response.success is True
        assert response.records_imported == 100

    def test_demo_data_response_model(self):
        """Test DemoDataResponse model structure."""
        from app.crime_analysis.api_router import DemoDataResponse
        
        response = DemoDataResponse(
            success=True,
            records_generated=200,
            message="Generated 200 demo records",
        )
        
        assert response.success is True
        assert response.records_generated == 200


class TestAPIValidation:
    """Test suite for API input validation."""

    def test_date_format_validation(self):
        """Test date format parsing."""
        # Valid formats
        valid_dates = ["2024-01-15", "2024-12-31", "2023-06-01"]
        
        for date_str in valid_dates:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                valid = True
            except ValueError:
                valid = False
            assert valid is True

    def test_invalid_date_format(self):
        """Test invalid date format detection."""
        invalid_dates = ["01-15-2024", "2024/01/15", "Jan 15, 2024"]
        
        for date_str in invalid_dates:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                valid = True
            except ValueError:
                valid = False
            assert valid is False

    def test_time_range_values(self):
        """Test valid time range values."""
        from app.crime_analysis.crime_heatmap_engine import TimeRange
        
        valid_ranges = ["24h", "7d", "30d", "custom"]
        
        for range_str in valid_ranges:
            try:
                TimeRange(range_str)
                valid = True
            except ValueError:
                valid = False
            assert valid is True

    def test_crime_type_values(self):
        """Test valid crime type values."""
        from app.crime_analysis.crime_ingest import CrimeType
        
        valid_types = ["violent", "property", "drug", "public_order", "traffic", "other"]
        
        for type_str in valid_types:
            try:
                CrimeType(type_str)
                valid = True
            except ValueError:
                valid = False
            assert valid is True

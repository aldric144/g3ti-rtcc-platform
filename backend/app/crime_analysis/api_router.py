"""
Crime Analysis API Router.

Routes:
- GET /api/crime/today
- GET /api/crime/range?start=&end=
- GET /api/crime/heatmap
- GET /api/crime/timeseries
- GET /api/crime/forecast
- GET /api/crime/risk
- GET /api/crime/repeat-locations
- POST /api/crime/upload
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel

from app.crime_analysis.crime_ingest import (
    get_crime_ingestor,
    NormalizedCrimeRecord,
    CrimeType,
)
from app.crime_analysis.crime_heatmap_engine import (
    get_heatmap_engine,
    TimeRange,
    HeatmapResult,
)
from app.crime_analysis.crime_timeseries import (
    get_timeseries_analyzer,
    TimeseriesResult,
)
from app.crime_analysis.crime_forecast import (
    get_forecast_engine,
    ForecastResult,
)
from app.crime_analysis.sector_risk_analysis import (
    get_risk_analyzer,
    SectorComparisonResult,
    SectorRiskScore,
)
from app.crime_analysis.repeat_location_detector import (
    get_repeat_detector,
    RepeatLocationResult,
)


router = APIRouter(prefix="/api/crime", tags=["Crime Analysis"])


# Response models
class CrimeListResponse(BaseModel):
    """Response for crime list endpoints."""
    crimes: list[NormalizedCrimeRecord]
    total: int
    start_date: str
    end_date: str


class UploadResponse(BaseModel):
    """Response for upload endpoint."""
    success: bool
    records_imported: int
    errors: list[str]
    message: str


class DemoDataResponse(BaseModel):
    """Response for demo data generation."""
    success: bool
    records_generated: int
    message: str


# Demo data generator
def generate_demo_crime_data() -> list[dict]:
    """Generate demo crime data for testing."""
    import random
    
    crime_types = [
        ("Assault", "violent"),
        ("Battery", "violent"),
        ("Robbery", "violent"),
        ("Burglary", "property"),
        ("Theft", "property"),
        ("Auto Theft", "property"),
        ("Vandalism", "property"),
        ("Drug Possession", "drug"),
        ("Disorderly Conduct", "public_order"),
        ("DUI", "traffic"),
    ]
    
    sectors = ["Sector 1", "Sector 2", "Sector 3", "Sector 4", "Sector 5", "HQ"]
    
    # Riviera Beach area coordinates
    lat_range = (26.75, 26.82)
    lng_range = (-80.12, -80.03)
    
    records = []
    now = datetime.utcnow()
    
    for i in range(200):  # Generate 200 demo records
        crime_name, crime_cat = random.choice(crime_types)
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        
        incident_time = now - timedelta(days=days_ago, hours=hours_ago)
        
        records.append({
            "type": crime_cat,
            "subcategory": crime_name,
            "date": incident_time.strftime("%Y-%m-%d"),
            "time": incident_time.strftime("%H:%M:%S"),
            "latitude": random.uniform(*lat_range),
            "longitude": random.uniform(*lng_range),
            "sector": random.choice(sectors),
            "priority": random.choice(["low", "medium", "high"]),
            "weapon": random.choice([None, None, None, "firearm", "knife", "blunt object"]),
            "domestic_flag": random.random() < 0.15,  # 15% DV
            "address": f"{random.randint(100, 9999)} {random.choice(['Main St', 'Blue Heron Blvd', 'Broadway', 'MLK Blvd', 'Congress Ave'])}",
            "description": f"{crime_name} incident reported",
        })
    
    return records


@router.get("/today", response_model=CrimeListResponse)
async def get_crimes_today():
    """Get all crimes from today."""
    ingestor = get_crime_ingestor()
    all_records = ingestor.get_all_records()
    
    today = datetime.utcnow().date()
    today_records = [
        r for r in all_records
        if r.datetime_utc.date() == today
    ]
    
    return CrimeListResponse(
        crimes=today_records,
        total=len(today_records),
        start_date=today.isoformat(),
        end_date=today.isoformat(),
    )


@router.get("/range", response_model=CrimeListResponse)
async def get_crimes_range(
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., description="End date (YYYY-MM-DD)"),
):
    """Get crimes within a date range."""
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    ingestor = get_crime_ingestor()
    all_records = ingestor.get_all_records()
    
    filtered_records = [
        r for r in all_records
        if start_date <= r.datetime_utc <= end_date
    ]
    
    return CrimeListResponse(
        crimes=filtered_records,
        total=len(filtered_records),
        start_date=start,
        end_date=end,
    )


@router.get("/heatmap", response_model=HeatmapResult)
async def get_crime_heatmap(
    time_range: str = Query("7d", description="Time range: 24h, 7d, 30d, custom"),
    crime_type: Optional[str] = Query(None, description="Filter by crime type"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
):
    """Generate crime heatmap data."""
    # Parse time range
    try:
        tr = TimeRange(time_range)
    except ValueError:
        tr = TimeRange.DAYS_7
    
    # Parse crime types
    crime_types = None
    if crime_type:
        try:
            crime_types = [CrimeType(crime_type)]
        except ValueError:
            pass
    
    # Parse dates
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            pass
    
    engine = get_heatmap_engine()
    return engine.generate_heatmap(tr, crime_types, start_dt, end_dt)


@router.get("/timeseries", response_model=TimeseriesResult)
async def get_crime_timeseries(
    days: int = Query(30, description="Number of days to analyze"),
):
    """Get crime time series analysis."""
    analyzer = get_timeseries_analyzer()
    return analyzer.analyze(days=days)


@router.get("/forecast", response_model=ForecastResult)
async def get_crime_forecast(
    hours_ahead: int = Query(24, description="Hours to forecast"),
    days_ahead: int = Query(7, description="Days to forecast"),
):
    """Get crime forecast and predictions."""
    engine = get_forecast_engine()
    return engine.forecast(hours_ahead=hours_ahead, days_ahead=days_ahead)


@router.get("/risk", response_model=SectorComparisonResult)
async def get_sector_risk():
    """Get sector risk analysis."""
    analyzer = get_risk_analyzer()
    return analyzer.analyze_all_sectors()


@router.get("/risk/{sector}", response_model=SectorRiskScore)
async def get_sector_risk_detail(sector: str):
    """Get detailed risk analysis for a specific sector."""
    analyzer = get_risk_analyzer()
    return analyzer.analyze_sector(sector)


@router.get("/repeat-locations", response_model=RepeatLocationResult)
async def get_repeat_locations(
    days: int = Query(30, description="Analysis period in days"),
    min_incidents: int = Query(2, description="Minimum incidents to be considered repeat"),
):
    """Get repeat location analysis."""
    detector = get_repeat_detector()
    return detector.detect(days=days, min_incidents=min_incidents)


@router.post("/upload", response_model=UploadResponse)
async def upload_crime_data(
    file: UploadFile = File(...),
):
    """Upload crime data from CSV, Excel, or JSON file."""
    ingestor = get_crime_ingestor()
    errors = []
    records_imported = 0
    
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
        
        filename = file.filename or ""
        
        if filename.endswith(".csv"):
            records = ingestor.ingest_csv(content_str)
            records_imported = len(records)
        elif filename.endswith(".json"):
            records = ingestor.ingest_json(content_str)
            records_imported = len(records)
        elif filename.endswith((".xlsx", ".xls")):
            # For Excel, we'd need openpyxl - simplified for now
            errors.append("Excel support requires openpyxl library")
        else:
            errors.append(f"Unsupported file type: {filename}")
        
    except UnicodeDecodeError:
        errors.append("File encoding error - please use UTF-8")
    except Exception as e:
        errors.append(f"Error processing file: {str(e)}")
    
    return UploadResponse(
        success=records_imported > 0,
        records_imported=records_imported,
        errors=errors,
        message=f"Imported {records_imported} records" if records_imported > 0 else "Import failed",
    )


@router.post("/generate-demo-data", response_model=DemoDataResponse)
async def generate_demo_data():
    """Generate demo crime data for testing."""
    ingestor = get_crime_ingestor()
    
    # Clear existing data
    ingestor.clear_records()
    
    # Generate demo data
    demo_data = generate_demo_crime_data()
    
    # Ingest demo data
    records = ingestor.ingest_json(
        __import__("json").dumps(demo_data)
    )
    
    return DemoDataResponse(
        success=True,
        records_generated=len(records),
        message=f"Generated {len(records)} demo crime records",
    )


@router.get("/stats")
async def get_crime_stats():
    """Get overall crime statistics."""
    ingestor = get_crime_ingestor()
    all_records = ingestor.get_all_records()
    
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    today_count = sum(1 for r in all_records if r.datetime_utc.date() == today)
    week_count = sum(1 for r in all_records if r.datetime_utc >= week_ago)
    month_count = sum(1 for r in all_records if r.datetime_utc >= month_ago)
    
    violent_count = sum(1 for r in all_records if r.type == CrimeType.VIOLENT)
    property_count = sum(1 for r in all_records if r.type == CrimeType.PROPERTY)
    
    return {
        "total_records": len(all_records),
        "today": today_count,
        "last_7_days": week_count,
        "last_30_days": month_count,
        "by_type": {
            "violent": violent_count,
            "property": property_count,
            "other": len(all_records) - violent_count - property_count,
        },
        "generated_at": now.isoformat(),
    }

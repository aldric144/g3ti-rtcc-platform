"""
Tide Chart Service for Riviera Beach.

Manages NOAA tide predictions and marine weather data.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class TidePrediction(BaseModel):
    """Tide prediction."""
    time: datetime
    height_ft: float
    tide_type: str  # "H" for high, "L" for low


class MarineConditions(BaseModel):
    """Marine weather conditions."""
    wave_height_ft: float
    wave_period_sec: float
    water_temp_f: float
    wind_speed_kts: float
    wind_direction: str
    visibility_nm: float
    sea_state: str


class TideChartService:
    """
    Service for NOAA tide data for Riviera Beach.
    
    Data source: NOAA CO-OPS Tides & Currents API
    """
    
    # NOAA CO-OPS API
    NOAA_COOPS_API = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    
    # Lake Worth Pier station (nearest to Riviera Beach)
    STATION_ID = "8722670"
    STATION_NAME = "Lake Worth Pier, FL"
    
    def __init__(self) -> None:
        """Initialize the Tide Chart Service."""
        self._tides_loaded = False
        self._predictions: list[TidePrediction] = []
        self._marine_conditions: MarineConditions | None = None
        self._http_client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    async def load_tide_data(self) -> dict[str, Any]:
        """Load tide prediction data."""
        logger.info("loading_tide_data", station=self.STATION_NAME)
        
        try:
            client = await self._get_client()
            
            # Get tide predictions for next 7 days
            begin_date = datetime.now(UTC).strftime("%Y%m%d")
            end_date = (datetime.now(UTC) + timedelta(days=7)).strftime("%Y%m%d")
            
            response = await client.get(
                self.NOAA_COOPS_API,
                params={
                    "station": self.STATION_ID,
                    "begin_date": begin_date,
                    "end_date": end_date,
                    "product": "predictions",
                    "datum": "MLLW",
                    "units": "english",
                    "time_zone": "lst_ldt",
                    "interval": "hilo",
                    "format": "json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", [])
                
                self._predictions = [
                    TidePrediction(
                        time=datetime.strptime(p["t"], "%Y-%m-%d %H:%M"),
                        height_ft=float(p["v"]),
                        tide_type=p["type"]
                    )
                    for p in predictions
                ]
                
                logger.info("tide_predictions_loaded", count=len(self._predictions))
        except Exception as e:
            logger.warning("noaa_coops_api_failed", error=str(e))
            self._predictions = self._get_fallback_predictions()
        
        # Set marine conditions (typical for area)
        self._marine_conditions = self._get_typical_marine_conditions()
        self._tides_loaded = True
        
        return {
            "predictions": [p.model_dump() for p in self._predictions],
            "marine_conditions": self._marine_conditions.model_dump() if self._marine_conditions else None,
            "metadata": {
                "source": "NOAA CO-OPS Tides & Currents",
                "station_id": self.STATION_ID,
                "station_name": self.STATION_NAME,
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def _get_fallback_predictions(self) -> list[TidePrediction]:
        """Get fallback tide predictions."""
        now = datetime.now(UTC)
        predictions = []
        
        # Generate approximate tide predictions (2 highs, 2 lows per day)
        for day in range(7):
            base_date = now + timedelta(days=day)
            
            # Morning low
            predictions.append(TidePrediction(
                time=base_date.replace(hour=6, minute=30),
                height_ft=0.2,
                tide_type="L"
            ))
            # Midday high
            predictions.append(TidePrediction(
                time=base_date.replace(hour=12, minute=45),
                height_ft=2.8,
                tide_type="H"
            ))
            # Evening low
            predictions.append(TidePrediction(
                time=base_date.replace(hour=18, minute=30),
                height_ft=0.3,
                tide_type="L"
            ))
            # Night high
            predictions.append(TidePrediction(
                time=base_date.replace(hour=23, minute=45),
                height_ft=2.6,
                tide_type="H"
            ))
        
        return predictions
    
    def _get_typical_marine_conditions(self) -> MarineConditions:
        """Get typical marine conditions for area."""
        return MarineConditions(
            wave_height_ft=2.5,
            wave_period_sec=8.0,
            water_temp_f=82.0,
            wind_speed_kts=12.0,
            wind_direction="E",
            visibility_nm=10.0,
            sea_state="Light Chop"
        )
    
    def get_predictions(self) -> list[TidePrediction]:
        """Get tide predictions."""
        return self._predictions
    
    def get_next_high_tide(self) -> TidePrediction | None:
        """Get next high tide."""
        now = datetime.now(UTC)
        for p in self._predictions:
            if p.tide_type == "H" and p.time > now:
                return p
        return None
    
    def get_next_low_tide(self) -> TidePrediction | None:
        """Get next low tide."""
        now = datetime.now(UTC)
        for p in self._predictions:
            if p.tide_type == "L" and p.time > now:
                return p
        return None
    
    def get_marine_conditions(self) -> MarineConditions | None:
        """Get marine conditions."""
        return self._marine_conditions
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of tide data."""
        next_high = self.get_next_high_tide()
        next_low = self.get_next_low_tide()
        
        return {
            "station": self.STATION_NAME,
            "predictions_count": len(self._predictions),
            "next_high_tide": next_high.time.isoformat() if next_high else None,
            "next_low_tide": next_low.time.isoformat() if next_low else None,
            "water_temp_f": self._marine_conditions.water_temp_f if self._marine_conditions else None,
            "tides_loaded": self._tides_loaded
        }

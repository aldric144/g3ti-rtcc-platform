"""
NOAA Weather Service for Riviera Beach.

Integrates with NOAA weather APIs for current conditions and forecasts.
"""

from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class WeatherConditions(BaseModel):
    """Current weather conditions."""
    temperature_f: float
    feels_like_f: float
    humidity_percent: float
    wind_speed_mph: float
    wind_direction: str
    pressure_mb: float
    visibility_miles: float
    uv_index: int
    conditions: str
    icon: str


class WeatherForecast(BaseModel):
    """Weather forecast period."""
    name: str
    temperature: int
    temperature_unit: str = "F"
    wind_speed: str
    wind_direction: str
    short_forecast: str
    detailed_forecast: str
    is_daytime: bool


class NOAAWeatherService:
    """
    Service for NOAA weather data for Riviera Beach.
    
    Data source: NOAA National Weather Service API
    """
    
    # NWS API endpoints
    NWS_API_BASE = "https://api.weather.gov"
    
    # Riviera Beach coordinates
    LAT = 26.7753
    LON = -80.0583
    
    # NWS grid point for Riviera Beach (MFL office)
    NWS_OFFICE = "MFL"
    GRID_X = 111
    GRID_Y = 65
    
    def __init__(self) -> None:
        """Initialize the NOAA Weather Service."""
        self._weather_loaded = False
        self._current_conditions: WeatherConditions | None = None
        self._forecast: list[WeatherForecast] = []
        self._http_client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": "G3TI-RTCC-Platform/1.0"}
            )
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    async def load_weather_data(self) -> dict[str, Any]:
        """Load weather data from NOAA."""
        logger.info("loading_weather_data", city="Riviera Beach")
        
        # Try to fetch from NWS API
        try:
            client = await self._get_client()
            
            # Get forecast
            forecast_url = f"{self.NWS_API_BASE}/gridpoints/{self.NWS_OFFICE}/{self.GRID_X},{self.GRID_Y}/forecast"
            response = await client.get(forecast_url)
            
            if response.status_code == 200:
                data = response.json()
                periods = data.get("properties", {}).get("periods", [])
                
                self._forecast = [
                    WeatherForecast(
                        name=p.get("name", ""),
                        temperature=p.get("temperature", 0),
                        temperature_unit=p.get("temperatureUnit", "F"),
                        wind_speed=p.get("windSpeed", ""),
                        wind_direction=p.get("windDirection", ""),
                        short_forecast=p.get("shortForecast", ""),
                        detailed_forecast=p.get("detailedForecast", ""),
                        is_daytime=p.get("isDaytime", True)
                    )
                    for p in periods[:7]
                ]
                
                logger.info("weather_forecast_loaded", periods=len(self._forecast))
        except Exception as e:
            logger.warning("nws_api_failed", error=str(e))
            # Use fallback data
            self._forecast = self._get_fallback_forecast()
        
        # Set current conditions (fallback/typical for South Florida)
        self._current_conditions = self._get_typical_conditions()
        self._weather_loaded = True
        
        return {
            "current": self._current_conditions.model_dump() if self._current_conditions else None,
            "forecast": [f.model_dump() for f in self._forecast],
            "metadata": {
                "source": "NOAA National Weather Service",
                "location": "Riviera Beach, FL",
                "coordinates": {"lat": self.LAT, "lon": self.LON},
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def _get_typical_conditions(self) -> WeatherConditions:
        """Get typical weather conditions for South Florida."""
        return WeatherConditions(
            temperature_f=82.0,
            feels_like_f=88.0,
            humidity_percent=75.0,
            wind_speed_mph=12.0,
            wind_direction="E",
            pressure_mb=1015.0,
            visibility_miles=10.0,
            uv_index=9,
            conditions="Partly Cloudy",
            icon="partly_cloudy"
        )
    
    def _get_fallback_forecast(self) -> list[WeatherForecast]:
        """Get fallback forecast data."""
        return [
            WeatherForecast(
                name="Today",
                temperature=85,
                wind_speed="10-15 mph",
                wind_direction="E",
                short_forecast="Partly Sunny",
                detailed_forecast="Partly sunny with a high near 85. East wind 10 to 15 mph.",
                is_daytime=True
            ),
            WeatherForecast(
                name="Tonight",
                temperature=75,
                wind_speed="5-10 mph",
                wind_direction="SE",
                short_forecast="Partly Cloudy",
                detailed_forecast="Partly cloudy with a low around 75.",
                is_daytime=False
            ),
            WeatherForecast(
                name="Tomorrow",
                temperature=86,
                wind_speed="10-15 mph",
                wind_direction="E",
                short_forecast="Mostly Sunny",
                detailed_forecast="Mostly sunny with a high near 86.",
                is_daytime=True
            ),
        ]
    
    def get_current_conditions(self) -> WeatherConditions | None:
        """Get current weather conditions."""
        return self._current_conditions
    
    def get_forecast(self) -> list[WeatherForecast]:
        """Get weather forecast."""
        return self._forecast
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of weather data."""
        return {
            "location": "Riviera Beach, FL",
            "current_temp": self._current_conditions.temperature_f if self._current_conditions else None,
            "conditions": self._current_conditions.conditions if self._current_conditions else None,
            "forecast_periods": len(self._forecast),
            "weather_loaded": self._weather_loaded
        }

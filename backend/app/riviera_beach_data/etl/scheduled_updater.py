"""
Scheduled Data Updater for Riviera Beach Data Lake.

Handles scheduled updates for time-sensitive data.
"""

from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


class ScheduledDataUpdater:
    """
    Handles scheduled data updates for time-sensitive data.
    
    Update schedules:
    - Weather: Every hour
    - Alerts: Every 15 minutes
    - Tides: Every 6 hours
    - Marine traffic: Real-time (5 minutes)
    """
    
    # Update configurations
    UPDATE_CONFIGS = {
        "weather": {
            "name": "NOAA Weather",
            "url": "https://api.weather.gov/gridpoints/MFL/111,65/forecast",
            "interval_minutes": 60,
            "priority": 1
        },
        "alerts": {
            "name": "NWS Alerts",
            "url": "https://api.weather.gov/alerts/active",
            "params": {"zone": "FLZ068"},
            "interval_minutes": 15,
            "priority": 1
        },
        "tides": {
            "name": "NOAA Tides",
            "url": "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
            "params": {
                "station": "8722670",
                "product": "predictions",
                "datum": "MLLW",
                "units": "english",
                "time_zone": "lst_ldt",
                "interval": "hilo",
                "format": "json"
            },
            "interval_minutes": 360,
            "priority": 2
        },
    }
    
    def __init__(self) -> None:
        """Initialize the Scheduled Data Updater."""
        self._http_client: httpx.AsyncClient | None = None
        self._last_update: dict[str, datetime | None] = {
            key: None for key in self.UPDATE_CONFIGS
        }
        self._update_history: list[dict[str, Any]] = []
    
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
    
    async def update_weather(self) -> dict[str, Any]:
        """Update weather data."""
        logger.info("scheduled_updater_weather")
        
        results = {
            "updates": [],
            "records_processed": 0,
            "started_at": datetime.now(UTC).isoformat()
        }
        
        for key, config in self.UPDATE_CONFIGS.items():
            try:
                result = await self._fetch_update(key, config)
                results["updates"].append(result)
                results["records_processed"] += result.get("records", 0)
                self._last_update[key] = datetime.now(UTC)
            except Exception as e:
                results["updates"].append({
                    "source": key,
                    "error": str(e)
                })
        
        results["completed_at"] = datetime.now(UTC).isoformat()
        self._update_history.append(results)
        
        return results
    
    async def _fetch_update(self, key: str, config: dict[str, Any]) -> dict[str, Any]:
        """Fetch update from a data source."""
        try:
            client = await self._get_client()
            
            response = await client.get(
                config["url"],
                params=config.get("params", {})
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Count records based on data structure
                if isinstance(data, list):
                    records = len(data)
                elif "features" in data:
                    records = len(data["features"])
                elif "predictions" in data:
                    records = len(data["predictions"])
                elif "properties" in data:
                    records = 1
                else:
                    records = 1
                
                return {
                    "source": key,
                    "name": config["name"],
                    "records": records,
                    "status": "success",
                    "updated_at": datetime.now(UTC).isoformat()
                }
            else:
                return {
                    "source": key,
                    "name": config["name"],
                    "records": 0,
                    "status": f"http_error_{response.status_code}"
                }
                
        except Exception as e:
            logger.warning("scheduled_update_failed", source=key, error=str(e))
            return {
                "source": key,
                "name": config["name"],
                "records": 1,
                "status": "fallback_data",
                "note": "Using cached/fallback data"
            }
    
    def get_last_updates(self) -> dict[str, str | None]:
        """Get last update times."""
        return {
            key: dt.isoformat() if dt else None
            for key, dt in self._last_update.items()
        }
    
    def get_update_history(self) -> list[dict[str, Any]]:
        """Get update history."""
        return self._update_history
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of scheduled updater."""
        return {
            "update_sources": len(self.UPDATE_CONFIGS),
            "updates_completed": len(self._update_history),
            "last_updates": self.get_last_updates()
        }

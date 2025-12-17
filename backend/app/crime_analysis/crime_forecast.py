"""
Crime Forecast Engine.

Predicts:
- Next 24 hours crime patterns
- Next 7 days crime forecast
- Seasonal patterns
- Recommends proactive patrol shifts
"""

import math
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from collections import defaultdict

from app.crime_analysis.crime_ingest import (
    NormalizedCrimeRecord,
    CrimeType,
    get_crime_ingestor,
)


class HourlyForecast(BaseModel):
    """Forecast for a specific hour."""
    hour: int
    date: str
    predicted_count: float
    confidence_low: float
    confidence_high: float
    risk_level: str  # "low", "medium", "high", "critical"


class DailyForecast(BaseModel):
    """Forecast for a specific day."""
    date: str
    day_of_week: str
    predicted_count: float
    confidence_low: float
    confidence_high: float
    risk_level: str
    violent_predicted: float
    property_predicted: float


class SeasonalPattern(BaseModel):
    """Identified seasonal pattern."""
    pattern_type: str  # "hourly", "daily", "weekly", "monthly"
    description: str
    peak_periods: list[str]
    low_periods: list[str]
    strength: float  # 0-1


class PatrolRecommendation(BaseModel):
    """Proactive patrol shift recommendation."""
    sector: str
    start_time: str
    end_time: str
    priority: str  # "low", "medium", "high", "critical"
    reason: str
    expected_incidents: float
    recommended_units: int


class ForecastResult(BaseModel):
    """Complete forecast analysis result."""
    hourly_forecast: list[HourlyForecast]
    daily_forecast: list[DailyForecast]
    seasonal_patterns: list[SeasonalPattern]
    patrol_recommendations: list[PatrolRecommendation]
    model_accuracy: float
    last_updated: str


class CrimeForecastEngine:
    """Generates crime forecasts and patrol recommendations."""
    
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Risk thresholds
    RISK_THRESHOLDS = {
        "critical": 10,
        "high": 6,
        "medium": 3,
        "low": 0,
    }
    
    def __init__(self):
        self.ingestor = get_crime_ingestor()
    
    def _calculate_hourly_averages(
        self,
        records: list[NormalizedCrimeRecord],
    ) -> dict[int, dict]:
        """Calculate average crime counts by hour."""
        hourly_data = defaultdict(lambda: {"counts": [], "violent": 0, "property": 0})
        
        # Group by date and hour
        date_hour_counts = defaultdict(lambda: defaultdict(int))
        for record in records:
            date_key = record.datetime_utc.strftime("%Y-%m-%d")
            hour = record.datetime_utc.hour
            date_hour_counts[date_key][hour] += 1
            
            if record.type == CrimeType.VIOLENT:
                hourly_data[hour]["violent"] += 1
            elif record.type == CrimeType.PROPERTY:
                hourly_data[hour]["property"] += 1
        
        # Calculate averages
        for date_key, hours in date_hour_counts.items():
            for hour, count in hours.items():
                hourly_data[hour]["counts"].append(count)
        
        result = {}
        for hour in range(24):
            counts = hourly_data[hour]["counts"]
            if counts:
                avg = sum(counts) / len(counts)
                std = math.sqrt(sum((c - avg) ** 2 for c in counts) / len(counts)) if len(counts) > 1 else avg * 0.3
            else:
                avg = 0
                std = 0
            
            result[hour] = {
                "average": avg,
                "std": std,
                "violent_total": hourly_data[hour]["violent"],
                "property_total": hourly_data[hour]["property"],
            }
        
        return result
    
    def _calculate_daily_averages(
        self,
        records: list[NormalizedCrimeRecord],
    ) -> dict[int, dict]:
        """Calculate average crime counts by day of week."""
        daily_data = defaultdict(lambda: {"counts": [], "violent": 0, "property": 0})
        
        # Group by week and day
        week_day_counts = defaultdict(lambda: defaultdict(int))
        for record in records:
            week_key = record.datetime_utc.strftime("%Y-W%W")
            day = record.datetime_utc.weekday()
            week_day_counts[week_key][day] += 1
            
            if record.type == CrimeType.VIOLENT:
                daily_data[day]["violent"] += 1
            elif record.type == CrimeType.PROPERTY:
                daily_data[day]["property"] += 1
        
        # Calculate averages
        for week_key, days in week_day_counts.items():
            for day, count in days.items():
                daily_data[day]["counts"].append(count)
        
        result = {}
        for day in range(7):
            counts = daily_data[day]["counts"]
            if counts:
                avg = sum(counts) / len(counts)
                std = math.sqrt(sum((c - avg) ** 2 for c in counts) / len(counts)) if len(counts) > 1 else avg * 0.3
            else:
                avg = 0
                std = 0
            
            num_weeks = len(week_day_counts)
            result[day] = {
                "average": avg,
                "std": std,
                "violent_avg": daily_data[day]["violent"] / max(num_weeks, 1),
                "property_avg": daily_data[day]["property"] / max(num_weeks, 1),
            }
        
        return result
    
    def _get_risk_level(self, predicted_count: float) -> str:
        """Determine risk level based on predicted count."""
        if predicted_count >= self.RISK_THRESHOLDS["critical"]:
            return "critical"
        elif predicted_count >= self.RISK_THRESHOLDS["high"]:
            return "high"
        elif predicted_count >= self.RISK_THRESHOLDS["medium"]:
            return "medium"
        return "low"
    
    def _generate_hourly_forecast(
        self,
        hourly_averages: dict[int, dict],
        hours_ahead: int = 24,
    ) -> list[HourlyForecast]:
        """Generate hourly forecast."""
        forecasts = []
        now = datetime.utcnow()
        
        for i in range(hours_ahead):
            forecast_time = now + timedelta(hours=i)
            hour = forecast_time.hour
            date_str = forecast_time.strftime("%Y-%m-%d")
            
            avg_data = hourly_averages.get(hour, {"average": 0, "std": 0})
            predicted = avg_data["average"]
            std = avg_data["std"]
            
            # Apply simple trend adjustment (slight increase for recent patterns)
            trend_factor = 1.0 + (0.01 * (i / 24))  # Slight increase over time
            predicted *= trend_factor
            
            forecasts.append(HourlyForecast(
                hour=hour,
                date=date_str,
                predicted_count=round(predicted, 2),
                confidence_low=round(max(0, predicted - 1.96 * std), 2),
                confidence_high=round(predicted + 1.96 * std, 2),
                risk_level=self._get_risk_level(predicted),
            ))
        
        return forecasts
    
    def _generate_daily_forecast(
        self,
        daily_averages: dict[int, dict],
        days_ahead: int = 7,
    ) -> list[DailyForecast]:
        """Generate daily forecast."""
        forecasts = []
        now = datetime.utcnow()
        
        for i in range(days_ahead):
            forecast_date = now + timedelta(days=i)
            day = forecast_date.weekday()
            date_str = forecast_date.strftime("%Y-%m-%d")
            
            avg_data = daily_averages.get(day, {"average": 0, "std": 0, "violent_avg": 0, "property_avg": 0})
            predicted = avg_data["average"]
            std = avg_data["std"]
            
            forecasts.append(DailyForecast(
                date=date_str,
                day_of_week=self.DAY_NAMES[day],
                predicted_count=round(predicted, 2),
                confidence_low=round(max(0, predicted - 1.96 * std), 2),
                confidence_high=round(predicted + 1.96 * std, 2),
                risk_level=self._get_risk_level(predicted),
                violent_predicted=round(avg_data["violent_avg"], 2),
                property_predicted=round(avg_data["property_avg"], 2),
            ))
        
        return forecasts
    
    def _identify_seasonal_patterns(
        self,
        records: list[NormalizedCrimeRecord],
        hourly_averages: dict[int, dict],
        daily_averages: dict[int, dict],
    ) -> list[SeasonalPattern]:
        """Identify seasonal patterns in crime data."""
        patterns = []
        
        # Hourly pattern
        hourly_counts = [(h, hourly_averages[h]["average"]) for h in range(24)]
        hourly_counts.sort(key=lambda x: x[1], reverse=True)
        
        peak_hours = [f"{h}:00" for h, _ in hourly_counts[:4]]
        low_hours = [f"{h}:00" for h, _ in hourly_counts[-4:]]
        
        if hourly_counts[0][1] > 0:
            hourly_strength = (hourly_counts[0][1] - hourly_counts[-1][1]) / hourly_counts[0][1]
        else:
            hourly_strength = 0
        
        patterns.append(SeasonalPattern(
            pattern_type="hourly",
            description="Crime peaks during late evening and early morning hours",
            peak_periods=peak_hours,
            low_periods=low_hours,
            strength=round(min(hourly_strength, 1.0), 2),
        ))
        
        # Daily pattern
        daily_counts = [(d, daily_averages[d]["average"]) for d in range(7)]
        daily_counts.sort(key=lambda x: x[1], reverse=True)
        
        peak_days = [self.DAY_NAMES[d] for d, _ in daily_counts[:2]]
        low_days = [self.DAY_NAMES[d] for d, _ in daily_counts[-2:]]
        
        if daily_counts[0][1] > 0:
            daily_strength = (daily_counts[0][1] - daily_counts[-1][1]) / daily_counts[0][1]
        else:
            daily_strength = 0
        
        patterns.append(SeasonalPattern(
            pattern_type="weekly",
            description="Crime activity varies by day of week",
            peak_periods=peak_days,
            low_periods=low_days,
            strength=round(min(daily_strength, 1.0), 2),
        ))
        
        return patterns
    
    def _generate_patrol_recommendations(
        self,
        records: list[NormalizedCrimeRecord],
        hourly_forecast: list[HourlyForecast],
    ) -> list[PatrolRecommendation]:
        """Generate proactive patrol shift recommendations."""
        recommendations = []
        
        # Get sector crime counts
        sector_counts = defaultdict(lambda: {"total": 0, "violent": 0})
        for record in records:
            sector_counts[record.sector]["total"] += 1
            if record.type == CrimeType.VIOLENT:
                sector_counts[record.sector]["violent"] += 1
        
        # Sort sectors by crime count
        sorted_sectors = sorted(
            sector_counts.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )[:5]  # Top 5 sectors
        
        # Find high-risk time windows
        high_risk_hours = [f for f in hourly_forecast if f.risk_level in ["high", "critical"]]
        
        for sector, counts in sorted_sectors:
            if counts["total"] < 3:
                continue
            
            # Determine priority
            if counts["violent"] > 5:
                priority = "critical"
                units = 3
            elif counts["violent"] > 2:
                priority = "high"
                units = 2
            elif counts["total"] > 10:
                priority = "medium"
                units = 2
            else:
                priority = "low"
                units = 1
            
            # Find best patrol window
            if high_risk_hours:
                start_hour = high_risk_hours[0].hour
                end_hour = (start_hour + 4) % 24
            else:
                start_hour = 20  # Default evening patrol
                end_hour = 0
            
            recommendations.append(PatrolRecommendation(
                sector=sector,
                start_time=f"{start_hour:02d}:00",
                end_time=f"{end_hour:02d}:00",
                priority=priority,
                reason=f"High crime activity: {counts['total']} incidents, {counts['violent']} violent",
                expected_incidents=round(counts["total"] / 7, 1),  # Weekly average
                recommended_units=units,
            ))
        
        return recommendations
    
    def forecast(
        self,
        hours_ahead: int = 24,
        days_ahead: int = 7,
        lookback_days: int = 30,
    ) -> ForecastResult:
        """Generate complete crime forecast."""
        # Get historical records
        all_records = self.ingestor.get_all_records()
        
        # Filter to lookback period
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        records = [r for r in all_records if r.datetime_utc >= cutoff]
        
        # Calculate averages
        hourly_averages = self._calculate_hourly_averages(records)
        daily_averages = self._calculate_daily_averages(records)
        
        # Generate forecasts
        hourly_forecast = self._generate_hourly_forecast(hourly_averages, hours_ahead)
        daily_forecast = self._generate_daily_forecast(daily_averages, days_ahead)
        
        # Identify patterns
        seasonal_patterns = self._identify_seasonal_patterns(records, hourly_averages, daily_averages)
        
        # Generate patrol recommendations
        patrol_recommendations = self._generate_patrol_recommendations(records, hourly_forecast)
        
        # Calculate model accuracy (simplified)
        model_accuracy = 0.75 if len(records) > 100 else 0.5 if len(records) > 20 else 0.3
        
        return ForecastResult(
            hourly_forecast=hourly_forecast,
            daily_forecast=daily_forecast,
            seasonal_patterns=seasonal_patterns,
            patrol_recommendations=patrol_recommendations,
            model_accuracy=model_accuracy,
            last_updated=datetime.utcnow().isoformat(),
        )


# Global engine instance
_engine: Optional[CrimeForecastEngine] = None


def get_forecast_engine() -> CrimeForecastEngine:
    """Get or create the global forecast engine."""
    global _engine
    if _engine is None:
        _engine = CrimeForecastEngine()
    return _engine

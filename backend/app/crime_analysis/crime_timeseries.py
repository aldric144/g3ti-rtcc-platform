"""
Crime Time Series Analysis Module.

Creates:
- Daily and hourly crime timelines
- Trend prediction using simple moving average and linear regression
- Jump alerts for anomaly detection
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


class TimeseriesPoint(BaseModel):
    """Single point in time series."""
    timestamp: str
    count: int
    violent_count: int = 0
    property_count: int = 0
    other_count: int = 0


class TrendInfo(BaseModel):
    """Trend analysis information."""
    direction: str  # "increasing", "decreasing", "stable"
    slope: float
    change_percent: float
    confidence: float


class AnomalyAlert(BaseModel):
    """Anomaly/jump alert."""
    timestamp: str
    expected_count: float
    actual_count: int
    deviation: float
    severity: str  # "low", "medium", "high", "critical"
    description: str


class TimeseriesResult(BaseModel):
    """Complete time series analysis result."""
    hourly_data: list[TimeseriesPoint]
    daily_data: list[TimeseriesPoint]
    trend: TrendInfo
    anomalies: list[AnomalyAlert]
    total_incidents: int
    average_daily: float
    peak_hour: int
    peak_day: str


class CrimeTimeseriesAnalyzer:
    """Analyzes crime time series data."""
    
    # Standard deviation multiplier for anomaly detection
    ANOMALY_THRESHOLD = 2.0
    
    # Minimum data points for trend analysis
    MIN_TREND_POINTS = 3
    
    def __init__(self):
        self.ingestor = get_crime_ingestor()
    
    def _aggregate_hourly(
        self,
        records: list[NormalizedCrimeRecord],
        start: datetime,
        end: datetime,
    ) -> list[TimeseriesPoint]:
        """Aggregate records by hour."""
        hourly_counts = defaultdict(lambda: {"total": 0, "violent": 0, "property": 0, "other": 0})
        
        for record in records:
            hour_key = record.datetime_utc.strftime("%Y-%m-%d %H:00")
            hourly_counts[hour_key]["total"] += 1
            
            if record.type == CrimeType.VIOLENT:
                hourly_counts[hour_key]["violent"] += 1
            elif record.type == CrimeType.PROPERTY:
                hourly_counts[hour_key]["property"] += 1
            else:
                hourly_counts[hour_key]["other"] += 1
        
        # Fill in missing hours
        result = []
        current = start.replace(minute=0, second=0, microsecond=0)
        while current <= end:
            hour_key = current.strftime("%Y-%m-%d %H:00")
            counts = hourly_counts.get(hour_key, {"total": 0, "violent": 0, "property": 0, "other": 0})
            result.append(TimeseriesPoint(
                timestamp=hour_key,
                count=counts["total"],
                violent_count=counts["violent"],
                property_count=counts["property"],
                other_count=counts["other"],
            ))
            current += timedelta(hours=1)
        
        return result
    
    def _aggregate_daily(
        self,
        records: list[NormalizedCrimeRecord],
        start: datetime,
        end: datetime,
    ) -> list[TimeseriesPoint]:
        """Aggregate records by day."""
        daily_counts = defaultdict(lambda: {"total": 0, "violent": 0, "property": 0, "other": 0})
        
        for record in records:
            day_key = record.datetime_utc.strftime("%Y-%m-%d")
            daily_counts[day_key]["total"] += 1
            
            if record.type == CrimeType.VIOLENT:
                daily_counts[day_key]["violent"] += 1
            elif record.type == CrimeType.PROPERTY:
                daily_counts[day_key]["property"] += 1
            else:
                daily_counts[day_key]["other"] += 1
        
        # Fill in missing days
        result = []
        current = start.replace(hour=0, minute=0, second=0, microsecond=0)
        while current <= end:
            day_key = current.strftime("%Y-%m-%d")
            counts = daily_counts.get(day_key, {"total": 0, "violent": 0, "property": 0, "other": 0})
            result.append(TimeseriesPoint(
                timestamp=day_key,
                count=counts["total"],
                violent_count=counts["violent"],
                property_count=counts["property"],
                other_count=counts["other"],
            ))
            current += timedelta(days=1)
        
        return result
    
    def _calculate_trend(self, data: list[TimeseriesPoint]) -> TrendInfo:
        """Calculate trend using linear regression."""
        if len(data) < self.MIN_TREND_POINTS:
            return TrendInfo(
                direction="stable",
                slope=0.0,
                change_percent=0.0,
                confidence=0.0,
            )
        
        # Simple linear regression
        n = len(data)
        x_values = list(range(n))
        y_values = [p.count for p in data]
        
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        # Calculate slope
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator
        
        # Calculate R-squared for confidence
        y_pred = [y_mean + slope * (x - x_mean) for x in x_values]
        ss_res = sum((y - yp) ** 2 for y, yp in zip(y_values, y_pred))
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)
        
        if ss_tot == 0:
            r_squared = 0.0
        else:
            r_squared = 1 - (ss_res / ss_tot)
        
        # Determine direction
        if abs(slope) < 0.1:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        # Calculate percent change
        if y_values[0] > 0:
            change_percent = ((y_values[-1] - y_values[0]) / y_values[0]) * 100
        else:
            change_percent = 0.0
        
        return TrendInfo(
            direction=direction,
            slope=round(slope, 4),
            change_percent=round(change_percent, 2),
            confidence=round(max(0, r_squared), 2),
        )
    
    def _detect_anomalies(self, data: list[TimeseriesPoint]) -> list[AnomalyAlert]:
        """Detect anomalies using statistical methods."""
        if len(data) < 5:
            return []
        
        counts = [p.count for p in data]
        
        # Calculate mean and standard deviation
        mean = sum(counts) / len(counts)
        variance = sum((c - mean) ** 2 for c in counts) / len(counts)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0
        
        anomalies = []
        for point in data:
            if std_dev > 0:
                z_score = (point.count - mean) / std_dev
            else:
                z_score = 0
            
            if abs(z_score) > self.ANOMALY_THRESHOLD:
                # Determine severity
                if abs(z_score) > 4:
                    severity = "critical"
                elif abs(z_score) > 3:
                    severity = "high"
                elif abs(z_score) > 2.5:
                    severity = "medium"
                else:
                    severity = "low"
                
                direction = "spike" if z_score > 0 else "drop"
                
                anomalies.append(AnomalyAlert(
                    timestamp=point.timestamp,
                    expected_count=round(mean, 1),
                    actual_count=point.count,
                    deviation=round(z_score, 2),
                    severity=severity,
                    description=f"Crime {direction} detected: {point.count} incidents vs expected {round(mean, 1)}",
                ))
        
        return anomalies
    
    def _find_peak_hour(self, records: list[NormalizedCrimeRecord]) -> int:
        """Find the hour with most incidents."""
        hour_counts = defaultdict(int)
        for record in records:
            hour_counts[record.datetime_utc.hour] += 1
        
        if not hour_counts:
            return 0
        
        return max(hour_counts.keys(), key=lambda h: hour_counts[h])
    
    def _find_peak_day(self, records: list[NormalizedCrimeRecord]) -> str:
        """Find the day of week with most incidents."""
        day_counts = defaultdict(int)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for record in records:
            day_counts[record.datetime_utc.weekday()] += 1
        
        if not day_counts:
            return "Unknown"
        
        peak_day_idx = max(day_counts.keys(), key=lambda d: day_counts[d])
        return day_names[peak_day_idx]
    
    def analyze(
        self,
        days: int = 30,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> TimeseriesResult:
        """Perform complete time series analysis."""
        # Get all records
        all_records = self.ingestor.get_all_records()
        
        # Determine date range
        end = end_date or datetime.utcnow()
        start = start_date or (end - timedelta(days=days))
        
        # Filter records
        filtered_records = [
            r for r in all_records
            if start <= r.datetime_utc <= end
        ]
        
        # Generate aggregations
        hourly_data = self._aggregate_hourly(filtered_records, start, end)
        daily_data = self._aggregate_daily(filtered_records, start, end)
        
        # Calculate trend
        trend = self._calculate_trend(daily_data)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(daily_data)
        
        # Calculate statistics
        total_incidents = len(filtered_records)
        num_days = max((end - start).days, 1)
        average_daily = total_incidents / num_days
        
        peak_hour = self._find_peak_hour(filtered_records)
        peak_day = self._find_peak_day(filtered_records)
        
        return TimeseriesResult(
            hourly_data=hourly_data,
            daily_data=daily_data,
            trend=trend,
            anomalies=anomalies,
            total_incidents=total_incidents,
            average_daily=round(average_daily, 2),
            peak_hour=peak_hour,
            peak_day=peak_day,
        )


# Global analyzer instance
_analyzer: Optional[CrimeTimeseriesAnalyzer] = None


def get_timeseries_analyzer() -> CrimeTimeseriesAnalyzer:
    """Get or create the global time series analyzer."""
    global _analyzer
    if _analyzer is None:
        _analyzer = CrimeTimeseriesAnalyzer()
    return _analyzer

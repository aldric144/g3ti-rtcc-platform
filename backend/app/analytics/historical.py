"""
Historical Analytics Engine for G3TI RTCC-UIP.

This module provides historical trend analysis capabilities including:
- Time-series analysis
- Year-over-year comparisons
- Seasonal pattern detection
- Statistical trend analysis
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..db.elasticsearch import ElasticsearchManager
from ..db.neo4j import Neo4jManager
from ..db.redis import RedisManager

logger = logging.getLogger(__name__)


class TrendAnalysis(BaseModel):
    """Trend analysis result."""

    model_config = ConfigDict(from_attributes=True)

    period_type: str = Field(description="Analysis period type")
    start_date: datetime = Field(description="Analysis start date")
    end_date: datetime = Field(description="Analysis end date")

    # Trend metrics
    trend_direction: str = Field(description="Trend: increasing, decreasing, stable")
    trend_strength: float = Field(ge=0, le=1, description="Trend strength (0-1)")
    percent_change: float = Field(description="Overall percent change")
    slope: float = Field(description="Trend line slope")

    # Statistical metrics
    mean: float = Field(description="Mean value")
    median: float = Field(description="Median value")
    std_dev: float = Field(description="Standard deviation")
    min_value: float = Field(description="Minimum value")
    max_value: float = Field(description="Maximum value")

    # Time series data
    periods: list[str] = Field(description="Period labels")
    values: list[float] = Field(description="Values per period")

    # Seasonality
    has_seasonality: bool = Field(default=False, description="Whether seasonality detected")
    seasonal_pattern: dict[str, float] | None = Field(
        default=None, description="Seasonal pattern if detected"
    )

    # Confidence
    confidence: float = Field(ge=0, le=1, description="Analysis confidence")
    data_points: int = Field(description="Number of data points")


class ComparisonResult(BaseModel):
    """Year-over-year or period comparison result."""

    model_config = ConfigDict(from_attributes=True)

    comparison_type: str = Field(description="Comparison type")
    base_period: str = Field(description="Base period label")
    comparison_period: str = Field(description="Comparison period label")

    # Metrics
    base_total: int = Field(description="Base period total")
    comparison_total: int = Field(description="Comparison period total")
    absolute_change: int = Field(description="Absolute change")
    percent_change: float = Field(description="Percent change")

    # Breakdown
    category_changes: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Changes by category"
    )
    beat_changes: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Changes by beat"
    )

    # Significance
    is_significant: bool = Field(description="Whether change is statistically significant")
    significance_level: float = Field(description="Statistical significance level")


class HistoricalAnalyticsEngine:
    """
    Engine for historical crime analytics.

    Provides comprehensive historical analysis including:
    - Trend analysis over time
    - Year-over-year comparisons
    - Seasonal pattern detection
    - Statistical analysis
    """

    # Cache settings
    CACHE_PREFIX = "analytics:historical:"
    CACHE_TTL = 3600  # 1 hour

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
    ):
        """
        Initialize the Historical Analytics Engine.

        Args:
            neo4j: Neo4j database manager
            es: Elasticsearch manager
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        logger.info("HistoricalAnalyticsEngine initialized")

    async def analyze_trend(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "monthly",
        crime_category: str | None = None,
        beat: str | None = None,
    ) -> TrendAnalysis:
        """
        Analyze crime trends over a time period.

        Args:
            jurisdiction: Jurisdiction code
            start_date: Analysis start date
            end_date: Analysis end date
            granularity: Time granularity (daily, weekly, monthly, yearly)
            crime_category: Optional crime category filter
            beat: Optional beat filter

        Returns:
            Trend analysis result
        """
        # Check cache
        cache_key = self._build_cache_key(
            "trend", jurisdiction, start_date, end_date, granularity, crime_category, beat
        )
        cached = await self._get_cached(cache_key)
        if cached:
            return TrendAnalysis(**cached)

        # Fetch aggregated data
        time_series = await self._fetch_time_series(
            jurisdiction, start_date, end_date, granularity, crime_category, beat
        )

        if not time_series:
            return self._empty_trend_analysis(start_date, end_date, granularity)

        # Extract values
        periods = [ts["period"] for ts in time_series]
        values = [float(ts["count"]) for ts in time_series]

        # Calculate statistics
        mean = sum(values) / len(values)
        sorted_values = sorted(values)
        median = sorted_values[len(sorted_values) // 2]
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance)
        min_value = min(values)
        max_value = max(values)

        # Calculate trend
        slope, trend_direction, trend_strength = self._calculate_trend(values)

        # Calculate percent change
        if values[0] > 0:
            percent_change = ((values[-1] - values[0]) / values[0]) * 100
        else:
            percent_change = 0.0

        # Detect seasonality
        has_seasonality, seasonal_pattern = self._detect_seasonality(values, granularity)

        # Calculate confidence based on data points
        confidence = min(1.0, len(values) / 12)  # Full confidence at 12+ data points

        result = TrendAnalysis(
            period_type=granularity,
            start_date=start_date,
            end_date=end_date,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            percent_change=round(percent_change, 2),
            slope=round(slope, 4),
            mean=round(mean, 2),
            median=round(median, 2),
            std_dev=round(std_dev, 2),
            min_value=min_value,
            max_value=max_value,
            periods=periods,
            values=values,
            has_seasonality=has_seasonality,
            seasonal_pattern=seasonal_pattern,
            confidence=confidence,
            data_points=len(values),
        )

        # Cache result
        await self._set_cached(cache_key, result.model_dump())

        return result

    async def compare_periods(
        self,
        jurisdiction: str,
        base_start: datetime,
        base_end: datetime,
        comparison_start: datetime,
        comparison_end: datetime,
        crime_category: str | None = None,
    ) -> ComparisonResult:
        """
        Compare two time periods.

        Args:
            jurisdiction: Jurisdiction code
            base_start: Base period start
            base_end: Base period end
            comparison_start: Comparison period start
            comparison_end: Comparison period end
            crime_category: Optional crime category filter

        Returns:
            Comparison result
        """
        # Fetch data for both periods
        base_data = await self._fetch_period_data(
            jurisdiction, base_start, base_end, crime_category
        )
        comparison_data = await self._fetch_period_data(
            jurisdiction, comparison_start, comparison_end, crime_category
        )

        base_total = base_data.get("total", 0)
        comparison_total = comparison_data.get("total", 0)

        absolute_change = comparison_total - base_total
        if base_total > 0:
            percent_change = (absolute_change / base_total) * 100
        else:
            percent_change = 0.0

        # Calculate category changes
        category_changes = self._calculate_category_changes(
            base_data.get("by_category", {}),
            comparison_data.get("by_category", {}),
        )

        # Calculate beat changes
        beat_changes = self._calculate_beat_changes(
            base_data.get("by_beat", {}),
            comparison_data.get("by_beat", {}),
        )

        # Determine statistical significance
        is_significant, significance_level = self._calculate_significance(
            base_total, comparison_total, base_data.get("std_dev", 0)
        )

        return ComparisonResult(
            comparison_type="period",
            base_period=f"{base_start.strftime('%Y-%m-%d')} to {base_end.strftime('%Y-%m-%d')}",
            comparison_period=(
                f"{comparison_start.strftime('%Y-%m-%d')} to "
                f"{comparison_end.strftime('%Y-%m-%d')}"
            ),
            base_total=base_total,
            comparison_total=comparison_total,
            absolute_change=absolute_change,
            percent_change=round(percent_change, 2),
            category_changes=category_changes,
            beat_changes=beat_changes,
            is_significant=is_significant,
            significance_level=significance_level,
        )

    async def year_over_year_analysis(
        self,
        jurisdiction: str,
        years: list[int],
        crime_category: str | None = None,
    ) -> dict[str, Any]:
        """
        Perform year-over-year analysis.

        Args:
            jurisdiction: Jurisdiction code
            years: List of years to analyze
            crime_category: Optional crime category filter

        Returns:
            Year-over-year analysis data
        """
        yearly_data: dict[int, dict[str, Any]] = {}
        comparisons: list[ComparisonResult] = []

        # Fetch data for each year
        for year in sorted(years):
            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31, 23, 59, 59)

            data = await self._fetch_period_data(
                jurisdiction, start, end, crime_category
            )
            yearly_data[year] = data

        # Compare consecutive years
        sorted_years = sorted(years)
        for i in range(1, len(sorted_years)):
            base_year = sorted_years[i - 1]
            comp_year = sorted_years[i]

            comparison = await self.compare_periods(
                jurisdiction,
                datetime(base_year, 1, 1),
                datetime(base_year, 12, 31, 23, 59, 59),
                datetime(comp_year, 1, 1),
                datetime(comp_year, 12, 31, 23, 59, 59),
                crime_category,
            )
            comparisons.append(comparison)

        # Calculate overall trend
        totals = [yearly_data[y].get("total", 0) for y in sorted_years]
        if len(totals) >= 2 and totals[0] > 0:
            overall_change = ((totals[-1] - totals[0]) / totals[0]) * 100
        else:
            overall_change = 0.0

        return {
            "years": sorted_years,
            "yearly_totals": {y: yearly_data[y].get("total", 0) for y in sorted_years},
            "yearly_data": yearly_data,
            "comparisons": [c.model_dump() for c in comparisons],
            "overall_percent_change": round(overall_change, 2),
            "trend": "increasing" if overall_change > 5 else (
                "decreasing" if overall_change < -5 else "stable"
            ),
        }

    async def get_seasonal_patterns(
        self,
        jurisdiction: str,
        years: list[int],
        crime_category: str | None = None,
    ) -> dict[str, Any]:
        """
        Analyze seasonal patterns across multiple years.

        Args:
            jurisdiction: Jurisdiction code
            years: Years to analyze
            crime_category: Optional crime category filter

        Returns:
            Seasonal pattern analysis
        """
        # Aggregate monthly data across years
        monthly_totals: dict[int, list[int]] = {m: [] for m in range(1, 13)}
        hourly_totals: dict[int, list[int]] = {h: [] for h in range(24)}
        dow_totals: dict[int, list[int]] = {d: [] for d in range(7)}

        for year in years:
            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31, 23, 59, 59)

            # Fetch monthly breakdown
            monthly_data = await self._fetch_time_series(
                jurisdiction, start, end, "monthly", crime_category
            )

            for item in monthly_data:
                month = int(item["period"].split("-")[1])
                monthly_totals[month].append(item["count"])

        # Calculate averages
        monthly_averages = {
            m: sum(vals) / len(vals) if vals else 0
            for m, vals in monthly_totals.items()
        }

        # Identify peak and low months
        sorted_months = sorted(monthly_averages.items(), key=lambda x: x[1], reverse=True)
        peak_months = [m for m, _ in sorted_months[:3]]
        low_months = [m for m, _ in sorted_months[-3:]]

        # Calculate seasonality index
        overall_avg = sum(monthly_averages.values()) / 12 if monthly_averages else 1
        seasonality_index = {
            m: round(avg / overall_avg, 2) if overall_avg > 0 else 1.0
            for m, avg in monthly_averages.items()
        }

        return {
            "monthly_averages": monthly_averages,
            "seasonality_index": seasonality_index,
            "peak_months": peak_months,
            "low_months": low_months,
            "has_strong_seasonality": max(seasonality_index.values()) > 1.3,
            "years_analyzed": years,
        }

    async def _fetch_time_series(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str,
        crime_category: str | None = None,
        beat: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch time series data from Elasticsearch."""
        try:
            # Determine date histogram interval
            interval_map = {
                "daily": "day",
                "weekly": "week",
                "monthly": "month",
                "yearly": "year",
            }
            interval = interval_map.get(granularity, "month")

            # Build query
            must_clauses = [
                {"term": {"jurisdiction": jurisdiction}},
                {"range": {"timestamp": {
                    "gte": start_date.isoformat(),
                    "lte": end_date.isoformat(),
                }}},
            ]

            if crime_category:
                must_clauses.append({"term": {"crime_category": crime_category}})
            if beat:
                must_clauses.append({"term": {"beat": beat}})

            query = {
                "bool": {"must": must_clauses}
            }

            aggs = {
                "time_series": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": interval,
                        "format": "yyyy-MM-dd",
                    }
                }
            }

            result = await self.es.search(
                index="datalake_incidents",
                query=query,
                aggs=aggs,
                size=0,
            )

            buckets = result.get("aggregations", {}).get("time_series", {}).get("buckets", [])

            return [
                {"period": b["key_as_string"], "count": b["doc_count"]}
                for b in buckets
            ]

        except Exception as e:
            logger.error(f"Failed to fetch time series: {e}")
            # Return mock data for development
            return self._generate_mock_time_series(start_date, end_date, granularity)

    def _generate_mock_time_series(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str,
    ) -> list[dict[str, Any]]:
        """Generate mock time series data for development."""
        import random

        result = []
        current = start_date

        while current <= end_date:
            # Add some seasonality
            month_factor = 1.0 + 0.3 * math.sin(current.month * math.pi / 6)
            base_count = int(100 * month_factor + random.randint(-20, 20))

            result.append({
                "period": current.strftime("%Y-%m-%d"),
                "count": max(0, base_count),
            })

            if granularity == "daily":
                current += timedelta(days=1)
            elif granularity == "weekly":
                current += timedelta(weeks=1)
            elif granularity == "monthly":
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            else:  # yearly
                current = current.replace(year=current.year + 1)

        return result

    async def _fetch_period_data(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        crime_category: str | None = None,
    ) -> dict[str, Any]:
        """Fetch aggregated data for a period."""
        try:
            must_clauses = [
                {"term": {"jurisdiction": jurisdiction}},
                {"range": {"timestamp": {
                    "gte": start_date.isoformat(),
                    "lte": end_date.isoformat(),
                }}},
            ]

            if crime_category:
                must_clauses.append({"term": {"crime_category": crime_category}})

            query = {"bool": {"must": must_clauses}}

            aggs = {
                "by_category": {
                    "terms": {"field": "crime_category", "size": 20}
                },
                "by_beat": {
                    "terms": {"field": "beat", "size": 50}
                },
            }

            result = await self.es.search(
                index="datalake_incidents",
                query=query,
                aggs=aggs,
                size=0,
            )

            total = result.get("hits", {}).get("total", {}).get("value", 0)

            by_category = {
                b["key"]: b["doc_count"]
                for b in result.get("aggregations", {}).get("by_category", {}).get("buckets", [])
            }

            by_beat = {
                b["key"]: b["doc_count"]
                for b in result.get("aggregations", {}).get("by_beat", {}).get("buckets", [])
            }

            return {
                "total": total,
                "by_category": by_category,
                "by_beat": by_beat,
            }

        except Exception as e:
            logger.error(f"Failed to fetch period data: {e}")
            # Return mock data
            import random
            return {
                "total": random.randint(500, 2000),
                "by_category": {
                    "violent": random.randint(50, 200),
                    "property": random.randint(200, 500),
                    "drug": random.randint(50, 150),
                    "other": random.randint(100, 300),
                },
                "by_beat": {},
            }

    def _calculate_trend(self, values: list[float]) -> tuple[float, str, float]:
        """Calculate trend from time series values."""
        if len(values) < 2:
            return 0.0, "stable", 0.0

        n = len(values)
        x = list(range(n))

        # Calculate linear regression slope
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # Determine trend direction
        if slope > 0.5:
            direction = "increasing"
        elif slope < -0.5:
            direction = "decreasing"
        else:
            direction = "stable"

        # Calculate trend strength (R-squared)
        if denominator > 0:
            ss_res = sum((values[i] - (y_mean + slope * (x[i] - x_mean))) ** 2 for i in range(n))
            ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
            strength = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        else:
            strength = 0.0

        return slope, direction, max(0, min(1, strength))

    def _detect_seasonality(
        self,
        values: list[float],
        granularity: str,
    ) -> tuple[bool, dict[str, float] | None]:
        """Detect seasonal patterns in time series."""
        if granularity != "monthly" or len(values) < 12:
            return False, None

        # Calculate monthly averages if we have multiple years
        if len(values) >= 24:
            monthly_avgs: dict[int, list[float]] = {m: [] for m in range(12)}
            for i, v in enumerate(values):
                monthly_avgs[i % 12].append(v)

            pattern = {
                str(m + 1): sum(vals) / len(vals) if vals else 0
                for m, vals in monthly_avgs.items()
            }

            # Check for seasonality (variance in monthly averages)
            avg_values = list(pattern.values())
            mean = sum(avg_values) / len(avg_values)
            variance = sum((v - mean) ** 2 for v in avg_values) / len(avg_values)
            cv = math.sqrt(variance) / mean if mean > 0 else 0

            has_seasonality = cv > 0.15  # Coefficient of variation > 15%

            return has_seasonality, pattern if has_seasonality else None

        return False, None

    def _calculate_category_changes(
        self,
        base: dict[str, int],
        comparison: dict[str, int],
    ) -> dict[str, dict[str, Any]]:
        """Calculate changes by category."""
        all_categories = set(base.keys()) | set(comparison.keys())
        changes = {}

        for cat in all_categories:
            base_val = base.get(cat, 0)
            comp_val = comparison.get(cat, 0)
            absolute = comp_val - base_val
            percent = ((absolute / base_val) * 100) if base_val > 0 else 0

            changes[cat] = {
                "base": base_val,
                "comparison": comp_val,
                "absolute_change": absolute,
                "percent_change": round(percent, 2),
            }

        return changes

    def _calculate_beat_changes(
        self,
        base: dict[str, int],
        comparison: dict[str, int],
    ) -> dict[str, dict[str, Any]]:
        """Calculate changes by beat."""
        # Same logic as category changes
        return self._calculate_category_changes(base, comparison)

    def _calculate_significance(
        self,
        base_total: int,
        comparison_total: int,
        std_dev: float,
    ) -> tuple[bool, float]:
        """Calculate statistical significance of change."""
        if std_dev == 0 or base_total == 0:
            return False, 0.0

        # Simple z-score based significance
        z_score = abs(comparison_total - base_total) / std_dev

        # Approximate p-value
        if z_score >= 2.576:
            return True, 0.01
        elif z_score >= 1.96:
            return True, 0.05
        elif z_score >= 1.645:
            return True, 0.10
        else:
            return False, 1.0

    def _empty_trend_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str,
    ) -> TrendAnalysis:
        """Return empty trend analysis."""
        return TrendAnalysis(
            period_type=granularity,
            start_date=start_date,
            end_date=end_date,
            trend_direction="stable",
            trend_strength=0.0,
            percent_change=0.0,
            slope=0.0,
            mean=0.0,
            median=0.0,
            std_dev=0.0,
            min_value=0.0,
            max_value=0.0,
            periods=[],
            values=[],
            confidence=0.0,
            data_points=0,
        )

    def _build_cache_key(self, *args: Any) -> str:
        """Build cache key from arguments."""
        parts = [str(a) for a in args if a is not None]
        return f"{self.CACHE_PREFIX}{':'.join(parts)}"

    async def _get_cached(self, key: str) -> dict[str, Any] | None:
        """Get cached value."""
        try:
            return await self.redis.get(key)
        except Exception:
            return None

    async def _set_cached(self, key: str, value: dict[str, Any]) -> None:
        """Set cached value."""
        try:
            await self.redis.set(key, value, ex=self.CACHE_TTL)
        except Exception as e:
            logger.warning(f"Failed to cache value: {e}")

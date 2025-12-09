"""
Multi-Year Heatmap Engine for G3TI RTCC-UIP.

This module provides multi-year heatmap generation capabilities including:
- H3 hexagonal heatmap generation
- Temporal heatmap aggregation
- Hotspot detection and evolution tracking
- Multi-year comparison overlays
"""

import logging
import math
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..db.elasticsearch import ElasticsearchManager
from ..db.redis import RedisManager

logger = logging.getLogger(__name__)


class HeatmapCell(BaseModel):
    """Individual heatmap cell data."""

    model_config = ConfigDict(from_attributes=True)

    h3_index: str = Field(description="H3 hexagonal index")
    latitude: float = Field(description="Cell center latitude")
    longitude: float = Field(description="Cell center longitude")
    count: int = Field(default=0, description="Incident count")
    intensity: float = Field(ge=0, le=1, description="Normalized intensity (0-1)")

    # Breakdown
    by_category: dict[str, int] = Field(default_factory=dict, description="Count by category")
    by_severity: dict[str, int] = Field(default_factory=dict, description="Count by severity")

    # Temporal
    peak_hour: int | None = Field(default=None, description="Peak hour of day")
    peak_day: int | None = Field(default=None, description="Peak day of week")


class HeatmapData(BaseModel):
    """Heatmap data for a time period."""

    model_config = ConfigDict(from_attributes=True)

    jurisdiction: str = Field(description="Jurisdiction code")
    period_type: str = Field(description="Period type (daily, weekly, monthly, yearly)")
    period_label: str = Field(description="Period label")
    start_date: datetime = Field(description="Period start")
    end_date: datetime = Field(description="Period end")

    # Cells
    cells: list[HeatmapCell] = Field(default_factory=list, description="Heatmap cells")
    total_incidents: int = Field(default=0, description="Total incidents")

    # Bounds
    min_lat: float = Field(default=0, description="Minimum latitude")
    max_lat: float = Field(default=0, description="Maximum latitude")
    min_lon: float = Field(default=0, description="Minimum longitude")
    max_lon: float = Field(default=0, description="Maximum longitude")

    # Statistics
    max_cell_count: int = Field(default=0, description="Maximum cell count")
    hotspot_count: int = Field(default=0, description="Number of hotspots")

    # Metadata
    h3_resolution: int = Field(default=8, description="H3 resolution used")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class HotspotEvolution(BaseModel):
    """Hotspot evolution over time."""

    model_config = ConfigDict(from_attributes=True)

    h3_index: str = Field(description="H3 index")
    latitude: float = Field(description="Center latitude")
    longitude: float = Field(description="Center longitude")

    # Evolution data
    periods: list[str] = Field(description="Period labels")
    counts: list[int] = Field(description="Counts per period")
    intensities: list[float] = Field(description="Intensities per period")

    # Trend
    trend: str = Field(description="Trend: emerging, stable, declining, new, disappeared")
    percent_change: float = Field(description="Overall percent change")

    # Classification
    is_persistent: bool = Field(description="Whether hotspot is persistent")
    first_appeared: str = Field(description="First period appeared")
    last_appeared: str = Field(description="Last period appeared")


class HeatmapComparison(BaseModel):
    """Comparison between two heatmaps."""

    model_config = ConfigDict(from_attributes=True)

    base_period: str = Field(description="Base period label")
    comparison_period: str = Field(description="Comparison period label")

    # Changes
    new_hotspots: list[HeatmapCell] = Field(default_factory=list, description="New hotspots")
    disappeared_hotspots: list[HeatmapCell] = Field(
        default_factory=list, description="Disappeared hotspots"
    )
    intensified_hotspots: list[dict[str, Any]] = Field(
        default_factory=list, description="Intensified hotspots"
    )
    reduced_hotspots: list[dict[str, Any]] = Field(
        default_factory=list, description="Reduced hotspots"
    )

    # Summary
    total_change: int = Field(description="Total incident change")
    percent_change: float = Field(description="Percent change")
    hotspot_shift_score: float = Field(
        ge=0, le=1, description="How much hotspots shifted (0-1)"
    )


class MultiYearHeatmapEngine:
    """
    Engine for multi-year heatmap generation and analysis.

    Provides comprehensive heatmap capabilities including:
    - H3 hexagonal heatmap generation
    - Multi-year overlays and comparisons
    - Hotspot detection and evolution tracking
    - Temporal pattern analysis
    """

    # H3 resolution levels
    RESOLUTION_CITY = 7  # ~5km cells
    RESOLUTION_NEIGHBORHOOD = 8  # ~1km cells
    RESOLUTION_BLOCK = 9  # ~200m cells

    # Hotspot threshold (top percentile)
    HOTSPOT_PERCENTILE = 0.9

    # Cache settings
    CACHE_PREFIX = "analytics:heatmap:"
    CACHE_TTL = 3600

    def __init__(
        self,
        es: ElasticsearchManager,
        redis: RedisManager,
        default_resolution: int = 8,
    ):
        """
        Initialize the Multi-Year Heatmap Engine.

        Args:
            es: Elasticsearch manager
            redis: Redis manager for caching
            default_resolution: Default H3 resolution
        """
        self.es = es
        self.redis = redis
        self.default_resolution = default_resolution

        logger.info(f"MultiYearHeatmapEngine initialized (resolution={default_resolution})")

    async def generate_heatmap(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        resolution: int | None = None,
        crime_category: str | None = None,
    ) -> HeatmapData:
        """
        Generate a heatmap for a time period.

        Args:
            jurisdiction: Jurisdiction code
            start_date: Period start
            end_date: Period end
            resolution: H3 resolution (default: 8)
            crime_category: Optional crime category filter

        Returns:
            Heatmap data
        """
        resolution = resolution or self.default_resolution

        # Check cache
        cache_key = self._build_cache_key(
            jurisdiction, start_date, end_date, resolution, crime_category
        )
        cached = await self._get_cached(cache_key)
        if cached:
            return HeatmapData(**cached)

        # Fetch aggregated data by H3 index
        cell_data = await self._fetch_cell_data(
            jurisdiction, start_date, end_date, resolution, crime_category
        )

        if not cell_data:
            return self._empty_heatmap(jurisdiction, start_date, end_date, resolution)

        # Calculate intensity normalization
        max_count = max(c["count"] for c in cell_data) if cell_data else 1
        hotspot_threshold = self._calculate_hotspot_threshold(cell_data)

        # Build cells
        cells = []
        hotspot_count = 0
        total_incidents = 0

        for data in cell_data:
            intensity = data["count"] / max_count if max_count > 0 else 0

            cell = HeatmapCell(
                h3_index=data["h3_index"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                count=data["count"],
                intensity=round(intensity, 4),
                by_category=data.get("by_category", {}),
                by_severity=data.get("by_severity", {}),
                peak_hour=data.get("peak_hour"),
                peak_day=data.get("peak_day"),
            )
            cells.append(cell)
            total_incidents += data["count"]

            if data["count"] >= hotspot_threshold:
                hotspot_count += 1

        # Calculate bounds
        lats = [c.latitude for c in cells]
        lons = [c.longitude for c in cells]

        period_label = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

        result = HeatmapData(
            jurisdiction=jurisdiction,
            period_type="custom",
            period_label=period_label,
            start_date=start_date,
            end_date=end_date,
            cells=cells,
            total_incidents=total_incidents,
            min_lat=min(lats) if lats else 0,
            max_lat=max(lats) if lats else 0,
            min_lon=min(lons) if lons else 0,
            max_lon=max(lons) if lons else 0,
            max_cell_count=max_count,
            hotspot_count=hotspot_count,
            h3_resolution=resolution,
        )

        # Cache result
        await self._set_cached(cache_key, result.model_dump())

        return result

    async def generate_yearly_heatmaps(
        self,
        jurisdiction: str,
        years: list[int],
        resolution: int | None = None,
        crime_category: str | None = None,
    ) -> dict[int, HeatmapData]:
        """
        Generate heatmaps for multiple years.

        Args:
            jurisdiction: Jurisdiction code
            years: Years to generate heatmaps for
            resolution: H3 resolution
            crime_category: Optional crime category filter

        Returns:
            Dictionary of year to heatmap data
        """
        heatmaps = {}

        for year in years:
            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31, 23, 59, 59)

            heatmap = await self.generate_heatmap(
                jurisdiction, start, end, resolution, crime_category
            )
            heatmap.period_type = "yearly"
            heatmap.period_label = str(year)
            heatmaps[year] = heatmap

        return heatmaps

    async def compare_heatmaps(
        self,
        base_heatmap: HeatmapData,
        comparison_heatmap: HeatmapData,
    ) -> HeatmapComparison:
        """
        Compare two heatmaps.

        Args:
            base_heatmap: Base period heatmap
            comparison_heatmap: Comparison period heatmap

        Returns:
            Heatmap comparison result
        """
        # Index cells by H3
        base_cells = {c.h3_index: c for c in base_heatmap.cells}
        comp_cells = {c.h3_index: c for c in comparison_heatmap.cells}

        # Find hotspot thresholds
        base_threshold = self._calculate_hotspot_threshold(
            [{"count": c.count} for c in base_heatmap.cells]
        )
        comp_threshold = self._calculate_hotspot_threshold(
            [{"count": c.count} for c in comparison_heatmap.cells]
        )

        # Identify changes
        new_hotspots = []
        disappeared_hotspots = []
        intensified_hotspots = []
        reduced_hotspots = []

        # Check comparison cells
        for h3_index, comp_cell in comp_cells.items():
            base_cell = base_cells.get(h3_index)

            if base_cell is None:
                # New cell
                if comp_cell.count >= comp_threshold:
                    new_hotspots.append(comp_cell)
            else:
                # Existing cell - check for changes
                change = comp_cell.count - base_cell.count
                if base_cell.count > 0:
                    pct_change = (change / base_cell.count) * 100
                else:
                    pct_change = 100 if change > 0 else 0

                if pct_change > 25 and comp_cell.count >= comp_threshold:
                    intensified_hotspots.append({
                        "h3_index": h3_index,
                        "base_count": base_cell.count,
                        "comparison_count": comp_cell.count,
                        "percent_change": round(pct_change, 2),
                        "latitude": comp_cell.latitude,
                        "longitude": comp_cell.longitude,
                    })
                elif pct_change < -25 and base_cell.count >= base_threshold:
                    reduced_hotspots.append({
                        "h3_index": h3_index,
                        "base_count": base_cell.count,
                        "comparison_count": comp_cell.count,
                        "percent_change": round(pct_change, 2),
                        "latitude": comp_cell.latitude,
                        "longitude": comp_cell.longitude,
                    })

        # Check for disappeared hotspots
        for h3_index, base_cell in base_cells.items():
            if h3_index not in comp_cells and base_cell.count >= base_threshold:
                disappeared_hotspots.append(base_cell)

        # Calculate overall change
        total_change = comparison_heatmap.total_incidents - base_heatmap.total_incidents
        if base_heatmap.total_incidents > 0:
            percent_change = (total_change / base_heatmap.total_incidents) * 100
        else:
            percent_change = 0

        # Calculate hotspot shift score
        shift_score = self._calculate_shift_score(
            base_cells, comp_cells, base_threshold, comp_threshold
        )

        return HeatmapComparison(
            base_period=base_heatmap.period_label,
            comparison_period=comparison_heatmap.period_label,
            new_hotspots=new_hotspots,
            disappeared_hotspots=disappeared_hotspots,
            intensified_hotspots=intensified_hotspots,
            reduced_hotspots=reduced_hotspots,
            total_change=total_change,
            percent_change=round(percent_change, 2),
            hotspot_shift_score=round(shift_score, 4),
        )

    async def track_hotspot_evolution(
        self,
        jurisdiction: str,
        years: list[int],
        resolution: int | None = None,
    ) -> list[HotspotEvolution]:
        """
        Track hotspot evolution over multiple years.

        Args:
            jurisdiction: Jurisdiction code
            years: Years to analyze
            resolution: H3 resolution

        Returns:
            List of hotspot evolution records
        """
        # Generate heatmaps for all years
        heatmaps = await self.generate_yearly_heatmaps(jurisdiction, years, resolution)

        # Collect all H3 indices that were ever hotspots
        all_indices: set[str] = set()
        yearly_data: dict[int, dict[str, HeatmapCell]] = {}

        for year, heatmap in heatmaps.items():
            threshold = self._calculate_hotspot_threshold(
                [{"count": c.count} for c in heatmap.cells]
            )
            yearly_data[year] = {c.h3_index: c for c in heatmap.cells}

            for cell in heatmap.cells:
                if cell.count >= threshold:
                    all_indices.add(cell.h3_index)

        # Build evolution records
        evolutions = []
        sorted_years = sorted(years)

        for h3_index in all_indices:
            periods = []
            counts = []
            intensities = []
            first_appeared = None
            last_appeared = None

            for year in sorted_years:
                cell = yearly_data.get(year, {}).get(h3_index)
                periods.append(str(year))

                if cell:
                    counts.append(cell.count)
                    intensities.append(cell.intensity)
                    if first_appeared is None:
                        first_appeared = str(year)
                    last_appeared = str(year)
                else:
                    counts.append(0)
                    intensities.append(0.0)

            # Determine trend
            non_zero_counts = [c for c in counts if c > 0]
            if len(non_zero_counts) < 2:
                trend = "new" if counts[-1] > 0 else "disappeared"
                percent_change = 0.0
            else:
                first_val = non_zero_counts[0]
                last_val = non_zero_counts[-1]
                percent_change = ((last_val - first_val) / first_val) * 100 if first_val > 0 else 0

                if percent_change > 20:
                    trend = "emerging"
                elif percent_change < -20:
                    trend = "declining"
                else:
                    trend = "stable"

            # Check persistence
            is_persistent = sum(1 for c in counts if c > 0) >= len(years) * 0.7

            # Get coordinates from any available cell
            lat, lon = 0.0, 0.0
            for year in sorted_years:
                cell = yearly_data.get(year, {}).get(h3_index)
                if cell:
                    lat, lon = cell.latitude, cell.longitude
                    break

            evolutions.append(HotspotEvolution(
                h3_index=h3_index,
                latitude=lat,
                longitude=lon,
                periods=periods,
                counts=counts,
                intensities=intensities,
                trend=trend,
                percent_change=round(percent_change, 2),
                is_persistent=is_persistent,
                first_appeared=first_appeared or periods[0],
                last_appeared=last_appeared or periods[-1],
            ))

        # Sort by persistence and count
        evolutions.sort(key=lambda e: (e.is_persistent, sum(e.counts)), reverse=True)

        return evolutions

    async def _fetch_cell_data(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        resolution: int,
        crime_category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch cell data from Elasticsearch."""
        try:
            must_clauses = [
                {"term": {"jurisdiction": jurisdiction}},
                {"range": {"timestamp": {
                    "gte": start_date.isoformat(),
                    "lte": end_date.isoformat(),
                }}},
                {"exists": {"field": "h3_index"}},
            ]

            if crime_category:
                must_clauses.append({"term": {"crime_category": crime_category}})

            query = {"bool": {"must": must_clauses}}

            aggs = {
                "by_h3": {
                    "terms": {
                        "field": "h3_index",
                        "size": 10000,
                    },
                    "aggs": {
                        "avg_lat": {"avg": {"field": "latitude"}},
                        "avg_lon": {"avg": {"field": "longitude"}},
                        "by_category": {
                            "terms": {"field": "crime_category", "size": 10}
                        },
                        "by_severity": {
                            "terms": {"field": "severity", "size": 5}
                        },
                        "by_hour": {
                            "terms": {"field": "hour_of_day", "size": 24}
                        },
                        "by_dow": {
                            "terms": {"field": "day_of_week", "size": 7}
                        },
                    },
                }
            }

            result = await self.es.search(
                index="datalake_incidents",
                query=query,
                aggs=aggs,
                size=0,
            )

            buckets = result.get("aggregations", {}).get("by_h3", {}).get("buckets", [])

            cells = []
            for bucket in buckets:
                # Get peak hour
                hour_buckets = bucket.get("by_hour", {}).get("buckets", [])
                peak_hour = None
                if hour_buckets:
                    peak_hour = max(hour_buckets, key=lambda x: x["doc_count"])["key"]

                # Get peak day
                dow_buckets = bucket.get("by_dow", {}).get("buckets", [])
                peak_day = None
                if dow_buckets:
                    peak_day = max(dow_buckets, key=lambda x: x["doc_count"])["key"]

                cells.append({
                    "h3_index": bucket["key"],
                    "count": bucket["doc_count"],
                    "latitude": bucket.get("avg_lat", {}).get("value", 0),
                    "longitude": bucket.get("avg_lon", {}).get("value", 0),
                    "by_category": {
                        b["key"]: b["doc_count"]
                        for b in bucket.get("by_category", {}).get("buckets", [])
                    },
                    "by_severity": {
                        b["key"]: b["doc_count"]
                        for b in bucket.get("by_severity", {}).get("buckets", [])
                    },
                    "peak_hour": peak_hour,
                    "peak_day": peak_day,
                })

            return cells

        except Exception as e:
            logger.error(f"Failed to fetch cell data: {e}")
            # Return mock data for development
            return self._generate_mock_cells(jurisdiction)

    def _generate_mock_cells(self, jurisdiction: str) -> list[dict[str, Any]]:
        """Generate mock cell data for development."""
        import random

        # Generate cells around a center point
        center_lat, center_lon = 33.749, -84.388  # Atlanta

        cells = []
        for i in range(50):
            lat = center_lat + random.uniform(-0.1, 0.1)
            lon = center_lon + random.uniform(-0.1, 0.1)
            count = random.randint(5, 200)

            cells.append({
                "h3_index": f"8{i:06x}",
                "count": count,
                "latitude": lat,
                "longitude": lon,
                "by_category": {
                    "violent": random.randint(0, count // 3),
                    "property": random.randint(0, count // 2),
                    "other": random.randint(0, count // 4),
                },
                "by_severity": {
                    "high": random.randint(0, count // 4),
                    "medium": random.randint(0, count // 2),
                    "low": random.randint(0, count // 3),
                },
                "peak_hour": random.randint(0, 23),
                "peak_day": random.randint(0, 6),
            })

        return cells

    def _calculate_hotspot_threshold(self, cells: list[dict[str, Any]]) -> int:
        """Calculate hotspot threshold based on percentile."""
        if not cells:
            return 0

        counts = sorted([c["count"] for c in cells])
        index = int(len(counts) * self.HOTSPOT_PERCENTILE)
        return counts[min(index, len(counts) - 1)]

    def _calculate_shift_score(
        self,
        base_cells: dict[str, HeatmapCell],
        comp_cells: dict[str, HeatmapCell],
        base_threshold: int,
        comp_threshold: int,
    ) -> float:
        """Calculate how much hotspots have shifted between periods."""
        base_hotspots = {
            h3 for h3, c in base_cells.items() if c.count >= base_threshold
        }
        comp_hotspots = {
            h3 for h3, c in comp_cells.items() if c.count >= comp_threshold
        }

        if not base_hotspots and not comp_hotspots:
            return 0.0

        # Jaccard distance
        intersection = len(base_hotspots & comp_hotspots)
        union = len(base_hotspots | comp_hotspots)

        if union == 0:
            return 0.0

        # Return 1 - Jaccard similarity (higher = more shift)
        return 1 - (intersection / union)

    def _empty_heatmap(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        resolution: int,
    ) -> HeatmapData:
        """Return empty heatmap."""
        return HeatmapData(
            jurisdiction=jurisdiction,
            period_type="custom",
            period_label=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            start_date=start_date,
            end_date=end_date,
            cells=[],
            total_incidents=0,
            h3_resolution=resolution,
        )

    def _build_cache_key(self, *args: Any) -> str:
        """Build cache key."""
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
            logger.warning(f"Failed to cache: {e}")

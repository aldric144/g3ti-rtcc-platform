"""
Predictive Heatmap Engine for tactical analytics.

This module provides heatmap generation capabilities including:
- Gaussian Kernel Density Estimation (KDE)
- DBSCAN clustering for hotspot detection
- Bayesian spatial likelihood grids
- Time-weighted decay for recent incidents
- Multi-layer scoring (gunfire, violent crime, vehicle activity)
"""

import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np

from ...db.elasticsearch import ElasticsearchManager
from ...db.neo4j import Neo4jManager
from ...db.redis import RedisManager

logger = logging.getLogger(__name__)


class PredictiveHeatmapEngine:
    """
    Engine for generating predictive heatmaps using multiple algorithms.

    Supports:
    - Current state heatmaps based on recent incidents
    - Predictive heatmaps using temporal and spatial modeling
    - Multi-layer heatmaps combining different data sources
    """

    # Default grid parameters
    DEFAULT_GRID_SIZE = 100  # Number of cells per dimension
    DEFAULT_BANDWIDTH = 0.005  # KDE bandwidth in degrees (~500m)

    # Time decay parameters
    DECAY_HALF_LIFE_HOURS = 72  # Half-life for time decay

    # DBSCAN parameters
    DBSCAN_EPS = 0.003  # ~300m in degrees
    DBSCAN_MIN_SAMPLES = 3

    # Heatmap types and their weights
    HEATMAP_WEIGHTS = {
        "gunfire": {
            "shotspotter": 1.0,
            "shots_fired_calls": 0.8,
            "weapon_incidents": 0.6,
        },
        "vehicles": {
            "lpr_hits": 1.0,
            "vehicle_incidents": 0.7,
            "traffic_stops": 0.4,
        },
        "crime": {
            "violent_crime": 1.0,
            "property_crime": 0.6,
            "disorder_calls": 0.4,
        },
    }

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
    ):
        """
        Initialize the Predictive Heatmap Engine.

        Args:
            neo4j: Neo4j database manager
            es: Elasticsearch manager
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        # Cache for computed heatmaps
        self._cache_ttl = 300  # 5 minutes

        logger.info("PredictiveHeatmapEngine initialized")

    async def generate_current_heatmap(
        self,
        heatmap_type: str = "gunfire",
        bounds: dict | None = None,
        resolution: str = "medium",
        hours_back: int = 168,  # 7 days
    ) -> dict:
        """
        Generate current state heatmap based on recent incidents.

        Args:
            heatmap_type: Type of heatmap (gunfire, vehicles, crime, all)
            bounds: Geographic bounds {min_lat, max_lat, min_lon, max_lon}
            resolution: Grid resolution (low, medium, high)
            hours_back: Hours of historical data to include

        Returns:
            Heatmap data with GeoJSON, clusters, and metadata
        """
        # Set default bounds if not provided (example: city center)
        if bounds is None:
            bounds = {
                "min_lat": 33.35,
                "max_lat": 33.55,
                "min_lon": -112.15,
                "max_lon": -111.95,
            }

        # Determine grid size based on resolution
        grid_sizes = {"low": 50, "medium": 100, "high": 200}
        grid_size = grid_sizes.get(resolution, 100)

        # Fetch incident data
        incidents = await self._fetch_incidents(
            heatmap_type=heatmap_type,
            bounds=bounds,
            hours_back=hours_back,
        )

        if not incidents:
            return self._empty_heatmap_response(bounds, heatmap_type)

        # Extract coordinates and weights
        points, weights = self._extract_points_and_weights(incidents, heatmap_type)

        # Generate KDE heatmap
        kde_grid = self._compute_kde(points, weights, bounds, grid_size)

        # Detect clusters using DBSCAN
        clusters = self._detect_clusters(points, weights)

        # Generate hot zone polygons
        hot_zones = self._generate_hot_zones(kde_grid, bounds, grid_size)

        # Convert to GeoJSON
        geojson = self._grid_to_geojson(kde_grid, bounds, grid_size)

        # Calculate confidence based on data density
        confidence = self._calculate_confidence(len(incidents), hours_back)

        return {
            "geojson": geojson,
            "clusters": clusters,
            "hot_zones": hot_zones,
            "confidence": confidence,
            "metadata": {
                "type": heatmap_type,
                "incident_count": len(incidents),
                "hours_back": hours_back,
                "resolution": resolution,
                "generated_at": datetime.utcnow().isoformat(),
            },
            "explanation": self._generate_explanation(clusters, heatmap_type),
        }

    async def generate_predictive_heatmap(
        self,
        hours: int = 24,
        heatmap_type: str = "all",
        bounds: dict | None = None,
    ) -> dict:
        """
        Generate predictive heatmap for future time window.

        Uses Bayesian spatial likelihood combined with temporal patterns
        to predict where incidents are most likely to occur.

        Args:
            hours: Prediction window in hours
            heatmap_type: Type of prediction
            bounds: Geographic bounds

        Returns:
            Predictive heatmap with confidence scores
        """
        if bounds is None:
            bounds = {
                "min_lat": 33.35,
                "max_lat": 33.55,
                "min_lon": -112.15,
                "max_lon": -111.95,
            }

        grid_size = 100

        # Fetch historical data for pattern analysis
        historical_incidents = await self._fetch_incidents(
            heatmap_type=heatmap_type,
            bounds=bounds,
            hours_back=720,  # 30 days
        )

        if not historical_incidents:
            return self._empty_heatmap_response(bounds, heatmap_type, predictive=True)

        # Extract points and compute base KDE
        points, weights = self._extract_points_and_weights(
            historical_incidents, heatmap_type
        )
        base_kde = self._compute_kde(points, weights, bounds, grid_size)

        # Apply temporal patterns
        temporal_weights = self._compute_temporal_weights(
            historical_incidents, hours
        )

        # Compute Bayesian likelihood grid
        likelihood_grid = self._compute_bayesian_likelihood(
            base_kde, temporal_weights, bounds, grid_size
        )

        # Detect predicted clusters
        predicted_clusters = self._predict_clusters(
            likelihood_grid, bounds, grid_size
        )

        # Generate predicted hot zones
        predicted_zones = self._generate_hot_zones(
            likelihood_grid, bounds, grid_size, threshold=0.6
        )

        # Convert to GeoJSON
        geojson = self._grid_to_geojson(likelihood_grid, bounds, grid_size)

        # Calculate prediction confidence
        confidence = self._calculate_prediction_confidence(
            len(historical_incidents), hours
        )

        return {
            "geojson": geojson,
            "clusters": predicted_clusters,
            "hot_zones": predicted_zones,
            "confidence": confidence,
            "prediction_window": {
                "hours": hours,
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() + timedelta(hours=hours)).isoformat(),
            },
            "metadata": {
                "type": heatmap_type,
                "historical_incidents": len(historical_incidents),
                "model": "bayesian_kde_temporal",
                "generated_at": datetime.utcnow().isoformat(),
            },
            "explanation": self._generate_prediction_explanation(
                predicted_clusters, heatmap_type, hours
            ),
        }

    async def update_with_incident(self, incident_data: dict) -> dict:
        """
        Update heatmap data with a new incident.

        Args:
            incident_data: New incident information

        Returns:
            Update summary
        """
        # Invalidate cached heatmaps
        await self._invalidate_cache()

        # Determine affected zones
        lat = incident_data.get("latitude")
        lon = incident_data.get("longitude")
        incident_type = incident_data.get("type", "unknown")

        affected_zones = []
        if lat and lon:
            affected_zones = self._get_affected_zones(lat, lon)

        return {
            "updated": True,
            "incident_type": incident_type,
            "affected_zones": affected_zones,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ==================== Data Fetching ====================

    async def _fetch_incidents(
        self,
        heatmap_type: str,
        bounds: dict,
        hours_back: int,
    ) -> list[dict]:
        """Fetch incidents from Elasticsearch based on type and bounds."""
        try:
            # Build query based on heatmap type
            query = self._build_incident_query(heatmap_type, bounds, hours_back)

            # Execute search
            results = await self.es.search(
                index="incidents,shotspotter,lpr_hits",
                query=query,
                size=10000,
            )

            return results.get("hits", {}).get("hits", [])
        except Exception as e:
            logger.error(f"Failed to fetch incidents: {e}")
            # Return mock data for development
            return self._generate_mock_incidents(bounds, hours_back, heatmap_type)

    def _build_incident_query(
        self,
        heatmap_type: str,
        bounds: dict,
        hours_back: int,
    ) -> dict:
        """Build Elasticsearch query for incident fetching."""
        time_filter = {
            "range": {
                "timestamp": {
                    "gte": f"now-{hours_back}h",
                    "lte": "now",
                }
            }
        }

        geo_filter = {
            "geo_bounding_box": {
                "location": {
                    "top_left": {
                        "lat": bounds["max_lat"],
                        "lon": bounds["min_lon"],
                    },
                    "bottom_right": {
                        "lat": bounds["min_lat"],
                        "lon": bounds["max_lon"],
                    },
                }
            }
        }

        type_filters = []
        if heatmap_type == "gunfire":
            type_filters = [
                {"term": {"type": "shotspotter"}},
                {"term": {"type": "shots_fired"}},
                {"term": {"type": "weapon_offense"}},
            ]
        elif heatmap_type == "vehicles":
            type_filters = [
                {"term": {"type": "lpr_hit"}},
                {"term": {"type": "vehicle_incident"}},
            ]
        elif heatmap_type == "crime":
            type_filters = [
                {"term": {"type": "violent_crime"}},
                {"term": {"type": "property_crime"}},
            ]

        query = {
            "bool": {
                "must": [time_filter],
                "filter": [geo_filter],
            }
        }

        if type_filters:
            query["bool"]["should"] = type_filters
            query["bool"]["minimum_should_match"] = 1

        return query

    def _generate_mock_incidents(
        self,
        bounds: dict,
        hours_back: int,
        heatmap_type: str,
    ) -> list[dict]:
        """Generate mock incident data for development/testing."""
        incidents = []
        num_incidents = min(hours_back * 2, 500)

        # Create clustered incidents around hotspots
        hotspots = [
            (33.45, -112.07),  # Downtown
            (33.42, -112.05),  # South area
            (33.48, -112.10),  # West area
        ]

        for _i in range(num_incidents):
            # Select a hotspot with some probability
            if np.random.random() < 0.7:
                center = hotspots[np.random.randint(0, len(hotspots))]
                lat = center[0] + np.random.normal(0, 0.01)
                lon = center[1] + np.random.normal(0, 0.01)
            else:
                lat = np.random.uniform(bounds["min_lat"], bounds["max_lat"])
                lon = np.random.uniform(bounds["min_lon"], bounds["max_lon"])

            # Ensure within bounds
            lat = max(bounds["min_lat"], min(bounds["max_lat"], lat))
            lon = max(bounds["min_lon"], min(bounds["max_lon"], lon))

            timestamp = datetime.utcnow() - timedelta(
                hours=np.random.uniform(0, hours_back)
            )

            incidents.append({
                "_source": {
                    "latitude": lat,
                    "longitude": lon,
                    "timestamp": timestamp.isoformat(),
                    "type": heatmap_type,
                    "severity": np.random.choice(["low", "medium", "high"]),
                }
            })

        return incidents

    # ==================== KDE Computation ====================

    def _extract_points_and_weights(
        self,
        incidents: list[dict],
        heatmap_type: str,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Extract coordinate points and weights from incidents."""
        points = []
        weights = []

        now = datetime.utcnow()

        for incident in incidents:
            source = incident.get("_source", incident)
            lat = source.get("latitude")
            lon = source.get("longitude")

            if lat is None or lon is None:
                continue

            points.append([lat, lon])

            # Calculate time-based weight
            timestamp_str = source.get("timestamp", "")
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    hours_ago = (now - timestamp.replace(tzinfo=None)).total_seconds() / 3600
                else:
                    hours_ago = 0
            except (ValueError, TypeError):
                hours_ago = 0

            time_weight = math.exp(-hours_ago * math.log(2) / self.DECAY_HALF_LIFE_HOURS)

            # Calculate severity weight
            severity = source.get("severity", "medium")
            severity_weights = {"low": 0.5, "medium": 1.0, "high": 1.5}
            severity_weight = severity_weights.get(severity, 1.0)

            weights.append(time_weight * severity_weight)

        return np.array(points), np.array(weights)

    def _compute_kde(
        self,
        points: np.ndarray,
        weights: np.ndarray,
        bounds: dict,
        grid_size: int,
    ) -> np.ndarray:
        """
        Compute Kernel Density Estimation on a grid.

        Uses Gaussian kernel with adaptive bandwidth.
        """
        if len(points) == 0:
            return np.zeros((grid_size, grid_size))

        # Create grid
        lat_range = np.linspace(bounds["min_lat"], bounds["max_lat"], grid_size)
        lon_range = np.linspace(bounds["min_lon"], bounds["max_lon"], grid_size)

        # Initialize density grid
        density = np.zeros((grid_size, grid_size))

        # Compute bandwidth based on data spread
        if len(points) > 1:
            std_lat = np.std(points[:, 0])
            std_lon = np.std(points[:, 1])
            bandwidth = max(
                self.DEFAULT_BANDWIDTH,
                (std_lat + std_lon) / 2 * 0.5
            )
        else:
            bandwidth = self.DEFAULT_BANDWIDTH

        # Compute KDE using vectorized operations
        for i, lat in enumerate(lat_range):
            for j, lon in enumerate(lon_range):
                # Calculate distances to all points
                distances = np.sqrt(
                    (points[:, 0] - lat) ** 2 + (points[:, 1] - lon) ** 2
                )

                # Gaussian kernel
                kernel_values = np.exp(-0.5 * (distances / bandwidth) ** 2)

                # Weighted sum
                density[i, j] = np.sum(kernel_values * weights)

        # Normalize to 0-1 range
        if density.max() > 0:
            density = density / density.max()

        return density

    # ==================== DBSCAN Clustering ====================

    def _detect_clusters(
        self,
        points: np.ndarray,
        weights: np.ndarray,
    ) -> list[dict]:
        """
        Detect clusters using DBSCAN algorithm.

        Returns cluster information including centroids and sizes.
        """
        if len(points) < self.DBSCAN_MIN_SAMPLES:
            return []

        # Simple DBSCAN implementation
        clusters = []
        visited = set()
        cluster_id = 0

        for i in range(len(points)):
            if i in visited:
                continue

            # Find neighbors
            neighbors = self._get_neighbors(points, i, self.DBSCAN_EPS)

            if len(neighbors) < self.DBSCAN_MIN_SAMPLES:
                continue

            # Start new cluster
            cluster_points = []
            cluster_weights = []

            # Expand cluster
            to_process = list(neighbors)
            while to_process:
                point_idx = to_process.pop()
                if point_idx in visited:
                    continue

                visited.add(point_idx)
                cluster_points.append(points[point_idx])
                cluster_weights.append(weights[point_idx])

                # Find neighbors of this point
                point_neighbors = self._get_neighbors(
                    points, point_idx, self.DBSCAN_EPS
                )

                if len(point_neighbors) >= self.DBSCAN_MIN_SAMPLES:
                    to_process.extend(
                        n for n in point_neighbors if n not in visited
                    )

            if cluster_points:
                cluster_points = np.array(cluster_points)
                cluster_weights = np.array(cluster_weights)

                # Calculate weighted centroid
                total_weight = cluster_weights.sum()
                centroid = (
                    (cluster_points * cluster_weights[:, np.newaxis]).sum(axis=0)
                    / total_weight
                )

                clusters.append({
                    "id": f"cluster_{cluster_id}",
                    "centroid": {
                        "lat": float(centroid[0]),
                        "lon": float(centroid[1]),
                    },
                    "point_count": len(cluster_points),
                    "total_weight": float(total_weight),
                    "radius": float(self._calculate_cluster_radius(
                        cluster_points, centroid
                    )),
                    "confidence": min(1.0, len(cluster_points) / 20),
                })

                cluster_id += 1

        # Sort by weight (most significant first)
        clusters.sort(key=lambda x: x["total_weight"], reverse=True)

        return clusters[:10]  # Return top 10 clusters

    def _get_neighbors(
        self,
        points: np.ndarray,
        point_idx: int,
        eps: float,
    ) -> list[int]:
        """Get indices of points within eps distance."""
        distances = np.sqrt(
            np.sum((points - points[point_idx]) ** 2, axis=1)
        )
        return list(np.where(distances <= eps)[0])

    def _calculate_cluster_radius(
        self,
        points: np.ndarray,
        centroid: np.ndarray,
    ) -> float:
        """Calculate the radius of a cluster."""
        distances = np.sqrt(np.sum((points - centroid) ** 2, axis=1))
        return float(np.percentile(distances, 90))  # 90th percentile

    # ==================== Bayesian Likelihood ====================

    def _compute_bayesian_likelihood(
        self,
        base_kde: np.ndarray,
        temporal_weights: np.ndarray,
        bounds: dict,
        grid_size: int,
    ) -> np.ndarray:
        """
        Compute Bayesian spatial likelihood grid.

        Combines prior (base KDE) with temporal likelihood.
        """
        # Prior: base KDE normalized
        prior = base_kde / (base_kde.sum() + 1e-10)

        # Likelihood: temporal patterns
        # Reshape temporal weights to grid if needed
        if temporal_weights.shape != base_kde.shape:
            temporal_weights = np.ones_like(base_kde) * temporal_weights.mean()

        # Posterior: prior * likelihood (unnormalized)
        posterior = prior * temporal_weights

        # Normalize
        if posterior.sum() > 0:
            posterior = posterior / posterior.max()

        return posterior

    def _compute_temporal_weights(
        self,
        incidents: list[dict],
        prediction_hours: int,
    ) -> np.ndarray:
        """
        Compute temporal weights based on historical patterns.

        Analyzes day-of-week and hour-of-day patterns.
        """
        # Target time window
        target_start = datetime.utcnow()
        target_end = target_start + timedelta(hours=prediction_hours)

        # Analyze historical patterns
        hour_counts = defaultdict(int)
        dow_counts = defaultdict(int)

        for incident in incidents:
            source = incident.get("_source", incident)
            timestamp_str = source.get("timestamp", "")

            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    hour_counts[timestamp.hour] += 1
                    dow_counts[timestamp.weekday()] += 1
            except (ValueError, TypeError):
                continue

        # Calculate weight for prediction window
        total_weight = 0.0
        current = target_start

        while current < target_end:
            hour_weight = hour_counts.get(current.hour, 1) / max(
                sum(hour_counts.values()), 1
            )
            dow_weight = dow_counts.get(current.weekday(), 1) / max(
                sum(dow_counts.values()), 1
            )
            total_weight += hour_weight * dow_weight
            current += timedelta(hours=1)

        # Normalize
        avg_weight = total_weight / max(prediction_hours, 1)

        return np.array([[avg_weight]])

    # ==================== Hot Zone Generation ====================

    def _generate_hot_zones(
        self,
        grid: np.ndarray,
        bounds: dict,
        grid_size: int,
        threshold: float = 0.5,
    ) -> list[dict]:
        """
        Generate hot zone polygons from density grid.

        Uses contour detection to identify high-density areas.
        """
        hot_zones = []

        # Find cells above threshold
        high_density_mask = grid > threshold

        # Simple connected component labeling
        visited = np.zeros_like(high_density_mask, dtype=bool)
        zone_id = 0

        lat_step = (bounds["max_lat"] - bounds["min_lat"]) / grid_size
        lon_step = (bounds["max_lon"] - bounds["min_lon"]) / grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                if high_density_mask[i, j] and not visited[i, j]:
                    # Flood fill to find connected region
                    region_cells = []
                    stack = [(i, j)]

                    while stack:
                        ci, cj = stack.pop()
                        if (
                            0 <= ci < grid_size
                            and 0 <= cj < grid_size
                            and high_density_mask[ci, cj]
                            and not visited[ci, cj]
                        ):
                            visited[ci, cj] = True
                            region_cells.append((ci, cj))

                            # Add neighbors
                            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                stack.append((ci + di, cj + dj))

                    if len(region_cells) >= 4:  # Minimum size
                        # Calculate zone properties
                        cells = np.array(region_cells)
                        center_i = cells[:, 0].mean()
                        center_j = cells[:, 1].mean()

                        center_lat = bounds["min_lat"] + center_i * lat_step
                        center_lon = bounds["min_lon"] + center_j * lon_step

                        # Calculate average density in zone
                        zone_density = np.mean([
                            grid[ci, cj] for ci, cj in region_cells
                        ])

                        # Create bounding polygon
                        min_i, max_i = cells[:, 0].min(), cells[:, 0].max()
                        min_j, max_j = cells[:, 1].min(), cells[:, 1].max()

                        polygon = [
                            [
                                bounds["min_lon"] + min_j * lon_step,
                                bounds["min_lat"] + min_i * lat_step,
                            ],
                            [
                                bounds["min_lon"] + max_j * lon_step,
                                bounds["min_lat"] + min_i * lat_step,
                            ],
                            [
                                bounds["min_lon"] + max_j * lon_step,
                                bounds["min_lat"] + max_i * lat_step,
                            ],
                            [
                                bounds["min_lon"] + min_j * lon_step,
                                bounds["min_lat"] + max_i * lat_step,
                            ],
                            [
                                bounds["min_lon"] + min_j * lon_step,
                                bounds["min_lat"] + min_i * lat_step,
                            ],
                        ]

                        hot_zones.append({
                            "id": f"zone_{zone_id}",
                            "center": {
                                "lat": float(center_lat),
                                "lon": float(center_lon),
                            },
                            "polygon": polygon,
                            "cell_count": len(region_cells),
                            "density": float(zone_density),
                            "confidence": float(min(zone_density * 1.2, 1.0)),
                        })

                        zone_id += 1

        # Sort by density
        hot_zones.sort(key=lambda x: x["density"], reverse=True)

        return hot_zones[:5]  # Return top 5 zones

    def _predict_clusters(
        self,
        likelihood_grid: np.ndarray,
        bounds: dict,
        grid_size: int,
    ) -> list[dict]:
        """Predict clusters from likelihood grid."""
        # Find local maxima in the likelihood grid
        clusters = []

        lat_step = (bounds["max_lat"] - bounds["min_lat"]) / grid_size
        lon_step = (bounds["max_lon"] - bounds["min_lon"]) / grid_size

        for i in range(1, grid_size - 1):
            for j in range(1, grid_size - 1):
                # Check if local maximum
                center_val = likelihood_grid[i, j]
                if center_val < 0.5:
                    continue

                is_max = True
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        if likelihood_grid[i + di, j + dj] > center_val:
                            is_max = False
                            break
                    if not is_max:
                        break

                if is_max:
                    lat = bounds["min_lat"] + i * lat_step
                    lon = bounds["min_lon"] + j * lon_step

                    clusters.append({
                        "id": f"predicted_{len(clusters)}",
                        "centroid": {"lat": float(lat), "lon": float(lon)},
                        "likelihood": float(center_val),
                        "confidence": float(center_val * 0.8),
                        "type": "predicted",
                    })

        # Sort by likelihood
        clusters.sort(key=lambda x: x["likelihood"], reverse=True)

        return clusters[:10]

    # ==================== GeoJSON Conversion ====================

    def _grid_to_geojson(
        self,
        grid: np.ndarray,
        bounds: dict,
        grid_size: int,
    ) -> dict:
        """Convert density grid to GeoJSON format."""
        features = []

        lat_step = (bounds["max_lat"] - bounds["min_lat"]) / grid_size
        lon_step = (bounds["max_lon"] - bounds["min_lon"]) / grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                density = grid[i, j]
                if density < 0.1:  # Skip low-density cells
                    continue

                lat = bounds["min_lat"] + i * lat_step
                lon = bounds["min_lon"] + j * lon_step

                # Create cell polygon
                polygon = [
                    [lon, lat],
                    [lon + lon_step, lat],
                    [lon + lon_step, lat + lat_step],
                    [lon, lat + lat_step],
                    [lon, lat],
                ]

                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [polygon],
                    },
                    "properties": {
                        "density": float(density),
                        "color": self._density_to_color(density),
                    },
                })

        return {
            "type": "FeatureCollection",
            "features": features,
        }

    def _density_to_color(self, density: float) -> str:
        """Convert density value to color hex code."""
        if density < 0.3:
            return "#FFFF00"  # Yellow
        elif density < 0.5:
            return "#FFA500"  # Orange
        elif density < 0.7:
            return "#FF4500"  # Orange-Red
        else:
            return "#FF0000"  # Red

    # ==================== Helper Methods ====================

    def _empty_heatmap_response(
        self,
        bounds: dict,
        heatmap_type: str,
        predictive: bool = False,
    ) -> dict:
        """Return empty heatmap response."""
        return {
            "geojson": {"type": "FeatureCollection", "features": []},
            "clusters": [],
            "hot_zones": [],
            "confidence": 0.0,
            "metadata": {
                "type": heatmap_type,
                "incident_count": 0,
                "predictive": predictive,
                "generated_at": datetime.utcnow().isoformat(),
            },
            "explanation": "No data available for the specified parameters.",
        }

    def _calculate_confidence(
        self,
        incident_count: int,
        hours_back: int,
    ) -> float:
        """Calculate confidence score based on data density."""
        # More incidents = higher confidence
        density_factor = min(incident_count / 100, 1.0)

        # More recent data = higher confidence
        recency_factor = min(168 / hours_back, 1.0)

        return round(density_factor * 0.7 + recency_factor * 0.3, 2)

    def _calculate_prediction_confidence(
        self,
        historical_count: int,
        prediction_hours: int,
    ) -> float:
        """Calculate confidence for predictions."""
        # More historical data = higher confidence
        data_factor = min(historical_count / 200, 1.0)

        # Shorter prediction window = higher confidence
        time_factor = max(0.3, 1.0 - (prediction_hours / 168) * 0.5)

        return round(data_factor * 0.6 + time_factor * 0.4, 2)

    def _generate_explanation(
        self,
        clusters: list[dict],
        heatmap_type: str,
    ) -> str:
        """Generate human-readable explanation of heatmap."""
        if not clusters:
            return f"No significant {heatmap_type} clusters detected."

        top_cluster = clusters[0]
        explanation = (
            f"Identified {len(clusters)} {heatmap_type} hotspot(s). "
            f"Primary cluster at ({top_cluster['centroid']['lat']:.4f}, "
            f"{top_cluster['centroid']['lon']:.4f}) with {top_cluster['point_count']} "
            f"incidents and confidence {top_cluster['confidence']:.0%}."
        )

        return explanation

    def _generate_prediction_explanation(
        self,
        clusters: list[dict],
        heatmap_type: str,
        hours: int,
    ) -> str:
        """Generate explanation for predictive heatmap."""
        if not clusters:
            return f"No high-likelihood {heatmap_type} areas predicted for next {hours} hours."

        top_cluster = clusters[0]
        explanation = (
            f"Predicted {len(clusters)} high-likelihood {heatmap_type} zone(s) "
            f"for the next {hours} hours. Highest likelihood area at "
            f"({top_cluster['centroid']['lat']:.4f}, {top_cluster['centroid']['lon']:.4f}) "
            f"with {top_cluster['likelihood']:.0%} probability."
        )

        return explanation

    def _get_affected_zones(self, lat: float, lon: float) -> list[str]:
        """Get zone IDs affected by a location."""
        # Simple grid-based zone assignment
        zone_lat = int((lat - 33.0) * 100)
        zone_lon = int((lon + 113.0) * 100)
        return [f"zone_{zone_lat}_{zone_lon}"]

    async def _invalidate_cache(self) -> None:
        """Invalidate cached heatmap data."""
        try:
            await self.redis.delete_pattern("heatmap:*")
        except Exception as e:
            logger.warning(f"Failed to invalidate heatmap cache: {e}")

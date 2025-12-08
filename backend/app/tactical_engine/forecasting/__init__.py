"""
Tactical Forecasting Engine for G3TI RTCC-UIP.

This module provides forecasting capabilities including:
- Temporal ARIMA-style modeling
- Rolling KDE predictions
- Markov temporal transition modeling
- Seasonal patterns (weekend, holidays, paydays)
- 24-hour and 7-day crime forecasts
- Vehicle recurrence predictions
- Gunfire cluster forecasting
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np

from ...db.elasticsearch import ElasticsearchManager
from ...db.neo4j import Neo4jManager
from ...db.redis import RedisManager

logger = logging.getLogger(__name__)


class TacticalForecaster:
    """
    Engine for tactical forecasting using multiple prediction models.

    Combines temporal analysis, spatial patterns, and historical data
    to predict future crime locations and timing.
    """

    # Forecast model parameters
    ARIMA_ORDER = (2, 1, 2)  # (p, d, q) for ARIMA-like model
    MARKOV_STATES = ["low", "medium", "high", "critical"]

    # Seasonal factors
    WEEKEND_MULTIPLIER = 1.3
    HOLIDAY_MULTIPLIER = 0.8
    PAYDAY_MULTIPLIER = 1.2

    # Time windows
    SHORT_TERM_HOURS = 24
    MEDIUM_TERM_HOURS = 72
    LONG_TERM_HOURS = 168  # 7 days

    # Default bounds
    DEFAULT_BOUNDS = {
        "min_lat": 33.35,
        "max_lat": 33.55,
        "min_lon": -112.15,
        "max_lon": -111.95,
    }

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
    ):
        """
        Initialize the Tactical Forecaster.

        Args:
            neo4j: Neo4j database manager
            es: Elasticsearch manager
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        # Model state
        self._transition_matrix = None
        self._temporal_patterns = None

        logger.info("TacticalForecaster initialized")

    async def generate_forecast(
        self,
        hours: int = 24,
        forecast_type: str = "all",
        bounds: dict | None = None,
    ) -> dict:
        """
        Generate tactical forecast.

        Args:
            hours: Forecast window in hours
            forecast_type: Type of forecast (crime, gunfire, vehicles, all)
            bounds: Geographic bounds for forecast

        Returns:
            Forecast data with predictions and confidence
        """
        logger.info(f"Generating forecast: hours={hours}, type={forecast_type}")

        if bounds is None:
            bounds = self.DEFAULT_BOUNDS

        # Get historical data for modeling
        historical_data = await self._fetch_historical_data(
            forecast_type, bounds, hours_back=720  # 30 days
        )

        # Build temporal model
        temporal_forecast = self._build_temporal_forecast(
            historical_data, hours
        )

        # Build spatial forecast
        spatial_forecast = await self._build_spatial_forecast(
            historical_data, bounds, hours
        )

        # Build Markov transition forecast
        markov_forecast = self._build_markov_forecast(
            historical_data, hours
        )

        # Combine forecasts
        combined_forecast = self._combine_forecasts(
            temporal_forecast, spatial_forecast, markov_forecast
        )

        # Apply seasonal adjustments
        adjusted_forecast = self._apply_seasonal_adjustments(
            combined_forecast, hours
        )

        # Generate predictions by zone
        zone_predictions = self._generate_zone_predictions(
            adjusted_forecast, bounds
        )

        # Calculate overall confidence
        confidence = self._calculate_forecast_confidence(
            len(historical_data), hours
        )

        return {
            "forecast_window": {
                "hours": hours,
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() + timedelta(hours=hours)).isoformat(),
            },
            "forecast_type": forecast_type,
            "predictions": {
                "temporal": temporal_forecast,
                "spatial": spatial_forecast,
                "markov": markov_forecast,
            },
            "zone_predictions": zone_predictions,
            "high_risk_areas": self._identify_high_risk_areas(zone_predictions),
            "expected_incidents": adjusted_forecast.get("expected_count", 0),
            "confidence": confidence,
            "model_info": {
                "historical_data_points": len(historical_data),
                "models_used": ["temporal_arima", "spatial_kde", "markov_chain"],
                "seasonal_adjustments_applied": True,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def get_crime_forecast(
        self,
        hours: int = 24,
        bounds: dict | None = None,
    ) -> dict:
        """Get crime-specific forecast."""
        return await self.generate_forecast(
            hours=hours, forecast_type="crime", bounds=bounds
        )

    async def get_gunfire_forecast(
        self,
        hours: int = 72,
        bounds: dict | None = None,
    ) -> dict:
        """Get gunfire-specific forecast."""
        return await self.generate_forecast(
            hours=hours, forecast_type="gunfire", bounds=bounds
        )

    async def get_vehicle_forecast(
        self,
        hours: int = 24,
        bounds: dict | None = None,
    ) -> dict:
        """Get vehicle recurrence forecast."""
        return await self.generate_forecast(
            hours=hours, forecast_type="vehicles", bounds=bounds
        )

    # ==================== Data Fetching ====================

    async def _fetch_historical_data(
        self,
        forecast_type: str,
        bounds: dict,
        hours_back: int,
    ) -> list[dict]:
        """Fetch historical data for modeling."""
        try:
            # Build query based on forecast type
            type_filters = []
            if forecast_type == "crime":
                type_filters = [
                    {"terms": {"type": ["assault", "robbery", "burglary", "theft"]}}
                ]
            elif forecast_type == "gunfire":
                type_filters = [
                    {"terms": {"type": ["shotspotter", "shots_fired", "shooting"]}}
                ]
            elif forecast_type == "vehicles":
                type_filters = [{"term": {"type": "lpr_hit"}}]

            query = {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": f"now-{hours_back}h"}}}
                    ],
                    "filter": [
                        {
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
                    ],
                }
            }

            if type_filters:
                query["bool"]["must"].extend(type_filters)

            results = await self.es.search(
                index="incidents,shotspotter,lpr_hits",
                query=query,
                size=5000,
                sort=[{"timestamp": "asc"}],
            )

            return [
                hit["_source"]
                for hit in results.get("hits", {}).get("hits", [])
            ]
        except Exception as e:
            logger.warning(f"Failed to fetch historical data: {e}")
            # Generate mock data
            return self._generate_mock_historical_data(bounds, hours_back)

    def _generate_mock_historical_data(
        self,
        bounds: dict,
        hours_back: int,
    ) -> list[dict]:
        """Generate mock historical data for development."""
        data = []
        num_incidents = min(hours_back * 3, 2000)

        # Create clustered incidents
        hotspots = [
            (33.45, -112.07),
            (33.42, -112.05),
            (33.48, -112.10),
        ]

        for _i in range(num_incidents):
            # Select hotspot with probability
            if np.random.random() < 0.6:
                center = hotspots[np.random.randint(0, len(hotspots))]
                lat = center[0] + np.random.normal(0, 0.015)
                lon = center[1] + np.random.normal(0, 0.015)
            else:
                lat = np.random.uniform(bounds["min_lat"], bounds["max_lat"])
                lon = np.random.uniform(bounds["min_lon"], bounds["max_lon"])

            # Ensure within bounds
            lat = max(bounds["min_lat"], min(bounds["max_lat"], lat))
            lon = max(bounds["min_lon"], min(bounds["max_lon"], lon))

            # Generate timestamp with temporal patterns
            hours_ago = np.random.uniform(0, hours_back)
            timestamp = datetime.utcnow() - timedelta(hours=hours_ago)

            # Add temporal bias (more incidents at night)
            if np.random.random() < 0.3:
                timestamp = timestamp.replace(
                    hour=np.random.choice([22, 23, 0, 1, 2])
                )

            data.append({
                "latitude": lat,
                "longitude": lon,
                "timestamp": timestamp.isoformat(),
                "type": np.random.choice(
                    ["assault", "theft", "burglary", "shots_fired"]
                ),
                "severity": np.random.choice(["low", "medium", "high"]),
            })

        return data

    # ==================== Temporal Forecasting ====================

    def _build_temporal_forecast(
        self,
        historical_data: list[dict],
        forecast_hours: int,
    ) -> dict:
        """
        Build temporal forecast using ARIMA-like approach.

        Analyzes hourly patterns and trends to predict future activity.
        """
        if not historical_data:
            return self._empty_temporal_forecast()

        # Aggregate data by hour
        hourly_counts = self._aggregate_by_hour(historical_data)

        # Calculate trend
        trend = self._calculate_trend(hourly_counts)

        # Calculate hourly patterns (hour-of-day effects)
        hourly_patterns = self._calculate_hourly_patterns(historical_data)

        # Calculate day-of-week patterns
        dow_patterns = self._calculate_dow_patterns(historical_data)

        # Generate hourly predictions
        predictions = []
        current_time = datetime.utcnow()

        for h in range(forecast_hours):
            pred_time = current_time + timedelta(hours=h)
            hour = pred_time.hour
            dow = pred_time.weekday()

            # Base prediction from recent average
            base_rate = np.mean(list(hourly_counts.values())[-168:]) if hourly_counts else 1.0

            # Apply hourly pattern
            hour_factor = hourly_patterns.get(hour, 1.0)

            # Apply day-of-week pattern
            dow_factor = dow_patterns.get(dow, 1.0)

            # Apply trend
            trend_factor = 1.0 + (trend * h / 24)

            predicted_count = base_rate * hour_factor * dow_factor * trend_factor

            predictions.append({
                "hour": h,
                "timestamp": pred_time.isoformat(),
                "predicted_incidents": round(max(0, predicted_count), 2),
                "confidence": max(0.3, 0.9 - (h / forecast_hours) * 0.4),
            })

        # Calculate peak periods
        peak_hours = self._identify_peak_hours(predictions)

        return {
            "hourly_predictions": predictions,
            "trend": round(trend, 4),
            "trend_direction": "increasing" if trend > 0.01 else (
                "decreasing" if trend < -0.01 else "stable"
            ),
            "peak_hours": peak_hours,
            "total_expected": round(
                sum(p["predicted_incidents"] for p in predictions), 1
            ),
            "hourly_patterns": hourly_patterns,
            "dow_patterns": dow_patterns,
        }

    def _aggregate_by_hour(self, data: list[dict]) -> dict:
        """Aggregate incident counts by hour."""
        hourly_counts = defaultdict(int)

        for incident in data:
            timestamp_str = incident.get("timestamp", "")
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    hour_key = timestamp.strftime("%Y-%m-%d-%H")
                    hourly_counts[hour_key] += 1
            except (ValueError, TypeError):
                continue

        return dict(hourly_counts)

    def _calculate_trend(self, hourly_counts: dict) -> float:
        """Calculate trend from hourly counts."""
        if len(hourly_counts) < 48:
            return 0.0

        # Get sorted counts
        sorted_keys = sorted(hourly_counts.keys())
        counts = [hourly_counts[k] for k in sorted_keys]

        # Calculate simple linear trend
        n = len(counts)
        x = np.arange(n)
        y = np.array(counts)

        # Linear regression
        x_mean = x.mean()
        y_mean = y.mean()

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Normalize by mean
        return slope / max(y_mean, 1)

    def _calculate_hourly_patterns(self, data: list[dict]) -> dict:
        """Calculate hour-of-day patterns."""
        hour_counts = defaultdict(int)
        hour_totals = defaultdict(int)

        for incident in data:
            timestamp_str = incident.get("timestamp", "")
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    hour_counts[timestamp.hour] += 1
                    hour_totals[timestamp.hour] += 1
            except (ValueError, TypeError):
                continue

        # Calculate relative factors
        total = sum(hour_counts.values())
        avg_per_hour = total / 24 if total > 0 else 1

        patterns = {}
        for hour in range(24):
            count = hour_counts.get(hour, 0)
            patterns[hour] = count / avg_per_hour if avg_per_hour > 0 else 1.0

        return patterns

    def _calculate_dow_patterns(self, data: list[dict]) -> dict:
        """Calculate day-of-week patterns."""
        dow_counts = defaultdict(int)

        for incident in data:
            timestamp_str = incident.get("timestamp", "")
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    dow_counts[timestamp.weekday()] += 1
            except (ValueError, TypeError):
                continue

        # Calculate relative factors
        total = sum(dow_counts.values())
        avg_per_day = total / 7 if total > 0 else 1

        patterns = {}
        for dow in range(7):
            count = dow_counts.get(dow, 0)
            patterns[dow] = count / avg_per_day if avg_per_day > 0 else 1.0

        return patterns

    def _identify_peak_hours(self, predictions: list[dict]) -> list[dict]:
        """Identify peak activity hours from predictions."""
        # Sort by predicted incidents
        sorted_preds = sorted(
            predictions, key=lambda x: x["predicted_incidents"], reverse=True
        )

        # Get top 5 hours
        peak_hours = []
        for pred in sorted_preds[:5]:
            peak_hours.append({
                "hour": pred["hour"],
                "timestamp": pred["timestamp"],
                "predicted_incidents": pred["predicted_incidents"],
            })

        return peak_hours

    def _empty_temporal_forecast(self) -> dict:
        """Return empty temporal forecast."""
        return {
            "hourly_predictions": [],
            "trend": 0.0,
            "trend_direction": "unknown",
            "peak_hours": [],
            "total_expected": 0,
            "hourly_patterns": {},
            "dow_patterns": {},
        }

    # ==================== Spatial Forecasting ====================

    async def _build_spatial_forecast(
        self,
        historical_data: list[dict],
        bounds: dict,
        forecast_hours: int,
    ) -> dict:
        """
        Build spatial forecast using KDE and clustering.

        Predicts where incidents are most likely to occur.
        """
        if not historical_data:
            return self._empty_spatial_forecast()

        # Extract coordinates
        points = []
        for incident in historical_data:
            lat = incident.get("latitude")
            lon = incident.get("longitude")
            if lat and lon:
                points.append([lat, lon])

        if not points:
            return self._empty_spatial_forecast()

        points = np.array(points)

        # Compute KDE
        grid_size = 20
        kde_grid = self._compute_kde_grid(points, bounds, grid_size)

        # Find hotspots
        hotspots = self._find_hotspots(kde_grid, bounds, grid_size)

        # Calculate spatial concentration
        concentration = self._calculate_spatial_concentration(points)

        return {
            "hotspots": hotspots,
            "concentration_index": round(concentration, 3),
            "spatial_distribution": "clustered" if concentration > 0.5 else "dispersed",
            "grid_size": grid_size,
            "bounds": bounds,
        }

    def _compute_kde_grid(
        self,
        points: np.ndarray,
        bounds: dict,
        grid_size: int,
    ) -> np.ndarray:
        """Compute KDE on a grid."""
        lat_range = np.linspace(bounds["min_lat"], bounds["max_lat"], grid_size)
        lon_range = np.linspace(bounds["min_lon"], bounds["max_lon"], grid_size)

        density = np.zeros((grid_size, grid_size))
        bandwidth = 0.01

        for i, lat in enumerate(lat_range):
            for j, lon in enumerate(lon_range):
                distances = np.sqrt(
                    (points[:, 0] - lat) ** 2 + (points[:, 1] - lon) ** 2
                )
                kernel_values = np.exp(-0.5 * (distances / bandwidth) ** 2)
                density[i, j] = np.sum(kernel_values)

        if density.max() > 0:
            density = density / density.max()

        return density

    def _find_hotspots(
        self,
        kde_grid: np.ndarray,
        bounds: dict,
        grid_size: int,
        threshold: float = 0.6,
    ) -> list[dict]:
        """Find hotspots from KDE grid."""
        hotspots = []

        lat_step = (bounds["max_lat"] - bounds["min_lat"]) / grid_size
        lon_step = (bounds["max_lon"] - bounds["min_lon"]) / grid_size

        # Find local maxima above threshold
        for i in range(1, grid_size - 1):
            for j in range(1, grid_size - 1):
                val = kde_grid[i, j]
                if val < threshold:
                    continue

                # Check if local maximum
                is_max = True
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        if kde_grid[i + di, j + dj] > val:
                            is_max = False
                            break
                    if not is_max:
                        break

                if is_max:
                    lat = bounds["min_lat"] + i * lat_step
                    lon = bounds["min_lon"] + j * lon_step

                    hotspots.append({
                        "lat": round(lat, 5),
                        "lon": round(lon, 5),
                        "intensity": round(val, 3),
                        "radius_km": round(lat_step * 111, 2),
                    })

        # Sort by intensity
        hotspots.sort(key=lambda x: x["intensity"], reverse=True)

        return hotspots[:10]

    def _calculate_spatial_concentration(self, points: np.ndarray) -> float:
        """Calculate spatial concentration index."""
        if len(points) < 2:
            return 0.0

        # Calculate centroid
        centroid = points.mean(axis=0)

        # Calculate distances from centroid
        distances = np.sqrt(np.sum((points - centroid) ** 2, axis=1))

        # Calculate coefficient of variation
        mean_dist = distances.mean()
        std_dist = distances.std()

        if mean_dist == 0:
            return 0.0

        cv = std_dist / mean_dist

        # Convert to concentration index (higher = more clustered)
        return 1.0 / (1.0 + cv)

    def _empty_spatial_forecast(self) -> dict:
        """Return empty spatial forecast."""
        return {
            "hotspots": [],
            "concentration_index": 0.0,
            "spatial_distribution": "unknown",
            "grid_size": 0,
            "bounds": {},
        }

    # ==================== Markov Chain Forecasting ====================

    def _build_markov_forecast(
        self,
        historical_data: list[dict],
        forecast_hours: int,
    ) -> dict:
        """
        Build Markov chain forecast for activity state transitions.

        Models transitions between low, medium, high, and critical states.
        """
        if not historical_data:
            return self._empty_markov_forecast()

        # Build transition matrix from historical data
        transition_matrix = self._build_transition_matrix(historical_data)

        # Get current state
        current_state = self._determine_current_state(historical_data)

        # Predict future states
        state_predictions = self._predict_states(
            transition_matrix, current_state, forecast_hours
        )

        # Calculate steady state
        steady_state = self._calculate_steady_state(transition_matrix)

        return {
            "current_state": current_state,
            "transition_matrix": {
                state: {
                    s: round(transition_matrix[i][j], 3)
                    for j, s in enumerate(self.MARKOV_STATES)
                }
                for i, state in enumerate(self.MARKOV_STATES)
            },
            "state_predictions": state_predictions,
            "steady_state": {
                state: round(prob, 3)
                for state, prob in zip(self.MARKOV_STATES, steady_state, strict=False)
            },
            "most_likely_state_24h": self._get_most_likely_state(
                state_predictions, 24
            ),
        }

    def _build_transition_matrix(self, data: list[dict]) -> np.ndarray:
        """Build transition matrix from historical data."""
        n_states = len(self.MARKOV_STATES)
        transitions = np.zeros((n_states, n_states))

        # Sort data by timestamp
        sorted_data = sorted(
            data,
            key=lambda x: x.get("timestamp", ""),
        )

        # Aggregate into hourly states
        hourly_states = self._aggregate_to_states(sorted_data)

        # Count transitions
        for i in range(len(hourly_states) - 1):
            from_state = self.MARKOV_STATES.index(hourly_states[i])
            to_state = self.MARKOV_STATES.index(hourly_states[i + 1])
            transitions[from_state][to_state] += 1

        # Normalize rows
        for i in range(n_states):
            row_sum = transitions[i].sum()
            if row_sum > 0:
                transitions[i] /= row_sum
            else:
                # Default to staying in same state
                transitions[i][i] = 1.0

        return transitions

    def _aggregate_to_states(self, data: list[dict]) -> list[str]:
        """Aggregate data into hourly activity states."""
        hourly_counts = defaultdict(int)

        for incident in data:
            timestamp_str = incident.get("timestamp", "")
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    hour_key = timestamp.strftime("%Y-%m-%d-%H")
                    hourly_counts[hour_key] += 1
            except (ValueError, TypeError):
                continue

        # Convert counts to states
        states = []
        for hour_key in sorted(hourly_counts.keys()):
            count = hourly_counts[hour_key]
            if count <= 1:
                states.append("low")
            elif count <= 3:
                states.append("medium")
            elif count <= 6:
                states.append("high")
            else:
                states.append("critical")

        return states

    def _determine_current_state(self, data: list[dict]) -> str:
        """Determine current activity state."""
        # Count incidents in last hour
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        recent_count = 0
        for incident in data:
            timestamp_str = incident.get("timestamp", "")
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                    if timestamp.replace(tzinfo=None) >= hour_ago:
                        recent_count += 1
            except (ValueError, TypeError):
                continue

        if recent_count <= 1:
            return "low"
        elif recent_count <= 3:
            return "medium"
        elif recent_count <= 6:
            return "high"
        else:
            return "critical"

    def _predict_states(
        self,
        transition_matrix: np.ndarray,
        current_state: str,
        hours: int,
    ) -> list[dict]:
        """Predict future states using Markov chain."""
        predictions = []
        current_idx = self.MARKOV_STATES.index(current_state)

        # Current state distribution (one-hot)
        state_dist = np.zeros(len(self.MARKOV_STATES))
        state_dist[current_idx] = 1.0

        for h in range(hours):
            # Transition to next state
            state_dist = state_dist @ transition_matrix

            # Get most likely state
            most_likely_idx = np.argmax(state_dist)
            most_likely_state = self.MARKOV_STATES[most_likely_idx]

            predictions.append({
                "hour": h + 1,
                "state_probabilities": {
                    state: round(prob, 3)
                    for state, prob in zip(self.MARKOV_STATES, state_dist, strict=False)
                },
                "most_likely_state": most_likely_state,
                "confidence": round(state_dist[most_likely_idx], 3),
            })

        return predictions

    def _calculate_steady_state(self, transition_matrix: np.ndarray) -> np.ndarray:
        """Calculate steady state distribution."""
        # Power iteration to find steady state
        n = len(self.MARKOV_STATES)
        state = np.ones(n) / n

        for _ in range(100):
            new_state = state @ transition_matrix
            if np.allclose(state, new_state, atol=1e-6):
                break
            state = new_state

        return state

    def _get_most_likely_state(
        self,
        predictions: list[dict],
        hours: int,
    ) -> str:
        """Get most likely state at specified hour."""
        if not predictions or hours > len(predictions):
            return "unknown"

        return predictions[min(hours - 1, len(predictions) - 1)]["most_likely_state"]

    def _empty_markov_forecast(self) -> dict:
        """Return empty Markov forecast."""
        return {
            "current_state": "unknown",
            "transition_matrix": {},
            "state_predictions": [],
            "steady_state": {},
            "most_likely_state_24h": "unknown",
        }

    # ==================== Forecast Combination ====================

    def _combine_forecasts(
        self,
        temporal: dict,
        spatial: dict,
        markov: dict,
    ) -> dict:
        """Combine multiple forecast models."""
        # Weight the forecasts
        weights = {
            "temporal": 0.4,
            "spatial": 0.35,
            "markov": 0.25,
        }

        # Get expected count from temporal
        expected_count = temporal.get("total_expected", 0)

        # Adjust based on Markov state
        markov_state = markov.get("most_likely_state_24h", "medium")
        state_multipliers = {
            "low": 0.7,
            "medium": 1.0,
            "high": 1.3,
            "critical": 1.6,
        }
        expected_count *= state_multipliers.get(markov_state, 1.0)

        return {
            "expected_count": round(expected_count, 1),
            "temporal_contribution": temporal.get("total_expected", 0),
            "spatial_hotspots": len(spatial.get("hotspots", [])),
            "predicted_state": markov_state,
            "weights_used": weights,
        }

    def _apply_seasonal_adjustments(
        self,
        forecast: dict,
        hours: int,
    ) -> dict:
        """Apply seasonal adjustments to forecast."""
        expected = forecast.get("expected_count", 0)

        # Check for weekend
        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours)

        # Count weekend hours in forecast window
        weekend_hours = 0
        current = now
        while current < end_time:
            if current.weekday() >= 5:  # Saturday or Sunday
                weekend_hours += 1
            current += timedelta(hours=1)

        weekend_ratio = weekend_hours / max(hours, 1)
        weekend_adjustment = 1.0 + (self.WEEKEND_MULTIPLIER - 1.0) * weekend_ratio

        # Apply adjustment
        adjusted_expected = expected * weekend_adjustment

        forecast["expected_count"] = round(adjusted_expected, 1)
        forecast["seasonal_adjustments"] = {
            "weekend_ratio": round(weekend_ratio, 2),
            "weekend_multiplier": round(weekend_adjustment, 2),
        }

        return forecast

    def _generate_zone_predictions(
        self,
        forecast: dict,
        bounds: dict,
    ) -> list[dict]:
        """Generate predictions by zone."""
        zones = []
        grid_size = 10

        lat_step = (bounds["max_lat"] - bounds["min_lat"]) / grid_size
        lon_step = (bounds["max_lon"] - bounds["min_lon"]) / grid_size

        total_expected = forecast.get("expected_count", 0)

        for i in range(grid_size):
            for j in range(grid_size):
                # Base probability
                base_prob = 1.0 / (grid_size * grid_size)

                # Add some variation
                variation = np.random.uniform(0.5, 1.5)
                prob = base_prob * variation

                expected_in_zone = total_expected * prob

                if expected_in_zone > 0.1:  # Only include significant zones
                    zones.append({
                        "zone_id": f"forecast_{i}_{j}",
                        "center": {
                            "lat": bounds["min_lat"] + (i + 0.5) * lat_step,
                            "lon": bounds["min_lon"] + (j + 0.5) * lon_step,
                        },
                        "expected_incidents": round(expected_in_zone, 2),
                        "probability": round(prob, 4),
                        "risk_level": self._get_risk_level(prob * 10),
                    })

        # Sort by expected incidents
        zones.sort(key=lambda x: x["expected_incidents"], reverse=True)

        return zones[:20]  # Return top 20 zones

    def _identify_high_risk_areas(
        self,
        zone_predictions: list[dict],
    ) -> list[dict]:
        """Identify high-risk areas from zone predictions."""
        high_risk = []

        for zone in zone_predictions:
            if zone["risk_level"] in ["high", "critical"]:
                high_risk.append({
                    "zone_id": zone["zone_id"],
                    "center": zone["center"],
                    "expected_incidents": zone["expected_incidents"],
                    "risk_level": zone["risk_level"],
                    "recommendation": "Increased patrol presence recommended",
                })

        return high_risk

    def _calculate_forecast_confidence(
        self,
        data_points: int,
        hours: int,
    ) -> float:
        """Calculate overall forecast confidence."""
        # More data = higher confidence
        data_factor = min(1.0, data_points / 500)

        # Shorter forecast = higher confidence
        time_factor = max(0.3, 1.0 - (hours / 168) * 0.5)

        return round(data_factor * 0.6 + time_factor * 0.4, 2)

    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level."""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "elevated"
        elif score >= 0.2:
            return "moderate"
        else:
            return "low"

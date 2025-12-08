"use client";

/**
 * Forecast Panel Component
 *
 * Displays tactical forecasts including:
 * - 24-hour predictions
 * - 7-day forecasts
 * - Crime type forecasts
 * - Gunfire predictions
 * - Vehicle recurrence forecasts
 */

import { useState, useEffect, useCallback } from "react";

interface ForecastData {
  forecast_window: {
    start: string;
    end: string;
    hours: number;
  };
  forecast_type: string;
  predictions: {
    temporal: {
      trend: number;
      trend_direction: string;
      peak_hours: number[];
      peak_days: string[];
    };
    spatial: {
      hotspots: Hotspot[];
      concentration_index: number;
    };
    markov: {
      current_state: string;
      predicted_states: { hour: number; state: string; probability: number }[];
      steady_state: Record<string, number>;
    };
  };
  zone_predictions: ZonePrediction[];
  high_risk_areas: HighRiskArea[];
  expected_incidents: number;
  confidence: number;
  model_info: {
    models_used: string[];
    data_points: number;
    last_updated: string;
  };
  generated_at: string;
}

interface Hotspot {
  lat: number;
  lon: number;
  intensity: number;
  radius: number;
}

interface ZonePrediction {
  zone_id: string;
  predicted_incidents: number;
  risk_change: number;
  confidence: number;
}

interface HighRiskArea {
  zone_id: string;
  risk_score: number;
  predicted_activity: string;
  confidence: number;
}

type ForecastType = "all" | "crime" | "gunfire" | "vehicles";
type TimeWindow = "24h" | "72h" | "7d";

export function ForecastPanel() {
  const [forecastType, setForecastType] = useState<ForecastType>("all");
  const [timeWindow, setTimeWindow] = useState<TimeWindow>("24h");
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const hours =
        timeWindow === "24h" ? 24 : timeWindow === "72h" ? 72 : 168;
      const response = await fetch(
        `/api/tactical/forecast?hours=${hours}&type=${forecastType}`
      );
      if (!response.ok) throw new Error("Failed to fetch forecast");
      const data = await response.json();
      setForecast(data);
    } catch (err) {
      console.error("Failed to fetch forecast:", err);
      setError(err instanceof Error ? err.message : "Failed to load forecast");
      setForecast(generateMockForecast(forecastType, timeWindow));
    } finally {
      setLoading(false);
    }
  }, [forecastType, timeWindow]);

  useEffect(() => {
    fetchForecast();
  }, [fetchForecast]);

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-2">
            <select
              value={forecastType}
              onChange={(e) => setForecastType(e.target.value as ForecastType)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            >
              <option value="all">All Activity</option>
              <option value="crime">Crime</option>
              <option value="gunfire">Gunfire</option>
              <option value="vehicles">Vehicles</option>
            </select>
            <select
              value={timeWindow}
              onChange={(e) => setTimeWindow(e.target.value as TimeWindow)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            >
              <option value="24h">24 Hours</option>
              <option value="72h">72 Hours</option>
              <option value="7d">7 Days</option>
            </select>
          </div>
          <button
            onClick={fetchForecast}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50"
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded p-3 text-red-400">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-gray-800 rounded-lg" />
          <div className="h-64 bg-gray-800 rounded-lg" />
        </div>
      )}

      {/* Forecast content */}
      {!loading && forecast && (
        <>
          {/* Summary */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="text-lg font-semibold mb-4">Forecast Summary</h2>
            <div className="grid grid-cols-4 gap-4">
              <SummaryCard
                label="Expected Incidents"
                value={forecast.expected_incidents.toFixed(1)}
                subtext={`Next ${forecast.forecast_window.hours}h`}
                color="blue"
              />
              <SummaryCard
                label="Confidence"
                value={`${(forecast.confidence * 100).toFixed(0)}%`}
                subtext="Model confidence"
                color="green"
              />
              <SummaryCard
                label="Trend"
                value={`${forecast.predictions.temporal.trend > 0 ? "+" : ""}${(forecast.predictions.temporal.trend * 100).toFixed(0)}%`}
                subtext={forecast.predictions.temporal.trend_direction}
                color={
                  forecast.predictions.temporal.trend > 0 ? "red" : "green"
                }
              />
              <SummaryCard
                label="High Risk Areas"
                value={forecast.high_risk_areas.length.toString()}
                subtext="Zones identified"
                color="orange"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Temporal predictions */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Temporal Patterns</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm text-gray-400 mb-2">Peak Hours</h4>
                  <div className="flex gap-2">
                    {forecast.predictions.temporal.peak_hours.map((hour) => (
                      <span
                        key={hour}
                        className="px-3 py-1 bg-orange-900/50 text-orange-400 rounded"
                      >
                        {hour}:00
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm text-gray-400 mb-2">Peak Days</h4>
                  <div className="flex gap-2">
                    {forecast.predictions.temporal.peak_days.map((day) => (
                      <span
                        key={day}
                        className="px-3 py-1 bg-blue-900/50 text-blue-400 rounded capitalize"
                      >
                        {day}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Markov predictions */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">State Predictions</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm text-gray-400 mb-2">Current State</h4>
                  <StateIndicator
                    state={forecast.predictions.markov.current_state}
                  />
                </div>
                <div>
                  <h4 className="text-sm text-gray-400 mb-2">
                    Predicted States
                  </h4>
                  <div className="space-y-1">
                    {forecast.predictions.markov.predicted_states
                      .slice(0, 6)
                      .map((ps) => (
                        <div
                          key={ps.hour}
                          className="flex justify-between text-sm"
                        >
                          <span className="text-gray-400">+{ps.hour}h</span>
                          <StateIndicator state={ps.state} small />
                          <span className="text-gray-500">
                            {(ps.probability * 100).toFixed(0)}%
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Spatial predictions */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Spatial Predictions</h3>
            <div className="grid grid-cols-2 gap-6">
              {/* Hotspots */}
              <div>
                <h4 className="text-sm text-gray-400 mb-3">
                  Predicted Hotspots ({forecast.predictions.spatial.hotspots.length})
                </h4>
                <div className="space-y-2">
                  {forecast.predictions.spatial.hotspots
                    .slice(0, 5)
                    .map((hotspot, idx) => (
                      <div
                        key={idx}
                        className="flex justify-between items-center p-2 bg-gray-700 rounded"
                      >
                        <span className="font-mono text-sm">
                          {hotspot.lat.toFixed(4)}, {hotspot.lon.toFixed(4)}
                        </span>
                        <span
                          className={`text-sm ${
                            hotspot.intensity >= 0.8
                              ? "text-red-400"
                              : hotspot.intensity >= 0.6
                                ? "text-orange-400"
                                : "text-yellow-400"
                          }`}
                        >
                          {(hotspot.intensity * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                </div>
              </div>

              {/* High risk areas */}
              <div>
                <h4 className="text-sm text-gray-400 mb-3">High Risk Areas</h4>
                <div className="space-y-2">
                  {forecast.high_risk_areas.slice(0, 5).map((area) => (
                    <div
                      key={area.zone_id}
                      className="flex justify-between items-center p-2 bg-gray-700 rounded"
                    >
                      <div>
                        <span className="font-medium">{area.zone_id}</span>
                        <span className="text-xs text-gray-400 ml-2">
                          {area.predicted_activity}
                        </span>
                      </div>
                      <span
                        className={`text-sm ${
                          area.risk_score >= 0.8
                            ? "text-red-400"
                            : area.risk_score >= 0.6
                              ? "text-orange-400"
                              : "text-yellow-400"
                        }`}
                      >
                        {(area.risk_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Zone predictions */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Zone Predictions</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-gray-700">
                    <th className="pb-2 pr-4">Zone</th>
                    <th className="pb-2 pr-4">Predicted Incidents</th>
                    <th className="pb-2 pr-4">Risk Change</th>
                    <th className="pb-2">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {forecast.zone_predictions.slice(0, 10).map((zp) => (
                    <tr key={zp.zone_id} className="border-b border-gray-700/50">
                      <td className="py-2 pr-4 font-medium">{zp.zone_id}</td>
                      <td className="py-2 pr-4">
                        {zp.predicted_incidents.toFixed(1)}
                      </td>
                      <td className="py-2 pr-4">
                        <span
                          className={
                            zp.risk_change > 0
                              ? "text-red-400"
                              : zp.risk_change < 0
                                ? "text-green-400"
                                : "text-gray-400"
                          }
                        >
                          {zp.risk_change > 0 ? "+" : ""}
                          {(zp.risk_change * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="py-2">{(zp.confidence * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Model info */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold mb-2">Model Information</h3>
            <div className="flex gap-6 text-sm text-gray-400">
              <span>
                Models: {forecast.model_info.models_used.join(", ")}
              </span>
              <span>Data points: {forecast.model_info.data_points}</span>
              <span>
                Updated:{" "}
                {new Date(forecast.model_info.last_updated).toLocaleString()}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Helper components
function SummaryCard({
  label,
  value,
  subtext,
  color,
}: {
  label: string;
  value: string;
  subtext: string;
  color: "blue" | "green" | "red" | "orange";
}) {
  const colors = {
    blue: "border-blue-700 text-blue-400",
    green: "border-green-700 text-green-400",
    red: "border-red-700 text-red-400",
    orange: "border-orange-700 text-orange-400",
  };

  return (
    <div className={`p-4 bg-gray-700/50 rounded border-l-4 ${colors[color]}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm text-gray-300">{label}</div>
      <div className="text-xs text-gray-500">{subtext}</div>
    </div>
  );
}

function StateIndicator({ state, small = false }: { state: string; small?: boolean }) {
  const stateColors: Record<string, string> = {
    low: "bg-green-900/50 text-green-400",
    medium: "bg-yellow-900/50 text-yellow-400",
    high: "bg-orange-900/50 text-orange-400",
    critical: "bg-red-900/50 text-red-400",
  };

  return (
    <span
      className={`px-2 py-0.5 rounded capitalize ${small ? "text-xs" : "text-sm"} ${stateColors[state] || stateColors.medium}`}
    >
      {state}
    </span>
  );
}

// Mock data generator
function generateMockForecast(
  type: ForecastType,
  window: TimeWindow
): ForecastData {
  const hours = window === "24h" ? 24 : window === "72h" ? 72 : 168;
  const now = new Date();

  return {
    forecast_window: {
      start: now.toISOString(),
      end: new Date(now.getTime() + hours * 60 * 60 * 1000).toISOString(),
      hours,
    },
    forecast_type: type,
    predictions: {
      temporal: {
        trend: 0.15,
        trend_direction: "increasing",
        peak_hours: [22, 23, 0, 1],
        peak_days: ["friday", "saturday"],
      },
      spatial: {
        hotspots: [
          { lat: 33.45, lon: -112.07, intensity: 0.85, radius: 0.02 },
          { lat: 33.42, lon: -112.05, intensity: 0.72, radius: 0.015 },
          { lat: 33.48, lon: -112.10, intensity: 0.65, radius: 0.018 },
        ],
        concentration_index: 0.68,
      },
      markov: {
        current_state: "medium",
        predicted_states: [
          { hour: 1, state: "medium", probability: 0.6 },
          { hour: 2, state: "high", probability: 0.55 },
          { hour: 4, state: "high", probability: 0.7 },
          { hour: 6, state: "medium", probability: 0.5 },
          { hour: 12, state: "low", probability: 0.45 },
          { hour: 24, state: "medium", probability: 0.5 },
        ],
        steady_state: { low: 0.3, medium: 0.4, high: 0.25, critical: 0.05 },
      },
    },
    zone_predictions: [
      {
        zone_id: "micro_5_12",
        predicted_incidents: 3.5,
        risk_change: 0.2,
        confidence: 0.78,
      },
      {
        zone_id: "micro_3_8",
        predicted_incidents: 2.8,
        risk_change: 0.1,
        confidence: 0.72,
      },
      {
        zone_id: "micro_7_15",
        predicted_incidents: 2.2,
        risk_change: -0.05,
        confidence: 0.68,
      },
      {
        zone_id: "micro_2_5",
        predicted_incidents: 1.8,
        risk_change: 0.15,
        confidence: 0.65,
      },
      {
        zone_id: "micro_9_11",
        predicted_incidents: 1.5,
        risk_change: -0.1,
        confidence: 0.62,
      },
    ],
    high_risk_areas: [
      {
        zone_id: "micro_5_12",
        risk_score: 0.85,
        predicted_activity: "high",
        confidence: 0.78,
      },
      {
        zone_id: "micro_3_8",
        risk_score: 0.72,
        predicted_activity: "elevated",
        confidence: 0.72,
      },
      {
        zone_id: "micro_7_15",
        risk_score: 0.65,
        predicted_activity: "elevated",
        confidence: 0.68,
      },
    ],
    expected_incidents: 12.5,
    confidence: 0.75,
    model_info: {
      models_used: ["temporal_arima", "spatial_kde", "markov_chain"],
      data_points: 1250,
      last_updated: now.toISOString(),
    },
    generated_at: now.toISOString(),
  };
}

"use client";

import React, { useState, useEffect } from "react";

interface HazardPrediction {
  prediction_id: string;
  hazard_type: string;
  threat_level: number;
  threat_level_name: string;
  confidence_score: number;
  time_to_impact_hours: number;
  affected_zones: string[];
  affected_population: number;
  recommended_actions: string[];
  agencies_required: string[];
}

interface ActiveHazard {
  hazard_id: string;
  hazard_type: string;
  threat_level: number;
  affected_zones: string[];
  time_to_impact_hours: number;
  status: string;
}

export default function DisasterPredictionDashboard() {
  const [activeHazards, setActiveHazards] = useState<ActiveHazard[]>([]);
  const [selectedHazardType, setSelectedHazardType] = useState("hurricane");
  const [prediction, setPrediction] = useState<HazardPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [predicting, setPredicting] = useState(false);

  const hazardTypes = [
    { value: "hurricane", label: "Hurricane", icon: "🌀" },
    { value: "tornado", label: "Tornado", icon: "🌪️" },
    { value: "flooding", label: "Flooding", icon: "🌊" },
    { value: "storm_surge", label: "Storm Surge", icon: "🌊" },
    { value: "urban_fire", label: "Urban Fire", icon: "🔥" },
    { value: "hazmat_release", label: "Hazmat Release", icon: "☢️" },
    { value: "bridge_collapse", label: "Bridge Collapse", icon: "🌉" },
    { value: "power_grid_failure", label: "Power Grid Failure", icon: "⚡" },
  ];

  useEffect(() => {
    fetchActiveHazards();
    const interval = setInterval(fetchActiveHazards, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchActiveHazards = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/emergency-ai/hazards");
      if (response.ok) {
        const data = await response.json();
        setActiveHazards(data.active_hazards || []);
      }
    } catch (error) {
      console.error("Failed to fetch active hazards:", error);
    } finally {
      setLoading(false);
    }
  };

  const runPrediction = async () => {
    try {
      setPredicting(true);
      const response = await fetch("/api/emergency-ai/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hazard_type: selectedHazardType,
          noaa_data: {
            wind_speed_mph: 75,
            rainfall_inches: 6,
            pressure_mb: 985,
          },
          nhc_data: {
            storm_name: "Test Storm",
            category: 1,
            storm_surge_feet: 4,
            movement_speed_mph: 12,
          },
          origin_zone: "Zone_A",
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setPrediction(data);
      }
    } catch (error) {
      console.error("Failed to run prediction:", error);
    } finally {
      setPredicting(false);
    }
  };

  const getThreatLevelColor = (level: number) => {
    switch (level) {
      case 1:
        return "bg-green-500";
      case 2:
        return "bg-blue-500";
      case 3:
        return "bg-yellow-500";
      case 4:
        return "bg-orange-500";
      case 5:
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Storm Track & Hazard Map</h2>
          <div className="bg-gray-700 rounded-lg h-96 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <p className="text-4xl mb-2">🗺️</p>
              <p>Interactive Hazard Map</p>
              <p className="text-sm">NOAA/NHC Storm Track Overlay</p>
              <p className="text-sm">Flood Prediction Zones</p>
              <p className="text-sm">Fire Spread Models</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Active Hazards</h2>
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : activeHazards.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <p className="text-2xl mb-2">✓</p>
              <p>No active hazards</p>
            </div>
          ) : (
            <div className="space-y-3">
              {activeHazards.map((hazard) => (
                <div
                  key={hazard.hazard_id}
                  className="bg-gray-700 rounded-lg p-3"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium capitalize">
                      {hazard.hazard_type.replace("_", " ")}
                    </span>
                    <span
                      className={`px-2 py-1 rounded text-xs ${getThreatLevelColor(
                        hazard.threat_level
                      )}`}
                    >
                      Level {hazard.threat_level}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400">
                    Zones: {hazard.affected_zones.join(", ")}
                  </p>
                  <p className="text-sm text-gray-400">
                    Impact: {hazard.time_to_impact_hours}h
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Run Hazard Prediction</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Hazard Type
              </label>
              <select
                value={selectedHazardType}
                onChange={(e) => setSelectedHazardType(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
              >
                {hazardTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.icon} {type.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={runPrediction}
              disabled={predicting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {predicting ? "Running Prediction..." : "Run Prediction Model"}
            </button>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Prediction Results</h2>
          {prediction ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Threat Level</span>
                <span
                  className={`px-3 py-1 rounded ${getThreatLevelColor(
                    prediction.threat_level
                  )}`}
                >
                  {prediction.threat_level_name}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Confidence</span>
                <span>{(prediction.confidence_score * 100).toFixed(1)}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Time to Impact</span>
                <span>{prediction.time_to_impact_hours.toFixed(1)} hours</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Affected Population</span>
                <span>{prediction.affected_population.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-gray-400 block mb-2">Affected Zones</span>
                <div className="flex flex-wrap gap-2">
                  {prediction.affected_zones.map((zone) => (
                    <span
                      key={zone}
                      className="bg-gray-700 px-2 py-1 rounded text-sm"
                    >
                      {zone}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <span className="text-gray-400 block mb-2">
                  Recommended Actions
                </span>
                <ul className="text-sm space-y-1">
                  {prediction.recommended_actions.map((action, idx) => (
                    <li key={idx} className="text-yellow-400">
                      • {action}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <p>Run a prediction to see results</p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Hazard Severity Timeline</h2>
        <div className="bg-gray-700 rounded-lg h-48 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <p>24-Hour Hazard Severity Forecast</p>
            <p className="text-sm">Timeline visualization of predicted hazard intensity</p>
          </div>
        </div>
      </div>
    </div>
  );
}

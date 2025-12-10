"use client";

import { useState, useEffect } from "react";

interface TrafficPrediction {
  segment: string;
  congestion: string;
  speed_mph: number;
  crash_risk: number;
}

interface CrimePrediction {
  timestamp: string;
  time_window_hours: number;
  displacement_zones: Array<{
    zone_id: string;
    zone_name: string;
    base_risk: number;
    predicted_risk: number;
    risk_change: number;
  }>;
  risk_increase_areas: Array<{
    zone_id: string;
    zone_name: string;
    increase_percent: number;
  }>;
  factors: string[];
  patrol_recommendations: Array<{
    zone_id: string;
    action: string;
    recommended_units: number;
    priority: string;
  }>;
  confidence: string;
}

interface InfrastructurePrediction {
  element_id: string;
  element_name: string;
  type: string;
  risk_level: string;
  failure_probability: number;
  factors: string[];
  actions: string[];
}

interface PopulationPrediction {
  timestamp: string;
  area_predictions: Array<{
    zone_id: string;
    zone_name: string;
    base_population: number;
    predicted_population: number;
    change_percent: number;
  }>;
  peak_locations: Array<{
    zone_id: string;
    zone_name: string;
    predicted_density: number;
  }>;
  peak_times: string[];
  special_events: Array<{
    event_id: string;
    name: string;
    expected_attendance: number;
  }>;
  traffic_impact: {
    congestion_increase_percent: number;
    affected_roads: string[];
  };
}

type PredictionType = "traffic" | "crime" | "infrastructure" | "population";

export default function PredictionConsole() {
  const [predictionType, setPredictionType] = useState<PredictionType>("traffic");
  const [hoursAhead, setHoursAhead] = useState(24);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [trafficPredictions, setTrafficPredictions] = useState<TrafficPrediction[] | null>(null);
  const [crimePrediction, setCrimePrediction] = useState<CrimePrediction | null>(null);
  const [infraPredictions, setInfraPredictions] = useState<InfrastructurePrediction[] | null>(null);
  const [populationPrediction, setPopulationPrediction] = useState<PopulationPrediction | null>(null);

  useEffect(() => {
    fetchPredictions();
  }, [predictionType, hoursAhead]);

  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let endpoint = "";
      switch (predictionType) {
        case "traffic":
          endpoint = `/api/citybrain/city/predictions/traffic?hours_ahead=${hoursAhead}`;
          break;
        case "crime":
          endpoint = `/api/citybrain/city/predictions/crime?hours_ahead=${hoursAhead}`;
          break;
        case "infrastructure":
          endpoint = "/api/citybrain/city/predictions/infrastructure";
          break;
        case "population":
          endpoint = `/api/citybrain/city/predictions/population?hours_ahead=${hoursAhead}`;
          break;
      }
      
      const response = await fetch(endpoint);
      if (!response.ok) throw new Error("Failed to fetch predictions");
      const data = await response.json();
      
      switch (predictionType) {
        case "traffic":
          setTrafficPredictions(data.predictions);
          break;
        case "crime":
          setCrimePrediction(data.prediction);
          break;
        case "infrastructure":
          setInfraPredictions(data.predictions);
          break;
        case "population":
          setPopulationPrediction(data.prediction);
          break;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const getCongestionColor = (level: string) => {
    switch (level) {
      case "free_flow": return "text-green-400";
      case "light": return "text-green-300";
      case "moderate": return "text-yellow-400";
      case "heavy": return "text-orange-400";
      case "gridlock": return "text-red-400";
      default: return "text-gray-400";
    }
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "minimal": return "text-green-400";
      case "low": return "text-green-300";
      case "moderate": return "text-yellow-400";
      case "high": return "text-orange-400";
      case "severe": return "text-red-400";
      case "extreme": return "text-red-600";
      default: return "text-gray-400";
    }
  };

  const getRiskBg = (level: string) => {
    switch (level.toLowerCase()) {
      case "minimal": return "bg-green-500/20";
      case "low": return "bg-green-500/20";
      case "moderate": return "bg-yellow-500/20";
      case "high": return "bg-orange-500/20";
      case "severe": return "bg-red-500/20";
      case "extreme": return "bg-red-600/20";
      default: return "bg-gray-500/20";
    }
  };

  const predictionTypes: { id: PredictionType; label: string; icon: string }[] = [
    { id: "traffic", label: "Traffic Flow", icon: "🚗" },
    { id: "crime", label: "Crime Displacement", icon: "🚨" },
    { id: "infrastructure", label: "Infrastructure Risk", icon: "🏗️" },
    { id: "population", label: "Population Movement", icon: "👥" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Prediction Console</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">Forecast:</span>
            <select
              value={hoursAhead}
              onChange={(e) => setHoursAhead(parseInt(e.target.value))}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="6">6 hours</option>
              <option value="12">12 hours</option>
              <option value="24">24 hours</option>
              <option value="48">48 hours</option>
              <option value="72">72 hours</option>
            </select>
          </div>
          <button
            onClick={fetchPredictions}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="flex space-x-2 overflow-x-auto pb-2">
        {predictionTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => setPredictionType(type.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg whitespace-nowrap ${
              predictionType === type.id
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            <span>{type.icon}</span>
            <span className="text-sm">{type.label}</span>
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
        </div>
      ) : error ? (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
          <p className="text-red-400">Error: {error}</p>
        </div>
      ) : (
        <>
          {predictionType === "traffic" && trafficPredictions && (
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="p-4 border-b border-gray-700">
                <h3 className="font-semibold">Traffic Flow Predictions</h3>
                <p className="text-sm text-gray-400">Next {hoursAhead} hours</p>
              </div>
              <div className="divide-y divide-gray-700">
                {trafficPredictions.map((pred, idx) => (
                  <div key={idx} className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{pred.segment}</p>
                        <p className={`text-sm capitalize ${getCongestionColor(pred.congestion)}`}>
                          {pred.congestion.replace(/_/g, " ")}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-white">{pred.speed_mph.toFixed(0)} mph</p>
                        <p className="text-xs text-gray-400">
                          Crash Risk: {(pred.crash_risk * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {predictionType === "crime" && crimePrediction && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h3 className="font-semibold mb-3">Risk Increase Areas</h3>
                  <div className="space-y-2">
                    {crimePrediction.risk_increase_areas.map((area) => (
                      <div key={area.zone_id} className="flex items-center justify-between bg-red-500/10 rounded p-2">
                        <span className="text-sm">{area.zone_name}</span>
                        <span className="text-sm text-red-400">+{area.increase_percent.toFixed(0)}%</span>
                      </div>
                    ))}
                    {crimePrediction.risk_increase_areas.length === 0 && (
                      <p className="text-sm text-gray-500">No significant risk increases</p>
                    )}
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h3 className="font-semibold mb-3">Contributing Factors</h3>
                  <div className="flex flex-wrap gap-2">
                    {crimePrediction.factors.map((factor, idx) => (
                      <span key={idx} className="px-2 py-1 bg-gray-700 rounded text-xs capitalize">
                        {factor.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 className="font-semibold mb-3">Patrol Recommendations</h3>
                <div className="space-y-2">
                  {crimePrediction.patrol_recommendations.map((rec, idx) => (
                    <div key={idx} className="flex items-center justify-between bg-gray-700/50 rounded p-3">
                      <div>
                        <p className="text-sm font-medium capitalize">{rec.action.replace(/_/g, " ")}</p>
                        <p className="text-xs text-gray-400">Zone: {rec.zone_id}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-white">{rec.recommended_units > 0 ? "+" : ""}{rec.recommended_units} units</p>
                        <p className={`text-xs capitalize ${rec.priority === "high" ? "text-red-400" : "text-gray-400"}`}>
                          {rec.priority} priority
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {predictionType === "infrastructure" && infraPredictions && (
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="p-4 border-b border-gray-700">
                <h3 className="font-semibold">Infrastructure Risk Assessment</h3>
              </div>
              <div className="divide-y divide-gray-700">
                {infraPredictions.map((pred) => (
                  <div key={pred.element_id} className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium">{pred.element_name}</p>
                        <p className="text-sm text-gray-400 capitalize">{pred.type.replace(/_/g, " ")}</p>
                        {pred.factors.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {pred.factors.map((factor, idx) => (
                              <span key={idx} className="px-2 py-0.5 bg-gray-700 rounded text-xs">
                                {factor.replace(/_/g, " ")}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 rounded text-xs font-medium capitalize ${getRiskBg(pred.risk_level)} ${getRiskColor(pred.risk_level)}`}>
                          {pred.risk_level}
                        </span>
                        <p className="text-xs text-gray-400 mt-1">
                          {(pred.failure_probability * 100).toFixed(1)}% probability
                        </p>
                      </div>
                    </div>
                    {pred.actions.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-700">
                        <p className="text-xs text-gray-400 mb-1">Recommended Actions:</p>
                        <div className="flex flex-wrap gap-1">
                          {pred.actions.map((action, idx) => (
                            <span key={idx} className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded text-xs">
                              {action.replace(/_/g, " ")}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {predictionType === "population" && populationPrediction && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h3 className="font-semibold mb-3">Peak Density Locations</h3>
                  <div className="space-y-2">
                    {populationPrediction.peak_locations.map((loc) => (
                      <div key={loc.zone_id} className="flex items-center justify-between bg-gray-700/50 rounded p-2">
                        <span className="text-sm">{loc.zone_name}</span>
                        <span className="text-sm text-white">{loc.predicted_density.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h3 className="font-semibold mb-3">Traffic Impact</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Congestion Increase</span>
                      <span className="text-sm text-orange-400">
                        +{populationPrediction.traffic_impact.congestion_increase_percent}%
                      </span>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Affected Roads:</p>
                      <div className="flex flex-wrap gap-1">
                        {populationPrediction.traffic_impact.affected_roads.map((road, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-gray-700 rounded text-xs">
                            {road}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 className="font-semibold mb-3">Area Population Predictions</h3>
                <div className="space-y-2">
                  {populationPrediction.area_predictions.map((area) => (
                    <div key={area.zone_id} className="flex items-center justify-between bg-gray-700/50 rounded p-3">
                      <div>
                        <p className="text-sm font-medium">{area.zone_name}</p>
                        <p className="text-xs text-gray-400">
                          Base: {area.base_population.toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-white">{area.predicted_population.toLocaleString()}</p>
                        <p className={`text-xs ${area.change_percent > 0 ? "text-green-400" : "text-red-400"}`}>
                          {area.change_percent > 0 ? "+" : ""}{area.change_percent.toFixed(0)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

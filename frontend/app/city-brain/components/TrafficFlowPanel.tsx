"use client";

import { useState, useEffect } from "react";

interface TrafficIncident {
  incident_id: string;
  incident_type: string;
  location: string;
  severity: string;
  description: string;
  reported_at: string;
  estimated_clearance: string | null;
}

interface TrafficCondition {
  segment_id: string;
  road_name: string;
  congestion_level: string;
  current_speed_mph: number;
  free_flow_speed_mph: number;
  travel_time_minutes: number;
}

interface TrafficData {
  incidents: TrafficIncident[];
  conditions: TrafficCondition[];
  summary: {
    total_incidents: number;
    congested_segments: number;
    total_segments: number;
  };
}

export default function TrafficFlowPanel() {
  const [trafficData, setTrafficData] = useState<TrafficData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<"conditions" | "incidents">("conditions");

  useEffect(() => {
    fetchTrafficData();
    const interval = setInterval(fetchTrafficData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchTrafficData = async () => {
    try {
      const response = await fetch("/api/citybrain/city/traffic");
      if (!response.ok) throw new Error("Failed to fetch traffic data");
      const data = await response.json();
      setTrafficData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const getCongestionColor = (level: string) => {
    switch (level) {
      case "free_flow": return "bg-green-500";
      case "light": return "bg-green-400";
      case "moderate": return "bg-yellow-500";
      case "heavy": return "bg-orange-500";
      case "gridlock": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getCongestionTextColor = (level: string) => {
    switch (level) {
      case "free_flow": return "text-green-400";
      case "light": return "text-green-300";
      case "moderate": return "text-yellow-400";
      case "heavy": return "text-orange-400";
      case "gridlock": return "text-red-400";
      default: return "text-gray-400";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical": return "bg-red-600";
      case "major": return "bg-orange-600";
      case "moderate": return "bg-yellow-600";
      case "minor": return "bg-blue-600";
      default: return "bg-gray-600";
    }
  };

  const getSpeedRatio = (current: number, freeFlow: number) => {
    return (current / freeFlow) * 100;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
        <p className="text-red-400">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Traffic Flow Monitor</h2>
        <div className="flex items-center space-x-4">
          <div className="flex bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setSelectedView("conditions")}
              className={`px-3 py-1 rounded text-sm ${
                selectedView === "conditions"
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Conditions
            </button>
            <button
              onClick={() => setSelectedView("incidents")}
              className={`px-3 py-1 rounded text-sm ${
                selectedView === "incidents"
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Incidents ({trafficData?.summary.total_incidents || 0})
            </button>
          </div>
          <button
            onClick={fetchTrafficData}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-sm text-gray-400">Total Segments</p>
          <p className="text-2xl font-bold text-white">
            {trafficData?.summary.total_segments || 0}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-sm text-gray-400">Congested</p>
          <p className="text-2xl font-bold text-orange-400">
            {trafficData?.summary.congested_segments || 0}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-sm text-gray-400">Active Incidents</p>
          <p className="text-2xl font-bold text-red-400">
            {trafficData?.summary.total_incidents || 0}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-sm text-gray-400">Flow Efficiency</p>
          <p className="text-2xl font-bold text-green-400">
            {trafficData?.conditions
              ? (
                  (trafficData.conditions.reduce(
                    (sum, c) => sum + c.current_speed_mph / c.free_flow_speed_mph,
                    0
                  ) /
                    trafficData.conditions.length) *
                  100
                ).toFixed(0)
              : 0}
            %
          </p>
        </div>
      </div>

      {selectedView === "conditions" ? (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold">Road Conditions</h3>
          </div>
          <div className="divide-y divide-gray-700">
            {trafficData?.conditions.map((condition) => (
              <div key={condition.segment_id} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${getCongestionColor(condition.congestion_level)}`} />
                    <span className="font-medium">{condition.road_name}</span>
                  </div>
                  <span className={`text-sm font-medium capitalize ${getCongestionTextColor(condition.congestion_level)}`}>
                    {condition.congestion_level.replace(/_/g, " ")}
                  </span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex-1">
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${getCongestionColor(condition.congestion_level)}`}
                        style={{ width: `${getSpeedRatio(condition.current_speed_mph, condition.free_flow_speed_mph)}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-gray-400">
                      {condition.current_speed_mph.toFixed(0)} / {condition.free_flow_speed_mph} mph
                    </span>
                    <span className="text-gray-400">
                      {condition.travel_time_minutes.toFixed(1)} min
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold">Active Incidents</h3>
          </div>
          <div className="divide-y divide-gray-700">
            {trafficData?.incidents && trafficData.incidents.length > 0 ? (
              trafficData.incidents.map((incident) => (
                <div key={incident.incident_id} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(incident.severity)}`}>
                        {incident.severity}
                      </div>
                      <div>
                        <p className="font-medium">{incident.incident_type}</p>
                        <p className="text-sm text-gray-400">{incident.location}</p>
                        <p className="text-sm text-gray-500 mt-1">{incident.description}</p>
                      </div>
                    </div>
                    <div className="text-right text-sm">
                      <p className="text-gray-400">
                        {new Date(incident.reported_at).toLocaleTimeString()}
                      </p>
                      {incident.estimated_clearance && (
                        <p className="text-gray-500">
                          Est. clear: {new Date(incident.estimated_clearance).toLocaleTimeString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                No active incidents
              </div>
            )}
          </div>
        </div>
      )}

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-semibold mb-4">Congestion Legend</h3>
        <div className="flex flex-wrap gap-4">
          {[
            { level: "free_flow", label: "Free Flow" },
            { level: "light", label: "Light" },
            { level: "moderate", label: "Moderate" },
            { level: "heavy", label: "Heavy" },
            { level: "gridlock", label: "Gridlock" },
          ].map((item) => (
            <div key={item.level} className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getCongestionColor(item.level)}`} />
              <span className="text-sm text-gray-400">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

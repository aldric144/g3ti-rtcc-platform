"use client";

import { useState, useEffect } from "react";

interface CityState {
  timestamp: string;
  weather: Record<string, unknown>;
  traffic: Record<string, unknown>;
  utilities: Record<string, unknown>;
  incidents: Record<string, unknown>;
  predictions: Record<string, unknown>;
  population_estimate: number;
  active_events: Array<Record<string, unknown>>;
  module_statuses: Record<string, unknown>;
  overall_health: number;
}

interface CityBrainDashboardProps {
  cityState: CityState | null;
}

interface ModuleStatus {
  name: string;
  status: string;
  health: number;
  last_update: string;
}

export default function CityBrainDashboard({ cityState }: CityBrainDashboardProps) {
  const [modules, setModules] = useState<ModuleStatus[]>([]);

  useEffect(() => {
    if (cityState?.module_statuses) {
      const moduleList = Object.entries(cityState.module_statuses).map(([name, data]) => ({
        name,
        status: (data as Record<string, unknown>).status as string || "unknown",
        health: (data as Record<string, unknown>).health as number || 0,
        last_update: (data as Record<string, unknown>).last_update as string || "",
      }));
      setModules(moduleList);
    }
  }, [cityState]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running":
      case "operational":
        return "bg-green-500";
      case "degraded":
        return "bg-yellow-500";
      case "error":
      case "offline":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getHealthColor = (health: number) => {
    if (health >= 0.9) return "text-green-400";
    if (health >= 0.7) return "text-yellow-400";
    if (health >= 0.5) return "text-orange-400";
    return "text-red-400";
  };

  if (!cityState) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-400">No city state data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-400">System Health</h3>
            <div className={`w-3 h-3 rounded-full ${cityState.overall_health >= 0.8 ? "bg-green-500" : "bg-yellow-500"}`} />
          </div>
          <p className={`text-3xl font-bold mt-2 ${getHealthColor(cityState.overall_health)}`}>
            {(cityState.overall_health * 100).toFixed(0)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">All modules operational</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-400">Population</h3>
            <span className="text-blue-400 text-xs">Live Estimate</span>
          </div>
          <p className="text-3xl font-bold mt-2 text-white">
            {cityState.population_estimate?.toLocaleString() || "N/A"}
          </p>
          <p className="text-xs text-gray-500 mt-1">Current city population</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-400">Active Events</h3>
            <span className="text-orange-400 text-xs">
              {cityState.active_events?.length || 0} active
            </span>
          </div>
          <p className="text-3xl font-bold mt-2 text-white">
            {cityState.active_events?.length || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">City events in progress</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-400">Last Update</h3>
            <span className="text-green-400 text-xs">Live</span>
          </div>
          <p className="text-lg font-bold mt-2 text-white">
            {new Date(cityState.timestamp).toLocaleTimeString()}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {new Date(cityState.timestamp).toLocaleDateString()}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Weather Conditions</h3>
          {cityState.weather ? (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Temperature</span>
                <span className="text-white">
                  {(cityState.weather as Record<string, unknown>).temperature_f || "N/A"}°F
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Humidity</span>
                <span className="text-white">
                  {(cityState.weather as Record<string, unknown>).humidity_percent || "N/A"}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Wind</span>
                <span className="text-white">
                  {(cityState.weather as Record<string, unknown>).wind_speed_mph || "N/A"} mph
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Conditions</span>
                <span className="text-white">
                  {(cityState.weather as Record<string, unknown>).conditions || "N/A"}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No weather data</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Traffic Status</h3>
          {cityState.traffic ? (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Overall</span>
                <span className={`font-medium ${
                  (cityState.traffic as Record<string, unknown>).overall_status === "normal"
                    ? "text-green-400"
                    : "text-yellow-400"
                }`}>
                  {(cityState.traffic as Record<string, unknown>).overall_status || "N/A"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Active Incidents</span>
                <span className="text-white">
                  {(cityState.traffic as Record<string, unknown>).incident_count || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Congested Roads</span>
                <span className="text-white">
                  {(cityState.traffic as Record<string, unknown>).congested_segments || 0}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No traffic data</p>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Utility Status</h3>
          {cityState.utilities ? (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Power Grid</span>
                <span className={`font-medium ${
                  (cityState.utilities as Record<string, unknown>).power_status === "normal"
                    ? "text-green-400"
                    : "text-yellow-400"
                }`}>
                  {(cityState.utilities as Record<string, unknown>).power_status || "N/A"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Water System</span>
                <span className={`font-medium ${
                  (cityState.utilities as Record<string, unknown>).water_status === "normal"
                    ? "text-green-400"
                    : "text-yellow-400"
                }`}>
                  {(cityState.utilities as Record<string, unknown>).water_status || "N/A"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Active Outages</span>
                <span className="text-white">
                  {(cityState.utilities as Record<string, unknown>).outage_count || 0}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No utility data</p>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Module Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          {modules.map((module) => (
            <div
              key={module.name}
              className="bg-gray-700/50 rounded-lg p-3 text-center"
            >
              <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${getStatusColor(module.status)}`} />
              <p className="text-xs font-medium text-white capitalize">
                {module.name.replace(/_/g, " ")}
              </p>
              <p className={`text-xs mt-1 ${getHealthColor(module.health)}`}>
                {(module.health * 100).toFixed(0)}%
              </p>
            </div>
          ))}
        </div>
      </div>

      {cityState.active_events && cityState.active_events.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Active Events</h3>
          <div className="space-y-2">
            {cityState.active_events.slice(0, 5).map((event, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-gray-700/50 rounded-lg p-3"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    event.priority === "critical" ? "bg-red-500" :
                    event.priority === "high" ? "bg-orange-500" :
                    event.priority === "medium" ? "bg-yellow-500" : "bg-blue-500"
                  }`} />
                  <div>
                    <p className="text-sm font-medium text-white">
                      {event.title as string || "Unknown Event"}
                    </p>
                    <p className="text-xs text-gray-400">
                      {event.event_type as string || "event"}
                    </p>
                  </div>
                </div>
                <span className="text-xs text-gray-400">
                  {event.timestamp ? new Date(event.timestamp as string).toLocaleTimeString() : ""}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">City Profile: Riviera Beach, FL 33404</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-gray-400">Coordinates</p>
            <p className="text-sm text-white">26.7753°N, 80.0583°W</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Area</p>
            <p className="text-sm text-white">9.76 sq mi</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">County</p>
            <p className="text-sm text-white">Palm Beach County</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">State</p>
            <p className="text-sm text-white">Florida</p>
          </div>
        </div>
      </div>
    </div>
  );
}

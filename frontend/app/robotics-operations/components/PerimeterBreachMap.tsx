"use client";

import React, { useState, useEffect } from "react";

interface SensorZone {
  zone_id: string;
  name: string;
  zone_type: string;
  bounds: { min_x: number; min_y: number; max_x: number; max_y: number };
  is_active: boolean;
  sensor_count: number;
}

interface PerimeterBreach {
  breach_id: string;
  zone_id: string;
  zone_name: string;
  severity: string;
  risk_score: number;
  breach_type: string;
  position: { x: number; y: number };
  detected_at: string;
  status: string;
  entity_count: number;
  response_dispatched: boolean;
}

interface ThermalAnomaly {
  anomaly_id: string;
  sensor_id: string;
  position: { x: number; y: number };
  temperature: number;
  signature_type: string;
  confidence: number;
  detected_at: string;
}

export default function PerimeterBreachMap() {
  const [zones, setZones] = useState<SensorZone[]>([]);
  const [breaches, setBreaches] = useState<PerimeterBreach[]>([]);
  const [thermalAnomalies, setThermalAnomalies] = useState<ThermalAnomaly[]>([]);
  const [selectedBreach, setSelectedBreach] = useState<PerimeterBreach | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [showResolved, setShowResolved] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const mockZones: SensorZone[] = [
      { zone_id: "zone-north", name: "North Perimeter", zone_type: "perimeter", bounds: { min_x: 0, min_y: 180, max_x: 200, max_y: 200 }, is_active: true, sensor_count: 8 },
      { zone_id: "zone-east", name: "East Perimeter", zone_type: "perimeter", bounds: { min_x: 180, min_y: 0, max_x: 200, max_y: 200 }, is_active: true, sensor_count: 6 },
      { zone_id: "zone-south", name: "South Perimeter", zone_type: "perimeter", bounds: { min_x: 0, min_y: 0, max_x: 200, max_y: 20 }, is_active: true, sensor_count: 8 },
      { zone_id: "zone-west", name: "West Perimeter", zone_type: "perimeter", bounds: { min_x: 0, min_y: 0, max_x: 20, max_y: 200 }, is_active: true, sensor_count: 6 },
      { zone_id: "zone-entrance", name: "Main Entrance", zone_type: "access_point", bounds: { min_x: 90, min_y: 0, max_x: 110, max_y: 10 }, is_active: true, sensor_count: 4 },
    ];

    const mockBreaches: PerimeterBreach[] = [
      {
        breach_id: "breach-001",
        zone_id: "zone-north",
        zone_name: "North Perimeter",
        severity: "high",
        risk_score: 78,
        breach_type: "intrusion",
        position: { x: 120, y: 195 },
        detected_at: new Date(Date.now() - 300000).toISOString(),
        status: "active",
        entity_count: 2,
        response_dispatched: true,
      },
      {
        breach_id: "breach-002",
        zone_id: "zone-east",
        zone_name: "East Perimeter",
        severity: "medium",
        risk_score: 52,
        breach_type: "suspicious_activity",
        position: { x: 190, y: 80 },
        detected_at: new Date(Date.now() - 600000).toISOString(),
        status: "acknowledged",
        entity_count: 1,
        response_dispatched: false,
      },
      {
        breach_id: "breach-003",
        zone_id: "zone-entrance",
        zone_name: "Main Entrance",
        severity: "low",
        risk_score: 25,
        breach_type: "loitering",
        position: { x: 100, y: 5 },
        detected_at: new Date(Date.now() - 1800000).toISOString(),
        status: "resolved",
        entity_count: 1,
        response_dispatched: false,
      },
    ];

    const mockAnomalies: ThermalAnomaly[] = [
      { anomaly_id: "thermal-001", sensor_id: "sensor-n3", position: { x: 120, y: 192 }, temperature: 37.2, signature_type: "human", confidence: 0.92, detected_at: new Date(Date.now() - 60000).toISOString() },
      { anomaly_id: "thermal-002", sensor_id: "sensor-n3", position: { x: 125, y: 193 }, temperature: 36.8, signature_type: "human", confidence: 0.88, detected_at: new Date(Date.now() - 60000).toISOString() },
    ];

    setZones(mockZones);
    setBreaches(mockBreaches);
    setThermalAnomalies(mockAnomalies);
    setIsLoading(false);
  }, []);

  const filteredBreaches = breaches.filter((breach) => {
    if (!showResolved && breach.status === "resolved") return false;
    if (filterSeverity !== "all" && breach.severity !== filterSeverity) return false;
    return true;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-600";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-red-500";
      case "acknowledged":
        return "text-yellow-500";
      case "resolved":
        return "text-green-500";
      default:
        return "text-gray-500";
    }
  };

  const getBreachTypeIcon = (type: string) => {
    switch (type) {
      case "intrusion":
        return "🚨";
      case "suspicious_activity":
        return "👁️";
      case "loitering":
        return "🚶";
      case "vehicle":
        return "🚗";
      case "fence_cut":
        return "✂️";
      default:
        return "⚠️";
    }
  };

  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-96 bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white">Perimeter Security</h2>
        <div className="flex gap-2 items-center">
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-gray-700 text-white rounded px-3 py-1 text-sm"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <label className="flex items-center gap-2 text-gray-400 text-sm">
            <input
              type="checkbox"
              checked={showResolved}
              onChange={(e) => setShowResolved(e.target.checked)}
              className="rounded"
            />
            Show Resolved
          </label>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="bg-gray-900 rounded-lg p-4 relative" style={{ height: "400px" }}>
            <div className="absolute inset-4 border-2 border-gray-700 rounded">
              {zones.map((zone) => (
                <div
                  key={zone.zone_id}
                  className={`absolute border ${zone.is_active ? "border-green-500 border-opacity-50" : "border-gray-600"}`}
                  style={{
                    left: `${zone.bounds.min_x / 2}%`,
                    top: `${(200 - zone.bounds.max_y) / 2}%`,
                    width: `${(zone.bounds.max_x - zone.bounds.min_x) / 2}%`,
                    height: `${(zone.bounds.max_y - zone.bounds.min_y) / 2}%`,
                  }}
                  title={zone.name}
                >
                  <span className="absolute -top-5 left-0 text-xs text-gray-500">{zone.name}</span>
                </div>
              ))}

              {filteredBreaches.map((breach) => (
                <div
                  key={breach.breach_id}
                  className={`absolute w-6 h-6 rounded-full flex items-center justify-center cursor-pointer transform -translate-x-1/2 -translate-y-1/2 ${
                    breach.status === "active" ? "animate-pulse" : ""
                  } ${getSeverityColor(breach.severity)}`}
                  style={{
                    left: `${breach.position.x / 2}%`,
                    top: `${(200 - breach.position.y) / 2}%`,
                  }}
                  onClick={() => setSelectedBreach(breach)}
                  title={`${breach.breach_type} - ${breach.severity}`}
                >
                  <span className="text-xs">{getBreachTypeIcon(breach.breach_type)}</span>
                </div>
              ))}

              {thermalAnomalies.map((anomaly) => (
                <div
                  key={anomaly.anomaly_id}
                  className="absolute w-3 h-3 rounded-full bg-red-400 opacity-60 transform -translate-x-1/2 -translate-y-1/2"
                  style={{
                    left: `${anomaly.position.x / 2}%`,
                    top: `${(200 - anomaly.position.y) / 2}%`,
                  }}
                  title={`Thermal: ${anomaly.temperature}°C (${anomaly.signature_type})`}
                />
              ))}
            </div>

            <div className="absolute bottom-2 left-2 flex gap-4 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-red-600"></div>
                <span className="text-gray-400">Critical</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                <span className="text-gray-400">High</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span className="text-gray-400">Medium</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span className="text-gray-400">Low</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full bg-red-400 opacity-60"></div>
                <span className="text-gray-400">Thermal</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-white font-medium mb-3">Active Breaches</h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {filteredBreaches.filter(b => b.status !== "resolved").map((breach) => (
                <div
                  key={breach.breach_id}
                  className={`bg-gray-800 rounded p-2 cursor-pointer ${
                    selectedBreach?.breach_id === breach.breach_id ? "ring-1 ring-blue-500" : ""
                  }`}
                  onClick={() => setSelectedBreach(breach)}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span>{getBreachTypeIcon(breach.breach_type)}</span>
                      <span className="text-white text-sm">{breach.zone_name}</span>
                    </div>
                    <div className={`px-2 py-0.5 rounded text-xs text-white ${getSeverityColor(breach.severity)}`}>
                      {breach.severity}
                    </div>
                  </div>
                  <div className="flex justify-between text-xs mt-1">
                    <span className={getStatusColor(breach.status)}>{breach.status}</span>
                    <span className="text-gray-400">Score: {breach.risk_score}</span>
                  </div>
                </div>
              ))}
              {filteredBreaches.filter(b => b.status !== "resolved").length === 0 && (
                <div className="text-gray-400 text-sm text-center py-4">No active breaches</div>
              )}
            </div>
          </div>

          {selectedBreach && (
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-medium mb-3">Breach Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">ID:</span>
                  <span className="text-white">{selectedBreach.breach_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Type:</span>
                  <span className="text-white capitalize">{selectedBreach.breach_type.replace("_", " ")}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Zone:</span>
                  <span className="text-white">{selectedBreach.zone_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Risk Score:</span>
                  <span className="text-white">{selectedBreach.risk_score}/100</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Entities:</span>
                  <span className="text-white">{selectedBreach.entity_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Response:</span>
                  <span className={selectedBreach.response_dispatched ? "text-green-500" : "text-yellow-500"}>
                    {selectedBreach.response_dispatched ? "Dispatched" : "Pending"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Detected:</span>
                  <span className="text-white">{new Date(selectedBreach.detected_at).toLocaleTimeString()}</span>
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                {selectedBreach.status === "active" && (
                  <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1 rounded text-sm flex-1">
                    Acknowledge
                  </button>
                )}
                {selectedBreach.status !== "resolved" && (
                  <>
                    <button className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm flex-1">
                      Resolve
                    </button>
                    {!selectedBreach.response_dispatched && (
                      <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm flex-1">
                        Dispatch
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-white font-medium mb-3">Zone Status</h3>
            <div className="space-y-2">
              {zones.map((zone) => (
                <div key={zone.zone_id} className="flex justify-between items-center text-sm">
                  <span className="text-gray-300">{zone.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">{zone.sensor_count} sensors</span>
                    <div className={`w-2 h-2 rounded-full ${zone.is_active ? "bg-green-500" : "bg-red-500"}`}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

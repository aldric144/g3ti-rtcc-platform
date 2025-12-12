"use client";

import React, { useState, useEffect } from "react";

interface SatelliteImage {
  image_id: string;
  source: string;
  capture_time: string;
  location: {
    lat: number;
    lon: number;
    region?: string;
  };
  resolution_meters: number;
  cloud_cover_percent: number;
}

interface ChangeDetection {
  detection_id: string;
  change_category: string;
  location: {
    lat: number;
    lon: number;
    region?: string;
  };
  area_sq_km: number;
  change_magnitude: number;
  confidence: string;
  description: string;
  timestamp: string;
}

interface MilitaryDetection {
  detection_id: string;
  activity_type: string;
  unit_types: string[];
  estimated_personnel: number;
  vehicle_count: number;
  aircraft_count: number;
  confidence: string;
  assessment: string;
  location: {
    lat: number;
    lon: number;
    region?: string;
  };
  timestamp: string;
}

interface SatelliteAlert {
  alert_id: string;
  alert_type: string;
  priority: number;
  title: string;
  description: string;
  location: {
    lat: number;
    lon: number;
    region?: string;
  };
  recommended_action: string;
  expires_at: string;
}

const MONITORED_LOCATIONS = [
  { name: "South China Sea", lat: 12.0, lon: 114.0, type: "maritime" },
  { name: "Taiwan Strait", lat: 24.0, lon: 119.0, type: "maritime" },
  { name: "Persian Gulf", lat: 26.5, lon: 51.0, type: "maritime" },
  { name: "Black Sea", lat: 43.5, lon: 34.0, type: "maritime" },
  { name: "Ukraine Border", lat: 50.0, lon: 36.0, type: "military" },
  { name: "Korean DMZ", lat: 38.0, lon: 127.0, type: "military" },
  { name: "Gaza", lat: 31.5, lon: 34.5, type: "conflict" },
  { name: "Amazon Basin", lat: -3.0, lon: -60.0, type: "environmental" },
];

const IMAGERY_SOURCES = [
  { id: "sentinel_2", name: "Sentinel-2", resolution: "10m" },
  { id: "landsat_8", name: "Landsat-8", resolution: "30m" },
  { id: "planet", name: "Planet", resolution: "3m" },
  { id: "maxar", name: "Maxar", resolution: "0.3m" },
  { id: "capella", name: "Capella SAR", resolution: "0.5m" },
];

export default function SatellitePanel() {
  const [selectedLocation, setSelectedLocation] = useState(MONITORED_LOCATIONS[0]);
  const [detections, setDetections] = useState<ChangeDetection[]>([]);
  const [militaryDetections, setMilitaryDetections] = useState<MilitaryDetection[]>([]);
  const [alerts, setAlerts] = useState<SatelliteAlert[]>([]);
  const [activeTab, setActiveTab] = useState<"changes" | "military" | "maritime" | "alerts">("changes");

  useEffect(() => {
    const mockDetections: ChangeDetection[] = [
      {
        detection_id: "CD-001",
        change_category: "military_activity",
        location: { lat: 50.0, lon: 36.0, region: "Ukraine Border" },
        area_sq_km: 2.5,
        change_magnitude: 0.85,
        confidence: "high",
        description: "Military activity detected (3 units)",
        timestamp: new Date().toISOString(),
      },
      {
        detection_id: "CD-002",
        change_category: "infrastructure_damaged",
        location: { lat: 31.5, lon: 34.5, region: "Gaza" },
        area_sq_km: 1.2,
        change_magnitude: 0.92,
        confidence: "very_high",
        description: "Infrastructure damage detected (severity: 92%)",
        timestamp: new Date().toISOString(),
      },
      {
        detection_id: "CD-003",
        change_category: "maritime_activity",
        location: { lat: 12.0, lon: 114.0, region: "South China Sea" },
        area_sq_km: 5.0,
        change_magnitude: 0.65,
        confidence: "medium",
        description: "Maritime activity change (8 vessels)",
        timestamp: new Date().toISOString(),
      },
      {
        detection_id: "CD-004",
        change_category: "environmental_change",
        location: { lat: -3.0, lon: -60.0, region: "Amazon Basin" },
        area_sq_km: 15.0,
        change_magnitude: 0.72,
        confidence: "high",
        description: "Environmental change detected (magnitude: 72%)",
        timestamp: new Date().toISOString(),
      },
    ];
    setDetections(mockDetections);

    const mockMilitary: MilitaryDetection[] = [
      {
        detection_id: "MA-001",
        activity_type: "deployment",
        unit_types: ["armor", "artillery", "logistics"],
        estimated_personnel: 2500,
        vehicle_count: 150,
        aircraft_count: 12,
        confidence: "high",
        assessment: "Active military deployment detected",
        location: { lat: 50.0, lon: 36.0, region: "Ukraine Border" },
        timestamp: new Date().toISOString(),
      },
      {
        detection_id: "MA-002",
        activity_type: "exercise",
        unit_types: ["infantry", "air_defense"],
        estimated_personnel: 1200,
        vehicle_count: 45,
        aircraft_count: 8,
        confidence: "medium",
        assessment: "Military exercise in progress",
        location: { lat: 38.0, lon: 127.0, region: "Korean DMZ" },
        timestamp: new Date().toISOString(),
      },
      {
        detection_id: "MA-003",
        activity_type: "buildup",
        unit_types: ["armor", "infantry", "headquarters"],
        estimated_personnel: 3500,
        vehicle_count: 200,
        aircraft_count: 20,
        confidence: "high",
        assessment: "Force buildup observed",
        location: { lat: 24.0, lon: 119.0, region: "Taiwan Strait" },
        timestamp: new Date().toISOString(),
      },
    ];
    setMilitaryDetections(mockMilitary);

    const mockAlerts: SatelliteAlert[] = [
      {
        alert_id: "SA-001",
        alert_type: "military_activity",
        priority: 4,
        title: "Military Activity Alert: Deployment",
        description: "Active military deployment detected",
        location: { lat: 50.0, lon: 36.0, region: "Ukraine Border" },
        recommended_action: "Escalate to intelligence analysts immediately",
        expires_at: new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString(),
      },
      {
        alert_id: "SA-002",
        alert_type: "infrastructure_damaged",
        priority: 3,
        title: "Satellite Alert: Infrastructure Damaged",
        description: "Infrastructure damage detected (severity: 92%)",
        location: { lat: 31.5, lon: 34.5, region: "Gaza" },
        recommended_action: "Coordinate with disaster response teams",
        expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      },
    ];
    setAlerts(mockAlerts);
  }, []);

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case "very_high": return "text-green-400";
      case "high": return "text-blue-400";
      case "medium": return "text-yellow-400";
      case "low": return "text-orange-400";
      default: return "text-gray-400";
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "military_activity": return "bg-red-500";
      case "infrastructure_damaged": return "bg-orange-500";
      case "maritime_activity": return "bg-blue-500";
      case "environmental_change": return "bg-green-500";
      case "infrastructure_new": return "bg-cyan-500";
      default: return "bg-gray-500";
    }
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 4) return "bg-red-500";
    if (priority >= 3) return "bg-orange-500";
    if (priority >= 2) return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Monitored Locations</h2>
          <div className="space-y-2">
            {MONITORED_LOCATIONS.map(location => (
              <button
                key={location.name}
                onClick={() => setSelectedLocation(location)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedLocation.name === location.name
                    ? "bg-blue-600/30 border border-blue-500"
                    : "bg-gray-700/50 hover:bg-gray-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">{location.name}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    location.type === "military" ? "bg-red-500" :
                    location.type === "maritime" ? "bg-blue-500" :
                    location.type === "conflict" ? "bg-orange-500" :
                    "bg-green-500"
                  }`}>
                    {location.type}
                  </span>
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {location.lat.toFixed(1)}°, {location.lon.toFixed(1)}°
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-3 bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">{selectedLocation.name} Analysis</h2>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-400">Source:</span>
              <select className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm">
                {IMAGERY_SOURCES.map(source => (
                  <option key={source.id} value={source.id}>
                    {source.name} ({source.resolution})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="bg-gray-900 rounded-lg h-64 flex items-center justify-center mb-4">
            <div className="text-center">
              <div className="text-6xl mb-2">🛰️</div>
              <p className="text-gray-400">Satellite Imagery Viewer</p>
              <p className="text-sm text-gray-500">
                Location: {selectedLocation.lat.toFixed(2)}°, {selectedLocation.lon.toFixed(2)}°
              </p>
            </div>
          </div>

          <div className="flex space-x-2 mb-4">
            {(["changes", "military", "maritime", "alerts"] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab
                    ? "bg-blue-600 text-white"
                    : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {activeTab === "changes" && (
            <div className="space-y-2">
              {detections.map(detection => (
                <div key={detection.detection_id} className="bg-gray-700/50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-0.5 rounded text-xs ${getCategoryColor(detection.change_category)}`}>
                        {detection.change_category.replace(/_/g, " ")}
                      </span>
                      <span className="font-mono text-xs text-gray-400">{detection.detection_id}</span>
                    </div>
                    <span className={`text-sm ${getConfidenceColor(detection.confidence)}`}>
                      {detection.confidence} confidence
                    </span>
                  </div>
                  <p className="text-sm mt-2">{detection.description}</p>
                  <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                    <span>Area: {detection.area_sq_km.toFixed(2)} km²</span>
                    <span>Magnitude: {(detection.change_magnitude * 100).toFixed(0)}%</span>
                    <span>{new Date(detection.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "military" && (
            <div className="space-y-2">
              {militaryDetections.map(detection => (
                <div key={detection.detection_id} className="bg-gray-700/50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-0.5 rounded text-xs bg-red-500">
                        {detection.activity_type}
                      </span>
                      <span className="font-mono text-xs text-gray-400">{detection.detection_id}</span>
                    </div>
                    <span className={`text-sm ${getConfidenceColor(detection.confidence)}`}>
                      {detection.confidence} confidence
                    </span>
                  </div>
                  <p className="text-sm mt-2 font-medium">{detection.assessment}</p>
                  <div className="grid grid-cols-4 gap-2 mt-2 text-xs">
                    <div className="bg-gray-600/50 rounded p-2 text-center">
                      <div className="text-gray-400">Personnel</div>
                      <div className="font-bold text-lg">{detection.estimated_personnel.toLocaleString()}</div>
                    </div>
                    <div className="bg-gray-600/50 rounded p-2 text-center">
                      <div className="text-gray-400">Vehicles</div>
                      <div className="font-bold text-lg">{detection.vehicle_count}</div>
                    </div>
                    <div className="bg-gray-600/50 rounded p-2 text-center">
                      <div className="text-gray-400">Aircraft</div>
                      <div className="font-bold text-lg">{detection.aircraft_count}</div>
                    </div>
                    <div className="bg-gray-600/50 rounded p-2 text-center">
                      <div className="text-gray-400">Units</div>
                      <div className="font-bold text-lg">{detection.unit_types.length}</div>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {detection.unit_types.map(unit => (
                      <span key={unit} className="px-2 py-0.5 bg-gray-600 rounded text-xs">
                        {unit}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "maritime" && (
            <div className="bg-gray-700/50 rounded-lg p-4 text-center">
              <p className="text-gray-400">Maritime detection analysis for {selectedLocation.name}</p>
              <p className="text-sm text-gray-500 mt-2">
                Vessel tracking, port activity, and anomaly detection
              </p>
            </div>
          )}

          {activeTab === "alerts" && (
            <div className="space-y-2">
              {alerts.map(alert => (
                <div
                  key={alert.alert_id}
                  className={`p-3 rounded-lg border-l-4 ${
                    alert.priority >= 4
                      ? "bg-red-900/20 border-red-500"
                      : alert.priority >= 3
                      ? "bg-orange-900/20 border-orange-500"
                      : "bg-yellow-900/20 border-yellow-500"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-0.5 rounded text-xs ${getPriorityColor(alert.priority)}`}>
                        P{alert.priority}
                      </span>
                      <span className="font-mono text-xs text-gray-400">{alert.alert_id}</span>
                    </div>
                    <span className="text-xs text-gray-400">
                      Expires: {new Date(alert.expires_at).toLocaleString()}
                    </span>
                  </div>
                  <h3 className="font-semibold mt-2">{alert.title}</h3>
                  <p className="text-sm text-gray-400 mt-1">{alert.description}</p>
                  <div className="mt-2 p-2 bg-gray-700/50 rounded text-sm">
                    <span className="text-gray-400">Action: </span>
                    <span className="text-blue-400">{alert.recommended_action}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

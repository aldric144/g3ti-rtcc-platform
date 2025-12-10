"use client";

import { useState, useEffect } from "react";

interface DynamicObject {
  id: string;
  type: string;
  name: string;
  status: string;
  location: {
    lat: number;
    lng: number;
  };
}

interface Overlay {
  id: string;
  type: string;
  title: string;
  description: string;
  severity: string;
  geometry: Record<string, unknown>;
}

interface DigitalTwinData {
  timestamp: string;
  mode: string;
  current_time: string;
  objects: {
    objects: Record<string, DynamicObject[]>;
    total_count: number;
    by_status: Record<string, number>;
  };
  overlays: {
    overlays: Record<string, Overlay[]>;
    total_active: number;
    by_severity: Record<string, number>;
  };
  traffic: Array<{
    id: string;
    road: string;
    congestion: string;
    speed: number;
  }>;
  statistics: Record<string, unknown>;
  timewarp: {
    mode: string;
    current_time: string;
    playback_speed: number;
    snapshots_stored: number;
  };
}

export default function DigitalTwin3DView() {
  const [twinData, setTwinData] = useState<DigitalTwinData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedObjectType, setSelectedObjectType] = useState<string | null>(null);
  const [timelineMode, setTimelineMode] = useState<string>("live");
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);

  useEffect(() => {
    fetchDigitalTwin();
    const interval = setInterval(fetchDigitalTwin, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDigitalTwin = async () => {
    try {
      const response = await fetch("/api/citybrain/city/digital-twin");
      if (!response.ok) throw new Error("Failed to fetch digital twin data");
      const data = await response.json();
      setTwinData(data.digital_twin);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleTimelineChange = async (mode: string) => {
    try {
      await fetch("/api/citybrain/city/simulation/play", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode,
          playback_speed: playbackSpeed,
          hours_ahead: mode === "simulation" ? 24 : undefined,
        }),
      });
      setTimelineMode(mode);
      fetchDigitalTwin();
    } catch (err) {
      console.error("Failed to change timeline mode:", err);
    }
  };

  const getObjectIcon = (type: string) => {
    switch (type) {
      case "police_unit": return "🚔";
      case "fire_unit": return "🚒";
      case "ems_unit": return "🚑";
      case "drone": return "🛸";
      case "boat": return "🚤";
      case "city_vehicle": return "🚐";
      default: return "📍";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "available": return "bg-green-500";
      case "busy": return "bg-yellow-500";
      case "en_route": return "bg-blue-500";
      case "on_scene": return "bg-orange-500";
      case "out_of_service": return "bg-red-500";
      default: return "bg-gray-500";
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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-600";
      case "high": return "bg-orange-500";
      case "medium": return "bg-yellow-500";
      case "low": return "bg-blue-500";
      default: return "bg-gray-500";
    }
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
        <h2 className="text-xl font-bold">Digital Twin - Riviera Beach</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">Timeline:</span>
            <select
              value={timelineMode}
              onChange={(e) => handleTimelineChange(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="live">Live</option>
              <option value="historical">Historical</option>
              <option value="simulation">Simulation</option>
            </select>
          </div>
          {timelineMode !== "live" && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-400">Speed:</span>
              <select
                value={playbackSpeed}
                onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
              >
                <option value="0.5">0.5x</option>
                <option value="1">1x</option>
                <option value="2">2x</option>
                <option value="5">5x</option>
                <option value="10">10x</option>
              </select>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold">City Map View</h3>
            <p className="text-sm text-gray-400">
              {twinData?.timewarp?.current_time
                ? new Date(twinData.timewarp.current_time).toLocaleString()
                : "Live"}
            </p>
          </div>
          <div className="relative h-96 bg-gray-900">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="w-64 h-64 border-2 border-blue-500/30 rounded-lg relative">
                  <div className="absolute top-2 left-2 text-xs text-gray-500">
                    26.80°N
                  </div>
                  <div className="absolute bottom-2 left-2 text-xs text-gray-500">
                    26.75°N
                  </div>
                  <div className="absolute bottom-2 right-2 text-xs text-gray-500">
                    -80.03°W
                  </div>
                  <div className="absolute top-2 right-2 text-xs text-gray-500">
                    -80.09°W
                  </div>
                  
                  {twinData?.objects?.objects &&
                    Object.entries(twinData.objects.objects).map(([type, objects]) =>
                      objects.map((obj) => (
                        <div
                          key={obj.id}
                          className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer hover:scale-125 transition-transform"
                          style={{
                            left: `${((obj.location.lng + 80.09) / 0.06) * 100}%`,
                            top: `${((26.80 - obj.location.lat) / 0.05) * 100}%`,
                          }}
                          title={`${obj.name} - ${obj.status}`}
                        >
                          <span className="text-lg">{getObjectIcon(type)}</span>
                        </div>
                      ))
                    )}
                  
                  <div className="absolute inset-0 flex items-center justify-center text-gray-600">
                    <span className="text-sm">Riviera Beach</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-semibold mb-3">Dynamic Objects</h3>
            <div className="space-y-2">
              {twinData?.objects?.objects &&
                Object.entries(twinData.objects.objects).map(([type, objects]) => (
                  <button
                    key={type}
                    onClick={() => setSelectedObjectType(selectedObjectType === type ? null : type)}
                    className={`w-full flex items-center justify-between p-2 rounded ${
                      selectedObjectType === type ? "bg-blue-600" : "bg-gray-700 hover:bg-gray-600"
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span>{getObjectIcon(type)}</span>
                      <span className="text-sm capitalize">{type.replace(/_/g, " ")}</span>
                    </div>
                    <span className="text-sm text-gray-400">{objects.length}</span>
                  </button>
                ))}
            </div>
            <div className="mt-3 pt-3 border-t border-gray-700">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Total Objects</span>
                <span className="text-white">{twinData?.objects?.total_count || 0}</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-semibold mb-3">Object Status</h3>
            <div className="space-y-2">
              {twinData?.objects?.by_status &&
                Object.entries(twinData.objects.by_status).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${getStatusColor(status)}`} />
                      <span className="text-sm capitalize">{status.replace(/_/g, " ")}</span>
                    </div>
                    <span className="text-sm text-gray-400">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-semibold mb-3">Traffic Segments</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {twinData?.traffic?.map((segment) => (
              <div
                key={segment.id}
                className="flex items-center justify-between bg-gray-700/50 rounded p-2"
              >
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${getCongestionColor(segment.congestion)}`} />
                  <span className="text-sm">{segment.road}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-xs text-gray-400 capitalize">
                    {segment.congestion.replace(/_/g, " ")}
                  </span>
                  <span className="text-sm text-white">{segment.speed.toFixed(0)} mph</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-semibold mb-3">Active Overlays</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {twinData?.overlays?.overlays &&
              Object.entries(twinData.overlays.overlays).map(([type, overlays]) =>
                overlays.map((overlay) => (
                  <div
                    key={overlay.id}
                    className="bg-gray-700/50 rounded p-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${getSeverityColor(overlay.severity)}`} />
                        <span className="text-sm font-medium">{overlay.title}</span>
                      </div>
                      <span className="text-xs text-gray-400 capitalize">
                        {type.replace(/_/g, " ")}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{overlay.description}</p>
                  </div>
                ))
              )}
            {(!twinData?.overlays?.overlays || 
              Object.keys(twinData.overlays.overlays).length === 0) && (
              <p className="text-sm text-gray-500">No active overlays</p>
            )}
          </div>
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Total Active</span>
              <span className="text-white">{twinData?.overlays?.total_active || 0}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-semibold mb-3">TimeWarp Engine</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-gray-400">Mode</p>
            <p className="text-sm text-white capitalize">{twinData?.timewarp?.mode || "live"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Current Time</p>
            <p className="text-sm text-white">
              {twinData?.timewarp?.current_time
                ? new Date(twinData.timewarp.current_time).toLocaleTimeString()
                : "N/A"}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Playback Speed</p>
            <p className="text-sm text-white">{twinData?.timewarp?.playback_speed || 1}x</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Snapshots Stored</p>
            <p className="text-sm text-white">{twinData?.timewarp?.snapshots_stored || 0}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

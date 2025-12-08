"use client";

/**
 * Patrol Optimizer Component
 *
 * Provides patrol route optimization with:
 * - Route generation based on risk zones
 * - Waypoint management
 * - Route statistics
 * - Coverage analysis
 */

import { useState, useCallback } from "react";

interface PatrolOptimizerProps {
  selectedShift: string;
}

interface PatrolRoute {
  unit: string;
  shift: string;
  route: Waypoint[];
  priority_zones: PriorityZone[];
  statistics: RouteStatistics;
  justification: string[];
  generated_at: string;
  valid_until: string;
}

interface Waypoint {
  lat: number;
  lon: number;
  sequence: number;
  type: string;
  zone_id?: string;
  total_score?: number;
  distance_from_previous?: number;
  cumulative_distance?: number;
}

interface PriorityZone {
  zone_id: string;
  priority: number;
  type: string;
}

interface RouteStatistics {
  total_distance: number;
  patrol_distance: number;
  return_distance: number;
  waypoint_count: number;
  avg_priority: number;
  max_priority: number;
  coverage_area_sqkm: number;
  estimated_duration_hours: number;
}

export function PatrolOptimizer({ selectedShift }: PatrolOptimizerProps) {
  const [unit, setUnit] = useState("Unit1");
  const [startingPoint, setStartingPoint] = useState({ lat: 33.45, lon: -112.07 });
  const [maxDistance, setMaxDistance] = useState(15);
  const [waypointCount, setWaypointCount] = useState(10);
  const [route, setRoute] = useState<PatrolRoute | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateRoute = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/tactical/patrol/route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          unit,
          shift: selectedShift,
          starting_point: [startingPoint.lat, startingPoint.lon],
          max_distance: maxDistance,
          waypoint_count: waypointCount,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate route");
      }

      const data = await response.json();
      setRoute(data);
    } catch (err) {
      console.error("Failed to generate route:", err);
      setError(err instanceof Error ? err.message : "Failed to generate route");
      // Set mock data for development
      setRoute(generateMockRoute(unit, selectedShift, waypointCount));
    } finally {
      setLoading(false);
    }
  }, [unit, selectedShift, startingPoint, maxDistance, waypointCount]);

  return (
    <div className="space-y-6">
      {/* Configuration panel */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Route Configuration</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Unit</label>
            <input
              type="text"
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Starting Lat
            </label>
            <input
              type="number"
              step="0.001"
              value={startingPoint.lat}
              onChange={(e) =>
                setStartingPoint((p) => ({ ...p, lat: parseFloat(e.target.value) }))
              }
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Starting Lon
            </label>
            <input
              type="number"
              step="0.001"
              value={startingPoint.lon}
              onChange={(e) =>
                setStartingPoint((p) => ({ ...p, lon: parseFloat(e.target.value) }))
              }
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Max Distance (km)
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={maxDistance}
              onChange={(e) => setMaxDistance(parseInt(e.target.value))}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Waypoints</label>
            <input
              type="number"
              min="3"
              max="20"
              value={waypointCount}
              onChange={(e) => setWaypointCount(parseInt(e.target.value))}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={generateRoute}
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium disabled:opacity-50"
            >
              {loading ? "Generating..." : "Generate Route"}
            </button>
          </div>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded p-3 text-red-400">
          {error}
        </div>
      )}

      {/* Route display */}
      {route && (
        <div className="grid grid-cols-12 gap-6">
          {/* Route map */}
          <div className="col-span-8">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">
                Optimized Route for {route.unit}
              </h3>
              <RouteMap route={route} startingPoint={startingPoint} />
            </div>
          </div>

          {/* Route details */}
          <div className="col-span-4 space-y-4">
            {/* Statistics */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-3">Route Statistics</h3>
              <div className="space-y-2 text-sm">
                <StatRow
                  label="Total Distance"
                  value={`${route.statistics.total_distance.toFixed(1)} km`}
                />
                <StatRow
                  label="Patrol Distance"
                  value={`${route.statistics.patrol_distance.toFixed(1)} km`}
                />
                <StatRow
                  label="Waypoints"
                  value={route.statistics.waypoint_count.toString()}
                />
                <StatRow
                  label="Avg Priority"
                  value={`${(route.statistics.avg_priority * 100).toFixed(0)}%`}
                />
                <StatRow
                  label="Est. Duration"
                  value={`${route.statistics.estimated_duration_hours.toFixed(1)} hrs`}
                />
                <StatRow
                  label="Coverage Area"
                  value={`${route.statistics.coverage_area_sqkm.toFixed(1)} km²`}
                />
              </div>
            </div>

            {/* Priority zones */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-3">Priority Zones</h3>
              <div className="space-y-2">
                {route.priority_zones.slice(0, 5).map((zone, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between text-sm p-2 bg-gray-700 rounded"
                  >
                    <span>{zone.zone_id}</span>
                    <span className="text-orange-400">
                      {(zone.priority * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Justifications */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-3">Route Justification</h3>
              <div className="space-y-2 text-sm text-gray-400 max-h-48 overflow-y-auto">
                {route.justification.map((j, idx) => (
                  <p key={idx}>{j}</p>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Waypoint list */}
      {route && route.route.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Waypoint Details</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-400 border-b border-gray-700">
                  <th className="pb-2 pr-4">#</th>
                  <th className="pb-2 pr-4">Type</th>
                  <th className="pb-2 pr-4">Location</th>
                  <th className="pb-2 pr-4">Priority</th>
                  <th className="pb-2 pr-4">Distance</th>
                  <th className="pb-2">Cumulative</th>
                </tr>
              </thead>
              <tbody>
                {route.route.map((wp, idx) => (
                  <tr key={idx} className="border-b border-gray-700/50">
                    <td className="py-2 pr-4">{wp.sequence}</td>
                    <td className="py-2 pr-4">
                      <span className="px-2 py-0.5 bg-gray-700 rounded text-xs">
                        {wp.type.replace("_", " ")}
                      </span>
                    </td>
                    <td className="py-2 pr-4 font-mono text-xs">
                      {wp.lat.toFixed(4)}, {wp.lon.toFixed(4)}
                    </td>
                    <td className="py-2 pr-4">
                      {wp.total_score
                        ? `${(wp.total_score * 100).toFixed(0)}%`
                        : "-"}
                    </td>
                    <td className="py-2 pr-4">
                      {wp.distance_from_previous
                        ? `${wp.distance_from_previous.toFixed(1)} km`
                        : "-"}
                    </td>
                    <td className="py-2">
                      {wp.cumulative_distance
                        ? `${wp.cumulative_distance.toFixed(1)} km`
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// Route map component
interface RouteMapProps {
  route: PatrolRoute;
  startingPoint: { lat: number; lon: number };
}

function RouteMap({ route, startingPoint }: RouteMapProps) {
  const canvasWidth = 600;
  const canvasHeight = 400;

  // Calculate bounds from waypoints
  const allPoints = [
    startingPoint,
    ...route.route.map((wp) => ({ lat: wp.lat, lon: wp.lon })),
  ];
  const lats = allPoints.map((p) => p.lat);
  const lons = allPoints.map((p) => p.lon);

  const padding = 0.02;
  const bounds = {
    minLat: Math.min(...lats) - padding,
    maxLat: Math.max(...lats) + padding,
    minLon: Math.min(...lons) - padding,
    maxLon: Math.max(...lons) + padding,
  };

  const toCanvasCoords = (lat: number, lon: number) => {
    const x =
      ((lon - bounds.minLon) / (bounds.maxLon - bounds.minLon)) * canvasWidth;
    const y =
      ((bounds.maxLat - lat) / (bounds.maxLat - bounds.minLat)) * canvasHeight;
    return { x, y };
  };

  const startCoords = toCanvasCoords(startingPoint.lat, startingPoint.lon);

  return (
    <div className="relative" style={{ height: canvasHeight }}>
      <svg
        className="absolute inset-0"
        width={canvasWidth}
        height={canvasHeight}
        viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
      >
        {/* Grid background */}
        <defs>
          <pattern
            id="grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="1"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Route path */}
        {route.route.length > 0 && (
          <path
            d={`M ${startCoords.x} ${startCoords.y} ${route.route
              .map((wp) => {
                const coords = toCanvasCoords(wp.lat, wp.lon);
                return `L ${coords.x} ${coords.y}`;
              })
              .join(" ")}`}
            fill="none"
            stroke="rgb(59, 130, 246)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Starting point */}
        <circle
          cx={startCoords.x}
          cy={startCoords.y}
          r="10"
          fill="rgb(34, 197, 94)"
          stroke="white"
          strokeWidth="2"
        />
        <text
          x={startCoords.x}
          y={startCoords.y + 4}
          textAnchor="middle"
          fill="white"
          fontSize="10"
          fontWeight="bold"
        >
          S
        </text>

        {/* Waypoints */}
        {route.route.map((wp, idx) => {
          const coords = toCanvasCoords(wp.lat, wp.lon);
          const color =
            wp.type === "high_risk_zone"
              ? "rgb(239, 68, 68)"
              : wp.type === "predicted_hotspot"
                ? "rgb(249, 115, 22)"
                : wp.type === "priority_zone"
                  ? "rgb(168, 85, 247)"
                  : "rgb(59, 130, 246)";

          return (
            <g key={idx}>
              <circle
                cx={coords.x}
                cy={coords.y}
                r="8"
                fill={color}
                stroke="white"
                strokeWidth="2"
              />
              <text
                x={coords.x}
                y={coords.y + 3}
                textAnchor="middle"
                fill="white"
                fontSize="9"
                fontWeight="bold"
              >
                {wp.sequence}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute bottom-2 left-2 bg-gray-800/80 rounded px-2 py-1 text-xs flex gap-3">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-green-500" /> Start
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-red-500" /> High Risk
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-orange-500" /> Hotspot
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-blue-500" /> Waypoint
        </span>
      </div>
    </div>
  );
}

// Stat row component
function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-400">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

// Generate mock route data
function generateMockRoute(
  unit: string,
  shift: string,
  waypointCount: number
): PatrolRoute {
  const waypoints: Waypoint[] = [];
  const types = [
    "high_risk_zone",
    "predicted_hotspot",
    "historical_pattern",
    "priority_zone",
  ];

  let cumulative = 0;
  for (let i = 0; i < waypointCount; i++) {
    const distance = 1 + Math.random() * 2;
    cumulative += distance;

    waypoints.push({
      lat: 33.45 + (Math.random() - 0.5) * 0.1,
      lon: -112.07 + (Math.random() - 0.5) * 0.1,
      sequence: i + 1,
      type: types[Math.floor(Math.random() * types.length)],
      total_score: 0.9 - i * 0.05,
      distance_from_previous: distance,
      cumulative_distance: cumulative,
    });
  }

  return {
    unit,
    shift,
    route: waypoints,
    priority_zones: waypoints.slice(0, 5).map((wp) => ({
      zone_id: wp.zone_id || `zone_${wp.sequence}`,
      priority: wp.total_score || 0.5,
      type: wp.type,
    })),
    statistics: {
      total_distance: cumulative + 3,
      patrol_distance: cumulative,
      return_distance: 3,
      waypoint_count: waypointCount,
      avg_priority: 0.7,
      max_priority: 0.9,
      coverage_area_sqkm: 15.5,
      estimated_duration_hours: (cumulative + 3) / 30,
    },
    justification: [
      "Waypoint 1: High-risk zone with risk score 90% - proactive presence recommended",
      "Waypoint 2: Predicted hotspot with 85% confidence for shift period",
      "Waypoint 3: Historical pattern location with 12 incidents during similar hours",
      "Waypoint 4: Command-designated priority zone",
      "Waypoint 5: General patrol point with priority score 75%",
    ],
    generated_at: new Date().toISOString(),
    valid_until: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
  };
}

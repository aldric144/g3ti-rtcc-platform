"use client";

/**
 * Heatmap Viewer Component
 *
 * Displays predictive heatmaps with:
 * - Current activity heatmap
 * - Predictive heatmap (24h, 7d)
 * - Gunfire clusters
 * - LPR hotspots
 * - Repeat offender zones
 */

import { useState, useEffect, useCallback } from "react";

interface HeatmapViewerProps {
  compact?: boolean;
  onZoneSelect?: (zoneId: string) => void;
}

interface HeatmapData {
  geojson: GeoJSONFeatureCollection;
  clusters: Cluster[];
  hot_zones: HotZone[];
  confidence: number;
  explanation: string;
  generated_at: string;
}

interface GeoJSONFeatureCollection {
  type: string;
  features: GeoJSONFeature[];
}

interface GeoJSONFeature {
  type: string;
  geometry: {
    type: string;
    coordinates: number[] | number[][] | number[][][];
  };
  properties: Record<string, unknown>;
}

interface Cluster {
  id: string;
  center: { lat: number; lon: number };
  radius: number;
  intensity: number;
  incident_count: number;
}

interface HotZone {
  id: string;
  bounds: {
    min_lat: number;
    max_lat: number;
    min_lon: number;
    max_lon: number;
  };
  risk_score: number;
  confidence: number;
}

type HeatmapType = "all" | "gunfire" | "vehicles" | "crime";
type TimeRange = "current" | "24h" | "72h" | "7d";

export function HeatmapViewer({ compact = false, onZoneSelect }: HeatmapViewerProps) {
  const [heatmapType, setHeatmapType] = useState<HeatmapType>("all");
  const [timeRange, setTimeRange] = useState<TimeRange>("current");
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showClusters, setShowClusters] = useState(true);
  const [showHotZones, setShowHotZones] = useState(true);

  // Fetch heatmap data
  const fetchHeatmap = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      let url: string;
      if (timeRange === "current") {
        url = `/api/tactical/heatmap/current?type=${heatmapType}`;
      } else {
        const hours = timeRange === "24h" ? 24 : timeRange === "72h" ? 72 : 168;
        url = `/api/tactical/heatmap/predict?hours=${hours}&type=${heatmapType}`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch heatmap: ${response.statusText}`);
      }

      const data = await response.json();
      setHeatmapData(data);
    } catch (err) {
      console.error("Failed to fetch heatmap:", err);
      setError(err instanceof Error ? err.message : "Failed to load heatmap");
      // Set mock data for development
      setHeatmapData(generateMockHeatmapData());
    } finally {
      setLoading(false);
    }
  }, [heatmapType, timeRange]);

  useEffect(() => {
    fetchHeatmap();
  }, [fetchHeatmap]);

  // Handle cluster click
  const handleClusterClick = (cluster: Cluster) => {
    console.log("Cluster clicked:", cluster);
    // Could zoom to cluster or show details
  };

  // Handle hot zone click
  const handleHotZoneClick = (zone: HotZone) => {
    if (onZoneSelect) {
      onZoneSelect(zone.id);
    }
  };

  if (compact) {
    return (
      <CompactHeatmapView
        data={heatmapData}
        loading={loading}
        onZoneSelect={onZoneSelect}
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-2">
          {/* Heatmap type selector */}
          <select
            value={heatmapType}
            onChange={(e) => setHeatmapType(e.target.value as HeatmapType)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
          >
            <option value="all">All Activity</option>
            <option value="gunfire">Gunfire</option>
            <option value="vehicles">Vehicles</option>
            <option value="crime">Crime</option>
          </select>

          {/* Time range selector */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as TimeRange)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
          >
            <option value="current">Current</option>
            <option value="24h">Predict 24h</option>
            <option value="72h">Predict 72h</option>
            <option value="7d">Predict 7 Days</option>
          </select>
        </div>

        <div className="flex gap-4">
          {/* Layer toggles */}
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showClusters}
              onChange={(e) => setShowClusters(e.target.checked)}
              className="rounded"
            />
            Show Clusters
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showHotZones}
              onChange={(e) => setShowHotZones(e.target.checked)}
              className="rounded"
            />
            Show Hot Zones
          </label>

          {/* Refresh button */}
          <button
            onClick={fetchHeatmap}
            disabled={loading}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50"
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded p-3 text-red-400">
          {error}
        </div>
      )}

      {/* Main content */}
      <div className="grid grid-cols-12 gap-4">
        {/* Map area */}
        <div className="col-span-9">
          <div className="bg-gray-800 rounded-lg overflow-hidden">
            <HeatmapCanvas
              data={heatmapData}
              showClusters={showClusters}
              showHotZones={showHotZones}
              onClusterClick={handleClusterClick}
              onHotZoneClick={handleHotZoneClick}
            />
          </div>
        </div>

        {/* Side panel */}
        <div className="col-span-3 space-y-4">
          {/* Confidence indicator */}
          {heatmapData && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-2">Confidence</h3>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${heatmapData.confidence * 100}%` }}
                  />
                </div>
                <span className="text-sm">
                  {(heatmapData.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {heatmapData.explanation}
              </p>
            </div>
          )}

          {/* Clusters list */}
          {showClusters && heatmapData?.clusters && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-2">
                Clusters ({heatmapData.clusters.length})
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {heatmapData.clusters.slice(0, 5).map((cluster) => (
                  <button
                    key={cluster.id}
                    onClick={() => handleClusterClick(cluster)}
                    className="w-full text-left p-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                  >
                    <div className="flex justify-between">
                      <span>Cluster {cluster.id}</span>
                      <span className="text-orange-400">
                        {(cluster.intensity * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="text-xs text-gray-400">
                      {cluster.incident_count} incidents
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Hot zones list */}
          {showHotZones && heatmapData?.hot_zones && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-2">
                Hot Zones ({heatmapData.hot_zones.length})
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {heatmapData.hot_zones.slice(0, 5).map((zone) => (
                  <button
                    key={zone.id}
                    onClick={() => handleHotZoneClick(zone)}
                    className="w-full text-left p-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                  >
                    <div className="flex justify-between">
                      <span>{zone.id}</span>
                      <span
                        className={
                          zone.risk_score >= 0.8
                            ? "text-red-400"
                            : zone.risk_score >= 0.6
                              ? "text-orange-400"
                              : "text-yellow-400"
                        }
                      >
                        {(zone.risk_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="text-xs text-gray-400">
                      Confidence: {(zone.confidence * 100).toFixed(0)}%
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold mb-2">Legend</h3>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gradient-to-r from-blue-500 to-red-500" />
            <span>Density (Low to High)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full border-2 border-orange-500" />
            <span>Cluster</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded border-2 border-red-500" />
            <span>Hot Zone</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Compact heatmap view for overview tab
interface CompactHeatmapViewProps {
  data: HeatmapData | null;
  loading: boolean;
  onZoneSelect?: (zoneId: string) => void;
}

function CompactHeatmapView({ data, loading, onZoneSelect }: CompactHeatmapViewProps) {
  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading heatmap...</div>
      </div>
    );
  }

  return (
    <HeatmapCanvas
      data={data}
      showClusters={true}
      showHotZones={true}
      onHotZoneClick={(zone) => onZoneSelect?.(zone.id)}
    />
  );
}

// Heatmap canvas component (simplified visualization)
interface HeatmapCanvasProps {
  data: HeatmapData | null;
  showClusters: boolean;
  showHotZones: boolean;
  onClusterClick?: (cluster: Cluster) => void;
  onHotZoneClick?: (zone: HotZone) => void;
}

function HeatmapCanvas({
  data,
  showClusters,
  showHotZones,
  onClusterClick,
  onHotZoneClick,
}: HeatmapCanvasProps) {
  // This is a simplified visualization
  // In production, this would use Mapbox GL or Leaflet
  const canvasWidth = 800;
  const canvasHeight = 500;

  // Default bounds
  const bounds = {
    minLat: 33.35,
    maxLat: 33.55,
    minLon: -112.15,
    maxLon: -111.95,
  };

  // Convert lat/lon to canvas coordinates
  const toCanvasCoords = (lat: number, lon: number) => {
    const x =
      ((lon - bounds.minLon) / (bounds.maxLon - bounds.minLon)) * canvasWidth;
    const y =
      ((bounds.maxLat - lat) / (bounds.maxLat - bounds.minLat)) * canvasHeight;
    return { x, y };
  };

  if (!data) {
    return (
      <div
        className="flex items-center justify-center bg-gray-900"
        style={{ height: canvasHeight }}
      >
        <span className="text-gray-400">No heatmap data available</span>
      </div>
    );
  }

  return (
    <div className="relative" style={{ height: canvasHeight }}>
      {/* Base map placeholder */}
      <div
        className="absolute inset-0 bg-gray-900"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* Heatmap overlay - simplified grid visualization */}
      <svg
        className="absolute inset-0"
        width={canvasWidth}
        height={canvasHeight}
        viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
      >
        {/* Render heatmap grid from GeoJSON */}
        {data.geojson?.features?.map((feature, idx) => {
          if (feature.geometry.type === "Polygon") {
            const coords = feature.geometry.coordinates[0] as number[][];
            const points = coords
              .map((coord) => {
                const { x, y } = toCanvasCoords(coord[1], coord[0]);
                return `${x},${y}`;
              })
              .join(" ");

            const density = (feature.properties?.density as number) || 0;
            const color = densityToColor(density);

            return (
              <polygon
                key={idx}
                points={points}
                fill={color}
                fillOpacity={0.6}
                stroke="none"
              />
            );
          }
          return null;
        })}

        {/* Render clusters */}
        {showClusters &&
          data.clusters?.map((cluster) => {
            const { x, y } = toCanvasCoords(
              cluster.center.lat,
              cluster.center.lon
            );
            const radius = Math.max(10, cluster.radius * 1000);

            return (
              <g key={cluster.id}>
                <circle
                  cx={x}
                  cy={y}
                  r={radius}
                  fill="rgba(249, 115, 22, 0.3)"
                  stroke="rgb(249, 115, 22)"
                  strokeWidth={2}
                  className="cursor-pointer"
                  onClick={() => onClusterClick?.(cluster)}
                />
                <text
                  x={x}
                  y={y}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="white"
                  fontSize={10}
                >
                  {cluster.incident_count}
                </text>
              </g>
            );
          })}

        {/* Render hot zones */}
        {showHotZones &&
          data.hot_zones?.map((zone) => {
            const topLeft = toCanvasCoords(
              zone.bounds.max_lat,
              zone.bounds.min_lon
            );
            const bottomRight = toCanvasCoords(
              zone.bounds.min_lat,
              zone.bounds.max_lon
            );
            const width = bottomRight.x - topLeft.x;
            const height = bottomRight.y - topLeft.y;

            const color =
              zone.risk_score >= 0.8
                ? "rgb(239, 68, 68)"
                : zone.risk_score >= 0.6
                  ? "rgb(249, 115, 22)"
                  : "rgb(234, 179, 8)";

            return (
              <rect
                key={zone.id}
                x={topLeft.x}
                y={topLeft.y}
                width={width}
                height={height}
                fill="none"
                stroke={color}
                strokeWidth={2}
                strokeDasharray="4"
                className="cursor-pointer"
                onClick={() => onHotZoneClick?.(zone)}
              />
            );
          })}
      </svg>

      {/* Map info overlay */}
      <div className="absolute bottom-2 left-2 bg-gray-800/80 rounded px-2 py-1 text-xs">
        Generated: {new Date(data.generated_at).toLocaleTimeString()}
      </div>
    </div>
  );
}

// Helper function to convert density to color
function densityToColor(density: number): string {
  // Blue (low) -> Yellow -> Red (high)
  if (density < 0.33) {
    const t = density / 0.33;
    return `rgb(${Math.round(59 + t * 175)}, ${Math.round(130 + t * 126)}, ${Math.round(246 - t * 46)})`;
  } else if (density < 0.66) {
    const t = (density - 0.33) / 0.33;
    return `rgb(${Math.round(234)}, ${Math.round(256 - t * 77)}, ${Math.round(200 - t * 192)})`;
  } else {
    const t = (density - 0.66) / 0.34;
    return `rgb(${Math.round(234 + t * 5)}, ${Math.round(179 - t * 111)}, ${Math.round(8)})`;
  }
}

// Generate mock heatmap data for development
function generateMockHeatmapData(): HeatmapData {
  const features: GeoJSONFeature[] = [];
  const gridSize = 10;
  const bounds = {
    minLat: 33.35,
    maxLat: 33.55,
    minLon: -112.15,
    maxLon: -111.95,
  };

  const latStep = (bounds.maxLat - bounds.minLat) / gridSize;
  const lonStep = (bounds.maxLon - bounds.minLon) / gridSize;

  // Create hotspots
  const hotspots = [
    { lat: 33.45, lon: -112.07, intensity: 0.9 },
    { lat: 33.42, lon: -112.05, intensity: 0.7 },
    { lat: 33.48, lon: -112.10, intensity: 0.6 },
  ];

  for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
      const minLat = bounds.minLat + i * latStep;
      const maxLat = minLat + latStep;
      const minLon = bounds.minLon + j * lonStep;
      const maxLon = minLon + lonStep;

      const centerLat = (minLat + maxLat) / 2;
      const centerLon = (minLon + maxLon) / 2;

      // Calculate density based on distance to hotspots
      let density = 0.1;
      for (const hotspot of hotspots) {
        const dist = Math.sqrt(
          Math.pow(centerLat - hotspot.lat, 2) +
            Math.pow(centerLon - hotspot.lon, 2)
        );
        density += hotspot.intensity * Math.exp(-dist * 50);
      }
      density = Math.min(1, density);

      features.push({
        type: "Feature",
        geometry: {
          type: "Polygon",
          coordinates: [
            [
              [minLon, minLat],
              [maxLon, minLat],
              [maxLon, maxLat],
              [minLon, maxLat],
              [minLon, minLat],
            ],
          ],
        },
        properties: { density },
      });
    }
  }

  return {
    geojson: {
      type: "FeatureCollection",
      features,
    },
    clusters: hotspots.map((h, i) => ({
      id: `cluster-${i}`,
      center: { lat: h.lat, lon: h.lon },
      radius: 0.02,
      intensity: h.intensity,
      incident_count: Math.round(h.intensity * 20),
    })),
    hot_zones: hotspots.slice(0, 2).map((h, i) => ({
      id: `zone-${i}`,
      bounds: {
        min_lat: h.lat - 0.02,
        max_lat: h.lat + 0.02,
        min_lon: h.lon - 0.02,
        max_lon: h.lon + 0.02,
      },
      risk_score: h.intensity,
      confidence: 0.8 - i * 0.1,
    })),
    confidence: 0.85,
    explanation:
      "High activity detected in central and southern zones based on recent incident patterns.",
    generated_at: new Date().toISOString(),
  };
}

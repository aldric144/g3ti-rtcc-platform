"use client";

import { useState, useEffect } from "react";

interface HeatmapData {
  zones: Array<{
    zone_id: string;
    zone_name: string;
    latitude: number;
    longitude: number;
    value: number;
    type: string;
  }>;
  legend: {
    min: number;
    max: number;
    unit: string;
  };
}

type HeatmapType = "crime" | "traffic" | "population" | "temperature" | "air_quality";

export default function LiveCityHeatmap() {
  const [heatmapType, setHeatmapType] = useState<HeatmapType>("crime");
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState("24h");

  useEffect(() => {
    fetchHeatmapData();
  }, [heatmapType, timeRange]);

  const fetchHeatmapData = async () => {
    setLoading(true);
    try {
      const mockData = generateMockHeatmapData(heatmapType);
      setHeatmapData(mockData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const generateMockHeatmapData = (type: HeatmapType): HeatmapData => {
    const zones = [
      { id: "downtown", name: "Downtown/Marina", lat: 26.7753, lng: -80.0583 },
      { id: "singer_island", name: "Singer Island", lat: 26.7850, lng: -80.0350 },
      { id: "westside", name: "Westside", lat: 26.7700, lng: -80.0750 },
      { id: "central", name: "Central Business", lat: 26.7780, lng: -80.0600 },
      { id: "industrial", name: "Industrial/Port", lat: 26.7650, lng: -80.0500 },
      { id: "north", name: "North Riviera", lat: 26.7900, lng: -80.0650 },
    ];

    const typeConfig: Record<HeatmapType, { min: number; max: number; unit: string }> = {
      crime: { min: 0, max: 100, unit: "incidents" },
      traffic: { min: 0, max: 100, unit: "congestion %" },
      population: { min: 0, max: 15000, unit: "people" },
      temperature: { min: 70, max: 100, unit: "°F" },
      air_quality: { min: 0, max: 200, unit: "AQI" },
    };

    const config = typeConfig[type];

    return {
      zones: zones.map((zone) => ({
        zone_id: zone.id,
        zone_name: zone.name,
        latitude: zone.lat,
        longitude: zone.lng,
        value: Math.random() * (config.max - config.min) + config.min,
        type,
      })),
      legend: config,
    };
  };

  const getHeatColor = (value: number, min: number, max: number) => {
    const normalized = (value - min) / (max - min);
    if (normalized < 0.2) return "bg-green-500";
    if (normalized < 0.4) return "bg-yellow-400";
    if (normalized < 0.6) return "bg-orange-400";
    if (normalized < 0.8) return "bg-orange-600";
    return "bg-red-600";
  };

  const getHeatOpacity = (value: number, min: number, max: number) => {
    const normalized = (value - min) / (max - min);
    return 0.3 + normalized * 0.7;
  };

  const heatmapTypes: { id: HeatmapType; label: string; icon: string }[] = [
    { id: "crime", label: "Crime Density", icon: "🚨" },
    { id: "traffic", label: "Traffic Congestion", icon: "🚗" },
    { id: "population", label: "Population Density", icon: "👥" },
    { id: "temperature", label: "Temperature", icon: "🌡️" },
    { id: "air_quality", label: "Air Quality", icon: "💨" },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Live City Heatmap</h2>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
          >
            <option value="1h">Last 1 Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
          <button
            onClick={fetchHeatmapData}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="flex space-x-2 overflow-x-auto pb-2">
        {heatmapTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => setHeatmapType(type.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg whitespace-nowrap ${
              heatmapType === type.id
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            <span>{type.icon}</span>
            <span className="text-sm">{type.label}</span>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-700">
            <h3 className="font-semibold">
              {heatmapTypes.find((t) => t.id === heatmapType)?.label} - Riviera Beach
            </h3>
          </div>
          <div className="relative h-96 bg-gray-900 p-4">
            <div className="absolute inset-4 border-2 border-gray-700 rounded-lg">
              {heatmapData?.zones.map((zone) => {
                const left = ((zone.longitude + 80.09) / 0.08) * 100;
                const top = ((26.80 - zone.latitude) / 0.06) * 100;
                const color = getHeatColor(
                  zone.value,
                  heatmapData.legend.min,
                  heatmapData.legend.max
                );
                const opacity = getHeatOpacity(
                  zone.value,
                  heatmapData.legend.min,
                  heatmapData.legend.max
                );

                return (
                  <div
                    key={zone.zone_id}
                    className={`absolute w-16 h-16 rounded-full ${color} transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center cursor-pointer hover:scale-110 transition-transform`}
                    style={{
                      left: `${Math.min(90, Math.max(10, left))}%`,
                      top: `${Math.min(90, Math.max(10, top))}%`,
                      opacity,
                    }}
                    title={`${zone.zone_name}: ${zone.value.toFixed(1)} ${heatmapData.legend.unit}`}
                  >
                    <span className="text-xs font-bold text-white drop-shadow-lg">
                      {zone.value.toFixed(0)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-semibold mb-3">Legend</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded bg-green-500" />
                  <span className="text-sm">Low</span>
                </div>
                <span className="text-sm text-gray-400">
                  {heatmapData?.legend.min.toFixed(0)} {heatmapData?.legend.unit}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded bg-yellow-400" />
                  <span className="text-sm">Moderate</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded bg-orange-500" />
                  <span className="text-sm">High</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded bg-red-600" />
                  <span className="text-sm">Critical</span>
                </div>
                <span className="text-sm text-gray-400">
                  {heatmapData?.legend.max.toFixed(0)} {heatmapData?.legend.unit}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-semibold mb-3">Zone Details</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {heatmapData?.zones
                .sort((a, b) => b.value - a.value)
                .map((zone) => (
                  <div
                    key={zone.zone_id}
                    className="flex items-center justify-between bg-gray-700/50 rounded p-2"
                  >
                    <span className="text-sm">{zone.zone_name}</span>
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-2 h-2 rounded-full ${getHeatColor(
                          zone.value,
                          heatmapData.legend.min,
                          heatmapData.legend.max
                        )}`}
                      />
                      <span className="text-sm text-white">
                        {zone.value.toFixed(1)}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-semibold mb-3">Statistics</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Average</span>
                <span className="text-sm text-white">
                  {heatmapData
                    ? (
                        heatmapData.zones.reduce((sum, z) => sum + z.value, 0) /
                        heatmapData.zones.length
                      ).toFixed(1)
                    : "N/A"}{" "}
                  {heatmapData?.legend.unit}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Maximum</span>
                <span className="text-sm text-white">
                  {heatmapData
                    ? Math.max(...heatmapData.zones.map((z) => z.value)).toFixed(1)
                    : "N/A"}{" "}
                  {heatmapData?.legend.unit}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">Minimum</span>
                <span className="text-sm text-white">
                  {heatmapData
                    ? Math.min(...heatmapData.zones.map((z) => z.value)).toFixed(1)
                    : "N/A"}{" "}
                  {heatmapData?.legend.unit}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

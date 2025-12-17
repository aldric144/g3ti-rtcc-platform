'use client';

import React, { useState, useEffect, useRef } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';

interface HeatmapPoint {
  latitude: number;
  longitude: number;
  intensity: number;
  weight: number;
}

interface Hotspot {
  cluster_id: number;
  center_lat: number;
  center_lng: number;
  radius_meters: number;
  incident_count: number;
  crime_types: string[];
  severity_score: number;
  top_crimes: string[];
}

interface HeatmapData {
  points: HeatmapPoint[];
  hotspots: Hotspot[];
  time_range: string;
  start_date: string;
  end_date: string;
  total_incidents: number;
  bounds: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
}

type TimeRange = '24h' | '7d' | '30d';
type CrimeFilter = 'all' | 'violent' | 'property' | 'drug';

export default function CrimeHeatmap() {
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('7d');
  const [crimeFilter, setCrimeFilter] = useState<CrimeFilter>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedHotspot, setSelectedHotspot] = useState<Hotspot | null>(null);
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchHeatmapData();
  }, [timeRange, crimeFilter]);

  const fetchHeatmapData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        time_range: timeRange,
      });
      if (crimeFilter !== 'all') {
        params.append('crime_type', crimeFilter);
      }

      const response = await fetch(`${API_BASE_URL}/api/crime/heatmap?${params}`);
      if (response.ok) {
        const data = await response.json();
        setHeatmapData(data);
      } else {
        setError('Failed to load heatmap data');
      }
    } catch (err) {
      setError('Error loading heatmap data');
    } finally {
      setIsLoading(false);
    }
  };

  const getIntensityColor = (intensity: number) => {
    if (intensity > 7) return 'bg-red-600';
    if (intensity > 5) return 'bg-orange-500';
    if (intensity > 3) return 'bg-yellow-500';
    if (intensity > 1) return 'bg-green-500';
    return 'bg-blue-500';
  };

  const getSeverityColor = (score: number) => {
    if (score >= 4) return 'text-red-500';
    if (score >= 3) return 'text-orange-500';
    if (score >= 2) return 'text-yellow-500';
    return 'text-green-500';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-2">
          <span className="text-gray-400 self-center">Time Range:</span>
          {(['24h', '7d', '30d'] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {range === '24h' ? '24 Hours' : range === '7d' ? '7 Days' : '30 Days'}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <span className="text-gray-400 self-center">Filter:</span>
          {(['all', 'violent', 'property', 'drug'] as CrimeFilter[]).map((filter) => (
            <button
              key={filter}
              onClick={() => setCrimeFilter(filter)}
              className={`px-3 py-1 rounded capitalize ${
                crimeFilter === filter
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {filter === 'all' ? 'All Crime' : filter}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="text-red-400 text-center py-4">{error}</div>
      )}

      {/* Stats Bar */}
      {heatmapData && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-white">{heatmapData.total_incidents}</div>
            <div className="text-gray-400 text-sm">Total Incidents</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-orange-400">{heatmapData.hotspots.length}</div>
            <div className="text-gray-400 text-sm">Hotspot Clusters</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-400">{heatmapData.points.length}</div>
            <div className="text-gray-400 text-sm">Heat Points</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-sm font-medium text-white">
              {heatmapData.start_date} - {heatmapData.end_date}
            </div>
            <div className="text-gray-400 text-sm">Analysis Period</div>
          </div>
        </div>
      )}

      {/* Map Placeholder with Heatmap Visualization */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div 
            ref={mapRef}
            className="bg-gray-700/50 rounded-lg h-96 relative overflow-hidden"
          >
            {/* Simple grid-based heatmap visualization */}
            <div className="absolute inset-0 p-4">
              <div className="text-gray-400 text-sm mb-2">Crime Density Heatmap</div>
              <div className="grid grid-cols-10 gap-1 h-full">
                {heatmapData?.points.slice(0, 100).map((point, idx) => (
                  <div
                    key={idx}
                    className={`rounded ${getIntensityColor(point.intensity)} opacity-70`}
                    style={{ opacity: 0.3 + (point.intensity / 10) * 0.7 }}
                    title={`Intensity: ${point.intensity.toFixed(2)}`}
                  />
                ))}
              </div>
            </div>
            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-gray-800/90 rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-2">Intensity</div>
              <div className="flex gap-1">
                <div className="w-4 h-4 bg-blue-500 rounded" title="Low"></div>
                <div className="w-4 h-4 bg-green-500 rounded" title="Medium-Low"></div>
                <div className="w-4 h-4 bg-yellow-500 rounded" title="Medium"></div>
                <div className="w-4 h-4 bg-orange-500 rounded" title="High"></div>
                <div className="w-4 h-4 bg-red-600 rounded" title="Critical"></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>
          </div>
        </div>

        {/* Hotspots List */}
        <div className="bg-gray-700/50 rounded-lg p-4 h-96 overflow-y-auto">
          <h3 className="text-lg font-semibold text-white mb-4">Identified Hotspots</h3>
          <div className="space-y-3">
            {heatmapData?.hotspots.map((hotspot) => (
              <div
                key={hotspot.cluster_id}
                onClick={() => setSelectedHotspot(hotspot)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedHotspot?.cluster_id === hotspot.cluster_id
                    ? 'bg-blue-600/30 border border-blue-500'
                    : 'bg-gray-600/50 hover:bg-gray-600'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="text-white font-medium">Cluster #{hotspot.cluster_id + 1}</div>
                    <div className="text-gray-400 text-sm">
                      {hotspot.incident_count} incidents
                    </div>
                  </div>
                  <div className={`text-lg font-bold ${getSeverityColor(hotspot.severity_score)}`}>
                    {hotspot.severity_score.toFixed(1)}
                  </div>
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {hotspot.crime_types.slice(0, 3).map((type) => (
                    <span
                      key={type}
                      className="px-2 py-0.5 bg-gray-700 rounded text-xs text-gray-300"
                    >
                      {type}
                    </span>
                  ))}
                </div>
              </div>
            ))}
            {(!heatmapData?.hotspots || heatmapData.hotspots.length === 0) && (
              <div className="text-gray-500 text-center py-4">No hotspots identified</div>
            )}
          </div>
        </div>
      </div>

      {/* Selected Hotspot Details */}
      {selectedHotspot && (
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Hotspot Details - Cluster #{selectedHotspot.cluster_id + 1}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-gray-400 text-sm">Location</div>
              <div className="text-white">
                {selectedHotspot.center_lat.toFixed(4)}, {selectedHotspot.center_lng.toFixed(4)}
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Radius</div>
              <div className="text-white">{Math.round(selectedHotspot.radius_meters)}m</div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Incidents</div>
              <div className="text-white">{selectedHotspot.incident_count}</div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Severity</div>
              <div className={`font-bold ${getSeverityColor(selectedHotspot.severity_score)}`}>
                {selectedHotspot.severity_score.toFixed(2)} / 5.0
              </div>
            </div>
          </div>
          <div className="mt-4">
            <div className="text-gray-400 text-sm mb-2">Top Crimes</div>
            <div className="flex flex-wrap gap-2">
              {selectedHotspot.top_crimes.map((crime) => (
                <span
                  key={crime}
                  className="px-3 py-1 bg-gray-600 rounded-full text-sm text-gray-200"
                >
                  {crime}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';

interface RepeatLocation {
  location_id: string;
  latitude: number;
  longitude: number;
  address: string | null;
  incident_count: number;
  first_incident: string;
  last_incident: string;
  crime_types: string[];
  severity_score: number;
  is_business: boolean;
  sector: string;
  incidents: {
    id: string;
    type: string;
    subcategory: string;
    datetime: string;
    priority: string;
  }[];
}

interface LocationCluster {
  cluster_id: string;
  center_lat: number;
  center_lng: number;
  radius_meters: number;
  total_incidents: number;
  location_count: number;
  sector: string;
}

interface RepeatLocationData {
  repeat_locations: RepeatLocation[];
  clusters: LocationCluster[];
  total_repeat_locations: number;
  total_incidents_at_repeats: number;
  top_10_hotspots: RepeatLocation[];
  analysis_period: string;
}

export default function RepeatLocations() {
  const [data, setData] = useState<RepeatLocationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);
  const [minIncidents, setMinIncidents] = useState(2);
  const [selectedLocation, setSelectedLocation] = useState<RepeatLocation | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'business' | 'residential'>('all');

  useEffect(() => {
    fetchData();
  }, [days, minIncidents]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/crime/repeat-locations?days=${days}&min_incidents=${minIncidents}`
      );
      if (response.ok) {
        setData(await response.json());
      } else {
        setError('Failed to load repeat location data');
      }
    } catch (err) {
      setError('Error loading repeat location data');
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (score: number) => {
    if (score >= 4) return 'text-red-500';
    if (score >= 3) return 'text-orange-500';
    if (score >= 2) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getSeverityBg = (score: number) => {
    if (score >= 4) return 'bg-red-500/20 border-red-500';
    if (score >= 3) return 'bg-orange-500/20 border-orange-500';
    if (score >= 2) return 'bg-yellow-500/20 border-yellow-500';
    return 'bg-green-500/20 border-green-500';
  };

  const filteredLocations = data?.repeat_locations.filter(loc => {
    if (filterType === 'business') return loc.is_business;
    if (filterType === 'residential') return !loc.is_business;
    return true;
  }) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-400 text-center py-8">{error}</div>;
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-4 items-center">
          <div className="flex gap-2 items-center">
            <span className="text-gray-400">Period:</span>
            {[7, 14, 30, 60].map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1 rounded ${
                  days === d
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
          <div className="flex gap-2 items-center">
            <span className="text-gray-400">Min Incidents:</span>
            <select
              value={minIncidents}
              onChange={(e) => setMinIncidents(Number(e.target.value))}
              className="bg-gray-700 text-white rounded px-3 py-1"
            >
              {[2, 3, 4, 5, 10].map((n) => (
                <option key={n} value={n}>{n}+</option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex gap-2">
          {(['all', 'business', 'residential'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1 rounded capitalize ${
                filterType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Repeat Locations</div>
          <div className="text-2xl font-bold text-white">{data?.total_repeat_locations || 0}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Total Incidents</div>
          <div className="text-2xl font-bold text-orange-400">{data?.total_incidents_at_repeats || 0}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Location Clusters</div>
          <div className="text-2xl font-bold text-blue-400">{data?.clusters.length || 0}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Analysis Period</div>
          <div className="text-lg font-medium text-white">{data?.analysis_period || 'N/A'}</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Location List */}
        <div className="lg:col-span-2 bg-gray-700/50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-4">
            Repeat Call Hotspots ({filteredLocations.length})
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-gray-600">
                  <th className="pb-2 pr-4">Location</th>
                  <th className="pb-2 pr-4">Incidents</th>
                  <th className="pb-2 pr-4">Severity</th>
                  <th className="pb-2 pr-4">Type</th>
                  <th className="pb-2 pr-4">Sector</th>
                  <th className="pb-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredLocations.slice(0, 20).map((loc) => (
                  <tr
                    key={loc.location_id}
                    className={`border-b border-gray-700/50 cursor-pointer hover:bg-gray-600/30 ${
                      selectedLocation?.location_id === loc.location_id ? 'bg-blue-600/20' : ''
                    }`}
                    onClick={() => setSelectedLocation(loc)}
                  >
                    <td className="py-3 pr-4">
                      <div className="text-white font-medium">
                        {loc.address || `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`}
                      </div>
                      <div className="text-gray-500 text-xs">
                        Last: {new Date(loc.last_incident).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="py-3 pr-4">
                      <span className="text-xl font-bold text-white">{loc.incident_count}</span>
                    </td>
                    <td className="py-3 pr-4">
                      <span className={`font-bold ${getSeverityColor(loc.severity_score)}`}>
                        {loc.severity_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="py-3 pr-4">
                      <span className={`px-2 py-1 rounded text-xs ${
                        loc.is_business
                          ? 'bg-purple-500/20 text-purple-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {loc.is_business ? 'Business' : 'Residential'}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-gray-300">{loc.sector}</td>
                    <td className="py-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedLocation(loc);
                        }}
                        className="text-blue-400 hover:text-blue-300 text-sm"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Location Details / Map */}
        <div className="space-y-4">
          {/* Selected Location Details */}
          {selectedLocation ? (
            <div className={`rounded-lg p-4 border ${getSeverityBg(selectedLocation.severity_score)}`}>
              <h3 className="text-lg font-semibold text-white mb-2">Location Details</h3>
              <div className="space-y-2">
                <div>
                  <span className="text-gray-400 text-sm">Address:</span>
                  <div className="text-white">
                    {selectedLocation.address || 'No address available'}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400 text-sm">Coordinates:</span>
                  <div className="text-white text-sm">
                    {selectedLocation.latitude.toFixed(6)}, {selectedLocation.longitude.toFixed(6)}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-gray-400 text-sm">Incidents:</span>
                    <div className="text-2xl font-bold text-white">{selectedLocation.incident_count}</div>
                  </div>
                  <div>
                    <span className="text-gray-400 text-sm">Severity:</span>
                    <div className={`text-2xl font-bold ${getSeverityColor(selectedLocation.severity_score)}`}>
                      {selectedLocation.severity_score.toFixed(2)}
                    </div>
                  </div>
                </div>
                <div>
                  <span className="text-gray-400 text-sm">Crime Types:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedLocation.crime_types.map((type) => (
                      <span
                        key={type}
                        className="px-2 py-0.5 bg-gray-600 rounded text-xs text-gray-200"
                      >
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400 text-sm">Time Range:</span>
                  <div className="text-white text-sm">
                    {new Date(selectedLocation.first_incident).toLocaleDateString()} - {new Date(selectedLocation.last_incident).toLocaleDateString()}
                  </div>
                </div>
              </div>

              {/* Recent Incidents */}
              <div className="mt-4">
                <span className="text-gray-400 text-sm">Recent Incidents:</span>
                <div className="mt-2 space-y-2 max-h-48 overflow-y-auto">
                  {selectedLocation.incidents.map((incident) => (
                    <div
                      key={incident.id}
                      className="bg-gray-700/50 rounded p-2 text-sm"
                    >
                      <div className="flex justify-between">
                        <span className="text-white font-medium">{incident.subcategory}</span>
                        <span className={`text-xs px-1.5 py-0.5 rounded ${
                          incident.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                          incident.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-green-500/20 text-green-400'
                        }`}>
                          {incident.priority}
                        </span>
                      </div>
                      <div className="text-gray-500 text-xs">
                        {new Date(incident.datetime).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-700/50 rounded-lg p-4 text-center text-gray-500">
              Select a location to view details
            </div>
          )}

          {/* Top 10 Hotspots */}
          <div className="bg-gray-700/50 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-3">Top 10 Hotspots</h3>
            <div className="space-y-2">
              {data?.top_10_hotspots.slice(0, 10).map((loc, idx) => (
                <div
                  key={loc.location_id}
                  onClick={() => setSelectedLocation(loc)}
                  className={`flex items-center gap-3 p-2 rounded cursor-pointer hover:bg-gray-600/50 ${
                    selectedLocation?.location_id === loc.location_id ? 'bg-blue-600/20' : ''
                  }`}
                >
                  <span className="text-gray-500 font-bold w-6">#{idx + 1}</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-white text-sm truncate">
                      {loc.address || `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`}
                    </div>
                    <div className="text-gray-500 text-xs">{loc.sector}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-bold">{loc.incident_count}</div>
                    <div className={`text-xs ${getSeverityColor(loc.severity_score)}`}>
                      {loc.severity_score.toFixed(1)}
                    </div>
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

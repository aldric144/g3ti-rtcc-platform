'use client';

import { useState, useEffect } from 'react';

interface Heatmap {
  heatmap_id: string;
  heatmap_type: string;
  name: string;
  region_codes: string[];
  total_incidents: number;
  max_value: number;
  avg_value: number;
  created_at: string;
}

interface Cluster {
  cluster_id: string;
  cluster_type: string;
  name: string;
  center_lat: number;
  center_lon: number;
  radius_km: number;
  jurisdictions: string[];
  incident_count: number;
  incident_count_7d: number;
  trend: string;
  trend_percent: number;
  risk_level: string;
  crime_types: string[];
}

interface Trajectory {
  trajectory_id: string;
  offender_id: string;
  offender_name: string;
  jurisdictions_crossed: string[];
  total_incidents: number;
  risk_level: string;
  confidence: string;
  last_known_location?: {
    latitude: number;
    longitude: number;
    timestamp: string;
  };
}

export default function RegionalAnalytics() {
  const [heatmaps, setHeatmaps] = useState<Heatmap[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [trajectories, setTrajectories] = useState<Trajectory[]>([]);
  const [activeTab, setActiveTab] = useState<'heatmaps' | 'clusters' | 'trajectories' | 'riskmap'>('heatmaps');
  const [selectedRegion, setSelectedRegion] = useState<string>('all');

  useEffect(() => {
    loadHeatmaps();
    loadClusters();
    loadTrajectories();
  }, []);

  const loadHeatmaps = async () => {
    setHeatmaps([
      { heatmap_id: 'hm-001', heatmap_type: 'crime', name: 'Regional Crime Heatmap', region_codes: ['CA-METRO', 'CA-COUNTY', 'CA-EAST'], total_incidents: 1245, max_value: 45, avg_value: 12.3, created_at: new Date().toISOString() },
      { heatmap_id: 'hm-002', heatmap_type: 'violence', name: 'Violence Hotspots', region_codes: ['CA-METRO', 'CA-COUNTY'], total_incidents: 342, max_value: 18, avg_value: 4.2, created_at: new Date().toISOString() },
      { heatmap_id: 'hm-003', heatmap_type: 'property_crime', name: 'Property Crime Distribution', region_codes: ['CA-METRO', 'CA-COUNTY', 'CA-EAST', 'CA-WEST'], total_incidents: 876, max_value: 32, avg_value: 8.7, created_at: new Date().toISOString() },
      { heatmap_id: 'hm-004', heatmap_type: 'shots_fired', name: 'ShotSpotter Activations', region_codes: ['CA-METRO'], total_incidents: 156, max_value: 12, avg_value: 2.1, created_at: new Date().toISOString() },
    ]);
  };

  const loadClusters = async () => {
    setClusters([
      { cluster_id: 'cl-001', cluster_type: 'emerging', name: 'Downtown Vehicle Burglaries', center_lat: 34.0522, center_lon: -118.2437, radius_km: 1.2, jurisdictions: ['CA-METRO', 'CA-COUNTY'], incident_count: 45, incident_count_7d: 18, trend: 'increasing_fast', trend_percent: 35, risk_level: 'high', crime_types: ['burglary', 'theft'] },
      { cluster_id: 'cl-002', cluster_type: 'active', name: 'East Side Robberies', center_lat: 34.0622, center_lon: -118.2337, radius_km: 0.8, jurisdictions: ['CA-EAST'], incident_count: 28, incident_count_7d: 8, trend: 'stable', trend_percent: 2, risk_level: 'moderate', crime_types: ['robbery'] },
      { cluster_id: 'cl-003', cluster_type: 'declining', name: 'Mall Area Shoplifting', center_lat: 34.0422, center_lon: -118.2537, radius_km: 0.5, jurisdictions: ['CA-METRO'], incident_count: 67, incident_count_7d: 5, trend: 'decreasing', trend_percent: -25, risk_level: 'low', crime_types: ['shoplifting', 'theft'] },
    ]);
  };

  const loadTrajectories = async () => {
    setTrajectories([
      { trajectory_id: 'traj-001', offender_id: 'off-001', offender_name: 'John Doe', jurisdictions_crossed: ['CA-METRO', 'CA-COUNTY', 'CA-EAST'], total_incidents: 8, risk_level: 'high', confidence: 'high', last_known_location: { latitude: 34.0522, longitude: -118.2437, timestamp: new Date(Date.now() - 2 * 3600000).toISOString() } },
      { trajectory_id: 'traj-002', offender_id: 'off-002', offender_name: 'Jane Smith', jurisdictions_crossed: ['CA-METRO', 'CA-WEST'], total_incidents: 5, risk_level: 'moderate', confidence: 'medium', last_known_location: { latitude: 34.0622, longitude: -118.2637, timestamp: new Date(Date.now() - 12 * 3600000).toISOString() } },
    ]);
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'moderate': return 'bg-yellow-500 text-black';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getTrendIcon = (trend: string) => {
    if (trend.includes('increasing')) return '📈';
    if (trend.includes('decreasing')) return '📉';
    return '➡️';
  };

  const getClusterTypeColor = (type: string) => {
    switch (type) {
      case 'emerging': return 'text-red-400';
      case 'active': return 'text-yellow-400';
      case 'declining': return 'text-green-400';
      case 'dormant': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Regional Analytics</h2>
          <p className="text-gray-400 text-sm">Multi-city crime analysis and predictions</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
          >
            <option value="all">All Regions</option>
            <option value="CA-METRO">Metro City</option>
            <option value="CA-COUNTY">County</option>
            <option value="CA-EAST">East District</option>
            <option value="CA-WEST">West District</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-blue-400">{heatmaps.length}</div>
          <div className="text-gray-400 text-sm">Active Heatmaps</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-orange-400">{clusters.filter(c => c.cluster_type === 'emerging').length}</div>
          <div className="text-gray-400 text-sm">Emerging Clusters</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-red-400">{clusters.filter(c => c.risk_level === 'high').length}</div>
          <div className="text-gray-400 text-sm">High-Risk Areas</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-purple-400">{trajectories.length}</div>
          <div className="text-gray-400 text-sm">Cross-Jurisdiction Offenders</div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="border-b border-gray-700">
          <div className="flex">
            {['heatmaps', 'clusters', 'trajectories', 'riskmap'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`px-4 py-3 text-sm font-medium capitalize ${
                  activeTab === tab
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab === 'riskmap' ? 'Risk Map' : tab}
              </button>
            ))}
          </div>
        </div>

        <div className="p-4">
          {activeTab === 'heatmaps' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="space-y-4">
                <h4 className="font-medium">Available Heatmaps</h4>
                {heatmaps.map((hm) => (
                  <div key={hm.heatmap_id} className="bg-gray-700/50 rounded p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h5 className="font-medium">{hm.name}</h5>
                        <p className="text-sm text-gray-400 capitalize">{hm.heatmap_type.replace('_', ' ')}</p>
                      </div>
                      <button className="text-sm text-blue-400 hover:text-blue-300">View</button>
                    </div>
                    <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Incidents</span>
                        <p className="font-medium">{hm.total_incidents}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Max Value</span>
                        <p className="font-medium">{hm.max_value}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Avg Value</span>
                        <p className="font-medium">{hm.avg_value.toFixed(1)}</p>
                      </div>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {hm.region_codes.map((code) => (
                        <span key={code} className="text-xs bg-gray-600 px-2 py-0.5 rounded">
                          {code}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <div className="bg-gray-700/50 rounded-lg h-96 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">🗺️</div>
                  <p className="text-gray-400">Regional Heatmap Visualization</p>
                  <p className="text-sm text-gray-500">Select a heatmap to view</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'clusters' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Crime Clusters</h4>
                <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm">
                  + Create Cluster
                </button>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {clusters.map((cluster) => (
                  <div key={cluster.cluster_id} className="bg-gray-700/50 rounded p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h5 className="font-medium">{cluster.name}</h5>
                        <p className={`text-sm capitalize ${getClusterTypeColor(cluster.cluster_type)}`}>
                          {cluster.cluster_type}
                        </p>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${getRiskColor(cluster.risk_level)}`}>
                        {cluster.risk_level}
                      </span>
                    </div>
                    <div className="mt-3 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Total Incidents</span>
                        <span>{cluster.incident_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Last 7 Days</span>
                        <span>{cluster.incident_count_7d}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Trend</span>
                        <span>
                          {getTrendIcon(cluster.trend)} {cluster.trend_percent > 0 ? '+' : ''}{cluster.trend_percent}%
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1">
                      {cluster.crime_types.map((type) => (
                        <span key={type} className="text-xs bg-gray-600 px-2 py-0.5 rounded capitalize">
                          {type}
                        </span>
                      ))}
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {cluster.jurisdictions.map((jur) => (
                        <span key={jur} className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                          {jur}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'trajectories' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Cross-Jurisdiction Offender Trajectories</h4>
              </div>
              <div className="space-y-4">
                {trajectories.map((traj) => (
                  <div key={traj.trajectory_id} className="bg-gray-700/50 rounded p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h5 className="font-medium">{traj.offender_name}</h5>
                        <p className="text-sm text-gray-400">ID: {traj.offender_id}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded ${getRiskColor(traj.risk_level)}`}>
                          {traj.risk_level} risk
                        </span>
                        <span className="text-xs bg-gray-600 px-2 py-1 rounded">
                          {traj.confidence} confidence
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Total Incidents</span>
                        <p className="font-medium">{traj.total_incidents}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Jurisdictions Crossed</span>
                        <p className="font-medium">{traj.jurisdictions_crossed.length}</p>
                      </div>
                    </div>
                    <div className="mt-3">
                      <span className="text-sm text-gray-500">Trajectory Path:</span>
                      <div className="flex items-center space-x-2 mt-1">
                        {traj.jurisdictions_crossed.map((jur, idx) => (
                          <span key={jur} className="flex items-center">
                            <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                              {jur}
                            </span>
                            {idx < traj.jurisdictions_crossed.length - 1 && (
                              <span className="mx-1 text-gray-500">→</span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                    {traj.last_known_location && (
                      <div className="mt-3 text-sm">
                        <span className="text-gray-500">Last Known Location:</span>
                        <p className="text-gray-300">
                          {traj.last_known_location.latitude.toFixed(4)}, {traj.last_known_location.longitude.toFixed(4)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(traj.last_known_location.timestamp).toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'riskmap' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2 bg-gray-700/50 rounded-lg h-96 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">🎯</div>
                  <p className="text-gray-400">Federated Risk Map</p>
                  <p className="text-sm text-gray-500">Real-time risk overlay across all jurisdictions</p>
                </div>
              </div>
              <div className="space-y-4">
                <div className="bg-gray-700/50 rounded p-4">
                  <h5 className="font-medium mb-3">Risk Legend</h5>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="w-4 h-4 bg-red-500 rounded"></span>
                      <span className="text-sm">Critical Risk</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-4 h-4 bg-orange-500 rounded"></span>
                      <span className="text-sm">High Risk</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-4 h-4 bg-yellow-500 rounded"></span>
                      <span className="text-sm">Moderate Risk</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-4 h-4 bg-green-500 rounded"></span>
                      <span className="text-sm">Low Risk</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-4 h-4 bg-gray-500 rounded"></span>
                      <span className="text-sm">Minimal Risk</span>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-700/50 rounded p-4">
                  <h5 className="font-medium mb-3">Data Sources</h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Crime History</span>
                      <span>30%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Recent Incidents</span>
                      <span>25%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Environmental</span>
                      <span>15%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Time of Day</span>
                      <span>10%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Special Events</span>
                      <span>10%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Officer Presence</span>
                      <span>10%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

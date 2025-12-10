'use client';

import React, { useState, useEffect } from 'react';

interface CrisisAlert {
  alert_id: string;
  crisis_type: string;
  severity: string;
  alert_level: string;
  title: string;
  description: string;
  location: {
    lat: number;
    lng: number;
    address?: string;
  };
  affected_area_km2: number;
  population_at_risk: number;
  recommendations: string[];
  created_at: string;
}

interface Storm {
  storm_id: string;
  name: string;
  category: string;
  wind_speed_mph: number;
  current_position: { lat: number; lng: number };
  predicted_path: Array<{ lat: number; lng: number }>;
}

interface Fire {
  fire_id: string;
  name: string;
  area_acres: number;
  containment_percent: number;
  spread_rate: string;
  origin: { lat: number; lng: number };
}

interface CrisisMapProps {
  onAlertSelect?: (alert: CrisisAlert) => void;
}

export default function CrisisMap({ onAlertSelect }: CrisisMapProps) {
  const [alerts, setAlerts] = useState<CrisisAlert[]>([]);
  const [storms, setStorms] = useState<Storm[]>([]);
  const [fires, setFires] = useState<Fire[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<CrisisAlert | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCrisisData();
    const interval = setInterval(fetchCrisisData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchCrisisData = async () => {
    try {
      const [alertsRes, stormsRes, firesRes] = await Promise.all([
        fetch('/api/emergency/crisis/alerts'),
        fetch('/api/emergency/crisis/storms'),
        fetch('/api/emergency/crisis/fires'),
      ]);

      if (alertsRes.ok) setAlerts(await alertsRes.json());
      if (stormsRes.ok) setStorms(await stormsRes.json());
      if (firesRes.ok) setFires(await firesRes.json());
    } catch (error) {
      console.error('Failed to fetch crisis data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'catastrophic': return 'bg-purple-600';
      case 'critical': return 'bg-red-600';
      case 'severe': return 'bg-orange-500';
      case 'moderate': return 'bg-yellow-500';
      case 'minor': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getCrisisIcon = (type: string): string => {
    switch (type) {
      case 'storm': return '🌀';
      case 'flood': return '🌊';
      case 'fire': return '🔥';
      case 'earthquake': return '🌍';
      case 'explosion': return '💥';
      default: return '⚠️';
    }
  };

  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter(a => a.crisis_type === filter);

  const handleAlertClick = (alert: CrisisAlert) => {
    setSelectedAlert(alert);
    onAlertSelect?.(alert);
  };

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 h-full flex items-center justify-center">
        <div className="text-gray-400">Loading crisis data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>🗺️</span> Crisis Map
        </h2>
        <div className="flex items-center gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-gray-800 text-white px-3 py-1 rounded text-sm"
          >
            <option value="all">All Crises</option>
            <option value="storm">Storms</option>
            <option value="flood">Floods</option>
            <option value="fire">Fires</option>
            <option value="earthquake">Earthquakes</option>
            <option value="explosion">Explosions</option>
          </select>
          <button
            onClick={fetchCrisisData}
            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-gray-800 rounded-lg p-4 relative">
          <div className="absolute inset-0 flex items-center justify-center text-gray-600">
            <div className="text-center">
              <div className="text-6xl mb-2">🗺️</div>
              <div>Interactive Map View</div>
              <div className="text-sm text-gray-500 mt-2">
                {filteredAlerts.length} active alerts
              </div>
            </div>
          </div>

          <div className="absolute top-4 left-4 space-y-2">
            {storms.map(storm => (
              <div key={storm.storm_id} className="bg-blue-900/80 px-3 py-2 rounded text-sm">
                <div className="text-blue-300 font-medium">🌀 {storm.name}</div>
                <div className="text-gray-400 text-xs">
                  Cat {storm.category} • {storm.wind_speed_mph} mph
                </div>
              </div>
            ))}
          </div>

          <div className="absolute top-4 right-4 space-y-2">
            {fires.slice(0, 3).map(fire => (
              <div key={fire.fire_id} className="bg-red-900/80 px-3 py-2 rounded text-sm">
                <div className="text-red-300 font-medium">🔥 {fire.name}</div>
                <div className="text-gray-400 text-xs">
                  {fire.area_acres.toLocaleString()} acres • {fire.containment_percent}% contained
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 overflow-y-auto">
          <h3 className="text-white font-medium mb-3">Active Alerts</h3>
          <div className="space-y-2">
            {filteredAlerts.length === 0 ? (
              <div className="text-gray-500 text-sm text-center py-4">
                No active alerts
              </div>
            ) : (
              filteredAlerts.map(alert => (
                <div
                  key={alert.alert_id}
                  onClick={() => handleAlertClick(alert)}
                  className={`p-3 rounded cursor-pointer transition-colors ${
                    selectedAlert?.alert_id === alert.alert_id
                      ? 'bg-gray-700 ring-2 ring-blue-500'
                      : 'bg-gray-700/50 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <span className="text-lg">{getCrisisIcon(alert.crisis_type)}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium text-sm truncate">
                          {alert.title}
                        </span>
                        <span className={`px-1.5 py-0.5 rounded text-xs text-white ${getSeverityColor(alert.severity)}`}>
                          {alert.severity}
                        </span>
                      </div>
                      <div className="text-gray-400 text-xs mt-1">
                        {alert.population_at_risk.toLocaleString()} at risk
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {selectedAlert && (
        <div className="mt-4 bg-gray-800 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-white font-medium flex items-center gap-2">
                {getCrisisIcon(selectedAlert.crisis_type)} {selectedAlert.title}
              </h3>
              <p className="text-gray-400 text-sm mt-1">{selectedAlert.description}</p>
            </div>
            <button
              onClick={() => setSelectedAlert(null)}
              className="text-gray-500 hover:text-white"
            >
              ✕
            </button>
          </div>
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="bg-gray-700/50 p-3 rounded">
              <div className="text-gray-400 text-xs">Severity</div>
              <div className={`text-sm font-medium ${
                selectedAlert.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
              }`}>
                {selectedAlert.severity.toUpperCase()}
              </div>
            </div>
            <div className="bg-gray-700/50 p-3 rounded">
              <div className="text-gray-400 text-xs">Alert Level</div>
              <div className="text-white text-sm font-medium">{selectedAlert.alert_level}</div>
            </div>
            <div className="bg-gray-700/50 p-3 rounded">
              <div className="text-gray-400 text-xs">Affected Area</div>
              <div className="text-white text-sm font-medium">{selectedAlert.affected_area_km2} km²</div>
            </div>
            <div className="bg-gray-700/50 p-3 rounded">
              <div className="text-gray-400 text-xs">Population at Risk</div>
              <div className="text-white text-sm font-medium">
                {selectedAlert.population_at_risk.toLocaleString()}
              </div>
            </div>
          </div>
          {selectedAlert.recommendations.length > 0 && (
            <div className="mt-4">
              <div className="text-gray-400 text-xs mb-2">Recommendations</div>
              <ul className="text-sm text-gray-300 space-y-1">
                {selectedAlert.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-400">•</span> {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

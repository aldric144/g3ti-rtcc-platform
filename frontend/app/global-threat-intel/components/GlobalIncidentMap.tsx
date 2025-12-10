'use client';

import { useState, useEffect } from 'react';

interface GlobalIncident {
  incident_id: string;
  incident_type: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  source: string;
  country: string;
  region: string;
  latitude: number;
  longitude: number;
  casualties: number;
  injuries: number;
  reported_at: string;
}

interface CrisisAlert {
  alert_id: string;
  title: string;
  alert_level: string;
  affected_countries: string[];
  is_active: boolean;
  issued_at: string;
}

interface Props {
  compact?: boolean;
}

export default function GlobalIncidentMap({ compact = false }: Props) {
  const [incidents, setIncidents] = useState<GlobalIncident[]>([]);
  const [alerts, setAlerts] = useState<CrisisAlert[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<GlobalIncident | null>(null);
  const [activeView, setActiveView] = useState<'map' | 'list' | 'alerts'>('map');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockIncidents: GlobalIncident[] = [
      {
        incident_id: 'inc-001',
        incident_type: 'terrorism',
        title: 'Suspected Terrorist Attack',
        description: 'Multiple explosions reported in city center...',
        severity: 'catastrophic',
        status: 'ongoing',
        source: 'dhs',
        country: 'United States',
        region: 'Northeast',
        latitude: 40.7128,
        longitude: -74.006,
        casualties: 12,
        injuries: 45,
        reported_at: new Date().toISOString(),
      },
      {
        incident_id: 'inc-002',
        incident_type: 'earthquake',
        title: 'Major Earthquake',
        description: '7.2 magnitude earthquake struck coastal region...',
        severity: 'severe',
        status: 'ongoing',
        source: 'usgs',
        country: 'Japan',
        region: 'Kanto',
        latitude: 35.6762,
        longitude: 139.6503,
        casualties: 0,
        injuries: 120,
        reported_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        incident_id: 'inc-003',
        incident_type: 'cyber_attack',
        title: 'Critical Infrastructure Cyber Attack',
        description: 'Power grid systems compromised in multiple states...',
        severity: 'severe',
        status: 'investigating',
        source: 'cisa',
        country: 'United States',
        region: 'Midwest',
        latitude: 41.8781,
        longitude: -87.6298,
        casualties: 0,
        injuries: 0,
        reported_at: new Date(Date.now() - 7200000).toISOString(),
      },
      {
        incident_id: 'inc-004',
        incident_type: 'civil_unrest',
        title: 'Large Scale Protests',
        description: 'Thousands gathered in downtown area, some violence reported...',
        severity: 'moderate',
        status: 'monitoring',
        source: 'custom',
        country: 'France',
        region: 'Ile-de-France',
        latitude: 48.8566,
        longitude: 2.3522,
        casualties: 0,
        injuries: 15,
        reported_at: new Date(Date.now() - 14400000).toISOString(),
      },
    ];

    const mockAlerts: CrisisAlert[] = [
      {
        alert_id: 'alert-001',
        title: 'Elevated Terrorism Threat Level',
        alert_level: 'warning',
        affected_countries: ['United States', 'United Kingdom', 'France'],
        is_active: true,
        issued_at: new Date().toISOString(),
      },
      {
        alert_id: 'alert-002',
        title: 'Tsunami Warning - Pacific Region',
        alert_level: 'emergency',
        affected_countries: ['Japan', 'Philippines', 'Indonesia'],
        is_active: true,
        issued_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        alert_id: 'alert-003',
        title: 'Cyber Threat Advisory',
        alert_level: 'advisory',
        affected_countries: ['United States', 'Canada'],
        is_active: true,
        issued_at: new Date(Date.now() - 7200000).toISOString(),
      },
    ];

    setTimeout(() => {
      setIncidents(mockIncidents);
      setAlerts(mockAlerts);
      setLoading(false);
    }, 500);
  }, []);

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      minor: 'text-blue-400 bg-blue-500/20',
      moderate: 'text-yellow-400 bg-yellow-500/20',
      severe: 'text-orange-400 bg-orange-500/20',
      catastrophic: 'text-red-500 bg-red-600/30',
    };
    return colors[severity] || 'text-gray-400 bg-gray-500/20';
  };

  const getAlertLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      advisory: 'text-blue-400 bg-blue-500/20 border-blue-500',
      watch: 'text-yellow-400 bg-yellow-500/20 border-yellow-500',
      warning: 'text-orange-400 bg-orange-500/20 border-orange-500',
      emergency: 'text-red-500 bg-red-600/30 border-red-500',
    };
    return colors[level] || 'text-gray-400 bg-gray-500/20 border-gray-500';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      ongoing: 'text-red-400 bg-red-500/20',
      investigating: 'text-orange-400 bg-orange-500/20',
      monitoring: 'text-yellow-400 bg-yellow-500/20',
      resolved: 'text-green-400 bg-green-500/20',
    };
    return colors[status] || 'text-gray-400 bg-gray-500/20';
  };

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-green-400">
            Global Incident Map
          </h3>
        </div>
        <div className="h-64 bg-gray-900 relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-2">🌍</div>
              <p className="text-gray-400 text-sm">Interactive Map View</p>
              <p className="text-green-400 text-xs mt-1">
                {incidents.length} active incidents
              </p>
            </div>
          </div>
          {incidents.slice(0, 3).map((incident, idx) => (
            <div
              key={incident.incident_id}
              className={`absolute w-4 h-4 rounded-full animate-pulse ${
                incident.severity === 'catastrophic'
                  ? 'bg-red-500'
                  : incident.severity === 'severe'
                    ? 'bg-orange-500'
                    : 'bg-yellow-500'
              }`}
              style={{
                left: `${20 + idx * 25}%`,
                top: `${30 + idx * 15}%`,
              }}
            ></div>
          ))}
        </div>
        <div className="p-4">
          <div className="space-y-2">
            {incidents.slice(0, 2).map((incident) => (
              <div
                key={incident.incident_id}
                className="flex justify-between items-center text-sm"
              >
                <span className="text-gray-300 truncate">{incident.title}</span>
                <span
                  className={`px-2 py-0.5 text-xs rounded ${getSeverityColor(incident.severity)}`}
                >
                  {incident.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-green-400">
            Global Incident Monitor
          </h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveView('map')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'map'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Map View
            </button>
            <button
              onClick={() => setActiveView('list')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'list'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Incident List
            </button>
            <button
              onClick={() => setActiveView('alerts')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'alerts'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Crisis Alerts
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
          </div>
        ) : activeView === 'map' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2 h-96 bg-gray-900 rounded-lg relative overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-8xl mb-4">🌍</div>
                  <p className="text-gray-400">Interactive Global Map</p>
                  <p className="text-green-400 text-sm mt-2">
                    {incidents.length} incidents tracked worldwide
                  </p>
                </div>
              </div>
              {incidents.map((incident, idx) => (
                <div
                  key={incident.incident_id}
                  onClick={() => setSelectedIncident(incident)}
                  className={`absolute cursor-pointer transition-transform hover:scale-150 ${
                    selectedIncident?.incident_id === incident.incident_id
                      ? 'scale-150'
                      : ''
                  }`}
                  style={{
                    left: `${15 + idx * 20}%`,
                    top: `${20 + idx * 18}%`,
                  }}
                >
                  <div
                    className={`w-6 h-6 rounded-full animate-pulse flex items-center justify-center ${
                      incident.severity === 'catastrophic'
                        ? 'bg-red-500'
                        : incident.severity === 'severe'
                          ? 'bg-orange-500'
                          : 'bg-yellow-500'
                    }`}
                  >
                    <span className="text-xs text-white font-bold">
                      {idx + 1}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="space-y-4">
              {selectedIncident ? (
                <div className="bg-gray-700/50 rounded-lg p-4 border border-green-500">
                  <h3 className="font-semibold text-white mb-2">
                    {selectedIncident.title}
                  </h3>
                  <p className="text-sm text-gray-300 mb-3">
                    {selectedIncident.description}
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Type:</span>
                      <span className="text-white capitalize">
                        {selectedIncident.incident_type.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Location:</span>
                      <span className="text-white">
                        {selectedIncident.region}, {selectedIncident.country}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Severity:</span>
                      <span
                        className={`px-2 py-0.5 rounded ${getSeverityColor(selectedIncident.severity)}`}
                      >
                        {selectedIncident.severity}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Status:</span>
                      <span
                        className={`px-2 py-0.5 rounded ${getStatusColor(selectedIncident.status)}`}
                      >
                        {selectedIncident.status}
                      </span>
                    </div>
                    {(selectedIncident.casualties > 0 ||
                      selectedIncident.injuries > 0) && (
                      <div className="pt-2 border-t border-gray-600">
                        <div className="flex justify-between text-red-400">
                          <span>Casualties:</span>
                          <span>{selectedIncident.casualties}</span>
                        </div>
                        <div className="flex justify-between text-orange-400">
                          <span>Injuries:</span>
                          <span>{selectedIncident.injuries}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="bg-gray-700/50 rounded-lg p-4 text-center">
                  <p className="text-gray-400">
                    Click on an incident marker to view details
                  </p>
                </div>
              )}
              <div className="bg-gray-700/50 rounded-lg p-4">
                <h4 className="font-semibold text-white mb-3">Quick Stats</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-800 p-2 rounded text-center">
                    <p className="text-2xl font-bold text-green-400">
                      {incidents.length}
                    </p>
                    <p className="text-xs text-gray-400">Active Incidents</p>
                  </div>
                  <div className="bg-gray-800 p-2 rounded text-center">
                    <p className="text-2xl font-bold text-red-400">
                      {incidents.filter((i) => i.severity === 'catastrophic').length}
                    </p>
                    <p className="text-xs text-gray-400">Critical</p>
                  </div>
                  <div className="bg-gray-800 p-2 rounded text-center">
                    <p className="text-2xl font-bold text-orange-400">
                      {alerts.filter((a) => a.is_active).length}
                    </p>
                    <p className="text-xs text-gray-400">Active Alerts</p>
                  </div>
                  <div className="bg-gray-800 p-2 rounded text-center">
                    <p className="text-2xl font-bold text-yellow-400">
                      {new Set(incidents.map((i) => i.country)).size}
                    </p>
                    <p className="text-xs text-gray-400">Countries</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : activeView === 'list' ? (
          <div className="space-y-4">
            {incidents.map((incident) => (
              <div
                key={incident.incident_id}
                className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-green-500 transition-colors"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-white">{incident.title}</h3>
                    <p className="text-sm text-gray-400">
                      {incident.region}, {incident.country} •{' '}
                      {incident.incident_type.replace(/_/g, ' ')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-1 text-xs rounded ${getStatusColor(incident.status)}`}
                    >
                      {incident.status}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs rounded ${getSeverityColor(incident.severity)}`}
                    >
                      {incident.severity}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-300 mb-3">{incident.description}</p>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex space-x-4">
                    <span className="text-gray-400">
                      Source:{' '}
                      <span className="text-white uppercase">{incident.source}</span>
                    </span>
                    {incident.casualties > 0 && (
                      <span className="text-red-400">
                        {incident.casualties} casualties
                      </span>
                    )}
                    {incident.injuries > 0 && (
                      <span className="text-orange-400">
                        {incident.injuries} injuries
                      </span>
                    )}
                  </div>
                  <span className="text-gray-500">
                    {new Date(incident.reported_at).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div
                key={alert.alert_id}
                className={`p-4 rounded-lg border-l-4 ${getAlertLevelColor(alert.alert_level)}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-white">{alert.title}</h3>
                  <span
                    className={`px-3 py-1 text-sm rounded uppercase ${getAlertLevelColor(alert.alert_level)}`}
                  >
                    {alert.alert_level}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 mb-3">
                  {alert.affected_countries.map((country, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 text-xs bg-gray-600 rounded"
                    >
                      {country}
                    </span>
                  ))}
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span
                    className={`px-2 py-1 rounded ${
                      alert.is_active
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-gray-500/20 text-gray-400'
                    }`}
                  >
                    {alert.is_active ? 'ACTIVE' : 'INACTIVE'}
                  </span>
                  <span className="text-gray-500">
                    Issued: {new Date(alert.issued_at).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

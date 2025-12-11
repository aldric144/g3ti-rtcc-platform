'use client';

import { useState } from 'react';

interface TimelineEvent {
  id: string;
  timestamp: string;
  type: 'deployment' | 'failover' | 'crash' | 'update' | 'maintenance' | 'security';
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical' | 'success';
  service?: string;
  operator?: string;
  duration?: number;
}

const mockTimelineEvents: TimelineEvent[] = [
  { id: '1', timestamp: '2024-12-11T06:00:00Z', type: 'deployment', title: 'Phase 27 Deployment', description: 'Enterprise Infrastructure module deployed successfully', severity: 'success', service: 'infra-service', operator: 'devin-ai' },
  { id: '2', timestamp: '2024-12-11T05:30:00Z', type: 'update', title: 'AI Engine Model Update', description: 'Predictive policing model v3.2.1 deployed', severity: 'success', service: 'ai-engine', operator: 'system' },
  { id: '3', timestamp: '2024-12-10T22:15:00Z', type: 'maintenance', title: 'Scheduled Maintenance', description: 'Database optimization and index rebuild', severity: 'info', service: 'postgres-primary', operator: 'admin_johnson', duration: 45 },
  { id: '4', timestamp: '2024-12-10T14:30:00Z', type: 'failover', title: 'Region Failover Test', description: 'Successful failover from us-gov-east-1 to us-gov-west-1', severity: 'success', service: 'multi-region', operator: 'admin_johnson', duration: 45 },
  { id: '5', timestamp: '2024-12-10T08:00:00Z', type: 'deployment', title: 'Phase 26 Deployment', description: 'Ethics Guardian module deployed', severity: 'success', service: 'ethics-guardian', operator: 'devin-ai' },
  { id: '6', timestamp: '2024-12-09T16:45:00Z', type: 'security', title: 'Security Alert', description: 'Blocked unauthorized access attempt from foreign IP', severity: 'warning', service: 'zero-trust-gateway' },
  { id: '7', timestamp: '2024-12-09T12:00:00Z', type: 'update', title: 'Certificate Renewal', description: 'TLS certificates renewed for all services', severity: 'success', service: 'api-gateway', operator: 'system' },
  { id: '8', timestamp: '2024-12-08T09:30:00Z', type: 'crash', title: 'Service Recovery', description: 'WebSocket broker recovered from memory exhaustion', severity: 'critical', service: 'websocket-broker', duration: 120 },
  { id: '9', timestamp: '2024-12-07T18:00:00Z', type: 'deployment', title: 'Phase 25 Deployment', description: 'AI City Constitution module deployed', severity: 'success', service: 'city-governance', operator: 'devin-ai' },
  { id: '10', timestamp: '2024-12-06T14:00:00Z', type: 'maintenance', title: 'Elasticsearch Reindex', description: 'Full reindex of investigation documents', severity: 'info', service: 'elasticsearch', operator: 'admin_smith', duration: 180 },
];

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'deployment': return '🚀';
    case 'failover': return '🔄';
    case 'crash': return '💥';
    case 'update': return '📦';
    case 'maintenance': return '🔧';
    case 'security': return '🔒';
    default: return '📋';
  }
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'success': return 'border-green-500 bg-green-500/10';
    case 'info': return 'border-blue-500 bg-blue-500/10';
    case 'warning': return 'border-yellow-500 bg-yellow-500/10';
    case 'critical': return 'border-red-500 bg-red-500/10';
    default: return 'border-gray-500 bg-gray-500/10';
  }
};

const getTypeColor = (type: string) => {
  switch (type) {
    case 'deployment': return 'bg-purple-600/20 text-purple-400';
    case 'failover': return 'bg-blue-600/20 text-blue-400';
    case 'crash': return 'bg-red-600/20 text-red-400';
    case 'update': return 'bg-green-600/20 text-green-400';
    case 'maintenance': return 'bg-yellow-600/20 text-yellow-400';
    case 'security': return 'bg-orange-600/20 text-orange-400';
    default: return 'bg-gray-600/20 text-gray-400';
  }
};

export default function InfrastructureTimeline() {
  const [events] = useState<TimelineEvent[]>(mockTimelineEvents);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');

  const eventTypes = ['all', 'deployment', 'failover', 'crash', 'update', 'maintenance', 'security'];
  const severities = ['all', 'success', 'info', 'warning', 'critical'];

  const filteredEvents = events.filter(event => {
    if (filterType !== 'all' && event.type !== filterType) return false;
    if (filterSeverity !== 'all' && event.severity !== filterSeverity) return false;
    return true;
  });

  const stats = {
    deployments: events.filter(e => e.type === 'deployment').length,
    failovers: events.filter(e => e.type === 'failover').length,
    crashes: events.filter(e => e.type === 'crash').length,
    updates: events.filter(e => e.type === 'update').length,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Infrastructure Timeline</h2>
        <div className="flex items-center space-x-4">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
          >
            {eventTypes.map(type => (
              <option key={type} value={type}>
                {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
          >
            {severities.map(sev => (
              <option key={sev} value={sev}>
                {sev === 'all' ? 'All Severities' : sev.charAt(0).toUpperCase() + sev.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-purple-700">
          <h3 className="text-sm text-gray-400 mb-1">Deployments (30d)</h3>
          <p className="text-3xl font-bold text-purple-400">{stats.deployments}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-blue-700">
          <h3 className="text-sm text-gray-400 mb-1">Failovers (30d)</h3>
          <p className="text-3xl font-bold text-blue-400">{stats.failovers}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <h3 className="text-sm text-gray-400 mb-1">Crashes (30d)</h3>
          <p className="text-3xl font-bold text-red-400">{stats.crashes}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
          <h3 className="text-sm text-gray-400 mb-1">Updates (30d)</h3>
          <p className="text-3xl font-bold text-green-400">{stats.updates}</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-medium mb-4">Event Timeline</h3>
        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-700"></div>
          <div className="space-y-4">
            {filteredEvents.map((event, index) => (
              <div key={event.id} className="relative flex items-start">
                <div className={`absolute left-6 w-5 h-5 rounded-full flex items-center justify-center text-xs ${getSeverityColor(event.severity)} border-2`}>
                  {getTypeIcon(event.type)}
                </div>
                <div className={`ml-16 flex-1 rounded-lg p-4 border-l-4 ${getSeverityColor(event.severity)}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-0.5 rounded text-xs ${getTypeColor(event.type)}`}>
                        {event.type.toUpperCase()}
                      </span>
                      <h4 className="font-medium">{event.title}</h4>
                    </div>
                    <span className="text-sm text-gray-400">
                      {new Date(event.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300 mb-2">{event.description}</p>
                  <div className="flex items-center space-x-4 text-xs text-gray-400">
                    {event.service && (
                      <span className="flex items-center">
                        <span className="mr-1">Service:</span>
                        <span className="text-blue-400">{event.service}</span>
                      </span>
                    )}
                    {event.operator && (
                      <span className="flex items-center">
                        <span className="mr-1">Operator:</span>
                        <span className="text-green-400">{event.operator}</span>
                      </span>
                    )}
                    {event.duration && (
                      <span className="flex items-center">
                        <span className="mr-1">Duration:</span>
                        <span className="text-yellow-400">{event.duration}s</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-medium mb-4">Deployment History</h3>
          <div className="space-y-2">
            {events.filter(e => e.type === 'deployment').slice(0, 5).map((event) => (
              <div key={event.id} className="flex items-center justify-between bg-gray-900 rounded-lg p-3">
                <div>
                  <p className="text-sm font-medium">{event.title}</p>
                  <p className="text-xs text-gray-400">{event.service}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400">{new Date(event.timestamp).toLocaleDateString()}</p>
                  <span className="text-xs text-green-400">Success</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-medium mb-4">System Health Trend</h3>
          <div className="h-48 flex items-end justify-between space-x-2">
            {[98, 99, 97, 100, 99, 98, 100, 99, 100, 99, 98, 100].map((value, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div
                  className={`w-full rounded-t ${
                    value >= 99 ? 'bg-green-500' : value >= 95 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ height: `${value}%` }}
                ></div>
                <span className="text-xs text-gray-400 mt-1">{index + 1}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
            <span>Last 12 hours</span>
            <span>Avg: 98.9% uptime</span>
          </div>
        </div>
      </div>
    </div>
  );
}

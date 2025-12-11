'use client';

import { useState, useEffect } from 'react';

interface RegionNode {
  id: string;
  name: string;
  status: 'active' | 'standby' | 'syncing' | 'offline';
  isPrimary: boolean;
  endpoint: string;
  latency: number;
  syncLag: number;
  services: { name: string; status: string }[];
}

interface FailoverEvent {
  id: string;
  timestamp: string;
  fromRegion: string;
  toRegion: string;
  reason: string;
  duration: number;
  success: boolean;
}

const mockRegions: RegionNode[] = [
  {
    id: 'us-gov-east-1',
    name: 'AWS GovCloud East',
    status: 'active',
    isPrimary: true,
    endpoint: 'https://rtcc-east.rivierabeach.gov',
    latency: 12,
    syncLag: 0,
    services: [
      { name: 'API Gateway', status: 'healthy' },
      { name: 'AI Engine', status: 'healthy' },
      { name: 'Database', status: 'healthy' },
      { name: 'WebSocket', status: 'healthy' },
    ],
  },
  {
    id: 'us-gov-west-1',
    name: 'AWS GovCloud West',
    status: 'standby',
    isPrimary: false,
    endpoint: 'https://rtcc-west.rivierabeach.gov',
    latency: 45,
    syncLag: 150,
    services: [
      { name: 'API Gateway', status: 'standby' },
      { name: 'AI Engine', status: 'standby' },
      { name: 'Database', status: 'replica' },
      { name: 'WebSocket', status: 'standby' },
    ],
  },
];

const mockFailoverEvents: FailoverEvent[] = [
  { id: '1', timestamp: '2024-12-10T14:30:00Z', fromRegion: 'us-gov-east-1', toRegion: 'us-gov-west-1', reason: 'Scheduled maintenance', duration: 45000, success: true },
  { id: '2', timestamp: '2024-12-05T08:15:00Z', fromRegion: 'us-gov-west-1', toRegion: 'us-gov-east-1', reason: 'Maintenance complete', duration: 38000, success: true },
  { id: '3', timestamp: '2024-11-28T22:45:00Z', fromRegion: 'us-gov-east-1', toRegion: 'us-gov-west-1', reason: 'Health check failure', duration: 52000, success: true },
];

export default function HighAvailabilityDashboard() {
  const [regions, setRegions] = useState<RegionNode[]>(mockRegions);
  const [failoverEvents] = useState<FailoverEvent[]>(mockFailoverEvents);
  const [failoverReadiness, setFailoverReadiness] = useState(0.95);

  useEffect(() => {
    const interval = setInterval(() => {
      setRegions(prev => prev.map(region => ({
        ...region,
        latency: Math.max(5, region.latency + (Math.random() - 0.5) * 5),
        syncLag: region.isPrimary ? 0 : Math.max(0, region.syncLag + (Math.random() - 0.5) * 50),
      })));
      setFailoverReadiness(prev => Math.max(0.8, Math.min(1, prev + (Math.random() - 0.5) * 0.05)));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'healthy':
        return 'text-green-400';
      case 'standby':
      case 'replica':
        return 'text-blue-400';
      case 'syncing':
        return 'text-yellow-400';
      case 'offline':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">High Availability Dashboard</h2>
        <div className="flex items-center space-x-4">
          <div className="bg-gray-800 rounded-lg px-4 py-2 border border-gray-700">
            <span className="text-sm text-gray-400">Failover Readiness:</span>
            <span className={`ml-2 font-bold ${
              failoverReadiness >= 0.9 ? 'text-green-400' :
              failoverReadiness >= 0.7 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {(failoverReadiness * 100).toFixed(1)}%
            </span>
          </div>
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            Test Failover
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {regions.map((region) => (
          <div
            key={region.id}
            className={`bg-gray-800 rounded-lg p-6 border ${
              region.isPrimary ? 'border-green-500' : 'border-gray-700'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-lg">{region.name}</h3>
                <p className="text-sm text-gray-400">{region.id}</p>
              </div>
              <div className="text-right">
                {region.isPrimary && (
                  <span className="bg-green-600 text-xs px-2 py-1 rounded-full">PRIMARY</span>
                )}
                <p className={`text-sm mt-1 capitalize ${getStatusColor(region.status)}`}>
                  {region.status}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-900 rounded-lg p-3">
                <span className="text-xs text-gray-400">Latency</span>
                <p className={`text-xl font-bold ${
                  region.latency < 20 ? 'text-green-400' :
                  region.latency < 50 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {region.latency.toFixed(0)}ms
                </p>
              </div>
              <div className="bg-gray-900 rounded-lg p-3">
                <span className="text-xs text-gray-400">Sync Lag</span>
                <p className={`text-xl font-bold ${
                  region.syncLag < 100 ? 'text-green-400' :
                  region.syncLag < 500 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {region.syncLag.toFixed(0)}ms
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <span className="text-sm text-gray-400">Services</span>
              <div className="grid grid-cols-2 gap-2">
                {region.services.map((service, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-900 rounded px-3 py-2">
                    <span className="text-sm">{service.name}</span>
                    <span className={`text-xs capitalize ${getStatusColor(service.status)}`}>
                      {service.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-700">
              <span className="text-xs text-gray-400">Endpoint:</span>
              <p className="text-sm font-mono text-blue-400">{region.endpoint}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-medium mb-2">RTO Target</h3>
          <p className="text-3xl font-bold text-green-400">5 min</p>
          <p className="text-sm text-gray-400">Recovery Time Objective</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-medium mb-2">RPO Target</h3>
          <p className="text-3xl font-bold text-green-400">1 min</p>
          <p className="text-sm text-gray-400">Recovery Point Objective</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-medium mb-2">Uptime (30d)</h3>
          <p className="text-3xl font-bold text-green-400">99.99%</p>
          <p className="text-sm text-gray-400">Service Availability</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-medium mb-4">Recent Failover Events</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-2">Timestamp</th>
                <th className="pb-2">From</th>
                <th className="pb-2">To</th>
                <th className="pb-2">Reason</th>
                <th className="pb-2">Duration</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {failoverEvents.map((event) => (
                <tr key={event.id} className="border-b border-gray-700/50">
                  <td className="py-3">{new Date(event.timestamp).toLocaleString()}</td>
                  <td className="py-3">{event.fromRegion}</td>
                  <td className="py-3">{event.toRegion}</td>
                  <td className="py-3">{event.reason}</td>
                  <td className="py-3">{(event.duration / 1000).toFixed(1)}s</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      event.success ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
                    }`}>
                      {event.success ? 'Success' : 'Failed'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

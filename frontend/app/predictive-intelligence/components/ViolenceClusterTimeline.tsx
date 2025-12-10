'use client';

import { useState, useEffect } from 'react';

interface ViolenceCluster {
  cluster_id: string;
  name: string;
  center_lat: number;
  center_lon: number;
  radius_m: number;
  incident_count: number;
  severity: string;
  trend: string;
  first_incident: string;
  last_incident: string;
  predicted_next: string | null;
  confidence: number;
}

interface TimelineEvent {
  event_id: string;
  cluster_id: string;
  timestamp: string;
  event_type: string;
  severity: string;
  description: string;
}

export default function ViolenceClusterTimeline() {
  const [clusters, setClusters] = useState<ViolenceCluster[]>([]);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    const mockClusters: ViolenceCluster[] = [
      {
        cluster_id: 'cluster-001',
        name: 'Downtown Violence Cluster',
        center_lat: 33.749,
        center_lon: -84.388,
        radius_m: 500,
        incident_count: 23,
        severity: 'HIGH',
        trend: 'INCREASING',
        first_incident: '2024-10-15',
        last_incident: '2024-12-08',
        predicted_next: '2024-12-12',
        confidence: 78,
      },
      {
        cluster_id: 'cluster-002',
        name: 'Westside Hotspot',
        center_lat: 33.755,
        center_lon: -84.420,
        radius_m: 750,
        incident_count: 15,
        severity: 'MODERATE',
        trend: 'STABLE',
        first_incident: '2024-09-20',
        last_incident: '2024-12-05',
        predicted_next: null,
        confidence: 62,
      },
      {
        cluster_id: 'cluster-003',
        name: 'Airport Area Cluster',
        center_lat: 33.640,
        center_lon: -84.428,
        radius_m: 1000,
        incident_count: 31,
        severity: 'CRITICAL',
        trend: 'INCREASING',
        first_incident: '2024-08-01',
        last_incident: '2024-12-09',
        predicted_next: '2024-12-11',
        confidence: 85,
      },
    ];

    const mockEvents: TimelineEvent[] = [
      { event_id: 'evt-001', cluster_id: 'cluster-001', timestamp: '2024-12-08T22:30:00Z', event_type: 'ASSAULT', severity: 'HIGH', description: 'Aggravated assault near transit station' },
      { event_id: 'evt-002', cluster_id: 'cluster-003', timestamp: '2024-12-09T01:15:00Z', event_type: 'SHOOTING', severity: 'CRITICAL', description: 'Shots fired in parking lot' },
      { event_id: 'evt-003', cluster_id: 'cluster-001', timestamp: '2024-12-07T19:45:00Z', event_type: 'ROBBERY', severity: 'MODERATE', description: 'Armed robbery at convenience store' },
      { event_id: 'evt-004', cluster_id: 'cluster-002', timestamp: '2024-12-05T23:00:00Z', event_type: 'ASSAULT', severity: 'MODERATE', description: 'Domestic violence call' },
      { event_id: 'evt-005', cluster_id: 'cluster-003', timestamp: '2024-12-08T03:30:00Z', event_type: 'SHOOTING', severity: 'HIGH', description: 'Drive-by shooting reported' },
    ];

    setClusters(mockClusters);
    setEvents(mockEvents);
  }, [timeRange]);

  const severityColors: Record<string, string> = {
    LOW: 'bg-blue-500',
    MODERATE: 'bg-yellow-500',
    HIGH: 'bg-orange-500',
    CRITICAL: 'bg-red-500',
  };

  const filteredEvents = selectedCluster
    ? events.filter((e) => e.cluster_id === selectedCluster)
    : events;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Violence Cluster Analysis</h2>
        <div className="flex space-x-2">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded ${
                timeRange === range ? 'bg-blue-600' : 'bg-gray-700'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {clusters.map((cluster) => (
          <button
            key={cluster.cluster_id}
            onClick={() =>
              setSelectedCluster(
                selectedCluster === cluster.cluster_id ? null : cluster.cluster_id
              )
            }
            className={`text-left p-4 rounded-lg transition-colors ${
              selectedCluster === cluster.cluster_id
                ? 'bg-blue-600'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold">{cluster.name}</div>
              <span
                className={`px-2 py-0.5 rounded text-xs ${
                  severityColors[cluster.severity]
                }`}
              >
                {cluster.severity}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-400">Incidents:</span>
                <span className="ml-1">{cluster.incident_count}</span>
              </div>
              <div>
                <span className="text-gray-400">Trend:</span>
                <span
                  className={`ml-1 ${
                    cluster.trend === 'INCREASING'
                      ? 'text-red-400'
                      : cluster.trend === 'DECREASING'
                      ? 'text-green-400'
                      : 'text-yellow-400'
                  }`}
                >
                  {cluster.trend}
                </span>
              </div>
            </div>

            {cluster.predicted_next && (
              <div className="mt-3 pt-3 border-t border-gray-600">
                <div className="text-sm">
                  <span className="text-gray-400">Predicted Next:</span>
                  <span className="ml-1 text-red-400">
                    {new Date(cluster.predicted_next).toLocaleDateString()}
                  </span>
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Confidence: {cluster.confidence}%
                </div>
              </div>
            )}
          </button>
        ))}
      </div>

      <div className="bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">
          Event Timeline
          {selectedCluster && (
            <span className="text-sm font-normal text-gray-400 ml-2">
              (Filtered by {clusters.find((c) => c.cluster_id === selectedCluster)?.name})
            </span>
          )}
        </h3>

        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-600"></div>

          <div className="space-y-4">
            {filteredEvents.map((event) => (
              <div key={event.event_id} className="relative pl-10">
                <div
                  className={`absolute left-2.5 w-3 h-3 rounded-full ${
                    severityColors[event.severity]
                  }`}
                ></div>

                <div className="bg-gray-600 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-medium">{event.event_type}</div>
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        severityColors[event.severity]
                      }`}
                    >
                      {event.severity}
                    </span>
                  </div>
                  <div className="text-sm text-gray-300">{event.description}</div>
                  <div className="text-xs text-gray-400 mt-2">
                    {new Date(event.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {filteredEvents.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            No events found for the selected criteria
          </div>
        )}
      </div>
    </div>
  );
}

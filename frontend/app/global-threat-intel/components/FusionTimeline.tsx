'use client';

import { useState, useEffect } from 'react';

interface FusionEvent {
  event_id: string;
  event_type: string;
  source_module: string;
  title: string;
  description: string;
  priority: string;
  threat_score: number;
  entity_id: string;
  entity_name: string;
  jurisdiction_codes: string[];
  timestamp: string;
  related_events: string[];
}

interface Props {
  expanded?: boolean;
}

export default function FusionTimeline({ expanded = false }: Props) {
  const [events, setEvents] = useState<FusionEvent[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockEvents: FusionEvent[] = [
      {
        event_id: 'evt-001',
        event_type: 'alert',
        source_module: 'threat_alerts',
        title: 'Critical Threat Alert Generated',
        description: 'Cross-domain fusion detected high-risk entity with connections to dark web activity and extremist networks.',
        priority: 'critical',
        threat_score: 92,
        entity_id: 'ent-001',
        entity_name: 'Subject Alpha',
        jurisdiction_codes: ['US-NY'],
        timestamp: new Date().toISOString(),
        related_events: ['evt-002', 'evt-003'],
      },
      {
        event_id: 'evt-002',
        event_type: 'signal',
        source_module: 'dark_web_monitor',
        title: 'Dark Web Signal Detected',
        description: 'Weapons trafficking discussion mentioning local area detected on dark forum.',
        priority: 'high',
        threat_score: 85,
        entity_id: 'ent-001',
        entity_name: 'Subject Alpha',
        jurisdiction_codes: ['US-NY'],
        timestamp: new Date(Date.now() - 300000).toISOString(),
        related_events: ['evt-001'],
      },
      {
        event_id: 'evt-003',
        event_type: 'network',
        source_module: 'extremist_networks',
        title: 'Network Connection Identified',
        description: 'Subject linked to known extremist channel with high influence score.',
        priority: 'high',
        threat_score: 78,
        entity_id: 'ent-001',
        entity_name: 'Subject Alpha',
        jurisdiction_codes: ['US-NY', 'US-NJ'],
        timestamp: new Date(Date.now() - 600000).toISOString(),
        related_events: ['evt-001'],
      },
      {
        event_id: 'evt-004',
        event_type: 'incident',
        source_module: 'global_incidents',
        title: 'Global Incident Correlation',
        description: 'Cyber attack pattern matches local infrastructure vulnerability assessment.',
        priority: 'moderate',
        threat_score: 65,
        entity_id: 'loc-001',
        entity_name: 'Power Grid Sector 7',
        jurisdiction_codes: ['US-CA'],
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        related_events: [],
      },
      {
        event_id: 'evt-005',
        event_type: 'spike',
        source_module: 'osint_harvester',
        title: 'Keyword Spike Detected',
        description: 'Significant increase in social media mentions of planned protest activity.',
        priority: 'moderate',
        threat_score: 55,
        entity_id: 'kw-001',
        entity_name: '#protest',
        jurisdiction_codes: ['US-DC'],
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        related_events: [],
      },
      {
        event_id: 'evt-006',
        event_type: 'score',
        source_module: 'threat_scoring_engine',
        title: 'Threat Score Updated',
        description: 'Entity threat score increased due to new intelligence from multiple sources.',
        priority: 'high',
        threat_score: 82,
        entity_id: 'ent-002',
        entity_name: 'Militia Group Beta',
        jurisdiction_codes: ['US-PA'],
        timestamp: new Date(Date.now() - 5400000).toISOString(),
        related_events: [],
      },
      {
        event_id: 'evt-007',
        event_type: 'correlation',
        source_module: 'global_incidents',
        title: 'Geo-Threat Correlation',
        description: 'Regional earthquake may impact local emergency response capabilities.',
        priority: 'low',
        threat_score: 35,
        entity_id: 'inc-002',
        entity_name: 'Japan Earthquake',
        jurisdiction_codes: ['US-HI', 'US-CA'],
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        related_events: [],
      },
    ];

    setTimeout(() => {
      setEvents(mockEvents);
      setLoading(false);
    }, 500);
  }, []);

  const getEventTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      alert: '🚨',
      signal: '📡',
      network: '🕸️',
      incident: '⚠️',
      spike: '📈',
      score: '📊',
      correlation: '🔗',
    };
    return icons[type] || '📌';
  };

  const getEventTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      alert: 'border-red-500 bg-red-500/10',
      signal: 'border-purple-500 bg-purple-500/10',
      network: 'border-amber-500 bg-amber-500/10',
      incident: 'border-green-500 bg-green-500/10',
      spike: 'border-cyan-500 bg-cyan-500/10',
      score: 'border-red-400 bg-red-400/10',
      correlation: 'border-blue-500 bg-blue-500/10',
    };
    return colors[type] || 'border-gray-500 bg-gray-500/10';
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      critical: 'text-red-500 bg-red-500/20',
      high: 'text-orange-400 bg-orange-500/20',
      moderate: 'text-yellow-400 bg-yellow-500/20',
      low: 'text-blue-400 bg-blue-500/20',
    };
    return colors[priority] || 'text-gray-400 bg-gray-500/20';
  };

  const getModuleColor = (module: string) => {
    const colors: Record<string, string> = {
      dark_web_monitor: 'text-purple-400',
      osint_harvester: 'text-cyan-400',
      extremist_networks: 'text-amber-400',
      global_incidents: 'text-green-400',
      threat_scoring_engine: 'text-red-400',
      threat_alerts: 'text-red-500',
    };
    return colors[module] || 'text-gray-400';
  };

  const filteredEvents = filter === 'all' 
    ? events 
    : events.filter(e => e.event_type === filter);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-blue-400">Fusion Timeline</h2>
          <div className="flex space-x-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-1 text-sm bg-gray-700 border border-gray-600 rounded text-white"
            >
              <option value="all">All Events</option>
              <option value="alert">Alerts</option>
              <option value="signal">Signals</option>
              <option value="network">Network</option>
              <option value="incident">Incidents</option>
              <option value="spike">Spikes</option>
              <option value="score">Scores</option>
              <option value="correlation">Correlations</option>
            </select>
          </div>
        </div>
      </div>

      <div className="p-4">
        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-700"></div>
          
          <div className="space-y-4">
            {filteredEvents.slice(0, expanded ? filteredEvents.length : 5).map((event, idx) => (
              <div key={event.event_id} className="relative pl-14">
                <div
                  className={`absolute left-4 w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                    event.priority === 'critical'
                      ? 'bg-red-500 animate-pulse'
                      : event.priority === 'high'
                        ? 'bg-orange-500'
                        : event.priority === 'moderate'
                          ? 'bg-yellow-500'
                          : 'bg-blue-500'
                  }`}
                >
                  {idx + 1}
                </div>
                
                <div
                  className={`p-4 rounded-lg border-l-4 ${getEventTypeColor(event.event_type)}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{getEventTypeIcon(event.event_type)}</span>
                      <div>
                        <h3 className="font-semibold text-white">{event.title}</h3>
                        <p className={`text-xs ${getModuleColor(event.source_module)}`}>
                          {event.source_module.replace(/_/g, ' ')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2 py-1 text-xs rounded ${getPriorityColor(event.priority)}`}
                      >
                        {event.priority}
                      </span>
                      <span className="text-xs text-gray-500">{formatTime(event.timestamp)}</span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-300 mb-3">{event.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="text-gray-400">
                        Entity: <span className="text-white">{event.entity_name}</span>
                      </span>
                      <span className="text-gray-400">
                        Score:{' '}
                        <span
                          className={`font-bold ${
                            event.threat_score >= 80
                              ? 'text-red-400'
                              : event.threat_score >= 60
                                ? 'text-orange-400'
                                : event.threat_score >= 40
                                  ? 'text-yellow-400'
                                  : 'text-blue-400'
                          }`}
                        >
                          {event.threat_score}
                        </span>
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {event.related_events.length > 0 && (
                        <span className="text-xs text-gray-500">
                          {event.related_events.length} related
                        </span>
                      )}
                      <div className="flex space-x-1">
                        {event.jurisdiction_codes.slice(0, 2).map((code, i) => (
                          <span
                            key={i}
                            className="px-1.5 py-0.5 text-xs bg-gray-600 rounded"
                          >
                            {code}
                          </span>
                        ))}
                        {event.jurisdiction_codes.length > 2 && (
                          <span className="px-1.5 py-0.5 text-xs bg-gray-600 rounded">
                            +{event.jurisdiction_codes.length - 2}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {!expanded && filteredEvents.length > 5 && (
          <div className="mt-4 text-center">
            <span className="text-sm text-blue-400 cursor-pointer hover:underline">
              View All {filteredEvents.length} Events →
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

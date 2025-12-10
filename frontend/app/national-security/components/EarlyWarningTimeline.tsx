'use client';

import { useState, useEffect } from 'react';

interface EarlyWarning {
  signal_id: string;
  title: string;
  description: string;
  urgency: string;
  domains_affected: string[];
  risk_score: number;
  probability: number;
  time_horizon_hours: number;
  is_active: boolean;
  acknowledged: boolean;
  created_at: string;
  expires_at: string;
}

interface FusionEvent {
  event_id: string;
  timestamp: string;
  event_type: string;
  domain: string;
  severity: number;
  description: string;
  impact_assessment: string;
}

export default function EarlyWarningTimeline() {
  const [warnings, setWarnings] = useState<EarlyWarning[]>([]);
  const [events, setEvents] = useState<FusionEvent[]>([]);
  const [activeView, setActiveView] = useState<'warnings' | 'timeline'>('warnings');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [warningsRes, eventsRes] = await Promise.all([
        fetch('/api/national-security/fusion/early-warnings?active_only=true&limit=20'),
        fetch('/api/national-security/fusion/timeline?hours=48&limit=30'),
      ]);

      if (warningsRes.ok) {
        const data = await warningsRes.json();
        setWarnings(data.warnings || []);
      }
      if (eventsRes.ok) {
        const data = await eventsRes.json();
        setEvents(data.events || []);
      }
    } catch (error) {
      console.error('Failed to fetch early warning data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'emergency':
        return 'text-red-500 bg-red-900/50 border-red-500';
      case 'flash':
        return 'text-red-400 bg-red-900/30 border-red-500/50';
      case 'immediate':
        return 'text-orange-400 bg-orange-900/30 border-orange-500/50';
      case 'priority':
        return 'text-yellow-400 bg-yellow-900/30 border-yellow-500/50';
      case 'routine':
        return 'text-blue-400 bg-blue-900/30 border-blue-500/50';
      default:
        return 'text-gray-400 bg-gray-700 border-gray-600';
    }
  };

  const getDomainColor = (domain: string) => {
    switch (domain) {
      case 'cyber':
        return 'bg-cyan-900/50 text-cyan-400';
      case 'geopolitical':
        return 'bg-emerald-900/50 text-emerald-400';
      case 'financial':
        return 'bg-amber-900/50 text-amber-400';
      case 'insider':
        return 'bg-purple-900/50 text-purple-400';
      case 'terrorism':
        return 'bg-red-900/50 text-red-400';
      case 'infrastructure':
        return 'bg-blue-900/50 text-blue-400';
      default:
        return 'bg-gray-700 text-gray-400';
    }
  };

  const getSeverityColor = (severity: number) => {
    if (severity >= 80) return 'text-red-400';
    if (severity >= 60) return 'text-orange-400';
    if (severity >= 40) return 'text-yellow-400';
    return 'text-blue-400';
  };

  const formatTimeRemaining = (expiresAt: string) => {
    const now = new Date();
    const expires = new Date(expiresAt);
    const diff = expires.getTime() - now.getTime();
    
    if (diff <= 0) return 'Expired';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }
    return `${hours}h ${minutes}m`;
  };

  const acknowledgeWarning = async (signalId: string) => {
    try {
      const response = await fetch(`/api/national-security/fusion/early-warnings/${signalId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ acknowledged_by: 'current_user' }),
      });
      
      if (response.ok) {
        fetchData();
      }
    } catch (error) {
      console.error('Failed to acknowledge warning:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-yellow-400">Early Warning System</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveView('warnings')}
              className={`px-3 py-1 text-sm rounded transition-colors ${
                activeView === 'warnings'
                  ? 'bg-yellow-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Active Warnings ({warnings.length})
            </button>
            <button
              onClick={() => setActiveView('timeline')}
              className={`px-3 py-1 text-sm rounded transition-colors ${
                activeView === 'timeline'
                  ? 'bg-yellow-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Event Timeline
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">
        {activeView === 'warnings' ? (
          <div className="space-y-4">
            {warnings.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No active early warnings
              </div>
            ) : (
              warnings.map((warning) => (
                <div
                  key={warning.signal_id}
                  className={`p-4 rounded-lg border ${getUrgencyColor(warning.urgency)}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getUrgencyColor(warning.urgency)}`}>
                          {warning.urgency}
                        </span>
                        <span className="text-white font-semibold">{warning.title}</span>
                        {!warning.acknowledged && (
                          <span className="px-2 py-0.5 bg-red-900/50 text-red-400 text-xs rounded animate-pulse">
                            UNACKNOWLEDGED
                          </span>
                        )}
                      </div>
                      <p className="mt-2 text-sm text-gray-300">{warning.description}</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {warning.domains_affected.map((domain, idx) => (
                          <span
                            key={idx}
                            className={`px-2 py-0.5 rounded text-xs ${getDomainColor(domain)}`}
                          >
                            {domain}
                          </span>
                        ))}
                      </div>
                      <div className="mt-3 flex items-center space-x-6 text-xs text-gray-500">
                        <span>Probability: {(warning.probability * 100).toFixed(0)}%</span>
                        <span>Horizon: {warning.time_horizon_hours}h</span>
                        <span>Expires: {formatTimeRemaining(warning.expires_at)}</span>
                        <span>Created: {new Date(warning.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="flex flex-col items-end ml-4">
                      <div className="text-2xl font-bold text-yellow-400">
                        {warning.risk_score.toFixed(0)}
                      </div>
                      <div className="text-xs text-gray-500">Risk Score</div>
                      {!warning.acknowledged && (
                        <button
                          onClick={() => acknowledgeWarning(warning.signal_id)}
                          className="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
                        >
                          Acknowledge
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-700" />
            <div className="space-y-4">
              {events.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No recent events in timeline
                </div>
              ) : (
                events.map((event, idx) => (
                  <div key={event.event_id} className="relative pl-10">
                    <div className={`absolute left-2 w-4 h-4 rounded-full border-2 ${
                      event.severity >= 70 ? 'bg-red-500 border-red-400' :
                      event.severity >= 50 ? 'bg-orange-500 border-orange-400' :
                      event.severity >= 30 ? 'bg-yellow-500 border-yellow-400' :
                      'bg-blue-500 border-blue-400'
                    }`} />
                    <div className="p-3 bg-gray-700/50 rounded-lg border border-gray-600">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className={`px-2 py-0.5 rounded text-xs ${getDomainColor(event.domain)}`}>
                            {event.domain}
                          </span>
                          <span className="text-white font-medium">{event.event_type}</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`text-lg font-bold ${getSeverityColor(event.severity)}`}>
                            {event.severity.toFixed(0)}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(event.timestamp).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <p className="mt-2 text-sm text-gray-400">{event.description}</p>
                      {event.impact_assessment && (
                        <p className="mt-1 text-xs text-gray-500">
                          Impact: {event.impact_assessment}
                        </p>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

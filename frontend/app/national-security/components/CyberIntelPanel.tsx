'use client';

import { useState, useEffect } from 'react';

interface CyberIntelPanelProps {
  compact?: boolean;
}

interface MalwareSignal {
  signal_id: string;
  malware_type: string;
  severity: string;
  name: string;
  description: string;
  confidence_score: number;
  is_active: boolean;
  first_seen: string;
}

interface BotnetActivity {
  activity_id: string;
  botnet_name: string;
  status: string;
  estimated_size: number;
  threat_score: number;
  detected_at: string;
}

interface RansomwareAlert {
  alert_id: string;
  ransomware_family: string;
  severity: string;
  threat_score: number;
  is_active: boolean;
  first_detected: string;
}

export default function CyberIntelPanel({ compact = false }: CyberIntelPanelProps) {
  const [malwareSignals, setMalwareSignals] = useState<MalwareSignal[]>([]);
  const [botnetActivities, setBotnetActivities] = useState<BotnetActivity[]>([]);
  const [ransomwareAlerts, setRansomwareAlerts] = useState<RansomwareAlert[]>([]);
  const [activeView, setActiveView] = useState<'malware' | 'botnet' | 'ransomware'>('malware');
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [malwareRes, botnetRes, ransomwareRes, metricsRes] = await Promise.all([
        fetch('/api/national-security/cyber/malware?limit=20'),
        fetch('/api/national-security/cyber/botnets?limit=20'),
        fetch('/api/national-security/cyber/ransomware?limit=20'),
        fetch('/api/national-security/cyber/metrics'),
      ]);

      if (malwareRes.ok) {
        const data = await malwareRes.json();
        setMalwareSignals(data.signals || []);
      }
      if (botnetRes.ok) {
        const data = await botnetRes.json();
        setBotnetActivities(data.activities || []);
      }
      if (ransomwareRes.ok) {
        const data = await ransomwareRes.json();
        setRansomwareAlerts(data.alerts || []);
      }
      if (metricsRes.ok) {
        const data = await metricsRes.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch cyber intel data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-400 bg-red-900/30';
      case 'high':
        return 'text-orange-400 bg-orange-900/30';
      case 'medium':
        return 'text-yellow-400 bg-yellow-900/30';
      case 'low':
        return 'text-green-400 bg-green-900/30';
      default:
        return 'text-gray-400 bg-gray-700';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-red-400';
      case 'monitoring':
        return 'text-yellow-400';
      case 'dormant':
        return 'text-gray-400';
      case 'disrupted':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-cyan-400">Cyber Intelligence</h3>
          <span className="text-xs text-gray-500">
            {metrics?.total_malware_signals || 0} signals
          </span>
        </div>
        <div className="space-y-2">
          {malwareSignals.slice(0, 3).map((signal) => (
            <div
              key={signal.signal_id}
              className="flex items-center justify-between p-2 bg-gray-700/50 rounded"
            >
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-0.5 rounded text-xs ${getSeverityColor(signal.severity)}`}>
                  {signal.severity}
                </span>
                <span className="text-sm text-white truncate max-w-[150px]">
                  {signal.name}
                </span>
              </div>
              <span className="text-xs text-gray-400">{signal.malware_type}</span>
            </div>
          ))}
        </div>
        {metrics && (
          <div className="mt-4 pt-4 border-t border-gray-700 grid grid-cols-3 gap-2 text-center">
            <div>
              <div className="text-lg font-bold text-red-400">
                {metrics.active_malware_signals || 0}
              </div>
              <div className="text-xs text-gray-500">Active</div>
            </div>
            <div>
              <div className="text-lg font-bold text-orange-400">
                {metrics.total_botnet_activities || 0}
              </div>
              <div className="text-xs text-gray-500">Botnets</div>
            </div>
            <div>
              <div className="text-lg font-bold text-yellow-400">
                {metrics.active_ransomware_alerts || 0}
              </div>
              <div className="text-xs text-gray-500">Ransomware</div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-cyan-400">Cyber Threat Intelligence</h2>
          <div className="flex space-x-2">
            {(['malware', 'botnet', 'ransomware'] as const).map((view) => (
              <button
                key={view}
                onClick={() => setActiveView(view)}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  activeView === view
                    ? 'bg-cyan-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {view.charAt(0).toUpperCase() + view.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {metrics && (
        <div className="p-4 border-b border-gray-700 bg-gray-800/50">
          <div className="grid grid-cols-5 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-cyan-400">
                {metrics.total_malware_signals || 0}
              </div>
              <div className="text-xs text-gray-500">Total Signals</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-400">
                {metrics.active_malware_signals || 0}
              </div>
              <div className="text-xs text-gray-500">Active Malware</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-400">
                {metrics.total_botnet_activities || 0}
              </div>
              <div className="text-xs text-gray-500">Botnets Tracked</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">
                {metrics.active_ransomware_alerts || 0}
              </div>
              <div className="text-xs text-gray-500">Ransomware Alerts</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-400">
                {metrics.total_vulnerability_reports || 0}
              </div>
              <div className="text-xs text-gray-500">Vulnerabilities</div>
            </div>
          </div>
        </div>
      )}

      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400" />
          </div>
        ) : (
          <>
            {activeView === 'malware' && (
              <div className="space-y-3">
                {malwareSignals.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No malware signals detected
                  </div>
                ) : (
                  malwareSignals.map((signal) => (
                    <div
                      key={signal.signal_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-cyan-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(signal.severity)}`}>
                              {signal.severity.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">{signal.name}</span>
                            {signal.is_active && (
                              <span className="px-2 py-0.5 bg-red-900/50 text-red-400 text-xs rounded">
                                ACTIVE
                              </span>
                            )}
                          </div>
                          <p className="mt-2 text-sm text-gray-400">{signal.description}</p>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>Type: {signal.malware_type}</span>
                            <span>Confidence: {(signal.confidence_score * 100).toFixed(0)}%</span>
                            <span>First seen: {new Date(signal.first_seen).toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'botnet' && (
              <div className="space-y-3">
                {botnetActivities.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No botnet activities detected
                  </div>
                ) : (
                  botnetActivities.map((activity) => (
                    <div
                      key={activity.activity_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-orange-500/50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-3">
                            <span className="text-white font-medium">{activity.botnet_name}</span>
                            <span className={`text-sm ${getStatusColor(activity.status)}`}>
                              {activity.status}
                            </span>
                          </div>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>Est. Size: {activity.estimated_size.toLocaleString()} nodes</span>
                            <span>Detected: {new Date(activity.detected_at).toLocaleString()}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-orange-400">
                            {activity.threat_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Threat Score</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'ransomware' && (
              <div className="space-y-3">
                {ransomwareAlerts.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No ransomware alerts
                  </div>
                ) : (
                  ransomwareAlerts.map((alert) => (
                    <div
                      key={alert.alert_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-yellow-500/50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                              {alert.severity.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">{alert.ransomware_family}</span>
                            {alert.is_active && (
                              <span className="px-2 py-0.5 bg-red-900/50 text-red-400 text-xs rounded">
                                ACTIVE THREAT
                              </span>
                            )}
                          </div>
                          <div className="mt-2 text-xs text-gray-500">
                            First detected: {new Date(alert.first_detected).toLocaleString()}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-yellow-400">
                            {alert.threat_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Threat Score</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

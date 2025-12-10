'use client';

import { useState, useEffect } from 'react';

interface InsiderThreatPanelProps {
  compact?: boolean;
}

interface RiskProfile {
  profile_id: string;
  employee_id: string;
  employee_name: string;
  department: string;
  role: string;
  risk_level: string;
  risk_score: number;
  is_privileged: boolean;
  last_assessment: string;
}

interface BehaviorDeviation {
  deviation_id: string;
  employee_id: string;
  behavior_type: string;
  description: string;
  deviation_score: number;
  severity: string;
  is_acknowledged: boolean;
  detected_at: string;
}

interface AccessAnomaly {
  anomaly_id: string;
  employee_id: string;
  anomaly_type: string;
  description: string;
  resource_accessed: string;
  risk_score: number;
  severity: string;
  investigation_status: string;
  detected_at: string;
}

export default function InsiderThreatPanel({ compact = false }: InsiderThreatPanelProps) {
  const [profiles, setProfiles] = useState<RiskProfile[]>([]);
  const [deviations, setDeviations] = useState<BehaviorDeviation[]>([]);
  const [anomalies, setAnomalies] = useState<AccessAnomaly[]>([]);
  const [activeView, setActiveView] = useState<'profiles' | 'deviations' | 'anomalies'>('profiles');
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [profilesRes, deviationsRes, anomaliesRes, metricsRes] = await Promise.all([
        fetch('/api/national-security/insider/profiles?limit=20'),
        fetch('/api/national-security/insider/deviations?limit=20'),
        fetch('/api/national-security/insider/anomalies?limit=20'),
        fetch('/api/national-security/insider/metrics'),
      ]);

      if (profilesRes.ok) {
        const data = await profilesRes.json();
        setProfiles(data.profiles || []);
      }
      if (deviationsRes.ok) {
        const data = await deviationsRes.json();
        setDeviations(data.deviations || []);
      }
      if (anomaliesRes.ok) {
        const data = await anomaliesRes.json();
        setAnomalies(data.anomalies || []);
      }
      if (metricsRes.ok) {
        const data = await metricsRes.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch insider threat data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'text-red-400 bg-red-900/30';
      case 'high':
        return 'text-orange-400 bg-orange-900/30';
      case 'elevated':
        return 'text-yellow-400 bg-yellow-900/30';
      case 'moderate':
        return 'text-blue-400 bg-blue-900/30';
      case 'low':
        return 'text-green-400 bg-green-900/30';
      default:
        return 'text-gray-400 bg-gray-700';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'text-red-400';
      case 'investigating':
        return 'text-yellow-400';
      case 'resolved':
        return 'text-green-400';
      case 'false_positive':
        return 'text-gray-400';
      default:
        return 'text-gray-400';
    }
  };

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-purple-400">Insider Threat</h3>
          <span className="text-xs text-gray-500">
            {metrics?.total_profiles || 0} profiles
          </span>
        </div>
        <div className="space-y-2">
          {profiles.filter(p => p.risk_score >= 50).slice(0, 3).map((profile) => (
            <div
              key={profile.profile_id}
              className="flex items-center justify-between p-2 bg-gray-700/50 rounded"
            >
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-0.5 rounded text-xs ${getRiskLevelColor(profile.risk_level)}`}>
                  {profile.risk_level}
                </span>
                <span className="text-sm text-white truncate max-w-[120px]">
                  {profile.employee_name}
                </span>
              </div>
              <span className="text-sm font-bold text-orange-400">
                {profile.risk_score.toFixed(0)}
              </span>
            </div>
          ))}
        </div>
        {metrics && (
          <div className="mt-4 pt-4 border-t border-gray-700 grid grid-cols-3 gap-2 text-center">
            <div>
              <div className="text-lg font-bold text-red-400">
                {metrics.high_risk_count || 0}
              </div>
              <div className="text-xs text-gray-500">High Risk</div>
            </div>
            <div>
              <div className="text-lg font-bold text-yellow-400">
                {metrics.unacknowledged_deviations || 0}
              </div>
              <div className="text-xs text-gray-500">Deviations</div>
            </div>
            <div>
              <div className="text-lg font-bold text-orange-400">
                {metrics.open_anomalies || 0}
              </div>
              <div className="text-xs text-gray-500">Anomalies</div>
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
          <h2 className="text-xl font-bold text-purple-400">Insider Threat Detection</h2>
          <div className="flex space-x-2">
            {(['profiles', 'deviations', 'anomalies'] as const).map((view) => (
              <button
                key={view}
                onClick={() => setActiveView(view)}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  activeView === view
                    ? 'bg-purple-600 text-white'
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
              <div className="text-2xl font-bold text-purple-400">
                {metrics.total_profiles || 0}
              </div>
              <div className="text-xs text-gray-500">Total Profiles</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-400">
                {metrics.high_risk_count || 0}
              </div>
              <div className="text-xs text-gray-500">High Risk</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">
                {metrics.unacknowledged_deviations || 0}
              </div>
              <div className="text-xs text-gray-500">Unack. Deviations</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-400">
                {metrics.open_anomalies || 0}
              </div>
              <div className="text-xs text-gray-500">Open Anomalies</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-400">
                {metrics.total_assessments || 0}
              </div>
              <div className="text-xs text-gray-500">Assessments</div>
            </div>
          </div>
        </div>
      )}

      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400" />
          </div>
        ) : (
          <>
            {activeView === 'profiles' && (
              <div className="space-y-3">
                {profiles.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No risk profiles found
                  </div>
                ) : (
                  profiles.map((profile) => (
                    <div
                      key={profile.profile_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-purple-500/50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskLevelColor(profile.risk_level)}`}>
                              {profile.risk_level.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">{profile.employee_name}</span>
                            {profile.is_privileged && (
                              <span className="px-2 py-0.5 bg-yellow-900/50 text-yellow-400 text-xs rounded">
                                PRIVILEGED
                              </span>
                            )}
                          </div>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>ID: {profile.employee_id}</span>
                            <span>Dept: {profile.department}</span>
                            <span>Role: {profile.role}</span>
                            <span>Last Assessment: {new Date(profile.last_assessment).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-purple-400">
                            {profile.risk_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Risk Score</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'deviations' && (
              <div className="space-y-3">
                {deviations.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No behavior deviations detected
                  </div>
                ) : (
                  deviations.map((deviation) => (
                    <div
                      key={deviation.deviation_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-yellow-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskLevelColor(deviation.severity)}`}>
                              {deviation.severity.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">{deviation.behavior_type}</span>
                            {!deviation.is_acknowledged && (
                              <span className="px-2 py-0.5 bg-red-900/50 text-red-400 text-xs rounded">
                                UNACKNOWLEDGED
                              </span>
                            )}
                          </div>
                          <p className="mt-2 text-sm text-gray-400">{deviation.description}</p>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>Employee: {deviation.employee_id}</span>
                            <span>Detected: {new Date(deviation.detected_at).toLocaleString()}</span>
                          </div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-yellow-400">
                            {deviation.deviation_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Deviation</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'anomalies' && (
              <div className="space-y-3">
                {anomalies.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No access anomalies detected
                  </div>
                ) : (
                  anomalies.map((anomaly) => (
                    <div
                      key={anomaly.anomaly_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-orange-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskLevelColor(anomaly.severity)}`}>
                              {anomaly.severity.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">{anomaly.anomaly_type}</span>
                            <span className={`text-xs ${getStatusColor(anomaly.investigation_status)}`}>
                              {anomaly.investigation_status}
                            </span>
                          </div>
                          <p className="mt-2 text-sm text-gray-400">{anomaly.description}</p>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>Employee: {anomaly.employee_id}</span>
                            <span>Resource: {anomaly.resource_accessed}</span>
                            <span>Detected: {new Date(anomaly.detected_at).toLocaleString()}</span>
                          </div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-orange-400">
                            {anomaly.risk_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Risk Score</div>
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

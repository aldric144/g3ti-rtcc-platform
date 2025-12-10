'use client';

import { useState, useEffect } from 'react';

interface GeoRiskMapProps {
  compact?: boolean;
}

interface ConflictEvent {
  event_id: string;
  name: string;
  description: string;
  intensity: string;
  region: string;
  countries_involved: string[];
  is_active: boolean;
  escalation_risk: number;
  last_updated: string;
}

interface NationStateThreat {
  threat_id: string;
  actor_name: string;
  actor_type: string;
  country_of_origin: string;
  target_countries: string[];
  overall_threat_score: number;
  capability_score: number;
  intent_score: number;
  assessment_date: string;
}

interface GeoEconomicRisk {
  risk_id: string;
  country: string;
  region: string;
  stability_level: string;
  overall_risk_score: number;
  economic_risk_score: number;
  political_risk_score: number;
  security_risk_score: number;
  assessment_date: string;
}

export default function GeoRiskMap({ compact = false }: GeoRiskMapProps) {
  const [conflicts, setConflicts] = useState<ConflictEvent[]>([]);
  const [threats, setThreats] = useState<NationStateThreat[]>([]);
  const [geoRisks, setGeoRisks] = useState<GeoEconomicRisk[]>([]);
  const [activeView, setActiveView] = useState<'conflicts' | 'threats' | 'economic'>('conflicts');
  const [metrics, setMetrics] = useState<any>(null);
  const [conflictIndex, setConflictIndex] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [conflictsRes, threatsRes, geoRisksRes, metricsRes, indexRes] = await Promise.all([
        fetch('/api/national-security/geopolitical/conflicts?limit=20'),
        fetch('/api/national-security/geopolitical/threats?limit=20'),
        fetch('/api/national-security/geopolitical/geo-economic?limit=20'),
        fetch('/api/national-security/geopolitical/metrics'),
        fetch('/api/national-security/geopolitical/conflict-index'),
      ]);

      if (conflictsRes.ok) {
        const data = await conflictsRes.json();
        setConflicts(data.events || []);
      }
      if (threatsRes.ok) {
        const data = await threatsRes.json();
        setThreats(data.threats || []);
      }
      if (geoRisksRes.ok) {
        const data = await geoRisksRes.json();
        setGeoRisks(data.risks || []);
      }
      if (metricsRes.ok) {
        const data = await metricsRes.json();
        setMetrics(data);
      }
      if (indexRes.ok) {
        const data = await indexRes.json();
        setConflictIndex(data);
      }
    } catch (error) {
      console.error('Failed to fetch geopolitical data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case 'war':
        return 'text-red-400 bg-red-900/30';
      case 'high':
        return 'text-orange-400 bg-orange-900/30';
      case 'medium':
        return 'text-yellow-400 bg-yellow-900/30';
      case 'low':
        return 'text-blue-400 bg-blue-900/30';
      case 'tension':
        return 'text-cyan-400 bg-cyan-900/30';
      default:
        return 'text-gray-400 bg-gray-700';
    }
  };

  const getStabilityColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'text-red-400 bg-red-900/30';
      case 'unstable':
        return 'text-orange-400 bg-orange-900/30';
      case 'volatile':
        return 'text-yellow-400 bg-yellow-900/30';
      case 'moderate':
        return 'text-blue-400 bg-blue-900/30';
      case 'stable':
        return 'text-green-400 bg-green-900/30';
      default:
        return 'text-gray-400 bg-gray-700';
    }
  };

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-emerald-400">Geopolitical Risk</h3>
          <span className="text-xs text-gray-500">
            {metrics?.total_conflict_events || 0} events
          </span>
        </div>
        <div className="space-y-2">
          {conflicts.filter(c => c.is_active).slice(0, 3).map((conflict) => (
            <div
              key={conflict.event_id}
              className="flex items-center justify-between p-2 bg-gray-700/50 rounded"
            >
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-0.5 rounded text-xs ${getIntensityColor(conflict.intensity)}`}>
                  {conflict.intensity}
                </span>
                <span className="text-sm text-white truncate max-w-[120px]">
                  {conflict.name}
                </span>
              </div>
              <span className="text-xs text-gray-400">{conflict.region}</span>
            </div>
          ))}
        </div>
        {conflictIndex && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Global Conflict Index</span>
              <span className={`text-xl font-bold ${
                conflictIndex.global_index >= 70 ? 'text-red-400' :
                conflictIndex.global_index >= 50 ? 'text-orange-400' :
                conflictIndex.global_index >= 30 ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {conflictIndex.global_index?.toFixed(1) || 'N/A'}
              </span>
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
          <h2 className="text-xl font-bold text-emerald-400">Geopolitical Risk Assessment</h2>
          <div className="flex space-x-2">
            {(['conflicts', 'threats', 'economic'] as const).map((view) => (
              <button
                key={view}
                onClick={() => setActiveView(view)}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  activeView === view
                    ? 'bg-emerald-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {view === 'economic' ? 'Geo-Economic' : view.charAt(0).toUpperCase() + view.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {conflictIndex && (
        <div className="p-4 border-b border-gray-700 bg-gray-800/50">
          <div className="grid grid-cols-5 gap-4 text-center">
            <div>
              <div className={`text-2xl font-bold ${
                conflictIndex.global_index >= 70 ? 'text-red-400' :
                conflictIndex.global_index >= 50 ? 'text-orange-400' :
                conflictIndex.global_index >= 30 ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {conflictIndex.global_index?.toFixed(1) || 'N/A'}
              </div>
              <div className="text-xs text-gray-500">Global Index</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-400">
                {metrics?.active_conflicts || 0}
              </div>
              <div className="text-xs text-gray-500">Active Conflicts</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-400">
                {metrics?.total_nation_state_threats || 0}
              </div>
              <div className="text-xs text-gray-500">Nation-State Threats</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">
                {metrics?.active_sanctions || 0}
              </div>
              <div className="text-xs text-gray-500">Active Sanctions</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-emerald-400">
                {metrics?.total_geo_economic_risks || 0}
              </div>
              <div className="text-xs text-gray-500">Economic Risks</div>
            </div>
          </div>
        </div>
      )}

      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-400" />
          </div>
        ) : (
          <>
            {activeView === 'conflicts' && (
              <div className="space-y-3">
                {conflicts.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No conflict events recorded
                  </div>
                ) : (
                  conflicts.map((conflict) => (
                    <div
                      key={conflict.event_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-emerald-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getIntensityColor(conflict.intensity)}`}>
                              {conflict.intensity.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">{conflict.name}</span>
                            {conflict.is_active && (
                              <span className="px-2 py-0.5 bg-red-900/50 text-red-400 text-xs rounded">
                                ACTIVE
                              </span>
                            )}
                          </div>
                          <p className="mt-2 text-sm text-gray-400">{conflict.description}</p>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>Region: {conflict.region}</span>
                            <span>Countries: {conflict.countries_involved.join(', ')}</span>
                            <span>Updated: {new Date(conflict.last_updated).toLocaleString()}</span>
                          </div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-orange-400">
                            {(conflict.escalation_risk * 100).toFixed(0)}%
                          </div>
                          <div className="text-xs text-gray-500">Escalation Risk</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'threats' && (
              <div className="space-y-3">
                {threats.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No nation-state threats assessed
                  </div>
                ) : (
                  threats.map((threat) => (
                    <div
                      key={threat.threat_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-red-500/50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-3">
                            <span className="text-white font-medium">{threat.actor_name}</span>
                            <span className="px-2 py-0.5 bg-gray-600 text-gray-300 text-xs rounded">
                              {threat.actor_type}
                            </span>
                          </div>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>Origin: {threat.country_of_origin}</span>
                            <span>Targets: {threat.target_countries.join(', ')}</span>
                            <span>Assessed: {new Date(threat.assessment_date).toLocaleDateString()}</span>
                          </div>
                          <div className="mt-2 flex items-center space-x-4">
                            <div className="flex items-center space-x-1">
                              <span className="text-xs text-gray-500">Capability:</span>
                              <span className="text-sm font-medium text-blue-400">
                                {threat.capability_score.toFixed(0)}
                              </span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <span className="text-xs text-gray-500">Intent:</span>
                              <span className="text-sm font-medium text-purple-400">
                                {threat.intent_score.toFixed(0)}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-red-400">
                            {threat.overall_threat_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Threat Score</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'economic' && (
              <div className="space-y-3">
                {geoRisks.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No geo-economic risks assessed
                  </div>
                ) : (
                  geoRisks.map((risk) => (
                    <div
                      key={risk.risk_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-yellow-500/50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getStabilityColor(risk.stability_level)}`}>
                              {risk.stability_level.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">{risk.country}</span>
                            <span className="text-xs text-gray-500">({risk.region})</span>
                          </div>
                          <div className="mt-2 flex items-center space-x-4">
                            <div className="flex items-center space-x-1">
                              <span className="text-xs text-gray-500">Economic:</span>
                              <span className="text-sm font-medium text-yellow-400">
                                {risk.economic_risk_score.toFixed(0)}
                              </span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <span className="text-xs text-gray-500">Political:</span>
                              <span className="text-sm font-medium text-orange-400">
                                {risk.political_risk_score.toFixed(0)}
                              </span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <span className="text-xs text-gray-500">Security:</span>
                              <span className="text-sm font-medium text-red-400">
                                {risk.security_risk_score.toFixed(0)}
                              </span>
                            </div>
                          </div>
                          <div className="mt-2 text-xs text-gray-500">
                            Assessed: {new Date(risk.assessment_date).toLocaleDateString()}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-emerald-400">
                            {risk.overall_risk_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Overall Risk</div>
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

'use client';

import { useState, useEffect } from 'react';

interface ThreatScore {
  score_id: string;
  entity_id: string;
  entity_type: string;
  entity_name: string;
  overall_score: number;
  threat_level: string;
  domain_scores: Record<string, number>;
  trend: string;
  jurisdiction_codes: string[];
  calculated_at: string;
}

interface ThreatMetrics {
  total_scores: number;
  critical_count: number;
  high_count: number;
  moderate_count: number;
  low_count: number;
  average_score: number;
}

interface Props {
  expanded?: boolean;
}

export default function ThreatScoreboard({ expanded = false }: Props) {
  const [scores, setScores] = useState<ThreatScore[]>([]);
  const [metrics, setMetrics] = useState<ThreatMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockScores: ThreatScore[] = [
      {
        score_id: 'score-001',
        entity_id: 'ent-001',
        entity_type: 'person',
        entity_name: 'Subject Alpha',
        overall_score: 92,
        threat_level: 'level_5_critical',
        domain_scores: {
          dark_web: 85,
          osint: 78,
          extremist_network: 95,
          local_crime: 88,
        },
        trend: 'increasing',
        jurisdiction_codes: ['US-NY', 'US-NJ'],
        calculated_at: new Date().toISOString(),
      },
      {
        score_id: 'score-002',
        entity_id: 'ent-002',
        entity_type: 'organization',
        entity_name: 'Militia Group Beta',
        overall_score: 85,
        threat_level: 'level_4_high',
        domain_scores: {
          dark_web: 45,
          osint: 72,
          extremist_network: 92,
          terrorism: 88,
        },
        trend: 'stable',
        jurisdiction_codes: ['US-PA', 'US-OH'],
        calculated_at: new Date(Date.now() - 1800000).toISOString(),
      },
      {
        score_id: 'score-003',
        entity_id: 'ent-003',
        entity_type: 'location',
        entity_name: 'Downtown District',
        overall_score: 68,
        threat_level: 'level_3_moderate',
        domain_scores: {
          osint: 65,
          local_crime: 72,
          gang: 58,
        },
        trend: 'decreasing',
        jurisdiction_codes: ['US-CA'],
        calculated_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        score_id: 'score-004',
        entity_id: 'ent-004',
        entity_type: 'person',
        entity_name: 'Subject Gamma',
        overall_score: 78,
        threat_level: 'level_4_high',
        domain_scores: {
          dark_web: 82,
          drug: 75,
          weapons: 68,
        },
        trend: 'increasing',
        jurisdiction_codes: ['US-FL'],
        calculated_at: new Date(Date.now() - 5400000).toISOString(),
      },
      {
        score_id: 'score-005',
        entity_id: 'ent-005',
        entity_type: 'vehicle',
        entity_name: 'Vehicle ABC-1234',
        overall_score: 55,
        threat_level: 'level_2_low',
        domain_scores: {
          local_crime: 48,
          gang: 62,
        },
        trend: 'stable',
        jurisdiction_codes: ['US-TX'],
        calculated_at: new Date(Date.now() - 7200000).toISOString(),
      },
    ];

    const mockMetrics: ThreatMetrics = {
      total_scores: 156,
      critical_count: 8,
      high_count: 24,
      moderate_count: 45,
      low_count: 79,
      average_score: 42.5,
    };

    setTimeout(() => {
      setScores(mockScores);
      setMetrics(mockMetrics);
      setLoading(false);
    }, 500);
  }, []);

  const getThreatLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      level_1_minimal: 'text-green-400 bg-green-500/20',
      level_2_low: 'text-blue-400 bg-blue-500/20',
      level_3_moderate: 'text-yellow-400 bg-yellow-500/20',
      level_4_high: 'text-orange-400 bg-orange-500/20',
      level_5_critical: 'text-red-500 bg-red-600/30',
    };
    return colors[level] || 'text-gray-400 bg-gray-500/20';
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-red-500';
    if (score >= 60) return 'text-orange-400';
    if (score >= 40) return 'text-yellow-400';
    if (score >= 20) return 'text-blue-400';
    return 'text-green-400';
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'increasing') return '↑';
    if (trend === 'decreasing') return '↓';
    return '→';
  };

  const getTrendColor = (trend: string) => {
    if (trend === 'increasing') return 'text-red-400';
    if (trend === 'decreasing') return 'text-green-400';
    return 'text-gray-400';
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold text-red-400">Threat Scoreboard</h2>
      </div>

      <div className="p-4">
        {metrics && (
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-6">
            <div className="bg-gray-700/50 p-3 rounded text-center">
              <p className="text-2xl font-bold text-white">{metrics.total_scores}</p>
              <p className="text-xs text-gray-400">Total Scores</p>
            </div>
            <div className="bg-red-900/30 p-3 rounded text-center border border-red-500/30">
              <p className="text-2xl font-bold text-red-400">{metrics.critical_count}</p>
              <p className="text-xs text-gray-400">Critical</p>
            </div>
            <div className="bg-orange-900/30 p-3 rounded text-center border border-orange-500/30">
              <p className="text-2xl font-bold text-orange-400">{metrics.high_count}</p>
              <p className="text-xs text-gray-400">High</p>
            </div>
            <div className="bg-yellow-900/30 p-3 rounded text-center border border-yellow-500/30">
              <p className="text-2xl font-bold text-yellow-400">{metrics.moderate_count}</p>
              <p className="text-xs text-gray-400">Moderate</p>
            </div>
            <div className="bg-blue-900/30 p-3 rounded text-center border border-blue-500/30">
              <p className="text-2xl font-bold text-blue-400">{metrics.low_count}</p>
              <p className="text-xs text-gray-400">Low</p>
            </div>
            <div className="bg-gray-700/50 p-3 rounded text-center">
              <p className="text-2xl font-bold text-white">{metrics.average_score.toFixed(1)}</p>
              <p className="text-xs text-gray-400">Avg Score</p>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {scores.slice(0, expanded ? scores.length : 5).map((score) => (
            <div
              key={score.score_id}
              className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-red-500 transition-colors"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-semibold text-white flex items-center">
                    {score.entity_name}
                    <span className={`ml-2 ${getTrendColor(score.trend)}`}>
                      {getTrendIcon(score.trend)}
                    </span>
                  </h3>
                  <p className="text-sm text-gray-400 capitalize">
                    {score.entity_type} • {score.jurisdiction_codes.join(', ')}
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <span
                    className={`px-2 py-1 text-xs rounded ${getThreatLevelColor(score.threat_level)}`}
                  >
                    {score.threat_level.replace('level_', 'L').replace(/_/g, ' ')}
                  </span>
                  <div
                    className={`w-16 h-16 rounded-full flex items-center justify-center border-4 ${
                      score.overall_score >= 80
                        ? 'border-red-500 bg-red-500/20'
                        : score.overall_score >= 60
                          ? 'border-orange-500 bg-orange-500/20'
                          : score.overall_score >= 40
                            ? 'border-yellow-500 bg-yellow-500/20'
                            : 'border-blue-500 bg-blue-500/20'
                    }`}
                  >
                    <span className={`text-xl font-bold ${getScoreColor(score.overall_score)}`}>
                      {score.overall_score}
                    </span>
                  </div>
                </div>
              </div>

              {expanded && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-3">
                  {Object.entries(score.domain_scores).map(([domain, domainScore]) => (
                    <div key={domain} className="bg-gray-800 p-2 rounded">
                      <p className="text-xs text-gray-400 capitalize">
                        {domain.replace(/_/g, ' ')}
                      </p>
                      <div className="flex items-center">
                        <div className="flex-1 bg-gray-600 rounded-full h-1.5 mr-2">
                          <div
                            className={`h-1.5 rounded-full ${
                              domainScore >= 80
                                ? 'bg-red-500'
                                : domainScore >= 60
                                  ? 'bg-orange-500'
                                  : domainScore >= 40
                                    ? 'bg-yellow-500'
                                    : 'bg-blue-500'
                            }`}
                            style={{ width: `${domainScore}%` }}
                          ></div>
                        </div>
                        <span className={`text-sm font-bold ${getScoreColor(domainScore)}`}>
                          {domainScore}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex justify-between items-center mt-3 text-xs text-gray-500">
                <span>Calculated: {new Date(score.calculated_at).toLocaleString()}</span>
                <div className="space-x-2">
                  <button className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white">
                    Details
                  </button>
                  <button className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-white">
                    Alert
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

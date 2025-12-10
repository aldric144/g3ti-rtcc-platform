'use client';

import { useState, useEffect } from 'react';

interface StabilityScore {
  assessment_id: string;
  timestamp: string;
  overall_score: number;
  stability_level: string;
  trend: string;
  confidence_level: number;
  key_drivers: string[];
  recommendations: string[];
  forecast_24h: number;
  forecast_7d: number;
  forecast_30d: number;
}

export default function NationalStabilityScore() {
  const [stabilityScore, setStabilityScore] = useState<StabilityScore | null>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [scoreRes, metricsRes] = await Promise.all([
        fetch('/api/national-security/fusion/stability-score'),
        fetch('/api/national-security/fusion/metrics'),
      ]);

      if (scoreRes.ok) {
        const data = await scoreRes.json();
        if (data.assessment_id) {
          setStabilityScore(data);
        }
      }
      if (metricsRes.ok) {
        const data = await metricsRes.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch stability score:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStabilityColor = (level: string) => {
    switch (level) {
      case 'optimal':
        return 'text-green-400';
      case 'stable':
        return 'text-blue-400';
      case 'elevated_concern':
        return 'text-yellow-400';
      case 'unstable':
        return 'text-orange-400';
      case 'critical':
        return 'text-red-400';
      case 'emergency':
        return 'text-red-500';
      default:
        return 'text-gray-400';
    }
  };

  const getStabilityBgColor = (level: string) => {
    switch (level) {
      case 'optimal':
        return 'bg-green-900/30 border-green-500/50';
      case 'stable':
        return 'bg-blue-900/30 border-blue-500/50';
      case 'elevated_concern':
        return 'bg-yellow-900/30 border-yellow-500/50';
      case 'unstable':
        return 'bg-orange-900/30 border-orange-500/50';
      case 'critical':
        return 'bg-red-900/30 border-red-500/50';
      case 'emergency':
        return 'bg-red-900/50 border-red-500';
      default:
        return 'bg-gray-700 border-gray-600';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return '↑';
      case 'stable':
        return '→';
      case 'degrading':
        return '↓';
      case 'rapidly_degrading':
        return '↓↓';
      default:
        return '→';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return 'text-green-400';
      case 'stable':
        return 'text-blue-400';
      case 'degrading':
        return 'text-orange-400';
      case 'rapidly_degrading':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getScoreGradient = (score: number) => {
    if (score < 20) return 'from-green-500 to-green-600';
    if (score < 35) return 'from-blue-500 to-blue-600';
    if (score < 50) return 'from-yellow-500 to-yellow-600';
    if (score < 70) return 'from-orange-500 to-orange-600';
    if (score < 85) return 'from-red-500 to-red-600';
    return 'from-red-600 to-red-700';
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-400" />
        </div>
      </div>
    );
  }

  if (!stabilityScore) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-red-400 mb-4">National Stability Score</h2>
        <div className="text-center py-8 text-gray-500">
          No stability assessment available. Calculate a new assessment to view the National Stability Score.
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gray-800 rounded-lg border ${getStabilityBgColor(stabilityScore.stability_level)}`}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-red-400">National Stability Score (NSS)</h2>
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-1 ${getTrendColor(stabilityScore.trend)}`}>
              <span className="text-lg">{getTrendIcon(stabilityScore.trend)}</span>
              <span className="text-sm capitalize">{stabilityScore.trend.replace('_', ' ')}</span>
            </div>
            <span className="text-xs text-gray-500">
              Updated: {new Date(stabilityScore.timestamp).toLocaleString()}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="flex flex-col items-center">
              <div className={`relative w-40 h-40 rounded-full bg-gradient-to-br ${getScoreGradient(stabilityScore.overall_score)} flex items-center justify-center shadow-lg`}>
                <div className="absolute inset-2 bg-gray-800 rounded-full flex items-center justify-center">
                  <div className="text-center">
                    <div className={`text-4xl font-bold ${getStabilityColor(stabilityScore.stability_level)}`}>
                      {stabilityScore.overall_score.toFixed(1)}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">/ 100</div>
                  </div>
                </div>
              </div>
              <div className={`mt-4 px-4 py-2 rounded-full ${getStabilityBgColor(stabilityScore.stability_level)}`}>
                <span className={`text-sm font-semibold uppercase ${getStabilityColor(stabilityScore.stability_level)}`}>
                  {stabilityScore.stability_level.replace('_', ' ')}
                </span>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Confidence: {(stabilityScore.confidence_level * 100).toFixed(0)}%
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <h3 className="text-sm font-semibold text-gray-400 mb-3">Forecasts</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <span className="text-sm text-gray-300">24 Hours</span>
                <span className={`text-lg font-bold ${getStabilityColor(
                  stabilityScore.forecast_24h < 35 ? 'stable' :
                  stabilityScore.forecast_24h < 50 ? 'elevated_concern' :
                  stabilityScore.forecast_24h < 70 ? 'unstable' : 'critical'
                )}`}>
                  {stabilityScore.forecast_24h.toFixed(1)}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <span className="text-sm text-gray-300">7 Days</span>
                <span className={`text-lg font-bold ${getStabilityColor(
                  stabilityScore.forecast_7d < 35 ? 'stable' :
                  stabilityScore.forecast_7d < 50 ? 'elevated_concern' :
                  stabilityScore.forecast_7d < 70 ? 'unstable' : 'critical'
                )}`}>
                  {stabilityScore.forecast_7d.toFixed(1)}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <span className="text-sm text-gray-300">30 Days</span>
                <span className={`text-lg font-bold ${getStabilityColor(
                  stabilityScore.forecast_30d < 35 ? 'stable' :
                  stabilityScore.forecast_30d < 50 ? 'elevated_concern' :
                  stabilityScore.forecast_30d < 70 ? 'unstable' : 'critical'
                )}`}>
                  {stabilityScore.forecast_30d.toFixed(1)}
                </span>
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <h3 className="text-sm font-semibold text-gray-400 mb-3">Key Drivers</h3>
            <div className="space-y-2 mb-4">
              {stabilityScore.key_drivers.length > 0 ? (
                stabilityScore.key_drivers.map((driver, idx) => (
                  <div
                    key={idx}
                    className="p-2 bg-red-900/20 border border-red-500/30 rounded text-sm text-red-300"
                  >
                    {driver}
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500">No significant risk drivers</div>
              )}
            </div>

            <h3 className="text-sm font-semibold text-gray-400 mb-3">Recommendations</h3>
            <div className="space-y-2">
              {stabilityScore.recommendations.slice(0, 3).map((rec, idx) => (
                <div
                  key={idx}
                  className="p-2 bg-blue-900/20 border border-blue-500/30 rounded text-sm text-blue-300"
                >
                  {rec}
                </div>
              ))}
            </div>
          </div>
        </div>

        {metrics && (
          <div className="mt-6 pt-6 border-t border-gray-700">
            <div className="grid grid-cols-5 gap-4 text-center">
              <div>
                <div className="text-xl font-bold text-purple-400">
                  {metrics.total_stability_assessments || 0}
                </div>
                <div className="text-xs text-gray-500">Assessments</div>
              </div>
              <div>
                <div className="text-xl font-bold text-cyan-400">
                  {metrics.total_fusion_results || 0}
                </div>
                <div className="text-xs text-gray-500">Fusion Results</div>
              </div>
              <div>
                <div className="text-xl font-bold text-yellow-400">
                  {metrics.active_warnings || 0}
                </div>
                <div className="text-xs text-gray-500">Active Warnings</div>
              </div>
              <div>
                <div className="text-xl font-bold text-orange-400">
                  {metrics.unacknowledged_warnings || 0}
                </div>
                <div className="text-xs text-gray-500">Unacknowledged</div>
              </div>
              <div>
                <div className="text-xl font-bold text-blue-400">
                  {metrics.total_trend_predictions || 0}
                </div>
                <div className="text-xs text-gray-500">Predictions</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

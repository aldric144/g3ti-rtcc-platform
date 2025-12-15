'use client';

import React, { useState, useEffect } from 'react';

interface FairnessAssessment {
  assessment_id: string;
  overall_fairness_score: number;
  passed: boolean;
  requires_review: boolean;
  bias_detected: boolean;
  disparity_count: number;
  recommendations: string[];
}

interface DisparityAlert {
  alert_id: string;
  disparity_type: string;
  protected_attribute: string;
  disparity_level: string;
  affected_groups: string[];
  disparity_ratio: number;
  description: string;
  recommendations: string[];
  created_at: string;
  acknowledged: boolean;
}

export default function FairnessDashboard() {
  const [alerts, setAlerts] = useState<DisparityAlert[]>([]);
  const [assessment, setAssessment] = useState<FairnessAssessment | null>(null);
  const [actionType, setActionType] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/moral/fairness/alerts');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Failed to fetch fairness alerts:', error);
    }
  };

  const handleAssess = async () => {
    if (!actionType) return;

    setLoading(true);
    try {
      const response = await fetch('/api/moral/fairness', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_type: actionType,
          requester_id: 'fairness_dashboard',
          context: {},
          historical_data: {},
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAssessment(data);
      }
    } catch (error) {
      console.error('Failed to assess fairness:', error);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/moral/fairness/alerts/${alertId}/acknowledge`, {
        method: 'POST',
      });

      if (response.ok) {
        fetchAlerts();
      }
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const getDisparityColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'severe':
        return 'bg-red-500/20 border-red-500/50 text-red-400';
      case 'high':
        return 'bg-orange-500/20 border-orange-500/50 text-orange-400';
      case 'moderate':
        return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400';
      case 'low':
        return 'bg-blue-500/20 border-blue-500/50 text-blue-400';
      default:
        return 'bg-slate-500/20 border-slate-500/50 text-slate-400';
    }
  };

  const getFairnessScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-green-400';
    if (score >= 0.8) return 'text-yellow-400';
    if (score >= 0.7) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
          <h2 className="text-xl font-semibold text-gold-400 mb-4 flex items-center gap-2">
            <span>📊</span> Fairness Assessment
          </h2>

          <div className="mb-4">
            <label className="block text-slate-400 text-sm mb-1">Action Type</label>
            <select
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-gold-500 focus:outline-none"
            >
              <option value="">Select action type...</option>
              <option value="arrest">Arrest</option>
              <option value="traffic_stop">Traffic Stop</option>
              <option value="search">Search</option>
              <option value="surveillance">Surveillance</option>
              <option value="resource_allocation">Resource Allocation</option>
              <option value="predictive_targeting">Predictive Targeting</option>
              <option value="risk_scoring">Risk Scoring</option>
            </select>
          </div>

          <button
            onClick={handleAssess}
            disabled={loading || !actionType}
            className="w-full bg-gold-500 hover:bg-gold-600 text-slate-900 font-semibold py-2 px-4 rounded transition-colors disabled:opacity-50"
          >
            {loading ? 'Assessing...' : 'Assess Fairness'}
          </button>

          {assessment && (
            <div className="mt-4 space-y-4">
              <div className="bg-slate-700/50 rounded p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400">Overall Fairness Score</span>
                  <span className={`text-2xl font-bold ${getFairnessScoreColor(assessment.overall_fairness_score)}`}>
                    {(assessment.overall_fairness_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-slate-600 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      assessment.overall_fairness_score >= 0.8 ? 'bg-green-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${assessment.overall_fairness_score * 100}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className={`rounded p-3 ${assessment.passed ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                  <div className="text-sm text-slate-400">Status</div>
                  <div className={assessment.passed ? 'text-green-400' : 'text-red-400'}>
                    {assessment.passed ? 'Passed' : 'Failed'}
                  </div>
                </div>
                <div className={`rounded p-3 ${assessment.bias_detected ? 'bg-red-500/20' : 'bg-green-500/20'}`}>
                  <div className="text-sm text-slate-400">Bias</div>
                  <div className={assessment.bias_detected ? 'text-red-400' : 'text-green-400'}>
                    {assessment.bias_detected ? 'Detected' : 'Not Detected'}
                  </div>
                </div>
              </div>

              {assessment.recommendations.length > 0 && (
                <div className="bg-slate-700/50 rounded p-4">
                  <div className="text-slate-400 text-sm mb-2">Recommendations</div>
                  <ul className="space-y-1">
                    {assessment.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                        <span className="text-gold-400 mt-1">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
          <h2 className="text-xl font-semibold text-gold-400 mb-4 flex items-center gap-2">
            <span>⚠️</span> Disparity Alerts
            {alerts.length > 0 && (
              <span className="ml-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                {alerts.length}
              </span>
            )}
          </h2>

          {alerts.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <p>No active disparity alerts</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {alerts.map((alert) => (
                <div
                  key={alert.alert_id}
                  className={`rounded-lg p-4 border ${getDisparityColor(alert.disparity_level)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="font-semibold">{alert.disparity_type}</div>
                      <div className="text-sm opacity-80">
                        {alert.protected_attribute} | Ratio: {alert.disparity_ratio.toFixed(2)}x
                      </div>
                    </div>
                    <span className="text-xs px-2 py-1 rounded bg-slate-700">
                      {alert.disparity_level.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm mb-2">{alert.description}</p>
                  {alert.affected_groups.length > 0 && (
                    <div className="text-xs mb-2">
                      Affected: {alert.affected_groups.join(', ')}
                    </div>
                  )}
                  <button
                    onClick={() => acknowledgeAlert(alert.alert_id)}
                    className="text-xs bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded transition-colors"
                  >
                    Acknowledge
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
        <h2 className="text-xl font-semibold text-gold-400 mb-4 flex items-center gap-2">
          <span>📈</span> Fairness Metrics Overview
        </h2>

        <div className="grid grid-cols-4 gap-4">
          <div className="bg-slate-700/50 rounded p-4 text-center">
            <div className="text-3xl font-bold text-green-400">87%</div>
            <div className="text-slate-400 text-sm">Demographic Parity</div>
          </div>
          <div className="bg-slate-700/50 rounded p-4 text-center">
            <div className="text-3xl font-bold text-yellow-400">82%</div>
            <div className="text-slate-400 text-sm">Equalized Odds</div>
          </div>
          <div className="bg-slate-700/50 rounded p-4 text-center">
            <div className="text-3xl font-bold text-blue-400">91%</div>
            <div className="text-slate-400 text-sm">Individual Fairness</div>
          </div>
          <div className="bg-slate-700/50 rounded p-4 text-center">
            <div className="text-3xl font-bold text-purple-400">85%</div>
            <div className="text-slate-400 text-sm">Counterfactual Fairness</div>
          </div>
        </div>
      </div>
    </div>
  );
}

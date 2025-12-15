'use client';

import React, { useState, useEffect } from 'react';

interface MoralAlert {
  alert_id: string;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  action_type: string;
  requester_id: string;
  details: Record<string, unknown>;
  recommendations: string[];
  requires_action: boolean;
  created_at: string;
  acknowledged: boolean;
}

interface GuardrailViolation {
  violation_id: string;
  rule_id: string;
  rule_name: string;
  guardrail_type: string;
  severity: string;
  action_type: string;
  action_description: string;
  requester_id: string;
  details: string;
  blocked: boolean;
  remediation_required: boolean;
  remediation_steps: string[];
  created_at: string;
  resolved: boolean;
}

interface MoralAlertsPanelProps {
  onAlertCountChange?: (count: number) => void;
}

export default function MoralAlertsPanel({ onAlertCountChange }: MoralAlertsPanelProps) {
  const [violations, setViolations] = useState<GuardrailViolation[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'blocking' | 'critical' | 'serious'>('all');

  useEffect(() => {
    fetchViolations();
    const interval = setInterval(fetchViolations, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (onAlertCountChange) {
      onAlertCountChange(violations.filter(v => !v.resolved).length);
    }
  }, [violations, onAlertCountChange]);

  const fetchViolations = async () => {
    try {
      const response = await fetch('/api/moral/guardrails/violations');
      if (response.ok) {
        const data = await response.json();
        setViolations(data.violations || []);
      }
    } catch (error) {
      console.error('Failed to fetch violations:', error);
    } finally {
      setLoading(false);
    }
  };

  const resolveViolation = async (violationId: string) => {
    try {
      const response = await fetch(`/api/moral/guardrails/violations/${violationId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resolved_by: 'dashboard_user',
          notes: 'Resolved via dashboard',
        }),
      });

      if (response.ok) {
        fetchViolations();
      }
    } catch (error) {
      console.error('Failed to resolve violation:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'blocking':
        return 'bg-red-600/30 border-red-500 text-red-300';
      case 'critical':
        return 'bg-orange-600/30 border-orange-500 text-orange-300';
      case 'serious':
        return 'bg-yellow-600/30 border-yellow-500 text-yellow-300';
      case 'warning':
        return 'bg-blue-600/30 border-blue-500 text-blue-300';
      default:
        return 'bg-slate-600/30 border-slate-500 text-slate-300';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'blocking':
        return '🛑';
      case 'critical':
        return '🔴';
      case 'serious':
        return '🟠';
      case 'warning':
        return '🟡';
      default:
        return '🔵';
    }
  };

  const getGuardrailTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'constitutional':
        return '📜';
      case 'youth_protection':
        return '👶';
      case 'vulnerable_population':
        return '🛡️';
      case 'use_of_force':
        return '⚔️';
      case 'discrimination':
        return '⚖️';
      case 'bias_prevention':
        return '🎯';
      case 'privacy':
        return '🔒';
      default:
        return '📋';
    }
  };

  const filteredViolations = violations.filter((v) => {
    if (filter === 'all') return true;
    return v.severity.toLowerCase() === filter;
  });

  const activeViolations = filteredViolations.filter(v => !v.resolved);
  const resolvedViolations = filteredViolations.filter(v => v.resolved);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gold-400 flex items-center gap-2">
          <span>🔔</span> Moral Alerts & Violations
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-sm">Filter:</span>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="bg-slate-700 text-white rounded px-3 py-1 border border-slate-600 focus:border-gold-500 focus:outline-none text-sm"
          >
            <option value="all">All Severities</option>
            <option value="blocking">Blocking</option>
            <option value="critical">Critical</option>
            <option value="serious">Serious</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-red-500/20 rounded-lg p-4 border border-red-500/30">
          <div className="text-red-400 text-2xl font-bold">
            {violations.filter(v => v.severity === 'blocking' && !v.resolved).length}
          </div>
          <div className="text-slate-400 text-sm">Blocking</div>
        </div>
        <div className="bg-orange-500/20 rounded-lg p-4 border border-orange-500/30">
          <div className="text-orange-400 text-2xl font-bold">
            {violations.filter(v => v.severity === 'critical' && !v.resolved).length}
          </div>
          <div className="text-slate-400 text-sm">Critical</div>
        </div>
        <div className="bg-yellow-500/20 rounded-lg p-4 border border-yellow-500/30">
          <div className="text-yellow-400 text-2xl font-bold">
            {violations.filter(v => v.severity === 'serious' && !v.resolved).length}
          </div>
          <div className="text-slate-400 text-sm">Serious</div>
        </div>
        <div className="bg-green-500/20 rounded-lg p-4 border border-green-500/30">
          <div className="text-green-400 text-2xl font-bold">
            {violations.filter(v => v.resolved).length}
          </div>
          <div className="text-slate-400 text-sm">Resolved</div>
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg border border-gold-500/20">
        <div className="p-4 border-b border-gold-500/20">
          <h3 className="text-lg font-semibold text-white">
            Active Violations ({activeViolations.length})
          </h3>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading violations...</div>
        ) : activeViolations.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            <p className="text-4xl mb-2">✓</p>
            <p>No active violations</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-700">
            {activeViolations.map((violation) => (
              <div key={violation.violation_id} className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{getSeverityIcon(violation.severity)}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{violation.rule_name}</span>
                        <span className={`text-xs px-2 py-0.5 rounded border ${getSeverityColor(violation.severity)}`}>
                          {violation.severity.toUpperCase()}
                        </span>
                        <span className="text-slate-500 text-sm">
                          {getGuardrailTypeIcon(violation.guardrail_type)} {violation.guardrail_type}
                        </span>
                      </div>
                      <p className="text-slate-400 text-sm mt-1">{violation.details}</p>
                    </div>
                  </div>
                  {violation.blocked && (
                    <span className="bg-red-500 text-white text-xs px-2 py-1 rounded">
                      BLOCKED
                    </span>
                  )}
                </div>

                <div className="ml-9 space-y-2">
                  <div className="text-sm">
                    <span className="text-slate-500">Action:</span>{' '}
                    <span className="text-slate-300">{violation.action_type}</span>
                    <span className="text-slate-500 ml-4">Requester:</span>{' '}
                    <span className="text-slate-300">{violation.requester_id}</span>
                  </div>

                  {violation.remediation_steps.length > 0 && (
                    <div className="bg-slate-700/50 rounded p-3">
                      <div className="text-slate-400 text-xs mb-1">Remediation Steps:</div>
                      <ul className="space-y-1">
                        {violation.remediation_steps.map((step, idx) => (
                          <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                            <span className="text-gold-400">{idx + 1}.</span>
                            <span>{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-slate-500 text-xs">
                      {new Date(violation.created_at).toLocaleString()}
                    </span>
                    <button
                      onClick={() => resolveViolation(violation.violation_id)}
                      className="bg-green-600 hover:bg-green-700 text-white text-sm px-4 py-1 rounded transition-colors"
                    >
                      Mark Resolved
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {resolvedViolations.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-600/50">
          <details>
            <summary className="p-4 cursor-pointer text-slate-400 hover:text-slate-300">
              Resolved Violations ({resolvedViolations.length})
            </summary>
            <div className="divide-y divide-slate-700 border-t border-slate-700">
              {resolvedViolations.slice(0, 5).map((violation) => (
                <div key={violation.violation_id} className="p-4 opacity-60">
                  <div className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span className="text-slate-300">{violation.rule_name}</span>
                    <span className="text-slate-500 text-sm">- {violation.action_type}</span>
                  </div>
                </div>
              ))}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}

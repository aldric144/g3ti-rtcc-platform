'use client';

import React, { useState, useEffect } from 'react';

interface AuditEntry {
  assessment_id: string;
  action_type: string;
  requester_id: string;
  decision: string;
  community_impact_score: number;
  risk_to_community: number;
  created_at: string;
  assessment_hash: string;
}

export default function EthicsAuditTrailViewer() {
  const [auditTrail, setAuditTrail] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'allow' | 'deny' | 'caution' | 'approval'>('all');
  const [requesterFilter, setRequesterFilter] = useState('');
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    fetchAuditTrail();
  }, [requesterFilter, limit]);

  const fetchAuditTrail = async () => {
    setLoading(true);
    try {
      let url = `/api/moral/audit?limit=${limit}`;
      if (requesterFilter) {
        url += `&requester_id=${encodeURIComponent(requesterFilter)}`;
      }
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setAuditTrail(data.audit_trail || []);
      }
    } catch (error) {
      console.error('Failed to fetch audit trail:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDecisionColor = (decision: string) => {
    switch (decision.toLowerCase()) {
      case 'allow':
        return 'text-green-400 bg-green-500/20';
      case 'allow_with_caution':
        return 'text-yellow-400 bg-yellow-500/20';
      case 'human_approval_needed':
        return 'text-orange-400 bg-orange-500/20';
      case 'deny':
        return 'text-red-400 bg-red-500/20';
      default:
        return 'text-slate-400 bg-slate-500/20';
    }
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision.toLowerCase()) {
      case 'allow':
        return '✓';
      case 'allow_with_caution':
        return '⚠';
      case 'human_approval_needed':
        return '👤';
      case 'deny':
        return '✗';
      default:
        return '?';
    }
  };

  const filteredTrail = auditTrail.filter((entry) => {
    if (filter === 'all') return true;
    if (filter === 'allow') return entry.decision.toLowerCase() === 'allow';
    if (filter === 'deny') return entry.decision.toLowerCase() === 'deny';
    if (filter === 'caution') return entry.decision.toLowerCase() === 'allow_with_caution';
    if (filter === 'approval') return entry.decision.toLowerCase() === 'human_approval_needed';
    return true;
  });

  const decisionCounts = {
    allow: auditTrail.filter(e => e.decision.toLowerCase() === 'allow').length,
    caution: auditTrail.filter(e => e.decision.toLowerCase() === 'allow_with_caution').length,
    approval: auditTrail.filter(e => e.decision.toLowerCase() === 'human_approval_needed').length,
    deny: auditTrail.filter(e => e.decision.toLowerCase() === 'deny').length,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gold-400 flex items-center gap-2">
          <span>📋</span> Ethics Audit Trail
        </h2>
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Filter by requester..."
            value={requesterFilter}
            onChange={(e) => setRequesterFilter(e.target.value)}
            className="bg-slate-700 text-white rounded px-3 py-1 border border-slate-600 focus:border-gold-500 focus:outline-none text-sm w-48"
          />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="bg-slate-700 text-white rounded px-3 py-1 border border-slate-600 focus:border-gold-500 focus:outline-none text-sm"
          >
            <option value="all">All Decisions</option>
            <option value="allow">Allowed</option>
            <option value="caution">With Caution</option>
            <option value="approval">Needs Approval</option>
            <option value="deny">Denied</option>
          </select>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="bg-slate-700 text-white rounded px-3 py-1 border border-slate-600 focus:border-gold-500 focus:outline-none text-sm"
          >
            <option value={25}>25 entries</option>
            <option value={50}>50 entries</option>
            <option value={100}>100 entries</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-green-500/20 rounded-lg p-4 border border-green-500/30">
          <div className="text-green-400 text-2xl font-bold">{decisionCounts.allow}</div>
          <div className="text-slate-400 text-sm">Allowed</div>
        </div>
        <div className="bg-yellow-500/20 rounded-lg p-4 border border-yellow-500/30">
          <div className="text-yellow-400 text-2xl font-bold">{decisionCounts.caution}</div>
          <div className="text-slate-400 text-sm">With Caution</div>
        </div>
        <div className="bg-orange-500/20 rounded-lg p-4 border border-orange-500/30">
          <div className="text-orange-400 text-2xl font-bold">{decisionCounts.approval}</div>
          <div className="text-slate-400 text-sm">Needs Approval</div>
        </div>
        <div className="bg-red-500/20 rounded-lg p-4 border border-red-500/30">
          <div className="text-red-400 text-2xl font-bold">{decisionCounts.deny}</div>
          <div className="text-slate-400 text-sm">Denied</div>
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg border border-gold-500/20 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-700/50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Timestamp</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Action Type</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Requester</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Decision</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Community Impact</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Risk</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-400">Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                    Loading audit trail...
                  </td>
                </tr>
              ) : filteredTrail.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    No audit entries found
                  </td>
                </tr>
              ) : (
                filteredTrail.map((entry) => (
                  <tr key={entry.assessment_id} className="hover:bg-slate-700/30">
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {new Date(entry.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-sm text-white font-medium">
                      {entry.action_type}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {entry.requester_id}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 text-sm px-2 py-1 rounded ${getDecisionColor(entry.decision)}`}>
                        <span>{getDecisionIcon(entry.decision)}</span>
                        {entry.decision.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-600 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              entry.community_impact_score >= 75 ? 'bg-red-500' :
                              entry.community_impact_score >= 50 ? 'bg-orange-500' :
                              entry.community_impact_score >= 25 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${entry.community_impact_score}%` }}
                          />
                        </div>
                        <span className="text-sm text-slate-400">{entry.community_impact_score.toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-600 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              entry.risk_to_community >= 75 ? 'bg-red-500' :
                              entry.risk_to_community >= 50 ? 'bg-orange-500' :
                              entry.risk_to_community >= 25 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${entry.risk_to_community}%` }}
                          />
                        </div>
                        <span className="text-sm text-slate-400">{entry.risk_to_community.toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-500 font-mono">
                      {entry.assessment_hash.substring(0, 8)}...
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-slate-500">
        <span>Showing {filteredTrail.length} of {auditTrail.length} entries</span>
        <button
          onClick={fetchAuditTrail}
          className="text-gold-400 hover:text-gold-300 transition-colors"
        >
          Refresh
        </button>
      </div>
    </div>
  );
}

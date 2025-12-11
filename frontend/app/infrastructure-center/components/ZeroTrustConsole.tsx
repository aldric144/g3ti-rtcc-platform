'use client';

import { useState, useEffect } from 'react';

interface AccessAttempt {
  id: string;
  timestamp: string;
  sourceIp: string;
  userId: string;
  role: string;
  resource: string;
  decision: 'ALLOW' | 'DENY' | 'CHALLENGE' | 'REQUIRE_MFA';
  trustScore: number;
  checksPassed: string[];
  checksFailed: string[];
  reason: string;
}

interface BlockedEntity {
  id: string;
  type: 'ip' | 'device';
  value: string;
  reason: string;
  blockedAt: string;
  blockedBy: string;
}

const mockAccessAttempts: AccessAttempt[] = [
  { id: '1', timestamp: '2024-12-11T06:00:00Z', sourceIp: '10.100.1.45', userId: 'officer_smith', role: 'PATROL_OFFICER', resource: '/api/mdt/dispatch', decision: 'ALLOW', trustScore: 0.92, checksPassed: ['ip_allowlist', 'token_validation', 'role_permissions', 'device_fingerprint'], checksFailed: [], reason: 'Access granted - all critical checks passed' },
  { id: '2', timestamp: '2024-12-11T05:58:00Z', sourceIp: '192.168.50.22', userId: 'analyst_jones', role: 'ANALYST', resource: '/api/analytics/reports', decision: 'ALLOW', trustScore: 0.85, checksPassed: ['ip_allowlist', 'token_validation', 'role_permissions'], checksFailed: ['mtls'], reason: 'Access granted - all critical checks passed' },
  { id: '3', timestamp: '2024-12-11T05:55:00Z', sourceIp: '203.45.67.89', userId: 'unknown', role: '', resource: '/api/admin/users', decision: 'DENY', trustScore: 0.15, checksPassed: [], checksFailed: ['ip_allowlist', 'geo_restriction', 'token_validation'], reason: 'Geographic restriction violation: Country CN not allowed' },
  { id: '4', timestamp: '2024-12-11T05:52:00Z', sourceIp: '10.101.2.100', userId: 'cmd_williams', role: 'RTCC_COMMANDER', resource: '/api/intel/classified', decision: 'REQUIRE_MFA', trustScore: 0.65, checksPassed: ['ip_allowlist', 'token_validation', 'role_permissions'], checksFailed: ['mfa_verified'], reason: 'MFA verification required due to low trust score' },
  { id: '5', timestamp: '2024-12-11T05:48:00Z', sourceIp: '10.100.3.78', userId: 'dispatch_brown', role: 'DISPATCHER', resource: '/api/dispatch/units', decision: 'ALLOW', trustScore: 0.88, checksPassed: ['ip_allowlist', 'token_validation', 'role_permissions', 'device_fingerprint', 'mtls'], checksFailed: [], reason: 'Access granted - all critical checks passed' },
];

const mockBlockedEntities: BlockedEntity[] = [
  { id: '1', type: 'ip', value: '203.45.67.89', reason: 'Repeated unauthorized access attempts', blockedAt: '2024-12-10T14:30:00Z', blockedBy: 'system' },
  { id: '2', type: 'ip', value: '185.220.101.45', reason: 'Known malicious IP (Tor exit node)', blockedAt: '2024-12-08T09:15:00Z', blockedBy: 'threat_intel' },
  { id: '3', type: 'device', value: 'fp_abc123def456', reason: 'Compromised device detected', blockedAt: '2024-12-05T16:45:00Z', blockedBy: 'admin_johnson' },
];

const getDecisionColor = (decision: string) => {
  switch (decision) {
    case 'ALLOW': return 'bg-green-600/20 text-green-400';
    case 'DENY': return 'bg-red-600/20 text-red-400';
    case 'CHALLENGE': return 'bg-yellow-600/20 text-yellow-400';
    case 'REQUIRE_MFA': return 'bg-blue-600/20 text-blue-400';
    default: return 'bg-gray-600/20 text-gray-400';
  }
};

const getTrustScoreColor = (score: number) => {
  if (score >= 0.8) return 'text-green-400';
  if (score >= 0.6) return 'text-yellow-400';
  if (score >= 0.4) return 'text-orange-400';
  return 'text-red-400';
};

export default function ZeroTrustConsole() {
  const [accessAttempts, setAccessAttempts] = useState<AccessAttempt[]>(mockAccessAttempts);
  const [blockedEntities, setBlockedEntities] = useState<BlockedEntity[]>(mockBlockedEntities);
  const [selectedAttempt, setSelectedAttempt] = useState<AccessAttempt | null>(null);
  const [stats, setStats] = useState({ total: 0, allowed: 0, denied: 0, challenged: 0 });

  useEffect(() => {
    const allowed = accessAttempts.filter(a => a.decision === 'ALLOW').length;
    const denied = accessAttempts.filter(a => a.decision === 'DENY').length;
    const challenged = accessAttempts.filter(a => a.decision === 'CHALLENGE' || a.decision === 'REQUIRE_MFA').length;
    setStats({ total: accessAttempts.length, allowed, denied, challenged });
  }, [accessAttempts]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Zero Trust Access Console</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-400">Policy:</span>
          <span className="bg-red-600/20 text-red-400 px-2 py-1 rounded text-sm">Deny All by Default</span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-sm text-gray-400 mb-1">Total Requests (24h)</h3>
          <p className="text-3xl font-bold">{stats.total.toLocaleString()}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
          <h3 className="text-sm text-gray-400 mb-1">Allowed</h3>
          <p className="text-3xl font-bold text-green-400">{stats.allowed.toLocaleString()}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <h3 className="text-sm text-gray-400 mb-1">Denied</h3>
          <p className="text-3xl font-bold text-red-400">{stats.denied.toLocaleString()}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
          <h3 className="text-sm text-gray-400 mb-1">Challenged</h3>
          <p className="text-3xl font-bold text-yellow-400">{stats.challenged.toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-medium mb-4">Recent Access Attempts</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {accessAttempts.map((attempt) => (
              <div
                key={attempt.id}
                onClick={() => setSelectedAttempt(attempt)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedAttempt?.id === attempt.id
                    ? 'bg-blue-600/20 border border-blue-500'
                    : 'bg-gray-900 hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 rounded text-xs ${getDecisionColor(attempt.decision)}`}>
                      {attempt.decision}
                    </span>
                    <span className="text-sm font-medium">{attempt.userId || 'unknown'}</span>
                    <span className="text-xs text-gray-400">({attempt.role || 'no role'})</span>
                  </div>
                  <span className={`text-sm font-bold ${getTrustScoreColor(attempt.trustScore)}`}>
                    {(attempt.trustScore * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{attempt.sourceIp}</span>
                  <span>{attempt.resource}</span>
                  <span>{new Date(attempt.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="font-medium mb-4">Blocked Entities</h3>
            <div className="space-y-2">
              {blockedEntities.map((entity) => (
                <div key={entity.id} className="bg-gray-900 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      entity.type === 'ip' ? 'bg-red-600/20 text-red-400' : 'bg-orange-600/20 text-orange-400'
                    }`}>
                      {entity.type.toUpperCase()}
                    </span>
                    <button className="text-xs text-blue-400 hover:text-blue-300">Unblock</button>
                  </div>
                  <p className="text-sm font-mono">{entity.value}</p>
                  <p className="text-xs text-gray-400 mt-1">{entity.reason}</p>
                </div>
              ))}
            </div>
          </div>

          {selectedAttempt && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="font-medium mb-4">Attempt Details</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-400">Reason:</span>
                  <p className="mt-1">{selectedAttempt.reason}</p>
                </div>
                <div>
                  <span className="text-gray-400">Checks Passed:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedAttempt.checksPassed.map((check, i) => (
                      <span key={i} className="bg-green-600/20 text-green-400 px-2 py-0.5 rounded text-xs">
                        {check}
                      </span>
                    ))}
                  </div>
                </div>
                {selectedAttempt.checksFailed.length > 0 && (
                  <div>
                    <span className="text-gray-400">Checks Failed:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedAttempt.checksFailed.map((check, i) => (
                        <span key={i} className="bg-red-600/20 text-red-400 px-2 py-0.5 rounded text-xs">
                          {check}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-medium mb-4">Geo-Restrictions</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-900 rounded-lg p-3">
            <span className="text-xs text-gray-400">Allowed Countries</span>
            <p className="text-lg font-bold text-green-400">United States</p>
          </div>
          <div className="bg-gray-900 rounded-lg p-3">
            <span className="text-xs text-gray-400">Allowed States</span>
            <p className="text-lg font-bold text-green-400">Florida</p>
          </div>
          <div className="bg-gray-900 rounded-lg p-3">
            <span className="text-xs text-gray-400">Primary Jurisdiction</span>
            <p className="text-lg font-bold text-blue-400">Riviera Beach</p>
          </div>
          <div className="bg-gray-900 rounded-lg p-3">
            <span className="text-xs text-gray-400">Extended Coverage</span>
            <p className="text-lg font-bold text-blue-400">Palm Beach County</p>
          </div>
        </div>
      </div>
    </div>
  );
}

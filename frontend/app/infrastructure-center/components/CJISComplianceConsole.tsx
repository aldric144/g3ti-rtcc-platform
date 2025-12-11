'use client';

import { useState } from 'react';

interface ComplianceRule {
  id: string;
  category: string;
  rule: string;
  status: 'compliant' | 'warning' | 'violation';
  lastChecked: string;
  details: string;
}

interface Violation {
  id: string;
  timestamp: string;
  userId: string;
  violationType: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  actionRequired: string;
  resolved: boolean;
}

interface OfficerUsage {
  userId: string;
  name: string;
  badge: string;
  queriesLast24h: number;
  flaggedQueries: number;
  lastActivity: string;
  complianceScore: number;
}

const mockComplianceRules: ComplianceRule[] = [
  { id: '1', category: 'Password Policy', rule: 'Minimum 8 characters with complexity', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: 'All users meet password requirements' },
  { id: '2', category: 'Password Policy', rule: 'Password change every 90 days', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: '98% compliance rate' },
  { id: '3', category: 'MFA', rule: 'MFA required for remote access', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: 'All remote users have MFA enabled' },
  { id: '4', category: 'MFA', rule: 'MFA required for CJI access', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: '100% compliance' },
  { id: '5', category: 'Session', rule: 'Session timeout after 30 minutes idle', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: 'Enforced at application level' },
  { id: '6', category: 'Encryption', rule: 'AES-256 for data at rest', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: 'All databases encrypted' },
  { id: '7', category: 'Encryption', rule: 'TLS 1.2+ for data in transit', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: 'TLS 1.3 enabled' },
  { id: '8', category: 'Audit', rule: 'Log all CJI access', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: 'Comprehensive audit logging active' },
  { id: '9', category: 'Training', rule: 'Security awareness training annually', status: 'warning', lastChecked: '2024-12-11T06:00:00Z', details: '3 users due for renewal within 30 days' },
  { id: '10', category: 'Background', rule: 'Fingerprint-based background check', status: 'compliant', lastChecked: '2024-12-11T06:00:00Z', details: 'All personnel cleared' },
];

const mockViolations: Violation[] = [
  { id: '1', timestamp: '2024-12-10T14:30:00Z', userId: 'officer_davis', violationType: 'SESSION_TIMEOUT', severity: 'low', description: 'Session exceeded idle timeout', actionRequired: 'Re-authenticate', resolved: true },
  { id: '2', timestamp: '2024-12-09T09:15:00Z', userId: 'analyst_chen', violationType: 'RESTRICTED_QUERY', severity: 'medium', description: 'Query without case number', actionRequired: 'Supervisor review required', resolved: false },
  { id: '3', timestamp: '2024-12-08T16:45:00Z', userId: 'dispatch_wilson', violationType: 'PASSWORD_POLICY', severity: 'medium', description: 'Password expired', actionRequired: 'Change password immediately', resolved: true },
];

const mockOfficerUsage: OfficerUsage[] = [
  { userId: 'officer_smith', name: 'John Smith', badge: 'RB-1234', queriesLast24h: 45, flaggedQueries: 0, lastActivity: '2024-12-11T05:58:00Z', complianceScore: 100 },
  { userId: 'analyst_jones', name: 'Sarah Jones', badge: 'RB-2345', queriesLast24h: 128, flaggedQueries: 2, lastActivity: '2024-12-11T06:00:00Z', complianceScore: 95 },
  { userId: 'cmd_williams', name: 'Mike Williams', badge: 'RB-0001', queriesLast24h: 23, flaggedQueries: 0, lastActivity: '2024-12-11T05:52:00Z', complianceScore: 100 },
  { userId: 'dispatch_brown', name: 'Lisa Brown', badge: 'RB-3456', queriesLast24h: 312, flaggedQueries: 1, lastActivity: '2024-12-11T05:48:00Z', complianceScore: 98 },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'compliant': return 'bg-green-600/20 text-green-400';
    case 'warning': return 'bg-yellow-600/20 text-yellow-400';
    case 'violation': return 'bg-red-600/20 text-red-400';
    default: return 'bg-gray-600/20 text-gray-400';
  }
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'low': return 'bg-blue-600/20 text-blue-400';
    case 'medium': return 'bg-yellow-600/20 text-yellow-400';
    case 'high': return 'bg-orange-600/20 text-orange-400';
    case 'critical': return 'bg-red-600/20 text-red-400';
    default: return 'bg-gray-600/20 text-gray-400';
  }
};

export default function CJISComplianceConsole() {
  const [complianceRules] = useState<ComplianceRule[]>(mockComplianceRules);
  const [violations] = useState<Violation[]>(mockViolations);
  const [officerUsage] = useState<OfficerUsage[]>(mockOfficerUsage);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = ['all', ...new Set(complianceRules.map(r => r.category))];
  const filteredRules = selectedCategory === 'all'
    ? complianceRules
    : complianceRules.filter(r => r.category === selectedCategory);

  const complianceScore = (complianceRules.filter(r => r.status === 'compliant').length / complianceRules.length) * 100;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">CJIS Compliance Console</h2>
        <div className="flex items-center space-x-4">
          <div className="bg-gray-800 rounded-lg px-4 py-2 border border-gray-700">
            <span className="text-sm text-gray-400">CJIS Policy Version:</span>
            <span className="ml-2 font-bold text-blue-400">5.9</span>
          </div>
          <div className="bg-gray-800 rounded-lg px-4 py-2 border border-gray-700">
            <span className="text-sm text-gray-400">Agency ORI:</span>
            <span className="ml-2 font-bold text-blue-400">FL0500400</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
          <h3 className="text-sm text-gray-400 mb-1">Compliance Score</h3>
          <p className={`text-3xl font-bold ${
            complianceScore >= 95 ? 'text-green-400' :
            complianceScore >= 80 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {complianceScore.toFixed(1)}%
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-sm text-gray-400 mb-1">Rules Compliant</h3>
          <p className="text-3xl font-bold text-green-400">
            {complianceRules.filter(r => r.status === 'compliant').length}/{complianceRules.length}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
          <h3 className="text-sm text-gray-400 mb-1">Warnings</h3>
          <p className="text-3xl font-bold text-yellow-400">
            {complianceRules.filter(r => r.status === 'warning').length}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <h3 className="text-sm text-gray-400 mb-1">Active Violations</h3>
          <p className="text-3xl font-bold text-red-400">
            {violations.filter(v => !v.resolved).length}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">Compliance Rules</h3>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-1 text-sm"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat === 'all' ? 'All Categories' : cat}</option>
              ))}
            </select>
          </div>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {filteredRules.map((rule) => (
              <div key={rule.id} className="bg-gray-900 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-400">{rule.category}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${getStatusColor(rule.status)}`}>
                    {rule.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm font-medium">{rule.rule}</p>
                <p className="text-xs text-gray-400 mt-1">{rule.details}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-medium mb-4">Recent Violations & Alerts</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {violations.map((violation) => (
              <div key={violation.id} className={`bg-gray-900 rounded-lg p-3 border-l-4 ${
                violation.resolved ? 'border-gray-600' : 'border-red-500'
              }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className={`px-2 py-0.5 rounded text-xs ${getSeverityColor(violation.severity)}`}>
                    {violation.severity.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(violation.timestamp).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm font-medium">{violation.violationType}</p>
                <p className="text-xs text-gray-400">{violation.description}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-blue-400">{violation.userId}</span>
                  {violation.resolved ? (
                    <span className="text-xs text-green-400">Resolved</span>
                  ) : (
                    <span className="text-xs text-red-400">{violation.actionRequired}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-medium mb-4">Officer Usage Patterns</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-2">Officer</th>
                <th className="pb-2">Badge</th>
                <th className="pb-2">Queries (24h)</th>
                <th className="pb-2">Flagged</th>
                <th className="pb-2">Last Activity</th>
                <th className="pb-2">Compliance</th>
              </tr>
            </thead>
            <tbody>
              {officerUsage.map((officer) => (
                <tr key={officer.userId} className="border-b border-gray-700/50">
                  <td className="py-3">{officer.name}</td>
                  <td className="py-3 font-mono text-gray-400">{officer.badge}</td>
                  <td className="py-3">{officer.queriesLast24h}</td>
                  <td className="py-3">
                    <span className={officer.flaggedQueries > 0 ? 'text-yellow-400' : 'text-green-400'}>
                      {officer.flaggedQueries}
                    </span>
                  </td>
                  <td className="py-3 text-gray-400">
                    {new Date(officer.lastActivity).toLocaleTimeString()}
                  </td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      officer.complianceScore >= 95 ? 'bg-green-600/20 text-green-400' :
                      officer.complianceScore >= 80 ? 'bg-yellow-600/20 text-yellow-400' :
                      'bg-red-600/20 text-red-400'
                    }`}>
                      {officer.complianceScore}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

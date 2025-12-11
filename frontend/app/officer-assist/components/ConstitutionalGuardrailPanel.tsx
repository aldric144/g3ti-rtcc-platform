'use client';

import React, { useState, useEffect } from 'react';

interface GuardrailAlert {
  id: string;
  timestamp: Date;
  officerId: string;
  actionType: string;
  status: 'PASS' | 'WARNING' | 'BLOCKED';
  description: string;
  legalCitation?: string;
  policyReference?: string;
  recommendation?: string;
  riskLevel: string;
}

interface PolicyReference {
  id: string;
  name: string;
  category: string;
  description: string;
  lastUpdated: Date;
}

const mockAlerts: GuardrailAlert[] = [
  {
    id: 'gr-001',
    timestamp: new Date(),
    officerId: 'RBPD-201',
    actionType: 'TRAFFIC_STOP',
    status: 'PASS',
    description: 'Traffic stop initiated with documented reasonable suspicion',
    legalCitation: 'Terry v. Ohio, 392 U.S. 1 (1968)',
    policyReference: 'RBPD Policy 310',
    riskLevel: 'LOW',
  },
  {
    id: 'gr-002',
    timestamp: new Date(Date.now() - 300000),
    officerId: 'RBPD-205',
    actionType: 'CONSENT_SEARCH',
    status: 'WARNING',
    description: 'Consent search - verify voluntary consent documented',
    legalCitation: 'Schneckloth v. Bustamonte, 412 U.S. 218 (1973)',
    policyReference: 'RBPD Policy 315',
    recommendation: 'Ensure consent is freely and voluntarily given',
    riskLevel: 'MEDIUM',
  },
  {
    id: 'gr-003',
    timestamp: new Date(Date.now() - 600000),
    officerId: 'RBPD-210',
    actionType: 'CUSTODIAL_INTERROGATION',
    status: 'BLOCKED',
    description: 'Miranda warnings required before custodial interrogation',
    legalCitation: 'Miranda v. Arizona, 384 U.S. 436 (1966)',
    policyReference: 'RBPD Policy 340',
    recommendation: 'Administer Miranda warnings before questioning',
    riskLevel: 'HIGH',
  },
];

const policyReferences: PolicyReference[] = [
  { id: 'pol-001', name: '4th Amendment - Search & Seizure', category: 'Constitutional', description: 'Protection against unreasonable searches and seizures', lastUpdated: new Date() },
  { id: 'pol-002', name: '5th Amendment - Self-Incrimination', category: 'Constitutional', description: 'Right against self-incrimination, Miranda rights', lastUpdated: new Date() },
  { id: 'pol-003', name: '14th Amendment - Due Process', category: 'Constitutional', description: 'Due process and equal protection', lastUpdated: new Date() },
  { id: 'pol-004', name: 'RBPD Use of Force Policy', category: 'Department', description: 'Policy 300 - Use of Force guidelines', lastUpdated: new Date() },
  { id: 'pol-005', name: 'RBPD Pursuit Policy', category: 'Department', description: 'Policy 314 - Vehicle pursuit guidelines', lastUpdated: new Date() },
  { id: 'pol-006', name: 'RBPD Bias-Free Policing', category: 'Department', description: 'Policy 402 - Bias-free policing requirements', lastUpdated: new Date() },
];

export default function ConstitutionalGuardrailPanel() {
  const [alerts, setAlerts] = useState<GuardrailAlert[]>(mockAlerts);
  const [selectedAlert, setSelectedAlert] = useState<GuardrailAlert | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const filteredAlerts = alerts.filter(alert => 
    filterStatus === 'all' || alert.status === filterStatus
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PASS': return 'bg-green-500';
      case 'WARNING': return 'bg-yellow-500';
      case 'BLOCKED': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusBgColor = (status: string) => {
    switch (status) {
      case 'PASS': return 'bg-green-900/30 border-green-700';
      case 'WARNING': return 'bg-yellow-900/30 border-yellow-700';
      case 'BLOCKED': return 'bg-red-900/30 border-red-700';
      default: return 'bg-gray-900/30 border-gray-700';
    }
  };

  const stats = {
    total: alerts.length,
    pass: alerts.filter(a => a.status === 'PASS').length,
    warning: alerts.filter(a => a.status === 'WARNING').length,
    blocked: alerts.filter(a => a.status === 'BLOCKED').length,
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-white">{stats.total}</div>
          <div className="text-gray-400 text-sm">Total Checks</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
          <div className="text-3xl font-bold text-green-400">{stats.pass}</div>
          <div className="text-gray-400 text-sm">Passed</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
          <div className="text-3xl font-bold text-yellow-400">{stats.warning}</div>
          <div className="text-gray-400 text-sm">Warnings</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <div className="text-3xl font-bold text-red-400">{stats.blocked}</div>
          <div className="text-gray-400 text-sm">Blocked</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Live Alerts</h2>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white"
            >
              <option value="all">All Status</option>
              <option value="PASS">Pass</option>
              <option value="WARNING">Warning</option>
              <option value="BLOCKED">Blocked</option>
            </select>
          </div>

          <div className="space-y-3">
            {filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                onClick={() => setSelectedAlert(alert)}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${getStatusBgColor(alert.status)} ${
                  selectedAlert?.id === alert.id ? 'ring-2 ring-blue-500' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(alert.status)}`} />
                    <div>
                      <div className="font-medium text-white">{alert.actionType.replace(/_/g, ' ')}</div>
                      <div className="text-sm text-gray-400">Officer: {alert.officerId}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-medium ${
                      alert.status === 'PASS' ? 'text-green-400' :
                      alert.status === 'WARNING' ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {alert.status}
                    </div>
                    <div className="text-xs text-gray-500">
                      {alert.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
                <p className="mt-2 text-sm text-gray-300">{alert.description}</p>
                {alert.recommendation && (
                  <p className="mt-2 text-sm text-yellow-300">
                    Recommendation: {alert.recommendation}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-white">Policy References</h2>
          <div className="space-y-2">
            {policyReferences.map((policy) => (
              <div
                key={policy.id}
                className="p-3 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-600 cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium text-white text-sm">{policy.name}</div>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    policy.category === 'Constitutional' ? 'bg-blue-900 text-blue-300' : 'bg-purple-900 text-purple-300'
                  }`}>
                    {policy.category}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">{policy.description}</p>
              </div>
            ))}
          </div>

          {selectedAlert && (
            <div className="mt-6 p-4 bg-gray-800 rounded-lg border border-gray-700">
              <h3 className="font-semibold text-white mb-3">Alert Details</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-gray-400">Legal Citation:</span>
                  <p className="text-blue-300">{selectedAlert.legalCitation || 'N/A'}</p>
                </div>
                <div>
                  <span className="text-gray-400">Policy Reference:</span>
                  <p className="text-purple-300">{selectedAlert.policyReference || 'N/A'}</p>
                </div>
                <div>
                  <span className="text-gray-400">Risk Level:</span>
                  <p className={`font-medium ${
                    selectedAlert.riskLevel === 'LOW' ? 'text-green-400' :
                    selectedAlert.riskLevel === 'MEDIUM' ? 'text-yellow-400' : 'text-red-400'
                  }`}>{selectedAlert.riskLevel}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

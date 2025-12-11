'use client';

import React, { useState, useEffect } from 'react';

interface Alert {
  id: string;
  timestamp: Date;
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  officerId: string;
  incidentId?: string;
  description: string;
  recommendation: string;
  acknowledged: boolean;
  resolved: boolean;
  source: string;
}

interface OfficerSummary {
  officerId: string;
  name: string;
  status: string;
  riskScore: number;
  activeIncident: boolean;
  lastUpdate: Date;
}

const mockAlerts: Alert[] = [
  {
    id: 'alert-001',
    timestamp: new Date(),
    type: 'USE_OF_FORCE_RISK',
    severity: 'CRITICAL',
    officerId: 'RBPD-210',
    incidentId: 'INC-2024-003',
    description: 'RED level use-of-force risk - armed suspect, officer in danger zone',
    recommendation: 'Respond to scene immediately or dispatch additional units',
    acknowledged: false,
    resolved: false,
    source: 'force_monitor',
  },
  {
    id: 'alert-002',
    timestamp: new Date(Date.now() - 300000),
    type: 'CONSTITUTIONAL_VIOLATION',
    severity: 'HIGH',
    officerId: 'RBPD-205',
    description: 'Miranda warning required before custodial interrogation',
    recommendation: 'Advise officer to administer Miranda warnings',
    acknowledged: false,
    resolved: false,
    source: 'guardrail_engine',
  },
  {
    id: 'alert-003',
    timestamp: new Date(Date.now() - 600000),
    type: 'FATIGUE_WARNING',
    severity: 'HIGH',
    officerId: 'RBPD-210',
    description: 'Officer fatigue level SEVERE - 13.5 hours on duty',
    recommendation: 'Consider mandatory rest period',
    acknowledged: true,
    resolved: false,
    source: 'safety_engine',
  },
  {
    id: 'alert-004',
    timestamp: new Date(Date.now() - 900000),
    type: 'POLICY_CONFLICT',
    severity: 'MEDIUM',
    officerId: 'RBPD-201',
    description: 'Consent search - verify voluntary consent documented',
    recommendation: 'Ensure consent is freely and voluntarily given',
    acknowledged: true,
    resolved: true,
    source: 'guardrail_engine',
  },
];

const mockOfficers: OfficerSummary[] = [
  { officerId: 'RBPD-201', name: 'Officer Johnson', status: 'ON_SCENE', riskScore: 0.25, activeIncident: true, lastUpdate: new Date() },
  { officerId: 'RBPD-205', name: 'Officer Martinez', status: 'AVAILABLE', riskScore: 0.55, activeIncident: false, lastUpdate: new Date() },
  { officerId: 'RBPD-210', name: 'Officer Williams', status: 'ON_SCENE', riskScore: 0.85, activeIncident: true, lastUpdate: new Date() },
  { officerId: 'RBPD-215', name: 'Officer Davis', status: 'AVAILABLE', riskScore: 0.15, activeIncident: false, lastUpdate: new Date() },
  { officerId: 'RBPD-220', name: 'Officer Brown', status: 'OUT_OF_SERVICE', riskScore: 0.30, activeIncident: false, lastUpdate: new Date() },
];

export default function SupervisorDashboard() {
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts);
  const [officers, setOfficers] = useState<OfficerSummary[]>(mockOfficers);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [showResolved, setShowResolved] = useState(false);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'LOW': return 'text-blue-400 bg-blue-900/30 border-blue-700';
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-900/30 border-yellow-700';
      case 'HIGH': return 'text-orange-400 bg-orange-900/30 border-orange-700';
      case 'CRITICAL': return 'text-red-400 bg-red-900/30 border-red-700';
      default: return 'text-gray-400 bg-gray-900/30 border-gray-700';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'AVAILABLE': return 'text-green-400';
      case 'ON_SCENE': return 'text-blue-400';
      case 'OUT_OF_SERVICE': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 0.3) return 'text-green-400';
    if (score < 0.6) return 'text-yellow-400';
    if (score < 0.8) return 'text-orange-400';
    return 'text-red-400';
  };

  const filteredAlerts = alerts.filter(alert => {
    if (!showResolved && alert.resolved) return false;
    if (filterSeverity !== 'all' && alert.severity !== filterSeverity) return false;
    return true;
  });

  const acknowledgeAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    ));
  };

  const resolveAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, resolved: true } : alert
    ));
  };

  const stats = {
    totalAlerts: alerts.filter(a => !a.resolved).length,
    unacknowledged: alerts.filter(a => !a.acknowledged && !a.resolved).length,
    critical: alerts.filter(a => a.severity === 'CRITICAL' && !a.resolved).length,
    officersOnDuty: officers.filter(o => o.status !== 'OUT_OF_SERVICE').length,
    highRiskOfficers: officers.filter(o => o.riskScore >= 0.6).length,
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-white">{stats.totalAlerts}</div>
          <div className="text-gray-400 text-sm">Active Alerts</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <div className="text-3xl font-bold text-red-400">{stats.unacknowledged}</div>
          <div className="text-gray-400 text-sm">Unacknowledged</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <div className="text-3xl font-bold text-red-400">{stats.critical}</div>
          <div className="text-gray-400 text-sm">Critical</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-blue-700">
          <div className="text-3xl font-bold text-blue-400">{stats.officersOnDuty}</div>
          <div className="text-gray-400 text-sm">Officers On Duty</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-orange-700">
          <div className="text-3xl font-bold text-orange-400">{stats.highRiskOfficers}</div>
          <div className="text-gray-400 text-sm">High Risk Officers</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Alert Queue</h2>
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 text-sm text-gray-400">
                <input
                  type="checkbox"
                  checked={showResolved}
                  onChange={(e) => setShowResolved(e.target.checked)}
                  className="rounded bg-gray-700 border-gray-600"
                />
                <span>Show Resolved</span>
              </label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white"
              >
                <option value="all">All Severity</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          <div className="space-y-3">
            {filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)} ${
                  alert.severity === 'CRITICAL' && !alert.acknowledged ? 'animate-pulse' : ''
                } ${alert.resolved ? 'opacity-50' : ''}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className={`w-3 h-3 rounded-full mt-1 ${
                      alert.severity === 'CRITICAL' ? 'bg-red-500' :
                      alert.severity === 'HIGH' ? 'bg-orange-500' :
                      alert.severity === 'MEDIUM' ? 'bg-yellow-500' : 'bg-blue-500'
                    }`} />
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-white">{alert.type.replace(/_/g, ' ')}</span>
                        <span className={`text-xs px-2 py-0.5 rounded ${getSeverityColor(alert.severity)}`}>
                          {alert.severity}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400 mt-1">
                        Officer: {alert.officerId} {alert.incidentId && `| Incident: ${alert.incidentId}`}
                      </div>
                      <p className="text-sm text-gray-300 mt-2">{alert.description}</p>
                      <p className="text-sm text-blue-300 mt-1">
                        Recommendation: {alert.recommendation}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">
                      {alert.timestamp.toLocaleTimeString()}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Source: {alert.source}
                    </div>
                  </div>
                </div>

                {!alert.resolved && (
                  <div className="mt-3 flex items-center space-x-3">
                    {!alert.acknowledged && (
                      <button
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                      >
                        Acknowledge
                      </button>
                    )}
                    <button
                      onClick={() => resolveAlert(alert.id)}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                    >
                      Resolve
                    </button>
                    <button className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded transition-colors">
                      View Details
                    </button>
                  </div>
                )}

                {alert.acknowledged && !alert.resolved && (
                  <div className="mt-2 text-xs text-green-400">
                    Acknowledged
                  </div>
                )}
              </div>
            ))}

            {filteredAlerts.length === 0 && (
              <div className="p-8 text-center text-gray-500">
                No alerts matching current filters
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-white">Officer Status</h2>
          <div className="space-y-3">
            {officers.map((officer) => (
              <div
                key={officer.officerId}
                className={`p-3 rounded-lg border ${
                  officer.riskScore >= 0.6 ? 'bg-red-900/20 border-red-700' : 'bg-gray-800 border-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-white">{officer.name}</div>
                    <div className="text-sm text-gray-400">{officer.officerId}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${getRiskColor(officer.riskScore)}`}>
                      {(officer.riskScore * 100).toFixed(0)}%
                    </div>
                    <div className={`text-xs ${getStatusColor(officer.status)}`}>
                      {officer.status.replace(/_/g, ' ')}
                    </div>
                  </div>
                </div>
                {officer.activeIncident && (
                  <div className="mt-2 text-xs text-blue-400">
                    Active Incident
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors">
                Emergency Broadcast
              </button>
              <button className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
                Request All Units Status
              </button>
              <button className="w-full px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded transition-colors">
                Dispatch Backup
              </button>
              <button className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded transition-colors">
                Generate Shift Report
              </button>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-3">Civil Liability Events</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Today</span>
                <span className="text-white">0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">This Week</span>
                <span className="text-white">2</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">This Month</span>
                <span className="text-white">5</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

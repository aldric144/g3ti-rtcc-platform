'use client';

import React, { useState, useEffect } from 'react';

interface ForceAssessment {
  id: string;
  incidentId: string;
  officerId: string;
  timestamp: Date;
  riskLevel: 'GREEN' | 'YELLOW' | 'RED';
  riskScore: number;
  suspectBehavior: string;
  escalationPattern: string;
  weaponDetected: boolean;
  weaponType: string;
  riskFactors: string[];
  protectiveFactors: string[];
  recommendedActions: string[];
  supervisorNotified: boolean;
  backupRequested: boolean;
  deEscalationRecommended: boolean;
}

const mockAssessments: ForceAssessment[] = [
  {
    id: 'fra-001',
    incidentId: 'INC-2024-001',
    officerId: 'RBPD-201',
    timestamp: new Date(),
    riskLevel: 'GREEN',
    riskScore: 0.25,
    suspectBehavior: 'COMPLIANT',
    escalationPattern: 'STABLE',
    weaponDetected: false,
    weaponType: 'NONE',
    riskFactors: [],
    protectiveFactors: ['Safe distance maintained (50 ft)', 'Scene is de-escalating'],
    recommendedActions: ['Continue de-escalation efforts', 'Maintain situational awareness'],
    supervisorNotified: false,
    backupRequested: false,
    deEscalationRecommended: false,
  },
  {
    id: 'fra-002',
    incidentId: 'INC-2024-002',
    officerId: 'RBPD-205',
    timestamp: new Date(Date.now() - 300000),
    riskLevel: 'YELLOW',
    riskScore: 0.55,
    suspectBehavior: 'ACTIVE_RESISTANT',
    escalationPattern: 'SLOWLY_ESCALATING',
    weaponDetected: false,
    weaponType: 'NONE',
    riskFactors: ['Suspect behavior: ACTIVE_RESISTANT', 'Scene escalation: SLOWLY_ESCALATING', 'Officer in caution zone (35 ft)'],
    protectiveFactors: ['Backup arriving in 2.0 minutes'],
    recommendedActions: ['Attempt verbal de-escalation', 'Continue de-escalation efforts', 'Maintain situational awareness'],
    supervisorNotified: false,
    backupRequested: false,
    deEscalationRecommended: true,
  },
  {
    id: 'fra-003',
    incidentId: 'INC-2024-003',
    officerId: 'RBPD-210',
    timestamp: new Date(Date.now() - 600000),
    riskLevel: 'RED',
    riskScore: 0.85,
    suspectBehavior: 'ASSAULTIVE',
    escalationPattern: 'RAPIDLY_ESCALATING',
    weaponDetected: true,
    weaponType: 'EDGED_WEAPON',
    riskFactors: ['Suspect behavior: ASSAULTIVE', 'Scene escalation: RAPIDLY_ESCALATING', 'Weapon detected: EDGED_WEAPON (75% confidence)', 'Officer in danger zone (15 ft)'],
    protectiveFactors: [],
    recommendedActions: ['Attempt verbal de-escalation', 'Request immediate backup', 'Notify supervisor immediately', 'Prepare for potential force application', 'Increase distance if tactically feasible'],
    supervisorNotified: true,
    backupRequested: true,
    deEscalationRecommended: true,
  },
];

export default function UseOfForceHeatMeter() {
  const [assessments, setAssessments] = useState<ForceAssessment[]>(mockAssessments);
  const [selectedAssessment, setSelectedAssessment] = useState<ForceAssessment | null>(null);
  const [activeIncident, setActiveIncident] = useState<ForceAssessment | null>(mockAssessments[2]);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'GREEN': return 'text-green-400';
      case 'YELLOW': return 'text-yellow-400';
      case 'RED': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getRiskBgColor = (level: string) => {
    switch (level) {
      case 'GREEN': return 'bg-green-900/30 border-green-700';
      case 'YELLOW': return 'bg-yellow-900/30 border-yellow-700';
      case 'RED': return 'bg-red-900/30 border-red-700';
      default: return 'bg-gray-900/30 border-gray-700';
    }
  };

  const getGaugeRotation = (score: number) => {
    return -90 + (score * 180);
  };

  const stats = {
    total: assessments.length,
    green: assessments.filter(a => a.riskLevel === 'GREEN').length,
    yellow: assessments.filter(a => a.riskLevel === 'YELLOW').length,
    red: assessments.filter(a => a.riskLevel === 'RED').length,
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-white">{stats.total}</div>
          <div className="text-gray-400 text-sm">Active Assessments</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
          <div className="text-3xl font-bold text-green-400">{stats.green}</div>
          <div className="text-gray-400 text-sm">Green Level</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
          <div className="text-3xl font-bold text-yellow-400">{stats.yellow}</div>
          <div className="text-gray-400 text-sm">Yellow Level</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <div className="text-3xl font-bold text-red-400">{stats.red}</div>
          <div className="text-gray-400 text-sm">Red Level</div>
        </div>
      </div>

      {activeIncident && activeIncident.riskLevel === 'RED' && (
        <div className="bg-red-900/50 border-2 border-red-500 rounded-lg p-4 animate-pulse">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-4 h-4 bg-red-500 rounded-full animate-ping" />
              <div>
                <div className="text-red-300 font-bold text-lg">RED LEVEL ALERT</div>
                <div className="text-red-200">Incident: {activeIncident.incidentId} | Officer: {activeIncident.officerId}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-red-300 text-2xl font-bold">{(activeIncident.riskScore * 100).toFixed(0)}%</div>
              <div className="text-red-400 text-sm">Risk Score</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h3 className="text-white font-semibold mb-4 text-center">Force Risk Gauge</h3>
            
            <div className="relative w-48 h-24 mx-auto mb-4">
              <svg viewBox="0 0 200 100" className="w-full h-full">
                <defs>
                  <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#22c55e" />
                    <stop offset="50%" stopColor="#eab308" />
                    <stop offset="100%" stopColor="#ef4444" />
                  </linearGradient>
                </defs>
                
                <path
                  d="M 20 90 A 80 80 0 0 1 180 90"
                  fill="none"
                  stroke="url(#gaugeGradient)"
                  strokeWidth="15"
                  strokeLinecap="round"
                />
                
                <g transform={`rotate(${getGaugeRotation(activeIncident?.riskScore || 0)}, 100, 90)`}>
                  <line
                    x1="100"
                    y1="90"
                    x2="100"
                    y2="30"
                    stroke="white"
                    strokeWidth="3"
                    strokeLinecap="round"
                  />
                  <circle cx="100" cy="90" r="8" fill="white" />
                </g>
                
                <text x="20" y="98" fill="#22c55e" fontSize="10" fontWeight="bold">GREEN</text>
                <text x="85" y="15" fill="#eab308" fontSize="10" fontWeight="bold">YELLOW</text>
                <text x="155" y="98" fill="#ef4444" fontSize="10" fontWeight="bold">RED</text>
              </svg>
            </div>

            <div className="text-center">
              <div className={`text-4xl font-bold ${getRiskColor(activeIncident?.riskLevel || 'GREEN')}`}>
                {activeIncident?.riskLevel || 'GREEN'}
              </div>
              <div className="text-gray-400 text-sm mt-1">
                Risk Score: {((activeIncident?.riskScore || 0) * 100).toFixed(0)}%
              </div>
            </div>

            {activeIncident && (
              <div className="mt-4 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Suspect Behavior:</span>
                  <span className="text-white">{activeIncident.suspectBehavior.replace(/_/g, ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Escalation:</span>
                  <span className="text-white">{activeIncident.escalationPattern.replace(/_/g, ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Weapon:</span>
                  <span className={activeIncident.weaponDetected ? 'text-red-400' : 'text-green-400'}>
                    {activeIncident.weaponDetected ? activeIncident.weaponType.replace(/_/g, ' ') : 'None'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="col-span-2 space-y-4">
          <h3 className="text-white font-semibold">Active Incidents</h3>
          <div className="space-y-3">
            {assessments.map((assessment) => (
              <div
                key={assessment.id}
                onClick={() => {
                  setSelectedAssessment(assessment);
                  setActiveIncident(assessment);
                }}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${getRiskBgColor(assessment.riskLevel)} ${
                  activeIncident?.id === assessment.id ? 'ring-2 ring-blue-500' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-4 h-4 rounded-full ${
                      assessment.riskLevel === 'GREEN' ? 'bg-green-500' :
                      assessment.riskLevel === 'YELLOW' ? 'bg-yellow-500' : 'bg-red-500'
                    } ${assessment.riskLevel === 'RED' ? 'animate-pulse' : ''}`} />
                    <div>
                      <div className="font-medium text-white">{assessment.incidentId}</div>
                      <div className="text-sm text-gray-400">Officer: {assessment.officerId}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-xl font-bold ${getRiskColor(assessment.riskLevel)}`}>
                      {assessment.riskLevel}
                    </div>
                    <div className="text-xs text-gray-500">
                      {(assessment.riskScore * 100).toFixed(0)}% risk
                    </div>
                  </div>
                </div>

                {assessment.riskFactors.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {assessment.riskFactors.slice(0, 3).map((factor, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-700/50 text-gray-300 rounded text-xs">
                        {factor}
                      </span>
                    ))}
                  </div>
                )}

                {assessment.recommendedActions.length > 0 && (
                  <div className="mt-3 p-2 bg-gray-800/50 rounded">
                    <div className="text-xs text-gray-400 mb-1">Recommended Action:</div>
                    <div className="text-sm text-white">{assessment.recommendedActions[0]}</div>
                  </div>
                )}

                <div className="mt-3 flex items-center space-x-4 text-xs">
                  {assessment.supervisorNotified && (
                    <span className="text-yellow-400">Supervisor Notified</span>
                  )}
                  {assessment.backupRequested && (
                    <span className="text-blue-400">Backup Requested</span>
                  )}
                  {assessment.deEscalationRecommended && (
                    <span className="text-green-400">De-escalation Recommended</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedAssessment && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-white font-semibold mb-4">Assessment Details: {selectedAssessment.incidentId}</h3>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h4 className="text-red-400 font-medium mb-2">Risk Factors</h4>
              {selectedAssessment.riskFactors.length > 0 ? (
                <ul className="space-y-1">
                  {selectedAssessment.riskFactors.map((factor, index) => (
                    <li key={index} className="text-sm text-gray-300 flex items-start space-x-2">
                      <span className="text-red-400">•</span>
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm">No risk factors identified</p>
              )}
            </div>
            <div>
              <h4 className="text-green-400 font-medium mb-2">Protective Factors</h4>
              {selectedAssessment.protectiveFactors.length > 0 ? (
                <ul className="space-y-1">
                  {selectedAssessment.protectiveFactors.map((factor, index) => (
                    <li key={index} className="text-sm text-gray-300 flex items-start space-x-2">
                      <span className="text-green-400">•</span>
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm">No protective factors identified</p>
              )}
            </div>
          </div>
          <div className="mt-4">
            <h4 className="text-blue-400 font-medium mb-2">Recommended Actions</h4>
            <ul className="space-y-1">
              {selectedAssessment.recommendedActions.map((action, index) => (
                <li key={index} className="text-sm text-gray-300 flex items-start space-x-2">
                  <span className="text-blue-400">→</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

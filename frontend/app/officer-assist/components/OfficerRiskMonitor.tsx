'use client';

import React, { useState, useEffect } from 'react';

interface OfficerStatus {
  officerId: string;
  name: string;
  badge: string;
  overallRiskScore: number;
  fatigueLevel: string;
  fatigueScore: number;
  stressScore: number;
  workloadScore: number;
  traumaExposureScore: number;
  hoursOnDuty: number;
  callsHandled: number;
  highStressCalls: number;
  breaksTaken: number;
  consecutiveDays: number;
  fitForDuty: boolean;
  supervisorReviewRequired: boolean;
  patternFlags: string[];
  recommendations: string[];
}

const mockOfficers: OfficerStatus[] = [
  {
    officerId: 'RBPD-201',
    name: 'Officer Johnson',
    badge: '2451',
    overallRiskScore: 0.25,
    fatigueLevel: 'NORMAL',
    fatigueScore: 0.2,
    stressScore: 0.3,
    workloadScore: 0.25,
    traumaExposureScore: 0.1,
    hoursOnDuty: 6.5,
    callsHandled: 8,
    highStressCalls: 1,
    breaksTaken: 1,
    consecutiveDays: 3,
    fitForDuty: true,
    supervisorReviewRequired: false,
    patternFlags: [],
    recommendations: [],
  },
  {
    officerId: 'RBPD-205',
    name: 'Officer Martinez',
    badge: '2467',
    overallRiskScore: 0.55,
    fatigueLevel: 'MODERATE',
    fatigueScore: 0.6,
    stressScore: 0.5,
    workloadScore: 0.55,
    traumaExposureScore: 0.3,
    hoursOnDuty: 10.2,
    callsHandled: 15,
    highStressCalls: 4,
    breaksTaken: 0,
    consecutiveDays: 5,
    fitForDuty: true,
    supervisorReviewRequired: true,
    patternFlags: ['High stress events: 5 in 30 days'],
    recommendations: ['Take mandatory rest break', 'Peer support contact recommended'],
  },
  {
    officerId: 'RBPD-210',
    name: 'Officer Williams',
    badge: '2489',
    overallRiskScore: 0.78,
    fatigueLevel: 'SEVERE',
    fatigueScore: 0.85,
    stressScore: 0.7,
    workloadScore: 0.8,
    traumaExposureScore: 0.6,
    hoursOnDuty: 13.5,
    callsHandled: 22,
    highStressCalls: 6,
    breaksTaken: 0,
    consecutiveDays: 6,
    fitForDuty: false,
    supervisorReviewRequired: true,
    patternFlags: ['Fatigue critical', 'No breaks taken', 'Trauma exposure elevated'],
    recommendations: ['IMMEDIATE: Remove from active duty pending review', 'Schedule wellness check', 'Consider counseling referral'],
  },
];

export default function OfficerRiskMonitor() {
  const [officers, setOfficers] = useState<OfficerStatus[]>(mockOfficers);
  const [selectedOfficer, setSelectedOfficer] = useState<OfficerStatus | null>(null);
  const [filterRisk, setFilterRisk] = useState<string>('all');

  const getRiskColor = (score: number) => {
    if (score < 0.3) return 'text-green-400';
    if (score < 0.6) return 'text-yellow-400';
    if (score < 0.8) return 'text-orange-400';
    return 'text-red-400';
  };

  const getRiskBgColor = (score: number) => {
    if (score < 0.3) return 'bg-green-900/30 border-green-700';
    if (score < 0.6) return 'bg-yellow-900/30 border-yellow-700';
    if (score < 0.8) return 'bg-orange-900/30 border-orange-700';
    return 'bg-red-900/30 border-red-700';
  };

  const getFatigueColor = (level: string) => {
    switch (level) {
      case 'NORMAL': return 'text-green-400';
      case 'MILD': return 'text-blue-400';
      case 'MODERATE': return 'text-yellow-400';
      case 'SEVERE': return 'text-orange-400';
      case 'CRITICAL': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const filteredOfficers = officers.filter(officer => {
    if (filterRisk === 'all') return true;
    if (filterRisk === 'high') return officer.overallRiskScore >= 0.6;
    if (filterRisk === 'review') return officer.supervisorReviewRequired;
    return true;
  });

  const stats = {
    total: officers.length,
    fitForDuty: officers.filter(o => o.fitForDuty).length,
    reviewRequired: officers.filter(o => o.supervisorReviewRequired).length,
    highRisk: officers.filter(o => o.overallRiskScore >= 0.6).length,
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-white">{stats.total}</div>
          <div className="text-gray-400 text-sm">Officers Monitored</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
          <div className="text-3xl font-bold text-green-400">{stats.fitForDuty}</div>
          <div className="text-gray-400 text-sm">Fit for Duty</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
          <div className="text-3xl font-bold text-yellow-400">{stats.reviewRequired}</div>
          <div className="text-gray-400 text-sm">Review Required</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <div className="text-3xl font-bold text-red-400">{stats.highRisk}</div>
          <div className="text-gray-400 text-sm">High Risk</div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Officer Status</h2>
        <select
          value={filterRisk}
          onChange={(e) => setFilterRisk(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white"
        >
          <option value="all">All Officers</option>
          <option value="high">High Risk</option>
          <option value="review">Review Required</option>
        </select>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          {filteredOfficers.map((officer) => (
            <div
              key={officer.officerId}
              onClick={() => setSelectedOfficer(officer)}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${getRiskBgColor(officer.overallRiskScore)} ${
                selectedOfficer?.officerId === officer.officerId ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-full bg-gray-700 flex items-center justify-center">
                    <span className="text-white font-bold">{officer.badge}</span>
                  </div>
                  <div>
                    <div className="font-medium text-white">{officer.name}</div>
                    <div className="text-sm text-gray-400">{officer.officerId}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${getRiskColor(officer.overallRiskScore)}`}>
                    {(officer.overallRiskScore * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">Risk Score</div>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-400">Fatigue</div>
                  <div className={getFatigueColor(officer.fatigueLevel)}>{officer.fatigueLevel}</div>
                </div>
                <div>
                  <div className="text-gray-400">Hours on Duty</div>
                  <div className="text-white">{officer.hoursOnDuty.toFixed(1)}h</div>
                </div>
                <div>
                  <div className="text-gray-400">Calls Handled</div>
                  <div className="text-white">{officer.callsHandled}</div>
                </div>
                <div>
                  <div className="text-gray-400">High Stress</div>
                  <div className={officer.highStressCalls > 3 ? 'text-red-400' : 'text-white'}>
                    {officer.highStressCalls}
                  </div>
                </div>
              </div>

              {!officer.fitForDuty && (
                <div className="mt-3 px-3 py-2 bg-red-900/50 rounded text-red-300 text-sm">
                  NOT FIT FOR DUTY - Immediate action required
                </div>
              )}

              {officer.patternFlags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {officer.patternFlags.map((flag, index) => (
                    <span key={index} className="px-2 py-1 bg-yellow-900/50 text-yellow-300 rounded text-xs">
                      {flag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="space-y-4">
          {selectedOfficer ? (
            <>
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h3 className="text-white font-semibold mb-4">Risk Breakdown</h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Fatigue</span>
                      <span className={getRiskColor(selectedOfficer.fatigueScore)}>
                        {(selectedOfficer.fatigueScore * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${selectedOfficer.fatigueScore < 0.3 ? 'bg-green-500' : selectedOfficer.fatigueScore < 0.6 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${selectedOfficer.fatigueScore * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Stress</span>
                      <span className={getRiskColor(selectedOfficer.stressScore)}>
                        {(selectedOfficer.stressScore * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${selectedOfficer.stressScore < 0.3 ? 'bg-green-500' : selectedOfficer.stressScore < 0.6 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${selectedOfficer.stressScore * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Workload</span>
                      <span className={getRiskColor(selectedOfficer.workloadScore)}>
                        {(selectedOfficer.workloadScore * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${selectedOfficer.workloadScore < 0.3 ? 'bg-green-500' : selectedOfficer.workloadScore < 0.6 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${selectedOfficer.workloadScore * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Trauma Exposure</span>
                      <span className={getRiskColor(selectedOfficer.traumaExposureScore)}>
                        {(selectedOfficer.traumaExposureScore * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${selectedOfficer.traumaExposureScore < 0.3 ? 'bg-green-500' : selectedOfficer.traumaExposureScore < 0.6 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${selectedOfficer.traumaExposureScore * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h3 className="text-white font-semibold mb-3">24-Hour Workload</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <div className="text-gray-400">Consecutive Days</div>
                    <div className="text-white font-medium">{selectedOfficer.consecutiveDays}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">Breaks Taken</div>
                    <div className={selectedOfficer.breaksTaken === 0 ? 'text-red-400 font-medium' : 'text-white font-medium'}>
                      {selectedOfficer.breaksTaken}
                    </div>
                  </div>
                </div>
              </div>

              {selectedOfficer.recommendations.length > 0 && (
                <div className="bg-gray-800 rounded-lg border border-yellow-700 p-4">
                  <h3 className="text-yellow-400 font-semibold mb-3">Recommendations</h3>
                  <ul className="space-y-2">
                    {selectedOfficer.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-300 flex items-start space-x-2">
                        <span className="text-yellow-400">→</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
              <p className="text-gray-400">Select an officer to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

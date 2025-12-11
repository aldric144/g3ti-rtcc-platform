'use client';

import React, { useState, useEffect } from 'react';

interface CoverPosition {
  id: string;
  description: string;
  coverType: string;
  distanceFeet: number;
  direction: string;
  effectiveness: number;
}

interface EscapeRoute {
  id: string;
  description: string;
  probability: number;
  direction: string;
  vehicleAccessible: boolean;
  interceptPoints: string[];
}

interface BackupUnit {
  unitId: string;
  unitType: string;
  etaMinutes: number;
  distanceMiles: number;
  status: string;
}

interface TacticalAdvice {
  id: string;
  scenario: string;
  threatLevel: string;
  primaryRecommendation: string;
  tacticalNotes: string[];
  warnings: string[];
  deEscalationOptions: string[];
  coverPositions: CoverPosition[];
  escapeRoutes: EscapeRoute[];
  backupUnits: BackupUnit[];
  communicationPlan: string;
  containmentStrategy: string;
  lethalCoverRequired: boolean;
  k9Recommended: boolean;
  airSupportRecommended: boolean;
}

const mockAdvice: TacticalAdvice = {
  id: 'ta-001',
  scenario: 'TRAFFIC_STOP',
  threatLevel: 'MODERATE',
  primaryRecommendation: 'Standard traffic stop approach - maintain tactical positioning',
  tacticalNotes: [
    'Position patrol vehicle offset to driver\'s side rear',
    'Use high beams and spotlight to illuminate vehicle interior',
    'Approach from driver\'s side rear quarter panel',
    'Maintain awareness of passenger compartment',
  ],
  warnings: [
    'Multiple occupants detected - maintain heightened awareness',
  ],
  deEscalationOptions: [
    'Use calm, clear verbal commands',
    'Explain reason for stop',
    'Allow subject to ask questions',
  ],
  coverPositions: [
    { id: 'cp-001', description: 'Engine block of patrol vehicle', coverType: 'HARD_COVER', distanceFeet: 15, direction: 'rear', effectiveness: 0.95 },
    { id: 'cp-002', description: 'Building corner', coverType: 'HARD_COVER', distanceFeet: 30, direction: 'west', effectiveness: 0.85 },
  ],
  escapeRoutes: [
    { id: 'er-001', description: 'Primary street - northbound', probability: 0.4, direction: 'north', vehicleAccessible: true, interceptPoints: ['Main St intersection', 'Highway on-ramp'] },
    { id: 'er-002', description: 'Alley - eastbound', probability: 0.3, direction: 'east', vehicleAccessible: false, interceptPoints: ['Alley exit at 2nd Ave'] },
  ],
  backupUnits: [
    { unitId: 'RBPD-201', unitType: 'Patrol', etaMinutes: 2.3, distanceMiles: 1.2, status: 'Responding' },
    { unitId: 'RBPD-205', unitType: 'Patrol', etaMinutes: 4.1, distanceMiles: 2.5, status: 'Responding' },
    { unitId: 'RBPD-K9', unitType: 'K9', etaMinutes: 8.5, distanceMiles: 5.0, status: 'Available' },
  ],
  communicationPlan: 'Standard radio protocol. Request TAC channel if situation escalates.',
  containmentStrategy: 'Standard scene containment. Control access points and maintain situational awareness.',
  lethalCoverRequired: false,
  k9Recommended: false,
  airSupportRecommended: false,
};

export default function TacticalAdvisorPanel() {
  const [advice, setAdvice] = useState<TacticalAdvice>(mockAdvice);
  const [selectedScenario, setSelectedScenario] = useState('TRAFFIC_STOP');
  const [activeSection, setActiveSection] = useState<string>('overview');

  const getThreatColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'text-green-400 bg-green-900/30';
      case 'MODERATE': return 'text-yellow-400 bg-yellow-900/30';
      case 'HIGH': return 'text-orange-400 bg-orange-900/30';
      case 'CRITICAL': return 'text-red-400 bg-red-900/30';
      default: return 'text-gray-400 bg-gray-900/30';
    }
  };

  const scenarios = [
    'TRAFFIC_STOP', 'FELONY_STOP', 'FOOT_PURSUIT', 'DOMESTIC_CALL',
    'SHOTS_FIRED', 'BURGLARY_IN_PROGRESS', 'ACTIVE_SHOOTER',
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
          >
            {scenarios.map((scenario) => (
              <option key={scenario} value={scenario}>
                {scenario.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getThreatColor(advice.threatLevel)}`}>
            Threat: {advice.threatLevel}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          {advice.lethalCoverRequired && (
            <span className="px-3 py-1 bg-red-900/50 text-red-300 rounded-full text-sm">
              Lethal Cover Required
            </span>
          )}
          {advice.k9Recommended && (
            <span className="px-3 py-1 bg-purple-900/50 text-purple-300 rounded-full text-sm">
              K9 Recommended
            </span>
          )}
          {advice.airSupportRecommended && (
            <span className="px-3 py-1 bg-blue-900/50 text-blue-300 rounded-full text-sm">
              Air Support Recommended
            </span>
          )}
        </div>
      </div>

      <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
        <h3 className="text-blue-300 font-semibold mb-2">Primary Recommendation</h3>
        <p className="text-white text-lg">{advice.primaryRecommendation}</p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-3">Tactical Notes</h3>
            <ul className="space-y-2">
              {advice.tacticalNotes.map((note, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-blue-400 mt-1">•</span>
                  <span className="text-gray-300">{note}</span>
                </li>
              ))}
            </ul>
          </div>

          {advice.warnings.length > 0 && (
            <div className="bg-red-900/20 rounded-lg border border-red-700 p-4">
              <h3 className="text-red-400 font-semibold mb-3">Warnings</h3>
              <ul className="space-y-2">
                {advice.warnings.map((warning, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-red-400 mt-1">⚠</span>
                    <span className="text-red-200">{warning}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-3">De-Escalation Options</h3>
            <ul className="space-y-2">
              {advice.deEscalationOptions.map((option, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-green-400 mt-1">→</span>
                  <span className="text-gray-300">{option}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-3">Cover Positions</h3>
              <div className="space-y-3">
                {advice.coverPositions.map((position) => (
                  <div key={position.id} className="p-3 bg-gray-700/50 rounded">
                    <div className="flex items-center justify-between">
                      <span className="text-white font-medium">{position.description}</span>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        position.coverType === 'HARD_COVER' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'
                      }`}>
                        {position.coverType.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <div className="text-sm text-gray-400 mt-1">
                      {position.distanceFeet} ft {position.direction} | {(position.effectiveness * 100).toFixed(0)}% effective
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-3">Escape Routes</h3>
              <div className="space-y-3">
                {advice.escapeRoutes.map((route) => (
                  <div key={route.id} className="p-3 bg-gray-700/50 rounded">
                    <div className="flex items-center justify-between">
                      <span className="text-white font-medium">{route.description}</span>
                      <span className="text-orange-400 text-sm">{(route.probability * 100).toFixed(0)}%</span>
                    </div>
                    <div className="text-sm text-gray-400 mt-1">
                      Direction: {route.direction} | {route.vehicleAccessible ? 'Vehicle' : 'Foot only'}
                    </div>
                    <div className="text-xs text-blue-300 mt-1">
                      Intercept: {route.interceptPoints.join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-3">Backup Units</h3>
            <div className="space-y-3">
              {advice.backupUnits.map((unit) => (
                <div key={unit.unitId} className="p-3 bg-gray-700/50 rounded">
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">{unit.unitId}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      unit.status === 'Responding' ? 'bg-green-900 text-green-300' : 'bg-blue-900 text-blue-300'
                    }`}>
                      {unit.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    {unit.unitType} | ETA: {unit.etaMinutes.toFixed(1)} min
                  </div>
                  <div className="text-xs text-gray-500">
                    {unit.distanceMiles.toFixed(1)} miles away
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-3">Communication Plan</h3>
            <p className="text-gray-300 text-sm">{advice.communicationPlan}</p>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-3">Containment Strategy</h3>
            <p className="text-gray-300 text-sm">{advice.containmentStrategy}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

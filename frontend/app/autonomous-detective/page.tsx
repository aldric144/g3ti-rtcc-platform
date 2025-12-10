'use client';

import React, { useState } from 'react';
import CrimeSceneReconstructionViewer from './components/CrimeSceneReconstructionViewer';
import OffenderBehaviorPanel from './components/OffenderBehaviorPanel';
import TheoryWorkbench from './components/TheoryWorkbench';
import EvidenceGraphExplorer from './components/EvidenceGraphExplorer';
import AutoInvestigatorConsole from './components/AutoInvestigatorConsole';
import CaseReportBuilder from './components/CaseReportBuilder';

type TabType = 'scene' | 'offender' | 'theory' | 'graph' | 'investigator' | 'reports';

export default function AutonomousDetectivePage() {
  const [activeTab, setActiveTab] = useState<TabType>('investigator');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'investigator', label: 'Auto Investigator', icon: '🔍' },
    { id: 'scene', label: 'Crime Scene', icon: '🏠' },
    { id: 'offender', label: 'Offender Profiling', icon: '👤' },
    { id: 'theory', label: 'Theory Workbench', icon: '💡' },
    { id: 'graph', label: 'Evidence Graph', icon: '🔗' },
    { id: 'reports', label: 'Reports', icon: '📄' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">
              Autonomous Detective AI (ADA)
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              AI-Powered Investigation Analysis & Case Management
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm text-gray-400">ADA Engine Active</span>
            </div>
            <select
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm"
              value={selectedCaseId || ''}
              onChange={(e) => setSelectedCaseId(e.target.value || null)}
            >
              <option value="">Select Case...</option>
              <option value="case-001">Case #2024-001 - Homicide</option>
              <option value="case-002">Case #2024-002 - Robbery</option>
              <option value="case-003">Case #2024-003 - Burglary Series</option>
            </select>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-400 bg-gray-700/50'
                  : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-700/30'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">
        {activeTab === 'investigator' && (
          <AutoInvestigatorConsole caseId={selectedCaseId} />
        )}
        {activeTab === 'scene' && (
          <CrimeSceneReconstructionViewer caseId={selectedCaseId} />
        )}
        {activeTab === 'offender' && (
          <OffenderBehaviorPanel caseId={selectedCaseId} />
        )}
        {activeTab === 'theory' && (
          <TheoryWorkbench caseId={selectedCaseId} />
        )}
        {activeTab === 'graph' && (
          <EvidenceGraphExplorer caseId={selectedCaseId} />
        )}
        {activeTab === 'reports' && (
          <CaseReportBuilder caseId={selectedCaseId} />
        )}
      </main>
    </div>
  );
}

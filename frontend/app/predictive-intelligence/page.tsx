'use client';

import { useState } from 'react';
import RiskTerrainViewer from './components/RiskTerrainViewer';
import PatrolOptimizationMap from './components/PatrolOptimizationMap';
import ViolenceClusterTimeline from './components/ViolenceClusterTimeline';
import ThreatProjectionGraphs from './components/ThreatProjectionGraphs';
import BiasAuditPanel from './components/BiasAuditPanel';

type TabType = 'terrain' | 'patrol' | 'clusters' | 'projections' | 'audit';

export default function PredictiveIntelligencePage() {
  const [activeTab, setActiveTab] = useState<TabType>('terrain');

  const tabs: { id: TabType; label: string }[] = [
    { id: 'terrain', label: 'Risk Terrain' },
    { id: 'patrol', label: 'Patrol Optimization' },
    { id: 'clusters', label: 'Violence Clusters' },
    { id: 'projections', label: 'Threat Projections' },
    { id: 'audit', label: 'Bias Audit' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-blue-400">
            Predictive Intelligence
          </h1>
          <p className="text-gray-400 mt-1">
            Ethical, Transparent, Non-Biased Crime Forecasting
          </p>
        </div>

        <div className="bg-yellow-900 bg-opacity-30 border border-yellow-600 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-yellow-500 mr-3 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h4 className="font-medium text-yellow-500">
                Ethical AI Notice
              </h4>
              <p className="text-sm text-gray-300 mt-1">
                All predictions are based on environmental and behavioral factors
                only. No racial, ethnic, or demographic identifiers are used.
                All models include bias safeguards and transparent audit logs.
              </p>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <div className="flex space-x-2 border-b border-gray-700">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          {activeTab === 'terrain' && <RiskTerrainViewer />}
          {activeTab === 'patrol' && <PatrolOptimizationMap />}
          {activeTab === 'clusters' && <ViolenceClusterTimeline />}
          {activeTab === 'projections' && <ThreatProjectionGraphs />}
          {activeTab === 'audit' && <BiasAuditPanel />}
        </div>
      </div>
    </div>
  );
}

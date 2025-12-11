'use client';

import React, { useState, useEffect } from 'react';
import ConstitutionalGuardrailPanel from './components/ConstitutionalGuardrailPanel';
import TacticalAdvisorPanel from './components/TacticalAdvisorPanel';
import OfficerRiskMonitor from './components/OfficerRiskMonitor';
import UseOfForceHeatMeter from './components/UseOfForceHeatMeter';
import SupervisorDashboard from './components/SupervisorDashboard';

type TabType = 'guardrails' | 'tactical' | 'risk' | 'force' | 'supervisor';

interface TabConfig {
  id: TabType;
  label: string;
  description: string;
}

const tabs: TabConfig[] = [
  { id: 'guardrails', label: 'Constitutional Guardrails', description: 'Real-time constitutional and policy compliance' },
  { id: 'tactical', label: 'Tactical Advisor', description: 'Live tactical guidance and recommendations' },
  { id: 'risk', label: 'Officer Risk Monitor', description: 'Fatigue, stress, and safety monitoring' },
  { id: 'force', label: 'Use of Force', description: 'Force risk assessment and monitoring' },
  { id: 'supervisor', label: 'Supervisor Dashboard', description: 'Command oversight and alerts' },
];

export default function OfficerAssistPage() {
  const [activeTab, setActiveTab] = useState<TabType>('guardrails');
  const [isConnected, setIsConnected] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
      setAlertCount(prev => Math.max(0, prev + Math.floor(Math.random() * 3) - 1));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'guardrails':
        return <ConstitutionalGuardrailPanel />;
      case 'tactical':
        return <TacticalAdvisorPanel />;
      case 'risk':
        return <OfficerRiskMonitor />;
      case 'force':
        return <UseOfForceHeatMeter />;
      case 'supervisor':
        return <SupervisorDashboard />;
      default:
        return <ConstitutionalGuardrailPanel />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">AI Officer Assist Suite</h1>
            <p className="text-gray-400 text-sm mt-1">
              Real-Time Constitutional Guardrails & Tactical Support
            </p>
          </div>
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-400">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            {alertCount > 0 && (
              <div className="flex items-center space-x-2 bg-red-900/50 px-3 py-1 rounded-full">
                <span className="text-red-400 font-semibold">{alertCount}</span>
                <span className="text-red-300 text-sm">Active Alerts</span>
              </div>
            )}
            <div className="text-sm text-gray-500">
              Last update: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </header>

      <div className="border-b border-gray-700 bg-gray-800/50">
        <nav className="flex space-x-1 px-6 py-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
              title={tab.description}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <main className="p-6">
        <div className="mb-4">
          <p className="text-gray-400 text-sm">
            {tabs.find(t => t.id === activeTab)?.description}
          </p>
        </div>
        {renderTabContent()}
      </main>

      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div>
            Riviera Beach Police Department | Agency ORI: FL0500400
          </div>
          <div>
            Phase 28: AI Officer Assist Suite | G3TI RTCC-UIP
          </div>
        </div>
      </footer>
    </div>
  );
}

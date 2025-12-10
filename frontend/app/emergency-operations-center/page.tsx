'use client';

import React, { useState } from 'react';
import CrisisMap from './components/CrisisMap';
import EvacuationRoutePanel from './components/EvacuationRoutePanel';
import ShelterCapacityBoard from './components/ShelterCapacityBoard';
import LogisticsCommandPanel from './components/LogisticsCommandPanel';
import MedicalSurgeForecastPanel from './components/MedicalSurgeForecastPanel';
import MultiIncidentCommandRoom from './components/MultiIncidentCommandRoom';
import DamageAssessmentViewer from './components/DamageAssessmentViewer';

type TabType = 'crisis' | 'evacuation' | 'shelters' | 'logistics' | 'medical' | 'command' | 'damage';

export default function EmergencyOperationsCenter() {
  const [activeTab, setActiveTab] = useState<TabType>('crisis');

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'crisis', label: 'Crisis Map', icon: '🗺️' },
    { id: 'evacuation', label: 'Evacuation', icon: '🚗' },
    { id: 'shelters', label: 'Shelters', icon: '🏠' },
    { id: 'logistics', label: 'Logistics', icon: '📦' },
    { id: 'medical', label: 'Medical', icon: '🏥' },
    { id: 'command', label: 'Command', icon: '🎖️' },
    { id: 'damage', label: 'Damage', icon: '🏚️' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'crisis':
        return <CrisisMap />;
      case 'evacuation':
        return <EvacuationRoutePanel />;
      case 'shelters':
        return <ShelterCapacityBoard />;
      case 'logistics':
        return <LogisticsCommandPanel />;
      case 'medical':
        return <MedicalSurgeForecastPanel />;
      case 'command':
        return <MultiIncidentCommandRoom />;
      case 'damage':
        return <DamageAssessmentViewer />;
      default:
        return <CrisisMap />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <span className="text-3xl">🚨</span>
              Emergency Operations Center
            </h1>
            <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm font-medium animate-pulse">
              LIVE
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-gray-400 text-sm">
              {new Date().toLocaleString()}
            </div>
            <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-medium">
              Declare Emergency
            </button>
          </div>
        </div>
      </header>

      <nav className="bg-gray-900 border-b border-gray-800 px-6">
        <div className="flex items-center gap-1 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 flex items-center gap-2 text-sm font-medium whitespace-nowrap transition-colors border-b-2 ${
                activeTab === tab.id
                  ? 'text-blue-400 border-blue-400 bg-gray-800/50'
                  : 'text-gray-400 border-transparent hover:text-white hover:bg-gray-800/30'
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6 h-[calc(100vh-140px)]">
        {renderContent()}
      </main>

      <footer className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 px-6 py-2">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-gray-400">System Status: Operational</span>
            </div>
            <div className="text-gray-500">|</div>
            <div className="text-gray-400">
              WebSocket: <span className="text-green-400">Connected</span>
            </div>
          </div>
          <div className="text-gray-500">
            G3TI RTCC-UIP • Phase 21 • Emergency Management Engine
          </div>
        </div>
      </footer>
    </div>
  );
}

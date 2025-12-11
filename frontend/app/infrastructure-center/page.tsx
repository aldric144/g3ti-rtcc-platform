'use client';

import { useState } from 'react';
import SystemMap from './components/SystemMap';
import HighAvailabilityDashboard from './components/HighAvailabilityDashboard';
import ZeroTrustConsole from './components/ZeroTrustConsole';
import CJISComplianceConsole from './components/CJISComplianceConsole';
import InfrastructureTimeline from './components/InfrastructureTimeline';

type TabType = 'system-map' | 'ha-dashboard' | 'zero-trust' | 'cjis-compliance' | 'timeline';

export default function InfrastructureCenterPage() {
  const [activeTab, setActiveTab] = useState<TabType>('system-map');

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'system-map', label: 'System Map', icon: '🗺️' },
    { id: 'ha-dashboard', label: 'High Availability', icon: '🔄' },
    { id: 'zero-trust', label: 'Zero Trust Access', icon: '🔐' },
    { id: 'cjis-compliance', label: 'CJIS Compliance', icon: '📋' },
    { id: 'timeline', label: 'Infrastructure Timeline', icon: '📊' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'system-map':
        return <SystemMap />;
      case 'ha-dashboard':
        return <HighAvailabilityDashboard />;
      case 'zero-trust':
        return <ZeroTrustConsole />;
      case 'cjis-compliance':
        return <CJISComplianceConsole />;
      case 'timeline':
        return <InfrastructureTimeline />;
      default:
        return <SystemMap />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Infrastructure Center</h1>
            <p className="text-gray-400 text-sm">
              G3TI RTCC-UIP Enterprise Deployment Management - Riviera Beach, FL
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm text-gray-300">All Systems Operational</span>
            </div>
            <div className="text-sm text-gray-400">
              {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="flex space-x-1 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">
        {renderTabContent()}
      </main>

      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div>
            Phase 27: Enterprise Deployment Infrastructure | CJIS Compliant | Zero-Trust Enabled
          </div>
          <div className="flex items-center space-x-4">
            <span>Primary Region: AWS GovCloud East</span>
            <span>|</span>
            <span>Failover Ready</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

'use client';

import { useState } from 'react';
import TenantManager from './components/TenantManager';
import SharedIntelHub from './components/SharedIntelHub';
import JointOpsRoom from './components/JointOpsRoom';
import RegionalAnalytics from './components/RegionalAnalytics';
import InterAgencyAlerts from './components/InterAgencyAlerts';

type TabType = 'tenants' | 'intel' | 'jointops' | 'analytics' | 'alerts';

export default function FusionCloudPage() {
  const [activeTab, setActiveTab] = useState<TabType>('tenants');

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'tenants', label: 'Tenant Manager', icon: '🏛️' },
    { id: 'intel', label: 'Shared Intelligence', icon: '📡' },
    { id: 'jointops', label: 'Joint Operations', icon: '🎯' },
    { id: 'analytics', label: 'Regional Analytics', icon: '📊' },
    { id: 'alerts', label: 'Inter-Agency Alerts', icon: '🚨' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">G3TI Fusion Cloud</h1>
            <p className="text-gray-400 text-sm">Multi-City / Multi-Agency Intelligence Platform</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm text-gray-400">Connected</span>
            </div>
            <div className="text-sm text-gray-400">
              {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="flex space-x-1 px-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-700/50'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/30'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">
        {activeTab === 'tenants' && <TenantManager />}
        {activeTab === 'intel' && <SharedIntelHub />}
        {activeTab === 'jointops' && <JointOpsRoom />}
        {activeTab === 'analytics' && <RegionalAnalytics />}
        {activeTab === 'alerts' && <InterAgencyAlerts />}
      </main>
    </div>
  );
}

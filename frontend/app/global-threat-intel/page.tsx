'use client';

import { useState } from 'react';
import DarkWebSignalsPanel from './components/DarkWebSignalsPanel';
import OSINTTrendsPanel from './components/OSINTTrendsPanel';
import ExtremistNetworksGraph from './components/ExtremistNetworksGraph';
import GlobalIncidentMap from './components/GlobalIncidentMap';
import ThreatScoreboard from './components/ThreatScoreboard';
import FusionTimeline from './components/FusionTimeline';

type TabType = 'overview' | 'dark-web' | 'osint' | 'extremist' | 'incidents' | 'scoring';

export default function GlobalThreatIntelPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const tabs: { id: TabType; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'dark-web', label: 'Dark Web' },
    { id: 'osint', label: 'OSINT' },
    { id: 'extremist', label: 'Extremist Networks' },
    { id: 'incidents', label: 'Global Incidents' },
    { id: 'scoring', label: 'Threat Scoring' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-red-500">
              Global Threat Intelligence Engine
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Phase 17: National-level intelligence capabilities for RTCC
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm text-gray-300">Live Feed Active</span>
            </div>
            <button className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-sm font-medium">
              Emergency Alert
            </button>
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
                  ? 'text-red-500 border-b-2 border-red-500 bg-gray-700/50'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/30'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ThreatScoreboard />
              <FusionTimeline />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <DarkWebSignalsPanel compact />
              <OSINTTrendsPanel compact />
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 className="text-lg font-semibold mb-4 text-orange-400">
                  Active Alerts
                </h3>
                <div className="space-y-3">
                  <AlertItem
                    priority="critical"
                    title="Dark Web Weapons Listing"
                    time="2 min ago"
                  />
                  <AlertItem
                    priority="high"
                    title="OSINT: Protest Planned"
                    time="15 min ago"
                  />
                  <AlertItem
                    priority="moderate"
                    title="Extremist Network Activity"
                    time="1 hr ago"
                  />
                </div>
              </div>
            </div>
            <GlobalIncidentMap compact />
          </div>
        )}

        {activeTab === 'dark-web' && <DarkWebSignalsPanel />}
        {activeTab === 'osint' && <OSINTTrendsPanel />}
        {activeTab === 'extremist' && <ExtremistNetworksGraph />}
        {activeTab === 'incidents' && <GlobalIncidentMap />}
        {activeTab === 'scoring' && (
          <div className="space-y-6">
            <ThreatScoreboard expanded />
            <FusionTimeline expanded />
          </div>
        )}
      </main>
    </div>
  );
}

function AlertItem({
  priority,
  title,
  time,
}: {
  priority: 'critical' | 'high' | 'moderate' | 'low';
  title: string;
  time: string;
}) {
  const priorityColors = {
    critical: 'bg-red-500/20 border-red-500 text-red-400',
    high: 'bg-orange-500/20 border-orange-500 text-orange-400',
    moderate: 'bg-yellow-500/20 border-yellow-500 text-yellow-400',
    low: 'bg-blue-500/20 border-blue-500 text-blue-400',
  };

  return (
    <div
      className={`p-3 rounded border-l-4 ${priorityColors[priority]} bg-gray-700/50`}
    >
      <div className="flex justify-between items-start">
        <span className="font-medium text-sm">{title}</span>
        <span className="text-xs text-gray-400">{time}</span>
      </div>
      <span className="text-xs uppercase mt-1 inline-block">{priority}</span>
    </div>
  );
}

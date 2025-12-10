'use client';

import { useState } from 'react';
import FleetStatusGrid from './components/FleetStatusGrid';
import TelemetryPanel from './components/TelemetryPanel';
import MissionQueue from './components/MissionQueue';
import LiveDroneVideo from './components/LiveDroneVideo';
import DroneRouteMap from './components/DroneRouteMap';

type TabType = 'fleet' | 'telemetry' | 'missions' | 'video' | 'map';

export default function DroneOperationsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('fleet');

  const tabs: { id: TabType; label: string }[] = [
    { id: 'fleet', label: 'Fleet Status' },
    { id: 'telemetry', label: 'Telemetry' },
    { id: 'missions', label: 'Missions' },
    { id: 'video', label: 'Live Video' },
    { id: 'map', label: 'Route Map' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-blue-400">Drone Operations</h1>
          <p className="text-gray-400 mt-1">
            Autonomous Drone Task Force Management
          </p>
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
          {activeTab === 'fleet' && <FleetStatusGrid />}
          {activeTab === 'telemetry' && <TelemetryPanel />}
          {activeTab === 'missions' && <MissionQueue />}
          {activeTab === 'video' && <LiveDroneVideo />}
          {activeTab === 'map' && <DroneRouteMap />}
        </div>
      </div>
    </div>
  );
}

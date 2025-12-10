'use client';

import { useState, useEffect } from 'react';

interface BuildingInspectorProps {
  buildingId: string;
  onClose: () => void;
}

interface Building {
  building_id: string;
  name: string;
  address: string;
  building_type: string;
  risk_level: string;
  floor_count: number;
  occupancy_capacity: number;
  current_occupancy: number;
  has_interior_mapping: boolean;
  emergency_contact: string;
  last_inspection: string;
}

export default function BuildingInspector({
  buildingId,
  onClose,
}: BuildingInspectorProps) {
  const [building, setBuilding] = useState<Building | null>(null);
  const [activeTab, setActiveTab] = useState<'info' | 'floors' | 'alerts'>('info');

  useEffect(() => {
    const mockBuilding: Building = {
      building_id: buildingId,
      name: 'City Hall',
      address: '55 Trinity Ave SW, Atlanta, GA 30303',
      building_type: 'GOVERNMENT',
      risk_level: 'HIGH',
      floor_count: 8,
      occupancy_capacity: 2000,
      current_occupancy: 450,
      has_interior_mapping: true,
      emergency_contact: '404-555-0100',
      last_inspection: '2024-11-15',
    };
    setBuilding(mockBuilding);
  }, [buildingId]);

  if (!building) {
    return null;
  }

  const riskColors: Record<string, string> = {
    LOW: 'text-green-400',
    MEDIUM: 'text-yellow-400',
    HIGH: 'text-orange-400',
    CRITICAL: 'text-red-400',
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Building Inspector</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex space-x-2 mb-4">
        {(['info', 'floors', 'alerts'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === tab ? 'bg-blue-600' : 'bg-gray-700'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'info' && (
        <div className="space-y-3">
          <div>
            <div className="text-lg font-medium">{building.name}</div>
            <div className="text-sm text-gray-400">{building.address}</div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-400">Type</span>
              <div>{building.building_type}</div>
            </div>
            <div>
              <span className="text-gray-400">Risk Level</span>
              <div className={riskColors[building.risk_level]}>
                {building.risk_level}
              </div>
            </div>
            <div>
              <span className="text-gray-400">Floors</span>
              <div>{building.floor_count}</div>
            </div>
            <div>
              <span className="text-gray-400">Occupancy</span>
              <div>
                {building.current_occupancy} / {building.occupancy_capacity}
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-gray-700">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Interior Mapping</span>
              <span className={building.has_interior_mapping ? 'text-green-400' : 'text-gray-500'}>
                {building.has_interior_mapping ? 'Available' : 'Not Available'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm mt-2">
              <span className="text-gray-400">Emergency Contact</span>
              <span>{building.emergency_contact}</span>
            </div>
            <div className="flex items-center justify-between text-sm mt-2">
              <span className="text-gray-400">Last Inspection</span>
              <span>{building.last_inspection}</span>
            </div>
          </div>

          {building.has_interior_mapping && (
            <button className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded text-sm mt-4">
              View Interior Map
            </button>
          )}
        </div>
      )}

      {activeTab === 'floors' && (
        <div className="space-y-2">
          {Array.from({ length: building.floor_count }, (_, i) => (
            <div
              key={i}
              className="flex items-center justify-between bg-gray-700 p-3 rounded"
            >
              <div>
                <div className="font-medium">Floor {i + 1}</div>
                <div className="text-xs text-gray-400">
                  {Math.floor(Math.random() * 50) + 10} occupants
                </div>
              </div>
              <button className="text-blue-400 text-sm hover:text-blue-300">
                View
              </button>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="space-y-2">
          <div className="bg-yellow-900 bg-opacity-50 p-3 rounded">
            <div className="flex items-center">
              <svg className="w-4 h-4 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-yellow-400 text-sm font-medium">
                Fire Alarm Test Scheduled
              </span>
            </div>
            <div className="text-xs text-gray-400 mt-1">
              Tomorrow at 10:00 AM
            </div>
          </div>

          <div className="bg-gray-700 p-3 rounded">
            <div className="flex items-center">
              <svg className="w-4 h-4 text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="text-sm">Elevator Maintenance</span>
            </div>
            <div className="text-xs text-gray-400 mt-1">
              Elevator B - Completed 2 days ago
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

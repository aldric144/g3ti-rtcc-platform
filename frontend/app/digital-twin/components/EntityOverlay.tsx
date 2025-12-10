'use client';

import { useState, useEffect } from 'react';

interface EntityOverlayProps {
  isLive: boolean;
}

interface EntityCount {
  officers: number;
  vehicles: number;
  drones: number;
  incidents: number;
  sensors: number;
}

export default function EntityOverlay({ isLive }: EntityOverlayProps) {
  const [counts, setCounts] = useState<EntityCount>({
    officers: 0,
    vehicles: 0,
    drones: 0,
    incidents: 0,
    sensors: 0,
  });

  useEffect(() => {
    setCounts({
      officers: 24,
      vehicles: 18,
      drones: 4,
      incidents: 7,
      sensors: 156,
    });

    if (isLive) {
      const interval = setInterval(() => {
        setCounts((prev) => ({
          ...prev,
          incidents: prev.incidents + (Math.random() > 0.8 ? 1 : 0),
        }));
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isLive]);

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Active Entities</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
            <span className="text-gray-300">Officers</span>
          </div>
          <span className="font-bold text-blue-400">{counts.officers}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
            <span className="text-gray-300">Vehicles</span>
          </div>
          <span className="font-bold text-green-400">{counts.vehicles}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
            <span className="text-gray-300">Drones</span>
          </div>
          <span className="font-bold text-purple-400">{counts.drones}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
            <span className="text-gray-300">Active Incidents</span>
          </div>
          <span className="font-bold text-red-400">{counts.incidents}</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>
            <span className="text-gray-300">Sensors Online</span>
          </div>
          <span className="font-bold text-yellow-400">{counts.sensors}</span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="text-sm text-gray-400 mb-2">Weather Overlay</div>
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Current</span>
          <span className="flex items-center">
            <svg className="w-5 h-5 mr-1 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
            72°F Clear
          </span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="text-sm text-gray-400 mb-2">Traffic Conditions</div>
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Overall</span>
          <span className="text-yellow-400">Moderate</span>
        </div>
        <div className="flex items-center justify-between mt-1">
          <span className="text-gray-300">Congested Roads</span>
          <span className="text-red-400">3</span>
        </div>
      </div>
    </div>
  );
}

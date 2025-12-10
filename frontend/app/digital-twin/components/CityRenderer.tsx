'use client';

import { useState, useEffect } from 'react';

interface CityRendererProps {
  activeLayers: string[];
  onBuildingSelect: (buildingId: string | null) => void;
  playbackTime: Date;
  isLive: boolean;
}

interface Entity {
  id: string;
  type: 'officer' | 'vehicle' | 'drone' | 'incident';
  latitude: number;
  longitude: number;
  label: string;
}

export default function CityRenderer({
  activeLayers,
  onBuildingSelect,
  playbackTime,
  isLive,
}: CityRendererProps) {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');

  useEffect(() => {
    const mockEntities: Entity[] = [
      { id: 'off-1', type: 'officer', latitude: 33.749, longitude: -84.388, label: 'Unit 12' },
      { id: 'off-2', type: 'officer', latitude: 33.751, longitude: -84.390, label: 'Unit 15' },
      { id: 'veh-1', type: 'vehicle', latitude: 33.748, longitude: -84.385, label: 'Patrol 7' },
      { id: 'drone-1', type: 'drone', latitude: 33.750, longitude: -84.387, label: 'EAGLE-1' },
      { id: 'inc-1', type: 'incident', latitude: 33.747, longitude: -84.389, label: 'Traffic Stop' },
    ];
    setEntities(mockEntities);
  }, [isLive, playbackTime]);

  const entityColors: Record<string, string> = {
    officer: 'bg-blue-500',
    vehicle: 'bg-green-500',
    drone: 'bg-purple-500',
    incident: 'bg-red-500',
  };

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex space-x-2">
          <button
            onClick={() => setViewMode('3d')}
            className={`px-3 py-1 rounded ${
              viewMode === '3d' ? 'bg-blue-600' : 'bg-gray-700'
            }`}
          >
            3D View
          </button>
          <button
            onClick={() => setViewMode('2d')}
            className={`px-3 py-1 rounded ${
              viewMode === '2d' ? 'bg-blue-600' : 'bg-gray-700'
            }`}
          >
            2D View
          </button>
        </div>
        <div className="text-sm text-gray-400">
          {isLive ? (
            <span className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Live Feed
            </span>
          ) : (
            <span>Replay: {playbackTime.toLocaleTimeString()}</span>
          )}
        </div>
      </div>

      <div className="aspect-video relative bg-gray-900 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-500">
            <svg
              className="w-20 h-20 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
              />
            </svg>
            <p className="text-lg">3D City Digital Twin</p>
            <p className="text-sm mt-2">
              Three.js / Cesium.js integration would render here
            </p>
            <p className="text-xs mt-4 text-gray-600">
              Click on buildings to inspect | Drag to rotate | Scroll to zoom
            </p>
          </div>
        </div>

        {activeLayers.includes('officers') &&
          entities
            .filter((e) => e.type === 'officer')
            .map((entity) => (
              <div
                key={entity.id}
                className="absolute w-6 h-6 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={{
                  left: `${30 + Math.random() * 40}%`,
                  top: `${30 + Math.random() * 40}%`,
                }}
                title={entity.label}
              >
                <div className={`w-6 h-6 rounded-full ${entityColors.officer} flex items-center justify-center`}>
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            ))}

        {activeLayers.includes('vehicles') &&
          entities
            .filter((e) => e.type === 'vehicle')
            .map((entity) => (
              <div
                key={entity.id}
                className="absolute w-6 h-6 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={{
                  left: `${30 + Math.random() * 40}%`,
                  top: `${30 + Math.random() * 40}%`,
                }}
                title={entity.label}
              >
                <div className={`w-6 h-6 rounded-full ${entityColors.vehicle} flex items-center justify-center`}>
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
                    <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z" />
                  </svg>
                </div>
              </div>
            ))}

        {activeLayers.includes('drones') &&
          entities
            .filter((e) => e.type === 'drone')
            .map((entity) => (
              <div
                key={entity.id}
                className="absolute w-6 h-6 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={{
                  left: `${30 + Math.random() * 40}%`,
                  top: `${30 + Math.random() * 40}%`,
                }}
                title={entity.label}
              >
                <div className={`w-6 h-6 rounded-full ${entityColors.drone} flex items-center justify-center`}>
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 2L4 12h5v6h2v-6h5L10 2z" />
                  </svg>
                </div>
              </div>
            ))}

        {activeLayers.includes('incidents') &&
          entities
            .filter((e) => e.type === 'incident')
            .map((entity) => (
              <div
                key={entity.id}
                className="absolute w-6 h-6 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={{
                  left: `${30 + Math.random() * 40}%`,
                  top: `${30 + Math.random() * 40}%`,
                }}
                title={entity.label}
              >
                <div className={`w-6 h-6 rounded-full ${entityColors.incident} flex items-center justify-center animate-pulse`}>
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            ))}

        <div className="absolute bottom-4 left-4 bg-gray-800 bg-opacity-90 rounded-lg p-3">
          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
              <span>Officers</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
              <span>Vehicles</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-purple-500 mr-1"></div>
              <span>Drones</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-red-500 mr-1"></div>
              <span>Incidents</span>
            </div>
          </div>
        </div>

        <div className="absolute bottom-4 right-4 flex flex-col space-y-2">
          <button className="bg-gray-800 hover:bg-gray-700 p-2 rounded">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
          <button className="bg-gray-800 hover:bg-gray-700 p-2 rounded">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            </svg>
          </button>
          <button className="bg-gray-800 hover:bg-gray-700 p-2 rounded">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

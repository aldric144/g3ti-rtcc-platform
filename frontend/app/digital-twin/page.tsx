'use client';

import { useState } from 'react';
import CityRenderer from './components/CityRenderer';
import EntityOverlay from './components/EntityOverlay';
import TimeTravelScrubber from './components/TimeTravelScrubber';
import BuildingInspector from './components/BuildingInspector';
import LayerControls from './components/LayerControls';

export default function DigitalTwinPage() {
  const [selectedBuilding, setSelectedBuilding] = useState<string | null>(null);
  const [playbackTime, setPlaybackTime] = useState<Date>(new Date());
  const [isLive, setIsLive] = useState(true);
  const [activeLayers, setActiveLayers] = useState<string[]>([
    'buildings',
    'roads',
    'officers',
    'vehicles',
    'drones',
    'incidents',
  ]);

  const toggleLayer = (layer: string) => {
    setActiveLayers((prev) =>
      prev.includes(layer) ? prev.filter((l) => l !== layer) : [...prev, layer]
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-blue-400">City Digital Twin</h1>
            <p className="text-gray-400 mt-1">
              3D Real-Time Environment Visualization
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsLive(!isLive)}
              className={`px-4 py-2 rounded-lg font-medium ${
                isLive
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              {isLive ? 'LIVE' : 'REPLAY'}
            </button>
            <span className="text-gray-400">
              {playbackTime.toLocaleString()}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <CityRenderer
              activeLayers={activeLayers}
              onBuildingSelect={setSelectedBuilding}
              playbackTime={playbackTime}
              isLive={isLive}
            />

            <div className="mt-4">
              <TimeTravelScrubber
                currentTime={playbackTime}
                onTimeChange={setPlaybackTime}
                isLive={isLive}
                onLiveToggle={() => setIsLive(!isLive)}
              />
            </div>
          </div>

          <div className="space-y-4">
            <LayerControls
              activeLayers={activeLayers}
              onToggleLayer={toggleLayer}
            />

            <EntityOverlay isLive={isLive} />

            {selectedBuilding && (
              <BuildingInspector
                buildingId={selectedBuilding}
                onClose={() => setSelectedBuilding(null)}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

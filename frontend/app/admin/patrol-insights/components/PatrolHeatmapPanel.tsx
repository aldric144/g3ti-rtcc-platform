'use client';

import { useState, useEffect } from 'react';
import { Map, Layers, ZoomIn, ZoomOut } from 'lucide-react';

interface PatrolHeatmapPanelProps {
  refreshKey: number;
}

export function PatrolHeatmapPanel({ refreshKey }: PatrolHeatmapPanelProps) {
  const [selectedLayer, setSelectedLayer] = useState<'intensity' | 'zones' | 'both'>('both');

  // Riviera Beach sectors for visualization
  const sectors = [
    { id: 'sector_1', name: 'Downtown/Marina', intensity: 0.75, status: 'balanced' },
    { id: 'sector_2', name: 'Singer Island', intensity: 0.45, status: 'under_policed' },
    { id: 'sector_3', name: 'Blue Heron Corridor', intensity: 0.85, status: 'over_policed' },
    { id: 'sector_4', name: 'Industrial District', intensity: 0.30, status: 'under_policed' },
    { id: 'sector_5', name: 'Residential North', intensity: 0.55, status: 'balanced' },
    { id: 'sector_6', name: 'Residential South', intensity: 0.60, status: 'balanced' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'over_policed':
        return 'bg-red-500';
      case 'under_policed':
        return 'bg-amber-500';
      case 'balanced':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="border-b border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
            <Map className="h-5 w-5" />
            Patrol Heatmap
          </h2>
          <div className="flex items-center gap-2">
            <select
              value={selectedLayer}
              onChange={(e) => setSelectedLayer(e.target.value as typeof selectedLayer)}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
            >
              <option value="intensity">Intensity Only</option>
              <option value="zones">Zones Only</option>
              <option value="both">Both Layers</option>
            </select>
          </div>
        </div>
      </div>

      {/* Map Placeholder */}
      <div className="relative h-96 bg-gray-100 dark:bg-gray-900">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <Map className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Patrol Heatmap - Riviera Beach, FL
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500">
              (Mapbox integration available)
            </p>
          </div>
        </div>

        {/* Zoom Controls */}
        <div className="absolute right-4 top-4 flex flex-col gap-1">
          <button className="rounded-lg bg-white p-2 shadow-md hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700">
            <ZoomIn className="h-4 w-4" />
          </button>
          <button className="rounded-lg bg-white p-2 shadow-md hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700">
            <ZoomOut className="h-4 w-4" />
          </button>
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 rounded-lg bg-white p-3 shadow-md dark:bg-gray-800">
          <p className="mb-2 text-xs font-medium text-gray-700 dark:text-gray-300">Patrol Intensity</p>
          <div className="flex items-center gap-1">
            <div className="h-3 w-6 rounded-l bg-green-300" />
            <div className="h-3 w-6 bg-yellow-300" />
            <div className="h-3 w-6 bg-orange-300" />
            <div className="h-3 w-6 rounded-r bg-red-300" />
          </div>
          <div className="mt-1 flex justify-between text-xs text-gray-500">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>
      </div>

      {/* Sector List */}
      <div className="border-t border-gray-200 p-4 dark:border-gray-700">
        <h3 className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-300">
          Sector Coverage
        </h3>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {sectors.map((sector) => (
            <div
              key={sector.id}
              className="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 p-2 dark:border-gray-700 dark:bg-gray-700/50"
            >
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {sector.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {Math.round(sector.intensity * 100)}% coverage
                </p>
              </div>
              <div className={`h-3 w-3 rounded-full ${getStatusColor(sector.status)}`} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

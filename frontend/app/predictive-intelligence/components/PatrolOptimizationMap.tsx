'use client';

import { useState, useEffect } from 'react';

interface PatrolRoute {
  route_id: string;
  unit_id: string;
  zones: string[];
  priority_score: number;
  estimated_coverage: number;
  distance_km: number;
  duration_minutes: number;
  optimized: boolean;
}

interface PatrolUnit {
  unit_id: string;
  call_sign: string;
  current_zone: string;
  status: string;
  assigned_route: string | null;
}

export default function PatrolOptimizationMap() {
  const [routes, setRoutes] = useState<PatrolRoute[]>([]);
  const [units, setUnits] = useState<PatrolUnit[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<PatrolRoute | null>(null);
  const [optimizationMode, setOptimizationMode] = useState<'coverage' | 'response' | 'balanced'>('balanced');

  useEffect(() => {
    const mockRoutes: PatrolRoute[] = [
      {
        route_id: 'route-001',
        unit_id: 'unit-12',
        zones: ['Downtown Core', 'Midtown', 'Buckhead'],
        priority_score: 85,
        estimated_coverage: 78,
        distance_km: 24.5,
        duration_minutes: 120,
        optimized: true,
      },
      {
        route_id: 'route-002',
        unit_id: 'unit-15',
        zones: ['Westside Industrial', 'Airport Corridor'],
        priority_score: 92,
        estimated_coverage: 65,
        distance_km: 18.2,
        duration_minutes: 90,
        optimized: true,
      },
      {
        route_id: 'route-003',
        unit_id: 'unit-08',
        zones: ['Buckhead', 'Midtown'],
        priority_score: 68,
        estimated_coverage: 82,
        distance_km: 15.8,
        duration_minutes: 75,
        optimized: false,
      },
    ];

    const mockUnits: PatrolUnit[] = [
      { unit_id: 'unit-12', call_sign: 'Alpha-12', current_zone: 'Downtown Core', status: 'ON_PATROL', assigned_route: 'route-001' },
      { unit_id: 'unit-15', call_sign: 'Bravo-15', current_zone: 'Airport Corridor', status: 'ON_PATROL', assigned_route: 'route-002' },
      { unit_id: 'unit-08', call_sign: 'Charlie-08', current_zone: 'Buckhead', status: 'AVAILABLE', assigned_route: null },
      { unit_id: 'unit-22', call_sign: 'Delta-22', current_zone: 'Midtown', status: 'ON_CALL', assigned_route: null },
    ];

    setRoutes(mockRoutes);
    setUnits(mockUnits);
  }, [optimizationMode]);

  const statusColors: Record<string, string> = {
    ON_PATROL: 'bg-green-500',
    AVAILABLE: 'bg-blue-500',
    ON_CALL: 'bg-yellow-500',
    OFF_DUTY: 'bg-gray-500',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Patrol Route Optimization</h2>
        <div className="flex items-center space-x-4">
          <span className="text-gray-400 text-sm">Optimize for:</span>
          <div className="flex space-x-2">
            {(['coverage', 'response', 'balanced'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setOptimizationMode(mode)}
                className={`px-3 py-1 rounded capitalize ${
                  optimizationMode === mode ? 'bg-blue-600' : 'bg-gray-700'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-gray-700 rounded-lg aspect-video flex items-center justify-center relative">
            <div className="text-center text-gray-500">
              <svg
                className="w-16 h-16 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                />
              </svg>
              <p>Optimized Patrol Routes</p>
              <p className="text-sm mt-2">
                Route visualization would render here
              </p>
            </div>

            <div className="absolute top-4 right-4 bg-gray-800 bg-opacity-90 rounded-lg p-3">
              <div className="text-xs font-medium mb-2">Route Legend</div>
              <div className="space-y-1 text-xs">
                <div className="flex items-center">
                  <div className="w-8 h-1 bg-blue-500 mr-2"></div>
                  <span>Active Route</span>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-1 bg-green-500 mr-2"></div>
                  <span>Optimized</span>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-1 bg-yellow-500 mr-2"></div>
                  <span>Suggested</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-4 gap-4">
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-blue-400">{units.length}</div>
              <div className="text-gray-400 text-sm">Total Units</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-400">
                {units.filter((u) => u.status === 'ON_PATROL').length}
              </div>
              <div className="text-gray-400 text-sm">On Patrol</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-yellow-400">
                {routes.filter((r) => r.optimized).length}
              </div>
              <div className="text-gray-400 text-sm">Optimized Routes</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-purple-400">
                {Math.round(routes.reduce((acc, r) => acc + r.estimated_coverage, 0) / routes.length)}%
              </div>
              <div className="text-gray-400 text-sm">Avg Coverage</div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4">Patrol Units</h3>
          <div className="space-y-2 mb-6">
            {units.map((unit) => (
              <div
                key={unit.unit_id}
                className="bg-gray-700 p-3 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium">{unit.call_sign}</div>
                  <span
                    className={`px-2 py-0.5 rounded text-xs ${statusColors[unit.status]}`}
                  >
                    {unit.status.replace('_', ' ')}
                  </span>
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  Zone: {unit.current_zone}
                </div>
              </div>
            ))}
          </div>

          <h3 className="text-lg font-semibold mb-4">Active Routes</h3>
          <div className="space-y-2">
            {routes.map((route) => (
              <button
                key={route.route_id}
                onClick={() => setSelectedRoute(route)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedRoute?.route_id === route.route_id
                    ? 'bg-blue-600'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium">
                    {units.find((u) => u.unit_id === route.unit_id)?.call_sign}
                  </div>
                  {route.optimized && (
                    <span className="text-green-400 text-xs">Optimized</span>
                  )}
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  {route.zones.length} zones | {route.distance_km} km
                </div>
                <div className="mt-2">
                  <div className="flex justify-between text-xs mb-1">
                    <span>Coverage</span>
                    <span>{route.estimated_coverage}%</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-1.5">
                    <div
                      className="bg-green-500 h-1.5 rounded-full"
                      style={{ width: `${route.estimated_coverage}%` }}
                    ></div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {selectedRoute && (
        <div className="mt-6 bg-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Route Details</h3>
            <button
              onClick={() => setSelectedRoute(null)}
              className="text-gray-400 hover:text-white"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Priority Score</div>
              <div className="text-xl font-bold">{selectedRoute.priority_score}</div>
            </div>
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Coverage</div>
              <div className="text-xl font-bold">{selectedRoute.estimated_coverage}%</div>
            </div>
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Distance</div>
              <div className="text-xl font-bold">{selectedRoute.distance_km} km</div>
            </div>
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Duration</div>
              <div className="text-xl font-bold">{selectedRoute.duration_minutes} min</div>
            </div>
            <div className="bg-gray-600 rounded-lg p-3">
              <div className="text-gray-400 text-sm">Zones</div>
              <div className="text-xl font-bold">{selectedRoute.zones.length}</div>
            </div>
          </div>

          <div className="mt-4">
            <div className="text-gray-400 text-sm mb-2">Route Zones</div>
            <div className="flex flex-wrap gap-2">
              {selectedRoute.zones.map((zone, i) => (
                <span
                  key={i}
                  className="bg-gray-600 px-3 py-1 rounded-full text-sm flex items-center"
                >
                  <span className="w-4 h-4 rounded-full bg-blue-500 mr-2 flex items-center justify-center text-xs">
                    {i + 1}
                  </span>
                  {zone}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

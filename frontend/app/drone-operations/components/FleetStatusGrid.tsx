'use client';

import { useState, useEffect } from 'react';

interface Drone {
  drone_id: string;
  call_sign: string;
  drone_type: string;
  status: string;
  battery_percent: number;
  latitude: number;
  longitude: number;
  altitude_m: number;
  current_mission_id: string | null;
}

const statusColors: Record<string, string> = {
  OFFLINE: 'bg-gray-500',
  STANDBY: 'bg-green-500',
  PREFLIGHT: 'bg-yellow-500',
  AIRBORNE: 'bg-blue-500',
  ON_MISSION: 'bg-purple-500',
  RETURNING: 'bg-cyan-500',
  LANDING: 'bg-orange-500',
  CHARGING: 'bg-yellow-400',
  MAINTENANCE: 'bg-red-400',
  EMERGENCY: 'bg-red-600',
};

export default function FleetStatusGrid() {
  const [drones, setDrones] = useState<Drone[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockDrones: Drone[] = [
      {
        drone_id: 'drone-001',
        call_sign: 'EAGLE-1',
        drone_type: 'SURVEILLANCE',
        status: 'AIRBORNE',
        battery_percent: 78,
        latitude: 33.749,
        longitude: -84.388,
        altitude_m: 120,
        current_mission_id: 'mission-001',
      },
      {
        drone_id: 'drone-002',
        call_sign: 'HAWK-2',
        drone_type: 'TACTICAL',
        status: 'STANDBY',
        battery_percent: 100,
        latitude: 33.751,
        longitude: -84.391,
        altitude_m: 0,
        current_mission_id: null,
      },
      {
        drone_id: 'drone-003',
        call_sign: 'FALCON-3',
        drone_type: 'SEARCH_RESCUE',
        status: 'ON_MISSION',
        battery_percent: 45,
        latitude: 33.745,
        longitude: -84.385,
        altitude_m: 80,
        current_mission_id: 'mission-002',
      },
      {
        drone_id: 'drone-004',
        call_sign: 'RAVEN-4',
        drone_type: 'TRAFFIC',
        status: 'CHARGING',
        battery_percent: 35,
        latitude: 33.752,
        longitude: -84.390,
        altitude_m: 0,
        current_mission_id: null,
      },
    ];
    setDrones(mockDrones);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  const statusCounts = drones.reduce((acc, drone) => {
    acc[drone.status] = (acc[drone.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-400">{drones.length}</div>
          <div className="text-gray-400 text-sm">Total Drones</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-400">
            {statusCounts['AIRBORNE'] || 0}
          </div>
          <div className="text-gray-400 text-sm">Airborne</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-400">
            {statusCounts['ON_MISSION'] || 0}
          </div>
          <div className="text-gray-400 text-sm">On Mission</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-yellow-400">
            {statusCounts['STANDBY'] || 0}
          </div>
          <div className="text-gray-400 text-sm">Available</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {drones.map((drone) => (
          <div
            key={drone.drone_id}
            className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="font-bold text-lg">{drone.call_sign}</div>
                <div className="text-gray-400 text-sm">{drone.drone_type}</div>
              </div>
              <div
                className={`px-3 py-1 rounded-full text-xs font-medium ${
                  statusColors[drone.status] || 'bg-gray-500'
                }`}
              >
                {drone.status}
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Battery</span>
                <span
                  className={
                    drone.battery_percent > 50
                      ? 'text-green-400'
                      : drone.battery_percent > 20
                      ? 'text-yellow-400'
                      : 'text-red-400'
                  }
                >
                  {drone.battery_percent}%
                </span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    drone.battery_percent > 50
                      ? 'bg-green-400'
                      : drone.battery_percent > 20
                      ? 'bg-yellow-400'
                      : 'bg-red-400'
                  }`}
                  style={{ width: `${drone.battery_percent}%` }}
                ></div>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Altitude</span>
                <span>{drone.altitude_m}m</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Position</span>
                <span className="text-xs">
                  {drone.latitude.toFixed(4)}, {drone.longitude.toFixed(4)}
                </span>
              </div>

              {drone.current_mission_id && (
                <div className="mt-2 pt-2 border-t border-gray-600">
                  <span className="text-purple-400 text-sm">
                    Mission: {drone.current_mission_id}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

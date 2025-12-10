'use client';

import { useState } from 'react';

interface DronePosition {
  drone_id: string;
  call_sign: string;
  latitude: number;
  longitude: number;
  altitude_m: number;
  heading_deg: number;
  status: string;
}

interface Waypoint {
  waypoint_id: string;
  sequence: number;
  latitude: number;
  longitude: number;
  completed: boolean;
}

interface Route {
  route_id: string;
  drone_id: string;
  waypoints: Waypoint[];
}

export default function DroneRouteMap() {
  const [drones] = useState<DronePosition[]>([
    {
      drone_id: 'drone-001',
      call_sign: 'EAGLE-1',
      latitude: 33.749,
      longitude: -84.388,
      altitude_m: 120,
      heading_deg: 45,
      status: 'AIRBORNE',
    },
    {
      drone_id: 'drone-003',
      call_sign: 'FALCON-3',
      latitude: 33.745,
      longitude: -84.385,
      altitude_m: 80,
      heading_deg: 180,
      status: 'ON_MISSION',
    },
  ]);

  const [routes] = useState<Route[]>([
    {
      route_id: 'route-001',
      drone_id: 'drone-001',
      waypoints: [
        { waypoint_id: 'wp-1', sequence: 1, latitude: 33.748, longitude: -84.390, completed: true },
        { waypoint_id: 'wp-2', sequence: 2, latitude: 33.749, longitude: -84.388, completed: true },
        { waypoint_id: 'wp-3', sequence: 3, latitude: 33.750, longitude: -84.386, completed: false },
        { waypoint_id: 'wp-4', sequence: 4, latitude: 33.751, longitude: -84.384, completed: false },
      ],
    },
  ]);

  const [selectedDrone, setSelectedDrone] = useState<string | null>('drone-001');

  return (
    <div>
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div className="bg-gray-700 rounded-lg aspect-video flex items-center justify-center relative">
            <div className="absolute top-4 left-4 bg-gray-800 bg-opacity-75 px-3 py-2 rounded">
              <div className="text-sm font-medium">Map View</div>
              <div className="text-xs text-gray-400">
                Center: 33.749°N, 84.388°W
              </div>
            </div>

            <div className="text-gray-500 text-center">
              <svg
                className="w-16 h-16 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                />
              </svg>
              <p>Interactive Map Placeholder</p>
              <p className="text-sm mt-2">
                Mapbox/Leaflet integration would display here
              </p>
            </div>

            {drones.map((drone) => (
              <div
                key={drone.drone_id}
                className={`absolute w-8 h-8 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer ${
                  selectedDrone === drone.drone_id ? 'z-10' : ''
                }`}
                style={{
                  left: `${50 + (drone.longitude + 84.388) * 1000}%`,
                  top: `${50 - (drone.latitude - 33.749) * 1000}%`,
                }}
                onClick={() => setSelectedDrone(drone.drone_id)}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    selectedDrone === drone.drone_id
                      ? 'bg-blue-500 ring-2 ring-white'
                      : 'bg-purple-500'
                  }`}
                  style={{ transform: `rotate(${drone.heading_deg}deg)` }}
                >
                  <svg
                    className="w-5 h-5 text-white"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 2L4 12h5v10h6V12h5L12 2z" />
                  </svg>
                </div>
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 text-xs bg-gray-800 px-2 py-1 rounded whitespace-nowrap">
                  {drone.call_sign}
                </div>
              </div>
            ))}

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
            </div>
          </div>

          <div className="mt-4 flex space-x-2">
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg text-sm">
              Show All Routes
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg text-sm">
              Show Geofences
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg text-sm">
              Show No-Fly Zones
            </button>
            <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm">
              Center on Selected
            </button>
          </div>
        </div>

        <div>
          <div className="bg-gray-700 rounded-lg p-4 mb-4">
            <h3 className="text-lg font-semibold mb-4">Active Drones</h3>
            <div className="space-y-2">
              {drones.map((drone) => (
                <button
                  key={drone.drone_id}
                  onClick={() => setSelectedDrone(drone.drone_id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedDrone === drone.drone_id
                      ? 'bg-blue-600'
                      : 'bg-gray-600 hover:bg-gray-500'
                  }`}
                >
                  <div className="font-medium">{drone.call_sign}</div>
                  <div className="text-sm text-gray-300">
                    Alt: {drone.altitude_m}m | Hdg: {drone.heading_deg}°
                  </div>
                </button>
              ))}
            </div>
          </div>

          {selectedDrone && (
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Route Waypoints</h3>
              {routes
                .filter((r) => r.drone_id === selectedDrone)
                .map((route) => (
                  <div key={route.route_id} className="space-y-2">
                    {route.waypoints.map((wp) => (
                      <div
                        key={wp.waypoint_id}
                        className={`flex items-center p-2 rounded ${
                          wp.completed ? 'bg-green-900' : 'bg-gray-600'
                        }`}
                      >
                        <div
                          className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
                            wp.completed ? 'bg-green-500' : 'bg-gray-500'
                          }`}
                        >
                          {wp.completed ? (
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path
                                fillRule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clipRule="evenodd"
                              />
                            </svg>
                          ) : (
                            <span className="text-xs">{wp.sequence}</span>
                          )}
                        </div>
                        <div className="text-sm">
                          <div>Waypoint {wp.sequence}</div>
                          <div className="text-xs text-gray-400">
                            {wp.latitude.toFixed(4)}, {wp.longitude.toFixed(4)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

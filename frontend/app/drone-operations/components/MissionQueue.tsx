'use client';

import { useState } from 'react';

interface Mission {
  mission_id: string;
  name: string;
  mission_type: string;
  status: string;
  priority: string;
  assigned_drone: string | null;
  waypoints_count: number;
  completed_waypoints: number;
  created_at: string;
  estimated_duration_minutes: number;
}

const statusColors: Record<string, string> = {
  DRAFT: 'bg-gray-500',
  PLANNED: 'bg-blue-500',
  APPROVED: 'bg-green-500',
  QUEUED: 'bg-yellow-500',
  PREFLIGHT: 'bg-orange-500',
  ACTIVE: 'bg-purple-500',
  PAUSED: 'bg-yellow-400',
  RETURNING: 'bg-cyan-500',
  COMPLETED: 'bg-green-400',
  ABORTED: 'bg-red-500',
  FAILED: 'bg-red-600',
};

const priorityColors: Record<string, string> = {
  LOW: 'text-gray-400',
  NORMAL: 'text-blue-400',
  HIGH: 'text-orange-400',
  URGENT: 'text-red-400',
  CRITICAL: 'text-red-600',
};

export default function MissionQueue() {
  const [missions] = useState<Mission[]>([
    {
      mission_id: 'mission-001',
      name: 'Downtown Surveillance',
      mission_type: 'SURVEILLANCE',
      status: 'ACTIVE',
      priority: 'HIGH',
      assigned_drone: 'EAGLE-1',
      waypoints_count: 8,
      completed_waypoints: 5,
      created_at: new Date(Date.now() - 3600000).toISOString(),
      estimated_duration_minutes: 45,
    },
    {
      mission_id: 'mission-002',
      name: 'Missing Person Search',
      mission_type: 'SEARCH',
      status: 'ACTIVE',
      priority: 'CRITICAL',
      assigned_drone: 'FALCON-3',
      waypoints_count: 12,
      completed_waypoints: 3,
      created_at: new Date(Date.now() - 1800000).toISOString(),
      estimated_duration_minutes: 60,
    },
    {
      mission_id: 'mission-003',
      name: 'Traffic Monitoring - I-85',
      mission_type: 'TRAFFIC',
      status: 'QUEUED',
      priority: 'NORMAL',
      assigned_drone: null,
      waypoints_count: 6,
      completed_waypoints: 0,
      created_at: new Date(Date.now() - 900000).toISOString(),
      estimated_duration_minutes: 30,
    },
    {
      mission_id: 'mission-004',
      name: 'Perimeter Patrol - Zone 5',
      mission_type: 'PATROL',
      status: 'PLANNED',
      priority: 'LOW',
      assigned_drone: null,
      waypoints_count: 10,
      completed_waypoints: 0,
      created_at: new Date().toISOString(),
      estimated_duration_minutes: 40,
    },
  ]);

  const activeMissions = missions.filter((m) =>
    ['ACTIVE', 'PREFLIGHT', 'RETURNING'].includes(m.status)
  );
  const queuedMissions = missions.filter((m) =>
    ['QUEUED', 'PLANNED', 'APPROVED'].includes(m.status)
  );

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-400">{missions.length}</div>
          <div className="text-gray-400 text-sm">Total Missions</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-400">
            {activeMissions.length}
          </div>
          <div className="text-gray-400 text-sm">Active</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-yellow-400">
            {queuedMissions.length}
          </div>
          <div className="text-gray-400 text-sm">Queued</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-red-400">
            {missions.filter((m) => m.priority === 'CRITICAL').length}
          </div>
          <div className="text-gray-400 text-sm">Critical</div>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4">Active Missions</h3>
        <div className="space-y-4">
          {activeMissions.map((mission) => (
            <div
              key={mission.mission_id}
              className="bg-gray-700 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="font-bold text-lg">{mission.name}</div>
                  <div className="text-gray-400 text-sm">
                    {mission.mission_type} | {mission.assigned_drone}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${priorityColors[mission.priority]}`}>
                    {mission.priority}
                  </span>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      statusColors[mission.status]
                    }`}
                  >
                    {mission.status}
                  </span>
                </div>
              </div>

              <div className="mb-2">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Progress</span>
                  <span>
                    {mission.completed_waypoints} / {mission.waypoints_count} waypoints
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-purple-500 h-2 rounded-full"
                    style={{
                      width: `${(mission.completed_waypoints / mission.waypoints_count) * 100}%`,
                    }}
                  ></div>
                </div>
              </div>

              <div className="flex justify-between text-sm text-gray-400">
                <span>Est. Duration: {mission.estimated_duration_minutes} min</span>
                <span>Started: {new Date(mission.created_at).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">Mission Queue</h3>
        <div className="bg-gray-700 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-600 text-gray-300">
                <th className="text-left py-3 px-4">Mission</th>
                <th className="text-left py-3 px-4">Type</th>
                <th className="text-left py-3 px-4">Priority</th>
                <th className="text-left py-3 px-4">Status</th>
                <th className="text-left py-3 px-4">Waypoints</th>
                <th className="text-left py-3 px-4">Duration</th>
              </tr>
            </thead>
            <tbody>
              {queuedMissions.map((mission) => (
                <tr
                  key={mission.mission_id}
                  className="border-t border-gray-600 hover:bg-gray-600"
                >
                  <td className="py-3 px-4">{mission.name}</td>
                  <td className="py-3 px-4 text-gray-400">{mission.mission_type}</td>
                  <td className={`py-3 px-4 ${priorityColors[mission.priority]}`}>
                    {mission.priority}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-1 rounded text-xs ${statusColors[mission.status]}`}
                    >
                      {mission.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">{mission.waypoints_count}</td>
                  <td className="py-3 px-4">{mission.estimated_duration_minutes} min</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

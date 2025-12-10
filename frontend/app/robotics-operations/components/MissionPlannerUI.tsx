"use client";

import React, { useState, useEffect } from "react";

interface Waypoint {
  waypoint_id: string;
  sequence: number;
  waypoint_type: string;
  position: { x: number; y: number; z: number };
  duration_seconds: number | null;
  actions: string[];
  is_completed: boolean;
}

interface Mission {
  mission_id: string;
  name: string;
  mission_type: string;
  status: string;
  assigned_robots: string[];
  waypoints: Waypoint[];
  priority: number;
  created_at: string;
  started_at: string | null;
  estimated_duration_minutes: number;
  progress_percent: number;
}

export default function MissionPlannerUI() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(true);

  const [newMission, setNewMission] = useState({
    name: "",
    mission_type: "patrol",
    priority: 5,
    assigned_robots: [] as string[],
  });

  useEffect(() => {
    const mockMissions: Mission[] = [
      {
        mission_id: "mission-001",
        name: "North Perimeter Patrol",
        mission_type: "patrol",
        status: "in_progress",
        assigned_robots: ["robot-001", "robot-002"],
        waypoints: [
          { waypoint_id: "wp-1", sequence: 0, waypoint_type: "navigate", position: { x: 0, y: 0, z: 0 }, duration_seconds: null, actions: [], is_completed: true },
          { waypoint_id: "wp-2", sequence: 1, waypoint_type: "scan", position: { x: 100, y: 0, z: 0 }, duration_seconds: 30, actions: ["scan_360"], is_completed: true },
          { waypoint_id: "wp-3", sequence: 2, waypoint_type: "navigate", position: { x: 100, y: 100, z: 0 }, duration_seconds: null, actions: [], is_completed: false },
          { waypoint_id: "wp-4", sequence: 3, waypoint_type: "scan", position: { x: 0, y: 100, z: 0 }, duration_seconds: 30, actions: ["scan_360"], is_completed: false },
        ],
        priority: 7,
        created_at: new Date(Date.now() - 3600000).toISOString(),
        started_at: new Date(Date.now() - 1800000).toISOString(),
        estimated_duration_minutes: 45,
        progress_percent: 50,
      },
      {
        mission_id: "mission-002",
        name: "Building A Investigation",
        mission_type: "investigate",
        status: "queued",
        assigned_robots: ["robot-003"],
        waypoints: [
          { waypoint_id: "wp-5", sequence: 0, waypoint_type: "navigate", position: { x: 50, y: 50, z: 1 }, duration_seconds: null, actions: [], is_completed: false },
          { waypoint_id: "wp-6", sequence: 1, waypoint_type: "investigate", position: { x: 60, y: 55, z: 1 }, duration_seconds: 60, actions: ["record", "scan"], is_completed: false },
        ],
        priority: 8,
        created_at: new Date(Date.now() - 1800000).toISOString(),
        started_at: null,
        estimated_duration_minutes: 20,
        progress_percent: 0,
      },
      {
        mission_id: "mission-003",
        name: "East Zone Search",
        mission_type: "search",
        status: "completed",
        assigned_robots: ["robot-004"],
        waypoints: [
          { waypoint_id: "wp-7", sequence: 0, waypoint_type: "navigate", position: { x: 200, y: 100, z: 0 }, duration_seconds: null, actions: [], is_completed: true },
          { waypoint_id: "wp-8", sequence: 1, waypoint_type: "scan", position: { x: 250, y: 100, z: 0 }, duration_seconds: 45, actions: ["thermal_scan"], is_completed: true },
        ],
        priority: 6,
        created_at: new Date(Date.now() - 7200000).toISOString(),
        started_at: new Date(Date.now() - 6000000).toISOString(),
        estimated_duration_minutes: 30,
        progress_percent: 100,
      },
    ];

    setMissions(mockMissions);
    setIsLoading(false);
  }, []);

  const filteredMissions = missions.filter((mission) => {
    if (filterStatus === "all") return true;
    if (filterStatus === "active") return ["in_progress", "dispatched"].includes(mission.status);
    return mission.status === filterStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "in_progress":
      case "dispatched":
        return "bg-green-500";
      case "queued":
      case "planned":
        return "bg-blue-500";
      case "completed":
        return "bg-gray-500";
      case "paused":
        return "bg-yellow-500";
      case "aborted":
      case "failed":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getMissionTypeIcon = (type: string) => {
    switch (type) {
      case "patrol":
        return "🔄";
      case "search":
        return "🔍";
      case "investigate":
        return "🔎";
      case "respond":
        return "🚨";
      case "escort":
        return "🛡️";
      case "surveillance":
        return "👁️";
      default:
        return "📋";
    }
  };

  const handleCreateMission = () => {
    const mission: Mission = {
      mission_id: `mission-${Date.now()}`,
      name: newMission.name,
      mission_type: newMission.mission_type,
      status: "planned",
      assigned_robots: newMission.assigned_robots,
      waypoints: [],
      priority: newMission.priority,
      created_at: new Date().toISOString(),
      started_at: null,
      estimated_duration_minutes: 0,
      progress_percent: 0,
    };

    setMissions([mission, ...missions]);
    setIsCreating(false);
    setNewMission({ name: "", mission_type: "patrol", priority: 5, assigned_robots: [] });
  };

  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-24 bg-gray-700 rounded"></div>
            <div className="h-24 bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white">Mission Planner</h2>
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-gray-700 text-white rounded px-3 py-1 text-sm"
          >
            <option value="all">All Missions</option>
            <option value="active">Active</option>
            <option value="queued">Queued</option>
            <option value="completed">Completed</option>
          </select>
          <button
            onClick={() => setIsCreating(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1 rounded text-sm"
          >
            + New Mission
          </button>
        </div>
      </div>

      {isCreating && (
        <div className="bg-gray-700 rounded-lg p-4 mb-6">
          <h3 className="text-white font-medium mb-4">Create New Mission</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-gray-400 text-sm block mb-1">Mission Name</label>
              <input
                type="text"
                value={newMission.name}
                onChange={(e) => setNewMission({ ...newMission, name: e.target.value })}
                className="w-full bg-gray-600 text-white rounded px-3 py-2"
                placeholder="Enter mission name"
              />
            </div>
            <div>
              <label className="text-gray-400 text-sm block mb-1">Mission Type</label>
              <select
                value={newMission.mission_type}
                onChange={(e) => setNewMission({ ...newMission, mission_type: e.target.value })}
                className="w-full bg-gray-600 text-white rounded px-3 py-2"
              >
                <option value="patrol">Patrol</option>
                <option value="search">Search</option>
                <option value="investigate">Investigate</option>
                <option value="respond">Respond</option>
                <option value="escort">Escort</option>
                <option value="surveillance">Surveillance</option>
              </select>
            </div>
            <div>
              <label className="text-gray-400 text-sm block mb-1">Priority (1-10)</label>
              <input
                type="number"
                min="1"
                max="10"
                value={newMission.priority}
                onChange={(e) => setNewMission({ ...newMission, priority: parseInt(e.target.value) })}
                className="w-full bg-gray-600 text-white rounded px-3 py-2"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCreateMission}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm"
            >
              Create Mission
            </button>
            <button
              onClick={() => setIsCreating(false)}
              className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {filteredMissions.map((mission) => (
          <div
            key={mission.mission_id}
            className={`bg-gray-700 rounded-lg p-4 cursor-pointer transition-all ${
              selectedMission?.mission_id === mission.mission_id ? "ring-2 ring-blue-500" : "hover:bg-gray-650"
            }`}
            onClick={() => setSelectedMission(mission)}
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getMissionTypeIcon(mission.mission_type)}</span>
                <div>
                  <div className="text-white font-medium">{mission.name}</div>
                  <div className="text-gray-400 text-sm">{mission.mission_id}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-400 text-sm">Priority: {mission.priority}</span>
                <div className={`px-2 py-1 rounded text-xs text-white ${getStatusColor(mission.status)}`}>
                  {mission.status.replace("_", " ").toUpperCase()}
                </div>
              </div>
            </div>

            {mission.status === "in_progress" && (
              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Progress</span>
                  <span className="text-white">{mission.progress_percent}%</span>
                </div>
                <div className="bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${mission.progress_percent}%` }}
                  ></div>
                </div>
              </div>
            )}

            <div className="flex justify-between text-sm text-gray-400">
              <span>Robots: {mission.assigned_robots.length}</span>
              <span>Waypoints: {mission.waypoints.length}</span>
              <span>Est. Duration: {mission.estimated_duration_minutes} min</span>
            </div>
          </div>
        ))}
      </div>

      {selectedMission && (
        <div className="mt-6 bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-medium text-white mb-4">Mission Details</h3>
          
          <div className="mb-4">
            <h4 className="text-gray-400 text-sm mb-2">Waypoints</h4>
            <div className="space-y-2">
              {selectedMission.waypoints.map((wp, index) => (
                <div
                  key={wp.waypoint_id}
                  className={`flex items-center gap-3 p-2 rounded ${
                    wp.is_completed ? "bg-gray-600" : "bg-gray-800"
                  }`}
                >
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                      wp.is_completed ? "bg-green-500 text-white" : "bg-gray-500 text-gray-300"
                    }`}
                  >
                    {wp.is_completed ? "✓" : index + 1}
                  </div>
                  <div className="flex-1">
                    <span className="text-white capitalize">{wp.waypoint_type}</span>
                    <span className="text-gray-400 text-sm ml-2">
                      ({wp.position.x}, {wp.position.y})
                    </span>
                  </div>
                  {wp.duration_seconds && (
                    <span className="text-gray-400 text-sm">{wp.duration_seconds}s</span>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-2">
            {selectedMission.status === "planned" || selectedMission.status === "queued" ? (
              <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm">
                Start Mission
              </button>
            ) : selectedMission.status === "in_progress" ? (
              <>
                <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded text-sm">
                  Pause
                </button>
                <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm">
                  Abort
                </button>
              </>
            ) : null}
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm">
              Edit Waypoints
            </button>
            <button className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded text-sm">
              View Timeline
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";

interface SwarmUnit {
  unit_id: string;
  robot_id: string;
  role: string;
  position: { x: number; y: number; z: number };
  battery_level: number;
  is_active: boolean;
}

interface Swarm {
  swarm_id: string;
  name: string;
  units: SwarmUnit[];
  leader_id: string | null;
  formation: string | null;
  mission_id: string | null;
  status: string;
  center_position: { x: number; y: number; z: number };
}

const FORMATION_TYPES = [
  { value: "triangle", label: "Triangle", icon: "🔺" },
  { value: "line", label: "Line", icon: "➖" },
  { value: "surround", label: "Surround", icon: "⭕" },
  { value: "wedge", label: "Wedge", icon: "◀" },
  { value: "column", label: "Column", icon: "⬇️" },
  { value: "diamond", label: "Diamond", icon: "💎" },
  { value: "spread", label: "Spread", icon: "↔️" },
];

const ROLE_COLORS: Record<string, string> = {
  leader: "bg-yellow-500",
  scout: "bg-blue-500",
  follow: "bg-gray-500",
  flank_left: "bg-green-500",
  flank_right: "bg-green-500",
  rear_guard: "bg-purple-500",
  overwatch: "bg-red-500",
  support: "bg-cyan-500",
};

export default function SwarmControlUI() {
  const [swarms, setSwarms] = useState<Swarm[]>([]);
  const [selectedSwarm, setSelectedSwarm] = useState<Swarm | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedFormation, setSelectedFormation] = useState<string>("triangle");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const mockSwarms: Swarm[] = [
      {
        swarm_id: "swarm-001",
        name: "Alpha Pack",
        units: [
          { unit_id: "unit-001", robot_id: "robot-001", role: "leader", position: { x: 100, y: 200, z: 0 }, battery_level: 85, is_active: true },
          { unit_id: "unit-002", robot_id: "robot-002", role: "scout", position: { x: 90, y: 190, z: 0 }, battery_level: 72, is_active: true },
          { unit_id: "unit-003", robot_id: "robot-004", role: "flank_left", position: { x: 85, y: 205, z: 0 }, battery_level: 95, is_active: true },
        ],
        leader_id: "robot-001",
        formation: "triangle",
        mission_id: "mission-001",
        status: "active",
        center_position: { x: 92, y: 198, z: 0 },
      },
      {
        swarm_id: "swarm-002",
        name: "Bravo Team",
        units: [
          { unit_id: "unit-004", robot_id: "robot-005", role: "leader", position: { x: 300, y: 150, z: 0 }, battery_level: 90, is_active: true },
          { unit_id: "unit-005", robot_id: "robot-006", role: "follow", position: { x: 295, y: 145, z: 0 }, battery_level: 88, is_active: true },
        ],
        leader_id: "robot-005",
        formation: "line",
        mission_id: null,
        status: "standby",
        center_position: { x: 297, y: 147, z: 0 },
      },
    ];

    setSwarms(mockSwarms);
    setIsLoading(false);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500";
      case "standby":
        return "bg-blue-500";
      case "forming":
        return "bg-yellow-500";
      case "disbanded":
        return "bg-gray-500";
      default:
        return "bg-gray-500";
    }
  };

  const handleFormationChange = (formation: string) => {
    setSelectedFormation(formation);
    if (selectedSwarm) {
      setSwarms(swarms.map(s => 
        s.swarm_id === selectedSwarm.swarm_id 
          ? { ...s, formation } 
          : s
      ));
      setSelectedSwarm({ ...selectedSwarm, formation });
    }
  };

  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white">Swarm Control</h2>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1 rounded text-sm"
        >
          + Create Swarm
        </button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-3">
          <h3 className="text-gray-400 text-sm font-medium">Active Swarms</h3>
          {swarms.map((swarm) => (
            <div
              key={swarm.swarm_id}
              className={`bg-gray-700 rounded-lg p-4 cursor-pointer transition-all ${
                selectedSwarm?.swarm_id === swarm.swarm_id ? "ring-2 ring-blue-500" : "hover:bg-gray-650"
              }`}
              onClick={() => setSelectedSwarm(swarm)}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="text-white font-medium">{swarm.name}</div>
                  <div className="text-gray-400 text-sm">{swarm.swarm_id}</div>
                </div>
                <div className={`px-2 py-1 rounded text-xs text-white ${getStatusColor(swarm.status)}`}>
                  {swarm.status.toUpperCase()}
                </div>
              </div>

              <div className="flex items-center gap-4 mb-3">
                <div className="flex items-center gap-1">
                  <span className="text-gray-400 text-sm">Units:</span>
                  <span className="text-white">{swarm.units.length}</span>
                </div>
                {swarm.formation && (
                  <div className="flex items-center gap-1">
                    <span className="text-gray-400 text-sm">Formation:</span>
                    <span className="text-white capitalize">{swarm.formation}</span>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap gap-1">
                {swarm.units.map((unit) => (
                  <div
                    key={unit.unit_id}
                    className={`px-2 py-1 rounded text-xs text-white ${ROLE_COLORS[unit.role] || "bg-gray-500"}`}
                    title={`${unit.robot_id} - ${unit.role}`}
                  >
                    {unit.role.replace("_", " ")}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div>
          {selectedSwarm ? (
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-medium mb-4">Swarm Details: {selectedSwarm.name}</h3>

              <div className="mb-4">
                <h4 className="text-gray-400 text-sm mb-2">Formation Control</h4>
                <div className="grid grid-cols-4 gap-2">
                  {FORMATION_TYPES.map((formation) => (
                    <button
                      key={formation.value}
                      onClick={() => handleFormationChange(formation.value)}
                      className={`p-2 rounded text-center transition-all ${
                        selectedSwarm.formation === formation.value
                          ? "bg-blue-600 text-white"
                          : "bg-gray-600 text-gray-300 hover:bg-gray-500"
                      }`}
                    >
                      <div className="text-xl">{formation.icon}</div>
                      <div className="text-xs">{formation.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-gray-400 text-sm mb-2">Unit Status</h4>
                <div className="space-y-2">
                  {selectedSwarm.units.map((unit) => (
                    <div key={unit.unit_id} className="bg-gray-800 rounded p-3 flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${unit.is_active ? "bg-green-500" : "bg-red-500"}`}></div>
                        <div>
                          <div className="text-white text-sm">{unit.robot_id}</div>
                          <div className={`text-xs px-2 py-0.5 rounded inline-block ${ROLE_COLORS[unit.role] || "bg-gray-500"}`}>
                            {unit.role.replace("_", " ")}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-sm ${unit.battery_level > 30 ? "text-green-500" : "text-red-500"}`}>
                          {unit.battery_level}%
                        </div>
                        <div className="text-gray-400 text-xs">
                          ({unit.position.x.toFixed(0)}, {unit.position.y.toFixed(0)})
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-gray-400 text-sm mb-2">Swarm Center</h4>
                <div className="bg-gray-800 rounded p-3 text-center">
                  <span className="text-white">
                    ({selectedSwarm.center_position.x.toFixed(1)}, {selectedSwarm.center_position.y.toFixed(1)})
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm flex-1">
                  Route Swarm
                </button>
                <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded text-sm flex-1">
                  Auto-Assign Roles
                </button>
                <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm">
                  Disband
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-gray-700 rounded-lg p-8 text-center">
              <div className="text-4xl mb-4">🤖</div>
              <div className="text-gray-400">Select a swarm to view details and controls</div>
            </div>
          )}
        </div>
      </div>

      {isCreating && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-96">
            <h3 className="text-white font-medium mb-4">Create New Swarm</h3>
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm block mb-1">Swarm Name</label>
                <input
                  type="text"
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                  placeholder="Enter swarm name"
                />
              </div>
              <div>
                <label className="text-gray-400 text-sm block mb-1">Initial Formation</label>
                <select className="w-full bg-gray-700 text-white rounded px-3 py-2">
                  {FORMATION_TYPES.map((f) => (
                    <option key={f.value} value={f.value}>{f.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-gray-400 text-sm block mb-1">Select Robots</label>
                <div className="bg-gray-700 rounded p-2 max-h-32 overflow-y-auto">
                  <div className="text-gray-400 text-sm">No available robots</div>
                </div>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm flex-1">
                Create
              </button>
              <button
                onClick={() => setIsCreating(false)}
                className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded text-sm flex-1"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

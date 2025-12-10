"use client";

import React, { useState, useEffect } from "react";

interface Robot {
  robot_id: string;
  name: string;
  robot_type: string;
  status: string;
  battery_level: number;
  location: { x: number; y: number; z: number };
  assigned_zone: string;
  last_update: string;
}

interface FleetSummary {
  total_robots: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  low_battery_count: number;
  needs_maintenance_count: number;
}

export default function RoboticsFleetPanel() {
  const [robots, setRobots] = useState<Robot[]>([]);
  const [summary, setSummary] = useState<FleetSummary | null>(null);
  const [selectedRobot, setSelectedRobot] = useState<Robot | null>(null);
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const mockRobots: Robot[] = [
      {
        robot_id: "robot-001",
        name: "K9-Alpha",
        robot_type: "robot_dog",
        status: "active",
        battery_level: 85,
        location: { x: 100, y: 200, z: 0 },
        assigned_zone: "zone-north",
        last_update: new Date().toISOString(),
      },
      {
        robot_id: "robot-002",
        name: "UGV-Bravo",
        robot_type: "ugv",
        status: "patrolling",
        battery_level: 72,
        location: { x: 150, y: 180, z: 0 },
        assigned_zone: "zone-east",
        last_update: new Date().toISOString(),
      },
      {
        robot_id: "robot-003",
        name: "Indoor-Charlie",
        robot_type: "indoor_robot",
        status: "charging",
        battery_level: 25,
        location: { x: 50, y: 50, z: 1 },
        assigned_zone: "building-a",
        last_update: new Date().toISOString(),
      },
      {
        robot_id: "robot-004",
        name: "K9-Delta",
        robot_type: "robot_dog",
        status: "standby",
        battery_level: 95,
        location: { x: 200, y: 100, z: 0 },
        assigned_zone: "zone-south",
        last_update: new Date().toISOString(),
      },
    ];

    const mockSummary: FleetSummary = {
      total_robots: 4,
      by_type: { robot_dog: 2, ugv: 1, indoor_robot: 1 },
      by_status: { active: 1, patrolling: 1, charging: 1, standby: 1 },
      low_battery_count: 1,
      needs_maintenance_count: 0,
    };

    setRobots(mockRobots);
    setSummary(mockSummary);
    setIsLoading(false);
  }, []);

  const filteredRobots = robots.filter((robot) => {
    if (filterType !== "all" && robot.robot_type !== filterType) return false;
    if (filterStatus !== "all" && robot.status !== filterStatus) return false;
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
      case "patrolling":
        return "bg-green-500";
      case "standby":
        return "bg-blue-500";
      case "charging":
        return "bg-yellow-500";
      case "offline":
      case "error":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getBatteryColor = (level: number) => {
    if (level > 60) return "text-green-500";
    if (level > 30) return "text-yellow-500";
    return "text-red-500";
  };

  const getRobotIcon = (type: string) => {
    switch (type) {
      case "robot_dog":
        return "🐕";
      case "ugv":
        return "🚗";
      case "indoor_robot":
        return "🤖";
      default:
        return "⚙️";
    }
  };

  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-20 bg-gray-700 rounded"></div>
            <div className="h-20 bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white">Robotics Fleet</h2>
        <div className="flex gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-gray-700 text-white rounded px-3 py-1 text-sm"
          >
            <option value="all">All Types</option>
            <option value="robot_dog">Robot Dogs</option>
            <option value="ugv">UGVs</option>
            <option value="indoor_robot">Indoor Robots</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-gray-700 text-white rounded px-3 py-1 text-sm"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="patrolling">Patrolling</option>
            <option value="standby">Standby</option>
            <option value="charging">Charging</option>
          </select>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-white">{summary.total_robots}</div>
            <div className="text-gray-400 text-sm">Total Robots</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-green-500">
              {(summary.by_status.active || 0) + (summary.by_status.patrolling || 0)}
            </div>
            <div className="text-gray-400 text-sm">Active</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-yellow-500">{summary.low_battery_count}</div>
            <div className="text-gray-400 text-sm">Low Battery</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-red-500">{summary.needs_maintenance_count}</div>
            <div className="text-gray-400 text-sm">Needs Maintenance</div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {filteredRobots.map((robot) => (
          <div
            key={robot.robot_id}
            className={`bg-gray-700 rounded-lg p-4 cursor-pointer transition-all ${
              selectedRobot?.robot_id === robot.robot_id ? "ring-2 ring-blue-500" : "hover:bg-gray-650"
            }`}
            onClick={() => setSelectedRobot(robot)}
          >
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getRobotIcon(robot.robot_type)}</span>
                <div>
                  <div className="text-white font-medium">{robot.name}</div>
                  <div className="text-gray-400 text-sm">{robot.robot_id}</div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className={`${getBatteryColor(robot.battery_level)} font-medium`}>
                  {robot.battery_level}%
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(robot.status)}`}></div>
                  <span className="text-gray-300 text-sm capitalize">{robot.status}</span>
                </div>
              </div>
            </div>
            <div className="mt-2 flex justify-between text-sm text-gray-400">
              <span>Zone: {robot.assigned_zone}</span>
              <span>
                Location: ({robot.location.x.toFixed(1)}, {robot.location.y.toFixed(1)})
              </span>
            </div>
          </div>
        ))}
      </div>

      {selectedRobot && (
        <div className="mt-6 bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-medium text-white mb-3">Robot Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">ID:</span>
              <span className="text-white ml-2">{selectedRobot.robot_id}</span>
            </div>
            <div>
              <span className="text-gray-400">Type:</span>
              <span className="text-white ml-2 capitalize">{selectedRobot.robot_type.replace("_", " ")}</span>
            </div>
            <div>
              <span className="text-gray-400">Status:</span>
              <span className="text-white ml-2 capitalize">{selectedRobot.status}</span>
            </div>
            <div>
              <span className="text-gray-400">Battery:</span>
              <span className={`ml-2 ${getBatteryColor(selectedRobot.battery_level)}`}>
                {selectedRobot.battery_level}%
              </span>
            </div>
            <div>
              <span className="text-gray-400">Zone:</span>
              <span className="text-white ml-2">{selectedRobot.assigned_zone}</span>
            </div>
            <div>
              <span className="text-gray-400">Last Update:</span>
              <span className="text-white ml-2">
                {new Date(selectedRobot.last_update).toLocaleTimeString()}
              </span>
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm">
              Send Command
            </button>
            <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm">
              View Telemetry
            </button>
            <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded text-sm">
              Assign Mission
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

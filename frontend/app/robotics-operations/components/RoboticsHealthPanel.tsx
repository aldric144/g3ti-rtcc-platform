"use client";

import React, { useState, useEffect } from "react";

interface ComponentHealth {
  component: string;
  status: string;
  health_score: number;
  temperature: number | null;
  wear_level: number | null;
  last_maintenance: string | null;
  predicted_failure: string | null;
}

interface RobotHealth {
  robot_id: string;
  robot_name: string;
  overall_status: string;
  overall_score: number;
  battery_health: number;
  motor_health: number;
  sensor_health: number;
  communication_health: number;
  components: ComponentHealth[];
  last_assessment: string;
  next_maintenance: string | null;
  alerts: string[];
}

export default function RoboticsHealthPanel() {
  const [healthData, setHealthData] = useState<RobotHealth[]>([]);
  const [selectedRobot, setSelectedRobot] = useState<RobotHealth | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const mockHealthData: RobotHealth[] = [
      {
        robot_id: "robot-001",
        robot_name: "K9-Alpha",
        overall_status: "healthy",
        overall_score: 92,
        battery_health: 95,
        motor_health: 88,
        sensor_health: 94,
        communication_health: 91,
        components: [
          { component: "Battery Pack", status: "healthy", health_score: 95, temperature: 32, wear_level: 12, last_maintenance: "2025-11-15", predicted_failure: null },
          { component: "Front Left Motor", status: "healthy", health_score: 90, temperature: 42, wear_level: 18, last_maintenance: "2025-11-20", predicted_failure: null },
          { component: "Front Right Motor", status: "healthy", health_score: 88, temperature: 44, wear_level: 20, last_maintenance: "2025-11-20", predicted_failure: null },
          { component: "Rear Left Motor", status: "healthy", health_score: 87, temperature: 41, wear_level: 22, last_maintenance: "2025-11-20", predicted_failure: null },
          { component: "Rear Right Motor", status: "healthy", health_score: 86, temperature: 43, wear_level: 24, last_maintenance: "2025-11-20", predicted_failure: null },
          { component: "LiDAR Sensor", status: "healthy", health_score: 96, temperature: 35, wear_level: 8, last_maintenance: "2025-12-01", predicted_failure: null },
          { component: "Camera Array", status: "healthy", health_score: 94, temperature: 38, wear_level: 10, last_maintenance: "2025-12-01", predicted_failure: null },
          { component: "IMU", status: "healthy", health_score: 98, temperature: 30, wear_level: 5, last_maintenance: "2025-12-01", predicted_failure: null },
        ],
        last_assessment: new Date(Date.now() - 300000).toISOString(),
        next_maintenance: "2025-12-20",
        alerts: [],
      },
      {
        robot_id: "robot-002",
        robot_name: "UGV-Bravo",
        overall_status: "warning",
        overall_score: 72,
        battery_health: 65,
        motor_health: 78,
        sensor_health: 82,
        communication_health: 85,
        components: [
          { component: "Battery Pack", status: "warning", health_score: 65, temperature: 38, wear_level: 45, last_maintenance: "2025-10-01", predicted_failure: "2026-02-15" },
          { component: "Left Motor", status: "healthy", health_score: 80, temperature: 48, wear_level: 30, last_maintenance: "2025-11-15", predicted_failure: null },
          { component: "Right Motor", status: "warning", health_score: 76, temperature: 52, wear_level: 35, last_maintenance: "2025-11-15", predicted_failure: "2026-03-01" },
          { component: "LiDAR Sensor", status: "healthy", health_score: 85, temperature: 36, wear_level: 15, last_maintenance: "2025-11-20", predicted_failure: null },
          { component: "Radar", status: "healthy", health_score: 88, temperature: 34, wear_level: 12, last_maintenance: "2025-11-20", predicted_failure: null },
        ],
        last_assessment: new Date(Date.now() - 600000).toISOString(),
        next_maintenance: "2025-12-15",
        alerts: ["Battery degradation detected", "Right motor showing increased wear"],
      },
      {
        robot_id: "robot-003",
        robot_name: "Indoor-Charlie",
        overall_status: "critical",
        overall_score: 45,
        battery_health: 25,
        motor_health: 55,
        sensor_health: 60,
        communication_health: 70,
        components: [
          { component: "Battery Pack", status: "critical", health_score: 25, temperature: 42, wear_level: 80, last_maintenance: "2025-08-01", predicted_failure: "2025-12-20" },
          { component: "Drive Motor", status: "warning", health_score: 55, temperature: 55, wear_level: 50, last_maintenance: "2025-10-01", predicted_failure: "2026-01-15" },
          { component: "Camera", status: "warning", health_score: 60, temperature: 40, wear_level: 40, last_maintenance: "2025-10-15", predicted_failure: null },
          { component: "WiFi Module", status: "healthy", health_score: 70, temperature: 35, wear_level: 25, last_maintenance: "2025-11-01", predicted_failure: null },
        ],
        last_assessment: new Date(Date.now() - 120000).toISOString(),
        next_maintenance: "2025-12-12",
        alerts: ["Critical: Battery replacement required", "Motor maintenance overdue", "Camera calibration needed"],
      },
      {
        robot_id: "robot-004",
        robot_name: "K9-Delta",
        overall_status: "healthy",
        overall_score: 98,
        battery_health: 99,
        motor_health: 97,
        sensor_health: 98,
        communication_health: 99,
        components: [
          { component: "Battery Pack", status: "healthy", health_score: 99, temperature: 28, wear_level: 2, last_maintenance: "2025-12-01", predicted_failure: null },
          { component: "Front Left Motor", status: "healthy", health_score: 98, temperature: 38, wear_level: 3, last_maintenance: "2025-12-01", predicted_failure: null },
          { component: "Front Right Motor", status: "healthy", health_score: 97, temperature: 39, wear_level: 4, last_maintenance: "2025-12-01", predicted_failure: null },
          { component: "Rear Left Motor", status: "healthy", health_score: 97, temperature: 37, wear_level: 4, last_maintenance: "2025-12-01", predicted_failure: null },
          { component: "Rear Right Motor", status: "healthy", health_score: 96, temperature: 38, wear_level: 5, last_maintenance: "2025-12-01", predicted_failure: null },
          { component: "LiDAR Sensor", status: "healthy", health_score: 99, temperature: 32, wear_level: 1, last_maintenance: "2025-12-05", predicted_failure: null },
          { component: "Camera Array", status: "healthy", health_score: 98, temperature: 34, wear_level: 2, last_maintenance: "2025-12-05", predicted_failure: null },
        ],
        last_assessment: new Date(Date.now() - 180000).toISOString(),
        next_maintenance: "2026-01-01",
        alerts: [],
      },
    ];

    setHealthData(mockHealthData);
    setIsLoading(false);
  }, []);

  const filteredHealth = healthData.filter((robot) => {
    if (filterStatus === "all") return true;
    return robot.overall_status === filterStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-500";
      case "warning":
        return "bg-yellow-500";
      case "critical":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    return "text-red-500";
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    return "bg-red-500";
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
        <h2 className="text-xl font-bold text-white">Robotics Health Monitor</h2>
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-gray-700 text-white rounded px-3 py-1 text-sm"
          >
            <option value="all">All Status</option>
            <option value="healthy">Healthy</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-white">{healthData.length}</div>
          <div className="text-gray-400 text-sm">Total Robots</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-500">
            {healthData.filter((r) => r.overall_status === "healthy").length}
          </div>
          <div className="text-gray-400 text-sm">Healthy</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-yellow-500">
            {healthData.filter((r) => r.overall_status === "warning").length}
          </div>
          <div className="text-gray-400 text-sm">Warning</div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-500">
            {healthData.filter((r) => r.overall_status === "critical").length}
          </div>
          <div className="text-gray-400 text-sm">Critical</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-3">
          {filteredHealth.map((robot) => (
            <div
              key={robot.robot_id}
              className={`bg-gray-700 rounded-lg p-4 cursor-pointer transition-all ${
                selectedRobot?.robot_id === robot.robot_id ? "ring-2 ring-blue-500" : "hover:bg-gray-650"
              }`}
              onClick={() => setSelectedRobot(robot)}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="text-white font-medium">{robot.robot_name}</div>
                  <div className="text-gray-400 text-sm">{robot.robot_id}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-2xl font-bold ${getScoreColor(robot.overall_score)}`}>
                    {robot.overall_score}
                  </span>
                  <div className={`px-2 py-1 rounded text-xs text-white ${getStatusColor(robot.overall_status)}`}>
                    {robot.overall_status.toUpperCase()}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-2 mb-3">
                <div>
                  <div className="text-gray-400 text-xs mb-1">Battery</div>
                  <div className="bg-gray-600 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(robot.battery_health)}`}
                      style={{ width: `${robot.battery_health}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs mb-1">Motors</div>
                  <div className="bg-gray-600 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(robot.motor_health)}`}
                      style={{ width: `${robot.motor_health}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs mb-1">Sensors</div>
                  <div className="bg-gray-600 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(robot.sensor_health)}`}
                      style={{ width: `${robot.sensor_health}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 text-xs mb-1">Comms</div>
                  <div className="bg-gray-600 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getProgressColor(robot.communication_health)}`}
                      style={{ width: `${robot.communication_health}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {robot.alerts.length > 0 && (
                <div className="text-red-400 text-xs">
                  {robot.alerts.length} alert{robot.alerts.length > 1 ? "s" : ""}
                </div>
              )}
            </div>
          ))}
        </div>

        <div>
          {selectedRobot ? (
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-medium mb-4">
                {selectedRobot.robot_name} - Component Health
              </h3>

              {selectedRobot.alerts.length > 0 && (
                <div className="bg-red-900 bg-opacity-30 border border-red-500 rounded-lg p-3 mb-4">
                  <h4 className="text-red-400 font-medium text-sm mb-2">Active Alerts</h4>
                  <ul className="space-y-1">
                    {selectedRobot.alerts.map((alert, index) => (
                      <li key={index} className="text-red-300 text-sm flex items-center gap-2">
                        <span>⚠️</span> {alert}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="space-y-2 max-h-64 overflow-y-auto mb-4">
                {selectedRobot.components.map((component, index) => (
                  <div key={index} className="bg-gray-800 rounded p-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white text-sm">{component.component}</span>
                      <div className="flex items-center gap-2">
                        <span className={`text-sm ${getScoreColor(component.health_score)}`}>
                          {component.health_score}%
                        </span>
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(component.status)}`}></div>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs text-gray-400">
                      {component.temperature && (
                        <div>Temp: {component.temperature}°C</div>
                      )}
                      {component.wear_level !== null && (
                        <div>Wear: {component.wear_level}%</div>
                      )}
                      {component.predicted_failure && (
                        <div className="text-yellow-400">
                          Fail: {component.predicted_failure}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                <div>
                  <span className="text-gray-400">Last Assessment:</span>
                  <div className="text-white">
                    {new Date(selectedRobot.last_assessment).toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400">Next Maintenance:</span>
                  <div className="text-white">
                    {selectedRobot.next_maintenance || "Not scheduled"}
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm flex-1">
                  Run Diagnostics
                </button>
                <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded text-sm flex-1">
                  Schedule Maintenance
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-gray-700 rounded-lg p-8 text-center h-full flex items-center justify-center">
              <div>
                <div className="text-4xl mb-4">🔧</div>
                <div className="text-gray-400">Select a robot to view detailed health information</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

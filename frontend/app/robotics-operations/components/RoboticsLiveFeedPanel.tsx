"use client";

import React, { useState, useEffect } from "react";

interface TelemetryData {
  robot_id: string;
  robot_name: string;
  location: { x: number; y: number; z: number };
  heading: number;
  speed: number;
  battery_level: number;
  battery_voltage: number;
  motor_temperatures: Record<string, number>;
  cpu_usage: number;
  memory_usage: number;
  signal_strength: number;
  active_sensors: string[];
  timestamp: string;
}

interface StreamSession {
  session_id: string;
  robot_id: string;
  robot_name: string;
  stream_type: string;
  status: string;
  viewers: number;
}

export default function RoboticsLiveFeedPanel() {
  const [telemetryData, setTelemetryData] = useState<TelemetryData[]>([]);
  const [activeStreams, setActiveStreams] = useState<StreamSession[]>([]);
  const [selectedStream, setSelectedStream] = useState<StreamSession | null>(null);
  const [viewMode, setViewMode] = useState<"telemetry" | "video">("telemetry");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const mockTelemetry: TelemetryData[] = [
      {
        robot_id: "robot-001",
        robot_name: "K9-Alpha",
        location: { x: 100.5, y: 200.3, z: 0 },
        heading: 45.0,
        speed: 1.2,
        battery_level: 85,
        battery_voltage: 24.5,
        motor_temperatures: { front_left: 42, front_right: 44, rear_left: 41, rear_right: 43 },
        cpu_usage: 35,
        memory_usage: 48,
        signal_strength: 92,
        active_sensors: ["lidar", "camera", "imu", "gps"],
        timestamp: new Date().toISOString(),
      },
      {
        robot_id: "robot-002",
        robot_name: "UGV-Bravo",
        location: { x: 150.2, y: 180.7, z: 0 },
        heading: 120.0,
        speed: 2.5,
        battery_level: 72,
        battery_voltage: 23.8,
        motor_temperatures: { left: 48, right: 47 },
        cpu_usage: 42,
        memory_usage: 55,
        signal_strength: 88,
        active_sensors: ["lidar", "camera", "radar"],
        timestamp: new Date().toISOString(),
      },
    ];

    const mockStreams: StreamSession[] = [
      {
        session_id: "stream-001",
        robot_id: "robot-001",
        robot_name: "K9-Alpha",
        stream_type: "video",
        status: "active",
        viewers: 3,
      },
      {
        session_id: "stream-002",
        robot_id: "robot-002",
        robot_name: "UGV-Bravo",
        stream_type: "video",
        status: "active",
        viewers: 1,
      },
    ];

    setTelemetryData(mockTelemetry);
    setActiveStreams(mockStreams);
    setIsLoading(false);

    const interval = setInterval(() => {
      setTelemetryData((prev) =>
        prev.map((t) => ({
          ...t,
          location: {
            x: t.location.x + (Math.random() - 0.5) * 0.5,
            y: t.location.y + (Math.random() - 0.5) * 0.5,
            z: t.location.z,
          },
          heading: (t.heading + (Math.random() - 0.5) * 5) % 360,
          speed: Math.max(0, t.speed + (Math.random() - 0.5) * 0.3),
          battery_level: Math.max(0, t.battery_level - Math.random() * 0.01),
          cpu_usage: Math.min(100, Math.max(0, t.cpu_usage + (Math.random() - 0.5) * 5)),
          memory_usage: Math.min(100, Math.max(0, t.memory_usage + (Math.random() - 0.5) * 2)),
          timestamp: new Date().toISOString(),
        }))
      );
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getSignalColor = (strength: number) => {
    if (strength > 80) return "text-green-500";
    if (strength > 50) return "text-yellow-500";
    return "text-red-500";
  };

  const getBatteryColor = (level: number) => {
    if (level > 60) return "text-green-500";
    if (level > 30) return "text-yellow-500";
    return "text-red-500";
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
        <h2 className="text-xl font-bold text-white">Live Feed</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode("telemetry")}
            className={`px-4 py-2 rounded text-sm ${
              viewMode === "telemetry" ? "bg-blue-600 text-white" : "bg-gray-700 text-gray-300"
            }`}
          >
            Telemetry
          </button>
          <button
            onClick={() => setViewMode("video")}
            className={`px-4 py-2 rounded text-sm ${
              viewMode === "video" ? "bg-blue-600 text-white" : "bg-gray-700 text-gray-300"
            }`}
          >
            Video Feeds
          </button>
        </div>
      </div>

      {viewMode === "telemetry" ? (
        <div className="space-y-4">
          {telemetryData.map((data) => (
            <div key={data.robot_id} className="bg-gray-700 rounded-lg p-4">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-white font-medium">{data.robot_name}</span>
                  <span className="text-gray-400 text-sm">({data.robot_id})</span>
                </div>
                <span className="text-gray-400 text-xs">
                  {new Date(data.timestamp).toLocaleTimeString()}
                </span>
              </div>

              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-gray-400 text-xs mb-1">Position</div>
                  <div className="text-white text-sm">
                    ({data.location.x.toFixed(1)}, {data.location.y.toFixed(1)})
                  </div>
                </div>
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-gray-400 text-xs mb-1">Heading</div>
                  <div className="text-white text-sm">{data.heading.toFixed(1)}°</div>
                </div>
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-gray-400 text-xs mb-1">Speed</div>
                  <div className="text-white text-sm">{data.speed.toFixed(2)} m/s</div>
                </div>
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-gray-400 text-xs mb-1">Battery</div>
                  <div className={`text-sm ${getBatteryColor(data.battery_level)}`}>
                    {data.battery_level.toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-gray-400 text-xs mb-1">CPU Usage</div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-600 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${data.cpu_usage}%` }}
                      ></div>
                    </div>
                    <span className="text-white text-xs">{data.cpu_usage.toFixed(0)}%</span>
                  </div>
                </div>
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-gray-400 text-xs mb-1">Memory</div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-600 rounded-full h-2">
                      <div
                        className="bg-purple-500 h-2 rounded-full"
                        style={{ width: `${data.memory_usage}%` }}
                      ></div>
                    </div>
                    <span className="text-white text-xs">{data.memory_usage.toFixed(0)}%</span>
                  </div>
                </div>
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-gray-400 text-xs mb-1">Signal</div>
                  <div className={`text-sm ${getSignalColor(data.signal_strength)}`}>
                    {data.signal_strength}%
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {data.active_sensors.map((sensor) => (
                  <span
                    key={sensor}
                    className="bg-gray-600 text-gray-300 px-2 py-1 rounded text-xs uppercase"
                  >
                    {sensor}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {activeStreams.map((stream) => (
              <div
                key={stream.session_id}
                className={`bg-gray-700 rounded-lg overflow-hidden cursor-pointer ${
                  selectedStream?.session_id === stream.session_id ? "ring-2 ring-blue-500" : ""
                }`}
                onClick={() => setSelectedStream(stream)}
              >
                <div className="aspect-video bg-gray-900 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-4xl mb-2">📹</div>
                    <div className="text-gray-400 text-sm">Live Stream</div>
                    <div className="text-white font-medium">{stream.robot_name}</div>
                  </div>
                </div>
                <div className="p-3 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-white text-sm">LIVE</span>
                  </div>
                  <div className="text-gray-400 text-sm">{stream.viewers} viewers</div>
                </div>
              </div>
            ))}
          </div>

          {selectedStream && (
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-medium mb-3">Stream Controls</h3>
              <div className="flex gap-2">
                <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm">
                  Stop Stream
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm">
                  Full Screen
                </button>
                <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm">
                  Record
                </button>
                <button className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded text-sm">
                  Screenshot
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

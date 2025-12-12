"use client";

import React, { useState, useEffect } from "react";

interface AgencyTask {
  task_id: string;
  agency: string;
  priority: number;
  priority_name: string;
  status: string;
  description: string;
  zone: string;
  assigned_units: string[];
  estimated_duration_hours: number;
}

interface EvacuationRoute {
  route_id: string;
  origin_zone: string;
  destination: string;
  route_name: string;
  distance_miles: number;
  estimated_time_minutes: number;
  status: string;
  time_to_clear_hours: number;
}

interface CoordinationPlan {
  plan_id: string;
  incident_type: string;
  threat_level: number;
  affected_zones: string[];
  total_tasks: number;
  total_resources_deployed: number;
  total_personnel_deployed: number;
  estimated_response_time_hours: number;
  agency_tasks: AgencyTask[];
  evacuation_routes: EvacuationRoute[];
  coordination_notes: string[];
}

export default function ResponseCoordinationConsole() {
  const [incidentType, setIncidentType] = useState("hurricane");
  const [threatLevel, setThreatLevel] = useState(3);
  const [selectedZones, setSelectedZones] = useState<string[]>(["Zone_A", "Zone_B"]);
  const [coordinationPlan, setCoordinationPlan] = useState<CoordinationPlan | null>(null);
  const [loading, setLoading] = useState(false);

  const incidentTypes = [
    { value: "hurricane", label: "Hurricane" },
    { value: "flooding", label: "Flooding" },
    { value: "fire", label: "Fire" },
    { value: "hazmat", label: "Hazmat Incident" },
    { value: "tornado", label: "Tornado" },
    { value: "earthquake", label: "Earthquake" },
  ];

  const zones = [
    "Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
    "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J",
  ];

  const coordinateResponse = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/emergency-ai/coordinate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_type: incidentType,
          threat_level: threatLevel,
          affected_zones: selectedZones,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCoordinationPlan(data);
      }
    } catch (error) {
      console.error("Failed to coordinate response:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleZone = (zone: string) => {
    setSelectedZones((prev) =>
      prev.includes(zone)
        ? prev.filter((z) => z !== zone)
        : [...prev, zone]
    );
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 5:
        return "bg-red-500";
      case 4:
        return "bg-orange-500";
      case 3:
        return "bg-yellow-500";
      case 2:
        return "bg-blue-500";
      default:
        return "bg-green-500";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open":
        return "text-green-400";
      case "congested":
        return "text-yellow-400";
      case "blocked":
      case "flooded":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Incident Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Incident Type
              </label>
              <select
                value={incidentType}
                onChange={(e) => setIncidentType(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
              >
                {incidentTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Threat Level: {threatLevel}
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={threatLevel}
                onChange={(e) => setThreatLevel(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-400">
                <span>Minimal</span>
                <span>Low</span>
                <span>Moderate</span>
                <span>High</span>
                <span>Extreme</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Affected Zones
              </label>
              <div className="grid grid-cols-5 gap-2">
                {zones.map((zone) => (
                  <button
                    key={zone}
                    onClick={() => toggleZone(zone)}
                    className={`px-2 py-1 rounded text-xs ${
                      selectedZones.includes(zone)
                        ? "bg-blue-600 text-white"
                        : "bg-gray-700 text-gray-400"
                    }`}
                  >
                    {zone.replace("Zone_", "")}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={coordinateResponse}
              disabled={loading || selectedZones.length === 0}
              className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {loading ? "Coordinating..." : "Coordinate Multi-Agency Response"}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Multi-Agency Assignment Board</h2>
          {coordinationPlan ? (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-700 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold">{coordinationPlan.total_tasks}</p>
                  <p className="text-xs text-gray-400">Tasks</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold">{coordinationPlan.total_resources_deployed}</p>
                  <p className="text-xs text-gray-400">Resources</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold">{coordinationPlan.total_personnel_deployed}</p>
                  <p className="text-xs text-gray-400">Personnel</p>
                </div>
                <div className="bg-gray-700 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold">{coordinationPlan.estimated_response_time_hours}h</p>
                  <p className="text-xs text-gray-400">Response Time</p>
                </div>
              </div>

              <div className="max-h-64 overflow-y-auto space-y-2">
                {coordinationPlan.agency_tasks.map((task) => (
                  <div
                    key={task.task_id}
                    className="bg-gray-700 rounded-lg p-3 flex items-center justify-between"
                  >
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`px-2 py-0.5 rounded text-xs ${getPriorityColor(
                            task.priority
                          )}`}
                        >
                          {task.priority_name}
                        </span>
                        <span className="font-medium capitalize">
                          {task.agency.replace("_", " ")}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mt-1">
                        {task.description}
                      </p>
                      <p className="text-xs text-gray-500">
                        Zone: {task.zone} | Units: {task.assigned_units.join(", ")}
                      </p>
                    </div>
                    <span className="text-xs text-gray-400 capitalize">
                      {task.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <p className="text-4xl mb-2">🚨</p>
              <p>Configure incident and coordinate response</p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Evacuation Route Visualizer</h2>
        {coordinationPlan && coordinationPlan.evacuation_routes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {coordinationPlan.evacuation_routes.map((route) => (
              <div key={route.route_id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{route.route_name}</span>
                  <span className={`text-sm ${getStatusColor(route.status)}`}>
                    {route.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-400">
                  From: {route.origin_zone} → {route.destination}
                </p>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Distance:</span>
                    <span className="ml-1">{route.distance_miles} mi</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Time:</span>
                    <span className="ml-1">{route.estimated_time_minutes} min</span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-gray-500">Clear Time:</span>
                    <span className="ml-1">{route.time_to_clear_hours.toFixed(1)} hours</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-gray-700 rounded-lg h-48 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <p>Evacuation routes will appear after coordination</p>
            </div>
          </div>
        )}
      </div>

      {coordinationPlan && coordinationPlan.coordination_notes.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Coordination Notes</h2>
          <ul className="space-y-2">
            {coordinationPlan.coordination_notes.map((note, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-blue-400">•</span>
                <span className="text-gray-300">{note}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

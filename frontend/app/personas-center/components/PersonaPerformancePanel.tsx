"use client";

import React, { useState, useEffect } from "react";

interface Persona {
  persona_id: string;
  name: string;
  persona_type: string;
  role: string;
  status: string;
  compliance_score: number;
  metrics: {
    total_interactions: number;
    successful_interactions: number;
    average_response_time_ms: number;
    missions_completed: number;
    missions_failed: number;
  };
}

interface PersonaPerformancePanelProps {
  personas: Persona[];
  selectedPersona: Persona | null;
}

const getPerformanceColor = (value: number, threshold: number): string => {
  if (value >= threshold * 0.95) return "text-green-400";
  if (value >= threshold * 0.8) return "text-yellow-400";
  return "text-red-400";
};

export default function PersonaPerformancePanel({
  personas,
  selectedPersona,
}: PersonaPerformancePanelProps) {
  const [timeRange, setTimeRange] = useState<string>("24h");
  const [sortBy, setSortBy] = useState<string>("compliance");

  const sortedPersonas = [...personas].sort((a, b) => {
    switch (sortBy) {
      case "compliance":
        return b.compliance_score - a.compliance_score;
      case "interactions":
        return (b.metrics?.total_interactions || 0) - (a.metrics?.total_interactions || 0);
      case "response_time":
        return (a.metrics?.average_response_time_ms || 0) - (b.metrics?.average_response_time_ms || 0);
      case "success_rate":
        const aRate = a.metrics?.total_interactions
          ? (a.metrics.successful_interactions / a.metrics.total_interactions) * 100
          : 0;
        const bRate = b.metrics?.total_interactions
          ? (b.metrics.successful_interactions / b.metrics.total_interactions) * 100
          : 0;
        return bRate - aRate;
      default:
        return 0;
    }
  });

  const overallStats = {
    totalInteractions: personas.reduce(
      (sum, p) => sum + (p.metrics?.total_interactions || 0),
      0
    ),
    avgCompliance:
      personas.length > 0
        ? personas.reduce((sum, p) => sum + p.compliance_score, 0) / personas.length
        : 0,
    avgResponseTime:
      personas.length > 0
        ? personas.reduce(
            (sum, p) => sum + (p.metrics?.average_response_time_ms || 0),
            0
          ) / personas.length
        : 0,
    totalMissionsCompleted: personas.reduce(
      (sum, p) => sum + (p.metrics?.missions_completed || 0),
      0
    ),
  };

  return (
    <div className="h-full overflow-y-auto bg-gray-900 p-4">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">
            Performance Dashboard
          </h2>
          <div className="flex space-x-2">
            {["24h", "7d", "30d", "all"].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 rounded text-sm ${
                  timeRange === range
                    ? "bg-blue-600 text-white"
                    : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Total Interactions</div>
            <div className="text-2xl font-bold text-white">
              {overallStats.totalInteractions.toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Avg Compliance</div>
            <div
              className={`text-2xl font-bold ${getPerformanceColor(
                overallStats.avgCompliance,
                100
              )}`}
            >
              {overallStats.avgCompliance.toFixed(1)}%
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Avg Response Time</div>
            <div className="text-2xl font-bold text-white">
              {overallStats.avgResponseTime.toFixed(0)}ms
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Missions Completed</div>
            <div className="text-2xl font-bold text-green-400">
              {overallStats.totalMissionsCompleted}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">
            Persona Performance Rankings
          </h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white"
            >
              <option value="compliance">Compliance Score</option>
              <option value="interactions">Total Interactions</option>
              <option value="response_time">Response Time</option>
              <option value="success_rate">Success Rate</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
                <th className="pb-3 pr-4">Rank</th>
                <th className="pb-3 pr-4">Persona</th>
                <th className="pb-3 pr-4">Type</th>
                <th className="pb-3 pr-4">Status</th>
                <th className="pb-3 pr-4">Compliance</th>
                <th className="pb-3 pr-4">Interactions</th>
                <th className="pb-3 pr-4">Success Rate</th>
                <th className="pb-3 pr-4">Avg Response</th>
                <th className="pb-3">Missions</th>
              </tr>
            </thead>
            <tbody>
              {sortedPersonas.map((persona, index) => {
                const successRate = persona.metrics?.total_interactions
                  ? (persona.metrics.successful_interactions /
                      persona.metrics.total_interactions) *
                    100
                  : 0;

                return (
                  <tr
                    key={persona.persona_id}
                    className={`border-b border-gray-700/50 ${
                      selectedPersona?.persona_id === persona.persona_id
                        ? "bg-blue-900/30"
                        : ""
                    }`}
                  >
                    <td className="py-3 pr-4">
                      <span
                        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                          index === 0
                            ? "bg-yellow-500 text-yellow-900"
                            : index === 1
                            ? "bg-gray-400 text-gray-900"
                            : index === 2
                            ? "bg-orange-600 text-orange-100"
                            : "bg-gray-700 text-gray-300"
                        }`}
                      >
                        {index + 1}
                      </span>
                    </td>
                    <td className="py-3 pr-4">
                      <div className="font-medium text-white">{persona.name}</div>
                      <div className="text-xs text-gray-500">{persona.role}</div>
                    </td>
                    <td className="py-3 pr-4">
                      <span className="text-sm text-gray-300 capitalize">
                        {persona.persona_type.replace("apex_", "")}
                      </span>
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`px-2 py-0.5 rounded text-xs capitalize ${
                          persona.status === "active"
                            ? "bg-green-600 text-green-100"
                            : persona.status === "busy"
                            ? "bg-blue-600 text-blue-100"
                            : "bg-gray-600 text-gray-100"
                        }`}
                      >
                        {persona.status}
                      </span>
                    </td>
                    <td className="py-3 pr-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-700 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              persona.compliance_score >= 95
                                ? "bg-green-500"
                                : persona.compliance_score >= 80
                                ? "bg-yellow-500"
                                : "bg-red-500"
                            }`}
                            style={{ width: `${persona.compliance_score}%` }}
                          ></div>
                        </div>
                        <span
                          className={`text-sm ${getPerformanceColor(
                            persona.compliance_score,
                            100
                          )}`}
                        >
                          {persona.compliance_score}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 pr-4 text-sm text-gray-300">
                      {(persona.metrics?.total_interactions || 0).toLocaleString()}
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`text-sm ${getPerformanceColor(
                          successRate,
                          100
                        )}`}
                      >
                        {successRate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-sm text-gray-300">
                      {(persona.metrics?.average_response_time_ms || 0).toFixed(0)}ms
                    </td>
                    <td className="py-3">
                      <span className="text-sm text-green-400">
                        {persona.metrics?.missions_completed || 0}
                      </span>
                      <span className="text-gray-500 mx-1">/</span>
                      <span className="text-sm text-red-400">
                        {persona.metrics?.missions_failed || 0}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {personas.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No persona data available
          </div>
        )}
      </div>
    </div>
  );
}

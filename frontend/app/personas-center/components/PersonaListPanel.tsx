"use client";

import React from "react";

interface Persona {
  persona_id: string;
  name: string;
  persona_type: string;
  role: string;
  status: string;
  emotional_state: string;
  compliance_score: number;
}

interface PersonaListPanelProps {
  personas: Persona[];
  selectedPersona: Persona | null;
  onSelectPersona: (persona: Persona) => void;
  loading: boolean;
}

const getPersonaTypeIcon = (type: string): string => {
  const icons: Record<string, string> = {
    apex_patrol: "🚔",
    apex_command: "⭐",
    apex_intel: "🔍",
    apex_crisis: "🤝",
    apex_robotics: "🤖",
    apex_investigations: "🔎",
  };
  return icons[type] || "👤";
};

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    active: "bg-green-500",
    standby: "bg-yellow-500",
    busy: "bg-blue-500",
    maintenance: "bg-orange-500",
    offline: "bg-gray-500",
    suspended: "bg-red-500",
  };
  return colors[status] || "bg-gray-500";
};

const getComplianceColor = (score: number): string => {
  if (score >= 95) return "text-green-400";
  if (score >= 85) return "text-yellow-400";
  if (score >= 70) return "text-orange-400";
  return "text-red-400";
};

export default function PersonaListPanel({
  personas,
  selectedPersona,
  onSelectPersona,
  loading,
}: PersonaListPanelProps) {
  const groupedPersonas = personas.reduce((acc, persona) => {
    const type = persona.persona_type;
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(persona);
    return acc;
  }, {} as Record<string, Persona[]>);

  const typeLabels: Record<string, string> = {
    apex_patrol: "Patrol Officers",
    apex_command: "Command Advisors",
    apex_intel: "Intel Analysts",
    apex_crisis: "Crisis Counselors",
    apex_robotics: "Robotics Coordinators",
    apex_investigations: "Investigation Detectives",
  };

  if (loading) {
    return (
      <div className="p-4">
        <h2 className="text-lg font-semibold text-gray-200 mb-4">
          Apex AI Officers
        </h2>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-gray-700 rounded-lg p-4 animate-pulse"
            >
              <div className="h-4 bg-gray-600 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-600 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold text-gray-200 mb-4">
        Apex AI Officers
      </h2>

      <div className="mb-4">
        <div className="flex items-center justify-between text-sm text-gray-400 mb-2">
          <span>Total: {personas.length}</span>
          <span>
            Active: {personas.filter((p) => p.status === "active").length}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {Object.entries(groupedPersonas).map(([type, typePersonas]) => (
          <div key={type}>
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
              {getPersonaTypeIcon(type)} {typeLabels[type] || type}
            </h3>
            <div className="space-y-2">
              {typePersonas.map((persona) => (
                <button
                  key={persona.persona_id}
                  onClick={() => onSelectPersona(persona)}
                  className={`w-full text-left p-3 rounded-lg transition-all ${
                    selectedPersona?.persona_id === persona.persona_id
                      ? "bg-blue-600 border border-blue-500"
                      : "bg-gray-700 hover:bg-gray-650 border border-transparent"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xl">
                        {getPersonaTypeIcon(persona.persona_type)}
                      </span>
                      <div>
                        <div className="font-medium text-white">
                          {persona.name}
                        </div>
                        <div className="text-xs text-gray-400">
                          {persona.role}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      <span
                        className={`w-2 h-2 rounded-full ${getStatusColor(
                          persona.status
                        )}`}
                      ></span>
                      <span
                        className={`text-xs ${getComplianceColor(
                          persona.compliance_score
                        )}`}
                      >
                        {persona.compliance_score}%
                      </span>
                    </div>
                  </div>

                  <div className="mt-2 flex items-center justify-between text-xs">
                    <span className="text-gray-400 capitalize">
                      {persona.status}
                    </span>
                    <span className="text-gray-500 capitalize">
                      {persona.emotional_state}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {personas.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No personas available</p>
        </div>
      )}
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import PersonaListPanel from "./components/PersonaListPanel";
import PersonaChatConsole from "./components/PersonaChatConsole";
import MissionBoard from "./components/MissionBoard";
import DecisionTraceViewer from "./components/DecisionTraceViewer";
import PersonaPerformancePanel from "./components/PersonaPerformancePanel";
import SupervisorOverridePanel from "./components/SupervisorOverridePanel";

interface Persona {
  persona_id: string;
  name: string;
  persona_type: string;
  role: string;
  status: string;
  emotional_state: string;
  compliance_score: number;
}

interface Mission {
  mission_id: string;
  title: string;
  description: string;
  mission_type: string;
  status: string;
  priority: string;
  created_by: string;
  assigned_personas: string[];
  tasks: Array<{
    task_id: string;
    task_type: string;
    description: string;
    status: string;
    sequence_number: number;
  }>;
  progress: {
    completion_percentage: number;
    total_tasks: number;
    completed: number;
    in_progress: number;
    failed: number;
  };
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export default function PersonasCenterPage() {
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null);
  const [activeTab, setActiveTab] = useState<string>("chat");
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPersonas();
    fetchMissions();
    const interval = setInterval(() => {
      fetchPersonas();
      fetchMissions();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchPersonas = async () => {
    try {
      const response = await fetch("/api/personas");
      if (response.ok) {
        const data = await response.json();
        setPersonas(data.personas || []);
      }
    } catch (error) {
      console.error("Failed to fetch personas:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMissions = async () => {
    try {
      const response = await fetch("/api/missions");
      if (response.ok) {
        const data = await response.json();
        setMissions(data.missions || []);
      }
    } catch (error) {
      console.error("Failed to fetch missions:", error);
    }
  };

  const handlePersonaSelect = (persona: Persona) => {
    setSelectedPersona(persona);
    setActiveTab("chat");
  };

  const handleMissionSelect = (mission: Mission) => {
    setSelectedMission(mission);
    setActiveTab("missions");
  };

  const tabs = [
    { id: "chat", label: "Chat Console", icon: "💬" },
    { id: "missions", label: "Mission Board", icon: "🎯" },
    { id: "decisions", label: "Decision Trace", icon: "🔍" },
    { id: "performance", label: "Performance", icon: "📊" },
    { id: "override", label: "Supervisor Override", icon: "⚡" },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">
              AI Persona Operations Center
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Apex AI Officers - Phase 34
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm text-gray-300">
                {personas.filter((p) => p.status === "active").length} Active
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
              <span className="text-sm text-gray-300">
                {missions.filter((m) => m.status === "in_progress").length} Missions
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-80px)]">
        <aside className="w-80 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <PersonaListPanel
            personas={personas}
            selectedPersona={selectedPersona}
            onSelectPersona={handlePersonaSelect}
            loading={loading}
          />
        </aside>

        <main className="flex-1 flex flex-col overflow-hidden">
          <nav className="bg-gray-800 border-b border-gray-700 px-4">
            <div className="flex space-x-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? "text-blue-400 border-b-2 border-blue-400"
                      : "text-gray-400 hover:text-gray-200"
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>
          </nav>

          <div className="flex-1 overflow-hidden">
            {activeTab === "chat" && (
              <PersonaChatConsole
                persona={selectedPersona}
                onPersonaSelect={handlePersonaSelect}
              />
            )}
            {activeTab === "missions" && (
              <MissionBoard
                missions={missions}
                selectedMission={selectedMission}
                onMissionSelect={handleMissionSelect}
                onRefresh={fetchMissions}
              />
            )}
            {activeTab === "decisions" && (
              <DecisionTraceViewer
                persona={selectedPersona}
                mission={selectedMission}
              />
            )}
            {activeTab === "performance" && (
              <PersonaPerformancePanel
                personas={personas}
                selectedPersona={selectedPersona}
              />
            )}
            {activeTab === "override" && (
              <SupervisorOverridePanel
                personas={personas}
                missions={missions}
                onRefresh={() => {
                  fetchPersonas();
                  fetchMissions();
                }}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

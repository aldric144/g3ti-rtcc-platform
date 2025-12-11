"use client";

import React, { useState } from "react";
import AutonomyCommandConsole from "./components/AutonomyCommandConsole";
import PolicyEngineManager from "./components/PolicyEngineManager";
import CityStabilizationDashboard from "./components/CityStabilizationDashboard";
import AutonomyAuditCenter from "./components/AutonomyAuditCenter";

type TabType = "command" | "policy" | "stabilization" | "audit";

interface TabConfig {
  id: TabType;
  label: string;
  description: string;
}

const tabs: TabConfig[] = [
  {
    id: "command",
    label: "Autonomy Command Console",
    description: "Manage pending actions, approvals, and view action explainability",
  },
  {
    id: "policy",
    label: "Policy Engine Manager",
    description: "Configure city operation policies, rules, and emergency overrides",
  },
  {
    id: "stabilization",
    label: "City Stabilization",
    description: "Monitor anomalies, cascade predictions, and stabilization actions",
  },
  {
    id: "audit",
    label: "Autonomy Audit Center",
    description: "View audit trails, compliance reports, and chain of custody",
  },
];

export default function AICityAutonomyPage() {
  const [activeTab, setActiveTab] = useState<TabType>("command");
  const [systemMode, setSystemMode] = useState<"autonomous" | "manual">("autonomous");

  const handleModeToggle = async () => {
    const newMode = systemMode === "autonomous" ? "manual" : "autonomous";
    setSystemMode(newMode);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "command":
        return <AutonomyCommandConsole />;
      case "policy":
        return <PolicyEngineManager />;
      case "stabilization":
        return <CityStabilizationDashboard />;
      case "audit":
        return <AutonomyAuditCenter />;
      default:
        return <AutonomyCommandConsole />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">
              AI City Autonomy - Level 2
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Riviera Beach Autonomous City Operations
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-400">System Mode:</span>
              <button
                onClick={handleModeToggle}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  systemMode === "autonomous"
                    ? "bg-green-600 hover:bg-green-700 text-white"
                    : "bg-yellow-600 hover:bg-yellow-700 text-white"
                }`}
              >
                {systemMode === "autonomous" ? "AUTONOMOUS" : "MANUAL"}
              </button>
            </div>
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  systemMode === "autonomous" ? "bg-green-500" : "bg-yellow-500"
                } animate-pulse`}
              />
              <span className="text-sm text-gray-300">
                {systemMode === "autonomous"
                  ? "Auto-executing Level 1 actions"
                  : "All actions require approval"}
              </span>
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-4 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-400 bg-gray-700/50"
                  : "border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-700/30"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">{renderTabContent()}</main>
    </div>
  );
}

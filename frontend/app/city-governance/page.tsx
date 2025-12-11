"use client";

import React, { useState } from "react";
import CityOperationsDashboard from "./components/CityOperationsDashboard";
import ResourceOptimizationPanel from "./components/ResourceOptimizationPanel";
import ScenarioSimulator from "./components/ScenarioSimulator";
import GovernanceKPIDashboard from "./components/GovernanceKPIDashboard";

type TabType = "operations" | "optimization" | "scenarios" | "kpi";

export default function CityGovernancePage() {
  const [activeTab, setActiveTab] = useState<TabType>("operations");

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "operations", label: "City Operations", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
    { id: "optimization", label: "Resource Optimization", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
    { id: "scenarios", label: "Scenario Simulator", icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" },
    { id: "kpi", label: "KPI Dashboard", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "operations":
        return <CityOperationsDashboard />;
      case "optimization":
        return <ResourceOptimizationPanel />;
      case "scenarios":
        return <ScenarioSimulator />;
      case "kpi":
        return <GovernanceKPIDashboard />;
      default:
        return <CityOperationsDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">
              AI City Governance Engine
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Riviera Beach Operations Co-Pilot - Phase 23
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-300">System Active</span>
            </div>
            <div className="text-sm text-gray-400">
              {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="flex space-x-1 px-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "text-blue-400 border-b-2 border-blue-400 bg-gray-700/50"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/30"
              }`}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d={tab.icon}
                />
              </svg>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">{renderTabContent()}</main>

      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>G3TI RTCC-UIP Platform - City Governance Module</span>
          <span>Riviera Beach, FL 33404</span>
        </div>
      </footer>
    </div>
  );
}

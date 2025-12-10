"use client";

import React, { useState } from "react";
import RoboticsFleetPanel from "./components/RoboticsFleetPanel";
import RoboticsLiveFeedPanel from "./components/RoboticsLiveFeedPanel";
import MissionPlannerUI from "./components/MissionPlannerUI";
import SwarmControlUI from "./components/SwarmControlUI";
import PerimeterBreachMap from "./components/PerimeterBreachMap";
import RoboticsHealthPanel from "./components/RoboticsHealthPanel";
import PatrolPatternEditor from "./components/PatrolPatternEditor";

type TabType = "fleet" | "live" | "missions" | "swarms" | "perimeter" | "health" | "patterns";

const TABS: { id: TabType; label: string; icon: string }[] = [
  { id: "fleet", label: "Fleet", icon: "🤖" },
  { id: "live", label: "Live Feed", icon: "📡" },
  { id: "missions", label: "Missions", icon: "🎯" },
  { id: "swarms", label: "Swarms", icon: "🐝" },
  { id: "perimeter", label: "Perimeter", icon: "🛡️" },
  { id: "health", label: "Health", icon: "🔧" },
  { id: "patterns", label: "Patterns", icon: "🗺️" },
];

export default function RoboticsOperationsPage() {
  const [activeTab, setActiveTab] = useState<TabType>("fleet");
  const [isConnected, setIsConnected] = useState(true);

  const renderTabContent = () => {
    switch (activeTab) {
      case "fleet":
        return <RoboticsFleetPanel />;
      case "live":
        return <RoboticsLiveFeedPanel />;
      case "missions":
        return <MissionPlannerUI />;
      case "swarms":
        return <SwarmControlUI />;
      case "perimeter":
        return <PerimeterBreachMap />;
      case "health":
        return <RoboticsHealthPanel />;
      case "patterns":
        return <PatrolPatternEditor />;
      default:
        return <RoboticsFleetPanel />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Autonomous Tactical Robotics Engine</h1>
            <p className="text-gray-400 text-sm">Phase 19 - ATRE Operations Center</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-500 animate-pulse" : "bg-red-500"}`}></div>
              <span className="text-sm text-gray-400">{isConnected ? "Connected" : "Disconnected"}</span>
            </div>
            <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-medium">
              Emergency Stop All
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        <nav className="w-48 bg-gray-800 min-h-[calc(100vh-80px)] border-r border-gray-700">
          <div className="p-4 space-y-2">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all ${
                  activeTab === tab.id
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:bg-gray-700 hover:text-white"
                }`}
              >
                <span className="text-xl">{tab.icon}</span>
                <span className="text-sm font-medium">{tab.label}</span>
              </button>
            ))}
          </div>

          <div className="p-4 border-t border-gray-700 mt-4">
            <h3 className="text-gray-500 text-xs font-medium uppercase mb-3">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Active Robots</span>
                <span className="text-green-500 font-medium">4</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Active Missions</span>
                <span className="text-blue-500 font-medium">2</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Active Swarms</span>
                <span className="text-purple-500 font-medium">1</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Breaches</span>
                <span className="text-red-500 font-medium">2</span>
              </div>
            </div>
          </div>

          <div className="p-4 border-t border-gray-700">
            <h3 className="text-gray-500 text-xs font-medium uppercase mb-3">System Health</h3>
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">Fleet Health</span>
                  <span className="text-green-500">92%</span>
                </div>
                <div className="bg-gray-700 rounded-full h-1.5">
                  <div className="bg-green-500 h-1.5 rounded-full" style={{ width: "92%" }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">Network</span>
                  <span className="text-green-500">98%</span>
                </div>
                <div className="bg-gray-700 rounded-full h-1.5">
                  <div className="bg-green-500 h-1.5 rounded-full" style={{ width: "98%" }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">Sensors</span>
                  <span className="text-yellow-500">85%</span>
                </div>
                <div className="bg-gray-700 rounded-full h-1.5">
                  <div className="bg-yellow-500 h-1.5 rounded-full" style={{ width: "85%" }}></div>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <main className="flex-1 p-6">
          {renderTabContent()}
        </main>
      </div>

      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
        <div className="flex justify-between items-center text-sm text-gray-400">
          <div className="flex items-center gap-4">
            <span>G3TI RTCC-UIP v19.0</span>
            <span>|</span>
            <span>ATRE Module</span>
          </div>
          <div className="flex items-center gap-4">
            <span>Last Sync: {new Date().toLocaleTimeString()}</span>
            <span>|</span>
            <span>WebSocket: {isConnected ? "Active" : "Inactive"}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

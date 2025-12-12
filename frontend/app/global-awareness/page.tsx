"use client";

import React, { useState, useEffect } from "react";
import WorldMapDashboard from "./components/WorldMapDashboard";
import RiskFusionDashboard from "./components/RiskFusionDashboard";
import SatellitePanel from "./components/SatellitePanel";
import CyberThreatPanel from "./components/CyberThreatPanel";
import EventCorrelationPanel from "./components/EventCorrelationPanel";

type TabType = "world-map" | "risk-fusion" | "satellite" | "cyber" | "events";

interface TabConfig {
  id: TabType;
  label: string;
  description: string;
}

const tabs: TabConfig[] = [
  {
    id: "world-map",
    label: "World Map",
    description: "Global situation overview with real-time signals",
  },
  {
    id: "risk-fusion",
    label: "Risk Fusion",
    description: "Multi-domain risk assessment and forecasting",
  },
  {
    id: "satellite",
    label: "Satellite Analysis",
    description: "AI-powered satellite imagery analysis",
  },
  {
    id: "cyber",
    label: "Cyber Intelligence",
    description: "Global cyber threat monitoring",
  },
  {
    id: "events",
    label: "Event Correlation",
    description: "Cause-effect cascade modeling",
  },
];

export default function GlobalAwarenessPage() {
  const [activeTab, setActiveTab] = useState<TabType>("world-map");
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      setIsConnected(true);
      setLastUpdate(new Date());
    };

    connectWebSocket();

    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 30000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  const renderActivePanel = () => {
    switch (activeTab) {
      case "world-map":
        return <WorldMapDashboard />;
      case "risk-fusion":
        return <RiskFusionDashboard />;
      case "satellite":
        return <SatellitePanel />;
      case "cyber":
        return <CyberThreatPanel />;
      case "events":
        return <EventCorrelationPanel />;
      default:
        return <WorldMapDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">
              Global Situation Awareness Engine
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Phase 32: Multi-Domain Intelligence Fusion
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  isConnected ? "bg-green-500" : "bg-red-500"
                }`}
              />
              <span className="text-sm text-gray-400">
                {isConnected ? "Connected" : "Disconnected"}
              </span>
            </div>
            {lastUpdate && (
              <span className="text-sm text-gray-500">
                Last update: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="flex space-x-1 px-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "text-blue-400 border-b-2 border-blue-400 bg-gray-700/50"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/30"
              }`}
              title={tab.description}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">{renderActivePanel()}</main>

      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>G3TI RTCC-UIP | Global Situation Awareness Engine v32.0</span>
          <span>
            Data Sources: GDACS, ReliefWeb, ACLED, AIS, ADS-B, Threat Intel, CVE
          </span>
        </div>
      </footer>
    </div>
  );
}

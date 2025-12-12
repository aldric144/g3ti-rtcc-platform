"use client";

import React, { useState } from "react";
import SentinelOverviewPanel from "./components/SentinelOverviewPanel";
import EthicsViolationFeed from "./components/EthicsViolationFeed";
import SystemLoadHeatmap from "./components/SystemLoadHeatmap";
import RecommendationConsole from "./components/RecommendationConsole";
import AutoCorrectionTimeline from "./components/AutoCorrectionTimeline";
import SupervisorControlPanel from "./components/SupervisorControlPanel";

type TabType = "overview" | "ethics" | "system-load" | "recommendations" | "corrections" | "control";

export default function SupervisorConsolePage() {
  const [activeTab, setActiveTab] = useState<TabType>("overview");

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "overview", label: "Sentinel Overview", icon: "shield" },
    { id: "ethics", label: "Ethics Violations", icon: "scale" },
    { id: "system-load", label: "System Load", icon: "activity" },
    { id: "recommendations", label: "Recommendations", icon: "lightbulb" },
    { id: "corrections", label: "Auto-Corrections", icon: "wrench" },
    { id: "control", label: "Control Panel", icon: "settings" },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "overview":
        return <SentinelOverviewPanel />;
      case "ethics":
        return <EthicsViolationFeed />;
      case "system-load":
        return <SystemLoadHeatmap />;
      case "recommendations":
        return <RecommendationConsole />;
      case "corrections":
        return <AutoCorrectionTimeline />;
      case "control":
        return <SupervisorControlPanel />;
      default:
        return <SentinelOverviewPanel />;
    }
  };

  const getIconSvg = (icon: string) => {
    switch (icon) {
      case "shield":
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        );
      case "scale":
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
          </svg>
        );
      case "activity":
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        );
      case "lightbulb":
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      case "wrench":
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        );
      case "settings":
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-purple-600 rounded-lg">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold">AI Sentinel Supervisor</h1>
              <p className="text-gray-400 text-sm">System-Wide Oversight & Ethical Governance</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-4 py-2 bg-green-900/50 rounded-lg border border-green-700">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-400 font-medium">System Active</span>
            </div>
            <div className="text-gray-400 text-sm">
              Phase 33 | RTCC-UIP
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800/50 border-b border-gray-700">
        <div className="flex space-x-1 px-6 py-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? "bg-purple-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-700"
              }`}
            >
              {getIconSvg(tab.icon)}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">
        {renderTabContent()}
      </main>

      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div>G3TI RTCC-UIP | AI Sentinel Supervisor v33.0</div>
          <div className="flex items-center space-x-4">
            <span>Constitutional Compliance: Active</span>
            <span>|</span>
            <span>Ethics Guard: Enabled</span>
            <span>|</span>
            <span>Auto-Correction: Ready</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

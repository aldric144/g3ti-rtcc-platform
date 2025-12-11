"use client";

import React, { useState } from "react";
import BiasMonitorConsole from "./components/BiasMonitorConsole";
import CivilRightsCompliancePanel from "./components/CivilRightsCompliancePanel";
import EthicsScoreDashboard from "./components/EthicsScoreDashboard";
import ProtectedCommunitiesViewer from "./components/ProtectedCommunitiesViewer";
import EthicsAuditCenter from "./components/EthicsAuditCenter";

type TabType = "bias" | "civil-rights" | "ethics-score" | "communities" | "audit";

const tabs: { id: TabType; label: string; icon: string }[] = [
  {
    id: "bias",
    label: "Bias Monitor",
    icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  },
  {
    id: "civil-rights",
    label: "Civil Rights",
    icon: "M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3",
  },
  {
    id: "ethics-score",
    label: "Ethics Score",
    icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
  },
  {
    id: "communities",
    label: "Protected Communities",
    icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z",
  },
  {
    id: "audit",
    label: "Ethics Audit",
    icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01",
  },
];

export default function EthicsCenterPage() {
  const [activeTab, setActiveTab] = useState<TabType>("bias");

  const renderTabContent = () => {
    switch (activeTab) {
      case "bias":
        return <BiasMonitorConsole />;
      case "civil-rights":
        return <CivilRightsCompliancePanel />;
      case "ethics-score":
        return <EthicsScoreDashboard />;
      case "communities":
        return <ProtectedCommunitiesViewer />;
      case "audit":
        return <EthicsAuditCenter />;
      default:
        return <BiasMonitorConsole />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="border-b border-gray-700 bg-gray-800">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                AI Ethics & Civil Rights Protection Center
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Phase 26: Bias Safeguards & Civil Rights Compliance for Riviera Beach, FL
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                <span className="text-sm text-gray-400">Ethics Guardian Active</span>
              </div>
              <div className="px-3 py-1 bg-blue-600 rounded-lg text-sm">
                NIST AI RMF Compliant
              </div>
            </div>
          </div>
        </div>

        <div className="px-6">
          <nav className="flex space-x-1 overflow-x-auto pb-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-t-lg transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? "bg-gray-900 text-white border-t border-l border-r border-gray-700"
                    : "text-gray-400 hover:text-white hover:bg-gray-700"
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
          </nav>
        </div>
      </div>

      <div className="p-6">{renderTabContent()}</div>
    </div>
  );
}

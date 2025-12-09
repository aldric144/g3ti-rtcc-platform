"use client";

import { useState } from "react";
import { TrendAnalytics } from "./components/TrendAnalytics";
import { HeatmapViewer } from "./components/HeatmapViewer";
import { OffenderAnalytics } from "./components/OffenderAnalytics";
import { DataLakeStats } from "./components/DataLakeStats";

type TabType = "trends" | "heatmaps" | "offenders" | "datalake";

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<TabType>("trends");

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "trends", label: "Trend Analysis", icon: "📈" },
    { id: "heatmaps", label: "Multi-Year Heatmaps", icon: "🗺️" },
    { id: "offenders", label: "Repeat Offenders", icon: "👤" },
    { id: "datalake", label: "Data Lake", icon: "💾" },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-6">
        <header className="mb-6">
          <h1 className="text-3xl font-bold text-blue-400">
            Historical Analytics Dashboard
          </h1>
          <p className="text-gray-400 mt-2">
            Multi-year crime analysis, heatmaps, and repeat offender tracking
          </p>
        </header>

        <nav className="flex space-x-1 mb-6 bg-gray-800 rounded-lg p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-4 py-3 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-700"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>

        <main>
          {activeTab === "trends" && <TrendAnalytics />}
          {activeTab === "heatmaps" && <HeatmapViewer />}
          {activeTab === "offenders" && <OffenderAnalytics />}
          {activeTab === "datalake" && <DataLakeStats />}
        </main>
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import FusionFeed from "./components/FusionFeed";
import PriorityQueue from "./components/PriorityQueue";
import SignalGraphView from "./components/SignalGraphView";
import PipelineStatusView from "./components/PipelineStatusView";
import EntityCorrelationViewer from "./components/EntityCorrelationViewer";
import AutoLeadsPanel from "./components/AutoLeadsPanel";

type TabType = "fusion" | "priority" | "signals" | "pipelines" | "correlations" | "leads";

interface IntelStats {
  signalsProcessed: number;
  fusionsCreated: number;
  alertsRouted: number;
  activeCorrelations: number;
  pipelinesRunning: number;
  leadsGenerated: number;
}

export default function IntelHubPage() {
  const [activeTab, setActiveTab] = useState<TabType>("fusion");
  const [stats, setStats] = useState<IntelStats>({
    signalsProcessed: 0,
    fusionsCreated: 0,
    alertsRouted: 0,
    activeCorrelations: 0,
    pipelinesRunning: 7,
    leadsGenerated: 0,
  });
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setStats((prev) => ({
        signalsProcessed: prev.signalsProcessed + Math.floor(Math.random() * 5),
        fusionsCreated: prev.fusionsCreated + Math.floor(Math.random() * 2),
        alertsRouted: prev.alertsRouted + Math.floor(Math.random() * 3),
        activeCorrelations: Math.floor(Math.random() * 50) + 10,
        pipelinesRunning: 7,
        leadsGenerated: prev.leadsGenerated + Math.floor(Math.random() * 2),
      }));
    }, 3000);

    setIsConnected(true);

    return () => clearInterval(interval);
  }, []);

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "fusion", label: "Fusion Feed", icon: "🔄" },
    { id: "priority", label: "Priority Queue", icon: "⚡" },
    { id: "signals", label: "Signal Graph", icon: "📊" },
    { id: "pipelines", label: "Pipelines", icon: "🔧" },
    { id: "correlations", label: "Correlations", icon: "🔗" },
    { id: "leads", label: "Auto Leads", icon: "🎯" },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Intelligence Orchestration Hub</h1>
            <p className="text-gray-400 text-sm">
              Master fusion layer coordinating all intelligence sources
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div
              className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
                isConnected ? "bg-green-900 text-green-300" : "bg-red-900 text-red-300"
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isConnected ? "bg-green-400 animate-pulse" : "bg-red-400"
                }`}
              />
              {isConnected ? "Connected" : "Disconnected"}
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-6 gap-4 p-6">
        <StatCard
          label="Signals Processed"
          value={stats.signalsProcessed}
          color="blue"
        />
        <StatCard
          label="Fusions Created"
          value={stats.fusionsCreated}
          color="purple"
        />
        <StatCard
          label="Alerts Routed"
          value={stats.alertsRouted}
          color="yellow"
        />
        <StatCard
          label="Active Correlations"
          value={stats.activeCorrelations}
          color="green"
        />
        <StatCard
          label="Pipelines Running"
          value={stats.pipelinesRunning}
          color="cyan"
        />
        <StatCard
          label="Leads Generated"
          value={stats.leadsGenerated}
          color="orange"
        />
      </div>

      <div className="px-6">
        <div className="flex gap-2 border-b border-gray-700">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "text-blue-400 border-b-2 border-blue-400"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <main className="p-6">
        {activeTab === "fusion" && <FusionFeed />}
        {activeTab === "priority" && <PriorityQueue />}
        {activeTab === "signals" && <SignalGraphView />}
        {activeTab === "pipelines" && <PipelineStatusView />}
        {activeTab === "correlations" && <EntityCorrelationViewer />}
        {activeTab === "leads" && <AutoLeadsPanel />}
      </main>
    </div>
  );
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: "bg-blue-900/50 border-blue-700 text-blue-300",
    purple: "bg-purple-900/50 border-purple-700 text-purple-300",
    yellow: "bg-yellow-900/50 border-yellow-700 text-yellow-300",
    green: "bg-green-900/50 border-green-700 text-green-300",
    cyan: "bg-cyan-900/50 border-cyan-700 text-cyan-300",
    orange: "bg-orange-900/50 border-orange-700 text-orange-300",
  };

  return (
    <div className={`rounded-lg border p-4 ${colorClasses[color]}`}>
      <div className="text-2xl font-bold">{value.toLocaleString()}</div>
      <div className="text-sm opacity-80">{label}</div>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import HealthGrid from "./components/HealthGrid";
import ServiceLatencyPanel from "./components/ServiceLatencyPanel";
import FailoverStatusCard from "./components/FailoverStatusCard";
import VendorIntegrationMap from "./components/VendorIntegrationMap";
import DiagnosticsTimeline from "./components/DiagnosticsTimeline";
import UptimeAnalytics from "./components/UptimeAnalytics";
import OpsAlertsFeed from "./components/OpsAlertsFeed";

interface OpsMetrics {
  servicesMonitored: number;
  healthyServices: number;
  activeFailovers: number;
  avgLatencyMs: number;
  uptimePercent: number;
  alertsToday: number;
}

export default function OperationsCenterPage() {
  const [activeTab, setActiveTab] = useState("health");
  const [metrics, setMetrics] = useState<OpsMetrics>({
    servicesMonitored: 24,
    healthyServices: 22,
    activeFailovers: 0,
    avgLatencyMs: 45,
    uptimePercent: 99.97,
    alertsToday: 3,
  });
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        avgLatencyMs: Math.max(20, prev.avgLatencyMs + (Math.random() - 0.5) * 10),
        alertsToday: prev.alertsToday + (Math.random() > 0.95 ? 1 : 0),
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: "health", label: "Health Grid" },
    { id: "latency", label: "Latency" },
    { id: "failover", label: "Failover" },
    { id: "vendors", label: "Vendors" },
    { id: "diagnostics", label: "Diagnostics" },
    { id: "uptime", label: "Uptime" },
    { id: "alerts", label: "Alerts" },
  ];

  const getStatusColor = (healthy: number, total: number) => {
    const ratio = healthy / total;
    if (ratio >= 0.95) return "bg-green-500";
    if (ratio >= 0.8) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">Operations Center</h1>
            <p className="text-gray-400 mt-1">
              24/7 RTCC Operational Continuity Monitoring
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  isConnected ? "bg-green-500 animate-pulse" : "bg-red-500"
                }`}
              />
              <span className="text-sm text-gray-400">
                {isConnected ? "Live" : "Disconnected"}
              </span>
            </div>
            <div className="text-sm text-gray-400">
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400">Services Monitored</div>
            <div className="text-2xl font-bold text-blue-400">
              {metrics.servicesMonitored}
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400">Healthy Services</div>
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold text-green-400">
                {metrics.healthyServices}
              </div>
              <div
                className={`w-2 h-2 rounded-full ${getStatusColor(
                  metrics.healthyServices,
                  metrics.servicesMonitored
                )}`}
              />
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400">Active Failovers</div>
            <div
              className={`text-2xl font-bold ${
                metrics.activeFailovers > 0 ? "text-yellow-400" : "text-green-400"
              }`}
            >
              {metrics.activeFailovers}
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400">Avg Latency</div>
            <div
              className={`text-2xl font-bold ${
                metrics.avgLatencyMs > 100
                  ? "text-yellow-400"
                  : "text-green-400"
              }`}
            >
              {metrics.avgLatencyMs.toFixed(0)}ms
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400">Uptime (24h)</div>
            <div
              className={`text-2xl font-bold ${
                metrics.uptimePercent >= 99.9
                  ? "text-green-400"
                  : metrics.uptimePercent >= 99
                  ? "text-yellow-400"
                  : "text-red-400"
              }`}
            >
              {metrics.uptimePercent.toFixed(2)}%
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400">Alerts Today</div>
            <div
              className={`text-2xl font-bold ${
                metrics.alertsToday > 10
                  ? "text-red-400"
                  : metrics.alertsToday > 5
                  ? "text-yellow-400"
                  : "text-blue-400"
              }`}
            >
              {metrics.alertsToday}
            </div>
          </div>
        </div>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          {activeTab === "health" && <HealthGrid />}
          {activeTab === "latency" && <ServiceLatencyPanel />}
          {activeTab === "failover" && <FailoverStatusCard />}
          {activeTab === "vendors" && <VendorIntegrationMap />}
          {activeTab === "diagnostics" && <DiagnosticsTimeline />}
          {activeTab === "uptime" && <UptimeAnalytics />}
          {activeTab === "alerts" && <OpsAlertsFeed />}
        </div>
      </div>
    </div>
  );
}

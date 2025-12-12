"use client";

import React, { useState, useEffect } from "react";

interface DashboardSummary {
  active_alerts: number;
  p1_critical_alerts: number;
  p2_high_alerts: number;
  pending_action_requests: number;
  pending_recommendations: number;
  unacknowledged_command_alerts: number;
  cascade_predictions_active: number;
  system_status: string;
  timestamp: string;
}

interface SystemHealth {
  overall_status: string;
  total_engines: number;
  healthy_count: number;
  degraded_count: number;
  warning_count: number;
  critical_count: number;
  offline_count: number;
  average_cpu_percent: number;
  average_memory_percent: number;
  average_latency_ms: number;
  active_alerts: number;
  critical_alerts: number;
}

interface Alert {
  alert_id: string;
  priority: number;
  title: string;
  description: string;
  sources: string[];
  affected_systems: string[];
  recommended_actions: string[];
  acknowledged: boolean;
  timestamp: string;
}

export default function SentinelOverviewPanel() {
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockDashboard: DashboardSummary = {
      active_alerts: 5,
      p1_critical_alerts: 1,
      p2_high_alerts: 2,
      pending_action_requests: 3,
      pending_recommendations: 4,
      unacknowledged_command_alerts: 2,
      cascade_predictions_active: 1,
      system_status: "WARNING",
      timestamp: new Date().toISOString(),
    };

    const mockHealth: SystemHealth = {
      overall_status: "WARNING",
      total_engines: 16,
      healthy_count: 12,
      degraded_count: 2,
      warning_count: 1,
      critical_count: 1,
      offline_count: 0,
      average_cpu_percent: 45.5,
      average_memory_percent: 62.3,
      average_latency_ms: 125.8,
      active_alerts: 5,
      critical_alerts: 1,
    };

    const mockAlerts: Alert[] = [
      {
        alert_id: "CON-A1B2C3D4",
        priority: 1,
        title: "Critical CPU Overload on Predictive AI Engine",
        description: "CPU usage at 95% on predictive_ai engine",
        sources: ["system_monitor"],
        affected_systems: ["predictive_ai", "intel_engine"],
        recommended_actions: ["Scale up compute resources", "Enable auto-scaling"],
        acknowledged: false,
        timestamp: new Date().toISOString(),
      },
      {
        alert_id: "CON-E5F6G7H8",
        priority: 2,
        title: "High Memory Usage on City Brain",
        description: "Memory usage at 88% on city_brain engine",
        sources: ["system_monitor", "auto_corrector"],
        affected_systems: ["city_brain"],
        recommended_actions: ["Clear caches", "Restart service if needed"],
        acknowledged: true,
        timestamp: new Date(Date.now() - 300000).toISOString(),
      },
    ];

    setDashboard(mockDashboard);
    setHealth(mockHealth);
    setAlerts(mockAlerts);
    setLoading(false);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "HEALTHY":
      case "NORMAL":
        return "text-green-400 bg-green-900/30 border-green-700";
      case "DEGRADED":
        return "text-yellow-400 bg-yellow-900/30 border-yellow-700";
      case "WARNING":
        return "text-orange-400 bg-orange-900/30 border-orange-700";
      case "CRITICAL":
        return "text-red-400 bg-red-900/30 border-red-700";
      default:
        return "text-gray-400 bg-gray-900/30 border-gray-700";
    }
  };

  const getPriorityBadge = (priority: number) => {
    switch (priority) {
      case 1:
        return <span className="px-2 py-1 text-xs font-bold bg-red-600 text-white rounded">P1 CRITICAL</span>;
      case 2:
        return <span className="px-2 py-1 text-xs font-bold bg-orange-600 text-white rounded">P2 HIGH</span>;
      case 3:
        return <span className="px-2 py-1 text-xs font-bold bg-yellow-600 text-white rounded">P3 MEDIUM</span>;
      case 4:
        return <span className="px-2 py-1 text-xs font-bold bg-blue-600 text-white rounded">P4 LOW</span>;
      default:
        return <span className="px-2 py-1 text-xs font-bold bg-gray-600 text-white rounded">P5 INFO</span>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg border ${getStatusColor(dashboard?.system_status || "")}`}>
          <div className="text-sm opacity-75">System Status</div>
          <div className="text-2xl font-bold">{dashboard?.system_status}</div>
          <div className="text-xs mt-1">{dashboard?.active_alerts} active alerts</div>
        </div>

        <div className="p-4 rounded-lg border border-red-700 bg-red-900/30">
          <div className="text-sm text-red-400">Critical Alerts</div>
          <div className="text-2xl font-bold text-red-400">{dashboard?.p1_critical_alerts}</div>
          <div className="text-xs text-red-400/75 mt-1">Requires immediate attention</div>
        </div>

        <div className="p-4 rounded-lg border border-orange-700 bg-orange-900/30">
          <div className="text-sm text-orange-400">High Priority</div>
          <div className="text-2xl font-bold text-orange-400">{dashboard?.p2_high_alerts}</div>
          <div className="text-xs text-orange-400/75 mt-1">Action recommended</div>
        </div>

        <div className="p-4 rounded-lg border border-purple-700 bg-purple-900/30">
          <div className="text-sm text-purple-400">Pending Requests</div>
          <div className="text-2xl font-bold text-purple-400">{dashboard?.pending_action_requests}</div>
          <div className="text-xs text-purple-400/75 mt-1">Awaiting approval</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            System Health Overview
          </h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Total Engines</span>
                <span className="font-semibold">{health?.total_engines}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-green-400">Healthy</span>
                <span className="font-semibold text-green-400">{health?.healthy_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-yellow-400">Degraded</span>
                <span className="font-semibold text-yellow-400">{health?.degraded_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-orange-400">Warning</span>
                <span className="font-semibold text-orange-400">{health?.warning_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-red-400">Critical</span>
                <span className="font-semibold text-red-400">{health?.critical_count}</span>
              </div>
            </div>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Avg CPU</span>
                  <span>{health?.average_cpu_percent.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full" 
                    style={{ width: `${health?.average_cpu_percent}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Avg Memory</span>
                  <span>{health?.average_memory_percent.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full" 
                    style={{ width: `${health?.average_memory_percent}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Avg Latency</span>
                  <span>{health?.average_latency_ms.toFixed(0)}ms</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{ width: `${Math.min((health?.average_latency_ms || 0) / 10, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Active Alerts
          </h3>
          
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {alerts.map((alert) => (
              <div 
                key={alert.alert_id}
                className={`p-3 rounded-lg border ${
                  alert.priority === 1 
                    ? "border-red-700 bg-red-900/20" 
                    : alert.priority === 2 
                    ? "border-orange-700 bg-orange-900/20"
                    : "border-gray-700 bg-gray-900/20"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      {getPriorityBadge(alert.priority)}
                      {alert.acknowledged && (
                        <span className="px-2 py-1 text-xs bg-green-900/50 text-green-400 rounded">ACK</span>
                      )}
                    </div>
                    <div className="font-medium text-sm">{alert.title}</div>
                    <div className="text-xs text-gray-400 mt-1">{alert.description}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(alert.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Pending Recommendations</span>
            <span className="text-2xl font-bold text-blue-400">{dashboard?.pending_recommendations}</span>
          </div>
          <div className="text-xs text-gray-500">Sentinel recommendations awaiting review</div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Command Alerts</span>
            <span className="text-2xl font-bold text-yellow-400">{dashboard?.unacknowledged_command_alerts}</span>
          </div>
          <div className="text-xs text-gray-500">Unacknowledged command staff alerts</div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Cascade Predictions</span>
            <span className="text-2xl font-bold text-purple-400">{dashboard?.cascade_predictions_active}</span>
          </div>
          <div className="text-xs text-gray-500">Active cascade outcome predictions</div>
        </div>
      </div>
    </div>
  );
}

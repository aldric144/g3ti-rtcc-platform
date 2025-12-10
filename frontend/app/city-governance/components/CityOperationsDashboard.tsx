"use client";

import React, { useState, useEffect } from "react";

interface Decision {
  decision_id: string;
  domain: string;
  title: string;
  description: string;
  priority: number;
  confidence: string;
  status: string;
  recommended_action: Record<string, unknown>;
  expected_impact: Record<string, unknown>;
  valid_until: string;
}

interface CityAlert {
  id: string;
  type: string;
  message: string;
  severity: "low" | "medium" | "high" | "critical";
  timestamp: string;
  zone: string;
}

interface Forecast {
  hour: number;
  crime_risk: number;
  traffic_level: number;
  resource_demand: number;
}

export default function CityOperationsDashboard() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [cityHealthScore, setCityHealthScore] = useState(87.5);
  const [resourceEfficiency, setResourceEfficiency] = useState(82.3);
  const [alerts, setAlerts] = useState<CityAlert[]>([]);
  const [forecast, setForecast] = useState<Forecast[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockDecisions: Decision[] = [
      {
        decision_id: "dec-001",
        domain: "public_safety",
        title: "Increase Downtown Patrol",
        description: "High crime risk detected in downtown area",
        priority: 3,
        confidence: "high",
        status: "pending",
        recommended_action: { action: "increase_patrol", units: 2 },
        expected_impact: { crime_reduction: 0.15 },
        valid_until: new Date(Date.now() + 4 * 3600000).toISOString(),
      },
      {
        decision_id: "dec-002",
        domain: "traffic_mobility",
        title: "Activate Traffic Reroute",
        description: "Congestion detected on Blue Heron Blvd",
        priority: 2,
        confidence: "medium",
        status: "pending",
        recommended_action: { action: "reroute", signals: true },
        expected_impact: { congestion_reduction: 0.2 },
        valid_until: new Date(Date.now() + 2 * 3600000).toISOString(),
      },
      {
        decision_id: "dec-003",
        domain: "utilities",
        title: "Pre-position Utility Crews",
        description: "Storm probability increasing",
        priority: 2,
        confidence: "high",
        status: "approved",
        recommended_action: { action: "stage_crews", count: 3 },
        expected_impact: { response_improvement: 0.25 },
        valid_until: new Date(Date.now() + 6 * 3600000).toISOString(),
      },
    ];

    const mockAlerts: CityAlert[] = [
      {
        id: "alert-001",
        type: "traffic",
        message: "Heavy congestion on US-1 northbound",
        severity: "medium",
        timestamp: new Date().toISOString(),
        zone: "downtown",
      },
      {
        id: "alert-002",
        type: "weather",
        message: "Thunderstorm warning - 2 hours",
        severity: "high",
        timestamp: new Date().toISOString(),
        zone: "citywide",
      },
      {
        id: "alert-003",
        type: "utility",
        message: "Minor power fluctuation - Singer Island",
        severity: "low",
        timestamp: new Date().toISOString(),
        zone: "singer_island",
      },
    ];

    const mockForecast: Forecast[] = Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      crime_risk: 0.2 + Math.sin(i / 4) * 0.15 + Math.random() * 0.1,
      traffic_level: 0.3 + Math.sin((i - 6) / 3) * 0.3 + Math.random() * 0.1,
      resource_demand: 0.4 + Math.sin(i / 5) * 0.2 + Math.random() * 0.1,
    }));

    setDecisions(mockDecisions);
    setAlerts(mockAlerts);
    setForecast(mockForecast);
    setLoading(false);
  }, []);

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 4:
        return "bg-red-500";
      case 3:
        return "bg-orange-500";
      case 2:
        return "bg-yellow-500";
      default:
        return "bg-blue-500";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "border-red-500 bg-red-500/10";
      case "high":
        return "border-orange-500 bg-orange-500/10";
      case "medium":
        return "border-yellow-500 bg-yellow-500/10";
      default:
        return "border-blue-500 bg-blue-500/10";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return "bg-green-500/20 text-green-400";
      case "rejected":
        return "bg-red-500/20 text-red-400";
      case "implemented":
        return "bg-blue-500/20 text-blue-400";
      default:
        return "bg-yellow-500/20 text-yellow-400";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-gray-400 text-sm font-medium">City Health Score</h3>
            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="mt-2">
            <span className="text-3xl font-bold text-white">{cityHealthScore.toFixed(1)}</span>
            <span className="text-gray-400 text-lg ml-1">/ 100</span>
          </div>
          <div className="mt-2 flex items-center text-sm">
            <span className="text-green-400">+2.3%</span>
            <span className="text-gray-500 ml-2">from last week</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-gray-400 text-sm font-medium">Resource Efficiency</h3>
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="mt-2">
            <span className="text-3xl font-bold text-white">{resourceEfficiency.toFixed(1)}</span>
            <span className="text-gray-400 text-lg ml-1">%</span>
          </div>
          <div className="mt-2 flex items-center text-sm">
            <span className="text-green-400">+1.5%</span>
            <span className="text-gray-500 ml-2">optimization gain</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-gray-400 text-sm font-medium">Active Decisions</h3>
            <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div className="mt-2">
            <span className="text-3xl font-bold text-white">{decisions.filter(d => d.status === "pending").length}</span>
            <span className="text-gray-400 text-lg ml-1">pending</span>
          </div>
          <div className="mt-2 flex items-center text-sm">
            <span className="text-blue-400">{decisions.length} total</span>
            <span className="text-gray-500 ml-2">recommendations</span>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-gray-400 text-sm font-medium">Active Alerts</h3>
            <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div className="mt-2">
            <span className="text-3xl font-bold text-white">{alerts.length}</span>
            <span className="text-gray-400 text-lg ml-1">active</span>
          </div>
          <div className="mt-2 flex items-center text-sm">
            <span className="text-orange-400">{alerts.filter(a => a.severity === "high" || a.severity === "critical").length} high priority</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Recommended Deployments</h2>
            <p className="text-sm text-gray-400">AI-generated operational recommendations</p>
          </div>
          <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
            {decisions.map((decision) => (
              <div
                key={decision.decision_id}
                className="bg-gray-700/50 rounded-lg p-4 border border-gray-600"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${getPriorityColor(decision.priority)}`}></div>
                    <div>
                      <h3 className="font-medium text-white">{decision.title}</h3>
                      <p className="text-sm text-gray-400">{decision.description}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(decision.status)}`}>
                    {decision.status}
                  </span>
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-gray-400">
                      Domain: <span className="text-white">{decision.domain.replace("_", " ")}</span>
                    </span>
                    <span className="text-gray-400">
                      Confidence: <span className="text-white">{decision.confidence}</span>
                    </span>
                  </div>
                  {decision.status === "pending" && (
                    <div className="flex space-x-2">
                      <button className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors">
                        Approve
                      </button>
                      <button className="px-3 py-1 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors">
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">City Alerts Feed</h2>
            <p className="text-sm text-gray-400">Real-time alerts and notifications</p>
          </div>
          <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`rounded-lg p-4 border-l-4 ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-medium text-gray-400 uppercase">{alert.type}</span>
                      <span className="text-xs text-gray-500">|</span>
                      <span className="text-xs text-gray-400">{alert.zone}</span>
                    </div>
                    <p className="mt-1 text-white">{alert.message}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    alert.severity === "critical" ? "bg-red-500/20 text-red-400" :
                    alert.severity === "high" ? "bg-orange-500/20 text-orange-400" :
                    alert.severity === "medium" ? "bg-yellow-500/20 text-yellow-400" :
                    "bg-blue-500/20 text-blue-400"
                  }`}>
                    {alert.severity}
                  </span>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Rolling 24-Hour Forecast</h2>
          <p className="text-sm text-gray-400">Predicted city metrics for the next 24 hours</p>
        </div>
        <div className="p-6">
          <div className="flex items-end justify-between h-48 space-x-1">
            {forecast.map((f, i) => (
              <div key={i} className="flex-1 flex flex-col items-center space-y-1">
                <div className="w-full flex flex-col space-y-1">
                  <div
                    className="w-full bg-red-500/60 rounded-t"
                    style={{ height: `${f.crime_risk * 100}px` }}
                    title={`Crime Risk: ${(f.crime_risk * 100).toFixed(0)}%`}
                  ></div>
                  <div
                    className="w-full bg-yellow-500/60"
                    style={{ height: `${f.traffic_level * 80}px` }}
                    title={`Traffic: ${(f.traffic_level * 100).toFixed(0)}%`}
                  ></div>
                  <div
                    className="w-full bg-blue-500/60 rounded-b"
                    style={{ height: `${f.resource_demand * 60}px` }}
                    title={`Resource Demand: ${(f.resource_demand * 100).toFixed(0)}%`}
                  ></div>
                </div>
                {i % 4 === 0 && (
                  <span className="text-xs text-gray-500">{f.hour}:00</span>
                )}
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500/60 rounded"></div>
              <span className="text-sm text-gray-400">Crime Risk</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-yellow-500/60 rounded"></div>
              <span className="text-sm text-gray-400">Traffic Level</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500/60 rounded"></div>
              <span className="text-sm text-gray-400">Resource Demand</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

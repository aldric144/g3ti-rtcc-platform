"use client";

import React, { useState, useEffect } from "react";

interface SafetyAlert {
  alert_id: string;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  affected_areas: string[];
  start_time: string;
  end_time: string | null;
  active: boolean;
}

export default function AlertsFeed() {
  const [alerts, setAlerts] = useState<SafetyAlert[]>([]);

  useEffect(() => {
    setAlerts([
      {
        alert_id: "1",
        alert_type: "traffic_advisory",
        severity: "low",
        title: "Road Construction on Blue Heron Blvd",
        message: "Lane closures expected between 9 AM and 4 PM. Please use alternate routes.",
        affected_areas: ["Downtown Riviera Beach"],
        start_time: new Date().toISOString(),
        end_time: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        active: true,
      },
      {
        alert_id: "2",
        alert_type: "community_notice",
        severity: "info",
        title: "National Night Out Planning",
        message: "Join us in planning this year's National Night Out event. Volunteers needed!",
        affected_areas: ["All Neighborhoods"],
        start_time: new Date().toISOString(),
        end_time: null,
        active: true,
      },
      {
        alert_id: "3",
        alert_type: "crime_prevention",
        severity: "medium",
        title: "Vehicle Break-in Prevention",
        message: "Recent increase in vehicle break-ins. Remember to lock your car and remove valuables.",
        affected_areas: ["West Riviera Beach", "Riviera Beach Heights"],
        start_time: new Date().toISOString(),
        end_time: null,
        active: true,
      },
    ]);
  }, []);

  const getAlertIcon = (type: string): string => {
    switch (type) {
      case "safety_alert":
        return "🚨";
      case "amber_alert":
        return "🟠";
      case "silver_alert":
        return "⚪";
      case "weather_emergency":
        return "🌪️";
      case "traffic_advisory":
        return "🚧";
      case "community_notice":
        return "📢";
      case "crime_prevention":
        return "🔒";
      case "public_safety":
        return "🛡️";
      default:
        return "ℹ️";
    }
  };

  const getSeverityStyle = (severity: string): { border: string; bg: string } => {
    switch (severity) {
      case "critical":
        return { border: "border-red-500", bg: "bg-red-50" };
      case "high":
        return { border: "border-orange-500", bg: "bg-orange-50" };
      case "medium":
        return { border: "border-yellow-500", bg: "bg-yellow-50" };
      case "low":
        return { border: "border-blue-500", bg: "bg-blue-50" };
      default:
        return { border: "border-gray-300", bg: "bg-gray-50" };
    }
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const activeAlerts = alerts.filter((a) => a.active);

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Safety Alerts</h3>
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
          {activeAlerts.length} Active
        </span>
      </div>

      <div className="space-y-4">
        {activeAlerts.length === 0 ? (
          <div className="text-center py-8">
            <span className="text-4xl">✅</span>
            <p className="text-gray-500 mt-2">No active alerts</p>
          </div>
        ) : (
          activeAlerts.map((alert) => {
            const style = getSeverityStyle(alert.severity);
            return (
              <div
                key={alert.alert_id}
                className={`border-l-4 ${style.border} ${style.bg} rounded-r-lg p-4`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">{getAlertIcon(alert.alert_type)}</span>
                    <div>
                      <h4 className="font-medium text-gray-900">{alert.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                    </div>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-4">
                    <span>📍 {alert.affected_areas.join(", ")}</span>
                    <span>🕐 {formatDate(alert.start_time)}</span>
                  </div>
                  <span className={`px-2 py-1 rounded capitalize ${
                    alert.severity === "critical" ? "bg-red-200 text-red-800" :
                    alert.severity === "high" ? "bg-orange-200 text-orange-800" :
                    alert.severity === "medium" ? "bg-yellow-200 text-yellow-800" :
                    "bg-blue-200 text-blue-800"
                  }`}>
                    {alert.severity}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="mt-4 pt-4 border-t">
        <p className="text-xs text-gray-500 text-center">
          Sign up for SMS/Email alerts to receive notifications directly
        </p>
      </div>
    </div>
  );
}

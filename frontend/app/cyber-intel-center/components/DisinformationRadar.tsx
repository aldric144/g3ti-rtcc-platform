"use client";

import React, { useState, useEffect } from "react";

interface DisinfoAlert {
  alert_id: string;
  disinfo_type: string;
  severity: string;
  source_platform: string;
  content_summary: string;
  viral_velocity: number;
  share_count: number;
  reach_estimate: number;
  bot_network_detected: boolean;
  community_tension_score: number;
  recommended_action: string;
  timestamp: string;
}

interface NarrativeCluster {
  id: string;
  narrative: string;
  sources: string[];
  reach: number;
  tension: number;
}

export default function DisinformationRadar() {
  const [alerts, setAlerts] = useState<DisinfoAlert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<DisinfoAlert | null>(null);
  const [filterType, setFilterType] = useState<string>("ALL");
  const [communityTension, setCommunityTension] = useState(0);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await fetch("/api/cyber-intel/alerts?alert_type=DISINFORMATION&limit=50");
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
        
        const tensions = (data.alerts || []).map((a: any) => a.community_tension_score || 0);
        const avgTension = tensions.length > 0
          ? tensions.reduce((a: number, b: number) => a + b, 0) / tensions.length
          : 0;
        setCommunityTension(avgTension);
      }
    } catch (error) {
      console.error("Failed to fetch disinfo alerts:", error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "EMERGENCY":
      case "CRITICAL":
        return "text-red-500 bg-red-500/20 border-red-500";
      case "HIGH":
        return "text-orange-500 bg-orange-500/20 border-orange-500";
      case "MEDIUM":
        return "text-yellow-500 bg-yellow-500/20 border-yellow-500";
      default:
        return "text-green-500 bg-green-500/20 border-green-500";
    }
  };

  const getTensionColor = (tension: number) => {
    if (tension >= 0.7) return "text-red-400 bg-red-500";
    if (tension >= 0.4) return "text-yellow-400 bg-yellow-500";
    return "text-green-400 bg-green-500";
  };

  const getPlatformIcon = (platform: string) => {
    const icons: { [key: string]: string } = {
      FACEBOOK: "FB",
      TWITTER_X: "X",
      INSTAGRAM: "IG",
      TIKTOK: "TT",
      YOUTUBE: "YT",
      TELEGRAM: "TG",
      NEXTDOOR: "ND",
      REDDIT: "RD",
    };
    return icons[platform] || platform.slice(0, 2);
  };

  const disinfoTypes = [
    "ALL",
    "VIRAL_FALSE_POST",
    "COORDINATED_PANIC",
    "EMERGENCY_HOAX",
    "FAKE_POLICE_PAGE",
    "BOT_NETWORK",
    "ELECTION_INTERFERENCE",
    "ANTI_POLICE_WAVE",
  ];

  const filteredAlerts = filterType === "ALL"
    ? alerts
    : alerts.filter((a) => a.disinfo_type === filterType);

  const botNetworks = alerts.filter((a) => a.bot_network_detected).length;
  const viralPosts = alerts.filter((a) => a.viral_velocity > 0.5).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-yellow-400">Disinformation Radar</h2>
        <div className="flex items-center space-x-4">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600"
          >
            {disinfoTypes.map((type) => (
              <option key={type} value={type}>
                {type.replace(/_/g, " ")}
              </option>
            ))}
          </select>
          <button
            onClick={fetchAlerts}
            className="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded-lg"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        <div className="bg-yellow-900/30 border border-yellow-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-yellow-400">{alerts.length}</div>
          <div className="text-sm text-yellow-300">Total Alerts</div>
        </div>
        <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-400">{botNetworks}</div>
          <div className="text-sm text-red-300">Bot Networks</div>
        </div>
        <div className="bg-orange-900/30 border border-orange-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-orange-400">{viralPosts}</div>
          <div className="text-sm text-orange-300">Viral Posts</div>
        </div>
        <div className="bg-purple-900/30 border border-purple-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-purple-400">
            {alerts.filter((a) => a.disinfo_type === "FAKE_POLICE_PAGE").length}
          </div>
          <div className="text-sm text-purple-300">Impersonations</div>
        </div>
        <div className={`rounded-lg p-4 text-center border ${
          communityTension >= 0.7 ? "bg-red-900/30 border-red-500" :
          communityTension >= 0.4 ? "bg-yellow-900/30 border-yellow-500" :
          "bg-green-900/30 border-green-500"
        }`}>
          <div className={`text-3xl font-bold ${
            communityTension >= 0.7 ? "text-red-400" :
            communityTension >= 0.4 ? "text-yellow-400" : "text-green-400"
          }`}>
            {Math.round(communityTension * 100)}%
          </div>
          <div className="text-sm text-gray-300">Tension Index</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Narrative Heatmap</h3>
          
          <div className="relative h-64 bg-gray-900 rounded-lg overflow-hidden mb-4">
            <svg className="w-full h-full" viewBox="0 0 800 250">
              <defs>
                <radialGradient id="tensionGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity="0.6" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
                </radialGradient>
              </defs>
              
              <circle cx="400" cy="125" r="40" fill="#1f2937" stroke="#4b5563" strokeWidth="2" />
              <text x="400" y="130" textAnchor="middle" fill="white" fontSize="12">RBPD</text>
              
              {filteredAlerts.slice(0, 15).map((alert, index) => {
                const angle = (index / 15) * 2 * Math.PI - Math.PI / 2;
                const radius = 80 + (alert.viral_velocity || 0) * 50;
                const x = 400 + radius * Math.cos(angle);
                const y = 125 + radius * Math.sin(angle);
                const size = 15 + (alert.share_count || 0) / 1000;
                const color = alert.severity === "CRITICAL" ? "#ef4444" :
                             alert.severity === "HIGH" ? "#f97316" :
                             alert.severity === "MEDIUM" ? "#eab308" : "#22c55e";
                
                return (
                  <g key={alert.alert_id}>
                    <line
                      x1="400"
                      y1="125"
                      x2={x}
                      y2={y}
                      stroke={color}
                      strokeWidth="1"
                      opacity="0.4"
                    />
                    <circle
                      cx={x}
                      cy={y}
                      r={Math.min(size, 25)}
                      fill={color}
                      opacity="0.5"
                      stroke={color}
                      strokeWidth="2"
                      className="cursor-pointer hover:opacity-80"
                      onClick={() => setSelectedAlert(alert)}
                    />
                    <text x={x} y={y + 35} textAnchor="middle" fill="#9ca3af" fontSize="8">
                      {getPlatformIcon(alert.source_platform)}
                    </text>
                  </g>
                );
              })}
            </svg>
            
            {filteredAlerts.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center text-gray-500">
                No disinformation detected
              </div>
            )}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-gray-700">
                  <th className="pb-2">Time</th>
                  <th className="pb-2">Type</th>
                  <th className="pb-2">Platform</th>
                  <th className="pb-2">Reach</th>
                  <th className="pb-2">Velocity</th>
                  <th className="pb-2">Severity</th>
                </tr>
              </thead>
              <tbody>
                {filteredAlerts.slice(0, 10).map((alert) => (
                  <tr
                    key={alert.alert_id}
                    className="border-b border-gray-700 hover:bg-gray-700/50 cursor-pointer"
                    onClick={() => setSelectedAlert(alert)}
                  >
                    <td className="py-2 text-sm">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-2 text-sm">{alert.disinfo_type.replace(/_/g, " ")}</td>
                    <td className="py-2">
                      <span className="px-2 py-1 bg-gray-700 rounded text-xs">
                        {getPlatformIcon(alert.source_platform)}
                      </span>
                    </td>
                    <td className="py-2 text-sm">{(alert.reach_estimate || 0).toLocaleString()}</td>
                    <td className="py-2">
                      <div className="w-20 bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-yellow-500 h-2 rounded-full"
                          style={{ width: `${(alert.viral_velocity || 0) * 100}%` }}
                        />
                      </div>
                    </td>
                    <td className="py-2">
                      <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Alert Details</h3>
          
          {selectedAlert ? (
            <div className="space-y-4">
              <div className={`px-3 py-2 rounded-lg border ${getSeverityColor(selectedAlert.severity)}`}>
                <span className="font-semibold">{selectedAlert.severity}</span>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Type</label>
                <div className="text-white">{selectedAlert.disinfo_type.replace(/_/g, " ")}</div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Platform</label>
                <div className="text-white">{selectedAlert.source_platform}</div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Content Summary</label>
                <div className="text-white text-sm bg-gray-700 p-2 rounded">
                  {selectedAlert.content_summary || "No content available"}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400">Shares</label>
                  <div className="text-white">{(selectedAlert.share_count || 0).toLocaleString()}</div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Reach</label>
                  <div className="text-white">{(selectedAlert.reach_estimate || 0).toLocaleString()}</div>
                </div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Viral Velocity</label>
                <div className="w-full bg-gray-700 rounded-full h-3 mt-1">
                  <div
                    className="bg-yellow-500 h-3 rounded-full"
                    style={{ width: `${(selectedAlert.viral_velocity || 0) * 100}%` }}
                  />
                </div>
              </div>
              
              {selectedAlert.bot_network_detected && (
                <div className="bg-red-900/30 border border-red-500 rounded-lg p-3">
                  <span className="text-red-400 font-semibold">Bot Network Detected</span>
                </div>
              )}
              
              <div>
                <label className="text-sm text-gray-400">Community Tension</label>
                <div className={`text-2xl font-bold ${getTensionColor(selectedAlert.community_tension_score || 0)}`}>
                  {Math.round((selectedAlert.community_tension_score || 0) * 100)}%
                </div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Recommended Action</label>
                <div className="text-yellow-400 text-sm">{selectedAlert.recommended_action}</div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              Select an alert to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

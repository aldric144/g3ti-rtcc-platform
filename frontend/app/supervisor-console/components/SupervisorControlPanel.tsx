"use client";

import React, { useState, useEffect } from "react";

interface ControlSetting {
  id: string;
  name: string;
  description: string;
  category: string;
  enabled: boolean;
  value?: string | number;
  type: "toggle" | "slider" | "select";
  options?: string[];
  min?: number;
  max?: number;
}

interface SystemStatistics {
  system_monitor: {
    total_engines_monitored: number;
    total_alerts_generated: number;
    active_alerts: number;
    feedback_loops_detected: number;
    overload_predictions: number;
  };
  auto_corrector: {
    total_corrections: number;
    completed: number;
    failed: number;
    pending: number;
    success_rate: number;
  };
  ethics_guard: {
    total_validations: number;
    approved: number;
    blocked: number;
    total_violations: number;
    critical_violations: number;
  };
  sentinel_engine: {
    total_alerts: number;
    resolved_alerts: number;
    total_action_requests: number;
    approved_requests: number;
    denied_requests: number;
  };
}

export default function SupervisorControlPanel() {
  const [settings, setSettings] = useState<ControlSetting[]>([]);
  const [statistics, setStatistics] = useState<SystemStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockSettings: ControlSetting[] = [
      {
        id: "auto_correction",
        name: "Auto-Correction Engine",
        description: "Enable automatic correction of detected system issues",
        category: "System",
        enabled: true,
        type: "toggle",
      },
      {
        id: "ethics_guard",
        name: "Ethics Guard",
        description: "Enable constitutional and legal compliance checking",
        category: "Compliance",
        enabled: true,
        type: "toggle",
      },
      {
        id: "bias_detection",
        name: "Bias Detection",
        description: "Enable automatic bias detection in AI predictions",
        category: "Compliance",
        enabled: true,
        type: "toggle",
      },
      {
        id: "auto_block",
        name: "Auto-Block Violations",
        description: "Automatically block actions that violate compliance rules",
        category: "Compliance",
        enabled: true,
        type: "toggle",
      },
      {
        id: "cascade_prediction",
        name: "Cascade Prediction",
        description: "Enable predictive cascade analysis for system events",
        category: "Prediction",
        enabled: true,
        type: "toggle",
      },
      {
        id: "command_alerts",
        name: "Command Staff Alerts",
        description: "Send critical alerts to command staff",
        category: "Notifications",
        enabled: true,
        type: "toggle",
      },
      {
        id: "max_autonomy_level",
        name: "Maximum Autonomy Level",
        description: "Maximum autonomy level for auto-approved actions",
        category: "Autonomy",
        enabled: true,
        type: "slider",
        value: 2,
        min: 0,
        max: 5,
      },
      {
        id: "alert_threshold",
        name: "Alert Severity Threshold",
        description: "Minimum severity for generating alerts",
        category: "Alerts",
        enabled: true,
        type: "select",
        value: "medium",
        options: ["info", "low", "medium", "high", "critical"],
      },
      {
        id: "correction_cooldown",
        name: "Correction Cooldown (seconds)",
        description: "Minimum time between corrections on same component",
        category: "System",
        enabled: true,
        type: "slider",
        value: 300,
        min: 60,
        max: 3600,
      },
      {
        id: "max_corrections_per_hour",
        name: "Max Corrections Per Hour",
        description: "Maximum number of auto-corrections per hour",
        category: "System",
        enabled: true,
        type: "slider",
        value: 20,
        min: 5,
        max: 100,
      },
    ];

    const mockStatistics: SystemStatistics = {
      system_monitor: {
        total_engines_monitored: 16,
        total_alerts_generated: 245,
        active_alerts: 5,
        feedback_loops_detected: 3,
        overload_predictions: 8,
      },
      auto_corrector: {
        total_corrections: 156,
        completed: 142,
        failed: 8,
        pending: 6,
        success_rate: 0.91,
      },
      ethics_guard: {
        total_validations: 1250,
        approved: 1180,
        blocked: 45,
        total_violations: 67,
        critical_violations: 12,
      },
      sentinel_engine: {
        total_alerts: 89,
        resolved_alerts: 72,
        total_action_requests: 45,
        approved_requests: 38,
        denied_requests: 7,
      },
    };

    setSettings(mockSettings);
    setStatistics(mockStatistics);
    setLoading(false);
  }, []);

  const toggleSetting = (id: string) => {
    setSettings(settings.map(s => 
      s.id === id ? { ...s, enabled: !s.enabled } : s
    ));
  };

  const updateSettingValue = (id: string, value: string | number) => {
    setSettings(settings.map(s => 
      s.id === id ? { ...s, value } : s
    ));
  };

  const groupedSettings = settings.reduce((acc, setting) => {
    if (!acc[setting.category]) {
      acc[setting.category] = [];
    }
    acc[setting.category].push(setting);
    return acc;
  }, {} as Record<string, ControlSetting[]>);

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
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <h4 className="text-sm font-medium text-gray-400 mb-3">System Monitor</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Engines Monitored</span>
              <span className="font-semibold">{statistics?.system_monitor.total_engines_monitored}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Total Alerts</span>
              <span className="font-semibold">{statistics?.system_monitor.total_alerts_generated}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Active Alerts</span>
              <span className="font-semibold text-yellow-400">{statistics?.system_monitor.active_alerts}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Feedback Loops</span>
              <span className="font-semibold">{statistics?.system_monitor.feedback_loops_detected}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Auto-Corrector</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Corrections</span>
              <span className="font-semibold">{statistics?.auto_corrector.total_corrections}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Completed</span>
              <span className="font-semibold text-green-400">{statistics?.auto_corrector.completed}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Failed</span>
              <span className="font-semibold text-red-400">{statistics?.auto_corrector.failed}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Success Rate</span>
              <span className="font-semibold">{((statistics?.auto_corrector.success_rate || 0) * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Ethics Guard</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Validations</span>
              <span className="font-semibold">{statistics?.ethics_guard.total_validations}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Approved</span>
              <span className="font-semibold text-green-400">{statistics?.ethics_guard.approved}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Blocked</span>
              <span className="font-semibold text-red-400">{statistics?.ethics_guard.blocked}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Critical Violations</span>
              <span className="font-semibold text-red-400">{statistics?.ethics_guard.critical_violations}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Sentinel Engine</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Alerts</span>
              <span className="font-semibold">{statistics?.sentinel_engine.total_alerts}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Resolved</span>
              <span className="font-semibold text-green-400">{statistics?.sentinel_engine.resolved_alerts}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Action Requests</span>
              <span className="font-semibold">{statistics?.sentinel_engine.total_action_requests}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Approved</span>
              <span className="font-semibold text-green-400">{statistics?.sentinel_engine.approved_requests}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold">Supervisor Control Settings</h3>
        </div>
        
        <div className="p-4 space-y-6">
          {Object.entries(groupedSettings).map(([category, categorySettings]) => (
            <div key={category}>
              <h4 className="text-sm font-medium text-purple-400 mb-3">{category}</h4>
              <div className="space-y-4">
                {categorySettings.map((setting) => (
                  <div key={setting.id} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">{setting.name}</div>
                      <div className="text-sm text-gray-400">{setting.description}</div>
                    </div>
                    
                    <div className="ml-4">
                      {setting.type === "toggle" && (
                        <button
                          onClick={() => toggleSetting(setting.id)}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            setting.enabled ? "bg-purple-600" : "bg-gray-600"
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              setting.enabled ? "translate-x-6" : "translate-x-1"
                            }`}
                          />
                        </button>
                      )}
                      
                      {setting.type === "slider" && (
                        <div className="flex items-center space-x-3">
                          <input
                            type="range"
                            min={setting.min}
                            max={setting.max}
                            value={setting.value as number}
                            onChange={(e) => updateSettingValue(setting.id, parseInt(e.target.value))}
                            className="w-32 h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                          />
                          <span className="w-12 text-right font-mono">{setting.value}</span>
                        </div>
                      )}
                      
                      {setting.type === "select" && (
                        <select
                          value={setting.value as string}
                          onChange={(e) => updateSettingValue(setting.id, e.target.value)}
                          className="bg-gray-600 border border-gray-500 rounded px-3 py-1 text-sm"
                        >
                          {setting.options?.map((option) => (
                            <option key={option} value={option}>
                              {option.charAt(0).toUpperCase() + option.slice(1)}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        <div className="p-4 border-t border-gray-700 flex justify-end space-x-3">
          <button className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded">
            Reset to Defaults
          </button>
          <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded">
            Save Changes
          </button>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-yellow-700 p-4">
        <h4 className="text-lg font-semibold text-yellow-400 mb-3">Emergency Controls</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 bg-red-900/30 border border-red-700 rounded-lg hover:bg-red-900/50 transition-colors">
            <div className="text-red-400 font-bold">EMERGENCY STOP</div>
            <div className="text-sm text-red-400/75">Halt all autonomous operations</div>
          </button>
          <button className="p-4 bg-orange-900/30 border border-orange-700 rounded-lg hover:bg-orange-900/50 transition-colors">
            <div className="text-orange-400 font-bold">LOCKDOWN MODE</div>
            <div className="text-sm text-orange-400/75">Require approval for all actions</div>
          </button>
          <button className="p-4 bg-yellow-900/30 border border-yellow-700 rounded-lg hover:bg-yellow-900/50 transition-colors">
            <div className="text-yellow-400 font-bold">SAFE MODE</div>
            <div className="text-sm text-yellow-400/75">Disable non-essential features</div>
          </button>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useState } from "react";

interface AuditEntry {
  entry_id: string;
  event_type: string;
  severity: string;
  timestamp: string;
  actor_id: string;
  actor_type: string;
  actor_name: string;
  resource_type: string;
  resource_id: string;
  description: string;
  compliance_tags: string[];
}

interface ChainOfCustody {
  chain_id: string;
  resource_type: string;
  resource_id: string;
  entries_count: number;
  created_at: string;
  last_updated: string;
  is_sealed: boolean;
}

interface ComplianceReport {
  report_id: string;
  report_type: string;
  period: string;
  compliance_standard: string;
  generated_at: string;
  summary: {
    total_events: number;
    compliance_score: number;
    findings_count: number;
  };
}

interface AutonomySummary {
  period: string;
  total_actions: number;
  actions_by_level: Record<string, number>;
  human_overrides: number;
  denied_actions: number;
  ai_vs_human_ratio: number;
}

const mockAuditEntries: AuditEntry[] = [
  {
    entry_id: "audit-001",
    event_type: "action_approved",
    severity: "low",
    timestamp: new Date(Date.now() - 60000).toISOString(),
    actor_id: "operator-001",
    actor_type: "human",
    actor_name: "Officer Johnson",
    resource_type: "autonomous_action",
    resource_id: "action-abc123",
    description: "Approved patrol deployment to Downtown district",
    compliance_tags: ["cjis", "nist"],
  },
  {
    entry_id: "audit-002",
    event_type: "action_executed",
    severity: "info",
    timestamp: new Date(Date.now() - 120000).toISOString(),
    actor_id: "autonomy-engine",
    actor_type: "ai_engine",
    actor_name: "Autonomy Engine",
    resource_type: "autonomous_action",
    resource_id: "action-def456",
    description: "Auto-executed traffic signal optimization on Blue Heron Blvd",
    compliance_tags: ["nist"],
  },
  {
    entry_id: "audit-003",
    event_type: "human_override",
    severity: "high",
    timestamp: new Date(Date.now() - 180000).toISOString(),
    actor_id: "supervisor-001",
    actor_type: "human",
    actor_name: "Sgt. Williams",
    resource_type: "autonomous_action",
    resource_id: "action-ghi789",
    description: "Override: Cancelled automated evacuation recommendation",
    compliance_tags: ["cjis", "nist", "fl_state"],
  },
  {
    entry_id: "audit-004",
    event_type: "emergency_override_activated",
    severity: "critical",
    timestamp: new Date(Date.now() - 240000).toISOString(),
    actor_id: "eoc-commander",
    actor_type: "human",
    actor_name: "EOC Commander",
    resource_type: "emergency_override",
    resource_id: "override-flooding",
    description: "Activated flood emergency override for coastal zones",
    compliance_tags: ["nist", "fl_state"],
  },
  {
    entry_id: "audit-005",
    event_type: "action_denied",
    severity: "medium",
    timestamp: new Date(Date.now() - 300000).toISOString(),
    actor_id: "operator-002",
    actor_type: "human",
    actor_name: "Officer Martinez",
    resource_type: "autonomous_action",
    resource_id: "action-jkl012",
    description: "Denied: Automated crowd dispersal recommendation",
    compliance_tags: ["cjis", "nist"],
  },
];

const mockChains: ChainOfCustody[] = [
  {
    chain_id: "chain-001",
    resource_type: "autonomous_action",
    resource_id: "action-abc123",
    entries_count: 5,
    created_at: new Date(Date.now() - 3600000).toISOString(),
    last_updated: new Date(Date.now() - 60000).toISOString(),
    is_sealed: false,
  },
  {
    chain_id: "chain-002",
    resource_type: "investigation",
    resource_id: "inv-2024-0342",
    entries_count: 12,
    created_at: new Date(Date.now() - 86400000).toISOString(),
    last_updated: new Date(Date.now() - 7200000).toISOString(),
    is_sealed: true,
  },
];

const mockReports: ComplianceReport[] = [
  {
    report_id: "report-001",
    report_type: "cjis_compliance",
    period: "24h",
    compliance_standard: "cjis",
    generated_at: new Date(Date.now() - 3600000).toISOString(),
    summary: {
      total_events: 156,
      compliance_score: 98.5,
      findings_count: 2,
    },
  },
  {
    report_id: "report-002",
    report_type: "nist_compliance",
    period: "7d",
    compliance_standard: "nist",
    generated_at: new Date(Date.now() - 86400000).toISOString(),
    summary: {
      total_events: 1247,
      compliance_score: 96.2,
      findings_count: 8,
    },
  },
];

const mockSummary: AutonomySummary = {
  period: "24h",
  total_actions: 47,
  actions_by_level: {
    level_0: 12,
    level_1: 28,
    level_2: 7,
  },
  human_overrides: 3,
  denied_actions: 2,
  ai_vs_human_ratio: 4.2,
};

export default function AutonomyAuditCenter() {
  const [auditEntries, setAuditEntries] = useState<AuditEntry[]>(mockAuditEntries);
  const [chains, setChains] = useState<ChainOfCustody[]>(mockChains);
  const [reports, setReports] = useState<ComplianceReport[]>(mockReports);
  const [summary, setSummary] = useState<AutonomySummary>(mockSummary);
  const [activeView, setActiveView] = useState<"logs" | "chains" | "reports" | "statistics">("logs");
  const [selectedPeriod, setSelectedPeriod] = useState<"24h" | "7d" | "30d">("24h");
  const [eventTypeFilter, setEventTypeFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "text-red-500 bg-red-500/20";
      case "high":
        return "text-orange-500 bg-orange-500/20";
      case "medium":
        return "text-yellow-500 bg-yellow-500/20";
      case "low":
        return "text-green-500 bg-green-500/20";
      case "info":
        return "text-blue-500 bg-blue-500/20";
      default:
        return "text-gray-500 bg-gray-500/20";
    }
  };

  const getEventTypeColor = (eventType: string) => {
    if (eventType.includes("approved") || eventType.includes("completed")) {
      return "text-green-400";
    } else if (eventType.includes("denied") || eventType.includes("failed")) {
      return "text-red-400";
    } else if (eventType.includes("override") || eventType.includes("emergency")) {
      return "text-orange-400";
    } else if (eventType.includes("executed")) {
      return "text-blue-400";
    }
    return "text-gray-400";
  };

  const getActorTypeIcon = (actorType: string) => {
    switch (actorType) {
      case "human":
        return "👤";
      case "ai_engine":
        return "🤖";
      case "system":
        return "⚙️";
      default:
        return "❓";
    }
  };

  const filteredEntries = auditEntries.filter((entry) => {
    if (eventTypeFilter !== "all" && entry.event_type !== eventTypeFilter) return false;
    if (severityFilter !== "all" && entry.severity !== severityFilter) return false;
    return true;
  });

  const handleGenerateReport = (standard: string) => {
    const newReport: ComplianceReport = {
      report_id: `report-${Date.now()}`,
      report_type: `${standard}_compliance`,
      period: selectedPeriod,
      compliance_standard: standard,
      generated_at: new Date().toISOString(),
      summary: {
        total_events: Math.floor(Math.random() * 200) + 50,
        compliance_score: 95 + Math.random() * 5,
        findings_count: Math.floor(Math.random() * 5),
      },
    };
    setReports((prev) => [newReport, ...prev]);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setActiveView("logs")}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeView === "logs"
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            Audit Logs
          </button>
          <button
            onClick={() => setActiveView("chains")}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeView === "chains"
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            Chain of Custody
          </button>
          <button
            onClick={() => setActiveView("reports")}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeView === "reports"
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            Compliance Reports
          </button>
          <button
            onClick={() => setActiveView("statistics")}
            className={`px-4 py-2 rounded-lg transition-colors ${
              activeView === "statistics"
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }`}
          >
            Statistics
          </button>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value as "24h" | "7d" | "30d")}
            className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm">
            Export PDF
          </button>
        </div>
      </div>

      {activeView === "logs" && (
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-9">
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Audit Trail</h2>
                <div className="flex items-center gap-3">
                  <select
                    value={eventTypeFilter}
                    onChange={(e) => setEventTypeFilter(e.target.value)}
                    className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-sm"
                  >
                    <option value="all">All Events</option>
                    <option value="action_approved">Approved</option>
                    <option value="action_denied">Denied</option>
                    <option value="action_executed">Executed</option>
                    <option value="human_override">Override</option>
                    <option value="emergency_override_activated">Emergency</option>
                  </select>
                  <select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value)}
                    className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-sm"
                  >
                    <option value="all">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="info">Info</option>
                  </select>
                </div>
              </div>
              <div className="divide-y divide-gray-700 max-h-[600px] overflow-y-auto">
                {filteredEntries.map((entry) => (
                  <div key={entry.entry_id} className="p-4 hover:bg-gray-700/50 transition-colors">
                    <div className="flex items-start gap-4">
                      <div className="text-2xl">{getActorTypeIcon(entry.actor_type)}</div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 text-xs rounded ${getSeverityColor(entry.severity)}`}>
                            {entry.severity.toUpperCase()}
                          </span>
                          <span className={`text-sm font-medium ${getEventTypeColor(entry.event_type)}`}>
                            {entry.event_type.replace(/_/g, " ").toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(entry.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-white mb-1">{entry.description}</p>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-gray-400">
                            Actor: <span className="text-gray-300">{entry.actor_name}</span>
                          </span>
                          <span className="text-gray-400">
                            Resource: <span className="text-gray-300">{entry.resource_id}</span>
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {entry.compliance_tags.map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded uppercase"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-span-3 space-y-6">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-4">Decision Distribution</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">AI Decisions</span>
                    <span className="text-blue-400">{Math.round((summary.ai_vs_human_ratio / (summary.ai_vs_human_ratio + 1)) * 100)}%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500"
                      style={{ width: `${(summary.ai_vs_human_ratio / (summary.ai_vs_human_ratio + 1)) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Human Decisions</span>
                    <span className="text-green-400">{Math.round((1 / (summary.ai_vs_human_ratio + 1)) * 100)}%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500"
                      style={{ width: `${(1 / (summary.ai_vs_human_ratio + 1)) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-4">Override Statistics</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Human Overrides</span>
                  <span className="text-orange-400 font-medium">{summary.human_overrides}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Denied Actions</span>
                  <span className="text-red-400 font-medium">{summary.denied_actions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Override Rate</span>
                  <span className="text-yellow-400 font-medium">
                    {((summary.human_overrides / summary.total_actions) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-4">Chain Integrity</h3>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 bg-green-500 rounded-full" />
                <span className="text-green-400">Verified</span>
              </div>
              <p className="text-gray-400 text-sm">
                All audit chains have been verified. No tampering detected.
              </p>
              <button className="mt-3 w-full px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded transition-colors">
                Run Integrity Check
              </button>
            </div>
          </div>
        </div>
      )}

      {activeView === "chains" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-4 py-3 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Chain of Custody Records</h2>
          </div>
          <div className="divide-y divide-gray-700">
            {chains.map((chain) => (
              <div key={chain.chain_id} className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-white font-medium">{chain.resource_type}</span>
                      <span className="text-gray-400">:</span>
                      <span className="text-blue-400">{chain.resource_id}</span>
                      {chain.is_sealed && (
                        <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">
                          SEALED
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>Chain ID: {chain.chain_id}</span>
                      <span>{chain.entries_count} entries</span>
                      <span>Created: {new Date(chain.created_at).toLocaleDateString()}</span>
                      <span>Updated: {new Date(chain.last_updated).toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="px-3 py-1.5 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors">
                      View Chain
                    </button>
                    {!chain.is_sealed && (
                      <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
                        Seal Chain
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeView === "reports" && (
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-8">
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="px-4 py-3 border-b border-gray-700">
                <h2 className="text-lg font-semibold text-white">Generated Reports</h2>
              </div>
              <div className="divide-y divide-gray-700">
                {reports.map((report) => (
                  <div key={report.report_id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-white font-medium capitalize">
                            {report.compliance_standard.toUpperCase()} Compliance Report
                          </span>
                          <span className="px-2 py-0.5 bg-gray-700 text-gray-300 text-xs rounded">
                            {report.period}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-gray-400">
                            Events: <span className="text-white">{report.summary.total_events}</span>
                          </span>
                          <span className="text-gray-400">
                            Score:{" "}
                            <span
                              className={
                                report.summary.compliance_score >= 95
                                  ? "text-green-400"
                                  : report.summary.compliance_score >= 90
                                  ? "text-yellow-400"
                                  : "text-red-400"
                              }
                            >
                              {report.summary.compliance_score.toFixed(1)}%
                            </span>
                          </span>
                          <span className="text-gray-400">
                            Findings: <span className="text-orange-400">{report.summary.findings_count}</span>
                          </span>
                          <span className="text-gray-500">
                            Generated: {new Date(report.generated_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button className="px-3 py-1.5 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors">
                          View
                        </button>
                        <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
                          Download PDF
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-span-4">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-4">Generate New Report</h3>
              <div className="space-y-3">
                <button
                  onClick={() => handleGenerateReport("cjis")}
                  className="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-left"
                >
                  <div className="font-medium">CJIS Compliance</div>
                  <div className="text-sm text-gray-400">Criminal Justice Information Services</div>
                </button>
                <button
                  onClick={() => handleGenerateReport("nist")}
                  className="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-left"
                >
                  <div className="font-medium">NIST Compliance</div>
                  <div className="text-sm text-gray-400">National Institute of Standards</div>
                </button>
                <button
                  onClick={() => handleGenerateReport("fl_state")}
                  className="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-left"
                >
                  <div className="font-medium">FL State Compliance</div>
                  <div className="text-sm text-gray-400">Florida State Statutes</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeView === "statistics" && (
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-8">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-white mb-6">Autonomy Summary - {selectedPeriod}</h2>
              <div className="grid grid-cols-4 gap-4 mb-8">
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <div className="text-3xl font-bold text-white">{summary.total_actions}</div>
                  <div className="text-gray-400 text-sm">Total Actions</div>
                </div>
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <div className="text-3xl font-bold text-blue-400">{summary.actions_by_level.level_1}</div>
                  <div className="text-gray-400 text-sm">Auto-Executed (L1)</div>
                </div>
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <div className="text-3xl font-bold text-purple-400">{summary.actions_by_level.level_2}</div>
                  <div className="text-gray-400 text-sm">Human-Approved (L2)</div>
                </div>
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <div className="text-3xl font-bold text-orange-400">{summary.human_overrides}</div>
                  <div className="text-gray-400 text-sm">Overrides</div>
                </div>
              </div>

              <h3 className="text-white font-medium mb-4">Actions by Level</h3>
              <div className="space-y-3 mb-8">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Level 0 (Observation)</span>
                    <span className="text-gray-300">{summary.actions_by_level.level_0}</span>
                  </div>
                  <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gray-500"
                      style={{ width: `${(summary.actions_by_level.level_0 / summary.total_actions) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Level 1 (Auto-Execute)</span>
                    <span className="text-blue-400">{summary.actions_by_level.level_1}</span>
                  </div>
                  <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500"
                      style={{ width: `${(summary.actions_by_level.level_1 / summary.total_actions) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Level 2 (Human-Confirmed)</span>
                    <span className="text-purple-400">{summary.actions_by_level.level_2}</span>
                  </div>
                  <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-purple-500"
                      style={{ width: `${(summary.actions_by_level.level_2 / summary.total_actions) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              <h3 className="text-white font-medium mb-4">AI vs Human Decision Ratio</h3>
              <div className="flex items-center gap-4">
                <div className="flex-1 h-8 bg-gray-700 rounded-full overflow-hidden flex">
                  <div
                    className="h-full bg-blue-500 flex items-center justify-center text-white text-sm"
                    style={{ width: `${(summary.ai_vs_human_ratio / (summary.ai_vs_human_ratio + 1)) * 100}%` }}
                  >
                    AI
                  </div>
                  <div
                    className="h-full bg-green-500 flex items-center justify-center text-white text-sm"
                    style={{ width: `${(1 / (summary.ai_vs_human_ratio + 1)) * 100}%` }}
                  >
                    Human
                  </div>
                </div>
                <span className="text-white font-medium">{summary.ai_vs_human_ratio.toFixed(1)}:1</span>
              </div>
            </div>
          </div>

          <div className="col-span-4 space-y-6">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-4">Compliance Scores</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-400">CJIS</span>
                    <span className="text-green-400">98.5%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500" style={{ width: "98.5%" }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-400">NIST</span>
                    <span className="text-green-400">96.2%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500" style={{ width: "96.2%" }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-400">FL State</span>
                    <span className="text-green-400">99.1%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500" style={{ width: "99.1%" }} />
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-4">Download Reports</h3>
              <div className="space-y-2">
                <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-sm text-left flex items-center justify-between">
                  <span>24h Autonomy Summary</span>
                  <span className="text-gray-400">PDF</span>
                </button>
                <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-sm text-left flex items-center justify-between">
                  <span>7d Autonomy Summary</span>
                  <span className="text-gray-400">PDF</span>
                </button>
                <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-sm text-left flex items-center justify-between">
                  <span>30d Autonomy Summary</span>
                  <span className="text-gray-400">PDF</span>
                </button>
                <button className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-sm text-left flex items-center justify-between">
                  <span>Full Audit Export</span>
                  <span className="text-gray-400">CSV</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

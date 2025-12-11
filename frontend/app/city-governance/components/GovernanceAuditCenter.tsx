"use client";

import React, { useState, useEffect } from "react";

interface AuditLogEntry {
  audit_id: string;
  timestamp: string;
  action: string;
  resource_type: string;
  resource_id: string;
  user_id: string;
  details: Record<string, unknown>;
  ip_address: string;
  session_id: string;
  compliance_tags: string[];
  outcome?: string;
  risk_level?: string;
}

interface AuditStatistics {
  total_entries: number;
  entries_today: number;
  entries_this_week: number;
  by_action: Record<string, number>;
  by_resource_type: Record<string, number>;
  by_user: Record<string, number>;
  by_risk_level: Record<string, number>;
}

const ACTION_COLORS: Record<string, string> = {
  validate_action: "text-blue-400",
  create_policy: "text-green-400",
  deactivate_policy: "text-red-400",
  create_approval_request: "text-yellow-400",
  submit_approval: "text-purple-400",
  escalate_approval: "text-orange-400",
  get_legal_document: "text-cyan-400",
  calculate_risk_score: "text-pink-400",
};

const RISK_LEVEL_COLORS: Record<string, string> = {
  low: "bg-green-900/30 text-green-400",
  elevated: "bg-yellow-900/30 text-yellow-400",
  high: "bg-orange-900/30 text-orange-400",
  critical: "bg-red-900/30 text-red-400",
};

const RESOURCE_TYPE_ICONS: Record<string, string> = {
  constitutional_validation: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
  policy: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  approval_request: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
  risk_assessment: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
  legal_document: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
};

export default function GovernanceAuditCenter() {
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [statistics, setStatistics] = useState<AuditStatistics | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<AuditLogEntry | null>(null);
  const [filterAction, setFilterAction] = useState("");
  const [filterResourceType, setFilterResourceType] = useState("");
  const [filterUser, setFilterUser] = useState("");
  const [filterRiskLevel, setFilterRiskLevel] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [dateRange, setDateRange] = useState<"today" | "week" | "month" | "all">("today");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditLogs();
    fetchStatistics();
  }, [dateRange]);

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const mockLogs: AuditLogEntry[] = [
        {
          audit_id: "const-audit-001",
          timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
          action: "validate_action",
          resource_type: "constitutional_validation",
          resource_id: "val-001",
          user_id: "ai-system",
          details: {
            action_type: "drone_property_entry",
            action_category: "drone_operation",
            result: "allowed_with_human_review",
            triggered_rules: 3,
          },
          ip_address: "internal",
          session_id: "api-session-001",
          compliance_tags: ["CJIS", "CONSTITUTIONAL"],
          outcome: "allowed_with_human_review",
          risk_level: "high",
        },
        {
          audit_id: "const-audit-002",
          timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
          action: "create_policy",
          resource_type: "policy",
          resource_id: "policy-new-001",
          user_id: "admin-johnson",
          details: {
            original_text: "Drones cannot enter private property without warrant",
            confidence: 0.92,
            source: "florida_statute",
          },
          ip_address: "192.168.1.100",
          session_id: "web-session-002",
          compliance_tags: ["CJIS", "CONSTITUTIONAL"],
          risk_level: "low",
        },
        {
          audit_id: "const-audit-003",
          timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
          action: "submit_approval",
          resource_type: "approval_request",
          resource_id: "req-001",
          user_id: "sgt-williams",
          details: {
            approval_type: "supervisor",
            decision: "approved",
            mfa_verified: true,
          },
          ip_address: "192.168.1.105",
          session_id: "web-session-003",
          compliance_tags: ["CJIS", "CONSTITUTIONAL"],
          outcome: "approved",
          risk_level: "elevated",
        },
        {
          audit_id: "const-audit-004",
          timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
          action: "calculate_risk_score",
          resource_type: "risk_assessment",
          resource_id: "risk-001",
          user_id: "ai-system",
          details: {
            action_type: "surveillance_escalation",
            total_score: 78,
            category: "high",
            requires_human_review: true,
          },
          ip_address: "internal",
          session_id: "api-session-002",
          compliance_tags: ["CJIS", "CONSTITUTIONAL"],
          risk_level: "high",
        },
        {
          audit_id: "const-audit-005",
          timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
          action: "validate_action",
          resource_type: "constitutional_validation",
          resource_id: "val-002",
          user_id: "ai-system",
          details: {
            action_type: "patrol_deployment",
            action_category: "patrol_deployment",
            result: "allowed",
            triggered_rules: 1,
          },
          ip_address: "internal",
          session_id: "api-session-003",
          compliance_tags: ["CJIS", "CONSTITUTIONAL"],
          outcome: "allowed",
          risk_level: "low",
        },
        {
          audit_id: "const-audit-006",
          timestamp: new Date(Date.now() - 90 * 60000).toISOString(),
          action: "create_approval_request",
          resource_type: "approval_request",
          resource_id: "req-002",
          user_id: "ai-system",
          details: {
            action_type: "robotics_property_entry",
            risk_score: 92,
            required_approvals: ["command_staff", "legal_review"],
          },
          ip_address: "internal",
          session_id: "api-session-004",
          compliance_tags: ["CJIS", "CONSTITUTIONAL"],
          risk_level: "critical",
        },
        {
          audit_id: "const-audit-007",
          timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
          action: "get_legal_document",
          resource_type: "legal_document",
          resource_id: "doc-florida-statute-934",
          user_id: "ofc-martinez",
          details: {
            document_title: "Florida Statute 934.50",
            source: "florida_statute",
          },
          ip_address: "192.168.1.110",
          session_id: "web-session-004",
          compliance_tags: ["CJIS"],
          risk_level: "low",
        },
        {
          audit_id: "const-audit-008",
          timestamp: new Date(Date.now() - 180 * 60000).toISOString(),
          action: "escalate_approval",
          resource_type: "approval_request",
          resource_id: "req-003",
          user_id: "sgt-johnson",
          details: {
            reason: "Requires command staff review due to high risk",
            new_approval_level: "command_staff",
          },
          ip_address: "192.168.1.105",
          session_id: "web-session-005",
          compliance_tags: ["CJIS", "CONSTITUTIONAL"],
          risk_level: "high",
        },
      ];
      setAuditLogs(mockLogs);
    } catch (error) {
      console.error("Failed to fetch audit logs:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    const mockStats: AuditStatistics = {
      total_entries: 1247,
      entries_today: 89,
      entries_this_week: 423,
      by_action: {
        validate_action: 456,
        create_policy: 34,
        submit_approval: 189,
        calculate_risk_score: 312,
        create_approval_request: 156,
        get_legal_document: 78,
        escalate_approval: 22,
      },
      by_resource_type: {
        constitutional_validation: 456,
        policy: 34,
        approval_request: 367,
        risk_assessment: 312,
        legal_document: 78,
      },
      by_user: {
        "ai-system": 768,
        "admin-johnson": 45,
        "sgt-williams": 123,
        "sgt-johnson": 98,
        "ofc-martinez": 67,
        others: 146,
      },
      by_risk_level: {
        low: 534,
        elevated: 312,
        high: 289,
        critical: 112,
      },
    };
    setStatistics(mockStats);
  };

  const filteredLogs = auditLogs.filter((log) => {
    const matchesAction = !filterAction || log.action === filterAction;
    const matchesResourceType = !filterResourceType || log.resource_type === filterResourceType;
    const matchesUser = !filterUser || log.user_id.toLowerCase().includes(filterUser.toLowerCase());
    const matchesRiskLevel = !filterRiskLevel || log.risk_level === filterRiskLevel;
    const matchesSearch =
      !searchQuery ||
      log.audit_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.resource_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      JSON.stringify(log.details).toLowerCase().includes(searchQuery.toLowerCase());
    return matchesAction && matchesResourceType && matchesUser && matchesRiskLevel && matchesSearch;
  });

  const exportLogs = () => {
    const csvContent = [
      ["Audit ID", "Timestamp", "Action", "Resource Type", "Resource ID", "User", "Risk Level", "Details"].join(","),
      ...filteredLogs.map((log) =>
        [
          log.audit_id,
          log.timestamp,
          log.action,
          log.resource_type,
          log.resource_id,
          log.user_id,
          log.risk_level || "N/A",
          JSON.stringify(log.details).replace(/,/g, ";"),
        ].join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `governance-audit-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Governance Audit Center</h2>
          <p className="text-gray-400 text-sm">
            CJIS-compliant audit trail for all constitutional governance operations
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as typeof dateRange)}
            className="px-3 py-1 bg-gray-800 border border-gray-700 rounded text-sm text-white"
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="all">All Time</option>
          </select>
          <button
            onClick={exportLogs}
            className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
          >
            Export CSV
          </button>
          <button
            onClick={fetchAuditLogs}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      {statistics && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="text-2xl font-bold text-white">{statistics.total_entries.toLocaleString()}</div>
            <div className="text-sm text-gray-400">Total Audit Entries</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="text-2xl font-bold text-blue-400">{statistics.entries_today}</div>
            <div className="text-sm text-gray-400">Entries Today</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="text-2xl font-bold text-green-400">{statistics.entries_this_week}</div>
            <div className="text-sm text-gray-400">Entries This Week</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="text-2xl font-bold text-red-400">{statistics.by_risk_level.critical}</div>
            <div className="text-sm text-gray-400">Critical Risk Events</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-4 gap-4">
        <input
          type="text"
          placeholder="Search audit logs..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
        />
        <select
          value={filterAction}
          onChange={(e) => setFilterAction(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
        >
          <option value="">All Actions</option>
          <option value="validate_action">Validate Action</option>
          <option value="create_policy">Create Policy</option>
          <option value="submit_approval">Submit Approval</option>
          <option value="create_approval_request">Create Approval Request</option>
          <option value="calculate_risk_score">Calculate Risk Score</option>
          <option value="get_legal_document">Get Legal Document</option>
          <option value="escalate_approval">Escalate Approval</option>
        </select>
        <select
          value={filterResourceType}
          onChange={(e) => setFilterResourceType(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
        >
          <option value="">All Resource Types</option>
          <option value="constitutional_validation">Constitutional Validation</option>
          <option value="policy">Policy</option>
          <option value="approval_request">Approval Request</option>
          <option value="risk_assessment">Risk Assessment</option>
          <option value="legal_document">Legal Document</option>
        </select>
        <select
          value={filterRiskLevel}
          onChange={(e) => setFilterRiskLevel(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
        >
          <option value="">All Risk Levels</option>
          <option value="low">Low</option>
          <option value="elevated">Elevated</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
              <span className="font-medium text-white">Audit Log Entries</span>
              <span className="text-sm text-gray-400">{filteredLogs.length} entries</span>
            </div>
            <div className="max-h-[600px] overflow-y-auto">
              {filteredLogs.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No audit entries match your filters
                </div>
              ) : (
                filteredLogs.map((log) => (
                  <button
                    key={log.audit_id}
                    onClick={() => setSelectedEntry(log)}
                    className={`w-full text-left px-4 py-3 border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors ${
                      selectedEntry?.audit_id === log.audit_id ? "bg-blue-900/20" : ""
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <div className="mt-1">
                          <svg
                            className="w-5 h-5 text-gray-500"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d={RESOURCE_TYPE_ICONS[log.resource_type] || RESOURCE_TYPE_ICONS.policy}
                            />
                          </svg>
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className={`text-sm font-medium ${ACTION_COLORS[log.action] || "text-white"}`}>
                              {log.action.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                            </span>
                            {log.risk_level && (
                              <span className={`px-1.5 py-0.5 rounded text-xs ${RISK_LEVEL_COLORS[log.risk_level]}`}>
                                {log.risk_level.toUpperCase()}
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-400 mt-0.5">
                            {log.resource_type.replace(/_/g, " ")} | {log.resource_id}
                          </div>
                          <div className="text-xs text-gray-500 mt-0.5">
                            by {log.user_id}
                          </div>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(log.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {selectedEntry ? (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-lg font-bold text-white mb-4">Entry Details</h3>

              <div className="space-y-3">
                <div>
                  <label className="text-xs text-gray-500 uppercase">Audit ID</label>
                  <div className="text-sm text-gray-300 font-mono">{selectedEntry.audit_id}</div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Timestamp</label>
                  <div className="text-sm text-white">
                    {new Date(selectedEntry.timestamp).toLocaleString()}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Action</label>
                  <div className={`text-sm font-medium ${ACTION_COLORS[selectedEntry.action] || "text-white"}`}>
                    {selectedEntry.action.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Resource</label>
                  <div className="text-sm text-white">
                    {selectedEntry.resource_type.replace(/_/g, " ")}
                  </div>
                  <div className="text-xs text-gray-400 font-mono">{selectedEntry.resource_id}</div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">User</label>
                  <div className="text-sm text-white">{selectedEntry.user_id}</div>
                </div>

                {selectedEntry.risk_level && (
                  <div>
                    <label className="text-xs text-gray-500 uppercase">Risk Level</label>
                    <div className="mt-1">
                      <span className={`px-2 py-1 rounded text-sm ${RISK_LEVEL_COLORS[selectedEntry.risk_level]}`}>
                        {selectedEntry.risk_level.toUpperCase()}
                      </span>
                    </div>
                  </div>
                )}

                <div>
                  <label className="text-xs text-gray-500 uppercase">Session Info</label>
                  <div className="text-xs text-gray-400">
                    IP: {selectedEntry.ip_address} | Session: {selectedEntry.session_id}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Compliance Tags</label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedEntry.compliance_tags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 bg-blue-900/30 text-blue-400 rounded text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Details</label>
                  <div className="bg-gray-900 rounded p-2 mt-1 max-h-48 overflow-y-auto">
                    <pre className="text-xs text-gray-300 whitespace-pre-wrap">
                      {JSON.stringify(selectedEntry.details, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="text-center text-gray-500 py-8">
                <svg
                  className="w-12 h-12 mx-auto mb-3 opacity-50"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
                <p>Select an entry to view details</p>
              </div>
            </div>
          )}

          {statistics && (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-sm font-bold text-white mb-3">Activity by Risk Level</h3>
              <div className="space-y-2">
                {Object.entries(statistics.by_risk_level).map(([level, count]) => {
                  const total = Object.values(statistics.by_risk_level).reduce((a, b) => a + b, 0);
                  const percentage = (count / total) * 100;

                  return (
                    <div key={level}>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-gray-400 capitalize">{level}</span>
                        <span className="text-gray-300">{count}</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            level === "critical"
                              ? "bg-red-500"
                              : level === "high"
                              ? "bg-orange-500"
                              : level === "elevated"
                              ? "bg-yellow-500"
                              : "bg-green-500"
                          }`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {statistics && (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-sm font-bold text-white mb-3">Top Users</h3>
              <div className="space-y-2">
                {Object.entries(statistics.by_user)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([user, count]) => (
                    <div key={user} className="flex items-center justify-between">
                      <span className="text-sm text-gray-300">{user}</span>
                      <span className="text-sm text-gray-500">{count}</span>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

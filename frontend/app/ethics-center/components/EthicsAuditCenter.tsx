"use client";

import React, { useState } from "react";

interface AuditEntry {
  id: string;
  timestamp: string;
  actionId: string;
  actionType: string;
  actorId: string;
  actorRole: string;
  severity: string;
  summary: string;
  hashChain: string;
  retentionDays: number;
}

const mockAuditEntries: AuditEntry[] = [
  {
    id: "audit-001",
    timestamp: "2024-01-15T15:00:00Z",
    actionId: "action-001",
    actionType: "patrol_routing",
    actorId: "system",
    actorRole: "AI",
    severity: "INFO",
    summary: "Decision: ALLOW for patrol_routing. This decision was reached through 5 analysis steps.",
    hashChain: "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678",
    retentionDays: 365,
  },
  {
    id: "audit-002",
    timestamp: "2024-01-15T14:45:00Z",
    actionId: "action-002",
    actionType: "surveillance",
    actorId: "officer-123",
    actorRole: "OPERATOR",
    severity: "WARNING",
    summary: "Decision: MODIFY for surveillance. Ethics score: 68/100. Conditions: Address CIVIL_RIGHTS concerns.",
    hashChain: "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456789a",
    retentionDays: 730,
  },
  {
    id: "audit-003",
    timestamp: "2024-01-15T14:30:00Z",
    actionId: "action-003",
    actionType: "enforcement",
    actorId: "system",
    actorRole: "AI",
    severity: "VIOLATION",
    summary: "Decision: BLOCK for enforcement. Constitutional violation detected. Action blocked pending ethics review.",
    hashChain: "c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456789ab0",
    retentionDays: 2555,
  },
  {
    id: "audit-004",
    timestamp: "2024-01-15T14:15:00Z",
    actionId: "action-004",
    actionType: "search",
    actorId: "supervisor-456",
    actorRole: "SUPERVISOR",
    severity: "WARNING",
    summary: "Decision: REVIEW for search. Fourth Amendment concern. Supervisor review required.",
    hashChain: "d4e5f6789012345678901234567890abcdef1234567890abcdef123456789ab0c1",
    retentionDays: 730,
  },
  {
    id: "audit-005",
    timestamp: "2024-01-15T14:00:00Z",
    actionId: "action-005",
    actionType: "drone_surveillance",
    actorId: "system",
    actorRole: "AI",
    severity: "CRITICAL",
    summary: "Decision: BLOCK for drone_surveillance. Florida Statute § 934.50 violation. Surveillance exceeds limits.",
    hashChain: "e5f6789012345678901234567890abcdef1234567890abcdef123456789ab0c1d2",
    retentionDays: 2555,
  },
];

const severityStats = [
  { severity: "INFO", count: 1847, color: "#3B82F6" },
  { severity: "WARNING", count: 234, color: "#EAB308" },
  { severity: "CRITICAL", count: 45, color: "#F97316" },
  { severity: "VIOLATION", count: 12, color: "#EF4444" },
];

export default function EthicsAuditCenter() {
  const [selectedEntry, setSelectedEntry] = useState<AuditEntry | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "INFO":
        return "bg-blue-500";
      case "WARNING":
        return "bg-yellow-500";
      case "CRITICAL":
        return "bg-orange-500";
      case "VIOLATION":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "INFO":
        return "bg-blue-900 text-blue-300";
      case "WARNING":
        return "bg-yellow-900 text-yellow-300";
      case "CRITICAL":
        return "bg-orange-900 text-orange-300";
      case "VIOLATION":
        return "bg-red-900 text-red-300";
      default:
        return "bg-gray-900 text-gray-300";
    }
  };

  const filteredEntries = mockAuditEntries.filter((entry) => {
    if (filterSeverity !== "all" && entry.severity !== filterSeverity) return false;
    if (searchQuery && !entry.summary.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handleExport = () => {
    const csvContent = [
      ["ID", "Timestamp", "Action ID", "Action Type", "Actor", "Role", "Severity", "Summary", "Hash", "Retention Days"].join(","),
      ...mockAuditEntries.map((entry) =>
        [
          entry.id,
          entry.timestamp,
          entry.actionId,
          entry.actionType,
          entry.actorId,
          entry.actorRole,
          entry.severity,
          `"${entry.summary}"`,
          entry.hashChain.substring(0, 16) + "...",
          entry.retentionDays,
        ].join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ethics-audit-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-sm text-gray-400">Total Entries</div>
          <div className="text-2xl font-bold text-white">2,138</div>
          <div className="text-xs text-gray-500 mt-1">Last 30 days</div>
        </div>
        {severityStats.map((stat) => (
          <div key={stat.severity} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400">{stat.severity}</div>
            <div className="text-2xl font-bold" style={{ color: stat.color }}>{stat.count}</div>
            <div className="text-xs text-gray-500 mt-1">
              {((stat.count / 2138) * 100).toFixed(1)}%
            </div>
          </div>
        ))}
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Audit Chain Integrity</h3>
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
            <span className="text-sm text-green-400">Chain Valid</span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-white">2,138</div>
            <div className="text-xs text-gray-400">Total Entries</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">100%</div>
            <div className="text-xs text-gray-400">Hash Verified</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-400">SHA-256</div>
            <div className="text-xs text-gray-400">Hash Algorithm</div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Audit Log</h3>
            <div className="flex items-center space-x-4">
              <input
                type="text"
                placeholder="Search entries..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-gray-700 text-white text-sm rounded px-3 py-1.5 border border-gray-600 w-48"
              />
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="bg-gray-700 text-white text-sm rounded px-3 py-1.5 border border-gray-600"
              >
                <option value="all">All Severity</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="CRITICAL">Critical</option>
                <option value="VIOLATION">Violation</option>
              </select>
              <button
                onClick={handleExport}
                className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-1.5 rounded transition-colors"
              >
                Export CSV
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 divide-x divide-gray-700">
          <div className="divide-y divide-gray-700 max-h-[500px] overflow-y-auto">
            {filteredEntries.map((entry) => (
              <div
                key={entry.id}
                onClick={() => setSelectedEntry(entry)}
                className={`p-4 cursor-pointer hover:bg-gray-750 transition-colors ${
                  selectedEntry?.id === entry.id ? "bg-gray-750" : ""
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className={`w-3 h-3 rounded-full ${getSeverityColor(entry.severity)}`}></span>
                    <div>
                      <div className="text-sm font-medium text-white capitalize">
                        {entry.actionType.replace(/_/g, " ")}
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(entry.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded ${getSeverityBadge(entry.severity)}`}>
                    {entry.severity}
                  </span>
                </div>
                <p className="text-xs text-gray-400 line-clamp-2">{entry.summary}</p>
              </div>
            ))}
          </div>

          <div className="p-4">
            {selectedEntry ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-semibold text-white">Entry Details</h4>
                  <span className={`text-xs px-2 py-1 rounded ${getSeverityBadge(selectedEntry.severity)}`}>
                    {selectedEntry.severity}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs text-gray-400">Entry ID</span>
                    <div className="text-sm text-white font-mono">{selectedEntry.id}</div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Action ID</span>
                    <div className="text-sm text-white font-mono">{selectedEntry.actionId}</div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Action Type</span>
                    <div className="text-sm text-white capitalize">{selectedEntry.actionType.replace(/_/g, " ")}</div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Timestamp</span>
                    <div className="text-sm text-white">{new Date(selectedEntry.timestamp).toLocaleString()}</div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Actor</span>
                    <div className="text-sm text-white">{selectedEntry.actorId}</div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Role</span>
                    <div className="text-sm text-white">{selectedEntry.actorRole}</div>
                  </div>
                </div>

                <div>
                  <span className="text-xs text-gray-400">Summary</span>
                  <p className="text-sm text-white mt-1">{selectedEntry.summary}</p>
                </div>

                <div>
                  <span className="text-xs text-gray-400">Hash Chain</span>
                  <div className="mt-1 p-2 bg-gray-900 rounded border border-gray-700">
                    <code className="text-xs text-green-400 break-all">{selectedEntry.hashChain}</code>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-700">
                  <div>
                    <span className="text-xs text-gray-400">Retention Period</span>
                    <div className="text-sm text-white">{selectedEntry.retentionDays} days</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="h-2 w-2 rounded-full bg-green-500"></span>
                    <span className="text-xs text-green-400">Hash Verified</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">
                Select an entry to view details
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

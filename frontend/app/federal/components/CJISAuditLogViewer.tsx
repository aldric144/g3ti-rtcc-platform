"use client";

import { useState } from "react";

interface AuditEntry {
  id: string;
  userId: string;
  userName: string;
  agencyId: string;
  action: string;
  resourceType: string;
  resourceId: string | null;
  success: boolean;
  timestamp: string;
  ipAddress: string | null;
  policyAreas: string[];
}

export function CJISAuditLogViewer() {
  const [entries, setEntries] = useState<AuditEntry[]>([
    {
      id: "audit-1",
      userId: "user-001",
      userName: "John Smith",
      agencyId: "FL0000000",
      action: "export",
      resourceType: "ndex_export",
      resourceId: "ndex-12345",
      success: true,
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      ipAddress: "192.168.1.100",
      policyAreas: ["5", "8"],
    },
    {
      id: "audit-2",
      userId: "user-002",
      userName: "Jane Doe",
      agencyId: "FL0000000",
      action: "query",
      resourceType: "ncic_query",
      resourceId: "ncic-67890",
      success: true,
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      ipAddress: "192.168.1.101",
      policyAreas: ["5", "7", "8"],
    },
    {
      id: "audit-3",
      userId: "user-003",
      userName: "Bob Wilson",
      agencyId: "FL0000000",
      action: "access_denied",
      resourceType: "federal_data",
      resourceId: null,
      success: false,
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      ipAddress: "192.168.1.102",
      policyAreas: ["5", "8"],
    },
  ]);

  const [filters, setFilters] = useState({
    action: "",
    resourceType: "",
    successOnly: false,
    failedOnly: false,
  });

  const [dateRange, setDateRange] = useState({
    start: "",
    end: "",
  });

  const actions = [
    { value: "", label: "All Actions" },
    { value: "login", label: "Login" },
    { value: "logout", label: "Logout" },
    { value: "query", label: "Query" },
    { value: "view", label: "View" },
    { value: "create", label: "Create" },
    { value: "update", label: "Update" },
    { value: "export", label: "Export" },
    { value: "access_denied", label: "Access Denied" },
  ];

  const resourceTypes = [
    { value: "", label: "All Resources" },
    { value: "ndex_export", label: "N-DEx Export" },
    { value: "ncic_query", label: "NCIC Query" },
    { value: "etrace_export", label: "eTrace Export" },
    { value: "sar_report", label: "SAR Report" },
    { value: "federal_data", label: "Federal Data" },
    { value: "audit_log", label: "Audit Log" },
  ];

  const getActionColor = (action: string) => {
    switch (action) {
      case "export":
        return "bg-blue-500";
      case "query":
        return "bg-purple-500";
      case "create":
        return "bg-green-500";
      case "update":
        return "bg-yellow-500";
      case "view":
        return "bg-gray-500";
      case "access_denied":
        return "bg-red-500";
      case "login":
        return "bg-teal-500";
      case "logout":
        return "bg-orange-500";
      default:
        return "bg-gray-500";
    }
  };

  const filteredEntries = entries.filter((entry) => {
    if (filters.action && entry.action !== filters.action) return false;
    if (filters.resourceType && entry.resourceType !== filters.resourceType) return false;
    if (filters.successOnly && !entry.success) return false;
    if (filters.failedOnly && entry.success) return false;
    return true;
  });

  const handleGenerateReport = () => {
    const report = {
      agency_id: "FL0000000",
      report_period: {
        start: dateRange.start || new Date(Date.now() - 86400000 * 30).toISOString(),
        end: dateRange.end || new Date().toISOString(),
      },
      statistics: {
        total_events: entries.length,
        successful: entries.filter((e) => e.success).length,
        failed: entries.filter((e) => !e.success).length,
        by_action: entries.reduce((acc, e) => {
          acc[e.action] = (acc[e.action] || 0) + 1;
          return acc;
        }, {} as Record<string, number>),
      },
      compliance_status: {
        area_5_access_control: "compliant",
        area_7_encryption: "compliant",
        area_8_auditing: "compliant",
        area_10_system_protection: "compliant",
      },
    };
    alert("Compliance Report Generated:\n\n" + JSON.stringify(report, null, 2));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-2">CJIS Audit Log Viewer</h2>
        <p className="text-gray-400">
          View and filter CJIS-compliant audit logs for all federal operations. Logs are retained
          for 7 years per CJIS Security Policy Area 8 requirements.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Action</label>
            <select
              value={filters.action}
              onChange={(e) => setFilters({ ...filters, action: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {actions.map((action) => (
                <option key={action.value} value={action.value}>
                  {action.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Resource Type</label>
            <select
              value={filters.resourceType}
              onChange={(e) => setFilters({ ...filters, resourceType: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {resourceTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Start Date</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">End Date</label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex items-center space-x-6 mt-4">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.successOnly}
              onChange={(e) =>
                setFilters({ ...filters, successOnly: e.target.checked, failedOnly: false })
              }
              className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Successful only</span>
          </label>
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.failedOnly}
              onChange={(e) =>
                setFilters({ ...filters, failedOnly: e.target.checked, successOnly: false })
              }
              className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Failed only</span>
          </label>
          <button
            onClick={handleGenerateReport}
            className="ml-auto bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Generate Compliance Report
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-white">{entries.length}</div>
          <div className="text-sm text-gray-400">Total Events</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-green-400">
            {entries.filter((e) => e.success).length}
          </div>
          <div className="text-sm text-gray-400">Successful</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-red-400">
            {entries.filter((e) => !e.success).length}
          </div>
          <div className="text-sm text-gray-400">Failed/Denied</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-blue-400">
            {new Set(entries.map((e) => e.userId)).size}
          </div>
          <div className="text-sm text-gray-400">Unique Users</div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">
          Audit Log ({filteredEntries.length} entries)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
                <th className="pb-3">Timestamp</th>
                <th className="pb-3">User</th>
                <th className="pb-3">Action</th>
                <th className="pb-3">Resource</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">IP Address</th>
                <th className="pb-3">Policy Areas</th>
              </tr>
            </thead>
            <tbody>
              {filteredEntries.map((entry) => (
                <tr key={entry.id} className="border-b border-gray-700/50">
                  <td className="py-3 text-gray-300 text-sm">
                    {new Date(entry.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3">
                    <div className="text-white text-sm">{entry.userName}</div>
                    <div className="text-xs text-gray-500">{entry.userId}</div>
                  </td>
                  <td className="py-3">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium text-white ${getActionColor(
                        entry.action
                      )}`}
                    >
                      {entry.action.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="py-3">
                    <div className="text-white text-sm">
                      {entry.resourceType.replace(/_/g, " ")}
                    </div>
                    {entry.resourceId && (
                      <div className="text-xs text-gray-500 font-mono">{entry.resourceId}</div>
                    )}
                  </td>
                  <td className="py-3">
                    {entry.success ? (
                      <span className="text-green-400 text-sm">Success</span>
                    ) : (
                      <span className="text-red-400 text-sm">Failed</span>
                    )}
                  </td>
                  <td className="py-3 text-gray-300 text-sm font-mono">
                    {entry.ipAddress || "-"}
                  </td>
                  <td className="py-3">
                    <div className="flex space-x-1">
                      {entry.policyAreas.map((area) => (
                        <span
                          key={area}
                          className="px-2 py-0.5 bg-gray-700 rounded text-xs text-gray-300"
                        >
                          Area {area}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Compliance Status */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">CJIS Policy Compliance Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { area: "5", name: "Access Control", status: "Enforced" },
            { area: "7", name: "Encryption", status: "Compliant" },
            { area: "8", name: "Auditing", status: "Active" },
            { area: "10", name: "System Protection", status: "Enforced" },
          ].map((policy) => (
            <div key={policy.area} className="bg-gray-700/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-300">Area {policy.area}</span>
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
              </div>
              <div className="text-white font-medium">{policy.name}</div>
              <div className="text-xs text-green-400 mt-1">{policy.status}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

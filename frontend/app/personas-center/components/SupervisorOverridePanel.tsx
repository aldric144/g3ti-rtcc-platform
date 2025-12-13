"use client";

import React, { useState, useEffect } from "react";

interface Persona {
  persona_id: string;
  name: string;
  persona_type: string;
  status: string;
}

interface Mission {
  mission_id: string;
  title: string;
  status: string;
  priority: string;
}

interface ApprovalRequest {
  request_id: string;
  mission_id: string;
  task_id?: string;
  request_type: string;
  description: string;
  urgency: string;
  requested_by: string;
  required_authority: string;
  status: string;
  created_at: string;
  expires_at: string;
}

interface Violation {
  violation_id: string;
  violation_type: string;
  framework: string;
  persona_id: string;
  action_type: string;
  description: string;
  severity: string;
  blocking: boolean;
  timestamp: string;
}

interface SupervisorOverridePanelProps {
  personas: Persona[];
  missions: Mission[];
  onRefresh: () => void;
}

const getUrgencyColor = (urgency: string): string => {
  const colors: Record<string, string> = {
    critical: "bg-red-600 text-red-100",
    high: "bg-orange-600 text-orange-100",
    medium: "bg-yellow-600 text-yellow-100",
    low: "bg-green-600 text-green-100",
    routine: "bg-gray-600 text-gray-100",
  };
  return colors[urgency] || "bg-gray-600 text-gray-100";
};

const getSeverityColor = (severity: string): string => {
  const colors: Record<string, string> = {
    critical: "text-red-400",
    high: "text-orange-400",
    medium: "text-yellow-400",
    low: "text-green-400",
  };
  return colors[severity] || "text-gray-400";
};

export default function SupervisorOverridePanel({
  personas,
  missions,
  onRefresh,
}: SupervisorOverridePanelProps) {
  const [activeTab, setActiveTab] = useState<"approvals" | "violations" | "overrides">(
    "approvals"
  );
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(
    null
  );
  const [approvalNotes, setApprovalNotes] = useState("");

  useEffect(() => {
    fetchApprovals();
    fetchViolations();
  }, []);

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/approvals/pending");
      if (response.ok) {
        const data = await response.json();
        setApprovals(data.approvals || []);
      }
    } catch (error) {
      console.error("Failed to fetch approvals:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchViolations = async () => {
    try {
      const response = await fetch("/api/compliance/violations");
      if (response.ok) {
        const data = await response.json();
        setViolations(data.violations || []);
      }
    } catch (error) {
      console.error("Failed to fetch violations:", error);
    }
  };

  const handleApprove = async (requestId: string) => {
    try {
      const response = await fetch(`/api/approvals/${requestId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          approved_by: "supervisor",
          notes: approvalNotes,
        }),
      });

      if (response.ok) {
        setApprovals((prev) => prev.filter((a) => a.request_id !== requestId));
        setSelectedApproval(null);
        setApprovalNotes("");
        onRefresh();
      }
    } catch (error) {
      console.error("Failed to approve:", error);
    }
  };

  const handleDeny = async (requestId: string) => {
    try {
      const response = await fetch(`/api/approvals/${requestId}/deny`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          denied_by: "supervisor",
          reason: approvalNotes || "Request denied by supervisor",
        }),
      });

      if (response.ok) {
        setApprovals((prev) => prev.filter((a) => a.request_id !== requestId));
        setSelectedApproval(null);
        setApprovalNotes("");
        onRefresh();
      }
    } catch (error) {
      console.error("Failed to deny:", error);
    }
  };

  const handleResolveViolation = async (violationId: string) => {
    try {
      const response = await fetch(
        `/api/compliance/violations/${violationId}/resolve`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            resolved_by: "supervisor",
            notes: "Resolved by supervisor override",
          }),
        }
      );

      if (response.ok) {
        setViolations((prev) =>
          prev.filter((v) => v.violation_id !== violationId)
        );
      }
    } catch (error) {
      console.error("Failed to resolve violation:", error);
    }
  };

  const handlePersonaStatusChange = async (
    personaId: string,
    newStatus: string
  ) => {
    try {
      const response = await fetch(`/api/personas/${personaId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        onRefresh();
      }
    } catch (error) {
      console.error("Failed to update persona status:", error);
    }
  };

  const tabs = [
    { id: "approvals", label: "Pending Approvals", count: approvals.length },
    { id: "violations", label: "Active Violations", count: violations.length },
    { id: "overrides", label: "Manual Overrides", count: 0 },
  ];

  return (
    <div className="h-full overflow-y-auto bg-gray-900">
      <div className="p-4 bg-gray-800 border-b border-gray-700 sticky top-0 z-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">
            Supervisor Override Panel
          </h2>
          <button
            onClick={() => {
              fetchApprovals();
              fetchViolations();
            }}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-300"
          >
            Refresh
          </button>
        </div>

        <div className="flex space-x-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 rounded-t text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "bg-gray-900 text-white"
                  : "bg-gray-700 text-gray-400 hover:text-gray-200"
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-red-600 rounded-full text-xs text-white">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="p-4">
        {activeTab === "approvals" && (
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : approvals.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">✓</div>
                <p>No pending approvals</p>
              </div>
            ) : (
              approvals.map((approval) => (
                <div
                  key={approval.request_id}
                  className={`bg-gray-800 rounded-lg p-4 border ${
                    selectedApproval?.request_id === approval.request_id
                      ? "border-blue-500"
                      : "border-gray-700"
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span
                          className={`px-2 py-0.5 rounded text-xs ${getUrgencyColor(
                            approval.urgency
                          )}`}
                        >
                          {approval.urgency}
                        </span>
                        <span className="text-white font-medium">
                          {approval.request_type}
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm mt-1">
                        {approval.description}
                      </p>
                    </div>
                    <div className="text-right text-xs text-gray-500">
                      <div>
                        Expires:{" "}
                        {new Date(approval.expires_at).toLocaleString()}
                      </div>
                      <div>
                        Requested by: {approval.requested_by}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                    <div>
                      <span className="text-gray-500">Mission:</span>
                      <span className="text-gray-300 ml-2">
                        {approval.mission_id.slice(0, 8)}...
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Authority Required:</span>
                      <span className="text-gray-300 ml-2 capitalize">
                        {approval.required_authority}
                      </span>
                    </div>
                  </div>

                  {selectedApproval?.request_id === approval.request_id ? (
                    <div className="space-y-3">
                      <textarea
                        value={approvalNotes}
                        onChange={(e) => setApprovalNotes(e.target.value)}
                        placeholder="Add notes (optional)..."
                        className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                        rows={2}
                      />
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleApprove(approval.request_id)}
                          className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-white font-medium"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleDeny(approval.request_id)}
                          className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-white font-medium"
                        >
                          Deny
                        </button>
                        <button
                          onClick={() => {
                            setSelectedApproval(null);
                            setApprovalNotes("");
                          }}
                          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-300"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setSelectedApproval(approval)}
                      className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white font-medium"
                    >
                      Review Request
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "violations" && (
          <div className="space-y-4">
            {violations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">✓</div>
                <p>No active violations</p>
              </div>
            ) : (
              violations.map((violation) => (
                <div
                  key={violation.violation_id}
                  className="bg-gray-800 rounded-lg p-4 border border-gray-700"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span
                          className={`text-sm font-medium ${getSeverityColor(
                            violation.severity
                          )}`}
                        >
                          {violation.severity.toUpperCase()}
                        </span>
                        {violation.blocking && (
                          <span className="px-2 py-0.5 bg-red-900 text-red-300 rounded text-xs">
                            BLOCKING
                          </span>
                        )}
                      </div>
                      <p className="text-white font-medium mt-1">
                        {violation.violation_type}
                      </p>
                      <p className="text-gray-400 text-sm mt-1">
                        {violation.description}
                      </p>
                    </div>
                    <div className="text-right text-xs text-gray-500">
                      <div>{new Date(violation.timestamp).toLocaleString()}</div>
                      <div className="capitalize">{violation.framework}</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                    <div>
                      <span className="text-gray-500">Persona:</span>
                      <span className="text-gray-300 ml-2">
                        {violation.persona_id}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Action:</span>
                      <span className="text-gray-300 ml-2">
                        {violation.action_type}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleResolveViolation(violation.violation_id)}
                    className="w-full px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded text-white font-medium"
                  >
                    Resolve Violation
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "overrides" && (
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4">
                Persona Status Override
              </h3>
              <div className="space-y-3">
                {personas.map((persona) => (
                  <div
                    key={persona.persona_id}
                    className="flex items-center justify-between p-3 bg-gray-700/50 rounded"
                  >
                    <div>
                      <div className="font-medium text-white">{persona.name}</div>
                      <div className="text-xs text-gray-400 capitalize">
                        {persona.persona_type.replace("apex_", "")} -{" "}
                        {persona.status}
                      </div>
                    </div>
                    <select
                      value={persona.status}
                      onChange={(e) =>
                        handlePersonaStatusChange(
                          persona.persona_id,
                          e.target.value
                        )
                      }
                      className="bg-gray-600 border border-gray-500 rounded px-3 py-1 text-sm text-white"
                    >
                      <option value="active">Active</option>
                      <option value="standby">Standby</option>
                      <option value="maintenance">Maintenance</option>
                      <option value="offline">Offline</option>
                      <option value="suspended">Suspended</option>
                    </select>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4">
                Emergency Actions
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <button className="p-3 bg-red-900/50 hover:bg-red-900 border border-red-700 rounded text-red-300 text-sm font-medium">
                  Suspend All Personas
                </button>
                <button className="p-3 bg-yellow-900/50 hover:bg-yellow-900 border border-yellow-700 rounded text-yellow-300 text-sm font-medium">
                  Pause All Missions
                </button>
                <button className="p-3 bg-blue-900/50 hover:bg-blue-900 border border-blue-700 rounded text-blue-300 text-sm font-medium">
                  Clear All Sessions
                </button>
                <button className="p-3 bg-green-900/50 hover:bg-green-900 border border-green-700 rounded text-green-300 text-sm font-medium">
                  Activate All Personas
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

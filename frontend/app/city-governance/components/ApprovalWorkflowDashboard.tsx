"use client";

import React, { useState, useEffect } from "react";

interface ApprovalSignature {
  approver_id: string;
  approval_type: string;
  decision: string;
  timestamp: string;
  mfa_verified: boolean;
  notes?: string;
}

interface ApprovalRequirement {
  approval_type: string;
  minimum_approvals: number;
  requires_mfa: boolean;
  timeout_minutes: number;
}

interface ApprovalRequest {
  request_id: string;
  action_id: string;
  action_type: string;
  action_category: string;
  risk_score: number;
  requested_by: string;
  context: Record<string, unknown>;
  requirements: ApprovalRequirement[];
  signatures: ApprovalSignature[];
  status: string;
  created_at: string;
  expires_at: string;
  completed_at?: string;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-500",
  approved: "bg-green-500",
  denied: "bg-red-500",
  expired: "bg-gray-500",
  escalated: "bg-purple-500",
};

const APPROVAL_TYPE_LABELS: Record<string, string> = {
  single_operator: "Single Operator",
  supervisor: "Supervisor",
  command_staff: "Command Staff",
  multi_factor: "Multi-Factor",
  legal_review: "Legal Review",
  city_manager: "City Manager",
  emergency_director: "Emergency Director",
};

const RISK_COLORS: Record<string, string> = {
  low: "text-green-400",
  elevated: "text-yellow-400",
  high: "text-orange-400",
  critical: "text-red-400",
};

export default function ApprovalWorkflowDashboard() {
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<ApprovalRequest | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("pending");
  const [filterApprovalType, setFilterApprovalType] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [approvalNotes, setApprovalNotes] = useState("");
  const [currentUserId] = useState("operator-001");
  const [currentUserRole] = useState("supervisor");

  useEffect(() => {
    fetchRequests();
    const interval = setInterval(fetchRequests, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const mockRequests: ApprovalRequest[] = [
        {
          request_id: "req-001",
          action_id: "action-drone-001",
          action_type: "drone_property_entry",
          action_category: "drone_operation",
          risk_score: 75,
          requested_by: "ai-system",
          context: {
            location: "123 Main St, Riviera Beach",
            incident_type: "suspicious_activity",
            drone_id: "RBPD-DRONE-01",
          },
          requirements: [
            { approval_type: "supervisor", minimum_approvals: 1, requires_mfa: true, timeout_minutes: 30 },
          ],
          signatures: [],
          status: "pending",
          created_at: new Date(Date.now() - 10 * 60000).toISOString(),
          expires_at: new Date(Date.now() + 20 * 60000).toISOString(),
        },
        {
          request_id: "req-002",
          action_id: "action-surveillance-001",
          action_type: "surveillance_escalation",
          action_category: "surveillance",
          risk_score: 85,
          requested_by: "ai-system",
          context: {
            target_area: "Zone 3 - Downtown",
            escalation_level: "enhanced",
            duration_hours: 4,
          },
          requirements: [
            { approval_type: "supervisor", minimum_approvals: 1, requires_mfa: true, timeout_minutes: 60 },
            { approval_type: "command_staff", minimum_approvals: 1, requires_mfa: true, timeout_minutes: 60 },
          ],
          signatures: [
            {
              approver_id: "sgt-johnson",
              approval_type: "supervisor",
              decision: "approved",
              timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
              mfa_verified: true,
              notes: "Approved for ongoing investigation",
            },
          ],
          status: "pending",
          created_at: new Date(Date.now() - 30 * 60000).toISOString(),
          expires_at: new Date(Date.now() + 30 * 60000).toISOString(),
        },
        {
          request_id: "req-003",
          action_id: "action-robotics-001",
          action_type: "robotics_property_entry",
          action_category: "robotics_deployment",
          risk_score: 92,
          requested_by: "ai-system",
          context: {
            robot_id: "RBPD-ROBOT-02",
            location: "456 Oak Ave",
            mission_type: "tactical_reconnaissance",
          },
          requirements: [
            { approval_type: "command_staff", minimum_approvals: 2, requires_mfa: true, timeout_minutes: 15 },
            { approval_type: "legal_review", minimum_approvals: 1, requires_mfa: false, timeout_minutes: 30 },
          ],
          signatures: [],
          status: "pending",
          created_at: new Date(Date.now() - 5 * 60000).toISOString(),
          expires_at: new Date(Date.now() + 10 * 60000).toISOString(),
        },
        {
          request_id: "req-004",
          action_id: "action-traffic-001",
          action_type: "traffic_enforcement_automation",
          action_category: "traffic_control",
          risk_score: 45,
          requested_by: "ai-system",
          context: {
            zone: "School Zone - MLK Blvd",
            enforcement_type: "speed_monitoring",
          },
          requirements: [
            { approval_type: "single_operator", minimum_approvals: 1, requires_mfa: false, timeout_minutes: 120 },
          ],
          signatures: [
            {
              approver_id: "ofc-smith",
              approval_type: "single_operator",
              decision: "approved",
              timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
              mfa_verified: false,
            },
          ],
          status: "approved",
          created_at: new Date(Date.now() - 120 * 60000).toISOString(),
          expires_at: new Date(Date.now() - 60 * 60000).toISOString(),
          completed_at: new Date(Date.now() - 60 * 60000).toISOString(),
        },
      ];
      setRequests(mockRequests);
    } catch (error) {
      console.error("Failed to fetch requests:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskCategory = (score: number): string => {
    if (score >= 80) return "critical";
    if (score >= 60) return "high";
    if (score >= 40) return "elevated";
    return "low";
  };

  const getTimeRemaining = (expiresAt: string): string => {
    const remaining = new Date(expiresAt).getTime() - Date.now();
    if (remaining <= 0) return "Expired";
    const minutes = Math.floor(remaining / 60000);
    if (minutes < 60) return `${minutes}m remaining`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ${minutes % 60}m remaining`;
  };

  const getCompletionPercentage = (request: ApprovalRequest): number => {
    const totalRequired = request.requirements.reduce((sum, req) => sum + req.minimum_approvals, 0);
    const completed = request.signatures.filter((sig) => sig.decision === "approved").length;
    return Math.min(100, (completed / totalRequired) * 100);
  };

  const canApprove = (request: ApprovalRequest): boolean => {
    if (request.status !== "pending") return false;
    const hasAlreadyApproved = request.signatures.some((sig) => sig.approver_id === currentUserId);
    if (hasAlreadyApproved) return false;
    
    const pendingRequirements = request.requirements.filter((req) => {
      const approvedCount = request.signatures.filter(
        (sig) => sig.approval_type === req.approval_type && sig.decision === "approved"
      ).length;
      return approvedCount < req.minimum_approvals;
    });
    
    return pendingRequirements.some((req) => {
      if (req.approval_type === "supervisor" && currentUserRole === "supervisor") return true;
      if (req.approval_type === "command_staff" && currentUserRole === "command_staff") return true;
      if (req.approval_type === "single_operator") return true;
      return false;
    });
  };

  const submitApproval = async (requestId: string, decision: "approved" | "denied") => {
    const request = requests.find((r) => r.request_id === requestId);
    if (!request) return;

    const newSignature: ApprovalSignature = {
      approver_id: currentUserId,
      approval_type: currentUserRole,
      decision,
      timestamp: new Date().toISOString(),
      mfa_verified: true,
      notes: approvalNotes || undefined,
    };

    const updatedRequest = {
      ...request,
      signatures: [...request.signatures, newSignature],
    };

    const totalRequired = updatedRequest.requirements.reduce((sum, req) => sum + req.minimum_approvals, 0);
    const totalApproved = updatedRequest.signatures.filter((sig) => sig.decision === "approved").length;
    const anyDenied = updatedRequest.signatures.some((sig) => sig.decision === "denied");

    if (anyDenied) {
      updatedRequest.status = "denied";
      updatedRequest.completed_at = new Date().toISOString();
    } else if (totalApproved >= totalRequired) {
      updatedRequest.status = "approved";
      updatedRequest.completed_at = new Date().toISOString();
    }

    setRequests(requests.map((r) => (r.request_id === requestId ? updatedRequest : r)));
    setSelectedRequest(updatedRequest);
    setApprovalNotes("");
  };

  const escalateRequest = async (requestId: string) => {
    const request = requests.find((r) => r.request_id === requestId);
    if (!request) return;

    const updatedRequest = {
      ...request,
      status: "escalated",
      requirements: [
        ...request.requirements,
        { approval_type: "command_staff", minimum_approvals: 1, requires_mfa: true, timeout_minutes: 30 },
      ],
    };

    setRequests(requests.map((r) => (r.request_id === requestId ? updatedRequest : r)));
    setSelectedRequest(updatedRequest);
  };

  const filteredRequests = requests.filter((request) => {
    const matchesStatus = !filterStatus || request.status === filterStatus;
    const matchesType =
      !filterApprovalType ||
      request.requirements.some((req) => req.approval_type === filterApprovalType);
    return matchesStatus && matchesType;
  });

  const pendingCount = requests.filter((r) => r.status === "pending").length;
  const urgentCount = requests.filter(
    (r) => r.status === "pending" && r.risk_score >= 80
  ).length;

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
          <h2 className="text-xl font-bold text-white">Approval Workflow Dashboard</h2>
          <p className="text-gray-400 text-sm">
            Human-in-the-loop approval management for high-risk AI actions
          </p>
        </div>
        <div className="flex items-center space-x-4">
          {urgentCount > 0 && (
            <div className="flex items-center space-x-2 px-3 py-1 bg-red-900/30 border border-red-600 rounded">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-red-400">{urgentCount} Urgent</span>
            </div>
          )}
          <div className="flex items-center space-x-2 px-3 py-1 bg-yellow-900/30 border border-yellow-600 rounded">
            <span className="text-sm text-yellow-400">{pendingCount} Pending</span>
          </div>
          <button
            onClick={fetchRequests}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="flex space-x-4">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="denied">Denied</option>
          <option value="expired">Expired</option>
          <option value="escalated">Escalated</option>
        </select>
        <select
          value={filterApprovalType}
          onChange={(e) => setFilterApprovalType(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
        >
          <option value="">All Approval Types</option>
          {Object.entries(APPROVAL_TYPE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-3">
          {filteredRequests.length === 0 ? (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
              <svg
                className="w-12 h-12 mx-auto mb-3 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-gray-400">No approval requests match your filters</p>
            </div>
          ) : (
            filteredRequests.map((request) => (
              <button
                key={request.request_id}
                onClick={() => setSelectedRequest(request)}
                className={`w-full text-left bg-gray-800 rounded-lg border transition-colors ${
                  selectedRequest?.request_id === request.request_id
                    ? "border-blue-500"
                    : "border-gray-700 hover:border-gray-600"
                }`}
              >
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${STATUS_COLORS[request.status]}`}></div>
                        <span className="font-medium text-white">
                          {request.action_type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                        </span>
                        <span
                          className={`text-sm font-bold ${
                            RISK_COLORS[getRiskCategory(request.risk_score)]
                          }`}
                        >
                          Risk: {request.risk_score}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400 mt-1">
                        {request.action_category.replace(/_/g, " ")} | Requested by {request.requested_by}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-500">
                        {new Date(request.created_at).toLocaleTimeString()}
                      </div>
                      {request.status === "pending" && (
                        <div
                          className={`text-xs mt-1 ${
                            new Date(request.expires_at).getTime() - Date.now() < 10 * 60000
                              ? "text-red-400"
                              : "text-yellow-400"
                          }`}
                        >
                          {getTimeRemaining(request.expires_at)}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Approval Progress</span>
                      <span>
                        {request.signatures.filter((s) => s.decision === "approved").length} /{" "}
                        {request.requirements.reduce((sum, r) => sum + r.minimum_approvals, 0)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          request.status === "approved"
                            ? "bg-green-500"
                            : request.status === "denied"
                            ? "bg-red-500"
                            : "bg-blue-500"
                        }`}
                        style={{ width: `${getCompletionPercentage(request)}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1 mt-3">
                    {request.requirements.map((req, i) => {
                      const approvedCount = request.signatures.filter(
                        (sig) => sig.approval_type === req.approval_type && sig.decision === "approved"
                      ).length;
                      const isComplete = approvedCount >= req.minimum_approvals;

                      return (
                        <span
                          key={i}
                          className={`px-2 py-0.5 rounded text-xs ${
                            isComplete
                              ? "bg-green-900/30 text-green-400"
                              : "bg-gray-700 text-gray-400"
                          }`}
                        >
                          {APPROVAL_TYPE_LABELS[req.approval_type] || req.approval_type}
                          {req.requires_mfa && " (MFA)"}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </button>
            ))
          )}
        </div>

        <div className="space-y-4">
          {selectedRequest ? (
            <>
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h3 className="text-lg font-bold text-white mb-4">Request Details</h3>

                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-500 uppercase">Request ID</label>
                    <div className="text-sm text-gray-300 font-mono">{selectedRequest.request_id}</div>
                  </div>

                  <div>
                    <label className="text-xs text-gray-500 uppercase">Action Type</label>
                    <div className="text-sm text-white">
                      {selectedRequest.action_type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-gray-500 uppercase">Risk Score</label>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            selectedRequest.risk_score >= 80
                              ? "bg-red-500"
                              : selectedRequest.risk_score >= 60
                              ? "bg-orange-500"
                              : selectedRequest.risk_score >= 40
                              ? "bg-yellow-500"
                              : "bg-green-500"
                          }`}
                          style={{ width: `${selectedRequest.risk_score}%` }}
                        ></div>
                      </div>
                      <span
                        className={`text-sm font-bold ${
                          RISK_COLORS[getRiskCategory(selectedRequest.risk_score)]
                        }`}
                      >
                        {selectedRequest.risk_score}
                      </span>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-gray-500 uppercase">Context</label>
                    <div className="bg-gray-900 rounded p-2 mt-1">
                      {Object.entries(selectedRequest.context).map(([key, value]) => (
                        <div key={key} className="text-xs">
                          <span className="text-gray-500">{key}:</span>{" "}
                          <span className="text-gray-300">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-gray-500 uppercase">Status</label>
                    <div className="flex items-center space-x-2 mt-1">
                      <div className={`w-3 h-3 rounded-full ${STATUS_COLORS[selectedRequest.status]}`}></div>
                      <span className="text-sm text-white capitalize">{selectedRequest.status}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <h3 className="text-sm font-bold text-white mb-3">Approval Chain</h3>
                <div className="space-y-2">
                  {selectedRequest.signatures.map((sig, i) => (
                    <div
                      key={i}
                      className={`p-2 rounded ${
                        sig.decision === "approved"
                          ? "bg-green-900/20 border border-green-600/30"
                          : "bg-red-900/20 border border-red-600/30"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-white">{sig.approver_id}</span>
                        <span
                          className={`text-xs ${
                            sig.decision === "approved" ? "text-green-400" : "text-red-400"
                          }`}
                        >
                          {sig.decision.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {APPROVAL_TYPE_LABELS[sig.approval_type]} |{" "}
                        {new Date(sig.timestamp).toLocaleString()}
                        {sig.mfa_verified && " | MFA Verified"}
                      </div>
                      {sig.notes && <div className="text-xs text-gray-400 mt-1">{sig.notes}</div>}
                    </div>
                  ))}

                  {selectedRequest.status === "pending" &&
                    selectedRequest.requirements.map((req, i) => {
                      const approvedCount = selectedRequest.signatures.filter(
                        (sig) => sig.approval_type === req.approval_type && sig.decision === "approved"
                      ).length;
                      const remaining = req.minimum_approvals - approvedCount;

                      if (remaining <= 0) return null;

                      return (
                        <div key={i} className="p-2 rounded bg-gray-700/50 border border-gray-600 border-dashed">
                          <div className="text-sm text-gray-400">
                            Awaiting: {APPROVAL_TYPE_LABELS[req.approval_type]}
                          </div>
                          <div className="text-xs text-gray-500">
                            {remaining} more approval{remaining > 1 ? "s" : ""} needed
                            {req.requires_mfa && " (MFA required)"}
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>

              {canApprove(selectedRequest) && (
                <div className="bg-gray-800 rounded-lg border border-blue-500 p-4">
                  <h3 className="text-sm font-bold text-white mb-3">Submit Approval</h3>
                  <textarea
                    value={approvalNotes}
                    onChange={(e) => setApprovalNotes(e.target.value)}
                    placeholder="Add notes (optional)"
                    className="w-full h-20 px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none mb-3"
                  />
                  <div className="flex space-x-2">
                    <button
                      onClick={() => submitApproval(selectedRequest.request_id, "approved")}
                      className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded font-medium text-sm"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => submitApproval(selectedRequest.request_id, "denied")}
                      className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded font-medium text-sm"
                    >
                      Deny
                    </button>
                  </div>
                  <button
                    onClick={() => escalateRequest(selectedRequest.request_id)}
                    className="w-full mt-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-medium text-sm"
                  >
                    Escalate to Command
                  </button>
                </div>
              )}
            </>
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
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p>Select a request to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

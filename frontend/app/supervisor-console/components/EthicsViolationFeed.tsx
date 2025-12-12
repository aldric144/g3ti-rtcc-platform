"use client";

import React, { useState, useEffect } from "react";

interface Violation {
  violation_id: string;
  violation_type: string;
  severity: string;
  framework: string;
  engine: string;
  action_attempted: string;
  description: string;
  blocked: boolean;
  escalated: boolean;
  reviewed_by: string | null;
  review_decision: string | null;
  timestamp: string;
}

interface ComplianceSummary {
  total_validations: number;
  approved: number;
  blocked: number;
  requires_review: number;
  approval_rate: number;
  total_violations: number;
  critical_violations: number;
  escalated_violations: number;
  bias_audits_conducted: number;
  compliance_rules_active: number;
}

export default function EthicsViolationFeed() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockViolations: Violation[] = [
      {
        violation_id: "VIO-A1B2C3D4",
        violation_type: "unlawful_surveillance",
        severity: "critical",
        framework: "4th_amendment",
        engine: "intel_orchestration",
        action_attempted: "facial_recognition",
        description: "Facial recognition attempted without warrant",
        blocked: true,
        escalated: true,
        reviewed_by: null,
        review_decision: null,
        timestamp: new Date().toISOString(),
      },
      {
        violation_id: "VIO-E5F6G7H8",
        violation_type: "bias_detection",
        severity: "critical",
        framework: "nij_standards",
        engine: "predictive_ai",
        action_attempted: "model_prediction:crime_forecast",
        description: "Bias detected in crime_forecast predictions",
        blocked: false,
        escalated: true,
        reviewed_by: null,
        review_decision: null,
        timestamp: new Date(Date.now() - 600000).toISOString(),
      },
      {
        violation_id: "VIO-I9J0K1L2",
        violation_type: "excessive_data_retention",
        severity: "warning",
        framework: "florida_statutes",
        engine: "data_lake",
        action_attempted: "data_storage",
        description: "Data exceeds retention limit of 90 days",
        blocked: false,
        escalated: false,
        reviewed_by: "Sgt. Johnson",
        review_decision: "approved_with_exception",
        timestamp: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        violation_id: "VIO-M3N4O5P6",
        violation_type: "unauthorized_access",
        severity: "violation",
        framework: "cjis_security_policy",
        engine: "officer_assist",
        action_attempted: "record_access",
        description: "Access attempted without proper authorization level",
        blocked: true,
        escalated: false,
        reviewed_by: null,
        review_decision: null,
        timestamp: new Date(Date.now() - 7200000).toISOString(),
      },
    ];

    const mockSummary: ComplianceSummary = {
      total_validations: 1250,
      approved: 1180,
      blocked: 45,
      requires_review: 25,
      approval_rate: 0.944,
      total_violations: 67,
      critical_violations: 12,
      escalated_violations: 8,
      bias_audits_conducted: 24,
      compliance_rules_active: 12,
    };

    setViolations(mockViolations);
    setSummary(mockSummary);
    setLoading(false);
  }, []);

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "emergency":
        return <span className="px-2 py-1 text-xs font-bold bg-purple-600 text-white rounded animate-pulse">EMERGENCY</span>;
      case "critical":
        return <span className="px-2 py-1 text-xs font-bold bg-red-600 text-white rounded">CRITICAL</span>;
      case "violation":
        return <span className="px-2 py-1 text-xs font-bold bg-orange-600 text-white rounded">VIOLATION</span>;
      case "warning":
        return <span className="px-2 py-1 text-xs font-bold bg-yellow-600 text-white rounded">WARNING</span>;
      default:
        return <span className="px-2 py-1 text-xs font-bold bg-gray-600 text-white rounded">INFO</span>;
    }
  };

  const getFrameworkLabel = (framework: string) => {
    const labels: Record<string, string> = {
      "4th_amendment": "4th Amendment",
      "5th_amendment": "5th Amendment",
      "14th_amendment": "14th Amendment",
      "florida_statutes": "Florida Statutes",
      "rbpd_general_orders": "RBPD General Orders",
      "cjis_security_policy": "CJIS Security Policy",
      "nist_800_53": "NIST 800-53",
      "nij_standards": "NIJ Standards",
    };
    return labels[framework] || framework;
  };

  const filteredViolations = violations.filter((v) => {
    if (filter === "all") return true;
    if (filter === "critical") return v.severity === "critical" || v.severity === "emergency";
    if (filter === "escalated") return v.escalated;
    if (filter === "blocked") return v.blocked;
    if (filter === "unreviewed") return !v.reviewed_by;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-4 rounded-lg border border-green-700 bg-green-900/30">
          <div className="text-sm text-green-400">Approval Rate</div>
          <div className="text-2xl font-bold text-green-400">
            {((summary?.approval_rate || 0) * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-green-400/75 mt-1">{summary?.approved} approved</div>
        </div>

        <div className="p-4 rounded-lg border border-red-700 bg-red-900/30">
          <div className="text-sm text-red-400">Blocked Actions</div>
          <div className="text-2xl font-bold text-red-400">{summary?.blocked}</div>
          <div className="text-xs text-red-400/75 mt-1">Compliance violations</div>
        </div>

        <div className="p-4 rounded-lg border border-orange-700 bg-orange-900/30">
          <div className="text-sm text-orange-400">Critical Violations</div>
          <div className="text-2xl font-bold text-orange-400">{summary?.critical_violations}</div>
          <div className="text-xs text-orange-400/75 mt-1">Requires attention</div>
        </div>

        <div className="p-4 rounded-lg border border-yellow-700 bg-yellow-900/30">
          <div className="text-sm text-yellow-400">Escalated</div>
          <div className="text-2xl font-bold text-yellow-400">{summary?.escalated_violations}</div>
          <div className="text-xs text-yellow-400/75 mt-1">Pending review</div>
        </div>

        <div className="p-4 rounded-lg border border-blue-700 bg-blue-900/30">
          <div className="text-sm text-blue-400">Bias Audits</div>
          <div className="text-2xl font-bold text-blue-400">{summary?.bias_audits_conducted}</div>
          <div className="text-xs text-blue-400/75 mt-1">Completed this period</div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold flex items-center">
              <svg className="w-5 h-5 mr-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Ethics Violation Feed
            </h3>
            <div className="flex space-x-2">
              {["all", "critical", "escalated", "blocked", "unreviewed"].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1 text-sm rounded ${
                    filter === f
                      ? "bg-purple-600 text-white"
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="divide-y divide-gray-700">
          {filteredViolations.map((violation) => (
            <div key={violation.violation_id} className="p-4 hover:bg-gray-700/50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    {getSeverityBadge(violation.severity)}
                    <span className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded">
                      {getFrameworkLabel(violation.framework)}
                    </span>
                    {violation.blocked && (
                      <span className="px-2 py-1 text-xs bg-red-900/50 text-red-400 rounded">BLOCKED</span>
                    )}
                    {violation.escalated && (
                      <span className="px-2 py-1 text-xs bg-yellow-900/50 text-yellow-400 rounded">ESCALATED</span>
                    )}
                  </div>
                  
                  <div className="font-medium">{violation.description}</div>
                  
                  <div className="mt-2 text-sm text-gray-400 space-y-1">
                    <div>
                      <span className="text-gray-500">Type:</span> {violation.violation_type.replace(/_/g, " ")}
                    </div>
                    <div>
                      <span className="text-gray-500">Engine:</span> {violation.engine}
                    </div>
                    <div>
                      <span className="text-gray-500">Action:</span> {violation.action_attempted}
                    </div>
                    {violation.reviewed_by && (
                      <div>
                        <span className="text-gray-500">Reviewed by:</span> {violation.reviewed_by} - {violation.review_decision}
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-2 text-xs text-gray-500">
                    {violation.violation_id} | {new Date(violation.timestamp).toLocaleString()}
                  </div>
                </div>
                
                <div className="flex flex-col space-y-2 ml-4">
                  {!violation.reviewed_by && (
                    <>
                      <button className="px-3 py-1 text-sm bg-green-600 hover:bg-green-700 text-white rounded">
                        Approve
                      </button>
                      <button className="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded">
                        Deny
                      </button>
                    </>
                  )}
                  <button className="px-3 py-1 text-sm bg-gray-600 hover:bg-gray-500 text-white rounded">
                    Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

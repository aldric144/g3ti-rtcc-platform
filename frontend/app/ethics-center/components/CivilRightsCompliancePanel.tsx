"use client";

import React, { useState } from "react";

interface Violation {
  id: string;
  type: string;
  description: string;
  legalBasis: string;
  citation: string;
  severity: string;
  blocked: boolean;
}

interface ComplianceCheck {
  id: string;
  timestamp: string;
  actionType: string;
  status: string;
  violations: Violation[];
  constitutionalConcerns: string[];
  blocked: boolean;
}

const mockComplianceChecks: ComplianceCheck[] = [
  {
    id: "cr-001",
    timestamp: "2024-01-15T14:45:00Z",
    actionType: "surveillance",
    status: "COMPLIANT",
    violations: [],
    constitutionalConcerns: [],
    blocked: false,
  },
  {
    id: "cr-002",
    timestamp: "2024-01-15T14:30:00Z",
    actionType: "search",
    status: "REQUIRES_REVIEW",
    violations: [
      {
        id: "v-001",
        type: "WARRANTLESS_SEARCH",
        description: "Search conducted without warrant or valid exception",
        legalBasis: "FOURTH_AMENDMENT",
        citation: "U.S. Const. amend. IV",
        severity: "HIGH",
        blocked: false,
      },
    ],
    constitutionalConcerns: ["Fourth Amendment - Warrant Requirement"],
    blocked: false,
  },
  {
    id: "cr-003",
    timestamp: "2024-01-15T14:15:00Z",
    actionType: "drone_surveillance",
    status: "NON_COMPLIANT_BLOCKED",
    violations: [
      {
        id: "v-002",
        type: "SURVEILLANCE_OVERREACH",
        description: "Drone surveillance exceeds 24-hour limit without warrant",
        legalBasis: "FLORIDA_STATUTE",
        citation: "Fla. Stat. § 934.50",
        severity: "CRITICAL",
        blocked: true,
      },
      {
        id: "v-003",
        type: "PRIVACY_VIOLATION",
        description: "Surveillance of private property without consent",
        legalBasis: "FLORIDA_CONSTITUTION",
        citation: "Fla. Const. art. I, § 23",
        severity: "HIGH",
        blocked: true,
      },
    ],
    constitutionalConcerns: ["Florida Privacy Right", "Fourth Amendment"],
    blocked: true,
  },
];

const complianceRules = [
  { id: "R-001", name: "Fourth Amendment - Warrant Requirement", framework: "U.S. Constitution", status: "active" },
  { id: "R-002", name: "Fourth Amendment - Probable Cause", framework: "U.S. Constitution", status: "active" },
  { id: "R-003", name: "First Amendment - Free Speech", framework: "U.S. Constitution", status: "active" },
  { id: "R-004", name: "First Amendment - Assembly", framework: "U.S. Constitution", status: "active" },
  { id: "R-005", name: "Fourteenth Amendment - Equal Protection", framework: "U.S. Constitution", status: "active" },
  { id: "R-006", name: "Fourteenth Amendment - Due Process", framework: "U.S. Constitution", status: "active" },
  { id: "R-007", name: "Florida Privacy Right", framework: "Florida Constitution", status: "active" },
  { id: "R-008", name: "Florida Drone Surveillance", framework: "Florida Statutes", status: "active" },
  { id: "R-009", name: "Riviera Beach Data Retention", framework: "Municipal Code", status: "active" },
  { id: "R-010", name: "DOJ Use of Force Guidelines", framework: "Federal Guidelines", status: "active" },
  { id: "R-011", name: "CJIS Security Policy", framework: "Federal Policy", status: "active" },
  { id: "R-012", name: "NIST AI Risk Management", framework: "Federal Framework", status: "active" },
  { id: "R-013", name: "Biometric Data Protection", framework: "Florida Statutes", status: "active" },
];

const retentionLimits = [
  { dataType: "Surveillance Footage", limit: 30, unit: "days" },
  { dataType: "Drone Footage", limit: 30, unit: "days" },
  { dataType: "License Plate Data", limit: 90, unit: "days" },
  { dataType: "Facial Recognition Queries", limit: 365, unit: "days" },
  { dataType: "Predictive Analytics", limit: 180, unit: "days" },
  { dataType: "General Records", limit: 2555, unit: "days" },
];

export default function CivilRightsCompliancePanel() {
  const [selectedCheck, setSelectedCheck] = useState<ComplianceCheck | null>(null);
  const [activeSection, setActiveSection] = useState<"checks" | "rules" | "retention">("checks");

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLIANT":
        return "bg-green-500";
      case "REQUIRES_REVIEW":
        return "bg-yellow-500";
      case "NON_COMPLIANT_BLOCKED":
        return "bg-red-500";
      case "CONDITIONAL_APPROVAL":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "COMPLIANT":
        return "Compliant";
      case "REQUIRES_REVIEW":
        return "Review Required";
      case "NON_COMPLIANT_BLOCKED":
        return "Blocked";
      case "CONDITIONAL_APPROVAL":
        return "Conditional";
      default:
        return status;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "text-red-400 bg-red-900/30";
      case "HIGH":
        return "text-orange-400 bg-orange-900/30";
      case "MEDIUM":
        return "text-yellow-400 bg-yellow-900/30";
      case "LOW":
        return "text-green-400 bg-green-900/30";
      default:
        return "text-gray-400 bg-gray-900/30";
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-sm text-gray-400">Total Checks</div>
          <div className="text-2xl font-bold text-white">2,156</div>
          <div className="text-xs text-gray-500 mt-1">Last 30 days</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
          <div className="text-sm text-gray-400">Compliant</div>
          <div className="text-2xl font-bold text-green-400">2,089</div>
          <div className="text-xs text-green-500 mt-1">96.9% compliance</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
          <div className="text-sm text-gray-400">Review Required</div>
          <div className="text-2xl font-bold text-yellow-400">54</div>
          <div className="text-xs text-yellow-500 mt-1">2.5% review rate</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <div className="text-sm text-gray-400">Blocked</div>
          <div className="text-2xl font-bold text-red-400">13</div>
          <div className="text-xs text-red-500 mt-1">0.6% block rate</div>
        </div>
      </div>

      <div className="flex space-x-2 border-b border-gray-700 pb-2">
        <button
          onClick={() => setActiveSection("checks")}
          className={`px-4 py-2 rounded-t text-sm ${
            activeSection === "checks" ? "bg-gray-800 text-white" : "text-gray-400 hover:text-white"
          }`}
        >
          Compliance Checks
        </button>
        <button
          onClick={() => setActiveSection("rules")}
          className={`px-4 py-2 rounded-t text-sm ${
            activeSection === "rules" ? "bg-gray-800 text-white" : "text-gray-400 hover:text-white"
          }`}
        >
          Active Rules ({complianceRules.length})
        </button>
        <button
          onClick={() => setActiveSection("retention")}
          className={`px-4 py-2 rounded-t text-sm ${
            activeSection === "retention" ? "bg-gray-800 text-white" : "text-gray-400 hover:text-white"
          }`}
        >
          Data Retention Limits
        </button>
      </div>

      {activeSection === "checks" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-white">Recent Compliance Checks</h3>
            </div>
            <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
              {mockComplianceChecks.map((check) => (
                <div
                  key={check.id}
                  onClick={() => setSelectedCheck(check)}
                  className={`p-4 cursor-pointer hover:bg-gray-750 transition-colors ${
                    selectedCheck?.id === check.id ? "bg-gray-750" : ""
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className={`w-3 h-3 rounded-full ${getStatusColor(check.status)}`}></span>
                      <div>
                        <div className="text-sm font-medium text-white capitalize">
                          {check.actionType.replace(/_/g, " ")}
                        </div>
                        <div className="text-xs text-gray-400">
                          {new Date(check.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      check.status === "COMPLIANT" ? "bg-green-900 text-green-300" :
                      check.status === "REQUIRES_REVIEW" ? "bg-yellow-900 text-yellow-300" :
                      "bg-red-900 text-red-300"
                    }`}>
                      {getStatusLabel(check.status)}
                    </span>
                  </div>
                  {check.violations.length > 0 && (
                    <div className="mt-2 text-xs text-red-400">
                      {check.violations.length} violation(s) detected
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-white">Check Details</h3>
            </div>
            {selectedCheck ? (
              <div className="p-4 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs text-gray-400">Check ID</span>
                    <div className="text-sm text-white font-mono">{selectedCheck.id}</div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Action Type</span>
                    <div className="text-sm text-white capitalize">{selectedCheck.actionType.replace(/_/g, " ")}</div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Status</span>
                    <div className={`text-sm px-2 py-0.5 rounded inline-block ${
                      selectedCheck.status === "COMPLIANT" ? "bg-green-900 text-green-300" :
                      selectedCheck.status === "REQUIRES_REVIEW" ? "bg-yellow-900 text-yellow-300" :
                      "bg-red-900 text-red-300"
                    }`}>
                      {getStatusLabel(selectedCheck.status)}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Blocked</span>
                    <div className={`text-sm ${selectedCheck.blocked ? "text-red-400" : "text-green-400"}`}>
                      {selectedCheck.blocked ? "Yes" : "No"}
                    </div>
                  </div>
                </div>

                {selectedCheck.violations.length > 0 && (
                  <div className="border-t border-gray-700 pt-4">
                    <h4 className="text-sm font-semibold text-white mb-3">Violations</h4>
                    <div className="space-y-3">
                      {selectedCheck.violations.map((violation) => (
                        <div key={violation.id} className="bg-gray-900 rounded p-3 border border-gray-700">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-white">{violation.type.replace(/_/g, " ")}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${getSeverityColor(violation.severity)}`}>
                              {violation.severity}
                            </span>
                          </div>
                          <p className="text-xs text-gray-400 mb-2">{violation.description}</p>
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-blue-400">{violation.legalBasis.replace(/_/g, " ")}</span>
                            <span className="text-gray-500">{violation.citation}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedCheck.constitutionalConcerns.length > 0 && (
                  <div className="border-t border-gray-700 pt-4">
                    <h4 className="text-sm font-semibold text-white mb-2">Constitutional Concerns</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedCheck.constitutionalConcerns.map((concern, idx) => (
                        <span key={idx} className="text-xs bg-red-900/30 text-red-300 px-2 py-1 rounded border border-red-700">
                          {concern}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                Select a check to view details
              </div>
            )}
          </div>
        </div>
      )}

      {activeSection === "rules" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Active Compliance Rules</h3>
            <p className="text-sm text-gray-400 mt-1">13 rules governing civil rights compliance</p>
          </div>
          <div className="divide-y divide-gray-700">
            {complianceRules.map((rule) => (
              <div key={rule.id} className="p-4 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className="text-xs text-gray-500 font-mono">{rule.id}</span>
                  <div>
                    <div className="text-sm font-medium text-white">{rule.name}</div>
                    <div className="text-xs text-gray-400">{rule.framework}</div>
                  </div>
                </div>
                <span className="text-xs px-2 py-1 rounded bg-green-900 text-green-300">
                  Active
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeSection === "retention" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Data Retention Limits</h3>
            <p className="text-sm text-gray-400 mt-1">Riviera Beach municipal code compliance</p>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {retentionLimits.map((item) => (
                <div key={item.dataType} className="bg-gray-900 rounded-lg p-4 border border-gray-700">
                  <div className="text-sm text-gray-400">{item.dataType}</div>
                  <div className="text-2xl font-bold text-white mt-1">
                    {item.limit} <span className="text-sm font-normal text-gray-500">{item.unit}</span>
                  </div>
                  <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${Math.min(100, (item.limit / 2555) * 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

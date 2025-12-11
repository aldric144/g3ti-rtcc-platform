"use client";

import React, { useState, useEffect } from "react";

interface VulnerabilityItem {
  id: string;
  name: string;
  severity: string;
  cvss_score: number;
  affected_system: string;
  patch_available: boolean;
  patch_id: string | null;
  description: string;
  mitigation: string;
}

interface PatchStatus {
  system: string;
  total_patches: number;
  applied: number;
  pending: number;
  critical_pending: number;
  last_updated: string;
}

interface HardeningRecommendation {
  id: string;
  category: string;
  recommendation: string;
  priority: string;
  effort: string;
  impact: string;
  status: string;
}

export default function SystemHardeningConsole() {
  const [vulnerabilities, setVulnerabilities] = useState<VulnerabilityItem[]>([]);
  const [patchStatus, setPatchStatus] = useState<PatchStatus[]>([]);
  const [recommendations, setRecommendations] = useState<HardeningRecommendation[]>([]);
  const [selectedVuln, setSelectedVuln] = useState<VulnerabilityItem | null>(null);
  const [overallScore, setOverallScore] = useState(75);

  useEffect(() => {
    loadMockData();
  }, []);

  const loadMockData = () => {
    setVulnerabilities([
      {
        id: "CVE-2024-1234",
        name: "OpenSSL Buffer Overflow",
        severity: "CRITICAL",
        cvss_score: 9.8,
        affected_system: "Web Server",
        patch_available: true,
        patch_id: "PATCH-2024-001",
        description: "Remote code execution vulnerability in OpenSSL",
        mitigation: "Apply patch PATCH-2024-001 immediately",
      },
      {
        id: "CVE-2024-5678",
        name: "SQL Injection in Legacy App",
        severity: "HIGH",
        cvss_score: 8.5,
        affected_system: "Records Management",
        patch_available: false,
        patch_id: null,
        description: "SQL injection vulnerability in legacy application",
        mitigation: "Implement input validation and parameterized queries",
      },
      {
        id: "CVE-2024-9012",
        name: "Weak TLS Configuration",
        severity: "MEDIUM",
        cvss_score: 5.3,
        affected_system: "Email Server",
        patch_available: true,
        patch_id: "CONFIG-2024-003",
        description: "TLS 1.0/1.1 still enabled",
        mitigation: "Disable TLS 1.0/1.1, enable TLS 1.3",
      },
    ]);

    setPatchStatus([
      {
        system: "Domain Controllers",
        total_patches: 45,
        applied: 42,
        pending: 3,
        critical_pending: 1,
        last_updated: "2024-12-10",
      },
      {
        system: "Web Servers",
        total_patches: 32,
        applied: 28,
        pending: 4,
        critical_pending: 2,
        last_updated: "2024-12-09",
      },
      {
        system: "Database Servers",
        total_patches: 28,
        applied: 27,
        pending: 1,
        critical_pending: 0,
        last_updated: "2024-12-10",
      },
      {
        system: "Workstations",
        total_patches: 156,
        applied: 148,
        pending: 8,
        critical_pending: 2,
        last_updated: "2024-12-08",
      },
    ]);

    setRecommendations([
      {
        id: "REC-001",
        category: "Network",
        recommendation: "Implement network segmentation for CJIS systems",
        priority: "HIGH",
        effort: "HIGH",
        impact: "HIGH",
        status: "IN_PROGRESS",
      },
      {
        id: "REC-002",
        category: "Authentication",
        recommendation: "Enable MFA for all administrative accounts",
        priority: "CRITICAL",
        effort: "MEDIUM",
        impact: "HIGH",
        status: "COMPLETED",
      },
      {
        id: "REC-003",
        category: "Encryption",
        recommendation: "Migrate to post-quantum cryptography",
        priority: "MEDIUM",
        effort: "HIGH",
        impact: "HIGH",
        status: "PLANNED",
      },
      {
        id: "REC-004",
        category: "Monitoring",
        recommendation: "Deploy EDR on all endpoints",
        priority: "HIGH",
        effort: "MEDIUM",
        impact: "HIGH",
        status: "IN_PROGRESS",
      },
    ]);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "CRITICAL":
        return "text-red-400";
      case "HIGH":
        return "text-orange-400";
      case "MEDIUM":
        return "text-yellow-400";
      default:
        return "text-green-400";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "bg-green-500/30 text-green-400";
      case "IN_PROGRESS":
        return "bg-yellow-500/30 text-yellow-400";
      case "PLANNED":
        return "bg-blue-500/30 text-blue-400";
      default:
        return "bg-gray-500/30 text-gray-400";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  const totalPending = patchStatus.reduce((sum, p) => sum + p.pending, 0);
  const criticalPending = patchStatus.reduce((sum, p) => sum + p.critical_pending, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-green-400">System Hardening Console</h2>
        <button
          onClick={loadMockData}
          className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg"
        >
          Run Security Scan
        </button>
      </div>

      <div className="grid grid-cols-5 gap-4">
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 text-center">
          <div className={`text-4xl font-bold ${getScoreColor(overallScore)}`}>
            {overallScore}
          </div>
          <div className="text-sm text-gray-400">Security Score</div>
        </div>
        <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-400">
            {vulnerabilities.filter((v) => v.severity === "CRITICAL").length}
          </div>
          <div className="text-sm text-red-300">Critical Vulns</div>
        </div>
        <div className="bg-orange-900/30 border border-orange-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-orange-400">{totalPending}</div>
          <div className="text-sm text-orange-300">Pending Patches</div>
        </div>
        <div className="bg-purple-900/30 border border-purple-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-purple-400">{criticalPending}</div>
          <div className="text-sm text-purple-300">Critical Patches</div>
        </div>
        <div className="bg-green-900/30 border border-green-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-400">
            {recommendations.filter((r) => r.status === "COMPLETED").length}/{recommendations.length}
          </div>
          <div className="text-sm text-green-300">Recommendations</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-300">Vulnerability Scoring</h3>
            
            <div className="space-y-3">
              {vulnerabilities.map((vuln) => (
                <div
                  key={vuln.id}
                  className={`p-4 rounded-lg border cursor-pointer hover:opacity-80 ${
                    vuln.severity === "CRITICAL"
                      ? "bg-red-900/20 border-red-500"
                      : vuln.severity === "HIGH"
                      ? "bg-orange-900/20 border-orange-500"
                      : "bg-gray-700 border-gray-600"
                  }`}
                  onClick={() => setSelectedVuln(vuln)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <span className="font-mono text-sm text-gray-400">{vuln.id}</span>
                      <span className="font-semibold">{vuln.name}</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(vuln.severity)}`}>
                        {vuln.severity}
                      </span>
                      <span className={`font-bold ${
                        vuln.cvss_score >= 9 ? "text-red-400" :
                        vuln.cvss_score >= 7 ? "text-orange-400" :
                        vuln.cvss_score >= 4 ? "text-yellow-400" : "text-green-400"
                      }`}>
                        CVSS: {vuln.cvss_score}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">System: {vuln.affected_system}</span>
                    <span className={vuln.patch_available ? "text-green-400" : "text-red-400"}>
                      {vuln.patch_available ? `Patch: ${vuln.patch_id}` : "No Patch Available"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-300">Patch Readiness</h3>
            
            <div className="space-y-4">
              {patchStatus.map((status) => (
                <div key={status.system} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold">{status.system}</span>
                    <span className="text-sm text-gray-400">
                      Last updated: {status.last_updated}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 mb-2">
                    <div className="flex-1">
                      <div className="w-full bg-gray-600 rounded-full h-3">
                        <div
                          className="bg-green-500 h-3 rounded-full"
                          style={{ width: `${(status.applied / status.total_patches) * 100}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-sm">
                      {status.applied}/{status.total_patches}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-yellow-400">Pending: {status.pending}</span>
                    {status.critical_pending > 0 && (
                      <span className="text-red-400">Critical: {status.critical_pending}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-300">Suggested Mitigations</h3>
            
            <div className="space-y-3">
              {recommendations.map((rec) => (
                <div
                  key={rec.id}
                  className="bg-gray-700 rounded-lg p-3"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-sm font-semibold ${getPriorityColor(rec.priority)}`}>
                      {rec.priority}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(rec.status)}`}>
                      {rec.status.replace("_", " ")}
                    </span>
                  </div>
                  <div className="text-sm text-white mb-2">{rec.recommendation}</div>
                  <div className="flex items-center space-x-4 text-xs text-gray-400">
                    <span>Category: {rec.category}</span>
                    <span>Effort: {rec.effort}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {selectedVuln && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-300">Vulnerability Details</h3>
                <button
                  onClick={() => setSelectedVuln(null)}
                  className="text-gray-400 hover:text-white"
                >
                  Close
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-400">CVE ID</label>
                  <div className="text-white font-mono">{selectedVuln.id}</div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Name</label>
                  <div className="text-white">{selectedVuln.name}</div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">CVSS Score</label>
                  <div className={`text-2xl font-bold ${
                    selectedVuln.cvss_score >= 9 ? "text-red-400" :
                    selectedVuln.cvss_score >= 7 ? "text-orange-400" : "text-yellow-400"
                  }`}>
                    {selectedVuln.cvss_score}
                  </div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Description</label>
                  <div className="text-white text-sm">{selectedVuln.description}</div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Mitigation</label>
                  <div className="text-yellow-400 text-sm">{selectedVuln.mitigation}</div>
                </div>
                {selectedVuln.patch_available && (
                  <button className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg">
                    Apply Patch: {selectedVuln.patch_id}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";

interface DataLakeStatistics {
  total_incidents: number;
  total_offenders: number;
  total_partitions: number;
  jurisdictions: string[];
  date_range: {
    earliest: string | null;
    latest: string | null;
  };
  storage_size_bytes: number;
}

interface QualityMetrics {
  overall_quality_score: number;
  completeness_score: number;
  accuracy_score: number;
  consistency_score: number;
  timeliness_score: number;
  metrics_by_field: Record<string, number>;
  issues: Array<{ field: string; issue: string; count: number }>;
}

interface ETLStatus {
  is_running: boolean;
  total_jobs: number;
  enabled_jobs: number;
  running_jobs: number;
  paused_jobs: number;
  total_executions: number;
  recent_failures: number;
}

interface RetentionPolicy {
  id: string;
  name: string;
  action: string;
  retention_days: number;
  status: string;
}

export function DataLakeStats() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DataLakeStatistics | null>(null);
  const [quality, setQuality] = useState<QualityMetrics | null>(null);
  const [etlStatus, setEtlStatus] = useState<ETLStatus | null>(null);
  const [policies, setPolicies] = useState<RetentionPolicy[]>([]);
  const [activeSection, setActiveSection] = useState<
    "overview" | "quality" | "etl" | "governance"
  >("overview");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, qualityRes, etlRes, policiesRes] = await Promise.all([
        fetch("/api/data-lake/stats"),
        fetch("/api/data-lake/governance/quality"),
        fetch("/api/data-lake/etl/status"),
        fetch("/api/data-lake/governance/retention"),
      ]);

      const [statsData, qualityData, etlData, policiesData] = await Promise.all(
        [statsRes.json(), qualityRes.json(), etlRes.json(), policiesRes.json()]
      );

      setStats(statsData);
      setQuality(qualityData);
      setEtlStatus(etlData);
      setPolicies(policiesData.policies || []);
    } catch (error) {
      console.error("Failed to load data lake stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-400";
    if (score >= 70) return "text-yellow-400";
    if (score >= 50) return "text-orange-400";
    return "text-red-400";
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 90) return "bg-green-500";
    if (score >= 70) return "bg-yellow-500";
    if (score >= 50) return "bg-orange-500";
    return "bg-red-500";
  };

  const sections = [
    { id: "overview" as const, label: "Overview", icon: "📊" },
    { id: "quality" as const, label: "Data Quality", icon: "✓" },
    { id: "etl" as const, label: "ETL Pipelines", icon: "⚙️" },
    { id: "governance" as const, label: "Governance", icon: "🔒" },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl text-gray-400">Loading data lake statistics...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex space-x-2 mb-6">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
              activeSection === section.id
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            <span>{section.icon}</span>
            <span>{section.label}</span>
          </button>
        ))}
      </div>

      {activeSection === "overview" && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Total Incidents</div>
              <div className="text-3xl font-bold text-blue-400">
                {stats.total_incidents.toLocaleString()}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Total Offenders</div>
              <div className="text-3xl font-bold text-purple-400">
                {stats.total_offenders.toLocaleString()}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Partitions</div>
              <div className="text-3xl font-bold text-green-400">
                {stats.total_partitions.toLocaleString()}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Storage Size</div>
              <div className="text-3xl font-bold text-yellow-400">
                {formatBytes(stats.storage_size_bytes)}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Jurisdictions</h3>
              <div className="flex flex-wrap gap-2">
                {stats.jurisdictions.length > 0 ? (
                  stats.jurisdictions.map((j) => (
                    <span
                      key={j}
                      className="bg-blue-900 text-blue-200 px-3 py-1 rounded-full"
                    >
                      {j}
                    </span>
                  ))
                ) : (
                  <span className="text-gray-500">No jurisdictions configured</span>
                )}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Date Range</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-400">Earliest Record</div>
                  <div className="text-lg font-semibold">
                    {stats.date_range.earliest || "N/A"}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Latest Record</div>
                  <div className="text-lg font-semibold">
                    {stats.date_range.latest || "N/A"}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeSection === "quality" && quality && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Overall Quality Score</h3>
            <div className="flex items-center space-x-4">
              <div
                className={`text-5xl font-bold ${getScoreColor(quality.overall_quality_score)}`}
              >
                {quality.overall_quality_score.toFixed(0)}%
              </div>
              <div className="flex-1">
                <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getScoreBarColor(quality.overall_quality_score)}`}
                    style={{ width: `${quality.overall_quality_score}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Completeness", score: quality.completeness_score },
              { label: "Accuracy", score: quality.accuracy_score },
              { label: "Consistency", score: quality.consistency_score },
              { label: "Timeliness", score: quality.timeliness_score },
            ].map((metric) => (
              <div key={metric.label} className="bg-gray-800 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">{metric.label}</div>
                <div
                  className={`text-2xl font-bold ${getScoreColor(metric.score)}`}
                >
                  {metric.score.toFixed(0)}%
                </div>
                <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getScoreBarColor(metric.score)}`}
                    style={{ width: `${metric.score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {quality.issues.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Quality Issues</h3>
              <div className="space-y-2">
                {quality.issues.map((issue, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between bg-gray-700 px-4 py-3 rounded"
                  >
                    <div>
                      <span className="font-medium">{issue.field}</span>
                      <span className="text-gray-400 mx-2">-</span>
                      <span className="text-gray-300">{issue.issue}</span>
                    </div>
                    <span className="bg-red-900 text-red-200 px-2 py-1 rounded text-sm">
                      {issue.count} records
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeSection === "etl" && etlStatus && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Scheduler Status</div>
              <div
                className={`text-2xl font-bold ${etlStatus.is_running ? "text-green-400" : "text-red-400"}`}
              >
                {etlStatus.is_running ? "Running" : "Stopped"}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Total Jobs</div>
              <div className="text-2xl font-bold text-blue-400">
                {etlStatus.total_jobs}
              </div>
              <div className="text-sm text-gray-500">
                {etlStatus.enabled_jobs} enabled
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Running Jobs</div>
              <div className="text-2xl font-bold text-yellow-400">
                {etlStatus.running_jobs}
              </div>
              <div className="text-sm text-gray-500">
                {etlStatus.paused_jobs} paused
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Recent Failures</div>
              <div
                className={`text-2xl font-bold ${etlStatus.recent_failures > 0 ? "text-red-400" : "text-green-400"}`}
              >
                {etlStatus.recent_failures}
              </div>
              <div className="text-sm text-gray-500">
                of {etlStatus.total_executions} executions
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">ETL Jobs</h3>
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                + Create Job
              </button>
            </div>

            <div className="text-center text-gray-500 py-8">
              <div className="text-4xl mb-2">⚙️</div>
              <p>No ETL jobs configured yet</p>
              <p className="text-sm">Create a job to start ingesting data</p>
            </div>
          </div>
        </div>
      )}

      {activeSection === "governance" && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Retention Policies</h3>
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                + Add Policy
              </button>
            </div>

            {policies.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-gray-700">
                      <th className="pb-3">Policy Name</th>
                      <th className="pb-3">Action</th>
                      <th className="pb-3">Retention Days</th>
                      <th className="pb-3">Status</th>
                      <th className="pb-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {policies.map((policy) => (
                      <tr
                        key={policy.id}
                        className="border-b border-gray-700"
                      >
                        <td className="py-3">{policy.name}</td>
                        <td className="py-3 capitalize">{policy.action}</td>
                        <td className="py-3">{policy.retention_days} days</td>
                        <td className="py-3">
                          <span
                            className={`px-2 py-1 rounded text-xs ${
                              policy.status === "active"
                                ? "bg-green-900 text-green-200"
                                : "bg-gray-700 text-gray-300"
                            }`}
                          >
                            {policy.status}
                          </span>
                        </td>
                        <td className="py-3">
                          <button className="text-blue-400 hover:text-blue-300 mr-3">
                            Edit
                          </button>
                          <button className="text-red-400 hover:text-red-300">
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <div className="text-4xl mb-2">🔒</div>
                <p>No retention policies configured</p>
                <p className="text-sm">
                  Add policies to manage data lifecycle
                </p>
              </div>
            )}
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">CJIS Compliance</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-700 rounded p-4">
                <div className="flex items-center justify-between">
                  <span>Access Controls</span>
                  <span className="text-green-400">Enabled</span>
                </div>
              </div>
              <div className="bg-gray-700 rounded p-4">
                <div className="flex items-center justify-between">
                  <span>Audit Logging</span>
                  <span className="text-green-400">Enabled</span>
                </div>
              </div>
              <div className="bg-gray-700 rounded p-4">
                <div className="flex items-center justify-between">
                  <span>Data Encryption</span>
                  <span className="text-green-400">AES-256</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Recent Audit Log</h3>
              <button className="text-blue-400 hover:text-blue-300 text-sm">
                View All
              </button>
            </div>

            <div className="text-center text-gray-500 py-8">
              <div className="text-4xl mb-2">📋</div>
              <p>No recent audit entries</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <button
          onClick={loadData}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded flex items-center space-x-2"
        >
          <span>🔄</span>
          <span>Refresh Data</span>
        </button>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";

interface SARReport {
  id: string;
  sarNumber: string;
  status: "draft" | "pending_review" | "approved" | "submitted" | "rejected";
  behaviorCategory: string;
  threatLevel: string;
  activityDate: string;
  createdAt: string;
}

interface SARForm {
  behaviorCategory: string;
  activityDate: string;
  activityTime: string;
  city: string;
  state: string;
  narrative: string;
  threatAssessment: string;
  behaviorIndicators: string[];
}

export function SARSubmissionPanel() {
  const [reports, setReports] = useState<SARReport[]>([]);
  const [sarForm, setSarForm] = useState<SARForm>({
    behaviorCategory: "observation_surveillance",
    activityDate: "",
    activityTime: "",
    city: "",
    state: "",
    narrative: "",
    threatAssessment: "unknown",
    behaviorIndicators: [],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const behaviorCategories = [
    { value: "observation_surveillance", label: "Observation/Surveillance" },
    { value: "photography", label: "Photography" },
    { value: "breach_intrusion", label: "Breach/Intrusion" },
    { value: "elicitation", label: "Elicitation" },
    { value: "weapons_explosives", label: "Weapons/Explosives" },
    { value: "cyber_attack", label: "Cyber Attack" },
    { value: "expressed_threat", label: "Expressed Threat" },
    { value: "testing_security", label: "Testing Security" },
    { value: "theft_loss", label: "Theft/Loss" },
    { value: "sabotage_tampering", label: "Sabotage/Tampering" },
    { value: "aviation", label: "Aviation" },
    { value: "critical_infrastructure", label: "Critical Infrastructure" },
    { value: "other", label: "Other" },
  ];

  const threatLevels = [
    { value: "critical", label: "Critical", color: "bg-red-600" },
    { value: "high", label: "High", color: "bg-orange-600" },
    { value: "medium", label: "Medium", color: "bg-yellow-600" },
    { value: "low", label: "Low", color: "bg-green-600" },
    { value: "unknown", label: "Unknown", color: "bg-gray-600" },
  ];

  const behaviorIndicatorOptions = [
    "photographing_facilities",
    "recording_activities",
    "monitoring_personnel",
    "timing_operations",
    "probing_security",
    "testing_response",
    "unauthorized_access",
    "trespassing",
    "questioning_employees",
    "suspicious_behavior",
  ];

  const states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
  ];

  const handleIndicatorToggle = (indicator: string) => {
    const current = sarForm.behaviorIndicators;
    if (current.includes(indicator)) {
      setSarForm({
        ...sarForm,
        behaviorIndicators: current.filter((i) => i !== indicator),
      });
    } else {
      setSarForm({
        ...sarForm,
        behaviorIndicators: [...current, indicator],
      });
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setResult(null);

    await new Promise((resolve) => setTimeout(resolve, 1500));

    const newReport: SARReport = {
      id: `sar-${Date.now()}`,
      sarNumber: `SAR-${new Date().toISOString().slice(0, 10).replace(/-/g, "")}-${Math.random()
        .toString(36)
        .substr(2, 8)
        .toUpperCase()}`,
      status: "draft",
      behaviorCategory: sarForm.behaviorCategory,
      threatLevel: sarForm.threatAssessment,
      activityDate: sarForm.activityDate || new Date().toISOString().split("T")[0],
      createdAt: new Date().toISOString(),
    };

    setReports([newReport, ...reports]);
    setResult({
      success: true,
      sarNumber: newReport.sarNumber,
      message: `SAR ${newReport.sarNumber} created successfully`,
      data: {
        sar_id: newReport.id,
        behavior_category: sarForm.behaviorCategory,
        threat_assessment: sarForm.threatAssessment,
        activity_location: `${sarForm.city || "Sample City"}, ${sarForm.state || "FL"}`,
        behavior_indicators: sarForm.behaviorIndicators,
        status: "draft",
        ise_sar_version: "1.5",
      },
    });
    setIsSubmitting(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "submitted":
      case "approved":
        return "bg-green-500";
      case "pending_review":
        return "bg-blue-500";
      case "draft":
        return "bg-yellow-500";
      case "rejected":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getThreatColor = (level: string) => {
    const found = threatLevels.find((t) => t.value === level);
    return found?.color || "bg-gray-600";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-2">
          DHS Suspicious Activity Reporting (SAR)
        </h2>
        <p className="text-gray-400">
          Create and submit Suspicious Activity Reports following ISE-SAR Functional Standard v1.5.
          Includes behavior categories, indicators, geo/temporal attributes, and threat assessment.
        </p>
      </div>

      {/* SAR Form */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Create SAR</h3>

        {/* Activity Information */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Activity Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Behavior Category</label>
              <select
                value={sarForm.behaviorCategory}
                onChange={(e) => setSarForm({ ...sarForm, behaviorCategory: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                {behaviorCategories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Activity Date</label>
              <input
                type="date"
                value={sarForm.activityDate}
                onChange={(e) => setSarForm({ ...sarForm, activityDate: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Activity Time</label>
              <input
                type="time"
                value={sarForm.activityTime}
                onChange={(e) => setSarForm({ ...sarForm, activityTime: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>
        </div>

        {/* Location */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Activity Location</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">City</label>
              <input
                type="text"
                value={sarForm.city}
                onChange={(e) => setSarForm({ ...sarForm, city: e.target.value })}
                placeholder="City name"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">State</label>
              <select
                value={sarForm.state}
                onChange={(e) => setSarForm({ ...sarForm, state: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <option value="">Select state</option>
                {states.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Threat Assessment */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Threat Assessment</h4>
          <div className="flex flex-wrap gap-2">
            {threatLevels.map((level) => (
              <button
                key={level.value}
                onClick={() => setSarForm({ ...sarForm, threatAssessment: level.value })}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  sarForm.threatAssessment === level.value
                    ? `${level.color} text-white ring-2 ring-white`
                    : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {level.label}
              </button>
            ))}
          </div>
        </div>

        {/* Behavior Indicators */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Behavior Indicators</h4>
          <div className="flex flex-wrap gap-2">
            {behaviorIndicatorOptions.map((indicator) => (
              <button
                key={indicator}
                onClick={() => handleIndicatorToggle(indicator)}
                className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                  sarForm.behaviorIndicators.includes(indicator)
                    ? "bg-red-600 text-white"
                    : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {indicator.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        {/* Narrative */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Narrative</h4>
          <textarea
            value={sarForm.narrative}
            onChange={(e) => setSarForm({ ...sarForm, narrative: e.target.value })}
            placeholder="Describe the suspicious activity in detail (minimum 50 characters)..."
            rows={4}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
          />
          <div className="text-xs text-gray-500 mt-1">
            {sarForm.narrative.length} / 50 minimum characters
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg transition-colors"
        >
          {isSubmitting ? "Creating SAR..." : "Create SAR"}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div
          className={`bg-gray-800 rounded-lg p-6 border ${
            result.success ? "border-green-500" : "border-red-500"
          }`}
        >
          <h3 className="text-lg font-semibold text-white mb-4">
            {result.success ? "SAR Created" : "Creation Failed"}
          </h3>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-gray-300">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Recent SARs */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Recent SAR Reports</h3>
        {reports.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            No SAR reports yet. Create your first SAR above.
          </div>
        ) : (
          <div className="space-y-2">
            {reports.map((report) => (
              <div
                key={report.id}
                className="bg-gray-700/50 rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex items-center space-x-4">
                  <span className="text-2xl">🚨</span>
                  <div>
                    <div className="font-medium text-white font-mono">{report.sarNumber}</div>
                    <div className="text-sm text-gray-400">
                      {report.behaviorCategory.replace(/_/g, " ")} | {report.activityDate}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium text-white ${getThreatColor(
                      report.threatLevel
                    )}`}
                  >
                    {report.threatLevel}
                  </span>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium text-white ${getStatusColor(
                      report.status
                    )}`}
                  >
                    {report.status.replace(/_/g, " ")}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

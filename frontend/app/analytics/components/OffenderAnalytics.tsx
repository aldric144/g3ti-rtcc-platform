"use client";

import { useState } from "react";

interface OffenderProfile {
  offender_id: string;
  jurisdiction: string;
  total_incidents: number;
  risk_score: number;
  risk_level: string;
  risk_factors: string[];
  is_repeat_offender: boolean;
  crime_categories: Record<string, number>;
  escalation_trend: string;
  known_associates: number;
  gang_affiliated: boolean;
}

interface RecidivismAnalysis {
  total_offenders: number;
  repeat_offenders: number;
  repeat_offender_rate: number;
  recidivism_rate_30_day: number;
  recidivism_rate_90_day: number;
  recidivism_rate_1_year: number;
  risk_distribution: Record<string, number>;
  recidivism_trend: string;
}

export function OffenderAnalytics() {
  const [jurisdiction, setJurisdiction] = useState("ATL");
  const [startDate, setStartDate] = useState("2023-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [minRiskScore, setMinRiskScore] = useState(60);
  const [loading, setLoading] = useState(false);
  const [recidivismData, setRecidivismData] =
    useState<RecidivismAnalysis | null>(null);
  const [highRiskOffenders, setHighRiskOffenders] = useState<OffenderProfile[]>(
    []
  );
  const [selectedOffender, setSelectedOffender] =
    useState<OffenderProfile | null>(null);

  const analyzeRecidivism = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        jurisdiction,
        start_date: startDate,
        end_date: endDate,
      });

      const response = await fetch(
        `/api/data-lake/offenders/recidivism?${params}`
      );
      const data = await response.json();
      setRecidivismData(data);

      const highRiskParams = new URLSearchParams({
        jurisdiction,
        min_risk_score: minRiskScore.toString(),
        limit: "50",
      });

      const highRiskResponse = await fetch(
        `/api/data-lake/offenders/high-risk?${highRiskParams}`
      );
      const highRiskData = await highRiskResponse.json();
      setHighRiskOffenders(highRiskData.offenders || []);
    } catch (error) {
      console.error("Failed to analyze recidivism:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "critical":
        return "bg-red-600";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      default:
        return "bg-green-500";
    }
  };

  const getEscalationIcon = (trend: string) => {
    switch (trend) {
      case "escalating":
        return "⬆️";
      case "de-escalating":
        return "⬇️";
      default:
        return "➡️";
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">
          Repeat Offender Analysis Parameters
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Jurisdiction
            </label>
            <select
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value="ATL">Atlanta</option>
              <option value="NYC">New York</option>
              <option value="LAX">Los Angeles</option>
              <option value="CHI">Chicago</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Min Risk Score
            </label>
            <input
              type="number"
              value={minRiskScore}
              onChange={(e) => setMinRiskScore(parseInt(e.target.value))}
              min={0}
              max={100}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            />
          </div>
        </div>

        <button
          onClick={analyzeRecidivism}
          disabled={loading}
          className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze Recidivism"}
        </button>
      </div>

      {recidivismData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400">Total Offenders</div>
              <div className="text-2xl font-bold text-white">
                {recidivismData.total_offenders.toLocaleString()}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400">Repeat Offenders</div>
              <div className="text-2xl font-bold text-red-400">
                {recidivismData.repeat_offenders.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">
                {recidivismData.repeat_offender_rate.toFixed(1)}% of total
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400">30-Day Recidivism</div>
              <div className="text-2xl font-bold text-orange-400">
                {recidivismData.recidivism_rate_30_day.toFixed(1)}%
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400">1-Year Recidivism</div>
              <div className="text-2xl font-bold text-yellow-400">
                {recidivismData.recidivism_rate_1_year.toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
              <div className="space-y-3">
                {Object.entries(recidivismData.risk_distribution).map(
                  ([level, count]) => {
                    const total = Object.values(
                      recidivismData.risk_distribution
                    ).reduce((a, b) => a + b, 0);
                    const percentage = total > 0 ? (count / total) * 100 : 0;
                    return (
                      <div key={level}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="capitalize">{level}</span>
                          <span>
                            {count} ({percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getRiskLevelColor(level)}`}
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  }
                )}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Recidivism Rates</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">30-Day Rate</span>
                  <div className="flex items-center">
                    <div className="w-32 h-3 bg-gray-700 rounded-full overflow-hidden mr-3">
                      <div
                        className="h-full bg-red-500"
                        style={{
                          width: `${recidivismData.recidivism_rate_30_day}%`,
                        }}
                      />
                    </div>
                    <span className="font-semibold">
                      {recidivismData.recidivism_rate_30_day.toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">90-Day Rate</span>
                  <div className="flex items-center">
                    <div className="w-32 h-3 bg-gray-700 rounded-full overflow-hidden mr-3">
                      <div
                        className="h-full bg-orange-500"
                        style={{
                          width: `${recidivismData.recidivism_rate_90_day}%`,
                        }}
                      />
                    </div>
                    <span className="font-semibold">
                      {recidivismData.recidivism_rate_90_day.toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">1-Year Rate</span>
                  <div className="flex items-center">
                    <div className="w-32 h-3 bg-gray-700 rounded-full overflow-hidden mr-3">
                      <div
                        className="h-full bg-yellow-500"
                        style={{
                          width: `${recidivismData.recidivism_rate_1_year}%`,
                        }}
                      />
                    </div>
                    <span className="font-semibold">
                      {recidivismData.recidivism_rate_1_year.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-gray-700">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Trend</span>
                  <span
                    className={`font-semibold ${
                      recidivismData.recidivism_trend === "increasing"
                        ? "text-red-400"
                        : recidivismData.recidivism_trend === "decreasing"
                          ? "text-green-400"
                          : "text-yellow-400"
                    }`}
                  >
                    {recidivismData.recidivism_trend.charAt(0).toUpperCase() +
                      recidivismData.recidivism_trend.slice(1)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {highRiskOffenders.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">
            High-Risk Offenders (Score &gt;= {minRiskScore})
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-gray-700">
                  <th className="pb-3">Offender ID</th>
                  <th className="pb-3">Risk Score</th>
                  <th className="pb-3">Risk Level</th>
                  <th className="pb-3">Incidents</th>
                  <th className="pb-3">Escalation</th>
                  <th className="pb-3">Associates</th>
                  <th className="pb-3">Gang</th>
                  <th className="pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {highRiskOffenders.map((offender) => (
                  <tr
                    key={offender.offender_id}
                    className="border-b border-gray-700 hover:bg-gray-750"
                  >
                    <td className="py-3 font-mono">{offender.offender_id}</td>
                    <td className="py-3">
                      <span className="font-bold text-lg">
                        {offender.risk_score.toFixed(0)}
                      </span>
                    </td>
                    <td className="py-3">
                      <span
                        className={`${getRiskLevelColor(offender.risk_level)} text-white text-xs px-2 py-1 rounded-full`}
                      >
                        {offender.risk_level.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3">{offender.total_incidents}</td>
                    <td className="py-3">
                      {getEscalationIcon(offender.escalation_trend)}{" "}
                      {offender.escalation_trend}
                    </td>
                    <td className="py-3">{offender.known_associates}</td>
                    <td className="py-3">
                      {offender.gang_affiliated ? (
                        <span className="text-red-400">Yes</span>
                      ) : (
                        <span className="text-gray-500">No</span>
                      )}
                    </td>
                    <td className="py-3">
                      <button
                        onClick={() => setSelectedOffender(offender)}
                        className="text-blue-400 hover:text-blue-300"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {selectedOffender && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-semibold">Offender Profile</h3>
              <button
                onClick={() => setSelectedOffender(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <div className="text-sm text-gray-400">Offender ID</div>
                <div className="font-mono">{selectedOffender.offender_id}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Jurisdiction</div>
                <div>{selectedOffender.jurisdiction}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Risk Score</div>
                <div className="text-2xl font-bold">
                  {selectedOffender.risk_score.toFixed(0)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Risk Level</div>
                <span
                  className={`${getRiskLevelColor(selectedOffender.risk_level)} text-white px-3 py-1 rounded-full`}
                >
                  {selectedOffender.risk_level.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="mb-6">
              <div className="text-sm text-gray-400 mb-2">Risk Factors</div>
              <div className="flex flex-wrap gap-2">
                {selectedOffender.risk_factors.map((factor, idx) => (
                  <span
                    key={idx}
                    className="bg-red-900 text-red-200 px-3 py-1 rounded-full text-sm"
                  >
                    {factor}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-6">
              <div className="text-sm text-gray-400 mb-2">Crime Categories</div>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(selectedOffender.crime_categories).map(
                  ([cat, count]) => (
                    <div
                      key={cat}
                      className="flex justify-between bg-gray-700 px-3 py-2 rounded"
                    >
                      <span className="capitalize">{cat}</span>
                      <span className="font-semibold">{count}</span>
                    </div>
                  )
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setSelectedOffender(null)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
              >
                Close
              </button>
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded">
                View Full Timeline
              </button>
            </div>
          </div>
        </div>
      )}

      {!recidivismData && !loading && (
        <div className="bg-gray-800 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">👤</div>
          <h3 className="text-xl font-semibold mb-2">No Analysis Data</h3>
          <p className="text-gray-400">
            Configure your parameters and click &quot;Analyze Recidivism&quot;
            to view repeat offender analytics.
          </p>
        </div>
      )}
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";

interface DomainRiskScore {
  domain: string;
  score: number;
  level: string;
  trend: string;
  contributing_factors: string[];
}

interface RegionalAssessment {
  region: string;
  overall_score: number;
  overall_level: string;
  primary_domain: string;
  secondary_domains: string[];
  forecast_7_day: number;
  forecast_30_day: number;
  domain_scores: Record<string, number>;
}

interface RiskAlert {
  alert_id: string;
  domain: string;
  region: string;
  title: string;
  risk_level: string;
  trigger_factors: string[];
  recommended_response: string;
  expires_at: string;
}

const RISK_DOMAINS = [
  "climate",
  "geopolitical",
  "cyber",
  "supply_chain",
  "health",
  "conflict",
  "economic",
  "infrastructure",
];

export default function RiskFusionDashboard() {
  const [selectedRegion, setSelectedRegion] = useState("Middle East");
  const [assessments, setAssessments] = useState<RegionalAssessment[]>([]);
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [domainScores, setDomainScores] = useState<DomainRiskScore[]>([]);

  useEffect(() => {
    const mockAssessments: RegionalAssessment[] = [
      {
        region: "Middle East",
        overall_score: 78.5,
        overall_level: "HIGH",
        primary_domain: "conflict",
        secondary_domains: ["geopolitical", "economic"],
        forecast_7_day: 82.0,
        forecast_30_day: 85.0,
        domain_scores: {
          climate: 45,
          geopolitical: 85,
          cyber: 55,
          supply_chain: 70,
          health: 50,
          conflict: 92,
          economic: 75,
          infrastructure: 60,
        },
      },
      {
        region: "Eastern Europe",
        overall_score: 82.3,
        overall_level: "CRITICAL",
        primary_domain: "conflict",
        secondary_domains: ["cyber", "economic"],
        forecast_7_day: 85.0,
        forecast_30_day: 88.0,
        domain_scores: {
          climate: 35,
          geopolitical: 90,
          cyber: 80,
          supply_chain: 75,
          health: 45,
          conflict: 95,
          economic: 80,
          infrastructure: 70,
        },
      },
      {
        region: "East Asia",
        overall_score: 65.2,
        overall_level: "HIGH",
        primary_domain: "geopolitical",
        secondary_domains: ["cyber", "supply_chain"],
        forecast_7_day: 68.0,
        forecast_30_day: 72.0,
        domain_scores: {
          climate: 50,
          geopolitical: 80,
          cyber: 70,
          supply_chain: 65,
          health: 40,
          conflict: 55,
          economic: 60,
          infrastructure: 45,
        },
      },
      {
        region: "North America",
        overall_score: 42.1,
        overall_level: "MODERATE",
        primary_domain: "cyber",
        secondary_domains: ["economic", "climate"],
        forecast_7_day: 44.0,
        forecast_30_day: 46.0,
        domain_scores: {
          climate: 55,
          geopolitical: 35,
          cyber: 60,
          supply_chain: 40,
          health: 35,
          conflict: 20,
          economic: 50,
          infrastructure: 30,
        },
      },
    ];
    setAssessments(mockAssessments);

    const mockAlerts: RiskAlert[] = [
      {
        alert_id: "RA-001",
        domain: "conflict",
        region: "Eastern Europe",
        title: "Elevated Conflict Risk in Eastern Europe",
        risk_level: "CRITICAL",
        trigger_factors: ["Active conflict", "Military buildup"],
        recommended_response: "URGENT: Activate contingency plans",
        expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        alert_id: "RA-002",
        domain: "cyber",
        region: "Western Europe",
        title: "Critical Infrastructure Cyber Threat",
        risk_level: "HIGH",
        trigger_factors: ["Ransomware campaigns", "State-sponsored activity"],
        recommended_response: "Enhance network monitoring",
        expires_at: new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString(),
      },
      {
        alert_id: "RA-003",
        domain: "supply_chain",
        region: "East Asia",
        title: "Supply Chain Disruption Risk",
        risk_level: "HIGH",
        trigger_factors: ["Port disruption", "Trade restrictions"],
        recommended_response: "Identify alternative suppliers",
        expires_at: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(),
      },
    ];
    setAlerts(mockAlerts);

    const selectedAssessment = mockAssessments.find(a => a.region === selectedRegion);
    if (selectedAssessment) {
      const scores: DomainRiskScore[] = RISK_DOMAINS.map(domain => ({
        domain,
        score: selectedAssessment.domain_scores[domain] || 30,
        level: selectedAssessment.domain_scores[domain] >= 80 ? "CRITICAL" :
               selectedAssessment.domain_scores[domain] >= 60 ? "HIGH" :
               selectedAssessment.domain_scores[domain] >= 40 ? "MODERATE" : "LOW",
        trend: Math.random() > 0.5 ? "deteriorating" : "stable",
        contributing_factors: ["Factor 1", "Factor 2"],
      }));
      setDomainScores(scores);
    }
  }, [selectedRegion]);

  const getRiskLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case "CRITICAL": return "bg-red-500 text-white";
      case "HIGH": return "bg-orange-500 text-white";
      case "MODERATE": return "bg-yellow-500 text-black";
      case "LOW": return "bg-green-500 text-white";
      default: return "bg-gray-500 text-white";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-red-500";
    if (score >= 60) return "text-orange-500";
    if (score >= 40) return "text-yellow-500";
    return "text-green-500";
  };

  const getBarColor = (score: number) => {
    if (score >= 80) return "bg-red-500";
    if (score >= 60) return "bg-orange-500";
    if (score >= 40) return "bg-yellow-500";
    return "bg-green-500";
  };

  const selectedAssessment = assessments.find(a => a.region === selectedRegion);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Regional Risk Summary</h2>
          <div className="space-y-2">
            {assessments.map(assessment => (
              <button
                key={assessment.region}
                onClick={() => setSelectedRegion(assessment.region)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedRegion === assessment.region
                    ? "bg-blue-600/30 border border-blue-500"
                    : "bg-gray-700/50 hover:bg-gray-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{assessment.region}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${getRiskLevelColor(assessment.overall_level)}`}>
                    {assessment.overall_level}
                  </span>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <div className="flex-1 bg-gray-600 rounded-full h-2 mr-3">
                    <div
                      className={`h-2 rounded-full ${getBarColor(assessment.overall_score)}`}
                      style={{ width: `${assessment.overall_score}%` }}
                    />
                  </div>
                  <span className={`text-sm font-bold ${getScoreColor(assessment.overall_score)}`}>
                    {assessment.overall_score.toFixed(1)}
                  </span>
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Primary: {assessment.primary_domain}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">{selectedRegion} Risk Analysis</h2>
            {selectedAssessment && (
              <span className={`px-3 py-1 rounded ${getRiskLevelColor(selectedAssessment.overall_level)}`}>
                Overall: {selectedAssessment.overall_score.toFixed(1)}
              </span>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {domainScores.map(score => (
              <div key={score.domain} className="bg-gray-700/50 rounded-lg p-3">
                <div className="text-xs text-gray-400 uppercase mb-1">{score.domain.replace("_", " ")}</div>
                <div className={`text-2xl font-bold ${getScoreColor(score.score)}`}>
                  {score.score}
                </div>
                <div className="flex items-center mt-1">
                  <span className={`text-xs px-1.5 py-0.5 rounded ${getRiskLevelColor(score.level)}`}>
                    {score.level}
                  </span>
                  <span className={`text-xs ml-2 ${
                    score.trend === "deteriorating" ? "text-red-400" : "text-gray-400"
                  }`}>
                    {score.trend === "deteriorating" ? "↑" : "→"}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {selectedAssessment && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-700/50 rounded-lg p-4">
                <h3 className="text-sm font-semibold mb-3">7-Day Forecast</h3>
                <div className="flex items-center justify-between">
                  <div className="flex-1 bg-gray-600 rounded-full h-3 mr-3">
                    <div
                      className={`h-3 rounded-full ${getBarColor(selectedAssessment.forecast_7_day)}`}
                      style={{ width: `${selectedAssessment.forecast_7_day}%` }}
                    />
                  </div>
                  <span className={`text-lg font-bold ${getScoreColor(selectedAssessment.forecast_7_day)}`}>
                    {selectedAssessment.forecast_7_day.toFixed(1)}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  {selectedAssessment.forecast_7_day > selectedAssessment.overall_score
                    ? "Risk expected to increase"
                    : "Risk expected to remain stable"}
                </p>
              </div>

              <div className="bg-gray-700/50 rounded-lg p-4">
                <h3 className="text-sm font-semibold mb-3">30-Day Forecast</h3>
                <div className="flex items-center justify-between">
                  <div className="flex-1 bg-gray-600 rounded-full h-3 mr-3">
                    <div
                      className={`h-3 rounded-full ${getBarColor(selectedAssessment.forecast_30_day)}`}
                      style={{ width: `${selectedAssessment.forecast_30_day}%` }}
                    />
                  </div>
                  <span className={`text-lg font-bold ${getScoreColor(selectedAssessment.forecast_30_day)}`}>
                    {selectedAssessment.forecast_30_day.toFixed(1)}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  Secondary risks: {selectedAssessment.secondary_domains.join(", ")}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Active Risk Alerts</h2>
        <div className="space-y-3">
          {alerts.map(alert => (
            <div
              key={alert.alert_id}
              className={`p-4 rounded-lg border-l-4 ${
                alert.risk_level === "CRITICAL"
                  ? "bg-red-900/20 border-red-500"
                  : alert.risk_level === "HIGH"
                  ? "bg-orange-900/20 border-orange-500"
                  : "bg-yellow-900/20 border-yellow-500"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${getRiskLevelColor(alert.risk_level)}`}>
                      {alert.risk_level}
                    </span>
                    <span className="text-sm text-gray-400">{alert.domain}</span>
                    <span className="text-sm text-gray-400">|</span>
                    <span className="text-sm text-gray-400">{alert.region}</span>
                  </div>
                  <h3 className="font-semibold mt-2">{alert.title}</h3>
                  <div className="text-sm text-gray-400 mt-1">
                    Triggers: {alert.trigger_factors.join(", ")}
                  </div>
                </div>
                <span className="text-xs text-gray-500">
                  Expires: {new Date(alert.expires_at).toLocaleString()}
                </span>
              </div>
              <div className="mt-3 p-2 bg-gray-700/50 rounded text-sm">
                <span className="text-gray-400">Recommended: </span>
                <span className="text-blue-400">{alert.recommended_response}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

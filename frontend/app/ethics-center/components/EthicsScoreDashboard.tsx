"use client";

import React, { useState } from "react";

interface ComponentScore {
  component: string;
  score: number;
  weight: number;
  factors: string[];
}

interface EthicsAssessment {
  id: string;
  timestamp: string;
  actionType: string;
  totalScore: number;
  level: string;
  colorCode: string;
  requiredAction: string;
  componentScores: ComponentScore[];
  humanReviewRequired: boolean;
}

const mockAssessments: EthicsAssessment[] = [
  {
    id: "eth-001",
    timestamp: "2024-01-15T15:00:00Z",
    actionType: "patrol_routing",
    totalScore: 92,
    level: "EXCELLENT",
    colorCode: "#22C55E",
    requiredAction: "ALLOW",
    componentScores: [
      { component: "FAIRNESS", score: 95, weight: 0.20, factors: ["No fairness concerns identified"] },
      { component: "CIVIL_RIGHTS", score: 100, weight: 0.20, factors: ["No civil rights concerns identified"] },
      { component: "USE_OF_FORCE", score: 85, weight: 0.15, factors: ["Low use-of-force risk"] },
      { component: "HISTORICAL_DISPARITY", score: 90, weight: 0.15, factors: ["No historical disparity concerns"] },
      { component: "POLICY_COMPLIANCE", score: 100, weight: 0.10, factors: ["Full policy compliance"] },
      { component: "TRANSPARENCY", score: 88, weight: 0.10, factors: ["Full transparency maintained"] },
      { component: "COMMUNITY_IMPACT", score: 85, weight: 0.05, factors: ["Minimal community impact"] },
      { component: "ACCOUNTABILITY", score: 90, weight: 0.05, factors: ["Full accountability maintained"] },
    ],
    humanReviewRequired: false,
  },
  {
    id: "eth-002",
    timestamp: "2024-01-15T14:45:00Z",
    actionType: "surveillance",
    totalScore: 68,
    level: "ACCEPTABLE",
    colorCode: "#EAB308",
    requiredAction: "MODIFY",
    componentScores: [
      { component: "FAIRNESS", score: 70, weight: 0.20, factors: ["Marginal disparate impact: 0.82"] },
      { component: "CIVIL_RIGHTS", score: 65, weight: 0.20, factors: ["Fourth Amendment concern"] },
      { component: "USE_OF_FORCE", score: 85, weight: 0.15, factors: ["Low use-of-force risk"] },
      { component: "HISTORICAL_DISPARITY", score: 60, weight: 0.15, factors: ["Historical disparity in similar actions"] },
      { component: "POLICY_COMPLIANCE", score: 80, weight: 0.10, factors: ["Full policy compliance"] },
      { component: "TRANSPARENCY", score: 55, weight: 0.10, factors: ["Moderate explainability: 0.65"] },
      { component: "COMMUNITY_IMPACT", score: 50, weight: 0.05, factors: ["Moderate community impact: 0.55"] },
      { component: "ACCOUNTABILITY", score: 75, weight: 0.05, factors: ["Full accountability maintained"] },
    ],
    humanReviewRequired: true,
  },
  {
    id: "eth-003",
    timestamp: "2024-01-15T14:30:00Z",
    actionType: "enforcement",
    totalScore: 35,
    level: "CRITICAL",
    colorCode: "#EF4444",
    requiredAction: "BLOCK",
    componentScores: [
      { component: "FAIRNESS", score: 30, weight: 0.20, factors: ["Bias detected in AI output", "Disparate impact ratio: 0.65"] },
      { component: "CIVIL_RIGHTS", score: 0, weight: 0.20, factors: ["Constitutional violation detected"] },
      { component: "USE_OF_FORCE", score: 40, weight: 0.15, factors: ["High force risk: 72", "Excessive force risk identified"] },
      { component: "HISTORICAL_DISPARITY", score: 45, weight: 0.15, factors: ["Historical disparity in similar actions", "Location shows enforcement disparity: 0.42"] },
      { component: "POLICY_COMPLIANCE", score: 60, weight: 0.10, factors: ["Policy violation: Use of force policy"] },
      { component: "TRANSPARENCY", score: 40, weight: 0.10, factors: ["Low explainability: 0.45", "Incomplete audit trail"] },
      { component: "COMMUNITY_IMPACT", score: 25, weight: 0.05, factors: ["High community impact: 0.78", "Protected community affected"] },
      { component: "ACCOUNTABILITY", score: 50, weight: 0.05, factors: ["Documentation incomplete"] },
    ],
    humanReviewRequired: true,
  },
];

const levelDistribution = [
  { level: "EXCELLENT", count: 856, percentage: 68.5, color: "#22C55E" },
  { level: "GOOD", count: 287, percentage: 23.0, color: "#84CC16" },
  { level: "ACCEPTABLE", count: 78, percentage: 6.2, color: "#EAB308" },
  { level: "CONCERNING", count: 22, percentage: 1.8, color: "#F97316" },
  { level: "CRITICAL", count: 7, percentage: 0.5, color: "#EF4444" },
];

export default function EthicsScoreDashboard() {
  const [selectedAssessment, setSelectedAssessment] = useState<EthicsAssessment | null>(null);

  const getLevelBadgeClass = (level: string) => {
    switch (level) {
      case "EXCELLENT":
        return "bg-green-900 text-green-300";
      case "GOOD":
        return "bg-lime-900 text-lime-300";
      case "ACCEPTABLE":
        return "bg-yellow-900 text-yellow-300";
      case "CONCERNING":
        return "bg-orange-900 text-orange-300";
      case "CRITICAL":
        return "bg-red-900 text-red-300";
      default:
        return "bg-gray-900 text-gray-300";
    }
  };

  const getActionBadgeClass = (action: string) => {
    switch (action) {
      case "ALLOW":
        return "bg-green-900 text-green-300";
      case "ALLOW_WITH_LOGGING":
        return "bg-lime-900 text-lime-300";
      case "MODIFY":
        return "bg-yellow-900 text-yellow-300";
      case "REVIEW":
        return "bg-orange-900 text-orange-300";
      case "BLOCK":
        return "bg-red-900 text-red-300";
      default:
        return "bg-gray-900 text-gray-300";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-400";
    if (score >= 75) return "text-lime-400";
    if (score >= 60) return "text-yellow-400";
    if (score >= 40) return "text-orange-400";
    return "text-red-400";
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 90) return "bg-green-500";
    if (score >= 75) return "bg-lime-500";
    if (score >= 60) return "bg-yellow-500";
    if (score >= 40) return "bg-orange-500";
    return "bg-red-500";
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-sm text-gray-400">Average Score</div>
          <div className="text-3xl font-bold text-green-400">87.3</div>
          <div className="text-xs text-gray-500 mt-1">Last 30 days</div>
        </div>
        {levelDistribution.map((item) => (
          <div key={item.level} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400">{item.level}</div>
            <div className="text-2xl font-bold" style={{ color: item.color }}>{item.count}</div>
            <div className="text-xs text-gray-500 mt-1">{item.percentage}%</div>
          </div>
        ))}
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Ethics Level Distribution</h3>
        <div className="flex h-8 rounded-lg overflow-hidden">
          {levelDistribution.map((item) => (
            <div
              key={item.level}
              className="flex items-center justify-center text-xs font-medium text-white"
              style={{ width: `${item.percentage}%`, backgroundColor: item.color }}
              title={`${item.level}: ${item.count} (${item.percentage}%)`}
            >
              {item.percentage > 5 && `${item.percentage}%`}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-400">
          <span>Excellent (90-100)</span>
          <span>Good (75-89)</span>
          <span>Acceptable (60-74)</span>
          <span>Concerning (40-59)</span>
          <span>Critical (0-39)</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Recent Assessments</h3>
          </div>
          <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
            {mockAssessments.map((assessment) => (
              <div
                key={assessment.id}
                onClick={() => setSelectedAssessment(assessment)}
                className={`p-4 cursor-pointer hover:bg-gray-750 transition-colors ${
                  selectedAssessment?.id === assessment.id ? "bg-gray-750" : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div
                      className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
                      style={{ backgroundColor: assessment.colorCode }}
                    >
                      {assessment.totalScore}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-white capitalize">
                        {assessment.actionType.replace(/_/g, " ")}
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(assessment.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs px-2 py-1 rounded ${getLevelBadgeClass(assessment.level)}`}>
                      {assessment.level}
                    </span>
                    {assessment.humanReviewRequired && (
                      <div className="mt-1 text-xs text-yellow-400">Review Required</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Assessment Details</h3>
          </div>
          {selectedAssessment ? (
            <div className="p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center text-white text-xl font-bold"
                    style={{ backgroundColor: selectedAssessment.colorCode }}
                  >
                    {selectedAssessment.totalScore}
                  </div>
                  <div>
                    <div className="text-lg font-semibold text-white capitalize">
                      {selectedAssessment.actionType.replace(/_/g, " ")}
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`text-xs px-2 py-0.5 rounded ${getLevelBadgeClass(selectedAssessment.level)}`}>
                        {selectedAssessment.level}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded ${getActionBadgeClass(selectedAssessment.requiredAction)}`}>
                        {selectedAssessment.requiredAction}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-700 pt-4">
                <h4 className="text-sm font-semibold text-white mb-3">Component Scores</h4>
                <div className="space-y-3">
                  {selectedAssessment.componentScores.map((comp) => (
                    <div key={comp.component}>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-400">{comp.component.replace(/_/g, " ")}</span>
                        <div className="flex items-center space-x-2">
                          <span className={getScoreColor(comp.score)}>{comp.score}</span>
                          <span className="text-gray-500 text-xs">({(comp.weight * 100).toFixed(0)}%)</span>
                        </div>
                      </div>
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${getScoreBarColor(comp.score)}`}
                          style={{ width: `${comp.score}%` }}
                        ></div>
                      </div>
                      {comp.factors.length > 0 && comp.score < 80 && (
                        <div className="mt-1 text-xs text-gray-500">
                          {comp.factors[0]}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {selectedAssessment.humanReviewRequired && (
                <div className="border-t border-gray-700 pt-4">
                  <div className="p-3 bg-yellow-900/30 border border-yellow-700 rounded">
                    <div className="flex items-center space-x-2">
                      <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <span className="text-sm text-yellow-300">Human review required before proceeding</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              Select an assessment to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

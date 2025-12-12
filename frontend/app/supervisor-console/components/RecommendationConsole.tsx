"use client";

import React, { useState, useEffect } from "react";

interface Recommendation {
  recommendation_id: string;
  recommendation_type: string;
  priority: number;
  title: string;
  description: string;
  rationale: string;
  affected_systems: string[];
  implementation_steps: string[];
  expected_outcome: string;
  risk_if_ignored: string;
  deadline: string | null;
  accepted: boolean;
  implemented: boolean;
  timestamp: string;
}

interface CascadePrediction {
  prediction_id: string;
  trigger_event: string;
  trigger_source: string;
  predicted_outcomes: { outcome: string; probability: number; time_to_impact_hours: number }[];
  probability: number;
  affected_systems: string[];
  mitigation_options: string[];
  confidence: number;
  timestamp: string;
}

export default function RecommendationConsole() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [cascades, setCascades] = useState<CascadePrediction[]>([]);
  const [activeTab, setActiveTab] = useState<"recommendations" | "cascades">("recommendations");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockRecommendations: Recommendation[] = [
      {
        recommendation_id: "REC-A1B2C3D4",
        recommendation_type: "immediate_action",
        priority: 1,
        title: "Scale Predictive AI Engine Immediately",
        description: "The Predictive AI engine is approaching critical load levels and requires immediate scaling.",
        rationale: "CPU at 92.5%, memory at 88.3%, queue depth at 1250. System will experience failures within 2 hours at current trajectory.",
        affected_systems: ["predictive_ai", "intel_engine", "city_brain"],
        implementation_steps: [
          "Increase instance count from 5 to 8",
          "Enable auto-scaling with max 12 instances",
          "Clear non-critical cache data",
          "Throttle low-priority requests"
        ],
        expected_outcome: "Reduce load to 60% within 30 minutes, prevent service degradation",
        risk_if_ignored: "System failure within 2 hours, cascading impact to dependent systems",
        deadline: new Date(Date.now() + 3600000).toISOString(),
        accepted: false,
        implemented: false,
        timestamp: new Date().toISOString(),
      },
      {
        recommendation_id: "REC-E5F6G7H8",
        recommendation_type: "preventive_action",
        priority: 2,
        title: "Update Bias Detection Models",
        description: "Recent bias audit detected elevated disparate impact scores in crime prediction models.",
        rationale: "Disparate impact score for race at 0.78, below 0.80 threshold. Model retraining recommended.",
        affected_systems: ["predictive_ai", "ethics_guardian"],
        implementation_steps: [
          "Schedule model retraining with balanced dataset",
          "Implement fairness constraints",
          "Run validation bias audit",
          "Deploy updated model with A/B testing"
        ],
        expected_outcome: "Achieve disparate impact scores above 0.85 for all protected classes",
        risk_if_ignored: "Continued bias in predictions, potential legal liability, civil rights concerns",
        deadline: new Date(Date.now() + 86400000 * 7).toISOString(),
        accepted: true,
        implemented: false,
        timestamp: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        recommendation_id: "REC-I9J0K1L2",
        recommendation_type: "resource_allocation",
        priority: 3,
        title: "Rebalance Load Between City Brain and Intel Engine",
        description: "Load imbalance detected between City Brain (78.9% memory) and Intel Engine (65.8% memory).",
        rationale: "Rebalancing will optimize resource utilization and improve overall system performance.",
        affected_systems: ["city_brain", "intel_orchestration"],
        implementation_steps: [
          "Migrate 15% of City Brain workload to Intel Engine",
          "Update routing rules",
          "Monitor for 24 hours",
          "Adjust as needed"
        ],
        expected_outcome: "Balanced load at approximately 72% for both engines",
        risk_if_ignored: "City Brain may experience memory pressure during peak hours",
        deadline: null,
        accepted: false,
        implemented: false,
        timestamp: new Date(Date.now() - 7200000).toISOString(),
      },
    ];

    const mockCascades: CascadePrediction[] = [
      {
        prediction_id: "CAS-A1B2C3D4",
        trigger_event: "Predictive AI Engine Overload",
        trigger_source: "system_monitor",
        predicted_outcomes: [
          { outcome: "System-wide performance degradation", probability: 0.7, time_to_impact_hours: 1 },
          { outcome: "Secondary system alerts", probability: 0.6, time_to_impact_hours: 2 },
          { outcome: "Increased operator workload", probability: 0.5, time_to_impact_hours: 4 },
        ],
        probability: 0.6,
        affected_systems: ["intel_engine", "predictive_ai", "city_brain", "emergency_management"],
        mitigation_options: [
          "Proactive resource scaling",
          "Enable circuit breakers",
          "Activate backup systems",
          "Notify relevant teams"
        ],
        confidence: 0.75,
        timestamp: new Date().toISOString(),
      },
    ];

    setRecommendations(mockRecommendations);
    setCascades(mockCascades);
    setLoading(false);
  }, []);

  const getPriorityBadge = (priority: number) => {
    switch (priority) {
      case 1:
        return <span className="px-2 py-1 text-xs font-bold bg-red-600 text-white rounded">P1 CRITICAL</span>;
      case 2:
        return <span className="px-2 py-1 text-xs font-bold bg-orange-600 text-white rounded">P2 HIGH</span>;
      case 3:
        return <span className="px-2 py-1 text-xs font-bold bg-yellow-600 text-white rounded">P3 MEDIUM</span>;
      case 4:
        return <span className="px-2 py-1 text-xs font-bold bg-blue-600 text-white rounded">P4 LOW</span>;
      default:
        return <span className="px-2 py-1 text-xs font-bold bg-gray-600 text-white rounded">P5 INFO</span>;
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      immediate_action: "Immediate Action",
      preventive_action: "Preventive Action",
      monitoring: "Monitoring",
      escalation: "Escalation",
      resource_allocation: "Resource Allocation",
      policy_change: "Policy Change",
      training: "Training",
      investigation: "Investigation",
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => setActiveTab("recommendations")}
          className={`px-4 py-2 rounded-lg ${
            activeTab === "recommendations"
              ? "bg-purple-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Recommendations ({recommendations.filter(r => !r.implemented).length})
        </button>
        <button
          onClick={() => setActiveTab("cascades")}
          className={`px-4 py-2 rounded-lg ${
            activeTab === "cascades"
              ? "bg-purple-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Cascade Predictions ({cascades.length})
        </button>
      </div>

      {activeTab === "recommendations" && (
        <div className="space-y-4">
          {recommendations.map((rec) => (
            <div 
              key={rec.recommendation_id}
              className={`bg-gray-800 rounded-lg border p-4 ${
                rec.priority === 1 
                  ? "border-red-700" 
                  : rec.priority === 2 
                  ? "border-orange-700"
                  : "border-gray-700"
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {getPriorityBadge(rec.priority)}
                  <span className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded">
                    {getTypeLabel(rec.recommendation_type)}
                  </span>
                  {rec.accepted && (
                    <span className="px-2 py-1 text-xs bg-green-900/50 text-green-400 rounded">ACCEPTED</span>
                  )}
                  {rec.implemented && (
                    <span className="px-2 py-1 text-xs bg-blue-900/50 text-blue-400 rounded">IMPLEMENTED</span>
                  )}
                </div>
                {rec.deadline && (
                  <div className="text-sm text-gray-400">
                    Deadline: {new Date(rec.deadline).toLocaleString()}
                  </div>
                )}
              </div>

              <h4 className="text-lg font-semibold mb-2">{rec.title}</h4>
              <p className="text-gray-400 mb-3">{rec.description}</p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="p-3 bg-gray-700/50 rounded-lg">
                  <div className="text-sm font-medium text-gray-300 mb-1">Rationale</div>
                  <div className="text-sm text-gray-400">{rec.rationale}</div>
                </div>
                <div className="p-3 bg-gray-700/50 rounded-lg">
                  <div className="text-sm font-medium text-gray-300 mb-1">Risk if Ignored</div>
                  <div className="text-sm text-red-400">{rec.risk_if_ignored}</div>
                </div>
              </div>

              <div className="mb-4">
                <div className="text-sm font-medium text-gray-300 mb-2">Implementation Steps</div>
                <ol className="list-decimal list-inside text-sm text-gray-400 space-y-1">
                  {rec.implementation_steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>

              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-500">
                  Affected: {rec.affected_systems.join(", ")}
                </div>
                <div className="flex space-x-2">
                  {!rec.accepted && (
                    <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded">
                      Accept
                    </button>
                  )}
                  {rec.accepted && !rec.implemented && (
                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded">
                      Mark Implemented
                    </button>
                  )}
                  <button className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded">
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === "cascades" && (
        <div className="space-y-4">
          {cascades.map((cascade) => (
            <div 
              key={cascade.prediction_id}
              className="bg-gray-800 rounded-lg border border-purple-700 p-4"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="text-lg font-semibold">{cascade.trigger_event}</h4>
                  <div className="text-sm text-gray-400">
                    Source: {cascade.trigger_source} | Confidence: {(cascade.confidence * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-purple-400">
                    {(cascade.probability * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-400">Overall Probability</div>
                </div>
              </div>

              <div className="mb-4">
                <div className="text-sm font-medium text-gray-300 mb-2">Predicted Outcomes</div>
                <div className="space-y-2">
                  {cascade.predicted_outcomes.map((outcome, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-gray-700/50 rounded">
                      <span className="text-sm">{outcome.outcome}</span>
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-gray-400">
                          {outcome.time_to_impact_hours}h
                        </span>
                        <div className="w-20 bg-gray-600 rounded-full h-2">
                          <div 
                            className="bg-purple-500 h-2 rounded-full" 
                            style={{ width: `${outcome.probability * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-12">
                          {(outcome.probability * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3 bg-gray-700/50 rounded-lg">
                  <div className="text-sm font-medium text-gray-300 mb-2">Affected Systems</div>
                  <div className="flex flex-wrap gap-1">
                    {cascade.affected_systems.map((system, idx) => (
                      <span key={idx} className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded">
                        {system}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="p-3 bg-gray-700/50 rounded-lg">
                  <div className="text-sm font-medium text-gray-300 mb-2">Mitigation Options</div>
                  <ul className="text-sm text-gray-400 space-y-1">
                    {cascade.mitigation_options.map((option, idx) => (
                      <li key={idx}>- {option}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

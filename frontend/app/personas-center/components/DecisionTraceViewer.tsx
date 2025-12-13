"use client";

import React, { useState, useEffect } from "react";

interface Persona {
  persona_id: string;
  name: string;
  persona_type: string;
}

interface Mission {
  mission_id: string;
  title: string;
}

interface ReasoningStep {
  step: number;
  action: string;
  result: string;
}

interface DecisionTrace {
  trace_id: string;
  session_id: string;
  turn_id: string;
  reasoning_steps: ReasoningStep[];
  constraints_checked: string[];
  constraints_passed: string[];
  constraints_failed: string[];
  data_sources_used: string[];
  confidence_factors: Record<string, number>;
  alternative_responses: string[];
  final_decision_rationale: string;
  timestamp: string;
  chain_of_custody_hash: string;
}

interface DecisionTraceViewerProps {
  persona: Persona | null;
  mission: Mission | null;
}

export default function DecisionTraceViewer({
  persona,
  mission,
}: DecisionTraceViewerProps) {
  const [traces, setTraces] = useState<DecisionTrace[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<DecisionTrace | null>(null);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<"timeline" | "tree">("timeline");

  useEffect(() => {
    if (persona) {
      fetchTraces();
    }
  }, [persona?.persona_id]);

  const fetchTraces = async () => {
    setLoading(true);
    try {
      const mockTraces: DecisionTrace[] = [
        {
          trace_id: "trace-001",
          session_id: "session-001",
          turn_id: "turn-001",
          reasoning_steps: [
            { step: 1, action: "intent_analysis", result: "query" },
            { step: 2, action: "domain_detection", result: "patrol" },
            { step: 3, action: "urgency_assessment", result: "medium" },
            { step: 4, action: "emotion_detection", result: "neutral" },
            { step: 5, action: "response_generation", result: "completed" },
          ],
          constraints_checked: ["4A-001", "4A-002", "POL-001", "ETH-001"],
          constraints_passed: ["4A-001", "4A-002", "POL-001", "ETH-001"],
          constraints_failed: [],
          data_sources_used: ["conversation_history", "persona_memory", "intent_patterns"],
          confidence_factors: {
            intent_confidence: 0.85,
            keyword_match: 0.7,
            domain_match: 1.0,
          },
          alternative_responses: [],
          final_decision_rationale: "Response generated based on query intent with 85% confidence",
          timestamp: new Date().toISOString(),
          chain_of_custody_hash: "abc123def456",
        },
      ];
      setTraces(mockTraces);
      if (mockTraces.length > 0) {
        setSelectedTrace(mockTraces[0]);
      }
    } catch (error) {
      console.error("Failed to fetch traces:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!persona) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-300 mb-2">
            Decision Trace Viewer
          </h3>
          <p className="text-gray-500">
            Select a persona to view decision traces
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex bg-gray-900">
      <div className="w-1/3 border-r border-gray-700 overflow-y-auto">
        <div className="p-4 bg-gray-800 border-b border-gray-700 sticky top-0">
          <h2 className="text-lg font-semibold text-white mb-2">
            Decision Traces
          </h2>
          <p className="text-sm text-gray-400">
            {persona.name} - {traces.length} traces
          </p>
          <div className="flex space-x-2 mt-3">
            <button
              onClick={() => setViewMode("timeline")}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === "timeline"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-300"
              }`}
            >
              Timeline
            </button>
            <button
              onClick={() => setViewMode("tree")}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === "tree"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-300"
              }`}
            >
              Tree View
            </button>
          </div>
        </div>

        <div className="p-4 space-y-2">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : traces.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No decision traces available
            </div>
          ) : (
            traces.map((trace) => (
              <button
                key={trace.trace_id}
                onClick={() => setSelectedTrace(trace)}
                className={`w-full text-left p-3 rounded-lg transition-all ${
                  selectedTrace?.trace_id === trace.trace_id
                    ? "bg-blue-600 border border-blue-500"
                    : "bg-gray-800 hover:bg-gray-750 border border-gray-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-white text-sm">
                    {trace.trace_id.slice(0, 12)}...
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-xs ${
                      trace.constraints_failed.length === 0
                        ? "bg-green-600 text-green-100"
                        : "bg-red-600 text-red-100"
                    }`}
                  >
                    {trace.constraints_failed.length === 0 ? "Passed" : "Failed"}
                  </span>
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {new Date(trace.timestamp).toLocaleString()}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {trace.reasoning_steps.length} steps |{" "}
                  {trace.constraints_checked.length} constraints
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="w-2/3 overflow-y-auto p-4">
        {selectedTrace ? (
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">
                Trace Details
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Trace ID:</span>
                  <span className="text-gray-300 ml-2 font-mono text-xs">
                    {selectedTrace.trace_id}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Session:</span>
                  <span className="text-gray-300 ml-2 font-mono text-xs">
                    {selectedTrace.session_id}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Timestamp:</span>
                  <span className="text-gray-300 ml-2">
                    {new Date(selectedTrace.timestamp).toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Chain Hash:</span>
                  <span className="text-gray-300 ml-2 font-mono text-xs">
                    {selectedTrace.chain_of_custody_hash.slice(0, 16)}...
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">
                Reasoning Steps
              </h3>
              <div className="space-y-2">
                {selectedTrace.reasoning_steps.map((step, idx) => (
                  <div
                    key={idx}
                    className="flex items-center space-x-3 p-2 bg-gray-700/50 rounded"
                  >
                    <span className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs text-white">
                      {step.step}
                    </span>
                    <div className="flex-1">
                      <span className="text-gray-300 capitalize">
                        {step.action.replace("_", " ")}
                      </span>
                    </div>
                    <span className="px-2 py-1 bg-gray-600 rounded text-xs text-gray-300">
                      {step.result}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">
                Constraints Check
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm text-gray-400 mb-2">
                    Passed ({selectedTrace.constraints_passed.length})
                  </h4>
                  <div className="space-y-1">
                    {selectedTrace.constraints_passed.map((c) => (
                      <div
                        key={c}
                        className="flex items-center space-x-2 text-sm"
                      >
                        <span className="text-green-400">✓</span>
                        <span className="text-gray-300">{c}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm text-gray-400 mb-2">
                    Failed ({selectedTrace.constraints_failed.length})
                  </h4>
                  {selectedTrace.constraints_failed.length === 0 ? (
                    <span className="text-gray-500 text-sm">None</span>
                  ) : (
                    <div className="space-y-1">
                      {selectedTrace.constraints_failed.map((c) => (
                        <div
                          key={c}
                          className="flex items-center space-x-2 text-sm"
                        >
                          <span className="text-red-400">✗</span>
                          <span className="text-gray-300">{c}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">
                Confidence Factors
              </h3>
              <div className="space-y-3">
                {Object.entries(selectedTrace.confidence_factors).map(
                  ([factor, value]) => (
                    <div key={factor}>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-400 capitalize">
                          {factor.replace("_", " ")}
                        </span>
                        <span className="text-white">
                          {(value * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${value * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">
                Data Sources Used
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedTrace.data_sources_used.map((source) => (
                  <span
                    key={source}
                    className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300"
                  >
                    {source.replace("_", " ")}
                  </span>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">
                Final Decision Rationale
              </h3>
              <p className="text-gray-300">
                {selectedTrace.final_decision_rationale}
              </p>
            </div>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">📋</div>
              <h3 className="text-xl font-semibold text-gray-300 mb-2">
                Select a Trace
              </h3>
              <p className="text-gray-500">
                Choose a decision trace to view details
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

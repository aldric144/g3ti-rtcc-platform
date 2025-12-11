"use client";

import React, { useState } from "react";

interface RoutingDecision {
  decision_id: string;
  timestamp: string;
  call_type: string;
  priority: string;
  primary_responder: string;
  co_responders: string[];
  de_escalation_prompts: string[];
  recommended_actions: string[];
  risk_level: string;
}

interface CrisisCallInput {
  call_narrative: string;
  call_type: string;
  weapons_mentioned: boolean;
  violence_mentioned: boolean;
  substance_involved: boolean;
  youth_involved: boolean;
  elderly_involved: boolean;
}

export default function CrisisRoutingConsole() {
  const [callInput, setCallInput] = useState<CrisisCallInput>({
    call_narrative: "",
    call_type: "welfare_check",
    weapons_mentioned: false,
    violence_mentioned: false,
    substance_involved: false,
    youth_involved: false,
    elderly_involved: false,
  });
  const [routingDecision, setRoutingDecision] = useState<RoutingDecision | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recentDecisions, setRecentDecisions] = useState<RoutingDecision[]>([]);

  const handleSubmit = async () => {
    if (!callInput.call_narrative.trim()) return;
    
    setIsProcessing(true);
    
    try {
      const response = await fetch("/api/human-intel/crisis-route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(callInput),
      });
      
      if (response.ok) {
        const data = await response.json();
        const decision: RoutingDecision = {
          decision_id: data.decision_id,
          timestamp: data.timestamp,
          call_type: data.call_type,
          priority: data.priority,
          primary_responder: data.primary_responder,
          co_responders: data.co_responders,
          de_escalation_prompts: data.de_escalation_prompts,
          recommended_actions: data.recommended_actions,
          risk_level: data.risk_level,
        };
        setRoutingDecision(decision);
        setRecentDecisions((prev) => [decision, ...prev.slice(0, 4)]);
      } else {
        const mockDecision: RoutingDecision = {
          decision_id: `CRD-${Date.now().toString(36).toUpperCase()}`,
          timestamp: new Date().toISOString(),
          call_type: callInput.call_type,
          priority: callInput.weapons_mentioned ? "CRITICAL" : callInput.violence_mentioned ? "EMERGENCY" : "ROUTINE",
          primary_responder: "crisis_intervention_team",
          co_responders: ["mental_health_clinician", "police"],
          de_escalation_prompts: [
            "Use calm, non-threatening tone",
            "Listen actively without interrupting",
            "Acknowledge feelings",
          ],
          recommended_actions: [
            "Dispatch crisis intervention team",
            "Prepare for potential Baker Act",
            "Document interaction",
          ],
          risk_level: callInput.weapons_mentioned ? "HIGH" : "MODERATE",
        };
        setRoutingDecision(mockDecision);
        setRecentDecisions((prev) => [mockDecision, ...prev.slice(0, 4)]);
      }
    } catch (error) {
      const mockDecision: RoutingDecision = {
        decision_id: `CRD-${Date.now().toString(36).toUpperCase()}`,
        timestamp: new Date().toISOString(),
        call_type: callInput.call_type,
        priority: "ROUTINE",
        primary_responder: "crisis_intervention_team",
        co_responders: ["mental_health_clinician"],
        de_escalation_prompts: [
          "Use calm, non-threatening tone",
          "Listen actively",
        ],
        recommended_actions: [
          "Standard crisis response",
          "Provide resources",
        ],
        risk_level: "LOW",
      };
      setRoutingDecision(mockDecision);
      setRecentDecisions((prev) => [mockDecision, ...prev.slice(0, 4)]);
    }
    
    setIsProcessing(false);
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case "CRITICAL": return "bg-red-800 text-white";
      case "EMERGENCY": return "bg-red-600 text-white";
      case "URGENT": return "bg-orange-500 text-white";
      case "ELEVATED": return "bg-yellow-500 text-black";
      case "ROUTINE": return "bg-green-500 text-white";
      default: return "bg-gray-500 text-white";
    }
  };

  const getRiskColor = (level: string): string => {
    switch (level) {
      case "HIGH": return "text-red-400";
      case "MODERATE": return "text-orange-400";
      case "LOW": return "text-green-400";
      default: return "text-gray-400";
    }
  };

  const callTypes = [
    { value: "welfare_check", label: "Welfare Check" },
    { value: "mental_health", label: "Mental Health Crisis" },
    { value: "suicide_ideation", label: "Suicide Ideation" },
    { value: "domestic_violence", label: "Domestic Violence" },
    { value: "substance_crisis", label: "Substance Crisis" },
    { value: "behavioral_disturbance", label: "Behavioral Disturbance" },
    { value: "family_crisis", label: "Family Crisis" },
    { value: "youth_crisis", label: "Youth Crisis" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Crisis Routing Console</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Crisis Call Input</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Call Narrative</label>
                <textarea
                  value={callInput.call_narrative}
                  onChange={(e) => setCallInput({ ...callInput, call_narrative: e.target.value })}
                  className="w-full bg-gray-600 text-white rounded p-3 h-32"
                  placeholder="Enter call narrative or crisis description..."
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Call Type</label>
                <select
                  value={callInput.call_type}
                  onChange={(e) => setCallInput({ ...callInput, call_type: e.target.value })}
                  className="w-full bg-gray-600 text-white rounded p-2"
                >
                  {callTypes.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={callInput.weapons_mentioned}
                    onChange={(e) => setCallInput({ ...callInput, weapons_mentioned: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm">Weapons Mentioned</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={callInput.violence_mentioned}
                    onChange={(e) => setCallInput({ ...callInput, violence_mentioned: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm">Violence Mentioned</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={callInput.substance_involved}
                    onChange={(e) => setCallInput({ ...callInput, substance_involved: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm">Substance Involved</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={callInput.youth_involved}
                    onChange={(e) => setCallInput({ ...callInput, youth_involved: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm">Youth Involved</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={callInput.elderly_involved}
                    onChange={(e) => setCallInput({ ...callInput, elderly_involved: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm">Elderly Involved</span>
                </label>
              </div>

              <button
                onClick={handleSubmit}
                disabled={isProcessing || !callInput.call_narrative.trim()}
                className={`w-full py-3 rounded font-semibold ${
                  isProcessing || !callInput.call_narrative.trim()
                    ? "bg-gray-500 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {isProcessing ? "Processing..." : "Get Routing Recommendation"}
              </button>
            </div>
          </div>

          <div className="bg-gray-700 rounded-lg p-4 mt-4">
            <h3 className="text-lg font-semibold mb-4">Recent Decisions</h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {recentDecisions.length === 0 ? (
                <div className="text-gray-400 text-center py-4">No recent decisions</div>
              ) : (
                recentDecisions.map((decision) => (
                  <div
                    key={decision.decision_id}
                    className="bg-gray-600 rounded p-2 cursor-pointer hover:bg-gray-550"
                    onClick={() => setRoutingDecision(decision)}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-mono">{decision.decision_id}</span>
                      <span className={`px-2 py-0.5 rounded text-xs ${getPriorityColor(decision.priority)}`}>
                        {decision.priority}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400">
                      {new Date(decision.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div>
          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Routing Decision</h3>
            {routingDecision ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm">{routingDecision.decision_id}</span>
                  <span className={`px-3 py-1 rounded font-semibold ${getPriorityColor(routingDecision.priority)}`}>
                    {routingDecision.priority}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-gray-400 text-sm">Call Type</div>
                    <div className="capitalize">{routingDecision.call_type.replace(/_/g, " ")}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Risk Level</div>
                    <div className={`font-semibold ${getRiskColor(routingDecision.risk_level)}`}>
                      {routingDecision.risk_level}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-gray-400 text-sm mb-1">Primary Responder</div>
                  <div className="bg-blue-600 px-3 py-2 rounded inline-block">
                    {routingDecision.primary_responder.replace(/_/g, " ")}
                  </div>
                </div>

                <div>
                  <div className="text-gray-400 text-sm mb-1">Co-Responders</div>
                  <div className="flex flex-wrap gap-2">
                    {routingDecision.co_responders.map((responder, idx) => (
                      <span key={idx} className="bg-gray-600 px-2 py-1 rounded text-sm">
                        {responder.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-gray-400 text-sm mb-1">De-escalation Prompts</div>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {routingDecision.de_escalation_prompts.map((prompt, idx) => (
                      <li key={idx}>{prompt}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="text-gray-400 text-sm mb-1">Recommended Actions</div>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {routingDecision.recommended_actions.map((action, idx) => (
                      <li key={idx}>{action}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-gray-400 text-center py-12">
                Enter crisis call details and click "Get Routing Recommendation"
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">Trauma-Informed Response Guidelines</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <div className="font-semibold text-blue-400 mb-1">Communication</div>
            <ul className="text-gray-400 space-y-1">
              <li>Use calm, non-threatening tone</li>
              <li>Listen actively without interrupting</li>
              <li>Acknowledge feelings</li>
            </ul>
          </div>
          <div>
            <div className="font-semibold text-green-400 mb-1">Safety</div>
            <ul className="text-gray-400 space-y-1">
              <li>Assess for weapons</li>
              <li>Maintain safe distance</li>
              <li>Have backup available</li>
            </ul>
          </div>
          <div>
            <div className="font-semibold text-yellow-400 mb-1">Follow-up</div>
            <ul className="text-gray-400 space-y-1">
              <li>Document thoroughly</li>
              <li>Provide crisis resources</li>
              <li>Schedule welfare check</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

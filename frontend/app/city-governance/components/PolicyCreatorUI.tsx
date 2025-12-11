"use client";

import React, { useState, useEffect } from "react";

interface MachineRule {
  rule_id: string;
  original_text: string;
  condition: {
    variable: string;
    operator: string;
    value: string;
  };
  action: string;
  variables: string[];
  confidence: number;
  ambiguities: Ambiguity[];
  source: string;
  category: string;
  priority: number;
  is_active: boolean;
  created_at: string;
}

interface Ambiguity {
  type: string;
  description: string;
  suggestions: string[];
}

interface PolicyConflict {
  conflict_id: string;
  policy_ids: string[];
  conflict_type: string;
  description: string;
  resolution_suggestions: string[];
  severity: string;
}

const LEGAL_SOURCES = [
  { value: "us_constitution", label: "U.S. Constitution" },
  { value: "florida_constitution", label: "Florida Constitution" },
  { value: "florida_statute", label: "Florida Statute" },
  { value: "riviera_beach_code", label: "Riviera Beach Code" },
  { value: "federal_framework", label: "Federal Framework" },
  { value: "agency_sop", label: "Agency SOP" },
  { value: "emergency_ordinance", label: "Emergency Ordinance" },
];

const LEGAL_CATEGORIES = [
  { value: "civil_rights", label: "Civil Rights" },
  { value: "public_safety", label: "Public Safety" },
  { value: "emergency_powers", label: "Emergency Powers" },
  { value: "city_authority", label: "City Authority" },
  { value: "autonomy_limits", label: "Autonomy Limits" },
  { value: "privacy", label: "Privacy" },
  { value: "surveillance", label: "Surveillance" },
  { value: "use_of_force", label: "Use of Force" },
  { value: "traffic", label: "Traffic" },
  { value: "fire_ems", label: "Fire/EMS" },
  { value: "property_rights", label: "Property Rights" },
  { value: "data_protection", label: "Data Protection" },
];

const ACTION_COLORS: Record<string, string> = {
  allow: "text-green-400 bg-green-900/30",
  block: "text-red-400 bg-red-900/30",
  require_approval: "text-yellow-400 bg-yellow-900/30",
  alert: "text-orange-400 bg-orange-900/30",
  log: "text-blue-400 bg-blue-900/30",
  escalate: "text-purple-400 bg-purple-900/30",
};

export default function PolicyCreatorUI() {
  const [policies, setPolicies] = useState<MachineRule[]>([]);
  const [conflicts, setConflicts] = useState<PolicyConflict[]>([]);
  const [newPolicyText, setNewPolicyText] = useState("");
  const [selectedSource, setSelectedSource] = useState("agency_sop");
  const [selectedCategory, setSelectedCategory] = useState("public_safety");
  const [priority, setPriority] = useState(50);
  const [translatedRule, setTranslatedRule] = useState<MachineRule | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState<MachineRule | null>(null);
  const [filterSource, setFilterSource] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const mockPolicies: MachineRule[] = [
        {
          rule_id: "policy-001",
          original_text: "Drones cannot enter private property without exigent circumstances or a warrant.",
          condition: {
            variable: "drone_location.is_private_property",
            operator: "equals",
            value: "true",
          },
          action: "require_approval",
          variables: ["drone_location", "incident.is_exigent", "warrant.is_valid"],
          confidence: 0.92,
          ambiguities: [],
          source: "florida_statute",
          category: "surveillance",
          priority: 85,
          is_active: true,
          created_at: new Date().toISOString(),
        },
        {
          rule_id: "policy-002",
          original_text: "All use of force incidents must be logged and reviewed within 24 hours.",
          condition: {
            variable: "action.type",
            operator: "equals",
            value: "use_of_force",
          },
          action: "log",
          variables: ["action.type", "review.deadline"],
          confidence: 0.95,
          ambiguities: [],
          source: "agency_sop",
          category: "use_of_force",
          priority: 90,
          is_active: true,
          created_at: new Date().toISOString(),
        },
        {
          rule_id: "policy-003",
          original_text: "Predictive policing actions targeting individuals require supervisor approval.",
          condition: {
            variable: "action.targets_individual",
            operator: "equals",
            value: "true",
          },
          action: "require_approval",
          variables: ["action.targets_individual", "action.category"],
          confidence: 0.88,
          ambiguities: [
            {
              type: "vague_condition",
              description: "Definition of 'targeting individuals' may vary",
              suggestions: ["Define specific criteria for individual targeting"],
            },
          ],
          source: "agency_sop",
          category: "civil_rights",
          priority: 80,
          is_active: true,
          created_at: new Date().toISOString(),
        },
      ];
      setPolicies(mockPolicies);
    } catch (error) {
      console.error("Failed to fetch policies:", error);
    } finally {
      setLoading(false);
    }
  };

  const translatePolicy = async () => {
    if (!newPolicyText.trim()) return;

    setIsTranslating(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const mockTranslation: MachineRule = {
        rule_id: `policy-${Date.now()}`,
        original_text: newPolicyText,
        condition: {
          variable: extractVariable(newPolicyText),
          operator: extractOperator(newPolicyText),
          value: extractValue(newPolicyText),
        },
        action: extractAction(newPolicyText),
        variables: extractVariables(newPolicyText),
        confidence: 0.75 + Math.random() * 0.2,
        ambiguities: detectAmbiguities(newPolicyText),
        source: selectedSource,
        category: selectedCategory,
        priority: priority,
        is_active: false,
        created_at: new Date().toISOString(),
      };

      setTranslatedRule(mockTranslation);
    } catch (error) {
      console.error("Translation failed:", error);
    } finally {
      setIsTranslating(false);
    }
  };

  const extractVariable = (text: string): string => {
    if (text.toLowerCase().includes("drone")) return "drone_operation.status";
    if (text.toLowerCase().includes("force")) return "action.use_of_force";
    if (text.toLowerCase().includes("surveillance")) return "surveillance.active";
    if (text.toLowerCase().includes("traffic")) return "traffic.enforcement";
    return "action.type";
  };

  const extractOperator = (text: string): string => {
    if (text.toLowerCase().includes("cannot") || text.toLowerCase().includes("must not")) return "not_equals";
    if (text.toLowerCase().includes("must") || text.toLowerCase().includes("require")) return "equals";
    if (text.toLowerCase().includes("greater") || text.toLowerCase().includes("exceed")) return "greater_than";
    return "equals";
  };

  const extractValue = (text: string): string => {
    if (text.toLowerCase().includes("private property")) return "private_property";
    if (text.toLowerCase().includes("emergency")) return "emergency";
    if (text.toLowerCase().includes("approval")) return "requires_approval";
    return "true";
  };

  const extractAction = (text: string): string => {
    if (text.toLowerCase().includes("block") || text.toLowerCase().includes("cannot")) return "block";
    if (text.toLowerCase().includes("approval") || text.toLowerCase().includes("review")) return "require_approval";
    if (text.toLowerCase().includes("alert") || text.toLowerCase().includes("notify")) return "alert";
    if (text.toLowerCase().includes("log") || text.toLowerCase().includes("record")) return "log";
    return "allow";
  };

  const extractVariables = (text: string): string[] => {
    const vars: string[] = [];
    if (text.toLowerCase().includes("drone")) vars.push("drone_operation");
    if (text.toLowerCase().includes("property")) vars.push("location.property_type");
    if (text.toLowerCase().includes("emergency") || text.toLowerCase().includes("exigent")) vars.push("incident.is_exigent");
    if (text.toLowerCase().includes("warrant")) vars.push("warrant.is_valid");
    if (text.toLowerCase().includes("force")) vars.push("action.force_level");
    if (text.toLowerCase().includes("approval")) vars.push("approval.status");
    return vars.length > 0 ? vars : ["action.type"];
  };

  const detectAmbiguities = (text: string): Ambiguity[] => {
    const ambiguities: Ambiguity[] = [];
    
    if (text.toLowerCase().includes("reasonable") || text.toLowerCase().includes("appropriate")) {
      ambiguities.push({
        type: "vague_condition",
        description: "Subjective terms like 'reasonable' or 'appropriate' need clarification",
        suggestions: ["Define specific measurable criteria"],
      });
    }
    
    if (!text.includes("hour") && !text.includes("minute") && !text.includes("day")) {
      if (text.toLowerCase().includes("within") || text.toLowerCase().includes("before")) {
        ambiguities.push({
          type: "temporal_ambiguity",
          description: "Time constraint not clearly specified",
          suggestions: ["Add specific time duration (e.g., 'within 24 hours')"],
        });
      }
    }

    return ambiguities;
  };

  const savePolicy = async () => {
    if (!translatedRule) return;

    const newPolicy = { ...translatedRule, is_active: true };
    setPolicies([...policies, newPolicy]);
    setTranslatedRule(null);
    setNewPolicyText("");
  };

  const checkConflicts = async () => {
    const mockConflicts: PolicyConflict[] = [
      {
        conflict_id: "conflict-001",
        policy_ids: ["policy-001", "policy-003"],
        conflict_type: "partial_overlap",
        description: "Both policies apply to drone operations but have different approval requirements",
        resolution_suggestions: [
          "Clarify which policy takes precedence",
          "Merge policies with combined conditions",
        ],
        severity: "medium",
      },
    ];
    setConflicts(mockConflicts);
  };

  const filteredPolicies = policies.filter((policy) => {
    const matchesSource = !filterSource || policy.source === filterSource;
    const matchesCategory = !filterCategory || policy.category === filterCategory;
    return matchesSource && matchesCategory;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Policy Creator & Translator</h2>
          <p className="text-gray-400 text-sm">
            Transform natural language policies into machine-readable rules
          </p>
        </div>
        <button
          onClick={checkConflicts}
          className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-sm"
        >
          Check Conflicts
        </button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-lg font-bold text-white mb-4">Create New Policy</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Natural Language Policy
                </label>
                <textarea
                  value={newPolicyText}
                  onChange={(e) => setNewPolicyText(e.target.value)}
                  placeholder="Enter policy in plain English (e.g., 'Drones cannot enter private property without exigent circumstances.')"
                  className="w-full h-32 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Legal Source</label>
                  <select
                    value={selectedSource}
                    onChange={(e) => setSelectedSource(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    {LEGAL_SOURCES.map((source) => (
                      <option key={source.value} value={source.value}>
                        {source.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Category</label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    {LEGAL_CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Priority: {priority}
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={priority}
                  onChange={(e) => setPriority(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Low</span>
                  <span>High</span>
                </div>
              </div>

              <button
                onClick={translatePolicy}
                disabled={!newPolicyText.trim() || isTranslating}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded font-medium"
              >
                {isTranslating ? "Translating..." : "Translate to Machine Rule"}
              </button>
            </div>
          </div>

          {translatedRule && (
            <div className="bg-gray-800 rounded-lg border border-blue-500 p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">Translated Rule</h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-400">Confidence:</span>
                  <span
                    className={`text-sm font-bold ${
                      translatedRule.confidence >= 0.9
                        ? "text-green-400"
                        : translatedRule.confidence >= 0.7
                        ? "text-yellow-400"
                        : "text-red-400"
                    }`}
                  >
                    {(translatedRule.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="bg-gray-900 rounded p-3">
                  <div className="text-xs text-gray-500 mb-1">CONDITION</div>
                  <code className="text-sm text-green-400">
                    IF {translatedRule.condition.variable} {translatedRule.condition.operator}{" "}
                    {translatedRule.condition.value}
                  </code>
                </div>

                <div className="bg-gray-900 rounded p-3">
                  <div className="text-xs text-gray-500 mb-1">ACTION</div>
                  <span className={`px-2 py-1 rounded text-sm ${ACTION_COLORS[translatedRule.action]}`}>
                    {translatedRule.action.replace(/_/g, " ").toUpperCase()}
                  </span>
                </div>

                <div className="bg-gray-900 rounded p-3">
                  <div className="text-xs text-gray-500 mb-1">VARIABLES</div>
                  <div className="flex flex-wrap gap-1">
                    {translatedRule.variables.map((v) => (
                      <span key={v} className="px-2 py-0.5 bg-gray-700 rounded text-xs text-gray-300">
                        {v}
                      </span>
                    ))}
                  </div>
                </div>

                {translatedRule.ambiguities.length > 0 && (
                  <div className="bg-yellow-900/20 border border-yellow-600/50 rounded p-3">
                    <div className="text-xs text-yellow-500 mb-2">AMBIGUITIES DETECTED</div>
                    {translatedRule.ambiguities.map((amb, i) => (
                      <div key={i} className="text-sm text-yellow-400">
                        <span className="font-medium">{amb.type}:</span> {amb.description}
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex space-x-3">
                  <button
                    onClick={savePolicy}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded font-medium"
                  >
                    Save Policy
                  </button>
                  <button
                    onClick={() => setTranslatedRule(null)}
                    className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded"
                  >
                    Discard
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Active Policies</h3>
              <span className="text-sm text-gray-400">{filteredPolicies.length} policies</span>
            </div>

            <div className="flex space-x-2 mb-4">
              <select
                value={filterSource}
                onChange={(e) => setFilterSource(e.target.value)}
                className="flex-1 px-3 py-1 bg-gray-900 border border-gray-700 rounded text-sm text-white"
              >
                <option value="">All Sources</option>
                {LEGAL_SOURCES.map((source) => (
                  <option key={source.value} value={source.value}>
                    {source.label}
                  </option>
                ))}
              </select>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="flex-1 px-3 py-1 bg-gray-900 border border-gray-700 rounded text-sm text-white"
              >
                <option value="">All Categories</option>
                {LEGAL_CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredPolicies.map((policy) => (
                <button
                  key={policy.rule_id}
                  onClick={() => setSelectedPolicy(policy)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedPolicy?.rule_id === policy.rule_id
                      ? "bg-blue-900/30 border-blue-500"
                      : "bg-gray-900 border-gray-700 hover:border-gray-600"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-white truncate">{policy.original_text}</div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">
                          {LEGAL_SOURCES.find((s) => s.value === policy.source)?.label}
                        </span>
                        <span className="text-xs text-gray-600">|</span>
                        <span className="text-xs text-gray-500">
                          {LEGAL_CATEGORIES.find((c) => c.value === policy.category)?.label}
                        </span>
                      </div>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs ${ACTION_COLORS[policy.action]}`}>
                      {policy.action.replace(/_/g, " ")}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {conflicts.length > 0 && (
            <div className="bg-gray-800 rounded-lg border border-yellow-600 p-4">
              <h3 className="text-lg font-bold text-yellow-400 mb-3">Policy Conflicts</h3>
              <div className="space-y-3">
                {conflicts.map((conflict) => (
                  <div key={conflict.conflict_id} className="bg-yellow-900/20 rounded p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-yellow-400">
                        {conflict.conflict_type.replace(/_/g, " ").toUpperCase()}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs ${
                          conflict.severity === "high"
                            ? "bg-red-900/50 text-red-400"
                            : conflict.severity === "medium"
                            ? "bg-yellow-900/50 text-yellow-400"
                            : "bg-gray-700 text-gray-400"
                        }`}
                      >
                        {conflict.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300">{conflict.description}</p>
                    <div className="mt-2">
                      <div className="text-xs text-gray-500 mb-1">Suggestions:</div>
                      <ul className="text-xs text-gray-400 list-disc list-inside">
                        {conflict.resolution_suggestions.map((sug, i) => (
                          <li key={i}>{sug}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

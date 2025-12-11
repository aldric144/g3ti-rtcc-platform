"use client";

import React, { useState, useEffect } from "react";

interface ConstitutionalRule {
  rule_id: string;
  layer: string;
  condition: string;
  action_categories: string[];
  result: string;
  priority: number;
  source_documents: string[];
  rationale: string;
  exceptions: string[];
  is_active: boolean;
}

interface ConstitutionStructure {
  layers: {
    [key: string]: ConstitutionalRule[];
  };
  total_rules: number;
  last_updated: string;
}

const LAYER_COLORS: Record<string, string> = {
  federal_constitutional: "bg-red-600",
  state_constitutional: "bg-orange-600",
  statutory: "bg-yellow-600",
  local_ordinance: "bg-green-600",
  agency_sop: "bg-blue-600",
  ethics: "bg-purple-600",
  autonomy: "bg-pink-600",
};

const LAYER_DESCRIPTIONS: Record<string, string> = {
  federal_constitutional: "U.S. Constitution and federal civil liberties protections",
  state_constitutional: "Florida Constitution provisions and state-level rights",
  statutory: "Florida State Statutes governing public safety and city authority",
  local_ordinance: "Riviera Beach Municipal Code and local regulations",
  agency_sop: "RBPD and Fire/EMS Standard Operating Procedures",
  ethics: "Bias prevention, accountability, and fairness requirements",
  autonomy: "AI autonomy level constraints and operational boundaries",
};

const RESULT_COLORS: Record<string, string> = {
  allowed: "text-green-400 bg-green-900/30",
  denied: "text-red-400 bg-red-900/30",
  allowed_with_human_review: "text-yellow-400 bg-yellow-900/30",
};

export default function AIConstitutionViewer() {
  const [constitution, setConstitution] = useState<ConstitutionStructure | null>(null);
  const [selectedLayer, setSelectedLayer] = useState<string | null>(null);
  const [selectedRule, setSelectedRule] = useState<ConstitutionalRule | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [expandedLayers, setExpandedLayers] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchConstitution();
  }, []);

  const fetchConstitution = async () => {
    setLoading(true);
    try {
      const mockConstitution: ConstitutionStructure = {
        layers: {
          federal_constitutional: [
            {
              rule_id: "fed-const-001",
              layer: "federal_constitutional",
              condition: "action_involves_search_or_seizure",
              action_categories: ["surveillance", "property_entry", "data_access"],
              result: "allowed_with_human_review",
              priority: 100,
              source_documents: ["US Constitution - 4th Amendment"],
              rationale: "Fourth Amendment protections require warrant or exigent circumstances for searches",
              exceptions: ["exigent_circumstances", "plain_view", "consent"],
              is_active: true,
            },
            {
              rule_id: "fed-const-002",
              layer: "federal_constitutional",
              condition: "action_restricts_speech_or_assembly",
              action_categories: ["crowd_management", "mass_alert"],
              result: "denied",
              priority: 100,
              source_documents: ["US Constitution - 1st Amendment"],
              rationale: "First Amendment protects freedom of speech and peaceful assembly",
              exceptions: ["imminent_lawless_action", "true_threats"],
              is_active: true,
            },
          ],
          state_constitutional: [
            {
              rule_id: "state-const-001",
              layer: "state_constitutional",
              condition: "action_involves_privacy_violation",
              action_categories: ["surveillance", "data_access"],
              result: "denied",
              priority: 95,
              source_documents: ["Florida Constitution - Article I, Section 23"],
              rationale: "Florida Constitution provides explicit right to privacy",
              exceptions: ["compelling_state_interest", "warrant_issued"],
              is_active: true,
            },
          ],
          statutory: [
            {
              rule_id: "stat-001",
              layer: "statutory",
              condition: "drone_operation_over_private_property",
              action_categories: ["drone_operation"],
              result: "allowed_with_human_review",
              priority: 80,
              source_documents: ["Florida Statute 934.50 - Freedom from Unwarranted Surveillance Act"],
              rationale: "Florida law restricts drone surveillance over private property",
              exceptions: ["emergency_response", "warrant_issued", "owner_consent"],
              is_active: true,
            },
            {
              rule_id: "stat-002",
              layer: "statutory",
              condition: "use_of_force_authorization",
              action_categories: ["use_of_force", "robotics_deployment"],
              result: "allowed_with_human_review",
              priority: 90,
              source_documents: ["Florida Statute 776.05 - Law Enforcement Use of Force"],
              rationale: "Use of force must be objectively reasonable and necessary",
              exceptions: [],
              is_active: true,
            },
          ],
          local_ordinance: [
            {
              rule_id: "local-001",
              layer: "local_ordinance",
              condition: "traffic_enforcement_in_school_zone",
              action_categories: ["traffic_control"],
              result: "allowed",
              priority: 70,
              source_documents: ["Riviera Beach Code - Chapter 70 Traffic"],
              rationale: "Enhanced traffic enforcement authorized in school zones",
              exceptions: [],
              is_active: true,
            },
          ],
          agency_sop: [
            {
              rule_id: "sop-001",
              layer: "agency_sop",
              condition: "patrol_deployment_change",
              action_categories: ["patrol_deployment", "resource_allocation"],
              result: "allowed",
              priority: 50,
              source_documents: ["RBPD SOP Manual - Section 4.2"],
              rationale: "Routine patrol adjustments within operational guidelines",
              exceptions: [],
              is_active: true,
            },
          ],
          ethics: [
            {
              rule_id: "ethics-001",
              layer: "ethics",
              condition: "predictive_action_targets_individual",
              action_categories: ["predictive_policing"],
              result: "allowed_with_human_review",
              priority: 85,
              source_documents: ["NIST AI RMF", "RBPD Ethics Policy"],
              rationale: "Predictive actions targeting individuals require bias review",
              exceptions: [],
              is_active: true,
            },
          ],
          autonomy: [
            {
              rule_id: "auto-001",
              layer: "autonomy",
              condition: "level_2_action_high_risk",
              action_categories: ["use_of_force", "property_entry", "surveillance_escalation"],
              result: "allowed_with_human_review",
              priority: 60,
              source_documents: ["G3TI Autonomy Framework"],
              rationale: "High-risk Level-2 actions require human confirmation",
              exceptions: ["imminent_threat_to_life"],
              is_active: true,
            },
          ],
        },
        total_rules: 42,
        last_updated: new Date().toISOString(),
      };
      setConstitution(mockConstitution);
    } catch (error) {
      console.error("Failed to fetch constitution:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleLayer = (layer: string) => {
    const newExpanded = new Set(expandedLayers);
    if (newExpanded.has(layer)) {
      newExpanded.delete(layer);
    } else {
      newExpanded.add(layer);
    }
    setExpandedLayers(newExpanded);
  };

  const filterRules = (rules: ConstitutionalRule[]) => {
    return rules.filter((rule) => {
      const matchesSearch =
        searchQuery === "" ||
        rule.condition.toLowerCase().includes(searchQuery.toLowerCase()) ||
        rule.rationale.toLowerCase().includes(searchQuery.toLowerCase()) ||
        rule.source_documents.some((doc) =>
          doc.toLowerCase().includes(searchQuery.toLowerCase())
        );
      const matchesCategory =
        filterCategory === "" ||
        rule.action_categories.includes(filterCategory);
      return matchesSearch && matchesCategory;
    });
  };

  const allCategories = constitution
    ? Array.from(
        new Set(
          Object.values(constitution.layers)
            .flat()
            .flatMap((rule) => rule.action_categories)
        )
      ).sort()
    : [];

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
          <h2 className="text-xl font-bold text-white">AI Constitution Viewer</h2>
          <p className="text-gray-400 text-sm">
            Hierarchical rule framework governing all autonomous city actions
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-400">
            Total Rules: <span className="text-blue-400 font-bold">{constitution?.total_rules}</span>
          </div>
          <button
            onClick={fetchConstitution}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="flex space-x-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search rules by condition, rationale, or source..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
        >
          <option value="">All Categories</option>
          {allCategories.map((cat) => (
            <option key={cat} value={cat}>
              {cat.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          {constitution &&
            Object.entries(constitution.layers).map(([layer, rules]) => {
              const filteredRules = filterRules(rules);
              if (filteredRules.length === 0 && (searchQuery || filterCategory)) {
                return null;
              }

              return (
                <div
                  key={layer}
                  className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden"
                >
                  <button
                    onClick={() => toggleLayer(layer)}
                    className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded ${LAYER_COLORS[layer]}`}></div>
                      <div className="text-left">
                        <div className="font-medium text-white">
                          {layer.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                        </div>
                        <div className="text-xs text-gray-400">
                          {LAYER_DESCRIPTIONS[layer]}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="text-sm text-gray-400">
                        {filteredRules.length} rules
                      </span>
                      <svg
                        className={`w-5 h-5 text-gray-400 transition-transform ${
                          expandedLayers.has(layer) ? "rotate-180" : ""
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </div>
                  </button>

                  {expandedLayers.has(layer) && (
                    <div className="border-t border-gray-700">
                      {filteredRules.map((rule) => (
                        <button
                          key={rule.rule_id}
                          onClick={() => setSelectedRule(rule)}
                          className={`w-full px-4 py-3 text-left hover:bg-gray-700/30 border-b border-gray-700/50 last:border-b-0 ${
                            selectedRule?.rule_id === rule.rule_id
                              ? "bg-blue-900/20"
                              : ""
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="text-sm font-medium text-white">
                                {rule.condition.replace(/_/g, " ")}
                              </div>
                              <div className="text-xs text-gray-400 mt-1">
                                {rule.action_categories.slice(0, 3).join(", ")}
                                {rule.action_categories.length > 3 && "..."}
                              </div>
                            </div>
                            <span
                              className={`px-2 py-1 rounded text-xs font-medium ${
                                RESULT_COLORS[rule.result]
                              }`}
                            >
                              {rule.result.replace(/_/g, " ").toUpperCase()}
                            </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
        </div>

        <div className="space-y-4">
          {selectedRule ? (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-lg font-bold text-white mb-4">Rule Details</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-500 uppercase">Rule ID</label>
                  <div className="text-sm text-gray-300 font-mono">
                    {selectedRule.rule_id}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Condition</label>
                  <div className="text-sm text-white">
                    {selectedRule.condition.replace(/_/g, " ")}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Result</label>
                  <div
                    className={`inline-block px-2 py-1 rounded text-sm font-medium ${
                      RESULT_COLORS[selectedRule.result]
                    }`}
                  >
                    {selectedRule.result.replace(/_/g, " ").toUpperCase()}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Priority</label>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${selectedRule.priority}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-300">{selectedRule.priority}</span>
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Action Categories</label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedRule.action_categories.map((cat) => (
                      <span
                        key={cat}
                        className="px-2 py-0.5 bg-gray-700 rounded text-xs text-gray-300"
                      >
                        {cat.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Source Documents</label>
                  <div className="space-y-1 mt-1">
                    {selectedRule.source_documents.map((doc, i) => (
                      <div key={i} className="text-sm text-blue-400">
                        {doc}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs text-gray-500 uppercase">Rationale</label>
                  <div className="text-sm text-gray-300 mt-1">
                    {selectedRule.rationale}
                  </div>
                </div>

                {selectedRule.exceptions.length > 0 && (
                  <div>
                    <label className="text-xs text-gray-500 uppercase">Exceptions</label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedRule.exceptions.map((exc) => (
                        <span
                          key={exc}
                          className="px-2 py-0.5 bg-yellow-900/30 text-yellow-400 rounded text-xs"
                        >
                          {exc.replace(/_/g, " ")}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="text-center text-gray-500 py-8">
                <svg
                  className="w-12 h-12 mx-auto mb-3 opacity-50"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p>Select a rule to view details</p>
              </div>
            </div>
          )}

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-sm font-bold text-white mb-3">Precedence Chain</h3>
            <div className="space-y-2">
              {Object.keys(LAYER_COLORS).map((layer, index) => (
                <div key={layer} className="flex items-center space-x-2">
                  <div className="w-6 text-center text-xs text-gray-500">
                    {index + 1}
                  </div>
                  <div className={`w-3 h-3 rounded ${LAYER_COLORS[layer]}`}></div>
                  <div className="text-sm text-gray-300">
                    {layer.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-3">
              Higher layers take precedence over lower layers
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

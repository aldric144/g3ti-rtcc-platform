"use client";

import React, { useState, useEffect } from "react";

interface ScenarioTemplate {
  scenario_id: string;
  scenario_type: string;
  name: string;
  description: string;
  variables: ScenarioVariable[];
  duration_hours: number;
  affected_zones: string[];
}

interface ScenarioVariable {
  variable_id: string;
  name: string;
  description: string;
  min_value: number;
  max_value: number;
  default_value: number;
  current_value: number;
  unit: string;
  category: string;
}

interface SimulationResult {
  result_id: string;
  scenario_id: string;
  status: string;
  outcome_paths: OutcomePath[];
  impact_assessments: ImpactAssessment[];
  overall_risk_score: number;
  recommended_actions: RecommendedAction[];
  resource_requirements: Record<string, number>;
  estimated_cost: number;
}

interface OutcomePath {
  path_id: string;
  name: string;
  probability: number;
  description: string;
  timeline: TimelineEvent[];
  final_metrics: Record<string, number>;
  risk_score: number;
  recommendations: string[];
}

interface TimelineEvent {
  event_id: string;
  timestamp: string;
  event_type: string;
  description: string;
  impact_score: number;
  affected_zones: string[];
}

interface ImpactAssessment {
  category: string;
  severity: string;
  description: string;
  metrics: Record<string, number>;
  mitigation_options: string[];
  recovery_time_hours: number;
}

interface RecommendedAction {
  action: string;
  category: string;
  priority: string;
  timing: string;
}

export default function ScenarioSimulator() {
  const [templates, setTemplates] = useState<ScenarioTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ScenarioTemplate | null>(null);
  const [variables, setVariables] = useState<ScenarioVariable[]>([]);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [selectedPath, setSelectedPath] = useState<OutcomePath | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationProgress, setSimulationProgress] = useState(0);
  const [activeTab, setActiveTab] = useState<"setup" | "results" | "timeline">("setup");

  useEffect(() => {
    const mockTemplates: ScenarioTemplate[] = [
      {
        scenario_id: "template-hurricane-cat3",
        scenario_type: "hurricane",
        name: "Category 3 Hurricane",
        description: "Simulation of a Category 3 hurricane impact on Riviera Beach",
        variables: [
          { variable_id: "v1", name: "Wind Speed", description: "Maximum sustained winds", min_value: 111, max_value: 129, default_value: 120, current_value: 120, unit: "mph", category: "weather" },
          { variable_id: "v2", name: "Storm Surge", description: "Expected storm surge height", min_value: 6, max_value: 12, default_value: 9, current_value: 9, unit: "feet", category: "weather" },
          { variable_id: "v3", name: "Rainfall", description: "Expected rainfall amount", min_value: 6, max_value: 15, default_value: 10, current_value: 10, unit: "inches", category: "weather" },
          { variable_id: "v4", name: "Evacuation Compliance", description: "Expected evacuation compliance rate", min_value: 50, max_value: 95, default_value: 75, current_value: 75, unit: "%", category: "population" },
        ],
        duration_hours: 72,
        affected_zones: ["singer_island", "marina", "downtown", "westside"],
      },
      {
        scenario_id: "template-major-event",
        scenario_type: "special_event",
        name: "Major Public Event",
        description: "Simulation of a major public event at the marina",
        variables: [
          { variable_id: "v1", name: "Expected Attendance", description: "Number of attendees", min_value: 5000, max_value: 50000, default_value: 15000, current_value: 15000, unit: "people", category: "crowd" },
          { variable_id: "v2", name: "Event Duration", description: "Duration of the event", min_value: 4, max_value: 12, default_value: 6, current_value: 6, unit: "hours", category: "timing" },
          { variable_id: "v3", name: "Parking Capacity", description: "Available parking spaces", min_value: 500, max_value: 5000, default_value: 2000, current_value: 2000, unit: "spaces", category: "infrastructure" },
        ],
        duration_hours: 12,
        affected_zones: ["marina", "downtown"],
      },
      {
        scenario_id: "template-power-outage",
        scenario_type: "infrastructure_outage",
        name: "Major Power Outage",
        description: "Simulation of a major power outage affecting multiple zones",
        variables: [
          { variable_id: "v1", name: "Customers Affected", description: "Number of customers without power", min_value: 1000, max_value: 20000, default_value: 5000, current_value: 5000, unit: "customers", category: "utilities" },
          { variable_id: "v2", name: "Estimated Restoration", description: "Expected restoration time", min_value: 2, max_value: 48, default_value: 8, current_value: 8, unit: "hours", category: "timing" },
          { variable_id: "v3", name: "Critical Facilities", description: "Number of critical facilities affected", min_value: 0, max_value: 10, default_value: 2, current_value: 2, unit: "facilities", category: "infrastructure" },
        ],
        duration_hours: 24,
        affected_zones: ["downtown", "westside", "industrial"],
      },
      {
        scenario_id: "template-road-closure",
        scenario_type: "road_closure",
        name: "Major Road Closure",
        description: "Simulation of a major road closure on Blue Heron Blvd",
        variables: [
          { variable_id: "v1", name: "Closure Duration", description: "Duration of road closure", min_value: 1, max_value: 72, default_value: 8, current_value: 8, unit: "hours", category: "timing" },
          { variable_id: "v2", name: "Lanes Affected", description: "Number of lanes closed", min_value: 1, max_value: 4, default_value: 2, current_value: 2, unit: "lanes", category: "infrastructure" },
          { variable_id: "v3", name: "Detour Capacity", description: "Capacity of detour routes", min_value: 50, max_value: 100, default_value: 70, current_value: 70, unit: "%", category: "traffic" },
        ],
        duration_hours: 12,
        affected_zones: ["downtown", "marina"],
      },
    ];

    setTemplates(mockTemplates);
  }, []);

  const handleSelectTemplate = (template: ScenarioTemplate) => {
    setSelectedTemplate(template);
    setVariables(template.variables.map(v => ({ ...v })));
    setSimulationResult(null);
    setSelectedPath(null);
    setActiveTab("setup");
  };

  const handleVariableChange = (variableId: string, value: number) => {
    setVariables(prev => prev.map(v => 
      v.variable_id === variableId ? { ...v, current_value: value } : v
    ));
  };

  const handleRunSimulation = async () => {
    if (!selectedTemplate) return;

    setIsSimulating(true);
    setSimulationProgress(0);

    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 200));
      setSimulationProgress(i);
    }

    const mockResult: SimulationResult = {
      result_id: `sim-${Date.now()}`,
      scenario_id: selectedTemplate.scenario_id,
      status: "completed",
      outcome_paths: [
        {
          path_id: "path-best",
          name: "Best Case",
          probability: 0.25,
          description: "Optimal response with minimal impact",
          timeline: generateMockTimeline(selectedTemplate, 0.5),
          final_metrics: { traffic_flow: 0.65, response_time: 6.2, coverage: 0.8, utility_uptime: 0.95 },
          risk_score: 0.35,
          recommendations: ["Maintain current resource levels", "Continue monitoring situation"],
        },
        {
          path_id: "path-likely",
          name: "Most Likely",
          probability: 0.50,
          description: "Expected outcome based on historical data",
          timeline: generateMockTimeline(selectedTemplate, 1.0),
          final_metrics: { traffic_flow: 0.45, response_time: 8.5, coverage: 0.65, utility_uptime: 0.85 },
          risk_score: 0.55,
          recommendations: ["Increase patrol presence", "Activate traffic management", "Pre-position resources"],
        },
        {
          path_id: "path-worst",
          name: "Worst Case",
          probability: 0.25,
          description: "Maximum impact scenario",
          timeline: generateMockTimeline(selectedTemplate, 1.8),
          final_metrics: { traffic_flow: 0.25, response_time: 12.0, coverage: 0.45, utility_uptime: 0.6 },
          risk_score: 0.85,
          recommendations: ["Request mutual aid", "Activate EOC", "Implement evacuation protocols"],
        },
      ],
      impact_assessments: [
        {
          category: "traffic",
          severity: "high",
          description: "Significant traffic disruption expected",
          metrics: { congestion_increase: 45, travel_time_increase: 30 },
          mitigation_options: ["Activate traffic management center", "Deploy traffic control officers"],
          recovery_time_hours: 8,
        },
        {
          category: "public_safety",
          severity: "moderate",
          description: "Increased demand on emergency services",
          metrics: { response_time_increase: 25, coverage_reduction: 15 },
          mitigation_options: ["Increase patrol presence", "Activate reserve officers"],
          recovery_time_hours: 12,
        },
        {
          category: "utilities",
          severity: selectedTemplate.scenario_type === "infrastructure_outage" ? "severe" : "low",
          description: "Potential utility service disruption",
          metrics: { outage_probability: 0.3, customers_affected: 2500 },
          mitigation_options: ["Pre-position repair crews", "Activate backup generators"],
          recovery_time_hours: 24,
        },
      ],
      overall_risk_score: 0.58,
      recommended_actions: [
        { action: "Activate traffic management center", category: "traffic", priority: "high", timing: "immediate" },
        { action: "Increase patrol presence in affected zones", category: "public_safety", priority: "high", timing: "immediate" },
        { action: "Pre-position utility crews", category: "utilities", priority: "medium", timing: "planned" },
        { action: "Coordinate with neighboring agencies", category: "emergency_services", priority: "medium", timing: "planned" },
      ],
      resource_requirements: {
        police_units: 5,
        fire_units: 3,
        ems_units: 4,
        public_works_crews: 2,
        utility_crews: 3,
      },
      estimated_cost: 45000,
    };

    setSimulationResult(mockResult);
    setSelectedPath(mockResult.outcome_paths[1]);
    setIsSimulating(false);
    setActiveTab("results");
  };

  const generateMockTimeline = (template: ScenarioTemplate, multiplier: number): TimelineEvent[] => {
    const events: TimelineEvent[] = [];
    const startTime = new Date();
    const eventTypes = ["warning_issued", "resources_deployed", "impact_detected", "response_initiated", "situation_stabilizing"];

    for (let i = 0; i < 8; i++) {
      events.push({
        event_id: `evt-${i}`,
        timestamp: new Date(startTime.getTime() + i * 3600000 * (template.duration_hours / 8)).toISOString(),
        event_type: eventTypes[i % eventTypes.length],
        description: `${eventTypes[i % eventTypes.length].replace(/_/g, " ")} - ${template.name}`,
        impact_score: Math.min(0.3 + (i / 8) * 0.5 * multiplier, 1.0),
        affected_zones: template.affected_zones.slice(0, Math.min(i + 1, template.affected_zones.length)),
      });
    }

    return events;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "severe":
      case "catastrophic":
        return "text-red-400 bg-red-500/20";
      case "high":
        return "text-orange-400 bg-orange-500/20";
      case "moderate":
        return "text-yellow-400 bg-yellow-500/20";
      default:
        return "text-blue-400 bg-blue-500/20";
    }
  };

  const getRiskColor = (risk: number) => {
    if (risk >= 0.7) return "text-red-400";
    if (risk >= 0.5) return "text-orange-400";
    if (risk >= 0.3) return "text-yellow-400";
    return "text-green-400";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Scenario Simulator</h2>
          <p className="text-sm text-gray-400">Model what-if scenarios and analyze potential outcomes</p>
        </div>
        {selectedTemplate && (
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab("setup")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === "setup" ? "bg-blue-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              Setup
            </button>
            <button
              onClick={() => setActiveTab("results")}
              disabled={!simulationResult}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === "results" ? "bg-blue-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              } disabled:opacity-50`}
            >
              Results
            </button>
            <button
              onClick={() => setActiveTab("timeline")}
              disabled={!simulationResult}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === "timeline" ? "bg-blue-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              } disabled:opacity-50`}
            >
              Timeline
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="px-4 py-3 border-b border-gray-700">
              <h3 className="font-medium text-white">Scenario Templates</h3>
            </div>
            <div className="p-2 space-y-2 max-h-96 overflow-y-auto">
              {templates.map((template) => (
                <button
                  key={template.scenario_id}
                  onClick={() => handleSelectTemplate(template)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedTemplate?.scenario_id === template.scenario_id
                      ? "bg-blue-600/20 border border-blue-500"
                      : "bg-gray-700/50 border border-transparent hover:bg-gray-700"
                  }`}
                >
                  <div className="font-medium text-white text-sm">{template.name}</div>
                  <div className="text-xs text-gray-400 mt-1">{template.description}</div>
                  <div className="flex items-center space-x-2 mt-2">
                    <span className="text-xs px-2 py-0.5 bg-gray-600 rounded text-gray-300">
                      {template.duration_hours}h
                    </span>
                    <span className="text-xs px-2 py-0.5 bg-gray-600 rounded text-gray-300">
                      {template.affected_zones.length} zones
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-3">
          {!selectedTemplate ? (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
              <svg className="w-16 h-16 mx-auto text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-white">Select a Scenario Template</h3>
              <p className="mt-2 text-gray-400">Choose a scenario from the left panel to begin simulation</p>
            </div>
          ) : activeTab === "setup" ? (
            <div className="space-y-6">
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-medium text-white">{selectedTemplate.name}</h3>
                    <p className="text-sm text-gray-400">{selectedTemplate.description}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-400">Duration:</span>
                    <span className="text-white font-medium">{selectedTemplate.duration_hours} hours</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {variables.map((variable) => (
                    <div key={variable.variable_id} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-medium text-gray-300">{variable.name}</label>
                        <span className="text-sm text-white font-medium">
                          {variable.current_value} {variable.unit}
                        </span>
                      </div>
                      <input
                        type="range"
                        min={variable.min_value}
                        max={variable.max_value}
                        value={variable.current_value}
                        onChange={(e) => handleVariableChange(variable.variable_id, Number(e.target.value))}
                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                      />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{variable.min_value} {variable.unit}</span>
                        <span>{variable.max_value} {variable.unit}</span>
                      </div>
                      <p className="text-xs text-gray-500">{variable.description}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-6 pt-6 border-t border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm text-gray-400">Affected Zones: </span>
                      <span className="text-white">{selectedTemplate.affected_zones.join(", ").replace(/_/g, " ")}</span>
                    </div>
                    <button
                      onClick={handleRunSimulation}
                      disabled={isSimulating}
                      className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center space-x-2 transition-colors disabled:opacity-50"
                    >
                      {isSimulating ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Simulating... {simulationProgress}%</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span>Run Simulation</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : activeTab === "results" && simulationResult ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                  <div className="text-sm text-gray-400">Overall Risk Score</div>
                  <div className={`text-3xl font-bold ${getRiskColor(simulationResult.overall_risk_score)}`}>
                    {(simulationResult.overall_risk_score * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                  <div className="text-sm text-gray-400">Estimated Cost</div>
                  <div className="text-3xl font-bold text-white">
                    ${simulationResult.estimated_cost.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                  <div className="text-sm text-gray-400">Resources Needed</div>
                  <div className="text-3xl font-bold text-white">
                    {Object.values(simulationResult.resource_requirements).reduce((a, b) => a + b, 0)}
                  </div>
                </div>
                <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                  <div className="text-sm text-gray-400">Impact Categories</div>
                  <div className="text-3xl font-bold text-white">
                    {simulationResult.impact_assessments.length}
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg border border-gray-700">
                <div className="px-6 py-4 border-b border-gray-700">
                  <h3 className="text-lg font-medium text-white">Outcome Paths</h3>
                </div>
                <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                  {simulationResult.outcome_paths.map((path) => (
                    <button
                      key={path.path_id}
                      onClick={() => setSelectedPath(path)}
                      className={`text-left p-4 rounded-lg border transition-colors ${
                        selectedPath?.path_id === path.path_id
                          ? "bg-blue-600/20 border-blue-500"
                          : "bg-gray-700/50 border-gray-600 hover:bg-gray-700"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-white">{path.name}</span>
                        <span className={`text-sm font-medium ${getRiskColor(path.risk_score)}`}>
                          {(path.risk_score * 100).toFixed(0)}% risk
                        </span>
                      </div>
                      <div className="text-sm text-gray-400 mb-2">{path.description}</div>
                      <div className="text-xs text-gray-500">
                        Probability: {(path.probability * 100).toFixed(0)}%
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gray-800 rounded-lg border border-gray-700">
                  <div className="px-6 py-4 border-b border-gray-700">
                    <h3 className="text-lg font-medium text-white">Impact Assessments</h3>
                  </div>
                  <div className="p-4 space-y-3">
                    {simulationResult.impact_assessments.map((assessment, i) => (
                      <div key={i} className="bg-gray-700/50 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-white capitalize">{assessment.category.replace(/_/g, " ")}</span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(assessment.severity)}`}>
                            {assessment.severity}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 mb-2">{assessment.description}</p>
                        <div className="text-xs text-gray-500">
                          Recovery time: {assessment.recovery_time_hours} hours
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg border border-gray-700">
                  <div className="px-6 py-4 border-b border-gray-700">
                    <h3 className="text-lg font-medium text-white">Recommended Actions</h3>
                  </div>
                  <div className="p-4 space-y-2">
                    {simulationResult.recommended_actions.map((action, i) => (
                      <div key={i} className="flex items-center justify-between bg-gray-700/50 rounded-lg p-3">
                        <div>
                          <div className="text-white text-sm">{action.action}</div>
                          <div className="text-xs text-gray-500 capitalize">{action.category.replace(/_/g, " ")}</div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            action.priority === "high" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"
                          }`}>
                            {action.priority}
                          </span>
                          <span className="text-xs text-gray-400">{action.timing}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-white">Resource Requirements</h3>
                  <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors">
                    Download Report
                  </button>
                </div>
                <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4">
                  {Object.entries(simulationResult.resource_requirements).map(([resource, count]) => (
                    <div key={resource} className="bg-gray-700/50 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-white">{count}</div>
                      <div className="text-xs text-gray-400 capitalize">{resource.replace(/_/g, " ")}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : activeTab === "timeline" && simulationResult && selectedPath ? (
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="px-6 py-4 border-b border-gray-700">
                <h3 className="text-lg font-medium text-white">Timeline: {selectedPath.name}</h3>
                <p className="text-sm text-gray-400">Event progression for selected outcome path</p>
              </div>
              <div className="p-6">
                <div className="relative">
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-700"></div>
                  <div className="space-y-6">
                    {selectedPath.timeline.map((event, i) => (
                      <div key={event.event_id} className="relative pl-10">
                        <div className={`absolute left-2 w-4 h-4 rounded-full border-2 ${
                          event.impact_score > 0.7 ? "bg-red-500 border-red-400" :
                          event.impact_score > 0.4 ? "bg-yellow-500 border-yellow-400" :
                          "bg-blue-500 border-blue-400"
                        }`}></div>
                        <div className="bg-gray-700/50 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-white capitalize">
                              {event.event_type.replace(/_/g, " ")}
                            </span>
                            <span className="text-sm text-gray-400">
                              {new Date(event.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-300">{event.description}</p>
                          <div className="mt-2 flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <span className="text-xs text-gray-500">Impact:</span>
                              <div className="w-24 bg-gray-600 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${
                                    event.impact_score > 0.7 ? "bg-red-500" :
                                    event.impact_score > 0.4 ? "bg-yellow-500" :
                                    "bg-blue-500"
                                  }`}
                                  style={{ width: `${event.impact_score * 100}%` }}
                                ></div>
                              </div>
                            </div>
                            <span className="text-xs text-gray-500">
                              Zones: {event.affected_zones.join(", ").replace(/_/g, " ")}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-700">
                  <h4 className="font-medium text-white mb-4">Final Metrics</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(selectedPath.final_metrics).map(([key, value]) => (
                      <div key={key} className="bg-gray-700/50 rounded-lg p-3">
                        <div className="text-xs text-gray-400 capitalize">{key.replace(/_/g, " ")}</div>
                        <div className="text-lg font-bold text-white">
                          {typeof value === "number" && value < 10 ? value.toFixed(1) : (value * 100).toFixed(0)}
                          {typeof value === "number" && value < 1 ? "%" : ""}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-700">
                  <h4 className="font-medium text-white mb-4">Path Recommendations</h4>
                  <ul className="space-y-2">
                    {selectedPath.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <svg className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-gray-300">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

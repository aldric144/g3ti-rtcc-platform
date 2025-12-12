"use client";

import React, { useState, useEffect } from "react";

interface GlobalEvent {
  event_id: string;
  category: string;
  title: string;
  description: string;
  timestamp: string;
  location: {
    lat: number;
    lon: number;
  };
  affected_regions: string[];
  affected_countries: string[];
  actors: string[];
  impact_magnitude: number;
}

interface EventCorrelation {
  correlation_id: string;
  source_event_id: string;
  target_event_id: string;
  correlation_type: string;
  strength: number;
  time_lag_hours: number;
}

interface CascadeEffect {
  cascade_id: string;
  trigger_event_id: string;
  cascade_type: string;
  total_impact_score: number;
  probability: number;
  propagation_path: Array<{
    step: number;
    category: string;
    impact: number;
    time_offset_days: number;
  }>;
  mitigation_options: string[];
}

interface EventPattern {
  pattern_id: string;
  pattern_name: string;
  pattern_type: string;
  frequency: number;
  confidence: number;
  description: string;
}

const EVENT_CATEGORIES = [
  { id: "political", label: "Political", color: "bg-blue-500" },
  { id: "military", label: "Military", color: "bg-red-500" },
  { id: "economic", label: "Economic", color: "bg-yellow-500" },
  { id: "social", label: "Social", color: "bg-purple-500" },
  { id: "environmental", label: "Environmental", color: "bg-green-500" },
  { id: "technological", label: "Technological", color: "bg-cyan-500" },
  { id: "health", label: "Health", color: "bg-pink-500" },
  { id: "security", label: "Security", color: "bg-orange-500" },
];

const CORRELATION_TYPES = [
  { id: "causal", label: "Causal", color: "text-red-400" },
  { id: "temporal", label: "Temporal", color: "text-blue-400" },
  { id: "spatial", label: "Spatial", color: "text-green-400" },
  { id: "thematic", label: "Thematic", color: "text-purple-400" },
  { id: "actor_based", label: "Actor-Based", color: "text-orange-400" },
];

export default function EventCorrelationPanel() {
  const [events, setEvents] = useState<GlobalEvent[]>([]);
  const [correlations, setCorrelations] = useState<EventCorrelation[]>([]);
  const [cascades, setCascades] = useState<CascadeEffect[]>([]);
  const [patterns, setPatterns] = useState<EventPattern[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<GlobalEvent | null>(null);
  const [activeView, setActiveView] = useState<"events" | "correlations" | "cascades" | "patterns">("events");

  useEffect(() => {
    const mockEvents: GlobalEvent[] = [
      {
        event_id: "GE-001",
        category: "military",
        title: "Military Escalation in Eastern Europe",
        description: "Significant troop movements detected along border regions",
        timestamp: new Date().toISOString(),
        location: { lat: 50.0, lon: 36.0 },
        affected_regions: ["Eastern Europe"],
        affected_countries: ["Ukraine", "Russia"],
        actors: ["Russian Federation", "Ukraine"],
        impact_magnitude: 5,
      },
      {
        event_id: "GE-002",
        category: "economic",
        title: "Energy Price Surge",
        description: "Natural gas prices spike due to supply concerns",
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        location: { lat: 52.5, lon: 13.4 },
        affected_regions: ["Western Europe", "Eastern Europe"],
        affected_countries: ["Germany", "Poland", "France"],
        actors: ["EU", "Energy Companies"],
        impact_magnitude: 4,
      },
      {
        event_id: "GE-003",
        category: "political",
        title: "Diplomatic Tensions Rise",
        description: "Multiple countries recall ambassadors amid escalating crisis",
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        location: { lat: 48.8, lon: 2.3 },
        affected_regions: ["Western Europe", "North America"],
        affected_countries: ["France", "USA", "UK"],
        actors: ["NATO", "EU"],
        impact_magnitude: 4,
      },
      {
        event_id: "GE-004",
        category: "social",
        title: "Refugee Crisis Intensifies",
        description: "Large-scale population displacement reported",
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        location: { lat: 50.4, lon: 30.5 },
        affected_regions: ["Eastern Europe", "Western Europe"],
        affected_countries: ["Ukraine", "Poland", "Germany"],
        actors: ["UNHCR", "Red Cross"],
        impact_magnitude: 5,
      },
      {
        event_id: "GE-005",
        category: "security",
        title: "Cyber Attack on Critical Infrastructure",
        description: "Coordinated cyber attacks target power grid systems",
        timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        location: { lat: 50.0, lon: 36.0 },
        affected_regions: ["Eastern Europe"],
        affected_countries: ["Ukraine"],
        actors: ["Unknown Threat Actor"],
        impact_magnitude: 4,
      },
    ];
    setEvents(mockEvents);

    const mockCorrelations: EventCorrelation[] = [
      {
        correlation_id: "EC-001",
        source_event_id: "GE-001",
        target_event_id: "GE-002",
        correlation_type: "causal",
        strength: 0.85,
        time_lag_hours: 48,
      },
      {
        correlation_id: "EC-002",
        source_event_id: "GE-001",
        target_event_id: "GE-003",
        correlation_type: "causal",
        strength: 0.78,
        time_lag_hours: 24,
      },
      {
        correlation_id: "EC-003",
        source_event_id: "GE-001",
        target_event_id: "GE-004",
        correlation_type: "causal",
        strength: 0.92,
        time_lag_hours: 72,
      },
      {
        correlation_id: "EC-004",
        source_event_id: "GE-005",
        target_event_id: "GE-001",
        correlation_type: "temporal",
        strength: 0.65,
        time_lag_hours: -96,
      },
    ];
    setCorrelations(mockCorrelations);

    const mockCascades: CascadeEffect[] = [
      {
        cascade_id: "CE-001",
        trigger_event_id: "GE-001",
        cascade_type: "branching",
        total_impact_score: 85.5,
        probability: 0.82,
        propagation_path: [
          { step: 1, category: "political", impact: 4.8, time_offset_days: 7 },
          { step: 2, category: "economic", impact: 3.84, time_offset_days: 14 },
          { step: 3, category: "social", impact: 3.07, time_offset_days: 21 },
        ],
        mitigation_options: [
          "Diplomatic intervention",
          "Economic sanctions",
          "Peacekeeping deployment",
        ],
      },
    ];
    setCascades(mockCascades);

    const mockPatterns: EventPattern[] = [
      {
        pattern_id: "EP-001",
        pattern_name: "military -> political Pattern",
        pattern_type: "sequential",
        frequency: 8,
        confidence: 0.75,
        description: "Pattern of military events followed by political events",
      },
      {
        pattern_id: "EP-002",
        pattern_name: "economic -> social Pattern",
        pattern_type: "sequential",
        frequency: 5,
        confidence: 0.68,
        description: "Pattern of economic events followed by social events",
      },
    ];
    setPatterns(mockPatterns);
  }, []);

  const getImpactColor = (magnitude: number) => {
    if (magnitude >= 5) return "text-red-500";
    if (magnitude >= 4) return "text-orange-500";
    if (magnitude >= 3) return "text-yellow-500";
    return "text-green-500";
  };

  const getCategoryColor = (category: string) => {
    return EVENT_CATEGORIES.find(c => c.id === category)?.color || "bg-gray-500";
  };

  const getCorrelationColor = (type: string) => {
    return CORRELATION_TYPES.find(c => c.id === type)?.color || "text-gray-400";
  };

  const getEventById = (id: string) => events.find(e => e.event_id === id);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Event Categories</h2>
          <div className="space-y-2">
            {EVENT_CATEGORIES.map(category => {
              const count = events.filter(e => e.category === category.id).length;
              return (
                <div
                  key={category.id}
                  className="flex items-center justify-between p-2 bg-gray-700/50 rounded"
                >
                  <div className="flex items-center space-x-2">
                    <span className={`w-3 h-3 rounded-full ${category.color}`} />
                    <span className="text-sm">{category.label}</span>
                  </div>
                  <span className="text-sm font-bold">{count}</span>
                </div>
              );
            })}
          </div>

          <div className="mt-6 p-3 bg-gray-700/50 rounded-lg">
            <h3 className="text-sm font-medium mb-2">Correlation Types</h3>
            <div className="space-y-1 text-sm">
              {CORRELATION_TYPES.map(type => (
                <div key={type.id} className="flex items-center space-x-2">
                  <span className={`${type.color}`}>●</span>
                  <span className="text-gray-400">{type.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-3 bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Event Correlation Analysis</h2>
            <div className="flex space-x-2">
              {(["events", "correlations", "cascades", "patterns"] as const).map(view => (
                <button
                  key={view}
                  onClick={() => setActiveView(view)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeView === view
                      ? "bg-blue-600 text-white"
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  }`}
                >
                  {view.charAt(0).toUpperCase() + view.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {activeView === "events" && (
            <div className="space-y-3">
              {events.map(event => (
                <div
                  key={event.event_id}
                  className={`bg-gray-700/50 rounded-lg p-4 cursor-pointer transition-colors ${
                    selectedEvent?.event_id === event.event_id
                      ? "ring-2 ring-blue-500"
                      : "hover:bg-gray-700"
                  }`}
                  onClick={() => setSelectedEvent(event)}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded text-xs ${getCategoryColor(event.category)}`}>
                          {event.category}
                        </span>
                        <span className="font-mono text-xs text-gray-400">{event.event_id}</span>
                        <span className={`font-bold ${getImpactColor(event.impact_magnitude)}`}>
                          Impact: {event.impact_magnitude}
                        </span>
                      </div>
                      <h3 className="font-semibold mt-2">{event.title}</h3>
                      <p className="text-sm text-gray-400 mt-1">{event.description}</p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(event.timestamp).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-3 text-sm">
                    <div>
                      <span className="text-gray-400">Regions</span>
                      <p className="font-medium">{event.affected_regions.join(", ")}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Countries</span>
                      <p className="font-medium">{event.affected_countries.join(", ")}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Actors</span>
                      <p className="font-medium">{event.actors.join(", ")}</p>
                    </div>
                  </div>

                  <div className="mt-3">
                    <span className="text-gray-400 text-sm">Correlations: </span>
                    <span className="text-blue-400 text-sm">
                      {correlations.filter(
                        c => c.source_event_id === event.event_id || c.target_event_id === event.event_id
                      ).length} linked events
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeView === "correlations" && (
            <div className="space-y-3">
              {correlations.map(correlation => {
                const sourceEvent = getEventById(correlation.source_event_id);
                const targetEvent = getEventById(correlation.target_event_id);
                return (
                  <div key={correlation.correlation_id} className="bg-gray-700/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className={`font-medium ${getCorrelationColor(correlation.correlation_type)}`}>
                          {correlation.correlation_type.replace(/_/g, " ")}
                        </span>
                        <span className="font-mono text-xs text-gray-400">{correlation.correlation_id}</span>
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-400">Strength: </span>
                        <span className="font-bold">{(correlation.strength * 100).toFixed(0)}%</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="flex-1 p-3 bg-gray-600/50 rounded">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-0.5 rounded text-xs ${getCategoryColor(sourceEvent?.category || "")}`}>
                            {sourceEvent?.category}
                          </span>
                          <span className="font-mono text-xs">{correlation.source_event_id}</span>
                        </div>
                        <p className="text-sm mt-1 truncate">{sourceEvent?.title}</p>
                      </div>

                      <div className="flex flex-col items-center">
                        <span className="text-2xl">→</span>
                        <span className="text-xs text-gray-400">
                          {correlation.time_lag_hours > 0 ? `+${correlation.time_lag_hours}h` : `${correlation.time_lag_hours}h`}
                        </span>
                      </div>

                      <div className="flex-1 p-3 bg-gray-600/50 rounded">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-0.5 rounded text-xs ${getCategoryColor(targetEvent?.category || "")}`}>
                            {targetEvent?.category}
                          </span>
                          <span className="font-mono text-xs">{correlation.target_event_id}</span>
                        </div>
                        <p className="text-sm mt-1 truncate">{targetEvent?.title}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {activeView === "cascades" && (
            <div className="space-y-3">
              {cascades.map(cascade => {
                const triggerEvent = getEventById(cascade.trigger_event_id);
                return (
                  <div key={cascade.cascade_id} className="bg-gray-700/50 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="px-2 py-0.5 rounded text-xs bg-red-500">
                            {cascade.cascade_type}
                          </span>
                          <span className="font-mono text-xs text-gray-400">{cascade.cascade_id}</span>
                        </div>
                        <h3 className="font-semibold mt-2">Cascade from: {triggerEvent?.title}</h3>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-orange-400">
                          {cascade.total_impact_score.toFixed(1)}
                        </div>
                        <div className="text-xs text-gray-400">Total Impact</div>
                      </div>
                    </div>

                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-400">Probability</span>
                        <span className="font-bold">{(cascade.probability * 100).toFixed(0)}%</span>
                      </div>
                      <div className="bg-gray-600 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${cascade.probability * 100}%` }}
                        />
                      </div>
                    </div>

                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Propagation Path</h4>
                      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
                        <div className="flex-shrink-0 p-2 bg-red-600/30 rounded text-center">
                          <div className="text-xs text-gray-400">Trigger</div>
                          <div className="font-medium">{triggerEvent?.category}</div>
                        </div>
                        {cascade.propagation_path.map((step, index) => (
                          <React.Fragment key={step.step}>
                            <span className="text-gray-500">→</span>
                            <div className="flex-shrink-0 p-2 bg-gray-600/50 rounded text-center">
                              <div className="text-xs text-gray-400">Step {step.step}</div>
                              <div className="font-medium">{step.category}</div>
                              <div className="text-xs text-orange-400">+{step.time_offset_days}d</div>
                            </div>
                          </React.Fragment>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Mitigation Options</h4>
                      <div className="flex flex-wrap gap-2">
                        {cascade.mitigation_options.map((option, index) => (
                          <span key={index} className="px-3 py-1 bg-blue-600/30 rounded text-sm">
                            {option}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {activeView === "patterns" && (
            <div className="space-y-3">
              {patterns.map(pattern => (
                <div key={pattern.pattern_id} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-0.5 rounded text-xs bg-purple-500">
                          {pattern.pattern_type}
                        </span>
                        <span className="font-mono text-xs text-gray-400">{pattern.pattern_id}</span>
                      </div>
                      <h3 className="font-semibold mt-2">{pattern.pattern_name}</h3>
                      <p className="text-sm text-gray-400 mt-1">{pattern.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-400">{pattern.frequency}</div>
                      <div className="text-xs text-gray-400">Occurrences</div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-400">Confidence</span>
                      <span className="font-bold">{(pattern.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="bg-gray-600 rounded-full h-2">
                      <div
                        className="bg-purple-500 h-2 rounded-full"
                        style={{ width: `${pattern.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

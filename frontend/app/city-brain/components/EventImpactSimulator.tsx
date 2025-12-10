"use client";

import { useState } from "react";

interface SimulationResult {
  scenario: string;
  timestamp: string;
  impact: {
    traffic: {
      congestion_increase_percent: number;
      affected_roads: string[];
      estimated_delays_minutes: number;
    };
    population: {
      affected_population: number;
      displacement_zones: string[];
    };
    infrastructure: {
      at_risk_elements: string[];
      estimated_damage_millions: number;
    };
    emergency_services: {
      additional_units_needed: number;
      response_time_increase_percent: number;
    };
  };
  recommendations: string[];
  timeline: Array<{
    time: string;
    event: string;
  }>;
}

type ScenarioType = "hurricane" | "flood" | "major_event" | "power_outage" | "traffic_incident";

export default function EventImpactSimulator() {
  const [scenarioType, setScenarioType] = useState<ScenarioType>("hurricane");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [hurricaneCategory, setHurricaneCategory] = useState(1);
  const [rainfallInches, setRainfallInches] = useState(4);
  const [eventAttendance, setEventAttendance] = useState(5000);
  const [outageCustomers, setOutageCustomers] = useState(2000);
  const [incidentSeverity, setIncidentSeverity] = useState("major");

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      
      let simulationResult: SimulationResult;
      
      switch (scenarioType) {
        case "hurricane":
          simulationResult = generateHurricaneSimulation(hurricaneCategory);
          break;
        case "flood":
          simulationResult = generateFloodSimulation(rainfallInches);
          break;
        case "major_event":
          simulationResult = generateEventSimulation(eventAttendance);
          break;
        case "power_outage":
          simulationResult = generateOutageSimulation(outageCustomers);
          break;
        case "traffic_incident":
          simulationResult = generateTrafficSimulation(incidentSeverity);
          break;
        default:
          throw new Error("Invalid scenario type");
      }
      
      setResult(simulationResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setLoading(false);
    }
  };

  const generateHurricaneSimulation = (category: number): SimulationResult => {
    const baseImpact = category * 20;
    return {
      scenario: `Category ${category} Hurricane`,
      timestamp: new Date().toISOString(),
      impact: {
        traffic: {
          congestion_increase_percent: baseImpact * 2,
          affected_roads: ["Blue Heron Blvd", "I-95", "Singer Island Causeway", "Military Trail"],
          estimated_delays_minutes: category * 30,
        },
        population: {
          affected_population: category * 8000,
          displacement_zones: category >= 3 ? ["Zone A", "Zone B", "Zone C"] : category >= 2 ? ["Zone A", "Zone B"] : ["Zone A"],
        },
        infrastructure: {
          at_risk_elements: ["Singer Island Substation", "Coastal Pump Stations", "Marina District Power Lines"],
          estimated_damage_millions: category * 50,
        },
        emergency_services: {
          additional_units_needed: category * 5,
          response_time_increase_percent: baseImpact,
        },
      },
      recommendations: [
        `Issue mandatory evacuation for Zone${category >= 2 ? "s" : ""} ${category >= 3 ? "A, B, C" : category >= 2 ? "A, B" : "A"}`,
        "Activate emergency shelters",
        "Pre-position emergency response teams",
        "Coordinate with FPL for rapid restoration",
        "Implement contraflow on evacuation routes",
      ],
      timeline: [
        { time: "-48h", event: "Hurricane Watch issued" },
        { time: "-36h", event: "Hurricane Warning issued" },
        { time: "-24h", event: "Mandatory evacuation begins" },
        { time: "-12h", event: "Shelters open" },
        { time: "0h", event: "Expected landfall" },
        { time: "+6h", event: "Peak storm surge" },
        { time: "+12h", event: "Storm passes" },
        { time: "+24h", event: "Damage assessment begins" },
      ],
    };
  };

  const generateFloodSimulation = (rainfall: number): SimulationResult => {
    const severity = rainfall > 6 ? "major" : rainfall > 4 ? "moderate" : "minor";
    return {
      scenario: `${severity.charAt(0).toUpperCase() + severity.slice(1)} Flooding (${rainfall}" rainfall)`,
      timestamp: new Date().toISOString(),
      impact: {
        traffic: {
          congestion_increase_percent: rainfall * 8,
          affected_roads: ["Blue Heron Blvd (low areas)", "Marina District", "Singer Island"],
          estimated_delays_minutes: rainfall * 5,
        },
        population: {
          affected_population: rainfall * 500,
          displacement_zones: rainfall > 6 ? ["Marina District", "Singer Island Lowlands"] : ["Marina District"],
        },
        infrastructure: {
          at_risk_elements: ["Lift Stations", "Storm Drains", "Road Underpasses"],
          estimated_damage_millions: rainfall * 2,
        },
        emergency_services: {
          additional_units_needed: Math.ceil(rainfall / 2),
          response_time_increase_percent: rainfall * 5,
        },
      },
      recommendations: [
        "Activate pump stations at maximum capacity",
        "Deploy high-water rescue teams",
        "Close flooded roadways",
        "Issue flood warnings to affected areas",
      ],
      timeline: [
        { time: "0h", event: "Heavy rainfall begins" },
        { time: `+${Math.ceil(rainfall / 2)}h`, event: "Street flooding reported" },
        { time: `+${rainfall}h`, event: "Peak flooding expected" },
        { time: `+${rainfall + 4}h`, event: "Waters begin receding" },
      ],
    };
  };

  const generateEventSimulation = (attendance: number): SimulationResult => {
    return {
      scenario: `Major Event (${attendance.toLocaleString()} attendees)`,
      timestamp: new Date().toISOString(),
      impact: {
        traffic: {
          congestion_increase_percent: Math.min(attendance / 100, 80),
          affected_roads: ["Blue Heron Blvd", "Broadway", "Ocean Drive"],
          estimated_delays_minutes: Math.ceil(attendance / 500),
        },
        population: {
          affected_population: attendance,
          displacement_zones: [],
        },
        infrastructure: {
          at_risk_elements: [],
          estimated_damage_millions: 0,
        },
        emergency_services: {
          additional_units_needed: Math.ceil(attendance / 2000),
          response_time_increase_percent: Math.min(attendance / 200, 30),
        },
      },
      recommendations: [
        "Deploy traffic control officers",
        "Activate overflow parking areas",
        "Increase patrol presence",
        "Coordinate with event organizers",
        "Pre-position EMS units",
      ],
      timeline: [
        { time: "-2h", event: "Traffic control begins" },
        { time: "-1h", event: "Attendees begin arriving" },
        { time: "0h", event: "Event starts" },
        { time: "+3h", event: "Peak attendance" },
        { time: "+5h", event: "Event ends, egress begins" },
        { time: "+6h", event: "Traffic returns to normal" },
      ],
    };
  };

  const generateOutageSimulation = (customers: number): SimulationResult => {
    return {
      scenario: `Power Outage (${customers.toLocaleString()} customers)`,
      timestamp: new Date().toISOString(),
      impact: {
        traffic: {
          congestion_increase_percent: customers > 5000 ? 40 : 20,
          affected_roads: ["Affected intersections"],
          estimated_delays_minutes: 15,
        },
        population: {
          affected_population: customers * 2.5,
          displacement_zones: [],
        },
        infrastructure: {
          at_risk_elements: ["Traffic signals", "Water pumps", "Communication systems"],
          estimated_damage_millions: 0.1,
        },
        emergency_services: {
          additional_units_needed: Math.ceil(customers / 3000),
          response_time_increase_percent: 15,
        },
      },
      recommendations: [
        "Deploy traffic control to affected intersections",
        "Activate backup generators at critical facilities",
        "Coordinate with FPL for restoration timeline",
        "Issue public notification",
      ],
      timeline: [
        { time: "0h", event: "Outage reported" },
        { time: "+15m", event: "FPL crews dispatched" },
        { time: "+1h", event: "Cause identified" },
        { time: "+2h", event: "Estimated restoration" },
      ],
    };
  };

  const generateTrafficSimulation = (severity: string): SimulationResult => {
    const multiplier = severity === "major" ? 3 : severity === "moderate" ? 2 : 1;
    return {
      scenario: `${severity.charAt(0).toUpperCase() + severity.slice(1)} Traffic Incident`,
      timestamp: new Date().toISOString(),
      impact: {
        traffic: {
          congestion_increase_percent: multiplier * 30,
          affected_roads: ["Blue Heron Blvd", "I-95 (nearby exits)"],
          estimated_delays_minutes: multiplier * 20,
        },
        population: {
          affected_population: multiplier * 1000,
          displacement_zones: [],
        },
        infrastructure: {
          at_risk_elements: [],
          estimated_damage_millions: 0,
        },
        emergency_services: {
          additional_units_needed: multiplier * 2,
          response_time_increase_percent: multiplier * 10,
        },
      },
      recommendations: [
        "Deploy traffic control",
        "Activate alternate route signage",
        "Coordinate with FDOT",
        "Issue traffic advisory",
      ],
      timeline: [
        { time: "0m", event: "Incident reported" },
        { time: "+5m", event: "First responders dispatched" },
        { time: "+15m", event: "Scene secured" },
        { time: `+${multiplier * 30}m`, event: "Lanes cleared" },
        { time: `+${multiplier * 45}m`, event: "Traffic returns to normal" },
      ],
    };
  };

  const scenarios: { id: ScenarioType; label: string; icon: string }[] = [
    { id: "hurricane", label: "Hurricane", icon: "🌀" },
    { id: "flood", label: "Flooding", icon: "🌊" },
    { id: "major_event", label: "Major Event", icon: "🎉" },
    { id: "power_outage", label: "Power Outage", icon: "⚡" },
    { id: "traffic_incident", label: "Traffic Incident", icon: "🚗" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Event Impact Simulator</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="font-semibold mb-4">Scenario Configuration</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Scenario Type</label>
              <div className="grid grid-cols-2 gap-2">
                {scenarios.map((scenario) => (
                  <button
                    key={scenario.id}
                    onClick={() => setScenarioType(scenario.id)}
                    className={`flex items-center space-x-2 p-2 rounded ${
                      scenarioType === scenario.id
                        ? "bg-blue-600"
                        : "bg-gray-700 hover:bg-gray-600"
                    }`}
                  >
                    <span>{scenario.icon}</span>
                    <span className="text-sm">{scenario.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {scenarioType === "hurricane" && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Hurricane Category: {hurricaneCategory}
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={hurricaneCategory}
                  onChange={(e) => setHurricaneCategory(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            )}

            {scenarioType === "flood" && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Rainfall: {rainfallInches} inches
                </label>
                <input
                  type="range"
                  min="1"
                  max="12"
                  value={rainfallInches}
                  onChange={(e) => setRainfallInches(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            )}

            {scenarioType === "major_event" && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Expected Attendance: {eventAttendance.toLocaleString()}
                </label>
                <input
                  type="range"
                  min="1000"
                  max="20000"
                  step="1000"
                  value={eventAttendance}
                  onChange={(e) => setEventAttendance(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            )}

            {scenarioType === "power_outage" && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Customers Affected: {outageCustomers.toLocaleString()}
                </label>
                <input
                  type="range"
                  min="500"
                  max="10000"
                  step="500"
                  value={outageCustomers}
                  onChange={(e) => setOutageCustomers(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            )}

            {scenarioType === "traffic_incident" && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">Incident Severity</label>
                <select
                  value={incidentSeverity}
                  onChange={(e) => setIncidentSeverity(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                >
                  <option value="minor">Minor</option>
                  <option value="moderate">Moderate</option>
                  <option value="major">Major</option>
                </select>
              </div>
            )}

            <button
              onClick={runSimulation}
              disabled={loading}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded font-medium"
            >
              {loading ? "Running Simulation..." : "Run Simulation"}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {error && (
            <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
              <p className="text-red-400">Error: {error}</p>
            </div>
          )}

          {result && (
            <>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h3 className="font-semibold mb-2">{result.scenario}</h3>
                <p className="text-sm text-gray-400">
                  Simulated at {new Date(result.timestamp).toLocaleString()}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Traffic Impact</h4>
                  <p className="text-2xl font-bold text-orange-400">
                    +{result.impact.traffic.congestion_increase_percent}%
                  </p>
                  <p className="text-xs text-gray-500">congestion increase</p>
                  <p className="text-sm text-gray-400 mt-2">
                    Est. delays: {result.impact.traffic.estimated_delays_minutes} min
                  </p>
                </div>

                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Population Affected</h4>
                  <p className="text-2xl font-bold text-white">
                    {result.impact.population.affected_population.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500">people</p>
                </div>

                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Est. Damage</h4>
                  <p className="text-2xl font-bold text-red-400">
                    ${result.impact.infrastructure.estimated_damage_millions}M
                  </p>
                  <p className="text-xs text-gray-500">estimated</p>
                </div>

                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Additional Units</h4>
                  <p className="text-2xl font-bold text-blue-400">
                    +{result.impact.emergency_services.additional_units_needed}
                  </p>
                  <p className="text-xs text-gray-500">emergency units needed</p>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h4 className="font-semibold mb-3">Recommendations</h4>
                <ul className="space-y-2">
                  {result.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <span className="text-blue-400">•</span>
                      <span className="text-sm">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h4 className="font-semibold mb-3">Timeline</h4>
                <div className="space-y-2">
                  {result.timeline.map((item, idx) => (
                    <div key={idx} className="flex items-center space-x-4">
                      <span className="text-sm font-mono text-gray-400 w-16">{item.time}</span>
                      <div className="w-2 h-2 rounded-full bg-blue-500" />
                      <span className="text-sm">{item.event}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {!result && !loading && (
            <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 text-center">
              <p className="text-gray-500">
                Configure a scenario and click "Run Simulation" to see impact predictions
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

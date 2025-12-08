"use client";

/**
 * Shift Briefing Component
 *
 * Displays shift briefing intelligence pack with:
 * - Top zones of concern
 * - Vehicles and persons of interest
 * - Case developments
 * - AI anomalies
 * - Patrol route recommendations
 * - Tactical advisories
 */

import { useState, useEffect, useCallback } from "react";

interface ShiftBriefingProps {
  selectedShift: string;
}

interface ShiftBriefingData {
  briefing_id: string;
  shift: {
    code: string;
    name: string;
    start_hour: number;
    end_hour: number;
    duration_hours: number;
  };
  generated_at: string;
  valid_until: string;
  zones_of_concern: ZoneOfConcern[];
  entity_highlights: {
    vehicles_of_interest: VehicleOfInterest[];
    persons_of_interest: PersonOfInterest[];
  };
  case_developments: CaseDevelopment[];
  ai_anomalies: AIAnomaly[];
  tactical_advisories: TacticalAdvisory[];
  overnight_summary: string;
  patrol_routes?: PatrolRoute[];
  tactical_map?: TacticalMap;
  statistics: BriefingStatistics;
}

interface ZoneOfConcern {
  zone_id: string;
  risk_score: number;
  risk_level: string;
  center: { lat: number; lon: number };
  top_factors: { name: string; contribution: number }[];
  recommendation: string;
}

interface VehicleOfInterest {
  id: string;
  plate: string;
  description: string;
  risk_score: number;
  flags: string[];
  last_seen: { lat: number; lon: number; time: string };
  action: string;
}

interface PersonOfInterest {
  id: string;
  name: string;
  risk_score: number;
  flags: string[];
  last_known_location: { lat: number; lon: number };
  action: string;
}

interface CaseDevelopment {
  case_id: string;
  title: string;
  update_type: string;
  summary: string;
  updated_at: string;
  priority: string;
}

interface AIAnomaly {
  id: string;
  type: string;
  description: string;
  severity: string;
  location: { lat: number; lon: number };
  detected_at: string;
  confidence: number;
}

interface TacticalAdvisory {
  priority: string;
  type: string;
  title: string;
  description: string;
  action: string;
}

interface PatrolRoute {
  unit: string;
  route: { lat: number; lon: number; sequence: number }[];
  statistics: { total_distance: number; waypoint_count: number };
}

interface TacticalMap {
  heatmap: object;
  clusters: object[];
  hot_zones: object[];
  generated_at: string;
}

interface BriefingStatistics {
  zones_of_concern_count: number;
  critical_zones: number;
  high_risk_zones: number;
  vehicles_of_interest_count: number;
  stolen_vehicles: number;
  persons_of_interest_count: number;
  active_warrants: number;
  critical_advisories: number;
  high_advisories: number;
}

export function ShiftBriefing({ selectedShift }: ShiftBriefingProps) {
  const [briefing, setBriefing] = useState<ShiftBriefingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string>("overview");

  const fetchBriefing = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/tactical/shiftbrief?shift=${selectedShift}&include_routes=true&include_heatmaps=true`
      );
      if (!response.ok) throw new Error("Failed to fetch briefing");
      const data = await response.json();
      setBriefing(data);
    } catch (err) {
      console.error("Failed to fetch briefing:", err);
      setError(err instanceof Error ? err.message : "Failed to load briefing");
      setBriefing(generateMockBriefing(selectedShift));
    } finally {
      setLoading(false);
    }
  }, [selectedShift]);

  useEffect(() => {
    fetchBriefing();
  }, [fetchBriefing]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-32 bg-gray-800 rounded-lg" />
        <div className="h-64 bg-gray-800 rounded-lg" />
      </div>
    );
  }

  if (error && !briefing) {
    return (
      <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 text-red-400">
        {error}
      </div>
    );
  }

  if (!briefing) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-400">
        No briefing data available
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold">
              {briefing.shift.name} Briefing
            </h2>
            <p className="text-gray-400 text-sm">
              {briefing.briefing_id} | Generated:{" "}
              {new Date(briefing.generated_at).toLocaleString()}
            </p>
            <p className="text-gray-400 text-sm">
              Valid until: {new Date(briefing.valid_until).toLocaleString()}
            </p>
          </div>
          <button
            onClick={fetchBriefing}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-5 gap-4 mt-4">
          <QuickStat
            label="Critical Zones"
            value={briefing.statistics.critical_zones}
            color="red"
          />
          <QuickStat
            label="High Risk Zones"
            value={briefing.statistics.high_risk_zones}
            color="orange"
          />
          <QuickStat
            label="Stolen Vehicles"
            value={briefing.statistics.stolen_vehicles}
            color="yellow"
          />
          <QuickStat
            label="Active Warrants"
            value={briefing.statistics.active_warrants}
            color="purple"
          />
          <QuickStat
            label="Critical Advisories"
            value={briefing.statistics.critical_advisories}
            color="red"
          />
        </div>
      </div>

      {/* Section navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {[
          { id: "overview", label: "Overview" },
          { id: "advisories", label: "Advisories" },
          { id: "zones", label: "Zones" },
          { id: "vehicles", label: "Vehicles" },
          { id: "persons", label: "Persons" },
          { id: "cases", label: "Cases" },
          { id: "anomalies", label: "Anomalies" },
        ].map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`px-4 py-2 rounded text-sm whitespace-nowrap ${
              activeSection === section.id
                ? "bg-blue-600"
                : "bg-gray-700 hover:bg-gray-600"
            }`}
          >
            {section.label}
          </button>
        ))}
      </div>

      {/* Section content */}
      {activeSection === "overview" && (
        <OverviewSection briefing={briefing} />
      )}
      {activeSection === "advisories" && (
        <AdvisoriesSection advisories={briefing.tactical_advisories} />
      )}
      {activeSection === "zones" && (
        <ZonesSection zones={briefing.zones_of_concern} />
      )}
      {activeSection === "vehicles" && (
        <VehiclesSection
          vehicles={briefing.entity_highlights.vehicles_of_interest}
        />
      )}
      {activeSection === "persons" && (
        <PersonsSection
          persons={briefing.entity_highlights.persons_of_interest}
        />
      )}
      {activeSection === "cases" && (
        <CasesSection cases={briefing.case_developments} />
      )}
      {activeSection === "anomalies" && (
        <AnomaliesSection anomalies={briefing.ai_anomalies} />
      )}
    </div>
  );
}

// Section components
function OverviewSection({ briefing }: { briefing: ShiftBriefingData }) {
  return (
    <div className="space-y-4">
      {/* Overnight summary */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">Overnight Summary</h3>
        <p className="text-gray-300">{briefing.overnight_summary}</p>
      </div>

      {/* Top advisories */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-3">Top Advisories</h3>
        <div className="space-y-2">
          {briefing.tactical_advisories.slice(0, 3).map((advisory, idx) => (
            <AdvisoryCard key={idx} advisory={advisory} />
          ))}
        </div>
      </div>

      {/* Top zones */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-3">Top Zones of Concern</h3>
        <div className="grid grid-cols-2 gap-3">
          {briefing.zones_of_concern.slice(0, 4).map((zone) => (
            <ZoneCard key={zone.zone_id} zone={zone} compact />
          ))}
        </div>
      </div>
    </div>
  );
}

function AdvisoriesSection({
  advisories,
}: {
  advisories: TacticalAdvisory[];
}) {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Tactical Advisories</h3>
      <div className="space-y-3">
        {advisories.map((advisory, idx) => (
          <AdvisoryCard key={idx} advisory={advisory} expanded />
        ))}
      </div>
    </div>
  );
}

function ZonesSection({ zones }: { zones: ZoneOfConcern[] }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Zones of Concern</h3>
      <div className="space-y-3">
        {zones.map((zone) => (
          <ZoneCard key={zone.zone_id} zone={zone} />
        ))}
      </div>
    </div>
  );
}

function VehiclesSection({ vehicles }: { vehicles: VehicleOfInterest[] }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Vehicles of Interest</h3>
      <div className="space-y-3">
        {vehicles.map((vehicle) => (
          <VehicleCard key={vehicle.id} vehicle={vehicle} />
        ))}
      </div>
    </div>
  );
}

function PersonsSection({ persons }: { persons: PersonOfInterest[] }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Persons of Interest</h3>
      <div className="space-y-3">
        {persons.map((person) => (
          <PersonCard key={person.id} person={person} />
        ))}
      </div>
    </div>
  );
}

function CasesSection({ cases }: { cases: CaseDevelopment[] }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Case Developments</h3>
      <div className="space-y-3">
        {cases.map((caseItem) => (
          <CaseCard key={caseItem.case_id} caseItem={caseItem} />
        ))}
      </div>
    </div>
  );
}

function AnomaliesSection({ anomalies }: { anomalies: AIAnomaly[] }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">AI Anomalies</h3>
      <div className="space-y-3">
        {anomalies.map((anomaly) => (
          <AnomalyCard key={anomaly.id} anomaly={anomaly} />
        ))}
      </div>
    </div>
  );
}

// Card components
function QuickStat({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: "red" | "orange" | "yellow" | "purple" | "blue";
}) {
  const colors = {
    red: "bg-red-900/30 border-red-700 text-red-400",
    orange: "bg-orange-900/30 border-orange-700 text-orange-400",
    yellow: "bg-yellow-900/30 border-yellow-700 text-yellow-400",
    purple: "bg-purple-900/30 border-purple-700 text-purple-400",
    blue: "bg-blue-900/30 border-blue-700 text-blue-400",
  };

  return (
    <div className={`p-3 rounded border ${colors[color]}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-xs opacity-80">{label}</div>
    </div>
  );
}

function AdvisoryCard({
  advisory,
  expanded = false,
}: {
  advisory: TacticalAdvisory;
  expanded?: boolean;
}) {
  const priorityColors: Record<string, string> = {
    critical: "border-red-500 bg-red-900/20",
    high: "border-orange-500 bg-orange-900/20",
    medium: "border-yellow-500 bg-yellow-900/20",
    low: "border-blue-500 bg-blue-900/20",
  };

  return (
    <div
      className={`p-3 rounded border-l-4 ${priorityColors[advisory.priority] || priorityColors.low}`}
    >
      <div className="flex justify-between items-start">
        <h4 className="font-medium">{advisory.title}</h4>
        <span className="text-xs uppercase px-2 py-0.5 bg-gray-700 rounded">
          {advisory.priority}
        </span>
      </div>
      <p className="text-sm text-gray-400 mt-1">{advisory.description}</p>
      {expanded && (
        <div className="mt-2 p-2 bg-gray-700/50 rounded text-sm">
          <span className="text-gray-400">Action: </span>
          {advisory.action}
        </div>
      )}
    </div>
  );
}

function ZoneCard({
  zone,
  compact = false,
}: {
  zone: ZoneOfConcern;
  compact?: boolean;
}) {
  const riskColors: Record<string, string> = {
    critical: "text-red-400",
    high: "text-orange-400",
    elevated: "text-yellow-400",
    moderate: "text-blue-400",
  };

  return (
    <div className="p-3 bg-gray-700 rounded">
      <div className="flex justify-between items-start">
        <span className="font-medium">{zone.zone_id}</span>
        <span className={`text-lg font-bold ${riskColors[zone.risk_level]}`}>
          {(zone.risk_score * 100).toFixed(0)}%
        </span>
      </div>
      {!compact && (
        <>
          <div className="text-sm text-gray-400 mt-1">
            Top factor: {zone.top_factors[0]?.name.replace(/_/g, " ")}
          </div>
          <div className="text-sm text-gray-300 mt-2">{zone.recommendation}</div>
        </>
      )}
    </div>
  );
}

function VehicleCard({ vehicle }: { vehicle: VehicleOfInterest }) {
  return (
    <div className="p-3 bg-gray-700 rounded">
      <div className="flex justify-between items-start">
        <div>
          <span className="font-mono font-bold text-lg">{vehicle.plate}</span>
          <span className="text-gray-400 ml-2">{vehicle.description}</span>
        </div>
        <div className="flex gap-1">
          {vehicle.flags.map((flag) => (
            <span
              key={flag}
              className={`text-xs px-2 py-0.5 rounded ${
                flag === "STOLEN"
                  ? "bg-red-900/50 text-red-400"
                  : flag === "HOTLIST"
                    ? "bg-orange-900/50 text-orange-400"
                    : "bg-gray-600 text-gray-300"
              }`}
            >
              {flag}
            </span>
          ))}
        </div>
      </div>
      <div className="text-sm text-gray-400 mt-1">
        Last seen: {new Date(vehicle.last_seen.time).toLocaleString()}
      </div>
      <div className="text-sm text-yellow-400 mt-2">{vehicle.action}</div>
    </div>
  );
}

function PersonCard({ person }: { person: PersonOfInterest }) {
  return (
    <div className="p-3 bg-gray-700 rounded">
      <div className="flex justify-between items-start">
        <span className="font-medium">{person.name}</span>
        <div className="flex gap-1">
          {person.flags.map((flag) => (
            <span
              key={flag}
              className={`text-xs px-2 py-0.5 rounded ${
                flag === "WARRANT"
                  ? "bg-red-900/50 text-red-400"
                  : flag === "GANG"
                    ? "bg-purple-900/50 text-purple-400"
                    : "bg-gray-600 text-gray-300"
              }`}
            >
              {flag}
            </span>
          ))}
        </div>
      </div>
      <div className="text-sm text-gray-400 mt-1">
        Risk Score: {(person.risk_score * 100).toFixed(0)}%
      </div>
      <div className="text-sm text-yellow-400 mt-2">{person.action}</div>
    </div>
  );
}

function CaseCard({ caseItem }: { caseItem: CaseDevelopment }) {
  return (
    <div className="p-3 bg-gray-700 rounded">
      <div className="flex justify-between items-start">
        <div>
          <span className="font-medium">{caseItem.case_id}</span>
          <span className="text-gray-400 ml-2">{caseItem.title}</span>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded ${
            caseItem.priority === "high"
              ? "bg-red-900/50 text-red-400"
              : "bg-gray-600 text-gray-300"
          }`}
        >
          {caseItem.update_type.replace(/_/g, " ")}
        </span>
      </div>
      <div className="text-sm text-gray-300 mt-2">{caseItem.summary}</div>
      <div className="text-xs text-gray-500 mt-1">
        Updated: {new Date(caseItem.updated_at).toLocaleString()}
      </div>
    </div>
  );
}

function AnomalyCard({ anomaly }: { anomaly: AIAnomaly }) {
  return (
    <div className="p-3 bg-gray-700 rounded">
      <div className="flex justify-between items-start">
        <span className="font-medium capitalize">
          {anomaly.type.replace(/_/g, " ")}
        </span>
        <span
          className={`text-xs px-2 py-0.5 rounded ${
            anomaly.severity === "high"
              ? "bg-red-900/50 text-red-400"
              : "bg-yellow-900/50 text-yellow-400"
          }`}
        >
          {anomaly.severity}
        </span>
      </div>
      <div className="text-sm text-gray-300 mt-1">{anomaly.description}</div>
      <div className="text-xs text-gray-500 mt-1">
        Confidence: {(anomaly.confidence * 100).toFixed(0)}% | Detected:{" "}
        {new Date(anomaly.detected_at).toLocaleString()}
      </div>
    </div>
  );
}

// Mock data generator
function generateMockBriefing(shift: string): ShiftBriefingData {
  const shiftInfo = {
    A: { name: "Day Shift", start_hour: 7, end_hour: 15 },
    B: { name: "Evening Shift", start_hour: 15, end_hour: 23 },
    C: { name: "Night Shift", start_hour: 23, end_hour: 7 },
  }[shift] || { name: "Day Shift", start_hour: 7, end_hour: 15 };

  return {
    briefing_id: `BRIEF-${shift}-${Date.now()}`,
    shift: {
      code: shift,
      name: shiftInfo.name,
      start_hour: shiftInfo.start_hour,
      end_hour: shiftInfo.end_hour,
      duration_hours: 8,
    },
    generated_at: new Date().toISOString(),
    valid_until: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
    zones_of_concern: [
      {
        zone_id: "micro_5_12",
        risk_score: 0.85,
        risk_level: "critical",
        center: { lat: 33.45, lon: -112.07 },
        top_factors: [{ name: "gunfire_frequency", contribution: 0.3 }],
        recommendation: "Immediate patrol presence required.",
      },
      {
        zone_id: "micro_3_8",
        risk_score: 0.72,
        risk_level: "high",
        center: { lat: 33.42, lon: -112.05 },
        top_factors: [{ name: "violent_crime_history", contribution: 0.25 }],
        recommendation: "Increased patrol frequency recommended.",
      },
    ],
    entity_highlights: {
      vehicles_of_interest: [
        {
          id: "VEH-1001",
          plate: "ABC1234",
          description: "Black Honda Accord",
          risk_score: 0.9,
          flags: ["STOLEN"],
          last_seen: {
            lat: 33.45,
            lon: -112.07,
            time: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          },
          action: "STOP AND RECOVER - Confirm stolen status",
        },
      ],
      persons_of_interest: [
        {
          id: "PER-2001",
          name: "John Doe",
          risk_score: 0.85,
          flags: ["WARRANT"],
          last_known_location: { lat: 33.44, lon: -112.06 },
          action: "ARREST - Active warrant",
        },
      ],
    },
    case_developments: [
      {
        case_id: "CASE-2025-1001",
        title: "Armed Robbery Investigation",
        update_type: "new_evidence",
        summary: "New surveillance footage obtained from nearby business.",
        updated_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        priority: "high",
      },
    ],
    ai_anomalies: [
      {
        id: "ANOM-3001",
        type: "activity_spike",
        description: "Unusual activity spike detected in zone micro_5_12",
        severity: "high",
        location: { lat: 33.45, lon: -112.07 },
        detected_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        confidence: 0.87,
      },
    ],
    tactical_advisories: [
      {
        priority: "critical",
        type: "zone_alert",
        title: "1 Critical Risk Zone",
        description: "Critical risk zone identified: micro_5_12.",
        action: "Deploy units to critical zones immediately",
      },
      {
        priority: "high",
        type: "vehicle_alert",
        title: "1 Stolen Vehicle Active",
        description: "Stolen vehicle ABC1234 in area.",
        action: "Stop and recover if observed.",
      },
    ],
    overnight_summary:
      "In the past 12 hours, there were 23 total incidents reported, including 3 significant incidents requiring follow-up. Activity levels were within normal range.",
    statistics: {
      zones_of_concern_count: 2,
      critical_zones: 1,
      high_risk_zones: 1,
      vehicles_of_interest_count: 1,
      stolen_vehicles: 1,
      persons_of_interest_count: 1,
      active_warrants: 1,
      critical_advisories: 1,
      high_advisories: 1,
    },
  };
}

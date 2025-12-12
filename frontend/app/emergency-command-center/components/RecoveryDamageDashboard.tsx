"use client";

import React, { useState } from "react";

interface DamageAssessment {
  assessment_id: string;
  zone: string;
  total_structures: number;
  structures_by_tier: Record<string, number>;
  total_damage_estimate: number;
  disaster_impact_index: number;
  displaced_residents: number;
  priority_repairs: string[];
}

interface InfrastructureRepair {
  repair_id: string;
  infrastructure_type: string;
  infrastructure_name: string;
  zone: string;
  estimated_cost: number;
  estimated_days: number;
  fema_category: string | null;
}

interface RecoveryPlan {
  plan_id: string;
  incident_type: string;
  affected_zones: string[];
  total_estimated_cost: number;
  federal_assistance_estimate: number;
  state_assistance_estimate: number;
  local_cost_share: number;
  insurance_claims_estimate: number;
  unmet_needs_estimate: number;
  population_affected: number;
  housing_units_damaged: number;
  businesses_affected: number;
  jobs_impacted: number;
  economic_impact_estimate: number;
  recovery_timeline_days: number;
  damage_assessments: DamageAssessment[];
  infrastructure_repairs: InfrastructureRepair[];
}

export default function RecoveryDamageDashboard() {
  const [incidentType, setIncidentType] = useState("hurricane");
  const [selectedZones, setSelectedZones] = useState<string[]>(["Zone_A", "Zone_B"]);
  const [severityFactor, setSeverityFactor] = useState(0.5);
  const [recoveryPlan, setRecoveryPlan] = useState<RecoveryPlan | null>(null);
  const [loading, setLoading] = useState(false);

  const zones = [
    "Zone_A", "Zone_B", "Zone_C", "Zone_D", "Zone_E",
    "Zone_F", "Zone_G", "Zone_H", "Zone_I", "Zone_J",
  ];

  const incidentTypes = [
    { value: "hurricane", label: "Hurricane" },
    { value: "flooding", label: "Flooding" },
    { value: "fire", label: "Fire" },
    { value: "tornado", label: "Tornado" },
  ];

  const createRecoveryPlan = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/emergency-ai/recovery-plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_type: incidentType,
          affected_zones: selectedZones,
          severity_factor: severityFactor,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setRecoveryPlan(data);
      }
    } catch (error) {
      console.error("Failed to create recovery plan:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleZone = (zone: string) => {
    setSelectedZones((prev) =>
      prev.includes(zone)
        ? prev.filter((z) => z !== zone)
        : [...prev, zone]
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getDamageTierColor = (tier: string) => {
    switch (tier) {
      case "destroyed":
        return "bg-red-500";
      case "major":
        return "bg-orange-500";
      case "moderate":
        return "bg-yellow-500";
      case "minor":
        return "bg-blue-500";
      default:
        return "bg-green-500";
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Recovery Plan Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Incident Type
              </label>
              <select
                value={incidentType}
                onChange={(e) => setIncidentType(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
              >
                {incidentTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Severity Factor: {(severityFactor * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.1"
                max="1"
                step="0.1"
                value={severityFactor}
                onChange={(e) => setSeverityFactor(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Affected Zones
              </label>
              <div className="grid grid-cols-5 gap-2">
                {zones.map((zone) => (
                  <button
                    key={zone}
                    onClick={() => toggleZone(zone)}
                    className={`px-2 py-1 rounded text-xs ${
                      selectedZones.includes(zone)
                        ? "bg-blue-600 text-white"
                        : "bg-gray-700 text-gray-400"
                    }`}
                  >
                    {zone.replace("Zone_", "")}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={createRecoveryPlan}
              disabled={loading || selectedZones.length === 0}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {loading ? "Generating Plan..." : "Generate Recovery Plan"}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Cost & Timeline Summary</h2>
          {recoveryPlan ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-400">Total Estimated Cost</p>
                <p className="text-xl font-bold text-red-400">
                  {formatCurrency(recoveryPlan.total_estimated_cost)}
                </p>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-400">Federal Assistance</p>
                <p className="text-xl font-bold text-green-400">
                  {formatCurrency(recoveryPlan.federal_assistance_estimate)}
                </p>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-400">State Assistance</p>
                <p className="text-xl font-bold text-blue-400">
                  {formatCurrency(recoveryPlan.state_assistance_estimate)}
                </p>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-400">Local Cost Share</p>
                <p className="text-xl font-bold text-yellow-400">
                  {formatCurrency(recoveryPlan.local_cost_share)}
                </p>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-400">Insurance Claims</p>
                <p className="text-xl font-bold text-purple-400">
                  {formatCurrency(recoveryPlan.insurance_claims_estimate)}
                </p>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-400">Recovery Timeline</p>
                <p className="text-xl font-bold text-orange-400">
                  {recoveryPlan.recovery_timeline_days} days
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <p className="text-4xl mb-2">📊</p>
              <p>Generate a recovery plan to see cost estimates</p>
            </div>
          )}
        </div>
      </div>

      {recoveryPlan && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Impact Summary</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Population Affected</p>
                  <p className="text-2xl font-bold">
                    {recoveryPlan.population_affected.toLocaleString()}
                  </p>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Housing Units Damaged</p>
                  <p className="text-2xl font-bold">
                    {recoveryPlan.housing_units_damaged.toLocaleString()}
                  </p>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Businesses Affected</p>
                  <p className="text-2xl font-bold">
                    {recoveryPlan.businesses_affected.toLocaleString()}
                  </p>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400">Jobs Impacted</p>
                  <p className="text-2xl font-bold">
                    {recoveryPlan.jobs_impacted.toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="mt-4 bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-400">Economic Impact Estimate</p>
                <p className="text-2xl font-bold text-red-400">
                  {formatCurrency(recoveryPlan.economic_impact_estimate)}
                </p>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Damage Assessments by Zone</h2>
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {recoveryPlan.damage_assessments.map((assessment) => (
                  <div
                    key={assessment.assessment_id}
                    className="bg-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{assessment.zone}</span>
                      <span className="text-sm text-gray-400">
                        Impact: {assessment.disaster_impact_index.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex space-x-1 mb-2">
                      {Object.entries(assessment.structures_by_tier).map(
                        ([tier, count]) => (
                          <div
                            key={tier}
                            className={`h-4 ${getDamageTierColor(tier)}`}
                            style={{
                              width: `${
                                (count / assessment.total_structures) * 100
                              }%`,
                            }}
                            title={`${tier}: ${count}`}
                          ></div>
                        )
                      )}
                    </div>
                    <p className="text-xs text-gray-400">
                      {assessment.displaced_residents} displaced |{" "}
                      {formatCurrency(assessment.total_damage_estimate)} damage
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Infrastructure Repairs</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-gray-700">
                    <th className="pb-3">Infrastructure</th>
                    <th className="pb-3">Type</th>
                    <th className="pb-3">Zone</th>
                    <th className="pb-3">FEMA Category</th>
                    <th className="pb-3">Est. Cost</th>
                    <th className="pb-3">Est. Days</th>
                  </tr>
                </thead>
                <tbody>
                  {recoveryPlan.infrastructure_repairs.map((repair) => (
                    <tr
                      key={repair.repair_id}
                      className="border-b border-gray-700"
                    >
                      <td className="py-3">{repair.infrastructure_name}</td>
                      <td className="py-3 capitalize">
                        {repair.infrastructure_type.replace("_", " ")}
                      </td>
                      <td className="py-3">{repair.zone}</td>
                      <td className="py-3">
                        {repair.fema_category?.replace("_", " ") || "N/A"}
                      </td>
                      <td className="py-3">{formatCurrency(repair.estimated_cost)}</td>
                      <td className="py-3">{repair.estimated_days}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Utility Outage Overlay</h2>
            <div className="bg-gray-700 rounded-lg h-48 flex items-center justify-center">
              <div className="text-center text-gray-400">
                <p>Real-time utility outage visualization</p>
                <p className="text-sm">Power, Water, Gas, Internet status by zone</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

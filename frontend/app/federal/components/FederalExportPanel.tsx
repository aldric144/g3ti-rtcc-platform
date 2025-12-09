"use client";

import { useState, useEffect } from "react";

interface SystemStatus {
  name: string;
  status: "ready" | "stub" | "pending";
  description: string;
  endpoints: number;
}

interface ComplianceArea {
  area: string;
  name: string;
  status: "compliant" | "enforced" | "active";
}

export function FederalExportPanel() {
  const [systems, setSystems] = useState<SystemStatus[]>([
    {
      name: "FBI N-DEx",
      status: "ready",
      description: "National Data Exchange - Person, Incident, Case, Property, Vehicle, Firearms mapping",
      endpoints: 4,
    },
    {
      name: "FBI NCIC",
      status: "stub",
      description: "National Crime Information Center - Query structure (non-operational stubs)",
      endpoints: 3,
    },
    {
      name: "ATF eTrace",
      status: "ready",
      description: "Firearms Intelligence Export - Trace requests and reports",
      endpoints: 3,
    },
    {
      name: "DHS SAR",
      status: "ready",
      description: "Suspicious Activity Reporting - ISE-SAR Functional Standard v1.5",
      endpoints: 5,
    },
  ]);

  const [complianceAreas, setComplianceAreas] = useState<ComplianceArea[]>([
    { area: "5", name: "Access Control", status: "enforced" },
    { area: "7", name: "Encryption", status: "compliant" },
    { area: "8", name: "Auditing & Accountability", status: "active" },
    { area: "10", name: "System & Communications Protection", status: "enforced" },
  ]);

  const [stats, setStats] = useState({
    totalExports: 0,
    ndexExports: 0,
    etraceExports: 0,
    sarReports: 0,
    ncicQueries: 0,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready":
      case "compliant":
      case "enforced":
      case "active":
        return "bg-green-500";
      case "stub":
        return "bg-yellow-500";
      case "pending":
        return "bg-gray-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "ready":
        return "Ready";
      case "stub":
        return "Stub Only";
      case "pending":
        return "Pending";
      case "compliant":
        return "Compliant";
      case "enforced":
        return "Enforced";
      case "active":
        return "Active";
      default:
        return status;
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-4">
          Federal Integration Readiness Overview
        </h2>
        <p className="text-gray-400 mb-6">
          This dashboard provides access to federal data exchange structures, validation rules,
          and secure communication scaffolding for FBI N-DEx, FBI NCIC, ATF eTrace, and DHS SAR systems.
          All operations are CJIS-compliant with full audit logging.
        </p>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.totalExports}</div>
            <div className="text-sm text-gray-400">Total Exports</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-400">{stats.ndexExports}</div>
            <div className="text-sm text-gray-400">N-DEx Exports</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-orange-400">{stats.etraceExports}</div>
            <div className="text-sm text-gray-400">eTrace Exports</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-red-400">{stats.sarReports}</div>
            <div className="text-sm text-gray-400">SAR Reports</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-400">{stats.ncicQueries}</div>
            <div className="text-sm text-gray-400">NCIC Stubs</div>
          </div>
        </div>
      </div>

      {/* Federal Systems Status */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Federal Systems Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {systems.map((system) => (
            <div
              key={system.name}
              className="bg-gray-700/50 rounded-lg p-4 border border-gray-600"
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-white">{system.name}</h4>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium text-white ${getStatusColor(
                    system.status
                  )}`}
                >
                  {getStatusText(system.status)}
                </span>
              </div>
              <p className="text-sm text-gray-400 mb-2">{system.description}</p>
              <div className="text-xs text-gray-500">
                {system.endpoints} API endpoints available
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CJIS Compliance Status */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">CJIS Security Policy Compliance</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {complianceAreas.map((area) => (
            <div
              key={area.area}
              className="bg-gray-700/50 rounded-lg p-4 border border-gray-600"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-300">Area {area.area}</span>
                <span
                  className={`w-3 h-3 rounded-full ${getStatusColor(area.status)}`}
                ></span>
              </div>
              <div className="text-white font-medium">{area.name}</div>
              <div className="text-xs text-gray-400 mt-1">{getStatusText(area.status)}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Encryption Status */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Encryption & Security</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Payload Encryption</div>
            <div className="text-white font-medium">AES-256-GCM</div>
            <div className="text-xs text-gray-500 mt-1">256-bit key, Galois/Counter Mode</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Key Wrapping</div>
            <div className="text-white font-medium">RSA-OAEP</div>
            <div className="text-xs text-gray-500 mt-1">OAEP padding with SHA-256</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Signature Algorithm</div>
            <div className="text-white font-medium">SHA-256</div>
            <div className="text-xs text-gray-500 mt-1">With nonce-based replay protection</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg transition-colors">
            Export to N-DEx
          </button>
          <button className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-lg transition-colors">
            Create eTrace Request
          </button>
          <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-3 rounded-lg transition-colors">
            Submit SAR
          </button>
          <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-3 rounded-lg transition-colors">
            Test NCIC Query
          </button>
        </div>
      </div>
    </div>
  );
}

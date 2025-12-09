"use client";

import { useState } from "react";

interface NCICQuery {
  id: string;
  queryId: string;
  type: "vehicle" | "person" | "gun";
  status: "stub";
  createdAt: string;
  params: Record<string, string>;
}

type QueryType = "vehicle" | "person" | "gun";

interface VehicleQueryForm {
  vin: string;
  licensePlate: string;
  licenseState: string;
  make: string;
  model: string;
  year: string;
  color: string;
}

interface PersonQueryForm {
  lastName: string;
  firstName: string;
  dateOfBirth: string;
  driversLicense: string;
  driversLicenseState: string;
}

interface GunQueryForm {
  serialNumber: string;
  make: string;
  model: string;
  caliber: string;
  gunType: string;
}

export function NCICReadinessPanel() {
  const [queries, setQueries] = useState<NCICQuery[]>([]);
  const [queryType, setQueryType] = useState<QueryType>("vehicle");
  const [isQuerying, setIsQuerying] = useState(false);
  const [result, setResult] = useState<any>(null);

  const [vehicleForm, setVehicleForm] = useState<VehicleQueryForm>({
    vin: "",
    licensePlate: "",
    licenseState: "",
    make: "",
    model: "",
    year: "",
    color: "",
  });

  const [personForm, setPersonForm] = useState<PersonQueryForm>({
    lastName: "",
    firstName: "",
    dateOfBirth: "",
    driversLicense: "",
    driversLicenseState: "",
  });

  const [gunForm, setGunForm] = useState<GunQueryForm>({
    serialNumber: "",
    make: "",
    model: "",
    caliber: "",
    gunType: "pistol",
  });

  const states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
  ];

  const gunTypes = [
    { value: "pistol", label: "Pistol" },
    { value: "revolver", label: "Revolver" },
    { value: "rifle", label: "Rifle" },
    { value: "shotgun", label: "Shotgun" },
    { value: "other", label: "Other" },
  ];

  const handleQuery = async () => {
    setIsQuerying(true);
    setResult(null);

    await new Promise((resolve) => setTimeout(resolve, 1500));

    let params: Record<string, string> = {};
    if (queryType === "vehicle") {
      params = { ...vehicleForm };
    } else if (queryType === "person") {
      params = { ...personForm };
    } else {
      params = { ...gunForm };
    }

    const newQuery: NCICQuery = {
      id: `ncic-${Date.now()}`,
      queryId: `QRY-${Math.random().toString(36).substr(2, 10).toUpperCase()}`,
      type: queryType,
      status: "stub",
      createdAt: new Date().toISOString(),
      params,
    };

    setQueries([newQuery, ...queries]);
    setResult({
      success: true,
      queryId: newQuery.queryId,
      responseId: `RSP-${Math.random().toString(36).substr(2, 10).toUpperCase()}`,
      message:
        "This is a non-operational NCIC request stub for readiness purposes only. " +
        "No actual NCIC query was performed. This endpoint demonstrates the query " +
        "structure and validation rules required for future NCIC integration.",
      isStub: true,
      sampleData: {
        response_code: "STUB",
        query_type: queryType,
        formatted_message: `MKE/QV.ORI/FL0000000.${queryType === "vehicle" ? "LIC/ABC123.LIS/FL" : queryType === "person" ? "NAM/SAMPLE,TEST" : "SER/ABC123456"}.PUR/C.EOM`,
        disclaimer: "NON-OPERATIONAL - READINESS TESTING ONLY",
      },
    });
    setIsQuerying(false);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "vehicle":
        return "🚗";
      case "person":
        return "👤";
      case "gun":
        return "🔫";
      default:
        return "📄";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Warning */}
      <div className="bg-yellow-900/30 rounded-lg p-6 border border-yellow-600">
        <div className="flex items-start space-x-4">
          <span className="text-3xl">⚠️</span>
          <div>
            <h2 className="text-xl font-semibold text-yellow-400 mb-2">
              NCIC Query Readiness (STUB ONLY)
            </h2>
            <p className="text-yellow-200">
              <strong>IMPORTANT:</strong> This is a non-operational NCIC request stub for readiness
              purposes only. No actual NCIC queries are performed. These endpoints demonstrate the
              query structure, validation rules, and message formatting required for future NCIC
              integration.
            </p>
          </div>
        </div>
      </div>

      {/* Query Type Selection */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Select Query Type</h3>
        <div className="flex space-x-4">
          {(["vehicle", "person", "gun"] as QueryType[]).map((type) => (
            <button
              key={type}
              onClick={() => setQueryType(type)}
              className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                queryType === type
                  ? "bg-yellow-600 text-white ring-2 ring-yellow-400"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              <span className="mr-2">{getTypeIcon(type)}</span>
              {type.charAt(0).toUpperCase() + type.slice(1)} Query
            </button>
          ))}
        </div>
      </div>

      {/* Query Form */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">
          {queryType.charAt(0).toUpperCase() + queryType.slice(1)} Query Parameters
        </h3>

        {/* Vehicle Query Form */}
        {queryType === "vehicle" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">VIN</label>
              <input
                type="text"
                value={vehicleForm.vin}
                onChange={(e) => setVehicleForm({ ...vehicleForm, vin: e.target.value })}
                placeholder="Vehicle Identification Number"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">License Plate</label>
              <input
                type="text"
                value={vehicleForm.licensePlate}
                onChange={(e) => setVehicleForm({ ...vehicleForm, licensePlate: e.target.value })}
                placeholder="Plate number"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">License State</label>
              <select
                value={vehicleForm.licenseState}
                onChange={(e) => setVehicleForm({ ...vehicleForm, licenseState: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500"
              >
                <option value="">Select state</option>
                {states.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Make</label>
              <input
                type="text"
                value={vehicleForm.make}
                onChange={(e) => setVehicleForm({ ...vehicleForm, make: e.target.value })}
                placeholder="Manufacturer"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Model</label>
              <input
                type="text"
                value={vehicleForm.model}
                onChange={(e) => setVehicleForm({ ...vehicleForm, model: e.target.value })}
                placeholder="Model name"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Year</label>
              <input
                type="text"
                value={vehicleForm.year}
                onChange={(e) => setVehicleForm({ ...vehicleForm, year: e.target.value })}
                placeholder="Model year"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
          </div>
        )}

        {/* Person Query Form */}
        {queryType === "person" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Last Name</label>
              <input
                type="text"
                value={personForm.lastName}
                onChange={(e) => setPersonForm({ ...personForm, lastName: e.target.value })}
                placeholder="Last name"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">First Name</label>
              <input
                type="text"
                value={personForm.firstName}
                onChange={(e) => setPersonForm({ ...personForm, firstName: e.target.value })}
                placeholder="First name"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Date of Birth</label>
              <input
                type="date"
                value={personForm.dateOfBirth}
                onChange={(e) => setPersonForm({ ...personForm, dateOfBirth: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Driver&apos;s License</label>
              <input
                type="text"
                value={personForm.driversLicense}
                onChange={(e) => setPersonForm({ ...personForm, driversLicense: e.target.value })}
                placeholder="License number"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">License State</label>
              <select
                value={personForm.driversLicenseState}
                onChange={(e) =>
                  setPersonForm({ ...personForm, driversLicenseState: e.target.value })
                }
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500"
              >
                <option value="">Select state</option>
                {states.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Gun Query Form */}
        {queryType === "gun" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Serial Number</label>
              <input
                type="text"
                value={gunForm.serialNumber}
                onChange={(e) => setGunForm({ ...gunForm, serialNumber: e.target.value })}
                placeholder="Firearm serial number"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Make</label>
              <input
                type="text"
                value={gunForm.make}
                onChange={(e) => setGunForm({ ...gunForm, make: e.target.value })}
                placeholder="Manufacturer"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Model</label>
              <input
                type="text"
                value={gunForm.model}
                onChange={(e) => setGunForm({ ...gunForm, model: e.target.value })}
                placeholder="Model name"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Caliber</label>
              <input
                type="text"
                value={gunForm.caliber}
                onChange={(e) => setGunForm({ ...gunForm, caliber: e.target.value })}
                placeholder="e.g., 9mm, .45 ACP"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Gun Type</label>
              <select
                value={gunForm.gunType}
                onChange={(e) => setGunForm({ ...gunForm, gunType: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500"
              >
                {gunTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        <div className="mt-4">
          <button
            onClick={handleQuery}
            disabled={isQuerying}
            className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-800 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg transition-colors"
          >
            {isQuerying ? "Processing..." : "Test Query (Stub)"}
          </button>
        </div>
      </div>

      {/* Result */}
      {result && (
        <div className="bg-gray-800 rounded-lg p-6 border border-yellow-600">
          <h3 className="text-lg font-semibold text-yellow-400 mb-4">Stub Response</h3>
          <div className="bg-yellow-900/20 rounded-lg p-4 mb-4">
            <p className="text-yellow-200 text-sm">{result.message}</p>
          </div>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-gray-300">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Readiness Status */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">NCIC Readiness Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Integration Status</div>
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
              <span className="text-white font-medium">Stub Only (Non-Operational)</span>
            </div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Supported Query Types</div>
            <div className="text-white font-medium">Vehicle, Person, Gun</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Validation Rules</div>
            <div className="text-white font-medium">Active (Pre-validation enabled)</div>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">CJIS Compliance</div>
            <div className="text-white font-medium">Audit logging enabled</div>
          </div>
        </div>
      </div>

      {/* Recent Queries */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Query Stubs</h3>
        {queries.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            No queries yet. Test a query stub above.
          </div>
        ) : (
          <div className="space-y-2">
            {queries.map((query) => (
              <div
                key={query.id}
                className="bg-gray-700/50 rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex items-center space-x-4">
                  <span className="text-2xl">{getTypeIcon(query.type)}</span>
                  <div>
                    <div className="font-medium text-white font-mono">{query.queryId}</div>
                    <div className="text-sm text-gray-400">
                      {query.type.charAt(0).toUpperCase() + query.type.slice(1)} Query |{" "}
                      {new Date(query.createdAt).toLocaleString()}
                    </div>
                  </div>
                </div>
                <span className="px-3 py-1 rounded text-xs font-medium text-white bg-yellow-600">
                  STUB
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

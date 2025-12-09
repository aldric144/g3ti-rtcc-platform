"use client";

import { useState } from "react";

interface ETraceRequest {
  id: string;
  traceNumber: string;
  status: "pending" | "validated" | "ready" | "submitted" | "failed";
  firearmType: string;
  serialNumber: string;
  recoveryDate: string;
  createdAt: string;
}

interface TraceForm {
  firearmType: string;
  make: string;
  model: string;
  caliber: string;
  serialNumber: string;
  recoveryDate: string;
  recoveryCity: string;
  recoveryState: string;
  crimeCode: string;
  incidentId: string;
}

export function ETraceExportViewer() {
  const [requests, setRequests] = useState<ETraceRequest[]>([]);
  const [traceForm, setTraceForm] = useState<TraceForm>({
    firearmType: "pistol",
    make: "",
    model: "",
    caliber: "",
    serialNumber: "",
    recoveryDate: "",
    recoveryCity: "",
    recoveryState: "",
    crimeCode: "",
    incidentId: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const firearmTypes = [
    { value: "pistol", label: "Pistol" },
    { value: "revolver", label: "Revolver" },
    { value: "rifle", label: "Rifle" },
    { value: "shotgun", label: "Shotgun" },
    { value: "derringer", label: "Derringer" },
    { value: "machine_gun", label: "Machine Gun" },
    { value: "submachine_gun", label: "Submachine Gun" },
    { value: "unknown", label: "Unknown" },
  ];

  const states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
  ];

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setResult(null);

    await new Promise((resolve) => setTimeout(resolve, 1500));

    const newRequest: ETraceRequest = {
      id: `etrace-${Date.now()}`,
      traceNumber: `TR-${new Date().getFullYear()}-${Math.random().toString(36).substr(2, 8).toUpperCase()}`,
      status: "ready",
      firearmType: traceForm.firearmType,
      serialNumber: traceForm.serialNumber || "***SAMPLE***",
      recoveryDate: traceForm.recoveryDate || new Date().toISOString().split("T")[0],
      createdAt: new Date().toISOString(),
    };

    setRequests([newRequest, ...requests]);
    setResult({
      success: true,
      traceNumber: newRequest.traceNumber,
      message: "eTrace request created successfully",
      data: {
        trace_id: newRequest.id,
        firearm_type: traceForm.firearmType,
        make: traceForm.make || "Sample Manufacturer",
        model: traceForm.model || "Model X",
        caliber: traceForm.caliber || "9MM",
        serial_number: "***MASKED***",
        recovery_location: `${traceForm.recoveryCity || "Sample City"}, ${traceForm.recoveryState || "FL"}`,
        status: "ready",
      },
    });
    setIsSubmitting(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready":
      case "submitted":
        return "bg-green-500";
      case "validated":
        return "bg-blue-500";
      case "pending":
        return "bg-yellow-500";
      case "failed":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-2">ATF eTrace Firearms Export</h2>
        <p className="text-gray-400">
          Generate firearm trace requests for ATF eTrace system. Includes weapon data normalization,
          recovery information, and possessor association mapping.
        </p>
      </div>

      {/* Trace Request Form */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Create Trace Request</h3>
        
        {/* Firearm Information */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Firearm Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Firearm Type</label>
              <select
                value={traceForm.firearmType}
                onChange={(e) => setTraceForm({ ...traceForm, firearmType: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
              >
                {firearmTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Make</label>
              <input
                type="text"
                value={traceForm.make}
                onChange={(e) => setTraceForm({ ...traceForm, make: e.target.value })}
                placeholder="Manufacturer"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Model</label>
              <input
                type="text"
                value={traceForm.model}
                onChange={(e) => setTraceForm({ ...traceForm, model: e.target.value })}
                placeholder="Model name"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Caliber</label>
              <input
                type="text"
                value={traceForm.caliber}
                onChange={(e) => setTraceForm({ ...traceForm, caliber: e.target.value })}
                placeholder="e.g., 9mm, .45 ACP"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Serial Number</label>
              <input
                type="text"
                value={traceForm.serialNumber}
                onChange={(e) => setTraceForm({ ...traceForm, serialNumber: e.target.value })}
                placeholder="Firearm serial number"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Crime Code (Optional)</label>
              <input
                type="text"
                value={traceForm.crimeCode}
                onChange={(e) => setTraceForm({ ...traceForm, crimeCode: e.target.value })}
                placeholder="NIBRS code"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
          </div>
        </div>

        {/* Recovery Information */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Recovery Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Recovery Date</label>
              <input
                type="date"
                value={traceForm.recoveryDate}
                onChange={(e) => setTraceForm({ ...traceForm, recoveryDate: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">City</label>
              <input
                type="text"
                value={traceForm.recoveryCity}
                onChange={(e) => setTraceForm({ ...traceForm, recoveryCity: e.target.value })}
                placeholder="Recovery city"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">State</label>
              <select
                value={traceForm.recoveryState}
                onChange={(e) => setTraceForm({ ...traceForm, recoveryState: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
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
              <label className="block text-xs text-gray-400 mb-1">Incident ID (Optional)</label>
              <input
                type="text"
                value={traceForm.incidentId}
                onChange={(e) => setTraceForm({ ...traceForm, incidentId: e.target.value })}
                placeholder="Related incident"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="bg-orange-600 hover:bg-orange-700 disabled:bg-orange-800 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg transition-colors"
        >
          {isSubmitting ? "Creating Request..." : "Create eTrace Request"}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div
          className={`bg-gray-800 rounded-lg p-6 border ${
            result.success ? "border-green-500" : "border-red-500"
          }`}
        >
          <h3 className="text-lg font-semibold text-white mb-4">
            {result.success ? "Request Created" : "Request Failed"}
          </h3>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-gray-300">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Recent Requests */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Trace Requests</h3>
        {requests.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            No trace requests yet. Create your first eTrace request above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
                  <th className="pb-3">Trace Number</th>
                  <th className="pb-3">Type</th>
                  <th className="pb-3">Serial</th>
                  <th className="pb-3">Recovery Date</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((req) => (
                  <tr key={req.id} className="border-b border-gray-700/50">
                    <td className="py-3 text-white font-mono text-sm">{req.traceNumber}</td>
                    <td className="py-3 text-gray-300 capitalize">{req.firearmType}</td>
                    <td className="py-3 text-gray-300 font-mono text-sm">{req.serialNumber}</td>
                    <td className="py-3 text-gray-300">{req.recoveryDate}</td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium text-white ${getStatusColor(
                          req.status
                        )}`}
                      >
                        {req.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";

interface NDExExport {
  id: string;
  type: "person" | "incident" | "arrest" | "case" | "vehicle" | "firearm";
  status: "pending" | "validated" | "ready" | "exported" | "failed";
  createdAt: string;
  resourceId: string;
}

interface ExportForm {
  type: "person" | "incident";
  resourceId: string;
  includeRelated: boolean;
}

export function NDExExportViewer() {
  const [exports, setExports] = useState<NDExExport[]>([]);
  const [selectedExport, setSelectedExport] = useState<NDExExport | null>(null);
  const [exportForm, setExportForm] = useState<ExportForm>({
    type: "incident",
    resourceId: "",
    includeRelated: true,
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState<any>(null);

  const handleExport = async () => {
    setIsExporting(true);
    setExportResult(null);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const newExport: NDExExport = {
      id: `ndex-${Date.now()}`,
      type: exportForm.type,
      status: "ready",
      createdAt: new Date().toISOString(),
      resourceId: exportForm.resourceId || `sample-${Date.now()}`,
    };

    setExports([newExport, ...exports]);
    setExportResult({
      success: true,
      exportId: newExport.id,
      message: `${exportForm.type} exported to N-DEx format successfully`,
      data: {
        [`${exportForm.type}_id`]: newExport.resourceId,
        status: "ready",
        schema_version: "5.0",
        federal_system: "ndex",
      },
    });
    setIsExporting(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready":
      case "exported":
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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "person":
        return "👤";
      case "incident":
        return "📋";
      case "arrest":
        return "⚖️";
      case "case":
        return "📁";
      case "vehicle":
        return "🚗";
      case "firearm":
        return "🔫";
      default:
        return "📄";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-2">N-DEx Data Exchange</h2>
        <p className="text-gray-400">
          Export records to FBI N-DEx format (v5.x schema). Supports Person, Incident, Arrest,
          Case, Property, Vehicle, and Firearms mapping with NIBRS offense code normalization.
        </p>
      </div>

      {/* Export Form */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Create N-DEx Export</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Export Type
            </label>
            <select
              value={exportForm.type}
              onChange={(e) =>
                setExportForm({ ...exportForm, type: e.target.value as "person" | "incident" })
              }
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="incident">Incident</option>
              <option value="person">Person</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Resource ID
            </label>
            <input
              type="text"
              value={exportForm.resourceId}
              onChange={(e) => setExportForm({ ...exportForm, resourceId: e.target.value })}
              placeholder="Enter ID or leave blank for sample"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-end">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={exportForm.includeRelated}
                onChange={(e) =>
                  setExportForm({ ...exportForm, includeRelated: e.target.checked })
                }
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-300">Include related entities</span>
            </label>
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg transition-colors"
          >
            {isExporting ? "Exporting..." : "Export to N-DEx"}
          </button>
        </div>
      </div>

      {/* Export Result */}
      {exportResult && (
        <div
          className={`bg-gray-800 rounded-lg p-6 border ${
            exportResult.success ? "border-green-500" : "border-red-500"
          }`}
        >
          <h3 className="text-lg font-semibold text-white mb-4">
            {exportResult.success ? "Export Successful" : "Export Failed"}
          </h3>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-gray-300">
              {JSON.stringify(exportResult, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Schema Information */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">N-DEx Schema Mapping</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { type: "Person", fields: "Name, DOB, Physical, Identifiers" },
            { type: "Incident", fields: "Date, Location, Offenses, Narrative" },
            { type: "Arrest", fields: "Date, Charges, Booking, Disposition" },
            { type: "Case", fields: "Number, Type, Status, Investigator" },
            { type: "Property", fields: "Type, Serial, Value, Status" },
            { type: "Vehicle", fields: "VIN, Plate, Make/Model, Color" },
            { type: "Firearm", fields: "Serial, Make/Model, Caliber, Type" },
            { type: "Location", fields: "Address, City, State, Coordinates" },
          ].map((schema) => (
            <div key={schema.type} className="bg-gray-700/50 rounded-lg p-3">
              <div className="font-medium text-white">{schema.type}</div>
              <div className="text-xs text-gray-400 mt-1">{schema.fields}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Exports */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Exports</h3>
        {exports.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            No exports yet. Create your first N-DEx export above.
          </div>
        ) : (
          <div className="space-y-2">
            {exports.map((exp) => (
              <div
                key={exp.id}
                className="bg-gray-700/50 rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex items-center space-x-4">
                  <span className="text-2xl">{getTypeIcon(exp.type)}</span>
                  <div>
                    <div className="font-medium text-white capitalize">{exp.type} Export</div>
                    <div className="text-sm text-gray-400">
                      ID: {exp.resourceId} | {new Date(exp.createdAt).toLocaleString()}
                    </div>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded text-xs font-medium text-white ${getStatusColor(
                    exp.status
                  )}`}
                >
                  {exp.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

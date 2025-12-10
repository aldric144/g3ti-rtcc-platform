"use client";

import { useState, useEffect } from "react";

type IntegrationStatus = "connected" | "degraded" | "disconnected" | "maintenance";

interface VendorIntegration {
  id: string;
  name: string;
  category: string;
  status: IntegrationStatus;
  endpoint: string;
  lastSync: string;
  latencyMs: number;
  requestsPerMinute: number;
  errorRate: number;
  uptime24h: number;
}

const mockVendors: VendorIntegration[] = [
  {
    id: "ndex",
    name: "N-DEx",
    category: "Federal",
    status: "connected",
    endpoint: "ndex-api.fbi.gov",
    lastSync: new Date(Date.now() - 30000).toISOString(),
    latencyMs: 145,
    requestsPerMinute: 12,
    errorRate: 0.1,
    uptime24h: 99.8,
  },
  {
    id: "ncic",
    name: "NCIC",
    category: "Federal",
    status: "connected",
    endpoint: "ncic.cjis.gov",
    lastSync: new Date(Date.now() - 15000).toISOString(),
    latencyMs: 132,
    requestsPerMinute: 45,
    errorRate: 0.05,
    uptime24h: 99.95,
  },
  {
    id: "etrace",
    name: "eTrace",
    category: "Federal",
    status: "degraded",
    endpoint: "etrace.atf.gov",
    lastSync: new Date(Date.now() - 120000).toISOString(),
    latencyMs: 890,
    requestsPerMinute: 3,
    errorRate: 2.5,
    uptime24h: 97.2,
  },
  {
    id: "dhs-sar",
    name: "DHS-SAR",
    category: "Federal",
    status: "connected",
    endpoint: "sar.dhs.gov",
    lastSync: new Date(Date.now() - 60000).toISOString(),
    latencyMs: 156,
    requestsPerMinute: 8,
    errorRate: 0.2,
    uptime24h: 99.5,
  },
  {
    id: "lpr-vendor",
    name: "LPR Network",
    category: "Vendor",
    status: "connected",
    endpoint: "api.lprnetwork.com",
    lastSync: new Date(Date.now() - 5000).toISOString(),
    latencyMs: 45,
    requestsPerMinute: 120,
    errorRate: 0.01,
    uptime24h: 99.99,
  },
  {
    id: "shotspotter",
    name: "ShotSpotter",
    category: "Vendor",
    status: "connected",
    endpoint: "api.shotspotter.com",
    lastSync: new Date(Date.now() - 10000).toISOString(),
    latencyMs: 38,
    requestsPerMinute: 5,
    errorRate: 0.0,
    uptime24h: 100.0,
  },
  {
    id: "cad-system",
    name: "CAD System",
    category: "Internal",
    status: "connected",
    endpoint: "cad.internal.rtcc",
    lastSync: new Date(Date.now() - 2000).toISOString(),
    latencyMs: 12,
    requestsPerMinute: 200,
    errorRate: 0.0,
    uptime24h: 99.99,
  },
  {
    id: "rms-system",
    name: "RMS System",
    category: "Internal",
    status: "maintenance",
    endpoint: "rms.internal.rtcc",
    lastSync: new Date(Date.now() - 3600000).toISOString(),
    latencyMs: 0,
    requestsPerMinute: 0,
    errorRate: 0,
    uptime24h: 95.0,
  },
];

const statusColors: Record<IntegrationStatus, string> = {
  connected: "bg-green-500",
  degraded: "bg-yellow-500",
  disconnected: "bg-red-500",
  maintenance: "bg-gray-500",
};

const statusBgColors: Record<IntegrationStatus, string> = {
  connected: "bg-green-500/10 border-green-500/30",
  degraded: "bg-yellow-500/10 border-yellow-500/30",
  disconnected: "bg-red-500/10 border-red-500/30",
  maintenance: "bg-gray-500/10 border-gray-500/30",
};

export default function VendorIntegrationMap() {
  const [vendors, setVendors] = useState<VendorIntegration[]>(mockVendors);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedVendor, setSelectedVendor] = useState<string | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setVendors((prev) =>
        prev.map((vendor) => ({
          ...vendor,
          latencyMs:
            vendor.status === "maintenance"
              ? 0
              : Math.max(10, vendor.latencyMs + (Math.random() - 0.5) * 20),
          lastSync:
            vendor.status === "maintenance"
              ? vendor.lastSync
              : new Date().toISOString(),
        }))
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const categories = ["all", ...new Set(vendors.map((v) => v.category))];

  const filteredVendors =
    selectedCategory === "all"
      ? vendors
      : vendors.filter((v) => v.category === selectedCategory);

  const statusCounts = vendors.reduce(
    (acc, vendor) => {
      acc[vendor.status] = (acc[vendor.status] || 0) + 1;
      return acc;
    },
    {} as Record<IntegrationStatus, number>
  );

  const formatLastSync = (isoString: string) => {
    const diff = Date.now() - new Date(isoString).getTime();
    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  const selectedVendorData = vendors.find((v) => v.id === selectedVendor);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Vendor Integration Map</h2>
        <div className="flex items-center gap-4">
          {(
            ["connected", "degraded", "disconnected", "maintenance"] as IntegrationStatus[]
          ).map((status) => (
            <div key={status} className="flex items-center gap-1">
              <div className={`w-3 h-3 rounded-full ${statusColors[status]}`} />
              <span className="text-sm text-gray-400 capitalize">
                {statusCounts[status] || 0}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCategory === category
                ? "bg-blue-600 text-white"
                : "bg-gray-700 text-gray-400 hover:bg-gray-600"
            }`}
          >
            {category === "all" ? "All" : category}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredVendors.map((vendor) => (
              <div
                key={vendor.id}
                onClick={() => setSelectedVendor(vendor.id)}
                className={`rounded-lg border p-4 cursor-pointer transition-all ${
                  selectedVendor === vendor.id
                    ? "ring-2 ring-blue-500"
                    : ""
                } ${statusBgColors[vendor.status]}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-medium">{vendor.name}</div>
                    <div className="text-xs text-gray-400">{vendor.category}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-3 h-3 rounded-full ${statusColors[vendor.status]} ${
                        vendor.status === "connected" ? "animate-pulse" : ""
                      }`}
                    />
                    <span className="text-xs text-gray-400 capitalize">
                      {vendor.status}
                    </span>
                  </div>
                </div>

                <div className="text-xs text-gray-500 mb-3 font-mono">
                  {vendor.endpoint}
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <div className="text-gray-400 text-xs">Latency</div>
                    <div
                      className={
                        vendor.latencyMs > 500
                          ? "text-yellow-400"
                          : vendor.latencyMs > 1000
                          ? "text-red-400"
                          : "text-white"
                      }
                    >
                      {vendor.latencyMs > 0 ? `${vendor.latencyMs.toFixed(0)}ms` : "N/A"}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-xs">Last Sync</div>
                    <div className="text-white">
                      {formatLastSync(vendor.lastSync)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-1">
          {selectedVendorData ? (
            <div className="bg-gray-700/30 rounded-lg border border-gray-600 p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">{selectedVendorData.name}</h3>
                <div
                  className={`px-2 py-1 rounded text-xs ${statusBgColors[selectedVendorData.status]} border`}
                >
                  {selectedVendorData.status}
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Endpoint</div>
                  <div className="text-sm font-mono bg-gray-800 rounded px-2 py-1">
                    {selectedVendorData.endpoint}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-400">Category</div>
                    <div className="font-medium">{selectedVendorData.category}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Latency</div>
                    <div className="font-medium">
                      {selectedVendorData.latencyMs > 0
                        ? `${selectedVendorData.latencyMs.toFixed(0)}ms`
                        : "N/A"}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Requests/min</div>
                    <div className="font-medium">
                      {selectedVendorData.requestsPerMinute}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Error Rate</div>
                    <div
                      className={`font-medium ${
                        selectedVendorData.errorRate > 1
                          ? "text-red-400"
                          : selectedVendorData.errorRate > 0.5
                          ? "text-yellow-400"
                          : "text-green-400"
                      }`}
                    >
                      {selectedVendorData.errorRate.toFixed(2)}%
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400 mb-2">Uptime (24h)</div>
                  <div className="relative h-4 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className={`absolute left-0 top-0 h-full rounded-full ${
                        selectedVendorData.uptime24h >= 99.9
                          ? "bg-green-500"
                          : selectedVendorData.uptime24h >= 99
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${selectedVendorData.uptime24h}%` }}
                    />
                  </div>
                  <div className="text-right text-sm mt-1">
                    {selectedVendorData.uptime24h.toFixed(2)}%
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400">Last Sync</div>
                  <div className="font-medium">
                    {new Date(selectedVendorData.lastSync).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-700/30 rounded-lg border border-gray-600 p-8 text-center text-gray-400">
              Select a vendor to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

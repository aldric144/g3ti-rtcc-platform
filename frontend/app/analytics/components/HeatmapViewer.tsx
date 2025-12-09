"use client";

import { useState } from "react";

interface HeatmapCell {
  h3_index: string;
  latitude: number;
  longitude: number;
  count: number;
  intensity: number;
}

interface HeatmapData {
  jurisdiction: string;
  period_label: string;
  cells: HeatmapCell[];
  total_incidents: number;
  hotspot_count: number;
  bounds: {
    min_lat: number;
    max_lat: number;
    min_lon: number;
    max_lon: number;
  };
}

interface HotspotEvolution {
  h3_index: string;
  trend: string;
  percent_change: number;
  is_persistent: boolean;
  counts: number[];
  periods: string[];
}

export function HeatmapViewer() {
  const [jurisdiction, setJurisdiction] = useState("ATL");
  const [years, setYears] = useState("2022,2023,2024");
  const [resolution, setResolution] = useState(8);
  const [crimeCategory, setCrimeCategory] = useState("");
  const [viewMode, setViewMode] = useState<"single" | "compare" | "evolution">(
    "single"
  );
  const [loading, setLoading] = useState(false);
  const [heatmapData, setHeatmapData] = useState<Record<
    number,
    HeatmapData
  > | null>(null);
  const [evolutionData, setEvolutionData] = useState<HotspotEvolution[] | null>(
    null
  );
  const [selectedYear, setSelectedYear] = useState<number | null>(null);

  const generateHeatmaps = async () => {
    setLoading(true);
    try {
      const yearList = years.split(",").map((y) => parseInt(y.trim()));

      if (viewMode === "evolution") {
        const params = new URLSearchParams({
          jurisdiction,
          years,
          resolution: resolution.toString(),
        });
        const response = await fetch(
          `/api/data-lake/heatmaps/evolution?${params}`
        );
        const data = await response.json();
        setEvolutionData(data.hotspots || []);
      } else {
        const params = new URLSearchParams({
          jurisdiction,
          years,
          resolution: resolution.toString(),
          ...(crimeCategory && { crime_category: crimeCategory }),
        });
        const response = await fetch(
          `/api/data-lake/heatmaps/yearly?${params}`
        );
        const data = await response.json();
        setHeatmapData(data.heatmaps || {});
        if (yearList.length > 0) {
          setSelectedYear(yearList[0]);
        }
      }
    } catch (error) {
      console.error("Failed to generate heatmaps:", error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendBadge = (trend: string) => {
    const badges: Record<string, { color: string; label: string }> = {
      emerging: { color: "bg-red-500", label: "Emerging" },
      stable: { color: "bg-yellow-500", label: "Stable" },
      declining: { color: "bg-green-500", label: "Declining" },
      new: { color: "bg-purple-500", label: "New" },
      disappeared: { color: "bg-gray-500", label: "Disappeared" },
    };
    const badge = badges[trend] || badges.stable;
    return (
      <span
        className={`${badge.color} text-white text-xs px-2 py-1 rounded-full`}
      >
        {badge.label}
      </span>
    );
  };

  const yearList = years
    .split(",")
    .map((y) => parseInt(y.trim()))
    .filter((y) => !isNaN(y));

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">
          Multi-Year Heatmap Configuration
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Jurisdiction
            </label>
            <select
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value="ATL">Atlanta</option>
              <option value="NYC">New York</option>
              <option value="LAX">Los Angeles</option>
              <option value="CHI">Chicago</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Years (comma-separated)
            </label>
            <input
              type="text"
              value={years}
              onChange={(e) => setYears(e.target.value)}
              placeholder="2022,2023,2024"
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              H3 Resolution
            </label>
            <select
              value={resolution}
              onChange={(e) => setResolution(parseInt(e.target.value))}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value={7}>7 - City (~5km)</option>
              <option value={8}>8 - Neighborhood (~1km)</option>
              <option value={9}>9 - Block (~200m)</option>
              <option value={10}>10 - Street (~50m)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Crime Category
            </label>
            <select
              value={crimeCategory}
              onChange={(e) => setCrimeCategory(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value="">All Categories</option>
              <option value="violent">Violent</option>
              <option value="property">Property</option>
              <option value="drug">Drug</option>
              <option value="disorder">Disorder</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">View Mode</label>
            <select
              value={viewMode}
              onChange={(e) =>
                setViewMode(e.target.value as "single" | "compare" | "evolution")
              }
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value="single">Single Year</option>
              <option value="compare">Year Comparison</option>
              <option value="evolution">Hotspot Evolution</option>
            </select>
          </div>
        </div>

        <button
          onClick={generateHeatmaps}
          disabled={loading}
          className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Heatmaps"}
        </button>
      </div>

      {viewMode !== "evolution" && heatmapData && (
        <>
          <div className="flex space-x-2 mb-4">
            {yearList.map((year) => (
              <button
                key={year}
                onClick={() => setSelectedYear(year)}
                className={`px-4 py-2 rounded ${
                  selectedYear === year
                    ? "bg-blue-600 text-white"
                    : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {year}
              </button>
            ))}
          </div>

          {selectedYear && heatmapData[selectedYear] && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">
                  Heatmap - {selectedYear}
                </h3>
                <div className="aspect-video bg-gray-900 rounded-lg flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <div className="text-4xl mb-2">🗺️</div>
                    <p>Map visualization would render here</p>
                    <p className="text-sm">
                      {heatmapData[selectedYear].cells.length} cells loaded
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Statistics</h3>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm text-gray-400">Total Incidents</div>
                    <div className="text-2xl font-bold text-blue-400">
                      {heatmapData[selectedYear].total_incidents.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Hotspot Count</div>
                    <div className="text-2xl font-bold text-red-400">
                      {heatmapData[selectedYear].hotspot_count}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Cell Count</div>
                    <div className="text-2xl font-bold text-white">
                      {heatmapData[selectedYear].cells.length}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">Resolution</div>
                    <div className="text-xl font-semibold text-gray-300">
                      H3 Level {resolution}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {viewMode === "evolution" && evolutionData && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Hotspot Evolution</h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-700 rounded p-4">
              <div className="text-sm text-gray-400">Total Hotspots</div>
              <div className="text-2xl font-bold">{evolutionData.length}</div>
            </div>
            <div className="bg-gray-700 rounded p-4">
              <div className="text-sm text-gray-400">Persistent</div>
              <div className="text-2xl font-bold text-yellow-400">
                {evolutionData.filter((h) => h.is_persistent).length}
              </div>
            </div>
            <div className="bg-gray-700 rounded p-4">
              <div className="text-sm text-gray-400">Emerging</div>
              <div className="text-2xl font-bold text-red-400">
                {evolutionData.filter((h) => h.trend === "emerging").length}
              </div>
            </div>
            <div className="bg-gray-700 rounded p-4">
              <div className="text-sm text-gray-400">Declining</div>
              <div className="text-2xl font-bold text-green-400">
                {evolutionData.filter((h) => h.trend === "declining").length}
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-gray-700">
                  <th className="pb-3">H3 Index</th>
                  <th className="pb-3">Trend</th>
                  <th className="pb-3">Change</th>
                  <th className="pb-3">Persistent</th>
                  {yearList.map((year) => (
                    <th key={year} className="pb-3">
                      {year}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {evolutionData.slice(0, 20).map((hotspot) => (
                  <tr
                    key={hotspot.h3_index}
                    className="border-b border-gray-700"
                  >
                    <td className="py-3 font-mono text-sm">
                      {hotspot.h3_index}
                    </td>
                    <td className="py-3">{getTrendBadge(hotspot.trend)}</td>
                    <td
                      className={`py-3 ${hotspot.percent_change > 0 ? "text-red-400" : "text-green-400"}`}
                    >
                      {hotspot.percent_change > 0 ? "+" : ""}
                      {hotspot.percent_change.toFixed(1)}%
                    </td>
                    <td className="py-3">
                      {hotspot.is_persistent ? (
                        <span className="text-yellow-400">Yes</span>
                      ) : (
                        <span className="text-gray-500">No</span>
                      )}
                    </td>
                    {hotspot.counts.map((count, idx) => (
                      <td key={idx} className="py-3">
                        {count}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!heatmapData && !evolutionData && !loading && (
        <div className="bg-gray-800 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">🗺️</div>
          <h3 className="text-xl font-semibold mb-2">No Heatmap Data</h3>
          <p className="text-gray-400">
            Configure your parameters and click &quot;Generate Heatmaps&quot; to
            view multi-year crime heatmaps.
          </p>
        </div>
      )}
    </div>
  );
}

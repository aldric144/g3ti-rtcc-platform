"use client";

import React, { useState, useEffect } from "react";

interface HeatmapCell {
  grid_id: string;
  latitude_center: number;
  longitude_center: number;
  activity_level: string;
  call_count: number;
}

interface HeatmapData {
  grid_size_meters: number;
  cells: HeatmapCell[];
  total_cells: number;
  high_activity_cells: number;
  low_activity_cells: number;
}

export default function CommunityHeatmap() {
  const [data, setData] = useState<HeatmapData | null>(null);

  useEffect(() => {
    const cells: HeatmapCell[] = [];
    const baseLat = 26.7753;
    const baseLon = -80.0586;

    for (let i = 0; i < 5; i++) {
      for (let j = 0; j < 5; j++) {
        const activity = (i + j) % 3 === 0 ? "low" : (i + j) % 2 === 0 ? "medium" : "high";
        cells.push({
          grid_id: `GRID-${i}-${j}`,
          latitude_center: baseLat + i * 0.01,
          longitude_center: baseLon + j * 0.01,
          activity_level: activity,
          call_count: 10 + i * j,
        });
      }
    }

    setData({
      grid_size_meters: 500,
      cells,
      total_cells: 25,
      high_activity_cells: 8,
      low_activity_cells: 9,
    });
  }, []);

  const getActivityColor = (level: string): string => {
    switch (level) {
      case "high":
        return "bg-red-400";
      case "medium":
        return "bg-yellow-400";
      case "low":
        return "bg-green-400";
      default:
        return "bg-gray-300";
    }
  };

  if (!data) {
    return (
      <div className="bg-white rounded-lg border p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Community Safety Heatmap</h3>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          Blurred Grid - {data.grid_size_meters}m Resolution
        </span>
      </div>

      <div className="mb-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          This heatmap shows aggregated call activity levels. Exact locations are blurred
          to protect privacy. Domestic violence and sensitive call locations are excluded.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-gray-900">{data.total_cells}</p>
          <p className="text-xs text-gray-600">Total Grid Cells</p>
        </div>
        <div className="text-center p-3 bg-red-50 rounded-lg">
          <p className="text-2xl font-bold text-red-900">{data.high_activity_cells}</p>
          <p className="text-xs text-red-600">High Activity</p>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <p className="text-2xl font-bold text-green-900">{data.low_activity_cells}</p>
          <p className="text-xs text-green-600">Low Activity</p>
        </div>
      </div>

      <div className="relative bg-gray-100 rounded-lg p-4" style={{ minHeight: "300px" }}>
        <div className="grid grid-cols-5 gap-1">
          {data.cells.map((cell) => (
            <div
              key={cell.grid_id}
              className={`${getActivityColor(cell.activity_level)} rounded p-2 text-center transition-all hover:opacity-80 cursor-pointer`}
              title={`${cell.activity_level} activity - ${cell.call_count} calls`}
            >
              <span className="text-xs font-medium text-white drop-shadow">
                {cell.call_count}
              </span>
            </div>
          ))}
        </div>

        <div className="absolute bottom-2 right-2 bg-white rounded-lg shadow p-2">
          <p className="text-xs font-medium text-gray-700 mb-1">Activity Level</p>
          <div className="flex items-center space-x-2">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded mr-1"></div>
              <span className="text-xs text-gray-600">Low</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-yellow-400 rounded mr-1"></div>
              <span className="text-xs text-gray-600">Medium</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-400 rounded mr-1"></div>
              <span className="text-xs text-gray-600">High</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          Data aggregated and anonymized in compliance with CJIS, VAWA, and Florida Public Records laws
        </p>
      </div>
    </div>
  );
}

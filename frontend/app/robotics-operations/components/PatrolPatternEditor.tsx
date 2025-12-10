"use client";

import React, { useState, useEffect } from "react";

interface PatrolWaypoint {
  waypoint_id: string;
  sequence: number;
  position: { x: number; y: number };
  dwell_time: number;
  actions: string[];
}

interface PatrolPattern {
  pattern_id: string;
  name: string;
  pattern_type: string;
  waypoints: PatrolWaypoint[];
  total_distance: number;
  estimated_duration_minutes: number;
  created_at: string;
  created_by: string;
  is_active: boolean;
}

const PATTERN_TYPES = [
  { value: "s_pattern", label: "S-Pattern", icon: "〰️", description: "Serpentine coverage pattern" },
  { value: "grid", label: "Grid", icon: "⊞", description: "Systematic grid coverage" },
  { value: "perimeter_loop", label: "Perimeter Loop", icon: "⭕", description: "Boundary patrol" },
  { value: "spiral", label: "Spiral", icon: "🌀", description: "Inward/outward spiral" },
  { value: "coverage", label: "Coverage", icon: "▦", description: "Full area coverage" },
];

export default function PatrolPatternEditor() {
  const [patterns, setPatterns] = useState<PatrolPattern[]>([]);
  const [selectedPattern, setSelectedPattern] = useState<PatrolPattern | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const [newPattern, setNewPattern] = useState({
    name: "",
    pattern_type: "perimeter_loop",
    area_bounds: { min_x: 0, min_y: 0, max_x: 200, max_y: 200 },
    spacing: 10,
  });

  useEffect(() => {
    const mockPatterns: PatrolPattern[] = [
      {
        pattern_id: "patrol-001",
        name: "North Perimeter Patrol",
        pattern_type: "perimeter_loop",
        waypoints: [
          { waypoint_id: "wp-1", sequence: 0, position: { x: 0, y: 180 }, dwell_time: 0, actions: [] },
          { waypoint_id: "wp-2", sequence: 1, position: { x: 50, y: 180 }, dwell_time: 10, actions: ["scan"] },
          { waypoint_id: "wp-3", sequence: 2, position: { x: 100, y: 180 }, dwell_time: 10, actions: ["scan"] },
          { waypoint_id: "wp-4", sequence: 3, position: { x: 150, y: 180 }, dwell_time: 10, actions: ["scan"] },
          { waypoint_id: "wp-5", sequence: 4, position: { x: 200, y: 180 }, dwell_time: 0, actions: [] },
        ],
        total_distance: 200,
        estimated_duration_minutes: 15,
        created_at: new Date(Date.now() - 86400000).toISOString(),
        created_by: "admin",
        is_active: true,
      },
      {
        pattern_id: "patrol-002",
        name: "Parking Lot Grid",
        pattern_type: "grid",
        waypoints: [
          { waypoint_id: "wp-6", sequence: 0, position: { x: 10, y: 10 }, dwell_time: 0, actions: [] },
          { waypoint_id: "wp-7", sequence: 1, position: { x: 10, y: 50 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-8", sequence: 2, position: { x: 10, y: 90 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-9", sequence: 3, position: { x: 50, y: 90 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-10", sequence: 4, position: { x: 50, y: 50 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-11", sequence: 5, position: { x: 50, y: 10 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-12", sequence: 6, position: { x: 90, y: 10 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-13", sequence: 7, position: { x: 90, y: 50 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-14", sequence: 8, position: { x: 90, y: 90 }, dwell_time: 0, actions: [] },
        ],
        total_distance: 320,
        estimated_duration_minutes: 25,
        created_at: new Date(Date.now() - 172800000).toISOString(),
        created_by: "admin",
        is_active: true,
      },
      {
        pattern_id: "patrol-003",
        name: "Building A Spiral",
        pattern_type: "spiral",
        waypoints: [
          { waypoint_id: "wp-15", sequence: 0, position: { x: 50, y: 50 }, dwell_time: 0, actions: [] },
          { waypoint_id: "wp-16", sequence: 1, position: { x: 60, y: 50 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-17", sequence: 2, position: { x: 60, y: 60 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-18", sequence: 3, position: { x: 40, y: 60 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-19", sequence: 4, position: { x: 40, y: 40 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-20", sequence: 5, position: { x: 70, y: 40 }, dwell_time: 5, actions: ["scan"] },
          { waypoint_id: "wp-21", sequence: 6, position: { x: 70, y: 70 }, dwell_time: 0, actions: [] },
        ],
        total_distance: 140,
        estimated_duration_minutes: 12,
        created_at: new Date(Date.now() - 259200000).toISOString(),
        created_by: "operator1",
        is_active: false,
      },
    ];

    setPatterns(mockPatterns);
    setIsLoading(false);
  }, []);

  const getPatternIcon = (type: string) => {
    const pattern = PATTERN_TYPES.find((p) => p.value === type);
    return pattern?.icon || "📍";
  };

  const handleCreatePattern = () => {
    const waypoints: PatrolWaypoint[] = [];
    const { min_x, min_y, max_x, max_y } = newPattern.area_bounds;

    if (newPattern.pattern_type === "perimeter_loop") {
      waypoints.push(
        { waypoint_id: `wp-${Date.now()}-1`, sequence: 0, position: { x: min_x, y: min_y }, dwell_time: 0, actions: [] },
        { waypoint_id: `wp-${Date.now()}-2`, sequence: 1, position: { x: max_x, y: min_y }, dwell_time: 10, actions: ["scan"] },
        { waypoint_id: `wp-${Date.now()}-3`, sequence: 2, position: { x: max_x, y: max_y }, dwell_time: 10, actions: ["scan"] },
        { waypoint_id: `wp-${Date.now()}-4`, sequence: 3, position: { x: min_x, y: max_y }, dwell_time: 10, actions: ["scan"] },
        { waypoint_id: `wp-${Date.now()}-5`, sequence: 4, position: { x: min_x, y: min_y }, dwell_time: 0, actions: [] }
      );
    }

    const pattern: PatrolPattern = {
      pattern_id: `patrol-${Date.now()}`,
      name: newPattern.name,
      pattern_type: newPattern.pattern_type,
      waypoints,
      total_distance: 0,
      estimated_duration_minutes: 0,
      created_at: new Date().toISOString(),
      created_by: "user",
      is_active: true,
    };

    setPatterns([pattern, ...patterns]);
    setIsCreating(false);
    setNewPattern({
      name: "",
      pattern_type: "perimeter_loop",
      area_bounds: { min_x: 0, min_y: 0, max_x: 200, max_y: 200 },
      spacing: 10,
    });
  };

  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white">Patrol Pattern Editor</h2>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1 rounded text-sm"
        >
          + New Pattern
        </button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-3">
          <h3 className="text-gray-400 text-sm font-medium">Saved Patterns</h3>
          {patterns.map((pattern) => (
            <div
              key={pattern.pattern_id}
              className={`bg-gray-700 rounded-lg p-4 cursor-pointer transition-all ${
                selectedPattern?.pattern_id === pattern.pattern_id ? "ring-2 ring-blue-500" : "hover:bg-gray-650"
              }`}
              onClick={() => setSelectedPattern(pattern)}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{getPatternIcon(pattern.pattern_type)}</span>
                  <div>
                    <div className="text-white font-medium">{pattern.name}</div>
                    <div className="text-gray-400 text-sm capitalize">
                      {pattern.pattern_type.replace("_", " ")}
                    </div>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs ${pattern.is_active ? "bg-green-500 text-white" : "bg-gray-600 text-gray-300"}`}>
                  {pattern.is_active ? "Active" : "Inactive"}
                </div>
              </div>
              <div className="flex justify-between text-sm text-gray-400">
                <span>{pattern.waypoints.length} waypoints</span>
                <span>{pattern.total_distance}m</span>
                <span>~{pattern.estimated_duration_minutes} min</span>
              </div>
            </div>
          ))}
        </div>

        <div>
          {selectedPattern ? (
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-medium mb-4">{selectedPattern.name}</h3>

              <div className="bg-gray-900 rounded-lg p-4 mb-4 relative" style={{ height: "250px" }}>
                <div className="absolute inset-4 border border-gray-700 rounded">
                  {selectedPattern.waypoints.map((wp, index) => (
                    <React.Fragment key={wp.waypoint_id}>
                      <div
                        className="absolute w-4 h-4 bg-blue-500 rounded-full transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center text-xs text-white"
                        style={{
                          left: `${(wp.position.x / 200) * 100}%`,
                          top: `${((200 - wp.position.y) / 200) * 100}%`,
                        }}
                        title={`Waypoint ${index + 1}`}
                      >
                        {index + 1}
                      </div>
                      {index < selectedPattern.waypoints.length - 1 && (
                        <svg
                          className="absolute inset-0 w-full h-full pointer-events-none"
                          style={{ overflow: "visible" }}
                        >
                          <line
                            x1={`${(wp.position.x / 200) * 100}%`}
                            y1={`${((200 - wp.position.y) / 200) * 100}%`}
                            x2={`${(selectedPattern.waypoints[index + 1].position.x / 200) * 100}%`}
                            y2={`${((200 - selectedPattern.waypoints[index + 1].position.y) / 200) * 100}%`}
                            stroke="#3B82F6"
                            strokeWidth="2"
                            strokeDasharray="4"
                          />
                        </svg>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-gray-400 text-sm mb-2">Waypoints</h4>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {selectedPattern.waypoints.map((wp, index) => (
                    <div key={wp.waypoint_id} className="bg-gray-800 rounded p-2 flex justify-between items-center text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-blue-400 font-medium">{index + 1}</span>
                        <span className="text-white">
                          ({wp.position.x}, {wp.position.y})
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-400">
                        {wp.dwell_time > 0 && <span>{wp.dwell_time}s</span>}
                        {wp.actions.length > 0 && (
                          <span className="text-xs bg-gray-700 px-2 py-0.5 rounded">
                            {wp.actions.join(", ")}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                <div>
                  <span className="text-gray-400">Total Distance:</span>
                  <div className="text-white">{selectedPattern.total_distance}m</div>
                </div>
                <div>
                  <span className="text-gray-400">Est. Duration:</span>
                  <div className="text-white">{selectedPattern.estimated_duration_minutes} min</div>
                </div>
                <div>
                  <span className="text-gray-400">Created:</span>
                  <div className="text-white">
                    {new Date(selectedPattern.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400">Created By:</span>
                  <div className="text-white">{selectedPattern.created_by}</div>
                </div>
              </div>

              <div className="flex gap-2">
                <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm flex-1">
                  Assign to Robot
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm flex-1">
                  Edit Pattern
                </button>
                <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm">
                  Delete
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-gray-700 rounded-lg p-8 text-center h-full flex items-center justify-center">
              <div>
                <div className="text-4xl mb-4">🗺️</div>
                <div className="text-gray-400">Select a pattern to view and edit</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {isCreating && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-[500px]">
            <h3 className="text-white font-medium mb-4">Create New Patrol Pattern</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-gray-400 text-sm block mb-1">Pattern Name</label>
                <input
                  type="text"
                  value={newPattern.name}
                  onChange={(e) => setNewPattern({ ...newPattern, name: e.target.value })}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                  placeholder="Enter pattern name"
                />
              </div>

              <div>
                <label className="text-gray-400 text-sm block mb-2">Pattern Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {PATTERN_TYPES.map((type) => (
                    <button
                      key={type.value}
                      onClick={() => setNewPattern({ ...newPattern, pattern_type: type.value })}
                      className={`p-3 rounded text-center transition-all ${
                        newPattern.pattern_type === type.value
                          ? "bg-blue-600 text-white"
                          : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                      }`}
                    >
                      <div className="text-xl mb-1">{type.icon}</div>
                      <div className="text-xs">{type.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-gray-400 text-sm block mb-1">Area Bounds</label>
                <div className="grid grid-cols-4 gap-2">
                  <div>
                    <label className="text-gray-500 text-xs">Min X</label>
                    <input
                      type="number"
                      value={newPattern.area_bounds.min_x}
                      onChange={(e) =>
                        setNewPattern({
                          ...newPattern,
                          area_bounds: { ...newPattern.area_bounds, min_x: parseInt(e.target.value) },
                        })
                      }
                      className="w-full bg-gray-700 text-white rounded px-2 py-1 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-gray-500 text-xs">Min Y</label>
                    <input
                      type="number"
                      value={newPattern.area_bounds.min_y}
                      onChange={(e) =>
                        setNewPattern({
                          ...newPattern,
                          area_bounds: { ...newPattern.area_bounds, min_y: parseInt(e.target.value) },
                        })
                      }
                      className="w-full bg-gray-700 text-white rounded px-2 py-1 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-gray-500 text-xs">Max X</label>
                    <input
                      type="number"
                      value={newPattern.area_bounds.max_x}
                      onChange={(e) =>
                        setNewPattern({
                          ...newPattern,
                          area_bounds: { ...newPattern.area_bounds, max_x: parseInt(e.target.value) },
                        })
                      }
                      className="w-full bg-gray-700 text-white rounded px-2 py-1 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-gray-500 text-xs">Max Y</label>
                    <input
                      type="number"
                      value={newPattern.area_bounds.max_y}
                      onChange={(e) =>
                        setNewPattern({
                          ...newPattern,
                          area_bounds: { ...newPattern.area_bounds, max_y: parseInt(e.target.value) },
                        })
                      }
                      className="w-full bg-gray-700 text-white rounded px-2 py-1 text-sm"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="text-gray-400 text-sm block mb-1">Spacing (meters)</label>
                <input
                  type="number"
                  value={newPattern.spacing}
                  onChange={(e) => setNewPattern({ ...newPattern, spacing: parseInt(e.target.value) })}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={handleCreatePattern}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm flex-1"
              >
                Generate Pattern
              </button>
              <button
                onClick={() => setIsCreating(false)}
                className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded text-sm flex-1"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

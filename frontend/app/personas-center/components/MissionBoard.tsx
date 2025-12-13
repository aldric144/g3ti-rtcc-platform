"use client";

import React, { useState } from "react";

interface Mission {
  mission_id: string;
  title: string;
  description: string;
  mission_type: string;
  status: string;
  priority: string;
  created_by: string;
  assigned_personas: string[];
  tasks: Array<{
    task_id: string;
    task_type: string;
    description: string;
    status: string;
    sequence_number: number;
  }>;
  progress: {
    completion_percentage: number;
    total_tasks: number;
    completed: number;
    in_progress: number;
    failed: number;
  };
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

interface MissionBoardProps {
  missions: Mission[];
  selectedMission: Mission | null;
  onMissionSelect: (mission: Mission) => void;
  onRefresh: () => void;
}

const getPriorityColor = (priority: string): string => {
  const colors: Record<string, string> = {
    critical: "bg-red-600 text-red-100",
    high: "bg-orange-600 text-orange-100",
    medium: "bg-yellow-600 text-yellow-100",
    low: "bg-green-600 text-green-100",
    routine: "bg-gray-600 text-gray-100",
  };
  return colors[priority] || "bg-gray-600 text-gray-100";
};

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    draft: "bg-gray-500",
    pending_approval: "bg-yellow-500",
    approved: "bg-blue-500",
    in_progress: "bg-green-500",
    paused: "bg-orange-500",
    completed: "bg-emerald-500",
    failed: "bg-red-500",
    cancelled: "bg-gray-600",
    blocked: "bg-red-600",
  };
  return colors[status] || "bg-gray-500";
};

const getTaskStatusIcon = (status: string): string => {
  const icons: Record<string, string> = {
    pending: "⏳",
    in_progress: "🔄",
    completed: "✓",
    failed: "✗",
  };
  return icons[status] || "•";
};

export default function MissionBoard({
  missions,
  selectedMission,
  onMissionSelect,
  onRefresh,
}: MissionBoardProps) {
  const [filter, setFilter] = useState<string>("all");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const filteredMissions = missions.filter((m) => {
    if (filter === "all") return true;
    if (filter === "active") return m.status === "in_progress";
    if (filter === "pending") return m.status === "pending_approval";
    if (filter === "completed") return m.status === "completed";
    return true;
  });

  const groupedMissions = {
    critical: filteredMissions.filter((m) => m.priority === "critical"),
    high: filteredMissions.filter((m) => m.priority === "high"),
    medium: filteredMissions.filter((m) => m.priority === "medium"),
    low: filteredMissions.filter((m) => m.priority === "low" || m.priority === "routine"),
  };

  return (
    <div className="h-full flex bg-gray-900">
      <div className="w-1/2 border-r border-gray-700 overflow-y-auto">
        <div className="p-4 bg-gray-800 border-b border-gray-700 sticky top-0 z-10">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-white">Mission Board</h2>
            <div className="flex space-x-2">
              <button
                onClick={onRefresh}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-300"
              >
                Refresh
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm text-white"
              >
                + New Mission
              </button>
            </div>
          </div>

          <div className="flex space-x-2">
            {["all", "active", "pending", "completed"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 rounded text-sm capitalize ${
                  filter === f
                    ? "bg-blue-600 text-white"
                    : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="p-4 space-y-6">
          {Object.entries(groupedMissions).map(([priority, priorityMissions]) => (
            priorityMissions.length > 0 && (
              <div key={priority}>
                <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                  {priority} Priority ({priorityMissions.length})
                </h3>
                <div className="space-y-2">
                  {priorityMissions.map((mission) => (
                    <button
                      key={mission.mission_id}
                      onClick={() => onMissionSelect(mission)}
                      className={`w-full text-left p-3 rounded-lg transition-all ${
                        selectedMission?.mission_id === mission.mission_id
                          ? "bg-blue-600 border border-blue-500"
                          : "bg-gray-800 hover:bg-gray-750 border border-gray-700"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span
                              className={`w-2 h-2 rounded-full ${getStatusColor(
                                mission.status
                              )}`}
                            ></span>
                            <span className="font-medium text-white">
                              {mission.title}
                            </span>
                          </div>
                          <p className="text-xs text-gray-400 mt-1 line-clamp-1">
                            {mission.description}
                          </p>
                        </div>
                        <span
                          className={`px-2 py-0.5 rounded text-xs ${getPriorityColor(
                            mission.priority
                          )}`}
                        >
                          {mission.priority}
                        </span>
                      </div>

                      <div className="mt-2">
                        <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                          <span>Progress</span>
                          <span>
                            {mission.progress.completed}/{mission.progress.total_tasks} tasks
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-1.5">
                          <div
                            className="bg-blue-500 h-1.5 rounded-full transition-all"
                            style={{
                              width: `${mission.progress.completion_percentage}%`,
                            }}
                          ></div>
                        </div>
                      </div>

                      <div className="mt-2 flex items-center justify-between text-xs">
                        <span className="text-gray-500 capitalize">
                          {mission.status.replace("_", " ")}
                        </span>
                        <span className="text-gray-500">
                          {mission.assigned_personas.length} personas
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )
          ))}

          {filteredMissions.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>No missions found</p>
            </div>
          )}
        </div>
      </div>

      <div className="w-1/2 overflow-y-auto">
        {selectedMission ? (
          <div className="p-4">
            <div className="bg-gray-800 rounded-lg p-4 mb-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h2 className="text-xl font-semibold text-white">
                    {selectedMission.title}
                  </h2>
                  <p className="text-gray-400 text-sm mt-1">
                    {selectedMission.description}
                  </p>
                </div>
                <div className="flex flex-col items-end space-y-2">
                  <span
                    className={`px-2 py-1 rounded text-xs ${getPriorityColor(
                      selectedMission.priority
                    )}`}
                  >
                    {selectedMission.priority}
                  </span>
                  <span
                    className={`px-2 py-1 rounded text-xs ${getStatusColor(
                      selectedMission.status
                    )} text-white`}
                  >
                    {selectedMission.status.replace("_", " ")}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Type:</span>
                  <span className="text-gray-300 ml-2">
                    {selectedMission.mission_type}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Created:</span>
                  <span className="text-gray-300 ml-2">
                    {new Date(selectedMission.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="mt-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-gray-400">Overall Progress</span>
                  <span className="text-white font-medium">
                    {selectedMission.progress.completion_percentage.toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{
                      width: `${selectedMission.progress.completion_percentage}%`,
                    }}
                  ></div>
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                  <span>{selectedMission.progress.completed} completed</span>
                  <span>{selectedMission.progress.in_progress} in progress</span>
                  <span>{selectedMission.progress.failed} failed</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 mb-4">
              <h3 className="text-lg font-semibold text-white mb-3">
                Tasks ({selectedMission.tasks.length})
              </h3>
              <div className="space-y-2">
                {selectedMission.tasks
                  .sort((a, b) => a.sequence_number - b.sequence_number)
                  .map((task) => (
                    <div
                      key={task.task_id}
                      className={`p-3 rounded-lg border ${
                        task.status === "completed"
                          ? "bg-green-900/20 border-green-700"
                          : task.status === "in_progress"
                          ? "bg-blue-900/20 border-blue-700"
                          : task.status === "failed"
                          ? "bg-red-900/20 border-red-700"
                          : "bg-gray-700/50 border-gray-600"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-2">
                          <span className="text-lg">
                            {getTaskStatusIcon(task.status)}
                          </span>
                          <div>
                            <div className="font-medium text-white">
                              {task.sequence_number}. {task.description}
                            </div>
                            <div className="text-xs text-gray-400 mt-1">
                              Type: {task.task_type}
                            </div>
                          </div>
                        </div>
                        <span
                          className={`px-2 py-0.5 rounded text-xs capitalize ${
                            task.status === "completed"
                              ? "bg-green-600 text-green-100"
                              : task.status === "in_progress"
                              ? "bg-blue-600 text-blue-100"
                              : task.status === "failed"
                              ? "bg-red-600 text-red-100"
                              : "bg-gray-600 text-gray-100"
                          }`}
                        >
                          {task.status}
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">
                Assigned Personas ({selectedMission.assigned_personas.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedMission.assigned_personas.map((personaId) => (
                  <span
                    key={personaId}
                    className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300"
                  >
                    {personaId}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-gray-300 mb-2">
                Select a Mission
              </h3>
              <p className="text-gray-500">
                Choose a mission from the list to view details
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

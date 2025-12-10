'use client';

import React, { useState, useEffect } from 'react';

interface IncidentRoom {
  room_id: string;
  incident_name: string;
  incident_type: string;
  status: string;
  priority: string;
  location: {
    lat: number;
    lng: number;
    address?: string;
  };
  commander: string;
  agencies_involved: string[];
  affected_population: number;
  casualties: {
    fatalities: number;
    injuries: number;
    missing: number;
  };
  active_tasks: number;
  completed_tasks: number;
  created_at: string;
}

interface Task {
  task_id: string;
  title: string;
  status: string;
  priority: string;
  assigned_to: string;
  assigned_agency: string;
  due_time?: string;
}

interface TimelineEvent {
  event_id: string;
  event_type: string;
  title: string;
  description: string;
  timestamp: string;
  source: string;
}

interface EOCStatus {
  eoc_id: string;
  name: string;
  activation_level: number;
  status: string;
  agencies_present: string[];
  active_incidents: number;
  personnel_on_duty: number;
}

interface CommandSummary {
  active_incidents: number;
  critical_incidents: number;
  total_affected_population: number;
  total_casualties: number;
  agencies_involved: number;
  eoc_status: EOCStatus | null;
}

export default function MultiIncidentCommandRoom() {
  const [rooms, setRooms] = useState<IncidentRoom[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<IncidentRoom | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [summary, setSummary] = useState<CommandSummary | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'timeline'>('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCommandData();
    const interval = setInterval(fetchCommandData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedRoom) {
      fetchRoomDetails(selectedRoom.room_id);
    }
  }, [selectedRoom]);

  const fetchCommandData = async () => {
    try {
      const [roomsRes, summaryRes] = await Promise.all([
        fetch('/api/emergency/command/rooms'),
        fetch('/api/emergency/command/summary'),
      ]);

      if (roomsRes.ok) {
        const roomsData = await roomsRes.json();
        setRooms(roomsData);
        if (!selectedRoom && roomsData.length > 0) {
          setSelectedRoom(roomsData[0]);
        }
      }
      if (summaryRes.ok) setSummary(await summaryRes.json());
    } catch (error) {
      console.error('Failed to fetch command data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoomDetails = async (roomId: string) => {
    try {
      const [tasksRes, timelineRes] = await Promise.all([
        fetch(`/api/emergency/command/room/${roomId}/tasks`),
        fetch(`/api/emergency/command/room/${roomId}/timeline`),
      ]);

      if (tasksRes.ok) setTasks(await tasksRes.json());
      if (timelineRes.ok) setTimeline(await timelineRes.json());
    } catch (error) {
      console.error('Failed to fetch room details:', error);
    }
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'critical': return 'bg-red-600';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'monitoring': return 'text-blue-400';
      case 'contained': return 'text-yellow-400';
      case 'resolved': return 'text-purple-400';
      case 'closed': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getTaskStatusColor = (status: string): string => {
    switch (status) {
      case 'completed': return 'bg-green-600';
      case 'in_progress': return 'bg-blue-600';
      case 'assigned': return 'bg-yellow-600';
      case 'pending': return 'bg-gray-600';
      case 'blocked': return 'bg-red-600';
      default: return 'bg-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 h-full flex items-center justify-center">
        <div className="text-gray-400">Loading command data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>🎖️</span> Multi-Incident Command
        </h2>
        {summary?.eoc_status && (
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">EOC Level:</span>
            <span className={`px-2 py-1 rounded text-sm font-medium ${
              summary.eoc_status.activation_level >= 3 ? 'bg-red-600' :
              summary.eoc_status.activation_level >= 2 ? 'bg-yellow-600' : 'bg-green-600'
            } text-white`}>
              {summary.eoc_status.activation_level}
            </span>
          </div>
        )}
      </div>

      {summary && (
        <div className="grid grid-cols-5 gap-3 mb-4">
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Active Incidents</div>
            <div className="text-white text-lg font-bold">{summary.active_incidents}</div>
          </div>
          <div className={`p-3 rounded ${summary.critical_incidents > 0 ? 'bg-red-900/50' : 'bg-gray-800'}`}>
            <div className="text-gray-400 text-xs">Critical</div>
            <div className={`text-lg font-bold ${summary.critical_incidents > 0 ? 'text-red-400' : 'text-white'}`}>
              {summary.critical_incidents}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Affected</div>
            <div className="text-white text-lg font-bold">
              {summary.total_affected_population.toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Casualties</div>
            <div className="text-white text-lg font-bold">{summary.total_casualties}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Agencies</div>
            <div className="text-white text-lg font-bold">{summary.agencies_involved}</div>
          </div>
        </div>
      )}

      <div className="flex-1 flex gap-4 overflow-hidden">
        <div className="w-1/3 bg-gray-800 rounded-lg p-3 overflow-y-auto">
          <h3 className="text-white font-medium mb-3">Incident Rooms</h3>
          <div className="space-y-2">
            {rooms.length === 0 ? (
              <div className="text-gray-500 text-center py-4">No active incidents</div>
            ) : (
              rooms.map(room => (
                <div
                  key={room.room_id}
                  onClick={() => setSelectedRoom(room)}
                  className={`p-3 rounded cursor-pointer transition-colors ${
                    selectedRoom?.room_id === room.room_id
                      ? 'bg-gray-700 ring-2 ring-blue-500'
                      : 'bg-gray-700/50 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 rounded text-xs text-white ${getPriorityColor(room.priority)}`}>
                      {room.priority.toUpperCase()}
                    </span>
                    <span className="text-white font-medium text-sm truncate">{room.incident_name}</span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-gray-400 text-xs">{room.incident_type}</span>
                    <span className={`text-xs ${getStatusColor(room.status)}`}>
                      {room.status.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="flex-1 bg-gray-800 rounded-lg p-4 overflow-y-auto">
          {selectedRoom ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-white font-medium text-lg">{selectedRoom.incident_name}</h3>
                  <div className="text-gray-400 text-sm">
                    Commander: {selectedRoom.commander}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-3 py-1 rounded text-sm ${
                      activeTab === 'overview' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
                    }`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab('tasks')}
                    className={`px-3 py-1 rounded text-sm ${
                      activeTab === 'tasks' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
                    }`}
                  >
                    Tasks
                  </button>
                  <button
                    onClick={() => setActiveTab('timeline')}
                    className={`px-3 py-1 rounded text-sm ${
                      activeTab === 'timeline' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
                    }`}
                  >
                    Timeline
                  </button>
                </div>
              </div>

              {activeTab === 'overview' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-gray-700/50 p-3 rounded">
                      <div className="text-gray-400 text-xs">Affected Population</div>
                      <div className="text-white text-lg font-bold">
                        {selectedRoom.affected_population.toLocaleString()}
                      </div>
                    </div>
                    <div className="bg-gray-700/50 p-3 rounded">
                      <div className="text-gray-400 text-xs">Casualties</div>
                      <div className="text-white text-lg font-bold">
                        {selectedRoom.casualties.fatalities + selectedRoom.casualties.injuries}
                      </div>
                      <div className="text-gray-500 text-xs">
                        {selectedRoom.casualties.fatalities} fatal, {selectedRoom.casualties.injuries} injured
                      </div>
                    </div>
                    <div className="bg-gray-700/50 p-3 rounded">
                      <div className="text-gray-400 text-xs">Tasks</div>
                      <div className="text-white text-lg font-bold">
                        {selectedRoom.completed_tasks} / {selectedRoom.active_tasks + selectedRoom.completed_tasks}
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="text-gray-400 text-xs mb-2">Agencies Involved</div>
                    <div className="flex flex-wrap gap-2">
                      {selectedRoom.agencies_involved.map((agency, i) => (
                        <span key={i} className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-sm">
                          {agency}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'tasks' && (
                <div className="space-y-2">
                  {tasks.length === 0 ? (
                    <div className="text-gray-500 text-center py-8">No tasks assigned</div>
                  ) : (
                    tasks.map(task => (
                      <div key={task.task_id} className="bg-gray-700/50 p-3 rounded">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className={`px-1.5 py-0.5 rounded text-xs text-white ${getTaskStatusColor(task.status)}`}>
                              {task.status.toUpperCase().replace('_', ' ')}
                            </span>
                            <span className="text-white text-sm">{task.title}</span>
                          </div>
                          <span className={`px-1.5 py-0.5 rounded text-xs text-white ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                        </div>
                        {task.assigned_to && (
                          <div className="text-gray-400 text-xs mt-1">
                            Assigned: {task.assigned_to} ({task.assigned_agency})
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'timeline' && (
                <div className="space-y-2">
                  {timeline.length === 0 ? (
                    <div className="text-gray-500 text-center py-8">No timeline events</div>
                  ) : (
                    timeline.map(event => (
                      <div key={event.event_id} className="bg-gray-700/50 p-3 rounded border-l-2 border-blue-500">
                        <div className="flex items-center justify-between">
                          <span className="text-white text-sm font-medium">{event.title}</span>
                          <span className="text-gray-500 text-xs">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="text-gray-400 text-sm mt-1">{event.description}</div>
                        <div className="text-gray-500 text-xs mt-1">Source: {event.source}</div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-gray-500 text-center py-8">Select an incident room</div>
          )}
        </div>
      </div>
    </div>
  );
}

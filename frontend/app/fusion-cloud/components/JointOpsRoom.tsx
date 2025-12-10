'use client';

import { useState, useEffect } from 'react';

interface Operation {
  operation_id: string;
  name: string;
  operation_type: string;
  status: string;
  lead_agency_name: string;
  commander_name: string;
  participating_agencies: Agency[];
  objectives: Objective[];
  start_time?: string;
  planned_start?: string;
}

interface Agency {
  participation_id: string;
  agency_name: string;
  role: string;
  units: Unit[];
  personnel_count: number;
  is_active: boolean;
}

interface Unit {
  unit_id: string;
  call_sign: string;
  unit_type: string;
  status: string;
  latitude: number;
  longitude: number;
}

interface Objective {
  objective_id: string;
  name: string;
  description: string;
  priority: number;
  status: string;
  assigned_agencies: string[];
}

interface TimelineEvent {
  event_id: string;
  event_type: string;
  title: string;
  description: string;
  source_agency_name: string;
  timestamp: string;
  is_critical: boolean;
}

export default function JointOpsRoom() {
  const [operations, setOperations] = useState<Operation[]>([]);
  const [selectedOperation, setSelectedOperation] = useState<Operation | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeView, setActiveView] = useState<'overview' | 'map' | 'timeline' | 'whiteboard'>('overview');

  useEffect(() => {
    loadOperations();
  }, []);

  useEffect(() => {
    if (selectedOperation) {
      loadTimeline(selectedOperation.operation_id);
    }
  }, [selectedOperation]);

  const loadOperations = async () => {
    setOperations([
      {
        operation_id: 'op-001',
        name: 'Operation Thunder Strike',
        operation_type: 'raid',
        status: 'active',
        lead_agency_name: 'Metro City PD',
        commander_name: 'Captain Johnson',
        participating_agencies: [
          {
            participation_id: 'part-001',
            agency_name: 'Metro City PD',
            role: 'commander',
            units: [
              { unit_id: 'u-001', call_sign: 'SWAT-1', unit_type: 'swat', status: 'deployed', latitude: 34.0522, longitude: -118.2437 },
              { unit_id: 'u-002', call_sign: 'SWAT-2', unit_type: 'swat', status: 'deployed', latitude: 34.0525, longitude: -118.2440 },
            ],
            personnel_count: 12,
            is_active: true,
          },
          {
            participation_id: 'part-002',
            agency_name: 'County Sheriff',
            role: 'team_leader',
            units: [
              { unit_id: 'u-003', call_sign: 'SO-15', unit_type: 'patrol', status: 'deployed', latitude: 34.0520, longitude: -118.2435 },
            ],
            personnel_count: 4,
            is_active: true,
          },
          {
            participation_id: 'part-003',
            agency_name: 'DEA',
            role: 'intelligence_officer',
            units: [],
            personnel_count: 2,
            is_active: true,
          },
        ],
        objectives: [
          { objective_id: 'obj-001', name: 'Secure perimeter', description: 'Establish outer perimeter', priority: 1, status: 'completed', assigned_agencies: ['County Sheriff'] },
          { objective_id: 'obj-002', name: 'Execute entry', description: 'Tactical entry on target location', priority: 1, status: 'in_progress', assigned_agencies: ['Metro City PD'] },
          { objective_id: 'obj-003', name: 'Evidence collection', description: 'Document and collect evidence', priority: 2, status: 'pending', assigned_agencies: ['DEA'] },
        ],
        start_time: new Date(Date.now() - 45 * 60000).toISOString(),
      },
      {
        operation_id: 'op-002',
        name: 'Regional Fugitive Sweep',
        operation_type: 'fugitive_apprehension',
        status: 'planning',
        lead_agency_name: 'US Marshals',
        commander_name: 'Deputy Marshal Williams',
        participating_agencies: [
          {
            participation_id: 'part-004',
            agency_name: 'US Marshals',
            role: 'commander',
            units: [],
            personnel_count: 6,
            is_active: true,
          },
          {
            participation_id: 'part-005',
            agency_name: 'Metro City PD',
            role: 'unit_member',
            units: [],
            personnel_count: 8,
            is_active: true,
          },
        ],
        objectives: [
          { objective_id: 'obj-004', name: 'Target identification', description: 'Confirm target locations', priority: 1, status: 'pending', assigned_agencies: ['US Marshals'] },
        ],
        planned_start: new Date(Date.now() + 24 * 3600000).toISOString(),
      },
    ]);
  };

  const loadTimeline = async (operationId: string) => {
    setTimeline([
      { event_id: 'evt-001', event_type: 'operation_started', title: 'Operation Started', description: 'Operation Thunder Strike initiated', source_agency_name: 'Metro City PD', timestamp: new Date(Date.now() - 45 * 60000).toISOString(), is_critical: true },
      { event_id: 'evt-002', event_type: 'unit_deployed', title: 'SWAT Team Deployed', description: 'SWAT-1 and SWAT-2 deployed to staging area', source_agency_name: 'Metro City PD', timestamp: new Date(Date.now() - 40 * 60000).toISOString(), is_critical: false },
      { event_id: 'evt-003', event_type: 'objective_completed', title: 'Perimeter Secured', description: 'Outer perimeter established by County Sheriff', source_agency_name: 'County Sheriff', timestamp: new Date(Date.now() - 30 * 60000).toISOString(), is_critical: false },
      { event_id: 'evt-004', event_type: 'intel_received', title: 'Intel Update', description: 'Confirmed 3 subjects inside target location', source_agency_name: 'DEA', timestamp: new Date(Date.now() - 20 * 60000).toISOString(), is_critical: true },
      { event_id: 'evt-005', event_type: 'decision', title: 'Entry Authorized', description: 'Commander authorized tactical entry', source_agency_name: 'Metro City PD', timestamp: new Date(Date.now() - 10 * 60000).toISOString(), is_critical: true },
    ]);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'planning': return 'bg-blue-500';
      case 'briefing': return 'bg-yellow-500';
      case 'paused': return 'bg-orange-500';
      case 'completed': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getObjectiveStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400';
      case 'in_progress': return 'text-yellow-400';
      case 'pending': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getTotalUnits = (agencies: Agency[]) => {
    return agencies.reduce((acc, a) => acc + a.units.length, 0);
  };

  const getTotalPersonnel = (agencies: Agency[]) => {
    return agencies.reduce((acc, a) => acc + a.personnel_count, 0);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Joint Operations Center</h2>
          <p className="text-gray-400 text-sm">Multi-agency operation coordination</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium"
        >
          + Create Operation
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {operations.map((op) => (
          <div
            key={op.operation_id}
            onClick={() => setSelectedOperation(op)}
            className={`bg-gray-800 rounded-lg p-4 border cursor-pointer transition-colors ${
              selectedOperation?.operation_id === op.operation_id
                ? 'border-blue-500'
                : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold">{op.name}</h3>
                <p className="text-gray-400 text-sm capitalize">{op.operation_type.replace('_', ' ')}</p>
              </div>
              <span className={`px-2 py-1 rounded text-xs ${getStatusColor(op.status)}`}>
                {op.status.toUpperCase()}
              </span>
            </div>
            <div className="mt-3 text-sm text-gray-400">
              <p>Lead: {op.lead_agency_name}</p>
              <p>Commander: {op.commander_name}</p>
            </div>
            <div className="mt-3 flex items-center space-x-4 text-sm">
              <span>{op.participating_agencies.length} agencies</span>
              <span>{getTotalUnits(op.participating_agencies)} units</span>
              <span>{getTotalPersonnel(op.participating_agencies)} personnel</span>
            </div>
          </div>
        ))}
      </div>

      {selectedOperation && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold">{selectedOperation.name}</h3>
                <p className="text-gray-400 text-sm">
                  {selectedOperation.lead_agency_name} | Commander: {selectedOperation.commander_name}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                {['overview', 'map', 'timeline', 'whiteboard'].map((view) => (
                  <button
                    key={view}
                    onClick={() => setActiveView(view as any)}
                    className={`px-3 py-1 rounded text-sm capitalize ${
                      activeView === view ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                    }`}
                  >
                    {view}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="p-4">
            {activeView === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Participating Agencies</h4>
                  <div className="space-y-3">
                    {selectedOperation.participating_agencies.map((agency) => (
                      <div key={agency.participation_id} className="bg-gray-700/50 rounded p-3">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{agency.agency_name}</span>
                          <span className="text-xs bg-gray-600 px-2 py-1 rounded capitalize">
                            {agency.role.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="mt-2 text-sm text-gray-400">
                          <span>{agency.personnel_count} personnel</span>
                          {agency.units.length > 0 && (
                            <span className="ml-4">{agency.units.length} units deployed</span>
                          )}
                        </div>
                        {agency.units.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {agency.units.map((unit) => (
                              <span
                                key={unit.unit_id}
                                className={`text-xs px-2 py-1 rounded ${
                                  unit.status === 'deployed' ? 'bg-green-500/20 text-green-400' : 'bg-gray-600'
                                }`}
                              >
                                {unit.call_sign}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                  <button className="mt-3 text-sm text-blue-400 hover:text-blue-300">
                    + Add Agency
                  </button>
                </div>

                <div>
                  <h4 className="font-medium mb-3">Objectives</h4>
                  <div className="space-y-3">
                    {selectedOperation.objectives.map((obj) => (
                      <div key={obj.objective_id} className="bg-gray-700/50 rounded p-3">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{obj.name}</span>
                          <span className={`text-sm capitalize ${getObjectiveStatusColor(obj.status)}`}>
                            {obj.status.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 mt-1">{obj.description}</p>
                        <div className="mt-2 flex items-center space-x-2">
                          <span className="text-xs text-gray-500">Assigned:</span>
                          {obj.assigned_agencies.map((agency) => (
                            <span key={agency} className="text-xs bg-gray-600 px-2 py-0.5 rounded">
                              {agency}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                  <button className="mt-3 text-sm text-blue-400 hover:text-blue-300">
                    + Add Objective
                  </button>
                </div>
              </div>
            )}

            {activeView === 'map' && (
              <div className="bg-gray-700/50 rounded-lg h-96 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">🗺️</div>
                  <p className="text-gray-400">Operations Map View</p>
                  <p className="text-sm text-gray-500">Real-time unit positions and area of operations</p>
                </div>
              </div>
            )}

            {activeView === 'timeline' && (
              <div className="space-y-4">
                <h4 className="font-medium">Operation Timeline</h4>
                <div className="relative">
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-700"></div>
                  <div className="space-y-4">
                    {timeline.map((event) => (
                      <div key={event.event_id} className="relative pl-10">
                        <div className={`absolute left-2 w-4 h-4 rounded-full ${
                          event.is_critical ? 'bg-red-500' : 'bg-blue-500'
                        }`}></div>
                        <div className="bg-gray-700/50 rounded p-3">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{event.title}</span>
                            <span className="text-xs text-gray-500">{formatTime(event.timestamp)}</span>
                          </div>
                          <p className="text-sm text-gray-400 mt-1">{event.description}</p>
                          <span className="text-xs text-gray-500">{event.source_agency_name}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <button className="text-sm text-blue-400 hover:text-blue-300">
                  + Add Timeline Event
                </button>
              </div>
            )}

            {activeView === 'whiteboard' && (
              <div className="bg-gray-700/50 rounded-lg h-96 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">📝</div>
                  <p className="text-gray-400">Shared Whiteboard</p>
                  <p className="text-sm text-gray-500">Collaborative planning and notes</p>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-700 flex space-x-3">
            {selectedOperation.status === 'planning' && (
              <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm">
                Start Operation
              </button>
            )}
            {selectedOperation.status === 'active' && (
              <>
                <button className="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded text-sm">
                  Pause Operation
                </button>
                <button className="bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded text-sm">
                  Complete Operation
                </button>
              </>
            )}
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm">
              Deploy Unit
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm">
              Send Alert
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

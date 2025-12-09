'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { MajorIncidentBoard } from './components/MajorIncidentBoard';
import { ICSOrgChart } from './components/ICSOrgChart';
import { CommandTimeline } from './components/CommandTimeline';
import { StrategyMapViewer } from './components/StrategyMapViewer';
import { ResourceAssignmentPanel } from './components/ResourceAssignmentPanel';
import { BriefingBuilder } from './components/BriefingBuilder';
import { CommandNotificationsPanel } from './components/CommandNotificationsPanel';

// Types
interface MajorIncident {
  id: string;
  incident_number: string;
  incident_type: string;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'contained' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  commander_badge: string | null;
  commander_name: string | null;
  rtcc_analyst: string | null;
  agencies: string[];
  units: string[];
  created_at: string;
  activated_at: string | null;
  closed_at: string | null;
}

interface ICSRole {
  role: string;
  role_name: string;
  section: string;
  badge: string | null;
  name: string | null;
  assigned_at: string | null;
}

interface TimelineEvent {
  id: string;
  event_type: string;
  source: string;
  title: string;
  description: string;
  priority: string;
  timestamp: string;
  is_pinned: boolean;
}

interface Resource {
  id: string;
  name: string;
  resource_type: string;
  status: string;
  agency: string;
  call_sign: string;
  role: string | null;
}

export default function CommandPage() {
  const [activeIncident, setActiveIncident] = useState<MajorIncident | null>(null);
  const [incidents, setIncidents] = useState<MajorIncident[]>([]);
  const [icsRoles, setIcsRoles] = useState<ICSRole[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showNotifications, setShowNotifications] = useState(true);

  // Load mock data (would be API calls in production)
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        // Mock incidents
        const mockIncidents: MajorIncident[] = [
          {
            id: 'inc-001',
            incident_number: 'MI-2024-0001',
            incident_type: 'active_shooter',
            title: 'Active Shooter - Downtown Mall',
            description: 'Reports of active shooter at Peachtree Center Mall. Multiple shots fired.',
            status: 'active',
            priority: 'critical',
            location: {
              latitude: 33.7590,
              longitude: -84.3880,
              address: '231 Peachtree St NE, Atlanta, GA 30303',
            },
            commander_badge: 'CMD-001',
            commander_name: 'Captain Rodriguez',
            rtcc_analyst: 'Analyst Chen',
            agencies: ['Atlanta PD', 'SWAT', 'EMS'],
            units: ['Alpha-11', 'Alpha-12', 'SWAT-01', 'SWAT-02', 'EMS-01'],
            created_at: '2024-01-15T14:30:00Z',
            activated_at: '2024-01-15T14:32:00Z',
            closed_at: null,
          },
          {
            id: 'inc-002',
            incident_number: 'MI-2024-0002',
            incident_type: 'barricaded_subject',
            title: 'Barricaded Subject - Residential',
            description: 'Armed subject barricaded in residence with possible hostages.',
            status: 'active',
            priority: 'high',
            location: {
              latitude: 33.7710,
              longitude: -84.3650,
              address: '456 Oak Street, Atlanta, GA 30312',
            },
            commander_badge: 'CMD-002',
            commander_name: 'Lieutenant Martinez',
            rtcc_analyst: 'Analyst Williams',
            agencies: ['Atlanta PD', 'Negotiators'],
            units: ['Bravo-21', 'Bravo-22', 'NEG-01'],
            created_at: '2024-01-15T15:00:00Z',
            activated_at: '2024-01-15T15:05:00Z',
            closed_at: null,
          },
        ];

        // Mock ICS roles for active incident
        const mockIcsRoles: ICSRole[] = [
          { role: 'incident_commander', role_name: 'Incident Commander', section: 'command', badge: 'CMD-001', name: 'Captain Rodriguez', assigned_at: '2024-01-15T14:32:00Z' },
          { role: 'deputy_commander', role_name: 'Deputy Commander', section: 'command', badge: 'DEP-001', name: 'Lieutenant Kim', assigned_at: '2024-01-15T14:35:00Z' },
          { role: 'operations_chief', role_name: 'Operations Chief', section: 'operations', badge: 'OPS-001', name: 'Sergeant Thompson', assigned_at: '2024-01-15T14:40:00Z' },
          { role: 'planning_chief', role_name: 'Planning Chief', section: 'planning', badge: 'PLN-001', name: 'Detective Harris', assigned_at: '2024-01-15T14:42:00Z' },
          { role: 'logistics_chief', role_name: 'Logistics Chief', section: 'logistics', badge: null, name: null, assigned_at: null },
          { role: 'safety_officer', role_name: 'Safety Officer', section: 'command', badge: 'SAF-001', name: 'Officer Davis', assigned_at: '2024-01-15T14:45:00Z' },
          { role: 'public_info_officer', role_name: 'Public Information Officer', section: 'command', badge: null, name: null, assigned_at: null },
          { role: 'intelligence_officer', role_name: 'Intelligence Officer', section: 'command', badge: 'INT-001', name: 'Analyst Chen', assigned_at: '2024-01-15T14:33:00Z' },
        ];

        // Mock timeline events
        const mockTimeline: TimelineEvent[] = [
          { id: 'evt-001', event_type: 'incident_created', source: 'cad', title: 'Incident Created', description: 'Major incident created from CAD call #2024-1234', priority: 'high', timestamp: '2024-01-15T14:30:00Z', is_pinned: false },
          { id: 'evt-002', event_type: 'incident_activated', source: 'command', title: 'Incident Activated', description: 'Incident activated by Captain Rodriguez', priority: 'high', timestamp: '2024-01-15T14:32:00Z', is_pinned: true },
          { id: 'evt-003', event_type: 'ics_role_assigned', source: 'command', title: 'IC Assigned', description: 'Captain Rodriguez assigned as Incident Commander', priority: 'medium', timestamp: '2024-01-15T14:32:00Z', is_pinned: false },
          { id: 'evt-004', event_type: 'unit_dispatched', source: 'cad', title: 'SWAT Dispatched', description: 'SWAT-01 and SWAT-02 dispatched to scene', priority: 'high', timestamp: '2024-01-15T14:35:00Z', is_pinned: false },
          { id: 'evt-005', event_type: 'perimeter_established', source: 'tactical', title: 'Perimeter Established', description: 'Outer perimeter established on Peachtree St', priority: 'high', timestamp: '2024-01-15T14:40:00Z', is_pinned: true },
          { id: 'evt-006', event_type: 'gunfire_detected', source: 'shotspotter', title: 'Gunfire Detected', description: 'ShotSpotter detected 3 rounds fired inside mall', priority: 'critical', timestamp: '2024-01-15T14:42:00Z', is_pinned: true },
          { id: 'evt-007', event_type: 'unit_arrived', source: 'cad', title: 'EMS On Scene', description: 'EMS-01 arrived and staged at command post', priority: 'medium', timestamp: '2024-01-15T14:45:00Z', is_pinned: false },
          { id: 'evt-008', event_type: 'command_note', source: 'command', title: 'Evacuation Update', description: 'North wing evacuation complete. 200+ civilians evacuated.', priority: 'high', timestamp: '2024-01-15T14:50:00Z', is_pinned: false },
        ];

        // Mock resources
        const mockResources: Resource[] = [
          { id: 'res-001', name: 'Alpha-11', resource_type: 'patrol_unit', status: 'on_scene', agency: 'Atlanta PD', call_sign: 'A-11', role: 'perimeter' },
          { id: 'res-002', name: 'Alpha-12', resource_type: 'patrol_unit', status: 'on_scene', agency: 'Atlanta PD', call_sign: 'A-12', role: 'perimeter' },
          { id: 'res-003', name: 'SWAT-01', resource_type: 'swat', status: 'on_scene', agency: 'Atlanta PD', call_sign: 'SWAT-1', role: 'entry_team' },
          { id: 'res-004', name: 'SWAT-02', resource_type: 'swat', status: 'on_scene', agency: 'Atlanta PD', call_sign: 'SWAT-2', role: 'entry_team' },
          { id: 'res-005', name: 'EMS-01', resource_type: 'ems', status: 'staged', agency: 'County EMS', call_sign: 'M-01', role: 'medical' },
          { id: 'res-006', name: 'K9-01', resource_type: 'k9', status: 'en_route', agency: 'Atlanta PD', call_sign: 'K9-1', role: null },
          { id: 'res-007', name: 'Air-01', resource_type: 'aviation', status: 'en_route', agency: 'Atlanta PD', call_sign: 'AIR-1', role: null },
          { id: 'res-008', name: 'Fire-01', resource_type: 'fire', status: 'staged', agency: 'Atlanta Fire', call_sign: 'E-01', role: 'standby' },
        ];

        setIncidents(mockIncidents);
        setActiveIncident(mockIncidents[0]);
        setIcsRoles(mockIcsRoles);
        setTimeline(mockTimeline);
        setResources(mockResources);
        setError(null);
      } catch (err) {
        setError('Failed to load command data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  // Handle incident selection
  const handleSelectIncident = useCallback((incident: MajorIncident) => {
    setActiveIncident(incident);
  }, []);

  // Handle activate incident
  const handleActivateIncident = useCallback((incidentId: string) => {
    setIncidents(prev => prev.map(inc => 
      inc.id === incidentId 
        ? { ...inc, status: 'active' as const, activated_at: new Date().toISOString() }
        : inc
    ));
    if (activeIncident?.id === incidentId) {
      setActiveIncident(prev => prev ? { ...prev, status: 'active', activated_at: new Date().toISOString() } : null);
    }
  }, [activeIncident]);

  // Handle close incident
  const handleCloseIncident = useCallback((incidentId: string) => {
    setIncidents(prev => prev.map(inc => 
      inc.id === incidentId 
        ? { ...inc, status: 'closed' as const, closed_at: new Date().toISOString() }
        : inc
    ));
    if (activeIncident?.id === incidentId) {
      setActiveIncident(prev => prev ? { ...prev, status: 'closed', closed_at: new Date().toISOString() } : null);
    }
  }, [activeIncident]);

  // Handle ICS role assignment (drag and drop)
  const handleAssignRole = useCallback((role: string, badge: string, name: string) => {
    setIcsRoles(prev => prev.map(r => 
      r.role === role 
        ? { ...r, badge, name, assigned_at: new Date().toISOString() }
        : r
    ));
  }, []);

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-red-500';
      case 'contained': return 'bg-yellow-500';
      case 'resolved': return 'bg-green-500';
      case 'closed': return 'bg-gray-500';
      default: return 'bg-blue-500';
    }
  };

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-600 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-yellow-500 text-black';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-lg text-white">Loading command center...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold">Major Incident Command Center</h1>
            {activeIncident && (
              <Badge className={getPriorityColor(activeIncident.priority)}>
                {activeIncident.priority.toUpperCase()}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              {showNotifications ? 'Hide' : 'Show'} Notifications
            </Button>
            {activeIncident && (
              <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${getStatusColor(activeIncident.status)} animate-pulse`} />
                <span className="text-sm font-medium">{activeIncident.incident_number}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="m-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex h-[calc(100vh-64px)]">
        {/* Left Sidebar - Incident List */}
        <div className="w-64 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <div className="p-3 border-b border-gray-700">
            <h2 className="text-sm font-semibold text-gray-400">ACTIVE INCIDENTS</h2>
          </div>
          <div className="p-2 space-y-2">
            {incidents.filter(i => i.status !== 'closed').map(incident => (
              <div
                key={incident.id}
                onClick={() => handleSelectIncident(incident)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  activeIncident?.id === incident.id 
                    ? 'bg-blue-600' 
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium">{incident.incident_number}</span>
                  <span className={`w-2 h-2 rounded-full ${getStatusColor(incident.status)}`} />
                </div>
                <p className="text-sm font-medium truncate">{incident.title}</p>
                <p className="text-xs text-gray-400 truncate">{incident.location.address}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="outline" className="text-xs">
                    {incident.units.length} units
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {incident.agencies.length} agencies
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          {activeIncident ? (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
              <div className="bg-gray-800 border-b border-gray-700 px-4">
                <TabsList className="bg-transparent">
                  <TabsTrigger value="overview" className="data-[state=active]:bg-gray-700">
                    Overview
                  </TabsTrigger>
                  <TabsTrigger value="ics" className="data-[state=active]:bg-gray-700">
                    ICS Structure
                  </TabsTrigger>
                  <TabsTrigger value="map" className="data-[state=active]:bg-gray-700">
                    Strategy Map
                  </TabsTrigger>
                  <TabsTrigger value="resources" className="data-[state=active]:bg-gray-700">
                    Resources
                  </TabsTrigger>
                  <TabsTrigger value="timeline" className="data-[state=active]:bg-gray-700">
                    Timeline
                  </TabsTrigger>
                  <TabsTrigger value="briefing" className="data-[state=active]:bg-gray-700">
                    Briefing
                  </TabsTrigger>
                </TabsList>
              </div>

              <div className="flex-1 overflow-y-auto p-4">
                <TabsContent value="overview" className="m-0 h-full">
                  <MajorIncidentBoard
                    incident={activeIncident}
                    icsRoles={icsRoles}
                    resources={resources}
                    timeline={timeline.slice(0, 5)}
                    onActivate={() => handleActivateIncident(activeIncident.id)}
                    onClose={() => handleCloseIncident(activeIncident.id)}
                  />
                </TabsContent>

                <TabsContent value="ics" className="m-0 h-full">
                  <ICSOrgChart
                    incidentId={activeIncident.id}
                    roles={icsRoles}
                    onAssignRole={handleAssignRole}
                  />
                </TabsContent>

                <TabsContent value="map" className="m-0 h-full">
                  <StrategyMapViewer
                    incidentId={activeIncident.id}
                    center={activeIncident.location}
                    resources={resources}
                  />
                </TabsContent>

                <TabsContent value="resources" className="m-0 h-full">
                  <ResourceAssignmentPanel
                    incidentId={activeIncident.id}
                    resources={resources}
                  />
                </TabsContent>

                <TabsContent value="timeline" className="m-0 h-full">
                  <CommandTimeline
                    incidentId={activeIncident.id}
                    events={timeline}
                  />
                </TabsContent>

                <TabsContent value="briefing" className="m-0 h-full">
                  <BriefingBuilder
                    incidentId={activeIncident.id}
                    incident={activeIncident}
                    icsRoles={icsRoles}
                    resources={resources}
                    timeline={timeline}
                  />
                </TabsContent>
              </div>
            </Tabs>
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">Select an incident to view details</p>
            </div>
          )}
        </div>

        {/* Right Sidebar - Notifications */}
        {showNotifications && (
          <div className="w-80 bg-gray-800 border-l border-gray-700 overflow-y-auto">
            <CommandNotificationsPanel incidentId={activeIncident?.id || null} />
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

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

interface Resource {
  id: string;
  name: string;
  resource_type: string;
  status: string;
  agency: string;
  call_sign: string;
  role: string | null;
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

interface MajorIncidentBoardProps {
  incident: MajorIncident;
  icsRoles: ICSRole[];
  resources: Resource[];
  timeline: TimelineEvent[];
  onActivate: () => void;
  onClose: () => void;
}

export function MajorIncidentBoard({
  incident,
  icsRoles,
  resources,
  timeline,
  onActivate,
  onClose,
}: MajorIncidentBoardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-red-500';
      case 'contained': return 'bg-yellow-500';
      case 'resolved': return 'bg-green-500';
      case 'closed': return 'bg-gray-500';
      default: return 'bg-blue-500';
    }
  };

  const getIncidentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      active_shooter: 'Active Shooter',
      barricaded_subject: 'Barricaded Subject',
      hostage_situation: 'Hostage Situation',
      pursuit: 'Vehicle Pursuit',
      riot: 'Civil Disturbance',
      hazmat: 'HazMat Incident',
      mass_casualty: 'Mass Casualty',
      bomb_threat: 'Bomb Threat',
      natural_disaster: 'Natural Disaster',
      officer_involved_shooting: 'Officer Involved Shooting',
      missing_person: 'Missing Person',
      other: 'Other',
    };
    return labels[type] || type;
  };

  const assignedRoles = icsRoles.filter(r => r.badge !== null);
  const unassignedRoles = icsRoles.filter(r => r.badge === null);

  const resourcesByStatus = {
    on_scene: resources.filter(r => r.status === 'on_scene'),
    en_route: resources.filter(r => r.status === 'en_route'),
    staged: resources.filter(r => r.status === 'staged'),
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDateTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="grid grid-cols-12 gap-4 h-full">
      {/* Main Info */}
      <div className="col-span-8 space-y-4">
        {/* Incident Header */}
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-xl font-bold text-white">{incident.title}</h2>
                  <Badge className={getStatusColor(incident.status)}>
                    {incident.status.toUpperCase()}
                  </Badge>
                </div>
                <p className="text-gray-400 mb-2">{incident.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <span>Type: {getIncidentTypeLabel(incident.incident_type)}</span>
                  <span>|</span>
                  <span>Created: {formatDateTime(incident.created_at)}</span>
                  {incident.activated_at && (
                    <>
                      <span>|</span>
                      <span>Activated: {formatDateTime(incident.activated_at)}</span>
                    </>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                {incident.status === 'pending' && (
                  <Button onClick={onActivate} className="bg-red-600 hover:bg-red-700">
                    Activate Incident
                  </Button>
                )}
                {incident.status === 'active' && (
                  <Button onClick={onClose} variant="outline">
                    Close Incident
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Location */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Location</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-white font-medium">{incident.location.address}</p>
            <p className="text-gray-400 text-sm">
              Coordinates: {incident.location.latitude.toFixed(4)}, {incident.location.longitude.toFixed(4)}
            </p>
          </CardContent>
        </Card>

        {/* Command Staff */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Command Staff</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-gray-400 text-xs">Incident Commander</p>
                <p className="text-white font-medium">
                  {incident.commander_name || 'Not Assigned'}
                </p>
                {incident.commander_badge && (
                  <p className="text-gray-400 text-xs">Badge: {incident.commander_badge}</p>
                )}
              </div>
              <div>
                <p className="text-gray-400 text-xs">RTCC Analyst</p>
                <p className="text-white font-medium">
                  {incident.rtcc_analyst || 'Not Assigned'}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">ICS Roles Filled</p>
                <p className="text-white font-medium">
                  {assignedRoles.length} / {icsRoles.length}
                </p>
                {unassignedRoles.length > 0 && (
                  <p className="text-yellow-400 text-xs">
                    {unassignedRoles.length} roles need assignment
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Resources Summary */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Resources ({resources.length} total)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-green-900/30 rounded-lg p-3">
                <p className="text-green-400 text-xs font-medium">ON SCENE</p>
                <p className="text-2xl font-bold text-white">{resourcesByStatus.on_scene.length}</p>
                <div className="mt-2 space-y-1">
                  {resourcesByStatus.on_scene.slice(0, 3).map(r => (
                    <p key={r.id} className="text-xs text-gray-300">{r.call_sign}</p>
                  ))}
                  {resourcesByStatus.on_scene.length > 3 && (
                    <p className="text-xs text-gray-500">+{resourcesByStatus.on_scene.length - 3} more</p>
                  )}
                </div>
              </div>
              <div className="bg-yellow-900/30 rounded-lg p-3">
                <p className="text-yellow-400 text-xs font-medium">EN ROUTE</p>
                <p className="text-2xl font-bold text-white">{resourcesByStatus.en_route.length}</p>
                <div className="mt-2 space-y-1">
                  {resourcesByStatus.en_route.slice(0, 3).map(r => (
                    <p key={r.id} className="text-xs text-gray-300">{r.call_sign}</p>
                  ))}
                </div>
              </div>
              <div className="bg-blue-900/30 rounded-lg p-3">
                <p className="text-blue-400 text-xs font-medium">STAGED</p>
                <p className="text-2xl font-bold text-white">{resourcesByStatus.staged.length}</p>
                <div className="mt-2 space-y-1">
                  {resourcesByStatus.staged.slice(0, 3).map(r => (
                    <p key={r.id} className="text-xs text-gray-300">{r.call_sign}</p>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Agencies */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Participating Agencies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {incident.agencies.map((agency, idx) => (
                <Badge key={idx} variant="outline" className="text-white border-gray-600">
                  {agency}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Right Sidebar - Timeline */}
      <div className="col-span-4">
        <Card className="bg-gray-800 border-gray-700 h-full">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm flex items-center justify-between">
              <span>Recent Activity</span>
              <Badge variant="outline" className="text-xs">{timeline.length} events</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {timeline.map(event => (
              <div
                key={event.id}
                className={`p-3 rounded-lg ${
                  event.is_pinned ? 'bg-yellow-900/30 border border-yellow-700' : 'bg-gray-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-400">{formatTime(event.timestamp)}</span>
                  {event.is_pinned && (
                    <Badge className="bg-yellow-600 text-xs">Pinned</Badge>
                  )}
                </div>
                <p className="text-sm font-medium text-white">{event.title}</p>
                <p className="text-xs text-gray-400">{event.description}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="outline" className="text-xs">
                    {event.source}
                  </Badge>
                  <Badge
                    variant="outline"
                    className={`text-xs ${
                      event.priority === 'critical' ? 'border-red-500 text-red-400' :
                      event.priority === 'high' ? 'border-orange-500 text-orange-400' :
                      'border-gray-500 text-gray-400'
                    }`}
                  >
                    {event.priority}
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

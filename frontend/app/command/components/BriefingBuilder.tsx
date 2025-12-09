'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface MajorIncident {
  id: string;
  incident_number: string;
  incident_type: string;
  title: string;
  description: string;
  status: string;
  priority: string;
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

interface BriefingBuilderProps {
  incidentId: string;
  incident: MajorIncident;
  icsRoles: ICSRole[];
  resources: Resource[];
  timeline: TimelineEvent[];
}

interface CommandNote {
  id: string;
  content: string;
  type: string;
  priority: string;
  created_by: string;
  created_at: string;
  is_pinned: boolean;
}

export function BriefingBuilder({
  incidentId,
  incident,
  icsRoles,
  resources,
  timeline,
}: BriefingBuilderProps) {
  const [activeSection, setActiveSection] = useState('notes');
  const [newNote, setNewNote] = useState('');
  const [notes, setNotes] = useState<CommandNote[]>([
    {
      id: 'note-001',
      content: 'Suspect described as male, 30s, wearing dark hoodie. Last seen heading toward north exit.',
      type: 'intelligence',
      priority: 'high',
      created_by: 'Analyst Chen',
      created_at: '2024-01-15T14:35:00Z',
      is_pinned: true,
    },
    {
      id: 'note-002',
      content: 'North wing evacuation complete. Approximately 200 civilians evacuated safely.',
      type: 'situation',
      priority: 'medium',
      created_by: 'Captain Rodriguez',
      created_at: '2024-01-15T14:50:00Z',
      is_pinned: false,
    },
    {
      id: 'note-003',
      content: 'SWAT entry team staged at south entrance. Awaiting green light.',
      type: 'tactical',
      priority: 'high',
      created_by: 'Sgt. Thompson',
      created_at: '2024-01-15T14:55:00Z',
      is_pinned: false,
    },
  ]);

  const sections = [
    { id: 'notes', label: 'Command Notes' },
    { id: 'briefing', label: 'Generate Briefing' },
    { id: 'export', label: 'Export' },
  ];

  const noteTypes = [
    { id: 'general', label: 'General', color: 'bg-gray-500' },
    { id: 'intelligence', label: 'Intelligence', color: 'bg-blue-500' },
    { id: 'tactical', label: 'Tactical', color: 'bg-orange-500' },
    { id: 'situation', label: 'Situation', color: 'bg-green-500' },
    { id: 'safety', label: 'Safety', color: 'bg-red-500' },
  ];

  const getNoteTypeColor = (type: string) => {
    const noteType = noteTypes.find(t => t.id === type);
    return noteType?.color || 'bg-gray-500';
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleAddNote = () => {
    if (!newNote.trim()) return;
    
    const note: CommandNote = {
      id: `note-${Date.now()}`,
      content: newNote,
      type: 'general',
      priority: 'medium',
      created_by: 'Current User',
      created_at: new Date().toISOString(),
      is_pinned: false,
    };
    
    setNotes(prev => [note, ...prev]);
    setNewNote('');
  };

  const togglePinNote = (noteId: string) => {
    setNotes(prev => prev.map(note =>
      note.id === noteId ? { ...note, is_pinned: !note.is_pinned } : note
    ));
  };

  const assignedRoles = icsRoles.filter(r => r.badge !== null);

  return (
    <div className="h-full flex gap-4">
      {/* Main Content */}
      <div className="flex-1 space-y-4">
        {/* Section Tabs */}
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-2">
            <div className="flex gap-2">
              {sections.map(section => (
                <Button
                  key={section.id}
                  variant={activeSection === section.id ? 'default' : 'outline'}
                  onClick={() => setActiveSection(section.id)}
                  className={activeSection === section.id ? 'bg-blue-600' : ''}
                >
                  {section.label}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Command Notes Section */}
        {activeSection === 'notes' && (
          <Card className="bg-gray-800 border-gray-700 flex-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm">Command Notes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add Note */}
              <div className="flex gap-2">
                <Input
                  placeholder="Add a command note..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddNote()}
                  className="flex-1 bg-gray-700 border-gray-600 text-white"
                />
                <Button onClick={handleAddNote} className="bg-blue-600">
                  Add Note
                </Button>
              </div>

              {/* Notes List */}
              <div className="space-y-3 max-h-[calc(100vh-400px)] overflow-y-auto">
                {/* Pinned Notes */}
                {notes.filter(n => n.is_pinned).length > 0 && (
                  <div className="mb-4">
                    <p className="text-xs text-yellow-400 mb-2">Pinned Notes</p>
                    {notes.filter(n => n.is_pinned).map(note => (
                      <div
                        key={note.id}
                        className="p-3 rounded-lg bg-yellow-900/20 border border-yellow-700 mb-2"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge className={`text-xs ${getNoteTypeColor(note.type)}`}>
                                {note.type}
                              </Badge>
                              <span className="text-xs text-gray-400">{formatTime(note.created_at)}</span>
                              <span className="text-xs text-gray-500">by {note.created_by}</span>
                            </div>
                            <p className="text-sm text-white">{note.content}</p>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => togglePinNote(note.id)}
                            className="text-yellow-400"
                          >
                            Unpin
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Regular Notes */}
                {notes.filter(n => !n.is_pinned).map(note => (
                  <div
                    key={note.id}
                    className="p-3 rounded-lg bg-gray-700"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={`text-xs ${getNoteTypeColor(note.type)}`}>
                            {note.type}
                          </Badge>
                          <span className="text-xs text-gray-400">{formatTime(note.created_at)}</span>
                          <span className="text-xs text-gray-500">by {note.created_by}</span>
                        </div>
                        <p className="text-sm text-white">{note.content}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => togglePinNote(note.id)}
                        className="text-gray-400 hover:text-yellow-400"
                      >
                        Pin
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Generate Briefing Section */}
        {activeSection === 'briefing' && (
          <Card className="bg-gray-800 border-gray-700 flex-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm">Command Briefing Generator</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-400">
                Generate a comprehensive command briefing based on current incident data.
              </p>

              {/* Briefing Preview */}
              <div className="bg-gray-900 rounded-lg p-4 space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-white mb-2">
                    Command Briefing: {incident.incident_number}
                  </h3>
                  <p className="text-sm text-gray-400">
                    Generated: {new Date().toLocaleString()}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-blue-400 mb-1">Executive Summary</h4>
                  <p className="text-sm text-gray-300">
                    {incident.title} - {incident.description}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-blue-400 mb-1">Location</h4>
                  <p className="text-sm text-gray-300">{incident.location.address}</p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-blue-400 mb-1">Command Structure</h4>
                  <p className="text-sm text-gray-300">
                    IC: {incident.commander_name || 'Not Assigned'} | 
                    RTCC: {incident.rtcc_analyst || 'Not Assigned'} | 
                    ICS Roles Filled: {assignedRoles.length}/{icsRoles.length}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-blue-400 mb-1">Resources</h4>
                  <p className="text-sm text-gray-300">
                    {resources.filter(r => r.status === 'on_scene').length} on scene, 
                    {resources.filter(r => r.status === 'en_route').length} en route, 
                    {resources.filter(r => r.status === 'staged').length} staged
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-blue-400 mb-1">Agencies</h4>
                  <p className="text-sm text-gray-300">{incident.agencies.join(', ')}</p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-blue-400 mb-1">Key Events</h4>
                  <ul className="text-sm text-gray-300 list-disc list-inside">
                    {timeline.filter(e => e.is_pinned || e.priority === 'critical').slice(0, 5).map(event => (
                      <li key={event.id}>{event.title}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <Button className="w-full bg-blue-600">
                Generate Full Briefing
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Export Section */}
        {activeSection === 'export' && (
          <Card className="bg-gray-800 border-gray-700 flex-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm">Export Options</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-400">
                Export incident data and briefings in various formats.
              </p>

              <div className="grid grid-cols-2 gap-4">
                <Card className="bg-gray-700 border-gray-600 p-4 cursor-pointer hover:bg-gray-600">
                  <div className="text-center">
                    <span className="text-3xl">📄</span>
                    <p className="text-sm font-medium text-white mt-2">PDF Report</p>
                    <p className="text-xs text-gray-400">Full briefing document</p>
                  </div>
                </Card>

                <Card className="bg-gray-700 border-gray-600 p-4 cursor-pointer hover:bg-gray-600">
                  <div className="text-center">
                    <span className="text-3xl">📝</span>
                    <p className="text-sm font-medium text-white mt-2">Word Document</p>
                    <p className="text-xs text-gray-400">Editable DOCX format</p>
                  </div>
                </Card>

                <Card className="bg-gray-700 border-gray-600 p-4 cursor-pointer hover:bg-gray-600">
                  <div className="text-center">
                    <span className="text-3xl">📊</span>
                    <p className="text-sm font-medium text-white mt-2">JSON Data</p>
                    <p className="text-xs text-gray-400">Machine-readable format</p>
                  </div>
                </Card>

                <Card className="bg-gray-700 border-gray-600 p-4 cursor-pointer hover:bg-gray-600">
                  <div className="text-center">
                    <span className="text-3xl">📋</span>
                    <p className="text-sm font-medium text-white mt-2">Timeline Export</p>
                    <p className="text-xs text-gray-400">Event log only</p>
                  </div>
                </Card>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Right Panel - Quick Stats */}
      <div className="w-72 space-y-4">
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Incident Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-xs text-gray-400">Status</p>
              <Badge className="bg-red-500">{incident.status.toUpperCase()}</Badge>
            </div>
            <div>
              <p className="text-xs text-gray-400">Priority</p>
              <Badge className="bg-orange-500">{incident.priority.toUpperCase()}</Badge>
            </div>
            <div>
              <p className="text-xs text-gray-400">Duration</p>
              <p className="text-white">
                {incident.activated_at 
                  ? `${Math.round((Date.now() - new Date(incident.activated_at).getTime()) / 60000)} minutes`
                  : 'Not activated'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Note Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div className="bg-gray-700 rounded p-2">
                <p className="text-lg font-bold text-white">{notes.length}</p>
                <p className="text-xs text-gray-400">Total Notes</p>
              </div>
              <div className="bg-gray-700 rounded p-2">
                <p className="text-lg font-bold text-yellow-400">{notes.filter(n => n.is_pinned).length}</p>
                <p className="text-xs text-gray-400">Pinned</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Note Types</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {noteTypes.map(type => {
              const count = notes.filter(n => n.type === type.id).length;
              return (
                <div key={type.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded ${type.color}`} />
                    <span className="text-sm text-gray-300">{type.label}</span>
                  </div>
                  <span className="text-sm text-white">{count}</span>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

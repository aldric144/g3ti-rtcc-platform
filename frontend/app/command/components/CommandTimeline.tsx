'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

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

interface CommandTimelineProps {
  incidentId: string;
  events: TimelineEvent[];
}

export function CommandTimeline({ incidentId, events }: CommandTimelineProps) {
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showPinnedOnly, setShowPinnedOnly] = useState(false);

  const eventTypes = [
    { id: 'all', label: 'All Events' },
    { id: 'incident', label: 'Incident' },
    { id: 'ics', label: 'ICS' },
    { id: 'unit', label: 'Units' },
    { id: 'tactical', label: 'Tactical' },
    { id: 'command', label: 'Command' },
  ];

  const sources = [
    { id: 'cad', label: 'CAD', color: 'bg-blue-500' },
    { id: 'command', label: 'Command', color: 'bg-purple-500' },
    { id: 'tactical', label: 'Tactical', color: 'bg-orange-500' },
    { id: 'shotspotter', label: 'ShotSpotter', color: 'bg-red-500' },
    { id: 'lpr', label: 'LPR', color: 'bg-green-500' },
    { id: 'officer_safety', label: 'Safety', color: 'bg-yellow-500' },
  ];

  const getSourceColor = (source: string) => {
    const s = sources.find(src => src.id === source);
    return s?.color || 'bg-gray-500';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'border-red-500 bg-red-900/30';
      case 'high': return 'border-orange-500 bg-orange-900/20';
      case 'medium': return 'border-yellow-500 bg-yellow-900/10';
      case 'low': return 'border-green-500 bg-green-900/10';
      default: return 'border-gray-500';
    }
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'incident_created':
      case 'incident_activated':
      case 'incident_closed':
        return '🚨';
      case 'ics_role_assigned':
      case 'commander_change':
        return '👤';
      case 'unit_dispatched':
      case 'unit_arrived':
        return '🚔';
      case 'perimeter_established':
        return '🔒';
      case 'gunfire_detected':
        return '💥';
      case 'command_note':
        return '📝';
      case 'resource_assigned':
        return '📦';
      default:
        return '📌';
    }
  };

  const filteredEvents = events.filter(event => {
    if (showPinnedOnly && !event.is_pinned) return false;
    if (filter !== 'all' && !event.event_type.includes(filter)) return false;
    if (searchTerm && !event.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !event.description.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  // Group events by date
  const eventsByDate = filteredEvents.reduce((acc, event) => {
    const date = formatDate(event.timestamp);
    if (!acc[date]) acc[date] = [];
    acc[date].push(event);
    return acc;
  }, {} as Record<string, TimelineEvent[]>);

  return (
    <div className="h-full flex flex-col">
      {/* Filters */}
      <Card className="bg-gray-800 border-gray-700 mb-4">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <Input
              placeholder="Search events..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64 bg-gray-700 border-gray-600 text-white"
            />
            <div className="flex gap-2">
              {eventTypes.map(type => (
                <Button
                  key={type.id}
                  variant={filter === type.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter(type.id)}
                  className={filter === type.id ? 'bg-blue-600' : ''}
                >
                  {type.label}
                </Button>
              ))}
            </div>
            <Button
              variant={showPinnedOnly ? 'default' : 'outline'}
              size="sm"
              onClick={() => setShowPinnedOnly(!showPinnedOnly)}
              className={showPinnedOnly ? 'bg-yellow-600' : ''}
            >
              Pinned Only
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Timeline */}
      <Card className="bg-gray-800 border-gray-700 flex-1 overflow-hidden">
        <CardHeader className="pb-2">
          <CardTitle className="text-white text-sm flex items-center justify-between">
            <span>Operational Timeline</span>
            <Badge variant="outline">{filteredEvents.length} events</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="overflow-y-auto h-[calc(100%-60px)]">
          {Object.entries(eventsByDate).map(([date, dateEvents]) => (
            <div key={date} className="mb-6">
              <div className="sticky top-0 bg-gray-800 py-2 z-10">
                <span className="text-xs font-medium text-gray-400 bg-gray-700 px-2 py-1 rounded">
                  {date}
                </span>
              </div>
              <div className="relative pl-6 border-l-2 border-gray-700 ml-2 space-y-4">
                {dateEvents.map(event => (
                  <div
                    key={event.id}
                    className={`relative p-4 rounded-lg border-l-4 ${getPriorityColor(event.priority)} bg-gray-700/50`}
                  >
                    {/* Timeline dot */}
                    <div className="absolute -left-[29px] top-4 w-4 h-4 rounded-full bg-gray-800 border-2 border-gray-600 flex items-center justify-center">
                      <span className="text-xs">{getEventIcon(event.event_type)}</span>
                    </div>

                    {/* Event content */}
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-gray-400">{formatTime(event.timestamp)}</span>
                          <Badge className={`text-xs ${getSourceColor(event.source)}`}>
                            {event.source}
                          </Badge>
                          {event.is_pinned && (
                            <Badge className="bg-yellow-600 text-xs">Pinned</Badge>
                          )}
                        </div>
                        <h4 className="text-sm font-medium text-white">{event.title}</h4>
                        <p className="text-xs text-gray-400 mt-1">{event.description}</p>
                      </div>
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
              </div>
            </div>
          ))}

          {filteredEvents.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">No events match your filters</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Source Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-xs">
        {sources.map(source => (
          <div key={source.id} className="flex items-center gap-1">
            <span className={`w-3 h-3 rounded ${source.color}`} />
            <span className="text-gray-400">{source.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

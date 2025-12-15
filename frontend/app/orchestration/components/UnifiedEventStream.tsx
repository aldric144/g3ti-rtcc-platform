'use client';

import React, { useState, useEffect, useRef } from 'react';

interface StreamEvent {
  id: string;
  type: string;
  source: string;
  category: string;
  priority: number;
  timestamp: string;
  title: string;
  summary: string;
  data: Record<string, unknown>;
  fused: boolean;
  source_count?: number;
}

export default function UnifiedEventStream() {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<StreamEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<StreamEvent | null>(null);
  const [filters, setFilters] = useState({
    category: 'all',
    priority: 'all',
    source: 'all',
    fusedOnly: false,
  });
  const [paused, setPaused] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const streamRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(() => {
      if (!paused) {
        fetchEvents();
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [paused]);

  useEffect(() => {
    applyFilters();
  }, [events, filters]);

  useEffect(() => {
    if (autoScroll && streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [filteredEvents, autoScroll]);

  const fetchEvents = async () => {
    try {
      const response = await fetch('/api/orchestration/events/history?limit=100');
      if (response.ok) {
        const data = await response.json();
        const mappedEvents: StreamEvent[] = (data.events || []).map((evt: Record<string, unknown>, index: number) => ({
          id: evt.event_id || `evt-${index}`,
          type: evt.event_type || 'unknown',
          source: evt._source || 'system',
          category: evt.category || 'general',
          priority: evt.priority || 5,
          timestamp: evt._ingested_at || new Date().toISOString(),
          title: evt.title || evt.event_type || 'Event',
          summary: evt.summary || '',
          data: evt,
          fused: false,
          source_count: 1,
        }));
        setEvents(mappedEvents);
      }
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...events];

    if (filters.category !== 'all') {
      filtered = filtered.filter((e) => e.category === filters.category);
    }
    if (filters.priority !== 'all') {
      filtered = filtered.filter((e) => e.priority === parseInt(filters.priority));
    }
    if (filters.source !== 'all') {
      filtered = filtered.filter((e) => e.source === filters.source);
    }
    if (filters.fusedOnly) {
      filtered = filtered.filter((e) => e.fused);
    }

    setFilteredEvents(filtered);
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return 'border-l-red-500 bg-red-900/20';
      case 2:
        return 'border-l-orange-500 bg-orange-900/20';
      case 3:
        return 'border-l-yellow-500 bg-yellow-900/20';
      case 4:
        return 'border-l-blue-500 bg-blue-900/20';
      default:
        return 'border-l-gray-500 bg-gray-900/20';
    }
  };

  const getPriorityLabel = (priority: number) => {
    switch (priority) {
      case 1:
        return 'CRITICAL';
      case 2:
        return 'HIGH';
      case 3:
        return 'MEDIUM';
      case 4:
        return 'LOW';
      default:
        return 'INFO';
    }
  };

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      incident: '🚨',
      alert: '⚠️',
      tactical: '🎯',
      officer: '👮',
      drone: '🚁',
      robot: '🤖',
      investigation: '🔍',
      threat: '⚡',
      emergency: '🆘',
      compliance: '📋',
      system: '⚙️',
      sensor: '📡',
      city: '🏙️',
      human_stability: '🧠',
      predictive: '📊',
      fusion: '🔗',
      cyber: '🔒',
      governance: '⚖️',
    };
    return icons[category] || '📌';
  };

  const uniqueSources = [...new Set(events.map((e) => e.source))];
  const uniqueCategories = [...new Set(events.map((e) => e.category))];

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-[#c9a227]">Unified Event Stream</h2>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded"
            />
            Auto-scroll
          </label>
          <button
            onClick={() => setPaused(!paused)}
            className={`px-3 py-1 rounded text-sm font-medium ${
              paused
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-yellow-600 hover:bg-yellow-700'
            }`}
          >
            {paused ? '▶ Resume' : '⏸ Pause'}
          </button>
          <button
            onClick={fetchEvents}
            className="px-3 py-1 bg-[#c9a227] text-[#0a1628] rounded text-sm font-medium hover:bg-[#d9b237]"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="flex gap-4 mb-4">
        <select
          value={filters.category}
          onChange={(e) => setFilters({ ...filters, category: e.target.value })}
          className="px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded-lg text-white text-sm"
        >
          <option value="all">All Categories</option>
          {uniqueCategories.map((cat) => (
            <option key={cat} value={cat}>
              {cat.replace(/_/g, ' ').toUpperCase()}
            </option>
          ))}
        </select>
        <select
          value={filters.priority}
          onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
          className="px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded-lg text-white text-sm"
        >
          <option value="all">All Priorities</option>
          <option value="1">Critical</option>
          <option value="2">High</option>
          <option value="3">Medium</option>
          <option value="4">Low</option>
          <option value="5">Info</option>
        </select>
        <select
          value={filters.source}
          onChange={(e) => setFilters({ ...filters, source: e.target.value })}
          className="px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded-lg text-white text-sm"
        >
          <option value="all">All Sources</option>
          {uniqueSources.map((src) => (
            <option key={src} value={src}>
              {src.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm px-3 py-2 bg-[#0a1628] border border-[#c9a227]/30 rounded-lg">
          <input
            type="checkbox"
            checked={filters.fusedOnly}
            onChange={(e) => setFilters({ ...filters, fusedOnly: e.target.checked })}
            className="rounded"
          />
          Fused Only
        </label>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Event Feed ({filteredEvents.length})</h3>
              <div className={`flex items-center gap-2 ${paused ? 'text-yellow-400' : 'text-green-400'}`}>
                <div className={`w-2 h-2 rounded-full ${paused ? 'bg-yellow-400' : 'bg-green-400 animate-pulse'}`}></div>
                <span className="text-xs">{paused ? 'PAUSED' : 'LIVE'}</span>
              </div>
            </div>

            <div
              ref={streamRef}
              className="space-y-2 max-h-[500px] overflow-y-auto"
            >
              {filteredEvents.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <p className="text-4xl mb-2">📡</p>
                  <p>No events match the current filters</p>
                </div>
              ) : (
                filteredEvents.map((event) => (
                  <div
                    key={event.id}
                    onClick={() => setSelectedEvent(event)}
                    className={`border-l-4 rounded-r-lg p-3 cursor-pointer transition-colors ${getPriorityColor(event.priority)} ${
                      selectedEvent?.id === event.id ? 'ring-1 ring-[#c9a227]' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getCategoryIcon(event.category)}</span>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{event.title}</span>
                            {event.fused && (
                              <span className="px-1.5 py-0.5 bg-purple-900/50 text-purple-400 rounded text-xs">
                                FUSED ({event.source_count})
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400">{event.summary || event.type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          event.priority === 1 ? 'bg-red-900/50 text-red-400' :
                          event.priority === 2 ? 'bg-orange-900/50 text-orange-400' :
                          event.priority === 3 ? 'bg-yellow-900/50 text-yellow-400' :
                          'bg-gray-900/50 text-gray-400'
                        }`}>
                          {getPriorityLabel(event.priority)}
                        </span>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                      <span>Source: {event.source}</span>
                      <span>•</span>
                      <span>Category: {event.category}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div>
          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20 mb-4">
            <h3 className="text-lg font-semibold mb-4">Event Details</h3>
            
            {selectedEvent ? (
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-gray-400">Event ID</label>
                  <p className="font-mono text-sm">{selectedEvent.id}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Type</label>
                  <p className="font-medium">{selectedEvent.type}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Source</label>
                  <p className="text-sm">{selectedEvent.source}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Category</label>
                  <p className="text-sm">{selectedEvent.category}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Priority</label>
                  <p className={`font-medium ${
                    selectedEvent.priority === 1 ? 'text-red-400' :
                    selectedEvent.priority === 2 ? 'text-orange-400' :
                    selectedEvent.priority === 3 ? 'text-yellow-400' : 'text-gray-400'
                  }`}>
                    {getPriorityLabel(selectedEvent.priority)}
                  </p>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Timestamp</label>
                  <p className="text-sm">{new Date(selectedEvent.timestamp).toLocaleString()}</p>
                </div>
                {selectedEvent.fused && (
                  <div>
                    <label className="text-xs text-gray-400">Fused Sources</label>
                    <p className="text-sm text-purple-400">{selectedEvent.source_count} events</p>
                  </div>
                )}
                <div className="border-t border-[#c9a227]/20 pt-4">
                  <label className="text-xs text-gray-400">Raw Data</label>
                  <pre className="mt-2 p-2 bg-[#1a2a4a] rounded text-xs overflow-auto max-h-[200px]">
                    {JSON.stringify(selectedEvent.data, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <p>Select an event to view details</p>
              </div>
            )}
          </div>

          <div className="bg-[#0a1628] rounded-lg p-4 border border-[#c9a227]/20">
            <h3 className="text-lg font-semibold mb-4">Stream Statistics</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Total Events</span>
                <span className="font-bold text-[#c9a227]">{events.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Filtered</span>
                <span className="font-bold text-blue-400">{filteredEvents.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Critical</span>
                <span className="font-bold text-red-400">
                  {events.filter((e) => e.priority === 1).length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Fused Events</span>
                <span className="font-bold text-purple-400">
                  {events.filter((e) => e.fused).length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Sources</span>
                <span className="font-bold text-green-400">{uniqueSources.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

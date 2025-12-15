'use client';

import { useState } from 'react';
import { AlertTriangle, Plus, Clock } from 'lucide-react';

interface MajorEvent {
  id: string;
  event_type: string;
  description: string;
  timestamp: string;
  recorded_by: string;
  case_number?: string;
}

const EVENT_TYPES = [
  '10-33 (Emergency)',
  'Priority 1 Assist',
  'Officer Down',
  'Shots Fired',
  'Pursuit',
  'Major Accident',
  'BOLO Hit',
  'Critical Incident',
  'Other',
];

interface MajorEventRecorderProps {
  refreshKey: number;
}

export function MajorEventRecorder({ refreshKey }: MajorEventRecorderProps) {
  const [events, setEvents] = useState<MajorEvent[]>([
    {
      id: '1',
      event_type: 'Shots Fired',
      description: 'ShotSpotter activation - Marina District. 3 rounds detected. Units 45, 47 responding.',
      timestamp: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
      recorded_by: 'Sgt. Johnson',
      case_number: 'RTCC-2025-00042',
    },
    {
      id: '2',
      event_type: 'Priority 1 Assist',
      description: 'Officer requested backup at Blue Heron & Congress. Suspect fleeing on foot.',
      timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
      recorded_by: 'Sgt. Johnson',
    },
  ]);

  const [showForm, setShowForm] = useState(false);
  const [newEvent, setNewEvent] = useState({
    event_type: '10-33 (Emergency)',
    description: '',
    case_number: '',
  });

  const handleAddEvent = (e: React.FormEvent) => {
    e.preventDefault();
    
    const event: MajorEvent = {
      id: Date.now().toString(),
      event_type: newEvent.event_type,
      description: newEvent.description,
      timestamp: new Date().toISOString(),
      recorded_by: 'admin',
      case_number: newEvent.case_number || undefined,
    };

    setEvents([event, ...events]);
    setNewEvent({ event_type: '10-33 (Emergency)', description: '', case_number: '' });
    setShowForm(false);
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="border-b border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            Major Events ({events.length})
          </h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-1 rounded-lg bg-amber-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-600"
          >
            <Plus className="h-4 w-4" />
            Record
          </button>
        </div>
      </div>

      {/* Add Form */}
      {showForm && (
        <div className="border-b border-gray-200 p-4 dark:border-gray-700">
          <form onSubmit={handleAddEvent} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                Event Type
              </label>
              <select
                value={newEvent.event_type}
                onChange={(e) => setNewEvent({ ...newEvent, event_type: e.target.value })}
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
              >
                {EVENT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                Description
              </label>
              <textarea
                value={newEvent.description}
                onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                rows={3}
                required
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
                Case Number (optional)
              </label>
              <input
                type="text"
                value={newEvent.case_number}
                onChange={(e) => setNewEvent({ ...newEvent, case_number: e.target.value })}
                placeholder="e.g., RTCC-2025-00042"
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-lg bg-amber-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-600"
              >
                Record Event
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Event List */}
      <div className="max-h-80 overflow-y-auto p-4">
        <div className="space-y-3">
          {events.map((event) => (
            <div
              key={event.id}
              className="rounded-lg border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-900/20"
            >
              <div className="flex items-center justify-between">
                <span className="rounded-full bg-amber-200 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-800 dark:text-amber-200">
                  {event.event_type}
                </span>
                {event.case_number && (
                  <span className="text-xs text-rtcc-primary">
                    {event.case_number}
                  </span>
                )}
              </div>
              <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
                {event.description}
              </p>
              <div className="mt-2 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                <span>{event.recorded_by}</span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

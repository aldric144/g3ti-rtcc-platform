'use client';

import { useState } from 'react';
import { Plus, Tag, Clock, User } from 'lucide-react';

interface EventNote {
  id: string;
  content: string;
  tag: string;
  timestamp: Date;
  author: string;
}

const TAG_COLORS: Record<string, string> = {
  OPS: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  'CAMERA ISSUE': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  PATROL: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  SUPERVISOR: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
  TECH: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
};

const AVAILABLE_TAGS = ['OPS', 'CAMERA ISSUE', 'PATROL', 'SUPERVISOR', 'TECH'];

export function AdminEventFeed() {
  const [notes, setNotes] = useState<EventNote[]>([
    {
      id: '1',
      content: 'Shift change completed. All systems operational.',
      tag: 'OPS',
      timestamp: new Date(Date.now() - 30 * 60000),
      author: 'Sgt. Johnson',
    },
    {
      id: '2',
      content: 'Camera 47 offline - maintenance scheduled for 1400.',
      tag: 'CAMERA ISSUE',
      timestamp: new Date(Date.now() - 60 * 60000),
      author: 'Tech Support',
    },
    {
      id: '3',
      content: 'Increased patrol requested for Blue Heron corridor.',
      tag: 'PATROL',
      timestamp: new Date(Date.now() - 90 * 60000),
      author: 'Lt. Martinez',
    },
  ]);

  const [showAddForm, setShowAddForm] = useState(false);
  const [newNote, setNewNote] = useState({ content: '', tag: 'OPS' });

  const handleAddNote = () => {
    if (!newNote.content.trim()) return;

    const note: EventNote = {
      id: Date.now().toString(),
      content: newNote.content,
      tag: newNote.tag,
      timestamp: new Date(),
      author: 'Admin',
    };

    setNotes([note, ...notes]);
    setNewNote({ content: '', tag: 'OPS' });
    setShowAddForm(false);
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Admin Event Feed
        </h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-1 rounded-lg bg-rtcc-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-rtcc-primary/90"
        >
          <Plus className="h-4 w-4" />
          Add Note
        </button>
      </div>

      {showAddForm && (
        <div className="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-600 dark:bg-gray-700">
          <textarea
            value={newNote.content}
            onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
            placeholder="Enter operational note..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
            rows={3}
          />
          <div className="mt-3 flex items-center justify-between">
            <select
              value={newNote.tag}
              onChange={(e) => setNewNote({ ...newNote, tag: e.target.value })}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800"
            >
              {AVAILABLE_TAGS.map((tag) => (
                <option key={tag} value={tag}>
                  {tag}
                </option>
              ))}
            </select>
            <div className="flex gap-2">
              <button
                onClick={() => setShowAddForm(false)}
                className="rounded-lg bg-gray-200 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={handleAddNote}
                className="rounded-lg bg-rtcc-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-rtcc-primary/90"
              >
                Add
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {notes.map((note) => (
          <div
            key={note.id}
            className="rounded-lg border border-gray-100 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-700/50"
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm text-gray-700 dark:text-gray-300">{note.content}</p>
              <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${TAG_COLORS[note.tag]}`}>
                {note.tag}
              </span>
            </div>
            <div className="mt-2 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                {note.author}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {note.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

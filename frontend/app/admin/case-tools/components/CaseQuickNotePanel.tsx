'use client';

import { useState } from 'react';
import { Save, Clock, User } from 'lucide-react';

interface CaseNote {
  id: string;
  case_id: string;
  content: string;
  is_rtcc_support: boolean;
  created_at: string;
  created_by: string;
}

export function CaseQuickNotePanel() {
  const [notes, setNotes] = useState<CaseNote[]>([
    {
      id: '1',
      case_id: 'RTCC-2025-00042',
      content: 'Camera footage reviewed - suspect vehicle identified heading northbound on US-1 at 14:32.',
      is_rtcc_support: true,
      created_at: new Date(Date.now() - 30 * 60000).toISOString(),
      created_by: 'admin',
    },
    {
      id: '2',
      case_id: 'RTCC-2025-00039',
      content: 'LPR hit confirmed - vehicle registered to POI from previous investigation.',
      is_rtcc_support: true,
      created_at: new Date(Date.now() - 60 * 60000).toISOString(),
      created_by: 'admin',
    },
  ]);

  const [newNote, setNewNote] = useState({
    case_id: '',
    content: '',
    is_rtcc_support: true,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const note: CaseNote = {
      id: Date.now().toString(),
      case_id: newNote.case_id || `TEMP-${Date.now()}`,
      content: newNote.content,
      is_rtcc_support: newNote.is_rtcc_support,
      created_at: new Date().toISOString(),
      created_by: 'admin',
    };

    setNotes([note, ...notes]);
    setNewNote({ case_id: '', content: '', is_rtcc_support: true });
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Add Note Form */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
          Quick Note Entry
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Case ID (optional)
            </label>
            <input
              type="text"
              value={newNote.case_id}
              onChange={(e) => setNewNote({ ...newNote, case_id: e.target.value })}
              placeholder="Leave blank for temporary ID"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Note Content
            </label>
            <textarea
              value={newNote.content}
              onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
              placeholder="Enter case note..."
              rows={4}
              required
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              checked={newNote.is_rtcc_support}
              onChange={(e) => setNewNote({ ...newNote, is_rtcc_support: e.target.checked })}
              className="rounded border-gray-300 dark:border-gray-600"
            />
            Mark as RTCC Support Note
          </label>
          <button
            type="submit"
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-rtcc-primary px-4 py-2 text-sm font-medium text-white hover:bg-rtcc-primary/90"
          >
            <Save className="h-4 w-4" />
            Save Note
          </button>
        </form>
      </div>

      {/* Recent Notes */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
          Recent Notes
        </h2>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {notes.map((note) => (
            <div
              key={note.id}
              className="rounded-lg border border-gray-100 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-700/50"
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-medium text-rtcc-primary">
                  {note.case_id}
                </span>
                {note.is_rtcc_support && (
                  <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900/30 dark:text-green-400">
                    RTCC Support
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300">{note.content}</p>
              <div className="mt-2 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  {note.created_by}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {new Date(note.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

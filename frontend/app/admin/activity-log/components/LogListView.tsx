'use client';

import { useState, useEffect } from 'react';
import { Clock, User, Tag, Archive, MoreVertical } from 'lucide-react';

interface LogEntry {
  id: string;
  log_type: string;
  priority: string;
  notes: string;
  tags: string[];
  editor: string;
  created_at: string;
  archived: boolean;
}

const PRIORITY_COLORS: Record<string, string> = {
  low: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  medium: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  high: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  critical: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
};

const TYPE_LABELS: Record<string, string> = {
  incident: 'Incident',
  shotspotter: 'ShotSpotter',
  lpr: 'LPR',
  camera_alert: 'Camera Alert',
  cad_assist: 'CAD Assist',
  patrol_request: 'Patrol Request',
  case_support: 'Case Support',
  supervisor_notice: 'Supervisor Notice',
};

interface LogListViewProps {
  searchParams: {
    keyword: string;
    logType: string;
    priority: string;
    includeArchived: boolean;
  };
  refreshKey: number;
}

export function LogListView({ searchParams, refreshKey }: LogListViewProps) {
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: '1',
      log_type: 'incident',
      priority: 'high',
      notes: 'Armed robbery reported at 1200 Blue Heron Blvd. Units 45 and 47 dispatched. RTCC providing camera support.',
      tags: ['robbery', 'priority'],
      editor: 'admin',
      created_at: new Date(Date.now() - 30 * 60000).toISOString(),
      archived: false,
    },
    {
      id: '2',
      log_type: 'shotspotter',
      priority: 'critical',
      notes: 'ShotSpotter activation - 3 rounds detected near Marina District. Patrol units notified.',
      tags: ['shots-fired', 'marina'],
      editor: 'admin',
      created_at: new Date(Date.now() - 60 * 60000).toISOString(),
      archived: false,
    },
    {
      id: '3',
      log_type: 'lpr',
      priority: 'medium',
      notes: 'Stolen vehicle hit - FL tag ABC123 - Last seen heading northbound on US-1.',
      tags: ['stolen-vehicle', 'lpr-hit'],
      editor: 'admin',
      created_at: new Date(Date.now() - 90 * 60000).toISOString(),
      archived: false,
    },
    {
      id: '4',
      log_type: 'patrol_request',
      priority: 'low',
      notes: 'Community request for increased patrol presence near Riviera Beach Elementary during school hours.',
      tags: ['community', 'school'],
      editor: 'admin',
      created_at: new Date(Date.now() - 120 * 60000).toISOString(),
      archived: false,
    },
  ]);

  const filteredLogs = logs.filter(log => {
    if (searchParams.keyword && !log.notes.toLowerCase().includes(searchParams.keyword.toLowerCase())) {
      return false;
    }
    if (searchParams.logType && log.log_type !== searchParams.logType) {
      return false;
    }
    if (searchParams.priority && log.priority !== searchParams.priority) {
      return false;
    }
    if (!searchParams.includeArchived && log.archived) {
      return false;
    }
    return true;
  });

  return (
    <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="border-b border-gray-200 px-6 py-4 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Log Entries ({filteredLogs.length})
        </h2>
      </div>
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {filteredLogs.map((log) => (
          <div key={log.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                    {TYPE_LABELS[log.log_type] || log.log_type}
                  </span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${PRIORITY_COLORS[log.priority]}`}>
                    {log.priority.toUpperCase()}
                  </span>
                  {log.archived && (
                    <span className="flex items-center gap-1 text-xs text-gray-500">
                      <Archive className="h-3 w-3" />
                      Archived
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300">{log.notes}</p>
                <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                  <span className="flex items-center gap-1">
                    <User className="h-3 w-3" />
                    {log.editor}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                  {log.tags.length > 0 && (
                    <span className="flex items-center gap-1">
                      <Tag className="h-3 w-3" />
                      {log.tags.join(', ')}
                    </span>
                  )}
                </div>
              </div>
              <button className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700">
                <MoreVertical className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
        {filteredLogs.length === 0 && (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            No log entries found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
}

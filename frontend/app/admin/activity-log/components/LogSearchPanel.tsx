'use client';

import { Search, Filter } from 'lucide-react';

const LOG_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'incident', label: 'Incident' },
  { value: 'shotspotter', label: 'ShotSpotter' },
  { value: 'lpr', label: 'LPR' },
  { value: 'camera_alert', label: 'Camera Alert' },
  { value: 'cad_assist', label: 'CAD Assist' },
  { value: 'patrol_request', label: 'Patrol Request' },
  { value: 'case_support', label: 'Case Support' },
  { value: 'supervisor_notice', label: 'Supervisor Notice' },
];

const PRIORITIES = [
  { value: '', label: 'All Priorities' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

interface LogSearchParams {
  keyword: string;
  logType: string;
  priority: string;
  includeArchived: boolean;
}

interface LogSearchPanelProps {
  searchParams: LogSearchParams;
  onSearchChange: (params: LogSearchParams) => void;
}

export function LogSearchPanel({ searchParams, onSearchChange }: LogSearchPanelProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
      <div className="flex flex-wrap items-center gap-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={searchParams.keyword}
            onChange={(e) => onSearchChange({ ...searchParams, keyword: e.target.value })}
            placeholder="Search logs..."
            className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-sm dark:border-gray-600 dark:bg-gray-700"
          />
        </div>
        <select
          value={searchParams.logType}
          onChange={(e) => onSearchChange({ ...searchParams, logType: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
        >
          {LOG_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        <select
          value={searchParams.priority}
          onChange={(e) => onSearchChange({ ...searchParams, priority: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700"
        >
          {PRIORITIES.map((priority) => (
            <option key={priority.value} value={priority.value}>
              {priority.label}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input
            type="checkbox"
            checked={searchParams.includeArchived}
            onChange={(e) => onSearchChange({ ...searchParams, includeArchived: e.target.checked })}
            className="rounded border-gray-300 dark:border-gray-600"
          />
          Include Archived
        </label>
      </div>
    </div>
  );
}

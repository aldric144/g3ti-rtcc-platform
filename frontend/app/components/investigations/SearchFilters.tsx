'use client';

import { useState } from 'react';

/**
 * Search filters component for investigations.
 */
export function SearchFilters() {
  const [entityTypes, setEntityTypes] = useState({
    person: true,
    vehicle: true,
    incident: true,
    address: true,
  });

  const [dateRange, setDateRange] = useState({
    from: '',
    to: '',
  });

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {/* Entity types */}
      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Entity Types
        </label>
        <div className="space-y-2">
          {Object.entries(entityTypes).map(([type, checked]) => (
            <label key={type} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={checked}
                onChange={(e) =>
                  setEntityTypes((prev) => ({
                    ...prev,
                    [type]: e.target.checked,
                  }))
                }
                className="rounded border-gray-300 text-rtcc-accent focus:ring-rtcc-accent"
              />
              <span className="text-sm capitalize text-gray-600 dark:text-gray-400">{type}s</span>
            </label>
          ))}
        </div>
      </div>

      {/* Date range */}
      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Date Range
        </label>
        <div className="space-y-2">
          <input
            type="date"
            value={dateRange.from}
            onChange={(e) => setDateRange((prev) => ({ ...prev, from: e.target.value }))}
            className="input"
            placeholder="From"
          />
          <input
            type="date"
            value={dateRange.to}
            onChange={(e) => setDateRange((prev) => ({ ...prev, to: e.target.value }))}
            className="input"
            placeholder="To"
          />
        </div>
      </div>

      {/* Quick filters */}
      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Quick Filters
        </label>
        <div className="flex flex-wrap gap-2">
          <button className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300">
            Last 24 hours
          </button>
          <button className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300">
            Last 7 days
          </button>
          <button className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300">
            Last 30 days
          </button>
        </div>
      </div>
    </div>
  );
}

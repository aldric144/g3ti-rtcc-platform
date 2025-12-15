'use client';

import { useState } from 'react';
import { FileText, Search, Download, Plus, Filter } from 'lucide-react';
import { LogEntryForm } from './components/LogEntryForm';
import { LogListView } from './components/LogListView';
import { LogSearchPanel } from './components/LogSearchPanel';
import { LogExportButton } from './components/LogExportButton';

export default function ActivityLogPage() {
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchParams, setSearchParams] = useState({
    keyword: '',
    logType: '',
    priority: '',
    includeArchived: false,
  });
  const [refreshKey, setRefreshKey] = useState(0);

  const handleLogCreated = () => {
    setShowAddForm(false);
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Daily Activity Log
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            RTCC Logbook - All entries are audited for CJIS compliance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <LogExportButton searchParams={searchParams} />
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 rounded-lg bg-rtcc-primary px-4 py-2 text-sm font-medium text-white hover:bg-rtcc-primary/90"
          >
            <Plus className="h-4 w-4" />
            New Entry
          </button>
        </div>
      </div>

      {/* Search Panel */}
      <LogSearchPanel 
        searchParams={searchParams} 
        onSearchChange={setSearchParams} 
      />

      {/* Add Form */}
      {showAddForm && (
        <LogEntryForm 
          onCancel={() => setShowAddForm(false)} 
          onSuccess={handleLogCreated}
        />
      )}

      {/* Log List */}
      <LogListView 
        searchParams={searchParams} 
        refreshKey={refreshKey}
      />
    </div>
  );
}

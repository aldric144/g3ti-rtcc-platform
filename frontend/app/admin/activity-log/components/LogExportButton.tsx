'use client';

import { useState } from 'react';
import { Download, FileJson, FileSpreadsheet } from 'lucide-react';

interface LogExportButtonProps {
  searchParams: {
    keyword: string;
    logType: string;
    priority: string;
    includeArchived: boolean;
  };
}

export function LogExportButton({ searchParams }: LogExportButtonProps) {
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const params = new URLSearchParams();
      params.set('format', format);
      if (searchParams.keyword) params.set('keyword', searchParams.keyword);
      if (searchParams.logType) params.set('log_type', searchParams.logType);
      if (searchParams.priority) params.set('priority', searchParams.priority);
      params.set('include_archived', searchParams.includeArchived.toString());

      const response = await fetch(`/api/v1/api/admin/logs/export?${params}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `activity_logs.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
    setShowMenu(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
      >
        <Download className="h-4 w-4" />
        Export
      </button>
      {showMenu && (
        <div className="absolute right-0 top-full mt-1 w-40 rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800">
          <button
            onClick={() => handleExport('json')}
            className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            <FileJson className="h-4 w-4" />
            Export JSON
          </button>
          <button
            onClick={() => handleExport('csv')}
            className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            <FileSpreadsheet className="h-4 w-4" />
            Export CSV
          </button>
        </div>
      )}
    </div>
  );
}

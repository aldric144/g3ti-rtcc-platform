'use client';

import { useState } from 'react';
import { Download, FileText, FileJson, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface CaseExportProps {
  caseId: string;
  caseNumber?: string;
}

/**
 * Case Export component for exporting case reports.
 * 
 * Supports:
 * - PDF export with full case summary
 * - JSON export for data integration
 */
export function CaseExport({ caseId, caseNumber }: CaseExportProps) {
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isExportingJson, setIsExportingJson] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const exportPdf = async () => {
    setIsExportingPdf(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`/api/investigations/case/${caseId}/export/pdf`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to export PDF');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `case_${caseNumber || caseId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccess('PDF exported successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export PDF');
    } finally {
      setIsExportingPdf(false);
    }
  };

  const exportJson = async () => {
    setIsExportingJson(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`/api/investigations/case/${caseId}/export/json`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to export JSON');
      }

      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `case_${caseNumber || caseId}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccess('JSON exported successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export JSON');
    } finally {
      setIsExportingJson(false);
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <Download className="h-5 w-5" />
        Export Case Report
      </h3>

      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Export the complete case file including summary, evidence, timeline, and recommendations.
      </p>

      <div className="grid grid-cols-2 gap-4">
        {/* PDF Export */}
        <button
          onClick={exportPdf}
          disabled={isExportingPdf || isExportingJson}
          className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isExportingPdf ? (
            <Loader2 className="h-8 w-8 animate-spin text-red-500 mb-2" />
          ) : (
            <FileText className="h-8 w-8 text-red-500 mb-2" />
          )}
          <span className="font-medium text-gray-900 dark:text-white">
            {isExportingPdf ? 'Generating...' : 'Export PDF'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Full formatted report
          </span>
        </button>

        {/* JSON Export */}
        <button
          onClick={exportJson}
          disabled={isExportingPdf || isExportingJson}
          className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isExportingJson ? (
            <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-2" />
          ) : (
            <FileJson className="h-8 w-8 text-blue-500 mb-2" />
          )}
          <span className="font-medium text-gray-900 dark:text-white">
            {isExportingJson ? 'Generating...' : 'Export JSON'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Machine-readable data
          </span>
        </button>
      </div>

      {/* Status messages */}
      {error && (
        <div className="mt-4 flex items-center gap-2 text-red-600 dark:text-red-400 text-sm">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {success && (
        <div className="mt-4 flex items-center gap-2 text-green-600 dark:text-green-400 text-sm">
          <CheckCircle className="h-4 w-4" />
          {success}
        </div>
      )}

      {/* Export info */}
      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <p className="text-xs text-gray-600 dark:text-gray-400">
          <strong>PDF Export includes:</strong> Case summary, risk assessment, suspects, vehicles, 
          linked incidents, timeline, evidence list, investigative leads, and recommendations.
        </p>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
          <strong>JSON Export includes:</strong> All case data in structured format for integration 
          with external systems or further analysis.
        </p>
      </div>
    </div>
  );
}

export default CaseExport;

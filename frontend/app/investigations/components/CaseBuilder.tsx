'use client';

import { useState } from 'react';
import { Plus, Loader2, AlertCircle, CheckCircle } from 'lucide-react';

interface CaseBuilderProps {
  onCaseCreated?: (caseData: any) => void;
}

/**
 * Case Builder component for auto-creating investigation cases.
 *
 * Allows users to create cases from:
 * - Incident IDs
 * - Suspect IDs
 * - Custom titles
 */
export function CaseBuilder({ onCaseCreated }: CaseBuilderProps) {
  const [incidentId, setIncidentId] = useState('');
  const [suspectId, setSuspectId] = useState('');
  const [title, setTitle] = useState('');
  const [isBuilding, setIsBuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleBuildCase = async () => {
    if (!incidentId && !suspectId) {
      setError('Please provide either an incident ID or suspect ID');
      return;
    }

    setIsBuilding(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/investigations/case/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          incident_id: incidentId || null,
          suspect_id: suspectId || null,
          title: title || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create case');
      }

      const caseData = await response.json();
      setSuccess(`Case ${caseData.case_number} created successfully`);

      // Clear form
      setIncidentId('');
      setSuspectId('');
      setTitle('');

      if (onCaseCreated) {
        onCaseCreated(caseData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create case');
    } finally {
      setIsBuilding(false);
    }
  };

  return (
    <div className="card">
      <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">Auto-Build Case</h3>

      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Incident ID
          </label>
          <input
            type="text"
            value={incidentId}
            onChange={(e) => setIncidentId(e.target.value)}
            placeholder="Enter incident ID (e.g., INC12345)"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          />
        </div>

        <div className="text-center text-sm text-gray-500 dark:text-gray-400">- OR -</div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Suspect ID
          </label>
          <input
            type="text"
            value={suspectId}
            onChange={(e) => setSuspectId(e.target.value)}
            placeholder="Enter suspect entity ID"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Case Title (Optional)
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter custom case title"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          />
        </div>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        {success && (
          <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
            <CheckCircle className="h-4 w-4" />
            {success}
          </div>
        )}

        <button
          onClick={handleBuildCase}
          disabled={isBuilding || (!incidentId && !suspectId)}
          className="btn-primary flex w-full items-center justify-center gap-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isBuilding ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Building Case...
            </>
          ) : (
            <>
              <Plus className="h-4 w-4" />
              Build Case
            </>
          )}
        </button>
      </div>

      <div className="mt-4 rounded-lg bg-blue-50 p-3 dark:bg-blue-900/20">
        <p className="text-sm text-blue-700 dark:text-blue-300">
          The case builder will automatically:
        </p>
        <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-blue-600 dark:text-blue-400">
          <li>Link related incidents</li>
          <li>Identify suspects and vehicles</li>
          <li>Collect evidence from all sources</li>
          <li>Generate timeline</li>
          <li>Calculate risk assessment</li>
          <li>Create investigative leads</li>
        </ul>
      </div>
    </div>
  );
}

export default CaseBuilder;

'use client';

import { useState } from 'react';
import { Link2, Loader2, AlertCircle, X, Plus } from 'lucide-react';

interface LinkageResult {
  linked_incidents: any[];
  confidence_scores: Record<string, number>;
  explanations: string[];
}

interface IncidentLinkerProps {
  onLinkageFound?: (result: LinkageResult) => void;
}

/**
 * Incident Linker component for finding related incidents.
 * 
 * Analyzes incidents for relationships including:
 * - Temporal proximity
 * - Geographic proximity
 * - Entity overlap
 * - Narrative similarity
 * - Ballistic matches
 * - Vehicle recurrence
 */
export function IncidentLinker({ onLinkageFound }: IncidentLinkerProps) {
  const [incidentIds, setIncidentIds] = useState<string[]>(['']);
  const [isLinking, setIsLinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<LinkageResult | null>(null);

  const addIncidentField = () => {
    setIncidentIds([...incidentIds, '']);
  };

  const removeIncidentField = (index: number) => {
    if (incidentIds.length > 1) {
      setIncidentIds(incidentIds.filter((_, i) => i !== index));
    }
  };

  const updateIncidentId = (index: number, value: string) => {
    const updated = [...incidentIds];
    updated[index] = value;
    setIncidentIds(updated);
  };

  const handleLink = async () => {
    const validIds = incidentIds.filter(id => id.trim() !== '');
    
    if (validIds.length === 0) {
      setError('Please provide at least one incident ID');
      return;
    }

    setIsLinking(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/investigations/link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          incident_ids: validIds,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to link incidents');
      }

      const linkageResult = await response.json();
      setResult(linkageResult);

      if (onLinkageFound) {
        onLinkageFound(linkageResult);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to link incidents');
    } finally {
      setIsLinking(false);
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    if (score >= 0.4) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Link Incidents
      </h3>
      
      <div className="space-y-4">
        <div className="space-y-2">
          {incidentIds.map((id, index) => (
            <div key={index} className="flex items-center gap-2">
              <input
                type="text"
                value={id}
                onChange={(e) => updateIncidentId(index, e.target.value)}
                placeholder={`Incident ID ${index + 1}`}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              />
              {incidentIds.length > 1 && (
                <button
                  onClick={() => removeIncidentField(index)}
                  className="p-2 text-gray-400 hover:text-red-500"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}
        </div>

        <button
          onClick={addIncidentField}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          <Plus className="h-3 w-3" />
          Add another incident
        </button>

        {error && (
          <div className="flex items-center gap-2 text-red-600 dark:text-red-400 text-sm">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        <button
          onClick={handleLink}
          disabled={isLinking}
          className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLinking ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Link2 className="h-4 w-4" />
              Find Linkages
            </>
          )}
        </button>
      </div>

      {result && (
        <div className="mt-6 space-y-4">
          <h4 className="font-medium text-gray-900 dark:text-white">
            Found {result.linked_incidents.length} Linked Incidents
          </h4>

          {result.linked_incidents.length > 0 && (
            <div className="space-y-2">
              {result.linked_incidents.map((incident, index) => (
                <div
                  key={index}
                  className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {incident.incident_id}
                    </span>
                    {result.confidence_scores[incident.incident_id] !== undefined && (
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(result.confidence_scores[incident.incident_id])}`}>
                        {(result.confidence_scores[incident.incident_id] * 100).toFixed(0)}% confidence
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {incident.incident_type} - {incident.summary || 'No summary'}
                  </p>
                </div>
              ))}
            </div>
          )}

          {result.explanations.length > 0 && (
            <div className="mt-4">
              <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Linkage Explanations
              </h5>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                {result.explanations.slice(0, 5).map((explanation, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-blue-500 mt-1">-</span>
                    {explanation}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default IncidentLinker;

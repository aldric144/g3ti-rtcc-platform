'use client';

import React, { useState, useEffect } from 'react';

interface Hypothesis {
  hypothesis_id: string;
  title: string;
  description: string;
  hypothesis_type: string;
  status: string;
  confidence_score: number;
  supporting_evidence: number;
  contradictions: number;
}

interface Contradiction {
  contradiction_id: string;
  hypothesis_id: string;
  contradiction_type: string;
  description: string;
  severity: string;
}

interface Props {
  caseId: string | null;
}

export default function TheoryWorkbench({ caseId }: Props) {
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [contradictions, setContradictions] = useState<Contradiction[]>([]);
  const [selectedHypothesis, setSelectedHypothesis] = useState<Hypothesis | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (caseId) {
      loadHypotheses();
    }
  }, [caseId]);

  const loadHypotheses = async () => {
    setLoading(true);
    setTimeout(() => {
      setHypotheses([
        {
          hypothesis_id: 'hyp-001',
          title: 'Domestic Dispute Escalation',
          description: 'The incident resulted from an escalating domestic dispute between the victim and a known associate.',
          hypothesis_type: 'primary_suspect',
          status: 'active',
          confidence_score: 0.78,
          supporting_evidence: 5,
          contradictions: 1,
        },
        {
          hypothesis_id: 'hyp-002',
          title: 'Burglary Gone Wrong',
          description: 'The perpetrator entered with intent to burglarize but was interrupted by the victim.',
          hypothesis_type: 'crime_scenario',
          status: 'active',
          confidence_score: 0.62,
          supporting_evidence: 3,
          contradictions: 2,
        },
        {
          hypothesis_id: 'hyp-003',
          title: 'Targeted Attack',
          description: 'The victim was specifically targeted by an unknown assailant with premeditation.',
          hypothesis_type: 'crime_scenario',
          status: 'investigating',
          confidence_score: 0.45,
          supporting_evidence: 2,
          contradictions: 3,
        },
      ]);
      setContradictions([
        {
          contradiction_id: 'con-001',
          hypothesis_id: 'hyp-001',
          contradiction_type: 'timeline',
          description: 'Witness places suspect at different location during incident window',
          severity: 'moderate',
        },
        {
          contradiction_id: 'con-002',
          hypothesis_id: 'hyp-002',
          contradiction_type: 'evidence',
          description: 'No signs of forced entry at any access point',
          severity: 'high',
        },
        {
          contradiction_id: 'con-003',
          hypothesis_id: 'hyp-002',
          contradiction_type: 'behavioral',
          description: 'Nothing of value was taken despite opportunity',
          severity: 'moderate',
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const generateNewHypotheses = async () => {
    setGenerating(true);
    setTimeout(() => {
      setGenerating(false);
    }, 2000);
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-900/50 text-green-400',
      investigating: 'bg-yellow-900/50 text-yellow-400',
      rejected: 'bg-red-900/50 text-red-400',
      confirmed: 'bg-blue-900/50 text-blue-400',
    };
    return colors[status] || 'bg-gray-700 text-gray-400';
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      low: 'text-green-400',
      moderate: 'text-yellow-400',
      high: 'text-orange-400',
      critical: 'text-red-400',
    };
    return colors[severity] || 'text-gray-400';
  };

  if (!caseId) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-800 rounded-lg">
        <p className="text-gray-400">Select a case to view theory workbench</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Theory Workbench</h2>
        <button
          onClick={generateNewHypotheses}
          disabled={generating}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-sm flex items-center gap-2"
        >
          {generating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Generating...
            </>
          ) : (
            <>Generate New Hypotheses</>
          )}
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 space-y-4">
            <h3 className="font-medium text-gray-300">Active Hypotheses</h3>
            {hypotheses.map((hyp) => (
              <div
                key={hyp.hypothesis_id}
                className={`bg-gray-800 rounded-lg p-4 cursor-pointer border-2 transition-colors ${
                  selectedHypothesis?.hypothesis_id === hyp.hypothesis_id
                    ? 'border-blue-500'
                    : 'border-transparent hover:border-gray-600'
                }`}
                onClick={() => setSelectedHypothesis(hyp)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-medium">{hyp.title}</h4>
                    <span className="text-xs text-gray-400 capitalize">
                      {hyp.hypothesis_type.replace('_', ' ')}
                    </span>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(hyp.status)}`}>
                    {hyp.status}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-3">{hyp.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-green-400">
                      {hyp.supporting_evidence} supporting
                    </span>
                    <span className="text-red-400">
                      {hyp.contradictions} contradictions
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-400">Confidence:</span>
                    <div className="w-24 bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${hyp.confidence_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-blue-400">
                      {(hyp.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="space-y-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3">Hypothesis Ranking</h3>
              <div className="space-y-2">
                {[...hypotheses]
                  .sort((a, b) => b.confidence_score - a.confidence_score)
                  .map((hyp, index) => (
                    <div
                      key={hyp.hypothesis_id}
                      className="flex items-center gap-3 text-sm"
                    >
                      <span className="w-6 h-6 flex items-center justify-center bg-gray-700 rounded-full text-xs">
                        {index + 1}
                      </span>
                      <span className="flex-1 truncate">{hyp.title}</span>
                      <span className="text-blue-400">
                        {(hyp.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3">Contradictions</h3>
              <div className="space-y-3">
                {contradictions
                  .filter(
                    (c) =>
                      !selectedHypothesis ||
                      c.hypothesis_id === selectedHypothesis.hypothesis_id
                  )
                  .map((con) => (
                    <div
                      key={con.contradiction_id}
                      className="bg-gray-700 rounded p-3"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-400 capitalize">
                          {con.contradiction_type}
                        </span>
                        <span className={`text-xs ${getSeverityColor(con.severity)}`}>
                          {con.severity}
                        </span>
                      </div>
                      <p className="text-sm">{con.description}</p>
                    </div>
                  ))}
              </div>
            </div>

            {selectedHypothesis && (
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-medium mb-3">Actions</h3>
                <div className="space-y-2">
                  <button className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm">
                    Mark as Confirmed
                  </button>
                  <button className="w-full px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-sm">
                    Request More Evidence
                  </button>
                  <button className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-sm">
                    Reject Hypothesis
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState } from 'react';

interface MoralAssessment {
  assessment_id: string;
  action_type: string;
  decision: string;
  reasoning_summary: string;
  community_impact_score: number;
  risk_to_community: number;
  required_approvals: string[];
  conditions: string[];
  confidence: number;
  assessment_hash: string;
}

interface ReasoningCapsule {
  capsule_id: string;
  action_type: string;
  decision: string;
  key_factors: string[];
  constraints_applied: string[];
  ethical_principles: string[];
  human_readable_explanation: string;
  confidence: number;
}

export default function EthicalReasoningConsole() {
  const [actionType, setActionType] = useState('');
  const [actionDescription, setActionDescription] = useState('');
  const [requesterId, setRequesterId] = useState('');
  const [assessment, setAssessment] = useState<MoralAssessment | null>(null);
  const [reasoning, setReasoning] = useState<ReasoningCapsule | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAssess = async () => {
    if (!actionType || !actionDescription || !requesterId) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/moral/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_type: actionType,
          action_description: actionDescription,
          requester_id: requesterId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAssessment(data);

        const reasoningResponse = await fetch('/api/moral/reason', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action_type: actionType,
            context: { description: actionDescription },
          }),
        });

        if (reasoningResponse.ok) {
          const reasoningData = await reasoningResponse.json();
          setReasoning(reasoningData);
        }
      } else {
        setError('Failed to perform assessment');
      }
    } catch (err) {
      setError('Error connecting to moral compass service');
    } finally {
      setLoading(false);
    }
  };

  const getDecisionColor = (decision: string) => {
    switch (decision.toLowerCase()) {
      case 'allow':
        return 'text-green-400 bg-green-500/20';
      case 'allow_with_caution':
        return 'text-yellow-400 bg-yellow-500/20';
      case 'human_approval_needed':
        return 'text-orange-400 bg-orange-500/20';
      case 'deny':
        return 'text-red-400 bg-red-500/20';
      default:
        return 'text-slate-400 bg-slate-500/20';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-red-400';
    if (score >= 50) return 'text-orange-400';
    if (score >= 25) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
        <h2 className="text-xl font-semibold text-gold-400 mb-4 flex items-center gap-2">
          <span>⚖️</span> Ethical Assessment Console
        </h2>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-slate-400 text-sm mb-1">Action Type</label>
            <select
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-gold-500 focus:outline-none"
            >
              <option value="">Select action type...</option>
              <option value="arrest">Arrest</option>
              <option value="detention">Detention</option>
              <option value="search">Search</option>
              <option value="surveillance">Surveillance</option>
              <option value="use_of_force">Use of Force</option>
              <option value="traffic_stop">Traffic Stop</option>
              <option value="interrogation">Interrogation</option>
              <option value="predictive_targeting">Predictive Targeting</option>
              <option value="resource_allocation">Resource Allocation</option>
              <option value="community_engagement">Community Engagement</option>
            </select>
          </div>
          <div>
            <label className="block text-slate-400 text-sm mb-1">Requester ID</label>
            <input
              type="text"
              value={requesterId}
              onChange={(e) => setRequesterId(e.target.value)}
              placeholder="Officer/System ID"
              className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-gold-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-slate-400 text-sm mb-1">Action Description</label>
          <textarea
            value={actionDescription}
            onChange={(e) => setActionDescription(e.target.value)}
            placeholder="Describe the action to be assessed..."
            rows={3}
            className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-gold-500 focus:outline-none"
          />
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded text-red-400">
            {error}
          </div>
        )}

        <button
          onClick={handleAssess}
          disabled={loading}
          className="w-full bg-gold-500 hover:bg-gold-600 text-slate-900 font-semibold py-2 px-4 rounded transition-colors disabled:opacity-50"
        >
          {loading ? 'Assessing...' : 'Perform Ethical Assessment'}
        </button>
      </div>

      {assessment && (
        <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
          <h3 className="text-lg font-semibold text-gold-400 mb-4">Assessment Result</h3>

          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-slate-700/50 rounded p-4">
              <div className="text-slate-400 text-sm mb-1">Decision</div>
              <div className={`text-lg font-bold px-3 py-1 rounded inline-block ${getDecisionColor(assessment.decision)}`}>
                {assessment.decision.replace(/_/g, ' ').toUpperCase()}
              </div>
            </div>
            <div className="bg-slate-700/50 rounded p-4">
              <div className="text-slate-400 text-sm mb-1">Community Impact</div>
              <div className={`text-2xl font-bold ${getScoreColor(assessment.community_impact_score)}`}>
                {assessment.community_impact_score.toFixed(0)}%
              </div>
            </div>
            <div className="bg-slate-700/50 rounded p-4">
              <div className="text-slate-400 text-sm mb-1">Risk to Community</div>
              <div className={`text-2xl font-bold ${getScoreColor(assessment.risk_to_community)}`}>
                {assessment.risk_to_community.toFixed(0)}%
              </div>
            </div>
          </div>

          <div className="bg-slate-700/50 rounded p-4 mb-4">
            <div className="text-slate-400 text-sm mb-2">Reasoning Summary</div>
            <p className="text-white">{assessment.reasoning_summary}</p>
          </div>

          {assessment.required_approvals.length > 0 && (
            <div className="bg-orange-500/10 border border-orange-500/30 rounded p-4 mb-4">
              <div className="text-orange-400 text-sm font-semibold mb-2">Required Approvals</div>
              <ul className="list-disc list-inside text-orange-300">
                {assessment.required_approvals.map((approval, idx) => (
                  <li key={idx}>{approval}</li>
                ))}
              </ul>
            </div>
          )}

          {assessment.conditions.length > 0 && (
            <div className="bg-slate-700/50 rounded p-4">
              <div className="text-slate-400 text-sm mb-2">Conditions</div>
              <ul className="list-disc list-inside text-slate-300">
                {assessment.conditions.map((condition, idx) => (
                  <li key={idx}>{condition}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
            <span>Assessment ID: {assessment.assessment_id}</span>
            <span>Confidence: {(assessment.confidence * 100).toFixed(0)}%</span>
            <span>Hash: {assessment.assessment_hash}</span>
          </div>
        </div>
      )}

      {reasoning && (
        <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
          <h3 className="text-lg font-semibold text-gold-400 mb-4">Reasoning Explanation</h3>

          <div className="bg-slate-700/50 rounded p-4 mb-4">
            <p className="text-white">{reasoning.human_readable_explanation}</p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="text-slate-400 text-sm mb-2">Key Factors</div>
              <ul className="space-y-1">
                {reasoning.key_factors.map((factor, idx) => (
                  <li key={idx} className="text-slate-300 text-sm flex items-center gap-2">
                    <span className="text-gold-400">•</span> {factor}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <div className="text-slate-400 text-sm mb-2">Legal Constraints</div>
              <ul className="space-y-1">
                {reasoning.constraints_applied.map((constraint, idx) => (
                  <li key={idx} className="text-slate-300 text-sm flex items-center gap-2">
                    <span className="text-blue-400">•</span> {constraint}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <div className="text-slate-400 text-sm mb-2">Ethical Principles</div>
              <ul className="space-y-1">
                {reasoning.ethical_principles.map((principle, idx) => (
                  <li key={idx} className="text-slate-300 text-sm flex items-center gap-2">
                    <span className="text-purple-400">•</span> {principle}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useState, useEffect } from 'react';

interface InvestigationResult {
  result_id: string;
  case_id: string;
  status: string;
  suspects_count: number;
  theories_count: number;
  linked_cases_count: number;
  confidence_score: number;
  processing_time_seconds: number;
  report_id: string | null;
}

interface TriageItem {
  triage_id: string;
  case_id: string;
  priority: string;
  score: number;
  reasons: string[];
  recommended_actions: string[];
}

interface Props {
  caseId: string | null;
}

export default function AutoInvestigatorConsole({ caseId }: Props) {
  const [investigations, setInvestigations] = useState<InvestigationResult[]>([]);
  const [triageItems, setTriageItems] = useState<TriageItem[]>([]);
  const [activeTab, setActiveTab] = useState<'investigate' | 'triage'>('investigate');
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setTimeout(() => {
      setInvestigations([
        {
          result_id: 'inv-001',
          case_id: 'case-001',
          status: 'completed',
          suspects_count: 2,
          theories_count: 3,
          linked_cases_count: 1,
          confidence_score: 0.78,
          processing_time_seconds: 45.2,
          report_id: 'rpt-001',
        },
        {
          result_id: 'inv-002',
          case_id: 'case-002',
          status: 'completed',
          suspects_count: 1,
          theories_count: 2,
          linked_cases_count: 0,
          confidence_score: 0.62,
          processing_time_seconds: 38.7,
          report_id: 'rpt-002',
        },
      ]);
      setTriageItems([
        {
          triage_id: 'tri-001',
          case_id: 'case-003',
          priority: 'critical',
          score: 85,
          reasons: ['new_evidence', 'suspect_identified'],
          recommended_actions: ['Review new evidence', 'Prepare interview strategy'],
        },
        {
          triage_id: 'tri-002',
          case_id: 'case-004',
          priority: 'high',
          score: 72,
          reasons: ['forensic_results', 'pattern_match'],
          recommended_actions: ['Review forensic results', 'Cross-reference linked cases'],
        },
        {
          triage_id: 'tri-003',
          case_id: 'case-005',
          priority: 'medium',
          score: 55,
          reasons: ['stale_case', 'scheduled_review'],
          recommended_actions: ['Review for new angles', 'Consider cold case protocols'],
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const startInvestigation = async () => {
    if (!caseId) return;

    setIsInvestigating(true);
    setProgress(0);
    setCurrentStage('Initializing...');

    const stages = [
      { stage: 'Analyzing crime scene...', progress: 20 },
      { stage: 'Profiling offender behavior...', progress: 40 },
      { stage: 'Generating theories...', progress: 60 },
      { stage: 'Linking related cases...', progress: 80 },
      { stage: 'Building report...', progress: 95 },
      { stage: 'Complete', progress: 100 },
    ];

    for (const { stage, progress: prog } of stages) {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setCurrentStage(stage);
      setProgress(prog);
    }

    setInvestigations((prev) => [
      {
        result_id: `inv-${Date.now()}`,
        case_id: caseId,
        status: 'completed',
        suspects_count: 2,
        theories_count: 4,
        linked_cases_count: 2,
        confidence_score: 0.82,
        processing_time_seconds: 9.0,
        report_id: `rpt-${Date.now()}`,
      },
      ...prev,
    ]);

    setIsInvestigating(false);
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-red-900/50 text-red-400 border-red-500',
      high: 'bg-orange-900/50 text-orange-400 border-orange-500',
      medium: 'bg-yellow-900/50 text-yellow-400 border-yellow-500',
      low: 'bg-green-900/50 text-green-400 border-green-500',
      routine: 'bg-gray-700 text-gray-400 border-gray-500',
    };
    return colors[priority] || 'bg-gray-700 text-gray-400 border-gray-500';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: 'text-green-400',
      in_progress: 'text-yellow-400',
      failed: 'text-red-400',
    };
    return colors[status] || 'text-gray-400';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Auto Investigator Console</h2>
        <div className="flex bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('investigate')}
            className={`px-4 py-2 rounded text-sm ${activeTab === 'investigate' ? 'bg-blue-600' : ''}`}
          >
            Auto Investigate
          </button>
          <button
            onClick={() => setActiveTab('triage')}
            className={`px-4 py-2 rounded text-sm ${activeTab === 'triage' ? 'bg-blue-600' : ''}`}
          >
            Daily Triage
          </button>
        </div>
      </div>

      {activeTab === 'investigate' && (
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 space-y-4">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="font-medium mb-4">Start New Investigation</h3>
              {caseId ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <span className="text-gray-400">Selected Case:</span>
                    <span className="font-medium">{caseId}</span>
                  </div>

                  {isInvestigating ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span>{currentStage}</span>
                        <span>{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-3">
                        <div
                          className="bg-blue-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={startInvestigation}
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium flex items-center gap-2"
                    >
                      <span>🔍</span>
                      Start Auto Investigation
                    </button>
                  )}

                  <div className="text-sm text-gray-400">
                    ADA will analyze the crime scene, profile offender behavior, generate theories,
                    link related cases, and produce a comprehensive investigation report.
                  </div>
                </div>
              ) : (
                <p className="text-gray-400">Select a case from the dropdown above to start an investigation</p>
              )}
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-4">Recent Investigations</h3>
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
              ) : (
                <div className="space-y-3">
                  {investigations.map((inv) => (
                    <div key={inv.result_id} className="bg-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <span className="font-medium">{inv.case_id}</span>
                          <span className={`text-sm ${getStatusColor(inv.status)}`}>
                            {inv.status}
                          </span>
                        </div>
                        <span className="text-sm text-gray-400">
                          {inv.processing_time_seconds.toFixed(1)}s
                        </span>
                      </div>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Suspects</span>
                          <p className="font-medium">{inv.suspects_count}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">Theories</span>
                          <p className="font-medium">{inv.theories_count}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">Linked Cases</span>
                          <p className="font-medium">{inv.linked_cases_count}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">Confidence</span>
                          <p className="font-medium text-blue-400">
                            {(inv.confidence_score * 100).toFixed(0)}%
                          </p>
                        </div>
                      </div>
                      {inv.report_id && (
                        <div className="mt-3 pt-3 border-t border-gray-600">
                          <button className="text-sm text-blue-400 hover:text-blue-300">
                            View Report →
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3">Investigation Pipeline</h3>
              <div className="space-y-3">
                {[
                  { stage: 'Scene Analysis', icon: '🏠' },
                  { stage: 'Offender Profiling', icon: '👤' },
                  { stage: 'Theory Generation', icon: '💡' },
                  { stage: 'Case Linking', icon: '🔗' },
                  { stage: 'Report Building', icon: '📄' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <span className="text-lg">{item.icon}</span>
                    <span className="text-sm">{item.stage}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-3">Statistics</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Investigations</span>
                  <span>{investigations.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Confidence</span>
                  <span>
                    {investigations.length > 0
                      ? (
                          (investigations.reduce((sum, i) => sum + i.confidence_score, 0) /
                            investigations.length) *
                          100
                        ).toFixed(0)
                      : 0}
                    %
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Processing Time</span>
                  <span>
                    {investigations.length > 0
                      ? (
                          investigations.reduce((sum, i) => sum + i.processing_time_seconds, 0) /
                          investigations.length
                        ).toFixed(1)
                      : 0}
                    s
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'triage' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">Daily Case Triage</h3>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
              Run Daily Triage
            </button>
          </div>

          <div className="grid grid-cols-5 gap-4">
            {['critical', 'high', 'medium', 'low', 'routine'].map((priority) => {
              const count = triageItems.filter((t) => t.priority === priority).length;
              return (
                <div
                  key={priority}
                  className={`bg-gray-800 rounded-lg p-4 border-l-4 ${getPriorityColor(priority)}`}
                >
                  <div className="text-2xl font-bold">{count}</div>
                  <div className="text-sm text-gray-400 capitalize">{priority}</div>
                </div>
              );
            })}
          </div>

          <div className="space-y-3">
            {triageItems.map((item) => (
              <div
                key={item.triage_id}
                className={`bg-gray-800 rounded-lg p-4 border-l-4 ${getPriorityColor(item.priority)}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="font-medium">{item.case_id}</span>
                    <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(item.priority)}`}>
                      {item.priority.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-sm text-gray-400">Score: {item.score}</span>
                </div>

                <div className="mb-3">
                  <span className="text-sm text-gray-400">Reasons:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {item.reasons.map((reason, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-700 rounded text-xs"
                      >
                        {reason.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-sm text-gray-400">Recommended Actions:</span>
                  <ul className="mt-1 space-y-1">
                    {item.recommended_actions.map((action, index) => (
                      <li key={index} className="text-sm flex items-center gap-2">
                        <span className="w-1 h-1 bg-blue-500 rounded-full"></span>
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-3 pt-3 border-t border-gray-700 flex gap-2">
                  <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                    Start Investigation
                  </button>
                  <button className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                    Mark Reviewed
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

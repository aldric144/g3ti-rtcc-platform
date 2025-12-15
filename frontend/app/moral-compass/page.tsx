'use client';

import React, { useState, useEffect } from 'react';
import EthicalReasoningConsole from './components/EthicalReasoningConsole';
import FairnessDashboard from './components/FairnessDashboard';
import MoralAlertsPanel from './components/MoralAlertsPanel';
import CulturalContextViewer from './components/CulturalContextViewer';
import EthicsAuditTrailViewer from './components/EthicsAuditTrailViewer';
import ReasoningChainVisualizer from './components/ReasoningChainVisualizer';

type TabType = 'reasoning' | 'fairness' | 'alerts' | 'context' | 'audit' | 'chain';

interface MoralCompassStats {
  moral_engine: {
    total_assessments: number;
    decisions_made: number;
    vetoes_issued: number;
  };
  ethical_guardrails: {
    total_checks: number;
    violations: number;
    blocked: number;
  };
  fairness_analyzer: {
    total_assessments: number;
    passed: number;
    failed: number;
    bias_detected: number;
  };
  culture_context: {
    contexts_generated: number;
    events_tracked: number;
    neighborhoods_profiled: number;
  };
  moral_graph: {
    total_nodes: number;
    total_edges: number;
    capsules_generated: number;
  };
}

export default function MoralCompassHQ() {
  const [activeTab, setActiveTab] = useState<TabType>('reasoning');
  const [stats, setStats] = useState<MoralCompassStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/moral/statistics');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch moral compass stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'reasoning', label: 'Ethical Reasoning', icon: '⚖️' },
    { id: 'fairness', label: 'Fairness Dashboard', icon: '📊' },
    { id: 'alerts', label: 'Moral Alerts', icon: '🔔' },
    { id: 'context', label: 'Cultural Context', icon: '🌍' },
    { id: 'audit', label: 'Audit Trail', icon: '📋' },
    { id: 'chain', label: 'Reasoning Chain', icon: '🔗' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'reasoning':
        return <EthicalReasoningConsole />;
      case 'fairness':
        return <FairnessDashboard />;
      case 'alerts':
        return <MoralAlertsPanel onAlertCountChange={setAlertCount} />;
      case 'context':
        return <CulturalContextViewer />;
      case 'audit':
        return <EthicsAuditTrailViewer />;
      case 'chain':
        return <ReasoningChainVisualizer />;
      default:
        return <EthicalReasoningConsole />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-navy-900 to-slate-800">
      <div className="p-6">
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gold-400 flex items-center gap-3">
                <span className="text-4xl">🧭</span>
                AI Moral Compass HQ
              </h1>
              <p className="text-slate-400 mt-1">
                Ethical Reasoning Engine for Responsible AI Operations
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-slate-800/50 rounded-lg px-4 py-2 border border-gold-500/30">
                <span className="text-slate-400 text-sm">System Status:</span>
                <span className="ml-2 text-green-400 font-semibold">Active</span>
              </div>
            </div>
          </div>
        </div>

        {stats && (
          <div className="grid grid-cols-5 gap-4 mb-6">
            <div className="bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
              <div className="text-gold-400 text-2xl font-bold">
                {stats.moral_engine.total_assessments}
              </div>
              <div className="text-slate-400 text-sm">Moral Assessments</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
              <div className="text-blue-400 text-2xl font-bold">
                {stats.fairness_analyzer.total_assessments}
              </div>
              <div className="text-slate-400 text-sm">Fairness Checks</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
              <div className="text-red-400 text-2xl font-bold">
                {stats.ethical_guardrails.violations}
              </div>
              <div className="text-slate-400 text-sm">Violations Detected</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
              <div className="text-purple-400 text-2xl font-bold">
                {stats.culture_context.neighborhoods_profiled}
              </div>
              <div className="text-slate-400 text-sm">Neighborhoods Profiled</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
              <div className="text-green-400 text-2xl font-bold">
                {stats.moral_graph.capsules_generated}
              </div>
              <div className="text-slate-400 text-sm">Reasoning Capsules</div>
            </div>
          </div>
        )}

        <div className="bg-slate-800/30 rounded-lg border border-gold-500/20">
          <div className="border-b border-gold-500/20">
            <nav className="flex">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-4 text-sm font-medium transition-colors relative ${
                    activeTab === tab.id
                      ? 'text-gold-400 bg-slate-800/50'
                      : 'text-slate-400 hover:text-gold-300 hover:bg-slate-800/30'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                  {tab.id === 'alerts' && alertCount > 0 && (
                    <span className="ml-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {alertCount}
                    </span>
                  )}
                  {activeTab === tab.id && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gold-400" />
                  )}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">{renderTabContent()}</div>
        </div>

        <div className="mt-6 text-center text-slate-500 text-sm">
          <p>
            AI Moral Compass Engine v1.0 | Phase 35 | G3TI RTCC-UIP Platform
          </p>
          <p className="mt-1">
            Ensuring Constitutional Compliance, Non-Discrimination, and Community Trust
          </p>
        </div>
      </div>
    </div>
  );
}

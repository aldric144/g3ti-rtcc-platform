'use client';

import React, { useState, useEffect, useCallback } from 'react';

const GOLD = '#c9a227';
const NAVY = '#0a1628';

interface SystemStatus {
  modules_ok: boolean;
  websockets_ok: boolean;
  endpoints_ok: boolean;
  orchestration_ok: boolean;
  database_ok: boolean;
  ai_engines_ok: boolean;
  latency_ms: number;
  load_factor: number;
  deployment_score: number;
  errors: string[];
  warnings: string[];
  module_count: number;
  websocket_count: number;
  api_count: number;
}

interface OrchestrationStatus {
  kernel_ok: boolean;
  event_router_ok: boolean;
  workflow_engine_ok: boolean;
  policy_engine_ok: boolean;
  resource_manager_ok: boolean;
  event_bus_ok: boolean;
  response_time_ms: number;
  workflows_registered: number;
}

export default function SystemPrelaunchPage() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [orchestrationStatus, setOrchestrationStatus] = useState<OrchestrationStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      setLoading(true);

      const [sysRes, orchRes] = await Promise.all([
        fetch('/api/system/prelaunch/status'),
        fetch('/api/system/prelaunch/orchestration'),
      ]);

      if (sysRes.ok) {
        setSystemStatus(await sysRes.json());
      }
      if (orchRes.ok) {
        setOrchestrationStatus(await orchRes.json());
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const triggerValidation = async () => {
    setValidating(true);
    try {
      await fetch('/api/system/prelaunch/validate', { method: 'POST' });
      await fetchStatus();
    } finally {
      setValidating(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const getScoreGrade = (score: number) => {
    if (score >= 95) return { grade: 'A+', color: '#22c55e' };
    if (score >= 90) return { grade: 'A', color: '#22c55e' };
    if (score >= 85) return { grade: 'B+', color: '#84cc16' };
    if (score >= 80) return { grade: 'B', color: '#eab308' };
    if (score >= 70) return { grade: 'C', color: '#f97316' };
    return { grade: 'F', color: '#ef4444' };
  };

  const scoreInfo = getScoreGrade(systemStatus?.deployment_score ?? 0);

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: NAVY }}>
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                System Pre-Launch Diagnostics
              </h1>
              <p className="text-white/60">
                Complete system validation and deployment readiness assessment
              </p>
            </div>
            <button
              onClick={triggerValidation}
              disabled={validating}
              className="px-6 py-3 rounded-lg text-white font-medium transition-all disabled:opacity-50"
              style={{ backgroundColor: GOLD }}
            >
              {validating ? 'Validating...' : 'Run Full Validation'}
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          <div className="lg:col-span-1 bg-white/5 rounded-lg p-6 border border-white/10 flex flex-col items-center justify-center">
            <div className="text-6xl font-bold mb-2" style={{ color: scoreInfo.color }}>
              {scoreInfo.grade}
            </div>
            <div className="text-3xl font-bold text-white mb-1">
              {systemStatus?.deployment_score?.toFixed(1) ?? 0}%
            </div>
            <div className="text-white/60 text-sm">Deployment Score</div>
            <div className={`mt-4 px-4 py-2 rounded-full text-sm ${
              (systemStatus?.deployment_score ?? 0) >= 85
                ? 'bg-green-500/20 text-green-400'
                : 'bg-red-500/20 text-red-400'
            }`}>
              {(systemStatus?.deployment_score ?? 0) >= 85 ? 'Ready for Deploy' : 'Not Ready'}
            </div>
          </div>

          <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-3 gap-4">
            <StatusTile
              title="Modules"
              count={systemStatus?.module_count ?? 0}
              ok={systemStatus?.modules_ok ?? false}
              subtitle="60+ validated"
            />
            <StatusTile
              title="WebSockets"
              count={systemStatus?.websocket_count ?? 0}
              ok={systemStatus?.websockets_ok ?? false}
              subtitle="80+ channels"
            />
            <StatusTile
              title="API Endpoints"
              count={systemStatus?.api_count ?? 0}
              ok={systemStatus?.endpoints_ok ?? false}
              subtitle="All schemas valid"
            />
            <StatusTile
              title="Orchestration"
              count={orchestrationStatus?.workflows_registered ?? 0}
              ok={systemStatus?.orchestration_ok ?? false}
              subtitle="Workflows registered"
            />
            <StatusTile
              title="Database"
              count={1}
              ok={systemStatus?.database_ok ?? false}
              subtitle="Neo4j + Redis + ES"
            />
            <StatusTile
              title="AI Engines"
              count={15}
              ok={systemStatus?.ai_engines_ok ?? false}
              subtitle="All operational"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white/5 rounded-lg p-6 border border-white/10">
            <h3 className="text-lg font-semibold mb-4" style={{ color: GOLD }}>
              Orchestration Engine Signal
            </h3>
            <div className="space-y-3">
              <OrchestrationItem
                name="Orchestration Kernel"
                ok={orchestrationStatus?.kernel_ok ?? false}
              />
              <OrchestrationItem
                name="Event Router"
                ok={orchestrationStatus?.event_router_ok ?? false}
              />
              <OrchestrationItem
                name="Workflow Engine"
                ok={orchestrationStatus?.workflow_engine_ok ?? false}
              />
              <OrchestrationItem
                name="Policy Binding Engine"
                ok={orchestrationStatus?.policy_engine_ok ?? false}
              />
              <OrchestrationItem
                name="Resource Manager"
                ok={orchestrationStatus?.resource_manager_ok ?? false}
              />
              <OrchestrationItem
                name="Event Fusion Bus"
                ok={orchestrationStatus?.event_bus_ok ?? false}
              />
            </div>
            <div className="mt-4 pt-4 border-t border-white/10 flex justify-between text-sm">
              <span className="text-white/60">Response Time</span>
              <span className="text-white">{orchestrationStatus?.response_time_ms?.toFixed(2) ?? 0}ms</span>
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-6 border border-white/10">
            <h3 className="text-lg font-semibold mb-4" style={{ color: GOLD }}>
              System Metrics
            </h3>
            <div className="space-y-4">
              <MetricBar
                label="System Latency"
                value={systemStatus?.latency_ms ?? 0}
                max={1000}
                unit="ms"
                threshold={500}
              />
              <MetricBar
                label="Load Factor"
                value={(systemStatus?.load_factor ?? 0) * 100}
                max={100}
                unit="%"
                threshold={80}
              />
              <MetricBar
                label="Deployment Score"
                value={systemStatus?.deployment_score ?? 0}
                max={100}
                unit="%"
                threshold={85}
                inverse
              />
            </div>
          </div>
        </div>

        {((systemStatus?.errors?.length ?? 0) > 0 || (systemStatus?.warnings?.length ?? 0) > 0) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {(systemStatus?.errors?.length ?? 0) > 0 && (
              <div className="bg-red-500/10 rounded-lg p-6 border border-red-500/30">
                <h3 className="text-lg font-semibold text-red-400 mb-4">
                  Errors ({systemStatus?.errors.length})
                </h3>
                <ul className="space-y-2">
                  {systemStatus?.errors.map((err, i) => (
                    <li key={i} className="text-red-300 text-sm flex items-start">
                      <span className="mr-2 text-red-400">●</span>
                      {err}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {(systemStatus?.warnings?.length ?? 0) > 0 && (
              <div className="bg-yellow-500/10 rounded-lg p-6 border border-yellow-500/30">
                <h3 className="text-lg font-semibold text-yellow-400 mb-4">
                  Warnings ({systemStatus?.warnings.length})
                </h3>
                <ul className="space-y-2">
                  {systemStatus?.warnings.map((warn, i) => (
                    <li key={i} className="text-yellow-300 text-sm flex items-start">
                      <span className="mr-2 text-yellow-400">●</span>
                      {warn}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="bg-white/5 rounded-lg p-6 border border-white/10">
          <h3 className="text-lg font-semibold mb-4" style={{ color: GOLD }}>
            Expected Behaviors
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { behavior: 'Real-time WebSocket events appear in UI', status: 'expected' },
              { behavior: 'Orchestration Engine responds within 500ms', status: 'expected' },
              { behavior: 'All 20 workflows are registered and executable', status: 'expected' },
              { behavior: 'Data Lake → Prediction → UI pipeline validated', status: 'expected' },
              { behavior: 'Constitutional guardrails are enforced', status: 'expected' },
              { behavior: 'Multi-agency coordination is operational', status: 'expected' },
            ].map((item, index) => (
              <div
                key={index}
                className="flex items-center space-x-3 p-3 bg-white/5 rounded-lg"
              >
                <span className="text-green-400">✓</span>
                <span className="text-white/80 text-sm">{item.behavior}</span>
              </div>
            ))}
          </div>
        </div>

        <footer className="mt-8 text-center text-white/40 text-sm">
          <p>G3TI RTCC-UIP | Phase 39: System Pre-Launch Diagnostics</p>
          <p className="mt-1">Riviera Beach, Florida 33404</p>
        </footer>
      </div>
    </div>
  );
}

function StatusTile({
  title,
  count,
  ok,
  subtitle,
}: {
  title: string;
  count: number;
  ok: boolean;
  subtitle: string;
}) {
  return (
    <div className="bg-white/5 rounded-lg p-4 border border-white/10">
      <div className="flex items-center justify-between mb-2">
        <span className="text-white/70 text-sm">{title}</span>
        <span style={{ color: ok ? '#22c55e' : '#ef4444', fontSize: '1.25rem' }}>
          {ok ? '●' : '○'}
        </span>
      </div>
      <div className="text-2xl font-bold text-white">{count}</div>
      <div className="text-xs text-white/50">{subtitle}</div>
    </div>
  );
}

function OrchestrationItem({ name, ok }: { name: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-white/5">
      <span className="text-white/80">{name}</span>
      <span
        className={`px-2 py-1 rounded text-xs ${
          ok ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
        }`}
      >
        {ok ? 'OK' : 'FAIL'}
      </span>
    </div>
  );
}

function MetricBar({
  label,
  value,
  max,
  unit,
  threshold,
  inverse = false,
}: {
  label: string;
  value: number;
  max: number;
  unit: string;
  threshold: number;
  inverse?: boolean;
}) {
  const percentage = Math.min((value / max) * 100, 100);
  const isGood = inverse ? value >= threshold : value <= threshold;

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-white/70">{label}</span>
        <span className="text-white">{value.toFixed(1)}{unit}</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{
            width: `${percentage}%`,
            backgroundColor: isGood ? '#22c55e' : '#ef4444',
          }}
        />
      </div>
    </div>
  );
}

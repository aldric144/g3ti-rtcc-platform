'use client';

import React, { useState, useEffect, useCallback } from 'react';

interface ModuleStatus {
  module_id: string;
  module_name: string;
  module_path: string;
  category: string;
  status: string;
  response_time_ms: number;
  errors: string[];
  warnings: string[];
}

interface WebSocketStatus {
  channel_id: string;
  channel_path: string;
  channel_name: string;
  status: string;
  ping_latency_ms: number;
  handshake_ok: boolean;
  broadcast_ok: boolean;
  errors: string[];
}

interface APIStatus {
  endpoint_id: string;
  endpoint_path: string;
  method: string;
  status: string;
  response_time_ms: number;
  schema_valid: boolean;
  errors: string[];
}

interface PrelaunchStatus {
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

const GOLD = '#c9a227';
const NAVY = '#0a1628';

export default function PreLaunchChecklistPanel() {
  const [status, setStatus] = useState<PrelaunchStatus | null>(null);
  const [modules, setModules] = useState<ModuleStatus[]>([]);
  const [websockets, setWebsockets] = useState<WebSocketStatus[]>([]);
  const [endpoints, setEndpoints] = useState<APIStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'modules' | 'websockets' | 'endpoints'>('overview');

  const fetchStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const statusRes = await fetch('/api/system/prelaunch/status');
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setStatus(statusData);
      }

      const modulesRes = await fetch('/api/system/prelaunch/modules');
      if (modulesRes.ok) {
        const modulesData = await modulesRes.json();
        setModules(modulesData.modules || []);
      }

      const wsRes = await fetch('/api/system/prelaunch/websockets');
      if (wsRes.ok) {
        const wsData = await wsRes.json();
        setWebsockets(wsData.websockets || []);
      }

      const apiRes = await fetch('/api/system/prelaunch/endpoints');
      if (apiRes.ok) {
        const apiData = await apiRes.json();
        setEndpoints(apiData.endpoints || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch status');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const getStatusColor = (ok: boolean) => ok ? '#22c55e' : '#ef4444';
  const getStatusIcon = (ok: boolean) => ok ? '●' : '○';

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatusCard
          title="Modules"
          ok={status?.modules_ok ?? false}
          count={status?.module_count ?? 0}
        />
        <StatusCard
          title="WebSockets"
          ok={status?.websockets_ok ?? false}
          count={status?.websocket_count ?? 0}
        />
        <StatusCard
          title="API Endpoints"
          ok={status?.endpoints_ok ?? false}
          count={status?.api_count ?? 0}
        />
        <StatusCard
          title="Orchestration"
          ok={status?.orchestration_ok ?? false}
          count={1}
        />
        <StatusCard
          title="Database"
          ok={status?.database_ok ?? false}
          count={1}
        />
        <StatusCard
          title="AI Engines"
          ok={status?.ai_engines_ok ?? false}
          count={1}
        />
      </div>

      <div className="bg-white/5 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: GOLD }}>
          System Metrics
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            label="Latency"
            value={`${status?.latency_ms?.toFixed(1) ?? 0}ms`}
          />
          <MetricCard
            label="Load Factor"
            value={`${((status?.load_factor ?? 0) * 100).toFixed(1)}%`}
          />
          <MetricCard
            label="Deployment Score"
            value={`${status?.deployment_score?.toFixed(1) ?? 0}%`}
            highlight={true}
          />
          <MetricCard
            label="Ready Status"
            value={(status?.deployment_score ?? 0) >= 85 ? 'READY' : 'NOT READY'}
            highlight={(status?.deployment_score ?? 0) >= 85}
          />
        </div>
      </div>

      {(status?.errors?.length ?? 0) > 0 && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <h4 className="text-red-400 font-semibold mb-2">Errors</h4>
          <ul className="space-y-1">
            {status?.errors.map((err, i) => (
              <li key={i} className="text-red-300 text-sm">{err}</li>
            ))}
          </ul>
        </div>
      )}

      {(status?.warnings?.length ?? 0) > 0 && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
          <h4 className="text-yellow-400 font-semibold mb-2">Warnings</h4>
          <ul className="space-y-1">
            {status?.warnings.map((warn, i) => (
              <li key={i} className="text-yellow-300 text-sm">{warn}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderModules = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold" style={{ color: GOLD }}>
          Module Status Grid ({modules.length} modules)
        </h3>
        <span className={`px-3 py-1 rounded-full text-sm ${status?.modules_ok ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
          {status?.modules_ok ? 'All OK' : 'Issues Detected'}
        </span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {modules.map((module) => (
          <div
            key={module.module_id}
            className="bg-white/5 rounded-lg p-3 border border-white/10"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-white/90">{module.module_name}</span>
              <span style={{ color: module.status === 'ok' ? '#22c55e' : '#ef4444' }}>
                {getStatusIcon(module.status === 'ok')}
              </span>
            </div>
            <div className="text-xs text-white/50 mb-1">{module.module_path}</div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-white/60">{module.category}</span>
              <span className="text-white/60">{module.response_time_ms.toFixed(2)}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderWebsockets = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold" style={{ color: GOLD }}>
          WebSocket Connectivity Matrix ({websockets.length} channels)
        </h3>
        <span className={`px-3 py-1 rounded-full text-sm ${status?.websockets_ok ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
          {status?.websockets_ok ? 'All Connected' : 'Connection Issues'}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-2 px-3 text-white/70">Channel</th>
              <th className="text-left py-2 px-3 text-white/70">Path</th>
              <th className="text-center py-2 px-3 text-white/70">Status</th>
              <th className="text-center py-2 px-3 text-white/70">Handshake</th>
              <th className="text-center py-2 px-3 text-white/70">Broadcast</th>
              <th className="text-right py-2 px-3 text-white/70">Latency</th>
            </tr>
          </thead>
          <tbody>
            {websockets.map((ws) => (
              <tr key={ws.channel_id} className="border-b border-white/5 hover:bg-white/5">
                <td className="py-2 px-3 text-white/90">{ws.channel_name}</td>
                <td className="py-2 px-3 text-white/60 font-mono text-xs">{ws.channel_path}</td>
                <td className="py-2 px-3 text-center">
                  <span style={{ color: ws.status === 'ok' ? '#22c55e' : '#ef4444' }}>
                    {getStatusIcon(ws.status === 'ok')}
                  </span>
                </td>
                <td className="py-2 px-3 text-center">
                  <span style={{ color: ws.handshake_ok ? '#22c55e' : '#ef4444' }}>
                    {ws.handshake_ok ? '✓' : '✗'}
                  </span>
                </td>
                <td className="py-2 px-3 text-center">
                  <span style={{ color: ws.broadcast_ok ? '#22c55e' : '#ef4444' }}>
                    {ws.broadcast_ok ? '✓' : '✗'}
                  </span>
                </td>
                <td className="py-2 px-3 text-right text-white/60">{ws.ping_latency_ms.toFixed(1)}ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderEndpoints = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold" style={{ color: GOLD }}>
          API Endpoint Validator ({endpoints.length} endpoints)
        </h3>
        <span className={`px-3 py-1 rounded-full text-sm ${status?.endpoints_ok ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
          {status?.endpoints_ok ? 'All Valid' : 'Validation Issues'}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-2 px-3 text-white/70">Method</th>
              <th className="text-left py-2 px-3 text-white/70">Endpoint</th>
              <th className="text-center py-2 px-3 text-white/70">Status</th>
              <th className="text-center py-2 px-3 text-white/70">Schema</th>
              <th className="text-right py-2 px-3 text-white/70">Response Time</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.map((ep) => (
              <tr key={ep.endpoint_id} className="border-b border-white/5 hover:bg-white/5">
                <td className="py-2 px-3">
                  <span className="px-2 py-0.5 rounded text-xs font-mono bg-blue-500/20 text-blue-400">
                    {ep.method}
                  </span>
                </td>
                <td className="py-2 px-3 text-white/90 font-mono text-xs">{ep.endpoint_path}</td>
                <td className="py-2 px-3 text-center">
                  <span style={{ color: ep.status === 'ok' ? '#22c55e' : '#ef4444' }}>
                    {getStatusIcon(ep.status === 'ok')}
                  </span>
                </td>
                <td className="py-2 px-3 text-center">
                  <span style={{ color: ep.schema_valid ? '#22c55e' : '#ef4444' }}>
                    {ep.schema_valid ? '✓' : '✗'}
                  </span>
                </td>
                <td className="py-2 px-3 text-right text-white/60">{ep.response_time_ms.toFixed(2)}ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  if (loading && !status) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2" style={{ borderColor: GOLD }}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 text-center">
        <p className="text-red-400">{error}</p>
        <button
          onClick={fetchStatus}
          className="mt-4 px-4 py-2 rounded-lg text-white"
          style={{ backgroundColor: GOLD }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold" style={{ color: GOLD }}>
          Pre-Launch Checklist
        </h2>
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="px-4 py-2 rounded-lg text-white transition-opacity disabled:opacity-50"
          style={{ backgroundColor: GOLD }}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="flex space-x-2 border-b border-white/10">
        {(['overview', 'modules', 'websockets', 'endpoints'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'border-b-2 text-white'
                : 'text-white/60 hover:text-white/80'
            }`}
            style={{ borderColor: activeTab === tab ? GOLD : 'transparent' }}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'modules' && renderModules()}
      {activeTab === 'websockets' && renderWebsockets()}
      {activeTab === 'endpoints' && renderEndpoints()}
    </div>
  );
}

function StatusCard({ title, ok, count }: { title: string; ok: boolean; count: number }) {
  return (
    <div className="bg-white/5 rounded-lg p-4 border border-white/10">
      <div className="flex items-center justify-between mb-2">
        <span className="text-white/70 text-sm">{title}</span>
        <span style={{ color: ok ? '#22c55e' : '#ef4444', fontSize: '1.5rem' }}>
          {ok ? '●' : '○'}
        </span>
      </div>
      <div className="text-2xl font-bold text-white">{count}</div>
      <div className={`text-xs ${ok ? 'text-green-400' : 'text-red-400'}`}>
        {ok ? 'Operational' : 'Issues Detected'}
      </div>
    </div>
  );
}

function MetricCard({ label, value, highlight = false }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="bg-white/5 rounded-lg p-4">
      <div className="text-white/60 text-sm mb-1">{label}</div>
      <div
        className="text-xl font-bold"
        style={{ color: highlight ? GOLD : 'white' }}
      >
        {value}
      </div>
    </div>
  );
}

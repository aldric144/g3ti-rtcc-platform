'use client';

import React from 'react';
import PreLaunchChecklistPanel from './components/PreLaunchChecklistPanel';
import DeploymentSummaryCard from './components/DeploymentSummaryCard';

const GOLD = '#c9a227';
const NAVY = '#0a1628';

export default function LiveSystemCheckPage() {
  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: NAVY }}>
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Live System Check
              </h1>
              <p className="text-white/60">
                G3TI RTCC-UIP Pre-Launch Validation & Deployment Readiness
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="px-4 py-2 rounded-lg bg-white/5 border border-white/10">
                <span className="text-white/60 text-sm">Environment:</span>
                <span className="text-white ml-2 font-medium">Preview</span>
              </div>
              <div className="px-4 py-2 rounded-lg" style={{ backgroundColor: `${GOLD}20`, border: `1px solid ${GOLD}40` }}>
                <span style={{ color: GOLD }} className="font-medium">Phase 39</span>
              </div>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <PreLaunchChecklistPanel />
          </div>
          <div className="lg:col-span-1">
            <DeploymentSummaryCard />
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickActionCard
            title="Run Full Validation"
            description="Execute complete system validation"
            icon="🔍"
            action="/api/system/prelaunch/validate"
          />
          <QuickActionCard
            title="WebSocket Stress Test"
            description="Test 500 concurrent events"
            icon="⚡"
            action="/api/system/prelaunch/websocket-check/stress"
          />
          <QuickActionCard
            title="View Repair Suggestions"
            description="Get auto-fix recommendations"
            icon="🔧"
            action="/api/system/prelaunch/websocket-check/repair-suggestions"
          />
          <QuickActionCard
            title="Check Orchestration"
            description="Verify Phase 38 integration"
            icon="🎯"
            action="/api/system/prelaunch/orchestration"
          />
        </div>

        <div className="mt-8 bg-white/5 rounded-lg p-6 border border-white/10">
          <h3 className="text-lg font-semibold mb-4" style={{ color: GOLD }}>
            System Integration Overview
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
            {[
              'Data Lake', 'Intel Orchestration', 'Ops Continuity', 'Autonomous Ops',
              'Fusion Cloud', 'Threat Intel', 'National Security', 'Robotics',
              'Detective AI', 'Emergency Mgmt', 'City Brain', 'City Governance',
              'City Autonomy', 'Constitution', 'Ethics Guardian', 'Enterprise Infra',
              'Officer Assist', 'Cyber Intel', 'Human Stability', 'Emergency AI',
              'Global Awareness', 'AI Sentinel', 'AI Personas', 'Moral Compass',
              'Public Guardian', 'Master UI', 'Orchestration', 'System Integration',
            ].map((module, index) => (
              <div
                key={index}
                className="bg-white/5 rounded px-2 py-1 text-center text-xs text-white/70 border border-white/10"
              >
                {module}
              </div>
            ))}
          </div>
        </div>

        <footer className="mt-8 text-center text-white/40 text-sm">
          <p>G3TI RTCC-UIP | Riviera Beach, Florida 33404</p>
          <p className="mt-1">Phase 39: Full System Preview Deployment & Live Frontend Activation</p>
        </footer>
      </div>
    </div>
  );
}

function QuickActionCard({
  title,
  description,
  icon,
  action,
}: {
  title: string;
  description: string;
  icon: string;
  action: string;
}) {
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState<string | null>(null);

  const handleClick = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(action, { method: action.includes('validate') ? 'POST' : 'GET' });
      if (res.ok) {
        const data = await res.json();
        setResult(JSON.stringify(data, null, 2).slice(0, 100) + '...');
      } else {
        setResult('Request failed');
      }
    } catch (err) {
      setResult('Error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="bg-white/5 rounded-lg p-4 border border-white/10 cursor-pointer hover:bg-white/10 transition-colors"
      onClick={handleClick}
    >
      <div className="flex items-center space-x-3 mb-2">
        <span className="text-2xl">{icon}</span>
        <div>
          <h4 className="text-white font-medium text-sm">{title}</h4>
          <p className="text-white/50 text-xs">{description}</p>
        </div>
      </div>
      {loading && (
        <div className="text-xs text-white/60 mt-2">Loading...</div>
      )}
      {result && (
        <div className="text-xs text-green-400 mt-2 font-mono truncate">{result}</div>
      )}
    </div>
  );
}

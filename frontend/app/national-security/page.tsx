'use client';

import { useState, useEffect } from 'react';
import CyberIntelPanel from './components/CyberIntelPanel';
import InsiderThreatPanel from './components/InsiderThreatPanel';
import GeoRiskMap from './components/GeoRiskMap';
import FinancialCrimeGraph from './components/FinancialCrimeGraph';
import NationalStabilityScore from './components/NationalStabilityScore';
import EarlyWarningTimeline from './components/EarlyWarningTimeline';

interface TabConfig {
  id: string;
  label: string;
  icon: string;
}

const tabs: TabConfig[] = [
  { id: 'overview', label: 'Overview', icon: '🛡️' },
  { id: 'cyber', label: 'Cyber Intel', icon: '💻' },
  { id: 'insider', label: 'Insider Threat', icon: '👤' },
  { id: 'geopolitical', label: 'Geo Risk', icon: '🌍' },
  { id: 'financial', label: 'Financial Crime', icon: '💰' },
  { id: 'fusion', label: 'Risk Fusion', icon: '🔗' },
];

export default function NationalSecurityPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [wsConnected, setWsConnected] = useState(false);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetchMetrics();
    fetchAlerts();
    
    const interval = setInterval(() => {
      fetchMetrics();
      fetchAlerts();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/national-security/metrics');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/national-security/alerts?active_only=true&limit=10');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  };

  const renderOverview = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="lg:col-span-2">
        <NationalStabilityScore />
      </div>
      <div className="lg:col-span-2">
        <EarlyWarningTimeline />
      </div>
      <CyberIntelPanel compact />
      <InsiderThreatPanel compact />
      <GeoRiskMap compact />
      <FinancialCrimeGraph compact />
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'cyber':
        return <CyberIntelPanel />;
      case 'insider':
        return <InsiderThreatPanel />;
      case 'geopolitical':
        return <GeoRiskMap />;
      case 'financial':
        return <FinancialCrimeGraph />;
      case 'fusion':
        return (
          <div className="grid grid-cols-1 gap-6">
            <NationalStabilityScore />
            <EarlyWarningTimeline />
          </div>
        );
      default:
        return renderOverview();
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
      case 'emergency':
        return 'bg-red-500';
      case 'flash':
      case 'immediate':
        return 'bg-orange-500';
      case 'priority':
        return 'bg-yellow-500';
      default:
        return 'bg-blue-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-red-400">
              National Security Engine
            </h1>
            <span className="px-3 py-1 bg-red-900 text-red-300 text-sm rounded-full">
              AI-NSE
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
              wsConnected ? 'bg-green-900 text-green-300' : 'bg-gray-700 text-gray-400'
            }`}>
              <span className={`w-2 h-2 rounded-full ${
                wsConnected ? 'bg-green-400 animate-pulse' : 'bg-gray-500'
              }`} />
              <span className="text-sm">
                {wsConnected ? 'Live' : 'Connecting...'}
              </span>
            </div>
            <span className="text-gray-400 text-sm">
              {new Date().toLocaleString()}
            </span>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700 px-6">
        <div className="flex space-x-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-red-400 border-b-2 border-red-400 bg-gray-700/50'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/30'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {alerts.length > 0 && (
        <div className="bg-red-900/30 border-b border-red-800 px-6 py-3">
          <div className="flex items-center space-x-4 overflow-x-auto">
            <span className="text-red-400 font-semibold whitespace-nowrap">
              Active Alerts:
            </span>
            {alerts.slice(0, 5).map((alert) => (
              <div
                key={alert.alert_id}
                className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
                  getPriorityColor(alert.priority)
                } bg-opacity-30`}
              >
                <span className={`w-2 h-2 rounded-full ${getPriorityColor(alert.priority)}`} />
                <span className="text-sm whitespace-nowrap">{alert.title}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <main className="p-6">
        {renderContent()}
      </main>

      {metrics && (
        <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <div className="flex items-center space-x-6">
              <span>
                Cyber Signals: {metrics.cyber_intel?.total_malware_signals || 0}
              </span>
              <span>
                Risk Profiles: {metrics.insider_threat?.total_profiles || 0}
              </span>
              <span>
                Geo Events: {metrics.geopolitical_risk?.total_conflict_events || 0}
              </span>
              <span>
                Fraud Patterns: {metrics.financial_crime?.total_fraud_patterns || 0}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span>
                Active Alerts: {metrics.security_alerts?.active_alerts || 0}
              </span>
              <span>
                Stability Score: {metrics.national_risk_fusion?.latest_stability_score?.toFixed(1) || 'N/A'}
              </span>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
}

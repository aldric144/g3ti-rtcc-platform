'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Lazy load components for better performance
const CrimeDashboard = dynamic(() => import('./CrimeDashboard'), { ssr: false });
const CrimeHeatmap = dynamic(() => import('./CrimeHeatmap'), { ssr: false });
const TrendCharts = dynamic(() => import('./TrendCharts'), { ssr: false });
const CrimeForecastPanel = dynamic(() => import('./CrimeForecastPanel'), { ssr: false });
const RepeatLocations = dynamic(() => import('./RepeatLocations'), { ssr: false });
const UploadCrimeData = dynamic(() => import('./UploadCrimeData'), { ssr: false });

type TabType = 'dashboard' | 'heatmap' | 'trends' | 'forecast' | 'repeat' | 'upload';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';

export default function CrimeAnalysisPage() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [isLoading, setIsLoading] = useState(true);
  const [hasData, setHasData] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkDataAvailability();
  }, []);

  const checkDataAvailability = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/crime/stats`);
      if (response.ok) {
        const data = await response.json();
        setHasData(data.total_records > 0);
      }
    } catch (err) {
      console.error('Error checking data availability:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const generateDemoData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/crime/generate-demo-data`, {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        setHasData(true);
        alert(`Generated ${data.records_generated} demo crime records`);
      } else {
        setError('Failed to generate demo data');
      }
    } catch (err) {
      setError('Error generating demo data');
    } finally {
      setIsLoading(false);
    }
  };

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'heatmap', label: 'Heatmap', icon: '🗺️' },
    { id: 'trends', label: 'Trends', icon: '📈' },
    { id: 'forecast', label: 'Forecast', icon: '🔮' },
    { id: 'repeat', label: 'Repeat Locations', icon: '📍' },
    { id: 'upload', label: 'Upload Data', icon: '📤' },
  ];

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      );
    }

    if (!hasData && activeTab !== 'upload') {
      return (
        <div className="flex flex-col items-center justify-center h-96 space-y-4">
          <div className="text-gray-400 text-lg">No crime data available</div>
          <p className="text-gray-500 text-sm">Upload crime data or generate demo data to get started</p>
          <div className="flex space-x-4">
            <button
              onClick={generateDemoData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Generate Demo Data
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Upload Data
            </button>
          </div>
        </div>
      );
    }

    switch (activeTab) {
      case 'dashboard':
        return <CrimeDashboard />;
      case 'heatmap':
        return <CrimeHeatmap />;
      case 'trends':
        return <TrendCharts />;
      case 'forecast':
        return <CrimeForecastPanel />;
      case 'repeat':
        return <RepeatLocations />;
      case 'upload':
        return <UploadCrimeData onUploadSuccess={() => { setHasData(true); checkDataAvailability(); }} />;
      default:
        return <CrimeDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">Crime Analysis</h1>
          <p className="text-gray-400">
            Comprehensive crime analytics, heatmaps, trends, and forecasting
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-700 pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="bg-gray-800 rounded-xl p-6 min-h-[600px]">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

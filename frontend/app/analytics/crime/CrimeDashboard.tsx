'use client';

import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';

interface CrimeStats {
  total_records: number;
  today: number;
  last_7_days: number;
  last_30_days: number;
  by_type: {
    violent: number;
    property: number;
    other: number;
  };
}

interface SectorRisk {
  sector: string;
  overall_score: number;
  risk_level: string;
  total_incidents: number;
  violent_crimes: number;
}

interface RiskComparison {
  sectors: SectorRisk[];
  highest_risk_sector: string;
  lowest_risk_sector: string;
  city_average_score: number;
}

export default function CrimeDashboard() {
  const [stats, setStats] = useState<CrimeStats | null>(null);
  const [riskData, setRiskData] = useState<RiskComparison | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [statsRes, riskRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/crime/stats`),
        fetch(`${API_BASE_URL}/api/crime/risk`),
      ]);

      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
      if (riskRes.ok) {
        setRiskData(await riskRes.json());
      }
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'text-red-500 bg-red-500/20';
      case 'high': return 'text-orange-500 bg-orange-500/20';
      case 'elevated': return 'text-yellow-500 bg-yellow-500/20';
      case 'moderate': return 'text-blue-500 bg-blue-500/20';
      default: return 'text-green-500 bg-green-500/20';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center py-8">{error}</div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Total Records</div>
          <div className="text-3xl font-bold text-white">{stats?.total_records || 0}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Today</div>
          <div className="text-3xl font-bold text-blue-400">{stats?.today || 0}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Last 7 Days</div>
          <div className="text-3xl font-bold text-green-400">{stats?.last_7_days || 0}</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Last 30 Days</div>
          <div className="text-3xl font-bold text-purple-400">{stats?.last_30_days || 0}</div>
        </div>
      </div>

      {/* Crime Type Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Crime by Type</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Violent Crimes</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-red-500 h-2 rounded-full"
                    style={{
                      width: `${stats?.total_records ? (stats.by_type.violent / stats.total_records) * 100 : 0}%`,
                    }}
                  ></div>
                </div>
                <span className="text-red-400 font-semibold">{stats?.by_type.violent || 0}</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Property Crimes</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-yellow-500 h-2 rounded-full"
                    style={{
                      width: `${stats?.total_records ? (stats.by_type.property / stats.total_records) * 100 : 0}%`,
                    }}
                  ></div>
                </div>
                <span className="text-yellow-400 font-semibold">{stats?.by_type.property || 0}</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Other Crimes</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{
                      width: `${stats?.total_records ? (stats.by_type.other / stats.total_records) * 100 : 0}%`,
                    }}
                  ></div>
                </div>
                <span className="text-blue-400 font-semibold">{stats?.by_type.other || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* City Risk Overview */}
        <div className="bg-gray-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">City Risk Overview</h3>
          {riskData && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">City Average Score</span>
                <span className="text-2xl font-bold text-white">{riskData.city_average_score.toFixed(1)}/5</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Highest Risk</span>
                <span className="text-red-400 font-semibold">{riskData.highest_risk_sector}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Lowest Risk</span>
                <span className="text-green-400 font-semibold">{riskData.lowest_risk_sector}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sector Risk Ranking */}
      <div className="bg-gray-700/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Sector Risk Ranking</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-600">
                <th className="pb-2">Sector</th>
                <th className="pb-2">Risk Score</th>
                <th className="pb-2">Risk Level</th>
                <th className="pb-2">Total Incidents</th>
                <th className="pb-2">Violent Crimes</th>
              </tr>
            </thead>
            <tbody>
              {riskData?.sectors.map((sector, index) => (
                <tr key={sector.sector} className="border-b border-gray-700/50">
                  <td className="py-3 text-white font-medium">{sector.sector}</td>
                  <td className="py-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-600 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${(sector.overall_score / 5) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-white">{sector.overall_score.toFixed(1)}</span>
                    </div>
                  </td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(sector.risk_level)}`}>
                      {sector.risk_level.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 text-gray-300">{sector.total_incidents}</td>
                  <td className="py-3 text-red-400">{sector.violent_crimes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

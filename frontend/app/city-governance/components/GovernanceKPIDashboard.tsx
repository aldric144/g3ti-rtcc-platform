"use client";

import React, { useState, useEffect } from "react";

interface KPIMetric {
  metric_id: string;
  name: string;
  category: string;
  value: number;
  unit: string;
  target: number;
  threshold_warning: number;
  threshold_critical: number;
  trend: string;
  change_percent: number;
  status: string;
}

interface DepartmentScore {
  department: string;
  overall_score: number;
  trend: string;
  recommendations: string[];
}

interface CityHealthIndex {
  overall_score: number;
  component_scores: Record<string, number>;
  trend: string;
  change_from_previous: number;
  grade: string;
}

interface BudgetMetrics {
  total_budget: number;
  spent_to_date: number;
  projected_spend: number;
  variance: number;
  variance_percent: number;
  overtime_cost: number;
  overtime_hours: number;
  projected_overtime: number;
  budget_health: string;
}

interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export default function GovernanceKPIDashboard() {
  const [kpis, setKpis] = useState<KPIMetric[]>([]);
  const [cityHealth, setCityHealth] = useState<CityHealthIndex | null>(null);
  const [departmentScores, setDepartmentScores] = useState<DepartmentScore[]>([]);
  const [budgetMetrics, setBudgetMetrics] = useState<BudgetMetrics | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedPeriod, setSelectedPeriod] = useState<string>("daily");
  const [responseTimeSeries, setResponseTimeSeries] = useState<TimeSeriesPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockKPIs: KPIMetric[] = [
      { metric_id: "rt-police", name: "Police Response Time", category: "response_time", value: 4.8, unit: "minutes", target: 5.0, threshold_warning: 6.0, threshold_critical: 8.0, trend: "improving", change_percent: -2.5, status: "on_target" },
      { metric_id: "rt-fire", name: "Fire Response Time", category: "response_time", value: 3.9, unit: "minutes", target: 4.0, threshold_warning: 5.0, threshold_critical: 7.0, trend: "improving", change_percent: -1.8, status: "on_target" },
      { metric_id: "rt-ems", name: "EMS Response Time", category: "response_time", value: 5.5, unit: "minutes", target: 6.0, threshold_warning: 7.0, threshold_critical: 9.0, trend: "stable", change_percent: 0.5, status: "on_target" },
      { metric_id: "pe-coverage", name: "Zone Coverage", category: "patrol_efficiency", value: 87.5, unit: "percent", target: 90.0, threshold_warning: 85.0, threshold_critical: 75.0, trend: "improving", change_percent: 1.5, status: "warning" },
      { metric_id: "pe-calls", name: "Calls per Unit per Shift", category: "patrol_efficiency", value: 8.2, unit: "calls", target: 10.0, threshold_warning: 12.0, threshold_critical: 15.0, trend: "stable", change_percent: -0.8, status: "on_target" },
      { metric_id: "tr-congestion", name: "Traffic Congestion Score", category: "traffic", value: 28.5, unit: "score", target: 25.0, threshold_warning: 35.0, threshold_critical: 50.0, trend: "stable", change_percent: -1.2, status: "warning" },
      { metric_id: "ut-power", name: "Power Grid Uptime", category: "utility_uptime", value: 99.7, unit: "percent", target: 99.9, threshold_warning: 99.5, threshold_critical: 99.0, trend: "stable", change_percent: 0.1, status: "on_target" },
      { metric_id: "ut-water", name: "Water System Uptime", category: "utility_uptime", value: 99.85, unit: "percent", target: 99.9, threshold_warning: 99.5, threshold_critical: 99.0, trend: "stable", change_percent: 0.05, status: "on_target" },
      { metric_id: "fe-availability", name: "Fire/EMS Unit Availability", category: "fire_ems_readiness", value: 92.5, unit: "percent", target: 95.0, threshold_warning: 90.0, threshold_critical: 85.0, trend: "stable", change_percent: 0.5, status: "warning" },
      { metric_id: "fe-equipment", name: "Equipment Readiness", category: "fire_ems_readiness", value: 98.2, unit: "percent", target: 99.0, threshold_warning: 97.0, threshold_critical: 95.0, trend: "stable", change_percent: 0.2, status: "on_target" },
    ];

    const mockCityHealth: CityHealthIndex = {
      overall_score: 84.7,
      component_scores: {
        response_time: 92.5,
        patrol_efficiency: 82.3,
        traffic: 71.5,
        utilities: 99.2,
        fire_ems: 88.5,
      },
      trend: "improving",
      change_from_previous: 2.3,
      grade: "B",
    };

    const mockDepartmentScores: DepartmentScore[] = [
      { department: "Police", overall_score: 88.5, trend: "improving", recommendations: ["Continue proactive patrol initiatives", "Focus on response time in Zone 3"] },
      { department: "Fire", overall_score: 91.2, trend: "stable", recommendations: ["Maintain equipment readiness protocols", "Schedule additional training sessions"] },
      { department: "EMS", overall_score: 85.0, trend: "stable", recommendations: ["Monitor peak hour coverage", "Review mutual aid agreements"] },
      { department: "Public Works", overall_score: 78.5, trend: "improving", recommendations: ["Accelerate preventive maintenance schedule", "Review outage response procedures"] },
    ];

    const mockBudgetMetrics: BudgetMetrics = {
      total_budget: 45000000,
      spent_to_date: 38250000,
      projected_spend: 44100000,
      variance: 900000,
      variance_percent: 2.0,
      overtime_cost: 162500,
      overtime_hours: 2500,
      projected_overtime: 3000,
      budget_health: "healthy",
    };

    const mockTimeSeries: TimeSeriesPoint[] = Array.from({ length: 24 }, (_, i) => ({
      timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
      value: 4.5 + Math.sin(i / 4) * 0.5 + Math.random() * 0.3,
    }));

    setKpis(mockKPIs);
    setCityHealth(mockCityHealth);
    setDepartmentScores(mockDepartmentScores);
    setBudgetMetrics(mockBudgetMetrics);
    setResponseTimeSeries(mockTimeSeries);
    setLoading(false);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "on_target":
        return "text-green-400";
      case "warning":
        return "text-yellow-400";
      case "critical":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "improving":
        return (
          <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        );
      case "declining":
        return (
          <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
          </svg>
        );
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case "A":
        return "text-green-400 bg-green-500/20";
      case "B":
        return "text-blue-400 bg-blue-500/20";
      case "C":
        return "text-yellow-400 bg-yellow-500/20";
      case "D":
        return "text-orange-400 bg-orange-500/20";
      default:
        return "text-red-400 bg-red-500/20";
    }
  };

  const categories = [
    { id: "all", label: "All KPIs" },
    { id: "response_time", label: "Response Time" },
    { id: "patrol_efficiency", label: "Patrol Efficiency" },
    { id: "traffic", label: "Traffic" },
    { id: "utility_uptime", label: "Utilities" },
    { id: "fire_ems_readiness", label: "Fire/EMS" },
  ];

  const filteredKPIs = selectedCategory === "all" 
    ? kpis 
    : kpis.filter(k => k.category === selectedCategory);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {cityHealth && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-white">City Health Index</h2>
                <p className="text-sm text-gray-400">Overall city performance score</p>
              </div>
              <div className={`px-4 py-2 rounded-lg text-2xl font-bold ${getGradeColor(cityHealth.grade)}`}>
                {cityHealth.grade}
              </div>
            </div>
            <div className="flex items-center space-x-8 mb-6">
              <div>
                <div className="text-5xl font-bold text-white">{cityHealth.overall_score.toFixed(1)}</div>
                <div className="text-sm text-gray-400">out of 100</div>
              </div>
              <div className="flex items-center space-x-2">
                {getTrendIcon(cityHealth.trend)}
                <span className={`text-sm ${cityHealth.change_from_previous >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {cityHealth.change_from_previous >= 0 ? "+" : ""}{cityHealth.change_from_previous.toFixed(1)}%
                </span>
                <span className="text-sm text-gray-500">from last period</span>
              </div>
            </div>
            <div className="grid grid-cols-5 gap-4">
              {Object.entries(cityHealth.component_scores).map(([key, value]) => (
                <div key={key} className="text-center">
                  <div className="relative w-16 h-16 mx-auto">
                    <svg className="w-16 h-16 transform -rotate-90">
                      <circle cx="32" cy="32" r="28" stroke="#374151" strokeWidth="4" fill="none" />
                      <circle
                        cx="32"
                        cy="32"
                        r="28"
                        stroke={value >= 90 ? "#10B981" : value >= 70 ? "#3B82F6" : "#F59E0B"}
                        strokeWidth="4"
                        fill="none"
                        strokeDasharray={`${value * 1.76} 176`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-sm font-bold text-white">{value.toFixed(0)}</span>
                    </div>
                  </div>
                  <div className="mt-2 text-xs text-gray-400 capitalize">{key.replace(/_/g, " ")}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Department Scores</h3>
            <div className="space-y-4">
              {departmentScores.map((dept) => (
                <div key={dept.department} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">{dept.department}</span>
                    <div className="flex items-center space-x-2">
                      {getTrendIcon(dept.trend)}
                      <span className="text-white font-bold">{dept.overall_score.toFixed(1)}</span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        dept.overall_score >= 90 ? "bg-green-500" :
                        dept.overall_score >= 80 ? "bg-blue-500" :
                        dept.overall_score >= 70 ? "bg-yellow-500" :
                        "bg-red-500"
                      }`}
                      style={{ width: `${dept.overall_score}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="px-6 py-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Response Time Trendline</h3>
            <div className="flex space-x-2">
              {["daily", "weekly", "monthly"].map((period) => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    selectedPeriod === period
                      ? "bg-blue-600 text-white"
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  }`}
                >
                  {period.charAt(0).toUpperCase() + period.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="h-48 flex items-end space-x-1">
            {responseTimeSeries.map((point, i) => (
              <div key={i} className="flex-1 flex flex-col items-center">
                <div
                  className="w-full bg-blue-500 rounded-t hover:bg-blue-400 transition-colors cursor-pointer"
                  style={{ height: `${(point.value / 8) * 100}%` }}
                  title={`${point.value.toFixed(2)} min at ${new Date(point.timestamp).toLocaleTimeString()}`}
                ></div>
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>{new Date(responseTimeSeries[0]?.timestamp).toLocaleTimeString()}</span>
            <span>Target: 5.0 min</span>
            <span>{new Date(responseTimeSeries[responseTimeSeries.length - 1]?.timestamp).toLocaleTimeString()}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {budgetMetrics && (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Budget & Overtime</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-400">Budget Utilization</span>
                  <span className="text-white">
                    ${(budgetMetrics.spent_to_date / 1000000).toFixed(1)}M / ${(budgetMetrics.total_budget / 1000000).toFixed(1)}M
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${
                      budgetMetrics.budget_health === "healthy" ? "bg-green-500" : "bg-yellow-500"
                    }`}
                    style={{ width: `${(budgetMetrics.spent_to_date / budgetMetrics.total_budget) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400">Projected Variance</div>
                  <div className={`text-xl font-bold ${budgetMetrics.variance >= 0 ? "text-green-400" : "text-red-400"}`}>
                    {budgetMetrics.variance >= 0 ? "+" : ""}${(budgetMetrics.variance / 1000).toFixed(0)}K
                  </div>
                  <div className="text-xs text-gray-500">{budgetMetrics.variance_percent.toFixed(1)}% under budget</div>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <div className="text-sm text-gray-400">Overtime Cost</div>
                  <div className="text-xl font-bold text-yellow-400">
                    ${(budgetMetrics.overtime_cost / 1000).toFixed(0)}K
                  </div>
                  <div className="text-xs text-gray-500">{budgetMetrics.overtime_hours.toLocaleString()} hours</div>
                </div>
              </div>
              <div className="pt-4 border-t border-gray-700">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Overtime Forecast</h4>
                <div className="flex items-center space-x-4">
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-yellow-500"
                      style={{ width: `${(budgetMetrics.overtime_hours / budgetMetrics.projected_overtime) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-400">
                    {budgetMetrics.overtime_hours.toLocaleString()} / {budgetMetrics.projected_overtime.toLocaleString()} hrs
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Fire/EMS Coverage Map</h3>
          <div className="grid grid-cols-3 gap-3">
            {[
              { zone: "Downtown", coverage: 95, units: 2 },
              { zone: "Singer Island", coverage: 88, units: 1 },
              { zone: "Westside", coverage: 82, units: 2 },
              { zone: "Marina", coverage: 90, units: 1 },
              { zone: "Industrial", coverage: 75, units: 1 },
              { zone: "North", coverage: 78, units: 1 },
            ].map((zone) => (
              <div
                key={zone.zone}
                className={`p-3 rounded-lg border ${
                  zone.coverage >= 90 ? "bg-green-500/10 border-green-500/30" :
                  zone.coverage >= 80 ? "bg-blue-500/10 border-blue-500/30" :
                  "bg-yellow-500/10 border-yellow-500/30"
                }`}
              >
                <div className="text-sm font-medium text-white">{zone.zone}</div>
                <div className="text-2xl font-bold text-white">{zone.coverage}%</div>
                <div className="text-xs text-gray-400">{zone.units} units</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700">
        <div className="px-6 py-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">KPI Metrics</h3>
            <div className="flex space-x-2">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    selectedCategory === cat.id
                      ? "bg-blue-600 text-white"
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredKPIs.map((kpi) => (
              <div key={kpi.metric_id} className="bg-gray-700/50 rounded-lg p-4 border border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">{kpi.name}</span>
                  {getTrendIcon(kpi.trend)}
                </div>
                <div className="flex items-baseline space-x-2">
                  <span className={`text-2xl font-bold ${getStatusColor(kpi.status)}`}>
                    {kpi.value.toFixed(1)}
                  </span>
                  <span className="text-sm text-gray-400">{kpi.unit}</span>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="text-gray-500">Target: {kpi.target} {kpi.unit}</span>
                  <span className={kpi.change_percent >= 0 ? "text-green-400" : "text-red-400"}>
                    {kpi.change_percent >= 0 ? "+" : ""}{kpi.change_percent.toFixed(1)}%
                  </span>
                </div>
                <div className="mt-2 w-full bg-gray-600 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${
                      kpi.status === "on_target" ? "bg-green-500" :
                      kpi.status === "warning" ? "bg-yellow-500" :
                      "bg-red-500"
                    }`}
                    style={{ width: `${Math.min((kpi.value / kpi.threshold_critical) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Traffic Congestion Score</h3>
          <div className="flex items-center justify-center">
            <div className="relative w-48 h-48">
              <svg className="w-48 h-48 transform -rotate-90">
                <circle cx="96" cy="96" r="88" stroke="#374151" strokeWidth="12" fill="none" />
                <circle
                  cx="96"
                  cy="96"
                  r="88"
                  stroke="#3B82F6"
                  strokeWidth="12"
                  fill="none"
                  strokeDasharray={`${(100 - 28.5) * 5.53} 553`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold text-white">28.5</span>
                <span className="text-sm text-gray-400">Congestion Score</span>
              </div>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs">
            <div className="bg-green-500/20 rounded p-2">
              <div className="text-green-400 font-medium">Low</div>
              <div className="text-gray-400">&lt; 25</div>
            </div>
            <div className="bg-yellow-500/20 rounded p-2">
              <div className="text-yellow-400 font-medium">Moderate</div>
              <div className="text-gray-400">25-50</div>
            </div>
            <div className="bg-red-500/20 rounded p-2">
              <div className="text-red-400 font-medium">High</div>
              <div className="text-gray-400">&gt; 50</div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Crowd Density Forecast</h3>
          <div className="space-y-3">
            {[
              { time: "Now", density: 35, location: "Downtown" },
              { time: "+2 hours", density: 55, location: "Marina" },
              { time: "+4 hours", density: 70, location: "Beach Area" },
              { time: "+6 hours", density: 45, location: "Downtown" },
            ].map((forecast, i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="w-20 text-sm text-gray-400">{forecast.time}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-white">{forecast.location}</span>
                    <span className={
                      forecast.density >= 60 ? "text-red-400" :
                      forecast.density >= 40 ? "text-yellow-400" :
                      "text-green-400"
                    }>
                      {forecast.density}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        forecast.density >= 60 ? "bg-red-500" :
                        forecast.density >= 40 ? "bg-yellow-500" :
                        "bg-green-500"
                      }`}
                      style={{ width: `${forecast.density}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Utility Uptime</h3>
          <span className="text-sm text-gray-400">Last 30 days</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { name: "Power Grid", uptime: 99.7, incidents: 2, mttr: 45 },
            { name: "Water System", uptime: 99.85, incidents: 1, mttr: 30 },
            { name: "Communications", uptime: 99.95, incidents: 0, mttr: 0 },
          ].map((utility) => (
            <div key={utility.name} className="bg-gray-700/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="font-medium text-white">{utility.name}</span>
                <span className={`text-lg font-bold ${
                  utility.uptime >= 99.9 ? "text-green-400" :
                  utility.uptime >= 99.5 ? "text-blue-400" :
                  "text-yellow-400"
                }`}>
                  {utility.uptime}%
                </span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2 mb-3">
                <div
                  className={`h-2 rounded-full ${
                    utility.uptime >= 99.9 ? "bg-green-500" :
                    utility.uptime >= 99.5 ? "bg-blue-500" :
                    "bg-yellow-500"
                  }`}
                  style={{ width: `${utility.uptime}%` }}
                ></div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-500">Incidents</span>
                  <div className="text-white font-medium">{utility.incidents}</div>
                </div>
                <div>
                  <span className="text-gray-500">Avg MTTR</span>
                  <div className="text-white font-medium">{utility.mttr > 0 ? `${utility.mttr} min` : "N/A"}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

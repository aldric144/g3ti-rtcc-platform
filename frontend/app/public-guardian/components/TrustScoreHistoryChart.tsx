"use client";

import React, { useState, useEffect } from "react";

interface HistoryPoint {
  date: string;
  score: number;
}

interface TrustHistory {
  average_score: number;
  min_score: number;
  max_score: number;
  trend: number;
  points: HistoryPoint[];
}

export default function TrustScoreHistoryChart() {
  const [data, setData] = useState<TrustHistory | null>(null);
  const [period, setPeriod] = useState<"30" | "90" | "365">("30");

  useEffect(() => {
    const points: HistoryPoint[] = [];
    const now = new Date();
    const days = parseInt(period);

    for (let i = days; i >= 0; i -= Math.ceil(days / 12)) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      points.push({
        date: date.toISOString().split("T")[0],
        score: 68 + Math.random() * 10,
      });
    }

    const scores = points.map((p) => p.score);
    setData({
      average_score: scores.reduce((a, b) => a + b, 0) / scores.length,
      min_score: Math.min(...scores),
      max_score: Math.max(...scores),
      trend: points[points.length - 1].score - points[0].score,
      points,
    });
  }, [period]);

  if (!data) {
    return (
      <div className="bg-white rounded-lg border p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-48 bg-gray-200 rounded"></div>
      </div>
    );
  }

  const maxScore = Math.max(...data.points.map((p) => p.score));
  const minScore = Math.min(...data.points.map((p) => p.score));
  const range = maxScore - minScore || 1;

  const getY = (score: number): number => {
    return 150 - ((score - minScore) / range) * 130;
  };

  const pathD = data.points
    .map((point, index) => {
      const x = (index / (data.points.length - 1)) * 580 + 10;
      const y = getY(point.score);
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Trust Score History</h3>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value as typeof period)}
          className="text-sm border rounded-md px-2 py-1"
        >
          <option value="30">Last 30 Days</option>
          <option value="90">Last 90 Days</option>
          <option value="365">Last Year</option>
        </select>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-4">
        <div className="text-center p-2 bg-blue-50 rounded">
          <p className="text-lg font-bold text-blue-900">{data.average_score.toFixed(1)}</p>
          <p className="text-xs text-blue-600">Average</p>
        </div>
        <div className="text-center p-2 bg-green-50 rounded">
          <p className="text-lg font-bold text-green-900">{data.max_score.toFixed(1)}</p>
          <p className="text-xs text-green-600">Max</p>
        </div>
        <div className="text-center p-2 bg-yellow-50 rounded">
          <p className="text-lg font-bold text-yellow-900">{data.min_score.toFixed(1)}</p>
          <p className="text-xs text-yellow-600">Min</p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <p className={`text-lg font-bold ${data.trend >= 0 ? "text-green-600" : "text-red-600"}`}>
            {data.trend >= 0 ? "+" : ""}{data.trend.toFixed(1)}
          </p>
          <p className="text-xs text-gray-600">Trend</p>
        </div>
      </div>

      <div className="relative h-48 bg-gray-50 rounded-lg overflow-hidden">
        <svg width="100%" height="100%" viewBox="0 0 600 160" preserveAspectRatio="none">
          <defs>
            <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
            </linearGradient>
          </defs>

          {[0, 25, 50, 75, 100].map((pct) => (
            <line
              key={pct}
              x1="10"
              y1={150 - (pct / 100) * 130}
              x2="590"
              y2={150 - (pct / 100) * 130}
              stroke="#e5e7eb"
              strokeWidth="1"
            />
          ))}

          <path
            d={`${pathD} L 590 150 L 10 150 Z`}
            fill="url(#chartGradient)"
          />

          <path
            d={pathD}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {data.points.map((point, index) => {
            const x = (index / (data.points.length - 1)) * 580 + 10;
            const y = getY(point.score);
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r="4"
                fill="#3b82f6"
                className="hover:r-6 transition-all"
              />
            );
          })}
        </svg>

        <div className="absolute bottom-0 left-0 right-0 flex justify-between px-2 text-xs text-gray-500">
          {data.points.filter((_, i) => i % 3 === 0).map((point, index) => (
            <span key={index}>{new Date(point.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

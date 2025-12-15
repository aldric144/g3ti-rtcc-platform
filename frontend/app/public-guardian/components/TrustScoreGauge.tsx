"use client";

import React, { useState, useEffect } from "react";

interface TrustScoreData {
  overall_score: number;
  trust_level: string;
  trend_vs_previous: number;
  confidence: number;
  fairness_audit_passed: boolean;
  bias_audit_passed: boolean;
}

export default function TrustScoreGauge() {
  const [data, setData] = useState<TrustScoreData | null>(null);

  useEffect(() => {
    setData({
      overall_score: 72.5,
      trust_level: "high",
      trend_vs_previous: 2.3,
      confidence: 0.92,
      fairness_audit_passed: true,
      bias_audit_passed: true,
    });
  }, []);

  const getScoreColor = (score: number): string => {
    if (score >= 80) return "#22c55e";
    if (score >= 65) return "#3b82f6";
    if (score >= 50) return "#eab308";
    if (score >= 35) return "#f97316";
    return "#ef4444";
  };

  const getLevelLabel = (level: string): string => {
    switch (level) {
      case "very_high":
        return "Very High";
      case "high":
        return "High";
      case "moderate":
        return "Moderate";
      case "low":
        return "Low";
      case "very_low":
        return "Very Low";
      default:
        return level;
    }
  };

  if (!data) {
    return (
      <div className="bg-white rounded-lg border p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-48 bg-gray-200 rounded"></div>
      </div>
    );
  }

  const scoreColor = getScoreColor(data.overall_score);
  const circumference = 2 * Math.PI * 80;
  const strokeDashoffset = circumference - (data.overall_score / 100) * circumference;

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Community Trust Score</h3>

      <div className="flex flex-col items-center">
        <div className="relative w-48 h-48">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
            <circle
              cx="100"
              cy="100"
              r="80"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="16"
            />
            <circle
              cx="100"
              cy="100"
              r="80"
              fill="none"
              stroke={scoreColor}
              strokeWidth="16"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-bold" style={{ color: scoreColor }}>
              {data.overall_score}
            </span>
            <span className="text-sm text-gray-500">out of 100</span>
          </div>
        </div>

        <div className="mt-4 text-center">
          <span
            className="text-lg font-medium px-3 py-1 rounded-full"
            style={{ backgroundColor: `${scoreColor}20`, color: scoreColor }}
          >
            {getLevelLabel(data.trust_level)}
          </span>
        </div>

        <div className="mt-4 w-full grid grid-cols-2 gap-4">
          <div className="text-center p-2 bg-gray-50 rounded">
            <p className={`text-lg font-bold ${data.trend_vs_previous >= 0 ? "text-green-600" : "text-red-600"}`}>
              {data.trend_vs_previous >= 0 ? "+" : ""}{data.trend_vs_previous}
            </p>
            <p className="text-xs text-gray-500">vs Previous</p>
          </div>
          <div className="text-center p-2 bg-gray-50 rounded">
            <p className="text-lg font-bold text-blue-600">
              {(data.confidence * 100).toFixed(0)}%
            </p>
            <p className="text-xs text-gray-500">Confidence</p>
          </div>
        </div>

        <div className="mt-4 w-full space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Fairness Audit</span>
            <span className={data.fairness_audit_passed ? "text-green-600" : "text-red-600"}>
              {data.fairness_audit_passed ? "Passed" : "Failed"}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Bias Audit</span>
            <span className={data.bias_audit_passed ? "text-green-600" : "text-red-600"}>
              {data.bias_audit_passed ? "Passed" : "Failed"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

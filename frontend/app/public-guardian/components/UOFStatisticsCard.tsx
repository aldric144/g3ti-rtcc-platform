"use client";

import React, { useState, useEffect } from "react";

interface UOFData {
  total_incidents: number;
  by_type: Record<string, number>;
  by_outcome: Record<string, number>;
  de_escalation_success_rate: number;
  complaints_filed: number;
  complaints_sustained: number;
  per_1000_contacts: number;
  trend_vs_previous: number;
}

export default function UOFStatisticsCard() {
  const [data, setData] = useState<UOFData | null>(null);

  useEffect(() => {
    setData({
      total_incidents: 12,
      by_type: {
        verbal_commands: 5,
        physical_control: 4,
        taser: 2,
        oc_spray: 1,
        firearm_displayed: 0,
      },
      by_outcome: {
        no_injury: 8,
        minor_injury: 3,
        medical_attention: 1,
      },
      de_escalation_success_rate: 78.5,
      complaints_filed: 2,
      complaints_sustained: 0,
      per_1000_contacts: 1.2,
      trend_vs_previous: -8.2,
    });
  }, []);

  if (!data) {
    return (
      <div className="bg-white rounded-lg border p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Use of Force Statistics</h3>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          Aggregated & Redacted
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-900">{data.total_incidents}</p>
          <p className="text-xs text-blue-600">Total Incidents</p>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <p className="text-2xl font-bold text-green-900">
            {data.de_escalation_success_rate}%
          </p>
          <p className="text-xs text-green-600">De-escalation Rate</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-gray-900">{data.per_1000_contacts}</p>
          <p className="text-xs text-gray-600">Per 1,000 Contacts</p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-2">By Type</p>
        <div className="space-y-2">
          {Object.entries(data.by_type).map(([type, count]) => (
            <div key={type} className="flex items-center justify-between">
              <span className="text-xs text-gray-600 capitalize">
                {type.replace(/_/g, " ")}
              </span>
              <span className="text-xs font-medium text-gray-900">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-2">Outcomes</p>
        <div className="space-y-2">
          {Object.entries(data.by_outcome).map(([outcome, count]) => (
            <div key={outcome} className="flex items-center justify-between">
              <span className="text-xs text-gray-600 capitalize">
                {outcome.replace(/_/g, " ")}
              </span>
              <span className="text-xs font-medium text-gray-900">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-4 border-t">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Complaints Filed</span>
          <span className="text-sm font-medium text-gray-900">{data.complaints_filed}</span>
        </div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Complaints Sustained</span>
          <span className="text-sm font-medium text-gray-900">{data.complaints_sustained}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Trend vs Previous</span>
          <span className={`text-sm font-medium ${
            data.trend_vs_previous < 0 ? "text-green-600" : "text-red-600"
          }`}>
            {data.trend_vs_previous > 0 ? "+" : ""}{data.trend_vs_previous}%
          </span>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import TransparencyMetricsPanel from "./components/TransparencyMetricsPanel";
import ResponseTimeCard from "./components/ResponseTimeCard";
import UOFStatisticsCard from "./components/UOFStatisticsCard";
import SafetyTrendCharts from "./components/SafetyTrendCharts";
import CommunityHeatmap from "./components/CommunityHeatmap";
import EventsList from "./components/EventsList";
import AlertsFeed from "./components/AlertsFeed";
import EngagementCalendar from "./components/EngagementCalendar";
import TrustScoreGauge from "./components/TrustScoreGauge";
import TrustScoreHistoryChart from "./components/TrustScoreHistoryChart";
import NeighborhoodSentimentMap from "./components/NeighborhoodSentimentMap";
import FeedbackForm from "./components/FeedbackForm";
import FeedbackSentimentPanel from "./components/FeedbackSentimentPanel";
import CommonConcernsList from "./components/CommonConcernsList";

type TabType = "transparency" | "engagement" | "trust" | "feedback";

interface Statistics {
  transparency: {
    reports_generated: number;
    weekly_reports: number;
    monthly_reports: number;
  };
  engagement: {
    events_created: number;
    alerts_sent: number;
    total_attendance: number;
  };
  trust_score: {
    current_score: number;
    current_level: string;
    neighborhoods_tracked: number;
  };
  feedback: {
    total_feedback: number;
    resolved_feedback: number;
    sentiment_analyses: number;
  };
}

export default function PublicGuardianPage() {
  const [activeTab, setActiveTab] = useState<TabType>("transparency");
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        setStatistics({
          transparency: {
            reports_generated: 156,
            weekly_reports: 52,
            monthly_reports: 12,
          },
          engagement: {
            events_created: 48,
            alerts_sent: 23,
            total_attendance: 2450,
          },
          trust_score: {
            current_score: 72.5,
            current_level: "high",
            neighborhoods_tracked: 5,
          },
          feedback: {
            total_feedback: 342,
            resolved_feedback: 298,
            sentiment_analyses: 342,
          },
        });
      } catch (error) {
        console.error("Failed to fetch statistics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, []);

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "transparency", label: "Transparency Dashboard", icon: "📊" },
    { id: "engagement", label: "Community Engagement", icon: "🤝" },
    { id: "trust", label: "Trust Score", icon: "⭐" },
    { id: "feedback", label: "Public Feedback", icon: "💬" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-blue-900 to-blue-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Public Safety Guardian</h1>
              <p className="text-blue-200 mt-1">
                Community Transparency & Engagement Portal
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-blue-200">Riviera Beach Police Department</p>
                <p className="text-xs text-blue-300">
                  Last Updated: {new Date().toLocaleString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                <span className="text-2xl">🛡️</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {statistics && (
        <div className="bg-white border-b shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-900">
                  {statistics.transparency.reports_generated}
                </p>
                <p className="text-sm text-blue-600">Reports Generated</p>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-900">
                  {statistics.engagement.events_created}
                </p>
                <p className="text-sm text-green-600">Community Events</p>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <p className="text-2xl font-bold text-yellow-900">
                  {statistics.trust_score.current_score}
                </p>
                <p className="text-sm text-yellow-600">Trust Score</p>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <p className="text-2xl font-bold text-purple-900">
                  {statistics.feedback.total_feedback}
                </p>
                <p className="text-sm text-purple-600">Feedback Received</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b">
            <nav className="flex space-x-1 p-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === tab.id
                      ? "bg-blue-900 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div>
              </div>
            ) : (
              <>
                {activeTab === "transparency" && (
                  <div className="space-y-6">
                    <h2 className="text-xl font-semibold text-gray-900">
                      Public Transparency Dashboard
                    </h2>
                    <p className="text-gray-600">
                      View aggregated, redacted statistics about police department
                      operations and community safety.
                    </p>
                    <div className="grid grid-cols-2 gap-6">
                      <TransparencyMetricsPanel />
                      <ResponseTimeCard />
                    </div>
                    <div className="grid grid-cols-2 gap-6">
                      <UOFStatisticsCard />
                      <SafetyTrendCharts />
                    </div>
                    <CommunityHeatmap />
                  </div>
                )}

                {activeTab === "engagement" && (
                  <div className="space-y-6">
                    <h2 className="text-xl font-semibold text-gray-900">
                      Community Engagement Center
                    </h2>
                    <p className="text-gray-600">
                      Stay informed about community events, safety alerts, and
                      engagement opportunities.
                    </p>
                    <div className="grid grid-cols-2 gap-6">
                      <EventsList />
                      <AlertsFeed />
                    </div>
                    <EngagementCalendar />
                  </div>
                )}

                {activeTab === "trust" && (
                  <div className="space-y-6">
                    <h2 className="text-xl font-semibold text-gray-900">
                      Community Trust Score Dashboard
                    </h2>
                    <p className="text-gray-600">
                      Track community trust metrics and neighborhood sentiment
                      across Riviera Beach.
                    </p>
                    <div className="grid grid-cols-3 gap-6">
                      <TrustScoreGauge />
                      <div className="col-span-2">
                        <TrustScoreHistoryChart />
                      </div>
                    </div>
                    <NeighborhoodSentimentMap />
                  </div>
                )}

                {activeTab === "feedback" && (
                  <div className="space-y-6">
                    <h2 className="text-xl font-semibold text-gray-900">
                      Public Feedback Console
                    </h2>
                    <p className="text-gray-600">
                      Share your feedback, concerns, and suggestions with the
                      Riviera Beach Police Department.
                    </p>
                    <div className="grid grid-cols-2 gap-6">
                      <FeedbackForm />
                      <FeedbackSentimentPanel />
                    </div>
                    <CommonConcernsList />
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <footer className="text-center text-gray-500 text-sm py-4">
          <p>
            Riviera Beach Police Department - Public Safety Guardian Portal
          </p>
          <p className="mt-1">
            All data is automatically redacted for public release in compliance
            with CJIS, VAWA, HIPAA, and Florida Public Records laws.
          </p>
        </footer>
      </div>
    </div>
  );
}

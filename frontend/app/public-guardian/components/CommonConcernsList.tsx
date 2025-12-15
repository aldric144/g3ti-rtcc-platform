"use client";

import React, { useState, useEffect } from "react";

interface Concern {
  category: string;
  count: number;
  percentage: number;
}

interface RecentFeedback {
  id: string;
  title: string;
  sentiment: string;
  category: string;
  neighborhood: string;
  created_at: string;
}

export default function CommonConcernsList() {
  const [concerns, setConcerns] = useState<Concern[]>([]);
  const [recentFeedback, setRecentFeedback] = useState<RecentFeedback[]>([]);
  const [view, setView] = useState<"concerns" | "recent">("concerns");

  useEffect(() => {
    setConcerns([
      { category: "response_time", count: 28, percentage: 35.4 },
      { category: "safety_concerns", count: 22, percentage: 27.8 },
      { category: "traffic", count: 15, percentage: 19.0 },
      { category: "property_crime", count: 8, percentage: 10.1 },
      { category: "noise", count: 6, percentage: 7.6 },
    ]);

    setRecentFeedback([
      {
        id: "1",
        title: "Great response to my call",
        sentiment: "very_positive",
        category: "officer_conduct",
        neighborhood: "Singer Island",
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "2",
        title: "Speeding on Blue Heron",
        sentiment: "negative",
        category: "traffic",
        neighborhood: "Downtown Riviera Beach",
        created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "3",
        title: "Youth basketball program suggestion",
        sentiment: "positive",
        category: "community_programs",
        neighborhood: "West Riviera Beach",
        created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "4",
        title: "Noise complaint - construction",
        sentiment: "negative",
        category: "noise",
        neighborhood: "Riviera Beach Heights",
        created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "5",
        title: "Thank you for the town hall",
        sentiment: "positive",
        category: "communication",
        neighborhood: "Port of Palm Beach Area",
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      },
    ]);
  }, []);

  const getCategoryIcon = (category: string): string => {
    switch (category) {
      case "response_time":
        return "⏱️";
      case "safety_concerns":
        return "🛡️";
      case "traffic":
        return "🚗";
      case "property_crime":
        return "🏠";
      case "noise":
        return "🔊";
      case "officer_conduct":
        return "👮";
      case "community_programs":
        return "🤝";
      case "communication":
        return "📢";
      default:
        return "📋";
    }
  };

  const getCategoryLabel = (category: string): string => {
    return category.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const getSentimentColor = (sentiment: string): string => {
    switch (sentiment) {
      case "very_positive":
        return "bg-green-100 text-green-800";
      case "positive":
        return "bg-green-50 text-green-700";
      case "neutral":
        return "bg-gray-100 text-gray-700";
      case "negative":
        return "bg-orange-100 text-orange-800";
      case "very_negative":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  const formatTimeAgo = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}d ago`;
    if (diffHours > 0) return `${diffHours}h ago`;
    return "Just now";
  };

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Community Voices</h3>
        <div className="flex space-x-1">
          <button
            onClick={() => setView("concerns")}
            className={`px-3 py-1 text-sm rounded ${
              view === "concerns"
                ? "bg-blue-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Top Concerns
          </button>
          <button
            onClick={() => setView("recent")}
            className={`px-3 py-1 text-sm rounded ${
              view === "recent"
                ? "bg-blue-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Recent Feedback
          </button>
        </div>
      </div>

      {view === "concerns" ? (
        <div className="space-y-3">
          {concerns.map((concern, index) => (
            <div
              key={concern.category}
              className="flex items-center p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center justify-center w-8 h-8 bg-white rounded-full mr-3 text-lg">
                {getCategoryIcon(concern.category)}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-900">
                    {getCategoryLabel(concern.category)}
                  </span>
                  <span className="text-sm text-gray-600">
                    {concern.count} reports
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${concern.percentage}%` }}
                  ></div>
                </div>
              </div>
              <span className="ml-3 text-sm font-medium text-gray-500">
                #{index + 1}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {recentFeedback.map((feedback) => (
            <div
              key={feedback.id}
              className="p-3 border rounded-lg hover:shadow-sm transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <span className="text-xl">{getCategoryIcon(feedback.category)}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {feedback.title}
                    </p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-xs text-gray-500">
                        {feedback.neighborhood}
                      </span>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-500">
                        {formatTimeAgo(feedback.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded ${getSentimentColor(
                    feedback.sentiment
                  )}`}
                >
                  {feedback.sentiment.replace("_", " ")}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t text-center">
        <p className="text-xs text-gray-500">
          All feedback is anonymized and aggregated to protect privacy
        </p>
      </div>
    </div>
  );
}

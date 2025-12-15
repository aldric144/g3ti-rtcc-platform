"use client";

import React, { useState, useEffect } from "react";

interface SentimentData {
  total: number;
  average_sentiment: number;
  distribution: {
    very_positive: number;
    positive: number;
    neutral: number;
    negative: number;
    very_negative: number;
  };
  positive_percentage: number;
  negative_percentage: number;
}

export default function FeedbackSentimentPanel() {
  const [data, setData] = useState<SentimentData | null>(null);

  useEffect(() => {
    setData({
      total: 342,
      average_sentiment: 0.25,
      distribution: {
        very_positive: 45,
        positive: 98,
        neutral: 120,
        negative: 58,
        very_negative: 21,
      },
      positive_percentage: 41.8,
      negative_percentage: 23.1,
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

  const getSentimentColor = (sentiment: string): string => {
    switch (sentiment) {
      case "very_positive":
        return "bg-green-500";
      case "positive":
        return "bg-green-300";
      case "neutral":
        return "bg-gray-400";
      case "negative":
        return "bg-orange-400";
      case "very_negative":
        return "bg-red-500";
      default:
        return "bg-gray-300";
    }
  };

  const getSentimentLabel = (sentiment: string): string => {
    return sentiment.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const total = Object.values(data.distribution).reduce((a, b) => a + b, 0);

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Community Sentiment</h3>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-900">{data.total}</p>
          <p className="text-xs text-blue-600">Total Feedback</p>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <p className="text-2xl font-bold text-green-900">{data.positive_percentage}%</p>
          <p className="text-xs text-green-600">Positive</p>
        </div>
        <div className="text-center p-3 bg-red-50 rounded-lg">
          <p className="text-2xl font-bold text-red-900">{data.negative_percentage}%</p>
          <p className="text-xs text-red-600">Negative</p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-2">Average Sentiment</p>
        <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="absolute left-1/2 h-full w-1 bg-gray-800 z-10"
            style={{ transform: "translateX(-50%)" }}
          ></div>
          <div
            className={`h-full ${data.average_sentiment >= 0 ? "bg-green-500" : "bg-red-500"} rounded-full`}
            style={{
              width: `${Math.abs(data.average_sentiment) * 50}%`,
              marginLeft: data.average_sentiment >= 0 ? "50%" : `${50 - Math.abs(data.average_sentiment) * 50}%`,
            }}
          ></div>
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Very Negative</span>
          <span>Neutral</span>
          <span>Very Positive</span>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-2">Sentiment Distribution</p>
        <div className="flex h-8 rounded-lg overflow-hidden">
          {Object.entries(data.distribution).map(([sentiment, count]) => (
            <div
              key={sentiment}
              className={`${getSentimentColor(sentiment)} transition-all`}
              style={{ width: `${(count / total) * 100}%` }}
              title={`${getSentimentLabel(sentiment)}: ${count} (${((count / total) * 100).toFixed(1)}%)`}
            ></div>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        {Object.entries(data.distribution).map(([sentiment, count]) => (
          <div key={sentiment} className="flex items-center justify-between">
            <div className="flex items-center">
              <div className={`w-3 h-3 ${getSentimentColor(sentiment)} rounded mr-2`}></div>
              <span className="text-sm text-gray-600">{getSentimentLabel(sentiment)}</span>
            </div>
            <div className="flex items-center">
              <span className="text-sm font-medium text-gray-900 mr-2">{count}</span>
              <span className="text-xs text-gray-500">
                ({((count / total) * 100).toFixed(1)}%)
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import {
  Lightbulb,
  ChevronRight,
  Clock,
  Target,
  AlertCircle,
  CheckCircle,
  ArrowRight,
} from 'lucide-react';

interface Prediction {
  id: string;
  type: string;
  description: string;
  probability: number;
  time_horizon: string;
  entities: string[];
}

interface AIRecommendationsProps {
  recommendations: string[];
  predictions: Prediction[];
}

const predictionTypeConfig: Record<string, { icon: typeof Target; color: string }> = {
  vehicle_trajectory: {
    icon: Target,
    color: 'text-green-600 dark:text-green-400',
  },
  crime_heat: {
    icon: AlertCircle,
    color: 'text-red-600 dark:text-red-400',
  },
  gunfire_recurrence: {
    icon: Target,
    color: 'text-orange-600 dark:text-orange-400',
  },
  offender_pathway: {
    icon: ArrowRight,
    color: 'text-purple-600 dark:text-purple-400',
  },
};

function ProbabilityBadge({ probability }: { probability: number }) {
  const percentage = Math.min(100, Math.max(0, probability * 100));
  const getColor = () => {
    if (percentage >= 80) return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
    if (percentage >= 60)
      return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400';
    if (percentage >= 40)
      return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400';
    return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
  };

  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getColor()}`}>
      {percentage.toFixed(0)}% likely
    </span>
  );
}

function PredictionCard({ prediction }: { prediction: Prediction }) {
  const [expanded, setExpanded] = useState(false);
  const config = predictionTypeConfig[prediction.type] || {
    icon: Target,
    color: 'text-gray-600 dark:text-gray-400',
  };
  const Icon = config.icon;

  return (
    <div
      className="cursor-pointer rounded-lg border border-gray-200 bg-gray-50 p-3 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800/50 dark:hover:bg-gray-800"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-2">
          <Icon className={`mt-0.5 h-4 w-4 ${config.color}`} />
          <div>
            <p className="text-sm text-gray-700 dark:text-gray-300">{prediction.description}</p>
            <div className="mt-1 flex items-center gap-2">
              <ProbabilityBadge probability={prediction.probability} />
              <span className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                <Clock className="h-3 w-3" />
                {prediction.time_horizon}
              </span>
            </div>
          </div>
        </div>
        <ChevronRight
          className={`h-4 w-4 text-gray-400 transition-transform ${expanded ? 'rotate-90' : ''}`}
        />
      </div>

      {expanded && prediction.entities.length > 0 && (
        <div className="mt-3 border-t border-gray-200 pt-3 dark:border-gray-700">
          <p className="mb-2 text-xs font-medium text-gray-500 dark:text-gray-400">
            Related Entities
          </p>
          <div className="flex flex-wrap gap-1">
            {prediction.entities.map((entity, index) => (
              <span
                key={index}
                className="inline-flex items-center rounded-full bg-white px-2 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300"
              >
                {entity}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function RecommendationItem({ recommendation, index }: { recommendation: string; index: number }) {
  const [completed, setCompleted] = useState(false);

  return (
    <div
      className={`flex items-start gap-3 rounded-lg p-3 transition-colors ${
        completed ? 'bg-green-50 dark:bg-green-900/20' : 'bg-gray-50 dark:bg-gray-800/50'
      }`}
    >
      <button
        onClick={() => setCompleted(!completed)}
        className={`mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
          completed
            ? 'border-green-500 bg-green-500 text-white'
            : 'border-gray-300 hover:border-indigo-500 dark:border-gray-600'
        }`}
      >
        {completed && <CheckCircle className="h-3 w-3" />}
      </button>
      <p
        className={`text-sm ${
          completed
            ? 'text-gray-500 line-through dark:text-gray-400'
            : 'text-gray-700 dark:text-gray-300'
        }`}
      >
        {recommendation}
      </p>
    </div>
  );
}

export function AIRecommendations({ recommendations, predictions }: AIRecommendationsProps) {
  const hasContent = recommendations.length > 0 || predictions.length > 0;

  if (!hasContent) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <Lightbulb className="h-12 w-12 text-gray-300 dark:text-gray-600" />
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          No recommendations available
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500">
          Run a query to get AI-powered recommendations
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {predictions.length > 0 && (
        <div>
          <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Predictions
          </h3>
          <div className="space-y-2">
            {predictions.map((prediction) => (
              <PredictionCard key={prediction.id} prediction={prediction} />
            ))}
          </div>
        </div>
      )}

      {recommendations.length > 0 && (
        <div>
          <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Recommended Actions
          </h3>
          <div className="space-y-2">
            {recommendations.map((recommendation, index) => (
              <RecommendationItem key={index} recommendation={recommendation} index={index} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

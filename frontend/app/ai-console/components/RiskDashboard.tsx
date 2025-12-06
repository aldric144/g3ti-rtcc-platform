'use client';

import { Shield, AlertTriangle, User, Car, MapPin, Crosshair } from 'lucide-react';

interface RiskFactor {
  name: string;
  weight: number;
  value: number;
  contribution: number;
}

interface RiskScore {
  entity_id: string;
  entity_type: string;
  score: number;
  level: string;
  factors: RiskFactor[];
  last_updated: string;
}

interface RiskDashboardProps {
  riskScores: Record<string, RiskScore>;
}

const riskLevelConfig: Record<string, { color: string; bgColor: string; borderColor: string }> = {
  critical: {
    color: 'text-red-700 dark:text-red-400',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    borderColor: 'border-red-200 dark:border-red-800',
  },
  high: {
    color: 'text-orange-700 dark:text-orange-400',
    bgColor: 'bg-orange-50 dark:bg-orange-900/20',
    borderColor: 'border-orange-200 dark:border-orange-800',
  },
  medium: {
    color: 'text-yellow-700 dark:text-yellow-400',
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
  },
  low: {
    color: 'text-green-700 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    borderColor: 'border-green-200 dark:border-green-800',
  },
  minimal: {
    color: 'text-gray-700 dark:text-gray-400',
    bgColor: 'bg-gray-50 dark:bg-gray-900/20',
    borderColor: 'border-gray-200 dark:border-gray-800',
  },
};

const entityTypeIcons: Record<string, typeof User> = {
  person: User,
  vehicle: Car,
  address: MapPin,
  weapon: Crosshair,
};

function RiskScoreCard({ score }: { score: RiskScore }) {
  const config = riskLevelConfig[score.level.toLowerCase()] || riskLevelConfig.minimal;
  const Icon = entityTypeIcons[score.entity_type.toLowerCase()] || Shield;

  return (
    <div className={`rounded-lg border p-3 ${config.bgColor} ${config.borderColor}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon className={`h-4 w-4 ${config.color}`} />
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400 capitalize">
            {score.entity_type}
          </span>
        </div>
        <span className={`text-lg font-bold ${config.color}`}>
          {score.score.toFixed(0)}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[120px]">
          {score.entity_id}
        </span>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${config.bgColor} ${config.color}`}>
          {score.level}
        </span>
      </div>
      {score.factors && score.factors.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
          <p className="text-[10px] font-medium text-gray-500 dark:text-gray-400 mb-1">
            Top Factors
          </p>
          <div className="space-y-1">
            {score.factors.slice(0, 3).map((factor, index) => (
              <div key={index} className="flex items-center justify-between text-[10px]">
                <span className="text-gray-600 dark:text-gray-400">{factor.name}</span>
                <span className="text-gray-500">+{factor.contribution.toFixed(0)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function RiskSummary({ scores }: { scores: RiskScore[] }) {
  const summary = {
    critical: scores.filter((s) => s.level.toLowerCase() === 'critical').length,
    high: scores.filter((s) => s.level.toLowerCase() === 'high').length,
    medium: scores.filter((s) => s.level.toLowerCase() === 'medium').length,
    low: scores.filter((s) => s.level.toLowerCase() === 'low').length,
  };

  const avgScore = scores.length > 0
    ? scores.reduce((sum, s) => sum + s.score, 0) / scores.length
    : 0;

  return (
    <div className="mb-4 grid grid-cols-2 gap-2">
      <div className="rounded-lg bg-gray-100 p-3 dark:bg-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">Avg Score</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">
          {avgScore.toFixed(0)}
        </p>
      </div>
      <div className="rounded-lg bg-gray-100 p-3 dark:bg-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">Total Entities</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">
          {scores.length}
        </p>
      </div>
      <div className="col-span-2 flex gap-2">
        {summary.critical > 0 && (
          <span className="flex-1 rounded bg-red-100 px-2 py-1 text-center text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {summary.critical} Critical
          </span>
        )}
        {summary.high > 0 && (
          <span className="flex-1 rounded bg-orange-100 px-2 py-1 text-center text-xs font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">
            {summary.high} High
          </span>
        )}
        {summary.medium > 0 && (
          <span className="flex-1 rounded bg-yellow-100 px-2 py-1 text-center text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
            {summary.medium} Medium
          </span>
        )}
        {summary.low > 0 && (
          <span className="flex-1 rounded bg-green-100 px-2 py-1 text-center text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            {summary.low} Low
          </span>
        )}
      </div>
    </div>
  );
}

export function RiskDashboard({ riskScores }: RiskDashboardProps) {
  const scores = Object.values(riskScores);

  if (scores.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <Shield className="h-12 w-12 text-gray-300 dark:text-gray-600" />
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          No risk scores available
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500">
          Run a query to see entity risk scores
        </p>
      </div>
    );
  }

  const sortedScores = [...scores].sort((a, b) => b.score - a.score);

  return (
    <div>
      <RiskSummary scores={scores} />
      <div className="space-y-2 max-h-[300px] overflow-y-auto">
        {sortedScores.map((score) => (
          <RiskScoreCard key={score.entity_id} score={score} />
        ))}
      </div>
    </div>
  );
}

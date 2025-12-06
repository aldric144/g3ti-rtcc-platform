'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Brain,
  Search,
  AlertTriangle,
  TrendingUp,
  Shield,
  Lightbulb,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { AISearchBar } from './components/AISearchBar';
import { EntityGraph } from './components/EntityGraph';
import { AnomalyFeed } from './components/AnomalyFeed';
import { PatternResults } from './components/PatternResults';
import { RiskDashboard } from './components/RiskDashboard';
import { AIRecommendations } from './components/AIRecommendations';

interface AIQueryResult {
  query_id: string;
  original_query: string;
  summary: string;
  entities: Entity[];
  incidents: Incident[];
  relationships: Relationship[];
  risk_scores: Record<string, RiskScore>;
  anomalies: Anomaly[];
  patterns: Pattern[];
  predictions: Prediction[];
  recommendations: string[];
  processed_at: string;
  processing_time_ms: number;
  confidence: number;
}

interface Entity {
  id: string;
  type: string;
  name: string;
  properties: Record<string, unknown>;
  risk_level?: string;
}

interface Incident {
  id: string;
  type: string;
  description: string;
  timestamp: string;
  location?: { lat: number; lng: number };
}

interface Relationship {
  source_id: string;
  target_id: string;
  type: string;
  properties: Record<string, unknown>;
}

interface RiskScore {
  entity_id: string;
  entity_type: string;
  score: number;
  level: string;
  factors: RiskFactor[];
  last_updated: string;
}

interface RiskFactor {
  name: string;
  weight: number;
  value: number;
  contribution: number;
}

interface Anomaly {
  id: string;
  type: string;
  severity: string;
  description: string;
  detected_at: string;
  entities: string[];
  confidence: number;
}

interface Pattern {
  id: string;
  type: string;
  description: string;
  frequency: number;
  strength: number;
  entities: string[];
  locations?: { lat: number; lng: number }[];
}

interface Prediction {
  id: string;
  type: string;
  description: string;
  probability: number;
  time_horizon: string;
  entities: string[];
}

export default function AIConsolePage() {
  const [queryResult, setQueryResult] = useState<AIQueryResult | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingAnomalies, setIsLoadingAnomalies] = useState(false);
  const [isLoadingPatterns, setIsLoadingPatterns] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  const fetchAnomalies = useCallback(async (hours: number = 24) => {
    setIsLoadingAnomalies(true);
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`/api/v1/ai/anomalies?hours=${hours}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setAnomalies(data.anomalies || []);
      }
    } catch (err) {
      console.error('Failed to fetch anomalies:', err);
    } finally {
      setIsLoadingAnomalies(false);
    }
  }, []);

  const fetchPatterns = useCallback(async (type?: string) => {
    setIsLoadingPatterns(true);
    try {
      const token = localStorage.getItem('auth_token');
      const url = type ? `/api/v1/ai/patterns?type=${type}` : '/api/v1/ai/patterns';
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setPatterns(data.patterns || []);
      }
    } catch (err) {
      console.error('Failed to fetch patterns:', err);
    } finally {
      setIsLoadingPatterns(false);
    }
  }, []);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/v1/ai/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const data = await response.json();
      setQueryResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomalies();
    fetchPatterns();

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/api/v1/realtime/ai-events`;
    
    let ws: WebSocket | null = null;
    
    try {
      ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setWsConnected(true);
        console.log('AI Events WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'anomaly_detected') {
            setAnomalies((prev) => [data.payload, ...prev].slice(0, 50));
          } else if (data.type === 'pattern_shift') {
            setPatterns((prev) => [data.payload, ...prev].slice(0, 50));
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
        console.log('AI Events WebSocket disconnected');
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
      };
    } catch (err) {
      console.error('Failed to connect WebSocket:', err);
    }

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [fetchAnomalies, fetchPatterns]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="h-8 w-8 text-indigo-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                AI Intelligence Console
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Natural language queries, pattern analysis, and predictive intelligence
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${
                wsConnected
                  ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                  : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  wsConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              {wsConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>
        </div>

        <div className="mb-6">
          <AISearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {error && (
          <div className="mb-6 rounded-lg bg-red-50 p-4 text-red-700 dark:bg-red-900/20 dark:text-red-400">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              <span>{error}</span>
            </div>
          </div>
        )}

        {queryResult && (
          <div className="mb-6 rounded-lg bg-white p-4 shadow dark:bg-gray-800">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Query Results
              </h2>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>Confidence: {(queryResult.confidence * 100).toFixed(1)}%</span>
                <span>Time: {queryResult.processing_time_ms.toFixed(0)}ms</span>
              </div>
            </div>
            <p className="mb-4 text-gray-700 dark:text-gray-300">
              {queryResult.summary}
            </p>
            
            {queryResult.entities.length > 0 && (
              <div className="mb-4">
                <h3 className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Entity Graph ({queryResult.entities.length} entities, {queryResult.relationships.length} relationships)
                </h3>
                <EntityGraph
                  entities={queryResult.entities}
                  relationships={queryResult.relationships}
                />
              </div>
            )}
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <div className="rounded-lg bg-white p-4 shadow dark:bg-gray-800">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-orange-500" />
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Anomalies & Alerts
                  </h2>
                </div>
                <button
                  onClick={() => fetchAnomalies()}
                  disabled={isLoadingAnomalies}
                  className="rounded p-1 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {isLoadingAnomalies ? (
                    <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                  ) : (
                    <RefreshCw className="h-4 w-4 text-gray-500" />
                  )}
                </button>
              </div>
              <AnomalyFeed anomalies={anomalies} />
            </div>

            <div className="rounded-lg bg-white p-4 shadow dark:bg-gray-800">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-500" />
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Patterns & Trends
                  </h2>
                </div>
                <button
                  onClick={() => fetchPatterns()}
                  disabled={isLoadingPatterns}
                  className="rounded p-1 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {isLoadingPatterns ? (
                    <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                  ) : (
                    <RefreshCw className="h-4 w-4 text-gray-500" />
                  )}
                </button>
              </div>
              <PatternResults patterns={patterns} />
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-lg bg-white p-4 shadow dark:bg-gray-800">
              <div className="mb-4 flex items-center gap-2">
                <Shield className="h-5 w-5 text-red-500" />
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Risk Scores
                </h2>
              </div>
              <RiskDashboard
                riskScores={queryResult?.risk_scores || {}}
              />
            </div>

            <div className="rounded-lg bg-white p-4 shadow dark:bg-gray-800">
              <div className="mb-4 flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  AI Recommendations
                </h2>
              </div>
              <AIRecommendations
                recommendations={queryResult?.recommendations || []}
                predictions={queryResult?.predictions || []}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';

interface BiasMetric {
  metric_id: string;
  name: string;
  description: string;
  score: number;
  threshold: number;
  status: string;
  last_checked: string;
}

interface AuditLog {
  log_id: string;
  timestamp: string;
  action: string;
  model: string;
  result: string;
  details: string;
}

interface ProtectedAttribute {
  attribute: string;
  excluded: boolean;
  reason: string;
}

export default function BiasAuditPanel() {
  const [metrics, setMetrics] = useState<BiasMetric[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [protectedAttributes, setProtectedAttributes] = useState<ProtectedAttribute[]>([]);

  useEffect(() => {
    const mockMetrics: BiasMetric[] = [
      {
        metric_id: 'metric-001',
        name: 'Demographic Parity',
        description: 'Ensures predictions are independent of protected attributes',
        score: 0.92,
        threshold: 0.80,
        status: 'PASS',
        last_checked: '2024-12-09T10:00:00Z',
      },
      {
        metric_id: 'metric-002',
        name: 'Equal Opportunity',
        description: 'True positive rates are equal across groups',
        score: 0.88,
        threshold: 0.80,
        status: 'PASS',
        last_checked: '2024-12-09T10:00:00Z',
      },
      {
        metric_id: 'metric-003',
        name: 'Predictive Parity',
        description: 'Precision is equal across groups',
        score: 0.85,
        threshold: 0.80,
        status: 'PASS',
        last_checked: '2024-12-09T10:00:00Z',
      },
      {
        metric_id: 'metric-004',
        name: 'Calibration',
        description: 'Predicted probabilities match actual outcomes',
        score: 0.91,
        threshold: 0.85,
        status: 'PASS',
        last_checked: '2024-12-09T10:00:00Z',
      },
      {
        metric_id: 'metric-005',
        name: 'Geographic Fairness',
        description: 'No systematic over/under-prediction by area',
        score: 0.78,
        threshold: 0.80,
        status: 'WARNING',
        last_checked: '2024-12-09T10:00:00Z',
      },
    ];

    const mockAuditLogs: AuditLog[] = [
      { log_id: 'log-001', timestamp: '2024-12-09T10:00:00Z', action: 'BIAS_CHECK', model: 'RiskTerrainModel', result: 'PASS', details: 'All metrics within thresholds' },
      { log_id: 'log-002', timestamp: '2024-12-09T09:30:00Z', action: 'MODEL_RETRAIN', model: 'ViolenceClusterModel', result: 'SUCCESS', details: 'Model retrained with updated data' },
      { log_id: 'log-003', timestamp: '2024-12-09T09:00:00Z', action: 'FEATURE_AUDIT', model: 'PatrolOptimizer', result: 'PASS', details: 'No prohibited features detected' },
      { log_id: 'log-004', timestamp: '2024-12-08T22:00:00Z', action: 'BIAS_CHECK', model: 'BehaviorPredictor', result: 'WARNING', details: 'Geographic fairness below threshold' },
      { log_id: 'log-005', timestamp: '2024-12-08T18:00:00Z', action: 'PREDICTION_AUDIT', model: 'RiskTerrainModel', result: 'PASS', details: '1,245 predictions audited' },
    ];

    const mockProtectedAttributes: ProtectedAttribute[] = [
      { attribute: 'Race/Ethnicity', excluded: true, reason: 'Protected class - federal law' },
      { attribute: 'Religion', excluded: true, reason: 'Protected class - federal law' },
      { attribute: 'National Origin', excluded: true, reason: 'Protected class - federal law' },
      { attribute: 'Gender', excluded: true, reason: 'Protected class - federal law' },
      { attribute: 'Age', excluded: true, reason: 'Protected class - limited exceptions' },
      { attribute: 'Disability Status', excluded: true, reason: 'Protected class - ADA' },
      { attribute: 'Sexual Orientation', excluded: true, reason: 'Protected class - state law' },
      { attribute: 'Socioeconomic Proxies', excluded: true, reason: 'Indirect discrimination risk' },
    ];

    setMetrics(mockMetrics);
    setAuditLogs(mockAuditLogs);
    setProtectedAttributes(mockProtectedAttributes);
  }, []);

  const statusColors: Record<string, string> = {
    PASS: 'bg-green-500',
    WARNING: 'bg-yellow-500',
    FAIL: 'bg-red-500',
    SUCCESS: 'bg-green-500',
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">Bias Audit & Transparency</h2>
        <p className="text-gray-400 text-sm mt-1">
          Continuous monitoring of AI models for fairness and bias
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-green-900 bg-opacity-30 border border-green-600 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-green-400 font-semibold">Overall Status</div>
              <div className="text-2xl font-bold text-white mt-1">COMPLIANT</div>
            </div>
            <svg className="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Metrics Passing</div>
          <div className="text-2xl font-bold mt-1">
            {metrics.filter((m) => m.status === 'PASS').length} / {metrics.length}
          </div>
          <div className="text-sm text-gray-400 mt-1">
            {metrics.filter((m) => m.status === 'WARNING').length} warnings
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Last Full Audit</div>
          <div className="text-2xl font-bold mt-1">2h ago</div>
          <div className="text-sm text-gray-400 mt-1">Next: in 4 hours</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Fairness Metrics</h3>
          <div className="space-y-4">
            {metrics.map((metric) => (
              <div key={metric.metric_id}>
                <div className="flex items-center justify-between mb-1">
                  <div>
                    <span className="font-medium">{metric.name}</span>
                    <span
                      className={`ml-2 px-2 py-0.5 rounded text-xs ${
                        statusColors[metric.status]
                      }`}
                    >
                      {metric.status}
                    </span>
                  </div>
                  <span className="text-sm">
                    {(metric.score * 100).toFixed(0)}% / {(metric.threshold * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      metric.status === 'PASS'
                        ? 'bg-green-500'
                        : metric.status === 'WARNING'
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${metric.score * 100}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-400 mt-1">{metric.description}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Protected Attributes</h3>
          <p className="text-sm text-gray-400 mb-4">
            The following attributes are explicitly excluded from all predictive models:
          </p>
          <div className="space-y-2">
            {protectedAttributes.map((attr, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-gray-600 p-2 rounded"
              >
                <div className="flex items-center">
                  <svg
                    className="w-5 h-5 text-red-400 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
                    />
                  </svg>
                  <span>{attr.attribute}</span>
                </div>
                <span className="text-xs text-gray-400">{attr.reason}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Audit Log</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-600">
                <th className="text-left py-2">Timestamp</th>
                <th className="text-left py-2">Action</th>
                <th className="text-left py-2">Model</th>
                <th className="text-left py-2">Result</th>
                <th className="text-left py-2">Details</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log) => (
                <tr key={log.log_id} className="border-b border-gray-600">
                  <td className="py-2">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-2">{log.action}</td>
                  <td className="py-2">{log.model}</td>
                  <td className="py-2">
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        statusColors[log.result]
                      }`}
                    >
                      {log.result}
                    </span>
                  </td>
                  <td className="py-2 text-gray-400">{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

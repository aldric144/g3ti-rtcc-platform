'use client';

import { useState, useEffect } from 'react';

interface FinancialCrimeGraphProps {
  compact?: boolean;
}

interface FraudPattern {
  pattern_id: string;
  fraud_type: string;
  name: string;
  risk_category: string;
  risk_score: number;
  total_amount: number;
  currency: string;
  is_confirmed: boolean;
  investigation_status: string;
  detected_at: string;
}

interface CryptoWalletRisk {
  assessment_id: string;
  wallet_address: string;
  blockchain: string;
  risk_category: string;
  risk_score: number;
  risk_indicators: string[];
  total_received: number;
  total_sent: number;
  transaction_count: number;
  assessment_date: string;
}

interface TransactionAnomaly {
  anomaly_id: string;
  transaction_id: string;
  anomaly_type: string;
  risk_score: number;
  flags: string[];
  source_entity: string;
  destination_entity: string;
  amount: number;
  currency: string;
  investigation_status: string;
  detected_at: string;
}

export default function FinancialCrimeGraph({ compact = false }: FinancialCrimeGraphProps) {
  const [fraudPatterns, setFraudPatterns] = useState<FraudPattern[]>([]);
  const [cryptoRisks, setCryptoRisks] = useState<CryptoWalletRisk[]>([]);
  const [anomalies, setAnomalies] = useState<TransactionAnomaly[]>([]);
  const [activeView, setActiveView] = useState<'fraud' | 'crypto' | 'anomalies'>('fraud');
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [fraudRes, cryptoRes, anomaliesRes, metricsRes] = await Promise.all([
        fetch('/api/national-security/financial/fraud-patterns?limit=20'),
        fetch('/api/national-security/financial/crypto-wallets?limit=20'),
        fetch('/api/national-security/financial/transaction-anomalies?limit=20'),
        fetch('/api/national-security/financial/metrics'),
      ]);

      if (fraudRes.ok) {
        const data = await fraudRes.json();
        setFraudPatterns(data.patterns || []);
      }
      if (cryptoRes.ok) {
        const data = await cryptoRes.json();
        setCryptoRisks(data.assessments || []);
      }
      if (anomaliesRes.ok) {
        const data = await anomaliesRes.json();
        setAnomalies(data.anomalies || []);
      }
      if (metricsRes.ok) {
        const data = await metricsRes.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch financial crime data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskCategoryColor = (category: string) => {
    switch (category) {
      case 'critical':
        return 'text-red-400 bg-red-900/30';
      case 'high':
        return 'text-orange-400 bg-orange-900/30';
      case 'elevated':
        return 'text-yellow-400 bg-yellow-900/30';
      case 'moderate':
        return 'text-blue-400 bg-blue-900/30';
      case 'low':
        return 'text-green-400 bg-green-900/30';
      default:
        return 'text-gray-400 bg-gray-700';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'text-red-400';
      case 'investigating':
        return 'text-yellow-400';
      case 'confirmed':
        return 'text-orange-400';
      case 'resolved':
        return 'text-green-400';
      case 'false_positive':
        return 'text-gray-400';
      default:
        return 'text-gray-400';
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const truncateAddress = (address: string) => {
    if (address.length <= 16) return address;
    return `${address.slice(0, 8)}...${address.slice(-6)}`;
  };

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-amber-400">Financial Crime</h3>
          <span className="text-xs text-gray-500">
            {metrics?.total_fraud_patterns || 0} patterns
          </span>
        </div>
        <div className="space-y-2">
          {fraudPatterns.slice(0, 3).map((pattern) => (
            <div
              key={pattern.pattern_id}
              className="flex items-center justify-between p-2 bg-gray-700/50 rounded"
            >
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-0.5 rounded text-xs ${getRiskCategoryColor(pattern.risk_category)}`}>
                  {pattern.risk_category}
                </span>
                <span className="text-sm text-white truncate max-w-[100px]">
                  {pattern.fraud_type}
                </span>
              </div>
              <span className="text-sm font-medium text-amber-400">
                {formatCurrency(pattern.total_amount, pattern.currency)}
              </span>
            </div>
          ))}
        </div>
        {metrics && (
          <div className="mt-4 pt-4 border-t border-gray-700 grid grid-cols-3 gap-2 text-center">
            <div>
              <div className="text-lg font-bold text-red-400">
                {metrics.confirmed_fraud_patterns || 0}
              </div>
              <div className="text-xs text-gray-500">Confirmed</div>
            </div>
            <div>
              <div className="text-lg font-bold text-orange-400">
                {metrics.high_risk_wallets || 0}
              </div>
              <div className="text-xs text-gray-500">Risky Wallets</div>
            </div>
            <div>
              <div className="text-lg font-bold text-yellow-400">
                {metrics.open_anomalies || 0}
              </div>
              <div className="text-xs text-gray-500">Anomalies</div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-amber-400">Financial Crime Intelligence</h2>
          <div className="flex space-x-2">
            {(['fraud', 'crypto', 'anomalies'] as const).map((view) => (
              <button
                key={view}
                onClick={() => setActiveView(view)}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  activeView === view
                    ? 'bg-amber-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {view === 'crypto' ? 'Crypto Wallets' : view.charAt(0).toUpperCase() + view.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {metrics && (
        <div className="p-4 border-b border-gray-700 bg-gray-800/50">
          <div className="grid grid-cols-5 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-amber-400">
                {metrics.total_fraud_patterns || 0}
              </div>
              <div className="text-xs text-gray-500">Fraud Patterns</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-400">
                {metrics.confirmed_fraud_patterns || 0}
              </div>
              <div className="text-xs text-gray-500">Confirmed</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-400">
                {metrics.total_crypto_assessments || 0}
              </div>
              <div className="text-xs text-gray-500">Wallet Assessments</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">
                {metrics.total_transaction_anomalies || 0}
              </div>
              <div className="text-xs text-gray-500">Anomalies</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-400">
                {metrics.total_networks || 0}
              </div>
              <div className="text-xs text-gray-500">Networks</div>
            </div>
          </div>
        </div>
      )}

      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-400" />
          </div>
        ) : (
          <>
            {activeView === 'fraud' && (
              <div className="space-y-3">
                {fraudPatterns.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No fraud patterns detected
                  </div>
                ) : (
                  fraudPatterns.map((pattern) => (
                    <div
                      key={pattern.pattern_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-amber-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskCategoryColor(pattern.risk_category)}`}>
                              {pattern.risk_category.toUpperCase()}
                            </span>
                            <span className="text-white font-medium">{pattern.name}</span>
                            {pattern.is_confirmed && (
                              <span className="px-2 py-0.5 bg-red-900/50 text-red-400 text-xs rounded">
                                CONFIRMED
                              </span>
                            )}
                            <span className={`text-xs ${getStatusColor(pattern.investigation_status)}`}>
                              {pattern.investigation_status}
                            </span>
                          </div>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>Type: {pattern.fraud_type}</span>
                            <span>Amount: {formatCurrency(pattern.total_amount, pattern.currency)}</span>
                            <span>Detected: {new Date(pattern.detected_at).toLocaleString()}</span>
                          </div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-amber-400">
                            {pattern.risk_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Risk Score</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'crypto' && (
              <div className="space-y-3">
                {cryptoRisks.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No crypto wallet assessments
                  </div>
                ) : (
                  cryptoRisks.map((wallet) => (
                    <div
                      key={wallet.assessment_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-orange-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskCategoryColor(wallet.risk_category)}`}>
                              {wallet.risk_category.toUpperCase()}
                            </span>
                            <span className="text-white font-mono text-sm">
                              {truncateAddress(wallet.wallet_address)}
                            </span>
                            <span className="px-2 py-0.5 bg-gray-600 text-gray-300 text-xs rounded">
                              {wallet.blockchain}
                            </span>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-1">
                            {wallet.risk_indicators.slice(0, 4).map((indicator, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-red-900/30 text-red-400 text-xs rounded"
                              >
                                {indicator}
                              </span>
                            ))}
                          </div>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>Received: {wallet.total_received.toFixed(4)}</span>
                            <span>Sent: {wallet.total_sent.toFixed(4)}</span>
                            <span>Txns: {wallet.transaction_count}</span>
                            <span>Assessed: {new Date(wallet.assessment_date).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-orange-400">
                            {wallet.risk_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Risk Score</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeView === 'anomalies' && (
              <div className="space-y-3">
                {anomalies.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No transaction anomalies detected
                  </div>
                ) : (
                  anomalies.map((anomaly) => (
                    <div
                      key={anomaly.anomaly_id}
                      className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-yellow-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className="text-white font-medium">{anomaly.anomaly_type}</span>
                            <span className={`text-xs ${getStatusColor(anomaly.investigation_status)}`}>
                              {anomaly.investigation_status}
                            </span>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-1">
                            {anomaly.flags.map((flag, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-yellow-900/30 text-yellow-400 text-xs rounded"
                              >
                                {flag}
                              </span>
                            ))}
                          </div>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                            <span>From: {anomaly.source_entity}</span>
                            <span>To: {anomaly.destination_entity}</span>
                            <span>Amount: {formatCurrency(anomaly.amount, anomaly.currency)}</span>
                            <span>Detected: {new Date(anomaly.detected_at).toLocaleString()}</span>
                          </div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-2xl font-bold text-yellow-400">
                            {anomaly.risk_score.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">Risk Score</div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

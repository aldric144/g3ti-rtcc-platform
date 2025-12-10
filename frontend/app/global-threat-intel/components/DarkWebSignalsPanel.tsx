'use client';

import { useState, useEffect } from 'react';

interface DarkWebSignal {
  signal_id: string;
  signal_type: string;
  source_platform: string;
  title: string;
  content_snippet: string;
  keywords_matched: string[];
  priority_score: number;
  status: string;
  detected_at: string;
}

interface MarketListing {
  listing_id: string;
  market_name: string;
  category: string;
  title: string;
  price: number;
  currency: string;
  threat_score: number;
  first_seen: string;
}

interface Props {
  compact?: boolean;
}

export default function DarkWebSignalsPanel({ compact = false }: Props) {
  const [signals, setSignals] = useState<DarkWebSignal[]>([]);
  const [listings, setListings] = useState<MarketListing[]>([]);
  const [activeView, setActiveView] = useState<'signals' | 'listings'>('signals');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockSignals: DarkWebSignal[] = [
      {
        signal_id: 'sig-001',
        signal_type: 'weapons_trafficking',
        source_platform: 'dark_forum_alpha',
        title: 'Weapons sale discussion detected',
        content_snippet: 'New shipment available...',
        keywords_matched: ['weapons', 'firearms', 'sale'],
        priority_score: 85,
        status: 'new',
        detected_at: new Date().toISOString(),
      },
      {
        signal_id: 'sig-002',
        signal_type: 'drug_trafficking',
        source_platform: 'market_beta',
        title: 'Fentanyl distribution network',
        content_snippet: 'Bulk pricing available...',
        keywords_matched: ['fentanyl', 'bulk', 'shipping'],
        priority_score: 92,
        status: 'escalated',
        detected_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        signal_id: 'sig-003',
        signal_type: 'identity_fraud',
        source_platform: 'forum_gamma',
        title: 'SSN database for sale',
        content_snippet: 'Fresh batch of verified...',
        keywords_matched: ['ssn', 'identity', 'database'],
        priority_score: 78,
        status: 'analyzing',
        detected_at: new Date(Date.now() - 7200000).toISOString(),
      },
    ];

    const mockListings: MarketListing[] = [
      {
        listing_id: 'lst-001',
        market_name: 'DarkMarket Alpha',
        category: 'weapons',
        title: 'Glock 19 Gen5',
        price: 850,
        currency: 'USD',
        threat_score: 88,
        first_seen: new Date().toISOString(),
      },
      {
        listing_id: 'lst-002',
        market_name: 'Underground Exchange',
        category: 'drugs',
        title: 'Fentanyl 100g',
        price: 2500,
        currency: 'USD',
        threat_score: 95,
        first_seen: new Date(Date.now() - 86400000).toISOString(),
      },
      {
        listing_id: 'lst-003',
        market_name: 'Identity Hub',
        category: 'fraud',
        title: 'Premium SSN Package',
        price: 150,
        currency: 'USD',
        threat_score: 72,
        first_seen: new Date(Date.now() - 172800000).toISOString(),
      },
    ];

    setTimeout(() => {
      setSignals(mockSignals);
      setListings(mockListings);
      setLoading(false);
    }, 500);
  }, []);

  const getPriorityColor = (score: number) => {
    if (score >= 80) return 'text-red-500 bg-red-500/20';
    if (score >= 60) return 'text-orange-500 bg-orange-500/20';
    if (score >= 40) return 'text-yellow-500 bg-yellow-500/20';
    return 'text-blue-500 bg-blue-500/20';
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-green-500/20 text-green-400',
      analyzing: 'bg-blue-500/20 text-blue-400',
      escalated: 'bg-red-500/20 text-red-400',
      resolved: 'bg-gray-500/20 text-gray-400',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400';
  };

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4 text-purple-400">
          Dark Web Signals
        </h3>
        <div className="space-y-3">
          {signals.slice(0, 3).map((signal) => (
            <div
              key={signal.signal_id}
              className="p-3 bg-gray-700/50 rounded border-l-4 border-purple-500"
            >
              <div className="flex justify-between items-start">
                <span className="font-medium text-sm truncate">
                  {signal.title}
                </span>
                <span
                  className={`text-xs px-2 py-1 rounded ${getPriorityColor(signal.priority_score)}`}
                >
                  {signal.priority_score}
                </span>
              </div>
              <span className="text-xs text-gray-400 mt-1 block">
                {signal.signal_type.replace(/_/g, ' ')}
              </span>
            </div>
          ))}
        </div>
        <div className="mt-4 text-center">
          <span className="text-sm text-purple-400 cursor-pointer hover:underline">
            View All Signals →
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-purple-400">
            Dark Web Intelligence
          </h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveView('signals')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'signals'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Signals
            </button>
            <button
              onClick={() => setActiveView('listings')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'listings'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Market Listings
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          </div>
        ) : activeView === 'signals' ? (
          <div className="space-y-4">
            {signals.map((signal) => (
              <div
                key={signal.signal_id}
                className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-purple-500 transition-colors"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-white">{signal.title}</h3>
                    <p className="text-sm text-gray-400">
                      {signal.source_platform} •{' '}
                      {signal.signal_type.replace(/_/g, ' ')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-1 text-xs rounded ${getStatusBadge(signal.status)}`}
                    >
                      {signal.status}
                    </span>
                    <span
                      className={`px-2 py-1 text-sm font-bold rounded ${getPriorityColor(signal.priority_score)}`}
                    >
                      {signal.priority_score}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-300 mb-2">
                  {signal.content_snippet}
                </p>
                <div className="flex flex-wrap gap-2">
                  {signal.keywords_matched.map((keyword, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
                <div className="mt-3 flex justify-between items-center">
                  <span className="text-xs text-gray-500">
                    Detected: {new Date(signal.detected_at).toLocaleString()}
                  </span>
                  <div className="space-x-2">
                    <button className="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded">
                      Analyze
                    </button>
                    <button className="px-3 py-1 text-xs bg-red-600 hover:bg-red-700 rounded">
                      Escalate
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 text-sm border-b border-gray-700">
                  <th className="pb-3">Market</th>
                  <th className="pb-3">Category</th>
                  <th className="pb-3">Title</th>
                  <th className="pb-3">Price</th>
                  <th className="pb-3">Threat Score</th>
                  <th className="pb-3">First Seen</th>
                </tr>
              </thead>
              <tbody>
                {listings.map((listing) => (
                  <tr
                    key={listing.listing_id}
                    className="border-b border-gray-700/50 hover:bg-gray-700/30"
                  >
                    <td className="py-3 text-sm">{listing.market_name}</td>
                    <td className="py-3">
                      <span className="px-2 py-1 text-xs bg-gray-600 rounded capitalize">
                        {listing.category}
                      </span>
                    </td>
                    <td className="py-3 text-sm font-medium">{listing.title}</td>
                    <td className="py-3 text-sm">
                      ${listing.price} {listing.currency}
                    </td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-1 text-sm font-bold rounded ${getPriorityColor(listing.threat_score)}`}
                      >
                        {listing.threat_score}
                      </span>
                    </td>
                    <td className="py-3 text-sm text-gray-400">
                      {new Date(listing.first_seen).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

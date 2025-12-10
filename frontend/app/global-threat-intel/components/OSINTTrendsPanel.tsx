'use client';

import { useState, useEffect } from 'react';

interface NewsArticle {
  article_id: string;
  source_name: string;
  title: string;
  summary: string;
  category: string;
  sentiment: string;
  relevance_score: number;
  published_at: string;
}

interface SocialSignal {
  signal_id: string;
  source_type: string;
  author_name: string;
  content: string;
  sentiment: string;
  hate_speech_detected: boolean;
  threat_score: number;
  posted_at: string;
}

interface KeywordSpike {
  spike_id: string;
  keyword: string;
  baseline_count: number;
  current_count: number;
  spike_percentage: number;
  status: string;
}

interface Props {
  compact?: boolean;
}

export default function OSINTTrendsPanel({ compact = false }: Props) {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [socialSignals, setSocialSignals] = useState<SocialSignal[]>([]);
  const [spikes, setSpikes] = useState<KeywordSpike[]>([]);
  const [activeView, setActiveView] = useState<'news' | 'social' | 'spikes'>('news');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockArticles: NewsArticle[] = [
      {
        article_id: 'art-001',
        source_name: 'Local News Network',
        title: 'Protest Planned for Downtown Area This Weekend',
        summary: 'Organizers expect thousands to gather for peaceful demonstration...',
        category: 'protest',
        sentiment: 'neutral',
        relevance_score: 85,
        published_at: new Date().toISOString(),
      },
      {
        article_id: 'art-002',
        source_name: 'Crime Watch Daily',
        title: 'Gang Activity Increases in East District',
        summary: 'Law enforcement reports uptick in gang-related incidents...',
        category: 'gang_activity',
        sentiment: 'negative',
        relevance_score: 92,
        published_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        article_id: 'art-003',
        source_name: 'Tech Security News',
        title: 'Ransomware Attack Targets Local Infrastructure',
        summary: 'Critical systems affected by sophisticated cyber attack...',
        category: 'cybersecurity',
        sentiment: 'threatening',
        relevance_score: 88,
        published_at: new Date(Date.now() - 7200000).toISOString(),
      },
    ];

    const mockSocialSignals: SocialSignal[] = [
      {
        signal_id: 'soc-001',
        source_type: 'social_twitter',
        author_name: '@activist_user',
        content: 'Everyone meet at city hall tomorrow at noon! #protest #justice',
        sentiment: 'negative',
        hate_speech_detected: false,
        threat_score: 45,
        posted_at: new Date().toISOString(),
      },
      {
        signal_id: 'soc-002',
        source_type: 'social_telegram',
        author_name: 'Anonymous Channel',
        content: 'Target identified. Moving forward with plan...',
        sentiment: 'threatening',
        hate_speech_detected: true,
        threat_score: 88,
        posted_at: new Date(Date.now() - 1800000).toISOString(),
      },
      {
        signal_id: 'soc-003',
        source_type: 'social_reddit',
        author_name: 'concerned_citizen',
        content: 'Has anyone noticed increased police presence downtown?',
        sentiment: 'neutral',
        hate_speech_detected: false,
        threat_score: 25,
        posted_at: new Date(Date.now() - 5400000).toISOString(),
      },
    ];

    const mockSpikes: KeywordSpike[] = [
      {
        spike_id: 'spk-001',
        keyword: 'protest',
        baseline_count: 50,
        current_count: 450,
        spike_percentage: 800,
        status: 'active',
      },
      {
        spike_id: 'spk-002',
        keyword: 'shooting',
        baseline_count: 20,
        current_count: 85,
        spike_percentage: 325,
        status: 'emerging',
      },
      {
        spike_id: 'spk-003',
        keyword: 'evacuation',
        baseline_count: 5,
        current_count: 45,
        spike_percentage: 800,
        status: 'active',
      },
    ];

    setTimeout(() => {
      setArticles(mockArticles);
      setSocialSignals(mockSocialSignals);
      setSpikes(mockSpikes);
      setLoading(false);
    }, 500);
  }, []);

  const getSentimentColor = (sentiment: string) => {
    const colors: Record<string, string> = {
      positive: 'text-green-400 bg-green-500/20',
      neutral: 'text-gray-400 bg-gray-500/20',
      negative: 'text-orange-400 bg-orange-500/20',
      threatening: 'text-red-400 bg-red-500/20',
      hateful: 'text-red-500 bg-red-600/20',
    };
    return colors[sentiment] || 'text-gray-400 bg-gray-500/20';
  };

  const getSpikeStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      emerging: 'text-yellow-400 bg-yellow-500/20',
      active: 'text-red-400 bg-red-500/20',
      declining: 'text-blue-400 bg-blue-500/20',
      resolved: 'text-gray-400 bg-gray-500/20',
    };
    return colors[status] || 'text-gray-400 bg-gray-500/20';
  };

  if (compact) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4 text-cyan-400">OSINT Trends</h3>
        <div className="space-y-3">
          {spikes.slice(0, 3).map((spike) => (
            <div
              key={spike.spike_id}
              className="p-3 bg-gray-700/50 rounded border-l-4 border-cyan-500"
            >
              <div className="flex justify-between items-start">
                <span className="font-medium text-sm">#{spike.keyword}</span>
                <span className="text-xs text-red-400">
                  +{spike.spike_percentage}%
                </span>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className="text-xs text-gray-400">
                  {spike.current_count} mentions
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded ${getSpikeStatusColor(spike.status)}`}
                >
                  {spike.status}
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 text-center">
          <span className="text-sm text-cyan-400 cursor-pointer hover:underline">
            View All Trends →
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-cyan-400">
            OSINT Intelligence
          </h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveView('news')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'news'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              News
            </button>
            <button
              onClick={() => setActiveView('social')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'social'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Social
            </button>
            <button
              onClick={() => setActiveView('spikes')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'spikes'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              Keyword Spikes
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
          </div>
        ) : activeView === 'news' ? (
          <div className="space-y-4">
            {articles.map((article) => (
              <div
                key={article.article_id}
                className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-cyan-500 transition-colors"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-white">{article.title}</h3>
                    <p className="text-sm text-gray-400">{article.source_name}</p>
                  </div>
                  <span className="text-sm font-bold text-cyan-400">
                    {article.relevance_score}%
                  </span>
                </div>
                <p className="text-sm text-gray-300 mb-2">{article.summary}</p>
                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    <span className="px-2 py-1 text-xs bg-gray-600 rounded capitalize">
                      {article.category.replace(/_/g, ' ')}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs rounded ${getSentimentColor(article.sentiment)}`}
                    >
                      {article.sentiment}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(article.published_at).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : activeView === 'social' ? (
          <div className="space-y-4">
            {socialSignals.map((signal) => (
              <div
                key={signal.signal_id}
                className={`p-4 bg-gray-700/50 rounded-lg border ${
                  signal.hate_speech_detected
                    ? 'border-red-500'
                    : 'border-gray-600'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="font-medium text-white">
                      {signal.author_name}
                    </span>
                    <span className="text-sm text-gray-400 ml-2">
                      {signal.source_type.replace('social_', '')}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {signal.hate_speech_detected && (
                      <span className="px-2 py-1 text-xs bg-red-600/30 text-red-400 rounded">
                        HATE SPEECH
                      </span>
                    )}
                    <span
                      className={`px-2 py-1 text-sm font-bold rounded ${
                        signal.threat_score >= 70
                          ? 'text-red-400 bg-red-500/20'
                          : signal.threat_score >= 40
                            ? 'text-orange-400 bg-orange-500/20'
                            : 'text-green-400 bg-green-500/20'
                      }`}
                    >
                      {signal.threat_score}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-300 mb-2">{signal.content}</p>
                <div className="flex items-center justify-between">
                  <span
                    className={`px-2 py-1 text-xs rounded ${getSentimentColor(signal.sentiment)}`}
                  >
                    {signal.sentiment}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(signal.posted_at).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {spikes.map((spike) => (
              <div
                key={spike.spike_id}
                className="p-4 bg-gray-700/50 rounded-lg border border-gray-600"
              >
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-lg font-bold text-white">#{spike.keyword}</h3>
                  <span
                    className={`px-3 py-1 text-sm rounded ${getSpikeStatusColor(spike.status)}`}
                  >
                    {spike.status}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 mb-3">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-cyan-400">
                      {spike.current_count}
                    </p>
                    <p className="text-xs text-gray-400">Current</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-400">
                      {spike.baseline_count}
                    </p>
                    <p className="text-xs text-gray-400">Baseline</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-400">
                      +{spike.spike_percentage}%
                    </p>
                    <p className="text-xs text-gray-400">Change</p>
                  </div>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-cyan-500 h-2 rounded-full"
                    style={{
                      width: `${Math.min((spike.current_count / (spike.baseline_count * 10)) * 100, 100)}%`,
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

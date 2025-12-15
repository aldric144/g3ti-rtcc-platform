'use client';

import React, { useState, useEffect } from 'react';

interface Neighborhood {
  neighborhood_id: string;
  name: string;
  trust_level: string;
  vulnerability_factors: string[];
  historical_trauma_score: number;
  community_resources: string[];
  key_stakeholders: string[];
  special_considerations: string[];
  last_updated: string;
}

interface LocalEvent {
  event_id: string;
  name: string;
  event_type: string;
  location: string;
  start_time: string;
  end_time: string | null;
  expected_attendance: number;
  community_significance: string;
  special_considerations: string[];
  active: boolean;
}

interface CommunityContext {
  context_id: string;
  location: string;
  neighborhood: Neighborhood | null;
  trust_level: string;
  sentiment: string;
  active_events: LocalEvent[];
  vulnerability_factors: string[];
  historical_trauma_present: boolean;
  special_considerations: string[];
  recommended_approach: string;
}

export default function CulturalContextViewer() {
  const [neighborhoods, setNeighborhoods] = useState<Neighborhood[]>([]);
  const [events, setEvents] = useState<LocalEvent[]>([]);
  const [selectedNeighborhood, setSelectedNeighborhood] = useState<string>('');
  const [context, setContext] = useState<CommunityContext | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNeighborhoods();
    fetchEvents();
  }, []);

  const fetchNeighborhoods = async () => {
    try {
      const response = await fetch('/api/moral/context/neighborhoods');
      if (response.ok) {
        const data = await response.json();
        setNeighborhoods(data.neighborhoods || []);
      }
    } catch (error) {
      console.error('Failed to fetch neighborhoods:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEvents = async () => {
    try {
      const response = await fetch('/api/moral/context/events');
      if (response.ok) {
        const data = await response.json();
        setEvents(data.events || []);
      }
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  };

  const fetchContext = async (location: string) => {
    try {
      const response = await fetch(`/api/moral/context?location=${encodeURIComponent(location)}`);
      if (response.ok) {
        const data = await response.json();
        setContext(data);
      }
    } catch (error) {
      console.error('Failed to fetch context:', error);
    }
  };

  const handleNeighborhoodSelect = (neighborhoodId: string) => {
    setSelectedNeighborhood(neighborhoodId);
    const neighborhood = neighborhoods.find(n => n.neighborhood_id === neighborhoodId);
    if (neighborhood) {
      fetchContext(neighborhood.name);
    }
  };

  const getTrustLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'very_high':
        return 'text-green-400 bg-green-500/20';
      case 'high':
        return 'text-green-300 bg-green-500/10';
      case 'moderate':
        return 'text-yellow-400 bg-yellow-500/20';
      case 'low':
        return 'text-orange-400 bg-orange-500/20';
      case 'very_low':
        return 'text-red-400 bg-red-500/20';
      default:
        return 'text-slate-400 bg-slate-500/20';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'very_positive':
        return '😊';
      case 'positive':
        return '🙂';
      case 'neutral':
        return '😐';
      case 'negative':
        return '😟';
      case 'very_negative':
        return '😢';
      default:
        return '❓';
    }
  };

  const getEventTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'festival':
        return '🎉';
      case 'funeral':
        return '🕯️';
      case 'vigil':
        return '🕯️';
      case 'protest':
        return '📢';
      case 'celebration':
        return '🎊';
      case 'religious':
        return '⛪';
      case 'community_meeting':
        return '🤝';
      case 'sports':
        return '⚽';
      case 'school':
        return '🏫';
      case 'emergency':
        return '🚨';
      default:
        return '📅';
    }
  };

  const getTraumaScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-red-400';
    if (score >= 0.5) return 'text-orange-400';
    if (score >= 0.3) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
          <h3 className="text-lg font-semibold text-gold-400 mb-4 flex items-center gap-2">
            <span>🏘️</span> Neighborhoods
          </h3>

          {loading ? (
            <div className="text-slate-400 text-center py-4">Loading...</div>
          ) : (
            <div className="space-y-2">
              {neighborhoods.map((neighborhood) => (
                <button
                  key={neighborhood.neighborhood_id}
                  onClick={() => handleNeighborhoodSelect(neighborhood.neighborhood_id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedNeighborhood === neighborhood.neighborhood_id
                      ? 'bg-gold-500/20 border border-gold-500/50'
                      : 'bg-slate-700/50 hover:bg-slate-700 border border-transparent'
                  }`}
                >
                  <div className="font-medium text-white">{neighborhood.name}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded ${getTrustLevelColor(neighborhood.trust_level)}`}>
                      {neighborhood.trust_level.replace(/_/g, ' ')}
                    </span>
                    <span className={`text-xs ${getTraumaScoreColor(neighborhood.historical_trauma_score)}`}>
                      Trauma: {(neighborhood.historical_trauma_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="col-span-2 space-y-4">
          {context ? (
            <>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
                <h3 className="text-lg font-semibold text-gold-400 mb-4">
                  Context: {context.location}
                </h3>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="bg-slate-700/50 rounded p-3">
                    <div className="text-slate-400 text-sm">Trust Level</div>
                    <div className={`text-lg font-semibold px-2 py-1 rounded inline-block mt-1 ${getTrustLevelColor(context.trust_level)}`}>
                      {context.trust_level.replace(/_/g, ' ').toUpperCase()}
                    </div>
                  </div>
                  <div className="bg-slate-700/50 rounded p-3">
                    <div className="text-slate-400 text-sm">Sentiment</div>
                    <div className="text-lg font-semibold text-white mt-1">
                      {getSentimentIcon(context.sentiment)} {context.sentiment.replace(/_/g, ' ')}
                    </div>
                  </div>
                  <div className="bg-slate-700/50 rounded p-3">
                    <div className="text-slate-400 text-sm">Historical Trauma</div>
                    <div className={`text-lg font-semibold mt-1 ${context.historical_trauma_present ? 'text-red-400' : 'text-green-400'}`}>
                      {context.historical_trauma_present ? 'Present' : 'Not Present'}
                    </div>
                  </div>
                </div>

                {context.vulnerability_factors.length > 0 && (
                  <div className="mb-4">
                    <div className="text-slate-400 text-sm mb-2">Vulnerability Factors</div>
                    <div className="flex flex-wrap gap-2">
                      {context.vulnerability_factors.map((factor, idx) => (
                        <span key={idx} className="bg-orange-500/20 text-orange-300 text-sm px-3 py-1 rounded">
                          {factor.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {context.special_considerations.length > 0 && (
                  <div className="mb-4">
                    <div className="text-slate-400 text-sm mb-2">Special Considerations</div>
                    <ul className="space-y-1">
                      {context.special_considerations.map((consideration, idx) => (
                        <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                          <span className="text-gold-400">•</span>
                          <span>{consideration}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="bg-gold-500/10 border border-gold-500/30 rounded p-4">
                  <div className="text-gold-400 text-sm font-semibold mb-1">Recommended Approach</div>
                  <p className="text-white">{context.recommended_approach}</p>
                </div>
              </div>

              {context.neighborhood && (
                <div className="bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
                  <h4 className="text-md font-semibold text-gold-400 mb-3">Neighborhood Details</h4>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-slate-400 text-sm mb-2">Community Resources</div>
                      <ul className="space-y-1">
                        {context.neighborhood.community_resources.map((resource, idx) => (
                          <li key={idx} className="text-slate-300 text-sm">• {resource}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="text-slate-400 text-sm mb-2">Key Stakeholders</div>
                      <ul className="space-y-1">
                        {context.neighborhood.key_stakeholders.map((stakeholder, idx) => (
                          <li key={idx} className="text-slate-300 text-sm">• {stakeholder}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-slate-800/50 rounded-lg p-8 border border-gold-500/20 text-center text-slate-500">
              <p className="text-4xl mb-2">🌍</p>
              <p>Select a neighborhood to view cultural context</p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-4 border border-gold-500/20">
        <h3 className="text-lg font-semibold text-gold-400 mb-4 flex items-center gap-2">
          <span>📅</span> Active Local Events
          {events.length > 0 && (
            <span className="ml-2 bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">
              {events.length}
            </span>
          )}
        </h3>

        {events.length === 0 ? (
          <div className="text-center py-4 text-slate-500">No active events</div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {events.map((event) => (
              <div key={event.event_id} className="bg-slate-700/50 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{getEventTypeIcon(event.event_type)}</span>
                  <div className="flex-1">
                    <div className="font-medium text-white">{event.name}</div>
                    <div className="text-slate-400 text-sm">{event.location}</div>
                    <div className="text-slate-500 text-xs mt-1">
                      {new Date(event.start_time).toLocaleString()}
                    </div>
                    {event.expected_attendance > 0 && (
                      <div className="text-slate-400 text-xs mt-1">
                        Expected: {event.expected_attendance} attendees
                      </div>
                    )}
                    {event.special_considerations.length > 0 && (
                      <div className="mt-2">
                        {event.special_considerations.map((consideration, idx) => (
                          <span key={idx} className="text-xs bg-slate-600 text-slate-300 px-2 py-0.5 rounded mr-1">
                            {consideration}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

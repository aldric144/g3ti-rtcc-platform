'use client';

import React, { useState, useEffect } from 'react';

interface BehavioralSignature {
  signature_id: string;
  category: string;
  patterns: string[];
  overall_score: number;
}

interface SuspectProfile {
  profile_id: string;
  demographics: Record<string, any>;
  psychological_traits: string[];
  behavioral_indicators: string[];
  risk_assessment: Record<string, any>;
  confidence: string;
}

interface Prediction {
  prediction_id: string;
  predicted_type: string;
  risk_level: string;
  confidence: number;
  predicted_location: Record<string, any>;
  predicted_timeframe: Record<string, any>;
}

interface Props {
  caseId: string | null;
}

export default function OffenderBehaviorPanel({ caseId }: Props) {
  const [signatures, setSignatures] = useState<BehavioralSignature[]>([]);
  const [profile, setProfile] = useState<SuspectProfile | null>(null);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [activeSection, setActiveSection] = useState<'signatures' | 'profile' | 'predictions'>('signatures');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (caseId) {
      loadData();
    }
  }, [caseId]);

  const loadData = async () => {
    setLoading(true);
    setTimeout(() => {
      setSignatures([
        {
          signature_id: 'sig-001',
          category: 'modus_operandi',
          patterns: ['entry:forced_rear', 'weapon:knife', 'time:night', 'target:residential'],
          overall_score: 0.78,
        },
        {
          signature_id: 'sig-002',
          category: 'signature',
          patterns: ['trophy:jewelry', 'staging:minimal', 'forensic:gloves_used'],
          overall_score: 0.65,
        },
        {
          signature_id: 'sig-003',
          category: 'precautionary',
          patterns: ['disguise:mask', 'escape:vehicle', 'surveillance:pre_offense'],
          overall_score: 0.72,
        },
      ]);
      setProfile({
        profile_id: 'profile-001',
        demographics: {
          age_range: { min: 25, max: 35 },
          gender: 'likely_male',
          employment_status: 'likely_employed',
          education_level: 'high_school_or_above',
          residence_type: 'within_offense_area',
        },
        psychological_traits: [
          'organized_personality',
          'above_average_intelligence',
          'planning_capability',
          'forensically_aware',
        ],
        behavioral_indicators: [
          'conducts_pre_offense_surveillance',
          'selective_victim_targeting',
          'plans_escape_routes',
          'uses_vehicle_in_offenses',
        ],
        risk_assessment: {
          level: 'high',
          violence_trend: 'stable',
          reoffense_likelihood: 'high',
        },
        confidence: 'moderate',
      });
      setPredictions([
        {
          prediction_id: 'pred-001',
          predicted_type: 'burglary',
          risk_level: 'high',
          confidence: 0.72,
          predicted_location: { lat: 33.749, lng: -84.388, radius_km: 5 },
          predicted_timeframe: {
            earliest: '2024-01-15',
            most_likely: '2024-01-22',
            latest: '2024-02-01',
          },
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const getRiskColor = (level: string) => {
    const colors: Record<string, string> = {
      low: 'text-green-400',
      medium: 'text-yellow-400',
      high: 'text-orange-400',
      critical: 'text-red-400',
    };
    return colors[level] || 'text-gray-400';
  };

  if (!caseId) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-800 rounded-lg">
        <p className="text-gray-400">Select a case to view offender behavior analysis</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Offender Behavior Analysis</h2>
        <div className="flex bg-gray-700 rounded-lg p-1">
          {(['signatures', 'profile', 'predictions'] as const).map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`px-4 py-2 rounded text-sm capitalize ${activeSection === section ? 'bg-blue-600' : ''}`}
            >
              {section}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          {activeSection === 'signatures' && (
            <div className="grid grid-cols-3 gap-4">
              {signatures.map((sig) => (
                <div key={sig.signature_id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium capitalize">{sig.category.replace('_', ' ')}</h3>
                    <span className="text-sm text-blue-400">
                      {(sig.overall_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="space-y-2">
                    {sig.patterns.map((pattern, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-2 text-sm bg-gray-700 rounded px-2 py-1"
                      >
                        <span className="text-gray-400">{pattern.split(':')[0]}:</span>
                        <span className="text-white">{pattern.split(':')[1]?.replace('_', ' ')}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${sig.overall_score * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeSection === 'profile' && profile && (
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-medium mb-4">Demographics Profile</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Age Range</span>
                    <span>{profile.demographics.age_range.min} - {profile.demographics.age_range.max} years</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Gender</span>
                    <span className="capitalize">{profile.demographics.gender.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Employment</span>
                    <span className="capitalize">{profile.demographics.employment_status.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Education</span>
                    <span className="capitalize">{profile.demographics.education_level.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Residence</span>
                    <span className="capitalize">{profile.demographics.residence_type.replace('_', ' ')}</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-medium mb-4">Risk Assessment</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Risk Level</span>
                    <span className={`capitalize ${getRiskColor(profile.risk_assessment.level)}`}>
                      {profile.risk_assessment.level}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Violence Trend</span>
                    <span className="capitalize">{profile.risk_assessment.violence_trend}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Reoffense Likelihood</span>
                    <span className={`capitalize ${getRiskColor(profile.risk_assessment.reoffense_likelihood)}`}>
                      {profile.risk_assessment.reoffense_likelihood}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Profile Confidence</span>
                    <span className="capitalize">{profile.confidence}</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-medium mb-4">Psychological Traits</h3>
                <div className="flex flex-wrap gap-2">
                  {profile.psychological_traits.map((trait, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-900/50 text-purple-300 rounded-full text-sm"
                    >
                      {trait.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="font-medium mb-4">Behavioral Indicators</h3>
                <div className="flex flex-wrap gap-2">
                  {profile.behavioral_indicators.map((indicator, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-900/50 text-blue-300 rounded-full text-sm"
                    >
                      {indicator.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeSection === 'predictions' && (
            <div className="space-y-4">
              {predictions.map((pred) => (
                <div key={pred.prediction_id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-medium capitalize">
                        Predicted: {pred.predicted_type}
                      </span>
                      <span className={`px-2 py-1 rounded text-sm ${getRiskColor(pred.risk_level)} bg-gray-700`}>
                        {pred.risk_level.toUpperCase()} RISK
                      </span>
                    </div>
                    <span className="text-blue-400">
                      {(pred.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm text-gray-400 mb-2">Predicted Location</h4>
                      <div className="bg-gray-700 rounded p-3">
                        <p className="text-sm">
                          Lat: {pred.predicted_location.lat}, Lng: {pred.predicted_location.lng}
                        </p>
                        <p className="text-sm text-gray-400">
                          Radius: {pred.predicted_location.radius_km} km
                        </p>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm text-gray-400 mb-2">Predicted Timeframe</h4>
                      <div className="bg-gray-700 rounded p-3">
                        <p className="text-sm">
                          Most Likely: {pred.predicted_timeframe.most_likely}
                        </p>
                        <p className="text-sm text-gray-400">
                          Range: {pred.predicted_timeframe.earliest} - {pred.predicted_timeframe.latest}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 flex gap-2">
                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                      Create Alert
                    </button>
                    <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                      View on Map
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

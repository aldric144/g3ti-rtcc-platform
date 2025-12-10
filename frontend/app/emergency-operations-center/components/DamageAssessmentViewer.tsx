'use client';

import React, { useState, useEffect } from 'react';

interface DamageAssessment {
  assessment_id: string;
  structure_type: string;
  damage_level: string;
  habitability: boolean;
  address: {
    street: string;
    city: string;
    state: string;
  };
  damage_description: string;
  affected_area_sqft: number;
  assessed_by: string;
  created_at: string;
}

interface DroneImage {
  image_id: string;
  location: {
    lat: number;
    lng: number;
  };
  processed: boolean;
  damage_detected: boolean;
  damage_classifications: Array<{
    damage_type: string;
    damage_level: string;
    confidence: number;
  }>;
}

interface RecoveryTimeline {
  timeline_id: string;
  area_name: string;
  current_phase: string;
  total_structures_affected: number;
  structures_repaired: number;
  structures_demolished: number;
  estimated_completion: string;
}

interface HighRiskStructure {
  risk_id: string;
  structure_id: string;
  risk_score: number;
  evacuation_required: boolean;
  demolition_recommended: boolean;
  immediate_hazards: string[];
}

interface DamageMetrics {
  assessments: {
    total: number;
    by_damage_level: {
      none: number;
      minor: number;
      moderate: number;
      major: number;
      destroyed: number;
    };
  };
  drone_images: {
    total_images: number;
    processed: number;
    damage_detected: number;
  };
  risk_assessments: {
    total_assessed: number;
    high_risk: number;
    evacuation_required: number;
    demolition_recommended: number;
  };
  recovery: {
    total_timelines: number;
    total_structures_affected: number;
    total_repaired: number;
  };
}

export default function DamageAssessmentViewer() {
  const [assessments, setAssessments] = useState<DamageAssessment[]>([]);
  const [droneImages, setDroneImages] = useState<DroneImage[]>([]);
  const [timelines, setTimelines] = useState<RecoveryTimeline[]>([]);
  const [highRisk, setHighRisk] = useState<HighRiskStructure[]>([]);
  const [metrics, setMetrics] = useState<DamageMetrics | null>(null);
  const [activeTab, setActiveTab] = useState<'assessments' | 'drone' | 'recovery' | 'risk'>('assessments');
  const [damageFilter, setDamageFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDamageData();
    const interval = setInterval(fetchDamageData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDamageData = async () => {
    try {
      const [assessmentsRes, droneRes, timelinesRes, riskRes, metricsRes] = await Promise.all([
        fetch('/api/emergency/damage/assessments'),
        fetch('/api/emergency/damage/drone-images?processed_only=true'),
        fetch('/api/emergency/damage/recovery-timelines'),
        fetch('/api/emergency/damage/high-risk'),
        fetch('/api/emergency/damage/metrics'),
      ]);

      if (assessmentsRes.ok) setAssessments(await assessmentsRes.json());
      if (droneRes.ok) setDroneImages(await droneRes.json());
      if (timelinesRes.ok) setTimelines(await timelinesRes.json());
      if (riskRes.ok) setHighRisk(await riskRes.json());
      if (metricsRes.ok) setMetrics(await metricsRes.json());
    } catch (error) {
      console.error('Failed to fetch damage data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDamageLevelColor = (level: string): string => {
    switch (level) {
      case 'destroyed': return 'bg-purple-600';
      case 'major': return 'bg-red-600';
      case 'moderate': return 'bg-orange-500';
      case 'minor': return 'bg-yellow-500';
      case 'none': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getPhaseColor = (phase: string): string => {
    switch (phase) {
      case 'emergency': return 'text-red-400';
      case 'short_term': return 'text-orange-400';
      case 'intermediate': return 'text-yellow-400';
      case 'long_term': return 'text-blue-400';
      case 'completed': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const filteredAssessments = damageFilter === 'all'
    ? assessments
    : assessments.filter(a => a.damage_level === damageFilter);

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 h-full flex items-center justify-center">
        <div className="text-gray-400">Loading damage data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>🏚️</span> Damage Assessment
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('assessments')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'assessments' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Assessments
          </button>
          <button
            onClick={() => setActiveTab('drone')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'drone' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Drone
          </button>
          <button
            onClick={() => setActiveTab('recovery')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'recovery' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Recovery
          </button>
          <button
            onClick={() => setActiveTab('risk')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'risk' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            High Risk
          </button>
        </div>
      </div>

      {metrics && (
        <div className="grid grid-cols-5 gap-3 mb-4">
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Assessments</div>
            <div className="text-white text-lg font-bold">{metrics.assessments?.total || 0}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Drone Images</div>
            <div className="text-white text-lg font-bold">
              {metrics.drone_images?.processed || 0} / {metrics.drone_images?.total_images || 0}
            </div>
          </div>
          <div className={`p-3 rounded ${(metrics.risk_assessments?.high_risk || 0) > 0 ? 'bg-red-900/50' : 'bg-gray-800'}`}>
            <div className="text-gray-400 text-xs">High Risk</div>
            <div className={`text-lg font-bold ${(metrics.risk_assessments?.high_risk || 0) > 0 ? 'text-red-400' : 'text-white'}`}>
              {metrics.risk_assessments?.high_risk || 0}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Structures Affected</div>
            <div className="text-white text-lg font-bold">
              {metrics.recovery?.total_structures_affected || 0}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">Repaired</div>
            <div className="text-green-400 text-lg font-bold">{metrics.recovery?.total_repaired || 0}</div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {activeTab === 'assessments' && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-gray-400 text-sm">Filter:</span>
              <select
                value={damageFilter}
                onChange={(e) => setDamageFilter(e.target.value)}
                className="bg-gray-800 text-white px-2 py-1 rounded text-sm"
              >
                <option value="all">All Levels</option>
                <option value="destroyed">Destroyed</option>
                <option value="major">Major</option>
                <option value="moderate">Moderate</option>
                <option value="minor">Minor</option>
                <option value="none">None</option>
              </select>
            </div>

            <div className="space-y-2">
              {filteredAssessments.length === 0 ? (
                <div className="text-gray-500 text-center py-8">No assessments found</div>
              ) : (
                filteredAssessments.map(assessment => (
                  <div key={assessment.assessment_id} className="bg-gray-800 p-4 rounded">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-xs text-white ${getDamageLevelColor(assessment.damage_level)}`}>
                            {assessment.damage_level.toUpperCase()}
                          </span>
                          <span className="text-white font-medium">{assessment.structure_type}</span>
                        </div>
                        <div className="text-gray-400 text-sm mt-1">
                          {assessment.address?.street || 'Unknown address'}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-sm ${assessment.habitability ? 'text-green-400' : 'text-red-400'}`}>
                          {assessment.habitability ? 'Habitable' : 'Uninhabitable'}
                        </div>
                        <div className="text-gray-500 text-xs">
                          {assessment.affected_area_sqft.toLocaleString()} sqft
                        </div>
                      </div>
                    </div>
                    {assessment.damage_description && (
                      <div className="text-gray-400 text-sm mt-2">{assessment.damage_description}</div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'drone' && (
          <div className="space-y-2">
            {droneImages.length === 0 ? (
              <div className="text-gray-500 text-center py-8">No processed drone images</div>
            ) : (
              droneImages.map(image => (
                <div key={image.image_id} className="bg-gray-800 p-4 rounded">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-16 h-16 bg-gray-700 rounded flex items-center justify-center text-2xl">
                        📷
                      </div>
                      <div>
                        <div className="text-white font-medium">Image {image.image_id.slice(0, 8)}</div>
                        <div className="text-gray-400 text-sm">
                          {image.location.lat.toFixed(4)}, {image.location.lng.toFixed(4)}
                        </div>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded text-sm ${
                      image.damage_detected ? 'bg-red-600 text-white' : 'bg-green-600 text-white'
                    }`}>
                      {image.damage_detected ? 'Damage Detected' : 'No Damage'}
                    </div>
                  </div>
                  {image.damage_classifications.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {image.damage_classifications.map((cls, i) => (
                        <span key={i} className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs">
                          {cls.damage_type}: {cls.damage_level} ({Math.round(cls.confidence * 100)}%)
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'recovery' && (
          <div className="space-y-2">
            {timelines.length === 0 ? (
              <div className="text-gray-500 text-center py-8">No recovery timelines</div>
            ) : (
              timelines.map(timeline => (
                <div key={timeline.timeline_id} className="bg-gray-800 p-4 rounded">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-white font-medium">{timeline.area_name}</div>
                      <div className={`text-sm ${getPhaseColor(timeline.current_phase)}`}>
                        Phase: {timeline.current_phase.replace('_', ' ').toUpperCase()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-gray-400 text-xs">Est. Completion</div>
                      <div className="text-white text-sm">
                        {new Date(timeline.estimated_completion).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400 text-xs">Affected</div>
                      <div className="text-white">{timeline.total_structures_affected}</div>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">Repaired</div>
                      <div className="text-green-400">{timeline.structures_repaired}</div>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">Demolished</div>
                      <div className="text-red-400">{timeline.structures_demolished}</div>
                    </div>
                  </div>
                  <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-green-500"
                      style={{
                        width: `${Math.round((timeline.structures_repaired / timeline.total_structures_affected) * 100)}%`
                      }}
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'risk' && (
          <div className="space-y-2">
            {highRisk.length === 0 ? (
              <div className="text-gray-500 text-center py-8">No high-risk structures</div>
            ) : (
              <>
                <div className="text-red-400 text-sm mb-2">⚠️ High Risk Structures</div>
                {highRisk.map(risk => (
                  <div key={risk.risk_id} className="bg-gray-800 p-4 rounded border-l-4 border-red-500">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium">Structure {risk.structure_id.slice(0, 8)}</div>
                        <div className="flex items-center gap-2 mt-1">
                          {risk.evacuation_required && (
                            <span className="bg-red-600 text-white px-2 py-0.5 rounded text-xs">
                              EVACUATE
                            </span>
                          )}
                          {risk.demolition_recommended && (
                            <span className="bg-purple-600 text-white px-2 py-0.5 rounded text-xs">
                              DEMOLISH
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-gray-400 text-xs">Risk Score</div>
                        <div className={`text-lg font-bold ${
                          risk.risk_score >= 0.9 ? 'text-red-400' :
                          risk.risk_score >= 0.7 ? 'text-orange-400' : 'text-yellow-400'
                        }`}>
                          {Math.round(risk.risk_score * 100)}%
                        </div>
                      </div>
                    </div>
                    {risk.immediate_hazards.length > 0 && (
                      <div className="mt-2">
                        <div className="text-gray-400 text-xs mb-1">Immediate Hazards</div>
                        <div className="flex flex-wrap gap-1">
                          {risk.immediate_hazards.map((hazard, i) => (
                            <span key={i} className="bg-red-900/50 text-red-300 px-2 py-0.5 rounded text-xs">
                              {hazard}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

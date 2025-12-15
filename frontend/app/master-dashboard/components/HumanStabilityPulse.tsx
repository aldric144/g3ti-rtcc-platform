'use client';

import React from 'react';
import { useMasterStore } from '../../../stores/masterStore';

const trendColors: Record<string, string> = {
  improving: '#22c55e',
  stable: '#3b82f6',
  declining: '#ef4444',
};

const trendIcons: Record<string, string> = {
  improving: '↑',
  stable: '→',
  declining: '↓',
};

export default function HumanStabilityPulse() {
  const { humanStability } = useMasterStore();

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    return '#ef4444';
  };

  return (
    <div
      style={{
        backgroundColor: '#0d1f3c',
        borderRadius: '12px',
        border: '1px solid #1e3a5f',
        padding: '16px',
        height: '200px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '12px',
        }}
      >
        <h3 style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: '#ffffff' }}>
          Human Stability
        </h3>
        <span
          style={{
            fontSize: '12px',
            color: trendColors[humanStability.trend],
            fontWeight: 'bold',
          }}
        >
          {trendIcons[humanStability.trend]} {humanStability.trend}
        </span>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '12px' }}>
        <div
          style={{
            fontSize: '36px',
            fontWeight: 'bold',
            color: getScoreColor(humanStability.overall_score),
          }}
        >
          {humanStability.overall_score}
        </div>
        <div style={{ fontSize: '10px', color: '#94a3b8' }}>Overall Score</div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '10px', color: '#94a3b8' }}>Mental Health Alerts</span>
          <span
            style={{
              fontSize: '12px',
              fontWeight: 'bold',
              color: humanStability.mental_health_alerts > 5 ? '#ef4444' : '#eab308',
            }}
          >
            {humanStability.mental_health_alerts}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '10px', color: '#94a3b8' }}>Crisis Interventions</span>
          <span
            style={{
              fontSize: '12px',
              fontWeight: 'bold',
              color: humanStability.crisis_interventions > 3 ? '#ef4444' : '#22c55e',
            }}
          >
            {humanStability.crisis_interventions}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '10px', color: '#94a3b8' }}>Community Wellness</span>
          <span
            style={{
              fontSize: '12px',
              fontWeight: 'bold',
              color: getScoreColor(humanStability.community_wellness),
            }}
          >
            {humanStability.community_wellness}%
          </span>
        </div>
      </div>
    </div>
  );
}

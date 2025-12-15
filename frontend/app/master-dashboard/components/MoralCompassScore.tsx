'use client';

import React from 'react';
import { useMasterStore } from '../../../stores/masterStore';

export default function MoralCompassScore() {
  const { moralCompass } = useMasterStore();

  const getScoreColor = (score: number) => {
    if (score >= 90) return '#22c55e';
    if (score >= 70) return '#eab308';
    return '#ef4444';
  };

  const metrics = [
    { label: 'Constitutional', value: moralCompass.constitutional_compliance },
    { label: 'Ethical', value: moralCompass.ethical_alignment },
    { label: 'Bias Detection', value: moralCompass.bias_detection },
    { label: 'Fairness', value: moralCompass.fairness_index },
  ];

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
          AI Moral Compass
        </h3>
        <span
          style={{
            fontSize: '10px',
            color: '#22c55e',
            fontWeight: 'bold',
          }}
        >
          COMPLIANT
        </span>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '12px' }}>
        <div
          style={{
            fontSize: '36px',
            fontWeight: 'bold',
            color: getScoreColor(moralCompass.overall_score),
          }}
        >
          {moralCompass.overall_score}
        </div>
        <div style={{ fontSize: '10px', color: '#94a3b8' }}>Compliance Score</div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {metrics.map((metric) => (
          <div key={metric.label} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '10px', color: '#94a3b8', flex: 1 }}>{metric.label}</span>
            <div
              style={{
                width: '60px',
                height: '4px',
                backgroundColor: '#1e3a5f',
                borderRadius: '2px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${metric.value}%`,
                  height: '100%',
                  backgroundColor: getScoreColor(metric.value),
                }}
              />
            </div>
            <span
              style={{
                fontSize: '10px',
                fontWeight: 'bold',
                color: getScoreColor(metric.value),
                width: '28px',
                textAlign: 'right',
              }}
            >
              {metric.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

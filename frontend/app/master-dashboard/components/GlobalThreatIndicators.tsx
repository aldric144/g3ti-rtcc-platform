'use client';

import React from 'react';
import { useMasterStore } from '../../../stores/masterStore';

const threatLevelColors: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
};

export default function GlobalThreatIndicators() {
  const { threats } = useMasterStore();

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const threatLevelOrder = ['critical', 'high', 'medium', 'low'];
  const sortedThreats = [...threats].sort(
    (a, b) => threatLevelOrder.indexOf(a.threat_level) - threatLevelOrder.indexOf(b.threat_level)
  );

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
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600', color: '#ffffff' }}>
          Global Threat Indicators
        </h3>
        <div style={{ display: 'flex', gap: '4px' }}>
          {threatLevelOrder.map((level) => {
            const count = threats.filter((t) => t.threat_level === level).length;
            return count > 0 ? (
              <span
                key={level}
                style={{
                  fontSize: '10px',
                  fontWeight: 'bold',
                  color: threatLevelColors[level],
                  padding: '2px 6px',
                  backgroundColor: `${threatLevelColors[level]}20`,
                  borderRadius: '4px',
                }}
              >
                {count}
              </span>
            ) : null;
          })}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {sortedThreats.length > 0 ? (
          sortedThreats.map((threat) => (
            <div
              key={threat.threat_id}
              style={{
                padding: '10px',
                backgroundColor: '#1e3a5f',
                borderRadius: '4px',
                marginBottom: '6px',
                borderLeft: `3px solid ${threatLevelColors[threat.threat_level]}`,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span
                      style={{
                        fontSize: '9px',
                        fontWeight: 'bold',
                        color: threatLevelColors[threat.threat_level],
                        textTransform: 'uppercase',
                      }}
                    >
                      {threat.threat_level}
                    </span>
                    <span style={{ fontSize: '10px', color: '#64748b' }}>
                      {threat.source.replace('_', ' ')}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', fontWeight: '500', color: '#ffffff', marginBottom: '4px' }}>
                    {threat.title}
                  </div>
                  <div style={{ display: 'flex', gap: '8px', fontSize: '10px', color: '#94a3b8' }}>
                    <span>{formatTime(threat.timestamp)}</span>
                    {threat.affected_areas.length > 0 && (
                      <span>{threat.affected_areas[0]}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', color: '#64748b', padding: '20px', fontSize: '14px' }}>
            No active threats
          </div>
        )}
      </div>
    </div>
  );
}

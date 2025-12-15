'use client';

import React, { useState } from 'react';
import { useMasterStore, Alert } from '../../../stores/masterStore';

const severityColors: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
  info: '#3b82f6',
};

const severityBgColors: Record<string, string> = {
  critical: 'rgba(239, 68, 68, 0.1)',
  high: 'rgba(249, 115, 22, 0.1)',
  medium: 'rgba(234, 179, 8, 0.1)',
  low: 'rgba(34, 197, 94, 0.1)',
  info: 'rgba(59, 130, 246, 0.1)',
};

export default function UnifiedAlertsFeed() {
  const { alerts, updateAlert } = useMasterStore();
  const [filter, setFilter] = useState<string>('all');

  const activeAlerts = alerts.filter((a) => a.active);
  const filteredAlerts = filter === 'all' 
    ? activeAlerts 
    : activeAlerts.filter((a) => a.severity === filter);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const handleAcknowledge = (alertId: string) => {
    updateAlert(alertId, { action_taken: true });
  };

  return (
    <div
      style={{
        backgroundColor: '#0d1f3c',
        borderRadius: '12px',
        border: '1px solid #1e3a5f',
        padding: '16px',
        height: '400px',
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
          Unified Alerts Feed
        </h3>
        <span
          style={{
            backgroundColor: '#ef4444',
            color: '#ffffff',
            fontSize: '12px',
            fontWeight: 'bold',
            padding: '2px 8px',
            borderRadius: '10px',
          }}
        >
          {activeAlerts.length} Active
        </span>
      </div>

      <div style={{ display: 'flex', gap: '4px', marginBottom: '12px', flexWrap: 'wrap' }}>
        {['all', 'critical', 'high', 'medium', 'low'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '4px 8px',
              fontSize: '11px',
              backgroundColor: filter === f ? '#c9a227' : '#1e3a5f',
              color: filter === f ? '#0a1628' : '#94a3b8',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              textTransform: 'capitalize',
            }}
          >
            {f}
          </button>
        ))}
      </div>

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {filteredAlerts.map((alert) => (
          <div
            key={alert.alert_id}
            style={{
              backgroundColor: severityBgColors[alert.severity],
              borderLeft: `3px solid ${severityColors[alert.severity]}`,
              borderRadius: '4px',
              padding: '10px',
              marginBottom: '8px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span
                    style={{
                      fontSize: '10px',
                      fontWeight: 'bold',
                      color: severityColors[alert.severity],
                      textTransform: 'uppercase',
                    }}
                  >
                    {alert.severity}
                  </span>
                  <span style={{ fontSize: '10px', color: '#94a3b8' }}>
                    {alert.source.replace('_', ' ')}
                  </span>
                </div>
                <div style={{ fontSize: '13px', fontWeight: '500', color: '#ffffff', marginBottom: '4px' }}>
                  {alert.title}
                </div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>
                  {alert.summary}
                </div>
                <div style={{ display: 'flex', gap: '8px', marginTop: '6px', fontSize: '10px' }}>
                  <span style={{ color: '#64748b' }}>{formatTime(alert.timestamp)}</span>
                  {alert.affected_areas.length > 0 && (
                    <span style={{ color: '#64748b' }}>{alert.affected_areas[0]}</span>
                  )}
                  {alert.constitutional_compliance_tag && (
                    <span style={{ color: '#22c55e' }}>Constitutional</span>
                  )}
                </div>
              </div>
              {alert.requires_action && !alert.action_taken && (
                <button
                  onClick={() => handleAcknowledge(alert.alert_id)}
                  style={{
                    padding: '4px 8px',
                    fontSize: '10px',
                    backgroundColor: '#c9a227',
                    color: '#0a1628',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                  }}
                >
                  ACK
                </button>
              )}
            </div>
          </div>
        ))}

        {filteredAlerts.length === 0 && (
          <div style={{ textAlign: 'center', color: '#64748b', padding: '20px', fontSize: '14px' }}>
            No alerts matching filter
          </div>
        )}
      </div>
    </div>
  );
}

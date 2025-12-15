'use client';

import React from 'react';
import { useMasterStore } from '../../../stores/masterStore';

const priorityColors: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
};

const statusColors: Record<string, string> = {
  open: '#3b82f6',
  active: '#22c55e',
  pending: '#eab308',
  closed: '#6b7280',
};

export default function InvestigationsQueue() {
  const { investigations } = useMasterStore();

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
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
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600', color: '#ffffff' }}>
          Investigations Queue
        </h3>
        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
          {investigations.filter((i) => i.status !== 'closed').length} Active
        </span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {investigations.map((investigation) => (
          <div
            key={investigation.case_id}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px',
              backgroundColor: '#1e3a5f',
              borderRadius: '4px',
              marginBottom: '6px',
              borderLeft: `3px solid ${priorityColors[investigation.priority]}`,
            }}
          >
            <div style={{ flex: 1, minWidth: 0 }}>
              <div
                style={{
                  fontSize: '12px',
                  fontWeight: '500',
                  color: '#ffffff',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {investigation.title}
              </div>
              <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                <span style={{ fontSize: '10px', color: '#94a3b8' }}>
                  {investigation.assigned_to}
                </span>
                <span style={{ fontSize: '10px', color: '#64748b' }}>
                  {formatDate(investigation.updated_at)}
                </span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontSize: '9px',
                  fontWeight: 'bold',
                  color: statusColors[investigation.status],
                  textTransform: 'uppercase',
                  padding: '2px 6px',
                  backgroundColor: `${statusColors[investigation.status]}20`,
                  borderRadius: '4px',
                }}
              >
                {investigation.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

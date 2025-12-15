'use client';

import React from 'react';
import { useMasterStore } from '../../../stores/masterStore';

const statusColors: Record<string, string> = {
  available: '#22c55e',
  on_call: '#3b82f6',
  responding: '#f97316',
  busy: '#eab308',
  off_duty: '#6b7280',
};

export default function OfficerSafetyGrid() {
  const { officers } = useMasterStore();

  const statusCounts = officers.reduce((acc, officer) => {
    acc[officer.status] = (acc[officer.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div
      style={{
        backgroundColor: '#0d1f3c',
        borderRadius: '12px',
        border: '1px solid #1e3a5f',
        padding: '16px',
        height: '200px',
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
          Officer Safety Status
        </h3>
        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
          {officers.length} Total
        </span>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
        {Object.entries(statusCounts).map(([status, count]) => (
          <div
            key={status}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              backgroundColor: '#1e3a5f',
              borderRadius: '4px',
            }}
          >
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: statusColors[status] || '#6b7280',
              }}
            />
            <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'capitalize' }}>
              {status.replace('_', ' ')}: {count}
            </span>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '8px' }}>
        {officers.slice(0, 10).map((officer) => (
          <div
            key={officer.officer_id}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              padding: '8px',
              backgroundColor: '#1e3a5f',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
            title={`${officer.name}\n${officer.badge_number}\nStatus: ${officer.status}${officer.current_assignment ? `\nAssignment: ${officer.current_assignment}` : ''}`}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: '#0d1f3c',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: `2px solid ${statusColors[officer.status] || '#6b7280'}`,
                marginBottom: '4px',
              }}
            >
              <span style={{ fontSize: '10px', fontWeight: 'bold', color: '#ffffff' }}>
                {officer.name.split(' ')[1]?.charAt(0) || officer.name.charAt(0)}
              </span>
            </div>
            <span style={{ fontSize: '9px', color: '#94a3b8', textAlign: 'center' }}>
              {officer.badge_number}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

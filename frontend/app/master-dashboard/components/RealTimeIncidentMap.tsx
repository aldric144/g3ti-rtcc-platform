'use client';

import React from 'react';
import { useMasterStore } from '../../../stores/masterStore';

export default function RealTimeIncidentMap() {
  const { alerts, officers, drones } = useMasterStore();

  const activeAlerts = alerts.filter((a) => a.active);

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
          Real-Time Incident Map
        </h3>
        <div style={{ display: 'flex', gap: '16px', fontSize: '12px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
            <span style={{ color: '#94a3b8' }}>Incidents ({activeAlerts.length})</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#3b82f6' }} />
            <span style={{ color: '#94a3b8' }}>Officers ({officers.length})</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#22c55e' }} />
            <span style={{ color: '#94a3b8' }}>Drones ({drones.length})</span>
          </span>
        </div>
      </div>

      <div
        style={{
          flex: 1,
          backgroundColor: '#1e3a5f',
          borderRadius: '8px',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: `
              linear-gradient(rgba(30, 58, 95, 0.5) 1px, transparent 1px),
              linear-gradient(90deg, rgba(30, 58, 95, 0.5) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />

        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            color: '#c9a227',
            fontWeight: 'bold',
            fontSize: '14px',
          }}
        >
          RIVIERA BEACH
          <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '4px' }}>
            26.7753° N, 80.0589° W
          </div>
        </div>

        {activeAlerts.map((alert, index) => (
          <div
            key={alert.alert_id}
            style={{
              position: 'absolute',
              top: `${20 + (index * 15) % 60}%`,
              left: `${15 + (index * 20) % 70}%`,
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              backgroundColor: alert.severity === 'critical' ? '#ef4444' : alert.severity === 'high' ? '#f97316' : '#eab308',
              border: '2px solid #ffffff',
              cursor: 'pointer',
              animation: alert.severity === 'critical' ? 'pulse 1s infinite' : 'none',
            }}
            title={alert.title}
          />
        ))}

        {officers.map((officer, index) => (
          <div
            key={officer.officer_id}
            style={{
              position: 'absolute',
              top: `${30 + (index * 12) % 50}%`,
              left: `${25 + (index * 18) % 60}%`,
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: officer.status === 'responding' ? '#f97316' : '#3b82f6',
              border: '2px solid #ffffff',
              cursor: 'pointer',
            }}
            title={`${officer.name} - ${officer.status}`}
          />
        ))}

        {drones.filter(d => d.status === 'active').map((drone, index) => (
          <div
            key={drone.drone_id}
            style={{
              position: 'absolute',
              top: `${15 + (index * 25) % 40}%`,
              left: `${40 + (index * 15) % 50}%`,
              width: '14px',
              height: '14px',
              backgroundColor: '#22c55e',
              transform: 'rotate(45deg)',
              cursor: 'pointer',
            }}
            title={`${drone.name} - Battery: ${drone.battery}%`}
          />
        ))}

        <div
          style={{
            position: 'absolute',
            bottom: '8px',
            right: '8px',
            display: 'flex',
            gap: '4px',
          }}
        >
          <button
            style={{
              padding: '4px 8px',
              backgroundColor: '#0d1f3c',
              border: '1px solid #1e3a5f',
              borderRadius: '4px',
              color: '#94a3b8',
              fontSize: '10px',
              cursor: 'pointer',
            }}
          >
            Zoom +
          </button>
          <button
            style={{
              padding: '4px 8px',
              backgroundColor: '#0d1f3c',
              border: '1px solid #1e3a5f',
              borderRadius: '4px',
              color: '#94a3b8',
              fontSize: '10px',
              cursor: 'pointer',
            }}
          >
            Zoom -
          </button>
        </div>
      </div>
    </div>
  );
}

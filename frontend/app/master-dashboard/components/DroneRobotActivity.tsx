'use client';

import React from 'react';
import { useMasterStore } from '../../../stores/masterStore';

const droneStatusColors: Record<string, string> = {
  active: '#22c55e',
  standby: '#3b82f6',
  returning: '#f97316',
  charging: '#eab308',
  maintenance: '#6b7280',
};

const robotStatusColors: Record<string, string> = {
  active: '#22c55e',
  standby: '#3b82f6',
  patrolling: '#22c55e',
  charging: '#eab308',
  maintenance: '#6b7280',
};

export default function DroneRobotActivity() {
  const { drones, robots } = useMasterStore();

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
          Drone & Robot Activity
        </h3>
      </div>

      <div style={{ display: 'flex', gap: '16px' }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '12px', color: '#c9a227', marginBottom: '8px', fontWeight: '600' }}>
            Drones ({drones.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {drones.map((drone) => (
              <div
                key={drone.drone_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '6px 8px',
                  backgroundColor: '#1e3a5f',
                  borderRadius: '4px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: droneStatusColors[drone.status] || '#6b7280',
                    }}
                  />
                  <span style={{ fontSize: '11px', color: '#ffffff' }}>{drone.name}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div
                    style={{
                      width: '40px',
                      height: '6px',
                      backgroundColor: '#0d1f3c',
                      borderRadius: '3px',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        width: `${drone.battery}%`,
                        height: '100%',
                        backgroundColor: drone.battery > 50 ? '#22c55e' : drone.battery > 20 ? '#eab308' : '#ef4444',
                      }}
                    />
                  </div>
                  <span style={{ fontSize: '10px', color: '#94a3b8' }}>{drone.battery}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '12px', color: '#c9a227', marginBottom: '8px', fontWeight: '600' }}>
            Robots ({robots.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {robots.map((robot) => (
              <div
                key={robot.robot_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '6px 8px',
                  backgroundColor: '#1e3a5f',
                  borderRadius: '4px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: robotStatusColors[robot.status] || '#6b7280',
                    }}
                  />
                  <span style={{ fontSize: '11px', color: '#ffffff' }}>{robot.name}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div
                    style={{
                      width: '40px',
                      height: '6px',
                      backgroundColor: '#0d1f3c',
                      borderRadius: '3px',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        width: `${robot.battery}%`,
                        height: '100%',
                        backgroundColor: robot.battery > 50 ? '#22c55e' : robot.battery > 20 ? '#eab308' : '#ef4444',
                      }}
                    />
                  </div>
                  <span style={{ fontSize: '10px', color: '#94a3b8' }}>{robot.battery}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

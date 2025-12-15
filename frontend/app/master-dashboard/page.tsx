'use client';

import React from 'react';
import MasterLayout from '../../components/navigation/MasterLayout';
import RealTimeIncidentMap from './components/RealTimeIncidentMap';
import UnifiedAlertsFeed from './components/UnifiedAlertsFeed';
import OfficerSafetyGrid from './components/OfficerSafetyGrid';
import TacticalHeatmapOverview from './components/TacticalHeatmapOverview';
import DroneRobotActivity from './components/DroneRobotActivity';
import InvestigationsQueue from './components/InvestigationsQueue';
import GlobalThreatIndicators from './components/GlobalThreatIndicators';
import HumanStabilityPulse from './components/HumanStabilityPulse';
import MoralCompassScore from './components/MoralCompassScore';

export default function MasterDashboardPage() {
  return (
    <MasterLayout currentPath="/master-dashboard">
      <div style={{ color: '#ffffff' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px',
          }}
        >
          <div>
            <h1
              style={{
                fontSize: '28px',
                fontWeight: 'bold',
                color: '#c9a227',
                margin: 0,
              }}
            >
              G3TI RTCC Master Dashboard
            </h1>
            <p style={{ color: '#94a3b8', margin: '4px 0 0 0', fontSize: '14px' }}>
              Unified Intelligence Platform - Riviera Beach Police Department
            </p>
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              backgroundColor: '#1e3a5f',
              borderRadius: '8px',
            }}
          >
            <span
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: '#22c55e',
                animation: 'pulse 2s infinite',
              }}
            />
            <span style={{ fontSize: '14px', color: '#94a3b8' }}>System Online</span>
          </div>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(12, 1fr)',
            gridTemplateRows: 'auto',
            gap: '16px',
          }}
        >
          <div style={{ gridColumn: 'span 8', gridRow: 'span 2' }}>
            <RealTimeIncidentMap />
          </div>

          <div style={{ gridColumn: 'span 4', gridRow: 'span 2' }}>
            <UnifiedAlertsFeed />
          </div>

          <div style={{ gridColumn: 'span 4' }}>
            <OfficerSafetyGrid />
          </div>

          <div style={{ gridColumn: 'span 4' }}>
            <TacticalHeatmapOverview />
          </div>

          <div style={{ gridColumn: 'span 4' }}>
            <DroneRobotActivity />
          </div>

          <div style={{ gridColumn: 'span 4' }}>
            <InvestigationsQueue />
          </div>

          <div style={{ gridColumn: 'span 4' }}>
            <GlobalThreatIndicators />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <HumanStabilityPulse />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <MoralCompassScore />
          </div>
        </div>
      </div>

      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </MasterLayout>
  );
}

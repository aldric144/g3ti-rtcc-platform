'use client';

import React, { useState, useEffect } from 'react';

interface TopNavBarProps {
  onMenuToggle: () => void;
  alertCount: number;
  operatorName: string;
  operatorStatus: 'online' | 'away' | 'busy' | 'offline';
}

export default function TopNavBar({
  onMenuToggle,
  alertCount,
  operatorName,
  operatorStatus,
}: TopNavBarProps) {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [searchQuery, setSearchQuery] = useState('');
  const [showAlerts, setShowAlerts] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date, timezone: string) => {
    return date.toLocaleTimeString('en-US', {
      timeZone: timezone,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  const statusColors = {
    online: '#22c55e',
    away: '#eab308',
    busy: '#ef4444',
    offline: '#6b7280',
  };

  return (
    <nav
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        height: '64px',
        backgroundColor: '#0a1628',
        borderBottom: '1px solid #1e3a5f',
        color: '#ffffff',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          onClick={onMenuToggle}
          style={{
            background: 'none',
            border: 'none',
            color: '#ffffff',
            cursor: 'pointer',
            padding: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" />
          </svg>
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              backgroundColor: '#c9a227',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              fontSize: '14px',
              color: '#0a1628',
            }}
          >
            RBPD
          </div>
          <div>
            <div style={{ fontWeight: 'bold', fontSize: '16px' }}>G3TI RTCC-UIP</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>
              Riviera Beach Police Department
            </div>
          </div>
        </div>
      </div>

      <div style={{ flex: 1, maxWidth: '500px', margin: '0 32px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#1e3a5f',
            borderRadius: '8px',
            padding: '8px 16px',
          }}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="#94a3b8"
            style={{ marginRight: '8px' }}
          >
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
          </svg>
          <input
            type="text"
            placeholder="AI-Powered Search (Ctrl+K)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              flex: 1,
              background: 'none',
              border: 'none',
              color: '#ffffff',
              fontSize: '14px',
              outline: 'none',
            }}
          />
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        <div style={{ textAlign: 'right', fontSize: '12px' }}>
          <div style={{ color: '#94a3b8' }}>UTC</div>
          <div style={{ fontFamily: 'monospace', fontSize: '14px' }}>
            {formatTime(currentTime, 'UTC')}
          </div>
        </div>
        <div style={{ textAlign: 'right', fontSize: '12px' }}>
          <div style={{ color: '#94a3b8' }}>Local (EST)</div>
          <div style={{ fontFamily: 'monospace', fontSize: '14px' }}>
            {formatTime(currentTime, 'America/New_York')}
          </div>
        </div>

        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowAlerts(!showAlerts)}
            style={{
              background: 'none',
              border: 'none',
              color: '#ffffff',
              cursor: 'pointer',
              padding: '8px',
              position: 'relative',
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" />
            </svg>
            {alertCount > 0 && (
              <span
                style={{
                  position: 'absolute',
                  top: '4px',
                  right: '4px',
                  backgroundColor: '#ef4444',
                  color: '#ffffff',
                  fontSize: '10px',
                  fontWeight: 'bold',
                  borderRadius: '50%',
                  width: '18px',
                  height: '18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {alertCount > 99 ? '99+' : alertCount}
              </span>
            )}
          </button>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 12px',
            backgroundColor: '#1e3a5f',
            borderRadius: '8px',
          }}
        >
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: '#c9a227',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              fontSize: '12px',
              color: '#0a1628',
            }}
          >
            {operatorName.charAt(0).toUpperCase()}
          </div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: '500' }}>{operatorName}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: statusColors[operatorStatus],
                }}
              />
              <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'capitalize' }}>
                {operatorStatus}
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

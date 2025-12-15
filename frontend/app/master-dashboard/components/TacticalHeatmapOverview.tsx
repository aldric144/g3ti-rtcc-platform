'use client';

import React from 'react';

interface HeatmapCell {
  x: number;
  y: number;
  intensity: number;
}

export default function TacticalHeatmapOverview() {
  const heatmapData: HeatmapCell[] = [
    { x: 2, y: 1, intensity: 0.8 },
    { x: 3, y: 1, intensity: 0.6 },
    { x: 2, y: 2, intensity: 0.9 },
    { x: 3, y: 2, intensity: 0.7 },
    { x: 4, y: 2, intensity: 0.4 },
    { x: 1, y: 3, intensity: 0.3 },
    { x: 2, y: 3, intensity: 0.5 },
    { x: 5, y: 3, intensity: 0.6 },
    { x: 4, y: 4, intensity: 0.4 },
    { x: 5, y: 4, intensity: 0.5 },
  ];

  const getColor = (intensity: number) => {
    if (intensity >= 0.8) return 'rgba(239, 68, 68, 0.8)';
    if (intensity >= 0.6) return 'rgba(249, 115, 22, 0.7)';
    if (intensity >= 0.4) return 'rgba(234, 179, 8, 0.6)';
    return 'rgba(34, 197, 94, 0.4)';
  };

  const gridSize = 6;
  const cellSize = 24;

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
          Tactical Heatmap
        </h3>
        <span style={{ fontSize: '12px', color: '#94a3b8' }}>Last 24h</span>
      </div>

      <div style={{ display: 'flex', gap: '16px' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${gridSize}, ${cellSize}px)`,
            gridTemplateRows: `repeat(${gridSize}, ${cellSize}px)`,
            gap: '2px',
            backgroundColor: '#1e3a5f',
            padding: '4px',
            borderRadius: '4px',
          }}
        >
          {Array.from({ length: gridSize * gridSize }).map((_, index) => {
            const x = index % gridSize;
            const y = Math.floor(index / gridSize);
            const cell = heatmapData.find((c) => c.x === x && c.y === y);
            return (
              <div
                key={index}
                style={{
                  width: cellSize,
                  height: cellSize,
                  backgroundColor: cell ? getColor(cell.intensity) : 'rgba(30, 58, 95, 0.3)',
                  borderRadius: '2px',
                }}
              />
            );
          })}
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '8px' }}>
            Crime Density
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: 'rgba(239, 68, 68, 0.8)', borderRadius: '2px' }} />
              <span style={{ fontSize: '10px', color: '#94a3b8' }}>High (80%+)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: 'rgba(249, 115, 22, 0.7)', borderRadius: '2px' }} />
              <span style={{ fontSize: '10px', color: '#94a3b8' }}>Medium (60-80%)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: 'rgba(234, 179, 8, 0.6)', borderRadius: '2px' }} />
              <span style={{ fontSize: '10px', color: '#94a3b8' }}>Low (40-60%)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: 'rgba(34, 197, 94, 0.4)', borderRadius: '2px' }} />
              <span style={{ fontSize: '10px', color: '#94a3b8' }}>Minimal (&lt;40%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import React from 'react';
import { useTheme } from '@/lib/theme';

export function TransitionOverlay() {
  const { isTransitioning, theme } = useTheme();

  if (!isTransitioning) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-[9999]">
      {/* Blur overlay */}
      <div
        className="absolute inset-0 animate-pulse"
        style={{
          backdropFilter: 'blur(4px)',
          background: `radial-gradient(circle at center, transparent 0%, ${theme.colors.background}40 100%)`,
          animation: 'fadeInOut 1s ease-in-out',
        }}
      />

      {/* Cosmic ripple rings */}
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
        <div
          className="absolute h-[200vmax] w-[200vmax] rounded-full"
          style={{
            border: `3px solid ${theme.colors.neuralBlue}`,
            animation: 'rippleExpand 1s ease-out forwards',
            opacity: 0.6,
          }}
        />
        <div
          className="absolute h-[200vmax] w-[200vmax] rounded-full"
          style={{
            border: `2px solid ${theme.colors.authorityGold}`,
            animation: 'rippleExpand 1s ease-out 0.1s forwards',
            opacity: 0.4,
          }}
        />
        <div
          className="absolute h-[200vmax] w-[200vmax] rounded-full"
          style={{
            border: `2px solid ${theme.colors.quantumPink}`,
            animation: 'rippleExpand 1s ease-out 0.2s forwards',
            opacity: 0.3,
          }}
        />
      </div>

      {/* Nebula sweep */}
      <div
        className="absolute inset-0"
        style={{
          background: `linear-gradient(90deg, transparent 0%, ${theme.colors.neuralBlue}20 50%, transparent 100%)`,
          animation: 'nebulaSweep 1s ease-in-out forwards',
        }}
      />

      <style jsx>{`
        @keyframes fadeInOut {
          0% {
            opacity: 0;
          }
          30% {
            opacity: 1;
          }
          70% {
            opacity: 1;
          }
          100% {
            opacity: 0;
          }
        }

        @keyframes rippleExpand {
          0% {
            transform: scale(0);
            opacity: 0.8;
          }
          100% {
            transform: scale(1);
            opacity: 0;
          }
        }

        @keyframes nebulaSweep {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
}

export default TransitionOverlay;

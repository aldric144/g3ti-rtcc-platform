'use client';

import React, { ReactNode } from 'react';
import { ThemeProvider } from '@/lib/theme';
import { CosmicBackground } from './CosmicBackground';
import { TransitionOverlay } from './TransitionOverlay';

interface ThemeProviderWrapperProps {
  children: ReactNode;
}

export function ThemeProviderWrapper({ children }: ThemeProviderWrapperProps) {
  return (
    <ThemeProvider>
      <CosmicBackground />
      <TransitionOverlay />
      <div className="relative z-10">{children}</div>
    </ThemeProvider>
  );
}

export default ThemeProviderWrapper;

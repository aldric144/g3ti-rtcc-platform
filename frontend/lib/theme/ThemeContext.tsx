'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { ThemeMode, ThemeConfig, themes, defaultTheme, getTheme } from './theme-config';

interface ThemeContextType {
  theme: ThemeConfig;
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
  isTransitioning: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'g3ti-theme-mode';

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [themeMode, setThemeModeState] = useState<ThemeMode>(defaultTheme);
  const [theme, setTheme] = useState<ThemeConfig>(getTheme(defaultTheme));
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Load saved theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null;
    if (savedTheme && themes[savedTheme]) {
      setThemeModeState(savedTheme);
      setTheme(getTheme(savedTheme));
    }
  }, []);

  // Apply theme CSS variables
  useEffect(() => {
    const root = document.documentElement;
    const colors = theme.colors;

    // Set CSS custom properties
    root.style.setProperty('--g3ti-background', colors.background);
    root.style.setProperty('--g3ti-background-secondary', colors.backgroundSecondary);
    root.style.setProperty('--g3ti-background-tertiary', colors.backgroundTertiary);
    root.style.setProperty('--g3ti-text-primary', colors.textPrimary);
    root.style.setProperty('--g3ti-text-secondary', colors.textSecondary);
    root.style.setProperty('--g3ti-text-muted', colors.textMuted);
    root.style.setProperty('--g3ti-neural-blue', colors.neuralBlue);
    root.style.setProperty('--g3ti-authority-gold', colors.authorityGold);
    root.style.setProperty('--g3ti-quantum-pink', colors.quantumPink);
    root.style.setProperty('--g3ti-threat-red', colors.threatRed);
    root.style.setProperty('--g3ti-panel-background', colors.panelBackground);
    root.style.setProperty('--g3ti-panel-border', colors.panelBorder);
    root.style.setProperty('--g3ti-panel-glow', colors.panelGlow);
    root.style.setProperty('--g3ti-online', colors.online);
    root.style.setProperty('--g3ti-offline', colors.offline);
    root.style.setProperty('--g3ti-degraded', colors.degraded);
    root.style.setProperty('--g3ti-camera-rbpd', colors.cameraRBPD);
    root.style.setProperty('--g3ti-camera-fdot', colors.cameraFDOT);
    root.style.setProperty('--g3ti-camera-lpr', colors.cameraLPR);
    root.style.setProperty('--g3ti-camera-ptz', colors.cameraPTZ);

    // Set theme class on body
    document.body.classList.remove('theme-neural-cosmic-dark', 'theme-cosmic-light-ops', 'theme-high-contrast-tactical');
    document.body.classList.add(`theme-${themeMode}`);

    // Set dark mode class for Tailwind
    if (themeMode === 'cosmic-light-ops') {
      document.documentElement.classList.remove('dark');
    } else {
      document.documentElement.classList.add('dark');
    }
  }, [theme, themeMode]);

  const setThemeMode = useCallback((mode: ThemeMode) => {
    if (mode === themeMode) return;

    // Start transition animation
    setIsTransitioning(true);

    // Add transition class to body
    document.body.classList.add('theme-transitioning');

    // Delay theme change slightly for animation effect
    setTimeout(() => {
      setThemeModeState(mode);
      setTheme(getTheme(mode));
      localStorage.setItem(THEME_STORAGE_KEY, mode);

      // End transition after animation completes
      setTimeout(() => {
        setIsTransitioning(false);
        document.body.classList.remove('theme-transitioning');
      }, 800);
    }, 200);
  }, [themeMode]);

  return (
    <ThemeContext.Provider value={{ theme, themeMode, setThemeMode, isTransitioning }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

export { ThemeContext };

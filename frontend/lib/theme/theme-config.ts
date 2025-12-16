/**
 * G3TI Super Theme Configuration - "Neural Cosmic Matrix"
 * 
 * A fusion of:
 * - Neural Shield (futuristic AI visuals)
 * - Threat Matrix Gold (elite command styling)
 * - Cosmic Ops (tactical cinematic dark theme)
 */

export type ThemeMode = 'neural-cosmic-dark' | 'cosmic-light-ops' | 'high-contrast-tactical';

export interface ThemeColors {
  // Core backgrounds
  background: string;
  backgroundSecondary: string;
  backgroundTertiary: string;
  
  // Text colors
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  
  // Brand colors
  neuralBlue: string;
  authorityGold: string;
  quantumPink: string;
  threatRed: string;
  
  // Panel styling
  panelBackground: string;
  panelBorder: string;
  panelGlow: string;
  
  // Status colors
  online: string;
  offline: string;
  degraded: string;
  
  // Camera type colors
  cameraRBPD: string;
  cameraFDOT: string;
  cameraLPR: string;
  cameraPTZ: string;
}

export interface ThemeConfig {
  name: string;
  mode: ThemeMode;
  colors: ThemeColors;
  enableParticles: boolean;
  enableNebula: boolean;
  enableAnimations: boolean;
  mapStyle: string;
}

// Neural Cosmic Dark - PRIMARY / DEFAULT
export const neuralCosmicDark: ThemeConfig = {
  name: 'Neural Cosmic Dark',
  mode: 'neural-cosmic-dark',
  colors: {
    background: '#030308',
    backgroundSecondary: '#0a0a12',
    backgroundTertiary: '#12121f',
    
    textPrimary: '#DCE2EB',
    textSecondary: '#9CA3AF',
    textMuted: '#6B7280',
    
    neuralBlue: '#1E90FF',
    authorityGold: '#D9B252',
    quantumPink: '#FF4FB2',
    threatRed: '#FF2740',
    
    panelBackground: 'rgba(10, 10, 18, 0.85)',
    panelBorder: 'rgba(30, 144, 255, 0.3)',
    panelGlow: 'rgba(30, 144, 255, 0.15)',
    
    online: '#22C55E',
    offline: '#EF4444',
    degraded: '#F59E0B',
    
    cameraRBPD: '#1E90FF',
    cameraFDOT: '#22C55E',
    cameraLPR: '#EF4444',
    cameraPTZ: '#D9B252',
  },
  enableParticles: true,
  enableNebula: true,
  enableAnimations: true,
  mapStyle: 'mapbox://styles/mapbox/dark-v11',
};

// Cosmic Light Ops - HIGH VISIBILITY MODE
export const cosmicLightOps: ThemeConfig = {
  name: 'Cosmic Light Ops',
  mode: 'cosmic-light-ops',
  colors: {
    background: '#F5F8FB',
    backgroundSecondary: '#E6EBF2',
    backgroundTertiary: '#FFFFFF',
    
    textPrimary: '#1F2937',
    textSecondary: '#4B5563',
    textMuted: '#9CA3AF',
    
    neuralBlue: '#2563EB',
    authorityGold: '#D9B252',
    quantumPink: '#EC4899',
    threatRed: '#DC2626',
    
    panelBackground: 'rgba(255, 255, 255, 0.95)',
    panelBorder: 'rgba(217, 178, 82, 0.4)',
    panelGlow: 'rgba(217, 178, 82, 0.1)',
    
    online: '#16A34A',
    offline: '#DC2626',
    degraded: '#D97706',
    
    cameraRBPD: '#2563EB',
    cameraFDOT: '#16A34A',
    cameraLPR: '#DC2626',
    cameraPTZ: '#D9B252',
  },
  enableParticles: true,
  enableNebula: false,
  enableAnimations: true,
  mapStyle: 'mapbox://styles/mapbox/light-v11',
};

// High-Contrast Tactical - ACCESSIBILITY MODE
export const highContrastTactical: ThemeConfig = {
  name: 'High-Contrast Tactical',
  mode: 'high-contrast-tactical',
  colors: {
    background: '#000000',
    backgroundSecondary: '#0A0A0A',
    backgroundTertiary: '#141414',
    
    textPrimary: '#FFFFFF',
    textSecondary: '#E5E5E5',
    textMuted: '#A3A3A3',
    
    neuralBlue: '#00BFFF',
    authorityGold: '#FFD700',
    quantumPink: '#FF69B4',
    threatRed: '#FF0000',
    
    panelBackground: '#0A0A0A',
    panelBorder: '#00BFFF',
    panelGlow: 'transparent',
    
    online: '#00FF00',
    offline: '#FF0000',
    degraded: '#FFFF00',
    
    cameraRBPD: '#00BFFF',
    cameraFDOT: '#00FF00',
    cameraLPR: '#FF0000',
    cameraPTZ: '#FFD700',
  },
  enableParticles: false,
  enableNebula: false,
  enableAnimations: false,
  mapStyle: 'mapbox://styles/mapbox/dark-v11',
};

export const themes: Record<ThemeMode, ThemeConfig> = {
  'neural-cosmic-dark': neuralCosmicDark,
  'cosmic-light-ops': cosmicLightOps,
  'high-contrast-tactical': highContrastTactical,
};

export const getTheme = (mode: ThemeMode): ThemeConfig => themes[mode];

export const defaultTheme: ThemeMode = 'neural-cosmic-dark';

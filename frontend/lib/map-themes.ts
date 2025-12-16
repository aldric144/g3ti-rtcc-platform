/**
 * Map Themes for G3TI RTCC-UIP Platform
 * 
 * Neural Cosmic Matrix Super Theme Integration:
 * 1. Neural Cosmic Dark - Primary command center theme
 * 2. Cosmic Light Ops - High visibility mode
 * 3. High-Contrast Tactical - ADA accessibility mode
 * 
 * Legacy themes (deprecated):
 * - tactical_dark, city_ops, night_ops
 */

export type MapThemeId = 'neural_cosmic_dark' | 'cosmic_light_ops' | 'high_contrast_tactical' | 'tactical_dark' | 'city_ops' | 'night_ops';

export interface MapTheme {
  id: MapThemeId;
  name: string;
  description: string;
  mapboxStyle: string;
  markerColors: {
    rbpd: string;
    fdot: string;
    lpr: string;
    ptz: string;
    default: string;
    incident: string;
    alert: string;
  };
  uiColors: {
    background: string;
    surface: string;
    primary: string;
    secondary: string;
    accent: string;
    text: string;
    textMuted: string;
    border: string;
  };
}

/**
 * Police Tactical Dark Theme
 * Navy base, neon blue roads, red incident markers
 */
export const TACTICAL_DARK_THEME: MapTheme = {
  id: 'tactical_dark',
  name: 'Police Tactical Dark',
  description: 'Navy base with neon blue roads and red incident markers',
  mapboxStyle: 'mapbox://styles/mapbox/dark-v11',
  markerColors: {
    rbpd: '#3B82F6',      // Blue
    fdot: '#10B981',      // Green
    lpr: '#EF4444',       // Red
    ptz: '#F59E0B',       // Gold/Amber
    default: '#6B7280',   // Gray
    incident: '#DC2626',  // Red
    alert: '#F97316',     // Orange
  },
  uiColors: {
    background: '#0F172A',  // Slate 900
    surface: '#1E293B',     // Slate 800
    primary: '#3B82F6',     // Blue 500
    secondary: '#1D4ED8',   // Blue 700
    accent: '#06B6D4',      // Cyan 500
    text: '#F8FAFC',        // Slate 50
    textMuted: '#94A3B8',   // Slate 400
    border: '#334155',      // Slate 700
  },
};

/**
 * City Operations Theme
 * White base, green municipal zones, blue water
 */
export const CITY_OPS_THEME: MapTheme = {
  id: 'city_ops',
  name: 'City Operations',
  description: 'Light theme with green municipal zones and blue water',
  mapboxStyle: 'mapbox://styles/mapbox/light-v11',
  markerColors: {
    rbpd: '#2563EB',      // Blue 600
    fdot: '#059669',      // Emerald 600
    lpr: '#DC2626',       // Red 600
    ptz: '#D97706',       // Amber 600
    default: '#4B5563',   // Gray 600
    incident: '#B91C1C',  // Red 700
    alert: '#EA580C',     // Orange 600
  },
  uiColors: {
    background: '#FFFFFF',  // White
    surface: '#F8FAFC',     // Slate 50
    primary: '#2563EB',     // Blue 600
    secondary: '#1D4ED8',   // Blue 700
    accent: '#059669',      // Emerald 600
    text: '#1E293B',        // Slate 800
    textMuted: '#64748B',   // Slate 500
    border: '#E2E8F0',      // Slate 200
  },
};

/**
 * RTCC Night Ops Theme
 * Navy/black base, gold camera icons, red alerts
 */
export const NIGHT_OPS_THEME: MapTheme = {
  id: 'night_ops',
  name: 'RTCC Night Ops',
  description: 'Dark navy base with gold camera icons and red alerts',
  mapboxStyle: 'mapbox://styles/mapbox/navigation-night-v1',
  markerColors: {
    rbpd: '#60A5FA',      // Blue 400
    fdot: '#34D399',      // Emerald 400
    lpr: '#F87171',       // Red 400
    ptz: '#FBBF24',       // Amber 400
    default: '#9CA3AF',   // Gray 400
    incident: '#EF4444',  // Red 500
    alert: '#F59E0B',     // Amber 500
  },
  uiColors: {
    background: '#030712',  // Gray 950
    surface: '#111827',     // Gray 900
    primary: '#FBBF24',     // Amber 400
    secondary: '#F59E0B',   // Amber 500
    accent: '#60A5FA',      // Blue 400
    text: '#F9FAFB',        // Gray 50
    textMuted: '#9CA3AF',   // Gray 400
    border: '#1F2937',      // Gray 800
  },
};

/**
 * Neural Cosmic Dark Theme (PRIMARY / DEFAULT)
 * Deep cosmic black with nebula gradients, neural blue glow, authority gold hierarchy
 */
export const NEURAL_COSMIC_DARK_THEME: MapTheme = {
  id: 'neural_cosmic_dark',
  name: 'Neural Cosmic Dark',
  description: 'Primary command center theme with cosmic visuals',
  mapboxStyle: 'mapbox://styles/mapbox/dark-v11',
  markerColors: {
    rbpd: '#1E90FF',      // Neural Electric Blue - RBPD Blue Glow
    fdot: '#22C55E',      // FDOT Green Glow
    lpr: '#FF2740',       // Threat Red - LPR Red Glow
    ptz: '#D9B252',       // Authority Gold - PTZ Gold Glow
    default: '#9CA3AF',   // Starlight Silver
    incident: '#FF2740',  // Threat Red
    alert: '#FF4FB2',     // Quantum Pink
  },
  uiColors: {
    background: '#030308',  // Cosmic Black
    surface: '#0a0a12',     // Background Secondary
    primary: '#1E90FF',     // Neural Electric Blue
    secondary: '#D9B252',   // Authority Gold
    accent: '#FF4FB2',      // Quantum Pink
    text: '#DCE2EB',        // Starlight Silver
    textMuted: '#6B7280',   // Muted Gray
    border: 'rgba(30, 144, 255, 0.3)',  // Neural Blue Border
  },
};

/**
 * Cosmic Light Ops Theme (HIGH VISIBILITY MODE)
 * White-silver gradient with gold borders and blue accents
 */
export const COSMIC_LIGHT_OPS_THEME: MapTheme = {
  id: 'cosmic_light_ops',
  name: 'Cosmic Light Ops',
  description: 'High visibility mode for daylight operations',
  mapboxStyle: 'mapbox://styles/mapbox/light-v11',
  markerColors: {
    rbpd: '#2563EB',      // Blue 600 - RBPD
    fdot: '#16A34A',      // Green 600 - FDOT
    lpr: '#DC2626',       // Red 600 - LPR
    ptz: '#D9B252',       // Authority Gold - PTZ
    default: '#4B5563',   // Gray 600
    incident: '#DC2626',  // Red 600
    alert: '#EC4899',     // Pink 500
  },
  uiColors: {
    background: '#F5F8FB',  // Light Background
    surface: '#FFFFFF',     // White
    primary: '#2563EB',     // Blue 600
    secondary: '#D9B252',   // Authority Gold
    accent: '#EC4899',      // Pink 500
    text: '#1F2937',        // Gray 800
    textMuted: '#9CA3AF',   // Gray 400
    border: 'rgba(217, 178, 82, 0.4)',  // Gold Border
  },
};

/**
 * High-Contrast Tactical Theme (ACCESSIBILITY MODE)
 * Matte black with pure white text, neon colors, no animations
 */
export const HIGH_CONTRAST_TACTICAL_THEME: MapTheme = {
  id: 'high_contrast_tactical',
  name: 'High-Contrast Tactical',
  description: 'ADA accessibility mode with maximum contrast',
  mapboxStyle: 'mapbox://styles/mapbox/dark-v11',
  markerColors: {
    rbpd: '#00BFFF',      // Neon Blue - RBPD
    fdot: '#00FF00',      // Neon Green - FDOT
    lpr: '#FF0000',       // Neon Red - LPR
    ptz: '#FFD700',       // Gold - PTZ
    default: '#FFFFFF',   // Pure White
    incident: '#FF0000',  // Neon Red
    alert: '#FFFF00',     // Neon Yellow
  },
  uiColors: {
    background: '#000000',  // Matte Black
    surface: '#0A0A0A',     // Near Black
    primary: '#00BFFF',     // Neon Blue
    secondary: '#FFD700',   // Gold
    accent: '#FF69B4',      // Hot Pink
    text: '#FFFFFF',        // Pure White
    textMuted: '#E5E5E5',   // Light Gray
    border: '#00BFFF',      // Neon Blue Border
  },
};

/**
 * All available map themes
 */
export const MAP_THEMES: Record<MapThemeId, MapTheme> = {
  neural_cosmic_dark: NEURAL_COSMIC_DARK_THEME,
  cosmic_light_ops: COSMIC_LIGHT_OPS_THEME,
  high_contrast_tactical: HIGH_CONTRAST_TACTICAL_THEME,
  tactical_dark: TACTICAL_DARK_THEME,
  city_ops: CITY_OPS_THEME,
  night_ops: NIGHT_OPS_THEME,
};

/**
 * Default theme - Neural Cosmic Dark
 */
export const DEFAULT_THEME: MapThemeId = 'neural_cosmic_dark';

/**
 * Get theme by ID
 */
export function getMapTheme(themeId: MapThemeId): MapTheme {
  return MAP_THEMES[themeId] || MAP_THEMES[DEFAULT_THEME];
}

/**
 * Get all theme options for selector
 */
export function getThemeOptions(): Array<{ id: MapThemeId; name: string; description: string }> {
  return Object.values(MAP_THEMES).map(theme => ({
    id: theme.id,
    name: theme.name,
    description: theme.description,
  }));
}

/**
 * Get marker color for camera type and jurisdiction
 */
export function getMarkerColor(
  theme: MapTheme,
  cameraType?: string,
  jurisdiction?: string
): string {
  if (cameraType === 'lpr') return theme.markerColors.lpr;
  if (cameraType === 'ptz') return theme.markerColors.ptz;
  if (jurisdiction === 'RBPD') return theme.markerColors.rbpd;
  if (jurisdiction === 'FDOT') return theme.markerColors.fdot;
  return theme.markerColors.default;
}

/**
 * Local storage key for theme preference
 */
export const THEME_STORAGE_KEY = 'rtcc-map-theme';

/**
 * Save theme preference to local storage
 */
export function saveThemePreference(themeId: MapThemeId): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(THEME_STORAGE_KEY, themeId);
  }
}

/**
 * Load theme preference from local storage
 */
export function loadThemePreference(): MapThemeId {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    if (saved && saved in MAP_THEMES) {
      return saved as MapThemeId;
    }
  }
  return DEFAULT_THEME;
}

/**
 * Map Themes for G3TI RTCC-UIP Platform
 * 
 * Three selectable map styles:
 * 1. Police Tactical Dark Theme (Black / Blue) - tactical_dark
 * 2. City Operations Theme (White / Blue / Green) - city_ops
 * 3. RTCC Night Ops Theme (Dark Navy / Gold) - night_ops
 */

export type MapThemeId = 'tactical_dark' | 'city_ops' | 'night_ops' | 'neptune_ops' | 'neptune_dark' | 'neptune_hivis';

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
 * Neptune Ops Mode Theme
 * Neptune Blue base with aqua glow accents and gold sector boundaries
 */
export const NEPTUNE_OPS_THEME: MapTheme = {
  id: 'neptune_ops',
  name: 'Neptune Ops Mode',
  description: 'Neptune blue base with aqua glow accents and gold boundaries',
  mapboxStyle: 'mapbox://styles/mapbox/dark-v11',
  markerColors: {
    rbpd: '#4FE3FF',      // Aqua Glow
    fdot: '#3A6EA5',      // Neptune Blue
    lpr: '#FF6B6B',       // Soft Red
    ptz: '#C9A34E',       // Gold
    default: '#7A8B9A',   // Muted Blue-Gray
    incident: '#FF4757',  // Alert Red
    alert: '#FFA502',     // Warning Orange
  },
  uiColors: {
    background: '#0A1A2F',  // Neptune Deep Navy
    surface: '#122640',     // Neptune Surface
    primary: '#3A6EA5',     // Neptune Blue
    secondary: '#4FE3FF',   // Aqua Glow
    accent: '#C9A34E',      // Gold
    text: '#E8F4FF',        // Light Blue White
    textMuted: '#7A9BBF',   // Muted Neptune
    border: '#1E3A5F',      // Neptune Border
  },
};

/**
 * Neptune Deep Night Theme
 * Deep navy with subtle blue glow for night operations
 */
export const NEPTUNE_DARK_THEME: MapTheme = {
  id: 'neptune_dark',
  name: 'Neptune Deep Night',
  description: 'Deep navy with subtle blue glow for stealth night operations',
  mapboxStyle: 'mapbox://styles/mapbox/navigation-night-v1',
  markerColors: {
    rbpd: '#4FE3FF',      // Aqua Glow
    fdot: '#2D5A87',      // Darker Neptune Blue
    lpr: '#FF5252',       // Red
    ptz: '#C9A34E',       // Gold
    default: '#5A6B7A',   // Dark Blue-Gray
    incident: '#FF3D3D',  // Bright Red
    alert: '#FF9500',     // Orange
  },
  uiColors: {
    background: '#050D18',  // Ultra Deep Navy
    surface: '#0A1A2F',     // Neptune Deep Navy
    primary: '#3A6EA5',     // Neptune Blue
    secondary: '#4FE3FF',   // Aqua Glow
    accent: '#C9A34E',      // Gold
    text: '#D4E6F7',        // Soft Blue White
    textMuted: '#5A7A9A',   // Dark Muted Neptune
    border: '#152A45',      // Dark Neptune Border
  },
};

/**
 * Neptune High Visibility Theme
 * High contrast Neptune theme for maximum visibility
 */
export const NEPTUNE_HIVIS_THEME: MapTheme = {
  id: 'neptune_hivis',
  name: 'Neptune High Visibility',
  description: 'High contrast Neptune theme for maximum visibility',
  mapboxStyle: 'mapbox://styles/mapbox/streets-v12',
  markerColors: {
    rbpd: '#00D4FF',      // Bright Aqua
    fdot: '#4A90D9',      // Bright Neptune Blue
    lpr: '#FF4444',       // Bright Red
    ptz: '#FFD700',       // Bright Gold
    default: '#8899AA',   // Light Blue-Gray
    incident: '#FF0000',  // Pure Red
    alert: '#FF8C00',     // Dark Orange
  },
  uiColors: {
    background: '#0F2847',  // Medium Neptune Navy
    surface: '#1A3A5C',     // Lighter Neptune Surface
    primary: '#4A90D9',     // Bright Neptune Blue
    secondary: '#00D4FF',   // Bright Aqua
    accent: '#FFD700',      // Bright Gold
    text: '#FFFFFF',        // Pure White
    textMuted: '#A0C4E8',   // Light Neptune
    border: '#2A5A8C',      // Visible Neptune Border
  },
};

/**
 * All available map themes
 */
export const MAP_THEMES: Record<MapThemeId, MapTheme> = {
  tactical_dark: TACTICAL_DARK_THEME,
  city_ops: CITY_OPS_THEME,
  night_ops: NIGHT_OPS_THEME,
  neptune_ops: NEPTUNE_OPS_THEME,
  neptune_dark: NEPTUNE_DARK_THEME,
  neptune_hivis: NEPTUNE_HIVIS_THEME,
};

/**
 * Default theme
 */
export const DEFAULT_THEME: MapThemeId = 'tactical_dark';

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

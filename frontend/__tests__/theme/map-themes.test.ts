/**
 * G3TI Super Theme - Map Theme Integration Tests
 * 
 * Tests for:
 * - Map theme definitions
 * - Camera pin colors
 * - Theme switching for maps
 */

import {
  MAP_THEMES,
  getMapTheme,
  getMarkerColor,
  DEFAULT_THEME,
  NEURAL_COSMIC_DARK_THEME,
  COSMIC_LIGHT_OPS_THEME,
  HIGH_CONTRAST_TACTICAL_THEME,
  MapThemeId,
} from '@/lib/map-themes';

describe('Map Theme Configuration', () => {
  describe('Theme Definitions', () => {
    it('should have Neural Cosmic Matrix themes defined', () => {
      expect(MAP_THEMES['neural_cosmic_dark']).toBeDefined();
      expect(MAP_THEMES['cosmic_light_ops']).toBeDefined();
      expect(MAP_THEMES['high_contrast_tactical']).toBeDefined();
    });

    it('should have Neural Cosmic Dark as default theme', () => {
      expect(DEFAULT_THEME).toBe('neural_cosmic_dark');
    });

    it('should return correct theme for each mode', () => {
      expect(getMapTheme('neural_cosmic_dark')).toBe(NEURAL_COSMIC_DARK_THEME);
      expect(getMapTheme('cosmic_light_ops')).toBe(COSMIC_LIGHT_OPS_THEME);
      expect(getMapTheme('high_contrast_tactical')).toBe(HIGH_CONTRAST_TACTICAL_THEME);
    });
  });

  describe('Neural Cosmic Dark Map Theme', () => {
    const theme = NEURAL_COSMIC_DARK_THEME;

    it('should have correct name and id', () => {
      expect(theme.name).toBe('Neural Cosmic Dark');
      expect(theme.id).toBe('neural_cosmic_dark');
    });

    it('should use dark Mapbox style', () => {
      expect(theme.mapboxStyle).toBe('mapbox://styles/mapbox/dark-v11');
    });

    it('should have correct camera marker colors', () => {
      expect(theme.markerColors.rbpd).toBe('#1E90FF'); // Neural Electric Blue
      expect(theme.markerColors.fdot).toBe('#22C55E'); // Green
      expect(theme.markerColors.lpr).toBe('#FF2740');  // Threat Red
      expect(theme.markerColors.ptz).toBe('#D9B252');  // Authority Gold
    });

    it('should have cosmic black background', () => {
      expect(theme.uiColors.background).toBe('#030308');
    });

    it('should have Neural Electric Blue as primary', () => {
      expect(theme.uiColors.primary).toBe('#1E90FF');
    });

    it('should have Authority Gold as secondary', () => {
      expect(theme.uiColors.secondary).toBe('#D9B252');
    });
  });

  describe('Cosmic Light Ops Map Theme', () => {
    const theme = COSMIC_LIGHT_OPS_THEME;

    it('should have correct name and id', () => {
      expect(theme.name).toBe('Cosmic Light Ops');
      expect(theme.id).toBe('cosmic_light_ops');
    });

    it('should use light Mapbox style', () => {
      expect(theme.mapboxStyle).toBe('mapbox://styles/mapbox/light-v11');
    });

    it('should have light background', () => {
      expect(theme.uiColors.background).toBe('#F5F8FB');
    });

    it('should have dark text for contrast', () => {
      expect(theme.uiColors.text).toBe('#1F2937');
    });
  });

  describe('High-Contrast Tactical Map Theme', () => {
    const theme = HIGH_CONTRAST_TACTICAL_THEME;

    it('should have correct name and id', () => {
      expect(theme.name).toBe('High-Contrast Tactical');
      expect(theme.id).toBe('high_contrast_tactical');
    });

    it('should have matte black background', () => {
      expect(theme.uiColors.background).toBe('#000000');
    });

    it('should have pure white text', () => {
      expect(theme.uiColors.text).toBe('#FFFFFF');
    });

    it('should have neon camera marker colors', () => {
      expect(theme.markerColors.rbpd).toBe('#00BFFF'); // Neon Blue
      expect(theme.markerColors.fdot).toBe('#00FF00'); // Neon Green
      expect(theme.markerColors.lpr).toBe('#FF0000');  // Neon Red
      expect(theme.markerColors.ptz).toBe('#FFD700');  // Gold
    });
  });

  describe('Camera Pin Color Selection', () => {
    const theme = NEURAL_COSMIC_DARK_THEME;

    it('should return RBPD color for RBPD jurisdiction', () => {
      const color = getMarkerColor(theme, undefined, 'RBPD');
      expect(color).toBe(theme.markerColors.rbpd);
    });

    it('should return FDOT color for FDOT jurisdiction', () => {
      const color = getMarkerColor(theme, undefined, 'FDOT');
      expect(color).toBe(theme.markerColors.fdot);
    });

    it('should return LPR color for LPR camera type', () => {
      const color = getMarkerColor(theme, 'lpr', 'RBPD');
      expect(color).toBe(theme.markerColors.lpr);
    });

    it('should return PTZ color for PTZ camera type', () => {
      const color = getMarkerColor(theme, 'ptz', 'RBPD');
      expect(color).toBe(theme.markerColors.ptz);
    });

    it('should return default color when no type or jurisdiction matches', () => {
      const color = getMarkerColor(theme, 'unknown', 'unknown');
      expect(color).toBe(theme.markerColors.default);
    });

    it('should prioritize camera type over jurisdiction', () => {
      const color = getMarkerColor(theme, 'lpr', 'FDOT');
      expect(color).toBe(theme.markerColors.lpr);
    });
  });

  describe('Theme UI Colors', () => {
    const allThemes = [
      NEURAL_COSMIC_DARK_THEME,
      COSMIC_LIGHT_OPS_THEME,
      HIGH_CONTRAST_TACTICAL_THEME,
    ];

    it('all themes should have required UI color properties', () => {
      const requiredColors = [
        'background',
        'surface',
        'primary',
        'secondary',
        'accent',
        'text',
        'textMuted',
        'border',
      ];

      allThemes.forEach((theme) => {
        requiredColors.forEach((colorKey) => {
          expect(theme.uiColors).toHaveProperty(colorKey);
          expect(theme.uiColors[colorKey as keyof typeof theme.uiColors]).toBeTruthy();
        });
      });
    });

    it('all themes should have required marker color properties', () => {
      const requiredMarkers = [
        'rbpd',
        'fdot',
        'lpr',
        'ptz',
        'default',
        'incident',
        'alert',
      ];

      allThemes.forEach((theme) => {
        requiredMarkers.forEach((markerKey) => {
          expect(theme.markerColors).toHaveProperty(markerKey);
          expect(theme.markerColors[markerKey as keyof typeof theme.markerColors]).toBeTruthy();
        });
      });
    });
  });

  describe('Map Theme Switching', () => {
    it('should return correct theme for valid theme ID', () => {
      const themeIds: MapThemeId[] = [
        'neural_cosmic_dark',
        'cosmic_light_ops',
        'high_contrast_tactical',
      ];

      themeIds.forEach((id) => {
        const theme = getMapTheme(id);
        expect(theme.id).toBe(id);
      });
    });

    it('should return default theme for invalid theme ID', () => {
      const theme = getMapTheme('invalid_theme' as MapThemeId);
      expect(theme).toBe(MAP_THEMES[DEFAULT_THEME]);
    });

    it('should have unique IDs for each theme', () => {
      const ids = Object.values(MAP_THEMES).map((t) => t.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('should have unique names for each theme', () => {
      const names = Object.values(MAP_THEMES).map((t) => t.name);
      const uniqueNames = new Set(names);
      expect(uniqueNames.size).toBe(names.length);
    });
  });
});

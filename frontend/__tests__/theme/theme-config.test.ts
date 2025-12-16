/**
 * G3TI Super Theme - Theme Configuration Tests
 * 
 * Tests for:
 * - Theme rendering
 * - Mode switching
 * - Color palette validation
 * - Animation state management
 */

import {
  themes,
  getTheme,
  defaultTheme,
  neuralCosmicDark,
  cosmicLightOps,
  highContrastTactical,
  ThemeMode,
  ThemeConfig,
} from '@/lib/theme/theme-config';

describe('Theme Configuration', () => {
  describe('Theme Definitions', () => {
    it('should have three themes defined', () => {
      expect(Object.keys(themes)).toHaveLength(3);
      expect(themes['neural-cosmic-dark']).toBeDefined();
      expect(themes['cosmic-light-ops']).toBeDefined();
      expect(themes['high-contrast-tactical']).toBeDefined();
    });

    it('should have Neural Cosmic Dark as default theme', () => {
      expect(defaultTheme).toBe('neural-cosmic-dark');
    });

    it('should return correct theme for each mode', () => {
      expect(getTheme('neural-cosmic-dark')).toBe(neuralCosmicDark);
      expect(getTheme('cosmic-light-ops')).toBe(cosmicLightOps);
      expect(getTheme('high-contrast-tactical')).toBe(highContrastTactical);
    });
  });

  describe('Neural Cosmic Dark Theme', () => {
    const theme = neuralCosmicDark;

    it('should have correct name and mode', () => {
      expect(theme.name).toBe('Neural Cosmic Dark');
      expect(theme.mode).toBe('neural-cosmic-dark');
    });

    it('should have cosmic black background', () => {
      expect(theme.colors.background).toBe('#030308');
    });

    it('should have Neural Electric Blue as primary color', () => {
      expect(theme.colors.neuralBlue).toBe('#1E90FF');
    });

    it('should have Authority Gold for hierarchy', () => {
      expect(theme.colors.authorityGold).toBe('#D9B252');
    });

    it('should have Threat Red for alerts', () => {
      expect(theme.colors.threatRed).toBe('#FF2740');
    });

    it('should have Quantum Pink as AI accent', () => {
      expect(theme.colors.quantumPink).toBe('#FF4FB2');
    });

    it('should have Starlight Silver for text', () => {
      expect(theme.colors.textPrimary).toBe('#DCE2EB');
    });

    it('should enable particles and nebula', () => {
      expect(theme.enableParticles).toBe(true);
      expect(theme.enableNebula).toBe(true);
    });

    it('should enable animations', () => {
      expect(theme.enableAnimations).toBe(true);
    });

    it('should use dark Mapbox style', () => {
      expect(theme.mapStyle).toBe('mapbox://styles/mapbox/dark-v11');
    });

    it('should have correct camera type colors', () => {
      expect(theme.colors.cameraRBPD).toBe('#1E90FF'); // Blue Glow
      expect(theme.colors.cameraFDOT).toBe('#22C55E'); // Green Glow
      expect(theme.colors.cameraLPR).toBe('#EF4444');  // Red Glow
      expect(theme.colors.cameraPTZ).toBe('#D9B252');  // Gold Glow
    });
  });

  describe('Cosmic Light Ops Theme', () => {
    const theme = cosmicLightOps;

    it('should have correct name and mode', () => {
      expect(theme.name).toBe('Cosmic Light Ops');
      expect(theme.mode).toBe('cosmic-light-ops');
    });

    it('should have light background', () => {
      expect(theme.colors.background).toBe('#F5F8FB');
    });

    it('should have dark text for contrast', () => {
      expect(theme.colors.textPrimary).toBe('#1F2937');
    });

    it('should enable particles but not nebula', () => {
      expect(theme.enableParticles).toBe(true);
      expect(theme.enableNebula).toBe(false);
    });

    it('should enable animations', () => {
      expect(theme.enableAnimations).toBe(true);
    });

    it('should use light Mapbox style', () => {
      expect(theme.mapStyle).toBe('mapbox://styles/mapbox/light-v11');
    });

    it('should have gold panel border', () => {
      expect(theme.colors.panelBorder).toContain('217, 178, 82');
    });
  });

  describe('High-Contrast Tactical Theme', () => {
    const theme = highContrastTactical;

    it('should have correct name and mode', () => {
      expect(theme.name).toBe('High-Contrast Tactical');
      expect(theme.mode).toBe('high-contrast-tactical');
    });

    it('should have matte black background', () => {
      expect(theme.colors.background).toBe('#000000');
    });

    it('should have pure white text', () => {
      expect(theme.colors.textPrimary).toBe('#FFFFFF');
    });

    it('should have neon blue as primary', () => {
      expect(theme.colors.neuralBlue).toBe('#00BFFF');
    });

    it('should have neon red for threats', () => {
      expect(theme.colors.threatRed).toBe('#FF0000');
    });

    it('should disable particles and nebula for accessibility', () => {
      expect(theme.enableParticles).toBe(false);
      expect(theme.enableNebula).toBe(false);
    });

    it('should disable animations for accessibility', () => {
      expect(theme.enableAnimations).toBe(false);
    });

    it('should have high contrast camera colors', () => {
      expect(theme.colors.cameraRBPD).toBe('#00BFFF'); // Neon Blue
      expect(theme.colors.cameraFDOT).toBe('#00FF00'); // Neon Green
      expect(theme.colors.cameraLPR).toBe('#FF0000');  // Neon Red
      expect(theme.colors.cameraPTZ).toBe('#FFD700');  // Gold
    });
  });

  describe('Theme Color Validation', () => {
    const allThemes = [neuralCosmicDark, cosmicLightOps, highContrastTactical];

    it('all themes should have required color properties', () => {
      const requiredColors = [
        'background',
        'backgroundSecondary',
        'backgroundTertiary',
        'textPrimary',
        'textSecondary',
        'textMuted',
        'neuralBlue',
        'authorityGold',
        'quantumPink',
        'threatRed',
        'panelBackground',
        'panelBorder',
        'panelGlow',
        'online',
        'offline',
        'degraded',
        'cameraRBPD',
        'cameraFDOT',
        'cameraLPR',
        'cameraPTZ',
      ];

      allThemes.forEach((theme) => {
        requiredColors.forEach((colorKey) => {
          expect(theme.colors).toHaveProperty(colorKey);
          expect(theme.colors[colorKey as keyof typeof theme.colors]).toBeTruthy();
        });
      });
    });

    it('all themes should have valid hex colors for primary colors', () => {
      const hexColorRegex = /^#[0-9A-Fa-f]{6}$/;
      const rgbaColorRegex = /^rgba?\(/;

      allThemes.forEach((theme) => {
        // Background colors should be hex
        expect(theme.colors.background).toMatch(hexColorRegex);
        expect(theme.colors.backgroundSecondary).toMatch(hexColorRegex);
        
        // Text colors should be hex
        expect(theme.colors.textPrimary).toMatch(hexColorRegex);
        
        // Brand colors should be hex
        expect(theme.colors.neuralBlue).toMatch(hexColorRegex);
        expect(theme.colors.authorityGold).toMatch(hexColorRegex);
        expect(theme.colors.threatRed).toMatch(hexColorRegex);
        
        // Panel colors can be rgba
        expect(
          theme.colors.panelBackground.match(hexColorRegex) ||
          theme.colors.panelBackground.match(rgbaColorRegex)
        ).toBeTruthy();
      });
    });
  });

  describe('Theme Mode Switching', () => {
    it('should return correct theme for valid mode', () => {
      const modes: ThemeMode[] = ['neural-cosmic-dark', 'cosmic-light-ops', 'high-contrast-tactical'];
      
      modes.forEach((mode) => {
        const theme = getTheme(mode);
        expect(theme.mode).toBe(mode);
      });
    });

    it('should have unique names for each theme', () => {
      const names = Object.values(themes).map((t) => t.name);
      const uniqueNames = new Set(names);
      expect(uniqueNames.size).toBe(names.length);
    });

    it('should have unique modes for each theme', () => {
      const modes = Object.values(themes).map((t) => t.mode);
      const uniqueModes = new Set(modes);
      expect(uniqueModes.size).toBe(modes.length);
    });
  });

  describe('Animation State Management', () => {
    it('Neural Cosmic Dark should have all animations enabled', () => {
      expect(neuralCosmicDark.enableAnimations).toBe(true);
      expect(neuralCosmicDark.enableParticles).toBe(true);
      expect(neuralCosmicDark.enableNebula).toBe(true);
    });

    it('Cosmic Light Ops should have animations but no nebula', () => {
      expect(cosmicLightOps.enableAnimations).toBe(true);
      expect(cosmicLightOps.enableParticles).toBe(true);
      expect(cosmicLightOps.enableNebula).toBe(false);
    });

    it('High-Contrast Tactical should have all animations disabled', () => {
      expect(highContrastTactical.enableAnimations).toBe(false);
      expect(highContrastTactical.enableParticles).toBe(false);
      expect(highContrastTactical.enableNebula).toBe(false);
    });
  });
});

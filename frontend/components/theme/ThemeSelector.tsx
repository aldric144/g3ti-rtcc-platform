'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useTheme } from '@/lib/theme';
import { ThemeMode } from '@/lib/theme/theme-config';

const themeOptions: { mode: ThemeMode; label: string; description: string }[] = [
  {
    mode: 'neural-cosmic-dark',
    label: 'Neural Cosmic Dark',
    description: 'Primary command center theme',
  },
  {
    mode: 'cosmic-light-ops',
    label: 'Cosmic Light Ops',
    description: 'High visibility mode',
  },
  {
    mode: 'high-contrast-tactical',
    label: 'Tactical',
    description: 'ADA accessibility mode',
  },
];

export function ThemeSelector() {
  const { themeMode, setThemeMode, theme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentOption = themeOptions.find((opt) => opt.mode === themeMode);

  return (
    <div ref={dropdownRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-lg px-3 py-2 transition-all duration-300 hover:scale-105"
        style={{
          background: theme.colors.panelBackground,
          border: `1px solid ${theme.colors.panelBorder}`,
          boxShadow: `0 0 10px ${theme.colors.panelGlow}`,
        }}
        aria-label="Theme selector"
        aria-expanded={isOpen}
      >
        <span className="text-xl" role="img" aria-label="crystal ball">
          🔮
        </span>
        <span
          className="hidden text-sm font-medium sm:inline"
          style={{ color: theme.colors.textPrimary }}
        >
          {currentOption?.label || 'Theme'}
        </span>
        <svg
          className={`h-4 w-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke={theme.colors.textSecondary}
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div
          className="absolute right-0 top-full z-50 mt-2 w-64 overflow-hidden rounded-lg shadow-xl"
          style={{
            background: theme.colors.panelBackground,
            border: `1px solid ${theme.colors.panelBorder}`,
            boxShadow: `0 4px 20px ${theme.colors.panelGlow}, 0 0 40px ${theme.colors.panelGlow}`,
          }}
        >
          <div
            className="border-b px-4 py-3"
            style={{ borderColor: theme.colors.panelBorder }}
          >
            <h3
              className="text-sm font-semibold"
              style={{ color: theme.colors.authorityGold }}
            >
              Select Theme Mode
            </h3>
          </div>
          <div className="p-2">
            {themeOptions.map((option) => (
              <button
                key={option.mode}
                onClick={() => {
                  setThemeMode(option.mode);
                  setIsOpen(false);
                }}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left transition-all duration-200"
                style={{
                  background:
                    themeMode === option.mode
                      ? `${theme.colors.neuralBlue}20`
                      : 'transparent',
                  borderLeft:
                    themeMode === option.mode
                      ? `3px solid ${theme.colors.neuralBlue}`
                      : '3px solid transparent',
                }}
              >
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-full"
                  style={{
                    background:
                      option.mode === 'neural-cosmic-dark'
                        ? 'linear-gradient(135deg, #030308, #1E90FF)'
                        : option.mode === 'cosmic-light-ops'
                          ? 'linear-gradient(135deg, #F5F8FB, #D9B252)'
                          : 'linear-gradient(135deg, #000000, #00BFFF)',
                    border: `2px solid ${theme.colors.authorityGold}`,
                  }}
                >
                  {option.mode === 'neural-cosmic-dark' && (
                    <span className="text-xs">🌌</span>
                  )}
                  {option.mode === 'cosmic-light-ops' && (
                    <span className="text-xs">☀️</span>
                  )}
                  {option.mode === 'high-contrast-tactical' && (
                    <span className="text-xs">🎯</span>
                  )}
                </div>
                <div className="flex-1">
                  <div
                    className="text-sm font-medium"
                    style={{ color: theme.colors.textPrimary }}
                  >
                    {option.label}
                  </div>
                  <div
                    className="text-xs"
                    style={{ color: theme.colors.textMuted }}
                  >
                    {option.description}
                  </div>
                </div>
                {themeMode === option.mode && (
                  <svg
                    className="h-5 w-5"
                    fill={theme.colors.neuralBlue}
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ThemeSelector;

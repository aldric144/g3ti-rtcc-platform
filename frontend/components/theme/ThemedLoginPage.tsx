'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { Eye, EyeOff, AlertCircle, Shield, Zap, Activity, Lock } from 'lucide-react';
import { useTheme } from '@/lib/theme';

interface ThemedLoginPageProps {
  onSubmit: (username: string, password: string) => Promise<boolean>;
  isLoading?: boolean;
  error?: string | null;
}

export function ThemedLoginPage({ onSubmit, isLoading = false, error }: ThemedLoginPageProps) {
  const { theme } = useTheme();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(username, password);
  };

  return (
    <div
      className="g3ti-login-container relative min-h-screen flex items-center justify-center overflow-hidden"
      style={{
        background: `radial-gradient(ellipse at center, ${theme.colors.backgroundSecondary} 0%, ${theme.colors.background} 100%)`,
      }}
    >
      {/* Animated nebula background */}
      {theme.enableNebula && (
        <>
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              background: `radial-gradient(circle at 20% 30%, ${theme.colors.neuralBlue}10 0%, transparent 50%),
                          radial-gradient(circle at 80% 70%, ${theme.colors.authorityGold}08 0%, transparent 50%)`,
            }}
          />
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              background: `radial-gradient(circle at 60% 20%, ${theme.colors.quantumPink}05 0%, transparent 40%)`,
              animation: theme.enableAnimations ? 'pulse 8s ease-in-out infinite' : 'none',
            }}
          />
        </>
      )}

      {/* Grid overlay for tactical feel */}
      <div
        className="absolute inset-0 pointer-events-none opacity-5"
        style={{
          backgroundImage: `linear-gradient(${theme.colors.neuralBlue}20 1px, transparent 1px),
                           linear-gradient(90deg, ${theme.colors.neuralBlue}20 1px, transparent 1px)`,
          backgroundSize: '50px 50px',
        }}
      />

      {/* Main login card */}
      <div className="relative z-10 w-full max-w-lg mx-4">
        <div
          className="g3ti-login-card rounded-2xl p-8 md:p-12"
          style={{
            background: theme.colors.panelBackground,
            border: `1px solid ${theme.colors.authorityGold}`,
            boxShadow: `0 0 40px ${theme.colors.authorityGold}20, 0 0 80px ${theme.colors.neuralBlue}10`,
            backdropFilter: 'blur(20px)',
          }}
        >
          {/* Logo and branding */}
          <div className="flex flex-col items-center mb-8">
            <div
              className="relative p-4 rounded-full mb-4"
              style={{
                background: `linear-gradient(135deg, ${theme.colors.background} 0%, ${theme.colors.backgroundSecondary} 100%)`,
                border: `2px solid ${theme.colors.authorityGold}`,
                boxShadow: `0 0 30px ${theme.colors.authorityGold}30`,
              }}
            >
              <Image
                src="/assets/rbpd/rbpd_logo_128.png"
                alt="RBPD Badge"
                width={96}
                height={96}
                priority
              />
              {/* Pulsing ring effect */}
              {theme.enableAnimations && (
                <div
                  className="absolute inset-0 rounded-full"
                  style={{
                    border: `2px solid ${theme.colors.neuralBlue}`,
                    animation: 'cosmicPulse 3s infinite',
                  }}
                />
              )}
            </div>

            <h1
              className="text-xl font-bold text-center"
              style={{ color: theme.colors.authorityGold }}
            >
              RIVIERA BEACH POLICE DEPARTMENT
            </h1>
            <p
              className="text-sm mt-1"
              style={{ color: theme.colors.textSecondary }}
            >
              Real Time Crime Center - Unified Intelligence Platform
            </p>

            {/* Status indicators */}
            <div className="flex items-center gap-4 mt-4">
              <div className="flex items-center gap-2">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{
                    background: theme.colors.online,
                    boxShadow: `0 0 8px ${theme.colors.online}`,
                  }}
                />
                <span className="text-xs" style={{ color: theme.colors.textMuted }}>
                  SYSTEM ONLINE
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Lock className="w-3 h-3" style={{ color: theme.colors.neuralBlue }} />
                <span className="text-xs" style={{ color: theme.colors.textMuted }}>
                  CJIS SECURED
                </span>
              </div>
            </div>
          </div>

          {/* Login form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error message */}
            {error && (
              <div
                className="flex items-center gap-2 rounded-lg p-4"
                style={{
                  background: `${theme.colors.threatRed}15`,
                  border: `1px solid ${theme.colors.threatRed}40`,
                }}
              >
                <AlertCircle className="h-5 w-5 flex-shrink-0" style={{ color: theme.colors.threatRed }} />
                <p className="text-sm" style={{ color: theme.colors.threatRed }}>
                  {error}
                </p>
              </div>
            )}

            {/* Username field */}
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium mb-2"
                style={{ color: theme.colors.textSecondary }}
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-lg outline-none transition-all"
                style={{
                  background: theme.colors.background,
                  border: `1px solid ${theme.colors.panelBorder}`,
                  color: theme.colors.textPrimary,
                }}
                placeholder="Enter your username"
                required
                autoComplete="username"
              />
            </div>

            {/* Password field */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium mb-2"
                style={{ color: theme.colors.textSecondary }}
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 pr-12 rounded-lg outline-none transition-all"
                  style={{
                    background: theme.colors.background,
                    border: `1px solid ${theme.colors.panelBorder}`,
                    color: theme.colors.textPrimary,
                  }}
                  placeholder="Enter your password"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1"
                  style={{ color: theme.colors.textMuted }}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 rounded-lg font-semibold transition-all"
              style={{
                background: `linear-gradient(135deg, ${theme.colors.neuralBlue} 0%, ${theme.colors.neuralBlue}CC 100%)`,
                color: '#FFFFFF',
                border: `1px solid ${theme.colors.neuralBlue}`,
                boxShadow: `0 0 20px ${theme.colors.neuralBlue}40`,
                opacity: isLoading ? 0.7 : 1,
              }}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <div
                    className="h-4 w-4 rounded-full border-2 border-white border-t-transparent"
                    style={{ animation: 'spin 1s linear infinite' }}
                  />
                  Authenticating...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Shield className="h-5 w-5" />
                  Secure Login
                </span>
              )}
            </button>
          </form>

          {/* CJIS compliance notice */}
          <div
            className="mt-8 rounded-lg p-4"
            style={{
              background: `${theme.colors.authorityGold}10`,
              border: `1px solid ${theme.colors.authorityGold}30`,
            }}
          >
            <p
              className="text-center text-xs"
              style={{ color: theme.colors.textMuted }}
            >
              This system contains Criminal Justice Information (CJI) and is subject to CJIS
              Security Policy requirements. Unauthorized access is prohibited and may result in
              criminal prosecution.
            </p>
          </div>

          {/* Feature indicators */}
          <div className="flex justify-center gap-6 mt-6">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4" style={{ color: theme.colors.neuralBlue }} />
              <span className="text-xs" style={{ color: theme.colors.textMuted }}>
                AI-Powered
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4" style={{ color: theme.colors.online }} />
              <span className="text-xs" style={{ color: theme.colors.textMuted }}>
                Real-Time
              </span>
            </div>
          </div>
        </div>

        {/* Version info */}
        <p
          className="text-center text-xs mt-4"
          style={{ color: theme.colors.textMuted }}
        >
          G3TI RTCC-UIP v2.0 | Neural Cosmic Matrix Theme
        </p>
      </div>

      {/* Keyframe animations */}
      <style jsx>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}

export default ThemedLoginPage;

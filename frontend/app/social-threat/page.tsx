'use client';

import { useTheme } from '@/lib/theme';
import { MessageSquare, AlertTriangle, TrendingUp, Eye, Shield } from 'lucide-react';

export default function SocialThreatAIPage() {
  const { theme } = useTheme();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: theme.colors.textPrimary }}>
            Social Threat AI
          </h1>
          <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
            AI-powered social media threat monitoring and analysis
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Active Monitors', value: '156', icon: Eye, color: theme.colors.neuralBlue },
          { label: 'Threats Detected', value: '8', icon: AlertTriangle, color: theme.colors.threatRed },
          { label: 'Trend Alerts', value: '23', icon: TrendingUp, color: theme.colors.authorityGold },
          { label: 'Mitigated', value: '12', icon: Shield, color: theme.colors.online },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-lg p-4"
            style={{
              background: theme.colors.panelBackground,
              border: `1px solid ${theme.colors.panelBorder}`,
            }}
          >
            <div className="flex items-center gap-3">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-full"
                style={{ background: `${stat.color}20` }}
              >
                <stat.icon className="h-5 w-5" style={{ color: stat.color }} />
              </div>
              <div>
                <p className="text-2xl font-bold" style={{ color: theme.colors.textPrimary }}>
                  {stat.value}
                </p>
                <p className="text-xs" style={{ color: theme.colors.textSecondary }}>
                  {stat.label}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div
        className="rounded-lg p-6"
        style={{
          background: theme.colors.panelBackground,
          border: `1px solid ${theme.colors.panelBorder}`,
        }}
      >
        <h2 className="mb-4 text-lg font-semibold" style={{ color: theme.colors.textPrimary }}>
          Threat Intelligence Feed
        </h2>
        <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
          Social threat intelligence data will appear here once connected to the HARPLIB backend.
        </p>
      </div>
    </div>
  );
}

'use client';

import { useTheme } from '@/lib/theme';
import { TrendingUp, BarChart3, Calendar, ArrowUp, ArrowDown } from 'lucide-react';

export default function CrimeTrendsPage() {
  const { theme } = useTheme();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: theme.colors.textPrimary }}>
            Crime Trends
          </h1>
          <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
            Historical crime trend analysis and patterns
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total Incidents', value: '1,247', change: '+12%', up: true, icon: BarChart3 },
          { label: 'Violent Crime', value: '89', change: '-8%', up: false, icon: TrendingUp },
          { label: 'Property Crime', value: '456', change: '+5%', up: true, icon: TrendingUp },
          { label: 'Avg Daily', value: '42', change: '-3%', up: false, icon: Calendar },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-lg p-4"
            style={{
              background: theme.colors.panelBackground,
              border: `1px solid ${theme.colors.panelBorder}`,
            }}
          >
            <div className="flex items-center justify-between">
              <stat.icon className="h-5 w-5" style={{ color: theme.colors.authorityGold }} />
              <span
                className="flex items-center text-xs"
                style={{ color: stat.up ? theme.colors.threatRed : theme.colors.online }}
              >
                {stat.up ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                {stat.change}
              </span>
            </div>
            <p className="mt-2 text-2xl font-bold" style={{ color: theme.colors.textPrimary }}>
              {stat.value}
            </p>
            <p className="text-xs" style={{ color: theme.colors.textSecondary }}>
              {stat.label}
            </p>
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
          Trend Analysis
        </h2>
        <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
          Crime trend charts will appear here once connected to the HARPLIB backend.
        </p>
      </div>
    </div>
  );
}

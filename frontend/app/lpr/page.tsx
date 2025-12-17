'use client';

import { useTheme } from '@/lib/theme';
import { Car, AlertTriangle, Search, Clock, MapPin } from 'lucide-react';

export default function LPRIntelligencePage() {
  const { theme } = useTheme();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: theme.colors.textPrimary }}>
            LPR Intelligence
          </h1>
          <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
            License Plate Recognition monitoring and alerts
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Active Readers', value: '24', icon: Car, color: theme.colors.neuralBlue },
          { label: 'Hits Today', value: '47', icon: AlertTriangle, color: theme.colors.threatRed },
          { label: 'Plates Scanned', value: '12,847', icon: Search, color: theme.colors.authorityGold },
          { label: 'Avg Response', value: '2.3s', icon: Clock, color: theme.colors.online },
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
          Recent LPR Hits
        </h2>
        <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
          LPR hit data will appear here once connected to the HARPLIB backend.
        </p>
      </div>
    </div>
  );
}

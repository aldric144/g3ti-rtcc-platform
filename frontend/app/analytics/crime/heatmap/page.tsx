'use client';

import { useTheme } from '@/lib/theme';
import { Flame, MapPin, Calendar, Filter } from 'lucide-react';

export default function CrimeHeatmapPage() {
  const { theme } = useTheme();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: theme.colors.textPrimary }}>
            Crime Heatmap
          </h1>
          <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
            Geographic visualization of crime density and patterns
          </p>
        </div>
      </div>

      <div
        className="rounded-lg p-6"
        style={{
          background: theme.colors.panelBackground,
          border: `1px solid ${theme.colors.panelBorder}`,
          minHeight: '400px',
        }}
      >
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <Flame className="mx-auto h-12 w-12 mb-4" style={{ color: theme.colors.authorityGold }} />
            <h2 className="text-lg font-semibold mb-2" style={{ color: theme.colors.textPrimary }}>
              Crime Heatmap Visualization
            </h2>
            <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
              Heatmap data will appear here once connected to the HARPLIB backend.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

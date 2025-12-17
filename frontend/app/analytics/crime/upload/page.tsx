'use client';

import { useTheme } from '@/lib/theme';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

export default function CrimeDataUploadPage() {
  const { theme } = useTheme();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: theme.colors.textPrimary }}>
            Upload Crime Data
          </h1>
          <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
            Import crime data from external sources
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Files Uploaded', value: '847', icon: FileText, color: theme.colors.neuralBlue },
          { label: 'Records Imported', value: '12.4K', icon: Upload, color: theme.colors.authorityGold },
          { label: 'Successful', value: '98%', icon: CheckCircle, color: theme.colors.online },
          { label: 'Errors', value: '23', icon: AlertCircle, color: theme.colors.threatRed },
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
          Upload Data
        </h2>
        <div
          className="border-2 border-dashed rounded-lg p-8 text-center"
          style={{ borderColor: theme.colors.panelBorder }}
        >
          <Upload className="mx-auto h-12 w-12 mb-4" style={{ color: theme.colors.authorityGold }} />
          <p className="text-sm mb-2" style={{ color: theme.colors.textPrimary }}>
            Drag and drop files here, or click to browse
          </p>
          <p className="text-xs" style={{ color: theme.colors.textSecondary }}>
            Supports CSV, Excel, and JSON formats
          </p>
        </div>
      </div>
    </div>
  );
}

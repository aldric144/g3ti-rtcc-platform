'use client';

import React, { ReactNode } from 'react';
import { useTheme } from '@/lib/theme';
import { ThemedSidebar } from './ThemedSidebar';

interface ThemedPageWrapperProps {
  children: ReactNode;
  showSidebar?: boolean;
  className?: string;
}

export function ThemedPageWrapper({
  children,
  showSidebar = true,
  className = '',
}: ThemedPageWrapperProps) {
  const { theme } = useTheme();

  return (
    <div
      className="flex min-h-screen"
      style={{
        background: theme.colors.background,
        color: theme.colors.textPrimary,
      }}
    >
      {showSidebar && <ThemedSidebar />}
      <main
        className={`flex-1 overflow-auto ${className}`}
        style={{
          background: theme.colors.background,
        }}
      >
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}

export default ThemedPageWrapper;

'use client';

import React, { useState, ReactNode } from 'react';
import TopNavBar from './TopNavBar';
import LeftSidebar from './LeftSidebar';

interface MasterLayoutProps {
  children: ReactNode;
  currentPath: string;
}

export default function MasterLayout({ children, currentPath }: MasterLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [alertCount] = useState(5);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        backgroundColor: '#0a1628',
      }}
    >
      <TopNavBar
        onMenuToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        alertCount={alertCount}
        operatorName="Operator"
        operatorStatus="online"
      />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <LeftSidebar isCollapsed={sidebarCollapsed} currentPath={currentPath} />

        <main
          style={{
            flex: 1,
            overflow: 'auto',
            padding: '24px',
            backgroundColor: '#0a1628',
          }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}

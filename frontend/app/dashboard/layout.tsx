'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import { EnterpriseSidebar } from '@/app/components/layout/EnterpriseSidebar';
import { Header } from '@/app/components/layout/Header';

/**
 * Dashboard layout with sidebar navigation and header.
 *
 * Provides:
 * - Authentication protection
 * - Responsive sidebar
 * - Global header with user info
 * - Main content area
 */
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-rtcc-dark">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-rtcc-accent border-t-transparent" />
          <p className="text-white/70">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen bg-[#0a0f24]">
      <EnterpriseSidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto bg-[#0d1526] p-6">{children}</main>
      </div>
    </div>
  );
}

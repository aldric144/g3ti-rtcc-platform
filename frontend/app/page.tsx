'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';

/**
 * Root page - redirects to dashboard or login based on auth state.
 */
export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.replace('/dashboard');
      } else {
        router.replace('/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while checking auth
  return (
    <div className="flex min-h-screen items-center justify-center bg-rtcc-dark">
      <div className="text-center">
        <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-rtcc-accent border-t-transparent" />
        <p className="text-white/70">Loading...</p>
      </div>
    </div>
  );
}

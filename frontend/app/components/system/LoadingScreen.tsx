'use client';

import Image from 'next/image';

/**
 * Loading screen component with RBPD branding.
 * Displays the RBPD badge and loading message during app initialization.
 */
export function LoadingScreen() {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-rtcc-dark">
      <Image
        src="/assets/rbpd/rbpd_logo_128.png"
        alt="Riviera Beach Police Department Badge"
        width={128}
        height={128}
        priority
      />
      <div className="mt-6 flex items-center gap-3">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
        <p className="text-lg text-white">Loading RTCC Unified Intelligence Platform...</p>
      </div>
      <p className="mt-4 text-sm text-white/60">Riviera Beach Police Department</p>
    </div>
  );
}

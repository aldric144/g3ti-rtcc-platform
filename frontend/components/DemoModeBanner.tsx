'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface DemoModeBannerProps {
  message?: string;
  dismissible?: boolean;
}

/**
 * Demo Mode Banner Component.
 * 
 * Displays a banner at the top of the page when the application
 * is running in demo mode with simulated data.
 */
export function DemoModeBanner({
  message = 'RTCC is running in Demo Mode — Some data is simulated.',
  dismissible = true,
}: DemoModeBannerProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if demo mode is active
    const checkDemoMode = () => {
      if (typeof window === 'undefined') return false;
      
      const demoFlag = localStorage.getItem('rtcc-demo-mode');
      const backendStatus = localStorage.getItem('rtcc-backend-status');
      
      return demoFlag === 'true' || backendStatus === 'unavailable';
    };

    // Check if banner was previously dismissed in this session
    const wasDismissed = sessionStorage.getItem('rtcc-demo-banner-dismissed') === 'true';
    
    if (!wasDismissed && checkDemoMode()) {
      setIsVisible(true);
    }

    // Also check periodically in case demo mode is triggered later
    const interval = setInterval(() => {
      if (!isDismissed && checkDemoMode()) {
        setIsVisible(true);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [isDismissed]);

  const handleDismiss = () => {
    setIsDismissed(true);
    setIsVisible(false);
    sessionStorage.setItem('rtcc-demo-banner-dismissed', 'true');
  };

  if (!isVisible) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-black px-4 py-2 shadow-md">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          <span className="font-medium text-sm">{message}</span>
        </div>
        {dismissible && (
          <button
            onClick={handleDismiss}
            className="p-1 hover:bg-amber-600 rounded transition-colors"
            aria-label="Dismiss banner"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}

export default DemoModeBanner;

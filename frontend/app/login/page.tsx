'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuthStore } from '@/lib/store/auth';

/**
 * Login page for the RTCC-UIP platform.
 * 
 * Provides secure authentication with:
 * - Username/password login
 * - MFA support (placeholder)
 * - Error handling
 * - CJIS compliance notice
 */
export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuthStore();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    const success = await login(username, password);
    if (success) {
      router.push('/dashboard');
    }
  };

  return (
    <div className="flex min-h-screen bg-gradient-rtcc">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-center px-12">
        <div className="max-w-md">
          <div className="flex items-center gap-3 mb-8">
            <Shield className="h-12 w-12 text-rtcc-accent" />
            <div>
              <h1 className="text-3xl font-bold text-white">G3TI RTCC-UIP</h1>
              <p className="text-white/70">Real Time Crime Center</p>
            </div>
          </div>
          
          <h2 className="text-4xl font-bold text-white mb-4">
            Unified Intelligence Platform
          </h2>
          
          <p className="text-lg text-white/80 mb-8">
            Comprehensive situational awareness and investigative intelligence
            for law enforcement operations.
          </p>
          
          <div className="space-y-4 text-white/70">
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-rtcc-accent" />
              <span>Real-time event monitoring</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-rtcc-accent" />
              <span>Multi-source intelligence fusion</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-rtcc-accent" />
              <span>Advanced investigative search</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-rtcc-accent" />
              <span>CJIS-compliant security</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Right side - Login form */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="rounded-2xl bg-white p-8 shadow-2xl">
            {/* Mobile logo */}
            <div className="lg:hidden flex items-center justify-center gap-2 mb-8">
              <Shield className="h-8 w-8 text-rtcc-primary" />
              <span className="text-xl font-bold text-rtcc-primary">G3TI RTCC-UIP</span>
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Sign in to your account
            </h2>
            <p className="text-gray-600 mb-8">
              Enter your credentials to access the platform
            </p>
            
            {/* Error message */}
            {error && (
              <div className="mb-6 flex items-center gap-2 rounded-lg bg-red-50 p-4 text-red-700">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="input"
                  placeholder="Enter your username"
                  required
                  autoComplete="username"
                />
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input pr-10"
                    placeholder="Enter your password"
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>
              
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full py-3"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Signing in...
                  </span>
                ) : (
                  'Sign in'
                )}
              </button>
            </form>
            
            {/* CJIS notice */}
            <div className="mt-8 rounded-lg bg-gray-50 p-4">
              <p className="text-xs text-gray-500 text-center">
                This system contains Criminal Justice Information (CJI) and is
                subject to CJIS Security Policy requirements. Unauthorized access
                is prohibited and may result in criminal prosecution.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Bell, Search, User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuthStore } from '@/lib/store/auth';
import { useEventStore } from '@/lib/store/events';
import { ThemeSelector } from '@/components/theme/ThemeSelector';

/**
 * Header component with search, notifications, and user menu.
 */
export function Header() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { unreadCount } = useEventStore();

  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6 dark:border-gray-700 dark:bg-gray-800">
      {/* RBPD Branding + Search */}
      <div className="flex items-center gap-4">
        {/* Mini badge and title */}
        <div className="flex items-center gap-2">
          <Image
            src="/assets/rbpd/rbpd_logo_32.png"
            alt="RBPD Badge"
            width={32}
            height={32}
          />
          <span className="hidden text-sm font-semibold text-gray-900 dark:text-white sm:block">
            Riviera Beach RTCC
          </span>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Quick search..."
            className="w-64 rounded-lg border border-gray-200 bg-gray-50 py-2 pl-10 pr-4 text-sm focus:border-rtcc-accent focus:outline-none focus:ring-1 focus:ring-rtcc-accent dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 rounded bg-gray-200 px-1.5 py-0.5 text-xs text-gray-500 dark:bg-gray-600 dark:text-gray-400">
            /
          </kbd>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Theme Selector - Neural Cosmic Matrix */}
        <ThemeSelector />

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
          >
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* Notifications dropdown */}
          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-80 rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
              <div className="border-b p-4 dark:border-gray-700">
                <h3 className="font-semibold text-gray-900 dark:text-white">Notifications</h3>
              </div>
              <div className="max-h-96 overflow-y-auto p-2">
                <p className="p-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  No new notifications
                </p>
              </div>
            </div>
          )}
        </div>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-rtcc-primary text-white">
              <User className="h-4 w-4" />
            </div>
            <div className="hidden text-left sm:block">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {user?.firstName} {user?.lastName}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{user?.role}</p>
            </div>
            <ChevronDown className="h-4 w-4 text-gray-500" />
          </button>

          {/* User dropdown */}
          {showUserMenu && (
            <div className="absolute right-0 top-full mt-2 w-48 rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
              <div className="p-2">
                <button
                  onClick={() => router.push('/settings')}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </button>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

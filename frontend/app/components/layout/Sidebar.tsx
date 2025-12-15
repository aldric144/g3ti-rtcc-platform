'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Map,
  Search,
  FileText,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
  Activity,
  Database,
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAuthStore } from '@/lib/store/auth';

/**
 * Navigation items for the sidebar.
 */
const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/map', label: 'Live Map', icon: Map },
  { href: '/investigations', label: 'Investigations', icon: Search },
  { href: '/entities', label: 'Entities', icon: Database },
  { href: '/events', label: 'Events', icon: Activity },
];

const adminItems = [
  { href: '/admin/users', label: 'User Management', icon: Users },
  { href: '/settings', label: 'Settings', icon: Settings },
];

/**
 * Sidebar navigation component.
 *
 * Features:
 * - Collapsible sidebar
 * - Role-based menu items
 * - Active state highlighting
 * - Responsive design
 */
export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const isAdmin = user?.role === 'admin' || user?.role === 'supervisor';

  return (
    <aside
      className={clsx(
        'flex flex-col bg-rtcc-dark transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo - RBPD Badge */}
      <div className="flex h-20 items-center justify-center border-b border-white/10 px-2">
        {!collapsed ? (
          <div className="flex items-center gap-2">
            <Image
              src="/assets/rbpd/rbpd_logo_64.png"
              alt="RBPD Badge"
              width={64}
              height={64}
            />
            <div className="flex flex-col">
              <span className="text-sm font-bold text-white">RBPD</span>
              <span className="text-xs text-white/70">RTCC-UIP</span>
            </div>
          </div>
        ) : (
          <Image
            src="/assets/rbpd/rbpd_logo_48.png"
            alt="RBPD Badge"
            width={48}
            height={48}
          />
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={clsx(
                    'flex items-center gap-3 rounded-lg px-3 py-2 transition-colors',
                    isActive
                      ? 'bg-rtcc-accent text-white'
                      : 'text-white/70 hover:bg-white/10 hover:text-white'
                  )}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* Admin section */}
        {isAdmin && (
          <>
            <div className="my-4 border-t border-white/10" />
            <ul className="space-y-1 px-2">
              {!collapsed && (
                <li className="px-3 py-2 text-xs font-semibold uppercase text-white/50">
                  Administration
                </li>
              )}
              {adminItems.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;

                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={clsx(
                        'flex items-center gap-3 rounded-lg px-3 py-2 transition-colors',
                        isActive
                          ? 'bg-rtcc-accent text-white'
                          : 'text-white/70 hover:bg-white/10 hover:text-white'
                      )}
                    >
                      <Icon className="h-5 w-5 flex-shrink-0" />
                      {!collapsed && <span>{item.label}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </>
        )}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t border-white/10 p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex w-full items-center justify-center rounded-lg p-2 text-white/70 hover:bg-white/10 hover:text-white"
        >
          {collapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
        </button>
      </div>
    </aside>
  );
}

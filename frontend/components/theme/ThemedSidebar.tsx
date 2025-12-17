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
  Camera,
  Plane,
  Dog,
  Car,
  AlertTriangle,
  Radio,
  Flame,
  MessageSquare,
  Navigation,
  Shield,
  LucideIcon,
  TrendingUp,
  MapPin,
  Upload,
  BarChart3,
  Bot,
  Eye,
  Siren,
  FileBarChart,
} from 'lucide-react';
import { useTheme } from '@/lib/theme';
import { ThemeSelector } from './ThemeSelector';

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  category?: string;
  hidden?: boolean;
}

const navItems: NavItem[] = [
  // Core Navigation
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, category: 'Core' },
  { href: '/live-map', label: 'Live Map', icon: Map, category: 'Core' },
  { href: '/cameras', label: 'Cameras', icon: Camera, category: 'Core' },
  { href: '/investigations', label: 'Investigations', icon: Search, category: 'Core' },
  { href: '/entities', label: 'Entities', icon: Database, category: 'Core' },
  { href: '/events', label: 'Events', icon: Activity, category: 'Core' },
  
  // Crime Analysis
  { href: '/analytics/crime/heatmap', label: 'Heatmap', icon: Flame, category: 'Crime Analysis' },
  { href: '/analytics/crime/trends', label: 'Trends', icon: TrendingUp, category: 'Crime Analysis' },
  { href: '/analytics/crime/forecast', label: 'Forecast', icon: BarChart3, category: 'Crime Analysis' },
  { href: '/analytics/crime/repeat-locations', label: 'Repeat Locations', icon: MapPin, category: 'Crime Analysis' },
  { href: '/analytics/crime/upload', label: 'Upload Data', icon: Upload, category: 'Crime Analysis' },
  
  // Intelligence
  { href: '/lpr', label: 'LPR Intelligence', icon: Car, category: 'Intelligence' },
  { href: '/social-threat', label: 'Social Threat AI', icon: MessageSquare, category: 'Intelligence' },
  
  // Assets
  { href: '/drones', label: 'Drones', icon: Plane, category: 'Assets' },
  { href: '/robots', label: 'Robotics Unit', icon: Bot, category: 'Assets' },
  
  // Operations
  { href: '/cad', label: 'CAD Feed', icon: Radio, category: 'Operations' },
  { href: '/officers', label: 'Officer Tracking', icon: Shield, category: 'Operations' },
  
  // Reports
  { href: '/reports', label: 'RTCC Reports', icon: FileBarChart, category: 'Reports' },
];

const adminItems: NavItem[] = [
  { href: '/admin/users', label: 'User Management', icon: Users, category: 'Admin' },
  { href: '/settings', label: 'Settings', icon: Settings, category: 'Admin' },
];

export function ThemedSidebar() {
  const pathname = usePathname();
  const { theme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const visibleNavItems = navItems.filter((item) => !item.hidden);
  const categories = [...new Set(visibleNavItems.map((item) => item.category))];

  const renderNavItem = (item: NavItem, isAdmin = false) => {
    const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
    const isHovered = hoveredItem === item.href;
    const Icon = item.icon;

    return (
      <li key={item.href}>
        <Link
          href={item.href}
          className="g3ti-sidebar-item g3ti-particle-trail relative flex items-center gap-3 rounded-lg px-3 py-2"
          style={{
            background: isActive
              ? `${theme.colors.neuralBlue}15`
              : isHovered
                ? `${theme.colors.neuralBlue}10`
                : 'transparent',
            borderLeft: isActive ? `3px solid ${theme.colors.neuralBlue}` : '3px solid transparent',
            color: isActive
              ? theme.colors.neuralBlue
              : isHovered
                ? theme.colors.textPrimary
                : theme.colors.textSecondary,
            transition: theme.enableAnimations ? 'all 0.3s ease' : 'none',
          }}
          onMouseEnter={() => setHoveredItem(item.href)}
          onMouseLeave={() => setHoveredItem(null)}
        >
          {/* Gold icon ring */}
          <div
            className="g3ti-sidebar-icon flex h-9 w-9 items-center justify-center rounded-full"
            style={{
              border: `2px solid ${isActive ? theme.colors.neuralBlue : theme.colors.authorityGold}`,
              background: isActive
                ? `${theme.colors.neuralBlue}20`
                : `${theme.colors.authorityGold}10`,
              boxShadow:
                isHovered || isActive
                  ? `0 0 15px ${isActive ? theme.colors.neuralBlue : theme.colors.authorityGold}40`
                  : 'none',
              transition: theme.enableAnimations ? 'all 0.3s ease' : 'none',
            }}
          >
            <Icon className="h-4 w-4" />
          </div>
          {!collapsed && <span className="font-medium">{item.label}</span>}

          {/* Particle trail effect */}
          {theme.enableAnimations && isHovered && (
            <div
              className="absolute left-0 top-1/2 h-0.5 w-full -translate-y-1/2"
              style={{
                background: `linear-gradient(90deg, transparent, ${theme.colors.neuralBlue}40, transparent)`,
                animation: 'particleTrail 0.5s ease forwards',
              }}
            />
          )}
        </Link>
      </li>
    );
  };

  return (
    <aside
      className="g3ti-sidebar flex flex-col transition-all duration-300"
      style={{
        width: collapsed ? '64px' : '256px',
        background: `linear-gradient(180deg, ${theme.colors.backgroundSecondary} 0%, ${theme.colors.background} 100%)`,
        borderRight: `1px solid ${theme.colors.panelBorder}`,
      }}
    >
      {/* Logo - RBPD Badge */}
      <div
        className="flex h-20 items-center justify-center px-2"
        style={{ borderBottom: `1px solid ${theme.colors.panelBorder}` }}
      >
        {!collapsed ? (
          <div className="flex items-center gap-2">
            <Image
              src="/assets/rbpd/rbpd_logo_64.png"
              alt="RBPD Badge"
              width={64}
              height={64}
            />
            <div className="flex flex-col">
              <span
                className="text-sm font-bold"
                style={{ color: theme.colors.authorityGold }}
              >
                RBPD
              </span>
              <span
                className="text-xs"
                style={{ color: theme.colors.textMuted }}
              >
                RTCC-UIP
              </span>
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

      {/* Theme Selector */}
      <div className="px-2 py-3" style={{ borderBottom: `1px solid ${theme.colors.panelBorder}` }}>
        {!collapsed ? (
          <ThemeSelector />
        ) : (
          <div className="flex justify-center">
            <span className="text-xl">🔮</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {categories.map((category) => (
          <div key={category} className="mb-4">
            {/* Category label with micro-glow */}
            {!collapsed && (
              <div
                className="g3ti-category-label px-4 py-2 text-xs font-semibold uppercase tracking-wider"
                style={{
                  color: theme.colors.authorityGold,
                  textShadow: theme.enableAnimations
                    ? `0 0 10px ${theme.colors.authorityGold}30`
                    : 'none',
                }}
              >
                {category}
              </div>
            )}
            <ul className="space-y-1 px-2">
              {visibleNavItems
                .filter((item) => item.category === category)
                .map((item) => renderNavItem(item))}
            </ul>
          </div>
        ))}

        {/* Admin section */}
        <div style={{ borderTop: `1px solid ${theme.colors.panelBorder}` }} className="mt-4 pt-4">
          {!collapsed && (
            <div
              className="g3ti-category-label px-4 py-2 text-xs font-semibold uppercase tracking-wider"
              style={{
                color: theme.colors.authorityGold,
                textShadow: theme.enableAnimations
                  ? `0 0 10px ${theme.colors.authorityGold}30`
                  : 'none',
              }}
            >
              Administration
            </div>
          )}
          <ul className="space-y-1 px-2">
            {adminItems.map((item) => renderNavItem(item, true))}
          </ul>
        </div>
      </nav>

      {/* Collapse toggle */}
      <div className="p-2" style={{ borderTop: `1px solid ${theme.colors.panelBorder}` }}>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex w-full items-center justify-center rounded-lg p-2 transition-colors"
          style={{
            color: theme.colors.textSecondary,
            background: 'transparent',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = `${theme.colors.neuralBlue}10`;
            e.currentTarget.style.color = theme.colors.textPrimary;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.color = theme.colors.textSecondary;
          }}
        >
          {collapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <ChevronLeft className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Particle trail animation keyframes */}
      <style jsx>{`
        @keyframes particleTrail {
          0% {
            transform: translateY(-50%) translateX(-100%);
            opacity: 0;
          }
          50% {
            opacity: 1;
          }
          100% {
            transform: translateY(-50%) translateX(100%);
            opacity: 0;
          }
        }
      `}</style>
    </aside>
  );
}

export default ThemedSidebar;

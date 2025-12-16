'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Map,
  Camera,
  Video,
  Users,
  AlertTriangle,
  Shield,
  BarChart3,
  Car,
  Target,
  Brain,
  Network,
  Database,
  Plane,
  Bot,
  Zap,
  Workflow,
  Bell,
  CloudSun,
  Waves,
  Radio,
  Building2,
  Heart,
  Baby,
  HeartPulse,
  Route,
  Scale,
  PieChart,
  AlertCircle,
  FileText,
  MessageSquare,
  TrendingUp,
  FolderOpen,
  Edit,
  CheckSquare,
  History,
  UserCog,
  Lock,
  ClipboardList,
  Settings,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  LucideIcon,
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAuthStore } from '@/lib/store/auth';

// Role type for permissions
type UserRole = 'viewer' | 'analyst' | 'supervisor' | 'admin' | 'commander' | 'system-integrator';

// Navigation item interface
interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  roles?: UserRole[];
  badge?: string;
  isNew?: boolean;
}

// Section interface
interface NavSection {
  id: string;
  label: string;
  icon: LucideIcon;
  items: NavItem[];
  roles?: UserRole[];
  defaultOpen?: boolean;
}

// Define all navigation sections
const navSections: NavSection[] = [
  {
    id: 'command',
    label: 'Command Operations',
    icon: Shield,
    defaultOpen: true,
    items: [
      { href: '/master-dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { href: '/live-map', label: 'Live Map', icon: Map },
      { href: '/cameras', label: 'Cameras', icon: Camera },
      { href: '/cameras/video-wall', label: 'Video Wall', icon: Video },
      { href: '/units', label: 'Units', icon: Users },
      { href: '/incidents', label: 'Incidents', icon: AlertTriangle },
      { href: '/officer-safety', label: 'Officer Safety Monitor', icon: Shield, badge: 'LIVE' },
    ],
  },
  {
    id: 'intelligence',
    label: 'Intelligence',
    icon: Brain,
    items: [
      { href: '/analytics/crime', label: 'Crime Analytics', icon: BarChart3 },
      { href: '/lpr-intel', label: 'LPR Intelligence', icon: Car },
      { href: '/gunshot', label: 'Gunshot Detection', icon: Target },
      { href: '/global-threat-intel', label: 'Threat Intelligence', icon: AlertTriangle },
      { href: '/constellation', label: 'Constellation Link Analysis', icon: Network },
      { href: '/entities', label: 'Entity & Suspect Profiles', icon: Database },
    ],
    roles: ['analyst', 'supervisor', 'admin', 'commander', 'system-integrator'],
  },
  {
    id: 'robotics',
    label: 'Robotics',
    icon: Bot,
    items: [
      { href: '/drones', label: 'Drone Operations', icon: Plane },
      { href: '/robotics', label: 'Robot Dog Ops', icon: Bot },
      { href: '/autonomy', label: 'Autonomous Dispatch Center', icon: Zap },
    ],
    roles: ['supervisor', 'admin', 'commander', 'system-integrator'],
  },
  {
    id: 'orchestration',
    label: 'Orchestration',
    icon: Workflow,
    items: [
      { href: '/orchestration', label: 'Orchestration Engine', icon: Workflow },
      { href: '/orchestration/builder', label: 'Workflow Builder', icon: Edit },
      { href: '/automations', label: 'Automations & Alerts', icon: Bell },
    ],
    roles: ['supervisor', 'admin', 'commander', 'system-integrator'],
  },
  {
    id: 'city-systems',
    label: 'City Systems',
    icon: Building2,
    items: [
      { href: '/traffic', label: 'Traffic (FDOT + City)', icon: Car },
      { href: '/weather', label: 'Weather & Marine', icon: CloudSun },
      { href: '/sensors', label: 'Smart Sensors', icon: Radio },
      { href: '/infrastructure', label: 'Infrastructure Map', icon: Building2 },
    ],
  },
  {
    id: 'human-stability',
    label: 'Human Stability',
    icon: Heart,
    items: [
      { href: '/human-intel/dv', label: 'DV Escalation Predictor', icon: AlertTriangle },
      { href: '/human-intel/youth', label: 'Youth Crisis Monitor', icon: Baby },
      { href: '/human-intel/suicide', label: 'Suicide Risk Detection', icon: HeartPulse },
      { href: '/human-intel/crisis-route', label: 'Mental Health Routing', icon: Route },
    ],
    roles: ['analyst', 'supervisor', 'admin', 'commander', 'system-integrator'],
  },
  {
    id: 'moral-compass',
    label: 'Moral Compass',
    icon: Scale,
    items: [
      { href: '/moral-compass', label: 'AI Moral Compass', icon: Scale },
      { href: '/moral-compass/fairness', label: 'Fairness Dashboard', icon: PieChart },
      { href: '/moral-compass/alerts', label: 'Ethics Alerts', icon: AlertCircle },
    ],
    roles: ['supervisor', 'admin', 'commander', 'system-integrator'],
  },
  {
    id: 'community-guardian',
    label: 'Community Guardian',
    icon: MessageSquare,
    items: [
      { href: '/public-guardian/reports', label: 'Public Transparency Reports', icon: FileText },
      { href: '/public-guardian/engagement', label: 'Community Engagement', icon: MessageSquare },
      { href: '/public-guardian/trust', label: 'Trust Score Dashboard', icon: TrendingUp },
    ],
    roles: ['supervisor', 'admin', 'commander', 'system-integrator'],
  },
  {
    id: 'data-management',
    label: 'Data Management',
    icon: FolderOpen,
    items: [
      { href: '/data-admin', label: 'Data Admin Portal', icon: FolderOpen },
      { href: '/data-admin/manual', label: 'Manual Updates', icon: Edit },
      { href: '/data-admin/validation', label: 'Validation Queue', icon: CheckSquare },
      { href: '/data-admin/history', label: 'Version History', icon: History },
    ],
    roles: ['admin', 'commander', 'system-integrator'],
  },
  {
    id: 'system-admin',
    label: 'System Admin',
    icon: Settings,
    items: [
      { href: '/admin/users', label: 'User Management', icon: UserCog },
      { href: '/admin/permissions', label: 'Roles & Permissions', icon: Lock },
      { href: '/admin/audit', label: 'Audit Logs', icon: ClipboardList },
      { href: '/admin/settings', label: 'System Settings', icon: Settings },
    ],
    roles: ['admin', 'system-integrator'],
  },
];

/**
 * Enterprise RTCC Sidebar Component
 * 
 * Features:
 * - 10 collapsible sections with all modules
 * - Role-based visibility
 * - Dark tactical theme with police blue accents
 * - Mini-sidebar mode when collapsed
 * - CJIS warning footer
 * - Active state highlighting
 */
export function EnterpriseSidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(['command']));

  // Get user role with fallback
  const userRole: UserRole = (user?.role as UserRole) || 'viewer';

  // Check if user has access to a section or item
  const hasAccess = (roles?: UserRole[]): boolean => {
    if (!roles || roles.length === 0) return true;
    return roles.includes(userRole);
  };

  // Toggle section open/closed
  const toggleSection = (sectionId: string) => {
    if (collapsed) return;
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(sectionId)) {
        next.delete(sectionId);
      } else {
        next.add(sectionId);
      }
      return next;
    });
  };

  // Check if a path is active
  const isActive = (href: string): boolean => {
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  // Check if any item in a section is active
  const isSectionActive = (section: NavSection): boolean => {
    return section.items.some((item) => isActive(item.href));
  };

  // Filter sections based on role
  const visibleSections = navSections.filter((section) => hasAccess(section.roles));

  return (
    <aside
      className={clsx(
        'flex flex-col bg-[#0a0f24] border-r border-[#1a2744] transition-all duration-300',
        collapsed ? 'w-16' : 'w-72'
      )}
    >
      {/* Logo Header */}
      <div className="flex h-16 items-center justify-between border-b border-[#1a2744] px-3">
        {!collapsed ? (
          <div className="flex items-center gap-3">
            <Image
              src="/assets/rbpd/rbpd_logo_48.png"
              alt="RBPD Badge"
              width={40}
              height={40}
              className="flex-shrink-0"
            />
            <div className="flex flex-col">
              <span className="text-sm font-bold text-white">RBPD RTCC</span>
              <span className="text-[10px] text-[#0050ff] font-medium">UNIFIED INTELLIGENCE</span>
            </div>
          </div>
        ) : (
          <Image
            src="/assets/rbpd/rbpd_logo_32.png"
            alt="RBPD Badge"
            width={32}
            height={32}
            className="mx-auto"
          />
        )}
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 overflow-y-auto py-2 scrollbar-thin scrollbar-thumb-[#1a2744] scrollbar-track-transparent">
        {visibleSections.map((section) => {
          const SectionIcon = section.icon;
          const isOpen = openSections.has(section.id);
          const sectionActive = isSectionActive(section);
          const visibleItems = section.items.filter((item) => hasAccess(item.roles));

          if (visibleItems.length === 0) return null;

          return (
            <div key={section.id} className="mb-1">
              {/* Section Header */}
              <button
                onClick={() => toggleSection(section.id)}
                className={clsx(
                  'flex w-full items-center gap-2 px-3 py-2 text-left transition-colors',
                  sectionActive
                    ? 'bg-[#0050ff]/10 text-[#0050ff]'
                    : 'text-gray-400 hover:bg-[#1a2744] hover:text-white'
                )}
              >
                <SectionIcon className="h-4 w-4 flex-shrink-0" />
                {!collapsed && (
                  <>
                    <span className="flex-1 text-xs font-semibold uppercase tracking-wider">
                      {section.label}
                    </span>
                    {isOpen ? (
                      <ChevronUp className="h-3 w-3" />
                    ) : (
                      <ChevronDown className="h-3 w-3" />
                    )}
                  </>
                )}
              </button>

              {/* Section Items */}
              {(isOpen || collapsed) && (
                <ul className={clsx('space-y-0.5', !collapsed && 'mt-1 pl-2')}>
                  {visibleItems.map((item) => {
                    const ItemIcon = item.icon;
                    const active = isActive(item.href);

                    return (
                      <li key={item.href}>
                        <Link
                          href={item.href}
                          className={clsx(
                            'flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-all',
                            active
                              ? 'bg-[#0050ff] text-white shadow-lg shadow-[#0050ff]/20'
                              : 'text-gray-400 hover:bg-[#1a2744] hover:text-white'
                          )}
                          title={collapsed ? item.label : undefined}
                        >
                          <ItemIcon className="h-4 w-4 flex-shrink-0" />
                          {!collapsed && (
                            <>
                              <span className="flex-1 truncate">{item.label}</span>
                              {item.badge && (
                                <span className="rounded bg-red-500 px-1.5 py-0.5 text-[10px] font-bold text-white animate-pulse">
                                  {item.badge}
                                </span>
                              )}
                              {item.isNew && (
                                <span className="rounded bg-green-500 px-1.5 py-0.5 text-[10px] font-bold text-white">
                                  NEW
                                </span>
                              )}
                            </>
                          )}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })}
      </nav>

      {/* CJIS Warning Footer */}
      {!collapsed && (
        <div className="border-t border-[#1a2744] bg-[#0a0f24] px-3 py-2">
          <div className="rounded bg-yellow-900/30 border border-yellow-700/50 px-2 py-1.5">
            <p className="text-[9px] text-yellow-500 leading-tight">
              <strong>CJIS WARNING:</strong> This system contains Criminal Justice Information. 
              Unauthorized access is prohibited. All activity is monitored and logged.
            </p>
          </div>
        </div>
      )}

      {/* Collapse Toggle */}
      <div className="border-t border-[#1a2744] p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex w-full items-center justify-center rounded-md p-2 text-gray-400 hover:bg-[#1a2744] hover:text-white transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <ChevronLeft className="h-5 w-5" />
          )}
        </button>
      </div>
    </aside>
  );
}

export default EnterpriseSidebar;

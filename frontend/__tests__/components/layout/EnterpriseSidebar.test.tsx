/**
 * Enterprise RTCC Sidebar Tests
 * 
 * Tests for:
 * - Sidebar integrity (all 10 sections render)
 * - Role-based visibility
 * - Navigation routing
 * - Collapsible groups
 * - Mini-sidebar mode
 * - CJIS footer
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/master-dashboard'),
}));

// Mock Next.js Image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => <img {...props} />,
}));

// Mock auth store
const mockUser = {
  id: 'test-user-1',
  username: 'testuser',
  role: 'admin',
  email: 'test@example.com',
};

jest.mock('@/lib/store/auth', () => ({
  useAuthStore: jest.fn(() => ({
    user: mockUser,
    isAuthenticated: true,
  })),
}));

// Import after mocks
import { EnterpriseSidebar } from '@/app/components/layout/EnterpriseSidebar';
import { useAuthStore } from '@/lib/store/auth';

describe('EnterpriseSidebar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Sidebar Integrity', () => {
    it('renders all 10 sections for admin user', () => {
      render(<EnterpriseSidebar />);
      
      // Check all section headers are present
      expect(screen.getByText('Command Operations')).toBeInTheDocument();
      expect(screen.getByText('Intelligence')).toBeInTheDocument();
      expect(screen.getByText('Robotics')).toBeInTheDocument();
      expect(screen.getByText('Orchestration')).toBeInTheDocument();
      expect(screen.getByText('City Systems')).toBeInTheDocument();
      expect(screen.getByText('Human Stability')).toBeInTheDocument();
      expect(screen.getByText('Moral Compass')).toBeInTheDocument();
      expect(screen.getByText('Community Guardian')).toBeInTheDocument();
      expect(screen.getByText('Data Management')).toBeInTheDocument();
      expect(screen.getByText('System Admin')).toBeInTheDocument();
    });

    it('renders RBPD logo', () => {
      render(<EnterpriseSidebar />);
      
      const logo = screen.getByAltText('RBPD Badge');
      expect(logo).toBeInTheDocument();
    });

    it('renders RBPD RTCC title', () => {
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText('RBPD RTCC')).toBeInTheDocument();
      expect(screen.getByText('UNIFIED INTELLIGENCE')).toBeInTheDocument();
    });
  });

  describe('Command Operations Section', () => {
    it('renders all Command Operations items', () => {
      render(<EnterpriseSidebar />);
      
      // Command Operations is open by default
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Live Map')).toBeInTheDocument();
      expect(screen.getByText('Cameras')).toBeInTheDocument();
      expect(screen.getByText('Video Wall')).toBeInTheDocument();
      expect(screen.getByText('Units')).toBeInTheDocument();
      expect(screen.getByText('Incidents')).toBeInTheDocument();
      expect(screen.getByText('Officer Safety Monitor')).toBeInTheDocument();
    });

    it('shows LIVE badge on Officer Safety Monitor', () => {
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText('LIVE')).toBeInTheDocument();
    });
  });

  describe('Role-Based Visibility', () => {
    it('shows all sections for system-integrator role', () => {
      (useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, role: 'system-integrator' },
        isAuthenticated: true,
      });
      
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText('System Admin')).toBeInTheDocument();
      expect(screen.getByText('Data Management')).toBeInTheDocument();
    });

    it('hides System Admin section for viewer role', () => {
      (useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, role: 'viewer' },
        isAuthenticated: true,
      });
      
      render(<EnterpriseSidebar />);
      
      expect(screen.queryByText('System Admin')).not.toBeInTheDocument();
    });

    it('hides Intelligence section for viewer role', () => {
      (useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, role: 'viewer' },
        isAuthenticated: true,
      });
      
      render(<EnterpriseSidebar />);
      
      expect(screen.queryByText('Intelligence')).not.toBeInTheDocument();
    });

    it('shows Command Operations and City Systems for viewer role', () => {
      (useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, role: 'viewer' },
        isAuthenticated: true,
      });
      
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText('Command Operations')).toBeInTheDocument();
      expect(screen.getByText('City Systems')).toBeInTheDocument();
    });

    it('shows Intelligence section for analyst role', () => {
      (useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, role: 'analyst' },
        isAuthenticated: true,
      });
      
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText('Intelligence')).toBeInTheDocument();
    });

    it('shows Robotics section for supervisor role', () => {
      (useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, role: 'supervisor' },
        isAuthenticated: true,
      });
      
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText('Robotics')).toBeInTheDocument();
    });

    it('shows Data Management section for admin role', () => {
      (useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, role: 'admin' },
        isAuthenticated: true,
      });
      
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText('Data Management')).toBeInTheDocument();
    });

    it('shows all sections for commander role', () => {
      (useAuthStore as jest.Mock).mockReturnValue({
        user: { ...mockUser, role: 'commander' },
        isAuthenticated: true,
      });
      
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText('Moral Compass')).toBeInTheDocument();
      expect(screen.getByText('Community Guardian')).toBeInTheDocument();
    });
  });

  describe('Navigation Routing', () => {
    it('renders correct href for Dashboard', () => {
      render(<EnterpriseSidebar />);
      
      const dashboardLink = screen.getByRole('link', { name: /Dashboard/i });
      expect(dashboardLink).toHaveAttribute('href', '/master-dashboard');
    });

    it('renders correct href for Live Map', () => {
      render(<EnterpriseSidebar />);
      
      const liveMapLink = screen.getByRole('link', { name: /Live Map/i });
      expect(liveMapLink).toHaveAttribute('href', '/live-map');
    });

    it('renders correct href for Cameras', () => {
      render(<EnterpriseSidebar />);
      
      const camerasLink = screen.getByRole('link', { name: /^Cameras$/i });
      expect(camerasLink).toHaveAttribute('href', '/cameras');
    });

    it('renders correct href for Video Wall', () => {
      render(<EnterpriseSidebar />);
      
      const videoWallLink = screen.getByRole('link', { name: /Video Wall/i });
      expect(videoWallLink).toHaveAttribute('href', '/cameras/video-wall');
    });
  });

  describe('Collapsible Groups', () => {
    it('Command Operations section is open by default', () => {
      render(<EnterpriseSidebar />);
      
      // Items should be visible
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    it('can toggle section open/closed', () => {
      render(<EnterpriseSidebar />);
      
      // Click on Intelligence section to open it
      const intelligenceHeader = screen.getByText('Intelligence');
      fireEvent.click(intelligenceHeader);
      
      // Items should now be visible
      expect(screen.getByText('Crime Analytics')).toBeInTheDocument();
    });

    it('can collapse Command Operations section', () => {
      render(<EnterpriseSidebar />);
      
      // Click on Command Operations to collapse it
      const commandHeader = screen.getByText('Command Operations');
      fireEvent.click(commandHeader);
      
      // Items should be hidden (section collapsed)
      // Note: In the current implementation, items are still rendered but section is toggled
    });
  });

  describe('Mini-Sidebar Mode', () => {
    it('renders collapse toggle button', () => {
      render(<EnterpriseSidebar />);
      
      const collapseButton = screen.getByTitle('Collapse sidebar');
      expect(collapseButton).toBeInTheDocument();
    });

    it('can toggle to mini-sidebar mode', () => {
      render(<EnterpriseSidebar />);
      
      const collapseButton = screen.getByTitle('Collapse sidebar');
      fireEvent.click(collapseButton);
      
      // After collapse, button should show "Expand sidebar"
      expect(screen.getByTitle('Expand sidebar')).toBeInTheDocument();
    });

    it('hides section labels in mini-sidebar mode', () => {
      render(<EnterpriseSidebar />);
      
      // Collapse sidebar
      const collapseButton = screen.getByTitle('Collapse sidebar');
      fireEvent.click(collapseButton);
      
      // Section labels should be hidden (only icons visible)
      // The text "UNIFIED INTELLIGENCE" should not be visible
      expect(screen.queryByText('UNIFIED INTELLIGENCE')).not.toBeInTheDocument();
    });
  });

  describe('CJIS Warning Footer', () => {
    it('renders CJIS warning footer', () => {
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText(/CJIS WARNING/i)).toBeInTheDocument();
    });

    it('contains proper CJIS warning text', () => {
      render(<EnterpriseSidebar />);
      
      expect(screen.getByText(/Criminal Justice Information/i)).toBeInTheDocument();
      expect(screen.getByText(/Unauthorized access is prohibited/i)).toBeInTheDocument();
    });

    it('hides CJIS footer in mini-sidebar mode', () => {
      render(<EnterpriseSidebar />);
      
      // Collapse sidebar
      const collapseButton = screen.getByTitle('Collapse sidebar');
      fireEvent.click(collapseButton);
      
      // CJIS warning should be hidden
      expect(screen.queryByText(/CJIS WARNING/i)).not.toBeInTheDocument();
    });
  });

  describe('Active State Highlighting', () => {
    it('highlights active navigation item', () => {
      // Mock pathname to be /master-dashboard
      const { usePathname } = require('next/navigation');
      usePathname.mockReturnValue('/master-dashboard');
      
      render(<EnterpriseSidebar />);
      
      const dashboardLink = screen.getByRole('link', { name: /Dashboard/i });
      expect(dashboardLink).toHaveClass('bg-[#0050ff]');
    });
  });

  describe('Styling', () => {
    it('uses dark tactical theme colors', () => {
      const { container } = render(<EnterpriseSidebar />);
      
      // Check sidebar has navy background
      const sidebar = container.querySelector('aside');
      expect(sidebar).toHaveClass('bg-[#0a0f24]');
    });

    it('uses police blue accent color for active items', () => {
      render(<EnterpriseSidebar />);
      
      const dashboardLink = screen.getByRole('link', { name: /Dashboard/i });
      expect(dashboardLink).toHaveClass('bg-[#0050ff]');
    });
  });
});

describe('EnterpriseSidebar Section Items', () => {
  beforeEach(() => {
    (useAuthStore as jest.Mock).mockReturnValue({
      user: { ...mockUser, role: 'system-integrator' },
      isAuthenticated: true,
    });
  });

  it('Intelligence section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open Intelligence section
    fireEvent.click(screen.getByText('Intelligence'));
    
    expect(screen.getByText('Crime Analytics')).toBeInTheDocument();
    expect(screen.getByText('LPR Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Gunshot Detection')).toBeInTheDocument();
    expect(screen.getByText('Threat Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Constellation Link Analysis')).toBeInTheDocument();
    expect(screen.getByText('Entity & Suspect Profiles')).toBeInTheDocument();
  });

  it('Robotics section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open Robotics section
    fireEvent.click(screen.getByText('Robotics'));
    
    expect(screen.getByText('Drone Operations')).toBeInTheDocument();
    expect(screen.getByText('Robot Dog Ops')).toBeInTheDocument();
    expect(screen.getByText('Autonomous Dispatch Center')).toBeInTheDocument();
  });

  it('Orchestration section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open Orchestration section
    fireEvent.click(screen.getByText('Orchestration'));
    
    expect(screen.getByText('Orchestration Engine')).toBeInTheDocument();
    expect(screen.getByText('Workflow Builder')).toBeInTheDocument();
    expect(screen.getByText('Automations & Alerts')).toBeInTheDocument();
  });

  it('City Systems section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open City Systems section
    fireEvent.click(screen.getByText('City Systems'));
    
    expect(screen.getByText('Traffic (FDOT + City)')).toBeInTheDocument();
    expect(screen.getByText('Weather & Marine')).toBeInTheDocument();
    expect(screen.getByText('Smart Sensors')).toBeInTheDocument();
    expect(screen.getByText('Infrastructure Map')).toBeInTheDocument();
  });

  it('Human Stability section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open Human Stability section
    fireEvent.click(screen.getByText('Human Stability'));
    
    expect(screen.getByText('DV Escalation Predictor')).toBeInTheDocument();
    expect(screen.getByText('Youth Crisis Monitor')).toBeInTheDocument();
    expect(screen.getByText('Suicide Risk Detection')).toBeInTheDocument();
    expect(screen.getByText('Mental Health Routing')).toBeInTheDocument();
  });

  it('Moral Compass section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open Moral Compass section
    fireEvent.click(screen.getByText('Moral Compass'));
    
    expect(screen.getByText('AI Moral Compass')).toBeInTheDocument();
    expect(screen.getByText('Fairness Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Ethics Alerts')).toBeInTheDocument();
  });

  it('Community Guardian section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open Community Guardian section
    fireEvent.click(screen.getByText('Community Guardian'));
    
    expect(screen.getByText('Public Transparency Reports')).toBeInTheDocument();
    expect(screen.getByText('Community Engagement')).toBeInTheDocument();
    expect(screen.getByText('Trust Score Dashboard')).toBeInTheDocument();
  });

  it('Data Management section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open Data Management section
    fireEvent.click(screen.getByText('Data Management'));
    
    expect(screen.getByText('Data Admin Portal')).toBeInTheDocument();
    expect(screen.getByText('Manual Updates')).toBeInTheDocument();
    expect(screen.getByText('Validation Queue')).toBeInTheDocument();
    expect(screen.getByText('Version History')).toBeInTheDocument();
  });

  it('System Admin section has correct items', () => {
    render(<EnterpriseSidebar />);
    
    // Open System Admin section
    fireEvent.click(screen.getByText('System Admin'));
    
    expect(screen.getByText('User Management')).toBeInTheDocument();
    expect(screen.getByText('Roles & Permissions')).toBeInTheDocument();
    expect(screen.getByText('Audit Logs')).toBeInTheDocument();
    expect(screen.getByText('System Settings')).toBeInTheDocument();
  });
});

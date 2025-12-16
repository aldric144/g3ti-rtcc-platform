import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { jwtDecode } from 'jwt-decode';
import { api } from '@/lib/api';
import { STORAGE_KEYS } from '@/shared/constants';

/**
 * User role type.
 */
export type Role = 'admin' | 'supervisor' | 'detective' | 'rtcc_analyst' | 'officer';

/**
 * User profile interface.
 */
export interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: Role;
  badgeNumber?: string;
  department?: string;
}

/**
 * Token payload from JWT.
 */
interface TokenPayload {
  sub: string;
  username: string;
  role: Role;
  exp: number;
  iat: number;
}

/**
 * Auth store state interface.
 */
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<boolean>;
  checkAuth: () => void;
  clearError: () => void;
  setUser: (user: User) => void;
}

/**
 * Check if a token is expired.
 */
function isTokenExpired(token: string): boolean {
  try {
    const decoded = jwtDecode<TokenPayload>(token);
    return decoded.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

/**
 * Auth store using Zustand with persistence.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,

      /**
       * Login with username and password.
       */
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await api.post('/auth/login', {
            username,
            password,
          });

          const { access_token, refresh_token } = response.data;

          // Decode token to get user info
          const decoded = jwtDecode<TokenPayload>(access_token);

          // Fetch full user profile
          const userResponse = await api.get('/auth/me', {
            headers: { Authorization: `Bearer ${access_token}` },
          });

          set({
            accessToken: access_token,
            refreshToken: refresh_token,
            user: userResponse.data,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          return true;
        } catch (error: any) {
          const message =
            error.response?.data?.detail ||
            error.response?.data?.message ||
            'Login failed. Please check your credentials.';

          set({
            isLoading: false,
            error: message,
            isAuthenticated: false,
            user: null,
            accessToken: null,
            refreshToken: null,
          });

          return false;
        }
      },

      /**
       * Logout and clear all auth state.
       */
      logout: async () => {
        const { accessToken } = get();

        try {
          if (accessToken) {
            await api.post('/auth/logout', null, {
              headers: { Authorization: `Bearer ${accessToken}` },
            });
          }
        } catch {
          // Ignore logout errors
        }

        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },

      /**
       * Refresh the access token.
       */
      refreshAuth: async () => {
        const { refreshToken } = get();

        if (!refreshToken) {
          set({ isAuthenticated: false, isLoading: false });
          return false;
        }

        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;

          // Fetch updated user profile
          const userResponse = await api.get('/auth/me', {
            headers: { Authorization: `Bearer ${access_token}` },
          });

          set({
            accessToken: access_token,
            refreshToken: refresh_token,
            user: userResponse.data,
            isAuthenticated: true,
            isLoading: false,
          });

          return true;
        } catch {
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });

          return false;
        }
      },

      /**
       * Check current auth state on app load.
       * Includes timeout to prevent infinite loading states.
       */
      checkAuth: () => {
        const { accessToken, refreshToken, refreshAuth } = get();

        // Safety timeout - ensure isLoading is set to false after 5 seconds max
        const safetyTimeout = setTimeout(() => {
          const currentState = get();
          if (currentState.isLoading) {
            console.warn('[Auth] Safety timeout triggered - forcing isLoading to false');
            set({ isLoading: false, isAuthenticated: false });
          }
        }, 5000);

        if (!accessToken) {
          clearTimeout(safetyTimeout);
          set({ isLoading: false, isAuthenticated: false });
          return;
        }

        if (isTokenExpired(accessToken)) {
          if (refreshToken && !isTokenExpired(refreshToken)) {
            // Call refreshAuth and ensure timeout is cleared when it completes
            refreshAuth().finally(() => {
              clearTimeout(safetyTimeout);
            });
          } else {
            clearTimeout(safetyTimeout);
            set({
              user: null,
              accessToken: null,
              refreshToken: null,
              isAuthenticated: false,
              isLoading: false,
            });
          }
        } else {
          clearTimeout(safetyTimeout);
          set({ isLoading: false, isAuthenticated: true });
        }
      },

      /**
       * Clear any error message.
       */
      clearError: () => set({ error: null }),

      /**
       * Set user profile.
       */
      setUser: (user: User) => set({ user }),
    }),
    {
      name: 'rtcc-auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);

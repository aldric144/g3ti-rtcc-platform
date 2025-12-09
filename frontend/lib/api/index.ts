/**
 * API client for the G3TI RTCC-UIP Backend.
 *
 * Provides a configured axios instance with:
 * - Base URL configuration
 * - Authentication token injection
 * - Error handling
 * - Request/response interceptors
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Create and configure the API client.
 */
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  client.interceptors.request.use(
    (config) => {
      // Get token from localStorage (set by auth store)
      if (typeof window !== 'undefined') {
        const authStorage = localStorage.getItem('rtcc-auth-storage');
        if (authStorage) {
          try {
            const { state } = JSON.parse(authStorage);
            if (state?.accessToken) {
              config.headers.Authorization = `Bearer ${state.accessToken}`;
            }
          } catch {
            // Ignore parse errors
          }
        }
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

      // Handle 401 errors (unauthorized)
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        // Try to refresh token
        if (typeof window !== 'undefined') {
          const authStorage = localStorage.getItem('rtcc-auth-storage');
          if (authStorage) {
            try {
              const { state } = JSON.parse(authStorage);
              if (state?.refreshToken) {
                const response = await axios.post(`${API_URL}/auth/refresh`, {
                  refresh_token: state.refreshToken,
                });

                const { access_token, refresh_token } = response.data;

                // Update stored tokens
                const newState = {
                  ...state,
                  accessToken: access_token,
                  refreshToken: refresh_token,
                };
                localStorage.setItem('rtcc-auth-storage', JSON.stringify({ state: newState }));

                // Retry original request
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `Bearer ${access_token}`;
                }
                return client(originalRequest);
              }
            } catch {
              // Refresh failed, clear auth state
              localStorage.removeItem('rtcc-auth-storage');
              window.location.href = '/login';
            }
          }
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
}

/**
 * Configured API client instance.
 */
export const api = createApiClient();

/**
 * API error response interface.
 */
export interface ApiError {
  errorCode: string;
  message: string;
  details?: Record<string, unknown>;
}

/**
 * Extract error message from API error response.
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiError | undefined;
    return data?.message || error.message || 'An error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
}

/**
 * API endpoints organized by domain.
 */
export const endpoints = {
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    refresh: '/auth/refresh',
    me: '/auth/me',
    users: '/auth/users',
  },
  entities: {
    base: '/entities',
    byType: (type: string) => `/entities/${type}`,
    byId: (type: string, id: string) => `/entities/${type}/${id}`,
    relationships: (type: string, id: string) => `/entities/${type}/${id}/relationships`,
    network: (type: string, id: string) => `/entities/${type}/${id}/network`,
    search: (type: string) => `/entities/${type}/search`,
  },
  investigations: {
    base: '/investigations',
    search: '/investigations/search',
    byId: (id: string) => `/investigations/${id}`,
  },
  realtime: {
    events: '/realtime/events',
    byId: (id: string) => `/realtime/events/${id}`,
    acknowledge: (id: string) => `/realtime/events/${id}/acknowledge`,
    stats: '/realtime/stats',
  },
  system: {
    health: '/system/health',
    info: '/system/info',
    config: '/system/config',
    metrics: '/system/metrics',
  },
};

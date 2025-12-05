/**
 * Common schemas for the G3TI RTCC-UIP Platform.
 */

/**
 * Paginated response wrapper.
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  pages: number;
}

/**
 * API error response.
 */
export interface ErrorResponse {
  errorCode: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
  requestId?: string;
}

/**
 * Health check response.
 */
export interface HealthCheck {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  components: Record<string, ComponentHealth>;
}

/**
 * Component health status.
 */
export interface ComponentHealth {
  status: 'healthy' | 'unhealthy';
  message?: string;
}

/**
 * Sort order configuration.
 */
export interface SortOrder {
  field: string;
  direction: 'asc' | 'desc';
}

/**
 * Filter condition.
 */
export interface FilterCondition {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'contains';
  value: unknown;
}

/**
 * Query parameters for list endpoints.
 */
export interface QueryParams {
  page?: number;
  pageSize?: number;
  sort?: SortOrder[];
  filters?: FilterCondition[];
  search?: string;
}

/**
 * Bulk operation result.
 */
export interface BulkOperationResult {
  total: number;
  successful: number;
  failed: number;
  errors: Array<{
    index: number;
    error: string;
  }>;
}

/**
 * Search query.
 */
export interface SearchQuery {
  query: string;
  entityTypes?: string[];
  dateFrom?: string;
  dateTo?: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  radiusMiles?: number;
  filters?: Record<string, unknown>;
  includeRelated?: boolean;
  page?: number;
  pageSize?: number;
}

/**
 * Search result item.
 */
export interface SearchResultItem {
  id: string;
  entityType: string;
  title: string;
  description?: string;
  score: number;
  highlights: Record<string, string[]>;
  metadata: Record<string, unknown>;
  location?: {
    latitude: number;
    longitude: number;
  };
  timestamp?: string;
}

/**
 * Search results.
 */
export interface SearchResults {
  query: string;
  total: number;
  page: number;
  pageSize: number;
  pages: number;
  items: SearchResultItem[];
  facets: Record<string, Record<string, number>>;
  suggestions: string[];
  tookMs: number;
}

/**
 * Date range.
 */
export interface DateRange {
  start: string;
  end: string;
}

/**
 * Time period presets.
 */
export type TimePeriod = 
  | 'last_hour'
  | 'last_24_hours'
  | 'last_7_days'
  | 'last_30_days'
  | 'last_90_days'
  | 'custom';

/**
 * Get date range for a time period.
 */
export function getDateRangeForPeriod(period: TimePeriod): DateRange | null {
  const now = new Date();
  let start: Date;

  switch (period) {
    case 'last_hour':
      start = new Date(now.getTime() - 60 * 60 * 1000);
      break;
    case 'last_24_hours':
      start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      break;
    case 'last_7_days':
      start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      break;
    case 'last_30_days':
      start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      break;
    case 'last_90_days':
      start = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
      break;
    case 'custom':
      return null;
    default:
      return null;
  }

  return {
    start: start.toISOString(),
    end: now.toISOString(),
  };
}

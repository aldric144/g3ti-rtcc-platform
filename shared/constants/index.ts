/**
 * Shared constants for the G3TI RTCC-UIP Platform.
 */

/**
 * API configuration.
 */
export const API_CONFIG = {
  VERSION: 'v1',
  PREFIX: '/api/v1',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

/**
 * WebSocket configuration.
 */
export const WS_CONFIG = {
  RECONNECT_INTERVAL: 5000,
  MAX_RECONNECT_ATTEMPTS: 10,
  HEARTBEAT_INTERVAL: 30000,
  MESSAGE_TIMEOUT: 10000,
} as const;

/**
 * Pagination defaults.
 */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;

/**
 * Map configuration.
 */
export const MAP_CONFIG = {
  DEFAULT_CENTER: [-95.7129, 37.0902] as [number, number], // US center
  DEFAULT_ZOOM: 4,
  MIN_ZOOM: 2,
  MAX_ZOOM: 20,
  CLUSTER_RADIUS: 50,
  CLUSTER_MAX_ZOOM: 14,
} as const;

/**
 * Date/time formats.
 */
export const DATE_FORMATS = {
  DATE: 'YYYY-MM-DD',
  TIME: 'HH:mm:ss',
  DATETIME: 'YYYY-MM-DD HH:mm:ss',
  DATETIME_SHORT: 'MM/DD/YY HH:mm',
  RELATIVE: 'relative',
} as const;

/**
 * Local storage keys.
 */
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'rtcc_access_token',
  REFRESH_TOKEN: 'rtcc_refresh_token',
  USER: 'rtcc_user',
  THEME: 'rtcc_theme',
  MAP_SETTINGS: 'rtcc_map_settings',
  EVENT_FILTERS: 'rtcc_event_filters',
} as const;

/**
 * Route paths.
 */
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  MAP: '/map',
  INVESTIGATIONS: '/investigations',
  INVESTIGATION_DETAIL: '/investigations/:id',
  ENTITIES: '/entities',
  ENTITY_DETAIL: '/entities/:type/:id',
  EVENTS: '/events',
  SETTINGS: '/settings',
  ADMIN: '/admin',
  ADMIN_USERS: '/admin/users',
} as const;

/**
 * HTTP status codes.
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

/**
 * Error codes.
 */
export const ERROR_CODES = {
  // Authentication
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  INVALID_TOKEN: 'INVALID_TOKEN',
  ACCOUNT_LOCKED: 'ACCOUNT_LOCKED',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',
  
  // Validation
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',
  
  // Resources
  NOT_FOUND: 'NOT_FOUND',
  DUPLICATE: 'DUPLICATE',
  
  // System
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
} as const;

/**
 * Entity types.
 */
export const ENTITY_TYPES = [
  'Person',
  'Vehicle',
  'Incident',
  'Weapon',
  'ShellCasing',
  'Address',
  'Camera',
  'LicensePlate',
] as const;

/**
 * Relationship types.
 */
export const RELATIONSHIP_TYPES = [
  'SUSPECT_IN',
  'VICTIM_IN',
  'WITNESS_IN',
  'OWNS',
  'DRIVES',
  'PASSENGER_IN',
  'RESIDES_AT',
  'WORKS_AT',
  'VISITED',
  'OCCURRED_AT',
  'REPORTED_AT',
  'ASSOCIATED_WITH',
  'FAMILY_OF',
  'KNOWN_ASSOCIATE',
  'LINKED_TO',
  'MATCHED_WITH',
  'CAPTURED_BY',
  'SEEN_AT',
  'USED_IN',
  'RECOVERED_AT',
] as const;

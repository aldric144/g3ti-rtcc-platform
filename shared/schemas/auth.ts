/**
 * Authentication schemas for the G3TI RTCC-UIP Platform.
 */

/**
 * User roles with hierarchy.
 * Higher roles have all permissions of lower roles.
 */
export enum Role {
  ADMIN = 'admin',
  SUPERVISOR = 'supervisor',
  DETECTIVE = 'detective',
  RTCC_ANALYST = 'rtcc_analyst',
  OFFICER = 'officer',
}

/**
 * Role hierarchy for permission checking.
 */
export const ROLE_HIERARCHY: Record<Role, number> = {
  [Role.ADMIN]: 5,
  [Role.SUPERVISOR]: 4,
  [Role.DETECTIVE]: 3,
  [Role.RTCC_ANALYST]: 2,
  [Role.OFFICER]: 1,
};

/**
 * Check if a role has permission for a required role.
 */
export function hasPermission(userRole: Role, requiredRole: Role): boolean {
  return ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY[requiredRole];
}

/**
 * User profile information.
 */
export interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  badgeNumber?: string;
  department?: string;
  role: Role;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
}

/**
 * Login request payload.
 */
export interface LoginRequest {
  username: string;
  password: string;
  mfaCode?: string;
}

/**
 * Authentication tokens.
 */
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

/**
 * Token payload (decoded JWT).
 */
export interface TokenPayload {
  sub: string;
  username: string;
  role: Role;
  exp: number;
  iat: number;
  type: 'access' | 'refresh';
  jti?: string;
}

/**
 * Password change request.
 */
export interface PasswordChangeRequest {
  currentPassword: string;
  newPassword: string;
}

/**
 * User creation request (admin only).
 */
export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  badgeNumber?: string;
  department?: string;
  role: Role;
  isActive?: boolean;
}

/**
 * User update request.
 */
export interface UpdateUserRequest {
  email?: string;
  firstName?: string;
  lastName?: string;
  badgeNumber?: string;
  department?: string;
  role?: Role;
  isActive?: boolean;
}

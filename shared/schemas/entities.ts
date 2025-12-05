/**
 * Entity schemas for the G3TI RTCC-UIP Platform.
 */

/**
 * Geographic location.
 */
export interface GeoLocation {
  latitude: number;
  longitude: number;
  accuracy?: number;
  altitude?: number;
}

/**
 * Gender enumeration.
 */
export enum Gender {
  MALE = 'male',
  FEMALE = 'female',
  OTHER = 'other',
  UNKNOWN = 'unknown',
}

/**
 * Incident type enumeration.
 */
export enum IncidentType {
  SHOOTING = 'shooting',
  ROBBERY = 'robbery',
  ASSAULT = 'assault',
  BURGLARY = 'burglary',
  THEFT = 'theft',
  HOMICIDE = 'homicide',
  DRUG_OFFENSE = 'drug_offense',
  TRAFFIC = 'traffic',
  DISTURBANCE = 'disturbance',
  SUSPICIOUS_ACTIVITY = 'suspicious_activity',
  OTHER = 'other',
}

/**
 * Incident status enumeration.
 */
export enum IncidentStatus {
  ACTIVE = 'active',
  PENDING = 'pending',
  CLOSED = 'closed',
  UNFOUNDED = 'unfounded',
}

/**
 * Camera status enumeration.
 */
export enum CameraStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  MAINTENANCE = 'maintenance',
  UNKNOWN = 'unknown',
}

/**
 * Association type enumeration.
 */
export enum AssociationType {
  SUSPECT = 'suspect',
  VICTIM = 'victim',
  WITNESS = 'witness',
  ASSOCIATE = 'associate',
  FAMILY = 'family',
  OWNER = 'owner',
  DRIVER = 'driver',
  PASSENGER = 'passenger',
}

/**
 * Person entity.
 */
export interface Person {
  id: string;
  firstName: string;
  lastName: string;
  middleName?: string;
  aliases?: string[];
  dateOfBirth?: string;
  gender?: Gender;
  race?: string;
  height?: number;
  weight?: number;
  eyeColor?: string;
  hairColor?: string;
  identifiers?: string[];
  address?: string;
  phone?: string;
  email?: string;
  gangAffiliation?: string;
  isArmedDangerous?: boolean;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Vehicle entity.
 */
export interface Vehicle {
  id: string;
  plateNumber?: string;
  plateState?: string;
  make?: string;
  model?: string;
  year?: number;
  color?: string;
  vin?: string;
  vehicleType?: string;
  isStolen?: boolean;
  isWanted?: boolean;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Incident entity.
 */
export interface Incident {
  id: string;
  incidentNumber: string;
  incidentType: IncidentType;
  title: string;
  description?: string;
  location?: GeoLocation;
  address?: string;
  occurredAt: string;
  reportedAt: string;
  status: IncidentStatus;
  severity?: number;
  respondingUnits?: string[];
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Camera entity.
 */
export interface Camera {
  id: string;
  name: string;
  location: GeoLocation;
  address?: string;
  cameraType?: string;
  owner?: string;
  status: CameraStatus;
  streamUrl?: string;
  coverageRadius?: number;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Association (relationship) between entities.
 */
export interface Association {
  id: string;
  sourceType: string;
  sourceId: string;
  targetType: string;
  targetId: string;
  associationType: AssociationType;
  confidence?: number;
  startDate?: string;
  endDate?: string;
  notes?: string;
  createdAt: string;
}

/**
 * Entity network for visualization.
 */
export interface EntityNetwork {
  nodes: EntityNode[];
  edges: EntityEdge[];
  centerNodeId: string;
}

/**
 * Node in entity network.
 */
export interface EntityNode {
  id: string;
  label: string;
  properties: Record<string, unknown>;
}

/**
 * Edge in entity network.
 */
export interface EntityEdge {
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
}

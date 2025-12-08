'use client';

import { useState } from 'react';
import { User, Car, MapPin, Shield, Camera, Users, AlertTriangle, Loader2 } from 'lucide-react';

interface EntityProfileData {
  entity_id: string;
  entity_type: string;
  name: string;
  prior_incidents: any[];
  address_history: any[];
  vehicle_connections: any[];
  weapon_matches: any[];
  lpr_activity: any[];
  bwc_interactions: any[];
  known_associates: any[];
  risk_score: number;
}

interface EntityProfileProps {
  entityId?: string;
  onProfileLoaded?: (profile: EntityProfileData) => void;
}

/**
 * Entity Profile component for viewing comprehensive entity information.
 *
 * Displays:
 * - Prior incidents
 * - Address history
 * - Vehicle connections
 * - Weapon/ballistic matches
 * - LPR activity trail
 * - BWC interactions
 * - Known associates
 * - Risk score
 */
export function EntityProfile({ entityId: initialEntityId, onProfileLoaded }: EntityProfileProps) {
  const [entityId, setEntityId] = useState(initialEntityId || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<EntityProfileData | null>(null);

  const loadProfile = async () => {
    if (!entityId.trim()) {
      setError('Please enter an entity ID');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/investigations/entities/${entityId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load entity profile');
      }

      const profileData = await response.json();
      setProfile(profileData);

      if (onProfileLoaded) {
        onProfileLoaded(profileData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 0.8) return 'text-red-600 bg-red-100';
    if (score >= 0.6) return 'text-orange-600 bg-orange-100';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 0.8) return 'Critical';
    if (score >= 0.6) return 'High';
    if (score >= 0.4) return 'Medium';
    return 'Low';
  };

  return (
    <div className="space-y-4">
      {/* Search input */}
      <div className="card">
        <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
          Entity Profile Lookup
        </h3>

        <div className="flex gap-2">
          <input
            type="text"
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            placeholder="Enter entity ID"
            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
            onKeyDown={(e) => e.key === 'Enter' && loadProfile()}
          />
          <button
            onClick={loadProfile}
            disabled={isLoading}
            className="btn-primary flex items-center gap-2 disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <User className="h-4 w-4" />
            )}
            Load Profile
          </button>
        </div>

        {error && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>}
      </div>

      {/* Profile display */}
      {profile && (
        <div className="space-y-4">
          {/* Header with risk score */}
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{profile.name}</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {profile.entity_type.toUpperCase()} - {profile.entity_id}
                </p>
              </div>
              <div className={`rounded-lg px-4 py-2 ${getRiskColor(profile.risk_score)}`}>
                <div className="text-2xl font-bold">{(profile.risk_score * 100).toFixed(0)}%</div>
                <div className="text-xs font-medium">{getRiskLabel(profile.risk_score)} Risk</div>
              </div>
            </div>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="card text-center">
              <AlertTriangle className="mx-auto mb-2 h-6 w-6 text-orange-500" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {profile.prior_incidents.length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Prior Incidents</div>
            </div>
            <div className="card text-center">
              <Car className="mx-auto mb-2 h-6 w-6 text-blue-500" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {profile.vehicle_connections.length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Vehicles</div>
            </div>
            <div className="card text-center">
              <Users className="mx-auto mb-2 h-6 w-6 text-purple-500" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {profile.known_associates.length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Associates</div>
            </div>
            <div className="card text-center">
              <Camera className="mx-auto mb-2 h-6 w-6 text-green-500" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {profile.lpr_activity.length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">LPR Hits</div>
            </div>
          </div>

          {/* Prior incidents */}
          {profile.prior_incidents.length > 0 && (
            <div className="card">
              <h4 className="mb-3 flex items-center gap-2 font-medium text-gray-900 dark:text-white">
                <AlertTriangle className="h-4 w-4 text-orange-500" />
                Prior Incidents
              </h4>
              <div className="max-h-48 space-y-2 overflow-y-auto">
                {profile.prior_incidents.map((incident, index) => (
                  <div key={index} className="rounded bg-gray-50 p-2 text-sm dark:bg-gray-800">
                    <div className="flex justify-between">
                      <span className="font-medium">{incident.incident_id}</span>
                      <span className="text-gray-500">{incident.incident_type}</span>
                    </div>
                    <p className="truncate text-gray-600 dark:text-gray-400">{incident.summary}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Vehicle connections */}
          {profile.vehicle_connections.length > 0 && (
            <div className="card">
              <h4 className="mb-3 flex items-center gap-2 font-medium text-gray-900 dark:text-white">
                <Car className="h-4 w-4 text-blue-500" />
                Vehicle Connections
              </h4>
              <div className="space-y-2">
                {profile.vehicle_connections.map((vehicle, index) => (
                  <div key={index} className="rounded bg-gray-50 p-2 text-sm dark:bg-gray-800">
                    <div className="font-medium">{vehicle.plate_number}</div>
                    <div className="text-gray-600 dark:text-gray-400">
                      {vehicle.year} {vehicle.make} {vehicle.model} - {vehicle.color}
                    </div>
                    <div className="text-xs text-gray-500">
                      Relationship: {vehicle.relationship}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Known associates */}
          {profile.known_associates.length > 0 && (
            <div className="card">
              <h4 className="mb-3 flex items-center gap-2 font-medium text-gray-900 dark:text-white">
                <Users className="h-4 w-4 text-purple-500" />
                Known Associates
              </h4>
              <div className="space-y-2">
                {profile.known_associates.map((associate, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between rounded bg-gray-50 p-2 text-sm dark:bg-gray-800"
                  >
                    <div>
                      <div className="font-medium">{associate.name}</div>
                      <div className="text-xs text-gray-500">{associate.relationship}</div>
                    </div>
                    {associate.incident_count > 0 && (
                      <span className="rounded bg-orange-100 px-2 py-1 text-xs text-orange-600">
                        {associate.incident_count} incidents
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Address history */}
          {profile.address_history.length > 0 && (
            <div className="card">
              <h4 className="mb-3 flex items-center gap-2 font-medium text-gray-900 dark:text-white">
                <MapPin className="h-4 w-4 text-red-500" />
                Address History
              </h4>
              <div className="space-y-2">
                {profile.address_history.map((address, index) => (
                  <div key={index} className="rounded bg-gray-50 p-2 text-sm dark:bg-gray-800">
                    <div className="font-medium">{address.street}</div>
                    <div className="text-gray-600 dark:text-gray-400">
                      {address.city}, {address.state} {address.zip}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Weapon matches */}
          {profile.weapon_matches.length > 0 && (
            <div className="card">
              <h4 className="mb-3 flex items-center gap-2 font-medium text-gray-900 dark:text-white">
                <Shield className="h-4 w-4 text-red-500" />
                Weapon/Ballistic Matches
              </h4>
              <div className="space-y-2">
                {profile.weapon_matches.map((weapon, index) => (
                  <div key={index} className="rounded bg-gray-50 p-2 text-sm dark:bg-gray-800">
                    <div className="font-medium">
                      {weapon.weapon_type} - {weapon.caliber}
                    </div>
                    <div className="text-gray-600 dark:text-gray-400">
                      {weapon.make} {weapon.model}
                    </div>
                    {weapon.ballistic_matches > 0 && (
                      <span className="text-xs text-red-600">
                        {weapon.ballistic_matches} ballistic matches
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default EntityProfile;

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { UnitTile } from './components/UnitTile';
import { AssignmentZone } from './components/AssignmentZone';
import { SceneOverview } from './components/SceneOverview';
import { TacticalCommsPanel } from './components/TacticalCommsPanel';

// Types
interface Unit {
  id: string;
  unit_id: string;
  badge: string | null;
  officer_name: string | null;
  status: 'available' | 'en_route' | 'on_scene' | 'busy';
  safety_level: 'green' | 'yellow' | 'orange' | 'red' | 'black';
  safety_score: number | null;
  role: string | null;
  latitude: number | null;
  longitude: number | null;
  shift: string | null;
  district: string | null;
}

interface Scene {
  id: string;
  incident_id: string;
  incident_type: string;
  address: string;
  status: 'active' | 'contained' | 'clearing' | 'secured' | 'closed';
  threat_level: string;
  units: Unit[];
  commander_unit_id: string | null;
  hazards: string[];
  tactical_notes: string[];
  recommended_actions: string[];
}

// Tactical roles for assignment zones
const TACTICAL_ROLES = [
  { id: 'contact', name: 'Contact', description: 'Primary contact with subject', color: 'bg-red-500' },
  { id: 'cover', name: 'Cover', description: 'Backup for contact officer', color: 'bg-orange-500' },
  { id: 'perimeter', name: 'Perimeter', description: 'Perimeter security', color: 'bg-yellow-500' },
  { id: 'ingress', name: 'Ingress', description: 'Entry point control', color: 'bg-blue-500' },
  { id: 'egress', name: 'Egress', description: 'Exit point control', color: 'bg-indigo-500' },
  { id: 'traffic', name: 'Traffic Control', description: 'Traffic management', color: 'bg-purple-500' },
  { id: 'surveillance', name: 'Surveillance', description: 'Observation post', color: 'bg-cyan-500' },
  { id: 'command', name: 'Command', description: 'On-scene commander', color: 'bg-gray-700' },
];

export default function OperationsPage() {
  const [availableUnits, setAvailableUnits] = useState<Unit[]>([]);
  const [activeScene, setActiveScene] = useState<Scene | null>(null);
  const [draggedUnit, setDraggedUnit] = useState<Unit | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCommsPanel, setShowCommsPanel] = useState(true);

  // Load mock data (would be API calls in production)
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        // Mock available units
        const mockUnits: Unit[] = [
          { id: '1', unit_id: 'Alpha-11', badge: 'A1101', officer_name: 'Officer Johnson', status: 'available', safety_level: 'green', safety_score: 92, role: null, latitude: 33.7490, longitude: -84.3880, shift: 'A', district: 'Central' },
          { id: '2', unit_id: 'Alpha-12', badge: 'A1201', officer_name: 'Officer Smith', status: 'available', safety_level: 'green', safety_score: 88, role: null, latitude: 33.7510, longitude: -84.3900, shift: 'A', district: 'Central' },
          { id: '3', unit_id: 'Bravo-21', badge: 'B2101', officer_name: 'Officer Williams', status: 'en_route', safety_level: 'yellow', safety_score: 75, role: null, latitude: 33.7480, longitude: -84.3850, shift: 'B', district: 'North' },
          { id: '4', unit_id: 'Bravo-22', badge: 'B2201', officer_name: 'Officer Brown', status: 'available', safety_level: 'green', safety_score: 95, role: null, latitude: 33.7520, longitude: -84.3920, shift: 'B', district: 'North' },
          { id: '5', unit_id: 'Charlie-31', badge: 'C3101', officer_name: 'Officer Davis', status: 'available', safety_level: 'green', safety_score: 90, role: null, latitude: 33.7470, longitude: -84.3870, shift: 'C', district: 'South' },
          { id: '6', unit_id: 'Charlie-32', badge: 'C3201', officer_name: 'Officer Miller', status: 'available', safety_level: 'orange', safety_score: 65, role: null, latitude: 33.7500, longitude: -84.3890, shift: 'C', district: 'South' },
          { id: '7', unit_id: 'K9-01', badge: 'K901', officer_name: 'Officer Wilson (K9)', status: 'available', safety_level: 'green', safety_score: 85, role: null, latitude: 33.7495, longitude: -84.3885, shift: 'A', district: 'Central' },
          { id: '8', unit_id: 'SWAT-01', badge: 'S101', officer_name: 'Sgt. Taylor', status: 'available', safety_level: 'green', safety_score: 98, role: null, latitude: 33.7505, longitude: -84.3895, shift: 'A', district: 'Central' },
        ];

        // Mock active scene
        const mockScene: Scene = {
          id: 'scene-001',
          incident_id: 'INC-2024-001234',
          incident_type: 'Armed Robbery',
          address: '123 Main Street, Atlanta, GA 30303',
          status: 'active',
          threat_level: 'high',
          units: [],
          commander_unit_id: null,
          hazards: ['Armed suspect', 'Multiple exits', 'Civilian presence'],
          tactical_notes: [
            'Suspect last seen heading north on foot',
            'Weapon described as black handgun',
            'Store has rear exit to alley',
          ],
          recommended_actions: [
            'Establish perimeter immediately',
            'Request K9 for tracking',
            'Coordinate with air support if available',
          ],
        };

        setAvailableUnits(mockUnits);
        setActiveScene(mockScene);
        setError(null);
      } catch (err) {
        setError('Failed to load operations data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  // Handle drag start
  const handleDragStart = useCallback((unit: Unit) => {
    setDraggedUnit(unit);
  }, []);

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setDraggedUnit(null);
  }, []);

  // Handle drop on assignment zone
  const handleDrop = useCallback((roleId: string) => {
    if (!draggedUnit || !activeScene) return;

    // Remove from available units
    setAvailableUnits(prev => prev.filter(u => u.id !== draggedUnit.id));

    // Add to scene with role
    const assignedUnit: Unit = {
      ...draggedUnit,
      role: roleId,
      status: 'on_scene',
    };

    setActiveScene(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        units: [...prev.units, assignedUnit],
      };
    });

    setDraggedUnit(null);
  }, [draggedUnit, activeScene]);

  // Handle removing unit from scene
  const handleRemoveUnit = useCallback((unitId: string) => {
    if (!activeScene) return;

    const unit = activeScene.units.find(u => u.id === unitId);
    if (!unit) return;

    // Remove from scene
    setActiveScene(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        units: prev.units.filter(u => u.id !== unitId),
      };
    });

    // Add back to available units
    const availableUnit: Unit = {
      ...unit,
      role: null,
      status: 'available',
    };
    setAvailableUnits(prev => [...prev, availableUnit]);
  }, [activeScene]);

  // Handle setting commander
  const handleSetCommander = useCallback((unitId: string) => {
    setActiveScene(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        commander_unit_id: unitId,
        units: prev.units.map(u => ({
          ...u,
          role: u.id === unitId ? 'command' : u.role,
        })),
      };
    });
  }, []);

  // Get units by role
  const getUnitsByRole = useCallback((roleId: string): Unit[] => {
    if (!activeScene) return [];
    return activeScene.units.filter(u => u.role === roleId);
  }, [activeScene]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading operations data...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Operations Command Center</h1>
          <p className="text-gray-400">Drag units to assign tactical roles</p>
        </div>
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            onClick={() => setShowCommsPanel(!showCommsPanel)}
          >
            {showCommsPanel ? 'Hide' : 'Show'} Comms Panel
          </Button>
          <Badge variant="outline" className="text-lg px-4 py-2">
            Active Scene: {activeScene?.incident_id || 'None'}
          </Badge>
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-12 gap-4">
        {/* Left Panel - Available Units */}
        <div className="col-span-3">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <span>Available Units</span>
                <Badge variant="secondary">{availableUnits.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-[calc(100vh-250px)] overflow-y-auto">
              {availableUnits.map(unit => (
                <UnitTile
                  key={unit.id}
                  unit={unit}
                  onDragStart={() => handleDragStart(unit)}
                  onDragEnd={handleDragEnd}
                  isDragging={draggedUnit?.id === unit.id}
                />
              ))}
              {availableUnits.length === 0 && (
                <p className="text-gray-500 text-center py-4">
                  All units assigned
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Center Panel - Assignment Zones */}
        <div className={showCommsPanel ? 'col-span-5' : 'col-span-6'}>
          {activeScene && (
            <SceneOverview scene={activeScene} />
          )}
          
          <div className="grid grid-cols-2 gap-3 mt-4">
            {TACTICAL_ROLES.map(role => (
              <AssignmentZone
                key={role.id}
                role={role}
                units={getUnitsByRole(role.id)}
                onDrop={() => handleDrop(role.id)}
                onRemoveUnit={handleRemoveUnit}
                onSetCommander={handleSetCommander}
                isDropTarget={draggedUnit !== null}
                isCommander={activeScene?.commander_unit_id !== null && 
                  getUnitsByRole(role.id).some(u => u.id === activeScene?.commander_unit_id)}
              />
            ))}
          </div>
        </div>

        {/* Right Panel - Scene Details & Comms */}
        <div className={showCommsPanel ? 'col-span-4' : 'col-span-3'}>
          {activeScene && (
            <div className="space-y-4">
              {/* Hazards */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-white text-sm">Hazards</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1">
                    {activeScene.hazards.map((hazard, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-red-500 rounded-full" />
                        <span className="text-sm text-gray-300">{hazard}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Tactical Notes */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-white text-sm">Tactical Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {activeScene.tactical_notes.map((note, idx) => (
                      <p key={idx} className="text-sm text-gray-300">
                        {note}
                      </p>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Recommended Actions */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-white text-sm">Recommended Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1">
                    {activeScene.recommended_actions.map((action, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <span className="text-blue-400 font-bold">{idx + 1}.</span>
                        <span className="text-sm text-gray-300">{action}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Communications Panel */}
              {showCommsPanel && (
                <TacticalCommsPanel sceneId={activeScene.id} />
              )}
            </div>
          )}
        </div>
      </div>

      {/* Unit Legend */}
      <div className="fixed bottom-4 left-4 bg-gray-800 rounded-lg p-3 border border-gray-700">
        <p className="text-xs text-gray-400 mb-2">Unit Status Legend</p>
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-green-500 rounded-full" />
            <span>Available</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-yellow-500 rounded-full" />
            <span>En Route</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-red-500 rounded-full" />
            <span>On Scene</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-purple-500 rounded-full" />
            <span>Command</span>
          </div>
        </div>
      </div>
    </div>
  );
}

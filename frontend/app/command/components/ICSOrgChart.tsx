'use client';

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface ICSRole {
  role: string;
  role_name: string;
  section: string;
  badge: string | null;
  name: string | null;
  assigned_at: string | null;
}

interface ICSOrgChartProps {
  incidentId: string;
  roles: ICSRole[];
  onAssignRole: (role: string, badge: string, name: string) => void;
}

interface PersonnelOption {
  badge: string;
  name: string;
  rank: string;
  unit: string;
}

export function ICSOrgChart({ incidentId, roles, onAssignRole }: ICSOrgChartProps) {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [draggedPerson, setDraggedPerson] = useState<PersonnelOption | null>(null);

  // Mock available personnel
  const availablePersonnel: PersonnelOption[] = [
    { badge: 'CMD-003', name: 'Captain Johnson', rank: 'Captain', unit: 'Command' },
    { badge: 'SGT-001', name: 'Sergeant Williams', rank: 'Sergeant', unit: 'Patrol' },
    { badge: 'SGT-002', name: 'Sergeant Brown', rank: 'Sergeant', unit: 'Investigations' },
    { badge: 'DET-001', name: 'Detective Garcia', rank: 'Detective', unit: 'Investigations' },
    { badge: 'DET-002', name: 'Detective Lee', rank: 'Detective', unit: 'Intelligence' },
    { badge: 'OFC-001', name: 'Officer Taylor', rank: 'Officer', unit: 'Patrol' },
    { badge: 'OFC-002', name: 'Officer Martinez', rank: 'Officer', unit: 'Patrol' },
    { badge: 'OFC-003', name: 'Officer Anderson', rank: 'Officer', unit: 'Traffic' },
    { badge: 'ANL-001', name: 'Analyst Wilson', rank: 'Analyst', unit: 'RTCC' },
    { badge: 'ANL-002', name: 'Analyst Thomas', rank: 'Analyst', unit: 'RTCC' },
  ];

  const filteredPersonnel = availablePersonnel.filter(p =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.badge.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.unit.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Group roles by section
  const rolesBySection = {
    command: roles.filter(r => r.section === 'command'),
    operations: roles.filter(r => r.section === 'operations'),
    planning: roles.filter(r => r.section === 'planning'),
    logistics: roles.filter(r => r.section === 'logistics'),
    finance: roles.filter(r => r.section === 'finance'),
  };

  const getSectionColor = (section: string) => {
    switch (section) {
      case 'command': return 'border-red-500 bg-red-900/20';
      case 'operations': return 'border-orange-500 bg-orange-900/20';
      case 'planning': return 'border-blue-500 bg-blue-900/20';
      case 'logistics': return 'border-green-500 bg-green-900/20';
      case 'finance': return 'border-purple-500 bg-purple-900/20';
      default: return 'border-gray-500 bg-gray-900/20';
    }
  };

  const handleDragStart = useCallback((person: PersonnelOption) => {
    setDraggedPerson(person);
  }, []);

  const handleDragEnd = useCallback(() => {
    setDraggedPerson(null);
  }, []);

  const handleDrop = useCallback((role: string) => {
    if (draggedPerson) {
      onAssignRole(role, draggedPerson.badge, draggedPerson.name);
      setDraggedPerson(null);
    }
  }, [draggedPerson, onAssignRole]);

  const handleAssignFromModal = useCallback((person: PersonnelOption) => {
    if (selectedRole) {
      onAssignRole(selectedRole, person.badge, person.name);
      setSelectedRole(null);
    }
  }, [selectedRole, onAssignRole]);

  const RoleCard = ({ role }: { role: ICSRole }) => (
    <div
      className={`p-3 rounded-lg border-2 ${getSectionColor(role.section)} ${
        draggedPerson ? 'border-dashed' : ''
      } transition-all cursor-pointer hover:opacity-80`}
      onDragOver={(e) => e.preventDefault()}
      onDrop={() => handleDrop(role.role)}
      onClick={() => !role.badge && setSelectedRole(role.role)}
    >
      <p className="text-xs text-gray-400 mb-1">{role.role_name}</p>
      {role.badge ? (
        <div>
          <p className="text-sm font-medium text-white">{role.name}</p>
          <p className="text-xs text-gray-400">Badge: {role.badge}</p>
          {role.assigned_at && (
            <p className="text-xs text-gray-500 mt-1">
              Assigned: {new Date(role.assigned_at).toLocaleTimeString()}
            </p>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-center py-2">
          <span className="text-xs text-gray-500">
            {draggedPerson ? 'Drop to assign' : 'Click to assign'}
          </span>
        </div>
      )}
    </div>
  );

  return (
    <div className="grid grid-cols-12 gap-4 h-full">
      {/* Org Chart */}
      <div className="col-span-9 space-y-4">
        {/* Command Section - Top */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              Command Staff
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-center mb-4">
              {/* Incident Commander at top */}
              {rolesBySection.command.filter(r => r.role === 'incident_commander').map(role => (
                <div key={role.role} className="w-48">
                  <RoleCard role={role} />
                </div>
              ))}
            </div>
            <div className="grid grid-cols-4 gap-3">
              {rolesBySection.command.filter(r => r.role !== 'incident_commander').map(role => (
                <RoleCard key={role.role} role={role} />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Section Chiefs Row */}
        <div className="grid grid-cols-4 gap-4">
          {/* Operations */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-xs flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-orange-500" />
                Operations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {rolesBySection.operations.map(role => (
                <RoleCard key={role.role} role={role} />
              ))}
              {rolesBySection.operations.length === 0 && (
                <p className="text-xs text-gray-500 text-center py-2">No roles defined</p>
              )}
            </CardContent>
          </Card>

          {/* Planning */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-xs flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                Planning
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {rolesBySection.planning.map(role => (
                <RoleCard key={role.role} role={role} />
              ))}
              {rolesBySection.planning.length === 0 && (
                <p className="text-xs text-gray-500 text-center py-2">No roles defined</p>
              )}
            </CardContent>
          </Card>

          {/* Logistics */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-xs flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                Logistics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {rolesBySection.logistics.map(role => (
                <RoleCard key={role.role} role={role} />
              ))}
              {rolesBySection.logistics.length === 0 && (
                <p className="text-xs text-gray-500 text-center py-2">No roles defined</p>
              )}
            </CardContent>
          </Card>

          {/* Finance */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-xs flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-500" />
                Finance/Admin
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {rolesBySection.finance.map(role => (
                <RoleCard key={role.role} role={role} />
              ))}
              {rolesBySection.finance.length === 0 && (
                <p className="text-xs text-gray-500 text-center py-2">No roles defined</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center gap-6 text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded border-2 border-dashed border-gray-500" />
            <span>Unassigned</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-gray-600" />
            <span>Assigned</span>
          </div>
          <span className="text-gray-600">|</span>
          <span>Drag personnel from the right panel to assign roles</span>
        </div>
      </div>

      {/* Personnel Panel */}
      <div className="col-span-3">
        <Card className="bg-gray-800 border-gray-700 h-full">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Available Personnel</CardTitle>
            <Input
              placeholder="Search by name, badge, or unit..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="mt-2 bg-gray-700 border-gray-600 text-white text-sm"
            />
          </CardHeader>
          <CardContent className="space-y-2 max-h-[calc(100vh-300px)] overflow-y-auto">
            {filteredPersonnel.map(person => (
              <div
                key={person.badge}
                draggable
                onDragStart={() => handleDragStart(person)}
                onDragEnd={handleDragEnd}
                className={`p-3 rounded-lg bg-gray-700 cursor-grab active:cursor-grabbing hover:bg-gray-600 transition-colors ${
                  draggedPerson?.badge === person.badge ? 'opacity-50' : ''
                }`}
              >
                <p className="text-sm font-medium text-white">{person.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="outline" className="text-xs">
                    {person.rank}
                  </Badge>
                  <span className="text-xs text-gray-400">{person.unit}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">Badge: {person.badge}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Assignment Modal */}
      {selectedRole && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="bg-gray-800 border-gray-700 w-96">
            <CardHeader>
              <CardTitle className="text-white">
                Assign {roles.find(r => r.role === selectedRole)?.role_name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Input
                placeholder="Search personnel..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-gray-700 border-gray-600 text-white"
              />
              <div className="max-h-60 overflow-y-auto space-y-2">
                {filteredPersonnel.map(person => (
                  <div
                    key={person.badge}
                    onClick={() => handleAssignFromModal(person)}
                    className="p-3 rounded-lg bg-gray-700 cursor-pointer hover:bg-gray-600"
                  >
                    <p className="text-sm font-medium text-white">{person.name}</p>
                    <p className="text-xs text-gray-400">{person.rank} - {person.unit}</p>
                  </div>
                ))}
              </div>
              <Button
                variant="outline"
                className="w-full mt-2"
                onClick={() => setSelectedRole(null)}
              >
                Cancel
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

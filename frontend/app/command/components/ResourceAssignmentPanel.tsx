'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Resource {
  id: string;
  name: string;
  resource_type: string;
  status: string;
  agency: string;
  call_sign: string;
  role: string | null;
}

interface ResourceAssignmentPanelProps {
  incidentId: string;
  resources: Resource[];
}

export function ResourceAssignmentPanel({ incidentId, resources }: ResourceAssignmentPanelProps) {
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);

  const resourceTypes = [
    { id: 'all', label: 'All Types' },
    { id: 'patrol_unit', label: 'Patrol' },
    { id: 'swat', label: 'SWAT' },
    { id: 'k9', label: 'K9' },
    { id: 'ems', label: 'EMS' },
    { id: 'fire', label: 'Fire' },
    { id: 'aviation', label: 'Aviation' },
  ];

  const roles = [
    'Perimeter',
    'Entry Team',
    'Cover',
    'Medical',
    'Traffic Control',
    'Surveillance',
    'Command Post',
    'Staging',
    'Standby',
  ];

  const getResourceIcon = (type: string) => {
    switch (type) {
      case 'patrol_unit': return '🚔';
      case 'swat': return '🛡️';
      case 'k9': return '🐕';
      case 'ems': return '🚑';
      case 'fire': return '🚒';
      case 'aviation': return '🚁';
      default: return '📍';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_scene': return 'bg-green-500';
      case 'en_route': return 'bg-yellow-500';
      case 'staged': return 'bg-blue-500';
      case 'available': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'on_scene': return 'On Scene';
      case 'en_route': return 'En Route';
      case 'staged': return 'Staged';
      case 'available': return 'Available';
      default: return status;
    }
  };

  const filteredResources = resources.filter(resource => {
    if (filter !== 'all' && resource.resource_type !== filter) return false;
    if (searchTerm && !resource.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !resource.call_sign.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const resourcesByStatus = {
    on_scene: filteredResources.filter(r => r.status === 'on_scene'),
    en_route: filteredResources.filter(r => r.status === 'en_route'),
    staged: filteredResources.filter(r => r.status === 'staged'),
  };

  const ResourceCard = ({ resource }: { resource: Resource }) => (
    <div
      className={`p-3 rounded-lg bg-gray-700 cursor-pointer hover:bg-gray-600 transition-colors ${
        selectedResource?.id === resource.id ? 'ring-2 ring-blue-500' : ''
      }`}
      onClick={() => setSelectedResource(resource)}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{getResourceIcon(resource.resource_type)}</span>
          <div>
            <p className="text-sm font-medium text-white">{resource.call_sign}</p>
            <p className="text-xs text-gray-400">{resource.name}</p>
          </div>
        </div>
        <span className={`w-3 h-3 rounded-full ${getStatusColor(resource.status)}`} />
      </div>
      <div className="flex items-center justify-between">
        <Badge variant="outline" className="text-xs">
          {resource.agency}
        </Badge>
        {resource.role && (
          <Badge className="bg-blue-600 text-xs">
            {resource.role}
          </Badge>
        )}
      </div>
    </div>
  );

  return (
    <div className="h-full flex gap-4">
      {/* Resource List */}
      <div className="flex-1 space-y-4">
        {/* Filters */}
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <Input
                placeholder="Search resources..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64 bg-gray-700 border-gray-600 text-white"
              />
              <div className="flex gap-2">
                {resourceTypes.map(type => (
                  <Button
                    key={type.id}
                    variant={filter === type.id ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setFilter(type.id)}
                    className={filter === type.id ? 'bg-blue-600' : ''}
                  >
                    {type.label}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Resources by Status */}
        <div className="grid grid-cols-3 gap-4">
          {/* On Scene */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-green-500" />
                On Scene ({resourcesByStatus.on_scene.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-[calc(100vh-350px)] overflow-y-auto">
              {resourcesByStatus.on_scene.map(resource => (
                <ResourceCard key={resource.id} resource={resource} />
              ))}
              {resourcesByStatus.on_scene.length === 0 && (
                <p className="text-xs text-gray-500 text-center py-4">No resources on scene</p>
              )}
            </CardContent>
          </Card>

          {/* En Route */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-yellow-500" />
                En Route ({resourcesByStatus.en_route.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-[calc(100vh-350px)] overflow-y-auto">
              {resourcesByStatus.en_route.map(resource => (
                <ResourceCard key={resource.id} resource={resource} />
              ))}
              {resourcesByStatus.en_route.length === 0 && (
                <p className="text-xs text-gray-500 text-center py-4">No resources en route</p>
              )}
            </CardContent>
          </Card>

          {/* Staged */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-blue-500" />
                Staged ({resourcesByStatus.staged.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-[calc(100vh-350px)] overflow-y-auto">
              {resourcesByStatus.staged.map(resource => (
                <ResourceCard key={resource.id} resource={resource} />
              ))}
              {resourcesByStatus.staged.length === 0 && (
                <p className="text-xs text-gray-500 text-center py-4">No resources staged</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Resource Details Panel */}
      <div className="w-80">
        <Card className="bg-gray-800 border-gray-700 h-full">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Resource Details</CardTitle>
          </CardHeader>
          <CardContent>
            {selectedResource ? (
              <div className="space-y-4">
                <div className="text-center py-4">
                  <span className="text-4xl">{getResourceIcon(selectedResource.resource_type)}</span>
                  <h3 className="text-lg font-bold text-white mt-2">{selectedResource.call_sign}</h3>
                  <p className="text-sm text-gray-400">{selectedResource.name}</p>
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-gray-400">Status</p>
                    <div className="flex items-center gap-2">
                      <span className={`w-3 h-3 rounded-full ${getStatusColor(selectedResource.status)}`} />
                      <span className="text-white">{getStatusLabel(selectedResource.status)}</span>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400">Agency</p>
                    <p className="text-white">{selectedResource.agency}</p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400">Type</p>
                    <p className="text-white capitalize">{selectedResource.resource_type.replace('_', ' ')}</p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400 mb-1">Assigned Role</p>
                    <Select defaultValue={selectedResource.role || ''}>
                      <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                        <SelectValue placeholder="Select role..." />
                      </SelectTrigger>
                      <SelectContent>
                        {roles.map(role => (
                          <SelectItem key={role} value={role.toLowerCase().replace(' ', '_')}>
                            {role}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="pt-4 space-y-2">
                  <Button className="w-full bg-green-600 hover:bg-green-700">
                    Mark Arrived
                  </Button>
                  <Button variant="outline" className="w-full">
                    Release Resource
                  </Button>
                  <Button variant="outline" className="w-full text-red-400 border-red-400 hover:bg-red-900/20">
                    Remove from Incident
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-500 text-center">
                  Select a resource to view details
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface Resource {
  id: string;
  name: string;
  resource_type: string;
  status: string;
  agency: string;
  call_sign: string;
  role: string | null;
}

interface StrategyMapViewerProps {
  incidentId: string;
  center: {
    latitude: number;
    longitude: number;
    address: string;
  };
  resources: Resource[];
}

interface MapLayer {
  id: string;
  name: string;
  visible: boolean;
  color: string;
}

export function StrategyMapViewer({ incidentId, center, resources }: StrategyMapViewerProps) {
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const [layers, setLayers] = useState<MapLayer[]>([
    { id: 'units', name: 'Units', visible: true, color: 'blue' },
    { id: 'perimeter', name: 'Perimeter', visible: true, color: 'red' },
    { id: 'cameras', name: 'Cameras', visible: true, color: 'green' },
    { id: 'gunfire', name: 'Gunfire Detection', visible: true, color: 'orange' },
    { id: 'threats', name: 'Threat Zones', visible: false, color: 'purple' },
    { id: 'evacuation', name: 'Evacuation Routes', visible: false, color: 'yellow' },
  ]);

  const drawingTools = [
    { id: 'perimeter', name: 'Draw Perimeter', icon: '🔲' },
    { id: 'hotzone', name: 'Hot Zone', icon: '🔥' },
    { id: 'searchgrid', name: 'Search Grid', icon: '📐' },
    { id: 'evacuation', name: 'Evacuation Route', icon: '🚶' },
    { id: 'marker', name: 'Add Marker', icon: '📍' },
    { id: 'text', name: 'Add Label', icon: '🏷️' },
  ];

  const toggleLayer = (layerId: string) => {
    setLayers(prev => prev.map(layer =>
      layer.id === layerId ? { ...layer, visible: !layer.visible } : layer
    ));
  };

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
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="h-full flex gap-4">
      {/* Map Area */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <Card className="bg-gray-800 border-gray-700 mb-4">
          <CardContent className="p-3">
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                {drawingTools.map(tool => (
                  <Button
                    key={tool.id}
                    variant={activeTool === tool.id ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setActiveTool(activeTool === tool.id ? null : tool.id)}
                    className={activeTool === tool.id ? 'bg-blue-600' : ''}
                  >
                    <span className="mr-1">{tool.icon}</span>
                    {tool.name}
                  </Button>
                ))}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  Undo
                </Button>
                <Button variant="outline" size="sm">
                  Clear All
                </Button>
                <Button variant="outline" size="sm">
                  Export
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Map Placeholder */}
        <Card className="bg-gray-800 border-gray-700 flex-1">
          <CardContent className="p-0 h-full relative">
            {/* Map would be rendered here with Leaflet/Mapbox */}
            <div className="absolute inset-0 bg-gray-900 flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">🗺️</div>
                <p className="text-gray-400 mb-2">Strategy Map</p>
                <p className="text-sm text-gray-500">
                  Center: {center.latitude.toFixed(4)}, {center.longitude.toFixed(4)}
                </p>
                <p className="text-xs text-gray-600 mt-1">{center.address}</p>
                
                {/* Mock map elements */}
                <div className="mt-8 grid grid-cols-3 gap-4 max-w-md mx-auto">
                  <div className="bg-red-900/30 border border-red-500 rounded-lg p-3">
                    <p className="text-xs text-red-400">Outer Perimeter</p>
                    <p className="text-sm text-white">Established</p>
                  </div>
                  <div className="bg-orange-900/30 border border-orange-500 rounded-lg p-3">
                    <p className="text-xs text-orange-400">Inner Perimeter</p>
                    <p className="text-sm text-white">Established</p>
                  </div>
                  <div className="bg-yellow-900/30 border border-yellow-500 rounded-lg p-3">
                    <p className="text-xs text-yellow-400">Hot Zone</p>
                    <p className="text-sm text-white">Active</p>
                  </div>
                </div>

                {activeTool && (
                  <div className="mt-4 p-3 bg-blue-900/30 border border-blue-500 rounded-lg inline-block">
                    <p className="text-sm text-blue-400">
                      {drawingTools.find(t => t.id === activeTool)?.icon} Drawing: {drawingTools.find(t => t.id === activeTool)?.name}
                    </p>
                    <p className="text-xs text-gray-400">Click on map to place points</p>
                  </div>
                )}
              </div>
            </div>

            {/* Unit positions overlay */}
            <div className="absolute bottom-4 left-4 right-4">
              <div className="flex flex-wrap gap-2">
                {resources.filter(r => r.status === 'on_scene').map(resource => (
                  <div
                    key={resource.id}
                    className="bg-gray-800/90 border border-gray-600 rounded px-2 py-1 flex items-center gap-1"
                  >
                    <span>{getResourceIcon(resource.resource_type)}</span>
                    <span className="text-xs text-white">{resource.call_sign}</span>
                    <span className={`w-2 h-2 rounded-full ${getStatusColor(resource.status)}`} />
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Right Panel - Layers & Resources */}
      <div className="w-72 space-y-4">
        {/* Layers */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Map Layers</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {layers.map(layer => (
              <div
                key={layer.id}
                onClick={() => toggleLayer(layer.id)}
                className={`p-2 rounded cursor-pointer flex items-center justify-between ${
                  layer.visible ? 'bg-gray-700' : 'bg-gray-800'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`w-3 h-3 rounded ${
                      layer.visible ? `bg-${layer.color}-500` : 'bg-gray-600'
                    }`}
                    style={{ backgroundColor: layer.visible ? layer.color : undefined }}
                  />
                  <span className={`text-sm ${layer.visible ? 'text-white' : 'text-gray-500'}`}>
                    {layer.name}
                  </span>
                </div>
                <Badge variant="outline" className="text-xs">
                  {layer.visible ? 'ON' : 'OFF'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Resources on Map */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Resources on Map</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 max-h-64 overflow-y-auto">
            {resources.map(resource => (
              <div
                key={resource.id}
                className="p-2 rounded bg-gray-700 flex items-center justify-between"
              >
                <div className="flex items-center gap-2">
                  <span>{getResourceIcon(resource.resource_type)}</span>
                  <div>
                    <p className="text-sm text-white">{resource.call_sign}</p>
                    <p className="text-xs text-gray-400">{resource.role || 'Unassigned'}</p>
                  </div>
                </div>
                <span className={`w-2 h-2 rounded-full ${getStatusColor(resource.status)}`} />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Map Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div className="bg-gray-700 rounded p-2">
                <p className="text-lg font-bold text-white">{resources.length}</p>
                <p className="text-xs text-gray-400">Resources</p>
              </div>
              <div className="bg-gray-700 rounded p-2">
                <p className="text-lg font-bold text-white">2</p>
                <p className="text-xs text-gray-400">Perimeters</p>
              </div>
              <div className="bg-gray-700 rounded p-2">
                <p className="text-lg font-bold text-white">4</p>
                <p className="text-xs text-gray-400">Cameras</p>
              </div>
              <div className="bg-gray-700 rounded p-2">
                <p className="text-lg font-bold text-white">1</p>
                <p className="text-xs text-gray-400">Hot Zones</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

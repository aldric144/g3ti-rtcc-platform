'use client';

import { useState } from 'react';
import { X, Eye, EyeOff } from 'lucide-react';

interface MapControlsProps {
  onClose: () => void;
}

interface Layer {
  id: string;
  name: string;
  enabled: boolean;
  color: string;
}

/**
 * Map layer controls panel.
 */
export function MapControls({ onClose }: MapControlsProps) {
  const [layers, setLayers] = useState<Layer[]>([
    { id: 'gunshots', name: 'Gunshot Alerts', enabled: true, color: '#dc2626' },
    { id: 'lpr', name: 'LPR Hits', enabled: true, color: '#ea580c' },
    { id: 'cameras', name: 'Cameras', enabled: true, color: '#22c55e' },
    { id: 'incidents', name: 'Incidents', enabled: true, color: '#2563eb' },
    { id: 'units', name: 'Units', enabled: false, color: '#8b5cf6' },
    { id: 'heatmap', name: 'Crime Heatmap', enabled: false, color: '#f59e0b' },
  ]);

  const toggleLayer = (id: string) => {
    setLayers((prev) =>
      prev.map((layer) =>
        layer.id === id ? { ...layer, enabled: !layer.enabled } : layer
      )
    );
  };

  return (
    <div className="rounded-lg bg-white shadow-lg dark:bg-gray-800">
      <div className="flex items-center justify-between border-b p-3 dark:border-gray-700">
        <h3 className="font-semibold text-gray-900 dark:text-white">
          Map Layers
        </h3>
        <button
          onClick={onClose}
          className="rounded p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-3 space-y-2">
        {layers.map((layer) => (
          <button
            key={layer.id}
            onClick={() => toggleLayer(layer.id)}
            className="flex w-full items-center justify-between rounded-lg px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <div className="flex items-center gap-3">
              <div
                className="h-3 w-3 rounded-full"
                style={{ backgroundColor: layer.color }}
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {layer.name}
              </span>
            </div>
            {layer.enabled ? (
              <Eye className="h-4 w-4 text-gray-500" />
            ) : (
              <EyeOff className="h-4 w-4 text-gray-400" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

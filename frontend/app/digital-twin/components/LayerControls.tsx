'use client';

interface LayerControlsProps {
  activeLayers: string[];
  onToggleLayer: (layer: string) => void;
}

const layers = [
  { id: 'buildings', label: 'Buildings', icon: '🏢' },
  { id: 'roads', label: 'Roads', icon: '🛣️' },
  { id: 'officers', label: 'Officers', icon: '👮' },
  { id: 'vehicles', label: 'Vehicles', icon: '🚔' },
  { id: 'drones', label: 'Drones', icon: '🚁' },
  { id: 'incidents', label: 'Incidents', icon: '⚠️' },
  { id: 'sensors', label: 'Sensors', icon: '📡' },
  { id: 'weather', label: 'Weather', icon: '🌤️' },
  { id: 'traffic', label: 'Traffic', icon: '🚦' },
  { id: 'crowd', label: 'Crowd Density', icon: '👥' },
];

export default function LayerControls({
  activeLayers,
  onToggleLayer,
}: LayerControlsProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Map Layers</h3>
      <div className="space-y-2">
        {layers.map((layer) => (
          <button
            key={layer.id}
            onClick={() => onToggleLayer(layer.id)}
            className={`w-full flex items-center justify-between p-2 rounded transition-colors ${
              activeLayers.includes(layer.id)
                ? 'bg-blue-600 bg-opacity-30 border border-blue-500'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <div className="flex items-center">
              <span className="mr-2">{layer.icon}</span>
              <span className="text-sm">{layer.label}</span>
            </div>
            <div
              className={`w-4 h-4 rounded-full ${
                activeLayers.includes(layer.id)
                  ? 'bg-blue-500'
                  : 'bg-gray-500'
              }`}
            >
              {activeLayers.includes(layer.id) && (
                <svg
                  className="w-4 h-4 text-white"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </div>
          </button>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-700">
        <button
          onClick={() => {
            layers.forEach((l) => {
              if (!activeLayers.includes(l.id)) {
                onToggleLayer(l.id);
              }
            });
          }}
          className="w-full bg-gray-700 hover:bg-gray-600 py-2 rounded text-sm mb-2"
        >
          Show All
        </button>
        <button
          onClick={() => {
            layers.forEach((l) => {
              if (activeLayers.includes(l.id)) {
                onToggleLayer(l.id);
              }
            });
          }}
          className="w-full bg-gray-700 hover:bg-gray-600 py-2 rounded text-sm"
        >
          Hide All
        </button>
      </div>
    </div>
  );
}

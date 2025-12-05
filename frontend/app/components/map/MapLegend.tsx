'use client';

/**
 * Map legend component showing marker meanings.
 */
export function MapLegend() {
  const items = [
    { color: '#dc2626', label: 'Gunshot Alert' },
    { color: '#ea580c', label: 'LPR Hit' },
    { color: '#22c55e', label: 'Camera' },
    { color: '#2563eb', label: 'Incident' },
    { color: '#8b5cf6', label: 'Unit' },
  ];

  return (
    <div className="rounded-lg bg-white/90 px-3 py-2 shadow-lg backdrop-blur dark:bg-gray-800/90">
      <div className="flex items-center gap-4">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-1.5">
            <div
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-xs text-gray-600 dark:text-gray-400">
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

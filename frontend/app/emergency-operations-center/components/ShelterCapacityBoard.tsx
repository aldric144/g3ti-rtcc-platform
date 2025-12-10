'use client';

import React, { useState, useEffect } from 'react';

interface Shelter {
  shelter_id: string;
  name: string;
  shelter_type: string;
  capacity: int;
  current_occupancy: number;
  status: string;
  address: {
    street: string;
    city: string;
    state: string;
  };
  amenities: string[];
  pet_friendly: boolean;
  medical_capability: boolean;
}

interface ShelterMetrics {
  total_shelters: number;
  open_shelters: number;
  total_capacity: number;
  total_occupancy: number;
  available_capacity: number;
}

export default function ShelterCapacityBoard() {
  const [shelters, setShelters] = useState<Shelter[]>([]);
  const [metrics, setMetrics] = useState<ShelterMetrics | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchShelterData();
    const interval = setInterval(fetchShelterData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchShelterData = async () => {
    try {
      const [sheltersRes, capacityRes] = await Promise.all([
        fetch('/api/emergency/resources/shelters'),
        fetch('/api/emergency/resources/shelters/capacity'),
      ]);

      if (sheltersRes.ok) setShelters(await sheltersRes.json());
      if (capacityRes.ok) {
        const data = await capacityRes.json();
        setMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Failed to fetch shelter data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'open': return 'bg-green-600';
      case 'full': return 'bg-red-600';
      case 'standby': return 'bg-yellow-600';
      case 'closed': return 'bg-gray-600';
      default: return 'bg-gray-600';
    }
  };

  const getOccupancyColor = (occupancy: number, capacity: number): string => {
    const percent = (occupancy / capacity) * 100;
    if (percent >= 90) return 'bg-red-500';
    if (percent >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const filteredShelters = filter === 'all'
    ? shelters
    : shelters.filter(s => s.status === filter);

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 h-full flex items-center justify-center">
        <div className="text-gray-400">Loading shelter data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>🏠</span> Shelter Capacity
        </h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-gray-800 text-white px-3 py-1 rounded text-sm"
        >
          <option value="all">All Shelters</option>
          <option value="open">Open</option>
          <option value="standby">Standby</option>
          <option value="full">Full</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      {metrics && (
        <div className="grid grid-cols-5 gap-3 mb-4">
          <div className="bg-gray-800 p-3 rounded text-center">
            <div className="text-gray-400 text-xs">Total</div>
            <div className="text-white text-lg font-bold">{metrics.total_shelters}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded text-center">
            <div className="text-gray-400 text-xs">Open</div>
            <div className="text-green-400 text-lg font-bold">{metrics.open_shelters}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded text-center">
            <div className="text-gray-400 text-xs">Capacity</div>
            <div className="text-white text-lg font-bold">{metrics.total_capacity.toLocaleString()}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded text-center">
            <div className="text-gray-400 text-xs">Occupied</div>
            <div className="text-white text-lg font-bold">{metrics.total_occupancy.toLocaleString()}</div>
          </div>
          <div className="bg-gray-800 p-3 rounded text-center">
            <div className="text-gray-400 text-xs">Available</div>
            <div className="text-blue-400 text-lg font-bold">{metrics.available_capacity.toLocaleString()}</div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        <div className="space-y-2">
          {filteredShelters.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No shelters found</div>
          ) : (
            filteredShelters.map(shelter => (
              <div key={shelter.shelter_id} className="bg-gray-800 p-4 rounded">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-white font-medium">{shelter.name}</span>
                      <span className={`px-2 py-0.5 rounded text-xs text-white ${getStatusColor(shelter.status)}`}>
                        {shelter.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="text-gray-400 text-sm mt-1">
                      {shelter.shelter_type} • {shelter.address?.city || 'Unknown'}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {shelter.pet_friendly && (
                      <span className="text-lg" title="Pet Friendly">🐾</span>
                    )}
                    {shelter.medical_capability && (
                      <span className="text-lg" title="Medical Capability">🏥</span>
                    )}
                  </div>
                </div>

                <div className="mt-3">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-400">Occupancy</span>
                    <span className="text-white">
                      {shelter.current_occupancy} / {shelter.capacity}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getOccupancyColor(shelter.current_occupancy, shelter.capacity)}`}
                      style={{ width: `${Math.min(100, (shelter.current_occupancy / shelter.capacity) * 100)}%` }}
                    />
                  </div>
                </div>

                {shelter.amenities && shelter.amenities.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {shelter.amenities.slice(0, 4).map((amenity, i) => (
                      <span key={i} className="bg-gray-700 text-gray-300 px-2 py-0.5 rounded text-xs">
                        {amenity}
                      </span>
                    ))}
                    {shelter.amenities.length > 4 && (
                      <span className="text-gray-500 text-xs">+{shelter.amenities.length - 4} more</span>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

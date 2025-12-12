"use client";

import React, { useState, useEffect } from "react";

interface Shelter {
  shelter_id: string;
  name: string;
  zone: string;
  address: string;
  capacity: number;
  current_occupancy: number;
  status: string;
  amenities: string[];
  special_needs_capacity: number;
  pet_friendly: boolean;
}

interface ResourceStatus {
  available_resources: Record<string, number>;
  total_shelter_capacity: number;
  total_shelter_occupancy: number;
  shelters: Shelter[];
}

export default function ResourceShelterDashboard() {
  const [resourceStatus, setResourceStatus] = useState<ResourceStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedShelter, setSelectedShelter] = useState<Shelter | null>(null);

  useEffect(() => {
    fetchResourceStatus();
    const interval = setInterval(fetchResourceStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchResourceStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/emergency-ai/resource-status");
      if (response.ok) {
        const data = await response.json();
        setResourceStatus(data);
      }
    } catch (error) {
      console.error("Failed to fetch resource status:", error);
    } finally {
      setLoading(false);
    }
  };

  const getOccupancyColor = (occupancy: number, capacity: number) => {
    const percent = (occupancy / capacity) * 100;
    if (percent >= 90) return "bg-red-500";
    if (percent >= 70) return "bg-orange-500";
    if (percent >= 50) return "bg-yellow-500";
    return "bg-green-500";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open":
        return "text-green-400";
      case "full":
        return "text-red-400";
      case "closed":
        return "text-gray-400";
      default:
        return "text-yellow-400";
    }
  };

  const resourceIcons: Record<string, string> = {
    patrol_units: "🚔",
    fire_engines: "🚒",
    ambulances: "🚑",
    rescue_squads: "🚨",
    evacuation_buses: "🚌",
    generators: "⚡",
    water_trucks: "💧",
    food_trucks: "🍽️",
    medical_teams: "🏥",
    search_rescue_teams: "🔍",
    drones: "🛸",
    boats: "🚤",
  };

  if (loading && !resourceStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-2">Total Shelter Capacity</h3>
          <p className="text-3xl font-bold text-blue-400">
            {resourceStatus?.total_shelter_capacity.toLocaleString() || 0}
          </p>
          <p className="text-sm text-gray-400">beds available</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-2">Current Occupancy</h3>
          <p className="text-3xl font-bold text-yellow-400">
            {resourceStatus?.total_shelter_occupancy.toLocaleString() || 0}
          </p>
          <p className="text-sm text-gray-400">residents sheltered</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-2">Available Capacity</h3>
          <p className="text-3xl font-bold text-green-400">
            {(
              (resourceStatus?.total_shelter_capacity || 0) -
              (resourceStatus?.total_shelter_occupancy || 0)
            ).toLocaleString()}
          </p>
          <p className="text-sm text-gray-400">beds remaining</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-2">Occupancy Rate</h3>
          <p className="text-3xl font-bold text-purple-400">
            {resourceStatus?.total_shelter_capacity
              ? (
                  (resourceStatus.total_shelter_occupancy /
                    resourceStatus.total_shelter_capacity) *
                  100
                ).toFixed(1)
              : 0}
            %
          </p>
          <p className="text-sm text-gray-400">utilization</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Available Resources</h2>
          <div className="grid grid-cols-2 gap-3">
            {resourceStatus?.available_resources &&
              Object.entries(resourceStatus.available_resources).map(
                ([resource, count]) => (
                  <div
                    key={resource}
                    className="bg-gray-700 rounded-lg p-3 flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-xl">
                        {resourceIcons[resource] || "📦"}
                      </span>
                      <span className="text-sm capitalize">
                        {resource.replace(/_/g, " ")}
                      </span>
                    </div>
                    <span className="font-bold text-lg">{count}</span>
                  </div>
                )
              )}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Shelter Status</h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {resourceStatus?.shelters.map((shelter) => (
              <div
                key={shelter.shelter_id}
                className={`bg-gray-700 rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedShelter?.shelter_id === shelter.shelter_id
                    ? "ring-2 ring-blue-500"
                    : "hover:bg-gray-600"
                }`}
                onClick={() => setSelectedShelter(shelter)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{shelter.name}</span>
                  <span className={`text-sm ${getStatusColor(shelter.status)}`}>
                    {shelter.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-2">{shelter.zone}</p>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getOccupancyColor(
                      shelter.current_occupancy,
                      shelter.capacity
                    )}`}
                    style={{
                      width: `${Math.min(
                        (shelter.current_occupancy / shelter.capacity) * 100,
                        100
                      )}%`,
                    }}
                  ></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  {shelter.current_occupancy} / {shelter.capacity} (
                  {((shelter.current_occupancy / shelter.capacity) * 100).toFixed(
                    0
                  )}
                  %)
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedShelter && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">
            Shelter Details: {selectedShelter.name}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-400">Address</p>
              <p className="font-medium">{selectedShelter.address}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Zone</p>
              <p className="font-medium">{selectedShelter.zone}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Special Needs Capacity</p>
              <p className="font-medium">{selectedShelter.special_needs_capacity}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Pet Friendly</p>
              <p className="font-medium">
                {selectedShelter.pet_friendly ? "Yes 🐾" : "No"}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <p className="text-sm text-gray-400 mb-2">Amenities</p>
            <div className="flex flex-wrap gap-2">
              {selectedShelter.amenities.map((amenity, idx) => (
                <span
                  key={idx}
                  className="bg-gray-700 px-3 py-1 rounded-full text-sm"
                >
                  {amenity}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Supply Alerts</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-yellow-400">⚠️</span>
              <span className="font-medium text-yellow-400">Low Supply</span>
            </div>
            <p className="text-sm text-gray-300">
              Water supplies at Zone_E distribution point below 30%
            </p>
          </div>
          <div className="bg-green-900/30 border border-green-600 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-green-400">✓</span>
              <span className="font-medium text-green-400">Resupply Complete</span>
            </div>
            <p className="text-sm text-gray-300">
              Medical supplies restocked at Community Center
            </p>
          </div>
          <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-blue-400">🚚</span>
              <span className="font-medium text-blue-400">In Transit</span>
            </div>
            <p className="text-sm text-gray-300">
              Generator shipment arriving in 2 hours
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
